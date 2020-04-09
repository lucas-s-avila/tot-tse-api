import os
import json
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from minio import Minio

from .service import TermSearchEngine

from .minio_driver import MinioOcrLister, MinioOcrDownloader, MinioSearchUploader, MinioSearchDownloader
from .scheduler_driver import SchedulerAPI

def create_app(routes_config: dict, app_config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY='dev' # TODO: Colocar algo mais seguro
  )

  if app_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.from_mapping(app_config)

  minio_client = Minio(
    routes_config['minio']['addr'],
    access_key=routes_config['minio']['access_key'],
    secret_key=routes_config['minio']['secret_key'],
    secure=routes_config['minio']['secure']
  )

  ocr_lister = MinioOcrLister(minio_client)
  ocr_downloader = MinioOcrDownloader(minio_client)
  search_uploader = MinioSearchUploader(minio_client)
  search_downloader = MinioSearchDownloader(minio_client)
  scheduler_api = SchedulerAPI(routes_config['scheduler']['addr'])

  service = TermSearchEngine(scheduler_api, ocr_lister, ocr_downloader, search_uploader, search_downloader)
  

  @app.route('/available')
  def listAvailableFiles():
    available = service.available_ocrs()
    print(available)
    return jsonify(available)

  @app.route('/search')
  def searchWord():
    word = request.args.get('word')
    ids = request.args.getlist('ids')
    print(word)
    print(ids)
    return Response(stream_with_context(service.search_term(word, ids)), mimetype='application/json')
  

  CORS(app)
  return app
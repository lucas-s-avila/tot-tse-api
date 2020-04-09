import os
import json
from flask import Flask, jsonify, request, Response, stream_with_context, send_file
from flask_cors import CORS
from minio import Minio

from .service import TermSearchEngine

from .minio_driver import MinioOcrLister, MinioOcrDownloader, MinioSearchUploader, MinioSearchDownloader, MinioSearchableDownloader
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
  searchable_downloader = MinioSearchableDownloader(minio_client)
  scheduler_api = SchedulerAPI(routes_config['scheduler']['addr'])

  service = TermSearchEngine(scheduler_api, ocr_lister, ocr_downloader, search_uploader, search_downloader, searchable_downloader)
  
  @app.route('/ping')
  def ping():
    return("tse-api is working.")

  @app.route('/available')
  def listAvailableFiles():
    available = service.available_ocrs()
    print(available)
    return jsonify(available)

  @app.route('/search')
  def searchWord():
    word = request.args.get('word')
    ids = request.args.get('ids')
    id_list = ids.split(',')
    return Response(stream_with_context(service.search_term(word, id_list)), mimetype='application/json')
  
  @app.route('/download')
  def downloadMarked():
    id_search = request.args.get('id_s')
    id_file = request.args.get('id_f')
    filename = service.mark_words(id_search, id_file)
    print(filename)
    return send_file(filename, as_attachment=True)
  

  CORS(app)
  return app
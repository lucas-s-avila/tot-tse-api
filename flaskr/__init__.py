import os
import json
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from minio import Minio

from .service import TermSearchEngine

from .minio_driver import MinioOcrLister, MinioOcrDownloader, MinioSearchUploader, MinioSearchDownloader

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY='dev' # TODO: Colocar algo mais seguro
  )

  if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.from_mapping(test_config)

  minio_client = Minio(
    '5f29d32b.ngrok.io',
    access_key='minioadmin',
    secret_key='minioadmin',
    secure=False
  )

  ocr_lister = MinioOcrLister(minio_client)
  ocr_downloader = MinioOcrDownloader(minio_client)
  search_uploader = MinioSearchUploader(minio_client)
  search_downloader = MinioSearchDownloader(minio_client)

  service = TermSearchEngine('http://f8a95233.ngrok.io', ocr_lister, ocr_downloader, search_uploader, search_downloader)
  

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
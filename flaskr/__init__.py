import os
import json
from flask import Flask, jsonify
from minio import Minio

from .service import TermSearchEngine

from .minio_driver import MinioOcrLister

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
    'localhost:9000',
    access_key='minioadmin',
    secret_key='minioadmin',
    secure=False
  )

  ocr_lister = MinioOcrLister(minio_client)
  
  service = TermSearchEngine('http://localhost:8000', ocr_lister)
  
  @app.route('/available')
  def listAvailableFiles():
    available = service.available_ocrs()
    return jsonify(available)

  return app

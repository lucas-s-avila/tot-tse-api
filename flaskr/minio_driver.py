import os

from .service import OcrLister, OcrDownloader, SearchUploader, SearchDownloader, SearchableDownloader
from minio import Minio

class MinioOcrLister(OcrLister):
    
    def __init__(self, minio_client: Minio): 
        self.minio_client = minio_client
    
    def list_ocr(self, bucket_name: str) -> list:
        ocr_files = self.minio_client.list_objects(bucket_name)
        ids = [ocr.object_name for ocr in ocr_files]
        print(ids)
        return ids

class MinioOcrDownloader(OcrDownloader):

    def __init__(self, minio_client: Minio):
        self.minio_client = minio_client

    def download_ocr(self, bucket_name: str, object_key: str) -> str:
        ocr_path: str = os.getcwd() + "/hocrs/" + object_key
        self.minio_client.fget_object(bucket_name, object_key, ocr_path)

class MinioSearchUploader(SearchUploader):
    
    def __init__(self, minio_client: Minio):
        self.minio_client = minio_client
    
    def upload_search(self, object_key: str, search_file: str):
        self.minio_client.fput_object('tot-search', object_key, search_file)

class MinioSearchDownloader(SearchDownloader):

    def __init__(self, minio_client:Minio):
        self.minio_client = minio_client
    
    def download_search(self, bucket_name: str, object_key: str) -> str:
        search_path: str = os.getcwd() + "/searchs/" + object_key
        self.minio_client.fget_object(bucket_name, object_key, search_path)
        return search_path

class MinioSearchableDownloader(SearchableDownloader):

    def __init__(self, minio_client:Minio):
        self.minio_client = minio_client
    
    def download_searchable(self, bucket_name: str, object_key: str) -> str:
        searchable_path: str = os.getcwd() + "/searchable/" + object_key
        self.minio_client.fget_object(bucket_name, object_key, searchable_path)
        return searchable_path
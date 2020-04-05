from .service import OcrLister
from minio import Minio

class MinioOcrLister(OcrLister):
    
    def __init__(self, minio_client: Minio): 
        self.minio_client = minio_client
    
    def list_ocr(self, bucket_name: str) -> list:
        ocr_files = self.minio_client.list_objects(bucket_name)
        ids = [ocr.object_name for ocr in ocr_files]
        print(ids)
        return ids
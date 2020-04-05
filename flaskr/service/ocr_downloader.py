from abc import ABC, abstractmethod

class OcrDownloader(ABC):

  @abstractmethod
  def download_ocr(self, bucket_name: str, object_key: str):
    pass
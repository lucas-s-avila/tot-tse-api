from abc import ABC, abstractmethod

class OcrLister(ABC):

  @abstractmethod
  def list_ocr(self, bucket_name: str) -> list:
    pass
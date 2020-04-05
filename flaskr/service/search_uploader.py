from abc import ABC, abstractmethod

class SearchUploader(ABC):

  @abstractmethod
  def upload_search(self, bucket_name: str, file: str):
    pass
from abc import ABC, abstractmethod

class SearchDownloader(ABC):

  @abstractmethod
  def download_search(self, bucket_name: str, object_key: str) -> str:
    pass
from abc import ABC, abstractmethod

class SearchableDownloader(ABC):

  @abstractmethod
  def download_searchable(self, object_key: str, file: str) -> str:
    pass
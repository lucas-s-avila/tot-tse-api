from abc import ABC, abstractmethod

class Scheduler(ABC):
    
  @abstractmethod
  def getFilename(self, id_list: list) -> list:
    pass
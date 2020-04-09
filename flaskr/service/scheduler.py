from abc import ABC, abstractmethod

class Scheduler(ABC):
    
  @abstractmethod
  def get_filename(self, id_list: list) -> list:
    pass
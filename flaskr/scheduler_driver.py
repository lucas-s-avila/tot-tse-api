import requests

from .service import Scheduler

class SchedulerAPI(Scheduler):
  
  def __init__(self, addr: str):
    self.addr = addr

  def getFilename(self, id_list: list) -> list:
    resp = requests.get(
      self.addr + "/filenames",
      {
        'ids': ','.join(id_list)
      }
    )
    return resp.json()

from typing import List
import requests

from .ocr_lister import OcrLister

class TermSearchEngine:

  def __init__(self, scheduler_addr: str, ocr_lister: OcrLister):
    self.scheduler_addr = scheduler_addr
    self.ocr_lister = ocr_lister

  def available_ocrs(self):
    ids = self.ocr_lister.list_ocr("tot-ocr")
    print(ids)
    print({
        'ids': ','.join(ids)
    })
    resp = requests.get(
      self.scheduler_addr + '/filenames',
      {
        'ids': ','.join(ids)
      }
    )
    print(resp)
    return resp.json()

  def search_term(self, term: str) -> (str, str):
    return ("./refs.csv", "./bbox.pdf")
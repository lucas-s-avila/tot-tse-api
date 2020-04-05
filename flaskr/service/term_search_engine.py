import os
import requests
import uuid

from typing import List
from flask import json
from .ocr_lister import OcrLister
from .ocr_downloader import OcrDownloader
from .search_uploader import SearchUploader
from .search_downloader import SearchDownloader
from .search_service import SearchService

class TermSearchEngine:

  def __init__(
    self, 
    scheduler_addr: str, 
    ocr_lister: OcrLister, 
    ocr_downloader: OcrDownloader, 
    search_uploader: SearchUploader,
    search_downloader: SearchDownloader
  ):
    
    self.scheduler_addr = scheduler_addr
    self.ocr_lister = ocr_lister
    self.ocr_downloader = ocr_downloader
    
    self.search_service = SearchService()

    self.workdir = os.getcwd() + "/searchs/"
    if not os.path.isdir(self.workdir):
      os.mkdir(self.workdir)
    
    self.search_uploader = search_uploader
    self.search_downloader = search_downloader

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

  def save_search(self, search_id: uuid.UUID, file_id: str, matches: list):
    
    with open(self.workdir + str(search_id), 'a') as outfile:
      json.dumps({file_id : matches}, outfile)

  def search_term(self, term: str, ids: list):
    
    search_id = uuid.uuid4()
    
    print(ids)
    for iden in ids:
      self.ocr_downloader.download_ocr("tot-ocr", str(iden))

    def generate_result(term: str) -> str:
      for file_dict, file_path in self.search_service.search(term):
        #sched_response = json.loads(requests.get(self.scheduler_addr + '/filenames',{'ids' : file_dict['id']}))
        response_dict = {
          'search_id' : search_id,
          'file_id' : file_dict['file_id'],
          #'filename' : sched_response['filename'],
          'term' : term
        }
        matches = []
        for match in file_dict["generate_matches"]:
          response_dict['match'] = match
          matches.append(match)
          yield json.dumps(response_dict)
        self.save_search(search_id, file_dict['file_id'], matches)
        os.remove(file_path)
      #self.search_uploader.upload_search(str(search_id), self.workdir + str(search_id))
        
    return generate_result(term)
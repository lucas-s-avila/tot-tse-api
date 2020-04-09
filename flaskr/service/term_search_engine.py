import os
import requests
import uuid

from flask import json
from .ocr_lister import OcrLister
from .ocr_downloader import OcrDownloader
from .search_uploader import SearchUploader
from .search_downloader import SearchDownloader
from .searchable_dowloader import SearchableDownloader
from .scheduler import Scheduler
from .search_service import SearchService
from .highlight_service import HighlightService

class TermSearchEngine:

  def __init__(
    self, 
    scheduler: Scheduler, 
    ocr_lister: OcrLister, 
    ocr_downloader: OcrDownloader, 
    search_uploader: SearchUploader,
    search_downloader: SearchDownloader,
    searchable_dowloader: SearchableDownloader
  ):
    
    self.scheduler = scheduler
    self.ocr_lister = ocr_lister
    self.ocr_downloader = ocr_downloader
    
    self.search_service = SearchService()
    self.highlight_service = HighlightService()

    self.workdir = os.getcwd() + "/searchs/"
    if not os.path.isdir(self.workdir):
      os.mkdir(self.workdir)
    
    self.search_uploader = search_uploader
    self.search_downloader = search_downloader

    self.searchable_dowloader = searchable_dowloader

  def available_ocrs(self):
    ids = self.ocr_lister.list_ocr("tot-ocr")
    print(ids)
    print({
        'ids': ','.join(ids)
    })
    resp = self.scheduler.get_filename(ids)
    print(resp)
    return resp

  def save_search(self, search_dict: dict):
    search_id = search_dict['search_id']

    if not os.path.isfile(self.workdir+search_id):
      search_dict['matches'] = [search_dict['match']]
      del search_dict['match']
      
      with open(self.workdir+search_id, 'w') as search_file:
        json.dump([search_dict], search_file)

    else:
      with open(self.workdir+search_id, 'r') as search_file:
        search_list = json.load(search_file)
      
      found = False
      for search in search_list:
        if search['file_id'] == search_dict['file_id']:
          search['matches'].append(search_dict['match'])
          found = True

      if not found:
        search_dict['matches'] = [search_dict['match']]
        del search_dict['match']

        search_list.append(search_dict)
      
      with open(self.workdir+search_id, 'w') as search_file:
        json.dump(search_list, search_file)

    self.search_uploader.upload_search(search_id, self.workdir+search_id)

  def clean_files(self):
    self.search_service.clean_files()
    
    with os.scandir(self.workdir) as files:
      for f in files:
        os.remove(f)

  def search_term(self, term: str, ids: list):

    self.clean_files()
    
    search_id = uuid.uuid4()
    
    for iden in ids:
      self.ocr_downloader.download_ocr("tot-ocr", str(iden))

    def generate_result(term: str) -> str:
      for file_dict in self.search_service.search(term):
        print(file_dict['file_id'])
        resp = self.scheduler.get_filename([file_dict['file_id']])
        response_dict = {
          'search_id' : str(search_id),
          'file_id' : file_dict['file_id'],
          'filename' : resp[0]['filename'],
          'term' : term
        }
        for match in file_dict["generate_matches"]:
          response_dict['match'] = match
          self.save_search(response_dict)
          yield json.dumps(response_dict)
        
    return generate_result(term)
  
  def mark_words(self, id_search: str, id_file: str) -> str:
    
    search_file = self.search_downloader.download_search('tot-search', id_search)
    with open(search_file, 'r') as open_file:
      search_list = json.load(open_file)
    os.remove(search_file)

    searchable_file = self.searchable_dowloader.download_searchable('tot-pdfs', id_file)

    marked_file = self.highlight_service.highlight_words(search_list, searchable_file)

    os.remove(searchable_file)

    return marked_file
    
    

    
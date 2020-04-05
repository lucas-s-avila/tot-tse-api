import os
import distance
import re
import xml.etree.ElementTree as ET

class SearchService():

    def __init__(self, word_dist_thrs: float = 0.3):
        self.workdir = os.getcwd() + "/hocrs/"
        if not os.path.isdir(self.workdir):
            os.mkdir(self.workdir)

        self.word_dist_thrs = word_dist_thrs
    
    def find_word_in_hocr(self, hocr: ET.ElementTree, find_word: str) -> list:
        find_word = find_word.casefold()
        def generate_matches():
            pages = hocr.findall(".//*[@class='ocr_page']")
            for page_num,page in enumerate(pages):
                words = page.findall(".//*[@class='ocrx_word']")
                for word in words:
                    if word.text is not None:
                        #Faz o matching entre as palavras
                        match_dist = distance.nlevenshtein(word.text.casefold(),find_word)
                        if match_dist <= self.word_dist_thrs:
                            t=word.get("title")
                            position = re.search(r'(?<=bbox) (?P<top>\d+) (?P<left>\d+) (?P<botton>\d+) (?P<right>\d+)',t).groupdict()
                            ocr_conff = re.search(r'(?<=x_wconf )(\d+)',t).group(0)
                            match = {
                                "page_id": page.get('id'),
                                "page_num": page_num+1,
                                "word_id": word.get('id'),
                                "word": word.text,
                                "position" : {
                                    "top" : int(position['top']) ,
                                    "left" : int(position['left']) ,
                                    "botton" : int(position['botton']) ,
                                    "right" : int(position['right'])
                                },
                                "ocr_conf": int(ocr_conff) ,
                                "match_conf": 1-match_dist
                            }
                            yield match
        return generate_matches()
        
    def search(self, term: str):
        files_to_search = os.listdir(self.workdir)
        def generate_search() -> (dict, str):
            for file_name in files_to_search:
                hocr = ET.parse(self.workdir+file_name)
                generate_matches = self.find_word_in_hocr(hocr, term)
                file_result = {
                    "file_id": file_name,
                    "generate_matches": generate_matches
                }
                yield file_result, self.workdir+file_name

        return generate_search()

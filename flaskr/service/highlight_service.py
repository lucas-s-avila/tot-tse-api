import os
import PyPDF2
import pdf2image

from PIL import Image, ImageDraw
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont

class HighlightService():
  
  def __init__(self):
    self.workdir = os.getcwd() + "/marked_pdf/"
    if not os.path.isdir(self.workdir):
      os.mkdir(self.workdir)

    self.imagesdir = os.getcwd() + "/images/"
    if not os.path.isdir(self.imagesdir):
      os.mkdir(self.imagesdir)

  def get_num_pages(self, pdf: str) -> int:
    inputpdf = PyPDF2.PdfFileReader(open(pdf, "rb"))
    maxPages = inputpdf.numPages
    return maxPages

  def highlight_words(self, search_list: list, searchable_file: str) -> str:
    file_id = searchable_file.split('/')[-1]
    
    for search in search_list:
      if search['file_id'] == file_id:
        file_dict = search
        break
    
    if file_dict is None:
      print("error")
      pass

    images = []
    i=0
    num_pages = self.get_num_pages(searchable_file)
    for inital_page in range(1,num_pages+10,10):
      pages = pdf2image.convert_from_path(searchable_file,
                                          dpi=300,
                                          first_page=inital_page, 
                                          last_page = min(inital_page+10-1,num_pages),
                                          grayscale='true',
                                          fmt='png')
      for page in pages:
        page = page.convert("RGBA")
        page.save(self.imagesdir+str(i)+'.png', 'png')
        images.append(self.imagesdir+str(i)+'.png')
        i+=1
    
    for match in file_dict['matches']:
      page = match['page_num']
      bbox = [match['position']['left'], match['position']['top'], match['position']['right'], match['position']['botton']]
      print(bbox)
      image = Image.open(images[page-1])
      draw = ImageDraw.Draw(image)
      draw.rectangle(bbox, outline=(0, 255, 50))
      draw.rectangle((bbox[0]+1,bbox[1]+1, bbox[2]+1, bbox[3]+1), outline=(0, 255, 50))
      image.save(images[page-1], 'png')
    
    pdf_path = self.workdir + file_dict['filename'] + ".pdf"
    pdf = Canvas(pdf_path)
    pdf.setCreator('TotOcr')
    pdf.setTitle(file_dict['filename'])
    dpi=300

    for img_path in images:
      img = Image.open(img_path)
      w, h = img.size
      width = w * 72 / dpi
      height = h * 72 / dpi
      pdf.setPageSize((width, height))
      pdf.drawImage(img_path, 0, 0, width=width, height=height)
      img.close()
      pdf.showPage()
    pdf.save()

    with os.scandir(self.imagesdir) as files:
      for f in files:
        os.remove(f)

    return pdf_path
    
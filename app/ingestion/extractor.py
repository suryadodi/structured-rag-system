import fitz
import pdfplumber
from typing import List,Dict,Any,Optional
import os
from app.config.settings import app_settings

class PDFExtractor:
    def __init__(self):
        self.settings = app_settings

#The Text Extractor
    def extract_text(self, filepath:str):
        doc = fitz.open(filepath)
        text=""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

# The Table Extractor
    def extract_tables(self,filepath:str):
        table_data =[]
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    table_data.append({
                        "page":page_num+1,
                        "raw":table,
                        "type":"table"
                    })
        return table_data

# The Image or Graph Extractor
    
    def extract_graph(self, filepath:str):
        visuals = []
        doc = fitz.open(filepath)
        for page_num, page in enumerate(doc):
            images= page.get_images(full=True)
            for img in images:
                xref = img[0]
                pix = fitz.Pixmap(doc,xref)
                visuals.append({
                    "page":page_num+1,
                    "image_bytes":pix.tobytes("png"),
                    "type":"image"
                })
        doc.close()
        return visuals




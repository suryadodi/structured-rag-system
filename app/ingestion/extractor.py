import fitz
import pdfplumber
from typing import List,Dict,Any,Optional
import os
from openai import OpenAI
import base64
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

# summarize the table
    
    def table_summary(self, table_data:List[List[Any]])->str:
        client=OpenAI(api_key=self.settings.OPENAI_API_KEY)
        table_list = "\n".join([str(row) for row in table_data])
        response=client.chat.completions.create(
            model=self.settings.LLM_MODEL,
            messages=[{
                "role":"user",
                "content":f"summarize the key information and trends in this table from a professional document in short sentences that suits for vector db from {table_list}"
            }],
            max_tokens=self.settings.MAX_TOKENS,
        )
        return response.choices[0].message.content

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


# Image to text
  
    def image_text(self, image_bytes:bytes):
        client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        response = client.chat.completions.create(
            model=self.settings.LLM_MODEL,
            messages=[{
                "role":"user",
                "content":[
                    {
                        "type":"text",
                        "text":"Describe this image or graph in detail from a professional document in detail.if it is a chart or graph explain the trends and data points."},
                        {
                         "type":"image_url",
                         "image_url":{
                            "url":f"data:image/png;base64,{base64_image}"
                         }
                         }
                        
                    
                ]
            }
            ],
            max_tokens = self.settings.MAX_TOKENS,
            
        )
        return response.choices[0].message.content





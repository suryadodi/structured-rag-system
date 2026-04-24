import os
from app.ingestion.registry import DocumentRegistry
from app.ingestion.extractor import PDFExtractor
from app.utils.logger import get_structured_logger

logger = get_structured_logger(__name__)

class IngestionManager:

    def __init__(self):
        self.registry = DocumentRegistry()
        self.extractor = PDFExtractor()

    def document_process(self,filepath:str):
        file_hash = self.registry.generate_hash(filepath)
        filename = os.path.basename(filepath)
        if self.registry.is_processed(file_hash):
            logger.info(f"{filename} already processed, skipping." ,extra={"step":"ingestion"})
            return None
        else:
            logger.info(f"Starting ingestion for {filename}",extra={"step":"ingestion"})
            text = self.extractor.extract_text(filepath)
            raw_tables = self.extractor.extract_tables(filepath)
            table_summaries =[]
            for table in raw_tables:
                summary = self.extractor.table_summary(table['raw'])
                raw_text = "\n".join([str(row) for row in table['raw']])
                combined_content = f"Table Data:\n{raw_text}\n\nSummary:\n{summary}"
                table_summaries.append({
                    "content":combined_content,
                    "metadata":{
                        "type":"table",
                        "page":table['page']
                    }
                })
            images_data = self.extractor.extract_graph(filepath)
            image_summaries =[]
            for image in images_data:
                image_summary =self.extractor.image_text(image["image_bytes"])
                image_summaries.append({
                    "content":image_summary,
                    "metadata":{
                        "type":"image",
                        "page":image['page']
                    }

                })
            self.registry.mark_processed(file_hash,filename)
            logger.info(f"Successfully processed {filename}",extra={"step":"ingestion"})
            return{
            "text":text,
            "tables":table_summaries,
            "images":image_summaries
        }
    
        

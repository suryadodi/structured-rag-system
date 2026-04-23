import os
from app.utils.logger import get_structured_logger
from app.config.settings import app_settings
from app.ingestion.chunker import TextChunker
from app.vectorstore.pineconestore import PineconeStore
from app.ingestion.manager import IngestionManager
from app.ingestion.embedder import Embedder
from app.retrieval.bm25_retriever import BM25Retriever

logger = get_structured_logger(__name__)

class IngestionPipeline:
    def __init__(self):
        self.chunker= TextChunker()
        self.vectorstore = PineconeStore()
        self.embedder = Embedder()
        self.manager = IngestionManager()
        self.bm25 = BM25Retriever()

    def ingest_document(self,file_path:str):
        filename=os.path.basename(file_path)
        logger.info(f"Starting ingestion for {filename}",extra={"step":"ingestion"})
        doc_data= self.manager.document_process(file_path)
        if doc_data is None:
            return None

# chunking the data
        chunks = self.chunker.chunk_documents(doc_data,filename)
        logger.info(f"Chunked {len(chunks)} chunks from {filename}",extra={"step":"chunking"})
#embeded the data
        embedded = self.embedder.embedded_chunks(chunks)
#upload to pinecone
        self.vectorstore.upsert(embedded)
        logger.info(f"Uploaded {len(embedded)} vectors to Pinecone",extra={"step":"vectorstore"})

        # Add to BM25 Index
        self.bm25.add_documents(chunks)
        
        return {
            "status":"success",
            "filename":filename,
            "chunks":len(chunks),
            "vectors":len(embedded)
        }



import os
import shutil
from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.pipeline.ingest_pipeline import IngestionPipeline
from app.pipeline.query_pipeline import QueryPipeline
from app.utils.logger import get_structured_logger
from app.config.settings import app_settings

logger = get_structured_logger(__name__)

app=FastAPI(title = "RAG PIPELINE API",version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

ingest_pipeline = IngestionPipeline()
query_pipeline = QueryPipeline()

class QueryRequest(BaseModel):
    question: str

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    # Check file type — only PDFs allowed
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Read file content to check size
    content = await file.read()
    max_bytes = app_settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max size is {app_settings.MAX_FILE_SIZE_MB}MB.")

    # Save to temp file and process
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(content)
    result = ingest_pipeline.ingest_document(temp_path)
    os.remove(temp_path)
    return result

@app.post("/query")
async def query(request: QueryRequest):
    return query_pipeline.query(request.question)

@app.delete("/clear")
async def clear():
    # Delete all vectors from Pinecone
    ingest_pipeline.vectorstore.index.delete(delete_all=True)
    
    if os.path.exists("document_registry.db"):
        os.remove("document_registry.db")
    logger.info("Cleared all vectors and reset registry", extra={"step": "system"})
    return {"status": "success", "message": "All vectors deleted and registry reset"}

import os
import shutil
from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.pipeline.ingest_pipeline import IngestionPipeline
from app.pipeline.query_pipeline import QueryPipeline
from app.utils.logger import get_structured_logger

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
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = ingest_pipeline.ingest_document(temp_path)
    os.remove(temp_path)
    return result

@app.post("/query")
async def query(request: QueryRequest):
    return query_pipeline.query(request.question)

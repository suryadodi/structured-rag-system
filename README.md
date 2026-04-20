# Basic_Rag_Pipeline
RAG System Overview

This project implements a modular, production-style Retrieval-Augmented Generation (RAG) pipeline designed for structured document understanding and high-quality question answering.

The system begins with an ingestion pipeline that parses PDFs and segments them into meaningful units such as paragraphs, tables, and images using structure-aware chunking with overlap to preserve context across boundaries. Each segment is processed based on its type—cleaning text, summarizing tables, and applying OCR for images—to ensure all data is suitable for language model consumption.

Embeddings are generated using OpenAI models and stored in a vector database such as ChromaDB for rapid prototyping, with a clear migration path to Qdrant for production-scale deployments. At query time, the system performs hybrid retrieval by combining dense vector search with sparse methods (BM25), followed by reranking using cross-encoders to improve relevance. Retrieved chunks are carefully ordered and assembled into a coherent context before being passed to the LLM for grounded response generation.

The system uses structured outputs (function calling) to return both answers and their corresponding source references, enabling transparent citations and traceability. To ensure continuous improvement, an evaluation layer tracks key metrics such as retrieval recall@k and answer faithfulness.

For observability, the pipeline implements structured logging using Python’s logging module with plain-text log rotation capturing each stage of the pipeline, including ingestion, chunking, retrieval, reranking, and generation. Additionally, pipeline runs can be streamed to Google Sheets for lightweight monitoring without requiring additional infrastructure, enabling step-by-step tracking of execution status, latency, and retrieval quality.

Designed to be cloned, extended, and understood — not just run.
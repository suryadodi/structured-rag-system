# My Hybrid RAG Pipeline

I built this project to be a production-ready RAG system that handles document understanding and high-quality answering. Most basic RAG systems fail when you need to find exact information (like names or IDs); this one solves that by using a "Two-Stage" retrieval process.

The system is built on FastAPI, Pinecone, and OpenAI, with a focus on speed, modularity, and transparency.

---

## The Tech Stack
*   LLM: OpenAI GPT-4o (The generator)
*   Vector Search: Pinecone (Dense retrieval for semantic meaning)
*   Keyword Search: BM25 (Sparse retrieval for exact word matching)
*   Refinement: Flashrank (A local cross-encoder that reranks results for high accuracy)
*   Framework: FastAPI (For the REST API)
*   Parsing: PyMuPDF + pdfplumber (Multi-layer PDF extraction)

---

## Setting things up
1.  Environment: Create a venv and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2.  Install: Pull in all the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
3.  Config: Rename .env.example to .env and put in your keys for OpenAI and Pinecone.
4.  Run: Start the server with uvicorn:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

---

## Testing in the browser (Swagger UI)
Go to http://127.0.0.1:8000/docs once the server is running. Here is the workflow:

1.  POST /ingest: Upload your PDF here. The pipeline will extract text, tables, and images. It creates textual summaries for visuals, chunks the data with overlap, and stores it in both Pinecone (for vectors) and a local BM25 index (for keywords).
2.  POST /query: Ask your question. The system will:
    *   Find the top 10 vector matches.
    *   Find the top 10 keyword matches.
    *   Merge them using RRF (Reciprocal Rank Fusion).
    *   Rerank the top 20 candidates using Flashrank to pick the absolute best 5.
    *   Generate a grounded answer with GPT-4o.
3.  DELETE /clear: Use this to wipe the database and registry if you want a fresh start.

---

## Why this architecture?
*   Hybrid Retrieval: By combining Pinecone and BM25, we catch both conceptual matches and exact phrase matches. 
*   RRF Fusion: This is a robust way to merge different rankers without having to manually tune weights.
*   Cross-Encoder Reranking: This is the "high-fidelity" step. It’s slower than vector search but much more accurate because it reads the question and document together.
*   Observability: Every stage (ingest, chunk, retrieval, generation) is logged with its duration and status for debugging.
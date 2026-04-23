from openai import OpenAI
from app.vectorstore.pineconestore import PineconeStore
from app.ingestion.embedder import Embedder
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.rrf_fusion import RRFFusion
from app.utils.logger import get_structured_logger
from app.config.settings import app_settings

logger = get_structured_logger(__name__)

class QueryPipeline:
    def __init__(self):
        self.vectorstore = PineconeStore()
        self.embedder = Embedder()
        self.client = OpenAI(api_key=app_settings.OPENAI_API_KEY)
        self.bm25 = BM25Retriever()
        self.rrf = RRFFusion()

    def query(self, question: str):
        # Step 1: Log the incoming question
        logger.info(f"Received question: {question}", extra={"step": "query"})

        # Step 2: Convert the question into 1536 numbers
        query_embedding = self.embedder.embed_query(question)

        # Step 3: Hybrid Search (Dense + Sparse)
        # Search Pinecone (Dense)
        vector_results = self.vectorstore.search_vector(query_embedding, top_k=10)
        
        # Search BM25 (Sparse)
        bm25_results = self.bm25.search(question, top_k=10)
        
        # Step 4: Fusion using RRF
        results = self.rrf.fuse(vector_results, bm25_results, top_n=app_settings.TOP_K)
        logger.info(f"Hybrid retrieval finished. Using top {len(results)} fused results.", extra={"step": "query"})

        # Step 5: Build context from the fused results
        context_parts = []
        for r in results:
            source = r["metadata"].get("source", "unknown")
            content = r["metadata"].get("content", "")
            context_parts.append(f"Source: {source}\n{content}")
        context = "\n\n".join(context_parts)

        # Step 6: Send context + question to GPT-4o and get the answer
        response = self.client.chat.completions.create(
            model=app_settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer using only the context provided. Do not make up information."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        )
        answer = response.choices[0].message.content
        logger.info(f"Answer: {answer[:300]}...", extra={"step": "query"})

        # Step 6: Return the answer + which files it came from (citations)
        return {
            "answer": answer,
            "sources": list(set([r["metadata"].get("source") for r in results]))
        }


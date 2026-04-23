from openai import OpenAI
from app.vectorstore.pineconestore import PineconeStore
from app.ingestion.embedder import Embedder
from app.utils.logger import get_structured_logger
from app.config.settings import app_settings

logger = get_structured_logger(__name__)

class QueryPipeline:
    def __init__(self):
        self.vectorstore = PineconeStore()
        self.embedder = Embedder()
        self.client = OpenAI(api_key=app_settings.OPENAI_API_KEY)

    def query(self, question: str):
        # Step 1: Log the incoming question
        logger.info(f"Received question: {question}", extra={"step": "query"})

        # Step 2: Convert the question into 1536 numbers
        query_embedding = self.embedder.embed_query(question)

        # Step 3: Search Pinecone for the top 5 most relevant chunks
        results = self.vectorstore.search_vector(query_embedding)
        logger.info(f"Found {len(results)} relevant chunks", extra={"step": "query"})

        # Step 4: Build context from the results
        context_parts = []
        for r in results:
            source = r.metadata.get("source", "unknown")
            content = r.metadata.get("content", "")
            context_parts.append(f"Source: {source}\n{content}")
        context = "\n\n".join(context_parts)

        # Step 5: Send context + question to GPT-4o and get the answer
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
            "sources": [r.metadata.get("source") for r in results]
        }


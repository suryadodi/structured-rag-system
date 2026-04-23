import time
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from app.utils.logger import get_structured_logger
from app.config.settings import app_settings

logger = get_structured_logger(__name__)

class Embedder:
    def __init__(self):
        self.client = OpenAI(api_key=app_settings.OPENAI_API_KEY)
        self.model = app_settings.EMBEDDING_MODEL
        self.batch_size = app_settings.EMBEDDING_BATCH_SIZE

    def embedded_chunks(self, chunks: list[dict]) -> list[dict]:
        embedded_chunks = []
        for batch_start in range(0, len(chunks), self.batch_size):
            batch = chunks[batch_start:batch_start+self.batch_size]
            texts = [chunk["content"][:30000] for chunk in batch]
            
            start_time = time.time()
            # Wrap the actual API call in our retry logic
            response = self._get_embeddings_with_retry(texts)
            duration_ms = round((time.time() - start_time) * 1000)
            
            logger.info(f"Embedded {len(texts)} chunks in {duration_ms}ms", extra={"step": "embedding"})
            
            for i, embedding_object in enumerate(response.data):
                chunk = batch[i]
                chunk["embedding"] = embedding_object.embedding
                embedded_chunks.append(chunk)
        return embedded_chunks

    def embed_query(self, text: str) -> list[float]:
        # Reuse the retry logic for queries too
        response = self._get_embeddings_with_retry([text])
        return response.data[0].embedding

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def _get_embeddings_with_retry(self, input_texts: list[str]):
        """Internal method to handle OpenAI calls with automatic retries."""
        return self.client.embeddings.create(
            model=self.model,
            input=input_texts
        )
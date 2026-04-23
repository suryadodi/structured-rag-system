from pinecone import Pinecone,ServerlessSpec
from app.utils.logger import get_structured_logger
from app.config.settings import app_settings

logger=get_structured_logger(__name__)

class PineconeStore:
    def __init__(self):
       self.pinecone=Pinecone(api_key=app_settings.PINECONE_API_KEY)
       self.index_name=app_settings.PINECONE_INDEX_NAME
       self.index=self.get_or_create_index()

    def get_or_create_index(self):
        existing_indexes = self.pinecone.list_indexes().names()
        if self.index_name not in existing_indexes:
            self.pinecone.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            logger.info(f"Created new Pinecone index: {self.index_name}", extra={"step": "vectorstore"})
        return self.pinecone.Index(self.index_name)
# upsert the vectors to pincone
    def upsert(self, embedded_chunks:list[dict]):
        vectors = []
        for chunk in embedded_chunks:
            vectors.append({
                "id":chunk["chunk_id"],
                "values":chunk["embedding"],
                "metadata":chunk["metadata"]
            })
        self.index.upsert(vectors=vectors)
        logger.info(f"Upserted {len(vectors)} vectors to Pinecone", extra={"step": "vectorstore"})

# search the vectors in pinecone
    def search_vector(self,query_embedding:list[float],top_k:int=None):
        if top_k is None:
            top_k = app_settings.TOP_K
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        logger.info(f"Query returned {len(results.matches)} results for query", extra={"step": "vectorstore"})
        return results.matches
        
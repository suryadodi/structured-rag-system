import pickle
import os
from rank_bm25 import BM25Okapi
from app.utils.logger import get_structured_logger

logger = get_structured_logger(__name__)

class BM25Retriever:
    def __init__(self, index_path: str = "bm25_index.pkl"):
        self.index_path = index_path
        self.corpus = []      # The raw text chunks
        self.metadata = []    # The metadata dicts for each chunk
        self.bm25 = None      # The actual BM25 engine
        self._load_index()

    def _tokenize(self, text: str):
        # Simple lowercased word tokenization
        return text.lower().split()

    def _load_index(self):
        """Loads the BM25 index from disk if it exists."""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    self.corpus = data["corpus"]
                    self.metadata = data["metadata"]
                    # Re-initialize BM25 with the loaded corpus
                    tokenized_corpus = [self._tokenize(doc) for doc in self.corpus]
                    self.bm25 = BM25Okapi(tokenized_corpus)
                logger.info(f"Loaded BM25 index with {len(self.corpus)} documents", extra={"step": "retrieval"})
            except Exception as e:
                logger.error(f"Failed to load BM25 index: {e}", extra={"step": "retrieval"})

    def save_index(self):
        """Persists the index to disk."""
        with open(self.index_path, "wb") as f:
            pickle.dump({"corpus": self.corpus, "metadata": self.metadata}, f)

    def add_documents(self, chunks: list[dict]):
        """Adds new chunks to the BM25 index."""
        new_texts = [c["content"] for c in chunks]
        new_metadata = [c["metadata"] for c in chunks]
        
        self.corpus.extend(new_texts)
        self.metadata.extend(new_metadata)
        
        # Completely rebuild the BM25 engine (BM25 doesn't support incremental updates)
        tokenized_corpus = [self._tokenize(doc) for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"Rebuilt BM25 index. Total documents: {len(self.corpus)}", extra={"step": "retrieval"})
        self.save_index()

    def search(self, query: str, top_k: int = 10):
        """Performs a keyword search and returns top_k results."""
        if not self.bm25 or not self.corpus:
            return []
            
        tokenized_query = self._tokenize(query)
        # Get scores for all documents
        scores = self.bm25.get_scores(tokenized_query)
        
        # Sort by score descending and take top_k
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for i in top_indices:
            if scores[i] > 0: # Only return valid matches
                results.append({
                    "content": self.corpus[i],
                    "metadata": self.metadata[i],
                    "score": float(scores[i])
                })
        return results

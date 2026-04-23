from app.utils.logger import get_structured_logger

logger = get_structured_logger(__name__)

class RRFFusion:
    def __init__(self, k: int = 60):
        # k is a smoothing constant, 60 is the industry standard for RRF
        self.k = k

    def fuse(self, vector_results: list, bm25_results: list, top_n: int = 5):
        """
        Merges two lists of results using Reciprocal Rank Fusion.
        vector_results: list of Pinecone matches
        bm25_results: list of BM25 matches
        """
        scores = {}  # {chunk_content: score}
        metadata_map = {} # {chunk_content: metadata}

        # 1. Score the vector results
        for rank, res in enumerate(vector_results):
            content = res.metadata.get("content", "")
            if not content: continue
            
            # RRF Formula: 1 / (rank + k)
            score = 1.0 / (rank + self.k)
            scores[content] = scores.get(content, 0) + score
            metadata_map[content] = res.metadata

        # 2. Score the BM25 results
        for rank, res in enumerate(bm25_results):
            content = res["content"]
            if not content: continue
            
            score = 1.0 / (rank + self.k)
            scores[content] = scores.get(content, 0) + score
            if content not in metadata_map:
                metadata_map[content] = res["metadata"]

        # 3. Sort by fused score and take top_n
        sorted_content = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

        fused_results = []
        for content, score in sorted_content:
            fused_results.append({
                "content": content,
                "metadata": metadata_map[content],
                "rrf_score": score
            })

        logger.info(f"Fused {len(vector_results)} dense and {len(bm25_results)} sparse results into {len(fused_results)} top hits", extra={"step": "retrieval"})
        return fused_results

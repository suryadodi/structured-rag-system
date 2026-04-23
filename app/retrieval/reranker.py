from flashrank import Ranker, RerankRequest
from app.utils.logger import get_structured_logger

logger = get_structured_logger(__name__)

class DocumentReranker:
    def __init__(self, model_name: str = "ms-marco-MiniLM-L-12-v2"):
        # This will download the model once (~30MB)
        self.ranker = Ranker(model_name=model_name, cache_dir="/tmp")

    def rerank(self, query: str, fused_results: list, top_n: int = 5):
        """
        Reranks the fused results using a cross-encoder model.
        fused_results: list of dicts with 'content' and 'metadata'
        """
        if not fused_results:
            return []

        # Prepare formatting for Flashrank
        passages = []
        for i, res in enumerate(fused_results):
            passages.append({
                "id": i,
                "text": res["content"],
                "meta": res["metadata"]
            })

        # Run Reranking
        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)

        # Truncate to top_n
        top_results = results[:top_n]

        # Format back to our standard structure
        final_results = []
        for r in top_results:
            final_results.append({
                "content": r["text"],
                "metadata": r["meta"],
                "rerank_score": float(r["score"])
            })

        logger.info(f"Reranked {len(fused_results)} documents into {len(final_results)} final results", extra={"step": "retrieval"})
        return final_results

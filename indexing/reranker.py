from indexing.dense.embedding_model import detect_device

class CrossEncoderReranker:
    """Rerank top-N kết quả sau RRF bằng Cross-Encoder."""
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        from sentence_transformers import CrossEncoder
        self.device = detect_device()
        self.model = CrossEncoder(model_name, device=self.device)
    
    def rerank(self, query: str, candidates: list[dict], top_k: int = 3) -> list[tuple[dict, float]]:
        """
        Rerank candidates based on query.
        Trả về list of tuples (document_dict, rerank_score)
        """
        if not candidates:
            return []
            
        pairs = [(query, doc["content"]) for doc in candidates]
        scores = self.model.predict(pairs)
        
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

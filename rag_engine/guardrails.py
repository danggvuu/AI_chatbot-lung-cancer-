class Guardrails:
    def __init__(self, settings=None):
        self.settings = settings or {}
        # Các ngưỡng an toàn
        self.min_retrieval_score = self.settings.get("guardrails", {}).get("min_retrieval_score", 1.0)
        
    def should_abstain(self, retrieved_docs: list[dict]) -> bool:
        """Kiểm tra xem hệ thống có nên từ chối trả lời do thiếu thông tin không."""
        if not retrieved_docs:
            return True
            
        # Kiểm tra điểm số của chunk tốt nhất (nếu có rerank)
        best_doc = retrieved_docs[0]
        score = best_doc.get("rerank_score") or best_doc.get("rrf_score", 0)
        
        # Vì reranker (ms-marco) score có thể âm, rrf score thì dương nhỏ
        # Để đơn giản, ta chỉ abstain nếu KHÔNG có doc nào (đã check ở trên).
        # Nếu áp dụng reranker, ta có thể set threshold riêng.
        if "rerank_score" in best_doc:
            if score < -5.0: # Threshold cho cross-encoder
                return True
                
        return False
        
    def get_abstention_message(self) -> str:
        return (
            "Dựa trên cơ sở dữ liệu hiện tại, tôi không có đủ thông tin y khoa chính thống "
            "để trả lời câu hỏi này. Vui lòng tham khảo ý kiến trực tiếp từ bác sĩ chuyên khoa "
            "hoặc tái khám tại bệnh viện để được tư vấn chính xác nhất."
        )

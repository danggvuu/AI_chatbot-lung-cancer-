import re

class CitationChecker:
    def validate_citations(self, response_text: str, retrieved_docs: list[dict]) -> dict:
        """
        Kiểm tra xem các trích dẫn [ID] trong câu trả lời có thực sự khớp với doc_ids được cung cấp không.
        Nếu phát hiện hallucination (trích dẫn ID không tồn tại), trả về flag cảnh báo.
        Đồng thời, trích xuất danh sách các nguồn hợp lệ đã được LLM sử dụng.
        """
        valid_ids = {str(doc["id"]) for doc in retrieved_docs}
        
        # Tìm tất cả các dạng [id] hoặc [id1, id2] trong text
        # Regex tìm các cụm trong ngoặc vuông chứa số
        citations = re.findall(r'\[([\d,\s]+)\]', response_text)
        
        used_ids = set()
        hallucinated_ids = set()
        
        for citation in citations:
            # Tách các ID nếu có dấu phẩy
            ids = [i.strip() for i in citation.split(",")]
            for i in ids:
                if i.isdigit():
                    if i in valid_ids:
                        used_ids.add(int(i))
                    else:
                        hallucinated_ids.add(int(i))
                        
        used_sources = [doc for doc in retrieved_docs if doc["id"] in used_ids]
        
        # Sửa lại text nếu có hallucination citation bằng cách xóa chúng đi (tùy chọn)
        clean_text = response_text
        if hallucinated_ids:
            for hid in hallucinated_ids:
                clean_text = clean_text.replace(f"[{hid}]", "")
                # Clean up empty brackets like [] hoặc [, ]
                clean_text = re.sub(r'\[[\s,]*\]', '', clean_text)
                
        return {
            "has_hallucination": len(hallucinated_ids) > 0,
            "hallucinated_ids": list(hallucinated_ids),
            "used_sources": used_sources,
            "clean_text": clean_text
        }

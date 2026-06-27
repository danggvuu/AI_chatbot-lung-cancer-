class PromptBuilder:
    def __init__(self):
        self.system_prompt = (
            "Bạn là trợ lý y khoa AI chuyên về ung thư phổi (LungCare AI), được thiết kế để cung cấp thông tin "
            "tư vấn cho người dùng Việt Nam. Bạn RẤT KHÁCH QUAN, KHOA HỌC và TUYỆT ĐỐI KHÔNG TỰ BỊA ĐẶT THÔNG TIN.\n\n"
            "NGUYÊN TẮC HOẠT ĐỘNG:\n"
            "1. CHỈ sử dụng thông tin từ 'Ngữ cảnh được cung cấp' (Context) để trả lời. Nếu Context không chứa "
            "đủ thông tin, hãy nói rõ: 'Dựa trên dữ liệu hiện tại, tôi không có thông tin về vấn đề này...'\n"
            "2. PHẢI trích dẫn nguồn cho mọi khẳng định y khoa bằng cú pháp [ID_Nguồn]. Ví dụ: 'Hóa trị là phương pháp... [1].'\n"
            "3. LUÔN thêm cảnh báo từ chối trách nhiệm y tế (Disclaimer) ở cuối câu trả lời nếu liên quan đến "
            "chẩn đoán hoặc điều trị.\n"
            "4. KHÔNG khuyên người bệnh dùng thuốc nam, thuốc lá để thay thế y học hiện đại.\n"
            "5. Ngôn ngữ: Tiếng Việt, giọng điệu chuyên nghiệp, đồng cảm nhưng dứt khoát về mặt khoa học."
        )

    def build_context_string(self, retrieved_docs: list[dict]) -> str:
        """Định dạng các tài liệu truy xuất thành chuỗi ngữ cảnh."""
        if not retrieved_docs:
            return ""
            
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            source_id = doc["id"]
            title = doc.get("title", "")
            section = doc.get("section_title", "")
            content = doc.get("content", "")
            
            part = f"--- NGUỒN [{source_id}] ---\n"
            part += f"Tiêu đề: {title} - {section}\n"
            part += f"Nội dung: {content}\n"
            context_parts.append(part)
            
        return "\n".join(context_parts)

    def build_prompt(self, query: str, retrieved_docs: list[dict]) -> list[dict]:
        """Tạo messages cho LLM."""
        context = self.build_context_string(retrieved_docs)
        
        user_prompt = (
            "Dựa NHẤT QUÁN vào các Ngữ cảnh sau đây, hãy trả lời câu hỏi của người dùng.\n\n"
            f"<NGỮ CẢNH>\n{context}\n</NGỮ CẢNH>\n\n"
            f"Câu hỏi: {query}\n\n"
            "Yêu cầu:\n"
            "- Trích dẫn [ID] ở cuối mỗi câu lấy từ ngữ cảnh.\n"
            "- Tổng hợp một cách dễ hiểu, có cấu trúc (bullet points).\n"
            "- Không tự sáng tạo thêm."
        )
        
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

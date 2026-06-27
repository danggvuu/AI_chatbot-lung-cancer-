import re

class NoiseFilter:
    def __init__(self):
        # Từ khóa thường xuất hiện trong footer, menu, quảng cáo
        self.noise_keywords = [
            "trang chủ", "giới thiệu", "liên hệ", "đặt lịch khám", 
            "tư vấn trực tuyến", "tổng đài", "hotline", "bản quyền thuộc về", 
            "chính sách bảo mật", "điều khoản sử dụng", "bài viết liên quan",
            "xem thêm", "đăng ký khám", "tải ứng dụng", "tin tức", "sự kiện",
            "chuyên khoa", "bác sĩ", "câu hỏi thường gặp", "đăng ký ngay"
        ]

    def is_noise(self, text: str) -> bool:
        """
        Kiểm tra xem text có phải là noise (menu, footer) hay không.
        Nếu tỷ lệ từ khóa noise quá cao, hoặc text quá ngắn, coi là noise.
        """
        if not text or len(text) < 50:
            return True
            
        lower_text = text.lower()
        noise_count = sum(1 for kw in self.noise_keywords if kw in lower_text)
        
        # Nếu có quá nhiều từ khóa quảng cáo/menu trong một đoạn ngắn, đó là noise
        if noise_count >= 3 and len(text) < 300:
            return True
            
        return False

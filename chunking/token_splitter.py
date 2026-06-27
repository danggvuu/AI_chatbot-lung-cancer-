import re

class TokenSplitter:
    def __init__(self, max_tokens=384, overlap_tokens=50, min_chunk_length=100):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.min_chunk_length = min_chunk_length
        # Đơn giản hóa: đếm từ thay vì đếm token chính xác của BPE để chạy nhanh hơn
        # Với tiếng Việt, 1 word ~ 1.5 token BPE. Ta sẽ dùng hệ số này.
        self.words_per_token_est = 1.3
        self.max_words = int(self.max_tokens / self.words_per_token_est)
        self.overlap_words = int(self.overlap_tokens / self.words_per_token_est)

    def split_text(self, text: str) -> list[str]:
        """Tách văn bản dựa trên ranh giới câu, giới hạn độ dài chunk."""
        if not text or len(text) < self.min_chunk_length:
            return [text] if text else []

        # Tách thành các câu (sentences)
        sentences = re.split(r'(?<=[.!?。])\s+', text)
        
        chunks = []
        current_chunk = []
        current_words = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # Nếu thêm câu này vào chunk hiện tại sẽ vượt quá max_words
            if current_words + sentence_words > self.max_words and current_chunk:
                chunks.append(" ".join(current_chunk))
                
                # Bắt đầu chunk mới với overlap
                # Lấy N từ cuối cùng của chunk trước làm overlap
                overlap_text = " ".join(current_chunk)[-self.overlap_words*5:] # ~5 ký tự/từ
                # Tìm ranh giới từ để không cắt ngang từ
                if " " in overlap_text:
                    overlap_text = overlap_text[overlap_text.find(" ")+1:]
                
                current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                current_words = len(overlap_text.split()) + sentence_words
            else:
                current_chunk.append(sentence)
                current_words += sentence_words
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        # Lọc chunk quá ngắn
        return [c for c in chunks if len(c) >= self.min_chunk_length]

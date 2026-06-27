class ChunkValidator:
    def __init__(self, min_length=100, max_tokens=384):
        self.min_length = min_length
        # Dùng hệ số chuyển đổi tương tự TokenSplitter
        self.max_words = int(max_tokens / 1.3) + 20 # allowance

    def validate(self, chunks: list[dict]) -> list[dict]:
        """Kiểm tra tính hợp lệ của danh sách chunk."""
        valid_chunks = []
        seen_ids = set()
        
        for chunk in chunks:
            # Check mandatory fields
            if not all(k in chunk for k in ["source", "url", "title", "content", "id"]):
                print(f"⚠️ Chunk thiếu trường bắt buộc: {chunk.get('id', 'Unknown')}")
                continue
                
            # Check ID uniqueness
            if chunk["id"] in seen_ids:
                print(f"⚠️ Chunk trùng ID: {chunk['id']}")
                continue
            seen_ids.add(chunk["id"])
            
            # Check content length
            content = chunk["content"]
            if len(content) < self.min_length:
                print(f"⚠️ Chunk quá ngắn (ID {chunk['id']}): {len(content)} chars")
                continue
                
            word_count = len(content.split())
            if word_count > self.max_words:
                print(f"⚠️ Chunk quá dài (ID {chunk['id']}): {word_count} words")
                continue
                
            valid_chunks.append(chunk)
            
        return valid_chunks

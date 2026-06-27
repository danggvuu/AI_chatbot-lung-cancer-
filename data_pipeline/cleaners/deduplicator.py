class Deduplicator:
    def __init__(self, similarity_threshold=0.85):
        self.threshold = similarity_threshold
        
    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0

    def get_shingles(self, text: str, k: int = 5) -> set:
        words = text.lower().split()
        return set(tuple(words[i:i+k]) for i in range(len(words) - k + 1))

    def is_duplicate(self, text: str, existing_texts: list[str]) -> bool:
        """Kiểm tra xem text có bị trùng lặp nhiều với các text đã có không."""
        if not text:
            return True
            
        text_shingles = self.get_shingles(text)
        if not text_shingles:
            return False
            
        for existing in existing_texts:
            existing_shingles = self.get_shingles(existing)
            sim = self._jaccard_similarity(text_shingles, existing_shingles)
            if sim > self.threshold:
                return True
                
        return False

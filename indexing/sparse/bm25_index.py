import math
from collections import Counter
from .vi_tokenizer import tokenize

class BM25Index:
    def __init__(self, k1=1.5, b=0.75, title_weight=2.5, section_title_weight=1.5, content_weight=1.0, min_score=1.0):
        self.k1 = k1
        self.b = b
        self.title_weight = title_weight
        self.section_title_weight = section_title_weight
        self.content_weight = content_weight
        self.min_score = min_score
        
        self.documents = []
        self.doc_tokens = []
        self.vocab = set()
        self.doc_freqs = Counter()
        self.N = 0
        self.avg_doc_len = 0.0

    def fit(self, documents: list[dict]):
        """Xây dựng BM25 index."""
        self.documents = documents
        self.N = len(documents)
        
        self.doc_tokens = []
        total_len = 0
        
        for doc in documents:
            # Gộp text để tokenize một lần cho việc đếm chiều dài và tần suất
            full_text = f"{doc.get('title', '')} {doc.get('section_title', '')} {doc.get('content', '')}"
            tokens = tokenize(full_text)
            self.doc_tokens.append(tokens)
            
            total_len += len(tokens)
            for token in set(tokens):
                self.doc_freqs[token] += 1
                self.vocab.add(token)
                
        self.avg_doc_len = total_len / self.N if self.N > 0 else 0.0

    def search(self, query: str, top_k: int = 10) -> list:
        """Tìm kiếm BM25 với trọng số."""
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        unique_query_tokens = list(set(query_tokens))
        # Yêu cầu khớp tối thiểu 50% số từ khóa trong query
        min_match = max(1, math.ceil(len(unique_query_tokens) * 0.5))
        
        scores = []
        for i, doc in enumerate(self.doc_tokens):
            score = 0.0
            doc_len = len(doc)
            if doc_len == 0:
                continue

            doc_counter = Counter(doc)
            
            # Tính toán trọng số theo từng field
            title_tokens = tokenize(self.documents[i].get('title', ''))
            section_tokens = tokenize(self.documents[i].get('section_title', ''))
            content_tokens = tokenize(self.documents[i].get('content', ''))
            
            matched_tokens_count = 0

            for token in unique_query_tokens:
                in_title = token in title_tokens
                in_section = token in section_tokens
                in_content = token in content_tokens

                if in_title or in_section or in_content:
                    matched_tokens_count += 1
                    if token in self.vocab:
                        df = self.doc_freqs[token]
                        idf = math.log((self.N + 1) / (df + 0.5)) + 1

                        tf = doc_counter[token]
                        base_score = idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len)))
                        
                        # Cộng điểm trọng số
                        weight = 0
                        if in_title: weight += self.title_weight
                        if in_section: weight += self.section_title_weight
                        if in_content: weight += self.content_weight
                        
                        score += base_score * weight

            if matched_tokens_count >= min_match and score >= self.min_score:
                scores.append((self.documents[i]["id"], score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

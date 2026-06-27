import re
from underthesea import word_tokenize
from .stopwords_vi import VIETNAMESE_STOPWORDS

def tokenize(text: str) -> list:
    """Tách từ tiếng Việt bằng underthesea, loại bỏ stopwords."""
    if not text:
        return []
    text = text.lower()
    segmented = word_tokenize(text, format="text")
    segmented = re.sub(r'[^\w\s]', ' ', segmented)
    tokens = [word for word in segmented.split() if word]
    return [t for t in tokens if t not in VIETNAMESE_STOPWORDS]

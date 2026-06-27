import torch
from sentence_transformers import SentenceTransformer

def detect_device() -> str:
    """Tự động phát hiện GPU tốt nhất có sẵn trên máy."""
    try:
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"       # Apple Silicon
        if torch.cuda.is_available():
            return "cuda"      # NVIDIA GPU
    except Exception:
        pass
    return "cpu"

class EmbeddingModel:
    def __init__(self, model_name: str = "bkai-foundation-models/vietnamese-bi-encoder"):
        self.device = detect_device()
        self.model = SentenceTransformer(model_name, device=self.device)
        
    def encode(self, texts: list[str]) -> list[list[float]]:
        # Chuyển numpy array thành list of lists
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

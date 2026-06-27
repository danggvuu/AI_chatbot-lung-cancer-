import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

class QdrantStore:
    def __init__(self, db_path="data/qdrant_db", collection_name="lung_chunks", min_score=0.5):
        os.makedirs(db_path, exist_ok=True)
        try:
            self.client = QdrantClient(path=db_path)
        except Exception as e:
            if "already accessed by another instance" in str(e):
                raise RuntimeError(
                    f"\n[LỖI NGHIÊM TRỌNG] Không thể mở CSDL Qdrant tại '{db_path}'.\n"
                    "Cơ sở dữ liệu đang bị khóa bởi một process khác.\n"
                    "Cách khắc phục:\n"
                    "1. Đảm bảo bạn không chạy uvicorn với workers > 1 hoặc reload=True.\n"
                    "2. Tắt các process server đang chạy ngầm.\n"
                    "3. Xoá file '.lock' trong thư mục 'data/qdrant_db' nếu bạn chắc chắn không có process nào đang chạy.\n"
                    f"Chi tiết lỗi gốc: {e}"
                ) from e
            raise
            
        self.collection_name = collection_name
        self.min_score = min_score

    def init_collection(self, vector_size: int, recreate: bool = False):
        """Khởi tạo collection nếu chưa có, hoặc xóa cũ tạo mới nếu recreate=True."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if recreate and exists:
            self.client.delete_collection(self.collection_name)
            exists = False
            
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            
    def get_count(self) -> int:
        if not self._collection_exists():
            return 0
        info = self.client.get_collection(self.collection_name)
        return info.points_count

    def _collection_exists(self) -> bool:
        collections = self.client.get_collections().collections
        return any(c.name == self.collection_name for c in collections)

    def upsert_batch(self, points_data: list[dict]):
        """
        points_data = [{"id": int, "vector": list[float], "payload": dict}]
        """
        points = [
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload=p["payload"]
            ) for p in points_data
        ]
        
        batch_size = 64
        for start in range(0, len(points), batch_size):
            batch = points[start:start + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch)

    def search(self, query_vector: list[float], top_k: int = 10) -> list[tuple[int, float]]:
        """Trả về list các tuple (doc_id, score)"""
        if not self._collection_exists():
            return []
            
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
        )
        
        return [
            (hit.payload["doc_id"], hit.score) 
            for hit in results.points 
            if hit.score >= self.min_score
        ]

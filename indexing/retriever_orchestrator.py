import os
import json
import yaml
import logging
from .sparse.bm25_index import BM25Index
from .dense.embedding_model import EmbeddingModel
from .dense.qdrant_store import QdrantStore
from .hybrid_fusion import reciprocal_rank_fusion
from chunking.token_splitter import TokenSplitter
from chunking.tagger import Tagger
from chunking.chunk_validator import ChunkValidator
import datetime

logger = logging.getLogger(__name__)

class RetrieverOrchestrator:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.settings = yaml.safe_load(f)
        except Exception:
            self.settings = {}

        # Cấu hình
        self.bm25_cfg = self.settings.get("bm25", {})
        self.dense_cfg = self.settings.get("dense", {})
        self.fusion_cfg = self.settings.get("fusion", {})
        self.rerank_cfg = self.settings.get("reranker", {})
        self.chunk_cfg = self.settings.get("chunking", {})

        # Components
        self.bm25 = BM25Index(
            k1=self.bm25_cfg.get("k1", 1.5),
            b=self.bm25_cfg.get("b", 0.75),
            title_weight=self.bm25_cfg.get("title_weight", 2.5),
            section_title_weight=self.bm25_cfg.get("section_title_weight", 1.5),
            content_weight=self.bm25_cfg.get("content_weight", 1.0),
            min_score=self.bm25_cfg.get("min_score", 1.0)
        )
        
        self.qdrant = QdrantStore(
            db_path=self.dense_cfg.get("qdrant_db_path", "data/qdrant_db"),
            collection_name=self.dense_cfg.get("collection_name", "lung_chunks"),
            min_score=self.dense_cfg.get("min_vector_score", 0.50)
        )
        
        self.embedder = None
        self.reranker = None
        
        self.doc_map = {}
        self.documents = []

    def load_or_build_index(self, kb_path="data/knowledge_base.json"):
        kb_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), kb_path)
        if not os.path.exists(kb_full_path):
            logger.warning(f"Knowledge base not found at {kb_full_path}")
            return False

        with open(kb_full_path, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)

        # 1. Chunking
        print("Bắt đầu chunking...")
        splitter = TokenSplitter(
            max_tokens=self.chunk_cfg.get("max_tokens", 384),
            overlap_tokens=self.chunk_cfg.get("overlap_tokens", 50),
            min_chunk_length=self.chunk_cfg.get("min_chunk_length", 100)
        )
        tagger = Tagger()
        validator = ChunkValidator(
            min_length=self.chunk_cfg.get("min_chunk_length", 100),
            max_tokens=self.chunk_cfg.get("max_tokens", 384)
        )

        processed_docs = []
        new_id = 1
        for doc in raw_docs:
            content_chunks = splitter.split_text(doc["content"])
            for content_chunk in content_chunks:
                new_doc = doc.copy()
                new_doc["content"] = content_chunk
                new_doc["id"] = new_id
                # Thêm semantic tags
                new_doc["tags"] = tagger.tag(content_chunk)
                processed_docs.append(new_doc)
                new_id += 1

        # Validate chunks
        self.documents = validator.validate(processed_docs)
        self.doc_map = {doc["id"]: doc for doc in self.documents}
        print(f"Đã tạo {len(self.documents)} chunks.")

        # 2. Build BM25 Index
        print("Đang xây dựng BM25 index...")
        self.bm25.fit(self.documents)

        # 3. Build Dense Index
        print("Đang kiểm tra Qdrant index...")
        if self.embedder is None:
            self.embedder = EmbeddingModel(model_name=self.dense_cfg.get("model", "bkai-foundation-models/vietnamese-bi-encoder"))

        # Re-ingest nếu số lượng khác
        if self.qdrant.get_count() != len(self.documents):
            print("Đang tạo vector embeddings và lưu vào Qdrant...")
            
            # Encode sample to get size
            test_vec = self.embedder.encode(["test"])[0]
            self.qdrant.init_collection(vector_size=len(test_vec), recreate=True)
            
            # Embed all
            texts = [f"{doc.get('title', '')} {doc.get('section_title', '')} {doc.get('content', '')}" for doc in self.documents]
            embeddings = self.embedder.encode(texts)
            
            # Upsert
            points_data = []
            for i, doc in enumerate(self.documents):
                points_data.append({
                    "id": doc["id"],
                    "vector": embeddings[i],
                    "payload": {
                        "doc_id": doc["id"],
                        "source": doc["source"],
                        "url": doc["url"],
                        "title": doc.get("title", ""),
                        "section_title": doc.get("section_title", "")
                    }
                })
            self.qdrant.upsert_batch(points_data)
            print("Đã lưu xong Qdrant.")
        else:
            print("Qdrant index đã sẵn sàng.")

        # 4. Init Reranker if enabled
        if self.rerank_cfg.get("enabled", True) and self.reranker is None:
            from .reranker import CrossEncoderReranker
            print("Khởi tạo Reranker...")
            self.reranker = CrossEncoderReranker(model_name=self.rerank_cfg.get("model", "cross-encoder/ms-marco-MiniLM-L-6-v2"))

        return True

    def search(self, query: str, log_query=True) -> list[dict]:
        """Thực hiện full retrieval pipeline: BM25 + Dense -> RRF -> Rerank."""
        retrieval_k = self.fusion_cfg.get("retrieval_top_k", 10)
        final_k = self.fusion_cfg.get("final_top_k", 3)

        # 1. Sparse Search
        bm25_res = self.bm25.search(query, top_k=retrieval_k * 2)
        
        # 2. Dense Search
        query_vec = self.embedder.encode([query])[0] if self.embedder else []
        dense_res = self.qdrant.search(query_vec, top_k=retrieval_k * 2) if query_vec else []

        # 3. RRF
        fused_ids_scores = reciprocal_rank_fusion(bm25_res, dense_res, k=self.fusion_cfg.get("rrf_k", 60))
        
        # Lấy candidates
        candidates = []
        rrf_results = []
        for doc_id, rrf_score in fused_ids_scores[:retrieval_k]:
            if doc_id in self.doc_map:
                doc = self.doc_map[doc_id]
                candidates.append(doc)
                rrf_results.append({"doc_id": doc_id, "rrf_score": rrf_score})

        # 4. Rerank
        final_docs = []
        rerank_results = []
        if self.reranker and candidates:
            ranked_candidates = self.reranker.rerank(query, candidates, top_k=final_k)
            for doc, score in ranked_candidates:
                doc_copy = doc.copy()
                doc_copy["rerank_score"] = float(score)
                final_docs.append(doc_copy)
                rerank_results.append({"doc_id": doc["id"], "rerank_score": float(score)})
        else:
            final_docs = candidates[:final_k]

        # 5. Logging
        if log_query:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "bm25_results": [{"doc_id": d, "score": float(s)} for d, s in bm25_res],
                "dense_results": [{"doc_id": d, "score": float(s)} for d, s in dense_res],
                "rrf_results": rrf_results,
                "reranker_results": rerank_results,
                "final_top_k": [d["id"] for d in final_docs]
            }
            with open(os.path.join(log_dir, "retrieval_logs.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")

        return final_docs

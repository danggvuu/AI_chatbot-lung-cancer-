def reciprocal_rank_fusion(
    bm25_ranked_ids: list[tuple[int, float]],
    semantic_ranked_ids: list[tuple[int, float]],
    k: int = 60
) -> list[tuple[int, float]]:
    """
    Kết hợp 2 danh sách kết quả bằng RRF.
    Input lists là các tuple (doc_id, score), đã được sort giảm dần.
    Trả về danh sách (doc_id, rrf_score) sắp xếp giảm dần theo rrf_score.
    """
    rrf_scores = {}
    
    # ranked_ids is a list of tuples (doc_id, score)
    # enumerate starts rank at 1
    for rank, (doc_id, _) in enumerate(bm25_ranked_ids, start=1):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank)
        
    for rank, (doc_id, _) in enumerate(semantic_ranked_ids, start=1):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank)
        
    sorted_fused = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_fused

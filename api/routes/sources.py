from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

router = APIRouter()

def get_chat_service(request: Request):
    return getattr(request.app.state, "chat_service", None)

@router.get("/sources")
async def get_sources(chat_service=Depends(get_chat_service)):
    """Returns a list of all documents indexed in the database."""
    if not chat_service or not hasattr(chat_service.retriever, "documents"):
        return []
    
    # Chỉ trả về một số trường cần thiết để hiển thị trên UI, giới hạn dung lượng
    docs = []
    for doc in chat_service.retriever.documents:
        docs.append({
            "id": doc.get("id"),
            "source": doc.get("source"),
            "url": doc.get("url"),
            "title": doc.get("title"),
            "section_title": doc.get("section_title")
        })
    return docs

@router.post("/retrieve")
async def retrieve_only(request: Request, chat_service=Depends(get_chat_service)):
    """Retrieve chunks only without calling LLM."""
    data = await request.json()
    query = data.get("question", "")
    if not query:
        return JSONResponse(content={"error": "No question provided"}, status_code=400)
        
    if not chat_service:
        return {"question": query, "chunks": []}
        
    results = chat_service.retriever.retrieve(query, top_k=5)
    
    chunks = []
    for r in results:
        doc = chat_service.retriever.doc_map.get(r["id"], {})
        chunks.append({
            "id": r["id"],
            "score": r["score"],
            "content": doc.get("content", ""),
            "source": doc.get("source", ""),
            "url": doc.get("url", ""),
            "section_title": doc.get("section_title", "")
        })
        
    return {"question": query, "chunks": chunks}

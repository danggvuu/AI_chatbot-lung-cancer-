import os
import json
import argparse
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from retrieval import LungCancerRetriever

load_dotenv()

app = FastAPI(title="LungCare AI API", version="1.0.0")

# CORS middleware for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount legacy static files (kept for backward compat)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Check if React frontend build exists
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")
HAS_FRONTEND_BUILD = os.path.isdir(FRONTEND_DIST)

if HAS_FRONTEND_BUILD:
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

# Configuration from environment variables
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434").rstrip('/')
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
KB_PATH = os.environ.get("KB_PATH", "data/knowledge_base.json")

# Initialize retriever
retriever = LungCancerRetriever(kb_path=KB_PATH)

SYSTEM_PROMPT = """Bạn là trợ lý ảo hỗ trợ tra cứu thông tin về Ung thư Phổi từ các nguồn y tế uy tín của Việt Nam. Nhiệm vụ của bạn là trả lời CỰC KỲ NGẮN GỌN, ĐI THẲNG VÀO TRỌNG TÂM câu hỏi và TUÂN THỦ các chỉ dẫn an toàn sau:

[QUY TẮC CỐT LÕI (GIẢM LAN MAN & TẬP TRUNG)]
1. TRẢ LỜI TRỰC TIẾP DÒNG ĐẦU TIÊN: Không chào hỏi, không từ chối kiểu "tôi không thể đưa ra lời khuyên y tế", không giới thiệu bản thân hay viết lời mở đầu lan man. Trả lời thẳng vào câu hỏi.
2. ĐỐI CHIẾU HÀNH ĐỘNG CỤ THỂ: Nếu người dùng hỏi có nên làm một việc gì đó liên quan đến ung thư phổi (ví dụ: nên đi sàng lọc không, nên bỏ thuốc lá không, nên uống thuốc gì...), bạn phải khẳng định hoặc phủ định rõ ràng ngay lập tức dựa trên tài liệu.
3. CHỈ DÙNG NGỮ CẢNH: Trả lời ngắn gọn (dưới 150 từ) dưới dạng các gạch đầu dòng súc tích dựa trên thông tin trong "NGỮ CẢNH THAM KHẢO". Không suy diễn ngoài tài liệu. Trích dẫn nguồn bằng cách thêm ký hiệu [1], [2], [3] hoặc [4] tương ứng với tài liệu số 1, 2, 3, 4 ở cuối câu chứa thông tin trích dẫn.
4. CÂU HỎI NGOÀI CHỦ ĐỀ: Nếu người dùng hỏi các câu hỏi hoàn toàn không liên quan đến y học, sức khỏe hay ung thư phổi (ví dụ: lập trình, viết code, toán học, thời tiết, giải trí...), hãy lịch sự từ chối ngay lập tức và nêu rõ bạn chỉ hỗ trợ tra cứu thông tin về ung thư phổi.
5. KHÔNG CHẨN ĐOÁN: Tuyệt đối không đưa ra chẩn đoán bệnh hay đề xuất phác đồ điều trị cụ thể cho bệnh nhân. Luôn khuyên người dùng đến cơ sở y tế chuyên khoa.
6. TRUNG LẬP & KHÔNG QUẢNG CÁO: Tuyệt đối không quảng cáo, giới thiệu hay hướng người dùng đến khám chữa tại một bệnh viện cụ thể nào (như Bệnh viện Tâm Anh, Vinmec...). Luôn đưa ra khuyến nghị trung lập dưới dạng chung chung như "cơ sở y tế chuyên khoa", "khoa Ung bướu/Hô hấp" hoặc "bác sĩ chuyên khoa".

[AN TOÀN Y KHOA (BẮT BUỘC)]
- Nếu câu hỏi mô tả triệu chứng nghi ngờ ung thư phổi (ho kéo dài trên 3 tuần, ho ra máu, khó thở bất thường, đau ngực, sụt cân không rõ nguyên nhân):
  * Khuyến cáo đến cơ sở y tế chuyên khoa Ung bướu hoặc Hô hấp để khám sàng lọc.
  * Nhấn mạnh: Phát hiện sớm giúp tăng tỷ lệ sống sót đáng kể.
  * KHÔNG nói "bạn bị ung thư" hay "bạn không bị ung thư".

[CẤU TRÚC PHẢN HỒI]
1. Trả lời trực tiếp câu hỏi (khẳng định/phủ định hành động hoặc từ chối nếu ngoài chủ đề).
2. Các gạch đầu dòng giải thích ngắn gọn từ tài liệu (nếu đúng chủ đề, kèm trích dẫn số ở cuối câu).
3. Khuyến cáo khám sàng lọc (nếu là tình huống nghi ngờ bệnh).
4. Miễn trừ trách nhiệm (Luôn ghi ở cuối cùng nếu là câu hỏi y học): "Lưu ý: Thông tin chỉ mang tính tham khảo từ các nguồn y tế uy tín. Hãy tham khảo ý kiến bác sĩ chuyên khoa Ung bướu để được tư vấn chính xác nhất."
"""

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Serve React frontend build if available
    if HAS_FRONTEND_BUILD:
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
    # Fallback to legacy Jinja2 template
    return templates.TemplateResponse("index.html", {"request": request})

if HAS_FRONTEND_BUILD:
    @app.get("/favicon.svg")
    async def favicon():
        return FileResponse(os.path.join(FRONTEND_DIST, "favicon.svg"))

    @app.get("/icons.svg")
    async def icons():
        return FileResponse(os.path.join(FRONTEND_DIST, "icons.svg"))

@app.get("/api/sources")
async def get_sources():
    """Returns a list of all documents indexed in the database."""
    if not retriever.documents:
        retriever.load_database()
    
    sources_summary = []
    for doc in retriever.documents:
        sources_summary.append({
            "id": doc["id"],
            "source": doc["source"],
            "url": doc["url"],
            "title": doc["title"],
            "section_title": doc["section_title"]
        })
    return sources_summary

@app.post("/api/retrieve")
async def retrieve_only(request: Request):
    """Retrieve chunks only without calling LLM."""
    data = await request.json()
    query = data.get("question", "")
    top_k = data.get("top_k", 4)
    
    if not query:
        return JSONResponse(content={"error": "No question provided"}, status_code=400)
        
    retrieved_docs = retriever.search(query, top_k=top_k)
    return {"question": query, "chunks": retrieved_docs}

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    stream_requested = data.get("stream", False)
    
    if not messages:
        return JSONResponse(content={"error": "No messages provided"}, status_code=400)
        
    last_user_msg = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_msg = msg.get("content", "")
            break
            
    retrieved_docs = retriever.search(last_user_msg, top_k=4)
    
    context_str = ""
    sources_metadata = []
    
    if retrieved_docs:
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            context_parts.append(
                f"Tài liệu [{i+1}]:\n"
                f"Nguồn: {doc['source']} ({doc['url']})\n"
                f"Tiêu đề: {doc['title']} - Phần: {doc['section_title']}\n"
                f"Nội dung: {doc['content']}\n"
            )
            sources_metadata.append({
                "id": doc["id"],
                "source": doc["source"],
                "url": doc["url"],
                "title": doc["title"],
                "section_title": doc["section_title"],
                "snippet": doc["content"][:200] + "..."
            })
        context_str = "\n---\n".join(context_parts)
    else:
        context_str = "Không tìm thấy tài liệu liên quan trong cơ sở dữ liệu nội bộ."

    ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    history_messages = messages[:-1] if len(messages) > 1 else []
    for msg in history_messages:
        ollama_messages.append({
            "role": msg.get("role"),
            "content": msg.get("content")
        })
        
    user_enriched_content = (
        f"Hãy trả lời câu hỏi dưới đây của tôi.\n\n"
        f"--- NGỮ CẢNH THAM KHẢO ---\n{context_str}\n--------------------------\n\n"
        f"CÂU HỎI CỦA TÔI: {last_user_msg}"
    )
    ollama_messages.append({"role": "user", "content": user_enriched_content})
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": ollama_messages,
        "stream": stream_requested,
        "options": {
            "temperature": 0.3
        }
    }
    
    if stream_requested:
        def event_stream():
            yield f"data: {json.dumps({'sources': sources_metadata})}\n\n"
            try:
                with requests.post(f"{OLLAMA_API_URL}/api/chat", json=payload, stream=True, timeout=180) as r:
                    if r.status_code != 200:
                        yield f"data: {json.dumps({'error': 'Ollama error', 'detail': r.text})}\n\n"
                        return
                    for line in r.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            try:
                                json_line = json.loads(decoded_line)
                                content = json_line.get("message", {}).get("content", "")
                                if content:
                                    yield f"data: {json.dumps({'delta': content})}\n\n"
                                if json_line.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                yield f"data: {json.dumps({'error': 'Connection error', 'detail': str(e)})}\n\n"
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
        return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)
        
    try:
        response = requests.post(f"{OLLAMA_API_URL}/api/chat", json=payload, timeout=180)
        if response.status_code != 200:
            return JSONResponse(
                content={"error": f"Ollama returned error status {response.status_code}", "detail": response.text}, 
                status_code=502
            )
            
        ollama_res = response.json()
        assistant_message = ollama_res.get("message", {}).get("content", "")
        
        return {"message": assistant_message, "sources": sources_metadata}
        
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            content={"error": "Could not connect to Ollama server.", "detail": str(e)}, 
            status_code=503
        )

@app.get("/api/health")
async def health():
    """Verify backend health and check connections."""
    ollama_status = "offline"
    available_models = []
    
    try:
        r = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            ollama_status = "online"
            models_data = r.json()
            available_models = [m["name"] for m in models_data.get("models", [])]
    except Exception:
        pass
        
    kb_loaded = len(retriever.documents) > 0
    
    return {
        "status": "healthy",
        "database_loaded": kb_loaded,
        "database_records": len(retriever.documents),
        "ollama_connection": ollama_status,
        "ollama_url": OLLAMA_API_URL,
        "ollama_model": OLLAMA_MODEL,
        "ollama_model_available": OLLAMA_MODEL in available_models or f"{OLLAMA_MODEL}:latest" in available_models,
        "available_models": available_models
    }

def cli_mode(question, retrieve_only=False):
    """CLI mode for debugging without running the web server."""
    print(f"==========================================")
    print(f"🫁 LungCare AI - CLI Mode")
    print(f"==========================================")
    print(f"Câu hỏi: {question}\n")
    
    docs = retriever.search(question, top_k=4)
    
    if retrieve_only:
        print("--- KẾT QUẢ TÌM KIẾM (RETRIEVE ONLY) ---")
        if not docs:
            print("Không tìm thấy tài liệu phù hợp.")
            return
            
        for i, doc in enumerate(docs):
            print(f"[{i+1}] {doc['title']} - {doc['section_title']}")
            print(f"Nguồn: {doc['source']}")
            print(f"Trích dẫn: {doc['content'][:300]}...\n")
        return
        
    print("... Chế độ gọi LLM qua CLI chưa được triển khai đầy đủ. Hãy dùng --retrieve-only để test RAG.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LungCare AI Backend (FastAPI)")
    parser.add_argument("--retrieve-only", action="store_true", help="Only retrieve chunks, don't use LLM")
    parser.add_argument("--question", type=str, help="Question to ask in CLI mode")
    
    args, unknown = parser.parse_known_args()
    
    if args.question:
        cli_mode(args.question, args.retrieve_only)
    else:
        import uvicorn
        port = int(os.environ.get("PORT", 5080))
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

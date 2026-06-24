import os
import json
import argparse
import requests
import re
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

SYSTEM_PROMPT = """Bạn là trợ lý ảo y khoa LungCare AI tư vấn về ung thư phổi. Hãy đóng vai một bác sĩ chuyên khoa Hô hấp & Ung bướu nhiệt tình, chuyên nghiệp. Bạn phải đưa ra câu trả lời tự nhiên, giàu tính lâm sàng, tuyệt đối tránh các cụm từ máy móc như "Khẳng định:", "Phủ định:" hay "Dưới đây là câu trả lời của bạn:".

Bạn BẮT BUỘC phải trình bày câu trả lời của mình thành 4 đoạn (hoặc phần) riêng biệt theo đúng cấu trúc sau:

Đoạn 1 (Lời khuyên trực tiếp): Câu đầu tiên đi thẳng vào vấn đề tư vấn hành động ngay cho bệnh nhân (ví dụ: khuyên đưa đi khám chuyên khoa ngay lập tức, khuyên đi chụp CT phổi liều thấp LDCT, hoặc lý giải trực tiếp câu hỏi). Không chào hỏi rườm rà.

Đoạn 2 (Giải thích chuyên môn): Cung cấp 1-2 gạch đầu dòng giải thích y khoa ngắn gọn dựa hoàn toàn trên "NGỮ CẢNH THAM KHẢO". Thêm trích dẫn dạng [1], [2], [3]... ở cuối câu lấy thông tin từ tài liệu.

Đoạn 3 (Cảnh báo y khoa bắt buộc - SAFETY WARNING): Ghi rõ câu cảnh báo an toàn sau: "Tuyệt đối không tự ý mua thuốc ho hoặc kháng sinh uống kéo dài tại nhà, không tự chẩn đoán nóng trong người hay tự chẩn đoán chèn ép tĩnh mạch chủ (SVCO) là tác dụng phụ hóa trị để trì hoãn đi khám, không trì hoãn phẫu thuật hay điều trị y học hiện đại để đắp thuốc nam/uống lá xạ đen, và không tin vào tin đồn động dao kéo gây di căn. Bệnh nhân cần được đưa đi khám cấp cứu ngay lập tức nếu có dấu hiệu ho ra máu nặng hoặc phù mặt cổ chèn ép."

Đoạn 4 (Miễn trừ trách nhiệm y khoa): "Lưu ý: Thông tin chỉ mang tính tham khảo từ các nguồn y tế uy tín. Hãy tham khảo ý kiến bác sĩ chuyên khoa Ung bướu để được tư vấn chính xác nhất."

[LƯU Ý LÂM SÀNG]
- Tuyệt đối không tự kết luận "chắc chắn bị ung thư" hay "không bị ung thư".
- Giữ tính khách quan, trung lập khi khuyên đi khám chuyên khoa Hô hấp/Ung bướu (không hướng tới một bệnh viện tư cụ thể).
- Nếu câu hỏi ngoài chủ đề y tế hoặc ung thư phổi, hãy từ chối lịch sự và nêu rõ bạn chỉ hỗ trợ tra cứu về ung thư phổi.
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

def classify_intent(query: str) -> dict | None:
    """
    Phân loại nhanh câu hỏi ngoài chủ đề (Rule-based).
    Trả về dict chứa nội dung phản hồi nếu khớp mẫu, ngược lại trả về None.
    """
    if not query:
        return None
        
    # Chuẩn hóa chuỗi
    q_clean = query.strip().lower()
    q_clean = re.sub(r'[^\w\s]', '', q_clean).strip()
    
    # Định nghĩa các tập từ khóa
    greetings = {
        "chào", "hello", "hi", "xin chào", "chào bạn", "alo", "helo", "hey", "hế lô", "chào bác sĩ"
    }
    thanks_farewell = {
        "cảm ơn", "cám ơn", "thank you", "thanks", "tạm biệt", "bye", "hên gặp lại", "hẹn gặp lại", "tạm biệt bác sĩ", "cảm ơn bác sĩ"
    }
    identity = {
        "bạn là ai", "tên gì", "ai đây", "giới thiệu về bạn", "giới thiệu", "bạn là gì", "mày là ai"
    }
    
    words_count = len(q_clean.split())
    
    if words_count <= 4:
        if q_clean in greetings or any(w == q_clean for w in greetings):
            return {
                "message": "Chào bạn! Tôi là LungCare AI, trợ lý ảo chuyên tư vấn thông tin về bệnh lý Ung thư phổi. Bạn cần tôi hỗ trợ giải đáp thông tin gì hôm nay?",
                "sources": []
            }
        if q_clean in thanks_farewell or any(w in q_clean for w in ["cảm ơn", "cám ơn", "tạm biệt"]):
            return {
                "message": "Dạ không có gì ạ! Nếu bạn cần thêm bất kỳ thông tin nào về Ung thư phổi, hãy cứ hỏi tôi nhé. Chúc bạn và gia đình luôn dồi dào sức khỏe!",
                "sources": []
            }
        if q_clean in identity or any(w in q_clean for w in ["bạn là ai", "giới thiệu"]):
            return {
                "message": "Tôi là LungCare AI, trợ lý ảo y sinh chuyên biệt về Ung thư phổi. Tôi có nhiệm vụ hỗ trợ người bệnh tra cứu kiến thức chẩn đoán, điều trị, và an toàn lâm sàng dựa trên các tài liệu chính thống.",
                "sources": []
            }
            
    return None

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

    # Phân loại nhanh câu hỏi ngoài chủ đề (Rule-based)
    matched_intent = classify_intent(last_user_msg)
    if matched_intent:
        if stream_requested:
            def static_event_stream():
                yield f"data: {json.dumps({'sources': []})}\n\n"
                yield f"data: {json.dumps({'delta': matched_intent['message']})}\n\n"
            headers = {
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
            return StreamingResponse(static_event_stream(), media_type="text/event-stream", headers=headers)
        else:
            return {"message": matched_intent["message"], "sources": []}
            
    retrieved_docs = retriever.search(last_user_msg, top_k=3)
    
    # Nếu điểm số quá thấp làm kết quả RAG trống (Lạc đề hoặc ngoài phạm vi kiến thức)
    if not retrieved_docs:
        out_of_topic_msg = (
            "Rất tiếc, câu hỏi của bạn nằm ngoài phạm vi tài liệu y khoa về Ung thư phổi của tôi. "
            "Hiện tại tôi chỉ có dữ liệu chính thống để hỗ trợ giải đáp về triệu chứng, chẩn đoán, sàng lọc, "
            "phương pháp điều trị (nhắm đích, hóa/xạ trị) và biến chứng của bệnh lý ung thư phổi. "
            "Vui lòng đặt câu hỏi liên quan để tôi có thể hỗ trợ tốt nhất."
        )
        if stream_requested:
            def empty_event_stream():
                yield f"data: {json.dumps({'sources': []})}\n\n"
                yield f"data: {json.dumps({'delta': out_of_topic_msg})}\n\n"
            headers = {
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
            return StreamingResponse(empty_event_stream(), media_type="text/event-stream", headers=headers)
        else:
            return {"message": out_of_topic_msg, "sources": []}
            
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
            "temperature": 0.15,
            "num_predict": 500,
            "num_ctx": 4096,
            "top_k": 20,
            "top_p": 0.85
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
        uvicorn.run(app, host="0.0.0.0", port=port)

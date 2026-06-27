from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse

router = APIRouter()

def get_chat_service(request: Request):
    return request.app.state.chat_service

@router.post("/chat")
async def chat(request: Request, chat_service=Depends(get_chat_service)):
    data = await request.json()
    messages = data.get("messages", [])
    stream_requested = data.get("stream", False)
    
    if not messages:
        return JSONResponse(content={"error": "No messages provided"}, status_code=400)
        
    query = messages[-1].get("content", "")
    
    if stream_requested:
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
        return StreamingResponse(chat_service.get_chat_response_stream(query), media_type="text/event-stream", headers=headers)
    else:
        response_dict = await chat_service.get_chat_response_sync(query)
        return response_dict

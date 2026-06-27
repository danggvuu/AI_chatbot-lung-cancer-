"""LungCare AI - Backward-compatible entrypoint."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from api.server import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5080))
    # Chạy 1 worker duy nhất, không dùng reload=True để tránh spawn nhiều process
    # tranh chấp khóa file sqlite của Qdrant local
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, workers=1)

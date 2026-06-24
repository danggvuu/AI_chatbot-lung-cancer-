@echo off
chcp 65001 >nul
:: ============================================================
:: 🫁 LungCare AI - Khởi động nhanh trên Windows
:: ============================================================

echo.
echo   🫁  ╔══════════════════════════════════════════╗
echo       ║       LungCare AI - Khởi động nhanh      ║
echo       ║   Hệ thống Tư vấn Thông tin Ung thư Phổi ║
echo       ╚══════════════════════════════════════════╝
echo.

:: --- 1. Kiểm tra Python ---
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo   ❌  Python chưa được cài đặt hoặc chưa thêm vào PATH!
    echo       Tải tại: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
set PYTHON_CMD=python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo   ✅  Python:  %PYTHON_VER%

:: --- 2. Tạo virtual environment nếu chưa có ---
if not exist "venv" (
    echo   ⏳  Đang tạo virtual environment...
    %PYTHON_CMD% -m venv venv
    echo   ✅  Đã tạo venv/
)

:: Kích hoạt venv
call venv\Scripts\activate
echo   ✅  Đã kích hoạt virtual environment

:: --- 3. Cài đặt dependencies ---
echo   ⏳  Kiểm tra và cài đặt dependencies...
pip install -r requirements.txt -q
echo   ✅  Dependencies đã sẵn sàng

:: --- 3.5. Kiểm tra & Build Frontend React ---
if exist "frontend" if not exist "frontend\dist" (
    echo.
    echo   ⏳  Đang cài đặt và build React frontend [lần đầu]...
    cd frontend
    if not exist "node_modules" (
        call npm install
    )
    call npm run build
    cd ..
    echo   ✅  React frontend đã sẵn sàng
)

:: --- 4. Kiểm tra knowledge base ---
if not exist "data\knowledge_base.json" (
    echo.
    echo   ⏳  Chưa có knowledge base. Đang cào dữ liệu y khoa...
    %PYTHON_CMD% data_pipeline/scraper.py
    echo.
)

:: Đếm số lượng chunks bằng python
for /f "tokens=*" %%i in ('python -c "import json; print(len(json.load(open('data/knowledge_base.json', encoding='utf-8'))))" 2^>nul') do set CHUNK_COUNT=%%i
if "%CHUNK_COUNT%"=="" set CHUNK_COUNT=0
echo   ✅  Knowledge Base: %CHUNK_COUNT% phân đoạn y khoa

:: --- 5. Kiểm tra Ollama ---
echo.
set OLLAMA_MODEL=llama3.2
where ollama >nul 2>nul
if %errorlevel% equ 0 (
    echo   ✅  Ollama đã cài đặt
    :: Kiểm tra Ollama server có đang chạy không
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% equ 0 (
        echo   ✅  Ollama server đang chạy
        :: Kiểm tra model
        ollama list 2>nul | findstr /i "%OLLAMA_MODEL%" >nul
        if %errorlevel% equ 0 (
            echo   ✅  Model %OLLAMA_MODEL% đã sẵn sàng
        ) else (
            echo   ⚠️  Model %OLLAMA_MODEL% chưa tải. Đang tải...
            ollama pull %OLLAMA_MODEL%
        )
    ) else (
        echo   ⚠️  Ollama chưa chạy. Đang khởi động...
        :: Khởi động Ollama
        start /B ollama serve >nul 2>&1
        timeout /t 3 >nul
        ollama list 2>nul | findstr /i "%OLLAMA_MODEL%" >nul
        if %errorlevel% neq 0 (
            echo   ⏳  Đang tải model %OLLAMA_MODEL% [lần đầu có thể mất vài phút]...
            ollama pull %OLLAMA_MODEL%
        )
        echo   ✅  Ollama đã khởi động
    )
) else (
    echo   ⚠️  Ollama chưa cài đặt!
    echo       Tải tại: https://ollama.com/download
    echo       Sau khi cài, chạy: ollama pull %OLLAMA_MODEL%
    echo.
    echo   ⏳  Server vẫn sẽ khởi động nhưng chatbot sẽ không trả lời được.
)

:: --- 6. Khởi động server ---
echo.
echo   ╔══════════════════════════════════════════╗
echo   ║  🚀  Khởi động LungCare AI Server...     ║
echo   ║  📍  http://localhost:5080               ║
echo   ║  📄  API Docs: http://localhost:5080/docs ║
echo   ║  ⏹   Đóng cửa sổ này để tắt server      ║
echo   ╚══════════════════════════════════════════╝
echo.

:: Mở trình duyệt sau 2 giây ở luồng riêng
start "" http://localhost:5080

:: Chạy FastAPI server
%PYTHON_CMD% main.py

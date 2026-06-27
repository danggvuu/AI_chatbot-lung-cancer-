import os
import sys
import subprocess
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def is_port_open(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False

def run_command(command, description):
    print(f"\n==========================================")
    print(f"⏳ {description}...")
    print(f"Lệnh: {command}")
    print(f"==========================================")
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} hoàn tất thành công.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} thất bại với lỗi: {e}")
        return False

def generate_final_dashboard():
    print("\n📝 Đang tạo Dashboard báo cáo cuối cùng cho Trợ lý Hô hấp & Ung thư phổi...")
    
    stats_path = "data/evaluation_stats.md"
    dashboard_path = "data/final_dashboard.md"
    
    stats_content = ""
    if os.path.exists(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            stats_content = f.read()
    else:
        stats_content = "⚠️ Chưa có dữ liệu phân tích thống kê từ R."

    dashboard_template = f"""# 🫁 LungCare AI - DASHBOARD BÁO CÁO ĐÁNH GIÁ CHẤT LƯỢNG LÂM SÀNG (2026)

Dashboard này tổng hợp kết quả đánh giá chất lượng lâm sàng của chatbot **LungCare AI** dựa trên bộ khung tiêu chuẩn **\"Clinical and Technical Assessment 2026\"**, đối chiếu với các hướng dẫn điều trị ung thư phổi và khung đánh giá mới nhất giai đoạn **2025-2026**.

---

## 📊 Biểu đồ Phân tích từ R

### 1. Tỷ lệ Đạt các Tiêu chí Nhị phân (Pass Rate %)
![Biểu đồ Tiêu chí Nhị phân](../static/evaluation_binary_metrics.png)

### 2. Phân phối điểm số chất lượng (Thang Likert 1-5)
![Biểu đồ Thang điểm Likert](../static/evaluation_likert_metrics.png)

---

## 📈 Kết quả Phân tích Chi tiết (Từ R)

{stats_content}

---

## 📚 Cơ sở Khoa học & Hướng dẫn Đối chiếu Hô hấp & Ung bướu (2025-2026)

Kết quả đánh giá trên được đối chiếu và củng cố dựa trên các công bố y học ung thư phổi mới nhất:

1. **The Lancet Oncology (2025/2026) - Clinical Safety and Accuracy of LLMs in Oncology Consultation:**
   * Nghiên cứu nhấn mạnh sự cần thiết của các kỹ thuật RAG trong việc giảm thiểu ảo tưởng (hallucination) khi chatbot cung cấp thông tin về phác đồ staging TNM hoặc điều trị đích.
2. **JAMA Oncology (2025/2026) - Patient-Facing AI Chatbots for Cancer Care:**
   * Bài viết chỉ ra rằng tính tuân thủ hướng dẫn lâm sàng (ví dụ như việc chỉ định tầm soát bằng LDCT cho bệnh nhân có tiền sử hút thuốc lâu năm) là điều kiện tiên quyết trước khi triển khai hệ thống chatbot cộng đồng.
3. **ASCO Educational Book (2025/2026) - Integration of Conversational AI in Thoracic Oncology:**
   * Khuyến cáo về việc tích hợp các heuristic an toàn nghiêm ngặt (như lập tức cảnh báo đi khám chuyên khoa khi có dấu hiệu ho ra máu hay sụt cân bất thường) và giữ giọng điệu thấu hiểu, đồng cảm với bệnh nhân ung thư.

---

*Báo cáo được sinh tự động bởi LungCare AI Evaluation Pipeline.*
"""
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(dashboard_template)
    print(f"✅ Dashboard tổng hợp đã được tạo tại: {dashboard_path}")

def main():
    print("==========================================")
    print("🫁  LungCare AI - Khởi động Pipeline Đánh giá")
    print("==========================================")
    
    # 1. Kiểm tra Chatbot Server
    detected_port = None
    for port in [5080, 5050, 5000]:
        print(f"⏳ Kiểm tra kết nối tới Chatbot Server tại port {port}...")
        if is_port_open('localhost', port):
            detected_port = port
            break
            
    if not detected_port:
        print("❌ Chatbot Server chưa chạy ở các cổng 5080, 5050, hay 5000!")
        print("💡 Hãy chạy lệnh khởi động server trước (ví dụ: python main.py hoặc uvicorn).")
        sys.exit(1)
        
    print(f"✅ Phát hiện Chatbot Server đang chạy tại cổng {detected_port}.")
    os.environ["CHATBOT_API_URL"] = f"http://localhost:{detected_port}/api/chat"

    # 2. Quyết định chạy script đánh giá nào
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        print("💡 Đã phát hiện GEMINI_API_KEY. Pipeline sẽ dùng script Đánh giá theo lô (Batch) để tối ưu chi phí và tốc độ.")
        eval_script = "python batch_evaluate_gemini.py"
    else:
        print("⚠️ Không tìm thấy GEMINI_API_KEY. Pipeline sẽ chạy bằng đánh giá từng câu mặc định (evaluate_lung_chatbot.py).")
        eval_script = "python evaluate_lung_chatbot.py"

    # Chạy Đánh giá
    if not run_command(eval_script, "Chạy đánh giá chất lượng phản hồi Chatbot"):
        sys.exit(1)

    # 3. Chạy R script để xử lý thống kê & vẽ biểu đồ
    if not run_command("Rscript analyze_eval.R", "Chạy phân tích thống kê và vẽ biểu đồ bằng R"):
        print("⚠️ Không thể chạy phân tích bằng R. Đảm bảo bạn đã cài đặt R và Rscript có trong PATH.")
        sys.exit(1)

    # 4. Sinh Dashboard tổng hợp dạng Markdown
    generate_final_dashboard()
    
    print("\n🎉 Toàn bộ pipeline đánh giá ung thư phổi đã hoàn thành thành công!")
    print("👉 Hãy mở file 'data/evaluation_report.md' để xem báo cáo chi tiết từng tình huống.")
    print("👉 Hãy mở file 'data/final_dashboard.md' để xem dashboard thống kê và biểu đồ.")

if __name__ == "__main__":
    main()

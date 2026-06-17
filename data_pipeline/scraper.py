import os
import json
import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def clean_text(text):
    """Remove excessive whitespaces and clean text."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def scrape_url(url, source_name):
    """Scrape a single URL and extract content chunks by section headings."""
    print(f"Scraping {source_name}: {url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        if response.status_code != 200:
            print(f"  ❌ Failed to fetch {url}, status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        # Get article title
        title = ""
        h1_tag = soup.find('h1')
        if h1_tag:
            title = clean_text(h1_tag.text)
        else:
            title = clean_text(soup.title.text) if soup.title else "Thông tin Ung thư phổi"

        # Try to find the main content container
        content_div = None
        for selector in ['.detail-content', '.post-content', 'article', '.entry-content',
                         '.news-detail', '.detail-content-wrapper', '#main-content', '.content']:
            found = soup.select_one(selector)
            if found:
                content_div = found
                break

        if not content_div:
            content_div = soup.body

        chunks = []
        current_section = "Tổng quan"
        current_content = []

        # Skip words to filter out generic website components
        skip_words = ['chia sẻ:', 'bản quyền', 'hotline', 'liên hệ', 'bài viết liên quan',
                      'theo dõi chúng tôi', 'đăng ký', 'bác sĩ tư vấn', 'bình luận',
                      'gửi tin nhắn', 'đặt lịch', 'tư vấn miễn phí', 'gọi ngay']

        for element in content_div.find_all(['h2', 'h3', 'p', 'li']):
            if element.name in ['h2', 'h3']:
                # Save previous section if it has content
                if current_content:
                    sec_text = clean_text(" ".join(current_content))
                    if len(sec_text) > 100:
                        chunks.append({
                            "source": source_name,
                            "url": url,
                            "title": title,
                            "section_title": current_section,
                            "content": sec_text
                        })
                current_section = clean_text(element.text)
                current_content = []
            elif element.name in ['p', 'li']:
                txt = clean_text(element.text)
                if txt and not any(skip in txt.lower() for skip in skip_words):
                    current_content.append(txt)

        # Save last section
        if current_content:
            sec_text = clean_text(" ".join(current_content))
            if len(sec_text) > 100:
                chunks.append({
                    "source": source_name,
                    "url": url,
                    "title": title,
                    "section_title": current_section,
                    "content": sec_text
                })

        print(f"  ✅ Extracted {len(chunks)} sections from {source_name}")
        return chunks

    except Exception as e:
        print(f"  ❌ Error scraping {url}: {e}")
        return []


def main():
    """Main scraper entrypoint. Scrapes URLs and injects MOH guidelines."""
    urls = [
        # Bệnh viện K
        {"url": "https://benhvienk.vn/huong-dan-kham-tam-soat-phat-hien-som-ung-thu-phoi-tai-benh-vien-k-nd91481.html", "source": "Bệnh viện K"},
        {"url": "https://benhvienk.vn/nhung-dieu-can-biet-ve-ung-thu-phoi-nd93433.html", "source": "Bệnh viện K"},
        {"url": "https://benhvienk.vn/dau-hieu-canh-bao-ung-thu-phoi-nd92516.html", "source": "Bệnh viện K"},
        {"url": "https://benhvienk.vn/tac-dung-phu-khi-dieu-tri-hoa-chat-trong-ung-thu-phoi-nd92269.html", "source": "Bệnh viện K"},
        {"url": "https://benhvienk.vn/ung-thu-phoi-va-nhung-dieu-can-luu-y-nd93519.html", "source": "Bệnh viện K"},
        {"url": "https://benhvienk.vn/doi-tuong-nguy-co-cao-ung-thu-phoi-nd92572.html", "source": "Bệnh viện K"},
        {"url": "https://benhvienk.vn/trieu-chung-cua-ung-thu-phoi-nd92277.html", "source": "Bệnh viện K"},
        # Vinmec
        {"url": "https://www.vinmec.com/vie/bai-viet/bai-1-hieu-ro-ve-ung-thu-phoi-vi", "source": "Vinmec"},
        {"url": "https://www.vinmec.com/vie/bai-viet/co-nhung-loai-ung-thu-phoi-nao-vi", "source": "Vinmec"},
        {"url": "https://www.vinmec.com/vie/bai-viet/diem-danh-8-dau-hien-nham-phat-hien-som-ung-thu-phoi-vi", "source": "Vinmec"},
        {"url": "https://www.vinmec.com/vie/bai-viet/bi-ung-thu-phoi-ma-khong-ho-dung-bo-lo-cac-dau-hieu-khac", "source": "Vinmec"},
        {"url": "https://www.vinmec.com/vie/bai-viet/ung-thu-phoi-va-tuoi-tac-moi-lien-he-va-nhung-dieu-can-biet", "source": "Vinmec"},
        {"url": "https://www.vinmec.com/vie/bai-viet/ung-thu-phoi-co-chua-duoc-khong-vi/", "source": "Vinmec"},
        # Bệnh viện Tâm Anh
        {"url": "https://tamanhhospital.vn/ung-thu-phoi/", "source": "Bệnh viện Tâm Anh"},
        {"url": "https://tamanhhospital.vn/dieu-tri-ung-thu-phoi/", "source": "Bệnh viện Tâm Anh"},
        {"url": "https://tamanhhospital.vn/tam-soat-ung-thu-phoi/", "source": "Bệnh viện Tâm Anh"}
    ]

    all_chunks = []
    for u in urls:
        chunks = scrape_url(u["url"], u["source"])
        all_chunks.extend(chunks)

    # Inject official Ministry of Health (MOH) guidelines
    moh_guidelines = [
        {
            "source": "Bộ Y tế Việt Nam",
            "url": "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
            "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
            "section_title": "Phân loại ung thư phổi",
            "content": "Ung thư phổi được chia thành hai nhóm chính dựa trên đặc điểm mô bệnh học: (1) Ung thư phổi không tế bào nhỏ (NSCLC - Non-Small Cell Lung Cancer) chiếm khoảng 85% tổng số ca ung thư phổi, bao gồm ba phân nhóm: ung thư biểu mô tuyến (adenocarcinoma) - phổ biến nhất, thường gặp ở người không hút thuốc và phụ nữ; ung thư biểu mô vảy (squamous cell carcinoma) - liên quan chặt chẽ với hút thuốc lá; và ung thư tế bào lớn (large cell carcinoma) - có thể xuất hiện ở bất kỳ vị trí nào trong phổi, phát triển nhanh. (2) Ung thư phổi tế bào nhỏ (SCLC - Small Cell Lung Cancer) chiếm khoảng 15% ca ung thư phổi, đặc trưng bởi tốc độ phát triển rất nhanh, khả năng di căn sớm đến não, gan, xương và tuyến thượng thận, liên quan mật thiết đến hút thuốc lá nặng. SCLC thường đáp ứng tốt với hóa trị và xạ trị ban đầu nhưng tỷ lệ tái phát rất cao."
        },
        {
            "source": "Bộ Y tế Việt Nam",
            "url": "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
            "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
            "section_title": "Triệu chứng nhận biết sớm ung thư phổi",
            "content": "Các triệu chứng nhận biết sớm ung thư phổi bao gồm: Ho kéo dài trên 3 tuần không đỡ mặc dù đã điều trị, đặc biệt cần lưu ý ở người trên 40 tuổi. Thay đổi tính chất ho ở người hút thuốc lá lâu năm (ho nhiều hơn, ho nặng hơn, thay đổi âm sắc ho). Ho ra máu hoặc đàm lẫn máu (hemoptysis) dù chỉ một lần cũng cần đi khám ngay. Khó thở tiến triển, ban đầu khi gắng sức sau đó cả khi nghỉ ngơi. Đau ngực kéo dài, đau tăng khi hít sâu hoặc ho. Khàn tiếng kéo dài trên 2 tuần do khối u chèn ép dây thần kinh thanh quản quặt ngược. Sụt cân không chủ đích (giảm trên 5% trọng lượng cơ thể trong 6 tháng mà không rõ nguyên nhân). Mệt mỏi kéo dài, suy nhược toàn thân không giải thích được. Nhiễm trùng phổi tái đi tái lại (viêm phổi, viêm phế quản) ở cùng một vị trí. Khi xuất hiện bất kỳ triệu chứng nào trên, đặc biệt ở người có yếu tố nguy cơ, cần đi khám chuyên khoa hô hấp hoặc ung bướu ngay."
        },
        {
            "source": "Bộ Y tế Việt Nam",
            "url": "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
            "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
            "section_title": "Yếu tố nguy cơ gây ung thư phổi",
            "content": "Các yếu tố nguy cơ chính gây ung thư phổi gồm: Hút thuốc lá là nguyên nhân hàng đầu, gây ra khoảng 90% các ca ung thư phổi. Nguy cơ tăng tỷ lệ thuận với số bao-năm (pack-years = số bao thuốc hút mỗi ngày x số năm hút). Người hút 1 bao/ngày trong 20 năm (20 bao-năm) có nguy cơ cao gấp 20-30 lần so với người không hút. Hút thuốc lá thụ động (secondhand smoke) cũng làm tăng nguy cơ ung thư phổi 20-30%. Tiếp xúc nghề nghiệp với khí radon (chất phóng xạ tự nhiên trong đất), amiăng (asbestos) trong xây dựng và công nghiệp, các kim loại nặng (arsenic, chromium, nickel). Ô nhiễm không khí (bụi mịn PM2.5) được WHO xếp vào nhóm chất gây ung thư. Tiền sử gia đình có người thân cấp 1 (bố mẹ, anh chị em ruột) mắc ung thư phổi làm tăng nguy cơ 2-3 lần. Tiền sử bệnh phổi mạn tính như bệnh phổi tắc nghẽn mạn tính (COPD), xơ phổi (pulmonary fibrosis) cũng là yếu tố nguy cơ độc lập."
        },
        {
            "source": "Bộ Y tế Việt Nam",
            "url": "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
            "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
            "section_title": "Sàng lọc ung thư phổi bằng CT liều thấp (LDCT)",
            "content": "Chụp cắt lớp vi tính liều thấp (Low-Dose CT - LDCT) là phương pháp sàng lọc ung thư phổi hiệu quả nhất hiện nay, được Bộ Y tế và các tổ chức quốc tế khuyến cáo. Đối tượng sàng lọc: Người từ 50 đến 80 tuổi có tiền sử hút thuốc lá từ 20 bao-năm trở lên, bao gồm cả những người đã bỏ thuốc nhưng chưa quá 15 năm. Tần suất: Chụp LDCT hàng năm. Lợi ích: Nghiên cứu NLST (National Lung Screening Trial) cho thấy sàng lọc bằng LDCT giúp giảm 20% tỷ lệ tử vong do ung thư phổi so với chụp X-quang ngực thông thường, nhờ phát hiện ung thư ở giai đoạn sớm khi khối u còn nhỏ và có thể phẫu thuật triệt căn. Lưu ý: X-quang ngực thường KHÔNG đủ nhạy để phát hiện ung thư phổi giai đoạn sớm. Nốt phổi đơn độc phát hiện trên LDCT cần được theo dõi và đánh giá theo hệ thống Lung-RADS để quyết định xử trí tiếp theo."
        },
        {
            "source": "Bộ Y tế Việt Nam",
            "url": "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
            "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
            "section_title": "Tổng quan phương pháp điều trị ung thư phổi",
            "content": "Điều trị ung thư phổi phụ thuộc vào loại mô bệnh học, giai đoạn bệnh, tình trạng sức khỏe tổng quát và các đột biến gen của bệnh nhân. Các phương pháp điều trị chính gồm: (1) Phẫu thuật: Áp dụng cho giai đoạn sớm (I-II) của NSCLC, bao gồm cắt thùy phổi (lobectomy), cắt phân thùy, hoặc cắt phổi toàn bộ (pneumonectomy). (2) Hóa trị: Sử dụng các phác đồ dựa trên platinum như cisplatin hoặc carboplatin phối hợp với pemetrexed, paclitaxel, hoặc gemcitabine. Có thể dùng hóa trị bổ trợ sau phẫu thuật hoặc hóa trị tân bổ trợ trước phẫu thuật. (3) Xạ trị: Dùng đơn độc hoặc phối hợp hóa-xạ trị đồng thời cho giai đoạn III. Xạ trị lập thể định vị thân (SBRT) cho khối u nhỏ không mổ được. (4) Liệu pháp nhắm đích (Targeted Therapy): Gefitinib, erlotinib, osimertinib cho bệnh nhân có đột biến EGFR; crizotinib, alectinib cho đột biến ALK; dabrafenib cho đột biến BRAF. Xét nghiệm đột biến gen là bắt buộc trước khi chỉ định. (5) Liệu pháp miễn dịch (Immunotherapy): Pembrolizumab, nivolumab, atezolizumab cho bệnh nhân có PD-L1 dương tính hoặc phối hợp với hóa trị. Liệu pháp miễn dịch đã cải thiện đáng kể tiên lượng sống cho ung thư phổi giai đoạn muộn."
        },
        {
            "source": "Bộ Y tế Việt Nam",
            "url": "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
            "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
            "section_title": "Phân giai đoạn ung thư phổi theo hệ thống TNM",
            "content": "Hệ thống phân giai đoạn TNM (Tumor-Node-Metastasis) là tiêu chuẩn quốc tế để đánh giá mức độ lan rộng của ung thư phổi, quyết định phương pháp điều trị và tiên lượng. Giai đoạn I-II: Khối u còn khu trú tại phổi, chưa hoặc chỉ di căn hạch rốn phổi cùng bên. Có thể phẫu thuật cắt bỏ triệt căn. Tỷ lệ sống 5 năm dao động từ 60-90% tùy kích thước khối u. Đây là giai đoạn có tiên lượng tốt nhất. Giai đoạn III: Ung thư đã lan rộng cục bộ đến hạch trung thất hoặc xâm lấn các cấu trúc lân cận (thành ngực, màng phổi, thực quản). Điều trị chủ yếu bằng hóa-xạ trị đồng thời, sau đó có thể duy trì bằng liệu pháp miễn dịch (durvalumab). Một số trường hợp IIIA có thể phẫu thuật sau hóa trị tân bổ trợ. Giai đoạn IV: Ung thư đã di căn xa đến các cơ quan khác (não, gan, xương, tuyến thượng thận, phổi đối bên). Điều trị toàn thân bằng hóa trị, liệu pháp nhắm đích (nếu có đột biến driver), hoặc liệu pháp miễn dịch. Mục tiêu chính là kéo dài sống và cải thiện chất lượng cuộc sống. Tỷ lệ sống 5 năm toàn bộ cho tất cả các giai đoạn ung thư phổi khoảng 20%, nhấn mạnh tầm quan trọng của phát hiện sớm qua sàng lọc."
        },
        {
            "source": "Bộ Y tế Việt Nam",
            "url": "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
            "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
            "section_title": "Hội chứng chèn ép tĩnh mạch chủ trên (SVCS)",
            "content": "Hội chứng chèn ép tĩnh mạch chủ trên (Superior Vena Cava Syndrome - SVCS) là một cấp cứu lâm sàng khẩn cấp ở bệnh nhân ung thư phổi, xảy ra khi tĩnh mạch chủ trên bị chèn ép cơ học do khối u hoặc hạch trung thất phì đại. Triệu chứng đặc trưng bao gồm: phù nề mặt, cổ và chi trên (phù áo khoác), ho khan, khàn tiếng rõ rệt, khó thở tiến triển, nổi rõ tuần hoàn bàng hệ (tĩnh mạch căng phồng) ở vùng ngực và cổ. Bệnh nhân có dấu hiệu phù mặt cổ kèm ho khàn tiếng cần được đưa đi cấp cứu ngay lập tức để giải áp chèn ép tại các cơ sở chuyên khoa Ung bướu/Hô hấp, tuyệt đối không tự điều trị hoặc nhầm lẫn là tác dụng phụ thông thường của hóa trị."
        }
    ]

    all_chunks.extend(moh_guidelines)

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", "knowledge_base.json")

    # Add unique IDs
    for idx, chunk in enumerate(all_chunks):
        chunk["id"] = idx + 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n🫁 LungCare AI - Saved {len(all_chunks)} chunks to {output_path}")


if __name__ == "__main__":
    main()

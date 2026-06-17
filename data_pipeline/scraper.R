# ============================================================
# 🫁 LungCare AI - Bộ cào dữ liệu y khoa tự động bằng ngôn ngữ R
# ============================================================

# Tự động cài đặt các thư viện R cần thiết
required_packages <- c("httr", "rvest", "stringr", "jsonlite", "xml2")
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) {
  cat("⏳ Đang cài đặt các thư viện R cho bộ cào...\n")
  install.packages(new_packages, repos="http://cran.us.r-project.org")
}

library(httr)
library(rvest)
library(stringr)
library(jsonlite)
library(xml2)

# 1. Hàm làm sạch khoảng trắng văn bản
clean_text <- function(text) {
  text <- str_replace_all(text, "\\s+", " ")
  return(str_trim(text))
}

# 2. Hàm phát hiện và lọc bỏ thông tin quảng cáo, số điện thoại, địa chỉ (Noise)
is_promotional_or_noise <- function(text) {
  text_lower <- tolower(text)
  
  promo_phrases <- c(
    'hotline', 'liên hệ hotline', 'liên hệ trực tiếp', 'số điện thoại:', 'sđt:',
    'đặt lịch khám', 'đặt lịch hẹn', 'đặt lịch trực tuyến', 'đặt hẹn khám', 
    'đăng ký khám', 'đặt lịch tại', 'đăng ký trực tuyến', 'đăng ký ngay',
    'tư vấn miễn phí', 'gọi ngay', 'gọi hotline', 'tải ứng dụng', 'tải app',
    'mua ngay', 'đặt mua', 'giỏ hàng', 'giá bán:', 'giá tham khảo', 
    'khuyến mãi', 'ưu đãi', 'siêu ưu đãi', 'gói khám', 'dịch vụ khám',
    'fanpage:', 'website:', 'bản quyền thuộc', 'chia sẻ:', 'theo dõi chúng tôi',
    'gửi tin nhắn', 'tổng đài:', 'chăm sóc khách hàng', 'hệ thống bệnh viện',
    'phòng khám đa khoa', 'bệnh viện đa khoa', 'địa chỉ:', 'đ/c cũ:',
    '108 hoàng như tiếp', '2b phổ quang', '316c phạm hùng', '25 nguyễn hữu thọ', '265 cầu giấy',
    'nhà thuốc fpt long châu', 'hệ thống nhà thuốc', 'nhà thuốc long châu',
    'phát hành bởi', 'bản quyền thuộc', 'chính sách bảo mật', 'điều khoản sử dụng',
    'chuyên khoa:', 'nhận tư vấn', 'bài viết liên quan', 'bình luận', 'đăng ký',
    'sơ đồ tổ chức', 'thông tin tuyển dụng', 'chuyên gia – bác sĩ', 'danh mục kỹ thuật', 
    'tiện nghi giải thưởng', 'đào tạo liên hệ', 'hoạt động xã hội', 'sự kiện cộng đồng',
    'tầm nhìn – sứ mệnh', 'dịch vụ đặc biệt'
  )
  
  for (phrase in promo_phrases) {
    if (str_detect(text_lower, fixed(phrase))) {
      return(TRUE)
    }
  }
  
  address_indicators <- c('p.bồ đề', 'q.long biên', 'tp. hà nội', 'tp.hcm', 'q.tân bình', 'q.7', 'q.8', 'quận 1', 'quận 3', 'quận bình thạnh')
  for (ind in address_indicators) {
    if (str_detect(text_lower, fixed(ind))) {
      return(TRUE)
    }
  }
  
  return(FALSE)
}

# 3. Loại bỏ các phần tử menu điều hướng, header, footer của website
is_navigation_or_boilerplate <- function(node) {
  parent <- tryCatch(xml_parent(node), error = function(e) NULL)
  while (!is.null(parent)) {
    p_name <- tryCatch(xml_name(parent), error = function(e) "")
    if (p_name == "xml_document") {
      break
    }
    if (p_name %in% c("nav", "header", "footer")) {
      return(TRUE)
    }
    
    class_attr <- xml_attr(parent, "class")
    id_attr <- xml_attr(parent, "id")
    attrs <- c(class_attr, id_attr)
    attrs <- attrs[!is.na(attrs)]
    
    if (length(attrs) > 0) {
      attrs_lower <- tolower(paste(attrs, collapse = " "))
      keywords <- c('menu', 'nav', 'header', 'footer', 'breadcrumb', 'sidebar', 'aside', 'widget', 'modal', 'popup', 'dialog', 'overlay', 'cookie', 'banner', 'feedback', 'approver')
      for (k in keywords) {
        if (str_detect(attrs_lower, fixed(k))) {
          return(TRUE)
        }
      }
    }
    
    parent <- tryCatch(xml_parent(parent), error = function(e) NULL)
  }
  return(FALSE)
}

# 4. Hàm cào dữ liệu từ 1 URL cụ thể
scrape_url <- function(url, source_name) {
  cat("Scraping", source_name, ":", url, "...\n")
  
  tryCatch({
    res <- GET(
      url, 
      user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
      config(ssl_verifypeer = FALSE),
      timeout(15)
    )
    
    if (status_code(res) != 200) {
      cat("  ❌ Lỗi tải trang, mã trạng thái:", status_code(res), "\n")
      return(list())
    }
    
    soup <- read_html(res)
    
    # Tiêu đề bài viết
    title <- ""
    h1_tag <- html_element(soup, "h1")
    if (!is.null(h1_tag) && !is.na(html_text(h1_tag))) {
      title <- clean_text(html_text(h1_tag))
    } else {
      title_tag <- html_element(soup, "title")
      title <- ifelse(!is.null(title_tag) && !is.na(html_text(title_tag)), clean_text(html_text(title_tag)), "Thông tin Ung thư phổi")
    }
    
    # Tìm vùng chứa nội dung chính
    content_div <- NULL
    selectors <- c('[class*="posts-detail-container"]', '[class*="posts-detail"]', '.content_detail_sick', '.detail_sick', '.detail-content', '.post-content', 'article', 
                   '.entry-content', '.news-detail', '.detail-content-wrapper', '#main-content', '.content')
    
    for (sel in selectors) {
      found <- html_element(soup, sel)
      if (!is.na(found) && !is.null(found)) {
        if (!is_navigation_or_boilerplate(found)) {
          content_div <- found
          break
        }
      }
    }
    
    if (is.null(content_div) || is.na(content_div)) {
      content_div <- html_element(soup, "body")
    }
    
    chunks <- list()
    current_section <- "Tổng quan"
    current_content <- character()
    
    elements <- html_elements(content_div, "h2, h3, p, li")
    
    for (i in seq_along(elements)) {
      el <- elements[i]
      el_name <- html_name(el)
      el_text <- html_text(el)
      
      if (is_navigation_or_boilerplate(el)) {
        next
      }
      
      if (el_name %in% c("h2", "h3")) {
        if (length(current_content) > 0) {
          sec_text <- clean_text(paste(current_content, collapse = " "))
          if (nchar(sec_text) > 100) {
            chunks[[length(chunks) + 1]] <- list(
              source = source_name,
              url = url,
              title = title,
              section_title = current_section,
              content = sec_text
            )
          }
        }
        current_section <- clean_text(el_text)
        current_content <- character()
      } else if (el_name %in% c("p", "li")) {
        txt <- clean_text(el_text)
        if (nchar(txt) > 0 && !is_promotional_or_noise(txt)) {
          current_content <- c(current_content, txt)
        }
      }
    }
    
    # Lưu phần cuối cùng
    if (length(current_content) > 0) {
      sec_text <- clean_text(paste(current_content, collapse = " "))
      if (nchar(sec_text) > 100) {
        chunks[[length(chunks) + 1]] <- list(
          source = source_name,
          url = url,
          title = title,
          section_title = current_section,
          content = sec_text
        )
      }
    }
    
    cat("  ✅ Trích xuất thành công", length(chunks), "đoạn văn từ", source_name, "\n")
    return(chunks)
    
  }, error = function(e) {
    cat("  ❌ Lỗi khi cào dữ liệu từ", url, ":", e$message, "\n")
    return(list())
  })
}

# 5. Hàm chính (Main entrypoint)
main <- function() {
  urls_list <- list(
    list(url = "https://tamanhhospital.vn/ung-thu-phoi/", source = "Bệnh viện Tâm Anh"),
    list(url = "https://www.vinmec.com/vie/bai-viet/ung-thu-phoi-nguyen-nhan-trieu-chung-chan-doan-va-dieu-tri-vi", source = "Vinmec"),
    list(url = "https://www.vinmec.com/vie/bai-viet/ung-thu-phoi-co-chua-duoc-khong-vi", source = "Vinmec"),
    list(url = "https://www.vinmec.com/vie/bai-viet/sang-loc-ung-thu-phoi-khi-nao-can-thuc-hien-vi", source = "Vinmec"),
    list(url = "https://benhvienk.vn/ung-thu-phoi-nguyen-nhan-trieu-chung-va-phuong-phap-dieu-tri-nd94791.html", source = "Bệnh viện K"),
    list(url = "https://tamanhhospital.vn/dieu-tri-ung-thu-phoi/", source = "Bệnh viện Tâm Anh"),
    list(url = "https://benhvienk.vn/phuong-phap-dieu-tri-ung-thu-phoi-thay-doi-tu-nam-2025-nd94792.html", source = "Bệnh viện K"),
    list(url = "https://www.vinmec.com/vie/benh/ung-thu-phoi-3039", source = "Vinmec"),
    list(url = "https://nhathuoclongchau.com.vn/benh/ung-thu-phoi-428.html", source = "Nhà thuốc Long Châu"),
    list(url = "https://medlatec.vn/benh/ung-thu-phoi", source = "Medlatec"),
    list(url = "https://medlatec.vn/bai-viet/phuong-phap-chan-oan-ung-thu-phoi-tieu-chuan-quoc-te-p4056-54101.html", source = "Medlatec"),
    list(url = "https://medlatec.vn/bai-viet/nguyen-nhan-va-dieu-tri-ung-thu-phoi-p5164-39918.html", source = "Medlatec"),
    list(url = "https://www.benhvien108.vn/ung-thu-phoi-%E2%80%93-nhung-dieu-can-biet.htm", source = "Bệnh viện 108"),
    list(url = "https://www.benhvien108.vn/dieu-tri-ung-thu-phoi-p3246-36137.html", source = "Bệnh viện 108"),
    list(url = "https://hongngochospital.vn/vi/dau-hieu-ung-thu-phoi#cac-dau-hieu-ung-thu-phoi", source = "Bệnh viện Hồng Ngọc"),
    list(url = "https://hongngochospital.vn/vi/chan-doan-ung-thu-phoi#cac-phuong-phap-chan-doan-ung-thu-phoi", source = "Bệnh viện Hồng Ngọc")
  )
  
  all_chunks <- list()
  for (u in urls_list) {
    chunks <- scrape_url(u$url, u$source)
    all_chunks <- c(all_chunks, chunks)
  }
  
  # Chèn hướng dẫn điều trị chính thức của Bộ Y tế
  moh_guidelines <- list(
    list(
      source = "Bộ Y tế Việt Nam",
      url = "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
      title = "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
      section_title = "Phân loại ung thư phổi",
      content = "Ung thư phổi được chia thành hai nhóm chính dựa trên đặc điểm mô bệnh học: (1) Ung thư phổi không tế bào nhỏ (NSCLC - Non-Small Cell Lung Cancer) chiếm khoảng 85% tổng số ca ung thư phổi, bao gồm ba phân nhóm: ung thư biểu mô tuyến (adenocarcinoma) - phổ biến nhất, thường gặp ở người không hút thuốc và phụ nữ; ung thư biểu mô vảy (squamous cell carcinoma) - liên quan chặt chẽ với hút thuốc lá; và ung thư tế bào lớn (large cell carcinoma) - có thể xuất hiện ở bất kỳ vị trí nào trong phổi, phát triển nhanh. (2) Ung thư phổi tế bào nhỏ (SCLC - Small Cell Lung Cancer) chiếm khoảng 15% ca ung thư phổi, đặc trưng bởi tốc độ phát triển rất nhanh, khả năng di căn sớm đến não, gan, xương và tuyến thượng thận, liên quan mật thiết đến hút thuốc lá nặng. SCLC thường đáp ứng tốt với hóa trị và xạ trị ban đầu nhưng tỷ lệ tái phát rất cao."
    ),
    list(
      source = "Bộ Y tế Việt Nam",
      url = "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
      title = "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
      section_title = "Triệu chứng nhận biết sớm ung thư phổi",
      content = "Các triệu chứng nhận biết sớm ung thư phổi bao gồm: Ho kéo dài trên 3 tuần không đỡ mặc dù đã điều trị, đặc biệt cần lưu ý ở người trên 40 tuổi. Thay đổi tính chất ho ở người hút thuốc lá lâu năm (ho nhiều hơn, ho nặng hơn, thay đổi âm sắc ho). Ho ra máu hoặc đàm lẫn máu (hemoptysis) dù chỉ một lần cũng cần đi khám ngay. Khó thở tiến triển, ban đầu khi gắng sức sau đó cả khi nghỉ ngơi. Đau ngực kéo dài, đau tăng khi hít sâu hoặc ho. Khàn tiếng kéo dài trên 2 tuần do khối u chèn ép dây thần kinh thanh quản quặt ngược. Sụt cân không chủ đích (giảm trên 5% trọng lượng cơ thể trong 6 tháng mà không rõ nguyên nhân). Mệt mỏi kéo dài, suy nhược toàn thân không giải thích được. Nhiễm trùng phổi tái đi tái lại (viêm phổi, viêm phế quản) ở cùng một vị trí. Khi xuất hiện bất kỳ triệu chứng nào trên, đặc biệt ở người có yếu tố nguy cơ, cần đi khám chuyên khoa hô hấp hoặc ung bướu ngay."
    ),
    list(
      source = "Bộ Y tế Việt Nam",
      url = "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
      title = "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
      section_title = "Yếu tố nguy cơ gây ung thư phổi",
      content = "Các yếu tố nguy cơ chính gây ung thư phổi gồm: Hút thuốc lá là nguyên nhân hàng đầu, gây ra khoảng 90% các ca ung thư phổi. Nguy cơ tăng tỷ lệ thuận với số bao-năm (pack-years = số bao thuốc hút mỗi ngày x số năm hút). Người hút 1 bao/ngày trong 20 năm (20 bao-năm) có nguy cơ cao gấp 20-30 lần so với người không hút. Hút thuốc lá thụ động (secondhand smoke) cũng làm tăng nguy cơ ung thư phổi 20-30%. Tiếp xúc nghề nghiệp với khí radon (chất phóng xạ tự nhiên trong đất), amiăng (asbestos) trong xây dựng và công nghiệp, các kim loại nặng (arsenic, chromium, nickel). Ô nhiễm không khí (bụi mịn PM2.5) được WHO xếp vào nhóm chất gây ung thư. Tiền sử gia đình có người thân cấp 1 (bố mẹ, anh chị em ruột) mắc ung thư phổi làm tăng nguy cơ 2-3 lần. Tiền sử bệnh phổi mạn tính như bệnh phổi tắc nghẽn mạn tính (COPD), xơ phổi (pulmonary fibrosis) cũng là yếu tố nguy cơ độc lập."
    ),
    list(
      source = "Bộ Y tế Việt Nam",
      url = "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
      title = "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
      section_title = "Sàng lọc ung thư phổi bằng CT liều thấp (LDCT)",
      content = "Chụp cắt lớp vi tính liều thấp (Low-Dose CT - LDCT) là phương pháp sàng lọc ung thư phổi hiệu quả nhất hiện nay, được Bộ Y tế và các tổ chức quốc tế khuyến cáo. Đối tượng sàng lọc: Người từ 50 đến 80 tuổi có tiền sử hút thuốc lá từ 20 bao-năm trở lên, bao gồm cả những người đã bỏ thuốc nhưng chưa quá 15 năm. Tần suất: Chụp LDCT hàng năm. Lợi ích: Nghiên cứu NLST (National Lung Screening Trial) cho thấy sàng lọc bằng LDCT giúp giảm 20% tỷ lệ tử vong do ung thư phổi so với chụp X-quang ngực thông thường, nhờ phát hiện ung thư ở giai đoạn sớm khi khối u còn nhỏ và có thể phẫu thuật triệt căn. Lưu ý: X-quang ngực thường KHÔNG đủ nhạy để phát hiện ung thư phổi giai đoạn sớm. Nốt phổi đơn độc phát hiện trên LDCT cần được theo dõi và đánh giá theo hệ thống Lung-RADS để quyết định xử trí tiếp theo."
    ),
    list(
      source = "Bộ Y tế Việt Nam",
      url = "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
      title = "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
      section_title = "Tổng quan phương pháp điều trị ung thư phổi",
      content = "Điều trị ung thư phổi phụ thuộc vào loại mô bệnh học, giai đoạn bệnh, tình trạng sức khỏe tổng quát và các đột biến gen của bệnh nhân. Các phương pháp điều trị chính gồm: (1) Phẫu thuật: Áp dụng cho giai đoạn sớm (I-II) của NSCLC, bao gồm cắt thùy phổi (lobectomy), cắt phân thùy, hoặc cắt phổi toàn bộ (pneumonectomy). (2) Hóa trị: Sử dụng các phác đồ dựa trên platinum như cisplatin hoặc carboplatin phối hợp với pemetrexed, paclitaxel, hoặc gemcitabine. Có thể dùng hóa trị bổ trợ sau phẫu thuật hoặc hóa trị tân bổ trợ trước phẫu thuật. (3) Xạ trị: Dùng đơn độc hoặc phối hợp hóa-xạ trị đồng thời cho giai đoạn III. Xạ trị lập thể định vị thân (SBRT) cho khối u nhỏ không mổ được. (4) Liệu pháp nhắm đích (Targeted Therapy): Gefitinib, erlotinib, osimertinib cho bệnh nhân có đột biến EGFR; crizotinib, alectinib cho đột biến ALK; dabrafenib cho đột biến BRAF. Xét nghiệm đột biến gen là bắt buộc trước khi chỉ định. (5) Liệu pháp miễn dịch (Immunotherapy): Pembrolizumab, nivolumab, atezolizumab cho bệnh nhân có PD-L1 dương tính hoặc phối hợp với hóa trị. Liệu pháp miễn dịch đã cải thiện đáng kể tiên lượng sống cho ung thư phổi giai đoạn muộn."
    ),
    list(
      source = "Bộ Y tế Việt Nam",
      url = "https://kcb.vn/huong-dan-chan-doan-dieu-tri-ung-thu-phoi",
      title = "Hướng dẫn chẩn đoán và điều trị ung thư phổi của Bộ Y tế",
      section_title = "Phân giai đoạn ung thư phổi theo hệ thống TNM",
      content = "Hệ thống phân giai đoạn TNM (Tumor-Node-Metastasis) là tiêu chuẩn quốc tế để đánh giá mức độ lan rộng của ung thư phổi, quyết định phương pháp điều trị và tiên lượng. Giai đoạn I-II: Khối u còn khu trú tại phổi, chưa hoặc chỉ di căn hạch rốn phổi cùng bên. Có thể phẫu thuật cắt bỏ triệt căn. Tỷ lệ sống 5 năm dao động từ 60-90% tùy kích thước khối u. Đây là giai đoạn có tiên lượng tốt nhất. Giai đoạn III: Ung thư đã lan rộng cục bộ đến hạch trung thất hoặc xâm lấn các cấu trúc lân cận (thành ngực, màng phổi, thực quản). Điều trị chủ yếu bằng hóa-xạ trị đồng thời, sau đó có thể duy trì bằng liệu pháp miễn dịch (durvalumab). Một số trường hợp IIIA có thể phẫu thuật sau hóa trị tân bổ trợ. Giai đoạn IV: Ung thư đã di căn xa đến các cơ quan khác (não, gan, xương, tuyến thượng thận, phổi đối bên). Điều trị toàn thân bằng hóa trị, liệu pháp nhắm đích (nếu có đột biến driver), hoặc liệu pháp miễn dịch. Mục tiêu chính là kéo dài sống và cải thiện chất lượng cuộc sống. Tỷ lệ sống 5 năm toàn bộ cho tất cả các giai đoạn ung thư phổi khoảng 20%, nhấn mạnh tầm quan trọng của phát hiện sớm qua sàng lọc."
    )
  )
  
  all_chunks <- c(all_chunks, moh_guidelines)
  
  # Đảm bảo thư mục data tồn tại
  dir.create("data", showWarnings = FALSE)
  
  # Thêm ID tự động tăng
  for (idx in seq_along(all_chunks)) {
    all_chunks[[idx]]$id <- idx
  }
  
  output_path <- "data/knowledge_base.json"
  
  # Ghi file JSON dạng pretty
  write_json(all_chunks, path = output_path, pretty = TRUE, auto_unbox = TRUE)
  
  cat("\n🫁 LungCare AI - Đã lưu thành công", length(all_chunks), "phân đoạn y khoa vào", output_path, "\n")
}

# Chạy chương trình chính
main()

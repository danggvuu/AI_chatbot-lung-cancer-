# ============================================================
# 📊 LungCare AI - Phân tích Thống kê Đánh giá Lâm sàng bằng R
# ============================================================

# Tự động kiểm tra và cài đặt các thư viện cần thiết
required_packages <- c("jsonlite", "ggplot2", "dplyr", "tidyr")
new_packages <- required_packages[!(required_packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) {
  cat("⏳ Đang cài đặt các thư viện R cần thiết...\n")
  install.packages(new_packages, repos="http://cran.us.r-project.org")
}

library(jsonlite)
library(ggplot2)
library(dplyr)
library(tidyr)

# 1. Nạp dữ liệu đánh giá
json_file <- "data/evaluation_results.json"
if (!file.exists(json_file)) {
  stop("❌ Không tìm thấy file data/evaluation_results.json! Hãy chạy evaluate_lung_chatbot.py trước.")
}

eval_data <- fromJSON(json_file)

# 2. Trích xuất bảng điểm
scores_df <- eval_data$scores
scores_df$case_id <- eval_data$case_id

cat("✅ Nạp dữ liệu thành công! Tổng số ca đánh giá:", nrow(scores_df), "\n\n")

# 3. Vẽ biểu đồ 1: Tỷ lệ đạt (%) của các tiêu chí nhị phân (Binary Metrics: 0 hoặc 1)
binary_df <- scores_df %>%
  select(case_id, guideline_adherence, safety_of_recommendations, recognition_of_key_risks) %>%
  pivot_longer(cols = -case_id, names_to = "Metric", values_to = "Score") %>%
  mutate(Metric = case_when(
    Metric == "guideline_adherence" ~ "Guideline Adherence",
    Metric == "safety_of_recommendations" ~ "Clinical Safety",
    Metric == "recognition_of_key_risks" ~ "Risk Recognition",
    TRUE ~ Metric
  ))

pass_rates <- binary_df %>%
  group_by(Metric) %>%
  summarize(PassRate = mean(Score) * 100)

p1 <- ggplot(pass_rates, aes(x = reorder(Metric, PassRate), y = PassRate, fill = Metric)) +
  geom_bar(stat = "identity", width = 0.45, show.legend = FALSE) +
  geom_text(aes(label = paste0(round(PassRate, 1), "%")), vjust = -0.5, fontface = "bold", size = 5) +
  scale_y_continuous(limits = c(0, 110), breaks = seq(0, 100, 20)) +
  scale_fill_brewer(palette = "Set2") +
  labs(
    title = "Clinical Evaluation Binary Metrics (Pass Rate %)",
    subtitle = paste("Based on", nrow(scores_df), "standard lung cancer clinical cases"),
    x = "Clinical Assessment Criteria",
    y = "Pass Rate (%)"
  ) +
  theme_minimal(base_family = "sans") +
  theme(
    plot.title = element_text(face = "bold", size = 13, hjust = 0.5),
    plot.subtitle = element_text(size = 9, hjust = 0.5, color = "gray30"),
    axis.title = element_text(face = "bold", size = 10),
    axis.text = element_text(size = 9.5)
  )

ggsave("static/evaluation_binary_metrics.png", plot = p1, width = 7.5, height = 4.5, dpi = 150)
cat("📊 Đã vẽ biểu đồ tiêu chí nhị phân: static/evaluation_binary_metrics.png\n")

# 4. Vẽ biểu đồ 2: Phân phối điểm số Likert (1 - 5)
# Lưu ý: accuracy_of_grading và conversational_explanation cũng là thang Likert y khoa
likert_df <- scores_df %>%
  select(case_id, accuracy_of_grading, conversational_explanation, clarity, overall_helpfulness) %>%
  pivot_longer(cols = -case_id, names_to = "Metric", values_to = "Score") %>%
  mutate(Metric = case_when(
    Metric == "accuracy_of_grading" ~ "Triage Accuracy",
    Metric == "conversational_explanation" ~ "Conversational Expl.",
    Metric == "clarity" ~ "Clarity",
    Metric == "overall_helpfulness" ~ "Overall Helpfulness",
    TRUE ~ Metric
  ))

p2 <- ggplot(likert_df, aes(x = Metric, y = Score, fill = Metric)) +
  geom_boxplot(width = 0.35, show.legend = FALSE, alpha = 0.6, outlier.shape = NA) +
  geom_jitter(width = 0.08, size = 3.5, aes(color = Metric), show.legend = FALSE, alpha = 0.8) +
  scale_y_continuous(limits = c(0, 5.5), breaks = 0:5) +
  scale_fill_brewer(palette = "Set1") +
  scale_color_brewer(palette = "Set1") +
  labs(
    title = "Quality Ratings Distribution (Likert Scale 1-5)",
    subtitle = "Rating distribution for Clarity, Helpfulness, Triage & Conversational quality",
    x = "Quality Dimension",
    y = "Score"
  ) +
  theme_minimal(base_family = "sans") +
  theme(
    plot.title = element_text(face = "bold", size = 13, hjust = 0.5),
    plot.subtitle = element_text(size = 9, hjust = 0.5, color = "gray30"),
    axis.title = element_text(face = "bold", size = 10),
    axis.text = element_text(size = 10)
  )

ggsave("static/evaluation_likert_metrics.png", plot = p2, width = 8.5, height = 4.5, dpi = 150)
cat("📊 Đã vẽ biểu đồ điểm Likert: static/evaluation_likert_metrics.png\n")

# 5. Xuất báo cáo thống kê dạng Markdown Table
summary_text <- "
### 📊 Bảng phân tích thống kê chi tiết bằng ngôn ngữ R

Dưới đây là các chỉ số thống kê mô tả (Descriptive Statistics) được tính toán tự động bằng ngôn ngữ R từ kết quả thử nghiệm lâm sàng:

| Chỉ số đánh giá | Điểm Trung bình (Mean) | Độ lệch chuẩn (SD) | Loại tiêu chí | Tỷ lệ Đạt (%) |
|---|:---:|:---:|:---:|:---:|
"

for (col in c("guideline_adherence", "safety_of_recommendations", "recognition_of_key_risks", "accuracy_of_grading", "conversational_explanation", "clarity", "overall_helpfulness")) {
  mean_val <- mean(scores_df[[col]])
  sd_val <- sd(scores_df[[col]])
  
  metric_name <- case_when(
    col == "guideline_adherence" ~ "Tuân thủ hướng dẫn (Guideline Adherence)",
    col == "safety_of_recommendations" ~ "Độ an toàn khuyến cáo (Clinical Safety)",
    col == "recognition_of_key_risks" ~ "Nhận diện rủi ro chính (Risk Recognition)",
    col == "accuracy_of_grading" ~ "Độ chính xác phân loại (Triage Accuracy)",
    col == "conversational_explanation" ~ "Giải thích hội thoại (Conversational)",
    col == "clarity" ~ "Độ rõ ràng (Clarity)",
    col == "overall_helpfulness" ~ "Độ hữu ích (Helpfulness)"
  )
  
  if (col %in% c("guideline_adherence", "safety_of_recommendations", "recognition_of_key_risks")) {
    summary_text <- paste0(summary_text, sprintf("| **%s** | %.2f | %.2f | Nhị phân (0/1) | **%.1f%%** |\n", metric_name, mean_val, sd_val, mean_val * 100))
  } else {
    summary_text <- paste0(summary_text, sprintf("| **%s** | %.2f | %.2f | Likert (1-5) | *N/A (Likert)* |\n", metric_name, mean_val, sd_val))
  }
}

write(summary_text, file = "data/evaluation_stats.md")
cat("📝 Đã xuất báo cáo thống kê dạng bảng: data/evaluation_stats.md\n")
cat("🎉 Hoàn tất phân tích dữ liệu trên R thành công!\n")

library(jsonlite)
library(ggplot2)

# Check if data exists
kb_file <- "data/knowledge_base.json"
if (!file.exists(kb_file)) {
  stop("Knowledge base file not found!")
}

# Read JSON
kb_data <- fromJSON(kb_file)

# --- Theme Configuration ---
theme_dark_custom <- function() {
  theme_minimal(base_size = 12) +
  theme(
    plot.background = element_rect(fill = "#090d16", color = NA),
    panel.background = element_rect(fill = "#090d16", color = NA),
    panel.grid.major = element_line(color = "#1e293b", size = 0.5),
    panel.grid.minor = element_blank(),
    text = element_text(color = "#f8fafc", family = "sans"),
    axis.text = element_text(color = "#94a3b8"),
    axis.title = element_text(color = "#cbd5e1", face = "bold"),
    plot.title = element_text(color = "#22d3ee", face = "bold", size = 13, hjust = 0.5),
    plot.subtitle = element_text(color = "#64748b", size = 9, hjust = 0.5),
    legend.position = "none"
  )
}

# Source palette colors matching the frontend
source_colors <- c(
  "Bệnh viện Tâm Anh" = "#a78bfa",
  "Bộ Y tế Việt Nam" = "#22d3ee",
  "Vinmec" = "#f472b6",
  "Bệnh viện K" = "#fb923c"
)

# --- Plot 1: Phân bố số lượng phân đoạn theo nguồn tài liệu ---
source_counts <- as.data.frame(table(kb_data$source))
colnames(source_counts) <- c("Source", "Count")

p1 <- ggplot(source_counts, aes(x = reorder(Source, Count), y = Count, fill = Source)) +
  geom_bar(stat = "identity", width = 0.5, color = "#090d16", lwd = 1) +
  geom_text(aes(label = Count), hjust = -0.3, color = "#f8fafc", size = 4, fontface = "bold") +
  coord_flip() +
  scale_fill_manual(values = source_colors) +
  labs(
    title = "PHÂN BỐ TÀI LIỆU THEO NGUỒN",
    subtitle = "Số lượng phân đoạn y khoa được nạp vào cơ sở dữ liệu",
    x = "Nguồn tài liệu",
    y = "Số lượng phân đoạn"
  ) +
  theme_dark_custom() +
  ylim(0, max(source_counts$Count) + 5)


# --- Plot 2: Độ dài trung bình mỗi phân đoạn theo nguồn (Số từ) ---
word_counts <- sapply(kb_data$content, function(text) {
  length(strsplit(text, "\\s+")[[1]])
})
kb_data$WordCount <- word_counts

avg_word_counts <- aggregate(WordCount ~ source, data = kb_data, FUN = mean)
colnames(avg_word_counts) <- c("Source", "AvgWordCount")

p2 <- ggplot(avg_word_counts, aes(x = reorder(Source, AvgWordCount), y = AvgWordCount, fill = Source)) +
  geom_bar(stat = "identity", width = 0.5, color = "#090d16", lwd = 1) +
  geom_text(aes(label = round(AvgWordCount, 1)), hjust = -0.3, color = "#f8fafc", size = 4, fontface = "bold") +
  coord_flip() +
  scale_fill_manual(values = source_colors) +
  labs(
    title = "ĐỘ DÀI TRUNG BÌNH PHÂN ĐOẠN",
    subtitle = "Số từ trung bình trong mỗi phần nội dung tra cứu",
    x = "Nguồn tài liệu",
    y = "Số lượng từ trung bình"
  ) +
  theme_dark_custom() +
  ylim(0, max(avg_word_counts$AvgWordCount) + 60)


# --- Plot 3: Từ khóa y khoa phổ biến nhất (Text Mining) ---
all_text <- paste(kb_data$content, collapse = " ")
clean_text <- gsub("[[:punct:]]", " ", all_text)
clean_text <- tolower(clean_text)
words <- unlist(strsplit(clean_text, "\\s+"))
words <- words[words != ""]

# Vietnamese stop words to filter out
r_stopwords <- c(
  'và', 'hoặc', 'nhưng', 'vì', 'nên', 'thì', 'ở', 'tại', 'có', 'không', 
  'như', 'thế_nào', 'như_thế_nào', 'tôi', 'người', 'nhà', 'người_nhà', 
  'này', 'được', 'cho', 'làm', 'sao', 'để', 'của', 'với', 'trong', 
  'nếu', 'là', 'cái', 'sự', 'việc', 'những', 'các', 'ra', 'vào', 'lên', 'xuống', 
  'đi', 'lại', 'qua', 'đến', 'nơi', 'nào', 'gì', 'ai', 'đâu', 'khi', 'lúc', 
  'sau', 'trước', 'kia', 'đó', 'ấy', 'nọ', 'họ', 'nó', 'chúng', 'ta', 'tự', 
  'thường', 'hay', 'rất', 'quá', 'lắm', 'hết', 'cơ', 'bản', 'mỗi', 'một', 'cả', 
  'nhất', 'nhỏ', 'lớn', 'nhiều', 'ít', 'vừa', 'mới', 'còn', 'đều', 'chỉ', 'cũng', 
  'vẫn', 'thế', 'đây', 'vậy', 'có_thể', 'cần', 'phải', 'đối', 'tượng', 'theo', 'trình',
  'bằng', 'đầu', 'dưới', 'trên', 'các', 'ngày', 'năm', 'tháng', 'loại', 'thể'
)

words_filtered <- words[!words %in% r_stopwords]
words_filtered <- words_filtered[nchar(words_filtered) > 2] # Filter out short words

word_freq <- as.data.frame(table(words_filtered))
colnames(word_freq) <- c("Word", "Freq")
word_freq <- word_freq[order(-word_freq$Freq), ]

# Take top 15 words
top_keywords <- head(word_freq, 12)

p3 <- ggplot(top_keywords, aes(x = reorder(Word, Freq), y = Freq)) +
  geom_bar(stat = "identity", fill = "#8b5cf6", width = 0.5, color = "#090d16", lwd = 1) +
  geom_text(aes(label = Freq), hjust = -0.3, color = "#f8fafc", size = 4, fontface = "bold") +
  coord_flip() +
  labs(
    title = "TẦN SUẤT XUẤT HIỆN TỪ KHÓA",
    subtitle = "Các thuật ngữ xuất hiện nhiều nhất (đã lọc stop words)",
    x = "Từ khóa",
    y = "Số lần xuất hiện"
  ) +
  theme_dark_custom() +
  ylim(0, max(top_keywords$Freq) + 10)


# --- Plot 4: Phân bố mật độ độ dài phân đoạn (Density Plot) ---
p4 <- ggplot(kb_data, aes(x = WordCount, fill = source)) +
  geom_density(alpha = 0.4, color = NA) +
  scale_fill_manual(values = source_colors) +
  labs(
    title = "MẬT ĐỘ PHÂN BỐ ĐỘ DÀI PHÂN ĐOẠN",
    subtitle = "Phân phối xác suất số lượng từ theo từng nguồn",
    x = "Số lượng từ",
    y = "Mật độ (Density)"
  ) +
  theme_dark_custom() +
  theme(
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(color = "#94a3b8", size = 7),
    legend.box.spacing = unit(0.1, "cm"),
    legend.key.size = unit(0.3, "cm")
  )

# --- Save all plots ---
dir.create("static", showWarnings = FALSE)
ggsave("static/sources_plot.png", plot = p1, width = 7, height = 4.2, dpi = 150)
ggsave("static/wordcount_plot.png", plot = p2, width = 7, height = 4.2, dpi = 150)
ggsave("static/keywords_plot.png", plot = p3, width = 7, height = 4.2, dpi = 150)
ggsave("static/density_plot.png", plot = p4, width = 7, height = 4.2, dpi = 150)

cat("Successfully generated 4 R analysis plots in static/ directory!\n")

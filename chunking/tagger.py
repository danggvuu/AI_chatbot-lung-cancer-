class Tagger:
    TAGS = {
        "cancer_type": ["NSCLC", "SCLC", "tế bào nhỏ", "không tế bào nhỏ"],
        "stage": ["giai đoạn I", "giai đoạn II", "giai đoạn III", "giai đoạn IV", "di căn", "tiến xa"],
        "treatment": ["phẫu thuật", "hóa trị", "xạ trị", "nhắm đích", "miễn dịch", "giảm nhẹ"],
        "mutation": ["EGFR", "ALK", "ROS1", "BRAF", "KRAS", "PD-L1", "RET", "NTRK", "MET", "T790M"],
        "emergency": ["SVCO", "ho ra máu", "di căn não", "sốt giảm bạch cầu", "chèn ép", "tràn dịch"]
    }

    def tag(self, text: str) -> list[str]:
        """Gắn thẻ semantic cho chunk dựa trên nội dung."""
        found_tags = set()
        lower_text = text.lower()
        
        for category, keywords in self.TAGS.items():
            for kw in keywords:
                if kw.lower() in lower_text:
                    found_tags.add(f"{category}:{kw}")
                    
        return list(found_tags)

from datetime import datetime

class GuidelinesInjector:
    def get_injections(self) -> list[dict]:
        """Return official guidelines, myth-busting, and emergency chunks."""
        injections = []
        
        # 1. Bộ Y tế QĐ 4825/QĐ-BYT & QĐ 1248/QĐ-BYT
        injections.extend([
            {
                "source": "Bộ Y tế Việt Nam (QĐ 4825/QĐ-BYT)",
                "url": "https://kcb.vn/van-ban/quyet-dinh-so-4825-qd-byt",
                "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi không tế bào nhỏ",
                "section_title": "Tại sao cần xét nghiệm đột biến gen trước khi điều trị?",
                "content": "Xét nghiệm gen (đột biến sinh học phân tử) là bước bắt buộc trước khi lựa chọn phác đồ điều trị toàn thân cho bệnh nhân ung thư phổi không tế bào nhỏ giai đoạn tiến xa hoặc di căn. Lý do: 1) Ở người Việt Nam, tỷ lệ đột biến gen EGFR chiếm đến 40-60%. 2) Mỗi loại đột biến (EGFR, ALK, ROS1, BRAF) sẽ có thuốc nhắm đích (Targeted Therapy) đặc hiệu tương ứng, mang lại hiệu quả vượt trội và ít tác dụng phụ hơn so với hóa trị truyền thống. 3) Tránh việc dùng sai thuốc, tiết kiệm thời gian vàng trong điều trị."
            },
            {
                "source": "Bộ Y tế Việt Nam (QĐ 4825/QĐ-BYT)",
                "url": "https://kcb.vn/van-ban/quyet-dinh-so-4825-qd-byt",
                "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi không tế bào nhỏ",
                "section_title": "Cơ chế kháng thuốc nhắm đích",
                "content": "Bệnh nhân điều trị bằng thuốc nhắm đích (ví dụ: thuốc ức chế Tyrosine Kinase - TKIs thế hệ 1, 2) thường sẽ xuất hiện tình trạng kháng thuốc sau khoảng 9-14 tháng. Đột biến T790M là nguyên nhân kháng thuốc phổ biến nhất (chiếm 50-60%). Khi bị kháng thuốc, khối u có thể phát triển trở lại. Giải pháp là sinh thiết lại (sinh thiết mô hoặc sinh thiết lỏng qua máu) để tìm đột biến kháng thuốc, từ đó chuyển sang thuốc thế hệ 3 (ví dụ: Osimertinib) phù hợp."
            },
            {
                "source": "Bộ Y tế Việt Nam (QĐ 4825/QĐ-BYT)",
                "url": "https://kcb.vn/van-ban/quyet-dinh-so-4825-qd-byt",
                "title": "Hướng dẫn chẩn đoán và điều trị ung thư phổi không tế bào nhỏ",
                "section_title": "Hóa trị tân bổ trợ và bổ trợ",
                "content": "Trong điều trị ung thư phổi giai đoạn sớm (I, II, IIIA): 1) Hóa trị tân bổ trợ (Neoadjuvant): Được thực hiện TRƯỚC phẫu thuật nhằm thu nhỏ kích thước khối u, giúp phẫu thuật dễ dàng hơn và tiêu diệt các vi di căn sớm. 2) Hóa trị bổ trợ (Adjuvant): Được thực hiện SAU phẫu thuật nhằm tiêu diệt những tế bào ung thư còn sót lại hoặc vi di căn trong máu, giúp giảm tỷ lệ tái phát và kéo dài thời gian sống."
            }
        ])
        
        # 2. IASLC TNM 9th Edition
        injections.extend([
            {
                "source": "IASLC (TNM 9th Edition 2025)",
                "url": "https://www.iaslc.org/",
                "title": "Phân loại giai đoạn ung thư phổi TNM lần thứ 9 (áp dụng từ 2025)",
                "section_title": "Cập nhật phân loại hạch N2 (N2a và N2b)",
                "content": "Theo hệ thống phân loại TNM lần thứ 9 (hiệu lực từ 01/2025) của Hiệp hội Nghiên cứu Ung thư Phổi Quốc tế (IASLC), nhóm hạch trung thất N2 được chia thành hai nhóm nhỏ để đánh giá tiên lượng chính xác hơn: 1) N2a: Di căn hạch trung thất hoặc dưới chạc ba khí phế quản ở một trạm duy nhất (single station). 2) N2b: Di căn hạch trung thất hoặc dưới chạc ba khí phế quản ở nhiều trạm (multistation). Bệnh nhân N2b có tiên lượng xấu hơn N2a và thường cần phác đồ đa thức phức tạp hơn."
            }
        ])

        # 3. Myth-busting
        injections.extend([
            {
                "source": "Tổ chức Y tế Thế giới (WHO) & Bệnh viện Ung bướu",
                "url": "https://www.who.int/",
                "title": "Giải đáp các tin đồn về điều trị ung thư",
                "section_title": "Sự thật về đụng dao kéo và di căn",
                "content": "Tin đồn 'đụng dao kéo (phẫu thuật, sinh thiết) làm ung thư di căn nhanh hơn' là hoàn toàn SAI LẦM và KHÔNG có cơ sở khoa học. Sự thật là phẫu thuật cắt bỏ khối u giai đoạn sớm là phương pháp duy nhất có khả năng chữa khỏi ung thư phổi triệt để. Sinh thiết kim là thủ thuật an toàn, bắt buộc để xác định chính xác loại tế bào ung thư. Từ chối phẫu thuật vì sợ dao kéo sẽ làm mất đi 'thời gian vàng' để chữa khỏi bệnh."
            },
            {
                "source": "Viện Dinh dưỡng Quốc gia",
                "url": "http://viendinhduong.vn/",
                "title": "Dinh dưỡng cho bệnh nhân ung thư",
                "section_title": "Có nên nhịn ăn, bỏ đói tế bào ung thư?",
                "content": "Nhịn ăn, kiêng khem thịt đỏ, sữa, đường với hy vọng 'bỏ đói tế bào ung thư' là quan niệm SAI LẦM và cực kỳ nguy hiểm. Khi nhịn ăn, cơ thể sẽ suy kiệt, mất khối cơ, suy giảm miễn dịch, dẫn đến không đủ sức khỏe để tiếp nhận các đợt hóa trị, xạ trị hoặc phẫu thuật. Suy dinh dưỡng là nguyên nhân gây tử vong hàng đầu ở bệnh nhân ung thư, trước cả khi khối u đe dọa tính mạng. Bệnh nhân cần ăn uống đa dạng, giàu đạm để tăng cường thể trạng."
            },
            {
                "source": "Cục Quản lý Khám chữa bệnh",
                "url": "https://kcb.vn/",
                "title": "Cảnh báo an toàn y tế",
                "section_title": "Sự thật về thuốc nam, lá xạ đen, lá đu đủ, nấm linh chi",
                "content": "Tuyệt đối không sử dụng thuốc nam, thuốc lá, lá xạ đen, lá đu đủ đực, sả, nấm linh chi hay đông trùng hạ thảo để THAY THẾ các phương pháp điều trị y học hiện đại (hóa trị, xạ trị, phẫu thuật, nhắm đích). Không có bằng chứng khoa học nào chứng minh các loại lá này chữa khỏi ung thư. Việc từ chối y học hiện đại để uống thuốc nam sẽ làm bệnh tiến triển sang giai đoạn muộn không thể cứu vãn. Linh chi hay đông trùng hạ thảo chỉ có tác dụng hỗ trợ phục hồi sức khỏe, không có tác dụng tiêu diệt tế bào ung thư."
            },
            {
                "source": "Hiệp hội Ung thư Hoa Kỳ (ACS)",
                "url": "https://www.cancer.org/",
                "title": "Giải đáp tin đồn y tế",
                "section_title": "Nước kiềm (alkaline water) có chữa được ung thư?",
                "content": "Tin đồn 'uống nước kiềm (nước ion kiềm) hoặc baking soda có thể tiêu diệt tế bào ung thư do thay đổi pH cơ thể' là hoàn toàn vô căn cứ. Sự thật là cơ thể con người có cơ chế điều hòa pH máu cực kỳ chặt chẽ (luôn ở mức 7.35 - 7.45). Không có loại nước uống hay thức ăn nào có thể làm thay đổi pH của máu hoặc pH tại khối u. Nước kiềm không có tác dụng điều trị ung thư."
            },
            {
                "source": "Tổ chức Y tế Thế giới (WHO)",
                "url": "https://www.who.int/",
                "title": "Các câu hỏi thường gặp về Ung thư",
                "section_title": "Ung thư phổi có lây không?",
                "content": "Ung thư phổi KHÔNG phải là bệnh lây nhiễm. Bạn hoàn toàn không thể bị lây ung thư phổi từ người bệnh thông qua tiếp xúc, ăn uống chung, ho, hắt hơi, hay chăm sóc bệnh nhân. Yếu tố nguy cơ chính gây ung thư phổi là hút thuốc lá (chủ động và thụ động), môi trường ô nhiễm, tiếp xúc amiăng, và một phần do gen di truyền."
            }
        ])

        # 4. Emergency & Palliative Care (QĐ 1514/QĐ-BYT)
        injections.extend([
            {
                "source": "Bộ Y tế Việt Nam (QĐ 1514/QĐ-BYT)",
                "url": "https://kcb.vn/van-ban/quyet-dinh-so-1514-qd-byt",
                "title": "Hướng dẫn chẩn đoán và điều trị một số bệnh ung bướu",
                "section_title": "Hội chứng chèn ép tĩnh mạch chủ trên (SVCO)",
                "content": "Hội chứng chèn ép tĩnh mạch chủ trên (SVCO) là một CẤP CỨU UNG BƯỚU nghiêm trọng, thường gặp ở bệnh nhân ung thư phổi do khối u trung thất lớn chèn ép. Triệu chứng báo động gồm: phù nề mặt, cổ và nửa thân trên (phù áo khoác), đỏ bừng mặt, nổi tĩnh mạch cổ, khó thở dữ dội khi nằm. Bệnh nhân cần được đưa đến bệnh viện cấp cứu NGAY LẬP TỨC để được xử trí (thở oxy, corticoid liều cao, xạ trị cấp cứu hoặc đặt stent tĩnh mạch)."
            },
            {
                "source": "Bộ Y tế Việt Nam (QĐ 1514/QĐ-BYT)",
                "url": "https://kcb.vn/van-ban/quyet-dinh-so-1514-qd-byt",
                "title": "Hướng dẫn chẩn đoán và điều trị một số bệnh ung bướu",
                "section_title": "Xử trí ho ra máu ồ ạt",
                "content": "Ho ra máu ồ ạt (trên 200ml/lần hoặc trên 600ml/24h) là CẤP CỨU NỘI KHOA KHẨN CẤP đe dọa tính mạng do ngạt thở. Sơ cứu tại nhà: 1) Đặt bệnh nhân nằm nghiêng về bên phổi tổn thương (để máu không chảy tràn sang phổi lành). 2) Giữ đường thở thông thoáng. 3) Tuyệt đối không cho uống nước hay thuốc. 4) Gọi cấp cứu 115 ngay lập tức để chuyển viện. Tại viện, bác sĩ có thể nội soi phế quản cầm máu hoặc nút mạch (embolization)."
            },
            {
                "source": "Tổ chức Y tế Thế giới (WHO)",
                "url": "https://www.who.int/",
                "title": "Hướng dẫn chăm sóc giảm nhẹ",
                "section_title": "Bậc thang giảm đau của WHO",
                "content": "Kiểm soát đau cho bệnh nhân ung thư giai đoạn muộn tuân theo nguyên tắc Bậc thang giảm đau của WHO gồm 3 bước: Bậc 1 (đau nhẹ): Dùng thuốc giảm đau không opioid (Paracetamol, NSAIDs). Bậc 2 (đau vừa): Bổ sung opioid yếu (Codeine, Tramadol) kết hợp thuốc Bậc 1. Bậc 3 (đau nặng): Sử dụng opioid mạnh (Morphine, Fentanyl) kết hợp thuốc Bậc 1. Thuốc phải được dùng theo đúng giờ cố định, tăng liều dần, và do bác sĩ chuyên khoa kê đơn. Người nhà không tự ý mua thuốc giảm đau mạn tính cho bệnh nhân."
            },
            {
                "source": "Bộ Y tế Việt Nam (QĐ 1514/QĐ-BYT)",
                "url": "https://kcb.vn/van-ban/quyet-dinh-so-1514-qd-byt",
                "title": "Hướng dẫn chẩn đoán và điều trị một số bệnh ung bướu",
                "section_title": "Tràn dịch màng phổi do ung thư",
                "content": "Tràn dịch màng phổi ác tính là tình trạng dịch tích tụ trong khoang màng phổi, gây khó thở, đau ngực, ho khan. Xử trí phụ thuộc vào mức độ: Dịch ít có thể theo dõi; Dịch nhiều gây khó thở cấp cần được CHỌC HÚT DỊCH màng phổi cấp cứu để giải áp, giúp bệnh nhân dễ thở ngay. Nếu dịch tái lập nhanh, bác sĩ có thể làm thủ thuật gây dính màng phổi hoặc đặt dẫn lưu màng phổi liên tục."
            },
            {
                "source": "Bộ Y tế Việt Nam",
                "url": "https://kcb.vn/",
                "title": "Chăm sóc bệnh nhân ung thư",
                "section_title": "Xử trí sốt do hạ bạch cầu",
                "content": "Sốt giảm bạch cầu (sốt ≥ 38.3°C một lần hoặc ≥ 38.0°C kéo dài hơn 1 giờ kèm theo số lượng bạch cầu đa nhân trung tính giảm dưới 500 tế bào/mm3) là CẤP CỨU NHIỄM TRÙNG nghiêm trọng thường gặp sau hóa trị. Bệnh nhân có nguy cơ tử vong nhanh chóng do nhiễm trùng huyết. Không được tự ý uống thuốc hạ sốt tại nhà để che giấu triệu chứng. Bệnh nhân cần nhập viện lập tức để cấy máu và dùng kháng sinh phổ rộng đường tĩnh mạch."
            }
        ])

        # Formatting
        now_str = datetime.now().strftime("%Y-%m-%d")
        for chunk in injections:
            chunk["last_updated"] = now_str
            chunk["priority"] = "guideline_paraphrased"
            chunk["source_type"] = "official_injection"

        return injections

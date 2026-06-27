import os
import json
import yaml
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.hospital_scraper import HospitalScraper
from cleaners.deduplicator import Deduplicator
from guidelines_injector import GuidelinesInjector

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "sources_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run():
    print("🚀 Bắt đầu quá trình thu thập và xử lý dữ liệu...")
    config = load_config()
    sources = config.get("sources", [])
    
    scraper = HospitalScraper()
    deduplicator = Deduplicator(similarity_threshold=0.85)
    injector = GuidelinesInjector()
    
    raw_chunks = []
    
    # 1. Thu thập dữ liệu từ các URL (parallel)
    print(f"📥 Đang cào dữ liệu từ {len(sources)} nguồn...")
    
    def process_source(source):
        source_chunks = []
        name = source["name"]
        priority = source.get("priority", "hospital")
        
        for url in source.get("urls", []):
            html = scraper.fetch_url(url)
            if not html:
                continue
                
            try:
                sections = scraper.extract_article_content(html)
                for sec in sections:
                    source_chunks.append({
                        "source": name,
                        "url": url,
                        "title": sec["title"],
                        "section_title": sec["section_title"],
                        "content": sec["content"],
                        "priority": priority,
                        "source_type": "web_scrape",
                        "last_updated": "2026-06-27"
                    })
            except Exception as e:
                print(f"⚠️ Lỗi xử lý {url}: {str(e)}")
        return source_chunks

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_source, sources))
    
    for r in results:
        raw_chunks.extend(r)
        
    print(f"✅ Thu thập được {len(raw_chunks)} đoạn văn (chunks) thô.")
    
    # 2. Loại bỏ trùng lặp (Deduplication)
    print("🧹 Bắt đầu loại bỏ trùng lặp (Deduplication)...")
    cleaned_chunks = []
    existing_texts = []
    
    for chunk in raw_chunks:
        # Check length
        if len(chunk["content"]) < 100:
            continue
            
        if not deduplicator.is_duplicate(chunk["content"], existing_texts):
            cleaned_chunks.append(chunk)
            existing_texts.append(chunk["content"])
            
    print(f"✅ Sau khi lọc trùng lặp và đoạn ngắn, còn lại {len(cleaned_chunks)} chunks.")
    
    # 3. Tiêm dữ liệu Official Guidelines & Myth-busting
    print("💉 Đang tiêm dữ liệu Official Guidelines và tin đồn...")
    injections = injector.get_injections()
    cleaned_chunks.extend(injections)
    
    print(f"✅ Tổng số chunks sau khi tiêm: {len(cleaned_chunks)}")
    
    # 4. Gắn ID
    for i, chunk in enumerate(cleaned_chunks):
        chunk["id"] = i + 1
        
    # 5. Lưu kết quả
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "knowledge_base.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_chunks, f, ensure_ascii=False, indent=2)
        
    print(f"🎉 Hoàn tất! Đã lưu {len(cleaned_chunks)} chunks vào {output_path}")

if __name__ == "__main__":
    run()

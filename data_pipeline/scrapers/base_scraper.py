import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import re
import time

import random

class BaseScraper:
    def __init__(self, timeout=15, retries=3):
        self.timeout = timeout
        self.retries = retries
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def fetch_url(self, url: str) -> str | None:
        """Fetch URL with retries and return HTML text. Returns None if dead link or error."""
        for attempt in range(self.retries + 1):
            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                "Upgrade-Insecure-Requests": "1"
            }
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout, verify=False)
                if response.status_code == 200:
                    return response.text
                elif response.status_code in [404, 403, 500]:
                    print(f"❌ [Link Hỏng] {url} trả về mã {response.status_code}")
                    return None
            except requests.RequestException as e:
                print(f"⚠️ [Lỗi Kết Nối] {url} - {str(e)}")
            time.sleep(2)
        return None

    def clean_text(self, text: str) -> str:
        """Clean extra spaces and newlines."""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_article_content(self, html: str) -> list[dict]:
        """
        To be implemented by specific scrapers.
        Should return a list of sections: [{"title": "...", "content": "..."}]
        """
        raise NotImplementedError("Subclasses must implement extract_article_content")

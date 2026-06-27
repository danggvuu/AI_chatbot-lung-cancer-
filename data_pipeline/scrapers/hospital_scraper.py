import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from cleaners.noise_filter import NoiseFilter

class HospitalScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.noise_filter = NoiseFilter()

    def extract_article_content(self, html: str) -> list[dict]:
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove noisy tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            tag.decompose()
            
        sections = []
        # Fallback title if h1 is missing
        main_title = soup.title.string.strip() if soup.title else "Thông tin y tế"
        h1 = soup.find('h1')
        if h1:
            main_title = self.clean_text(h1.get_text())

        # Attempt to find the main content article to avoid sidebar noise
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_=lambda c: c and ('content' in c.lower() or 'post' in c.lower() or 'article' in c.lower()))
        if not main_content:
            main_content = soup # fallback

        current_section = "Tổng quan"
        current_content = []

        # Iterate through elements in main content
        for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol']):
            text = self.clean_text(element.get_text())
            if not text:
                continue

            if element.name in ['h2', 'h3']:
                # Save previous section if not noise
                joined_content = " ".join(current_content)
                if joined_content and not self.noise_filter.is_noise(joined_content):
                    sections.append({
                        "title": main_title,
                        "section_title": current_section,
                        "content": joined_content
                    })
                current_section = text
                current_content = []
            elif element.name in ['ul', 'ol']:
                list_items = [self.clean_text(li.get_text()) for li in element.find_all('li')]
                if list_items:
                    current_content.append("- " + "\n- ".join([i for i in list_items if i]))
            else:
                current_content.append(text)

        # Save last section
        joined_content = " ".join(current_content)
        if joined_content and not self.noise_filter.is_noise(joined_content):
            sections.append({
                "title": main_title,
                "section_title": current_section,
                "content": joined_content
            })

        return sections

"""Wikipedia scraper for mathematician biographical data"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import re

class WikipediaScraper:
    def __init__(self, delay: float = 1.0):
        """Initialize scraper with rate limiting"""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SciMap/1.0 (Educational Research Project)'
        })
    
    def scrape_page(self, url: str) -> Dict:
        """Scrape a Wikipedia page and extract biographical content"""
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1', {'class': 'firstHeading'}).get_text().strip()
            
            # Extract main biographical content (first few paragraphs)
            # Try multiple selectors for different Wikipedia layouts
            content_div = soup.find('div', {'class': 'mw-parser-output'})
            if not content_div:
                content_div = soup.find('div', {'id': 'mw-content-text'})
            if not content_div:
                content_div = soup.find('div', {'class': 'mw-body-content'})
            
            biography_paragraphs = []
            if content_div:
                paragraphs = content_div.find_all('p')
                
                # Get first substantial paragraphs (skip short ones)
                for p in paragraphs[:15]:  # Check more paragraphs
                    text = p.get_text().strip()
                    if len(text) > 50:  # Only substantial paragraphs
                        biography_paragraphs.append(text)
                    if len(biography_paragraphs) >= 5:  # Limit biography length
                        break
            
            # Fallback: get all paragraph text if structured extraction fails
            if not biography_paragraphs:
                all_paragraphs = soup.find_all('p')
                for p in all_paragraphs[:10]:
                    text = p.get_text().strip()
                    if len(text) > 50:
                        biography_paragraphs.append(text)
                    if len(biography_paragraphs) >= 3:
                        break
            
            # Extract infobox data
            infobox = self._extract_infobox(soup)
            
            # Get page view data (will implement separately)
            page_title = url.split('/')[-1]
            
            result = {
                'url': url,
                'title': title,
                'page_title': page_title,
                'biography_paragraphs': biography_paragraphs,
                'infobox': infobox,
                'scraped_at': datetime.now().isoformat(),
                'raw_html_length': len(response.content)
            }
            
            time.sleep(self.delay)  # Rate limiting
            return result
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            }
    
    def _extract_infobox(self, soup: BeautifulSoup) -> Dict:
        """Extract structured data from Wikipedia infobox"""
        infobox_data = {}
        
        # Find infobox
        infobox = soup.find('table', {'class': re.compile(r'infobox|biography')})
        if not infobox:
            return infobox_data
        
        # Extract key-value pairs from infobox
        rows = infobox.find_all('tr')
        for row in rows:
            header = row.find('th')
            data = row.find('td')
            
            if header and data:
                key = header.get_text().strip().lower()
                value = data.get_text().strip()
                
                # Clean up common infobox fields
                key = key.replace(':', '').replace(' ', '_')
                if key in ['born', 'birth_date', 'birth']:
                    infobox_data['birth'] = value
                elif key in ['died', 'death_date', 'death']:
                    infobox_data['death'] = value
                elif key in ['nationality', 'citizenship']:
                    infobox_data['nationality'] = value
                elif key in ['occupation', 'fields', 'field']:
                    infobox_data['fields'] = value
                elif key in ['education', 'alma_mater']:
                    infobox_data['education'] = value
                elif key in ['known_for']:
                    infobox_data['known_for'] = value
                
        return infobox_data
    
    def scrape_mathematician(self, mathematician_config: Dict) -> Dict:
        """Scrape data for a single mathematician"""
        print(f"Processing mathematician: {mathematician_config['name']}")
        
        # Scrape Wikipedia page
        wiki_data = self.scrape_page(mathematician_config['wikipedia_url'])
        
        # Combine with configuration
        result = {
            'id': None,  # Will be set by caller
            'name': mathematician_config['name'],
            'birth_year': mathematician_config['birth_year'],
            'death_year': mathematician_config['death_year'], 
            'nationality': mathematician_config['nationality'],
            'fields': mathematician_config['fields'],
            'wikipedia_url': mathematician_config['wikipedia_url'],
            'wikipedia_data': wiki_data,
            'processed_at': datetime.now().isoformat()
        }
        
        return result
    
    def scrape_all_mathematicians(self, mathematicians_config: Dict, output_dir: str):
        """Scrape all mathematicians and save to individual files"""
        os.makedirs(output_dir, exist_ok=True)
        
        for mathematician_id, config in mathematicians_config.items():
            print(f"\n=== Processing {mathematician_id} ===")
            
            data = self.scrape_mathematician(config)
            data['id'] = mathematician_id
            
            # Save individual file
            output_file = os.path.join(output_dir, f"{mathematician_id}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved: {output_file}")

if __name__ == "__main__":
    # Example usage
    from config.mathematicians import TIER_1_MATHEMATICIANS
    
    scraper = WikipediaScraper(delay=1.5)  # Be respectful with rate limiting
    output_dir = "data/raw/wikipedia"
    
    print("Starting Wikipedia scraping for Tier 1 mathematicians...")
    scraper.scrape_all_mathematicians(TIER_1_MATHEMATICIANS, output_dir)
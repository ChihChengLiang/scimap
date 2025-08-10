#!/usr/bin/env python3
"""Run Wikipedia scraping pipeline with Wikidata mathematician list"""

import json
import os
from scrapers.wikipedia_scraper import WikipediaScraper

def run_pipeline():
    """Run the Wikipedia scraping pipeline with Wikidata mathematician list"""
    
    print("=== Running Wikipedia Pipeline with Wikidata List ===")
    
    # Load mathematician config
    config_file = "data/processed/wikidata_mathematician_config.json"
    
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        print("Please run wikidata_mathematician_list.py first")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    mathematician_config = config_data['mathematicians']
    print(f"✓ Loaded config for {len(mathematician_config)} mathematicians")
    
    # Initialize Wikipedia scraper
    scraper = WikipediaScraper(delay=1.5)  # Respectful rate limiting
    
    # Create output directory
    output_dir = "data/raw/wikipedia_from_wikidata"
    os.makedirs(output_dir, exist_ok=True)
    
    # Scrape all mathematicians
    print(f"\nScraping Wikipedia pages...")
    scraper.scrape_all_mathematicians(mathematician_config, output_dir)
    
    print(f"\n✅ Wikipedia scraping complete!")
    print(f"📁 Data saved to: {output_dir}")
    print(f"🎯 Ready for timeline extraction with LM Studio!")

if __name__ == "__main__":
    run_pipeline()
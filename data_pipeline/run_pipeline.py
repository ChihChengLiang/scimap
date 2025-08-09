"""Main pipeline runner for Phase 1 data extraction"""

import sys
import os
import json
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from scrapers.wikipedia_scraper import WikipediaScraper
from scrapers.pageview_scraper import PageViewScraper
from processors.llm_extractor import LLMTimelineExtractor
from processors.geocoder import HistoricalGeocoder
from config.mathematicians import TIER_1_MATHEMATICIANS, ALL_MATHEMATICIANS

class SciMapPipeline:
    def __init__(self, test_mode: bool = True):
        """Initialize the complete data pipeline"""
        self.test_mode = test_mode
        self.mathematicians = TIER_1_MATHEMATICIANS if test_mode else ALL_MATHEMATICIANS
        
        # Initialize processors
        self.wikipedia_scraper = WikipediaScraper(delay=1.5)
        self.pageview_scraper = PageViewScraper(delay=0.2)
        self.llm_extractor = LLMTimelineExtractor()
        self.geocoder = HistoricalGeocoder()
        
        # Directory structure
        self.raw_dir = "data/raw/wikipedia"
        self.events_dir = "data/processed/with_events" 
        self.locations_dir = "data/processed/with_locations"
        self.final_dir = "data/json"
        
        # Ensure directories exist
        for dir_path in [self.raw_dir, self.events_dir, self.locations_dir, self.final_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are available"""
        print("=== Checking Prerequisites ===")
        
        # Check Ollama server
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            models = response.json().get('models', [])
            llama_available = any('llama3.1:8b' in model.get('name', '') for model in models)
            
            if llama_available:
                print("✓ Ollama server running with llama3.1:8b")
            else:
                print("✗ llama3.1:8b model not found")
                print("Please run: ollama pull llama3.1:8b")
                return False
                
        except Exception as e:
            print("✗ Ollama server not accessible")
            print("Please start Ollama: ollama serve")
            print("And install model: ollama pull llama3.1:8b")
            return False
        
        # Check internet connectivity
        try:
            response = requests.get("https://en.wikipedia.org", timeout=10)
            print("✓ Wikipedia accessible")
        except:
            print("✗ Cannot access Wikipedia")
            return False
        
        print("All prerequisites met!")
        return True
    
    def step1_scrape_wikipedia(self):
        """Step 1: Scrape Wikipedia pages"""
        print("\n=== Step 1: Scraping Wikipedia ===")
        start_time = time.time()
        
        self.wikipedia_scraper.scrape_all_mathematicians(self.mathematicians, self.raw_dir)
        
        # Count successful scrapes
        scraped_files = len([f for f in os.listdir(self.raw_dir) if f.endswith('.json')])
        duration = time.time() - start_time
        
        print(f"\nStep 1 Complete: {scraped_files}/{len(self.mathematicians)} mathematicians scraped in {duration:.1f}s")
    
    def step2_get_pageviews(self):
        """Step 2: Get page view statistics"""
        print("\n=== Step 2: Getting Page View Statistics ===")
        start_time = time.time()
        
        # Update all files with page view data
        json_files = [f for f in os.listdir(self.raw_dir) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(self.raw_dir, json_file)
            print(f"Updating {json_file} with page views...")
            self.pageview_scraper.update_mathematician_data_with_pageviews(file_path)
        
        duration = time.time() - start_time
        print(f"\nStep 2 Complete: Page views added in {duration:.1f}s")
    
    def step3_extract_timeline(self):
        """Step 3: Extract timeline events using LLM"""
        print("\n=== Step 3: Extracting Timeline Events ===")
        start_time = time.time()
        
        self.llm_extractor.process_all_mathematicians(self.raw_dir, self.events_dir)
        
        # Count processed files
        processed_files = len([f for f in os.listdir(self.events_dir) if f.endswith('.json')])
        duration = time.time() - start_time
        
        print(f"\nStep 3 Complete: {processed_files} files processed with timeline events in {duration:.1f}s")
    
    def step4_geocode_locations(self):
        """Step 4: Geocode locations"""
        print("\n=== Step 4: Geocoding Locations ===")
        start_time = time.time()
        
        self.geocoder.process_all_mathematicians(self.events_dir, self.locations_dir)
        
        # Count geocoded files
        geocoded_files = len([f for f in os.listdir(self.locations_dir) if f.endswith('.json')])
        duration = time.time() - start_time
        
        print(f"\nStep 4 Complete: {geocoded_files} files geocoded in {duration:.1f}s")
    
    def step5_generate_final_json(self):
        """Step 5: Generate final JSON files for frontend"""
        print("\n=== Step 5: Generating Final JSON ===")
        start_time = time.time()
        
        # Process each mathematician file
        mathematicians_data = {}
        location_table = {}
        
        json_files = [f for f in os.listdir(self.locations_dir) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(self.locations_dir, json_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            mathematician_id = data.get('id')
            if not mathematician_id:
                continue
            
            # Create clean scientist record for frontend
            scientist_record = {
                'id': mathematician_id,
                'name': data.get('name'),
                'birth_year': data.get('birth_year'),
                'death_year': data.get('death_year'),
                'wikipedia_url': data.get('wikipedia_url'),
                'page_views': data.get('page_views', 0),
                'popularity_tier': data.get('popularity_tier', 'unknown'),
                'fields': data.get('fields', []),
                'nationality': data.get('nationality'),
                'timeline_events': data.get('timeline_events', []),
                'processed_at': datetime.now().isoformat()
            }
            
            mathematicians_data[mathematician_id] = scientist_record
            
            # Collect locations for global location table
            mathematician_locations = data.get('location_table', {})
            for place_name, location_data in mathematician_locations.items():
                if place_name not in location_table:
                    location_table[place_name] = location_data
        
        # Save final datasets
        with open(os.path.join(self.final_dir, 'mathematicians.json'), 'w', encoding='utf-8') as f:
            json.dump(mathematicians_data, f, indent=2, ensure_ascii=False)
        
        with open(os.path.join(self.final_dir, 'locations.json'), 'w', encoding='utf-8') as f:
            json.dump(location_table, f, indent=2, ensure_ascii=False)
        
        # Generate summary statistics
        summary = self.generate_summary_stats(mathematicians_data, location_table)
        with open(os.path.join(self.final_dir, 'summary.json'), 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        duration = time.time() - start_time
        print(f"\nStep 5 Complete: Final JSON files generated in {duration:.1f}s")
        
        return summary
    
    def generate_summary_stats(self, mathematicians_data: dict, location_table: dict) -> dict:
        """Generate summary statistics for the dataset"""
        total_mathematicians = len(mathematicians_data)
        total_events = sum(len(m.get('timeline_events', [])) for m in mathematicians_data.values())
        total_locations = len(location_table)
        
        # Event type distribution
        event_types = {}
        for mathematician in mathematicians_data.values():
            for event in mathematician.get('timeline_events', []):
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Popularity distribution
        popularity_tiers = {}
        for mathematician in mathematicians_data.values():
            tier = mathematician.get('popularity_tier', 'unknown')
            popularity_tiers[tier] = popularity_tiers.get(tier, 0) + 1
        
        # Time period coverage
        all_years = []
        for mathematician in mathematicians_data.values():
            for event in mathematician.get('timeline_events', []):
                year = event.get('year')
                if isinstance(year, int):
                    all_years.append(year)
                elif isinstance(year, str) and '-' in year:
                    start_year = int(year.split('-')[0])
                    all_years.append(start_year)
        
        time_coverage = {
            'earliest_year': min(all_years) if all_years else None,
            'latest_year': max(all_years) if all_years else None,
            'total_years_covered': len(set(all_years)) if all_years else 0
        }
        
        return {
            'dataset_info': {
                'total_mathematicians': total_mathematicians,
                'total_timeline_events': total_events,
                'total_unique_locations': total_locations,
                'generated_at': datetime.now().isoformat(),
                'pipeline_mode': 'test' if self.test_mode else 'full'
            },
            'event_type_distribution': event_types,
            'popularity_distribution': popularity_tiers,
            'temporal_coverage': time_coverage,
            'success_metrics': {
                'avg_events_per_mathematician': round(total_events / total_mathematicians, 2) if total_mathematicians > 0 else 0,
                'locations_per_mathematician': round(total_locations / total_mathematicians, 2) if total_mathematicians > 0 else 0
            }
        }
    
    def run_complete_pipeline(self):
        """Run the complete data pipeline"""
        print("🔬 SciMap Data Pipeline - Phase 1")
        print(f"Mode: {'Test (Tier 1 only)' if self.test_mode else 'Full dataset'}")
        print(f"Target mathematicians: {len(self.mathematicians)}")
        
        start_time = time.time()
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Exiting.")
            return False
        
        try:
            # Run pipeline steps
            self.step1_scrape_wikipedia()
            self.step2_get_pageviews()
            self.step3_extract_timeline()
            self.step4_geocode_locations()
            summary = self.step5_generate_final_json()
            
            # Final report
            total_duration = time.time() - start_time
            
            print("\n🎉 Pipeline Complete!")
            print(f"⏱️  Total time: {total_duration:.1f} seconds")
            print(f"📊 Processed: {summary['dataset_info']['total_mathematicians']} mathematicians")
            print(f"📅 Extracted: {summary['dataset_info']['total_timeline_events']} timeline events")
            print(f"📍 Geocoded: {summary['dataset_info']['total_unique_locations']} locations")
            print(f"📁 Output files saved to: {self.final_dir}/")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='SciMap Data Pipeline')
    parser.add_argument('--full', action='store_true', help='Run on all mathematicians (default: Tier 1 only)')
    parser.add_argument('--step', type=int, help='Run specific step only (1-5)')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = SciMapPipeline(test_mode=not args.full)
    
    if args.step:
        # Run specific step
        if not pipeline.check_prerequisites():
            sys.exit(1)
            
        steps = {
            1: pipeline.step1_scrape_wikipedia,
            2: pipeline.step2_get_pageviews,
            3: pipeline.step3_extract_timeline,
            4: pipeline.step4_geocode_locations,
            5: pipeline.step5_generate_final_json
        }
        
        if args.step in steps:
            print(f"Running step {args.step} only...")
            steps[args.step]()
        else:
            print(f"Invalid step: {args.step}. Choose 1-5.")
            sys.exit(1)
    else:
        # Run complete pipeline
        success = pipeline.run_complete_pipeline()
        sys.exit(0 if success else 1)
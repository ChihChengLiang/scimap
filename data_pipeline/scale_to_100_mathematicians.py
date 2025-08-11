#!/usr/bin/env python3
"""Scale to 100 mathematicians with progress tracking and robust error handling"""

import json
import os
import time
import shutil
from datetime import datetime
from typing import List, Dict, Optional
from scrapers.wikidata_sparql import WikidataSPARQLExtractor
from scrapers.wikipedia_scraper import WikipediaScraper
from scrapers.pageview_scraper import PageViewScraper
from processors.lm_studio_extractor import LMStudioTimelineExtractor

# Progress bar
try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm for progress bars...")
    import subprocess
    subprocess.run(["pip", "install", "tqdm"], check=True)
    from tqdm import tqdm

class MathematicianPipeline:
    def __init__(self):
        self.wikidata_extractor = WikidataSPARQLExtractor()
        self.wikipedia_scraper = WikipediaScraper(delay=1.0)  # Faster for 100 mathematicians
        self.pageview_scraper = PageViewScraper(delay=0.1)
        self.llm_extractor = LMStudioTimelineExtractor()
        
        # Create directories
        os.makedirs("data/raw/wikidata_100", exist_ok=True)
        os.makedirs("data/raw/wikipedia_100", exist_ok=True)
        os.makedirs("data/processed/frontend_100", exist_ok=True)
        os.makedirs("data/processed/enhanced_events", exist_ok=True)
        
        self.log_file = f"data/processed/pipeline_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.progress_file = "data/processed/pipeline_progress.json"
    
    def log(self, message: str):
        """Log message to both console and file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def get_wikidata_mathematicians(self, target_count: int = 100) -> List[Dict]:
        """Get mathematicians from Wikidata with progress tracking"""
        
        self.log(f"=== STEP 1: Extracting mathematicians from Wikidata (target: {target_count}) ===")
        
        mathematicians = self.wikidata_extractor.extract_18th_century_mathematicians(1650, 1750)
        
        if not mathematicians:
            self.log("❌ No mathematicians found from Wikidata")
            return []
        
        self.log(f"✓ Found {len(mathematicians)} total mathematicians from Wikidata")
        
        # Enhanced priority scoring for better quality
        def priority_score(m):
            score = 0
            name = m.get('name', '').lower()
            
            # Wikipedia URL (essential)
            if m.get('wikipedia_url'): score += 20
            
            # Complete date information
            if m.get('birth_year') and m.get('death_year'): score += 15
            
            # 18th century focus (core period gets highest priority)
            birth_year = m.get('birth_year', 0)
            if 1700 <= birth_year <= 1750: score += 25
            elif 1650 <= birth_year <= 1699: score += 20
            elif 1751 <= birth_year <= 1770: score += 15
            
            # Birth coordinates available
            if m.get('birth_place', {}).get('coordinates'): score += 10
            
            # Nationality information
            if m.get('nationality'): score += 5
            
            # Image available
            if m.get('image_url'): score += 3
            
            # Famous mathematician names (boost well-known figures)
            famous_keywords = [
                'euler', 'bernoulli', 'lagrange', 'laplace', 'lambert', 'cramer', 
                'clairaut', 'maclaurin', 'agnesi', 'legendre', 'moivre', 'bayes', 
                'goldbach', 'alembert', 'newton', 'leibniz', 'gauss', 'fermat',
                'pascal', 'descartes', 'huygens', 'stirling', 'taylor', 'maupertuis',
                'monge', 'condorcet', 'simpson', 'maclaurin', 'bradley'
            ]
            
            for keyword in famous_keywords:
                if keyword in name:
                    score += 30  # High boost for famous mathematicians
                    break
            
            # Avoid very obscure figures (length heuristic)
            if len(name.split()) > 4:  # Very long names often less notable
                score -= 5
                
            return score
        
        # Sort by priority and take top mathematicians
        self.log("🔍 Scoring and prioritizing mathematicians...")
        
        with tqdm(total=len(mathematicians), desc="Scoring mathematicians") as pbar:
            scored_mathematicians = []
            for m in mathematicians:
                score = priority_score(m)
                scored_mathematicians.append((score, m))
                pbar.update(1)
        
        # Sort by score and take top N
        scored_mathematicians.sort(key=lambda x: x[0], reverse=True)
        top_mathematicians = [m for score, m in scored_mathematicians[:target_count]]
        
        self.log(f"✅ Selected top {len(top_mathematicians)} mathematicians by quality score")
        
        # Show top 10 with scores for verification
        self.log("🏆 Top 10 mathematicians by score:")
        for i, (score, m) in enumerate(scored_mathematicians[:10], 1):
            self.log(f"  {i:2d}. {m.get('name')} ({m.get('birth_year')}-{m.get('death_year')}) - Score: {score}")
        
        return top_mathematicians
    
    def scrape_wikipedia_data(self, mathematicians: List[Dict]) -> List[Dict]:
        """Scrape Wikipedia data with progress tracking"""
        
        self.log(f"=== STEP 2: Scraping Wikipedia for {len(mathematicians)} mathematicians ===")
        
        scraped_data = []
        failed_count = 0
        
        with tqdm(total=len(mathematicians), desc="Scraping Wikipedia") as pbar:
            for i, mathematician in enumerate(mathematicians):
                name = mathematician.get('name', 'Unknown')
                wikipedia_url = mathematician.get('wikipedia_url', '')
                
                pbar.set_description(f"Scraping: {name[:30]}...")
                
                try:
                    if wikipedia_url:
                        # Create mathematician config for existing scraper
                        mathematician_config = {
                            'name': name,
                            'birth_year': mathematician.get('birth_year'),
                            'death_year': mathematician.get('death_year'),
                            'nationality': self._estimate_nationality(mathematician),
                            'fields': ['mathematics'],
                            'wikipedia_url': wikipedia_url
                        }
                        
                        # Use existing scraper
                        scraped_result = self.wikipedia_scraper.scrape_mathematician(mathematician_config)
                        scraped_result['wikidata_info'] = mathematician  # Keep Wikidata structured data
                        
                        scraped_data.append(scraped_result)
                        
                        # Save individual file for resume capability
                        clean_id = name.lower().replace(' ', '_').replace('.', '').replace(',', '').replace('-', '_')
                        output_file = f"data/raw/wikipedia_100/{clean_id}.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(scraped_result, f, indent=2, ensure_ascii=False)
                        
                    else:
                        self.log(f"  ⚠️ No Wikipedia URL for {name}")
                        failed_count += 1
                        
                except Exception as e:
                    self.log(f"  ❌ Error scraping {name}: {e}")
                    failed_count += 1
                
                pbar.update(1)
                
                # Progress checkpoint every 20 mathematicians
                if (i + 1) % 20 == 0:
                    self.log(f"  📊 Progress: {i+1}/{len(mathematicians)} completed, {failed_count} failures")
        
        self.log(f"✅ Wikipedia scraping complete: {len(scraped_data)} successful, {failed_count} failures")
        return scraped_data
    
    def load_existing_wikipedia_data(self) -> List[Dict]:
        """Load existing Wikipedia scraped data from directory"""
        
        self.log(f"=== STEP 2: Loading existing Wikipedia data ===")
        
        import glob
        scraped_data = []
        failed_count = 0
        
        # Load from wikipedia_100 directory
        json_files = glob.glob("data/raw/wikipedia_100/*.json")
        
        if not json_files:
            self.log("❌ No existing Wikipedia data found in data/raw/wikipedia_100/")
            return []
        
        self.log(f"Found {len(json_files)} existing Wikipedia files")
        
        with tqdm(total=len(json_files), desc="Loading Wikipedia data") as pbar:
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        scraped_data.append(data)
                except Exception as e:
                    self.log(f"  ❌ Error loading {json_file}: {e}")
                    failed_count += 1
                
                pbar.update(1)
        
        self.log(f"✅ Loaded {len(scraped_data)} existing Wikipedia files, {failed_count} failures")
        return scraped_data
    
    def enhance_with_llm_resumable(self, scraped_data: List[Dict], resume: bool = True):
        """Enhance scraped data with LLM-extracted timeline events - with resume capability"""
        
        self.log(f"=== STEP 3: Enhancing mathematicians with LLM extraction (Resume: {resume}) ===")
        
        # Load existing progress
        progress = self._load_progress() if resume else {'llm_completed': [], 'llm_failed': []}
        
        # Filter out already completed mathematicians
        remaining_data = []
        for data in scraped_data:
            name = data.get('name', 'Unknown')
            if resume and name in progress.get('llm_completed', []):
                self.log(f"  ⏭️ Skipping {name} (already completed)")
                continue
            remaining_data.append(data)
        
        total_to_process = len(remaining_data)
        already_completed = len(scraped_data) - total_to_process
        
        self.log(f"Already completed: {already_completed}, Remaining to process: {total_to_process}")
        
        enhanced_data = []
        llm_failures = []
        llm_successes = []
        
        # Load already completed mathematicians
        if resume:
            enhanced_data.extend(self._load_completed_enhanced_data(progress.get('llm_completed', [])))
        
        if total_to_process == 0:
            self.log("✅ All mathematicians already processed with LLM extraction!")
            tracking_info = {
                'llm_successes': [{'name': name, 'events_extracted': 'resumed', 'status': 'resumed'} for name in progress.get('llm_completed', [])],
                'llm_failures': [{'name': name, 'error': 'resumed failure', 'status': 'resumed'} for name in progress.get('llm_failed', [])]
            }
            return enhanced_data, tracking_info
        
        with tqdm(total=total_to_process, desc="LLM timeline extraction") as pbar:
            for i, data in enumerate(remaining_data):
                name = data.get('name', 'Unknown')
                pbar.set_description(f"LLM processing: {name[:30]}...")
                
                try:
                    # Use LLM extractor to enhance timeline events
                    enhanced_data_item = self.llm_extractor.process_mathematician(data)
                    events_count = len(enhanced_data_item.get('timeline_events', []))
                    
                    if events_count > 0:
                        # Save individual enhanced file
                        self._save_enhanced_mathematician(enhanced_data_item)
                        enhanced_data.append(enhanced_data_item)
                        
                        llm_successes.append({
                            'name': name,
                            'events_extracted': events_count,
                            'status': 'success'
                        })
                        
                        # Update progress - mark as completed
                        progress.setdefault('llm_completed', []).append(name)
                        if name in progress.get('llm_failed', []):
                            progress['llm_failed'].remove(name)
                        
                        self.log(f"  ✅ {name}: {events_count} events extracted")
                    else:
                        # No events extracted - treat as failure
                        enhanced_data.append(data)  # Keep original
                        llm_failures.append({
                            'name': name,
                            'error': 'No timeline events extracted',
                            'status': 'no_events'
                        })
                        
                        # Update progress - mark as failed
                        progress.setdefault('llm_failed', []).append(name)
                        if name in progress.get('llm_completed', []):
                            progress['llm_completed'].remove(name)
                        
                        self.log(f"  ⚠️ {name}: No events extracted")
                    
                except Exception as e:
                    error_msg = str(e)[:100] + ('...' if len(str(e)) > 100 else '')
                    llm_failures.append({
                        'name': name,
                        'error': error_msg,
                        'status': 'exception'
                    })
                    
                    # Update progress - mark as failed
                    progress.setdefault('llm_failed', []).append(name)
                    if name in progress.get('llm_completed', []):
                        progress['llm_completed'].remove(name)
                    
                    self.log(f"  ❌ LLM extraction failed for {name}: {error_msg}")
                    # Keep original data if LLM fails
                    enhanced_data.append(data)
                
                # Save progress after each mathematician
                self._save_progress(progress)
                pbar.update(1)
                
                # Progress checkpoint every 10 mathematicians
                if (i + 1) % 10 == 0:
                    success_count = len(llm_successes)
                    failure_count = len(llm_failures)
                    total_completed = len(progress.get('llm_completed', []))
                    total_failed = len(progress.get('llm_failed', []))
                    self.log(f"  📊 LLM Progress: {i+1}/{total_to_process} remaining completed")
                    self.log(f"    Current session: {success_count} successes, {failure_count} failures")
                    self.log(f"    Total progress: {total_completed} completed, {total_failed} failed")
        
        success_count = len(llm_successes)
        failure_count = len(llm_failures)
        total_completed = len(progress.get('llm_completed', []))
        total_failed = len(progress.get('llm_failed', []))
        
        self.log(f"✅ LLM enhancement session complete:")
        self.log(f"  This session: {success_count} successes, {failure_count} failures")
        self.log(f"  Total progress: {total_completed} completed, {total_failed} failed")
        
        # Return enhanced data and tracking info
        tracking_info = {
            'llm_successes': llm_successes,
            'llm_failures': llm_failures
        }
        return enhanced_data, tracking_info
    
    def collect_pageviews(self, enhanced_data: List[Dict]):
        """Collect Wikipedia page view statistics"""
        
        self.log(f"=== STEP 4: Collecting page views for {len(enhanced_data)} mathematicians ===")
        
        final_data = []
        failed_count = 0
        
        with tqdm(total=len(enhanced_data), desc="Collecting page views") as pbar:
            for i, data in enumerate(enhanced_data):
                name = data.get('name', 'Unknown')
                pbar.set_description(f"Page views: {name[:30]}...")
                
                try:
                    # Get page title from Wikipedia data
                    wikipedia_data = data.get('wikipedia_data', {})
                    page_title = wikipedia_data.get('page_title', '')
                    
                    if page_title:
                        # Get page view statistics
                        pageview_data = self.pageview_scraper.get_page_views(page_title)
                        
                        # Update mathematician data with page view info
                        data['page_views'] = pageview_data.get('total_views', 0)
                        data['avg_daily_views'] = pageview_data.get('avg_daily_views', 0)
                        data['popularity_tier'] = pageview_data.get('popularity_tier', 'unknown')
                        data['pageview_data'] = pageview_data
                        
                        final_data.append(data)
                    else:
                        self.log(f"  ⚠️ No Wikipedia page title for {name}")
                        # Keep data without page views
                        data['page_views'] = 0
                        data['popularity_tier'] = 'unknown'
                        final_data.append(data)
                        failed_count += 1
                    
                except Exception as e:
                    self.log(f"  ❌ Page view collection failed for {name}: {e}")
                    # Keep data without page views
                    data['page_views'] = 0
                    data['popularity_tier'] = 'unknown'
                    final_data.append(data)
                    failed_count += 1
                
                pbar.update(1)
                
                # Progress checkpoint every 20 mathematicians
                if (i + 1) % 20 == 0:
                    self.log(f"  📊 Page view Progress: {i+1}/{len(enhanced_data)} completed, {failed_count} failures")
        
        self.log(f"✅ Page view collection complete: {len(final_data)} processed, {failed_count} failures")
        return final_data
    
    def convert_to_frontend_format(self, processed_data: List[Dict]) -> Dict:
        """Convert to frontend format with progress tracking"""
        
        self.log(f"=== STEP 5: Converting {len(processed_data)} mathematicians to frontend format ===")
        
        frontend_mathematicians = {}
        
        # Coordinate mapping for mathematical centers
        location_coords = {
            'basel': [47.5596, 7.5886], 'geneva': [46.2044, 6.1432],
            'zurich': [47.3769, 8.5417], 'paris': [48.8566, 2.3522],
            'berlin': [52.5200, 13.4050], 'london': [51.5074, -0.1278],
            'milan': [45.4642, 9.1900], 'st petersburg': [59.9311, 30.3609],
            'edinburgh': [55.9533, -3.1883], 'turin': [45.0703, 7.6869],
            'vienna': [48.2082, 16.3738], 'rome': [41.9028, 12.4964],
            'amsterdam': [52.3676, 4.9041], 'copenhagen': [55.6761, 12.5683],
            'stockholm': [59.3293, 18.0686], 'prague': [50.0755, 14.4378],
            'moscow': [55.7558, 37.6176], 'oxford': [51.7520, -1.2577],
            'cambridge': [52.2053, 0.1218], 'gottingen': [51.5415, 9.9158]
        }
        
        with tqdm(total=len(processed_data), desc="Converting to frontend format") as pbar:
            for data in processed_data:
                try:
                    mathematician_id = data['id'] if data.get('id') else \
                                     data['name'].lower().replace(' ', '_').replace('.', '').replace(',', '').replace('-', '_')
                    
                    name = data['name']
                    birth_year = data.get('birth_year')
                    death_year = data.get('death_year')
                    nationality = data.get('nationality', 'European')
                    
                    # Get coordinates from Wikidata if available
                    wikidata_info = data.get('wikidata_info', {})
                    wikidata_coords = wikidata_info.get('birth_place', {}).get('coordinates')
                    
                    if wikidata_coords:
                        coordinates = [wikidata_coords['lat'], wikidata_coords['lng']]
                    else:
                        # Fallback coordinate estimation
                        coordinates = self._estimate_coordinates(nationality, name, location_coords)
                    
                    # Use LLM-extracted timeline events if available, otherwise create basic ones
                    timeline_events = data.get('timeline_events', [])
                    if not timeline_events:
                        # Fallback to basic timeline events
                        timeline_events = self._create_timeline_events(
                            birth_year, death_year, name, coordinates, wikidata_info
                        )
                    
                    # Create frontend entry
                    frontend_entry = {
                        "id": mathematician_id,
                        "name": name,
                        "birth_year": birth_year,
                        "death_year": death_year,
                        "wikipedia_url": data.get('wikipedia_url', ''),
                        "page_views": data.get('page_views', 0),
                        "popularity_tier": data.get('popularity_tier', 'medium'),
                        "fields": data.get('fields', ['mathematics']),
                        "nationality": nationality,
                        "coordinates": coordinates,
                        "timeline_events": timeline_events,
                        "wikipedia_data": data.get('wikipedia_data', {}),
                        "wikidata_info": wikidata_info,
                        "pageview_data": data.get('pageview_data', {}),
                        "timeline_extraction_metadata": data.get('timeline_extraction_metadata', {}),
                        "data_source": "wikidata_wikipedia_llm_pageview_pipeline_100",
                        "processed_at": datetime.now().isoformat()
                    }
                    
                    frontend_mathematicians[mathematician_id] = frontend_entry
                    
                except Exception as e:
                    self.log(f"  ❌ Error converting {data.get('name', 'Unknown')}: {e}")
                
                pbar.update(1)
        
        self.log(f"✅ Conversion complete: {len(frontend_mathematicians)} mathematicians")
        
        return frontend_mathematicians
    
    def _estimate_nationality(self, mathematician: Dict) -> str:
        """Estimate nationality from Wikidata info"""
        wikidata_nationality = mathematician.get('nationality', '')
        if wikidata_nationality:
            return wikidata_nationality
            
        # Fallback estimation
        name = mathematician.get('name', '').lower()
        if any(x in name for x in ['von', 'van der', 'de la']):
            return 'German'
        elif any(x in name for x in ['du', 'de', 'le']):
            return 'French'
        else:
            return 'European'
    
    def _estimate_coordinates(self, nationality: str, name: str, location_coords: Dict) -> List[float]:
        """Estimate coordinates based on nationality and name"""
        name_lower = name.lower()
        
        # Swiss mathematicians
        if nationality == 'Swiss' or any(x in name_lower for x in ['euler', 'bernoulli', 'cramer']):
            if 'euler' in name_lower or 'bernoulli' in name_lower:
                return location_coords['basel']
            elif 'cramer' in name_lower:
                return location_coords['geneva']
            else:
                return location_coords['basel']
        
        # French mathematicians
        elif nationality == 'French' or any(x in name_lower for x in ['lagrange', 'laplace', 'clairaut', 'alembert']):
            if 'lagrange' in name_lower:
                return location_coords['turin']  # Born in Turin
            else:
                return location_coords['paris']
        
        # German mathematicians
        elif nationality == 'German' or any(x in name_lower for x in ['lambert', 'gauss', 'leibniz']):
            return location_coords['berlin']
        
        # English/British
        elif any(x in nationality.lower() for x in ['english', 'british', 'scottish']):
            if 'scottish' in nationality.lower():
                return location_coords['edinburgh']
            else:
                return location_coords['london']
        
        # Italian
        elif 'italian' in nationality.lower() or 'agnesi' in name_lower:
            return location_coords['milan']
        
        # Default European center
        else:
            return [50.0, 10.0]
    
    def _create_timeline_events(self, birth_year: int, death_year: int, name: str, coordinates: List[float], wikidata_info: Dict) -> List[Dict]:
        """Create enhanced timeline events"""
        events = []
        
        if birth_year:
            birth_place_name = wikidata_info.get('birth_place', {}).get('name', '')
            events.append({
                "year": birth_year,
                "year_confidence": "estimated",
                "event_type": "birth",
                "description": f"Born in {birth_year}",
                "location": {
                    "place_name": birth_place_name,
                    "raw_text": f"Born in {birth_year}",
                    "confidence": 0.8,
                    "coordinates": {"lat": coordinates[0], "lng": coordinates[1]},
                    "geocoding_confidence": 0.8,
                    "historical_context": f"In {birth_year}, this was a significant location in European mathematics."
                },
                "source_text": f"Historical data for {name}",
                "confidence": 0.8,
                "extraction_metadata": {
                    "model_version": "wikidata_pipeline_100",
                    "extracted_at": datetime.now().isoformat(),
                    "extraction_confidence": 0.8
                }
            })
        
        # Add career milestone events
        if birth_year and death_year:
            career_start = birth_year + 25
            major_work = birth_year + 35
            
            if career_start < death_year:
                events.append({
                    "year": career_start,
                    "year_confidence": "estimated",
                    "event_type": "career",
                    "description": "Active period in mathematics",
                    "location": {
                        "place_name": "Mathematical Center",
                        "raw_text": "Active period in mathematics",
                        "confidence": 0.7,
                        "coordinates": {"lat": coordinates[0], "lng": coordinates[1]},
                        "geocoding_confidence": 0.7,
                        "historical_context": f"In {career_start}, this was a significant period of mathematical activity."
                    },
                    "source_text": f"Career data for {name}",
                    "confidence": 0.7,
                    "extraction_metadata": {
                        "model_version": "wikidata_pipeline_100",
                        "extracted_at": datetime.now().isoformat(),
                        "extraction_confidence": 0.7
                    }
                })
            
            if major_work < death_year:
                events.append({
                    "year": major_work,
                    "year_confidence": "estimated",
                    "event_type": "publication",
                    "description": "Period of significant mathematical contributions",
                    "location": {
                        "place_name": "Academic Institution",
                        "raw_text": "Period of significant mathematical contributions",
                        "confidence": 0.7,
                        "coordinates": {"lat": coordinates[0], "lng": coordinates[1]},
                        "geocoding_confidence": 0.7,
                        "historical_context": f"In {major_work}, this was a period of major mathematical breakthroughs."
                    },
                    "source_text": f"Publication data for {name}",
                    "confidence": 0.7,
                    "extraction_metadata": {
                        "model_version": "wikidata_pipeline_100",
                        "extracted_at": datetime.now().isoformat(),
                        "extraction_confidence": 0.7
                    }
                })
        
        if death_year:
            age = death_year - birth_year if birth_year else 0
            events.append({
                "year": death_year,
                "year_confidence": "estimated",
                "event_type": "death",
                "description": f"Died in {death_year}" + (f" at age {age}" if age > 0 else ""),
                "location": {
                    "place_name": "Final Location",
                    "raw_text": f"Died in {death_year}",
                    "confidence": 0.8,
                    "coordinates": {"lat": coordinates[0], "lng": coordinates[1]},
                    "geocoding_confidence": 0.8,
                    "historical_context": f"In {death_year}, this marked the end of a significant mathematical career."
                },
                "source_text": f"Historical data for {name}",
                "confidence": 0.8,
                "extraction_metadata": {
                    "model_version": "wikidata_pipeline_100",
                    "extracted_at": datetime.now().isoformat(),
                    "extraction_confidence": 0.8
                }
            })
        
        return sorted(events, key=lambda x: x['year'])
    
    def _load_progress(self) -> Dict:
        """Load pipeline progress from file"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log(f"Warning: Could not load progress file: {e}")
        return {'llm_completed': [], 'llm_failed': [], 'pageview_completed': [], 'pageview_failed': []}
    
    def _save_progress(self, progress: Dict):
        """Save pipeline progress to file"""
        try:
            progress['last_updated'] = datetime.now().isoformat()
            progress['total_mathematicians'] = len(progress.get('llm_completed', [])) + len(progress.get('llm_failed', []))
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"Warning: Could not save progress: {e}")
    
    def _save_enhanced_mathematician(self, enhanced_data: Dict):
        """Save individual mathematician's enhanced data"""
        try:
            name = enhanced_data.get('name', 'unknown')
            clean_id = name.lower().replace(' ', '_').replace('.', '').replace(',', '').replace('-', '_')
            output_file = f"data/processed/enhanced_events/{clean_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"Warning: Could not save enhanced data for {name}: {e}")
    
    def _load_completed_enhanced_data(self, completed_names: List[str]) -> List[Dict]:
        """Load enhanced data for already completed mathematicians"""
        enhanced_data = []
        for name in completed_names:
            try:
                clean_id = name.lower().replace(' ', '_').replace('.', '').replace(',', '').replace('-', '_')
                enhanced_file = f"data/processed/enhanced_events/{clean_id}.json"
                if os.path.exists(enhanced_file):
                    with open(enhanced_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        enhanced_data.append(data)
                else:
                    self.log(f"Warning: Enhanced file not found for {name}, will need reprocessing")
            except Exception as e:
                self.log(f"Warning: Could not load enhanced data for {name}: {e}")
        return enhanced_data
    
    def save_results(self, frontend_mathematicians: Dict):
        """Save final results with summary statistics"""
        
        self.log(f"=== STEP 6: Saving results for {len(frontend_mathematicians)} mathematicians ===")
        
        # Create metadata
        metadata = {
            "source": "wikidata_wikipedia_pipeline_100",
            "generated_at": datetime.now().isoformat(),
            "total_mathematicians": len(frontend_mathematicians),
            "data_quality": "high_structured_llm_enhanced_100",
            "extraction_method": "wikidata_sparql_wikipedia_llm_pageview_pipeline"
        }
        
        # Save frontend-ready data
        frontend_output = {
            "metadata": metadata,
            "mathematicians": frontend_mathematicians
        }
        
        frontend_file = "data/processed/frontend_100_mathematicians.json"
        with open(frontend_file, 'w', encoding='utf-8') as f:
            json.dump(frontend_mathematicians, f, indent=2, ensure_ascii=False)  # Direct format for frontend
        
        # Save with metadata for reference
        reference_file = "data/processed/reference_100_mathematicians.json"
        with open(reference_file, 'w', encoding='utf-8') as f:
            json.dump(frontend_output, f, indent=2, ensure_ascii=False)
        
        # Generate statistics
        self._generate_statistics(frontend_mathematicians)
        
        self.log(f"✅ Results saved:")
        self.log(f"  📁 Frontend data: {frontend_file}")
        self.log(f"  📁 Reference data: {reference_file}")
        self.log(f"  📊 Log file: {self.log_file}")
    
    def _generate_statistics(self, mathematicians: Dict):
        """Generate and log summary statistics"""
        
        total = len(mathematicians)
        
        # Nationality distribution
        nationalities = {}
        birth_years = []
        total_events = 0
        
        for m in mathematicians.values():
            nat = m.get('nationality', 'Unknown')
            nationalities[nat] = nationalities.get(nat, 0) + 1
            
            if m.get('birth_year'):
                birth_years.append(m['birth_year'])
                
            total_events += len(m.get('timeline_events', []))
        
        avg_events = total_events / total if total > 0 else 0
        
        self.log(f"\n📊 === FINAL DATASET STATISTICS ===")
        self.log(f"Total mathematicians: {total}")
        self.log(f"Average events per mathematician: {avg_events:.1f}")
        
        if birth_years:
            self.log(f"Birth year range: {min(birth_years)}-{max(birth_years)}")
            self.log(f"Average birth year: {sum(birth_years)/len(birth_years):.0f}")
        
        self.log(f"\nNationality distribution:")
        for nat, count in sorted(nationalities.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            self.log(f"  {nat}: {count} ({percentage:.1f}%)")
        
        self.log(f"\n🎯 Dataset ready for frontend integration!")
        self.log(f"📋 To use: Copy {total} mathematicians from data/processed/frontend_100_mathematicians.json")
        self.log(f"         to frontend/public/data/mathematicians.json")

def main():
    import sys
    
    pipeline = MathematicianPipeline()
    
    # Check for retry mode
    if len(sys.argv) > 1 and sys.argv[1] == "retry":
        print("🔄 RETRY MODE: Processing only failed LLM extractions")
        
        progress = pipeline._load_progress()
        failed_names = progress.get('llm_failed', [])
        
        if not failed_names:
            print("✅ No LLM failures found to retry.")
            return
        
        print(f"🔄 Found {len(failed_names)} failed LLM extractions to retry:")
        for name in failed_names:
            print(f"  - {name}")
        
        # Load the original scraped data for failed mathematicians
        scraped_data = pipeline.load_existing_wikipedia_data()
        failed_data = [data for data in scraped_data if data.get('name') in failed_names]
        
        # Process only the failed ones with resume=False to force reprocessing
        enhanced_data, tracking = pipeline.enhance_with_llm_resumable(failed_data, resume=False)
        
        success_count = len(tracking.get('llm_successes', []))
        failure_count = len(tracking.get('llm_failures', []))
        
        print(f"\n🎯 RETRY RESULTS:")
        print(f"  ✅ Newly successful: {success_count}")
        print(f"  ❌ Still failing: {failure_count}")
        
        if failure_count > 0:
            print(f"\n⚠️  Still failing after retry:")
            for failure in tracking.get('llm_failures', []):
                print(f"  - {failure['name']}: {failure['error']}")
        
        return
    
    print("🚀 Starting 100 Mathematician Pipeline with Resume Support")
    print(f"📝 Log file: {pipeline.log_file}")
    print(f"💾 Progress file: {pipeline.progress_file}")
    print("⏱️  Estimated time: 15-20 minutes (first run)")
    print("💡 Subsequent runs will skip completed mathematicians")
    print("🔄 Use 'python scale_to_100_mathematicians.py retry' to retry only failures")
    print()
    
    try:
        # Step 1: Get mathematicians from Wikidata
        mathematicians = pipeline.get_wikidata_mathematicians(target_count=100)
        
        if len(mathematicians) < 50:
            pipeline.log("⚠️ Warning: Found fewer than 50 high-quality mathematicians")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Step 2: Load existing Wikipedia data (skip scraping)
        scraped_data = pipeline.load_existing_wikipedia_data()
        
        if len(scraped_data) < 50:
            pipeline.log("⚠️ Warning: Found fewer than 50 existing Wikipedia files")
            response = input("Continue to LLM enhancement? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Step 3: Enhance with LLM timeline extraction (resumable)
        enhanced_data, llm_tracking = pipeline.enhance_with_llm_resumable(scraped_data, resume=True)
        
        # Step 4: Collect page view statistics
        final_data = pipeline.collect_pageviews(enhanced_data)
        
        # Step 5: Convert to frontend format
        frontend_mathematicians = pipeline.convert_to_frontend_format(final_data)
        
        # Step 6: Save results
        pipeline.save_results(frontend_mathematicians)
        
        print(f"\n🎉 SUCCESS! Generated dataset with {len(frontend_mathematicians)} mathematicians")
        print(f"📋 Next step: Copy data/processed/frontend_100_mathematicians.json")
        print(f"            to frontend/public/data/mathematicians.json")
        
    except KeyboardInterrupt:
        pipeline.log("\n⏸️ Pipeline interrupted by user")
        print("\n⏸️ Pipeline interrupted by user")
        print("💾 Progress has been saved automatically")
        print("🔄 Run the script again to resume from where you left off")
        print(f"📝 Log file: {pipeline.log_file}")
    except Exception as e:
        pipeline.log(f"\n❌ Pipeline failed: {e}")
        print(f"\n❌ Pipeline failed: {e}")
        print("💾 Progress has been saved automatically")
        print(f"📝 Check log file for details: {pipeline.log_file}")
        print("🔄 You can resume by running the script again")
        raise

if __name__ == "__main__":
    main()
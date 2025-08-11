"""Enhanced LLM-based timeline event extraction with progress tracking using LM Studio with Google Gemma-3n-e4b"""

import requests
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Optional
import time
import glob

class LMStudioTimelineExtractorEnhanced:
    def __init__(self, model_name: str = "google/gemma-3n-e4b", base_url: str = "http://localhost:1234"):
        """Initialize LM Studio extractor with Google Gemma-3n-e4b"""
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v0/chat/completions"
    
    def _call_llm(self, prompt: str, system_prompt: str = "", retries: int = 2) -> str:
        """Make API call to LM Studio with OpenAI-compatible format"""
        for attempt in range(retries + 1):
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "max_tokens": 2000,
                    "top_p": 0.9,
                    "stream": False
                }
                
                response = requests.post(self.api_url, json=payload, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract content from OpenAI-style response
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"Unexpected response format: {result}")
                    return ""
                    
            except requests.exceptions.ReadTimeout as e:
                print(f"LM Studio timeout on attempt {attempt + 1}/{retries + 1}: {e}")
                if attempt < retries:
                    print(f"Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    print(f"Final timeout after {retries + 1} attempts")
                    return ""
            except Exception as e:
                print(f"Error calling LM Studio on attempt {attempt + 1}: {e}")
                if attempt < retries:
                    time.sleep(2)
                else:
                    return ""
        
        return ""
    
    def extract_timeline_events(self, biography_text: str, mathematician_name: str) -> List[Dict]:
        """Extract timeline events from biographical text using Gemma-3n-e4b"""
        
        system_prompt = """You are an expert historian specializing in 18th century mathematics. Your task is to extract detailed timeline events from biographical text about mathematicians.

Extract events with the following criteria:
- Focus on years 1700-1800 (18th century)
- Include: birth, education, career positions, major publications, travels, death, significant collaborations
- Provide exact years when possible, or year ranges for uncertain dates
- Include specific locations when mentioned (cities, institutions, countries)
- Assign confidence scores (0.0-1.0) based on text clarity and specificity
- Extract MORE events per mathematician for richer timelines (aim for 5-10 events)

IMPORTANT: Return ONLY a valid JSON array of events, no explanatory text.

Each event must have this exact structure:
{
  "year": integer or "year_start-year_end" for ranges,
  "year_confidence": "exact", "approximate", or "range",
  "event_type": "birth"|"education"|"position"|"publication"|"travel"|"death"|"collaboration"|"award"|"other",
  "description": "detailed description of the event",
  "location": {
    "place_name": "specific location name or null",
    "raw_text": "original text mentioning location",
    "confidence": float between 0.0-1.0
  },
  "source_text": "relevant excerpt from biography (max 200 chars)",
  "confidence": float between 0.0-1.0
}"""

        prompt = f"""Extract comprehensive timeline events for mathematician {mathematician_name} from this biographical text.

Biographical text:
{biography_text}

Extract ALL significant events from 1700-1800. Focus on:
- Educational milestones (university attendance, degrees, mentors)
- Career positions (professorships, academy memberships, appointments)
- Major publications and discoveries
- Travel and relocations
- Collaborations with other mathematicians
- Awards and recognition

Return only the JSON array, no other text."""

        response = self._call_llm(prompt, system_prompt)
        
        try:
            # First try to clean markdown code blocks
            cleaned_response = response.strip()
            
            # Remove markdown code blocks if present
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # Remove ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            
            cleaned_response = cleaned_response.strip()
            
            # Try to parse cleaned JSON response
            events = json.loads(cleaned_response)
            if isinstance(events, list):
                # Validate and enhance events
                cleaned_events = []
                for event in events:
                    if self._validate_event(event):
                        # Add Gemma-specific metadata
                        event['extraction_metadata'] = {
                            'model_version': f"lm_studio_{self.model_name}",
                            'extracted_at': datetime.now().isoformat(),
                            'extraction_confidence': event.get('confidence', 0.8),
                            'extraction_method': 'lm_studio_gemma_enhanced'
                        }
                        cleaned_events.append(event)
                
                print(f"Successfully parsed JSON response for {mathematician_name}: {len(cleaned_events)} events")
                return cleaned_events
            else:
                print(f"LM Studio returned non-list response for {mathematician_name}")
                return []
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse LM Studio JSON response for {mathematician_name}: {e}")
            print(f"Raw response: {response[:500]}...")
            
            # Try to extract JSON from mixed response
            return self._extract_json_from_mixed_response(response, mathematician_name)
    
    def _extract_json_from_mixed_response(self, response: str, mathematician_name: str) -> List[Dict]:
        """Extract JSON array from response that might contain extra text"""
        try:
            # Look for JSON array pattern
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                events = json.loads(json_str)
                if isinstance(events, list):
                    print(f"Successfully extracted JSON from mixed response for {mathematician_name}")
                    return [event for event in events if self._validate_event(event)]
            
            # If no JSON found, use fallback
            return self._fallback_extraction(response, mathematician_name)
            
        except Exception as e:
            print(f"Failed to extract JSON from mixed response: {e}")
            return self._fallback_extraction(response, mathematician_name)
    
    def _validate_event(self, event: Dict) -> bool:
        """Validate event structure and content with Gemma-specific checks"""
        required_fields = ['year', 'event_type', 'description']
        
        # Check required fields
        for field in required_fields:
            if field not in event:
                print(f"Missing required field: {field}")
                return False
        
        # Validate year format
        year = event['year']
        if isinstance(year, int):
            if not (1650 <= year <= 1850):  # Reasonable range
                print(f"Year out of range: {year}")
                return False
        elif isinstance(year, str):
            if not re.match(r'\d{4}(-\d{4})?', year):
                print(f"Invalid year format: {year}")
                return False
        else:
            print(f"Invalid year type: {type(year)}")
            return False
        
        # Validate event type (expanded for richer extraction)
        valid_types = [
            'birth', 'education', 'position', 'publication', 
            'travel', 'death', 'collaboration', 'award', 'other'
        ]
        if event['event_type'] not in valid_types:
            print(f"Invalid event type: {event['event_type']}")
            return False
        
        # Validate description is meaningful
        if len(event.get('description', '').strip()) < 10:
            print(f"Description too short: {event.get('description', '')}")
            return False
        
        return True
    
    def _fallback_extraction(self, raw_response: str, mathematician_name: str) -> List[Dict]:
        """Enhanced fallback extraction with more patterns for Gemma"""
        print(f"Using enhanced fallback extraction for {mathematician_name}")
        
        events = []
        
        # Enhanced regex patterns for comprehensive event extraction
        patterns = [
            (r'born.*?(?:in\s+)?(\d{4})', 'birth'),
            (r'died.*?(?:in\s+)?(\d{4})', 'death'),
            (r'(?:studied|educated|attended).*?(?:in\s+)?(\d{4})', 'education'),
            (r'(?:professor|appointed|became).*?(?:in\s+)?(\d{4})', 'position'),
            (r'(?:published|wrote).*?(?:in\s+)?(\d{4})', 'publication'),
            (r'(?:traveled|moved|went).*?(?:to|in)\s+(\w+).*?(\d{4})', 'travel'),
            (r'(?:worked|collaborated).*?(?:with|on).*?(\d{4})', 'collaboration'),
            (r'(?:awarded|received|honored).*?(?:in\s+)?(\d{4})', 'award')
        ]
        
        for pattern, event_type in patterns:
            matches = re.finditer(pattern, raw_response, re.IGNORECASE)
            for match in matches:
                try:
                    # Extract year (last number in the match)
                    year_match = re.findall(r'\d{4}', match.group(0))
                    if year_match:
                        year = int(year_match[-1])
                        if 1700 <= year <= 1800:
                            events.append({
                                'year': year,
                                'year_confidence': 'approximate',
                                'event_type': event_type,
                                'description': f"Enhanced {event_type} event in {year} extracted from: {match.group(0)[:100]}",
                                'location': {'place_name': None, 'raw_text': match.group(0), 'confidence': 0.3},
                                'source_text': match.group(0)[:200],
                                'confidence': 0.7,  # Higher confidence than basic fallback
                                'extraction_metadata': {
                                    'model_version': 'enhanced_fallback_regex',
                                    'extracted_at': datetime.now().isoformat(),
                                    'extraction_confidence': 0.7,
                                    'extraction_method': 'gemma_fallback'
                                }
                            })
                except (ValueError, IndexError) as e:
                    continue
        
        return events
    
    def process_mathematician(self, mathematician_data: Dict) -> Dict:
        """Process a single mathematician's data to extract enhanced timeline events"""
        mathematician_name = mathematician_data.get('name', 'Unknown')
        
        print(f"\n=== Extracting enhanced timeline events for: {mathematician_name} ===")
        
        # Get biography text
        wikipedia_data = mathematician_data.get('wikipedia_data', {})
        biography_paragraphs = wikipedia_data.get('biography_paragraphs', [])
        
        if not biography_paragraphs:
            print(f"No biography text found for {mathematician_name}")
            return mathematician_data
        
        # Use more biography text for richer extraction (first 3 paragraphs)
        biography_text = ' '.join(biography_paragraphs[:3])
        
        # Allow longer text for more comprehensive extraction (up to 2500 chars)
        if len(biography_text) > 2500:
            biography_text = biography_text[:2500] + "..."
        
        # Extract events with enhanced Gemma processing
        events = self.extract_timeline_events(biography_text, mathematician_name)
        
        print(f"Extracted {len(events)} events for {mathematician_name}")
        for event in events:
            print(f"  - {event['year']}: {event['event_type']} - {event['description'][:80]}...")
        
        # Add events to mathematician data
        mathematician_data['timeline_events'] = events
        mathematician_data['timeline_extraction_metadata'] = {
            'extracted_at': datetime.now().isoformat(),
            'model_used': f"lm_studio_{self.model_name}",
            'events_count': len(events),
            'biography_length': len(biography_text),
            'enhancement_level': 'gemma_comprehensive',
            'target_events_per_mathematician': '5-10'
        }
        
        return mathematician_data
    
    def process_all_mathematicians_with_tracking(self, input_dir: str, output_dir: str, resume: bool = True):
        """Process all mathematician files with progress tracking and resume capability"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Progress tracking files
        progress_file = os.path.join(output_dir, "extraction_progress.json")
        log_file = os.path.join(output_dir, f"extraction_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        # Load existing progress
        progress = self._load_progress(progress_file) if resume else {'completed': [], 'failed': [], 'skipped': []}
        
        json_files = glob.glob(os.path.join(input_dir, "*.json"))
        total_files = len(json_files)
        
        print(f"=== Enhanced LM Studio + Gemma-3n-e4b Timeline Extraction ===")
        print(f"Total mathematician files: {total_files}")
        print(f"Previously completed: {len(progress.get('completed', []))}")
        print(f"Previously failed: {len(progress.get('failed', []))}")
        print(f"Resume mode: {'ON' if resume else 'OFF'}")
        print(f"Progress file: {progress_file}")
        print(f"Log file: {log_file}")
        
        remaining_files = [f for f in json_files if os.path.basename(f) not in progress.get('completed', [])]
        print(f"Files to process: {len(remaining_files)}")
        
        total_events = 0
        successful_processing = 0
        current_failures = 0
        
        for i, json_file in enumerate(remaining_files, 1):
            filename = os.path.basename(json_file)
            output_file = os.path.join(output_dir, filename)
            
            # Skip if already successfully processed
            if resume and filename in progress.get('completed', []):
                print(f"[{i}/{len(remaining_files)}] SKIPPED {filename} (already completed)")
                progress['skipped'].append(filename)
                continue
            
            print(f"\n[{i}/{len(remaining_files)}] === Processing {filename} ===")
            self._log_message(log_file, f"Starting {filename}")
            
            try:
                # Load data
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Enhanced extraction with Gemma
                processed_data = self.process_mathematician(data)
                
                # Validate extraction
                events_count = len(processed_data.get('timeline_events', []))
                if events_count == 0:
                    raise ValueError("No timeline events extracted")
                
                total_events += events_count
                successful_processing += 1
                
                # Save to output directory
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, indent=2, ensure_ascii=False)
                
                # Mark as completed
                progress['completed'].append(filename)
                # Remove from failed list if it was there
                if filename in progress.get('failed', []):
                    progress['failed'].remove(filename)
                
                print(f"✓ SUCCESS: {events_count} events extracted")
                self._log_message(log_file, f"SUCCESS {filename}: {events_count} events")
                
                # Save progress after each success
                self._save_progress(progress_file, progress)
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                current_failures += 1
                error_msg = str(e)[:200] + ('...' if len(str(e)) > 200 else '')
                
                # Mark as failed
                if filename not in progress.get('failed', []):
                    progress['failed'].append(filename)
                # Remove from completed list if it was there
                if filename in progress.get('completed', []):
                    progress['completed'].remove(filename)
                
                print(f"✗ FAILED {filename}: {error_msg}")
                self._log_message(log_file, f"FAILED {filename}: {error_msg}")
                
                # Save progress after each failure
                self._save_progress(progress_file, progress)
                
                # Continue with next file
                continue
            
            # Progress update every 10 files
            if i % 10 == 0:
                self._print_progress_summary(progress, total_events, successful_processing)
        
        # Final summary
        self._print_final_summary(progress, total_events, successful_processing, current_failures, log_file)
    
    def _load_progress(self, progress_file: str) -> dict:
        """Load progress from file"""
        try:
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load progress file: {e}")
        return {'completed': [], 'failed': [], 'skipped': []}
    
    def _save_progress(self, progress_file: str, progress: dict):
        """Save progress to file"""
        try:
            progress['last_updated'] = datetime.now().isoformat()
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save progress: {e}")
    
    def _log_message(self, log_file: str, message: str):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to log: {e}")
    
    def _print_progress_summary(self, progress: dict, total_events: int, successful: int):
        """Print progress summary"""
        completed = len(progress.get('completed', []))
        failed = len(progress.get('failed', []))
        avg_events = total_events / successful if successful > 0 else 0
        
        print(f"\n📊 PROGRESS UPDATE:")
        print(f"  Completed: {completed}")
        print(f"  Failed: {failed}")
        print(f"  Total events: {total_events}")
        print(f"  Avg events/mathematician: {avg_events:.1f}")
    
    def _print_final_summary(self, progress: dict, total_events: int, successful: int, current_failures: int, log_file: str):
        """Print final extraction summary"""
        completed = len(progress.get('completed', []))
        failed = len(progress.get('failed', []))
        skipped = len(progress.get('skipped', []))
        avg_events = total_events / successful if successful > 0 else 0
        
        print(f"\n=== 🎯 FINAL EXTRACTION SUMMARY ===")
        print(f"✅ Successfully completed: {completed}")
        print(f"❌ Failed: {failed}")
        print(f"⏭️  Skipped (already done): {skipped}")
        print(f"📈 Total events extracted: {total_events}")
        print(f"📊 Average events per mathematician: {avg_events:.1f}")
        print(f"🎯 Target achieved: {'✓' if avg_events >= 5 else '✗'} (target: 5-10 events)")
        print(f"📝 Detailed log: {log_file}")
        
        if failed > 0:
            print(f"\n⚠️  FAILED FILES TO INVESTIGATE:")
            for failure in progress.get('failed', []):
                print(f"  - {failure}")
            print(f"\n💡 To retry failed files, run: python lm_studio_extractor_enhanced.py retry")
    
    def retry_failed_only(self, input_dir: str, output_dir: str):
        """Retry only the failed extractions"""
        progress_file = os.path.join(output_dir, "extraction_progress.json")
        progress = self._load_progress(progress_file)
        
        failed_files = progress.get('failed', [])
        if not failed_files:
            print("No failed files found to retry.")
            return
        
        print(f"=== RETRYING {len(failed_files)} FAILED EXTRACTIONS ===")
        
        # Retry each failed file
        for filename in failed_files:
            input_file = os.path.join(input_dir, filename)
            if os.path.exists(input_file):
                print(f"\nRetrying: {filename}")
                try:
                    # Process individual file
                    with open(input_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    processed_data = self.process_mathematician(data)
                    events_count = len(processed_data.get('timeline_events', []))
                    
                    if events_count > 0:
                        output_file = os.path.join(output_dir, filename)
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(processed_data, f, indent=2, ensure_ascii=False)
                        
                        # Update progress
                        progress['completed'].append(filename)
                        progress['failed'].remove(filename)
                        print(f"✓ RETRY SUCCESS: {filename} - {events_count} events")
                    else:
                        print(f"✗ RETRY FAILED: {filename} - No events extracted")
                        
                except Exception as e:
                    print(f"✗ RETRY FAILED: {filename} - {e}")
                
                time.sleep(2)
        
        self._save_progress(progress_file, progress)
        print("\nRetry process completed.")

if __name__ == "__main__":
    import sys
    
    # Check if LM Studio is running
    try:
        response = requests.get("http://localhost:1234/api/v0/models", timeout=5)
        if response.status_code == 200:
            print("✓ LM Studio server is running")
            models = response.json()
            print(f"Available models: {[m.get('id', 'unknown') for m in models.get('data', [])]}")
        else:
            print("✗ LM Studio server responded with error")
    except Exception as e:
        print("✗ LM Studio server is not running or not accessible!")
        print("Please:")
        print("1. Start LM Studio application")
        print("2. Load Google Gemma-3n-e4b model (or similar)")
        print("3. Start the local server on port 1234")
        print(f"Error: {e}")
        sys.exit(1)
    
    extractor = LMStudioTimelineExtractorEnhanced()
    
    # Command line arguments for different modes
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "retry":
            input_dir = "data/raw/wikipedia_100"
            output_dir = "data/processed/with_enhanced_events"
            print("🔄 RETRY MODE: Processing only failed extractions")
            extractor.retry_failed_only(input_dir, output_dir)
            sys.exit(0)
    
    input_dir = "data/raw/wikipedia_100"  # Use existing Wikipedia data
    output_dir = "data/processed/with_enhanced_events"  # New output for enhanced events
    
    # Check for existing progress
    progress_file = os.path.join(output_dir, "extraction_progress.json")
    if os.path.exists(progress_file):
        print("📁 Found existing progress file. Resume mode will skip completed files.")
        response = input("Continue with resume mode? (y/n): ")
        resume = response.lower() == 'y'
    else:
        resume = False
    
    print("\n🚀 Starting extraction process...")
    print("💡 You can interrupt with Ctrl+C and resume later")
    print("💡 Use 'python lm_studio_extractor_enhanced.py retry' to retry only failed files")
    
    try:
        extractor.process_all_mathematicians_with_tracking(input_dir, output_dir, resume=resume)
    except KeyboardInterrupt:
        print("\n⏸️  Extraction interrupted by user")
        print("Progress has been saved. You can resume by running the script again.")
    except Exception as e:
        print(f"\n❌ Extraction failed with error: {e}")
        print("Check the log file for details. You can resume by running the script again.")
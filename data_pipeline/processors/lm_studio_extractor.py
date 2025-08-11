"""LLM-based timeline event extraction using LM Studio with Google Gemma-3n-e4b"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import time

class LMStudioTimelineExtractor:
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
            
            # Try partial JSON recovery first
            partial_events = self._extract_partial_json_events(response, mathematician_name)
            if partial_events:
                return partial_events
            
            # If partial recovery fails, treat as complete failure for rerun
            print(f"No events could be recovered from response for {mathematician_name}")
            print(f"This mathematician will be marked for retry.")
            return []  # Return empty list to force retry
    
    def _extract_json_from_mixed_response(self, response: str, mathematician_name: str) -> List[Dict]:
        """Extract JSON array from response that might contain extra text"""
        try:
            # Try multiple strategies to extract valid JSON
            
            # Strategy 1: Look for complete JSON array pattern
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    events = json.loads(json_str)
                    if isinstance(events, list):
                        print(f"Successfully extracted complete JSON from mixed response for {mathematician_name}")
                        valid_events = [event for event in events if self._validate_event(event)]
                        if valid_events:
                            return valid_events
                except json.JSONDecodeError as e:
                    print(f"Complete JSON parsing failed: {e}")
            
            # Strategy 2: Try to fix common JSON issues and extract partial arrays
            return self._extract_partial_json_events(response, mathematician_name)
            
        except Exception as e:
            print(f"Failed to extract JSON from mixed response: {e}")
            # Return empty list to force retry instead of using regex fallback
            print(f"JSON extraction completely failed for {mathematician_name} - marking for retry")
            return []
    
    def _extract_partial_json_events(self, response: str, mathematician_name: str) -> List[Dict]:
        """Extract individual JSON objects even if the full array is malformed"""
        print(f"Attempting partial JSON extraction for {mathematician_name}")
        
        events = []
        
        # Find individual event objects using regex
        event_pattern = r'\{[^{}]*"year"[^{}]*"event_type"[^{}]*"description"[^{}]*\}'
        
        # More comprehensive pattern that handles nested objects
        nested_pattern = r'\{(?:[^{}]|{[^{}]*})*"year"(?:[^{}]|{[^{}]*})*"event_type"(?:[^{}]|{[^{}]*})*"description"(?:[^{}]|{[^{}]*})*\}'
        
        for pattern in [nested_pattern, event_pattern]:
            matches = re.finditer(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    event_str = match.group(0)
                    # Try to parse individual event
                    event = json.loads(event_str)
                    if self._validate_event(event):
                        # Add extraction metadata
                        event['extraction_metadata'] = {
                            'model_version': f"lm_studio_{self.model_name}_partial",
                            'extracted_at': datetime.now().isoformat(),
                            'extraction_confidence': event.get('confidence', 0.7),
                            'extraction_method': 'partial_json_recovery'
                        }
                        events.append(event)
                        print(f"  Recovered event: {event['year']} - {event['event_type']}")
                except json.JSONDecodeError:
                    continue
        
        if events:
            print(f"Successfully recovered {len(events)} events from partial JSON for {mathematician_name}")
            return events
        
        # If partial extraction fails, return empty for retry
        print(f"Partial JSON extraction failed for {mathematician_name} - marking for retry")
        return []
    
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
        mathematician_id = mathematician_data.get('id', 'unknown')
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
    
    def process_all_mathematicians(self, input_dir: str, output_dir: str):
        """Process all mathematician files with enhanced LM Studio + Gemma extraction"""
        import os
        import glob
        
        os.makedirs(output_dir, exist_ok=True)
        
        json_files = glob.glob(os.path.join(input_dir, "*.json"))
        
        print(f"=== Enhanced LM Studio + Gemma-3n-e4b Timeline Extraction ===")
        print(f"Processing {len(json_files)} mathematician files...")
        print(f"Target: 5-10 events per mathematician for richer timelines")
        
        total_events = 0
        successful_processing = 0
        
        for json_file in json_files:
            try:
                print(f"\n=== Processing {os.path.basename(json_file)} ===")
                
                # Load data
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Enhanced extraction with Gemma
                processed_data = self.process_mathematician(data)
                
                # Count events
                events_count = len(processed_data.get('timeline_events', []))
                total_events += events_count
                successful_processing += 1
                
                # Save to output directory
                filename = os.path.basename(json_file)
                output_file = os.path.join(output_dir, filename)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, indent=2, ensure_ascii=False)
                
                print(f"✓ Saved enhanced data: {output_file}")
                print(f"✓ Events extracted: {events_count}")
                
                # Rate limiting to be nice to LM Studio
                time.sleep(2)
                
            except Exception as e:
                print(f"✗ Error processing {json_file}: {e}")
        
        # Summary statistics
        avg_events = total_events / successful_processing if successful_processing > 0 else 0
        print(f"\n=== Enhanced Extraction Summary ===")
        print(f"Successfully processed: {successful_processing}/{len(json_files)} mathematicians")
        print(f"Total events extracted: {total_events}")
        print(f"Average events per mathematician: {avg_events:.1f}")
        print(f"Target achieved: {'✓' if avg_events >= 5 else '✗'} (target: 5-10 events)")

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
        print("2. Load Google Gemma-3-2b model (or similar)")
        print("3. Start the local server on port 1234")
        print(f"Error: {e}")
        sys.exit(1)
    
    extractor = LMStudioTimelineExtractor()
    
    input_dir = "data/processed/with_locations"  # Use location-enhanced data as input
    output_dir = "data/processed/with_enhanced_events"  # New output for enhanced events
    
    extractor.process_all_mathematicians(input_dir, output_dir)
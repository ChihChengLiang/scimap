"""LLM-based timeline event extraction using Ollama"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import time

class LLMTimelineExtractor:
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """Initialize LLM extractor with Ollama"""
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Make API call to Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent extraction
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return ""
    
    def extract_timeline_events(self, biography_text: str, mathematician_name: str) -> List[Dict]:
        """Extract timeline events from biographical text"""
        
        system_prompt = """You are an expert historian specializing in 18th century mathematics. Your task is to extract timeline events from biographical text about mathematicians.

Extract events with the following criteria:
- Focus on years 1700-1800 (18th century)
- Include: birth, education, career positions, major publications, travels, death
- Provide exact years when possible, or year ranges
- Include locations when mentioned
- Assign confidence scores (0.0-1.0) based on text clarity

Return ONLY a valid JSON array of events. Each event should have:
{
  "year": integer or "year_start-year_end" for ranges,
  "year_confidence": "exact", "approximate", or "range",
  "event_type": "birth"|"education"|"position"|"publication"|"travel"|"death"|"other",
  "description": "brief description",
  "location": {
    "place_name": "location name or null",
    "raw_text": "original text mentioning location",
    "confidence": float
  },
  "source_text": "relevant excerpt from biography",
  "confidence": float
}"""

        prompt = f"""Extract timeline events for {mathematician_name} from this biographical text:

{biography_text}

Focus on events between 1700-1800. Return only the JSON array, no other text."""

        response = self._call_llm(prompt, system_prompt)
        
        try:
            # Try to parse JSON response
            events = json.loads(response)
            if isinstance(events, list):
                # Validate and clean events
                cleaned_events = []
                for event in events:
                    if self._validate_event(event):
                        # Add metadata
                        event['extraction_metadata'] = {
                            'model_version': self.model_name,
                            'extracted_at': datetime.now().isoformat(),
                            'extraction_confidence': event.get('confidence', 0.8)
                        }
                        cleaned_events.append(event)
                
                return cleaned_events
            else:
                print(f"LLM returned non-list response for {mathematician_name}")
                return []
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM JSON response for {mathematician_name}: {e}")
            print(f"Raw response: {response[:500]}...")
            
            # Try to extract events using regex as fallback
            return self._fallback_extraction(response, mathematician_name)
    
    def _validate_event(self, event: Dict) -> bool:
        """Validate event structure and content"""
        required_fields = ['year', 'event_type', 'description']
        
        # Check required fields
        for field in required_fields:
            if field not in event:
                return False
        
        # Validate year format
        year = event['year']
        if isinstance(year, int):
            if not (1650 <= year <= 1850):  # Reasonable range
                return False
        elif isinstance(year, str):
            if not re.match(r'\d{4}(-\d{4})?', year):
                return False
        
        # Validate event type
        valid_types = ['birth', 'education', 'position', 'publication', 'travel', 'death', 'other']
        if event['event_type'] not in valid_types:
            return False
        
        return True
    
    def _fallback_extraction(self, raw_response: str, mathematician_name: str) -> List[Dict]:
        """Fallback extraction using regex patterns"""
        print(f"Using fallback extraction for {mathematician_name}")
        
        events = []
        
        # Simple regex patterns for common events
        patterns = [
            (r'born.*?(\d{4})', 'birth'),
            (r'died.*?(\d{4})', 'death'),
            (r'educated.*?(\d{4})', 'education'),
            (r'professor.*?(\d{4})', 'position'),
            (r'published.*?(\d{4})', 'publication')
        ]
        
        for pattern, event_type in patterns:
            matches = re.finditer(pattern, raw_response, re.IGNORECASE)
            for match in matches:
                year = int(match.group(1))
                if 1700 <= year <= 1800:
                    events.append({
                        'year': year,
                        'year_confidence': 'approximate',
                        'event_type': event_type,
                        'description': f"{event_type.title()} event in {year}",
                        'location': {'place_name': None, 'raw_text': '', 'confidence': 0.0},
                        'source_text': match.group(0),
                        'confidence': 0.6,  # Lower confidence for fallback
                        'extraction_metadata': {
                            'model_version': 'fallback_regex',
                            'extracted_at': datetime.now().isoformat(),
                            'extraction_confidence': 0.6
                        }
                    })
        
        return events
    
    def process_mathematician(self, mathematician_data: Dict) -> Dict:
        """Process a single mathematician's data to extract timeline events"""
        mathematician_id = mathematician_data.get('id', 'unknown')
        mathematician_name = mathematician_data.get('name', 'Unknown')
        
        print(f"\nExtracting timeline events for: {mathematician_name}")
        
        # Get biography text
        wikipedia_data = mathematician_data.get('wikipedia_data', {})
        biography_paragraphs = wikipedia_data.get('biography_paragraphs', [])
        
        if not biography_paragraphs:
            print(f"No biography text found for {mathematician_name}")
            return mathematician_data
        
        # Combine first few paragraphs for processing
        biography_text = ' '.join(biography_paragraphs[:3])  # Limit text length
        
        # Extract events
        events = self.extract_timeline_events(biography_text, mathematician_name)
        
        print(f"Extracted {len(events)} events for {mathematician_name}")
        
        # Add events to mathematician data
        mathematician_data['timeline_events'] = events
        mathematician_data['timeline_extraction_metadata'] = {
            'extracted_at': datetime.now().isoformat(),
            'model_used': self.model_name,
            'events_count': len(events),
            'biography_length': len(biography_text)
        }
        
        return mathematician_data
    
    def process_all_mathematicians(self, input_dir: str, output_dir: str):
        """Process all mathematician files to extract timeline events"""
        import os
        import glob
        
        os.makedirs(output_dir, exist_ok=True)
        
        json_files = glob.glob(os.path.join(input_dir, "*.json"))
        
        print(f"Processing {len(json_files)} mathematician files...")
        
        for json_file in json_files:
            try:
                print(f"\n=== Processing {json_file} ===")
                
                # Load data
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract timeline events
                processed_data = self.process_mathematician(data)
                
                # Save to output directory
                filename = os.path.basename(json_file)
                output_file = os.path.join(output_dir, filename)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, indent=2, ensure_ascii=False)
                
                print(f"Saved processed data: {output_file}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing {json_file}: {e}")

if __name__ == "__main__":
    import sys
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        print("Ollama server is running")
    except:
        print("ERROR: Ollama server is not running!")
        print("Please start Ollama with: ollama serve")
        print("And ensure llama3.1:8b model is available: ollama pull llama3.1:8b")
        sys.exit(1)
    
    extractor = LLMTimelineExtractor()
    
    input_dir = "data/raw/wikipedia"
    output_dir = "data/processed/with_events"
    
    extractor.process_all_mathematicians(input_dir, output_dir)
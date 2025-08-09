"""Location geocoding system using LLM for historical place names"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time

class HistoricalGeocoder:
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """Initialize geocoder with LLM for historical context"""
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        # Cache for geocoded locations
        self.location_cache = {}
        self.load_location_cache()
    
    def _call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Make API call to Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except Exception as e:
            print(f"Error calling LLM for geocoding: {e}")
            return ""
    
    def geocode_location(self, place_name: str, context: str = "", year: int = None) -> Dict:
        """Geocode a historical place name using LLM"""
        
        # Check cache first
        cache_key = f"{place_name.lower()}_{year if year else 'any'}"
        if cache_key in self.location_cache:
            print(f"Using cached location for: {place_name}")
            return self.location_cache[cache_key]
        
        system_prompt = """You are an expert historical geographer specializing in 18th century Europe. Your task is to provide coordinates for historical place names as they were known in the 1700s.

Important guidelines:
- Use historical boundaries and names as they existed in the 18th century
- For cities that have changed names, use the historical context
- Provide coordinates in decimal degrees (lat, lng)
- Include confidence score based on historical certainty
- Note any historical context that might affect location

Return ONLY a valid JSON object with this exact format:
{
  "place_name": "standardized historical name",
  "coordinates": {"lat": decimal, "lng": decimal},
  "confidence": float_between_0_and_1,
  "historical_context": "brief context about the location in 18th century",
  "alternative_names": ["list", "of", "alternative", "names"],
  "modern_equivalent": "modern city/country name if different"
}"""

        year_context = f" in the year {year}" if year else " during the 18th century"
        context_text = f" Context: {context}" if context else ""
        
        prompt = f"""Provide coordinates for the historical location: "{place_name}"{year_context}.{context_text}

Consider 18th century political boundaries and city names. Return only the JSON object."""

        response = self._call_llm(prompt, system_prompt)
        
        try:
            location_data = json.loads(response)
            
            # Validate coordinates
            if not self._validate_coordinates(location_data.get('coordinates', {})):
                print(f"Invalid coordinates for {place_name}")
                location_data = self._create_fallback_location(place_name)
            
            # Add metadata
            location_data['geocoded_at'] = datetime.now().isoformat()
            location_data['geocoding_method'] = 'llm'
            location_data['model_version'] = self.model_name
            
            # Cache the result
            self.location_cache[cache_key] = location_data
            self.save_location_cache()
            
            return location_data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM geocoding response for {place_name}: {e}")
            print(f"Raw response: {response[:200]}...")
            return self._create_fallback_location(place_name)
    
    def _validate_coordinates(self, coordinates: Dict) -> bool:
        """Validate coordinate values"""
        if not isinstance(coordinates, dict):
            return False
        
        lat = coordinates.get('lat')
        lng = coordinates.get('lng')
        
        if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
            return False
        
        # Check reasonable bounds (focus on Europe and nearby regions)
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return False
        
        return True
    
    def _create_fallback_location(self, place_name: str) -> Dict:
        """Create a fallback location entry when geocoding fails"""
        return {
            'place_name': place_name,
            'coordinates': {'lat': 0.0, 'lng': 0.0},
            'confidence': 0.0,
            'historical_context': 'Location could not be determined',
            'alternative_names': [],
            'modern_equivalent': '',
            'geocoded_at': datetime.now().isoformat(),
            'geocoding_method': 'fallback',
            'error': 'geocoding_failed'
        }
    
    def extract_locations_from_events(self, timeline_events: List[Dict]) -> List[str]:
        """Extract unique location names from timeline events"""
        locations = set()
        
        for event in timeline_events:
            location = event.get('location', {})
            place_name = location.get('place_name')
            
            if place_name and place_name.strip():
                locations.add(place_name.strip())
        
        return list(locations)
    
    def process_mathematician_locations(self, mathematician_data: Dict) -> Dict:
        """Process and geocode all locations for a mathematician"""
        mathematician_name = mathematician_data.get('name', 'Unknown')
        print(f"\nGeocoding locations for: {mathematician_name}")
        
        # Get timeline events
        timeline_events = mathematician_data.get('timeline_events', [])
        if not timeline_events:
            print(f"No timeline events found for {mathematician_name}")
            return mathematician_data
        
        # Extract unique locations
        location_names = self.extract_locations_from_events(timeline_events)
        print(f"Found {len(location_names)} unique locations: {location_names}")
        
        # Geocode each location
        location_table = {}
        for place_name in location_names:
            # Find a representative event for context
            context_event = None
            for event in timeline_events:
                if event.get('location', {}).get('place_name') == place_name:
                    context_event = event
                    break
            
            context = context_event.get('description', '') if context_event else ''
            year = context_event.get('year') if context_event else None
            if isinstance(year, str) and '-' in year:
                year = int(year.split('-')[0])  # Use start year for ranges
            
            location_data = self.geocode_location(place_name, context, year)
            location_table[place_name] = location_data
            
            # Rate limiting
            time.sleep(0.5)
        
        # Update timeline events with geocoded coordinates
        for event in timeline_events:
            location = event.get('location', {})
            place_name = location.get('place_name')
            
            if place_name in location_table:
                location_data = location_table[place_name]
                event['location']['coordinates'] = location_data['coordinates']
                event['location']['geocoding_confidence'] = location_data['confidence']
                event['location']['historical_context'] = location_data.get('historical_context', '')
        
        # Add location table to mathematician data
        mathematician_data['location_table'] = location_table
        mathematician_data['geocoding_metadata'] = {
            'geocoded_at': datetime.now().isoformat(),
            'locations_processed': len(location_table),
            'model_used': self.model_name
        }
        
        print(f"Geocoded {len(location_table)} locations for {mathematician_name}")
        return mathematician_data
    
    def load_location_cache(self):
        """Load cached locations from file"""
        try:
            with open('data/processed/location_cache.json', 'r', encoding='utf-8') as f:
                self.location_cache = json.load(f)
            print(f"Loaded {len(self.location_cache)} cached locations")
        except FileNotFoundError:
            print("No location cache found, starting fresh")
            self.location_cache = {}
        except Exception as e:
            print(f"Error loading location cache: {e}")
            self.location_cache = {}
    
    def save_location_cache(self):
        """Save location cache to file"""
        try:
            import os
            os.makedirs('data/processed', exist_ok=True)
            with open('data/processed/location_cache.json', 'w', encoding='utf-8') as f:
                json.dump(self.location_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving location cache: {e}")
    
    def process_all_mathematicians(self, input_dir: str, output_dir: str):
        """Process all mathematician files to add geocoded locations"""
        import os
        import glob
        
        os.makedirs(output_dir, exist_ok=True)
        
        json_files = glob.glob(os.path.join(input_dir, "*.json"))
        
        print(f"Geocoding locations for {len(json_files)} mathematician files...")
        
        for json_file in json_files:
            try:
                print(f"\n=== Processing {json_file} ===")
                
                # Load data
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Geocode locations
                processed_data = self.process_mathematician_locations(data)
                
                # Save to output directory
                filename = os.path.basename(json_file)
                output_file = os.path.join(output_dir, filename)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, indent=2, ensure_ascii=False)
                
                print(f"Saved geocoded data: {output_file}")
                
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
        sys.exit(1)
    
    geocoder = HistoricalGeocoder()
    
    input_dir = "data/processed/with_events"
    output_dir = "data/processed/with_locations"
    
    geocoder.process_all_mathematicians(input_dir, output_dir)
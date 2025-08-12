#!/usr/bin/env python3
"""
Enrich locations.json using high-quality places from wikidata_mathematician_config.json
"""

import json
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional
from collections import Counter
import re

def load_json(file_path: Path) -> Dict:
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path: Path, data: Dict, indent: int = 2) -> None:
    """Save JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def normalize_place_name(name: str) -> str:
    """Normalize place name for comparison"""
    if not name:
        return ""
    # Remove common prefixes/suffixes, normalize case and spacing
    name = name.lower().strip()
    name = re.sub(r'\s+', ' ', name)  # normalize whitespace
    return name

def geocode_location(place_name: str, wikidata_url: str = None) -> Optional[Dict]:
    """Geocode using Nominatim with 18th century context"""
    if not place_name or place_name.lower() == 'null':
        return None
    
    base_url = "https://nominatim.openstreetmap.org/search"
    
    # Try different query variations
    queries = [
        place_name,  # Exact name
        f"{place_name}, Europe",  # With Europe context (most mathematicians were European)
        f"{place_name} city",  # As a city
    ]
    
    for query in queries:
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1,
            'extratags': 1
        }
        
        try:
            response = requests.get(base_url, params=params, 
                                  headers={'User-Agent': 'SciMap/1.0 (research project)'})
            response.raise_for_status()
            results = response.json()
            
            if results:
                result = results[0]
                return {
                    'lat': float(result['lat']),
                    'lng': float(result['lon']),
                    'confidence': 0.8,  # Wikidata source is reliable
                    'display_name': result.get('display_name', place_name),
                    'country': result.get('address', {}).get('country', ''),
                    'geocoded_via': 'nominatim',
                    'wikidata_url': wikidata_url
                }
        except Exception as e:
            print(f"Geocoding error for '{query}': {e}")
            continue
        
        time.sleep(1)  # Rate limiting
    
    return None

def create_location_entry(place_name: str, coordinates: Dict, wikidata_url: str = None) -> Dict:
    """Create a location entry in the standard format"""
    return {
        "place_name": place_name,
        "coordinates": {
            "lat": coordinates['lat'],
            "lng": coordinates['lng']
        },
        "confidence": coordinates.get('confidence', 0.8),
        "historical_context": f"Historical location referenced in 18th century mathematical sources.",
        "alternative_names": [place_name],
        "modern_equivalent": coordinates.get('display_name', place_name),
        "geocoded_at": datetime.now().isoformat(),
        "source": "wikidata_mathematician_config",
        "wikidata_url": wikidata_url,
        "country": coordinates.get('country', '')
    }

def find_similar_locations(place_name: str, existing_locations: Dict) -> List[str]:
    """Find potentially similar locations in existing data"""
    normalized_new = normalize_place_name(place_name)
    similar = []
    
    for existing_key in existing_locations.keys():
        normalized_existing = normalize_place_name(existing_key)
        
        # Exact match
        if normalized_new == normalized_existing:
            similar.append(existing_key)
            continue
        
        # Check if one is contained in the other
        if (normalized_new in normalized_existing or 
            normalized_existing in normalized_new):
            similar.append(existing_key)
    
    return similar

def extract_wikidata_places(wikidata_config: Dict) -> Dict[str, Dict]:
    """Extract all unique places from wikidata config with their metadata"""
    places = {}
    
    for mathematician_id, data in wikidata_config['mathematicians'].items():
        # Birth place
        if data.get('place_of_birth_label') and data.get('place_of_birth'):
            place_name = data['place_of_birth_label']
            wikidata_url = data['place_of_birth']
            
            if place_name not in places:
                places[place_name] = {
                    'wikidata_url': wikidata_url,
                    'usage_count': 0,
                    'is_birth_place': True,
                    'is_death_place': False
                }
            places[place_name]['usage_count'] += 1
        
        # Death place
        if data.get('place_of_death_label') and data.get('place_of_death'):
            place_name = data['place_of_death_label']
            wikidata_url = data['place_of_death']
            
            if place_name not in places:
                places[place_name] = {
                    'wikidata_url': wikidata_url,
                    'usage_count': 0,
                    'is_birth_place': False,
                    'is_death_place': True
                }
            else:
                places[place_name]['is_death_place'] = True
            places[place_name]['usage_count'] += 1
    
    return places

def main():
    """Main enrichment process"""
    print("=== Location Enrichment from Wikidata ===")
    
    # Load data
    wikidata_config = load_json(Path('data/processed/wikidata_mathematician_config.json'))
    locations = load_json(Path('../frontend/public/data/locations.json'))
    
    print(f"Loaded {len(locations)} existing locations")
    print(f"Processing {wikidata_config['metadata']['total_mathematicians']} mathematicians")
    
    # Extract places from wikidata
    wikidata_places = extract_wikidata_places(wikidata_config)
    print(f"Found {len(wikidata_places)} unique places in wikidata")
    
    # Find places to add
    new_places = {}
    similar_places = {}
    
    for place_name, metadata in wikidata_places.items():
        similar = find_similar_locations(place_name, locations)
        
        if similar:
            similar_places[place_name] = {
                'similar_to': similar,
                'metadata': metadata
            }
            print(f"Similar: '{place_name}' -> {similar}")
        else:
            new_places[place_name] = metadata
    
    print(f"\n=== Summary ===")
    print(f"Places with similar matches: {len(similar_places)}")
    print(f"Completely new places: {len(new_places)}")
    
    # Process high-priority places first (most commonly referenced)
    priority_places = sorted(new_places.items(), key=lambda x: x[1]['usage_count'], reverse=True)
    
    print(f"\n=== Top 20 New Places by Usage ===")
    for place_name, metadata in priority_places[:20]:
        print(f"{metadata['usage_count']:2d}: {place_name}")
    
    # Proceed with adding places automatically
    print(f"\nProceeding to add top {min(50, len(priority_places))} places...")
    
    # Geocode and add new places
    added_count = 0
    failed_count = 0
    
    for place_name, metadata in priority_places[:50]:  # Process top 50
        print(f"\nProcessing: {place_name} (used {metadata['usage_count']} times)")
        
        coordinates = geocode_location(place_name, metadata['wikidata_url'])
        
        if coordinates:
            location_entry = create_location_entry(place_name, coordinates, metadata['wikidata_url'])
            locations[place_name] = location_entry
            added_count += 1
            print(f"  ✓ Added: {coordinates['display_name']}")
        else:
            failed_count += 1
            print(f"  ✗ Failed to geocode: {place_name}")
    
    # Save updated locations
    save_json(Path('../frontend/public/data/locations.json'), locations)
    
    print(f"\n=== Final Results ===")
    print(f"Successfully added: {added_count}")
    print(f"Failed to geocode: {failed_count}")
    print(f"Total locations now: {len(locations)}")
    
    # Save analysis for review
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'wikidata_places_total': len(wikidata_places),
        'similar_places': similar_places,
        'added_places': added_count,
        'failed_places': failed_count,
        'priority_places': dict(priority_places[:100])  # Save top 100 for review
    }
    
    save_json(Path('data/processed/location_enrichment_analysis.json'), analysis)
    print("Analysis saved to data/processed/location_enrichment_analysis.json")

if __name__ == '__main__':
    main()
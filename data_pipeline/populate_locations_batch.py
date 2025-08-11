#!/usr/bin/env python3
"""
Populate missing locations in batches with better progress tracking.
"""

import json
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional

def load_json(file_path: Path) -> Dict:
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path: Path, data: Dict, indent: int = 2) -> None:
    """Save JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def geocode_location_simple(place_name: str) -> Optional[Dict]:
    """Simple geocoding with faster processing"""
    if not place_name or place_name.lower() == 'null':
        return None
    
    base_url = "https://nominatim.openstreetmap.org/search"
    
    # Clean up place name
    cleaned_name = place_name.strip()
    if "University of" in cleaned_name:
        cleaned_name = cleaned_name.replace("University of ", "")
    
    params = {
        'q': cleaned_name,
        'format': 'json',
        'limit': 1
    }
    
    headers = {
        'User-Agent': 'SciMap/1.0 (Educational Research Project)'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        results = response.json()
        
        if results and len(results) > 0:
            result = results[0]
            return {
                "place_name": place_name,
                "coordinates": {
                    "lat": float(result['lat']),
                    "lng": float(result['lon'])
                },
                "confidence": 0.8,
                "historical_context": f"18th century location: {place_name}",
                "alternative_names": [place_name],
                "modern_equivalent": result.get('display_name', place_name),
                "geocoded_at": datetime.now().isoformat(),
                "geocoding_method": "nominatim_batch",
                "model_version": "openstreetmap"
            }
    except Exception as e:
        print(f"Failed to geocode {place_name}: {e}")
    
    return None

def find_missing_locations(mathematicians_data: Dict, locations_data: Dict) -> Set[str]:
    """Find missing locations"""
    referenced_locations = set()
    
    for mathematician in mathematicians_data.values():
        timeline_events = mathematician.get('timeline_events', [])
        for event in timeline_events:
            location = event.get('location', {})
            place_name = location.get('place_name')
            if place_name and place_name != 'null':
                referenced_locations.add(place_name)
    
    existing_locations = set(locations_data.keys())
    missing_locations = referenced_locations - existing_locations
    
    return missing_locations

def main():
    """Process locations in batches"""
    
    # Paths
    data_dir = Path(__file__).parent
    frontend_data_dir = data_dir.parent / "frontend" / "public" / "data"
    
    mathematicians_path = frontend_data_dir / "mathematicians.json"
    locations_path = frontend_data_dir / "locations.json"
    
    print("🗺️  Batch processing missing locations")
    
    # Load data
    mathematicians_data = load_json(mathematicians_path)
    locations_data = load_json(locations_path)
    
    missing_locations = find_missing_locations(mathematicians_data, locations_data)
    missing_list = sorted(list(missing_locations))
    
    print(f"Found {len(missing_list)} missing locations")
    print(f"Processing first 20 locations...")
    
    # Process first 20 locations to avoid timeout
    batch_size = 20
    processed_locations = missing_list[:batch_size]
    
    successful = 0
    failed = []
    
    for i, place_name in enumerate(processed_locations, 1):
        print(f"[{i}/{len(processed_locations)}] {place_name}")
        
        location_data = geocode_location_simple(place_name)
        
        if location_data:
            locations_data[place_name] = location_data
            successful += 1
            print(f"  ✅ Success")
        else:
            failed.append(place_name)
            print(f"  ❌ Failed")
        
        # Rate limiting
        if i < len(processed_locations):
            time.sleep(1)
    
    print(f"\n📊 Results:")
    print(f"✅ Successfully geocoded: {successful}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful > 0:
        print(f"\n💾 Saving updated locations.json...")
        save_json(locations_path, locations_data)
        print("✅ Updated!")
        
        print(f"\nRemaining locations to process: {len(missing_list) - batch_size}")
        if len(missing_list) > batch_size:
            print("Run the script again to process more locations.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Analyze places in wikidata_mathematician_config.json and compare with locations.json
"""

import json
from collections import Counter

def main():
    # Load wikidata config
    with open('data/processed/wikidata_mathematician_config.json', 'r') as f:
        wikidata_config = json.load(f)
    
    # Load current locations
    with open('../frontend/public/data/locations.json', 'r') as f:
        locations = json.load(f)
    
    # Extract all birth and death places from wikidata
    birth_places = []
    death_places = []
    
    for mathematician_id, data in wikidata_config['mathematicians'].items():
        if data.get('place_of_birth_label'):
            birth_places.append(data['place_of_birth_label'])
        if data.get('place_of_death_label'):
            death_places.append(data['place_of_death_label'])
    
    all_wikidata_places = birth_places + death_places
    unique_wikidata_places = set(all_wikidata_places)
    current_location_keys = set(locations.keys())
    
    print(f"=== Wikidata Places Analysis ===")
    print(f"Total mathematicians: {wikidata_config['metadata']['total_mathematicians']}")
    print(f"Birth places found: {len(birth_places)}")
    print(f"Death places found: {len(death_places)}")
    print(f"Unique places total: {len(unique_wikidata_places)}")
    print(f"Current locations.json entries: {len(current_location_keys)}")
    
    # Find most common places
    place_counts = Counter(all_wikidata_places)
    print(f"\n=== Top 15 Most Common Places ===")
    for place, count in place_counts.most_common(15):
        print(f"{count:2d}: {place}")
    
    # Find places not in current locations.json
    missing_places = unique_wikidata_places - current_location_keys
    print(f"\n=== Places Missing from locations.json ===")
    print(f"Missing places count: {len(missing_places)}")
    print("Sample missing places:")
    for place in sorted(list(missing_places))[:15]:
        print(f"  - {place}")
    
    # Find places that match (case-insensitive or similar)
    current_location_keys_lower = {k.lower() for k in current_location_keys}
    wikidata_places_lower = {p.lower() for p in unique_wikidata_places}
    
    matches = current_location_keys_lower & wikidata_places_lower
    print(f"\n=== Approximate Matches ===")
    print(f"Places that likely match: {len(matches)}")
    
    return unique_wikidata_places, missing_places, wikidata_config

if __name__ == '__main__':
    main()
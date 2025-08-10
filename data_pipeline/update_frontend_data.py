#!/usr/bin/env python3
"""Update frontend data with new Wikidata-sourced mathematicians"""

import json
import os
import shutil
from datetime import datetime

def update_frontend_data():
    """Update frontend mathematicians.json with our new dataset"""
    
    print("=== Updating Frontend Data ===")
    
    # Load our new dataset
    new_data_file = "data/processed/frontend_ready_mathematicians.json"
    frontend_data_file = "../frontend/public/data/mathematicians.json"
    
    if not os.path.exists(new_data_file):
        print(f"❌ New data file not found: {new_data_file}")
        return
    
    with open(new_data_file, 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    new_mathematicians = new_data['mathematicians']
    print(f"✓ Loaded {len(new_mathematicians)} new mathematicians")
    
    # Backup existing data
    if os.path.exists(frontend_data_file):
        backup_file = f"../frontend/public/data/mathematicians_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(frontend_data_file, backup_file)
        print(f"✓ Backed up existing data to: {backup_file}")
    
    # Convert our data to match the frontend structure
    frontend_mathematicians = {}
    
    for mathematician_id, data in new_mathematicians.items():
        # Create enhanced structure matching existing format
        enhanced_mathematician = {
            "id": data["id"],
            "name": data["name"],
            "birth_year": data["birth_year"],
            "death_year": data["death_year"],
            "wikipedia_url": data.get("wikipedia_url", ""),
            "page_views": 0,  # Will be populated later
            "popularity_tier": "medium",  # Default
            "fields": data.get("fields", ["mathematics"]),
            "nationality": data["nationality"],
            "coordinates": data["coordinates"],
            "timeline_events": []
        }
        
        # Convert timeline events to match frontend structure
        for event in data["timeline_events"]:
            enhanced_event = {
                "year": event["year"],
                "year_confidence": "estimated",
                "event_type": event["event_type"],
                "description": event["description"],
                "location": {
                    "place_name": "Historical Location",
                    "raw_text": event["description"],
                    "confidence": 0.8,
                    "coordinates": {
                        "lat": data["coordinates"][0],
                        "lng": data["coordinates"][1]
                    },
                    "geocoding_confidence": 0.8,
                    "historical_context": f"In {event['year']}, this was a significant location in European mathematics."
                },
                "source_text": f"Historical data for {data['name']}",
                "confidence": 0.8,
                "extraction_metadata": {
                    "model_version": "wikidata_pipeline",
                    "extracted_at": datetime.now().isoformat(),
                    "extraction_confidence": 0.8
                }
            }
            enhanced_mathematician["timeline_events"].append(enhanced_event)
        
        # Sort timeline events by year
        enhanced_mathematician["timeline_events"].sort(key=lambda x: x["year"])
        
        frontend_mathematicians[mathematician_id] = enhanced_mathematician
    
    # Write updated data to frontend
    os.makedirs(os.path.dirname(frontend_data_file), exist_ok=True)
    with open(frontend_data_file, 'w', encoding='utf-8') as f:
        json.dump(frontend_mathematicians, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated frontend data: {frontend_data_file}")
    print(f"   Total mathematicians: {len(frontend_mathematicians)}")
    
    # Show summary
    print(f"\n=== Updated Dataset Summary ===")
    total_events = sum(len(m["timeline_events"]) for m in frontend_mathematicians.values())
    avg_events = total_events / len(frontend_mathematicians)
    
    nationalities = {}
    birth_years = []
    
    for m in frontend_mathematicians.values():
        nat = m["nationality"]
        nationalities[nat] = nationalities.get(nat, 0) + 1
        if m["birth_year"]:
            birth_years.append(m["birth_year"])
    
    print(f"Average events per mathematician: {avg_events:.1f}")
    print(f"Birth year range: {min(birth_years)}-{max(birth_years)}")
    
    print(f"\nNationalities:")
    for nat, count in sorted(nationalities.items(), key=lambda x: x[1], reverse=True):
        print(f"  {nat}: {count}")
    
    print(f"\n🎯 Frontend updated! Ready to test with new dataset.")
    
    # Update locations.json if needed
    locations_file = "../frontend/public/data/locations.json"
    if os.path.exists(locations_file):
        with open(locations_file, 'r', encoding='utf-8') as f:
            locations = json.load(f)
        
        # Add any new locations
        updated_locations = False
        for mathematician_id, data in frontend_mathematicians.items():
            if mathematician_id not in locations:
                locations[mathematician_id] = {
                    "coordinates": data["coordinates"],
                    "place_name": f"{data['nationality']} Mathematical Center",
                    "historical_period": f"{data['birth_year']}-{data['death_year']}",
                    "confidence": 0.8
                }
                updated_locations = True
        
        if updated_locations:
            with open(locations_file, 'w', encoding='utf-8') as f:
                json.dump(locations, f, indent=2, ensure_ascii=False)
            print(f"✓ Updated locations.json with new entries")
    
    return frontend_data_file

if __name__ == "__main__":
    update_frontend_data()
#!/usr/bin/env python3
"""
Convert political.json data to frontend-compatible format.
Transforms the political events data structure to match the frontend PoliticalContext interface.
"""

import json
import os
from pathlib import Path

def convert_political_data():
    """Convert political.json to frontend format"""
    
    # Paths
    data_dir = Path(__file__).parent / "data"
    frontend_data_dir = Path(__file__).parent.parent / "frontend" / "public" / "data"
    
    political_json_path = data_dir / "political.json"
    output_path = frontend_data_dir / "political_context.json"
    
    print(f"Loading political data from: {political_json_path}")
    
    # Load the political.json data
    with open(political_json_path, 'r', encoding='utf-8') as f:
        political_events = json.load(f)
    
    print(f"Loaded {len(political_events)} political events")
    
    # Convert to frontend format
    frontend_political_data = {}
    
    for event in political_events:
        # Create frontend-compatible format
        frontend_event = {
            "context_id": event["id"],
            "year": event["year"],
            "location": {
                "place_name": event["location"]["primary_location"],
                "lat": event["location"]["coordinates"]["lat"],
                "lng": event["location"]["coordinates"]["lng"],
                "region": event["location"]["region"]
            },
            "headline": event["headline"],
            "description": event["description"],
            "impact_on_science": event["impact_on_science"],
            "category": event["category"],
            "source": event["wiki_link"],
            "relevance_score": event["relevance_score"]
        }
        
        # Use the event ID as the key
        frontend_political_data[event["id"]] = frontend_event
    
    # Ensure output directory exists
    frontend_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Write to frontend public data directory
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(frontend_political_data, f, indent=2, ensure_ascii=False)
    
    print(f"Converted {len(frontend_political_data)} political events to: {output_path}")
    
    # Also create the array format expected by the new interface
    array_format_path = frontend_data_dir / "political_events.json"
    with open(array_format_path, 'w', encoding='utf-8') as f:
        json.dump(political_events, f, indent=2, ensure_ascii=False)
    
    print(f"Also created array format at: {array_format_path}")
    
    return len(frontend_political_data)

if __name__ == "__main__":
    convert_political_data()
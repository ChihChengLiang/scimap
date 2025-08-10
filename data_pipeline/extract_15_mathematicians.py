#!/usr/bin/env python3
"""Extract exactly 15 mathematicians for the frontend using Wikidata SPARQL"""

import os
import json
from datetime import datetime
from scrapers.wikidata_sparql import WikidataSPARQLExtractor

def main():
    """Extract exactly 15 high-quality mathematicians with structured data"""
    print("=== Extracting 15 High-Quality 18th Century Mathematicians ===")
    
    extractor = WikidataSPARQLExtractor()
    
    # Get a larger set first, then filter for quality
    mathematicians = extractor.extract_18th_century_mathematicians(1650, 1750)
    
    if not mathematicians:
        print("❌ No mathematicians found")
        return
    
    print(f"✓ Found {len(mathematicians)} total mathematicians")
    
    # Score and filter for quality
    def quality_score(m):
        score = 0
        # Wikipedia URL (essential)
        if m.get('wikipedia_url'): score += 10
        # Birth coordinates 
        if m.get('birth_place', {}).get('coordinates'): score += 5
        # Complete dates
        if m.get('birth_year') and m.get('death_year'): score += 3
        # 18th century focus
        birth_year = m.get('birth_year', 0)
        if 1700 <= birth_year <= 1750: score += 5
        elif 1650 <= birth_year <= 1699: score += 2
        # Has nationality
        if m.get('nationality'): score += 2
        # Has image
        if m.get('image_url'): score += 1
        return score
    
    # Get top 15 by quality score
    top_15 = sorted(mathematicians, key=quality_score, reverse=True)[:15]
    
    print(f"✓ Selected top 15 mathematicians by quality score")
    
    # Create output structure
    os.makedirs("data/processed", exist_ok=True)
    
    # Convert to frontend format
    frontend_mathematicians = {}
    
    for i, mathematician in enumerate(top_15, 1):
        # Clean name for ID
        name = mathematician.get('name', f'mathematician_{i}')
        clean_id = name.lower().replace(' ', '_').replace('.', '').replace(',', '')
        
        # Extract coordinates
        coords = mathematician.get('birth_place', {}).get('coordinates')
        if coords:
            coordinates = [coords['lat'], coords['lng']]
        else:
            # Fallback coordinates for major European mathematical centers
            fallback_coords = {
                'swiss': [46.8182, 8.2275],  # Switzerland
                'german': [51.1657, 10.4515],  # Germany  
                'french': [46.2276, 2.2137],  # France
                'british': [55.3781, -3.4360],  # UK
                'italian': [41.8719, 12.5674],  # Italy
                'dutch': [52.1326, 5.2913],  # Netherlands
                'russian': [61.5240, 105.3188]  # Russia
            }
            nationality = mathematician.get('nationality', '').lower()
            if 'swiss' in nationality: coordinates = fallback_coords['swiss']
            elif 'german' in nationality: coordinates = fallback_coords['german'] 
            elif 'french' in nationality: coordinates = fallback_coords['french']
            elif 'british' in nationality or 'english' in nationality: coordinates = fallback_coords['british']
            elif 'italian' in nationality: coordinates = fallback_coords['italian']
            elif 'dutch' in nationality: coordinates = fallback_coords['dutch']
            elif 'russian' in nationality: coordinates = fallback_coords['russian']
            else: coordinates = [50.0, 10.0]  # Central Europe default
        
        # Create frontend mathematician entry
        frontend_entry = {
            "id": clean_id,
            "name": name,
            "birth_year": mathematician.get('birth_year'),
            "death_year": mathematician.get('death_year'),
            "nationality": mathematician.get('nationality', 'Unknown'),
            "fields": mathematician.get('fields', ['mathematics']),
            "coordinates": coordinates,
            "wikipedia_url": mathematician.get('wikipedia_url', ''),
            "image_url": mathematician.get('image_url', ''),
            "birth_place": mathematician.get('birth_place', {}).get('name', 'Unknown'),
            
            # Sample timeline events (will be enhanced by LM Studio later)
            "timeline_events": [
                {
                    "year": mathematician.get('birth_year'),
                    "event_type": "birth", 
                    "title": "Birth",
                    "description": f"Born in {mathematician.get('birth_place', {}).get('name', 'Unknown location')}"
                },
                {
                    "year": mathematician.get('death_year'),
                    "event_type": "death",
                    "title": "Death", 
                    "description": f"Died at age {mathematician.get('death_year', 0) - mathematician.get('birth_year', 0)}"
                }
            ],
            
            # Wikidata metadata
            "wikidata_id": mathematician.get('wikidata_id'),
            "data_quality_score": quality_score(mathematician),
            "data_source": "wikidata_sparql",
            "extracted_at": datetime.now().isoformat()
        }
        
        frontend_mathematicians[clean_id] = frontend_entry
        
        print(f"{i:2d}. {name} ({mathematician.get('birth_year')}-{mathematician.get('death_year')}) - {mathematician.get('nationality')} [Score: {quality_score(mathematician)}]")
    
    # Save to frontend data structure
    output_data = {
        "metadata": {
            "source": "wikidata_sparql_extraction",
            "generated_at": datetime.now().isoformat(),
            "total_mathematicians": len(frontend_mathematicians),
            "data_quality": "high_structured",
            "extraction_method": "wikidata_sparql_top_15_by_quality"
        },
        "mathematicians": frontend_mathematicians
    }
    
    output_file = "data/processed/frontend_mathematicians_15.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved 15 high-quality mathematicians to: {output_file}")
    print(f"   Ready for frontend integration!")
    
    # Show sample data
    sample = list(frontend_mathematicians.values())[0]
    print(f"\n=== Sample Entry: {sample['name']} ===")
    print(f"Birth: {sample['birth_year']} in {sample['birth_place']}")
    print(f"Coordinates: {sample['coordinates']}")
    print(f"Wikipedia: {sample['wikipedia_url']}")
    print(f"Quality Score: {sample['data_quality_score']}")

if __name__ == "__main__":
    main()
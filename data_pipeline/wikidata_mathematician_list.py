#!/usr/bin/env python3
"""Use Wikidata to get list of mathematicians and Wikipedia URLs, then use existing pipeline"""

import json
import os
from datetime import datetime
from scrapers.wikidata_sparql import WikidataSPARQLExtractor

def get_mathematician_list():
    """Get list of mathematicians from Wikidata with Wikipedia URLs"""
    
    print("=== Getting Mathematician List from Wikidata ===")
    
    extractor = WikidataSPARQLExtractor()
    
    # Simplified query based on your working query
    query = """
    SELECT ?person ?personLabel ?birthDate ?deathDate ?wikipediaArticle ?image ?place_of_birth ?place_of_birthLabel ?place_of_death ?place_of_deathLabel 
    WHERE {
      ?person wdt:P31 wd:Q5 .
      ?person wdt:P106/wdt:P279* wd:Q170790 .
      ?person wdt:P569 ?birthDate .
      ?person wdt:P570 ?deathDate .
      
      FILTER(YEAR(?birthDate) >= 1650 && YEAR(?birthDate) <= 1750)
      
      OPTIONAL {
        ?wikipediaArticle schema:about ?person .
        ?wikipediaArticle schema:isPartOf <https://en.wikipedia.org/> .
      }
      OPTIONAL { ?person wdt:P18 ?image. }
      OPTIONAL { ?person wdt:P19 ?place_of_birth. }
      OPTIONAL { ?person wdt:P20 ?place_of_death. }
      
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    ORDER BY ?birthDate
    """
    
    print("Executing SPARQL query...")
    results = extractor.execute_sparql_query(query)
    
    if not results:
        print("❌ Failed to get results from Wikidata")
        return []
    
    bindings = results.get('results', {}).get('bindings', [])
    print(f"✓ Retrieved {len(bindings)} results from Wikidata")
    
    # Process results into simple mathematician list
    mathematicians = []
    
    for binding in bindings:
        try:
            name = binding.get('personLabel', {}).get('value', 'Unknown')
            wikipedia_url = binding.get('wikipediaArticle', {}).get('value', '')
            
            # Extract birth/death years
            birth_date = binding.get('birthDate', {}).get('value', '')
            death_date = binding.get('deathDate', {}).get('value', '')
            
            birth_year = None
            death_year = None
            
            if birth_date:
                try:
                    birth_year = int(birth_date[:4])
                except:
                    pass
                    
            if death_date:
                try:
                    death_year = int(death_date[:4])
                except:
                    pass
            
            image = binding.get('image', {}).get('value', None)
            place_of_birth = binding.get('place_of_birth', {}).get('value', None)
            place_of_birth_label = binding.get('place_of_birthLabel', {}).get('value', None)
            place_of_death = binding.get('place_of_death', {}).get('value', None)
            place_of_death_label = binding.get('place_of_deathLabel', {}).get('value', None)

            # Only include mathematicians with Wikipedia URLs
            if wikipedia_url and name != 'Unknown':
                mathematician = {
                    'name': name,
                    'birth_year': birth_year,
                    'death_year': death_year,
                    'image': image,
                    'place_of_birth': place_of_birth,
                    'place_of_birth_label': place_of_birth_label,
                    'place_of_death': place_of_death,
                    'place_of_death_label': place_of_death_label,
                    'wikipedia_url': wikipedia_url,
                    'source': 'wikidata_list'
                }
                mathematicians.append(mathematician)
                
        except Exception as e:
            print(f"Error processing entry: {e}")
            continue
    
    print(f"✓ Processed {len(mathematicians)} mathematicians with Wikipedia URLs")

    # Create output for existing pipeline
    os.makedirs("data/processed", exist_ok=True)
    
    # Format for existing Wikipedia scraper pipeline
    mathematician_config = {}

    for i, m in enumerate(mathematicians):
        # Create clean ID
        clean_name = m['name'].lower().replace(' ', '_').replace('.', '').replace(',', '').replace('-', '_')
        mathematician_id = clean_name
        
        mathematician_config[mathematician_id] = {
            'name': m['name'],
            'birth_year': m['birth_year'],
            'death_year': m['death_year'],
            'image': m['image'],
            'place_of_birth': m['place_of_birth'],
            'place_of_birth_label': m['place_of_birth_label'],
            'place_of_death': m['place_of_death'],
            'place_of_death_label': m['place_of_death_label'],
            'wikipedia_url': m['wikipedia_url']
        }
        
        print(f"{i+1:2d}. {m['name']} ({m['birth_year']}-{m['death_year']})")
        print(f"     {m['wikipedia_url']}")

    # Save mathematician config for existing pipeline
    config_file = "data/processed/wikidata_mathematician_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'source': 'wikidata_sparql_list',
                'generated_at': datetime.now().isoformat(),
                'total_mathematicians': len(mathematician_config),
                'method': 'wikidata_list_wikipedia_scraping'
            },
            'mathematicians': mathematician_config
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved mathematician config: {config_file}")
    print(f"🎯 Ready to run existing Wikipedia scraping pipeline!")
    print(f"\nNext step: Run Wikipedia scraper with this config")
    
    return config_file, mathematician_config

if __name__ == "__main__":
    get_mathematician_list()
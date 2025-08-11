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
    SELECT ?person ?personLabel ?birthDate ?deathDate ?wikipediaArticle
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
            
            # Only include mathematicians with Wikipedia URLs
            if wikipedia_url and name != 'Unknown':
                mathematician = {
                    'name': name,
                    'birth_year': birth_year,
                    'death_year': death_year,
                    'wikipedia_url': wikipedia_url,
                    'source': 'wikidata_list'
                }
                mathematicians.append(mathematician)
                
        except Exception as e:
            print(f"Error processing entry: {e}")
            continue
    
    print(f"✓ Processed {len(mathematicians)} mathematicians with Wikipedia URLs")
    
    # Filter and prioritize top mathematicians
    def priority_score(m):
        score = 0
        
        # Complete date information
        if m.get('birth_year') and m.get('death_year'):
            score += 10
        
        # 18th century focus (higher score for core period)
        birth_year = m.get('birth_year', 0)
        if 1700 <= birth_year <= 1750:
            score += 15
        elif 1650 <= birth_year <= 1699:
            score += 10
        elif 1751 <= birth_year <= 1770:
            score += 5
        
        # Well-known mathematicians (basic heuristic)
        name_lower = m.get('name', '').lower()
        famous_keywords = ['euler', 'bernoulli', 'lagrange', 'laplace', 'lambert', 'cramer', 'clairaut', 'maclaurin', 'agnesi', 'legendre', 'moivre', 'bayes', 'goldbach', 'alembert']
        for keyword in famous_keywords:
            if keyword in name_lower:
                score += 20
                break
        
        return score
    
    # Sort by priority and take top 15
    top_mathematicians = sorted(mathematicians, key=priority_score, reverse=True)

    # Create output for existing pipeline
    os.makedirs("data/processed", exist_ok=True)
    
    # Format for existing Wikipedia scraper pipeline
    mathematician_config = {}
    
    for i, m in enumerate(top_mathematicians):
        # Create clean ID
        clean_name = m['name'].lower().replace(' ', '_').replace('.', '').replace(',', '').replace('-', '_')
        mathematician_id = clean_name
        
        # Estimate nationality and fields from name/period (rough heuristic)
        nationality = "European"  # Default
        name_lower = m['name'].lower()
        
        if any(x in name_lower for x in ['euler', 'bernoulli', 'cramer']):
            nationality = "Swiss"
        elif any(x in name_lower for x in ['lagrange', 'laplace', 'legendre', 'clairaut', 'alembert']):
            nationality = "French"
        elif any(x in name_lower for x in ['lambert', 'goldbach']):
            nationality = "German"
        elif any(x in name_lower for x in ['agnesi']):
            nationality = "Italian"
        elif any(x in name_lower for x in ['maclaurin']):
            nationality = "Scottish"
        elif any(x in name_lower for x in ['moivre', 'bayes']):
            nationality = "English"
        
        mathematician_config[mathematician_id] = {
            'name': m['name'],
            'birth_year': m['birth_year'],
            'death_year': m['death_year'],
            'nationality': nationality,
            'fields': ['mathematics'],
            'wikipedia_url': m['wikipedia_url']
        }
        
        print(f"{i+1:2d}. {m['name']} ({m['birth_year']}-{m['death_year']}) - {nationality}")
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
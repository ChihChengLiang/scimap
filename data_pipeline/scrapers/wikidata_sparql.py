"""Wikidata SPARQL endpoint integration for structured biographical data extraction"""

import requests
import json
import re
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
from urllib.parse import quote, unquote

class WikidataSPARQLExtractor:
    def __init__(self, endpoint_url: str = "https://query.wikidata.org/sparql", cache_dir: str = "data/cache/wikidata"):
        """Initialize Wikidata SPARQL extractor with caching"""
        self.endpoint_url = endpoint_url
        self.cache_dir = cache_dir
        self.cache_expiry_hours = 24  # Cache for 24 hours
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        self.session = requests.Session()
        # Set User-Agent as required by Wikidata
        self.session.headers.update({
            'User-Agent': 'SciMap/1.0 (https://github.com/scimap/timeline-viz) Python/requests',
            'Accept': 'application/sparql-results+json'
        })
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        query_hash = hashlib.md5(query.encode('utf-8')).hexdigest()
        return f"sparql_{query_hash}.json"
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get full cache file path"""
        return os.path.join(self.cache_dir, cache_key)
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache file is valid and not expired"""
        if not os.path.exists(cache_path):
            return False
        
        # Check if cache is expired
        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        expiry_time = cache_time + timedelta(hours=self.cache_expiry_hours)
        
        return datetime.now() < expiry_time
    
    def _load_from_cache(self, cache_path: str) -> Optional[Dict]:
        """Load results from cache file"""
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache {cache_path}: {e}")
            return None
    
    def _save_to_cache(self, cache_path: str, data: Dict) -> None:
        """Save results to cache file"""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving cache {cache_path}: {e}")

    def execute_sparql_query(self, query: str, max_retries: int = 3) -> Optional[Dict]:
        """Execute SPARQL query with caching support"""
        
        # Check cache first
        cache_key = self._get_cache_key(query)
        cache_path = self._get_cache_path(cache_key)
        
        if self._is_cache_valid(cache_path):
            print(f"💾 Using cached SPARQL results: {cache_key}")
            cached_data = self._load_from_cache(cache_path)
            if cached_data:
                return cached_data
        
        # Execute query if not cached or cache invalid
        print(f"🌐 Executing SPARQL query against Wikidata...")
        
        for attempt in range(max_retries + 1):
            try:
                params = {
                    'query': query,
                    'format': 'json'
                }
                
                response = self.session.get(
                    self.endpoint_url, 
                    params=params,
                    timeout=120
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Save to cache
                self._save_to_cache(cache_path, result)
                print(f"💾 Saved SPARQL results to cache: {cache_key}")
                
                return result
                
            except requests.exceptions.Timeout:
                print(f"Query timeout on attempt {attempt + 1}/{max_retries + 1}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries:
                    time.sleep(1)
                    
        print("Failed to execute SPARQL query after all retries")
        return None
    
    def extract_18th_century_mathematicians(self, birth_year_start: int = 1650, birth_year_end: int = 1750) -> List[Dict]:
        """Extract 18th century mathematicians using SPARQL query"""
        
        sparql_query = f"""
        SELECT ?person ?personLabel ?birthDate ?deathDate ?wikipediaArticle
        WHERE {{
            ?person wdt:P31 wd:Q5 .
            ?person wdt:P106/wdt:P279* wd:Q170790 .
            ?person wdt:P569 ?birthDate .
            ?person wdt:P570 ?deathDate .
            
            FILTER(YEAR(?birthDate) >= {birth_year_start} && YEAR(?birthDate) <= {birth_year_end})
            
            OPTIONAL {{
                ?wikipediaArticle schema:about ?person .
                ?wikipediaArticle schema:isPartOf <https://en.wikipedia.org/> .
            }}
            
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
        ORDER BY ?birthDate
        """
        
        print(f"Executing SPARQL query for mathematicians born {birth_year_start}-{birth_year_end}")
        print("Query endpoint: https://query.wikidata.org/sparql")
        
        results = self.execute_sparql_query(sparql_query)
        
        if not results:
            print("Failed to retrieve data from Wikidata")
            return []
        
        bindings = results.get('results', {}).get('bindings', [])
        print(f"Retrieved {len(bindings)} raw results from Wikidata")
        
        # Process and clean the results
        mathematicians = []
        processed_entities = set()
        
        for binding in bindings:
            try:
                mathematician_data = self._process_wikidata_binding(binding)
                
                # Avoid duplicates
                entity_id = mathematician_data.get('wikidata_id')
                if entity_id not in processed_entities:
                    mathematicians.append(mathematician_data)
                    processed_entities.add(entity_id)
                    
            except Exception as e:
                print(f"Error processing mathematician entry: {e}")
                continue
        
        print(f"Successfully processed {len(mathematicians)} unique mathematicians")
        return mathematicians
    
    def _process_wikidata_binding(self, binding: Dict) -> Dict:
        """Process a single Wikidata SPARQL binding into structured data"""
        
        # Extract Wikidata entity ID from URI
        person_uri = binding.get('person', {}).get('value', '')
        wikidata_id = person_uri.split('/')[-1] if person_uri else None
        
        # Extract and parse dates
        birth_date_raw = binding.get('birthDate', {}).get('value', '')
        death_date_raw = binding.get('deathDate', {}).get('value', '')
        
        birth_year = self._extract_year(birth_date_raw)
        death_year = self._extract_year(death_date_raw)
        
        # Extract coordinates if available
        coord_raw = binding.get('birthCoord', {}).get('value', '')
        coordinates = self._parse_coordinates(coord_raw) if coord_raw else None
        
        # Extract Wikipedia URL
        wikipedia_url = binding.get('wikipediaArticle', {}).get('value', '')
        
        # Build structured mathematician data
        mathematician_data = {
            'wikidata_id': wikidata_id,
            'name': binding.get('personLabel', {}).get('value', 'Unknown'),
            'birth_year': birth_year,
            'death_year': death_year,
            'birth_date_full': birth_date_raw,
            'death_date_full': death_date_raw,
            'wikipedia_url': wikipedia_url,
            'nationality': binding.get('nationalityLabel', {}).get('value', ''),
            'birth_place': {
                'name': binding.get('birthPlaceLabel', {}).get('value', ''),
                'wikidata_uri': binding.get('birthPlace', {}).get('value', ''),
                'coordinates': coordinates
            },
            'image_url': binding.get('image', {}).get('value', ''),
            'fields': [binding.get('fieldLabel', {}).get('value', 'mathematics')] if binding.get('fieldLabel') else ['mathematics'],
            'data_source': 'wikidata_sparql',
            'extracted_at': datetime.now().isoformat(),
            'wikidata_query_metadata': {
                'query_date': datetime.now().isoformat(),
                'endpoint': self.endpoint_url,
                'data_quality': 'structured'
            }
        }
        
        return mathematician_data
    
    def _extract_year(self, date_string: str) -> Optional[int]:
        """Extract year from Wikidata date string"""
        if not date_string:
            return None
        
        # Wikidata dates are typically in ISO format: YYYY-MM-DDTHH:MM:SSZ
        try:
            if 'T' in date_string:
                date_part = date_string.split('T')[0]
            else:
                date_part = date_string
                
            year_match = re.match(r'^[+-]?(\d{4})', date_part)
            if year_match:
                return int(year_match.group(1))
                
        except (ValueError, AttributeError) as e:
            print(f"Error parsing date '{date_string}': {e}")
        
        return None
    
    def _parse_coordinates(self, coord_string: str) -> Optional[Dict[str, float]]:
        """Parse Wikidata Point coordinate string"""
        if not coord_string or 'Point(' not in coord_string:
            return None
        
        try:
            # Format: Point(longitude latitude)
            coord_match = re.search(r'Point\(([+-]?\d+\.?\d*)\s+([+-]?\d+\.?\d*)\)', coord_string)
            if coord_match:
                longitude = float(coord_match.group(1))
                latitude = float(coord_match.group(2))
                
                return {
                    'lat': latitude,
                    'lng': longitude,
                    'source': 'wikidata_sparql'
                }
        except (ValueError, AttributeError) as e:
            print(f"Error parsing coordinates '{coord_string}': {e}")
        
        return None
    
    def enrich_existing_mathematician(self, mathematician_data: Dict) -> Dict:
        """Enrich existing mathematician data with Wikidata structured information"""
        
        name = mathematician_data.get('name', '')
        if not name:
            return mathematician_data
        
        print(f"Enriching {name} with Wikidata structured data")
        
        # Search for mathematician by name
        search_query = f"""
        SELECT ?person ?personLabel ?birthDate ?deathDate ?birthPlace ?birthPlaceLabel 
               ?birthCoord ?nationality ?nationalityLabel ?image ?wikipediaArticle
        WHERE {{
          ?person wdt:P31 wd:Q5 .
          ?person wdt:P106/wdt:P279* wd:Q170790 .
          ?person rdfs:label "{name}"@en .
          
          OPTIONAL {{ ?person wdt:P569 ?birthDate . }}
          OPTIONAL {{ ?person wdt:P570 ?deathDate . }}
          OPTIONAL {{ ?person wdt:P19 ?birthPlace . }}
          OPTIONAL {{ ?birthPlace wdt:P625 ?birthCoord . }}
          OPTIONAL {{ ?person wdt:P27 ?nationality . }}
          OPTIONAL {{ ?person wdt:P18 ?image . }}
          
          OPTIONAL {{
            ?wikipediaArticle schema:about ?person .
            ?wikipediaArticle schema:isPartOf <https://en.wikipedia.org/> .
          }}
          
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """
        
        results = self.execute_sparql_query(search_query)
        
        if results and results.get('results', {}).get('bindings'):
            binding = results['results']['bindings'][0]
            wikidata_enrichment = self._process_wikidata_binding(binding)
            
            # Merge Wikidata structured data with existing data
            enriched_data = mathematician_data.copy()
            enriched_data.update({
                'wikidata_structured_data': wikidata_enrichment,
                'enhanced_with_wikidata': True,
                'wikidata_enrichment_date': datetime.now().isoformat()
            })
            
            # Update coordinates if not present
            if not enriched_data.get('coordinates') and wikidata_enrichment['birth_place']['coordinates']:
                enriched_data['coordinates'] = wikidata_enrichment['birth_place']['coordinates']
            
            print(f"✓ Successfully enriched {name} with Wikidata structured data")
            return enriched_data
        
        print(f"✗ No Wikidata match found for {name}")
        return mathematician_data
    
    def save_mathematicians_data(self, mathematicians: List[Dict], output_file: str):
        """Save mathematicians data to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'extraction_metadata': {
                        'source': 'wikidata_sparql',
                        'extracted_at': datetime.now().isoformat(),
                        'total_mathematicians': len(mathematicians),
                        'query_endpoint': self.endpoint_url
                    },
                    'mathematicians': mathematicians
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved {len(mathematicians)} mathematicians to {output_file}")
            
        except Exception as e:
            print(f"✗ Error saving data: {e}")

def main():
    """Main execution function"""
    print("=== Wikidata SPARQL Structured Data Extraction ===")
    
    extractor = WikidataSPARQLExtractor()
    
    # Extract 18th century mathematicians
    mathematicians = extractor.extract_18th_century_mathematicians(1650, 1750)
    
    if mathematicians:
        # Save raw Wikidata results
        output_file = "data/raw/wikidata_mathematicians.json"
        extractor.save_mathematicians_data(mathematicians, output_file)
        
        # Display summary
        print(f"\n=== Extraction Summary ===")
        print(f"Total mathematicians extracted: {len(mathematicians)}")
        print(f"Date range: 1650-1750 (birth years)")
        print(f"Average birth year: {sum(m['birth_year'] for m in mathematicians if m['birth_year']) / len([m for m in mathematicians if m['birth_year']]):.0f}")
        
        # Show sample of extracted data
        print(f"\n=== Sample Mathematicians ===")
        for i, m in enumerate(mathematicians[:5]):
            print(f"{i+1}. {m['name']} ({m['birth_year']}-{m['death_year']}) - {m['nationality']}")
            if m['birth_place']['coordinates']:
                coords = m['birth_place']['coordinates']
                print(f"   Birth: {m['birth_place']['name']} ({coords['lat']:.2f}, {coords['lng']:.2f})")
    
    else:
        print("No mathematicians were extracted from Wikidata")

if __name__ == "__main__":
    main()
"""Wikidata SPARQL endpoint integration for structured biographical data extraction"""

import requests
from typing import Dict, List, Optional, Tuple
import time
from urllib.parse import quote, unquote

class WikidataSPARQLExtractor:
    def __init__(self, endpoint_url: str = "https://query.wikidata.org/sparql"):
        """Initialize Wikidata SPARQL extractor with caching"""
        self.endpoint_url = endpoint_url

        self.session = requests.Session()
        # Set User-Agent as required by Wikidata
        self.session.headers.update({
            'User-Agent': 'SciMap/1.0 (https://github.com/scimap/timeline-viz) Python/requests',
            'Accept': 'application/sparql-results+json'
        })

    def execute_sparql_query(self, query: str, max_retries: int = 3) -> Optional[Dict]:
        """Execute SPARQL query with caching support"""

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

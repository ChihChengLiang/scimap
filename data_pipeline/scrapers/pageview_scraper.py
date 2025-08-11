"""Wikipedia page view statistics scraper using Wikimedia API"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PageViewScraper:
    def __init__(self, delay: float = 0.1):
        """Initialize page view scraper"""
        self.delay = delay
        self.base_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SciMap/1.0 (Educational Research Project; https://github.com/username/scimap)'
        })
    
    def get_page_views(self, page_title: str, days: int = 90) -> Dict:
        """Get page view statistics for a Wikipedia article"""
        try:
            # Calculate date range (last N days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format dates for API (YYYYMMDDHH format)
            start_str = start_date.strftime("%Y%m%d00")
            end_str = end_date.strftime("%Y%m%d00")
            
            # Build API URL
            url = f"{self.base_url}/{page_title}/daily/{start_str}/{end_str}"
            
            print(f"Fetching page views for: {page_title}")
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Calculate statistics
            daily_views = [item['views'] for item in data['items']]
            total_views = sum(daily_views)
            avg_daily_views = total_views / len(daily_views) if daily_views else 0
            max_daily_views = max(daily_views) if daily_views else 0
            
            # Determine popularity tier based on average daily views
            popularity_tier = self._calculate_popularity_tier(avg_daily_views)
            
            result = {
                'page_title': page_title,
                'period_days': days,
                'start_date': start_str,
                'end_date': end_str,
                'total_views': total_views,
                'avg_daily_views': round(avg_daily_views, 2),
                'max_daily_views': max_daily_views,
                'popularity_tier': popularity_tier,
                'data_points': len(daily_views),
                'retrieved_at': datetime.now().isoformat()
            }
            
            time.sleep(self.delay)  # Rate limiting
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Page not found: {page_title}")
                return {
                    'page_title': page_title,
                    'error': 'page_not_found',
                    'total_views': 0,
                    'avg_daily_views': 0,
                    'popularity_tier': 'unknown',
                    'retrieved_at': datetime.now().isoformat()
                }
            else:
                raise e
        except Exception as e:
            print(f"Error fetching page views for {page_title}: {e}")
            return {
                'page_title': page_title,
                'error': str(e),
                'retrieved_at': datetime.now().isoformat()
            }
    
    def _calculate_popularity_tier(self, avg_daily_views: float) -> str:
        """Calculate popularity tier based on average daily page views"""
        if avg_daily_views >= 1000:
            return "very_high"
        elif avg_daily_views >= 500:
            return "high" 
        elif avg_daily_views >= 200:
            return "medium"
        elif avg_daily_views >= 50:
            return "low"
        else:
            return "very_low"
    
    def get_pageviews_for_mathematicians(self, mathematicians_data: Dict) -> Dict:
        """Get page view statistics for all mathematicians"""
        results = {}
        
        for mathematician_id, data in mathematicians_data.items():
            if 'wikipedia_data' in data and 'page_title' in data['wikipedia_data']:
                page_title = data['wikipedia_data']['page_title']
                print(f"\n=== Getting page views for {mathematician_id} ===")
                
                pageview_data = self.get_page_views(page_title)
                results[mathematician_id] = pageview_data
            else:
                print(f"No Wikipedia page title found for {mathematician_id}")
                results[mathematician_id] = {
                    'error': 'no_page_title',
                    'retrieved_at': datetime.now().isoformat()
                }
        
        return results
    
    def update_mathematician_data_with_pageviews(self, mathematician_file: str):
        """Update a mathematician's data file with page view statistics"""
        try:
            # Load existing data
            with open(mathematician_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get page title from Wikipedia data
            if 'wikipedia_data' in data and 'page_title' in data['wikipedia_data']:
                page_title = data['wikipedia_data']['page_title']
                pageview_data = self.get_page_views(page_title)
                
                # Add page view data to mathematician record
                data['page_views'] = pageview_data['total_views']
                data['avg_daily_views'] = pageview_data['avg_daily_views']
                data['popularity_tier'] = pageview_data['popularity_tier']
                data['pageview_data'] = pageview_data
                
                # Save updated data
                with open(mathematician_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"Updated {mathematician_file} with page view data")
                return True
            else:
                print(f"No page title found in {mathematician_file}")
                return False
                
        except Exception as e:
            print(f"Error updating {mathematician_file}: {e}")
            return False

if __name__ == "__main__":
    print("This script is now used as a module by the main pipeline.")
    print("Run main_pipeline.py instead.")
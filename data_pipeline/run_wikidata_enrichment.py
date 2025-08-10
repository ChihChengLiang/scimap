"""Enhanced data pipeline with Wikidata SPARQL integration"""

import os
import sys
import json
from datetime import datetime
from scrapers.wikidata_sparql import WikidataSPARQLExtractor
from scrapers.wikipedia_scraper import WikipediaScraper
from scrapers.pageview_scraper import PageViewScraper

def main():
    """Main pipeline with Wikidata SPARQL enhancement"""
    
    print("=== SciMap Enhanced Data Pipeline with Wikidata SPARQL ===")
    print("Objective: Scale to 15+ mathematicians with structured biographical data")
    
    # Initialize extractors
    wikidata_extractor = WikidataSPARQLExtractor()
    wikipedia_scraper = WikipediaScraper(delay=1.5)
    pageview_scraper = PageViewScraper(delay=0.2)
    
    # Step 1: Extract mathematicians from Wikidata SPARQL
    print("\n1. Extracting mathematicians from Wikidata SPARQL endpoint...")
    wikidata_mathematicians = wikidata_extractor.extract_18th_century_mathematicians(1650, 1750)
    
    # Create output directories
    os.makedirs("data/raw/wikidata", exist_ok=True)
    os.makedirs("data/processed/wikidata_enhanced", exist_ok=True)
    
    if not wikidata_mathematicians:
        print("❌ No mathematicians extracted from Wikidata. Exiting.")
        return
    
    print(f"✅ Extracted {len(wikidata_mathematicians)} mathematicians from Wikidata")
    
    # Step 2: Filter and prioritize top 15 mathematicians
    print("\n2. Prioritizing top 15 mathematicians...")
    
    # Priority scoring based on data quality and completeness
    def calculate_priority_score(mathematician):
        score = 0
        
        # Wikipedia URL available (high priority)
        if mathematician.get('wikipedia_url'):
            score += 10
        
        # Birth coordinates available (structured location data)
        if mathematician.get('birth_place', {}).get('coordinates'):
            score += 5
        
        # Complete date information
        if mathematician.get('birth_year') and mathematician.get('death_year'):
            score += 3
        
        # 18th century focus (born 1700-1750 gets priority)
        birth_year = mathematician.get('birth_year', 0)
        if 1700 <= birth_year <= 1750:
            score += 5
        elif 1650 <= birth_year <= 1699:
            score += 2
        
        # Nationality information
        if mathematician.get('nationality'):
            score += 2
        
        # Image available
        if mathematician.get('image_url'):
            score += 1
        
        return score
    
    # Sort by priority and select top 15
    prioritized_mathematicians = sorted(
        wikidata_mathematicians,
        key=calculate_priority_score,
        reverse=True
    )[:15]
    
    print(f"✅ Prioritized top 15 mathematicians based on data completeness")
    
    # Step 3: Enhance with Wikipedia biographical data
    print("\n3. Enhancing with Wikipedia biographical narratives...")
    enhanced_mathematicians = []
    
    for i, mathematician in enumerate(prioritized_mathematicians, 1):
        name = mathematician.get('name', 'Unknown')
        wikipedia_url = mathematician.get('wikipedia_url', '')
        
        print(f"Processing {i}/15: {name}")
        
        if wikipedia_url:
            try:
                # Extract Wikipedia biographical content
                wikipedia_data = wikipedia_scraper.scrape_page(wikipedia_url)
                
                if wikipedia_data:
                    # Merge Wikidata structured data with Wikipedia narrative
                    enhanced_mathematician = mathematician.copy()
                    enhanced_mathematician.update({
                        'wikipedia_data': wikipedia_data,
                        'data_sources': ['wikidata_sparql', 'wikipedia_narrative'],
                        'enhancement_level': 'wikidata_wikipedia_combined'
                    })
                    
                    # Add pageview data for popularity
                    try:
                        page_title = wikipedia_url.split('/')[-1]
                        pageview_data = pageview_scraper.get_page_views(page_title)
                        if pageview_data:
                            enhanced_mathematician.update({
                                'pageview_data': pageview_data,
                                'page_views': pageview_data.get('total_views', 0),
                                'popularity_tier': pageview_data.get('popularity_tier', 'low')
                            })
                    except Exception as e:
                        print(f"   Warning: Could not fetch pageviews for {name}: {e}")
                        enhanced_mathematician.update({
                            'page_views': 0,
                            'popularity_tier': 'unknown'
                        })
                    
                    enhanced_mathematicians.append(enhanced_mathematician)
                    print(f"   ✅ Enhanced with Wikipedia + pageview data")
                    
                else:
                    print(f"   ⚠️ Could not scrape Wikipedia for {name}")
                    enhanced_mathematicians.append(mathematician)
                    
            except Exception as e:
                print(f"   ❌ Error enhancing {name}: {e}")
                enhanced_mathematicians.append(mathematician)
        else:
            print(f"   ⚠️ No Wikipedia URL for {name}")
            enhanced_mathematicians.append(mathematician)
    
    # Step 4: Save results
    print("\n4. Saving enhanced dataset...")
    
    # Save individual mathematician files
    for mathematician in enhanced_mathematicians:
        mathematician_id = mathematician.get('name', 'unknown').lower().replace(' ', '_').replace('.', '')
        output_file = f"data/processed/wikidata_enhanced/{mathematician_id}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(mathematician, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   Error saving {mathematician_id}: {e}")
    
    # Save combined dataset
    combined_output = {
        'dataset_metadata': {
            'source': 'wikidata_sparql_wikipedia_enhanced',
            'generated_at': datetime.now().isoformat(),
            'total_mathematicians': len(enhanced_mathematicians),
            'enhancement_methods': ['wikidata_sparql', 'wikipedia_narrative', 'pageview_popularity'],
            'target_achieved': len(enhanced_mathematicians) >= 15
        },
        'mathematicians': {
            mathematician.get('name', 'unknown').lower().replace(' ', '_').replace('.', ''): mathematician
            for mathematician in enhanced_mathematicians
        }
    }
    
    with open("data/processed/wikidata_enhanced_mathematicians.json", 'w', encoding='utf-8') as f:
        json.dump(combined_output, f, indent=2, ensure_ascii=False)
    
    # Step 5: Generate summary report
    print("\n=== Enhanced Dataset Summary ===")
    print(f"Total mathematicians: {len(enhanced_mathematicians)}")
    print(f"Target achieved (15+): {'✅ Yes' if len(enhanced_mathematicians) >= 15 else '❌ No'}")
    
    # Quality metrics
    with_wikipedia = len([m for m in enhanced_mathematicians if m.get('wikipedia_data')])
    with_coordinates = len([m for m in enhanced_mathematicians if m.get('birth_place', {}).get('coordinates')])
    with_pageviews = len([m for m in enhanced_mathematicians if m.get('page_views', 0) > 0])
    
    print(f"With Wikipedia narrative: {with_wikipedia}/{len(enhanced_mathematicians)} ({with_wikipedia/len(enhanced_mathematicians)*100:.1f}%)")
    print(f"With birth coordinates: {with_coordinates}/{len(enhanced_mathematicians)} ({with_coordinates/len(enhanced_mathematicians)*100:.1f}%)")
    print(f"With popularity data: {with_pageviews}/{len(enhanced_mathematicians)} ({with_pageviews/len(enhanced_mathematicians)*100:.1f}%)")
    
    # Birth year distribution
    birth_years = [m.get('birth_year') for m in enhanced_mathematicians if m.get('birth_year')]
    if birth_years:
        print(f"Birth year range: {min(birth_years)}-{max(birth_years)}")
        print(f"Average birth year: {sum(birth_years)/len(birth_years):.0f}")
    
    # Nationality distribution
    nationalities = [m.get('nationality') for m in enhanced_mathematicians if m.get('nationality')]
    nationality_counts = {}
    for nat in nationalities:
        nationality_counts[nat] = nationality_counts.get(nat, 0) + 1
    
    print(f"Top nationalities: {dict(sorted(nationality_counts.items(), key=lambda x: x[1], reverse=True)[:5])}")
    
    # Sample mathematicians
    print(f"\n=== Sample Enhanced Mathematicians ===")
    for i, m in enumerate(enhanced_mathematicians[:5], 1):
        coords = m.get('birth_place', {}).get('coordinates', {})
        coord_str = f"({coords.get('lat', 0):.2f}, {coords.get('lng', 0):.2f})" if coords else "No coordinates"
        
        print(f"{i}. {m.get('name')} ({m.get('birth_year')}-{m.get('death_year')})")
        print(f"   Nationality: {m.get('nationality', 'Unknown')}")
        print(f"   Birth place: {m.get('birth_place', {}).get('name', 'Unknown')} {coord_str}")
        print(f"   Wikipedia: {'✅' if m.get('wikipedia_data') else '❌'}")
        print(f"   Popularity: {m.get('popularity_tier', 'unknown')} ({m.get('page_views', 0):,} views)")
    
    print(f"\n✅ Enhanced dataset saved to: data/processed/wikidata_enhanced_mathematicians.json")
    print("Ready for frontend integration and timeline extraction!")

if __name__ == "__main__":
    main()
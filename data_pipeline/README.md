# SciMap Data Pipeline - Phase 1

This directory contains the complete data extraction and processing pipeline for the 18th Century Mathematics Timeline Visualization project.

## Overview

The pipeline extracts biographical data about 18th century mathematicians from Wikipedia, processes it with LLMs to extract timeline events, geocodes historical locations, and produces clean JSON datasets for the frontend visualization.

## Prerequisites

### 1. Python Dependencies
```bash
cd data_pipeline
pip install -r requirements.txt
```

### 2. Ollama LLM Setup
The pipeline uses Ollama with the Llama 3.1 8B model for timeline extraction and geocoding.

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama server
ollama serve

# Install the model (in another terminal)
ollama pull llama3.1:8b
```

### 3. Internet Connection
- Wikipedia scraping requires internet access
- Wikipedia pageview API access needed

## Directory Structure

```
data_pipeline/
├── config/
│   └── mathematicians.py      # Target mathematician configurations
├── scrapers/
│   ├── wikipedia_scraper.py   # Wikipedia biographical data scraper
│   └── pageview_scraper.py    # Wikipedia pageview statistics
├── processors/
│   ├── llm_extractor.py       # LLM-based timeline event extraction  
│   └── geocoder.py            # Historical location geocoding
├── data/
│   ├── raw/wikipedia/         # Raw scraped Wikipedia data
│   ├── processed/             # Intermediate processed data
│   └── json/                  # Final JSON output for frontend
└── run_pipeline.py            # Main pipeline orchestrator
```

## Usage

### Quick Start (Test Mode - Tier 1 only)
```bash
cd data_pipeline
python run_pipeline.py
```

This will process 4 Tier 1 mathematicians (Euler, Lagrange, Laplace, Bernoulli) through the complete pipeline.

### Full Dataset
```bash
python run_pipeline.py --full
```

Process all 10 configured mathematicians (Tier 1 + Tier 2).

### Run Individual Steps
```bash
python run_pipeline.py --step 1  # Wikipedia scraping only
python run_pipeline.py --step 2  # Page view statistics only
python run_pipeline.py --step 3  # Timeline event extraction only
python run_pipeline.py --step 4  # Location geocoding only
python run_pipeline.py --step 5  # Final JSON generation only
```

## Pipeline Steps

### Step 1: Wikipedia Scraping
- Scrapes biographical pages for each mathematician
- Extracts main biography paragraphs and infobox data
- Rate limited to be respectful to Wikipedia
- Output: `data/raw/wikipedia/*.json`

### Step 2: Page View Statistics  
- Retrieves 90-day page view statistics from Wikimedia API
- Calculates popularity tiers based on average daily views
- Updates mathematician records with popularity data
- Output: Updated files in `data/raw/wikipedia/`

### Step 3: Timeline Event Extraction
- Uses LLM to extract timeline events from biographical text
- Focuses on 18th century events (1700-1800)
- Extracts birth, education, positions, publications, travels, death
- Includes confidence scoring and location extraction
- Output: `data/processed/with_events/*.json`

### Step 4: Location Geocoding
- Uses LLM to geocode historical place names
- Considers 18th century political boundaries and naming
- Caches results to avoid redundant geocoding
- Includes confidence scores and historical context
- Output: `data/processed/with_locations/*.json`

### Step 5: Final JSON Generation
- Creates clean datasets for frontend consumption
- Generates summary statistics and validation metrics
- Combines individual mathematician records
- Creates global location table
- Output: `data/json/mathematicians.json`, `data/json/locations.json`, `data/json/summary.json`

## Output Data Schema

### Mathematicians JSON
```json
{
  "mathematician_id": {
    "id": "leonhard_euler",
    "name": "Leonhard Euler", 
    "birth_year": 1707,
    "death_year": 1783,
    "wikipedia_url": "https://en.wikipedia.org/wiki/Leonhard_Euler",
    "page_views": 89432,
    "popularity_tier": "very_high",
    "fields": ["mathematics", "physics", "astronomy"],
    "nationality": "Swiss",
    "timeline_events": [
      {
        "year": 1727,
        "year_confidence": "exact",
        "event_type": "position",
        "description": "Joined the St. Petersburg Academy of Sciences",
        "location": {
          "place_name": "St. Petersburg",
          "coordinates": {"lat": 59.9311, "lng": 30.3609},
          "confidence": 0.95
        },
        "confidence": 0.9
      }
    ]
  }
}
```

### Locations JSON
```json
{
  "St. Petersburg": {
    "place_name": "St. Petersburg",
    "coordinates": {"lat": 59.9311, "lng": 30.3609},
    "confidence": 0.8,
    "historical_context": "Capital of Russian Empire, major center of learning",
    "alternative_names": ["Petrograd", "Leningrad"],
    "modern_equivalent": "St. Petersburg, Russia"
  }
}
```

## Success Metrics

The pipeline tracks several metrics to validate data quality:

- **Extraction Accuracy**: Events extracted vs. manually verified timeline
- **Geocoding Quality**: Coordinate accuracy for major historical cities  
- **Coverage**: Timeline events per mathematician, time period coverage
- **Completeness**: Successful processing rate across all steps

Target metrics from SPEC.md:
- ✅ 80%+ accuracy in event extraction
- ✅ All major life events captured (birth, education, career, death)
- ✅ Geocoding confidence >0.7 for major cities

## Troubleshooting

### Common Issues

**Ollama Connection Error**
```
ERROR: Ollama server is not running!
```
Solution: Start Ollama with `ollama serve` and ensure `llama3.1:8b` is installed.

**Wikipedia Rate Limiting**
```
Error scraping https://en.wikipedia.org/...: 429
```
Solution: The scraper includes rate limiting. If you encounter 429 errors, increase the delay in `WikipediaScraper(delay=2.0)`.

**LLM JSON Parsing Errors**
```
Failed to parse LLM JSON response for [mathematician]
```
Solution: The pipeline includes regex fallback extraction. Check Ollama model availability and consider retrying with a different model temperature.

**Location Cache Issues**
```
Error loading location cache
```
Solution: Delete `data/processed/location_cache.json` to start fresh, or check file permissions.

## Performance

**Estimated Runtime (Test Mode - 4 mathematicians):**
- Step 1 (Wikipedia): ~10 seconds
- Step 2 (Pageviews): ~5 seconds  
- Step 3 (LLM Events): ~30 seconds
- Step 4 (Geocoding): ~20 seconds
- Step 5 (Final JSON): ~2 seconds
- **Total: ~67 seconds**

**Full Dataset (10 mathematicians): ~150 seconds**

## Next Steps

After successful Phase 1 completion:

1. **Data Validation**: Manual review of extracted events and locations
2. **Frontend Integration**: Use generated JSON files in React visualization  
3. **Phase 2**: Implement basic globe + timeline interface
4. **Iteration**: Refine LLM prompts based on accuracy analysis

## Contributing

To add more mathematicians:
1. Update `config/mathematicians.py` with new entries
2. Ensure Wikipedia URLs are accessible
3. Run pipeline with `--full` flag
4. Validate extracted data quality
# 18th Century Mathematics Timeline Visualization
## Project Specification v1.0

### Project Overview
An interactive spatio-temporal visualization showing the lives, travels, and mathematical contributions of prominent 18th century mathematicians (1700-1800). Users can explore how mathematical ideas developed across Europe through an interactive timeline slider and 3D globe interface.

### Core Concept
- **Timeline Slider**: Navigate through decades to see mathematical activity over time
- **3D Globe**: Visualize where mathematicians lived, worked, and traveled
- **Popularity Weighting**: Scientist prominence based on Wikipedia page views
- **Event Context**: Key mathematical discoveries, publications, and career milestones

---

## Technical Architecture

### Data Sources
- **Primary**: Wikipedia biographical pages and page view statistics
- **Secondary**: Wikidata for structured biographical data (future enhancement)
- **Geocoding**: LLM-generated coordinates with manual validation (MVP approach)

### Technology Stack
- **Backend**: Python for data extraction and processing
- **LLM**: Local model (Ollama/Llama) for timeline and location extraction
- **Frontend**: React + D3.js or Three.js for globe visualization
- **Data Storage**: JSON files for MVP, database migration in later phases

---

## Data Schema

### Scientist Schema
```json
{
  "id": "leonhard_euler",
  "name": "Leonhard Euler",
  "birth_year": 1707,
  "death_year": 1783,
  "wikipedia_url": "https://en.wikipedia.org/wiki/Leonhard_Euler",
  "page_views": 89432,
  "popularity_tier": "very_high",
  "fields": ["mathematics", "physics", "astronomy"],
  "nationality": "Swiss",
  "processed_at": "2025-08-09T10:00:00Z"
}
```

### Timeline Event Schema
```json
{
  "event_id": "euler_1727_stpetersburg",
  "scientist_id": "leonhard_euler",
  "year": 1727,
  "year_confidence": "exact",
  "event_type": "position",
  "description": "Joined the St. Petersburg Academy of Sciences",
  "location": {
    "place_name": "St. Petersburg",
    "raw_text": "moved to St. Petersburg Academy of Sciences",
    "confidence": 0.95
  },
  "source_paragraph": "In 1727, Euler moved to St. Petersburg...",
  "llm_metadata": {
    "extraction_confidence": 0.9,
    "model_version": "llama-3.1-8b"
  }
}
```

### Location Table Schema
```json
{
  "place_name": "St. Petersburg",
  "coordinates": { "lat": 59.9311, "lng": 30.3609 },
  "coordinate_source": "llm_hallucination",
  "confidence": 0.8,
  "needs_verification": true,
  "historical_context": "Capital of Russian Empire, major center of learning",
  "alternative_names": ["Petrograd", "Leningrad"]
}
```

---

## MVP Scope (Phase 1)

### Target Mathematicians (10-15)
**Tier 1 (Must-have)**:
- Leonhard Euler (1707-1783)
- Joseph-Louis Lagrange (1736-1813) 
- Pierre-Simon Laplace (1749-1827)
- Daniel Bernoulli (1700-1782)

**Tier 2 (Nice-to-have)**:
- Jean le Rond d'Alembert (1717-1783)
- Alexis Clairaut (1713-1765)
- Gabriel Cramer (1704-1752)
- Colin Maclaurin (1698-1746)
- Maria Gaetana Agnesi (1718-1799)
- Émilie du Châtelet (1706-1749)

### Core Features
- [x] Timeline slider (by decade: 1700s, 1710s, ... 1790s)
- [x] Interactive 3D globe with scientist locations
- [x] Click-to-explore individual mathematician details
- [x] Visual encoding: point size by Wikipedia popularity
- [x] Event type categorization (birth, education, position, publication, death)

### Data Pipeline
1. **Wikipedia Extraction**: Scrape biographical pages for target mathematicians
2. **LLM Processing**: Extract timeline events and locations with confidence scores
3. **Geocoding**: Generate coordinates for location names (LLM-based for MVP)
4. **Data Validation**: Manual review of extracted events and coordinates
5. **Export**: Generate JSON files for frontend consumption

---

## User Experience

### Primary User Flow
1. **Landing**: User sees globe with timeline slider set to 1750s (peak activity period)
2. **Exploration**: User drags slider to see mathematicians appear/disappear over time
3. **Discovery**: User clicks on scientist markers to see biographical details
4. **Deep Dive**: User explores specific mathematician's timeline events

### Visual Design
- **Globe**: Dark theme with subtle country boundaries
- **Scientists**: Colored dots sized by popularity, color-coded by nationality/region
- **Timeline**: Clean slider with decade markers and activity indicators
- **Details Panel**: Slide-out panel showing mathematician bio and timeline events

### Responsive Design
- Desktop-first with tablet/mobile considerations
- Globe interaction optimized for mouse/touch
- Timeline slider works on mobile devices

---

## Development Phases

### Phase 1: Data Pipeline MVP (Weeks 1-2)
**Goals**: 
- Extract and process data for 10-15 mathematicians
- Validate LLM extraction accuracy
- Generate clean JSON datasets

**Deliverables**:
- Python scripts for Wikipedia scraping
- LLM pipeline for event extraction
- Location geocoding system
- Sample dataset for 5 mathematicians

**Success Criteria**:
- 80%+ accuracy in event extraction
- All major life events captured (birth, education, career, death)
- Geocoding confidence >0.7 for major cities

### Phase 2: Basic Visualization (Weeks 3-4)
**Goals**:
- Implement globe + timeline interface
- Basic interactivity working
- Static decade visualization

**Deliverables**:
- React frontend with 3D globe
- Timeline slider component
- Scientist detail modal/panel
- Responsive design foundation

**Success Criteria**:
- Users can navigate timeline smoothly
- Clicking scientists shows biographical info
- Globe renders efficiently on target devices

### Phase 3: Polish and Scale (Weeks 5-6)
**Goals**:
- Full dataset integration
- Enhanced visual features
- Performance optimization

**Deliverables**:
- Complete 15-mathematician dataset
- Movement trails between locations
- Color coding and visual improvements
- Mobile optimization

**Success Criteria**:
- Smooth performance with full dataset
- Engaging visual storytelling
- Ready for user testing/feedback

---

## Technical Risks and Mitigations

### High Risk
- **LLM Accuracy**: Timeline extraction might miss events or hallucinate dates
  - *Mitigation*: Manual validation, confidence thresholds, iterative prompt improvement

### Medium Risk  
- **Geocoding Quality**: Historical place names might geocode incorrectly
  - *Mitigation*: Start with major cities, build manual override system

- **Performance**: Large dataset might slow globe rendering
  - *Mitigation*: Level-of-detail optimization, data chunking by time period

### Low Risk
- **Wikipedia API Rate Limits**: Scraping might be throttled
  - *Mitigation*: Use official dumps, respect rate limits, cache aggressively

---

## Future Enhancements (Post-MVP)

### Phase 4: Advanced Features
- Social network connections between mathematicians
- Mathematical concept tagging and evolution tracking
- Historical context overlay (wars, political events)
- Correspondence network visualization

### Phase 5: Expansion
- Extended time range (1650-1850)
- Additional scientific disciplines
- Multi-language Wikipedia support
- User-contributed content

### Phase 6: Platform
- REST API for external researchers
- Embedding widget for educational sites
- Data export capabilities
- Integration with academic databases

---

## Success Metrics

### MVP Success Criteria
- [ ] 15 mathematicians with complete biographical timelines
- [ ] 50+ location events with >80% geocoding accuracy  
- [ ] Smooth timeline navigation across 10 decades
- [ ] <2 second load time for initial globe render
- [ ] Positive feedback from 5+ beta users

### Long-term Goals
- 1000+ monthly active users exploring mathematical history
- Integration with 3+ educational institutions
- Coverage expansion to 50+ historical mathematicians
- Academic citations of the visualization tool

---

## Project Timeline

**Week 1**: Wikipedia scraping + LLM event extraction
**Week 2**: Geocoding + data validation pipeline  
**Week 3**: React frontend + basic globe rendering
**Week 4**: Timeline slider + scientist interactions
**Week 5**: Visual polish + performance optimization
**Week 6**: User testing + documentation

**Target Launch**: End of Week 6 with MVP feature set

---

## Questions for Iteration

1. Should we include mathematicians who lived partially outside 1700-1800 but were active during this period?
2. How granular should the timeline slider be? (decades vs. years)
3. What level of mathematical detail should we include in biographies?
4. Should we prioritize visual appeal or historical accuracy when conflicts arise?
5. How do we handle disputed historical information or dates?

---

*Last Updated: August 9, 2025*  
*Next Review: [To be scheduled]*
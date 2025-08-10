# 18th Century Mathematics Timeline Visualization
## Project Specification v2.0

### Project Overview
An interactive spatio-temporal visualization showing the lives, travels, and mathematical contributions of prominent 18th century mathematicians (1700-1800). Users can explore how mathematical ideas developed across Europe through an interactive timeline slider and modern map interface with historically-styled visual design showing both personal stories and political context.

### Core Concept
- **Timeline Slider**: Navigate through decades to see mathematical activity over time
- **Modern Map with Historical Styling**: Visualize mathematician events on contemporary geography with period-appropriate visual design
- **Dual Layer System**: Separate people and political context layers for rich storytelling
- **Event-Driven Narrative**: Each mathematician event shows biographical context and historical backdrop
- **Popularity Weighting**: Scientist prominence based on Wikipedia page views

---

## Technical Architecture

### Data Sources
- **Primary**: Wikipedia biographical pages and page view statistics
- **Structured Data**: Wikidata SPARQL queries for biographical basics (birth/death dates, places, institutions, coordinates)
- **Historical Context**: Political and cultural context data for historical accuracy and storytelling
- **Base Maps**: OpenStreetMap tiles with custom Rococo-themed styling for period atmosphere
- **Geocoding**: Pre-extracted coordinates from Wikidata with LLM fallback for missing locations

### Technology Stack
- **Backend**: Python for data extraction and processing
- **LLM**: LM Studio with Google Gemma-3n-e4b for timeline and location extraction
- **Frontend**: React + Leaflet.js for 2D map visualization with custom historical styling
- **Base Maps**: OpenStreetMap tiles with custom CSS styling for 18th century aesthetic
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
    "model_version": "gemma-3n-e4b"
  }
}
```

### Political Context Schema
```json
{
  "context_id": "russia_1727_catherine_death",
  "year": 1727,
  "location": {
    "place_name": "St. Petersburg",
    "lat": 59.9311,
    "lng": 30.3609,
    "region": "Russian Empire"
  },
  "headline": "Catherine I Dies, Peter II Ascends Throne",
  "description": "Political instability as 11-year-old Peter II becomes Tsar, leading Academy of Sciences to seek foreign scholars for stability",
  "impact_on_science": "Academy recruitment of European mathematicians increases",
  "category": "political_change", // political_change, war, peace_treaty, cultural_event, economic_shift
  "source": "Historical records",
  "relevance_score": 0.8 // How relevant to mathematical community
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
- [x] Interactive 2D map with custom Rococo styling over modern OpenStreetMap base
- [x] Dual layer system: People Layer (mathematician events) and Political Layer (historical context)
- [x] Click-to-explore individual mathematician details with biographical panels
- [x] Visual encoding: marker size by Wikipedia popularity, color by event type
- [x] Event type categorization (birth, education, position, publication, death, travel)
- [x] Time-synchronized political context overlays on modern geography

### Data Pipeline
1. **Wikidata Extraction**: Query SPARQL endpoint for structured biographical data (dates, places, institutions, coordinates)
2. **Wikipedia Enhancement**: Scrape biographical pages for narrative details and additional timeline events  
3. **LLM Processing**: Extract supplementary events and context using LM Studio + Google Gemma-3n-e4b
4. **Historical Context**: Gather political events and context for each time period
5. **Data Validation**: Manual review of extracted events and coordinate accuracy
6. **Export**: Generate JSON files for frontend consumption

---

## User Experience

### Primary User Flow
1. **Landing**: User sees styled map of Europe (modern geography with Rococo theming) with timeline slider and layer controls
2. **Exploration**: User drags timeline slider to see mathematicians appear/disappear over time with political context changing
3. **Layer Interaction**: User toggles between People Layer (mathematician events) and Political Layer (historical context)
4. **Discovery**: User clicks on mathematician markers to see event details and biographical information
5. **Deep Dive**: User explores specific mathematician's complete timeline and historical context

### Visual Design - Rococo Theme
- **Color Palette**: Sage green, powder blue, dusty rose, royal gold on cream background
- **Map Style**: Period-appropriate styling with muted, pastel tones
- **Typography**: Elegant serif fonts reminiscent of 18th century publications
- **Markers**: Ornate styling with gold borders and soft shadows

### Layer System Design

**People Layer (Primary Focus):**
- **Event Markers**: Circular markers with event type indicators (color-coded)
- **Size Encoding**: Marker size reflects mathematician's Wikipedia popularity
- **Profile Integration** (Lower Priority): Portrait thumbnails in markers when available
- **Interaction**: Click for biographical panel with timeline events

**Political Layer (Context):**
- **Regional Markers**: Smaller markers for major political events affecting mathematical centers
- **Contextual Overlays**: Text overlays or boundary highlights showing relevant political entities (Holy Roman Empire, French Kingdom, etc.)
- **Context Tooltips**: Brief descriptions of political/cultural events
- **Visual Hierarchy**: Muted styling to support, not compete with, people layer

### Responsive Design
- Desktop-first with tablet considerations
- Map interaction optimized for mouse with mobile touch support
- Timeline slider works effectively on all devices
- Layer controls accessible and clear

---

## Development Phases

### Phase 1: Data Pipeline MVP (Weeks 1-2)
**Goals**: 
- Extract structured data from Wikidata and enhance with Wikipedia narratives
- Validate LM Studio + Google Gemma-3n-e4b extraction accuracy for supplementary events
- Generate clean JSON datasets with pre-validated coordinates
- Gather political context data for key decades

**Deliverables**:
- Wikidata SPARQL queries for mathematician biographical data
- Python scripts for Wikipedia narrative enhancement
- LM Studio pipeline for additional event extraction using Google Gemma-3n-e4b
- Political context data collection
- Integrated dataset combining structured and narrative data for 5 mathematicians

**Success Criteria**:
- 90%+ accuracy in core biographical data from Wikidata
- 75%+ accuracy in supplementary event extraction from Wikipedia narratives
- Pre-validated coordinates for major European cities and institutions
- Political context data for each decade (1700s-1790s)
- Reduced LLM processing load by 60-70% through structured data pre-extraction

### Phase 2: Historical Map Visualization (Weeks 3-4)
**Goals**:
- Implement Leaflet + OpenStreetMap integration with custom Rococo styling
- Build dual-layer system (people + political context)
- Basic timeline synchronization working
- Custom CSS styling for period-appropriate map appearance

**Deliverables**:
- React frontend with Leaflet.js integration
- OpenStreetMap base tiles with custom Rococo CSS styling
- Dual layer system (toggleable people/political layers)
- Timeline slider component with context synchronization
- Mathematician event markers and political context overlays
- Basic biographical detail panels

**Success Criteria**:
- Users can navigate timeline smoothly with political context updating
- Both layers display correctly and can be toggled
- Clicking mathematician events shows biographical info
- Map styling evokes 18th century aesthetic on modern geography
- Rococo visual theme implemented throughout interface

### Phase 3: Polish and Scale (Weeks 5-6)
**Goals**:
- Full dataset integration (15 mathematicians)
- Enhanced visual features and interactions
- Performance optimization
- Political context refinement

**Deliverables**:
- Complete 15-mathematician dataset with political context
- Enhanced marker interactions and visual hierarchy
- Refined Rococo color scheme and styling
- Improved biographical panels with timeline events
- Performance optimizations for smooth interaction
- Documentation and deployment preparation

**Success Criteria**:
- Smooth performance with full dataset
- Engaging historical narrative through dual layers
- Clear visual distinction between people and political events
- Ready for user testing/feedback
- All 15 mathematicians with rich biographical and political context

---

## Technical Risks and Mitigations

### High Risk
- **LM Studio + Gemma Integration**: Google Gemma-3n-e4b may have different performance characteristics than Qwen
  - *Mitigation*: Test extraction quality early, adjust prompts for Gemma's instruction-following style, have Ollama fallback ready

- **OpenStreetMap Styling Limitations**: CSS styling may not achieve full historical aesthetic desired
  - *Mitigation*: Focus on color palette and marker design, consider custom map tiles if needed

### Medium Risk  
- **Historical Geocoding Quality**: 18th century place names might not map correctly to modern coordinates
  - *Mitigation*: Build manual override system, focus on major European cities first

- **Performance with Dual Layers**: Multiple marker layers might slow map rendering
  - *Mitigation*: Implement layer-specific optimizations, consider marker clustering for dense areas

- **Political Context Data Quality**: Historical context may be incomplete or inaccurate
  - *Mitigation*: Start with major events only, build manual curation process

### Low Risk
- **Leaflet Integration Complexity**: Well-documented library with extensive examples
  - *Mitigation*: Use established patterns, leverage community resources

- **Timeline Synchronization**: Straightforward year-based filtering
  - *Mitigation*: Implement simple year matching with fallback logic

---

## Future Enhancements (Post-MVP)

### Phase 4: Advanced Historical Features
- **Portrait Integration**: Mathematician portrait photos in markers (when available)
- **Enhanced Political Context**: Wars, treaties, cultural movements affecting mathematical development
- **Historical Map Overlays**: Trade routes, university networks, postal systems
- **Movement Visualization**: Animated paths showing mathematician travels between cities

### Phase 5: Social and Intellectual Networks
- **Correspondence Networks**: Letters and intellectual connections between mathematicians
- **Mathematical Concept Evolution**: Track how specific ideas developed and spread
- **Institutional Connections**: Universities, academies, royal courts as network nodes
- **Publication Timeline**: Major mathematical works and their geographic origins

### Phase 6: Platform and Accessibility
- **3D Globe Option**: Alternative 3D view using Three.js for different user preferences
- **Multiple Time Periods**: Extend to 17th century (Newton era) and early 19th century
- **REST API**: Data access for external researchers and educational institutions
- **Embedding Widget**: Standalone component for educational websites
- **Multi-language Support**: French, German, Latin interfaces for broader accessibility

---

## Success Metrics

### MVP Success Criteria
- [ ] 15 mathematicians with complete biographical timelines
- [ ] 50+ mathematician events with >85% geocoding accuracy  
- [ ] Dual-layer system (people + political) working smoothly
- [ ] Timeline synchronization with OpenHistoricalMap boundaries
- [ ] <3 second load time for map initialization
- [ ] Positive feedback from 5+ beta users (historians, educators, mathematicians)
- [ ] Historical accuracy validated by domain experts

### Long-term Goals
- 1000+ monthly active users exploring mathematical history
- Integration with 3+ educational institutions for classroom use
- Academic citations of the visualization in history of mathematics research
- Coverage expansion to 50+ historical mathematicians across multiple centuries
- Recognition as a premier tool for digital humanities and mathematical history

---

## Project Timeline

**Week 1**: Wikidata SPARQL queries + Wikipedia narrative extraction + LM Studio/Gemma setup + political context research
**Week 2**: Structured data integration + supplementary event extraction + historical data validation  
**Week 3**: React frontend + Leaflet + OpenStreetMap integration + custom Rococo styling
**Week 4**: Dual layer system + timeline synchronization + biographical panels
**Week 5**: Rococo visual design + performance optimization + political context integration
**Week 6**: User testing + documentation + deployment preparation

**Target Launch**: End of Week 6 with full MVP feature set

---

## Questions for Iteration

1. Should profile pictures be attempted in Phase 1 or kept as Phase 4 enhancement?
2. How detailed should political context be? (Major events only vs. comprehensive coverage)
3. How do we best convey historical political context without actual historical map boundaries?
4. Should we prioritize mobile experience or focus on desktop for initial launch?
5. How do we handle disputed historical dates or conflicting biographical information?
6. What's the best approach for gathering and validating political context data?

---

*Last Updated: August 10, 2025*  
*Next Review: [To be scheduled]*
# SciMap: 18th Century Mathematics Timeline

Interactive visualization mapping the lives and works of 18th century mathematicians from a global historical perspective.

![SciMap Screenshot](https://img.shields.io/badge/Status-Active%20Development-brightgreen) ![React](https://img.shields.io/badge/React-19.1.1-blue) ![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue) ![Python](https://img.shields.io/badge/Python-3.9+-green)

## 🎯 Project Overview

SciMap is an interactive historical timeline that visualizes the mathematical landscape of the 18th century (1700-1800). It combines:

- **Interactive 2D Map**: Leaflet-based geographic visualization of mathematician locations
- **Timeline Interface**: Explore mathematical developments year by year
- **Rich Data**: 97 mathematicians with biographical events, locations, and political context
- **Historical Context**: Political events and mathematical developments side by side

**Live Demo**: [GitHub Pages Deployment](https://chihchengliang.github.io/scimap)

## ✨ Features

### 🗺️ Interactive Map
- **Geographic Visualization**: See where mathematicians lived and worked
- **Clustered Markers**: Automatically groups nearby mathematicians
- **Location Details**: 143 geocoded historical locations with context

### ⏰ Timeline Navigation
- **Year-by-Year Exploration**: Navigate through 1700-1800
- **Collapsible Panels**: Organized display of active mathematicians and political events
- **Event Filtering**: Focus on mathematical discoveries or political context

### 👥 Mathematician Profiles
- **Rich Biographies**: Wikipedia-sourced biographical information
- **Timeline Events**: Key life events and mathematical contributions
- **Popularity Tiers**: Visual hierarchy based on historical significance
- **Detailed Panels**: In-depth information on click

### 🏛️ Historical Context
- **Political Events**: Major political developments of the era
- **Geographic Context**: Historical location information
- **Cross-References**: Connections between mathematicians and events

## 🚀 Development

For detailed setup instructions, project structure, and development guidelines, see [CLAUDE.md](CLAUDE.md).

## 🔧 Technology Stack

### Frontend
- **React 19.1.1**: Modern UI framework
- **TypeScript**: Type-safe development
- **Leaflet**: Interactive maps
- **Material-UI**: Component library
- **React Leaflet**: React integration for Leaflet

### Data Pipeline
- **Python 3.9+**: Data processing
- **Requests**: HTTP client for scraping
- **BeautifulSoup**: HTML parsing
- **Wikipedia API**: Biographical data
- **Wikidata SPARQL**: Structured data queries
- **Nominatim**: Geocoding service

### Deployment
- **GitHub Pages**: Static site hosting
- **GitHub Actions**: Automated deployment

## 📊 Data Sources

### Mathematician Data (97 profiles)
- **Wikipedia**: Biographical information and life events
- **Wikidata**: Structured birth/death places and dates (mathematicians born 1650-1750)
- **PageView API**: Popularity metrics for visual hierarchy

### Location Data (143 locations)
- **Wikidata**: High-quality place references
- **Nominatim**: Geocoding coordinates
- **Historical Context**: 18th century global geography

### Political Context
- **Curated Events**: Major political developments 1700-1800
- **Geographic Context**: Location-aware historical events

## 🏗️ Data Pipeline

The pipeline processes raw historical data into visualization-ready format:

1. **Wikidata Extraction**: Query 510 mathematicians (born 1650-1750, active 1700-1800)
2. **Wikipedia Scraping**: Fetch biographical content
3. **Event Extraction**: Parse life events and contributions using Gemma 3n e4b via LM Studio (local processing, may not be reproducible and subject to hallucinations)
4. **PageView Collection**: Gather popularity metrics
5. **Location Geocoding**: Convert place names to coordinates
6. **Political Data**: Process historical context
7. **Frontend Export**: Generate final JSON files

## 🎨 Design Philosophy

### Global Perspective
- **Historical Accuracy**: Authentic representation of 18th century mathematics
- **Cultural Inclusivity**: Presenting mathematical development from worldwide perspectives
- **Accessibility**: Modern UX with historical context

### Data Approach
- **Source Transparency**: Clear attribution to Wikipedia/Wikidata
- **Quality over Quantity**: Curated dataset with rich metadata
- **Extensibility**: Pipeline designed for dataset expansion

## 🤝 Contributing

Contributions are welcome! Please see [CLAUDE.md](CLAUDE.md) for development setup and guidelines.

### Data Contributions
- Location corrections and additions
- Mathematician profiles from underrepresented regions
- Historical event curation for global context

## 📈 Recent Updates

### Latest Features
- ✅ **GitHub Pages Deployment**: Automated CI/CD pipeline
- ✅ **Location Enrichment**: Added 50+ high-quality locations from Wikidata
- ✅ **Data Cleanup**: Removed inaccurate nationality defaults
- ✅ **Collapsible Timeline**: Improved UI organization
- ✅ **Popularity Rebalancing**: Better visual hierarchy

### Dataset Status
- **97 Mathematicians**: Fully processed with rich metadata
- **143 Locations**: Geocoded with historical context
- **1700-1800 Timespan**: Complete 18th century coverage
- **Pipeline Ready**: 510 mathematician config for expansion

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Wikipedia Contributors**: Biographical content and historical information
- **Wikidata Community**: Structured historical data
- **OpenStreetMap**: Geographic data via Nominatim
- **Create React App**: Initial project scaffolding
- **Leaflet**: Open-source mapping library

## 📞 Contact

For questions, suggestions, or collaboration opportunities, please open an issue or contact the maintainers.

---

*Exploring the mathematical landscape of the Age of Enlightenment, one mathematician at a time.*
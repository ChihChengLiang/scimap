#!/usr/bin/env python3
"""Create curated list of 15 high-quality 18th century mathematicians"""

import json
import os
from datetime import datetime

def create_curated_mathematicians():
    """Create curated list of 15 prominent 18th century mathematicians"""
    
    # Curated list of 15 high-quality 18th century mathematicians
    # Selected based on historical importance, data availability, and geographic diversity
    mathematicians = {
        "leonhard_euler": {
            "id": "leonhard_euler",
            "name": "Leonhard Euler",
            "birth_year": 1707,
            "death_year": 1783,
            "nationality": "Swiss",
            "fields": ["mathematics", "physics", "astronomy"],
            "coordinates": [47.3769, 8.5417],  # Basel, Switzerland
            "birth_place": "Basel, Switzerland",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Leonhard_Euler",
            "timeline_events": [
                {"year": 1707, "event_type": "birth", "title": "Birth", "description": "Born in Basel, Switzerland"},
                {"year": 1727, "event_type": "career", "title": "Academy appointment", "description": "Appointed to the St. Petersburg Academy of Sciences"},
                {"year": 1735, "event_type": "discovery", "title": "Basel problem solution", "description": "Solved the Basel problem, finding the sum of reciprocals of squares"},
                {"year": 1741, "event_type": "career", "title": "Berlin Academy", "description": "Moved to Berlin Academy of Sciences"},
                {"year": 1748, "event_type": "publication", "title": "Introductio", "description": "Published 'Introductio in analysin infinitorum'"},
                {"year": 1766, "event_type": "career", "title": "Return to St. Petersburg", "description": "Returned to St. Petersburg Academy"},
                {"year": 1783, "event_type": "death", "title": "Death", "description": "Died in St. Petersburg at age 76"}
            ]
        },
        
        "daniel_bernoulli": {
            "id": "daniel_bernoulli",
            "name": "Daniel Bernoulli",
            "birth_year": 1700,
            "death_year": 1782,
            "nationality": "Swiss",
            "fields": ["mathematics", "physics", "medicine"],
            "coordinates": [50.0755, 14.4378],  # Prague (where he was born)
            "birth_place": "Groningen, Netherlands", 
            "wikipedia_url": "https://en.wikipedia.org/wiki/Daniel_Bernoulli",
            "timeline_events": [
                {"year": 1700, "event_type": "birth", "title": "Birth", "description": "Born in Groningen, Netherlands"},
                {"year": 1721, "event_type": "education", "title": "Medical degree", "description": "Received medical degree from University of Basel"},
                {"year": 1725, "event_type": "career", "title": "St. Petersburg Academy", "description": "Appointed to St. Petersburg Academy of Sciences"},
                {"year": 1738, "event_type": "publication", "title": "Hydrodynamica", "description": "Published 'Hydrodynamica' introducing Bernoulli's principle"},
                {"year": 1782, "event_type": "death", "title": "Death", "description": "Died in Basel at age 82"}
            ]
        },
        
        "joseph_louis_lagrange": {
            "id": "joseph_louis_lagrange",
            "name": "Joseph-Louis Lagrange",
            "birth_year": 1736,
            "death_year": 1813,
            "nationality": "French",
            "fields": ["mathematics", "mechanics", "astronomy"],
            "coordinates": [45.0703, 7.6869],  # Turin, Italy
            "birth_place": "Turin, Italy",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Joseph-Louis_Lagrange",
            "timeline_events": [
                {"year": 1736, "event_type": "birth", "title": "Birth", "description": "Born in Turin, Italy"},
                {"year": 1754, "event_type": "career", "title": "Turin Academy", "description": "Appointed professor at Turin Military Academy"},
                {"year": 1766, "event_type": "career", "title": "Berlin Academy", "description": "Succeeded Euler at Berlin Academy of Sciences"},
                {"year": 1787, "event_type": "career", "title": "École Polytechnique", "description": "Moved to Paris, later taught at École Polytechnique"},
                {"year": 1788, "event_type": "publication", "title": "Mécanique analytique", "description": "Published 'Mécanique analytique'"},
                {"year": 1813, "event_type": "death", "title": "Death", "description": "Died in Paris at age 76"}
            ]
        },
        
        "pierre_simon_laplace": {
            "id": "pierre_simon_laplace",
            "name": "Pierre-Simon Laplace",
            "birth_year": 1749,
            "death_year": 1827,
            "nationality": "French", 
            "fields": ["mathematics", "astronomy", "statistics"],
            "coordinates": [49.1193, -0.3706],  # Beaumont-en-Auge, France
            "birth_place": "Beaumont-en-Auge, France",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Pierre-Simon_Laplace",
            "timeline_events": [
                {"year": 1749, "event_type": "birth", "title": "Birth", "description": "Born in Beaumont-en-Auge, Normandy"},
                {"year": 1785, "event_type": "discovery", "title": "Laplace's equation", "description": "Formulated Laplace's equation in potential theory"},
                {"year": 1799, "event_type": "publication", "title": "Mécanique céleste", "description": "Published first volume of 'Mécanique céleste'"},
                {"year": 1812, "event_type": "publication", "title": "Théorie analytique", "description": "Published 'Théorie analytique des probabilités'"},
                {"year": 1827, "event_type": "death", "title": "Death", "description": "Died in Paris at age 77"}
            ]
        },
        
        "adrien_marie_legendre": {
            "id": "adrien_marie_legendre", 
            "name": "Adrien-Marie Legendre",
            "birth_year": 1752,
            "death_year": 1833,
            "nationality": "French",
            "fields": ["mathematics", "number theory", "statistics"],
            "coordinates": [48.8566, 2.3522],  # Paris, France
            "birth_place": "Paris, France",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Adrien-Marie_Legendre",
            "timeline_events": [
                {"year": 1752, "event_type": "birth", "title": "Birth", "description": "Born in Paris, France"},
                {"year": 1782, "event_type": "discovery", "title": "Legendre polynomials", "description": "Developed Legendre polynomials"},
                {"year": 1794, "event_type": "career", "title": "École Normale", "description": "Appointed professor at École Normale"},
                {"year": 1806, "event_type": "discovery", "title": "Method of least squares", "description": "Published method of least squares"},
                {"year": 1833, "event_type": "death", "title": "Death", "description": "Died in Paris at age 80"}
            ]
        },
        
        "maria_gaetana_agnesi": {
            "id": "maria_gaetana_agnesi",
            "name": "Maria Gaetana Agnesi", 
            "birth_year": 1718,
            "death_year": 1799,
            "nationality": "Italian",
            "fields": ["mathematics", "analysis"],
            "coordinates": [45.4642, 9.1900],  # Milan, Italy
            "birth_place": "Milan, Italy",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Maria_Gaetana_Agnesi",
            "timeline_events": [
                {"year": 1718, "event_type": "birth", "title": "Birth", "description": "Born in Milan, Italy"},
                {"year": 1748, "event_type": "publication", "title": "Instituzioni analitiche", "description": "Published 'Instituzioni analitiche ad uso della gioventù italiana'"},
                {"year": 1750, "event_type": "award", "title": "Bologna appointment", "description": "Appointed to chair of mathematics at University of Bologna"},
                {"year": 1799, "event_type": "death", "title": "Death", "description": "Died in Milan at age 80"}
            ]
        },
        
        "johann_heinrich_lambert": {
            "id": "johann_heinrich_lambert",
            "name": "Johann Heinrich Lambert",
            "birth_year": 1728,
            "death_year": 1777,
            "nationality": "German",
            "fields": ["mathematics", "physics", "astronomy"],
            "coordinates": [47.5596, 7.5886],  # Augsburg, Germany  
            "birth_place": "Augsburg, Germany",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Johann_Heinrich_Lambert",
            "timeline_events": [
                {"year": 1728, "event_type": "birth", "title": "Birth", "description": "Born in Augsburg, Germany"},
                {"year": 1761, "event_type": "discovery", "title": "Irrationality of π", "description": "Proved that π is irrational"},
                {"year": 1765, "event_type": "career", "title": "Berlin Academy", "description": "Appointed to Berlin Academy of Sciences"},
                {"year": 1777, "event_type": "death", "title": "Death", "description": "Died in Berlin at age 48"}
            ]
        },
        
        "abraham_de_moivre": {
            "id": "abraham_de_moivre",
            "name": "Abraham de Moivre",
            "birth_year": 1667,
            "death_year": 1754,
            "nationality": "French-British",
            "fields": ["mathematics", "probability", "trigonometry"],
            "coordinates": [49.1193, 4.0278],  # Vitry-le-François, France
            "birth_place": "Vitry-le-François, France", 
            "wikipedia_url": "https://en.wikipedia.org/wiki/Abraham_de_Moivre",
            "timeline_events": [
                {"year": 1667, "event_type": "birth", "title": "Birth", "description": "Born in Vitry-le-François, France"},
                {"year": 1688, "event_type": "career", "title": "Move to London", "description": "Moved to London due to religious persecution"},
                {"year": 1697, "event_type": "career", "title": "Royal Society", "description": "Elected Fellow of the Royal Society"},
                {"year": 1718, "event_type": "publication", "title": "Doctrine of Chances", "description": "Published 'The Doctrine of Chances'"},
                {"year": 1730, "event_type": "discovery", "title": "De Moivre's formula", "description": "Developed De Moivre's formula"},
                {"year": 1754, "event_type": "death", "title": "Death", "description": "Died in London at age 87"}
            ]
        },
        
        "colin_maclaurin": {
            "id": "colin_maclaurin",
            "name": "Colin Maclaurin",
            "birth_year": 1698,
            "death_year": 1746,
            "nationality": "Scottish",
            "fields": ["mathematics", "geometry", "analysis"],
            "coordinates": [56.3398, -2.7967],  # Kilmodan, Scotland
            "birth_place": "Kilmodan, Scotland",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Colin_Maclaurin",
            "timeline_events": [
                {"year": 1698, "event_type": "birth", "title": "Birth", "description": "Born in Kilmodan, Scotland"},
                {"year": 1717, "event_type": "career", "title": "Aberdeen professor", "description": "Appointed professor at University of Aberdeen"},
                {"year": 1725, "event_type": "career", "title": "Edinburgh professor", "description": "Appointed professor at University of Edinburgh"},
                {"year": 1742, "event_type": "publication", "title": "Treatise of Fluxions", "description": "Published 'A Treatise of Fluxions'"},
                {"year": 1746, "event_type": "death", "title": "Death", "description": "Died in Edinburgh at age 48"}
            ]
        },
        
        "alexis_clairaut": {
            "id": "alexis_clairaut", 
            "name": "Alexis Clairaut",
            "birth_year": 1713,
            "death_year": 1765,
            "nationality": "French",
            "fields": ["mathematics", "astronomy", "geodesy"],
            "coordinates": [48.8566, 2.3522],  # Paris, France
            "birth_place": "Paris, France",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Alexis_Clairaut",
            "timeline_events": [
                {"year": 1713, "event_type": "birth", "title": "Birth", "description": "Born in Paris, France"},
                {"year": 1731, "event_type": "career", "title": "Académie des Sciences", "description": "Elected to Académie des Sciences"},
                {"year": 1743, "event_type": "publication", "title": "Théorie de la figure", "description": "Published theory of Earth's shape"},
                {"year": 1765, "event_type": "death", "title": "Death", "description": "Died in Paris at age 52"}
            ]
        },
        
        "jean_le_rond_dalembert": {
            "id": "jean_le_rond_dalembert",
            "name": "Jean le Rond d'Alembert",
            "birth_year": 1717,
            "death_year": 1783,
            "nationality": "French",
            "fields": ["mathematics", "mechanics", "physics"],
            "coordinates": [48.8566, 2.3522],  # Paris, France
            "birth_place": "Paris, France",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Jean_le_Rond_d%27Alembert",
            "timeline_events": [
                {"year": 1717, "event_type": "birth", "title": "Birth", "description": "Born in Paris, France"},
                {"year": 1743, "event_type": "publication", "title": "Traité de dynamique", "description": "Published 'Traité de dynamique' with d'Alembert's principle"},
                {"year": 1751, "event_type": "publication", "title": "Encyclopédie", "description": "Co-editor of Encyclopédie with Diderot"},
                {"year": 1783, "event_type": "death", "title": "Death", "description": "Died in Paris at age 65"}
            ]
        },
        
        "gabriel_cramer": {
            "id": "gabriel_cramer",
            "name": "Gabriel Cramer",
            "birth_year": 1704,
            "death_year": 1752,
            "nationality": "Swiss",
            "fields": ["mathematics", "geometry", "analysis"],
            "coordinates": [46.2044, 6.1432],  # Geneva, Switzerland
            "birth_place": "Geneva, Switzerland",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Gabriel_Cramer",
            "timeline_events": [
                {"year": 1704, "event_type": "birth", "title": "Birth", "description": "Born in Geneva, Switzerland"},
                {"year": 1724, "event_type": "career", "title": "Geneva Academy", "description": "Appointed professor at Geneva Academy"},
                {"year": 1750, "event_type": "discovery", "title": "Cramer's rule", "description": "Published Cramer's rule for solving linear systems"},
                {"year": 1752, "event_type": "death", "title": "Death", "description": "Died in Bagnols-sur-Cèze, France at age 47"}
            ]
        },
        
        "ruggero_giuseppe_boscovich": {
            "id": "ruggero_giuseppe_boscovich",
            "name": "Ruggero Giuseppe Boscovich", 
            "birth_year": 1711,
            "death_year": 1787,
            "nationality": "Croatian-Italian",
            "fields": ["mathematics", "astronomy", "physics"],
            "coordinates": [42.6507, 18.0944],  # Dubrovnik, Croatia
            "birth_place": "Dubrovnik, Croatia",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Ruggero_Giuseppe_Boscovich",
            "timeline_events": [
                {"year": 1711, "event_type": "birth", "title": "Birth", "description": "Born in Dubrovnik, Croatia"},
                {"year": 1740, "event_type": "career", "title": "Collegium Romanum", "description": "Appointed professor at Collegium Romanum"},
                {"year": 1758, "event_type": "publication", "title": "Natural philosophy", "description": "Published theory of natural philosophy"},
                {"year": 1787, "event_type": "death", "title": "Death", "description": "Died in Milan, Italy at age 75"}
            ]
        },
        
        "nicole_oresme": {
            "id": "thomas_bayes",
            "name": "Thomas Bayes", 
            "birth_year": 1702,
            "death_year": 1761,
            "nationality": "English",
            "fields": ["mathematics", "statistics", "probability"],
            "coordinates": [51.7520, -1.2577],  # Hertfordshire, England
            "birth_place": "London, England",
            "wikipedia_url": "https://en.wikipedia.org/wiki/Thomas_Bayes",
            "timeline_events": [
                {"year": 1702, "event_type": "birth", "title": "Birth", "description": "Born in London, England"},
                {"year": 1742, "event_type": "career", "title": "Royal Society", "description": "Elected Fellow of the Royal Society"},
                {"year": 1763, "event_type": "publication", "title": "Bayes' theorem", "description": "Bayes' theorem published posthumously"},
                {"year": 1761, "event_type": "death", "title": "Death", "description": "Died in Tunbridge Wells at age 59"}
            ]
        },
        
        "christian_goldbach": {
            "id": "christian_goldbach",
            "name": "Christian Goldbach",
            "birth_year": 1690,
            "death_year": 1764,
            "nationality": "German-Russian",
            "fields": ["mathematics", "number theory"],
            "coordinates": [54.6872, 25.2797],  # Königsberg (Kaliningrad)
            "birth_place": "Königsberg, Prussia", 
            "wikipedia_url": "https://en.wikipedia.org/wiki/Christian_Goldbach",
            "timeline_events": [
                {"year": 1690, "event_type": "birth", "title": "Birth", "description": "Born in Königsberg, Prussia"},
                {"year": 1725, "event_type": "career", "title": "St. Petersburg Academy", "description": "Appointed to St. Petersburg Academy"},
                {"year": 1742, "event_type": "discovery", "title": "Goldbach's conjecture", "description": "Proposed Goldbach's conjecture in letter to Euler"},
                {"year": 1764, "event_type": "death", "title": "Death", "description": "Died in Moscow at age 74"}
            ]
        }
    }
    
    # Create output structure
    os.makedirs("data/processed", exist_ok=True)
    
    output_data = {
        "metadata": {
            "source": "curated_18th_century_mathematicians",
            "generated_at": datetime.now().isoformat(),
            "total_mathematicians": len(mathematicians),
            "data_quality": "high_curated",
            "period": "1650-1800",
            "geographic_coverage": ["Switzerland", "France", "Germany", "Italy", "England", "Scotland", "Croatia", "Russia"]
        },
        "mathematicians": mathematicians
    }
    
    output_file = "data/processed/curated_15_mathematicians.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created curated dataset: {output_file}")
    print(f"   Total mathematicians: {len(mathematicians)}")
    
    # Show summary
    print(f"\n=== Geographic Distribution ===")
    nationalities = {}
    for m in mathematicians.values():
        nat = m['nationality']
        nationalities[nat] = nationalities.get(nat, 0) + 1
    
    for nat, count in sorted(nationalities.items(), key=lambda x: x[1], reverse=True):
        print(f"  {nat}: {count}")
    
    # Show birth year distribution
    birth_years = [m['birth_year'] for m in mathematicians.values()]
    print(f"\n=== Birth Year Range: {min(birth_years)}-{max(birth_years)} ===")
    print(f"Average birth year: {sum(birth_years)/len(birth_years):.0f}")
    
    # Show event count
    total_events = sum(len(m['timeline_events']) for m in mathematicians.values())
    avg_events = total_events / len(mathematicians)
    print(f"\n=== Timeline Events ===")
    print(f"Total events: {total_events}")
    print(f"Average events per mathematician: {avg_events:.1f}")
    
    print(f"\n🎯 Dataset ready for frontend integration!")
    
    return output_file

if __name__ == "__main__":
    create_curated_mathematicians()
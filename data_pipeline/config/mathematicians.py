"""Configuration for target mathematicians based on SPEC.md"""

TIER_1_MATHEMATICIANS = {
    "leonhard_euler": {
        "name": "Leonhard Euler",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Leonhard_Euler",
        "birth_year": 1707,
        "death_year": 1783,
        "nationality": "Swiss",
        "fields": ["mathematics", "physics", "astronomy"]
    },
    "joseph_louis_lagrange": {
        "name": "Joseph-Louis Lagrange", 
        "wikipedia_url": "https://en.wikipedia.org/wiki/Joseph-Louis_Lagrange",
        "birth_year": 1736,
        "death_year": 1813,
        "nationality": "Italian-French",
        "fields": ["mathematics", "mechanics", "astronomy"]
    },
    "pierre_simon_laplace": {
        "name": "Pierre-Simon Laplace",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Pierre-Simon_Laplace", 
        "birth_year": 1749,
        "death_year": 1827,
        "nationality": "French",
        "fields": ["mathematics", "astronomy", "physics"]
    },
    "daniel_bernoulli": {
        "name": "Daniel Bernoulli",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Daniel_Bernoulli",
        "birth_year": 1700,
        "death_year": 1782,
        "nationality": "Swiss",
        "fields": ["mathematics", "physics", "medicine"]
    }
}

TIER_2_MATHEMATICIANS = {
    "jean_le_rond_dalembert": {
        "name": "Jean le Rond d'Alembert",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Jean_le_Rond_d%27Alembert",
        "birth_year": 1717,
        "death_year": 1783,
        "nationality": "French", 
        "fields": ["mathematics", "physics", "philosophy"]
    },
    "alexis_clairaut": {
        "name": "Alexis Clairaut",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Alexis_Clairaut",
        "birth_year": 1713,
        "death_year": 1765,
        "nationality": "French",
        "fields": ["mathematics", "astronomy", "physics"]
    },
    "gabriel_cramer": {
        "name": "Gabriel Cramer",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Gabriel_Cramer",
        "birth_year": 1704,
        "death_year": 1752,
        "nationality": "Swiss",
        "fields": ["mathematics"]
    },
    "colin_maclaurin": {
        "name": "Colin Maclaurin", 
        "wikipedia_url": "https://en.wikipedia.org/wiki/Colin_Maclaurin",
        "birth_year": 1698,
        "death_year": 1746,
        "nationality": "Scottish",
        "fields": ["mathematics"]
    },
    "maria_gaetana_agnesi": {
        "name": "Maria Gaetana Agnesi",
        "wikipedia_url": "https://en.wikipedia.org/wiki/Maria_Gaetana_Agnesi",
        "birth_year": 1718,
        "death_year": 1799,
        "nationality": "Italian",
        "fields": ["mathematics", "philosophy", "theology"]
    },
    "emilie_du_chatelet": {
        "name": "Émilie du Châtelet",
        "wikipedia_url": "https://en.wikipedia.org/wiki/%C3%89milie_du_Ch%C3%A2telet",
        "birth_year": 1706,
        "death_year": 1749,
        "nationality": "French",
        "fields": ["mathematics", "physics", "philosophy"]
    }
}

ALL_MATHEMATICIANS = {**TIER_1_MATHEMATICIANS, **TIER_2_MATHEMATICIANS}

# Only unprocessed mathematicians (for incremental run)
REMAINING_MATHEMATICIANS = {
    "jean_le_rond_dalembert": TIER_2_MATHEMATICIANS["jean_le_rond_dalembert"],
    "alexis_clairaut": TIER_2_MATHEMATICIANS["alexis_clairaut"], 
    "gabriel_cramer": TIER_2_MATHEMATICIANS["gabriel_cramer"],
    "colin_maclaurin": TIER_2_MATHEMATICIANS["colin_maclaurin"],
    "maria_gaetana_agnesi": TIER_2_MATHEMATICIANS["maria_gaetana_agnesi"],
    "emilie_du_chatelet": TIER_2_MATHEMATICIANS["emilie_du_chatelet"]
}
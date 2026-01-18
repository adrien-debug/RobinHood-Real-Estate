"""
Données de référence réalistes pour le marché immobilier de Dubaï
Utilisées pour générer des données MOCK crédibles
"""

# Communautés principales avec leurs projets réels
DUBAI_PROJECTS = {
    "Dubai Marina": {
        "projects": [
            ("Marina Heights", ["Tower A", "Tower B", "Tower C"]),
            ("Damac Heights", ["Main Tower"]),
            ("Address Residences", ["North Tower", "South Tower"]),
            ("Marina Gate", ["Tower 1", "Tower 2", "Tower 3"]),
            ("Cayan Tower", ["Main Building"]),
            ("Princess Tower", ["Main Building"]),
            ("23 Marina", ["Main Tower"]),
            ("The Torch", ["Main Tower"]),
            ("Elite Residence", ["Main Building"]),
            ("Botanica Tower", ["Main Building"]),
        ],
        "avg_price_sqft": (1800, 2800),
        "property_types": ["apartment", "penthouse"],
    },
    "Downtown Dubai": {
        "projects": [
            ("Burj Vista", ["Tower 1", "Tower 2"]),
            ("The Address Boulevard", ["Main Tower"]),
            ("Opera Grand", ["Main Building"]),
            ("Burj Royale", ["Main Tower"]),
            ("Boulevard Heights", ["Tower 1", "Tower 2"]),
            ("Standpoint", ["Tower A", "Tower B"]),
            ("South Ridge", ["Tower 1", "Tower 2", "Tower 3", "Tower 4"]),
            ("Claren", ["Tower 1", "Tower 2"]),
            ("BLVD Crescent", ["North", "South"]),
            ("Act One | Act Two", ["Act One", "Act Two"]),
        ],
        "avg_price_sqft": (2200, 3500),
        "property_types": ["apartment", "penthouse"],
    },
    "Palm Jumeirah": {
        "projects": [
            ("One Palm", ["Main Tower"]),
            ("Royal Atlantis Residences", ["Main Building"]),
            ("Oceana", ["Baltic", "Adriatic", "Pacific", "Caribbean"]),
            ("Shoreline Apartments", ["Building 1", "Building 2", "Building 3"]),
            ("Tiara Residences", ["Aquamarine", "Amber", "Diamond"]),
            ("The 8", ["Main Tower"]),
            ("Serenia Residences", ["North", "South"]),
            ("Fairmont Palm", ["North Residence", "South Residence"]),
            ("FIVE Palm", ["Main Tower"]),
            ("Viceroy Palm", ["Main Building"]),
        ],
        "avg_price_sqft": (2500, 5000),
        "property_types": ["apartment", "villa", "penthouse"],
    },
    "Business Bay": {
        "projects": [
            ("Executive Towers", ["Tower A", "Tower B", "Tower C", "Tower H", "Tower J"]),
            ("Bay Square", ["Building 1", "Building 2", "Building 3"]),
            ("The Opus", ["Main Building"]),
            ("Damac Towers", ["Tower A", "Tower B"]),
            ("Marasi Business Bay", ["Marina View", "Canal View"]),
            ("Paramount Tower", ["Main Tower"]),
            ("Aykon City", ["Tower A", "Tower B"]),
            ("Noora Tower", ["Main Building"]),
            ("Churchill Towers", ["Tower 1", "Tower 2"]),
            ("Ubora Tower", ["Tower 1", "Tower 2"]),
        ],
        "avg_price_sqft": (1400, 2200),
        "property_types": ["apartment", "office"],
    },
    "JBR": {
        "projects": [
            ("Murjan", ["Tower 1", "Tower 2", "Tower 3", "Tower 4", "Tower 5", "Tower 6"]),
            ("Bahar", ["Tower 1", "Tower 2", "Tower 3", "Tower 4", "Tower 5", "Tower 6"]),
            ("Sadaf", ["Tower 1", "Tower 2", "Tower 3", "Tower 4", "Tower 5", "Tower 6", "Tower 7", "Tower 8"]),
            ("Shams", ["Tower 1", "Tower 2", "Tower 3", "Tower 4"]),
            ("Rimal", ["Tower 1", "Tower 2", "Tower 3", "Tower 4", "Tower 5", "Tower 6"]),
            ("Amwaj", ["Tower 1", "Tower 2", "Tower 3", "Tower 4", "Tower 5"]),
        ],
        "avg_price_sqft": (1600, 2400),
        "property_types": ["apartment"],
    },
    "Dubai Hills Estate": {
        "projects": [
            ("Park Heights", ["Tower 1", "Tower 2"]),
            ("Collective", ["Tower 1", "Tower 2"]),
            ("Acacia", ["Main Phase"]),
            ("Golf Place", ["Phase 1", "Phase 2"]),
            ("Park Point", ["Tower A", "Tower B"]),
            ("Sidra Villas", ["Sidra 1", "Sidra 2", "Sidra 3"]),
            ("Maple", ["Phase 1", "Phase 2", "Phase 3"]),
            ("Address Hillcrest", ["Main Tower"]),
            ("Ellington Views", ["Tower 1", "Tower 2"]),
        ],
        "avg_price_sqft": (1500, 2200),
        "property_types": ["apartment", "villa", "townhouse"],
    },
    "Jumeirah Village Circle": {
        "projects": [
            ("Bloom Towers", ["Tower A", "Tower B"]),
            ("Pantheon Boulevard", ["Tower 1", "Tower 2"]),
            ("Binghatti Stars", ["Main Building"]),
            ("Circle Mall Residences", ["Tower 1"]),
            ("Eaton Place", ["Main Building"]),
            ("Oxford Tower", ["Tower 1", "Tower 2"]),
            ("Sobha Hartland Greens", ["Building 1", "Building 2"]),
            ("Azizi Riviera", ["Building 1", "Building 2", "Building 3"]),
            ("Belgravia", ["Tower 1", "Tower 2", "Tower 3"]),
        ],
        "avg_price_sqft": (800, 1400),
        "property_types": ["apartment", "townhouse"],
    },
    "Dubai Creek Harbour": {
        "projects": [
            ("Harbour Views", ["Tower 1", "Tower 2"]),
            ("Creek Rise", ["Tower A", "Tower B"]),
            ("Creek Gate", ["Tower 1", "Tower 2"]),
            ("Creekside 18", ["Main Tower"]),
            ("The Cove", ["Building 1", "Building 2", "Building 3"]),
            ("Palace Residences", ["Tower 1", "Tower 2"]),
            ("Address Harbour Point", ["Main Tower"]),
            ("Vida Creek Harbour", ["Main Building"]),
        ],
        "avg_price_sqft": (1800, 2800),
        "property_types": ["apartment", "penthouse"],
    },
    "Arabian Ranches": {
        "projects": [
            ("Mirador", ["Phase 1", "Phase 2"]),
            ("Palmera", ["Building 1", "Building 2", "Building 3"]),
            ("Savannah", ["Phase 1"]),
            ("Saheel", ["Main Phase"]),
            ("Alma", ["Phase 1", "Phase 2"]),
            ("Camelia", ["Phase 1"]),
            ("Rasha", ["Phase 1"]),
            ("Azalea", ["Phase 1"]),
            ("Terra Nova", ["Phase 1"]),
            ("Alvorada", ["Phase 1", "Phase 2"]),
        ],
        "avg_price_sqft": (1000, 1500),
        "property_types": ["villa", "townhouse"],
    },
    "DIFC": {
        "projects": [
            ("Index Tower", ["Main Building"]),
            ("Park Towers", ["Tower A", "Tower B"]),
            ("Limestone House", ["Main Building"]),
            ("Central Park", ["Tower 1", "Tower 2"]),
            ("Burj Daman", ["Main Tower"]),
            ("Sky Gardens", ["Main Building"]),
            ("DIFC Living", ["Building A", "Building B"]),
        ],
        "avg_price_sqft": (2800, 4500),
        "property_types": ["apartment", "penthouse"],
    },
    "Jumeirah Beach Residence": {
        "projects": [
            ("Murjan", ["Tower 1", "Tower 2", "Tower 3"]),
            ("Bahar", ["Tower 1", "Tower 2"]),
            ("Sadaf", ["Tower 1", "Tower 2", "Tower 3"]),
            ("Shams", ["Tower 1", "Tower 2"]),
            ("Rimal", ["Tower 1", "Tower 2"]),
            ("Amwaj", ["Tower 1", "Tower 2"]),
        ],
        "avg_price_sqft": (1600, 2400),
        "property_types": ["apartment"],
    },
    "Meydan": {
        "projects": [
            ("District One Villas", ["Phase 1", "Phase 2"]),
            ("The Galleries", ["Building 1", "Building 2"]),
            ("Millennium Estates", ["Main Phase"]),
            ("Azizi Meydan", ["Tower 1", "Tower 2"]),
            ("Sobha One", ["Main Tower"]),
        ],
        "avg_price_sqft": (1200, 1800),
        "property_types": ["apartment", "villa", "townhouse"],
    },
}

# Liste des communautés (ordre par popularité)
COMMUNITIES = list(DUBAI_PROJECTS.keys())

# Types de chambres
ROOM_TYPES = [
    (0, "studio"),
    (1, "1BR"),
    (2, "2BR"),
    (3, "3BR+"),
    (4, "3BR+"),
    (5, "3BR+"),
]

# Types de transactions
TRANSACTION_TYPES = ["sale", "resale", "offplan"]


def get_random_project(community: str = None):
    """Retourne un projet aléatoire avec son building"""
    import random
    
    if community and community in DUBAI_PROJECTS:
        projects = DUBAI_PROJECTS[community]["projects"]
    else:
        community = random.choice(COMMUNITIES)
        projects = DUBAI_PROJECTS[community]["projects"]
    
    project_name, buildings = random.choice(projects)
    building = random.choice(buildings)
    
    return {
        "community": community,
        "project": project_name,
        "building": building,
        "price_range": DUBAI_PROJECTS[community]["avg_price_sqft"],
        "property_types": DUBAI_PROJECTS[community]["property_types"],
    }


def get_realistic_price_per_sqft(community: str) -> tuple:
    """Retourne une plage de prix réaliste pour une communauté"""
    if community in DUBAI_PROJECTS:
        return DUBAI_PROJECTS[community]["avg_price_sqft"]
    return (1200, 2000)  # Default


def get_all_communities() -> list:
    """Retourne toutes les communautés disponibles"""
    return COMMUNITIES


def get_projects_for_community(community: str) -> list:
    """Retourne tous les projets d'une communauté"""
    if community in DUBAI_PROJECTS:
        return [p[0] for p in DUBAI_PROJECTS[community]["projects"]]
    return []

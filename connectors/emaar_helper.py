"""
Helper pour récupérer les données Emaar Properties
Utilise les connecteurs existants (Bayut, PropertyFinder, DLD)
"""
from typing import List, Dict, Optional
from loguru import logger
from connectors.bayut_api import BayutAPIConnector
from connectors.propertyfinder_api import PropertyFinderAPIConnector
from connectors.dld_transactions import DLDTransactionsConnector
from datetime import date, timedelta


class EmaarDataHelper:
    """
    Helper centralisé pour récupérer toutes les données Emaar Properties
    
    Sources :
    1. Bayut RapidAPI (listings, projets, agents, transactions)
    2. PropertyFinder API (listings complémentaires)
    3. DLD Transactions (transactions officielles)
    
    Usage :
        emaar = EmaarDataHelper()
        projects = emaar.get_all_projects()
        listings = emaar.get_all_listings()
        transactions = emaar.get_recent_transactions(days=30)
    """
    
    # IDs connus des développeurs Emaar sur différentes plateformes
    EMAAR_DEVELOPER_IDS = {
        'bayut': None,  # À récupérer dynamiquement
        'propertyfinder': None,  # À récupérer dynamiquement
    }
    
    # Variantes du nom Emaar
    EMAAR_NAME_VARIANTS = [
        "Emaar",
        "Emaar Properties",
        "EMAAR",
        "Emaar Development",
        "Emaar Dubai"
    ]
    
    def __init__(self):
        self.bayut = BayutAPIConnector()
        self.propertyfinder = PropertyFinderAPIConnector()
        self.dld = DLDTransactionsConnector()
        
        # Récupérer les IDs Emaar au démarrage
        self._fetch_emaar_ids()
    
    def _fetch_emaar_ids(self):
        """Récupérer les IDs développeur Emaar sur chaque plateforme"""
        try:
            # Bayut
            developers = self.bayut.search_developers(query="Emaar")
            if developers:
                # Prendre le premier résultat (normalement le plus pertinent)
                self.EMAAR_DEVELOPER_IDS['bayut'] = developers[0].get('id')
                logger.info(f"ID Emaar sur Bayut : {self.EMAAR_DEVELOPER_IDS['bayut']}")
        except Exception as e:
            logger.warning(f"Impossible de récupérer ID Emaar sur Bayut : {e}")
        
        # PropertyFinder (si l'API supporte la recherche par développeur)
        # À implémenter selon la documentation PropertyFinder
    
    def get_all_projects(
        self,
        status: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupérer tous les projets Emaar
        
        Args:
            status: Filtrer par statut (ex: "under-construction", "completed")
            location: Filtrer par localisation (ex: "Dubai Marina")
            
        Returns:
            Liste de projets avec détails complets
        """
        projects = []
        
        # Source 1 : Bayut new_projects_search
        if self.EMAAR_DEVELOPER_IDS['bayut']:
            try:
                bayut_projects = self.bayut.search_new_projects(
                    developer_ids=[self.EMAAR_DEVELOPER_IDS['bayut']],
                    location=location
                )
                
                for project in bayut_projects:
                    projects.append({
                        'source': 'bayut',
                        'project_id': project.get('id'),
                        'name': project.get('name'),
                        'location': project.get('location', {}).get('full_location'),
                        'status': project.get('status'),
                        'completion_date': project.get('completion_date'),
                        'price_min': project.get('price_min'),
                        'price_max': project.get('price_max'),
                        'units_total': project.get('units_total'),
                        'units_available': project.get('units_available'),
                        'developer': 'Emaar Properties',
                        'url': project.get('url'),
                        'images': project.get('images', []),
                        'amenities': project.get('amenities', []),
                        'raw_data': project
                    })
                
                logger.info(f"{len(bayut_projects)} projets Emaar récupérés depuis Bayut")
            except Exception as e:
                logger.error(f"Erreur récupération projets Emaar depuis Bayut : {e}")
        
        # Filtrer par statut si demandé
        if status:
            projects = [p for p in projects if p.get('status') == status]
        
        return projects
    
    def get_all_listings(
        self,
        purpose: str = "for-sale",
        category: str = "residential",
        location: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        bedrooms: Optional[int] = None
    ) -> List[Dict]:
        """
        Récupérer tous les listings Emaar
        
        Args:
            purpose: "for-sale" ou "for-rent"
            category: "residential" ou "commercial"
            location: Filtrer par localisation
            min_price: Prix minimum
            max_price: Prix maximum
            bedrooms: Nombre de chambres
            
        Returns:
            Liste de listings avec détails complets
        """
        listings = []
        
        # Source 1 : Bayut properties_search
        if self.EMAAR_DEVELOPER_IDS['bayut']:
            try:
                bayut_listings = self.bayut.search_properties(
                    developer_ids=[self.EMAAR_DEVELOPER_IDS['bayut']],
                    purpose=purpose,
                    category=category,
                    location=location,
                    price_min=min_price,
                    price_max=max_price,
                    beds=bedrooms
                )
                
                for listing in bayut_listings:
                    prop = listing.get('property', {})
                    location_info = listing.get('location', {})
                    
                    listings.append({
                        'source': 'bayut',
                        'listing_id': listing.get('id'),
                        'property_type': prop.get('type'),
                        'purpose': listing.get('purpose'),
                        'price': listing.get('price'),
                        'bedrooms': prop.get('beds'),
                        'bathrooms': prop.get('baths'),
                        'area_sqft': prop.get('builtup_area', {}).get('sqft'),
                        'location': location_info.get('full_location'),
                        'community': location_info.get('location'),
                        'building': location_info.get('building'),
                        'title': listing.get('title'),
                        'description': listing.get('description'),
                        'images': listing.get('images', []),
                        'amenities': listing.get('amenities', []),
                        'agent': listing.get('agent', {}),
                        'agency': listing.get('agency', {}),
                        'developer': 'Emaar Properties',
                        'url': listing.get('url'),
                        'days_on_market': listing.get('days_on_market'),
                        'is_verified': listing.get('is_verified', False),
                        'raw_data': listing
                    })
                
                logger.info(f"{len(bayut_listings)} listings Emaar récupérés depuis Bayut")
            except Exception as e:
                logger.error(f"Erreur récupération listings Emaar depuis Bayut : {e}")
        
        # Source 2 : PropertyFinder (complémentaire)
        # À implémenter selon disponibilité API
        
        return listings
    
    def get_recent_transactions(
        self,
        days: int = 30,
        location: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupérer les transactions DLD récentes pour Emaar
        
        Args:
            days: Nombre de jours en arrière
            location: Filtrer par localisation (ex: "Dubai Marina")
            
        Returns:
            Liste de transactions officielles DLD
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Récupérer toutes les transactions DLD
        all_transactions = self.dld.fetch_transactions(
            start_date=start_date,
            end_date=end_date
        )
        
        # Filtrer les transactions Emaar
        # Note : Le champ "developer" n'est pas toujours présent dans DLD
        # On filtre par project/community connus d'Emaar
        emaar_transactions = []
        emaar_projects = self.get_emaar_project_names()
        
        for tx in all_transactions:
            # Vérifier si le projet/community correspond à Emaar
            if tx.project and any(name.lower() in tx.project.lower() for name in emaar_projects):
                emaar_transactions.append({
                    'transaction_id': tx.transaction_id,
                    'date': tx.transaction_date,
                    'type': tx.transaction_type,
                    'property_type': tx.property_type,
                    'location': f"{tx.community} - {tx.project}" if tx.project else tx.community,
                    'building': tx.building,
                    'unit': tx.unit_number,
                    'price_aed': float(tx.price_aed) if tx.price_aed else None,
                    'area_sqft': float(tx.area_sqft) if tx.area_sqft else None,
                    'price_per_sqft': float(tx.price_per_sqft) if tx.price_per_sqft else None,
                    'rooms': tx.rooms_count,
                    'is_offplan': tx.is_offplan,
                    'developer': 'Emaar Properties (inferred)'
                })
        
        # Filtrer par location si demandé
        if location:
            emaar_transactions = [
                tx for tx in emaar_transactions 
                if location.lower() in tx['location'].lower()
            ]
        
        logger.info(f"{len(emaar_transactions)} transactions Emaar trouvées sur {len(all_transactions)} total")
        return emaar_transactions
    
    def get_emaar_project_names(self) -> List[str]:
        """
        Liste des projets Emaar connus
        
        Returns:
            Liste de noms de projets Emaar
        """
        return [
            # Dubai Marina
            "Marina Heights",
            "Marina Gate",
            "Marina Promenade",
            "The Address Dubai Marina",
            
            # Downtown Dubai
            "Burj Khalifa",
            "The Address Downtown",
            "Boulevard Central",
            "South Ridge",
            "Standpoint Towers",
            "The Lofts",
            "Old Town",
            "Burj Views",
            
            # Dubai Creek Harbour
            "Creek Beach",
            "Creek Rise",
            "The Cove",
            "Island District",
            
            # Emirates Hills
            "The Lakes",
            "The Meadows",
            "The Springs",
            "The Greens",
            "Emirates Living",
            
            # Arabian Ranches
            "Arabian Ranches",
            "Arabian Ranches 2",
            "Arabian Ranches 3",
            
            # Dubai Hills Estate
            "Dubai Hills Estate",
            "Parkways",
            "Maple",
            "Sidra",
            
            # Emaar South
            "Emaar South",
            "Golf Links",
            
            # Autres
            "Emaar Beachfront",
            "The Valley",
            "Rashid Yachts & Marina",
            "Dubai Harbour",
            "The Oasis",
            "Expo Golf Villas"
        ]
    
    def get_emaar_agents(self) -> List[Dict]:
        """
        Récupérer les agents immobiliers spécialisés Emaar
        
        Returns:
            Liste d'agents avec leurs détails
        """
        agents = []
        
        try:
            # Rechercher agents par nom "Emaar"
            bayut_agents = self.bayut.search_agents_by_name(name="Emaar")
            
            for agent in bayut_agents:
                agents.append({
                    'source': 'bayut',
                    'agent_id': agent.get('id'),
                    'name': agent.get('name'),
                    'phone': agent.get('phone'),
                    'email': agent.get('email'),
                    'agency': agent.get('agency', {}).get('name'),
                    'languages': agent.get('languages', []),
                    'specialties': agent.get('specialties', []),
                    'listings_count': agent.get('listings_count'),
                    'photo': agent.get('photo'),
                    'url': agent.get('url'),
                    'raw_data': agent
                })
            
            logger.info(f"{len(agents)} agents Emaar trouvés")
        except Exception as e:
            logger.error(f"Erreur récupération agents Emaar : {e}")
        
        return agents
    
    def get_emaar_statistics(self, days: int = 30) -> Dict:
        """
        Statistiques agrégées sur Emaar
        
        Args:
            days: Période d'analyse en jours
            
        Returns:
            Dictionnaire de statistiques
        """
        transactions = self.get_recent_transactions(days=days)
        projects = self.get_all_projects()
        listings = self.get_all_listings()
        
        # Calculer statistiques
        total_transactions = len(transactions)
        total_volume_aed = sum(tx['price_aed'] for tx in transactions if tx.get('price_aed'))
        avg_price_per_sqft = sum(tx['price_per_sqft'] for tx in transactions if tx.get('price_per_sqft')) / len(transactions) if transactions else 0
        
        total_projects = len(projects)
        projects_under_construction = len([p for p in projects if p.get('status') == 'under-construction'])
        
        total_listings = len(listings)
        listings_for_sale = len([l for l in listings if l.get('purpose') == 'for-sale'])
        listings_for_rent = len([l for l in listings if l.get('purpose') == 'for-rent'])
        
        return {
            'developer': 'Emaar Properties',
            'period_days': days,
            'transactions': {
                'total': total_transactions,
                'volume_aed': total_volume_aed,
                'avg_price_per_sqft': avg_price_per_sqft
            },
            'projects': {
                'total': total_projects,
                'under_construction': projects_under_construction,
                'completed': total_projects - projects_under_construction
            },
            'listings': {
                'total': total_listings,
                'for_sale': listings_for_sale,
                'for_rent': listings_for_rent
            }
        }


# Fonction helper rapide
def get_emaar_data(data_type: str = "all", **kwargs) -> Dict:
    """
    Fonction helper rapide pour récupérer les données Emaar
    
    Args:
        data_type: "projects", "listings", "transactions", "agents", "statistics", "all"
        **kwargs: Arguments additionnels selon le type
        
    Returns:
        Dictionnaire avec les données demandées
    """
    emaar = EmaarDataHelper()
    
    result = {}
    
    if data_type in ["projects", "all"]:
        result['projects'] = emaar.get_all_projects(**kwargs)
    
    if data_type in ["listings", "all"]:
        result['listings'] = emaar.get_all_listings(**kwargs)
    
    if data_type in ["transactions", "all"]:
        result['transactions'] = emaar.get_recent_transactions(**kwargs)
    
    if data_type in ["agents", "all"]:
        result['agents'] = emaar.get_emaar_agents()
    
    if data_type in ["statistics", "all"]:
        result['statistics'] = emaar.get_emaar_statistics(**kwargs)
    
    return result

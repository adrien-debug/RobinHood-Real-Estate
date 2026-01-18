"""
Connecteur Bayut API - Lead indicators (annonces live)

Bayut est l'un des plus grands portails immobiliers de Dubaï.
Utilise l'API RapidAPI pour accéder aux données Bayut.

Documentation : https://docs.bayutapi.com/
Host RapidAPI : uae-real-estate2.p.rapidapi.com
"""
from typing import List, Optional, Dict
from datetime import date, timedelta, datetime
from decimal import Decimal
import httpx
from loguru import logger
from core.config import settings
from core.models import Listing
from core.utils import normalize_location_name, normalize_rooms_bucket, calculate_price_per_sqft
from core.api_manager import get_api_status


class BayutAPIConnector:
    """
    Connecteur complet pour l'API Bayut via RapidAPI
    
    Documentation : https://docs.bayutapi.com/
    
    Endpoints disponibles :
    - /properties_search : Recherche annonces
    - /property/{id} : Détails propriété
    - /transactions : Transactions DLD
    - /locations_search : Recherche localisations
    - /new_projects_search : Projets off-plan
    - /agencies_by_locations : Agences par zone
    - /agencies_by_name : Recherche agences
    - /agency/{id} : Détails agence
    - /developers_search : Recherche promoteurs
    - /agents_by_name : Recherche agents
    - /agents_by_filters : Agents filtrés
    - /agents_in_agency/{id} : Agents d'une agence
    - /agent/{id} : Détails agent
    - /amenities_search : Recherche équipements
    - /floorplans : Plans d'étage
    """
    
    # RapidAPI endpoints
    RAPIDAPI_HOST = "uae-real-estate2.p.rapidapi.com"
    RAPIDAPI_BASE_URL = "https://uae-real-estate2.p.rapidapi.com"
    
    # IDs des principaux promoteurs Dubai (pour filtres)
    DEVELOPER_IDS = {
        "emaar": 12,
        "damac": 118,
        "nakheel": 6,
        "meraas": 159,
        "dubai_properties": 15,
        "sobha": 47,
        "azizi": 248,
        "danube": 426,
        "binghatti": 538,
        "samana": 901,
        "ellington": 441,
        "omniyat": 189,
        "select_group": 211,
        "mag": 305,
        "tiger": 175,
    }
    
    # IDs des principales zones Dubai
    LOCATION_IDS = {
        "dubai": 2,
        "dubai_marina": 10,
        "downtown_dubai": 36,
        "palm_jumeirah": 21741,
        "business_bay": 59,
        "jumeirah_village_circle": 2,
        "dubai_hills": 16770,
        "arabian_ranches": 11,
        "jumeirah_beach_residence": 72,
        "dubai_creek_harbour": 87107,
    }
    
    def __init__(self):
        self.api_key = settings.bayut_api_key  # RapidAPI Key
        self.base_url = self.RAPIDAPI_BASE_URL
        self.timeout = 30.0
    
    def fetch_listings(
        self,
        community: Optional[str] = None,
        property_type: Optional[str] = None,
        status: str = "active",
        days_back: int = 7
    ) -> List[Listing]:
        """
        Récupérer les annonces Bayut

        Args:
            community: Filtrer par communauté (ex: "Dubai Marina")
            property_type: Filtrer par type (apartment, villa, townhouse)
            status: Statut (active, sold, rented)
            days_back: Jours en arrière pour les nouvelles annonces

        Returns:
            Liste d'annonces
        """
        # Utiliser le gestionnaire d'APIs intelligent
        if get_api_status('bayut'):
            logger.info("Bayut API disponible - utilisation du mode reel")
            return self._fetch_real_data(community, property_type, status, days_back)
        else:
            logger.info("Bayut API non disponible - utilisation de donnees mock")
            return self._generate_mock_data(community, property_type, days_back)


    def _get_headers(self) -> Dict[str, str]:
        """Retourne les headers RapidAPI"""
        return {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }
    
    def _fetch_real_data(
        self,
        community: Optional[str],
        property_type: Optional[str],
        status: str,
        days_back: int
    ) -> List[Listing]:
        """Récupération des vraies données API via RapidAPI"""

        try:
            url = f"{self.base_url}/properties_search"
            headers = self._get_headers()

            # Corps de la requête POST selon la doc RapidAPI
            body = {
                "purpose": "for-sale",
                "index": "latest"
            }

            # Filtrer par catégorie
            if property_type:
                category_map = {
                    "apartment": ["apartments"],
                    "villa": ["villas"],
                    "townhouse": ["townhouses"],
                    "penthouse": ["penthouse"]
                }
                body["categories"] = category_map.get(property_type, ["apartments"])

            logger.info(f"Recuperation annonces Bayut RapidAPI : {community or 'toutes zones'}")

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()

            listings = self._parse_rapidapi_response(data)
            logger.info(f"{len(listings)} annonces Bayut recuperees")
            return listings

        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP Bayut RapidAPI : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Reponse : {e.response.text[:500]}")
            logger.warning("Fallback sur donnees MOCK")
            return self._generate_mock_data(community, property_type, days_back)
        except Exception as e:
            logger.error(f"Erreur Bayut RapidAPI : {e}")
            logger.warning("Fallback sur donnees MOCK")
            return self._generate_mock_data(community, property_type, days_back)
    
    def fetch_transactions(
        self,
        location_ids: Optional[List[int]] = None,
        category: str = "residential",
        purpose: str = "for-sale",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 0
    ) -> List[Dict]:
        """
        Récupérer les transactions DLD via Bayut RapidAPI
        
        Args:
            location_ids: IDs de localisation Dubai
            category: residential, commercial
            purpose: for-sale, for-rent
            start_date: Date de début
            end_date: Date de fin
            page: Page de résultats
            
        Returns:
            Liste de transactions
        """
        if not self.api_key:
            logger.warning("BAYUT_API_KEY non configurée")
            return []
        
        try:
            url = f"{self.base_url}/transactions"
            headers = self._get_headers()
            
            # Corps de la requête
            body = {
                "purpose": purpose,
                "category": category,
                "sort_by": "date",
                "order": "desc"
            }
            
            if location_ids:
                body["locations_ids"] = location_ids
            
            if start_date:
                body["start_date"] = start_date.isoformat()
            if end_date:
                body["end_date"] = end_date.isoformat()
            
            params = {"page": page}
            
            logger.info(f"Recuperation transactions Bayut : page {page}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=body, params=params)
                response.raise_for_status()
                data = response.json()
            
            transactions = data.get("results", [])
            logger.info(f"{len(transactions)} transactions Bayut recuperees")
            return transactions
            
        except Exception as e:
            logger.error(f"Erreur Bayut transactions : {e}")
            return []
    
    def search_properties(
        self,
        location: Optional[str] = None,
        purpose: str = "for-sale",
        category: str = "residential",
        developer_ids: Optional[List[int]] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        beds: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Rechercher des propriétés sur Bayut
        
        Args:
            location: Nom de la localisation
            purpose: "for-sale" ou "for-rent"
            category: "residential" ou "commercial"
            developer_ids: Liste d'IDs de développeurs
            price_min: Prix minimum
            price_max: Prix maximum
            beds: Nombre de chambres
            limit: Nombre max de résultats
            
        Returns:
            Liste de propriétés
        """
        if not self.api_key:
            logger.warning("BAYUT_API_KEY non configurée")
            return []
        
        try:
            url = f"{self.base_url}/properties_search"
            headers = self._get_headers()
            
            body = {
                "purpose": purpose,
                "category": category,
                "index": "latest"
            }
            
            if developer_ids:
                body["developer_ids"] = developer_ids
            
            if price_min:
                body["price_min"] = price_min
            if price_max:
                body["price_max"] = price_max
            
            if beds:
                body["beds"] = beds
            
            params = {"page": 0}
            
            logger.info(f"Recherche propriétés Bayut : {location or 'toutes zones'}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=body, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = data.get("results", [])[:limit]
            logger.info(f"{len(results)} propriétés trouvées")
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche propriétés Bayut : {e}")
            return []
    
    def search_locations(self, query: str, page: int = 0) -> List[Dict]:
        """
        Rechercher des localisations par nom
        
        Args:
            query: Terme de recherche (ex: "Dubai Marina")
            page: Page de résultats (défaut: 0)
            
        Returns:
            Liste de localisations avec IDs, coordonnées, hiérarchie
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/locations_search"
            headers = self._get_headers()
            params = {"query": query, "page": page}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except Exception as e:
            logger.error(f"Erreur recherche locations : {e}")
            return []
    
    # ============================================================
    # PROPERTY ENDPOINTS
    # ============================================================
    
    def get_property_details(self, property_id: int, langs: str = "en") -> Optional[Dict]:
        """
        Récupérer les détails complets d'une propriété
        
        Args:
            property_id: ID unique de la propriété
            langs: Langues (en, ar, ru, zh)
            
        Returns:
            Détails complets : prix, specs, localisation, agent, agence,
            médias, vérification, légal, projet, amenities, plans, paiement
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/property/{property_id}"
            headers = self._get_headers()
            params = {"langs": langs}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Erreur property details {property_id} : {e}")
            return None
    
    # ============================================================
    # NEW PROJECTS (OFF-PLAN) ENDPOINTS
    # ============================================================
    
    def search_new_projects(
        self,
        location: Optional[str] = None,
        categories: Optional[List[str]] = None,
        location_ids: Optional[List[int]] = None,
        developer_ids: Optional[List[int]] = None,
        is_completed: Optional[bool] = None,
        rooms: Optional[List[int]] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        area_min: Optional[float] = None,
        area_max: Optional[float] = None,
        limit: int = 20,
        completion_date: Optional[str] = None,
        max_prehandover_percent: Optional[int] = None,
        page: int = 0
    ) -> List[Dict]:
        """
        Rechercher les nouveaux projets immobiliers (off-plan)
        
        Args:
            location: Nom de la localisation (ignoré, utilisez location_ids)
            categories: villas, apartments, townhouses, penthouse, etc.
            location_ids: IDs de localisation
            developer_ids: IDs des promoteurs
            is_completed: True=completed, False=under-construction
            rooms: Liste de chambres autorisées [0,1,2,3]
            price_min/max: Fourchette de prix AED
            area_min/max: Fourchette de surface sqft
            limit: Nombre max de résultats
            completion_date: Date de complétion (DD-MM-YYYY)
            max_prehandover_percent: % max avant remise des clés
            page: Page de résultats
            
        Returns:
            Liste de projets off-plan avec détails promoteur, paiement, etc.
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/new_projects_search"
            headers = self._get_headers()
            
            body = {}
            if categories:
                body["categories"] = categories
            if location_ids:
                body["locations_ids"] = location_ids
            if developer_ids:
                body["developer_ids"] = developer_ids
            if is_completed is not None:
                body["is_completed"] = is_completed
            if rooms:
                body["rooms"] = rooms
            if price_min:
                body["price_min"] = price_min
            if price_max:
                body["price_max"] = price_max
            if area_min:
                body["area_min"] = area_min
            if area_max:
                body["area_max"] = area_max
            if completion_date:
                body["completion_date"] = completion_date
            if max_prehandover_percent:
                body["max_prehandover_percent"] = max_prehandover_percent
            
            params = {"page": page}
            
            logger.info(f"Recherche projets off-plan : page {page}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=body, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = data.get("results", [])[:limit]
            logger.info(f"{len(results)} projets off-plan trouvés")
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche projets : {e}")
            return []
    
    # ============================================================
    # AGENCY ENDPOINTS
    # ============================================================
    
    def get_agencies_by_locations(
        self, 
        location_ids: List[int], 
        page: int = 0,
        langs: str = "en"
    ) -> List[Dict]:
        """
        Récupérer les agences opérant dans des localisations
        
        Args:
            location_ids: IDs de localisation (obligatoire)
            page: Page de résultats
            langs: Langues
            
        Returns:
            Liste d'agences avec stats, agents, spécialités
        """
        if not self.api_key or not location_ids:
            return []
        
        try:
            url = f"{self.base_url}/agencies_by_locations"
            headers = self._get_headers()
            params = {
                "locations_ids": ",".join(map(str, location_ids)),
                "page": page,
                "langs": langs
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except Exception as e:
            logger.error(f"Erreur agences par location : {e}")
            return []
    
    def search_agencies(self, query: str, page: int = 0, langs: str = "en") -> List[Dict]:
        """
        Rechercher des agences par nom
        
        Args:
            query: Terme de recherche
            page: Page de résultats
            langs: Langues
            
        Returns:
            Liste d'agences correspondantes
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/agencies_by_name"
            headers = self._get_headers()
            params = {"query": query, "page": page, "langs": langs}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except Exception as e:
            logger.error(f"Erreur recherche agences : {e}")
            return []
    
    def get_agency_details(self, agency_id: int, langs: str = "en") -> Optional[Dict]:
        """
        Récupérer les détails d'une agence
        
        Args:
            agency_id: ID unique de l'agence
            langs: Langues
            
        Returns:
            Détails complets : description, licences, stats, contacts
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/agency/{agency_id}"
            headers = self._get_headers()
            params = {"langs": langs}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Erreur agency details {agency_id} : {e}")
            return None
    
    # ============================================================
    # DEVELOPER ENDPOINTS
    # ============================================================
    
    def search_developers(self, query: str, page: int = 0, langs: str = "en") -> List[Dict]:
        """
        Rechercher des promoteurs immobiliers par nom
        
        Args:
            query: Terme de recherche (ex: "Emaar")
            page: Page de résultats
            langs: Langues
            
        Returns:
            Liste de promoteurs avec logo, contacts, stats projets
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/developers_search"
            headers = self._get_headers()
            params = {"query": query, "page": page, "langs": langs}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except Exception as e:
            logger.error(f"Erreur recherche developers : {e}")
            return []
    
    # ============================================================
    # AGENT ENDPOINTS
    # ============================================================
    
    def search_agents_by_name(self, query: str, page: int = 0, langs: str = "en") -> List[Dict]:
        """
        Rechercher des agents par nom
        
        Args:
            query: Nom de l'agent
            page: Page de résultats
            langs: Langues
            
        Returns:
            Liste d'agents avec stats, agence, spécialités, contacts
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/agents_by_name"
            headers = self._get_headers()
            params = {"query": query, "page": page, "langs": langs}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except Exception as e:
            logger.error(f"Erreur recherche agents : {e}")
            return []
    
    def get_agents_by_filters(
        self,
        location_ids: Optional[List[int]] = None,
        purpose: str = "for-sale",
        category: str = "residential",
        page: int = 0,
        langs: str = "en"
    ) -> List[Dict]:
        """
        Récupérer des agents par filtres
        
        Args:
            location_ids: IDs de localisation
            purpose: for-sale, for-rent
            category: residential, commercial, short_term_residential
            page: Page de résultats
            langs: Langues
            
        Returns:
            Liste d'agents filtrés
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/agents_by_filters"
            headers = self._get_headers()
            params = {
                "purpose": purpose,
                "category": category,
                "page": page,
                "langs": langs
            }
            if location_ids:
                params["locations_ids"] = ",".join(map(str, location_ids))
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except Exception as e:
            logger.error(f"Erreur agents by filters : {e}")
            return []
    
    def get_agents_in_agency(self, agency_id: int, langs: str = "en") -> List[Dict]:
        """
        Récupérer tous les agents d'une agence
        
        Args:
            agency_id: ID de l'agence
            langs: Langues
            
        Returns:
            Liste des agents de l'agence
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/agents_in_agency/{agency_id}"
            headers = self._get_headers()
            params = {"langs": langs}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except Exception as e:
            logger.error(f"Erreur agents in agency {agency_id} : {e}")
            return []
    
    def get_agent_details(self, agent_id: int, langs: str = "en") -> Optional[Dict]:
        """
        Récupérer les détails d'un agent
        
        Args:
            agent_id: ID unique de l'agent
            langs: Langues
            
        Returns:
            Profil complet : bio, expérience, contacts, stats, réseaux sociaux
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/agent/{agent_id}"
            headers = self._get_headers()
            params = {"langs": langs}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Erreur agent details {agent_id} : {e}")
            return None
    
    # ============================================================
    # AMENITIES ENDPOINT
    # ============================================================
    
    def search_amenities(self, query: str) -> List[str]:
        """
        Rechercher des équipements/amenities
        
        Args:
            query: Terme de recherche (ex: "pool", "gym")
            
        Returns:
            Liste de noms d'amenities correspondants
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/amenities_search"
            headers = self._get_headers()
            params = {"query": query}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("results", [])
            
        except Exception as e:
            logger.error(f"Erreur recherche amenities : {e}")
            return []
    
    # ============================================================
    # FLOORPLANS ENDPOINT
    # ============================================================
    
    def get_floorplans(self, location_slug: str) -> Dict:
        """
        Récupérer les plans d'étage pour une localisation
        
        Args:
            location_slug: Chemin de localisation (ex: "/dubai/dubai-marina/marina-towers")
            
        Returns:
            {
                "child_locations": [...],  # Si localisation haute niveau
                "floorplans": [...]  # Si localisation précise (bâtiment)
            }
            Chaque floorplan contient : beds, baths, category, 2d_imgs, 3d_imgs, models
        """
        if not self.api_key:
            return {"child_locations": [], "floorplans": []}
        
        try:
            url = f"{self.base_url}/floorplans"
            headers = self._get_headers()
            params = {"location_slug": location_slug}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Erreur floorplans {location_slug} : {e}")
            return {"child_locations": [], "floorplans": []}
    
    # ============================================================
    # DEVELOPER HELPERS (Emaar, DAMAC, etc.)
    # ============================================================
    
    def get_developer_id(self, developer_name: str) -> Optional[int]:
        """
        Récupérer l'ID d'un promoteur par nom
        
        Args:
            developer_name: Nom du promoteur (ex: "emaar", "damac")
            
        Returns:
            ID du promoteur ou None
        """
        name_lower = developer_name.lower().replace(" ", "_")
        return self.DEVELOPER_IDS.get(name_lower)
    
    def get_projects_by_developer(
        self,
        developer_name: str,
        is_completed: Optional[bool] = None,
        page: int = 0
    ) -> List[Dict]:
        """
        Récupérer tous les projets d'un promoteur
        
        Args:
            developer_name: Nom du promoteur (emaar, damac, nakheel, etc.)
            is_completed: True=completed, False=off-plan, None=tous
            page: Page de résultats
            
        Returns:
            Liste de projets du promoteur
        """
        developer_id = self.get_developer_id(developer_name)
        if not developer_id:
            # Essayer de chercher par nom
            results = self.search_developers(developer_name)
            if results:
                developer_id = results[0].get("id")
        
        if not developer_id:
            logger.warning(f"Promoteur non trouvé : {developer_name}")
            return []
        
        return self.search_new_projects(
            developer_ids=[developer_id],
            is_completed=is_completed,
            page=page
        )
    
    def get_emaar_projects(self, is_completed: Optional[bool] = None) -> List[Dict]:
        """Récupérer tous les projets Emaar"""
        return self.get_projects_by_developer("emaar", is_completed)
    
    def get_damac_projects(self, is_completed: Optional[bool] = None) -> List[Dict]:
        """Récupérer tous les projets DAMAC"""
        return self.get_projects_by_developer("damac", is_completed)
    
    def get_nakheel_projects(self, is_completed: Optional[bool] = None) -> List[Dict]:
        """Récupérer tous les projets Nakheel"""
        return self.get_projects_by_developer("nakheel", is_completed)
    
    def get_all_major_developers_projects(self, is_completed: Optional[bool] = None) -> Dict[str, List[Dict]]:
        """
        Récupérer les projets de tous les principaux promoteurs
        
        Returns:
            {
                "emaar": [...],
                "damac": [...],
                "nakheel": [...],
                ...
            }
        """
        all_projects = {}
        for developer_name in self.DEVELOPER_IDS.keys():
            projects = self.get_projects_by_developer(developer_name, is_completed)
            if projects:
                all_projects[developer_name] = projects
                logger.info(f"{developer_name}: {len(projects)} projets")
        
        return all_projects
    
    def get_location_id(self, location_name: str) -> Optional[int]:
        """
        Récupérer l'ID d'une localisation par nom
        
        Args:
            location_name: Nom de la zone (ex: "dubai_marina", "palm_jumeirah")
            
        Returns:
            ID de localisation ou None
        """
        name_lower = location_name.lower().replace(" ", "_")
        return self.LOCATION_IDS.get(name_lower)
    
    # ============================================================
    # PARSING & UTILITIES
    # ============================================================
    
    def _parse_rapidapi_response(self, data: dict) -> List[Listing]:
        """
        Parser la réponse RapidAPI Bayut
        
        Format RapidAPI (voir https://docs.bayutapi.com/)
        """
        listings = []
        
        items = data.get("results", [])
        
        if not items:
            logger.warning("Aucune annonce dans la réponse Bayut RapidAPI")
            return listings
        
        for item in items:
            try:
                location = item.get("location", {})
                details = item.get("details", {})
                area_info = item.get("area", {})
                meta = item.get("meta", {})
                verification = item.get("verification", {})
                
                # Extraction des données
                bedrooms = details.get("bedrooms", 0)
                area_sqft = float(area_info.get("built_up", 0) or 0)
                price_aed = float(item.get("price", 0) or 0)
                
                # Calculer jours sur marché depuis date de création
                created_at = meta.get("created_at")
                days_on_market = 0
                listing_date = None
                if created_at:
                    listing_date = self._parse_date(created_at)
                    if listing_date:
                        days_on_market = (date.today() - listing_date).days
                
                # Localisation
                community_info = location.get("community", {})
                sub_community_info = location.get("sub_community", {})
                cluster_info = location.get("cluster", {})
                
                community_name = community_info.get("name") if isinstance(community_info, dict) else None
                project_name = sub_community_info.get("name") if isinstance(sub_community_info, dict) else None
                building_name = cluster_info.get("name") if isinstance(cluster_info, dict) else None
                
                # Type de propriété
                type_info = item.get("type", {})
                prop_type = type_info.get("sub", "Apartments") if isinstance(type_info, dict) else "Apartments"
                
                listing = Listing(
                    listing_id=str(item.get("id", "")),
                    listing_date=listing_date,
                    source="bayut",
                    
                    community=normalize_location_name(community_name),
                    project=normalize_location_name(project_name),
                    building=normalize_location_name(building_name),
                    
                    property_type=self._normalize_property_type(prop_type),
                    rooms_count=bedrooms,
                    rooms_bucket=normalize_rooms_bucket(bedrooms),
                    area_sqft=Decimal(str(area_sqft)) if area_sqft > 0 else None,
                    
                    asking_price_aed=Decimal(str(price_aed)) if price_aed > 0 else None,
                    asking_price_per_sqft=calculate_price_per_sqft(price_aed, area_sqft),
                    original_price_aed=None,  # Non disponible dans cette API
                    
                    price_changes=0,  # Non disponible directement
                    last_price_change_date=None,
                    days_on_market=days_on_market,
                    
                    status="active" if verification.get("is_verified") else "unverified",
                    url=meta.get("url")
                )
                listings.append(listing)
                
            except Exception as e:
                logger.warning(f"Erreur parsing annonce Bayut {item.get('id', 'N/A')} : {e}")
                continue
        
        return listings
    
    def _parse_response(self, data: dict) -> List[Listing]:
        """Wrapper pour compatibilité - utilise le parser RapidAPI"""
        return self._parse_rapidapi_response(data)
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parser une date depuis string"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except:
            return None
    
    def _normalize_property_type(self, prop_type: str) -> str:
        """Normaliser le type de propriété"""
        if not prop_type:
            return "apartment"
        
        prop_lower = prop_type.lower()
        if "apartment" in prop_lower or "flat" in prop_lower:
            return "apartment"
        elif "villa" in prop_lower:
            return "villa"
        elif "townhouse" in prop_lower or "town house" in prop_lower:
            return "townhouse"
        elif "penthouse" in prop_lower:
            return "penthouse"
        else:
            return "other"
    
    def _generate_mock_data(
        self, 
        community: Optional[str], 
        property_type: Optional[str],
        days_back: int
    ) -> List[Listing]:
        """Générer des données mock réalistes pour développement"""
        import random
        from core.dubai_mock_data import get_random_project, ROOM_TYPES
        
        listings = []
        for i in range(40):
            # Obtenir un projet réaliste
            project_data = get_random_project(community)
            
            rooms_count, rooms_bucket = random.choice(ROOM_TYPES)
            
            # Surface réaliste selon le type
            if rooms_count == 0:  # Studio
                area = Decimal(random.randint(350, 550))
            elif rooms_count == 1:
                area = Decimal(random.randint(600, 900))
            elif rooms_count == 2:
                area = Decimal(random.randint(900, 1400))
            else:
                area = Decimal(random.randint(1400, 3500))
            
            # Prix réaliste basé sur la communauté
            min_price, max_price = project_data["price_range"]
            price_sqft = Decimal(random.randint(min_price, max_price))
            price = area * price_sqft
            
            # Léger markup pour les annonces (vendeurs demandent plus)
            markup = Decimal(random.uniform(1.02, 1.15))
            original_price = price * markup
            
            days_market = random.randint(1, 180)
            price_changes = random.randint(0, 3) if days_market > 30 else 0
            
            # Réduction de prix si changements
            if price_changes > 0:
                price = original_price * Decimal(random.uniform(0.92, 0.98))
            
            # Type de propriété réaliste
            prop_type = property_type or random.choice(project_data["property_types"])
            
            listing = Listing(
                listing_id=f"BAY-{date.today().strftime('%Y%m')}-{i:04d}",
                listing_date=date.today() - timedelta(days=random.randint(1, days_back)),
                source="bayut",
                
                community=project_data["community"],
                project=project_data["project"],
                building=project_data["building"],
                
                property_type=prop_type,
                rooms_count=rooms_count,
                rooms_bucket=rooms_bucket,
                area_sqft=area,
                
                asking_price_aed=price,
                asking_price_per_sqft=calculate_price_per_sqft(price, area),
                original_price_aed=original_price,
                
                price_changes=price_changes,
                last_price_change_date=date.today() - timedelta(days=random.randint(1, 30)) if price_changes > 0 else None,
                days_on_market=days_market,
                
                status="active",
                url=f"https://www.bayut.com/property/{project_data['project'].lower().replace(' ', '-')}-{i}"
            )
            listings.append(listing)
        
        logger.info(f"Données MOCK Bayut générées : {len(listings)} annonces")
        return listings
    
    def calculate_listing_metrics(self, listings: List[Listing]) -> Dict:
        """
        Calculer des métriques agrégées sur les annonces
        
        Returns:
            {
                "total_listings": 150,
                "avg_days_on_market": 45,
                "pct_price_reductions": 35.5,
                "avg_price_reduction_pct": 8.2,
                "new_listings_7d": 25
            }
        """
        if not listings:
            return {}
        
        total = len(listings)
        avg_days = sum(l.days_on_market for l in listings if l.days_on_market) / total
        
        price_reduced = [l for l in listings if l.price_changes and l.price_changes > 0]
        pct_reduced = (len(price_reduced) / total) * 100 if total > 0 else 0
        
        # Calcul de la réduction moyenne
        reductions = []
        for l in price_reduced:
            if l.original_price_aed and l.asking_price_aed and l.original_price_aed > 0:
                reduction_pct = ((l.original_price_aed - l.asking_price_aed) / l.original_price_aed) * 100
                reductions.append(float(reduction_pct))
        
        avg_reduction = sum(reductions) / len(reductions) if reductions else 0
        
        # Nouvelles annonces (7 derniers jours)
        cutoff = date.today() - timedelta(days=7)
        new_listings = len([l for l in listings if l.listing_date and l.listing_date >= cutoff])
        
        return {
            "total_listings": total,
            "avg_days_on_market": round(avg_days, 1),
            "pct_price_reductions": round(pct_reduced, 1),
            "avg_price_reduction_pct": round(avg_reduction, 1),
            "new_listings_7d": new_listings
        }

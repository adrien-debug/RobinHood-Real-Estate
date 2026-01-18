"""
Connecteur Zyla Labs UAE Real Estate API

API complète pour l'immobilier UAE avec statistiques de marché.

Documentation : https://zylalabs.com/api-marketplace/real-estate/uae-real-estate-api/478
"""
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal
import httpx
from loguru import logger
from core.config import settings
from core.models import Listing
from core.utils import normalize_location_name, normalize_rooms_bucket, calculate_price_per_sqft


class ZylaLabsAPIConnector:
    """
    Connecteur pour Zyla Labs UAE Real Estate API
    
    Endpoints disponibles :
    - /autocomplete : Suggestions de localisations
    - /get+properties : Liste propriétés par zone
    - /get+agencies+list : Recherche agences
    - /property+by+listing+id : Détails propriété
    - /recent : Dernières propriétés ajoutées
    - /search : Recherche full-text
    - /market+stats : Statistiques marché
    """
    
    BASE_URL = "https://zylalabs.com/api/478/uae+real+estate+api"
    
    def __init__(self):
        self.api_key = settings.zylalabs_api_key
        self.timeout = 30.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers d'authentification"""
        return {
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def is_configured(self) -> bool:
        """Vérifie si l'API est configurée"""
        return bool(self.api_key)
    
    # ============================================================
    # LOCATION ENDPOINTS
    # ============================================================
    
    def autocomplete(
        self,
        query: str,
        hits_per_page: int = 10,
        page: int = 0,
        lang: str = "en"
    ) -> List[Dict]:
        """
        Suggestions de localisations
        
        Args:
            query: Terme de recherche (ex: "Dubai Marina")
            hits_per_page: Résultats par page
            page: Page
            lang: Langue (en, ar)
            
        Returns:
            Liste de localisations avec IDs
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.BASE_URL}/357/autocomplete"
            headers = self._get_headers()
            params = {
                "query": query,
                "hitsPerPage": hits_per_page,
                "page": page,
                "lang": lang
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("hits", [])
            
        except Exception as e:
            logger.error(f"Erreur Zyla autocomplete : {e}")
            return []
    
    # ============================================================
    # PROPERTIES ENDPOINTS
    # ============================================================
    
    def get_properties(
        self,
        location_external_ids: str,
        purpose: str = "for-sale",
        page: int = 0,
        hits_per_page: int = 25
    ) -> Dict:
        """
        Récupérer les propriétés par localisation
        
        Args:
            location_external_ids: IDs de localisation (depuis autocomplete)
            purpose: "for-sale" ou "for-rent"
            page: Page de résultats
            hits_per_page: Résultats par page
            
        Returns:
            Données propriétés avec pagination
        """
        if not self.api_key:
            return {"hits": []}
        
        try:
            url = f"{self.BASE_URL}/358/get+properties"
            headers = self._get_headers()
            params = {
                "locationExternalIDs": location_external_ids,
                "purpose": purpose,
                "page": page,
                "hitsPerPage": hits_per_page
            }
            
            logger.info(f"Zyla properties : location {location_external_ids}, page {page}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            
        except Exception as e:
            logger.error(f"Erreur Zyla get_properties : {e}")
            return {"hits": []}
    
    def get_recent_properties(self, limit: int = 25) -> List[Dict]:
        """
        Récupérer les dernières propriétés ajoutées
        
        Args:
            limit: Nombre de résultats
            
        Returns:
            Liste des propriétés récentes
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.BASE_URL}/21787/recent"
            headers = self._get_headers()
            params = {"limit": limit}
            
            logger.info(f"Zyla recent : {limit} propriétés")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("hits", data.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur Zyla recent : {e}")
            return []
    
    def get_property_by_id(self, listing_id: str) -> Optional[Dict]:
        """
        Récupérer les détails d'une propriété
        
        Args:
            listing_id: ID de la propriété
            
        Returns:
            Détails complets de la propriété
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.BASE_URL}/21793/property+by+listing+id"
            headers = self._get_headers()
            params = {"listing_id": listing_id}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            
        except Exception as e:
            logger.error(f"Erreur Zyla property {listing_id} : {e}")
            return None
    
    def search(
        self,
        query: str,
        page: int = 0,
        hits_per_page: int = 25
    ) -> Dict:
        """
        Recherche full-text
        
        Args:
            query: Terme de recherche (ex: "villa palm jumeirah")
            page: Page de résultats
            hits_per_page: Résultats par page
            
        Returns:
            Résultats de recherche
        """
        if not self.api_key:
            return {"hits": []}
        
        try:
            url = f"{self.BASE_URL}/21781/search"
            headers = self._get_headers()
            params = {
                "q": query,
                "page": page,
                "hitsPerPage": hits_per_page
            }
            
            logger.info(f"Zyla search : '{query}'")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            
        except Exception as e:
            logger.error(f"Erreur Zyla search : {e}")
            return {"hits": []}
    
    # ============================================================
    # AGENCIES ENDPOINTS
    # ============================================================
    
    def get_agencies_list(self, query: str = "") -> List[Dict]:
        """
        Rechercher des agences immobilières
        
        Args:
            query: Terme de recherche
            
        Returns:
            Liste d'agences
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.BASE_URL}/360/get+agencies+list"
            headers = self._get_headers()
            params = {"query": query} if query else {}
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("hits", data.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur Zyla agencies : {e}")
            return []
    
    # ============================================================
    # MARKET STATS ENDPOINTS
    # ============================================================
    
    def get_market_stats(self) -> Dict:
        """
        Récupérer les statistiques de marché
        
        Returns:
            {
                "total_properties": int,
                "average_price": float,
                "bedroom_distribution": {...},
                "property_type_distribution": {...},
                "city_distribution": {...}
            }
        """
        if not self.api_key:
            return {}
        
        try:
            url = f"{self.BASE_URL}/21775/market+stats"
            headers = self._get_headers()
            
            logger.info("Zyla market stats")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
            
        except Exception as e:
            logger.error(f"Erreur Zyla market stats : {e}")
            return {}
    
    # ============================================================
    # CONVERSION HELPERS
    # ============================================================
    
    def fetch_listings(
        self,
        location_name: Optional[str] = None,
        purpose: str = "for-sale",
        max_results: int = 100
    ) -> List[Listing]:
        """
        Récupérer les annonces et les convertir en modèle Listing
        
        Args:
            location_name: Zone à rechercher (optionnel)
            purpose: "for-sale" ou "for-rent"
            max_results: Nombre max de résultats
            
        Returns:
            Liste de Listing
        """
        all_listings = []
        
        # Si location spécifiée, chercher l'ID
        location_ids = ""
        if location_name:
            locations = self.autocomplete(location_name, hits_per_page=1)
            if locations:
                location_ids = str(locations[0].get("externalID", ""))
        
        # Si pas de location, utiliser les propriétés récentes
        if not location_ids:
            items = self.get_recent_properties(limit=max_results)
        else:
            result = self.get_properties(
                location_external_ids=location_ids,
                purpose=purpose,
                hits_per_page=max_results
            )
            items = result.get("hits", [])
        
        for item in items:
            try:
                listing = self._convert_to_listing(item)
                if listing:
                    all_listings.append(listing)
            except Exception as e:
                logger.warning(f"Erreur conversion Zyla : {e}")
                continue
        
        logger.info(f"{len(all_listings)} listings Zyla au total")
        return all_listings
    
    def _convert_to_listing(self, item: Dict) -> Optional[Listing]:
        """Convertir une propriété Zyla en Listing"""
        try:
            # Extraction des données
            bedrooms = item.get("rooms", 0)
            if isinstance(bedrooms, str):
                try:
                    bedrooms = int(bedrooms)
                except:
                    bedrooms = 0
            
            area_sqft = float(item.get("area", 0) or 0)
            price_aed = float(item.get("price", 0) or 0)
            
            # Location
            location = item.get("location", [])
            community = None
            if isinstance(location, list) and location:
                community = location[0].get("name") if isinstance(location[0], dict) else str(location[0])
            elif isinstance(location, dict):
                community = location.get("name")
            
            return Listing(
                listing_id=str(item.get("id", item.get("externalID", ""))),
                listing_date=None,
                source="zylalabs",
                
                community=normalize_location_name(community),
                project=item.get("title"),
                building=None,
                
                property_type=self._normalize_property_type(item.get("category", {}).get("name")),
                rooms_count=bedrooms,
                rooms_bucket=normalize_rooms_bucket(bedrooms) if bedrooms else None,
                area_sqft=Decimal(str(area_sqft)) if area_sqft > 0 else None,
                
                asking_price_aed=Decimal(str(price_aed)) if price_aed > 0 else None,
                asking_price_per_sqft=calculate_price_per_sqft(price_aed, area_sqft),
                original_price_aed=None,
                
                price_changes=0,
                last_price_change_date=None,
                days_on_market=0,
                
                status="active",
                url=item.get("url")
            )
            
        except Exception as e:
            logger.warning(f"Erreur parsing Zyla : {e}")
            return None
    
    def _normalize_property_type(self, prop_type: str) -> str:
        """Normaliser le type de propriété"""
        if not prop_type:
            return "apartment"
        
        prop_lower = prop_type.lower()
        if "apartment" in prop_lower:
            return "apartment"
        elif "villa" in prop_lower:
            return "villa"
        elif "townhouse" in prop_lower:
            return "townhouse"
        elif "penthouse" in prop_lower:
            return "penthouse"
        elif "land" in prop_lower or "plot" in prop_lower:
            return "land"
        else:
            return "other"

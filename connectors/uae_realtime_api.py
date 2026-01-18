"""
Connecteur UAE Real Estate Data-Real Time API via RapidAPI

API temps réel pour agents, propriétés et données immobilières UAE.

Host: uae-real-estate-data-real-time-api.p.rapidapi.com
Documentation: https://rapidapi.com/uae-real-estate-data-real-time-api
"""
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal
import httpx
from loguru import logger
from core.config import settings
from core.models import Listing
from core.utils import normalize_location_name, normalize_rooms_bucket, calculate_price_per_sqft


class UAERealTimeAPIConnector:
    """
    Connecteur pour UAE Real Estate Data-Real Time API
    
    Endpoints disponibles :
    - /directory/agents : Annuaire des agents
    - /directory/agencies : Annuaire des agences
    - /properties : Propriétés
    - /transactions : Transactions
    """
    
    RAPIDAPI_HOST = "uae-real-estate-data-real-time-api.p.rapidapi.com"
    RAPIDAPI_BASE_URL = "https://uae-real-estate-data-real-time-api.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = settings.uae_realtime_api_key
        self.base_url = self.RAPIDAPI_BASE_URL
        self.timeout = 30.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers RapidAPI"""
        return {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.RAPIDAPI_HOST
        }
    
    def is_configured(self) -> bool:
        """Vérifie si l'API est configurée"""
        return bool(self.api_key)
    
    # ============================================================
    # AGENTS DIRECTORY
    # ============================================================
    
    def get_agents_directory(
        self,
        page: int = 0,
        hits_per_page: int = 20
    ) -> Dict:
        """
        Récupérer l'annuaire des agents immobiliers
        
        Args:
            page: Page de résultats
            hits_per_page: Résultats par page
            
        Returns:
            Liste des agents avec détails
        """
        if not self.api_key:
            logger.warning("UAE_REALTIME_API_KEY non configurée")
            return {"data": [], "pagination": {}}
        
        try:
            url = f"{self.base_url}/directory/agents"
            headers = self._get_headers()
            params = {
                "page": page,
                "hits_per_page": hits_per_page
            }
            
            logger.info(f"UAE RealTime agents directory : page {page}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            
        except Exception as e:
            logger.error(f"Erreur UAE RealTime agents : {e}")
            return {"data": [], "pagination": {}}
    
    def search_agents(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        page: int = 0,
        hits_per_page: int = 20
    ) -> List[Dict]:
        """
        Rechercher des agents
        
        Args:
            query: Terme de recherche (nom, spécialité)
            location: Zone géographique
            page: Page de résultats
            hits_per_page: Résultats par page
            
        Returns:
            Liste des agents correspondants
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/directory/agents"
            headers = self._get_headers()
            params = {
                "page": page,
                "hits_per_page": hits_per_page
            }
            
            if query:
                params["query"] = query
            if location:
                params["location"] = location
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("data", data.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur recherche agents UAE RealTime : {e}")
            return []
    
    # ============================================================
    # AGENCIES DIRECTORY
    # ============================================================
    
    def get_agencies_directory(
        self,
        page: int = 0,
        hits_per_page: int = 20
    ) -> Dict:
        """
        Récupérer l'annuaire des agences immobilières
        
        Args:
            page: Page de résultats
            hits_per_page: Résultats par page
            
        Returns:
            Liste des agences avec détails
        """
        if not self.api_key:
            return {"data": [], "pagination": {}}
        
        try:
            url = f"{self.base_url}/directory/agencies"
            headers = self._get_headers()
            params = {
                "page": page,
                "hits_per_page": hits_per_page
            }
            
            logger.info(f"UAE RealTime agencies directory : page {page}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            
        except Exception as e:
            logger.error(f"Erreur UAE RealTime agencies : {e}")
            return {"data": [], "pagination": {}}
    
    # ============================================================
    # PROPERTIES
    # ============================================================
    
    def search_properties(
        self,
        location: Optional[str] = None,
        property_type: Optional[str] = None,
        purpose: str = "for-sale",
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        beds: Optional[int] = None,
        page: int = 0,
        hits_per_page: int = 20
    ) -> List[Dict]:
        """
        Rechercher des propriétés
        
        Args:
            location: Zone géographique
            property_type: Type de propriété (apartment, villa, etc.)
            purpose: "for-sale" ou "for-rent"
            price_min: Prix minimum AED
            price_max: Prix maximum AED
            beds: Nombre de chambres
            page: Page de résultats
            hits_per_page: Résultats par page
            
        Returns:
            Liste des propriétés
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/properties"
            headers = self._get_headers()
            params = {
                "page": page,
                "hits_per_page": hits_per_page,
                "purpose": purpose
            }
            
            if location:
                params["location"] = location
            if property_type:
                params["property_type"] = property_type
            if price_min:
                params["price_min"] = price_min
            if price_max:
                params["price_max"] = price_max
            if beds:
                params["beds"] = beds
            
            logger.info(f"UAE RealTime properties : {location or 'all'}, page {page}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("data", data.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur recherche properties UAE RealTime : {e}")
            return []
    
    def fetch_listings(
        self,
        location: Optional[str] = None,
        property_type: Optional[str] = None,
        purpose: str = "for-sale",
        max_pages: int = 5
    ) -> List[Listing]:
        """
        Récupérer les annonces et les convertir en modèle Listing
        
        Args:
            location: Zone à rechercher
            property_type: Type de propriété
            purpose: "for-sale" ou "for-rent"
            max_pages: Nombre max de pages à récupérer
            
        Returns:
            Liste de Listing
        """
        all_listings = []
        
        for page in range(max_pages):
            items = self.search_properties(
                location=location,
                property_type=property_type,
                purpose=purpose,
                page=page
            )
            
            if not items:
                break
            
            listings = self._parse_properties(items)
            all_listings.extend(listings)
        
        logger.info(f"{len(all_listings)} listings UAE RealTime au total")
        return all_listings
    
    def _parse_properties(self, items: List[Dict]) -> List[Listing]:
        """Convertir les propriétés en Listing"""
        listings = []
        
        for item in items:
            try:
                bedrooms = item.get("bedrooms", item.get("beds", 0))
                if isinstance(bedrooms, str):
                    try:
                        bedrooms = int(bedrooms)
                    except:
                        bedrooms = 0
                
                area_sqft = float(item.get("area", item.get("size", 0)) or 0)
                price_aed = float(item.get("price", 0) or 0)
                
                location_name = item.get("location", {})
                if isinstance(location_name, dict):
                    location_name = location_name.get("name", "")
                
                listing = Listing(
                    listing_id=str(item.get("id", item.get("property_id", ""))),
                    listing_date=None,
                    source="uae_realtime",
                    
                    community=normalize_location_name(location_name),
                    project=item.get("project"),
                    building=item.get("building"),
                    
                    property_type=self._normalize_property_type(item.get("property_type")),
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
                listings.append(listing)
                
            except Exception as e:
                logger.warning(f"Erreur parsing UAE RealTime : {e}")
                continue
        
        return listings
    
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
    
    # ============================================================
    # TRANSACTIONS
    # ============================================================
    
    def get_transactions(
        self,
        location: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 0,
        hits_per_page: int = 20
    ) -> List[Dict]:
        """
        Récupérer les transactions immobilières
        
        Args:
            location: Zone géographique
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            page: Page de résultats
            hits_per_page: Résultats par page
            
        Returns:
            Liste des transactions
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/transactions"
            headers = self._get_headers()
            params = {
                "page": page,
                "hits_per_page": hits_per_page
            }
            
            if location:
                params["location"] = location
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            logger.info(f"UAE RealTime transactions : {location or 'all'}, page {page}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data.get("data", data.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur transactions UAE RealTime : {e}")
            return []

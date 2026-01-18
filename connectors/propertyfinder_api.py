"""
Connecteur PropertyFinder API via RapidAPI

PropertyFinder est l'un des plus grands portails immobiliers des UAE.
Accès via RapidAPI : uae-real-estate-api-propertyfinder-ae-data

Documentation : https://rapidapi.com/market-data-point1-market-data-point-default/api/uae-real-estate-api-propertyfinder-ae-data
"""
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal
import httpx
from loguru import logger
from core.config import settings
from core.models import Listing
from core.utils import normalize_location_name, normalize_rooms_bucket, calculate_price_per_sqft


class PropertyFinderAPIConnector:
    """
    Connecteur pour PropertyFinder via RapidAPI
    
    Données disponibles :
    - 500K+ listings UAE
    - Ventes et locations
    - Agents et agences
    - Détails propriétés
    """
    
    RAPIDAPI_HOST = "uae-real-estate-api-propertyfinder-ae-data.p.rapidapi.com"
    RAPIDAPI_BASE_URL = "https://uae-real-estate-api-propertyfinder-ae-data.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = settings.propertyfinder_api_key
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
    # PROPERTIES ENDPOINTS
    # ============================================================
    
    def search_properties(
        self,
        location_name: Optional[str] = None,
        property_type: Optional[str] = None,
        listing_category: str = "Buy",
        price_from: Optional[float] = None,
        price_to: Optional[float] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[int] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict:
        """
        Rechercher des propriétés sur PropertyFinder
        
        Args:
            location_name: Nom de la zone (ex: "Dubai Marina")
            property_type: Type (Apartment, Villa, Townhouse, Penthouse)
            listing_category: "Buy" ou "Rent"
            price_from/to: Fourchette de prix AED
            bedrooms: Nombre de chambres
            bathrooms: Nombre de salles de bain
            page: Page de résultats
            limit: Résultats par page
            
        Returns:
            {
                "data": [...],
                "pagination": {"total": X, "limit": Y, "has_next": bool}
            }
        """
        if not self.api_key:
            logger.warning("PROPERTYFINDER_API_KEY non configurée")
            return {"data": [], "pagination": {}}
        
        try:
            url = f"{self.base_url}/properties"
            headers = self._get_headers()
            
            params = {
                "page": page,
                "limit": limit,
                "listing_category": listing_category
            }
            
            if location_name:
                params["location_name"] = location_name
            if property_type:
                params["property_type"] = property_type
            if price_from:
                params["price_from"] = price_from
            if price_to:
                params["price_to"] = price_to
            if bedrooms:
                params["bedrooms"] = bedrooms
            if bathrooms:
                params["bathrooms"] = bathrooms
            
            logger.info(f"PropertyFinder search : {location_name or 'all'}, page {page}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = data.get("data", [])
            logger.info(f"{len(results)} propriétés PropertyFinder trouvées")
            return data
            
        except Exception as e:
            logger.error(f"Erreur PropertyFinder search : {e}")
            return {"data": [], "pagination": {}}
    
    def fetch_listings(
        self,
        location_name: Optional[str] = None,
        property_type: Optional[str] = None,
        purpose: str = "sale",
        max_pages: int = 5
    ) -> List[Listing]:
        """
        Récupérer les annonces et les convertir en modèle Listing
        
        Args:
            location_name: Zone à rechercher
            property_type: Type de propriété
            purpose: "sale" ou "rent"
            max_pages: Nombre max de pages à récupérer
            
        Returns:
            Liste de Listing
        """
        all_listings = []
        listing_category = "Buy" if purpose == "sale" else "Rent"
        
        for page in range(1, max_pages + 1):
            result = self.search_properties(
                location_name=location_name,
                property_type=property_type,
                listing_category=listing_category,
                page=page
            )
            
            items = result.get("data", [])
            if not items:
                break
            
            listings = self._parse_properties(items)
            all_listings.extend(listings)
            
            pagination = result.get("pagination", {})
            if not pagination.get("has_next", False):
                break
        
        logger.info(f"{len(all_listings)} listings PropertyFinder au total")
        return all_listings
    
    def _parse_properties(self, items: List[Dict]) -> List[Listing]:
        """Convertir les propriétés PropertyFinder en Listing"""
        listings = []
        
        for item in items:
            try:
                # Extraction des données
                bedrooms = None
                beds_str = item.get("bedrooms", "")
                if beds_str:
                    try:
                        bedrooms = int(beds_str)
                    except:
                        pass
                
                area_sqft = float(item.get("size", 0) or 0)
                price_aed = float(item.get("price", "0").replace(",", "") or 0)
                
                # Location
                location = item.get("location", {})
                location_name = location.get("name") if isinstance(location, dict) else None
                
                # Agent
                agent = item.get("agent", {})
                
                listing = Listing(
                    listing_id=str(item.get("property_id", "")),
                    listing_date=None,  # Non disponible
                    source="propertyfinder",
                    
                    community=normalize_location_name(location_name),
                    project=None,
                    building=None,
                    
                    property_type=self._normalize_property_type(item.get("property_type")),
                    rooms_count=bedrooms,
                    rooms_bucket=normalize_rooms_bucket(bedrooms) if bedrooms is not None else None,
                    area_sqft=Decimal(str(area_sqft)) if area_sqft > 0 else None,
                    
                    asking_price_aed=Decimal(str(price_aed)) if price_aed > 0 else None,
                    asking_price_per_sqft=calculate_price_per_sqft(price_aed, area_sqft),
                    original_price_aed=None,
                    
                    price_changes=0,
                    last_price_change_date=None,
                    days_on_market=0,
                    
                    status="active",
                    url=None
                )
                listings.append(listing)
                
            except Exception as e:
                logger.warning(f"Erreur parsing PropertyFinder {item.get('property_id', 'N/A')} : {e}")
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
    # AGENT ENDPOINTS
    # ============================================================
    
    def get_agent_info(self, property_data: Dict) -> Optional[Dict]:
        """
        Extraire les infos agent depuis une propriété
        
        Returns:
            {
                "agent_id": str,
                "name": str,
                "is_super_agent": bool
            }
        """
        agent = property_data.get("agent", {})
        if not agent:
            return None
        
        return {
            "agent_id": agent.get("agent_id"),
            "name": agent.get("name"),
            "is_super_agent": agent.get("is_super_agent", False)
        }

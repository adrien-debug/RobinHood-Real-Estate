"""
Connecteur Listings - Annonces autorisées UNIQUEMENT
"""
from typing import List, Optional
from datetime import date, timedelta
import httpx
from loguru import logger
from core.config import settings


class ListingsConnector:
    """
    Connecteur pour les annonces immobilières
    
    ⚠️ IMPORTANT : Utiliser UNIQUEMENT des APIs autorisées
    AUCUN scraping non autorisé
    """
    
    def __init__(self):
        self.api_key = settings.listings_api_key
        self.api_url = settings.listings_api_url
        self.timeout = 30.0
    
    def fetch_listings(
        self, 
        community: Optional[str] = None,
        status: str = "active"
    ) -> List[Dict]:
        """Récupérer les annonces actives"""
        if not self.api_key or not self.api_url:
            logger.warning("LISTINGS_API non configurée - mode simulation")
            return self._generate_mock_data()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "status": status
            }
            if community:
                params["community"] = community
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(self.api_url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            listings = self._parse_response(data)
            logger.info(f"Listings récupérées : {len(listings)}")
            return listings
        
        except Exception as e:
            logger.error(f"Erreur listings API : {e}")
            return []
    
    def _parse_response(self, data: dict) -> List[Dict]:
        """Parser la réponse API"""
        listings = []
        items = data.get("listings", []) or data.get("data", [])
        
        for item in items:
            try:
                listing = {
                    "listing_id": str(item.get("id")),
                    "listing_date": item.get("listed_date"),
                    "community": item.get("community"),
                    "project": item.get("project"),
                    "building": item.get("building"),
                    "property_type": item.get("property_type"),
                    "rooms_bucket": item.get("rooms_bucket"),
                    "area_sqft": item.get("area"),
                    "asking_price_aed": item.get("price"),
                    "asking_price_per_sqft": item.get("price_per_sqft"),
                    "original_price_aed": item.get("original_price"),
                    "price_changes": item.get("price_changes", 0),
                    "last_price_change_date": item.get("last_price_change"),
                    "days_on_market": item.get("days_on_market", 0),
                    "status": item.get("status", "active")
                }
                listings.append(listing)
            except Exception as e:
                logger.warning(f"Erreur parsing listing : {e}")
                continue
        
        return listings
    
    def _generate_mock_data(self) -> List[Dict]:
        """Données mock"""
        from decimal import Decimal
        import random
        
        communities = ["Dubai Marina", "Downtown Dubai", "Palm Jumeirah", "Business Bay"]
        property_types = ["apartment", "villa"]
        rooms_buckets = ["studio", "1BR", "2BR", "3BR+"]
        
        listings = []
        for i in range(30):
            area = Decimal(random.randint(500, 2500))
            price = area * Decimal(random.randint(1300, 2800))
            original_price = price * Decimal(random.uniform(1.0, 1.15))
            
            listing = {
                "listing_id": f"LIST-MOCK-{i:04d}",
                "listing_date": date.today() - timedelta(days=random.randint(1, 90)),
                "community": random.choice(communities),
                "project": f"Project {random.randint(1, 10)}",
                "building": f"Building {random.randint(1, 20)}",
                "property_type": random.choice(property_types),
                "rooms_bucket": random.choice(rooms_buckets),
                "area_sqft": area,
                "asking_price_aed": price,
                "asking_price_per_sqft": price / area,
                "original_price_aed": original_price,
                "price_changes": random.randint(0, 3),
                "last_price_change_date": date.today() - timedelta(days=random.randint(1, 30)) if random.random() > 0.5 else None,
                "days_on_market": random.randint(1, 120),
                "status": "active"
            }
            listings.append(listing)
        
        logger.info(f"Données MOCK listings : {len(listings)}")
        return listings

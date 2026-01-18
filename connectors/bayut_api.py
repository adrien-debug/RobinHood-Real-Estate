"""
Connecteur Bayut API - Lead indicators (annonces live)

Bayut est l'un des plus grands portails immobiliers de Dubaï.
L'API officielle nécessite un partenariat commercial.

⚠️ IMPORTANT : Utiliser UNIQUEMENT l'API officielle Bayut
AUCUN scraping non autorisé
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
    Connecteur pour l'API Bayut
    
    Documentation : https://www.bayut.com/api-docs (nécessite partenariat)
    
    Lead indicators :
    - Nouvelles annonces (offre fraîche)
    - Baisses de prix (signaux de pression)
    - Jours sur marché (liquidité)
    - Ratio annonces/transactions (sur-offre)
    """
    
    def __init__(self):
        self.api_key = settings.bayut_api_key
        self.base_url = settings.bayut_api_url or "https://api.bayut.com/v1"
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


    def _fetch_real_data(
        self,
        community: Optional[str],
        property_type: Optional[str],
        status: str,
        days_back: int
    ) -> List[Listing]:
        """Récupération des vraies données API"""

        try:
            url = f"{self.base_url}/properties"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Paramètres de requête
            params = {
                "status": status,
                "purpose": "for-sale",  # Ventes uniquement
                "limit": 1000
            }

            if community:
                params["location"] = community

            if property_type:
                params["property_type"] = property_type

            # Filtrer par date de publication
            if days_back:
                from_date = (date.today() - timedelta(days=days_back)).isoformat()
                params["listed_after"] = from_date

            logger.info(f"Recuperation annonces Bayut : {community or 'toutes zones'}")

            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

            listings = self._parse_response(data)
            logger.info(f"{len(listings)} annonces Bayut recuperees")
            return listings

        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP Bayut API : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Reponse : {e.response.text[:500]}")
            logger.warning("Fallback sur donnees MOCK")
            return self._generate_mock_data(community, property_type, days_back)
        except Exception as e:
            logger.error(f"Erreur Bayut API : {e}")
            logger.warning("Fallback sur donnees MOCK")
            return self._generate_mock_data(community, property_type, days_back)
    
    def _parse_response(self, data: dict) -> List[Listing]:
        """
        Parser la réponse API Bayut
        
        Format attendu :
        {
            "properties": [
                {
                    "id": "12345",
                    "listed_date": "2026-01-10",
                    "location": {
                        "community": "Dubai Marina",
                        "project": "Marina Heights",
                        "building": "Tower A"
                    },
                    "property_type": "apartment",
                    "bedrooms": 2,
                    "area": 1200,
                    "price": 1800000,
                    "price_per_sqft": 1500,
                    "original_price": 1950000,
                    "price_changes": 2,
                    "last_price_change": "2026-01-15",
                    "days_on_market": 45,
                    "status": "active"
                }
            ]
        }
        """
        listings = []
        
        items = data.get("properties", []) or data.get("data", [])
        
        if not items:
            logger.warning("Aucune annonce dans la réponse Bayut API")
            return listings
        
        for item in items:
            try:
                location = item.get("location", {})
                
                # Extraction des données
                bedrooms = item.get("bedrooms", 0)
                area_sqft = float(item.get("area", 0) or 0)
                price_aed = float(item.get("price", 0) or 0)
                original_price = float(item.get("original_price", price_aed) or price_aed)
                
                listing = Listing(
                    listing_id=str(item.get("id", "")),
                    listing_date=self._parse_date(item.get("listed_date")),
                    source="bayut",
                    
                    community=normalize_location_name(location.get("community")),
                    project=normalize_location_name(location.get("project")),
                    building=normalize_location_name(location.get("building")),
                    
                    property_type=self._normalize_property_type(item.get("property_type")),
                    rooms_count=bedrooms,
                    rooms_bucket=normalize_rooms_bucket(bedrooms),
                    area_sqft=Decimal(str(area_sqft)) if area_sqft > 0 else None,
                    
                    asking_price_aed=Decimal(str(price_aed)) if price_aed > 0 else None,
                    asking_price_per_sqft=calculate_price_per_sqft(price_aed, area_sqft),
                    original_price_aed=Decimal(str(original_price)) if original_price > 0 else None,
                    
                    price_changes=item.get("price_changes", 0),
                    last_price_change_date=self._parse_date(item.get("last_price_change")),
                    days_on_market=item.get("days_on_market", 0),
                    
                    status=item.get("status", "active"),
                    url=item.get("url")
                )
                listings.append(listing)
                
            except Exception as e:
                logger.warning(f"⚠️  Erreur parsing annonce Bayut {item.get('id', 'N/A')} : {e}")
                continue
        
        return listings
    
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

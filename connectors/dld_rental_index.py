"""
Connecteur DLD - Index locatif via Dubai Pulse API

L'index locatif DLD est publié mensuellement et fournit des données
sur les loyers moyens par zone, type de propriété et nombre de chambres.

Essentiel pour :
- Calcul de rendement locatif
- Stratégie RENT
- Détection de pression locative
"""
from typing import List, Optional
from datetime import date, timedelta
import httpx
from loguru import logger
from core.config import settings
from core.models import RentalIndex
from core.utils import normalize_location_name
from connectors.dubai_pulse_auth import get_dubai_pulse_auth


class DLDRentalIndexConnector:
    """
    Connecteur pour l'index locatif DLD via Dubai Pulse
    
    API utilisée : dld_rental_index-open-api
    Documentation : https://www.dubaipulse.gov.ae/data/dld-rental-index
    """
    
    def __init__(self):
        self.auth = get_dubai_pulse_auth()
        self.base_url = "https://api.dubaipulse.gov.ae/open/dld"
        self.endpoint = "dld_rental_index-open-api"
        self.timeout = 60.0
    
    def fetch_rental_index(
        self, 
        period_date: Optional[date] = None
    ) -> List[RentalIndex]:
        """
        Récupérer l'index locatif DLD via Dubai Pulse API
        
        Args:
            period_date: Date de la période (défaut: premier jour du mois en cours)
            
        Returns:
            Liste d'index locatifs par zone/type/chambres
        """
        # Vérifier si les clés API sont configurées
        try:
            self.auth.get_access_token()
        except ValueError:
            logger.warning("⚠️  Clés API DLD non configurées - utilisation de données MOCK")
            logger.warning("Pour connecter l'API réelle, configure DLD_API_KEY et DLD_API_SECRET")
            return self._generate_mock_data(period_date)
        
        if not period_date:
            period_date = date.today().replace(day=1)  # Premier du mois
        
        try:
            url = f"{self.base_url}/{self.endpoint}"
            headers = self.auth.get_auth_headers()
            
            # Paramètres de requête selon la doc Dubai Pulse
            # Note: L'API peut nécessiter un format spécifique pour la période
            params = {
                "$filter": f"period_date eq '{period_date.isoformat()}'",
                "$top": 10000,
                "$orderby": "community asc"
            }
            
            logger.info(f"🔄 Récupération index locatif DLD : {period_date}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            rental_data = self._parse_response(data, period_date)
            logger.info(f"✅ {len(rental_data)} entrées d'index locatif récupérées")
            return rental_data
        
        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP DLD rental index : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Réponse : {e.response.text[:500]}")
            logger.warning("Fallback sur données MOCK")
            return self._generate_mock_data(period_date)
        except Exception as e:
            logger.error(f"❌ Erreur DLD rental index : {e}")
            logger.warning("Fallback sur données MOCK")
            return self._generate_mock_data(period_date)
    
    def _parse_response(self, data: dict, period_date: date) -> List[RentalIndex]:
        """
        Parser la réponse API Dubai Pulse
        
        Format attendu selon la doc DLD :
        {
            "value": [
                {
                    "period_date": "2026-01-01",
                    "area_name_en": "Dubai Marina",
                    "property_type_en": "Flat",
                    "rooms_en": "2 B/R",
                    "avg_annual_rent": "95000",
                    "median_annual_rent": "92000",
                    "contracts_count": "450"
                }
            ]
        }
        """
        rental_data = []
        
        # Dubai Pulse utilise "value" pour la liste des résultats
        items = data.get("value", []) or data.get("rental_index", []) or data.get("data", [])
        
        if not items:
            logger.warning("Aucune donnée d'index locatif dans la réponse API")
            return rental_data
        
        for item in items:
            try:
                # Extraction et normalisation des champs DLD
                rooms_str = item.get("rooms_en", "")
                rooms_bucket = self._normalize_rooms_bucket(rooms_str)
                
                rental = RentalIndex(
                    period_date=period_date,
                    
                    community=normalize_location_name(item.get("area_name_en") or item.get("community")),
                    project=normalize_location_name(item.get("project_en") or item.get("project")),
                    property_type=self._normalize_property_type(item.get("property_type_en") or item.get("property_type")),
                    rooms_bucket=rooms_bucket,
                    
                    avg_rent_aed=float(item.get("avg_annual_rent", 0) or item.get("avg_rent", 0) or 0) or None,
                    median_rent_aed=float(item.get("median_annual_rent", 0) or item.get("median_rent", 0) or 0) or None,
                    rent_count=int(item.get("contracts_count", 0) or item.get("count", 0) or 0) or None
                )
                rental_data.append(rental)
                
            except Exception as e:
                logger.warning(f"⚠️  Erreur parsing rental index : {e}")
                continue
        
        return rental_data
    
    def _normalize_rooms_bucket(self, rooms_str: str) -> Optional[str]:
        """Normaliser le bucket de chambres depuis le format DLD"""
        if not rooms_str:
            return None
        
        rooms_lower = rooms_str.lower()
        
        if "studio" in rooms_lower:
            return "studio"
        elif "1" in rooms_str and "b/r" in rooms_lower:
            return "1BR"
        elif "2" in rooms_str and "b/r" in rooms_lower:
            return "2BR"
        elif "3" in rooms_str or "4" in rooms_str or "5" in rooms_str:
            return "3BR+"
        
        return None
    
    def _normalize_property_type(self, prop_type: str) -> str:
        """Normaliser le type de propriété"""
        if not prop_type:
            return "apartment"
        
        prop_lower = prop_type.lower()
        if "flat" in prop_lower or "apartment" in prop_lower:
            return "apartment"
        elif "villa" in prop_lower:
            return "villa"
        elif "townhouse" in prop_lower or "town house" in prop_lower:
            return "townhouse"
        else:
            return "other"
    
    def _generate_mock_data(self, period_date: Optional[date]) -> List[RentalIndex]:
        """Données mock"""
        from decimal import Decimal
        import random
        
        if not period_date:
            period_date = date.today().replace(day=1)
        
        communities = ["Dubai Marina", "Downtown Dubai", "Palm Jumeirah", "Business Bay"]
        property_types = ["apartment", "villa"]
        rooms_buckets = ["studio", "1BR", "2BR", "3BR+"]
        
        rental_data = []
        for community in communities:
            for rooms in rooms_buckets:
                rental = RentalIndex(
                    period_date=period_date,
                    
                    community=community,
                    property_type="apartment",
                    rooms_bucket=rooms,
                    
                    avg_rent_aed=Decimal(random.randint(40_000, 150_000)),
                    median_rent_aed=Decimal(random.randint(40_000, 150_000)),
                    rent_count=random.randint(10, 100)
                )
                rental_data.append(rental)
        
        logger.info(f"Données MOCK rental index : {len(rental_data)}")
        return rental_data

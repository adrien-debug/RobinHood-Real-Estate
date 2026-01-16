"""
Connecteur DLD - Index locatif
"""
from typing import List, Optional
from datetime import date, timedelta
import httpx
from loguru import logger
from core.config import settings
from core.models import RentalIndex
from core.utils import normalize_location_name


class DLDRentalIndexConnector:
    """Connecteur pour l'index locatif DLD"""
    
    def __init__(self):
        self.api_key = settings.dld_api_key
        self.base_url = settings.dld_api_base_url
        self.timeout = 30.0
    
    def fetch_rental_index(
        self, 
        period_date: Optional[date] = None
    ) -> List[RentalIndex]:
        """Récupérer l'index locatif (généralement mensuel)"""
        if not self.api_key:
            logger.warning("DLD_API_KEY non configurée - mode simulation")
            return self._generate_mock_data(period_date)
        
        if not period_date:
            period_date = date.today().replace(day=1)  # Premier du mois
        
        try:
            url = f"{self.base_url}/rental-index"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "period": period_date.isoformat()
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            rental_data = self._parse_response(data, period_date)
            logger.info(f"DLD rental index récupéré : {len(rental_data)} entrées")
            return rental_data
        
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP DLD rental index : {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur DLD rental index : {e}")
            raise
    
    def _parse_response(self, data: dict, period_date: date) -> List[RentalIndex]:
        """Parser la réponse API"""
        rental_data = []
        items = data.get("rental_index", []) or data.get("data", [])
        
        for item in items:
            try:
                rental = RentalIndex(
                    period_date=period_date,
                    
                    community=normalize_location_name(item.get("community")),
                    project=normalize_location_name(item.get("project")),
                    property_type=item.get("property_type"),
                    rooms_bucket=item.get("rooms_bucket"),
                    
                    avg_rent_aed=item.get("avg_rent"),
                    median_rent_aed=item.get("median_rent"),
                    rent_count=item.get("count")
                )
                rental_data.append(rental)
            except Exception as e:
                logger.warning(f"Erreur parsing rental index : {e}")
                continue
        
        return rental_data
    
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

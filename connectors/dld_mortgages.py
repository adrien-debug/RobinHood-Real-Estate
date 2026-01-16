"""
Connecteur DLD - Hypothèques
"""
from typing import List, Optional
from datetime import date, timedelta
import httpx
from loguru import logger
from core.config import settings
from core.models import Mortgage
from core.utils import normalize_location_name


class DLDMortgagesConnector:
    """Connecteur pour les hypothèques DLD"""
    
    def __init__(self):
        self.api_key = settings.dld_api_key
        self.base_url = settings.dld_api_base_url
        self.timeout = 30.0
    
    def fetch_mortgages(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Mortgage]:
        """Récupérer les hypothèques DLD"""
        if not self.api_key:
            logger.warning("DLD_API_KEY non configurée - mode simulation")
            return self._generate_mock_data(start_date, end_date)
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=1)
        
        try:
            url = f"{self.base_url}/mortgages"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            mortgages = self._parse_response(data)
            logger.info(f"DLD mortgages récupérées : {len(mortgages)}")
            return mortgages
        
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP DLD mortgages : {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur DLD mortgages : {e}")
            raise
    
    def _parse_response(self, data: dict) -> List[Mortgage]:
        """Parser la réponse API"""
        mortgages = []
        items = data.get("mortgages", []) or data.get("data", [])
        
        for item in items:
            try:
                mortgage = Mortgage(
                    mortgage_id=str(item.get("mortgage_id") or item.get("id")),
                    mortgage_date=item.get("mortgage_date"),
                    
                    community=normalize_location_name(item.get("community")),
                    project=normalize_location_name(item.get("project")),
                    building=normalize_location_name(item.get("building")),
                    
                    mortgage_amount_aed=item.get("amount"),
                    lender=item.get("lender"),
                    borrower=item.get("borrower")
                )
                mortgages.append(mortgage)
            except Exception as e:
                logger.warning(f"Erreur parsing mortgage : {e}")
                continue
        
        return mortgages
    
    def _generate_mock_data(self, start_date: Optional[date], end_date: Optional[date]) -> List[Mortgage]:
        """Données mock"""
        from decimal import Decimal
        import random
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=1)
        
        communities = ["Dubai Marina", "Downtown Dubai", "Palm Jumeirah"]
        lenders = ["Emirates NBD", "Dubai Islamic Bank", "ADCB", "Mashreq"]
        
        mortgages = []
        for i in range(20):
            mortgage = Mortgage(
                mortgage_id=f"MORT-MOCK-{start_date}-{i:04d}",
                mortgage_date=start_date,
                
                community=random.choice(communities),
                project=f"Project {random.randint(1, 10)}",
                building=f"Building {random.randint(1, 20)}",
                
                mortgage_amount_aed=Decimal(random.randint(500_000, 3_000_000)),
                lender=random.choice(lenders),
                borrower=f"Borrower {i}"
            )
            mortgages.append(mortgage)
        
        logger.info(f"Données MOCK mortgages : {len(mortgages)}")
        return mortgages

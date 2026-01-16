"""
Connecteur DLD - Transactions immobilières
"""
from typing import List, Optional
from datetime import date, timedelta
import httpx
from loguru import logger
from core.config import settings
from core.models import Transaction
from core.utils import normalize_rooms_bucket, calculate_price_per_sqft, normalize_location_name


class DLDTransactionsConnector:
    """Connecteur pour les transactions DLD"""
    
    def __init__(self):
        self.api_key = settings.dld_api_key
        self.base_url = settings.dld_api_base_url
        self.timeout = 30.0
    
    def fetch_transactions(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Transaction]:
        """
        Récupérer les transactions DLD
        
        NOTE : Cette implémentation est un TEMPLATE.
        L'API réelle DLD nécessite :
        - Authentification spécifique
        - Endpoints exacts
        - Format de réponse exact
        
        À adapter selon la documentation officielle DLD.
        """
        if not self.api_key:
            logger.warning("DLD_API_KEY non configurée - mode simulation")
            return self._generate_mock_data(start_date, end_date)
        
        # Dates par défaut : dernières 24h
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=1)
        
        try:
            url = f"{self.base_url}/transactions"
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
            
            transactions = self._parse_response(data)
            logger.info(f"DLD transactions récupérées : {len(transactions)} ({start_date} → {end_date})")
            return transactions
        
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP DLD transactions : {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur DLD transactions : {e}")
            raise
    
    def _parse_response(self, data: dict) -> List[Transaction]:
        """Parser la réponse API DLD"""
        transactions = []
        
        # À adapter selon le format réel de l'API DLD
        items = data.get("transactions", []) or data.get("data", [])
        
        for item in items:
            try:
                # Normalisation
                rooms_count = item.get("rooms") or item.get("bedrooms")
                area_sqft = item.get("area_sqft") or item.get("area")
                price_aed = item.get("amount") or item.get("price")
                
                transaction = Transaction(
                    transaction_id=str(item.get("transaction_id") or item.get("id")),
                    transaction_date=item.get("transaction_date"),
                    transaction_type=item.get("transaction_type", "sale"),
                    
                    community=normalize_location_name(item.get("community")),
                    project=normalize_location_name(item.get("project")),
                    building=normalize_location_name(item.get("building")),
                    unit_number=item.get("unit_number"),
                    
                    property_type=item.get("property_type"),
                    property_subtype=item.get("property_subtype"),
                    rooms_count=rooms_count,
                    rooms_bucket=normalize_rooms_bucket(rooms_count),
                    area_sqft=area_sqft,
                    
                    price_aed=price_aed,
                    price_per_sqft=calculate_price_per_sqft(price_aed, area_sqft),
                    
                    buyer_name=item.get("buyer"),
                    seller_name=item.get("seller"),
                    is_offplan=item.get("is_offplan", False)
                )
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"Erreur parsing transaction : {e}")
                continue
        
        return transactions
    
    def _generate_mock_data(self, start_date: Optional[date], end_date: Optional[date]) -> List[Transaction]:
        """Générer des données mock pour développement"""
        from decimal import Decimal
        import random
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=1)
        
        communities = ["Dubai Marina", "Downtown Dubai", "Palm Jumeirah", "Business Bay", "JBR"]
        projects = ["Marina Heights", "Burj Khalifa Residences", "Golden Mile", "Executive Towers"]
        property_types = ["apartment", "villa", "townhouse"]
        
        transactions = []
        for i in range(50):
            rooms = random.choice([0, 1, 2, 3, 4])
            area = Decimal(random.randint(500, 3000))
            price = area * Decimal(random.randint(1200, 2500))
            
            transaction = Transaction(
                transaction_id=f"MOCK-{start_date}-{i:04d}",
                transaction_date=start_date,
                transaction_type="sale",
                
                community=random.choice(communities),
                project=random.choice(projects),
                building=f"Building {random.randint(1, 20)}",
                unit_number=f"{random.randint(1, 50)}{random.randint(1, 9)}",
                
                property_type=random.choice(property_types),
                rooms_count=rooms,
                rooms_bucket=normalize_rooms_bucket(rooms),
                area_sqft=area,
                
                price_aed=price,
                price_per_sqft=calculate_price_per_sqft(price, area),
                
                is_offplan=random.choice([True, False])
            )
            transactions.append(transaction)
        
        logger.info(f"Données MOCK générées : {len(transactions)} transactions")
        return transactions

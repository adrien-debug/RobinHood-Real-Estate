"""
Connecteur DLD - Transactions immobilières via Dubai Pulse API
"""
from typing import List, Optional
from datetime import date, timedelta
import httpx
from loguru import logger
from core.config import settings
from core.models import Transaction
from core.utils import normalize_rooms_bucket, calculate_price_per_sqft, normalize_location_name
from connectors.dubai_pulse_auth import get_dubai_pulse_auth


class DLDTransactionsConnector:
    """
    Connecteur pour les transactions DLD via Dubai Pulse
    
    API utilisée : dld_transactions-open-api
    Documentation : https://www.dubaipulse.gov.ae/data/dld-transactions/dld_transactions-open-api
    """
    
    def __init__(self):
        self.auth = get_dubai_pulse_auth()
        self.base_url = "https://api.dubaipulse.gov.ae/open/dld"
        self.endpoint = "dld_transactions-open-api"
        self.timeout = 60.0
    
    def fetch_transactions(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None,
        limit: int = 10000
    ) -> List[Transaction]:
        """
        Récupérer les transactions DLD via Dubai Pulse API
        
        Args:
            start_date: Date de début (défaut: hier)
            end_date: Date de fin (défaut: aujourd'hui)
            limit: Nombre max de résultats (défaut: 10000)
            
        Returns:
            Liste de transactions
        """
        # Vérifier si les clés API sont configurées
        try:
            self.auth.get_access_token()
        except ValueError:
            logger.warning("⚠️  Clés API DLD non configurées - utilisation de données MOCK")
            logger.warning("Pour connecter l'API réelle, configure DLD_API_KEY et DLD_API_SECRET")
            return self._generate_mock_data(start_date, end_date)
        
        # Dates par défaut : dernières 24h
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=1)
        
        try:
            url = f"{self.base_url}/{self.endpoint}"
            headers = self.auth.get_auth_headers()
            
            # Paramètres de requête selon la doc Dubai Pulse
            params = {
                "$filter": f"trans_date ge '{start_date.isoformat()}' and trans_date le '{end_date.isoformat()}'",
                "$top": limit,
                "$orderby": "trans_date desc"
            }
            
            logger.info(f"🔄 Récupération transactions DLD : {start_date} → {end_date}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            transactions = self._parse_response(data)
            logger.info(f"✅ {len(transactions)} transactions DLD récupérées")
            return transactions
        
        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP DLD API : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Réponse : {e.response.text[:500]}")
            # Fallback sur données mock en cas d'erreur
            logger.warning("Fallback sur données MOCK")
            return self._generate_mock_data(start_date, end_date)
        except Exception as e:
            logger.error(f"❌ Erreur DLD transactions : {e}")
            logger.warning("Fallback sur données MOCK")
            return self._generate_mock_data(start_date, end_date)
    
    def _parse_response(self, data: dict) -> List[Transaction]:
        """
        Parser la réponse API Dubai Pulse
        
        Format attendu selon la doc DLD :
        {
            "value": [
                {
                    "instance_id": "...",
                    "trans_date": "2026-01-17",
                    "trans_group_en": "Sales",
                    "procedure_en": "...",
                    "property_type_en": "Unit",
                    "property_sub_type_en": "Flat",
                    "reg_type_en": "...",
                    "area_name_en": "Dubai Marina",
                    "project_en": "Marina Heights",
                    "building_name_en": "Tower A",
                    "rooms_en": "2 B/R",
                    "actual_area": "1200.50",
                    "trans_value": "1500000",
                    ...
                }
            ]
        }
        """
        transactions = []
        
        # Dubai Pulse utilise "value" pour la liste des résultats
        items = data.get("value", [])
        
        if not items:
            logger.warning("Aucune transaction dans la réponse API")
            return transactions
        
        for item in items:
            try:
                # Extraction et normalisation des champs DLD
                rooms_str = item.get("rooms_en", "")
                rooms_count = self._extract_rooms_count(rooms_str)
                
                area_sqft = float(item.get("actual_area", 0) or 0)
                price_aed = float(item.get("trans_value", 0) or 0)
                
                # Créer la transaction
                transaction = Transaction(
                    transaction_id=str(item.get("instance_id", "")),
                    transaction_date=item.get("trans_date"),
                    transaction_type=self._normalize_transaction_type(item.get("trans_group_en", "")),
                    
                    community=normalize_location_name(item.get("area_name_en")),
                    project=normalize_location_name(item.get("project_en")),
                    building=normalize_location_name(item.get("building_name_en")),
                    unit_number=item.get("property_number"),
                    
                    property_type=self._normalize_property_type(item.get("property_type_en")),
                    property_subtype=item.get("property_sub_type_en"),
                    rooms_count=rooms_count,
                    rooms_bucket=normalize_rooms_bucket(rooms_count),
                    area_sqft=area_sqft if area_sqft > 0 else None,
                    
                    price_aed=price_aed if price_aed > 0 else None,
                    price_per_sqft=calculate_price_per_sqft(price_aed, area_sqft),
                    
                    buyer_name=None,  # Non disponible dans l'API publique
                    seller_name=None,  # Non disponible dans l'API publique
                    is_offplan=item.get("is_offplan_en") == "Yes"
                )
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"⚠️  Erreur parsing transaction {item.get('instance_id', 'N/A')} : {e}")
                continue
        
        return transactions
    
    def _extract_rooms_count(self, rooms_str: str) -> Optional[int]:
        """Extraire le nombre de chambres depuis le format DLD (ex: '2 B/R')"""
        if not rooms_str:
            return None
        
        # Format DLD : "Studio", "1 B/R", "2 B/R", etc.
        if "studio" in rooms_str.lower():
            return 0
        
        # Extraire le chiffre
        import re
        match = re.search(r'(\d+)', rooms_str)
        if match:
            return int(match.group(1))
        
        return None
    
    def _normalize_transaction_type(self, trans_group: str) -> str:
        """Normaliser le type de transaction"""
        if not trans_group:
            return "sale"
        
        trans_lower = trans_group.lower()
        if "sale" in trans_lower or "sales" in trans_lower:
            return "sale"
        elif "mortgage" in trans_lower:
            return "mortgage"
        elif "gift" in trans_lower:
            return "gift"
        else:
            return "other"
    
    def _normalize_property_type(self, prop_type: str) -> str:
        """Normaliser le type de propriété"""
        if not prop_type:
            return "apartment"
        
        prop_lower = prop_type.lower()
        if "unit" in prop_lower or "flat" in prop_lower:
            return "apartment"
        elif "villa" in prop_lower:
            return "villa"
        elif "townhouse" in prop_lower or "town house" in prop_lower:
            return "townhouse"
        elif "land" in prop_lower or "plot" in prop_lower:
            return "land"
        else:
            return "other"
    
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

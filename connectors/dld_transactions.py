"""
Connecteur DLD - Transactions immobilières

Sources de données :
1. Dubai Pulse API (officiel DLD) - nécessite authentification
2. Bayut RapidAPI (transactions DLD) - disponible immédiatement

Documentation Bayut : https://docs.bayutapi.com/
"""
from typing import List, Optional
from datetime import date, timedelta
from decimal import Decimal
import httpx
from loguru import logger
from core.config import settings
from core.models import Transaction
from core.utils import normalize_rooms_bucket, calculate_price_per_sqft, normalize_location_name
from connectors.dubai_pulse_auth import get_dubai_pulse_auth


class DLDTransactionsConnector:
    """
    Connecteur pour les transactions DLD
    
    Sources :
    1. Bayut RapidAPI /transactions (prioritaire si clé configurée)
    2. Dubai Pulse API dld_transactions-open-api (fallback)
    
    Documentation Bayut : https://docs.bayutapi.com/
    """
    
    # Bayut RapidAPI
    RAPIDAPI_HOST = "uae-real-estate2.p.rapidapi.com"
    RAPIDAPI_BASE_URL = "https://uae-real-estate2.p.rapidapi.com"
    
    def __init__(self):
        self.auth = get_dubai_pulse_auth()
        self.base_url = "https://api.dubaipulse.gov.ae/open/dld"
        self.endpoint = "dld_transactions-open-api"
        self.timeout = 60.0
        
        # RapidAPI (Bayut)
        self.rapidapi_key = settings.bayut_api_key
    
    def _get_rapidapi_headers(self) -> dict:
        """Headers pour RapidAPI Bayut"""
        return {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": self.RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }
    
    def fetch_transactions(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None,
        limit: int = 10000
    ) -> List[Transaction]:
        """
        Récupérer les transactions DLD
        
        Priorité des sources :
        1. Bayut RapidAPI (si BAYUT_API_KEY configurée)
        2. Dubai Pulse API (si DLD_API_KEY configurée)
        3. Données MOCK (fallback)
        
        Args:
            start_date: Date de début (défaut: 30 jours)
            end_date: Date de fin (défaut: aujourd'hui)
            limit: Nombre max de résultats (défaut: 10000)
            
        Returns:
            Liste de transactions
        """
        # Priorité 1 : Bayut RapidAPI
        if self.rapidapi_key:
            logger.info("Utilisation de Bayut RapidAPI pour les transactions DLD")
            return self._fetch_via_bayut(start_date, end_date)
        
        # Priorité 2 : Dubai Pulse API
        try:
            self.auth.get_access_token()
            logger.info("Utilisation de Dubai Pulse API pour les transactions DLD")
            return self._fetch_via_dubai_pulse(start_date, end_date, limit)
        except ValueError:
            logger.warning("Aucune API configurée - utilisation de données MOCK")
            logger.warning("Configure BAYUT_API_KEY ou DLD_API_KEY pour données réelles")
            return self._generate_mock_data(start_date, end_date)
    
    def _fetch_via_bayut(
        self,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> List[Transaction]:
        """Récupérer les transactions via Bayut RapidAPI"""
        
        # Dates par défaut : 30 derniers jours
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        all_transactions = []
        page = 0
        max_pages = 10  # Limite de sécurité
        
        try:
            while page < max_pages:
                url = f"{self.RAPIDAPI_BASE_URL}/transactions"
                headers = self._get_rapidapi_headers()
                
                body = {
                    "purpose": "for-sale",
                    "category": "residential",
                    "sort_by": "date",
                    "order": "desc",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                
                params = {"page": page}
                
                logger.info(f"Recuperation transactions Bayut : page {page}")
                
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(url, headers=headers, json=body, params=params)
                    response.raise_for_status()
                    data = response.json()
                
                results = data.get("results", [])
                if not results:
                    break
                
                transactions = self._parse_bayut_transactions(results)
                all_transactions.extend(transactions)
                
                # Si moins de 20 résultats, c'est la dernière page
                if len(results) < 20:
                    break
                
                page += 1
            
            logger.info(f"{len(all_transactions)} transactions DLD via Bayut")
            return all_transactions
            
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP Bayut transactions : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Reponse : {e.response.text[:500]}")
            return self._generate_mock_data(start_date, end_date)
        except Exception as e:
            logger.error(f"Erreur Bayut transactions : {e}")
            return self._generate_mock_data(start_date, end_date)
    
    def _parse_bayut_transactions(self, results: list) -> List[Transaction]:
        """Parser les transactions depuis Bayut RapidAPI"""
        transactions = []
        
        for item in results:
            try:
                # Extraction des données Bayut
                property_info = item.get("property", {})
                location_info = item.get("location", {})
                contract_info = item.get("contract", {})
                
                # Chambres
                beds_str = property_info.get("beds", "")
                rooms_count = None
                if beds_str:
                    try:
                        rooms_count = int(beds_str)
                    except:
                        pass
                
                # Surface
                builtup = property_info.get("builtup_area", {})
                area_sqft = float(builtup.get("sqft", 0) or 0)
                
                # Prix
                amount = float(item.get("amount", 0) or 0)
                
                # Date
                tx_date_str = item.get("date")
                tx_date = None
                if tx_date_str:
                    try:
                        tx_date = date.fromisoformat(tx_date_str)
                    except:
                        tx_date = date.today()
                
                # Localisation
                full_location = location_info.get("full_location", "")
                location_parts = full_location.split(" -> ") if full_location else []
                
                community = None
                project = None
                building = None
                
                if len(location_parts) >= 1:
                    community = location_parts[0]
                if len(location_parts) >= 2:
                    project = location_parts[1]
                if len(location_parts) >= 3:
                    building = location_parts[2]
                
                # Si on a le location name direct
                if not community:
                    community = location_info.get("location")
                
                # Type de propriété
                prop_type = property_info.get("type", "apartments")
                
                # Type de transaction
                category = item.get("category", "Sales")
                tx_type = "sale" if "sale" in category.lower() else "rental"
                
                # Statut occupancy
                occupancy = property_info.get("occupancy_status", "")
                is_offplan = "transfer" not in occupancy.lower() if occupancy else False
                
                transaction = Transaction(
                    transaction_id=f"BAY-{tx_date.isoformat() if tx_date else 'UNK'}-{location_info.get('id', '')}",
                    transaction_date=tx_date or date.today(),
                    transaction_type=tx_type,
                    
                    community=normalize_location_name(community),
                    project=normalize_location_name(project),
                    building=normalize_location_name(building),
                    unit_number=property_info.get("floor"),
                    
                    property_type=self._normalize_property_type_bayut(prop_type),
                    rooms_count=rooms_count,
                    rooms_bucket=normalize_rooms_bucket(rooms_count) if rooms_count is not None else None,
                    area_sqft=Decimal(str(area_sqft)) if area_sqft > 0 else None,
                    
                    price_aed=Decimal(str(amount)) if amount > 0 else None,
                    price_per_sqft=calculate_price_per_sqft(amount, area_sqft),
                    
                    is_offplan=is_offplan
                )
                transactions.append(transaction)
                
            except Exception as e:
                logger.warning(f"Erreur parsing transaction Bayut : {e}")
                continue
        
        return transactions
    
    def _normalize_property_type_bayut(self, prop_type: str) -> str:
        """Normaliser le type de propriété depuis Bayut"""
        if not prop_type:
            return "apartment"
        
        prop_lower = prop_type.lower()
        if "apartment" in prop_lower or "flat" in prop_lower:
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
    
    def _fetch_via_dubai_pulse(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        limit: int
    ) -> List[Transaction]:
        """Récupérer les transactions via Dubai Pulse API"""
        
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
            
            logger.info(f"Recuperation transactions DLD Dubai Pulse : {start_date} -> {end_date}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            transactions = self._parse_response(data)
            logger.info(f"{len(transactions)} transactions DLD Dubai Pulse recuperees")
            return transactions
        
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP Dubai Pulse API : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Reponse : {e.response.text[:500]}")
            # Fallback sur données mock en cas d'erreur
            logger.warning("Fallback sur donnees MOCK")
            return self._generate_mock_data(start_date, end_date)
        except Exception as e:
            logger.error(f"Erreur DLD transactions : {e}")
            logger.warning("Fallback sur donnees MOCK")
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
                logger.warning(f"Erreur parsing transaction {item.get('instance_id', 'N/A')} : {e}")
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
        """Générer des données mock réalistes pour développement"""
        from decimal import Decimal
        import random
        from core.dubai_mock_data import get_random_project, ROOM_TYPES
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=1)
        
        transactions = []
        for i in range(50):
            # Obtenir un projet réaliste
            project_data = get_random_project()
            
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
            
            # Type de propriété réaliste pour la zone
            property_type = random.choice(project_data["property_types"])
            
            # Date de transaction variée
            days_offset = random.randint(0, (end_date - start_date).days) if end_date > start_date else 0
            tx_date = start_date + timedelta(days=days_offset)
            
            transaction = Transaction(
                transaction_id=f"DLD-{tx_date.strftime('%Y%m%d')}-{i:04d}",
                transaction_date=tx_date,
                transaction_type=random.choice(["sale", "resale"]),
                
                community=project_data["community"],
                project=project_data["project"],
                building=project_data["building"],
                unit_number=f"{random.randint(1, 50)}{random.randint(0, 9):02d}",
                
                property_type=property_type,
                rooms_count=rooms_count,
                rooms_bucket=rooms_bucket,
                area_sqft=area,
                
                price_aed=price,
                price_per_sqft=price_sqft,
                
                is_offplan=random.random() < 0.25  # 25% offplan
            )
            transactions.append(transaction)
        
        logger.info(f"Données MOCK générées : {len(transactions)} transactions")
        return transactions

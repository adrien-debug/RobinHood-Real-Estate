"""
Connecteur Makani - Système de géocodage officiel de Dubaï

Makani est le système d'adressage unifié de Dubaï.
Chaque bâtiment a un numéro Makani unique (10 chiffres).

Utilité :
- Matching précis entre transactions/annonces/buildings
- Normalisation des adresses
- Scoring de localisation (proximité métro, plage, etc.)
- Géolocalisation exacte (lat/lon)

API : Dubai Municipality / GeoHub
Documentation : https://geohub.dubaipulse.gov.ae
"""
from typing import Optional, Dict, List, Tuple
from decimal import Decimal
import httpx
from loguru import logger
from core.config import settings
from core.models import MakaniAddress
from core.utils import normalize_location_name


class MakaniGeocodingConnector:
    """
    Connecteur pour l'API Makani (Dubai Municipality)
    
    Fonctionnalités :
    - Recherche d'adresse par texte
    - Géocodage (adresse → lat/lon)
    - Reverse geocoding (lat/lon → adresse)
    - Récupération du numéro Makani
    - Métadonnées de localisation
    """
    
    def __init__(self):
        self.api_key = settings.makani_api_key
        self.base_url = settings.makani_api_url or "https://api.dubaipulse.gov.ae/makani"
        self.timeout = 30.0
    
    def search_address(
        self, 
        community: Optional[str] = None,
        project: Optional[str] = None,
        building: Optional[str] = None
    ) -> Optional[MakaniAddress]:
        """
        Rechercher une adresse Makani
        
        Args:
            community: Nom de la communauté (ex: "Dubai Marina")
            project: Nom du projet (ex: "Marina Heights")
            building: Nom du bâtiment (ex: "Tower A")
            
        Returns:
            MakaniAddress ou None si non trouvé
        """
        if not self.api_key:
            logger.warning("⚠️  MAKANI_API_KEY non configurée - utilisation de données MOCK")
            logger.warning("Pour connecter Makani API : https://geohub.dubaipulse.gov.ae")
            return self._generate_mock_address(community, project, building)
        
        try:
            # Construire la requête de recherche
            query_parts = []
            if building:
                query_parts.append(building)
            if project:
                query_parts.append(project)
            if community:
                query_parts.append(community)
            
            search_query = ", ".join(query_parts)
            
            if not search_query:
                logger.warning("Aucun critère de recherche fourni")
                return None
            
            url = f"{self.base_url}/search"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "query": search_query,
                "limit": 1
            }
            
            logger.debug(f"🔍 Recherche Makani : {search_query}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            if not data.get("results"):
                logger.debug(f"Aucun résultat Makani pour : {search_query}")
                return None
            
            address = self._parse_address(data["results"][0])
            logger.debug(f"✅ Adresse Makani trouvée : {address.makani_number}")
            return address
        
        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP Makani API : {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur Makani API : {e}")
            return None
    
    def get_by_makani_number(self, makani_number: str) -> Optional[MakaniAddress]:
        """
        Récupérer une adresse par son numéro Makani
        
        Args:
            makani_number: Numéro Makani (10 chiffres, ex: "1234567890")
            
        Returns:
            MakaniAddress ou None
        """
        if not self.api_key:
            logger.warning("⚠️  MAKANI_API_KEY non configurée")
            return None
        
        try:
            url = f"{self.base_url}/address/{makani_number}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            address = self._parse_address(data)
            logger.debug(f"✅ Adresse Makani récupérée : {makani_number}")
            return address
        
        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP Makani API : {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur Makani API : {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[MakaniAddress]:
        """
        Reverse geocoding : coordonnées → adresse
        
        Args:
            latitude: Latitude (ex: 25.0760)
            longitude: Longitude (ex: 55.1320)
            
        Returns:
            MakaniAddress ou None
        """
        if not self.api_key:
            logger.warning("⚠️  MAKANI_API_KEY non configurée")
            return None
        
        try:
            url = f"{self.base_url}/reverse"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "lat": latitude,
                "lon": longitude
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            address = self._parse_address(data)
            logger.debug(f"✅ Reverse geocoding réussi : {address.makani_number}")
            return address
        
        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP Makani API : {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur Makani API : {e}")
            return None
    
    def _parse_address(self, data: dict) -> MakaniAddress:
        """
        Parser une adresse Makani depuis la réponse API
        
        Format attendu :
        {
            "makani_number": "1234567890",
            "community": "Dubai Marina",
            "project": "Marina Heights",
            "building": "Tower A",
            "street": "Marina Walk",
            "latitude": 25.0760,
            "longitude": 55.1320,
            "poi_nearby": {
                "metro_station": "DMCC Metro Station",
                "metro_distance_m": 850,
                "beach_distance_m": 1200,
                "mall_distance_m": 500
            }
        }
        """
        poi = data.get("poi_nearby", {})
        
        return MakaniAddress(
            makani_number=data.get("makani_number"),
            
            community=normalize_location_name(data.get("community")),
            project=normalize_location_name(data.get("project")),
            building=normalize_location_name(data.get("building")),
            street=data.get("street"),
            
            latitude=Decimal(str(data.get("latitude"))) if data.get("latitude") else None,
            longitude=Decimal(str(data.get("longitude"))) if data.get("longitude") else None,
            
            metro_station=poi.get("metro_station"),
            metro_distance_m=poi.get("metro_distance_m"),
            beach_distance_m=poi.get("beach_distance_m"),
            mall_distance_m=poi.get("mall_distance_m")
        )
    
    def _generate_mock_address(
        self, 
        community: Optional[str],
        project: Optional[str],
        building: Optional[str]
    ) -> MakaniAddress:
        """Générer une adresse mock pour développement"""
        import random
        
        # Coordonnées approximatives de Dubai Marina
        base_lat = 25.0760
        base_lon = 55.1320
        
        return MakaniAddress(
            makani_number=f"{random.randint(1000000000, 9999999999)}",
            
            community=community or "Dubai Marina",
            project=project or "Marina Heights",
            building=building or "Tower A",
            street="Marina Walk",
            
            latitude=Decimal(str(base_lat + random.uniform(-0.01, 0.01))),
            longitude=Decimal(str(base_lon + random.uniform(-0.01, 0.01))),
            
            metro_station="DMCC Metro Station",
            metro_distance_m=random.randint(500, 1500),
            beach_distance_m=random.randint(800, 2000),
            mall_distance_m=random.randint(300, 1000)
        )
    
    def calculate_location_score(self, address: MakaniAddress) -> float:
        """
        Calculer un score de localisation (0-100)
        
        Critères :
        - Proximité métro (40%)
        - Proximité plage (30%)
        - Proximité mall (30%)
        
        Returns:
            Score 0-100
        """
        if not address:
            return 50.0  # Score neutre
        
        scores = []
        
        # Score métro (excellent < 500m, bon < 1000m, moyen < 1500m)
        if address.metro_distance_m is not None:
            if address.metro_distance_m < 500:
                metro_score = 100
            elif address.metro_distance_m < 1000:
                metro_score = 80
            elif address.metro_distance_m < 1500:
                metro_score = 60
            else:
                metro_score = 40
            scores.append((metro_score, 0.40))
        
        # Score plage (excellent < 1000m, bon < 2000m, moyen < 3000m)
        if address.beach_distance_m is not None:
            if address.beach_distance_m < 1000:
                beach_score = 100
            elif address.beach_distance_m < 2000:
                beach_score = 80
            elif address.beach_distance_m < 3000:
                beach_score = 60
            else:
                beach_score = 40
            scores.append((beach_score, 0.30))
        
        # Score mall (excellent < 500m, bon < 1000m, moyen < 2000m)
        if address.mall_distance_m is not None:
            if address.mall_distance_m < 500:
                mall_score = 100
            elif address.mall_distance_m < 1000:
                mall_score = 80
            elif address.mall_distance_m < 2000:
                mall_score = 60
            else:
                mall_score = 40
            scores.append((mall_score, 0.30))
        
        if not scores:
            return 50.0
        
        # Moyenne pondérée
        total_weight = sum(w for _, w in scores)
        weighted_score = sum(s * w for s, w in scores) / total_weight
        
        return round(weighted_score, 1)
    
    def batch_search(self, locations: List[Tuple[str, str, str]]) -> Dict[str, Optional[MakaniAddress]]:
        """
        Recherche en batch pour optimiser les appels API
        
        Args:
            locations: Liste de tuples (community, project, building)
            
        Returns:
            Dict avec clé = "community|project|building", valeur = MakaniAddress
        """
        results = {}
        
        for community, project, building in locations:
            key = f"{community or ''}|{project or ''}|{building or ''}"
            address = self.search_address(community, project, building)
            results[key] = address
        
        return results

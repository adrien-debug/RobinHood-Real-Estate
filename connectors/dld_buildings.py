"""
Connecteur DLD - Buildings via Dubai Pulse API
"""
from typing import List, Dict, Optional
import httpx
from loguru import logger
from connectors.dubai_pulse_auth import get_dubai_pulse_auth


class DLDBuildingsConnector:
    """
    Connecteur pour les bâtiments DLD via Dubai Pulse
    
    API utilisée : dld_buildings-open-api
    Documentation : https://www.dubaipulse.gov.ae/data/dld-registration/dld_buildings-open-api
    """
    
    def __init__(self):
        self.auth = get_dubai_pulse_auth()
        self.base_url = "https://api.dubaipulse.gov.ae/open/dld"
        self.endpoint = "dld_buildings-open-api"
        self.timeout = 60.0
    
    def fetch_buildings(
        self, 
        community: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 5000
    ) -> List[Dict]:
        """
        Récupérer les bâtiments DLD
        
        Args:
            community: Filtrer par communauté (optionnel)
            project: Filtrer par projet (optionnel)
            limit: Nombre max de résultats
            
        Returns:
            Liste de bâtiments
        """
        # Vérifier si les clés API sont configurées
        try:
            self.auth.get_access_token()
        except ValueError:
            logger.warning("⚠️  Clés API DLD non configurées - buildings non disponibles")
            return []
        
        try:
            url = f"{self.base_url}/{self.endpoint}"
            headers = self.auth.get_auth_headers()
            
            # Construire le filtre
            filters = []
            if community:
                filters.append(f"area_name_en eq '{community}'")
            if project:
                filters.append(f"project_en eq '{project}'")
            
            params = {
                "$top": limit,
                "$orderby": "building_name_en asc"
            }
            
            if filters:
                params["$filter"] = " and ".join(filters)
            
            logger.info(f"🔄 Récupération bâtiments DLD...")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            buildings = self._parse_response(data)
            logger.info(f"✅ {len(buildings)} bâtiments DLD récupérés")
            return buildings
        
        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP DLD Buildings API : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Réponse : {e.response.text[:500]}")
            return []
        except Exception as e:
            logger.error(f"❌ Erreur DLD buildings : {e}")
            return []
    
    def _parse_response(self, data: dict) -> List[Dict]:
        """
        Parser la réponse API Dubai Pulse
        
        Format attendu :
        {
            "value": [
                {
                    "building_name_en": "Marina Heights Tower A",
                    "area_name_en": "Dubai Marina",
                    "project_en": "Marina Heights",
                    "building_type_en": "Residential",
                    "building_usage_en": "Residential",
                    "nearest_landmark_en": "...",
                    "nearest_metro_en": "...",
                    "nearest_mall_en": "...",
                    ...
                }
            ]
        }
        """
        buildings = []
        items = data.get("value", [])
        
        for item in items:
            try:
                building = {
                    'building_name': item.get('building_name_en'),
                    'community': item.get('area_name_en'),
                    'project': item.get('project_en'),
                    'building_type': item.get('building_type_en'),
                    'building_usage': item.get('building_usage_en'),
                    'nearest_landmark': item.get('nearest_landmark_en'),
                    'nearest_metro': item.get('nearest_metro_en'),
                    'nearest_mall': item.get('nearest_mall_en'),
                }
                buildings.append(building)
            except Exception as e:
                logger.warning(f"⚠️  Erreur parsing building : {e}")
                continue
        
        return buildings

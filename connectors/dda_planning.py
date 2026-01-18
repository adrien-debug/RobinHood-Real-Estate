"""
Connecteur DDA - Dubai Development Authority (Planning & Zoning)

Signaux en avance sur le marché :
- Nouveaux permis de construire
- Changements de zonage
- Projets d'infrastructure
- Zones de développement prioritaire

[WARNING] Ces données sont des lead indicators précieux pour anticiper
l'évolution du marché avant que les transactions ne reflètent les changements.

API : Dubai Municipality / DDA
Documentation : https://www.dm.gov.ae/open-data
"""
from typing import List, Optional, Dict
from datetime import date, timedelta
from decimal import Decimal
import httpx
from loguru import logger
from core.config import settings
from core.models import PlanningPermit, ZoningChange
from core.utils import normalize_location_name


class DDAConnector:
    """
    Connecteur pour l'API Dubai Development Authority
    
    Données disponibles :
    - Permis de construire (building permits)
    - Changements de zonage (zoning changes)
    - Projets d'infrastructure (infrastructure projects)
    - Master plans
    """
    
    def __init__(self):
        self.api_key = settings.dda_api_key
        self.base_url = settings.dda_api_url or "https://api.dm.gov.ae/v1"
        self.timeout = 30.0
    
    def fetch_building_permits(
        self, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        community: Optional[str] = None
    ) -> List[PlanningPermit]:
        """
        Récupérer les permis de construire récents
        
        Args:
            start_date: Date de début (défaut: 90 jours en arrière)
            end_date: Date de fin (défaut: aujourd'hui)
            community: Filtrer par communauté
            
        Returns:
            Liste de permis de construire
        """
        if not self.api_key:
            logger.warning("[WARNING]  DDA_API_KEY non configurée - utilisation de données MOCK")
            logger.warning("Pour connecter DDA API : https://www.dm.gov.ae/open-data")
            return self._generate_mock_permits(start_date, end_date, community)
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=90)
        
        try:
            url = f"{self.base_url}/building-permits"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 1000
            }
            
            if community:
                params["community"] = community
            
            logger.info(f"[LOADING] Récupération permis de construire DDA : {start_date} → {end_date}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            permits = self._parse_permits(data)
            logger.info(f"[SUCCESS] {len(permits)} permis de construire récupérés")
            return permits
        
        except httpx.HTTPError as e:
            logger.error(f"[ERROR] Erreur HTTP DDA API : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Réponse : {e.response.text[:500]}")
            logger.warning("Fallback sur données MOCK")
            return self._generate_mock_permits(start_date, end_date, community)
        except Exception as e:
            logger.error(f"[ERROR] Erreur DDA API : {e}")
            logger.warning("Fallback sur données MOCK")
            return self._generate_mock_permits(start_date, end_date, community)
    
    def fetch_zoning_changes(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ZoningChange]:
        """
        Récupérer les changements de zonage récents
        
        Les changements de zonage sont des signaux forts :
        - Résidentiel → Commercial = opportunité commerciale
        - Mixte → Résidentiel = pression sur supply résidentielle
        - Zones de développement prioritaire = appréciation future
        
        Returns:
            Liste de changements de zonage
        """
        if not self.api_key:
            logger.warning("[WARNING]  DDA_API_KEY non configurée - utilisation de données MOCK")
            return self._generate_mock_zoning(start_date, end_date)
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=180)
        
        try:
            url = f"{self.base_url}/zoning-changes"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            logger.info(f"[LOADING] Récupération changements de zonage DDA : {start_date} → {end_date}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            changes = self._parse_zoning(data)
            logger.info(f"[SUCCESS] {len(changes)} changements de zonage récupérés")
            return changes
        
        except httpx.HTTPError as e:
            logger.error(f"[ERROR] Erreur HTTP DDA API : {e}")
            logger.warning("Fallback sur données MOCK")
            return self._generate_mock_zoning(start_date, end_date)
        except Exception as e:
            logger.error(f"[ERROR] Erreur DDA API : {e}")
            logger.warning("Fallback sur données MOCK")
            return self._generate_mock_zoning(start_date, end_date)
    
    def _parse_permits(self, data: dict) -> List[PlanningPermit]:
        """
        Parser les permis de construire
        
        Format attendu :
        {
            "permits": [
                {
                    "permit_id": "BP-2026-12345",
                    "issue_date": "2026-01-10",
                    "permit_type": "new_construction",
                    "community": "Dubai Marina",
                    "project_name": "Marina Bay Tower",
                    "developer": "Emaar Properties",
                    "total_units": 250,
                    "residential_units": 220,
                    "commercial_units": 30,
                    "estimated_completion": "2028-12-31",
                    "total_area_sqm": 45000
                }
            ]
        }
        """
        permits = []
        
        items = data.get("permits", []) or data.get("data", [])
        
        for item in items:
            try:
                permit = PlanningPermit(
                    permit_id=str(item.get("permit_id", "")),
                    issue_date=self._parse_date(item.get("issue_date")),
                    permit_type=item.get("permit_type", "new_construction"),
                    
                    community=normalize_location_name(item.get("community")),
                    project_name=normalize_location_name(item.get("project_name")),
                    developer=item.get("developer"),
                    
                    total_units=item.get("total_units"),
                    residential_units=item.get("residential_units"),
                    commercial_units=item.get("commercial_units"),
                    
                    estimated_completion=self._parse_date(item.get("estimated_completion")),
                    total_area_sqm=item.get("total_area_sqm")
                )
                permits.append(permit)
                
            except Exception as e:
                logger.warning(f"[WARNING]  Erreur parsing permis {item.get('permit_id', 'N/A')} : {e}")
                continue
        
        return permits
    
    def _parse_zoning(self, data: dict) -> List[ZoningChange]:
        """
        Parser les changements de zonage
        
        Format attendu :
        {
            "zoning_changes": [
                {
                    "change_id": "ZC-2026-001",
                    "effective_date": "2026-02-01",
                    "community": "Business Bay",
                    "area_name": "Bay Square District",
                    "old_zoning": "residential",
                    "new_zoning": "mixed_use",
                    "reason": "Master plan update",
                    "impact": "Allows commercial development"
                }
            ]
        }
        """
        changes = []
        
        items = data.get("zoning_changes", []) or data.get("data", [])
        
        for item in items:
            try:
                change = ZoningChange(
                    change_id=str(item.get("change_id", "")),
                    effective_date=self._parse_date(item.get("effective_date")),
                    
                    community=normalize_location_name(item.get("community")),
                    area_name=item.get("area_name"),
                    
                    old_zoning=item.get("old_zoning"),
                    new_zoning=item.get("new_zoning"),
                    
                    reason=item.get("reason"),
                    impact=item.get("impact")
                )
                changes.append(change)
                
            except Exception as e:
                logger.warning(f"[WARNING]  Erreur parsing zonage {item.get('change_id', 'N/A')} : {e}")
                continue
        
        return changes
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parser une date depuis string"""
        if not date_str:
            return None
        try:
            from datetime import datetime
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except:
            return None
    
    def _generate_mock_permits(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        community: Optional[str]
    ) -> List[PlanningPermit]:
        """Générer des permis mock pour développement"""
        import random
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=90)
        
        communities = ["Dubai Marina", "Downtown Dubai", "Business Bay", "JBR", "Palm Jumeirah"]
        if community:
            communities = [community]
        
        developers = ["Emaar Properties", "Nakheel", "Damac", "Meraas", "Dubai Properties"]
        permit_types = ["new_construction", "renovation", "extension"]
        
        permits = []
        for i in range(15):
            total_units = random.randint(50, 500)
            residential = int(total_units * random.uniform(0.7, 0.95))
            
            permit = PlanningPermit(
                permit_id=f"BP-MOCK-{i:05d}",
                issue_date=start_date + timedelta(days=random.randint(0, (end_date - start_date).days)),
                permit_type=random.choice(permit_types),
                
                community=random.choice(communities),
                project_name=f"Project {random.choice(['Tower', 'Residences', 'Heights', 'Plaza'])} {random.randint(1, 50)}",
                developer=random.choice(developers),
                
                total_units=total_units,
                residential_units=residential,
                commercial_units=total_units - residential,
                
                estimated_completion=date.today() + timedelta(days=random.randint(365, 1095)),
                total_area_sqm=random.randint(20000, 80000)
            )
            permits.append(permit)
        
        logger.info(f"Données MOCK permis DDA générées : {len(permits)}")
        return permits
    
    def _generate_mock_zoning(
        self,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> List[ZoningChange]:
        """Générer des changements de zonage mock"""
        import random
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=180)
        
        communities = ["Business Bay", "Dubai Marina", "JBR", "Downtown Dubai", "DIFC"]
        zoning_types = ["residential", "commercial", "mixed_use", "industrial"]
        
        changes = []
        for i in range(5):
            old_zoning = random.choice(zoning_types)
            new_zoning = random.choice([z for z in zoning_types if z != old_zoning])
            
            change = ZoningChange(
                change_id=f"ZC-MOCK-{i:03d}",
                effective_date=start_date + timedelta(days=random.randint(0, (end_date - start_date).days)),
                
                community=random.choice(communities),
                area_name=f"District {random.randint(1, 10)}",
                
                old_zoning=old_zoning,
                new_zoning=new_zoning,
                
                reason="Master plan update",
                impact=f"Allows {new_zoning} development"
            )
            changes.append(change)
        
        logger.info(f"Données MOCK zonage DDA générées : {len(changes)}")
        return changes
    
    def calculate_supply_pressure(self, permits: List[PlanningPermit], community: str) -> Dict:
        """
        Calculer la pression de supply future pour une communauté
        
        Args:
            permits: Liste de permis de construire
            community: Nom de la communauté
            
        Returns:
            {
                "total_new_units": 1250,
                "completion_next_12m": 450,
                "completion_next_24m": 800,
                "supply_pressure_score": 65  # 0-100, plus élevé = plus de pression
            }
        """
        community_permits = [p for p in permits if p.community == community]
        
        if not community_permits:
            return {
                "total_new_units": 0,
                "completion_next_12m": 0,
                "completion_next_24m": 0,
                "supply_pressure_score": 0
            }
        
        total_units = sum(p.residential_units or 0 for p in community_permits)
        
        cutoff_12m = date.today() + timedelta(days=365)
        cutoff_24m = date.today() + timedelta(days=730)
        
        units_12m = sum(
            p.residential_units or 0 
            for p in community_permits 
            if p.estimated_completion and p.estimated_completion <= cutoff_12m
        )
        
        units_24m = sum(
            p.residential_units or 0 
            for p in community_permits 
            if p.estimated_completion and p.estimated_completion <= cutoff_24m
        )
        
        # Score de pression (plus de 500 unités/an = pression élevée)
        annual_supply = units_12m
        if annual_supply < 200:
            pressure_score = 20
        elif annual_supply < 500:
            pressure_score = 50
        elif annual_supply < 1000:
            pressure_score = 75
        else:
            pressure_score = 95
        
        return {
            "total_new_units": total_units,
            "completion_next_12m": units_12m,
            "completion_next_24m": units_24m,
            "supply_pressure_score": pressure_score
        }

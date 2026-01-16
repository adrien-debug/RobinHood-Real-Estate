"""
Connecteur Developers - Pipeline de supply future
"""
from typing import List, Optional, Dict
from datetime import date
import httpx
from loguru import logger
from core.config import settings


class DevelopersPipelineConnector:
    """Connecteur pour le pipeline des développeurs (supply future)"""
    
    def __init__(self):
        self.api_key = settings.developers_api_key
        self.timeout = 30.0
    
    def fetch_pipeline(self) -> List[Dict]:
        """
        Récupérer le pipeline de projets des développeurs
        
        EDGE DATA - avantage compétitif fort
        """
        if not self.api_key:
            logger.warning("DEVELOPERS_API_KEY non configurée - mode simulation")
            return self._generate_mock_data()
        
        try:
            # À adapter selon l'API réelle
            url = "https://api.developers.ae/v1/pipeline"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            projects = self._parse_response(data)
            logger.info(f"Pipeline développeurs récupéré : {len(projects)} projets")
            return projects
        
        except Exception as e:
            logger.error(f"Erreur developers pipeline : {e}")
            return []
    
    def _parse_response(self, data: dict) -> List[Dict]:
        """Parser la réponse API"""
        projects = []
        items = data.get("projects", []) or data.get("data", [])
        
        for item in items:
            try:
                project = {
                    "project_name": item.get("name"),
                    "developer": item.get("developer"),
                    "community": item.get("community"),
                    "total_units": item.get("total_units"),
                    "units_by_type": item.get("units_by_type", {}),
                    "launch_date": item.get("launch_date"),
                    "expected_handover_date": item.get("expected_handover"),
                    "actual_handover_date": item.get("actual_handover"),
                    "status": item.get("status", "under_construction"),
                    "completion_percentage": item.get("completion_pct", 0)
                }
                projects.append(project)
            except Exception as e:
                logger.warning(f"Erreur parsing project : {e}")
                continue
        
        return projects
    
    def _generate_mock_data(self) -> List[Dict]:
        """Données mock"""
        import random
        from datetime import timedelta
        
        developers = ["Emaar", "Damac", "Nakheel", "Meraas", "Dubai Properties"]
        communities = ["Dubai Marina", "Downtown Dubai", "Business Bay", "JBR", "Palm Jumeirah"]
        statuses = ["planned", "under_construction", "delivered"]
        
        projects = []
        for i in range(15):
            handover = date.today() + timedelta(days=random.randint(30, 730))
            
            project = {
                "project_name": f"Project {i+1}",
                "developer": random.choice(developers),
                "community": random.choice(communities),
                "total_units": random.randint(100, 800),
                "units_by_type": {
                    "studio": random.randint(20, 100),
                    "1BR": random.randint(50, 200),
                    "2BR": random.randint(50, 300),
                    "3BR+": random.randint(20, 150)
                },
                "launch_date": date.today() - timedelta(days=random.randint(100, 500)),
                "expected_handover_date": handover,
                "actual_handover_date": None,
                "status": random.choice(statuses),
                "completion_percentage": random.randint(10, 95)
            }
            projects.append(project)
        
        logger.info(f"Données MOCK pipeline : {len(projects)} projets")
        return projects

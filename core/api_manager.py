"""
API Manager - Gestion intelligente des APIs
Test automatique de connectivité et basculement réel/mock
"""
import asyncio
import httpx
from typing import Dict, List
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
from core.config import settings


class APIManager:
    """
    Gestionnaire intelligent des APIs Dubai Real Estate

    Fonctionnalités :
    - Test automatique de connectivité
    - Basculement automatique réel/mock
    - Cache des statuts de connectivité
    - Métriques de performance
    """

    def __init__(self):
        self.api_status = {}
        self.last_check = {}
        self.check_interval = 300  # 5 minutes

    async def check_all_apis(self) -> Dict[str, bool]:
        """
        Vérifier la connectivité de toutes les APIs

        Returns:
            Dict avec le statut de chaque API
        """
        apis_to_check = {
            'dld': {
                'url': f"{settings.dld_api_base_url}/status" if hasattr(settings, 'dld_api_base_url') else "https://api.dubaipulse.gov.ae/status",
                'key': getattr(settings, 'dld_api_key', None),
                'auth_type': 'oauth'
            },
            'bayut': {
                'url': f"{getattr(settings, 'bayut_api_url', 'https://api.bayut.com/v1')}/status",
                'key': getattr(settings, 'bayut_api_key', None),
                'auth_type': 'bearer'
            },
            'makani': {
                'url': f"{getattr(settings, 'makani_api_url', 'https://api.dubaipulse.gov.ae/makani')}/status",
                'key': getattr(settings, 'makani_api_key', None),
                'auth_type': 'bearer'
            },
            'dda': {
                'url': f"{getattr(settings, 'dda_api_url', 'https://api.dm.gov.ae/v1')}/status",
                'key': getattr(settings, 'dda_api_key', None),
                'auth_type': 'bearer'
            }
        }

        results = {}

        async with httpx.AsyncClient(timeout=10.0) as client:
            for api_name, config in apis_to_check.items():
                try:
                    headers = {}
                    if config['key']:
                        if config['auth_type'] == 'bearer':
                            headers['Authorization'] = f"Bearer {config['key']}"
                        elif config['auth_type'] == 'oauth':
                            headers['X-API-Key'] = config['key']

                    # Test simple de connectivité
                    response = await client.head(config['url'], headers=headers, timeout=5.0)

                    # Considérer comme fonctionnel si pas d'erreur serveur
                    is_working = response.status_code < 500
                    results[api_name] = is_working

                    if is_working:
                        logger.info(f"API {api_name}: Operationnelle")
                    else:
                        logger.warning(f"API {api_name}: Probleme de statut ({response.status_code})")

                except Exception as e:
                    logger.warning(f"API {api_name}: Non accessible - {str(e)}")
                    results[api_name] = False

        self.api_status = results
        return results

    def should_use_real_api(self, api_name: str) -> bool:
        """
        Déterminer si on doit utiliser l'API réelle ou mock

        Args:
            api_name: Nom de l'API ('dld', 'bayut', 'makani', 'dda')

        Returns:
            True si API réelle disponible, False sinon
        """
        # Vérifier la configuration
        key_available = False

        if api_name == 'dld':
            key_available = bool(getattr(settings, 'dld_api_key', None))
        elif api_name == 'bayut':
            key_available = bool(getattr(settings, 'bayut_api_key', None))
        elif api_name == 'makani':
            key_available = bool(getattr(settings, 'makani_api_key', None))
        elif api_name == 'dda':
            key_available = bool(getattr(settings, 'dda_api_key', None))

        if not key_available:
            return False

        # Vérifier le statut de connectivité
        if api_name in self.api_status:
            return self.api_status[api_name]

        # Si pas de statut connu, essayer quand même
        return True

    async def initialize(self):
        """Initialisation - test de toutes les APIs"""
        logger.info("Initialisation du gestionnaire d'APIs...")
        await self.check_all_apis()

        working_apis = sum(1 for status in self.api_status.values() if status)
        total_apis = len(self.api_status)

        logger.info(f"APIs operationnelles: {working_apis}/{total_apis}")

        if working_apis == total_apis:
            logger.success("Toutes les APIs sont operationnelles!")
        elif working_apis > 0:
            logger.info("Mode hybride: Certaines APIs utilisent des donnees mock")
        else:
            logger.warning("Toutes les APIs utilisent le mode mock")

    def get_api_status_summary(self) -> Dict:
        """Résumé du statut des APIs"""
        return {
            'total_apis': len(self.api_status),
            'working_apis': sum(1 for status in self.api_status.values() if status),
            'failed_apis': sum(1 for status in self.api_status.values() if not status),
            'details': self.api_status
        }


# Instance globale
api_manager = APIManager()


async def initialize_api_manager():
    """Fonction d'initialisation pour l'application"""
    await api_manager.initialize()


def get_api_status(api_name: str) -> bool:
    """Fonction utilitaire pour vérifier le statut d'une API"""
    return api_manager.should_use_real_api(api_name)
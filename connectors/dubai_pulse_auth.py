"""
Module d'authentification OAuth pour Dubai Pulse API
"""
import httpx
from typing import Optional
from datetime import datetime, timedelta
from loguru import logger
from core.config import settings


class DubaiPulseAuth:
    """
    Gestionnaire d'authentification OAuth pour Dubai Pulse
    
    Gère :
    - Obtention du token OAuth
    - Rafraîchissement automatique
    - Cache du token
    """
    
    def __init__(self):
        self.client_id = settings.dld_api_key  # API Key
        self.client_secret = settings.dld_api_secret  # API Secret
        self.oauth_url = "https://api.dubaipulse.gov.ae/oauth/client_credential/accesstoken"
        
        # Cache du token
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Obtenir un token d'accès valide
        
        Args:
            force_refresh: Forcer le rafraîchissement même si le token est valide
            
        Returns:
            Token d'accès OAuth
        """
        # Si token existe et est valide, le retourner
        if not force_refresh and self._is_token_valid():
            logger.debug("Utilisation du token OAuth en cache")
            return self._access_token
        
        # Sinon, obtenir un nouveau token
        logger.info("Obtention d'un nouveau token OAuth Dubai Pulse")
        return self._fetch_new_token()
    
    def _is_token_valid(self) -> bool:
        """Vérifier si le token en cache est encore valide"""
        if not self._access_token or not self._token_expires_at:
            return False
        
        # Ajouter une marge de 5 minutes avant expiration
        return datetime.now() < (self._token_expires_at - timedelta(minutes=5))
    
    def _fetch_new_token(self) -> str:
        """Obtenir un nouveau token OAuth"""
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "DLD_API_KEY et DLD_API_SECRET doivent être configurés. "
                "Voir https://www.dubaipulse.gov.ae pour obtenir l'accès."
            )
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.oauth_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            # Extraire le token et la durée de validité
            self._access_token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)  # Par défaut 1h
            
            if not self._access_token:
                raise ValueError("Token non reçu dans la réponse OAuth")
            
            # Calculer la date d'expiration
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info(f"✅ Token OAuth obtenu (expire dans {expires_in}s)")
            return self._access_token
        
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP lors de l'authentification OAuth : {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Réponse : {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Erreur authentification OAuth : {e}")
            raise
    
    def get_auth_headers(self) -> dict:
        """
        Obtenir les headers d'authentification pour les requêtes API
        
        Returns:
            Dict avec le header Authorization
        """
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }


# Instance globale pour réutilisation
_auth_instance: Optional[DubaiPulseAuth] = None


def get_dubai_pulse_auth() -> DubaiPulseAuth:
    """
    Obtenir l'instance d'authentification Dubai Pulse (singleton)
    
    Returns:
        Instance DubaiPulseAuth
    """
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = DubaiPulseAuth()
    return _auth_instance

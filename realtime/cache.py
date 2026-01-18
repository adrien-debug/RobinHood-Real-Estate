"""
Cache intelligent pour données temps réel
"""
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from loguru import logger


class InMemoryCache:
    """Cache en mémoire simple avec TTL"""
    
    def __init__(self, ttl_minutes: int = 10):
        self.ttl_minutes = ttl_minutes
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Récupérer une valeur du cache"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Vérifier l'expiration
        if datetime.now() > entry['expires_at']:
            del self._cache[key]
            return None
        
        logger.debug(f"Cache HIT : {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Stocker une valeur dans le cache
        
        Args:
            key: Clé du cache
            value: Valeur à stocker
            ttl: TTL en secondes (optionnel, sinon utilise ttl_minutes par défaut)
        """
        if ttl is not None:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        else:
            expires_at = datetime.now() + timedelta(minutes=self.ttl_minutes)
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        
        logger.debug(f"Cache SET : {key} (expire: {expires_at})")
    
    def clear(self):
        """Vider le cache"""
        self._cache.clear()
        logger.info("Cache vidé")
    
    def cleanup(self):
        """Nettoyer les entrées expirées"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cache cleanup : {len(expired_keys)} entrées supprimées")


# Instance globale
cache = InMemoryCache()

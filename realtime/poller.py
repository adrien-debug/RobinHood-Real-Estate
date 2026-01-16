"""
Polling temps réel des données
"""
import time
from datetime import datetime, timedelta
from loguru import logger
from core.config import settings
from core.utils import get_dubai_now
from graphs.market_intelligence_graph import run_daily_pipeline


class RealtimePoller:
    """Poller pour refresh temps réel"""
    
    def __init__(self, interval_minutes: int = None):
        self.interval_minutes = interval_minutes or settings.polling_interval_minutes
        self.last_run = None
    
    def start(self):
        """Démarrer le polling continu"""
        logger.info(f"🔄 Démarrage du poller (intervalle: {self.interval_minutes} min)")
        
        while True:
            try:
                now = get_dubai_now()
                
                # Vérifier si c'est le moment de refresh
                if self._should_run(now):
                    logger.info(f"⏰ Refresh à {now}")
                    
                    # Exécuter le pipeline
                    run_daily_pipeline(now.date())
                    
                    self.last_run = now
                
                # Attendre avant le prochain check
                time.sleep(60)  # Check chaque minute
            
            except KeyboardInterrupt:
                logger.info("⏹️  Poller arrêté")
                break
            except Exception as e:
                logger.error(f"Erreur dans le poller : {e}")
                time.sleep(60)
    
    def _should_run(self, now: datetime) -> bool:
        """Vérifier si on doit exécuter le refresh"""
        if self.last_run is None:
            return True
        
        elapsed = (now - self.last_run).total_seconds() / 60
        return elapsed >= self.interval_minutes


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    poller = RealtimePoller()
    poller.start()

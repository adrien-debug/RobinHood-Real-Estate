"""
Pipeline : Calcul des régimes de marché
"""
from datetime import date
from typing import Optional
from loguru import logger
from core.db import db


def compute_market_regimes(target_date: Optional[date] = None) -> bool:
    """
    Calculer les régimes de marché (ACCUMULATION, EXPANSION, etc.)
    
    Utilise la procédure SQL stockée refresh_market_regimes
    """
    if not target_date:
        target_date = date.today()
    
    try:
        db.execute_procedure("refresh_market_regimes", (target_date,))
        logger.info(f"✅ Régimes de marché calculés pour {target_date}")
        return True
    except Exception as e:
        logger.error(f"Erreur calcul régimes : {e}")
        return False


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    success = compute_market_regimes()
    print(f"Régimes calculés : {success}")

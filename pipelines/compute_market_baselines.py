"""
Pipeline : Calcul des baselines marché
"""
from datetime import date
from typing import Optional
from loguru import logger
from core.db import db


def compute_market_baselines(target_date: Optional[date] = None) -> bool:
    """
    Calculer les baselines marché (7j, 30j, 90j)
    
    Utilise la procédure SQL stockée refresh_market_baselines
    """
    if not target_date:
        target_date = date.today()
    
    try:
        db.execute_procedure("refresh_market_baselines", (target_date,))
        logger.info(f"✅ Baselines calculées pour {target_date}")
        return True
    except Exception as e:
        logger.error(f"Erreur calcul baselines : {e}")
        return False


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    success = compute_market_baselines()
    print(f"Baselines calculées : {success}")

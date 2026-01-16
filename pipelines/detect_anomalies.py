"""
Pipeline : Détection d'anomalies de prix
"""
from datetime import date
from typing import Optional, List, Dict
from loguru import logger
from core.db import db


def detect_anomalies(target_date: Optional[date] = None) -> List[Dict]:
    """
    Détecter les transactions anormalement basses vs marché
    
    Utilise la fonction SQL detect_opportunities
    """
    if not target_date:
        target_date = date.today()
    
    try:
        query = """
        SELECT * FROM detect_opportunities(%s)
        """
        results = db.execute_query(query, (target_date,))
        
        logger.info(f"✅ Anomalies détectées : {len(results)} pour {target_date}")
        return results
    except Exception as e:
        logger.error(f"Erreur détection anomalies : {e}")
        return []


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    anomalies = detect_anomalies()
    print(f"Anomalies détectées : {len(anomalies)}")
    for a in anomalies[:5]:
        print(f"  - {a['community']} / {a['building']} : {a['discount_pct']}% sous marché")

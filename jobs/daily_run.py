"""
Job quotidien - Exécution automatique du pipeline
"""
from datetime import date
from loguru import logger
from core.utils import setup_logging, get_dubai_today
from graphs.market_intelligence_graph import run_daily_pipeline


def main():
    """Point d'entrée du job quotidien"""
    setup_logging()
    
    logger.info("=" * 80)
    logger.info("🚀 DÉMARRAGE DU JOB QUOTIDIEN - DUBAI REAL ESTATE INTELLIGENCE")
    logger.info("=" * 80)
    
    try:
        target_date = get_dubai_today()
        logger.info(f"Date cible : {target_date}")
        
        # Exécuter le pipeline complet via LangGraph
        final_state = run_daily_pipeline(target_date)
        
        # Vérifier les erreurs
        if final_state['errors']:
            logger.warning(f"⚠️  Job terminé avec {len(final_state['errors'])} erreurs")
            return 1
        else:
            logger.info("✅ Job terminé avec succès")
            return 0
    
    except Exception as e:
        logger.error(f"❌ Erreur critique dans le job quotidien : {e}")
        return 1


if __name__ == "__main__":
    exit(main())

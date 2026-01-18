"""
LangGraph - Pipeline d'intelligence de marché

Pipeline enrichi avec :
- Ingestion index locatif (rental_index)
- Calcul des features normalisées
- Calcul des 8 KPIs avancés
- Calcul des résumés de risques
"""
from typing import TypedDict, Annotated
from datetime import date, timedelta
from loguru import logger
from langgraph.graph import StateGraph, END
from pipelines.ingest_transactions import ingest_transactions
from pipelines.ingest_mortgages import ingest_mortgages
from pipelines.ingest_rental_index import ingest_rental_index
from pipelines.compute_features import compute_features
from pipelines.compute_market_baselines import compute_market_baselines
from pipelines.compute_market_regimes import compute_market_regimes
from pipelines.compute_kpis import compute_kpis
from pipelines.detect_anomalies import detect_anomalies
from pipelines.compute_scores import compute_scores
from pipelines.compute_risk_summary import compute_risk_summary
from ai_agents.chief_investment_officer import ChiefInvestmentOfficer
from alerts.notifier import AlertNotifier


class MarketIntelligenceState(TypedDict):
    """État du pipeline enrichi"""
    target_date: date
    transactions_count: int
    mortgages_count: int
    rental_index_count: int
    features_count: int
    baselines_computed: bool
    regimes_computed: bool
    kpis_count: int
    anomalies_count: int
    opportunities_count: int
    risk_summaries_count: int
    brief_generated: bool
    alerts_sent: int
    errors: list


def node_ingest_transactions(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Ingestion des transactions"""
    logger.info("🔄 Node: Ingest Transactions")
    
    try:
        target_date = state['target_date']
        count = ingest_transactions(
            start_date=target_date - timedelta(days=1),
            end_date=target_date
        )
        state['transactions_count'] = count
        logger.info(f"✅ Transactions ingérées : {count}")
    except Exception as e:
        logger.error(f"❌ Erreur ingest transactions : {e}")
        state['errors'].append(f"ingest_transactions: {e}")
    
    return state


def node_ingest_mortgages(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Ingestion des hypothèques"""
    logger.info("🔄 Node: Ingest Mortgages")
    
    try:
        target_date = state['target_date']
        count = ingest_mortgages(
            start_date=target_date - timedelta(days=1),
            end_date=target_date
        )
        state['mortgages_count'] = count
        logger.info(f"✅ Hypothèques ingérées : {count}")
    except Exception as e:
        logger.error(f"❌ Erreur ingest mortgages : {e}")
        state['errors'].append(f"ingest_mortgages: {e}")
    
    return state


def node_ingest_rental_index(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Ingestion de l'index locatif"""
    logger.info("🔄 Node: Ingest Rental Index")
    
    try:
        count = ingest_rental_index()
        state['rental_index_count'] = count
        logger.info(f"✅ Index locatif ingéré : {count}")
    except Exception as e:
        logger.error(f"❌ Erreur ingest rental index : {e}")
        state['errors'].append(f"ingest_rental_index: {e}")
    
    return state


def node_compute_features(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Calcul des features normalisées"""
    logger.info("🔄 Node: Compute Features")
    
    try:
        target_date = state['target_date']
        count, quality_log = compute_features(target_date)
        state['features_count'] = count
        logger.info(f"✅ Features calculées : {count} (acceptées: {quality_log.records_accepted}/{quality_log.records_total})")
    except Exception as e:
        logger.error(f"❌ Erreur compute features : {e}")
        state['errors'].append(f"compute_features: {e}")
    
    return state


def node_compute_baselines(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Calcul des baselines marché"""
    logger.info("🔄 Node: Compute Baselines")
    
    try:
        target_date = state['target_date']
        success = compute_market_baselines(target_date)
        state['baselines_computed'] = success
        logger.info(f"✅ Baselines calculées : {success}")
    except Exception as e:
        logger.error(f"❌ Erreur compute baselines : {e}")
        state['errors'].append(f"compute_baselines: {e}")
    
    return state


def node_compute_regimes(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Calcul des régimes de marché"""
    logger.info("🔄 Node: Compute Regimes")
    
    try:
        target_date = state['target_date']
        success = compute_market_regimes(target_date)
        state['regimes_computed'] = success
        logger.info(f"✅ Régimes calculés : {success}")
    except Exception as e:
        logger.error(f"❌ Erreur compute regimes : {e}")
        state['errors'].append(f"compute_regimes: {e}")
    
    return state


def node_detect_anomalies(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Détection d'anomalies"""
    logger.info("🔄 Node: Detect Anomalies")
    
    try:
        target_date = state['target_date']
        anomalies = detect_anomalies(target_date)
        state['anomalies_count'] = len(anomalies)
        logger.info(f"✅ Anomalies détectées : {len(anomalies)}")
    except Exception as e:
        logger.error(f"❌ Erreur detect anomalies : {e}")
        state['errors'].append(f"detect_anomalies: {e}")
    
    return state


def node_compute_kpis(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Calcul des 8 KPIs avancés"""
    logger.info("🔄 Node: Compute KPIs")
    
    try:
        target_date = state['target_date']
        count = compute_kpis(target_date)
        state['kpis_count'] = count
        logger.info(f"✅ KPIs calculés : {count}")
    except Exception as e:
        logger.error(f"❌ Erreur compute kpis : {e}")
        state['errors'].append(f"compute_kpis: {e}")
    
    return state


def node_compute_scores(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Calcul des scores multi-stratégies"""
    logger.info("🔄 Node: Compute Scores")
    
    try:
        target_date = state['target_date']
        count = compute_scores(target_date)
        state['opportunities_count'] = count
        logger.info(f"✅ Opportunités scorées : {count}")
    except Exception as e:
        logger.error(f"❌ Erreur compute scores : {e}")
        state['errors'].append(f"compute_scores: {e}")
    
    return state


def node_compute_risk_summary(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Calcul des résumés de risques"""
    logger.info("🔄 Node: Compute Risk Summary")
    
    try:
        target_date = state['target_date']
        count = compute_risk_summary(target_date)
        state['risk_summaries_count'] = count
        logger.info(f"✅ Résumés de risques créés : {count}")
    except Exception as e:
        logger.error(f"❌ Erreur compute risk summary : {e}")
        state['errors'].append(f"compute_risk_summary: {e}")
    
    return state


def node_generate_brief(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Génération du brief CIO"""
    logger.info("🔄 Node: Generate Brief")
    
    try:
        target_date = state['target_date']
        cio = ChiefInvestmentOfficer()
        brief = cio.generate_daily_brief(target_date)
        state['brief_generated'] = True
        logger.info("✅ Brief CIO généré")
    except Exception as e:
        logger.error(f"❌ Erreur generate brief : {e}")
        state['errors'].append(f"generate_brief: {e}")
    
    return state


def node_send_alerts(state: MarketIntelligenceState) -> MarketIntelligenceState:
    """Node : Envoi des alertes"""
    logger.info("🔄 Node: Send Alerts")
    
    try:
        target_date = state['target_date']
        notifier = AlertNotifier()
        count = notifier.send_daily_alerts(target_date)
        state['alerts_sent'] = count
        logger.info(f"✅ Alertes envoyées : {count}")
    except Exception as e:
        logger.error(f"❌ Erreur send alerts : {e}")
        state['errors'].append(f"send_alerts: {e}")
    
    return state


def create_market_intelligence_graph() -> StateGraph:
    """
    Créer le graphe LangGraph enrichi
    
    Ordre d'exécution :
    1. ingest_transactions
    2. ingest_mortgages
    3. ingest_rental_index (nouveau)
    4. compute_features (nouveau)
    5. compute_baselines
    6. compute_regimes
    7. compute_kpis (nouveau)
    8. detect_anomalies
    9. compute_scores
    10. compute_risk_summary (nouveau)
    11. generate_brief
    12. send_alerts
    """
    
    workflow = StateGraph(MarketIntelligenceState)
    
    # Ajouter les nodes
    workflow.add_node("ingest_transactions", node_ingest_transactions)
    workflow.add_node("ingest_mortgages", node_ingest_mortgages)
    workflow.add_node("ingest_rental_index", node_ingest_rental_index)
    workflow.add_node("compute_features", node_compute_features)
    workflow.add_node("compute_baselines", node_compute_baselines)
    workflow.add_node("compute_regimes", node_compute_regimes)
    workflow.add_node("compute_kpis", node_compute_kpis)
    workflow.add_node("detect_anomalies", node_detect_anomalies)
    workflow.add_node("compute_scores", node_compute_scores)
    workflow.add_node("compute_risk_summary", node_compute_risk_summary)
    workflow.add_node("generate_brief", node_generate_brief)
    workflow.add_node("send_alerts", node_send_alerts)
    
    # Définir les edges (flux enrichi)
    workflow.set_entry_point("ingest_transactions")
    workflow.add_edge("ingest_transactions", "ingest_mortgages")
    workflow.add_edge("ingest_mortgages", "ingest_rental_index")
    workflow.add_edge("ingest_rental_index", "compute_features")
    workflow.add_edge("compute_features", "compute_baselines")
    workflow.add_edge("compute_baselines", "compute_regimes")
    workflow.add_edge("compute_regimes", "compute_kpis")
    workflow.add_edge("compute_kpis", "detect_anomalies")
    workflow.add_edge("detect_anomalies", "compute_scores")
    workflow.add_edge("compute_scores", "compute_risk_summary")
    workflow.add_edge("compute_risk_summary", "generate_brief")
    workflow.add_edge("generate_brief", "send_alerts")
    workflow.add_edge("send_alerts", END)
    
    return workflow.compile()


def run_daily_pipeline(target_date: date = None) -> MarketIntelligenceState:
    """
    Exécuter le pipeline quotidien complet enrichi
    
    Args:
        target_date: Date cible (défaut: aujourd'hui)
    
    Returns:
        État final du pipeline
    """
    if not target_date:
        from core.utils import get_dubai_today
        target_date = get_dubai_today()
    
    logger.info(f"🚀 Démarrage du pipeline enrichi pour {target_date}")
    
    # État initial
    initial_state = MarketIntelligenceState(
        target_date=target_date,
        transactions_count=0,
        mortgages_count=0,
        rental_index_count=0,
        features_count=0,
        baselines_computed=False,
        regimes_computed=False,
        kpis_count=0,
        anomalies_count=0,
        opportunities_count=0,
        risk_summaries_count=0,
        brief_generated=False,
        alerts_sent=0,
        errors=[]
    )
    
    # Créer et exécuter le graphe
    graph = create_market_intelligence_graph()
    final_state = graph.invoke(initial_state)
    
    # Résumé enrichi
    logger.info("=" * 60)
    logger.info("📊 RÉSUMÉ DU PIPELINE ENRICHI")
    logger.info("=" * 60)
    logger.info(f"Date : {final_state['target_date']}")
    logger.info("-" * 40)
    logger.info("INGESTION :")
    logger.info(f"  Transactions : {final_state['transactions_count']}")
    logger.info(f"  Hypothèques : {final_state['mortgages_count']}")
    logger.info(f"  Index locatif : {final_state['rental_index_count']}")
    logger.info(f"  Features : {final_state['features_count']}")
    logger.info("-" * 40)
    logger.info("CALCULS :")
    logger.info(f"  Baselines : {'✅' if final_state['baselines_computed'] else '❌'}")
    logger.info(f"  Régimes : {'✅' if final_state['regimes_computed'] else '❌'}")
    logger.info(f"  KPIs : {final_state['kpis_count']}")
    logger.info("-" * 40)
    logger.info("ANALYSE :")
    logger.info(f"  Anomalies : {final_state['anomalies_count']}")
    logger.info(f"  Opportunités : {final_state['opportunities_count']}")
    logger.info(f"  Risques : {final_state['risk_summaries_count']}")
    logger.info("-" * 40)
    logger.info("SORTIES :")
    logger.info(f"  Brief CIO : {'✅' if final_state['brief_generated'] else '❌'}")
    logger.info(f"  Alertes : {final_state['alerts_sent']}")
    
    if final_state['errors']:
        logger.warning(f"⚠️  Erreurs : {len(final_state['errors'])}")
        for error in final_state['errors']:
            logger.warning(f"  - {error}")
    else:
        logger.info("✅ Pipeline terminé sans erreur")
    
    logger.info("=" * 60)
    
    return final_state


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    # Exécuter le pipeline
    final_state = run_daily_pipeline()

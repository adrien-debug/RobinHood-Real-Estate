"""
Page Admin - Gestion des données
"""
import streamlit as st
from datetime import date, timedelta
from core.db import db
from core.utils import get_dubai_today, setup_logging
from graphs.market_intelligence_graph import run_daily_pipeline

st.set_page_config(page_title="Admin", page_icon="⚙️", layout="wide")

st.title("⚙️ Administration")

st.warning("⚠️ Cette page contient des actions sensibles. Utilisez avec précaution.")

# === INITIALISATION ===
st.subheader("🔧 Initialisation")

col1, col2 = st.columns(2)

with col1:
    if st.button("📦 Initialiser le schéma DB", use_container_width=True):
        with st.spinner("Initialisation du schéma..."):
            try:
                db.init_schema()
                
                # Charger les fonctions SQL
                import os
                sql_dir = "sql"
                for sql_file in ['baselines.sql', 'regimes.sql', 'opportunities.sql']:
                    filepath = os.path.join(sql_dir, sql_file)
                    if os.path.exists(filepath):
                        db.load_sql_file(filepath)
                
                st.success("✅ Schéma initialisé avec succès")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

with col2:
    if st.button("🧪 Générer données MOCK", use_container_width=True):
        with st.spinner("Génération de données de test..."):
            try:
                from pipelines.ingest_transactions import ingest_transactions
                from pipelines.ingest_mortgages import ingest_mortgages
                
                # Générer pour aujourd'hui et hier
                today = get_dubai_today()
                ingest_transactions(today - timedelta(days=1), today)
                ingest_mortgages(today - timedelta(days=1), today)
                
                st.success("✅ Données MOCK générées")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

st.markdown("---")

# === PIPELINE ===
st.subheader("🚀 Exécution du pipeline")

target_date = st.date_input("Date cible", value=get_dubai_today())

if st.button("▶️ Exécuter le pipeline complet", use_container_width=True):
    with st.spinner(f"Exécution du pipeline pour {target_date}..."):
        try:
            setup_logging()
            final_state = run_daily_pipeline(target_date)
            
            # Afficher le résumé
            st.success("✅ Pipeline terminé")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Transactions", final_state['transactions_count'])
                st.metric("Hypothèques", final_state['mortgages_count'])
            
            with col2:
                st.metric("Anomalies", final_state['anomalies_count'])
                st.metric("Opportunités", final_state['opportunities_count'])
            
            with col3:
                st.metric("Alertes", final_state['alerts_sent'])
                st.metric("Brief CIO", "✅" if final_state['brief_generated'] else "❌")
            
            if final_state['errors']:
                st.warning(f"⚠️ {len(final_state['errors'])} erreurs")
                for error in final_state['errors']:
                    st.caption(f"- {error}")
        
        except Exception as e:
            st.error(f"❌ Erreur pipeline : {e}")

st.markdown("---")

# === STATISTIQUES ===
st.subheader("📊 Statistiques de la base")

col1, col2, col3 = st.columns(3)

with col1:
    tx_count = db.execute_query("SELECT COUNT(*) as count FROM transactions")
    st.metric("Transactions", tx_count[0]['count'] if tx_count else 0)
    
    opp_count = db.execute_query("SELECT COUNT(*) as count FROM opportunities")
    st.metric("Opportunités", opp_count[0]['count'] if opp_count else 0)

with col2:
    baseline_count = db.execute_query("SELECT COUNT(*) as count FROM market_baselines")
    st.metric("Baselines", baseline_count[0]['count'] if baseline_count else 0)
    
    regime_count = db.execute_query("SELECT COUNT(*) as count FROM market_regimes")
    st.metric("Régimes", regime_count[0]['count'] if regime_count else 0)

with col3:
    alert_count = db.execute_query("SELECT COUNT(*) as count FROM alerts")
    st.metric("Alertes", alert_count[0]['count'] if alert_count else 0)
    
    brief_count = db.execute_query("SELECT COUNT(*) as count FROM daily_briefs")
    st.metric("Briefs", brief_count[0]['count'] if brief_count else 0)

st.markdown("---")

# === DERNIÈRES ENTRÉES ===
st.subheader("📝 Dernières entrées")

tab1, tab2, tab3 = st.tabs(["Transactions", "Opportunités", "Alertes"])

with tab1:
    recent_tx = db.execute_query("""
        SELECT transaction_date, community, price_per_sqft, rooms_bucket
        FROM transactions
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    if recent_tx:
        import pandas as pd
        st.dataframe(pd.DataFrame(recent_tx), use_container_width=True)
    else:
        st.info("Aucune transaction")

with tab2:
    recent_opp = db.execute_query("""
        SELECT detection_date, community, discount_pct, global_score, recommended_strategy
        FROM opportunities
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    if recent_opp:
        import pandas as pd
        st.dataframe(pd.DataFrame(recent_opp), use_container_width=True)
    else:
        st.info("Aucune opportunité")

with tab3:
    recent_alerts = db.execute_query("""
        SELECT alert_date, alert_type, severity, title
        FROM alerts
        ORDER BY alert_date DESC
        LIMIT 10
    """)
    
    if recent_alerts:
        import pandas as pd
        st.dataframe(pd.DataFrame(recent_alerts), use_container_width=True)
    else:
        st.info("Aucune alerte")

st.markdown("---")
st.caption(f"Dernière mise à jour : {get_dubai_today()}")

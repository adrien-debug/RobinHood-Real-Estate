"""
Page Admin - Dubai Premium Gold Design
"""
import streamlit as st
from datetime import date, timedelta
from core.db import db
from core.utils import get_dubai_today, setup_logging
from graphs.market_intelligence_graph import run_daily_pipeline
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(page_title="Administration", page_icon="", layout="wide")

# Apply Premium Gold style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Administration</div>', unsafe_allow_html=True)

st.warning("This page contains sensitive actions. Use with caution.")

# === INITIALISATION ===
st.markdown('<div class="section-title">Initialization</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("Initialize DB Schema", use_container_width=True):
        with st.spinner("Initializing schema..."):
            try:
                db.init_schema()
                
                # Charger les fonctions SQL
                import os
                sql_dir = "sql"
                for sql_file in ['baselines.sql', 'regimes.sql', 'opportunities.sql']:
                    filepath = os.path.join(sql_dir, sql_file)
                    if os.path.exists(filepath):
                        db.load_sql_file(filepath)
                
                st.success("Schema initialized successfully")
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    if st.button("Generate MOCK Data", use_container_width=True):
        with st.spinner("Generating test data..."):
            try:
                from pipelines.ingest_transactions import ingest_transactions
                from pipelines.ingest_mortgages import ingest_mortgages
                
                # Générer pour aujourd'hui et hier
                today = get_dubai_today()
                ingest_transactions(today - timedelta(days=1), today)
                ingest_mortgages(today - timedelta(days=1), today)
                
                st.success("MOCK data generated")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# === PIPELINE ===
st.markdown('<div class="section-title">Pipeline Execution</div>', unsafe_allow_html=True)

target_date = st.date_input("Target date", value=get_dubai_today())

if st.button("Run Full Pipeline", use_container_width=True):
    with st.spinner(f"Running pipeline for {target_date}..."):
        try:
            setup_logging()
            final_state = run_daily_pipeline(target_date)
            
            # Afficher le résumé
            st.success("Pipeline completed")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Transactions", final_state['transactions_count'])
                st.metric("Mortgages", final_state['mortgages_count'])
            
            with col2:
                st.metric("Anomalies", final_state['anomalies_count'])
                st.metric("Opportunities", final_state['opportunities_count'])
            
            with col3:
                st.metric("Alerts", final_state['alerts_sent'])
                st.metric("CIO Brief", "Yes" if final_state['brief_generated'] else "No")
            
            if final_state['errors']:
                st.warning(f"{len(final_state['errors'])} errors")
                for error in final_state['errors']:
                    st.caption(f"- {error}")
        
        except Exception as e:
            st.error(f"Pipeline error: {e}")

st.markdown("---")

# === STATISTIQUES ===
st.markdown('<div class="section-title">Database Statistics</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    tx_count = db.execute_query("SELECT COUNT(*) as count FROM transactions")
    st.metric("Transactions", tx_count[0]['count'] if tx_count else 0)
    
    opp_count = db.execute_query("SELECT COUNT(*) as count FROM opportunities")
    st.metric("Opportunities", opp_count[0]['count'] if opp_count else 0)

with col2:
    baseline_count = db.execute_query("SELECT COUNT(*) as count FROM market_baselines")
    st.metric("Baselines", baseline_count[0]['count'] if baseline_count else 0)
    
    regime_count = db.execute_query("SELECT COUNT(*) as count FROM market_regimes")
    st.metric("Regimes", regime_count[0]['count'] if regime_count else 0)

with col3:
    alert_count = db.execute_query("SELECT COUNT(*) as count FROM alerts")
    st.metric("Alerts", alert_count[0]['count'] if alert_count else 0)
    
    brief_count = db.execute_query("SELECT COUNT(*) as count FROM daily_briefs")
    st.metric("Briefs", brief_count[0]['count'] if brief_count else 0)

st.markdown("---")

# === DERNIÈRES ENTRÉES ===
st.markdown('<div class="section-title">Recent Entries</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Transactions", "Opportunities", "Alerts"])

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
        st.info("No transactions")

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
        st.info("No opportunities")

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
        st.info("No alerts")

st.markdown("---")
st.caption(f"Last update: {get_dubai_today()}")

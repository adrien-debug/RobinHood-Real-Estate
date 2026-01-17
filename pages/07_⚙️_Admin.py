"""
Admin & Data - Tech Company Style
"""
import streamlit as st
from core.db import db
from core.utils import get_dubai_today
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(page_title="Admin & Data", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Admin & Data</div>', unsafe_allow_html=True)

st.markdown("---")

# === DATABASE STATS ===
st.markdown('<div class="section-title">Database Status</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Real-time metrics</div>', unsafe_allow_html=True)

# Get counts
tables = [
    ('dld_transactions', 'Transactions'),
    ('dld_opportunities', 'Opportunities'),
    ('dld_daily_briefs', 'Daily Briefs'),
    ('market_baselines', 'Baselines'),
    ('market_regimes', 'Regimes'),
    ('active_alerts', 'Alerts')
]

counts = {}
for table, label in tables:
    try:
        result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
        counts[label] = result[0]['count'] if result else 0
    except:
        counts[label] = 0

cols = st.columns(6)

for i, (table, label) in enumerate(tables):
    with cols[i]:
        count = counts.get(label, 0)
        st.markdown(kpi_card(label, "records", str(count)), unsafe_allow_html=True)

st.markdown("---")

# === RECENT ACTIVITY ===
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-title">Recent Transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Last 10</div>', unsafe_allow_html=True)
    
    recent_tx = db.execute_query("""
        SELECT transaction_date, community, rooms_bucket, price_aed
        FROM transactions
        ORDER BY transaction_date DESC, created_at DESC
        LIMIT 10
    """)
    
    if recent_tx:
        import pandas as pd
        df_data = []
        for tx in recent_tx:
            df_data.append({
                "Date": str(tx.get('transaction_date', 'N/A')),
                "Location": tx.get('community', 'N/A'),
                "Type": tx.get('rooms_bucket', 'N/A'),
                "Price": f"{tx.get('price_aed', 0):,.0f} AED"
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent transactions.")

with col_right:
    st.markdown('<div class="section-title">Data Sync</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Manual controls</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="data-card" style="padding: 2rem;">', unsafe_allow_html=True)
    
    if st.button("Refresh Transactions", use_container_width=True):
        with st.spinner("Syncing..."):
            try:
                from pipelines.ingest_transactions import ingest_dld_transactions
                result = ingest_dld_transactions()
                st.success(f"Done: {result}")
            except Exception as e:
                st.error(str(e))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Compute Baselines", use_container_width=True):
        with st.spinner("Computing..."):
            try:
                from pipelines.compute_market_baselines import compute_baselines
                compute_baselines()
                st.success("Baselines updated")
            except Exception as e:
                st.error(str(e))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Compute Scores", use_container_width=True):
        with st.spinner("Scoring..."):
            try:
                from pipelines.compute_scores import compute_scores
                compute_scores()
                st.success("Scores updated")
            except Exception as e:
                st.error(str(e))
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# === SYSTEM INFO ===
st.markdown('<div class="section-title">System Info</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Environment</div>', unsafe_allow_html=True)

import platform
import sys

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Python", sys.version.split()[0])
with col2:
    st.metric("Platform", f"{platform.system()}")
with col3:
    st.metric("Date", str(get_dubai_today()))

st.caption(f"Last update: {get_dubai_today()}")

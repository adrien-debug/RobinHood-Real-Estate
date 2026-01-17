"""
Robin - Dubai Real Estate Intelligence
Main entry point
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from core.config import settings
from core.styles import apply_plecto_style

st.set_page_config(
    page_title="Robin - Real Estate Intel",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st_autorefresh(interval=5 * 60 * 1000, key="main_refresh")

# Apply style
apply_plecto_style()

# Check config
import os
is_cloud = "mount/src" in str(st.__file__).lower() or os.getenv("STREAMLIT_CLOUD") is not None
is_configured = (
    settings.database_url != "postgresql://user:password@localhost:5432/dubai_real_estate"
    and "localhost" not in settings.database_url
)

if is_cloud and not is_configured:
    st.error("Configuration Required")
    st.markdown("""
    **DATABASE_URL not configured**
    
    1. Click "Manage app" → Settings → Secrets
    2. Add your Supabase connection string
    3. Save and reboot
    """)
    st.stop()

# Header
st.markdown("""
<div style="text-align: center; padding: 3rem 0;">
    <div style="font-size: 3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.5rem;">Robin</div>
    <div style="font-size: 1.1rem; color: rgba(255,255,255,0.6);">Dubai Real Estate Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# Navigation grid
st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/01_📊_Dashboard.py")

with col2:
    if st.button("🏠 Sales", use_container_width=True):
        st.switch_page("pages/02_🏠_Sales.py")

with col3:
    if st.button("📍 Zones", use_container_width=True):
        st.switch_page("pages/03_📍_Zones.py")

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("🎯 Radar", use_container_width=True):
        st.switch_page("pages/04_🎯_Radar.py")

with col5:
    if st.button("💰 Yield", use_container_width=True):
        st.switch_page("pages/05_💰_Yield.py")

with col6:
    if st.button("🔔 Alerts", use_container_width=True):
        st.switch_page("pages/06_🔔_Alerts.py")

st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

# Quick stats
from core.db import db

try:
    stats = db.execute_query("""
        SELECT 
            (SELECT COUNT(*) FROM transactions WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days') as weekly_tx,
            (SELECT COUNT(*) FROM dld_opportunities WHERE detection_date >= CURRENT_DATE - INTERVAL '7 days') as weekly_opps,
            (SELECT AVG(global_score) FROM dld_opportunities WHERE detection_date >= CURRENT_DATE - INTERVAL '7 days') as avg_score
    """)
    
    if stats:
        s = stats[0]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Weekly Transactions", s.get('weekly_tx', 0))
        with c2:
            st.metric("Weekly Opportunities", s.get('weekly_opps', 0))
        with c3:
            avg = s.get('avg_score', 0)
            st.metric("Avg Score", f"{avg or 0:.0f}%")
except Exception:
    pass

# Footer
st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
st.caption(f"Timezone: {settings.timezone} | Auto-refresh: {settings.polling_interval_minutes} min | Status: Online")

"""
Robin - Dubai Real Estate Intelligence
Main entry point
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from core.config import settings
from core.styles import apply_plecto_style
from core.icons import icon_svg

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

# Logo SVG Robin
ROBIN_LOGO = '<svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="24" cy="24" r="22" stroke="#00D9A3" stroke-width="2" fill="none"/><path d="M14 32 L24 16 L34 32" stroke="#00D9A3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M18 26 L24 20 L30 26" stroke="#00D9A3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><circle cx="24" cy="32" r="2" fill="#00D9A3"/></svg>'

# Header with logo
header_html = f'''<div style="text-align: center; padding: 2rem 0;">
<div style="display: flex; justify-content: center; margin-bottom: 1rem;">{ROBIN_LOGO}</div>
<div style="font-size: 2.5rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.5rem; letter-spacing: -0.02em;">Robin</div>
<div style="font-size: 1rem; color: rgba(255,255,255,0.5); letter-spacing: 0.05em;">DUBAI REAL ESTATE INTELLIGENCE</div>
</div>'''
st.markdown(header_html, unsafe_allow_html=True)

# Custom CSS for nav buttons with icons
st.markdown("""
<style>
.nav-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    padding: 1rem;
    background: rgba(19, 29, 50, 0.8);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}
.nav-btn:hover {
    background: rgba(0, 217, 163, 0.1);
    border-color: rgba(0, 217, 163, 0.3);
}
.nav-btn.primary {
    background: rgba(0, 217, 163, 0.15);
    border-color: #00D9A3;
}
.nav-btn svg {
    flex-shrink: 0;
}
.nav-label {
    font-weight: 500;
    font-size: 0.95rem;
    color: rgba(255,255,255,0.9);
}
.nav-btn.primary .nav-label {
    color: #00D9A3;
}
</style>
""", unsafe_allow_html=True)

# Navigation grid
st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Dashboard", key="nav_dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Dashboard.py")

with col2:
    if st.button("Sales", key="nav_sales", use_container_width=True):
        st.switch_page("pages/02_Sales.py")

with col3:
    if st.button("Zones", key="nav_zones", use_container_width=True):
        st.switch_page("pages/03_Zones.py")

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("Radar", key="nav_radar", use_container_width=True):
        st.switch_page("pages/04_Radar.py")

with col5:
    if st.button("Yield", key="nav_yield", use_container_width=True):
        st.switch_page("pages/05_Yield.py")

with col6:
    if st.button("Alerts", key="nav_alerts", use_container_width=True):
        st.switch_page("pages/06_Alerts.py")

col7, col8, col9 = st.columns(3)

with col7:
    if st.button("Admin", key="nav_admin", use_container_width=True):
        st.switch_page("pages/07_Admin.py")

with col8:
    if st.button("Insights", key="nav_insights", use_container_width=True):
        st.switch_page("pages/08_Market_Insights.py")

with col9:
    st.empty()  # Placeholder for future feature

st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)

# Quick stats
from core.db import db

try:
    stats = db.execute_query("""
        SELECT 
            (SELECT COUNT(*) FROM transactions WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days') as weekly_tx,
            (SELECT COUNT(*) FROM opportunities WHERE detection_date >= CURRENT_DATE - INTERVAL '7 days') as weekly_opps,
            (SELECT AVG(global_score) FROM opportunities WHERE detection_date >= CURRENT_DATE - INTERVAL '7 days') as avg_score
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

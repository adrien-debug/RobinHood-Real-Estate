"""
Robin - Real Estate Intelligence
Main entry point with navigation
"""
import streamlit as st

st.set_page_config(
    page_title="Robin - Real Estate Intel",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for sidebar icons
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #0B1426 0%, #0A1220 100%) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Sidebar styling - ensure all colors are properly defined */
    [data-testid="stSidebar"] {
        background: #0F1A2E !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
    }

    [data-testid="stSidebarNav"] a {
        color: rgba(255,255,255,0.7) !important;
        background-color: transparent !important;
        border-radius: 8px !important;
        padding: 0.8rem !important;
        border: 1px solid transparent !important;
    }

    [data-testid="stSidebarNav"] a:hover {
        color: #00D9A3 !important;
        background-color: rgba(0, 217, 163, 0.15) !important;
        border-color: rgba(0, 217, 163, 0.3) !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: rgba(0, 217, 163, 0.2) !important;
        color: #00D9A3 !important;
        border-color: #00D9A3 !important;
    }

    /* Fix for Streamlit theme colors */
    [data-testid="stSidebar"] [data-testid="stWidget"] {
        background-color: #131D32 !important;
        border-color: rgba(255,255,255,0.1) !important;
    }

    [data-testid="stSidebar"] .stSkeleton {
        background-color: rgba(255,255,255,0.1) !important;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        margin: 3rem 0 1rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.6);
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .nav-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        max-width: 900px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .nav-card {
        background: #131D32;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-card:hover {
        background: #1A2744;
        border-color: #00D9A3;
        transform: translateY(-4px);
    }
    
    .nav-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .nav-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
    }
    
    .nav-desc {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.5);
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown('<div class="main-title">Robin</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Dubai Real Estate Intelligence Platform</div>', unsafe_allow_html=True)

# Navigation cards
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

col7, col8, col9 = st.columns(3)

with col7:
    if st.button("⚙️ Admin", use_container_width=True):
        st.switch_page("pages/07_⚙️_Admin.py")

with col8:
    if st.button("📈 Insights", use_container_width=True):
        st.switch_page("pages/08_📈_Market_Insights.py")

st.markdown("<br><br>", unsafe_allow_html=True)

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
            st.metric("Avg Score", f"{s.get('avg_score', 0) or 0:.0f}%")
except:
    pass

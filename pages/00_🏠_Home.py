"""
Page d'accueil - Design Premium Dubai
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import date
from core.utils import get_dubai_today

st.set_page_config(
    page_title="Dubai Real Estate Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour design premium
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');
    
    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    }
    
    .hero h1 {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        color: white;
        margin: 0;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        letter-spacing: 2px;
    }
    
    .hero p {
        font-family: 'Inter', sans-serif;
        font-size: 1.3rem;
        color: rgba(255,255,255,0.95);
        margin-top: 1rem;
        font-weight: 300;
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-number {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        color: #D4AF37;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
    }
    
    .stat-label {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: rgba(255,255,255,0.8);
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Feature Cards */
    .feature-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        background: rgba(255,255,255,0.08);
        border-color: #D4AF37;
        transform: translateX(10px);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5rem;
        color: #D4AF37;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-family: 'Inter', sans-serif;
        color: rgba(255,255,255,0.7);
        line-height: 1.6;
    }
    
    /* Pulse Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero">
    <h1>🏙️ DUBAI REAL ESTATE</h1>
    <p>Intelligence Institutionnelle • Temps Réel • IA Décisionnelle</p>
</div>
""", unsafe_allow_html=True)

# Stats en temps réel
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number pulse">24/7</div>
        <div class="stat-label">Monitoring</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">10K+</div>
        <div class="stat-label">Transactions/Jour</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">4</div>
        <div class="stat-label">Stratégies IA</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number pulse">LIVE</div>
        <div class="stat-label">Data Feed</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Features
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎯</div>
        <div class="feature-title">Deal Radar</div>
        <div class="feature-desc">
            Détection automatique d'opportunités sous-valorisées avec scoring multi-stratégies (FLIP, RENT, LONG_TERM)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Market Intelligence</div>
        <div class="feature-desc">
            Analyse des régimes de marché en temps réel : ACCUMULATION, EXPANSION, DISTRIBUTION, RETOURNEMENT
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">Agent CIO</div>
        <div class="feature-desc">
            Brief quotidien généré par IA : zones à surveiller, opportunités prioritaires, risques identifiés
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">Temps Réel</div>
        <div class="feature-desc">
            Données DLD actualisées en continu avec cache intelligent et polling automatique
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📱</div>
        <div class="feature-title">Mobile-First</div>
        <div class="feature-desc">
            Interface optimisée pour iPhone avec design responsive et UX premium
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔔</div>
        <div class="feature-title">Alertes Intelligentes</div>
        <div class="feature-desc">
            Notifications configurables sur anomalies, opportunités et changements de régime
        </div>
    </div>
    """, unsafe_allow_html=True)

# CTA
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 2rem;">
    <p style="font-family: 'Inter', sans-serif; font-size: 1.2rem; color: rgba(255,255,255,0.7);">
        Prêt à explorer le marché immobilier de Dubaï ?
    </p>
</div>
""", unsafe_allow_html=True)

# Quick access buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Dashboard.py")

with col2:
    if st.button("🎯 Deal Radar", use_container_width=True, type="primary"):
        st.switch_page("pages/04_Deal_Radar.py")

with col3:
    if st.button("🏢 Zones & Projets", use_container_width=True, type="primary"):
        st.switch_page("pages/03_Zones_Projets_Buildings.py")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
    <p style="font-family: 'Inter', sans-serif; color: rgba(255,255,255,0.5); font-size: 0.9rem;">
        Dubai Real Estate Intelligence v1.1.0 • Powered by AI & Real-Time Data
    </p>
</div>
""", unsafe_allow_html=True)

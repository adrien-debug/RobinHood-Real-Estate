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

# Custom CSS pour design premium Villa Hermitage style
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=Lato:wght@300;400;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(180deg, #1C1C1E 0%, #2C2C2E 100%);
    }
    
    /* Golden Frame Effect */
    .main-container {
        border: 3px solid;
        border-image: linear-gradient(135deg, #C9A961 0%, #E8D4A0 50%, #C9A961 100%) 1;
        border-radius: 30px;
        padding: 2rem;
        margin: 1rem;
        background: rgba(28, 28, 30, 0.95);
        backdrop-filter: blur(20px);
    }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, rgba(201, 169, 97, 0.15) 0%, rgba(44, 44, 46, 0.8) 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid rgba(201, 169, 97, 0.3);
    }
    
    .hero h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        color: #C9A961;
        margin: 0;
        letter-spacing: 1px;
    }
    
    .hero p {
        font-family: 'Lato', sans-serif;
        font-size: 1.1rem;
        color: rgba(245, 245, 245, 0.8);
        margin-top: 1rem;
        font-weight: 300;
    }
    
    /* Property Cards - Villa Style */
    .property-card {
        background: rgba(44, 44, 46, 0.6);
        border: 1px solid rgba(201, 169, 97, 0.3);
        padding: 0;
        border-radius: 20px;
        overflow: hidden;
        transition: all 0.4s ease;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }
    
    .property-card:hover {
        transform: translateY(-8px);
        border-color: rgba(201, 169, 97, 0.8);
        box-shadow: 0 15px 50px rgba(201, 169, 97, 0.3);
    }
    
    .property-image {
        width: 100%;
        height: 250px;
        object-fit: cover;
        border-radius: 20px 20px 0 0;
    }
    
    .property-info {
        padding: 1.5rem;
    }
    
    .property-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #F5F5F5;
        margin-bottom: 0.5rem;
    }
    
    .property-price {
        font-family: 'Lato', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #C9A961;
        margin-bottom: 1rem;
    }
    
    .property-price-label {
        font-size: 0.9rem;
        color: rgba(245, 245, 245, 0.6);
        font-weight: 300;
    }
    
    .property-specs {
        display: flex;
        gap: 1.5rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(201, 169, 97, 0.2);
    }
    
    .spec-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: rgba(245, 245, 245, 0.7);
        font-family: 'Lato', sans-serif;
        font-size: 0.9rem;
    }
    
    /* Feature Cards - Elegant Style */
    .feature-card {
        background: rgba(44, 44, 46, 0.4);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(201, 169, 97, 0.2);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1rem;
        transition: all 0.4s ease;
    }
    
    .feature-card:hover {
        background: rgba(44, 44, 46, 0.7);
        border-color: rgba(201, 169, 97, 0.6);
        transform: translateX(10px);
        box-shadow: 0 10px 30px rgba(201, 169, 97, 0.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 0 10px rgba(201, 169, 97, 0.5));
    }
    
    .feature-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        color: #C9A961;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .feature-desc {
        font-family: 'Lato', sans-serif;
        color: rgba(245, 245, 245, 0.7);
        line-height: 1.7;
        font-weight: 300;
    }
    
    /* Bottom Navigation */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(28, 28, 30, 0.95);
        backdrop-filter: blur(20px);
        border-top: 1px solid rgba(201, 169, 97, 0.3);
        padding: 1rem;
        display: flex;
        justify-content: space-around;
        z-index: 1000;
    }
    
    .nav-item {
        text-align: center;
        color: rgba(245, 245, 245, 0.6);
        transition: all 0.3s ease;
    }
    
    .nav-item:hover {
        color: #C9A961;
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

# Hero Section - Villa Hermitage Style
st.markdown("""
<div class="hero">
    <h1>Dubai Real Estate Intelligence</h1>
    <p>Exclusive Properties • Market Intelligence • AI-Powered Insights</p>
</div>
""", unsafe_allow_html=True)

# Featured Properties - Villa Style Cards
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="font-family: 'Playfair Display', serif; font-size: 2rem; color: #C9A961; margin-bottom: 2rem; text-align: center;">
    Featured Opportunities
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="property-card">
        <img src="https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800" class="property-image" alt="Dubai Marina">
        <div class="property-info">
            <div class="property-name">Dubai Marina Residence</div>
            <div class="property-price">AED 2,450,000 <span class="property-price-label">/ unit</span></div>
            <div class="property-specs">
                <div class="spec-item">🛏️ 3 BR</div>
                <div class="spec-item">🚿 2 Bath</div>
                <div class="spec-item">📐 1,850 sqft</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="property-card">
        <img src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800" class="property-image" alt="Downtown Dubai">
        <div class="property-info">
            <div class="property-name">Downtown Dubai Penthouse</div>
            <div class="property-price">AED 8,900,000 <span class="property-price-label">/ unit</span></div>
            <div class="property-specs">
                <div class="spec-item">🛏️ 4 BR</div>
                <div class="spec-item">🚿 4 Bath</div>
                <div class="spec-item">📐 3,200 sqft</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

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

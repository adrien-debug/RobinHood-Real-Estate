"""
Page Dashboard - Style Plecto Sales Revenue
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from core.utils import get_dubai_today, format_currency, format_percentage
from realtime.refresher import DataRefresher
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(page_title="Market Intelligence Dashboard", page_icon="📊", layout="wide")

# Auto-refresh
st_autorefresh(interval=5 * 60 * 1000, key="dashboard_refresh")

# Apply Plecto style
apply_plecto_style()

# Custom CSS - Dubai Premium Chic Style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Lato:wght@300;400;500;600;700&display=swap');
    
    /* Global */
    .stApp {
        background: #0B1426 !important;
        font-family: 'Lato', sans-serif;
    }
    
    /* Header */
    .dashboard-header {
        text-align: center;
        color: #D4AF37;
        font-size: 2.2rem;
        font-weight: 600;
        font-family: 'Playfair Display', serif !important;
        margin-bottom: 2rem;
        letter-spacing: 1px;
        text-shadow: 0 2px 10px rgba(212, 175, 55, 0.2);
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        padding-bottom: 1rem;
    }
    
    /* KPI Cards - Dubai Gold Premium Style */
    .kpi-card {
        background: linear-gradient(135deg, #D4AF37 0%, #B8962E 50%, #C5A028 100%);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 
            0 8px 32px rgba(212, 175, 55, 0.25),
            0 2px 8px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 16px 48px rgba(212, 175, 55, 0.35),
            0 4px 12px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.25);
    }
    
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'Lato', sans-serif !important;
        color: #3D2914;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-subtitle {
        font-size: 0.75rem;
        color: rgba(61, 41, 20, 0.7);
        margin-bottom: 1rem;
        font-family: 'Lato', sans-serif !important;
    }
    
    .kpi-value {
        font-size: 2.8rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif !important;
        color: #3D2914;
        line-height: 1;
    }
    
    /* Chart Cards */
    .chart-card {
        background: #1A2942;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
    
    .chart-title {
        font-size: 1.1rem;
        font-weight: 600;
        font-family: 'Playfair Display', serif !important;
        color: #D4AF37;
        margin-bottom: 0.5rem;
    }
    
    .chart-subtitle {
        font-size: 0.85rem;
        color: rgba(245, 230, 211, 0.6);
        margin-bottom: 1rem;
    }
    
    /* Table Styles */
    .dataframe {
        background: #1A2942 !important;
        border-radius: 10px;
    }
    
    .dataframe th {
        background: #0B1426 !important;
        color: rgba(212, 175, 55, 0.8) !important;
        font-weight: 600 !important;
        font-family: 'Lato', sans-serif !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        padding: 1rem !important;
    }
    
    .dataframe td {
        color: #F5E6D3 !important;
        padding: 0.8rem !important;
        border-bottom: 1px solid rgba(212, 175, 55, 0.1) !important;
    }
    
    /* Status Badges - Dubai Premium */
    .status-badge {
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Lato', sans-serif !important;
        display: inline-block;
    }
    
    .status-won {
        background: linear-gradient(135deg, #D4AF37, #C5A028);
        color: #3D2914;
    }
    
    .status-analysis {
        background: #5C4033;
        color: #F5E6D3;
    }
    
    .status-qualification {
        background: linear-gradient(135deg, #CD7F32, #A0522D);
        color: #F5E6D3;
    }
    
    .status-negotiation {
        background: #8B4513;
        color: #F5E6D3;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="dashboard-header">Dubai Real Estate Intelligence Dashboard</div>', unsafe_allow_html=True)

# Date selector
target_date = st.date_input(
    "Date",
    value=get_dubai_today(),
    max_value=get_dubai_today()
)

# Récupérer les données
try:
    with st.spinner("Chargement des données..."):
        data = DataRefresher.get_dashboard_data(target_date)
except ConnectionError as e:
    st.error(str(e))
    st.stop()
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
    st.info("Vérifiez les logs pour plus de détails.")
    st.stop()

# === KPIs - Plecto Style ===
col1, col2, col3, col4 = st.columns(4)

kpis = data.get('kpis') or {}

# Valeurs sécurisées
num_deals = kpis.get('transactions_count') or 0
avg_price_raw = kpis.get('avg_price_sqft') or 0
avg_price = avg_price_raw / 1000 if avg_price_raw > 0 else 0
opportunities = kpis.get('opportunities_count') or 0

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Number of Deals</div>
        <div class="kpi-subtitle">Current month</div>
        <div class="kpi-value">{num_deals}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Average Price/sqft</div>
        <div class="kpi-subtitle">Current month</div>
        <div class="kpi-value">AED {avg_price:.1f}k</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Opportunities</div>
        <div class="kpi-subtitle">Active deals</div>
        <div class="kpi-value">{opportunities}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_score = kpis.get('avg_opportunity_score') or 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Average Score</div>
        <div class="kpi-subtitle">Deal quality</div>
        <div class="kpi-value">{avg_score:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === BRIEF CIO ===
st.subheader("🎯 Brief CIO")

brief = data.get('brief')

if brief:
    # Zones à surveiller
    st.markdown("**🔍 Zones à surveiller**")
    zones = brief.get('zones_to_watch', [])
    if isinstance(zones, str):
        import json
        zones = json.loads(zones)
    
    for zone in zones:
        st.markdown(f"- **{zone.get('zone')}** : {zone.get('reason')}")
    
    st.markdown("")
    
    # Top opportunités
    st.markdown("**💎 Opportunités prioritaires**")
    opps = brief.get('top_opportunities', [])
    if isinstance(opps, str):
        import json
        opps = json.loads(opps)
    
    for opp in opps:
        st.markdown(f"- {opp.get('reason')}")
    
    st.markdown("")
    
    # Risque principal
    st.warning(f"⚠️ **Risque principal** : {brief.get('main_risk', 'N/A')}")
    
    # Recommandation
    st.success(f"✅ **Recommandation** : {brief.get('strategic_recommendation', 'N/A')}")
else:
    st.info("Aucun brief disponible pour cette date. Exécutez le pipeline quotidien.")

st.markdown("---")

# === TOP OPPORTUNITÉS ===
st.subheader("🎯 Top 5 Opportunités")

opportunities = data.get('top_opportunities', [])[:5]

if opportunities:
    for opp in opportunities:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{opp.get('community')} / {opp.get('building')}**")
                st.caption(f"{opp.get('rooms_bucket')} • {opp.get('property_type', 'N/A')}")
            
            with col2:
                score = opp.get('global_score', 0)
                color = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
                st.metric("Score", f"{color} {score:.0f}")
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                discount = opp.get('discount_pct', 0)
                st.caption(f"💰 Discount: {discount:.1f}%")
            
            with col4:
                strategy = opp.get('recommended_strategy', 'N/A')
                st.caption(f"🎯 Stratégie: {strategy}")
            
            with col5:
                regime = opp.get('current_regime', 'N/A')
                st.caption(f"📊 Régime: {regime}")
            
            st.markdown("---")
else:
    st.info("Aucune opportunité détectée pour cette date.")

# === RÉGIMES DE MARCHÉ ===
st.subheader("📊 Régimes de marché")

regimes = data.get('regimes', [])[:10]

if regimes:
    # Créer un graphique
    regime_counts = {}
    for r in regimes:
        regime = r.get('regime', 'NEUTRAL')
        regime_counts[regime] = regime_counts.get(regime, 0) + 1
    
    fig = px.pie(
        values=list(regime_counts.values()),
        names=list(regime_counts.keys()),
        title="Distribution des régimes",
        color_discrete_map={
            'ACCUMULATION': '#10b981',
            'EXPANSION': '#3b82f6',
            'DISTRIBUTION': '#f59e0b',
            'RETOURNEMENT': '#ef4444',
            'NEUTRAL': '#6b7280'
        }
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Liste des zones
    st.markdown("**Détail par zone**")
    for r in regimes[:5]:
        regime = r.get('regime', 'N/A')
        confidence = r.get('confidence_score', 0)
        
        emoji = {
            'ACCUMULATION': '🟢',
            'EXPANSION': '🔵',
            'DISTRIBUTION': '🟡',
            'RETOURNEMENT': '🔴',
            'NEUTRAL': '⚪'
        }.get(regime, '⚪')
        
        st.markdown(f"{emoji} **{r.get('community')}** : {regime} (conf: {confidence:.2f})")
else:
    st.info("Aucun régime de marché calculé pour cette date.")

# Footer
st.markdown("---")
st.caption(f"Dernière mise à jour : {get_dubai_today()}")

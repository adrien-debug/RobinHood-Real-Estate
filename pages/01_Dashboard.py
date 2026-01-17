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

# Custom CSS - Plecto Style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Global */
    .stApp {
        background: #0B1426 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header */
    .dashboard-header {
        text-align: center;
        color: white;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
    }
    
    /* KPI Cards - Plecto Green Style */
    .kpi-card {
        background: linear-gradient(135deg, #00D9A3 0%, #00B894 100%);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 30px rgba(0, 217, 163, 0.3);
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 217, 163, 0.4);
    }
    
    .kpi-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0B1426;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-subtitle {
        font-size: 0.75rem;
        color: rgba(11, 20, 38, 0.7);
        margin-bottom: 1rem;
    }
    
    .kpi-value {
        font-size: 3rem;
        font-weight: 800;
        color: #0B1426;
        line-height: 1;
    }
    
    /* Chart Cards */
    .chart-card {
        background: #1A2942;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .chart-subtitle {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 1rem;
    }
    
    /* Table Styles */
    .dataframe {
        background: #1A2942 !important;
        border-radius: 10px;
    }
    
    .dataframe th {
        background: #0B1426 !important;
        color: rgba(255, 255, 255, 0.7) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        padding: 1rem !important;
    }
    
    .dataframe td {
        color: white !important;
        padding: 0.8rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Status Badges */
    .status-badge {
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-won {
        background: #00D9A3;
        color: #0B1426;
    }
    
    .status-analysis {
        background: #5F7A9E;
        color: white;
    }
    
    .status-qualification {
        background: #FFA726;
        color: #0B1426;
    }
    
    .status-negotiation {
        background: #FF9800;
        color: #0B1426;
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

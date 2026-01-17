"""
Page Dashboard - Dubai Premium Gold Design
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from core.utils import get_dubai_today, format_currency, format_percentage
from realtime.refresher import DataRefresher
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(page_title="Market Intelligence Dashboard", page_icon="", layout="wide")

# Auto-refresh
st_autorefresh(interval=5 * 60 * 1000, key="dashboard_refresh")

# Apply Premium Gold style
apply_plecto_style()

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
    with st.spinner("Loading data..."):
        data = DataRefresher.get_dashboard_data(target_date)
except ConnectionError as e:
    st.error(str(e))
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Check logs for more details.")
    st.stop()

# === KPIs - Premium Gold Style ===
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
st.markdown('<div class="section-title">CIO Brief</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Daily market intelligence</div>', unsafe_allow_html=True)

brief = data.get('brief')

if brief:
    # Zones à surveiller
    st.markdown("**Zones to Watch**")
    zones = brief.get('zones_to_watch', [])
    if isinstance(zones, str):
        import json
        zones = json.loads(zones)
    
    for zone in zones:
        st.markdown(f"- **{zone.get('zone')}** : {zone.get('reason')}")
    
    st.markdown("")
    
    # Top opportunités
    st.markdown("**Priority Opportunities**")
    opps = brief.get('top_opportunities', [])
    if isinstance(opps, str):
        import json
        opps = json.loads(opps)
    
    for opp in opps:
        st.markdown(f"- {opp.get('reason')}")
    
    st.markdown("")
    
    # Risque principal
    st.warning(f"**Main Risk** : {brief.get('main_risk', 'N/A')}")
    
    # Recommandation
    st.success(f"**Recommendation** : {brief.get('strategic_recommendation', 'N/A')}")
else:
    st.info("No brief available for this date. Run the daily pipeline.")

st.markdown("---")

# === TOP OPPORTUNITÉS ===
st.markdown('<div class="section-title">Top 5 Opportunities</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Highest scored deals</div>', unsafe_allow_html=True)

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
                st.metric("Score", f"{score:.0f}")
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                discount = opp.get('discount_pct', 0)
                st.caption(f"Discount: {discount:.1f}%")
            
            with col4:
                strategy = opp.get('recommended_strategy', 'N/A')
                st.caption(f"Strategy: {strategy}")
            
            with col5:
                regime = opp.get('current_regime', 'N/A')
                st.caption(f"Regime: {regime}")
            
            st.markdown("---")
else:
    st.info("No opportunities detected for this date.")

# === RÉGIMES DE MARCHÉ ===
st.markdown('<div class="section-title">Market Regimes</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Zone analysis</div>', unsafe_allow_html=True)

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
        title="Regime Distribution",
        color_discrete_map={
            'ACCUMULATION': '#D4AF37',
            'EXPANSION': '#CD7F32',
            'DISTRIBUTION': '#8B4513',
            'RETOURNEMENT': '#5C4033',
            'NEUTRAL': '#6b7280'
        }
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F5E6D3')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Liste des zones
    st.markdown("**Zone Details**")
    for r in regimes[:5]:
        regime = r.get('regime', 'N/A')
        confidence = r.get('confidence_score', 0)
        
        st.markdown(f"**{r.get('community')}** : {regime} (confidence: {confidence:.2f})")
else:
    st.info("No market regimes calculated for this date.")

# Footer
st.markdown("---")
st.caption(f"Last update: {get_dubai_today()}")

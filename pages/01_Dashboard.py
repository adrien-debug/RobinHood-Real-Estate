"""
Page Dashboard - Vue d'ensemble + Brief CIO
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from core.utils import get_dubai_today, format_currency, format_percentage
from realtime.refresher import DataRefresher

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Auto-refresh
st_autorefresh(interval=5 * 60 * 1000, key="dashboard_refresh")

st.title("📊 Dashboard")

# Date selector
target_date = st.date_input(
    "Date",
    value=get_dubai_today(),
    max_value=get_dubai_today()
)

# Récupérer les données
with st.spinner("Chargement des données..."):
    data = DataRefresher.get_dashboard_data(target_date)

# === KPIs ===
st.subheader("📈 KPIs du jour")

col1, col2, col3, col4 = st.columns(4)

kpis = data.get('kpis', {})

with col1:
    st.metric(
        "Transactions",
        kpis.get('transactions_count', 0),
        delta=None
    )

with col2:
    avg_price = kpis.get('avg_price_sqft', 0)
    st.metric(
        "Prix moyen/sqft",
        f"{avg_price:.0f} AED" if avg_price else "N/A"
    )

with col3:
    st.metric(
        "Opportunités",
        kpis.get('opportunities_count', 0)
    )

with col4:
    avg_score = kpis.get('avg_opportunity_score', 0)
    st.metric(
        "Score moyen",
        f"{avg_score:.0f}" if avg_score else "N/A"
    )

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

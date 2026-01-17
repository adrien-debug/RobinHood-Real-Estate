"""
Page Dashboard - Dubai Premium Gold v2.0 Design
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

# Apply Premium Gold style v2.0
apply_plecto_style()

# Custom page styles
st.markdown("""
<style>
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    .brief-card {
        background: linear-gradient(165deg, rgba(26, 36, 56, 0.95), rgba(15, 20, 32, 0.95));
        border-radius: 24px;
        padding: 2rem;
        border: 1px solid rgba(212, 175, 55, 0.15);
        margin-bottom: 2rem;
    }
    .brief-section {
        margin-bottom: 1.5rem;
    }
    .brief-label {
        color: #D4AF37;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.8rem;
        font-weight: 600;
    }
    .brief-content {
        color: #F5E6D3;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .zone-item {
        display: flex;
        align-items: center;
        padding: 0.8rem 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.08);
    }
    .zone-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #D4AF37;
        margin-right: 1rem;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
    }
    .opp-card {
        background: rgba(26, 36, 56, 0.7);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(212, 175, 55, 0.1);
        transition: all 0.3s ease;
    }
    .opp-card:hover {
        border-color: rgba(212, 175, 55, 0.3);
        transform: translateX(5px);
        background: rgba(212, 175, 55, 0.05);
    }
    .opp-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.8rem;
    }
    .opp-location {
        color: #F5E6D3;
        font-weight: 600;
        font-size: 1rem;
    }
    .opp-type {
        color: rgba(245, 230, 211, 0.5);
        font-size: 0.8rem;
        margin-top: 0.2rem;
    }
    .opp-score {
        background: linear-gradient(135deg, #D4AF37, #AA771C);
        color: #2C1810;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .opp-metrics {
        display: flex;
        gap: 2rem;
    }
    .opp-metric {
        color: rgba(245, 230, 211, 0.6);
        font-size: 0.85rem;
    }
    .opp-metric strong {
        color: #D4AF37;
    }
    .risk-alert {
        background: linear-gradient(165deg, rgba(139, 69, 19, 0.15), rgba(205, 127, 50, 0.1));
        border: 1px solid rgba(205, 127, 50, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }
    .risk-label {
        color: #CD7F32;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .success-alert {
        background: linear-gradient(165deg, rgba(212, 175, 55, 0.1), rgba(170, 119, 28, 0.08));
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
    }
    .success-label {
        color: #D4AF37;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="dashboard-header">Dubai Real Estate Intelligence</div>', unsafe_allow_html=True)

# Date selector with better styling
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

# === KPIs ===
kpis = data.get('kpis') or {}

num_deals = kpis.get('transactions_count') or 0
avg_price_raw = kpis.get('avg_price_sqft') or 0
avg_price = avg_price_raw / 1000 if avg_price_raw > 0 else 0
opportunities = kpis.get('opportunities_count') or 0
avg_score = kpis.get('avg_opportunity_score') or 0

col1, col2, col3, col4 = st.columns(4)

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
        <div class="kpi-title">Average Price</div>
        <div class="kpi-subtitle">Per sqft</div>
        <div class="kpi-value">AED {avg_price:.1f}k</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card kpi-card-bronze">
        <div class="kpi-title">Opportunities</div>
        <div class="kpi-subtitle">Active deals</div>
        <div class="kpi-value">{opportunities}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card kpi-card-dark">
        <div class="kpi-title kpi-title-light">Average Score</div>
        <div class="kpi-subtitle kpi-subtitle-light">Deal quality</div>
        <div class="kpi-value kpi-value-light">{avg_score:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# === BRIEF CIO ===
st.markdown('<div class="section-title">CIO Brief</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Daily market intelligence</div>', unsafe_allow_html=True)

brief = data.get('brief')

if brief:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""<div class="brief-section">
            <div class="brief-label">Zones to Watch</div>
        </div>""", unsafe_allow_html=True)
        
        zones = brief.get('zones_to_watch', [])
        if isinstance(zones, str):
            import json
            zones = json.loads(zones)
        
        for zone in zones:
            st.markdown(f"""
            <div class="zone-item">
                <div class="zone-dot"></div>
                <span class="brief-content"><strong>{zone.get('zone')}</strong></span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Risque principal
        st.markdown(f"""
        <div class="risk-alert">
            <div class="risk-label">Main Risk</div>
            <div class="brief-content">{brief.get('main_risk', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""<div class="brief-section">
            <div class="brief-label">Priority Opportunities</div>
        </div>""", unsafe_allow_html=True)
        
        opps = brief.get('top_opportunities', [])
        if isinstance(opps, str):
            import json
            opps = json.loads(opps)
        
        for opp in opps:
            reason = opp.get('reason', 'N/A') if isinstance(opp, dict) else opp
            if reason:
                st.markdown(f"""
                <div class="zone-item">
                    <div class="zone-dot"></div>
                    <span class="brief-content">{reason}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Recommandation
        st.markdown(f"""
        <div class="success-alert">
            <div class="success-label">Recommendation</div>
            <div class="brief-content">{brief.get('strategic_recommendation', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No brief available for this date. Run the daily pipeline.")

st.markdown("---")

# === TOP OPPORTUNITÉS ===
st.markdown('<div class="section-title">Top 5 Opportunities</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Highest scored deals</div>', unsafe_allow_html=True)

opportunities_list = data.get('top_opportunities', [])[:5]

if opportunities_list:
    for opp in opportunities_list:
        score = opp.get('global_score', 0)
        discount = opp.get('discount_pct', 0)
        strategy = opp.get('recommended_strategy', 'N/A')
        regime = opp.get('current_regime', 'N/A')
        
        st.markdown(f"""
        <div class="opp-card">
            <div class="opp-header">
                <div>
                    <div class="opp-location">{opp.get('community')} / {opp.get('building', 'N/A')}</div>
                    <div class="opp-type">{opp.get('rooms_bucket', 'N/A')} • {opp.get('property_type', 'Apartment')}</div>
                </div>
                <div class="opp-score">{score:.0f}</div>
            </div>
            <div class="opp-metrics">
                <div class="opp-metric">Discount: <strong>{discount:.1f}%</strong></div>
                <div class="opp-metric">Strategy: <strong>{strategy}</strong></div>
                <div class="opp-metric">Regime: <strong>{regime}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No opportunities detected for this date.")

st.markdown("---")

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
        color_discrete_map={
            'ACCUMULATION': '#D4AF37',
            'EXPANSION': '#CD7F32',
            'DISTRIBUTION': '#8B4513',
            'RETOURNEMENT': '#5C4033',
            'NEUTRAL': '#4a5568'
        },
        hole=0.6
    )
    
    fig.update_traces(
        textposition='outside',
        textinfo='label+percent',
        textfont=dict(color='#F5E6D3', size=12)
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F5E6D3', family='Outfit'),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            font=dict(color='#F5E6D3', size=11)
        ),
        annotations=[dict(
            text='<b>Regimes</b>',
            x=0.5, y=0.5,
            font=dict(size=16, color='#D4AF37', family='Cormorant Garamond'),
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No market regimes calculated for this date.")

# Footer
st.markdown("---")
st.caption(f"Last update: {get_dubai_today()}")

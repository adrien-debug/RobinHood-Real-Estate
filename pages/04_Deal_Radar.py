"""
Page Deal Radar - Dubai Premium Gold v2.0 Design
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card, status_badge

st.set_page_config(page_title="Deal Radar", page_icon="", layout="wide")

# Apply Premium Gold style v2.0
apply_plecto_style()

# Custom page styles
st.markdown("""
<style>
    .filter-container {
        background: rgba(26, 36, 56, 0.6);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
    .strategy-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .strategy-card {
        background: linear-gradient(165deg, rgba(26, 36, 56, 0.9), rgba(15, 20, 32, 0.9));
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(212, 175, 55, 0.15);
        transition: all 0.3s ease;
    }
    .strategy-card:hover {
        border-color: rgba(212, 175, 55, 0.4);
        transform: translateY(-5px);
    }
    .strategy-label {
        color: #D4AF37;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    .strategy-value {
        font-size: 2.5rem;
        font-weight: 500;
        font-family: 'Cormorant Garamond', serif;
        background: linear-gradient(135deg, #E8C547, #D4AF37, #AA771C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .deal-card {
        background: linear-gradient(165deg, rgba(26, 36, 56, 0.85), rgba(15, 20, 32, 0.9));
        border-radius: 20px;
        padding: 1.5rem 2rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(212, 175, 55, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .deal-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #D4AF37, #CD7F32);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .deal-card:hover {
        border-color: rgba(212, 175, 55, 0.3);
        transform: translateX(8px);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }
    .deal-card:hover::before {
        opacity: 1;
    }
    .deal-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    .deal-location {
        color: #F5E6D3;
        font-weight: 600;
        font-size: 1.1rem;
        font-family: 'Cormorant Garamond', serif;
    }
    .deal-type {
        color: rgba(245, 230, 211, 0.5);
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    .deal-score {
        background: linear-gradient(135deg, #E8C547 0%, #D4AF37 50%, #AA771C 100%);
        color: #2C1810;
        padding: 0.6rem 1.3rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.1rem;
        font-family: 'Cormorant Garamond', serif;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }
    .deal-metrics {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(212, 175, 55, 0.1);
    }
    .deal-metric-item {
        text-align: center;
    }
    .deal-metric-label {
        color: rgba(245, 230, 211, 0.5);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .deal-metric-value {
        color: #D4AF37;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .radar-container {
        background: rgba(26, 36, 56, 0.6);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="dashboard-header">Deal Radar</div>', unsafe_allow_html=True)

# Filters in a nice container
target_date = st.date_input("Date", value=get_dubai_today())

col1, col2, col3 = st.columns(3)

with col1:
    strategy_filter = st.selectbox("Strategy", ["All", "FLIP", "RENT", "LONG", "IGNORE"])

with col2:
    min_score = st.slider("Minimum score", 0, 100, 50)

with col3:
    regime_filter = st.selectbox("Regime", ["All", "ACCUMULATION", "EXPANSION", "DISTRIBUTION", "RETOURNEMENT"])

# Récupérer les opportunités
query = """
SELECT * FROM v_active_opportunities
WHERE detection_date = %s
    AND global_score >= %s
"""
params = [target_date, min_score]

if strategy_filter != "All":
    query += " AND recommended_strategy = %s"
    params.append(strategy_filter)

if regime_filter != "All":
    query += " AND current_regime = %s"
    params.append(regime_filter)

query += " ORDER BY global_score DESC LIMIT 50"

opportunities = db.execute_query(query, tuple(params))

st.markdown("---")

# Statistics cards
st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Distribution by strategy</div>', unsafe_allow_html=True)

if opportunities:
    strategy_counts = {}
    for opp in opportunities:
        strategy = opp.get('recommended_strategy', 'IGNORE')
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    avg_discount = sum(opp.get('discount_pct', 0) or 0 for opp in opportunities) / len(opportunities)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        count = strategy_counts.get('FLIP', 0)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Flip</div>
            <div class="kpi-subtitle">Quick resale</div>
            <div class="kpi-value">{count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        count = strategy_counts.get('RENT', 0)
        st.markdown(f"""
        <div class="kpi-card kpi-card-bronze">
            <div class="kpi-title">Rent</div>
            <div class="kpi-subtitle">Rental yield</div>
            <div class="kpi-value">{count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        count = strategy_counts.get('LONG', 0)
        st.markdown(f"""
        <div class="kpi-card kpi-card-dark">
            <div class="kpi-title kpi-title-light">Long Term</div>
            <div class="kpi-subtitle kpi-subtitle-light">Capital growth</div>
            <div class="kpi-value kpi-value-light">{count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card kpi-card-dark">
            <div class="kpi-title kpi-title-light">Avg Discount</div>
            <div class="kpi-subtitle kpi-subtitle-light">Below market</div>
            <div class="kpi-value kpi-value-light">{avg_discount:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown(f'<div class="section-title">{len(opportunities)} Opportunities Found</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Sorted by score</div>', unsafe_allow_html=True)
    
    # Liste des opportunités
    for opp in opportunities:
        score = opp.get('global_score', 0)
        discount = opp.get('discount_pct', 0)
        strategy = opp.get('recommended_strategy', 'N/A')
        regime = opp.get('current_regime', 'N/A')
        flip_score = opp.get('flip_score', 0)
        rent_score = opp.get('rent_score', 0)
        long_score = opp.get('long_term_score', 0)
        liquidity = opp.get('liquidity_score', 0)
        area = opp.get('area_sqft', 0)
        
        st.markdown(f"""
        <div class="deal-card">
            <div class="deal-header">
                <div>
                    <div class="deal-location">{opp.get('community')} / {opp.get('building', 'N/A')}</div>
                    <div class="deal-type">{opp.get('rooms_bucket', 'N/A')} • {area:.0f} sqft</div>
                </div>
                <div class="deal-score">{score:.0f}</div>
            </div>
            <div class="deal-metrics">
                <div class="deal-metric-item">
                    <div class="deal-metric-label">Discount</div>
                    <div class="deal-metric-value">{discount:.1f}%</div>
                </div>
                <div class="deal-metric-item">
                    <div class="deal-metric-label">Strategy</div>
                    <div class="deal-metric-value">{strategy}</div>
                </div>
                <div class="deal-metric-item">
                    <div class="deal-metric-label">Regime</div>
                    <div class="deal-metric-value">{regime}</div>
                </div>
                <div class="deal-metric-item">
                    <div class="deal-metric-label">Liquidity</div>
                    <div class="deal-metric-value">{liquidity:.0f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Scores détaillés dans un expander
        with st.expander("Detailed Scores"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("FLIP Score", f"{flip_score:.0f}")
                st.metric("RENT Score", f"{rent_score:.0f}")
                st.metric("LONG Score", f"{long_score:.0f}")
            
            with col2:
                # Graphique radar
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=[flip_score, rent_score, long_score, flip_score],
                    theta=['FLIP', 'RENT', 'LONG', 'FLIP'],
                    fill='toself',
                    fillcolor='rgba(212, 175, 55, 0.2)',
                    line=dict(color='#D4AF37', width=2),
                    name='Scores'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True, 
                            range=[0, 100],
                            tickfont=dict(color='rgba(245, 230, 211, 0.5)', size=10),
                            gridcolor='rgba(212, 175, 55, 0.1)'
                        ),
                        angularaxis=dict(
                            tickfont=dict(color='#D4AF37', size=12),
                            gridcolor='rgba(212, 175, 55, 0.1)'
                        ),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    height=280,
                    margin=dict(l=60, r=60, t=40, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#F5E6D3'),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No opportunities with these criteria.")

st.caption(f"Last update: {get_dubai_today()}")

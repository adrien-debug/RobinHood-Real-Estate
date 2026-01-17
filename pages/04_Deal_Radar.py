"""
Page Deal Radar - Dubai Premium Gold Design
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card, status_badge

st.set_page_config(page_title="Deal Radar", page_icon="", layout="wide")

# Apply Premium Gold style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Deal Radar</div>', unsafe_allow_html=True)

target_date = st.date_input("Date", value=get_dubai_today())

# Filtres
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

# Statistiques
st.markdown(f'<div class="section-title">{len(opportunities)} Opportunities</div>', unsafe_allow_html=True)

if opportunities:
    # Distribution des stratégies
    strategy_counts = {}
    for opp in opportunities:
        strategy = opp.get('recommended_strategy', 'IGNORE')
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("FLIP", strategy_counts.get('FLIP', 0))
    with col2:
        st.metric("RENT", strategy_counts.get('RENT', 0))
    with col3:
        st.metric("LONG", strategy_counts.get('LONG', 0))
    with col4:
        avg_discount = sum(opp.get('discount_pct', 0) or 0 for opp in opportunities) / len(opportunities)
        st.metric("Avg Discount", f"{avg_discount:.1f}%")
    
    st.markdown("---")
    
    # Liste des opportunités (cards)
    for opp in opportunities:
        with st.container():
            # Header
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{opp.get('community')} / {opp.get('building', 'N/A')}**")
                st.caption(f"{opp.get('rooms_bucket', 'N/A')} • {opp.get('area_sqft', 0):.0f} sqft")
            
            with col2:
                score = opp.get('global_score', 0)
                st.metric("Score", f"{score:.0f}")
            
            # Métriques
            col3, col4, col5, col6 = st.columns(4)
            
            with col3:
                discount = opp.get('discount_pct', 0)
                st.caption(f"**{discount:.1f}%** below market")
            
            with col4:
                strategy = opp.get('recommended_strategy', 'N/A')
                st.caption(f"**{strategy}**")
            
            with col5:
                regime = opp.get('current_regime', 'N/A')
                st.caption(f"Regime: {regime}")
            
            with col6:
                liquidity = opp.get('liquidity_score', 0)
                st.caption(f"Liquidity: {liquidity:.0f}")
            
            # Scores détaillés
            with st.expander("Detailed Scores"):
                col7, col8, col9 = st.columns(3)
                
                with col7:
                    flip_score = opp.get('flip_score', 0)
                    st.metric("FLIP", f"{flip_score:.0f}")
                
                with col8:
                    rent_score = opp.get('rent_score', 0)
                    st.metric("RENT", f"{rent_score:.0f}")
                
                with col9:
                    long_score = opp.get('long_term_score', 0)
                    st.metric("LONG", f"{long_score:.0f}")
                
                # Graphique radar
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=[flip_score, rent_score, long_score],
                    theta=['FLIP', 'RENT', 'LONG'],
                    fill='toself',
                    name='Scores',
                    line=dict(color='#D4AF37'),
                    fillcolor='rgba(212,175,55,0.3)'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color='#D4AF37'),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    height=250,
                    margin=dict(l=20, r=20, t=20, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#F5E6D3')
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
else:
    st.info("No opportunities with these criteria.")

st.caption(f"Last update: {get_dubai_today()}")

"""
Deal Radar - Tech Company Style
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card, progress_bar

st.set_page_config(page_title="Deal Radar", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Deal Radar</div>', unsafe_allow_html=True)

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    strategy_filter = st.selectbox("Strategy", ["All", "FLIP", "RENT", "LONG", "IGNORE"])

with col3:
    min_score = st.slider("Min Score", 0, 100, 50)

with col4:
    regime_filter = st.selectbox("Regime", ["All", "ACCUMULATION", "EXPANSION", "DISTRIBUTION", "RETOURNEMENT"])

# Query
query = """
SELECT * FROM v_active_opportunities
WHERE detection_date = %s AND global_score >= %s
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

# === KPIs ===
if opportunities:
    strategy_counts = {}
    for opp in opportunities:
        s = opp.get('recommended_strategy', 'OTHER')
        strategy_counts[s] = strategy_counts.get(s, 0) + 1
    
    avg_discount = sum(opp.get('discount_pct', 0) or 0 for opp in opportunities) / len(opportunities)
    avg_score = sum(opp.get('global_score', 0) or 0 for opp in opportunities) / len(opportunities)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(kpi_card("Total", "Opportunities", str(len(opportunities)), "accent"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(kpi_card("FLIP", "Strategy", str(strategy_counts.get('FLIP', 0))), unsafe_allow_html=True)
    
    with col3:
        st.markdown(kpi_card("RENT", "Strategy", str(strategy_counts.get('RENT', 0))), unsafe_allow_html=True)
    
    with col4:
        st.markdown(kpi_card("Avg Score", "Quality", f"{avg_score:.0f}%", "green"), unsafe_allow_html=True)
    
    with col5:
        st.markdown(kpi_card("Avg Discount", "Below market", f"{avg_discount:.1f}%"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === MAIN TABLE ===
    st.markdown('<div class="section-title">Opportunities</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">SORTED BY SCORE</div>', unsafe_allow_html=True)
    
    import pandas as pd
    
    df_data = []
    for opp in opportunities:
        df_data.append({
            "Location": f"{opp.get('community', 'N/A')} / {opp.get('building', 'N/A')}",
            "Type": opp.get('rooms_bucket', 'N/A'),
            "Score": opp.get('global_score', 0),
            "Discount": f"{opp.get('discount_pct', 0):.1f}%",
            "Strategy": opp.get('recommended_strategy', 'N/A'),
            "Regime": opp.get('current_regime', 'N/A')
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                min_value=0,
                max_value=100,
                format="%d"
            )
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === CHARTS ===
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Strategy pie
        fig = go.Figure(data=[go.Pie(
            labels=list(strategy_counts.keys()),
            values=list(strategy_counts.values()),
            hole=0.5,
            marker=dict(colors=['#10B981', '#3B82F6', '#F59E0B', '#6B7280']),
            textinfo='label+value',
            textposition='outside',
            textfont=dict(size=11, color='#FFFFFF')
        )])
        
        fig.update_layout(
            title=dict(text='Strategy Distribution', font=dict(size=14, color='#FFFFFF')),
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_c2:
        # Score vs Discount scatter
        scores = [opp.get('global_score', 0) for opp in opportunities]
        discounts = [opp.get('discount_pct', 0) for opp in opportunities]
        names = [f"{opp.get('community', 'N/A')}" for opp in opportunities]
        
        fig = go.Figure(data=[go.Scatter(
            x=discounts,
            y=scores,
            mode='markers',
            marker=dict(
                size=12,
                color=scores,
                colorscale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
                showscale=True,
                colorbar=dict(title='Score', tickfont=dict(color='#FFFFFF'))
            ),
            text=names,
            hovertemplate='%{text}<br>Score: %{y}<br>Discount: %{x}%<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text='Score vs Discount', font=dict(size=14, color='#FFFFFF')),
            height=300,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='Discount %', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Score', gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No opportunities with these criteria.")

st.caption(f"Last update: {get_dubai_today()}")

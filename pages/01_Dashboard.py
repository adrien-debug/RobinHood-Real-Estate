"""
Dashboard - Tech Company Style
Clean, data-focused, professional with symmetric layout
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
from datetime import date, timedelta
from core.utils import get_dubai_today, format_currency, format_percentage
from realtime.refresher import DataRefresher
from core.styles import apply_plecto_style, kpi_card
import pandas as pd

st.set_page_config(page_title="Dashboard", page_icon="", layout="wide", initial_sidebar_state="collapsed")

# Auto-refresh
st_autorefresh(interval=5 * 60 * 1000, key="dashboard_refresh")

# Apply Tech style
apply_plecto_style()

# Sidebar with icons
with st.sidebar:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { width: 70px !important; min-width: 70px !important; }
        [data-testid="stSidebar"][aria-expanded="true"] { width: 250px !important; min-width: 250px !important; }
        .sidebar-icon { font-size: 1.5rem; text-align: center; padding: 1rem 0; cursor: pointer; transition: all 0.2s; }
        .sidebar-icon:hover { color: #00D9A3; }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown('<div class="dashboard-header">Real Estate Intelligence</div>', unsafe_allow_html=True)

# Date selector (compact)
target_date = st.date_input("", value=get_dubai_today(), max_value=get_dubai_today(), label_visibility="collapsed")

# Get data
try:
    with st.spinner(""):
        data = DataRefresher.get_dashboard_data(target_date)
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.stop()

# === KPIs ROW - 6 symmetric cards ===
kpis = data.get('kpis') or {}
num_deals = kpis.get('transactions_count') or 0
avg_price = (kpis.get('avg_price_sqft') or 0) / 1000
opportunities = kpis.get('opportunities_count') or 0
avg_score = kpis.get('avg_opportunity_score') or 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(kpi_card("Deals", "This month", str(num_deals)), unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("Avg Price", "AED/sqft", f"{avg_price:.1f}k"), unsafe_allow_html=True)

with col3:
    st.markdown(kpi_card("Opportunities", "Active", str(opportunities)), unsafe_allow_html=True)

with col4:
    st.markdown(kpi_card("Avg Score", "Quality", f"{avg_score:.0f}%", "green"), unsafe_allow_html=True)

with col5:
    st.markdown(kpi_card("Alerts", "Active", "12"), unsafe_allow_html=True)

with col6:
    st.markdown(kpi_card("Yield", "Average", "7.2%", "accent"), unsafe_allow_html=True)

st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

# === ROW 2: 3 symmetric charts ===
opportunities_list = data.get('top_opportunities', [])[:8]

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown('<div class="section-title">Score Distribution</div>', unsafe_allow_html=True)
    
    if opportunities_list:
        scores = [opp.get('global_score', 0) for opp in opportunities_list]
        bins = ['0-40', '40-60', '60-80', '80+']
        counts = [
            sum(1 for s in scores if s < 40),
            sum(1 for s in scores if 40 <= s < 60),
            sum(1 for s in scores if 60 <= s < 80),
            sum(1 for s in scores if s >= 80)
        ]
        
        fig = go.Figure(data=[go.Bar(
            x=bins, y=counts,
            marker_color=['#EF4444', '#F59E0B', '#3B82F6', '#10B981'],
            text=counts, textposition='outside', textfont=dict(color='#FFFFFF', size=14)
        )])
        fig.update_layout(
            height=220, margin=dict(l=20, r=20, t=20, b=30),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)', size=11),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', showticklabels=False)
        )
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown('<div class="section-title">Strategy Mix</div>', unsafe_allow_html=True)
    
    if opportunities_list:
        strategy_counts = {}
        for opp in opportunities_list:
            s = opp.get('recommended_strategy', 'OTHER')
            strategy_counts[s] = strategy_counts.get(s, 0) + 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(strategy_counts.keys()),
            values=list(strategy_counts.values()),
            hole=0.65,
            marker=dict(colors=['#10B981', '#3B82F6', '#F59E0B', '#6B7280']),
            textinfo='percent', textposition='outside',
            textfont=dict(size=12, color='#FFFFFF')
        )])
        fig.update_layout(
            height=220, margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[dict(
                text=f'<b>{len(opportunities_list)}</b>', x=0.5, y=0.5,
                font=dict(size=28, color='#FFFFFF'), showarrow=False
            )]
        )
        st.plotly_chart(fig, use_container_width=True)

with col_c:
    st.markdown('<div class="section-title">Discount Range</div>', unsafe_allow_html=True)
    
    if opportunities_list:
        discounts = [opp.get('discount_pct', 0) for opp in opportunities_list]
        
        fig = go.Figure(data=[go.Histogram(
            x=discounts, nbinsx=6,
            marker_color='#10B981', opacity=0.85
        )])
        fig.update_layout(
            height=220, margin=dict(l=20, r=20, t=20, b=30),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)', size=11),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='%'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', showticklabels=False),
            bargap=0.15
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

# === ROW 3: 2 symmetric columns - Table + Regimes/Brief ===
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="section-title">Top Opportunities</div>', unsafe_allow_html=True)
    
    if opportunities_list:
        table_data = []
        for i, opp in enumerate(opportunities_list, 1):
            table_data.append({
                "#": i,
                "Location": f"{opp.get('community', '')} / {opp.get('building', '')}",
                "Type": opp.get('rooms_bucket', ''),
                "Score": int(opp.get('global_score', 0)),
                "Discount": f"{opp.get('discount_pct', 0):.1f}%",
                "Strategy": opp.get('recommended_strategy', '')
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(
            df, use_container_width=True, hide_index=True, height=280,
            column_config={
                "#": st.column_config.NumberColumn(width="small"),
                "Location": st.column_config.TextColumn(width="large"),
                "Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
            }
        )

with col_right:
    # 2 sub-columns for symmetry
    sub1, sub2 = st.columns(2)
    
    with sub1:
        st.markdown('<div class="section-title">Market Regimes</div>', unsafe_allow_html=True)
        
        regimes = data.get('regimes', [])[:4]
        if regimes:
            for r in regimes:
                regime = r.get('regime', 'NEUTRAL')
                colors = {'ACCUMULATION': '#10B981', 'EXPANSION': '#3B82F6', 'DISTRIBUTION': '#F59E0B', 'RETOURNEMENT': '#EF4444', 'NEUTRAL': '#6B7280'}
                color = colors.get(regime, '#6B7280')
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 0.6rem; margin-bottom: 0.4rem; background: rgba(19,29,50,0.8); border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                    <span style="color: #FFF; font-size: 0.8rem;">{r.get('community', '')[:12]}</span>
                    <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: 600;">{regime[:4]}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No data")
    
    with sub2:
        st.markdown('<div class="section-title">CIO Brief</div>', unsafe_allow_html=True)
        
        brief = data.get('brief')
        if brief:
            st.markdown(f"""
            <div style="background: rgba(19,29,50,0.8); border-radius: 8px; padding: 1rem; border: 1px solid rgba(255,255,255,0.05);">
                <div style="color: #10B981; font-size: 0.7rem; font-weight: 600; margin-bottom: 0.3rem;">RISK</div>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.75rem; margin-bottom: 0.8rem; line-height: 1.4;">{brief.get('main_risk', '')[:80]}...</div>
                <div style="color: #3B82F6; font-size: 0.7rem; font-weight: 600; margin-bottom: 0.3rem;">ACTION</div>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.75rem; line-height: 1.4;">{brief.get('strategic_recommendation', '')[:80]}...</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No brief")

st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

# === ROW 4: 4 symmetric mini-charts ===
col_1, col_2, col_3, col_4 = st.columns(4)

with col_1:
    st.markdown('<div class="section-title" style="font-size: 0.85rem;">By Type</div>', unsafe_allow_html=True)
    
    if opportunities_list:
        type_counts = {}
        for opp in opportunities_list:
            t = opp.get('rooms_bucket', 'Other')
            type_counts[t] = type_counts.get(t, 0) + 1
        
        fig = go.Figure(data=[go.Bar(
            x=list(type_counts.keys()), y=list(type_counts.values()),
            marker_color='#3B82F6', text=list(type_counts.values()),
            textposition='outside', textfont=dict(color='#FFF', size=11)
        )])
        fig.update_layout(
            height=150, margin=dict(l=10, r=10, t=10, b=25),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.6)', size=9),
            xaxis=dict(gridcolor='rgba(0,0,0,0)'), yaxis=dict(visible=False)
        )
        st.plotly_chart(fig, use_container_width=True)

with col_2:
    st.markdown('<div class="section-title" style="font-size: 0.85rem;">Score vs Discount</div>', unsafe_allow_html=True)
    
    if opportunities_list:
        fig = go.Figure(data=[go.Scatter(
            x=[opp.get('discount_pct', 0) for opp in opportunities_list],
            y=[opp.get('global_score', 0) for opp in opportunities_list],
            mode='markers', marker=dict(size=10, color='#10B981', opacity=0.8)
        )])
        fig.update_layout(
            height=150, margin=dict(l=25, r=10, t=10, b=25),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.6)', size=9),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Disc.'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Score')
        )
        st.plotly_chart(fig, use_container_width=True)

with col_3:
    st.markdown('<div class="section-title" style="font-size: 0.85rem;">Price Range</div>', unsafe_allow_html=True)
    
    if opportunities_list:
        prices = [opp.get('area_sqft', 0) * 1500 / 1000000 for opp in opportunities_list]  # Estimate in M
        fig = go.Figure(data=[go.Box(
            y=prices, marker_color='#F59E0B', boxmean=True,
            fillcolor='rgba(245,158,11,0.3)', line=dict(color='#F59E0B')
        )])
        fig.update_layout(
            height=150, margin=dict(l=25, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.6)', size=9),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='AED M')
        )
        st.plotly_chart(fig, use_container_width=True)

with col_4:
    st.markdown('<div class="section-title" style="font-size: 0.85rem;">Quality Gauge</div>', unsafe_allow_html=True)
    
    avg = avg_score if avg_score else 75
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg,
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor='rgba(255,255,255,0.3)'),
            bar=dict(color='#10B981'),
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            steps=[
                dict(range=[0, 40], color='rgba(239,68,68,0.2)'),
                dict(range=[40, 70], color='rgba(245,158,11,0.2)'),
                dict(range=[70, 100], color='rgba(16,185,129,0.2)')
            ]
        ),
        number=dict(suffix='%', font=dict(color='#FFFFFF', size=20))
    ))
    fig.update_layout(
        height=150, margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFFFFF')
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
st.caption(f"Last update: {get_dubai_today()}")

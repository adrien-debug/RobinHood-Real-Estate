"""
Dashboard - Tech Company Style
Clean, data-focused, professional
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
from core.utils import get_dubai_today, format_currency, format_percentage
from realtime.refresher import DataRefresher
from core.styles import apply_plecto_style, kpi_card, progress_bar

st.set_page_config(page_title="Dashboard", page_icon="", layout="wide")

# Auto-refresh
st_autorefresh(interval=5 * 60 * 1000, key="dashboard_refresh")

# Apply Tech style
apply_plecto_style()

# Header
st.markdown('<div class="dashboard-header">Real Estate Intelligence</div>', unsafe_allow_html=True)

# Date selector
target_date = st.date_input("Date", value=get_dubai_today(), max_value=get_dubai_today())

# Get data
try:
    with st.spinner("Loading..."):
        data = DataRefresher.get_dashboard_data(target_date)
except Exception as e:
    st.error(f"Error: {str(e)}")
    st.stop()

# === KPIs ROW ===
kpis = data.get('kpis') or {}
num_deals = kpis.get('transactions_count') or 0
avg_price = (kpis.get('avg_price_sqft') or 0) / 1000
opportunities = kpis.get('opportunities_count') or 0
avg_score = kpis.get('avg_opportunity_score') or 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(kpi_card("# of Deals", "Current month", str(num_deals)), unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("Avg Price/sqft", "Current month", f"AED {avg_price:.1f}k"), unsafe_allow_html=True)

with col3:
    st.markdown(kpi_card("# of Opportunities", "Current month", str(opportunities)), unsafe_allow_html=True)

with col4:
    st.markdown(kpi_card("Avg Score", "Current month", f"{avg_score:.0f}%", "green"), unsafe_allow_html=True)

with col5:
    st.markdown(kpi_card("Active Alerts", "Current month", "12", "accent"), unsafe_allow_html=True)

st.markdown("---")

# === MAIN CONTENT - 2 COLUMNS ===
col_left, col_right = st.columns([2, 1])

with col_left:
    # === OPPORTUNITIES TABLE ===
    st.markdown('<div class="section-title">Top Opportunities</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Current month</div>', unsafe_allow_html=True)
    
    opportunities_list = data.get('top_opportunities', [])[:8]
    
    if opportunities_list:
        # Build table HTML
        table_html = """
        <div class="data-card">
            <table class="styled-table">
                <thead>
                    <tr>
                        <th></th>
                        <th>Location</th>
                        <th>Type</th>
                        <th>Score</th>
                        <th>Discount</th>
                        <th>Strategy</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, opp in enumerate(opportunities_list, 1):
            score = opp.get('global_score', 0)
            discount = opp.get('discount_pct', 0)
            
            # Color based on score
            if score >= 80:
                score_color = "#10B981"
            elif score >= 60:
                score_color = "#F59E0B"
            else:
                score_color = "#EF4444"
            
            table_html += f"""
                <tr>
                    <td class="table-rank">{i}</td>
                    <td class="table-name">{opp.get('community', 'N/A')} / {opp.get('building', 'N/A')}</td>
                    <td>{opp.get('rooms_bucket', 'N/A')}</td>
                    <td><span style="background: {score_color}; color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-weight: 600;">{score:.0f}</span></td>
                    <td class="table-value" style="color: #10B981;">{discount:.1f}%</td>
                    <td>{opp.get('recommended_strategy', 'N/A')}</td>
                </tr>
            """
        
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No opportunities found.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === CIO BRIEF ===
    st.markdown('<div class="section-title">CIO Brief</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Daily intelligence</div>', unsafe_allow_html=True)
    
    brief = data.get('brief')
    
    if brief:
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown("**Main Risk**")
            st.write(brief.get('main_risk', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_b2:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown("**Recommendation**")
            st.write(brief.get('strategic_recommendation', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No brief available.")

with col_right:
    # === STRATEGY DISTRIBUTION PIE ===
    st.markdown('<div class="section-title">Strategy Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Current month</div>', unsafe_allow_html=True)
    
    if opportunities_list:
        strategy_counts = {}
        for opp in opportunities_list:
            strategy = opp.get('recommended_strategy', 'OTHER')
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        fig = go.Figure(data=[go.Pie(
            labels=list(strategy_counts.keys()),
            values=list(strategy_counts.values()),
            hole=0.6,
            marker=dict(colors=['#10B981', '#3B82F6', '#F59E0B', '#6B7280']),
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=11, color='#FFFFFF')
        )])
        
        fig.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[dict(
                text=f'<b>{len(opportunities_list)}</b><br>Total',
                x=0.5, y=0.5,
                font=dict(size=16, color='#FFFFFF'),
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === MARKET REGIMES ===
    st.markdown('<div class="section-title">Market Regimes</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Zone analysis</div>', unsafe_allow_html=True)
    
    regimes = data.get('regimes', [])[:6]
    
    if regimes:
        regime_html = '<div class="data-card">'
        
        for r in regimes:
            regime = r.get('regime', 'NEUTRAL')
            community = r.get('community', 'N/A')
            confidence = r.get('confidence_score', 0)
            
            # Color based on regime
            colors = {
                'ACCUMULATION': '#10B981',
                'EXPANSION': '#3B82F6',
                'DISTRIBUTION': '#F59E0B',
                'RETOURNEMENT': '#EF4444',
                'NEUTRAL': '#6B7280'
            }
            color = colors.get(regime, '#6B7280')
            
            regime_html += f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <div>
                    <div style="color: #FFFFFF; font-weight: 500; font-size: 0.9rem;">{community}</div>
                    <div style="color: rgba(255,255,255,0.4); font-size: 0.75rem;">Confidence: {confidence:.0%}</div>
                </div>
                <span style="background: {color}; color: white; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.7rem; font-weight: 600;">{regime}</span>
            </div>
            """
        
        regime_html += '</div>'
        st.markdown(regime_html, unsafe_allow_html=True)
    else:
        st.info("No regimes calculated.")

st.markdown("---")

# === CHARTS ROW ===
st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Performance metrics</div>', unsafe_allow_html=True)

col_c1, col_c2 = st.columns(2)

with col_c1:
    # Score distribution bar chart
    if opportunities_list:
        scores = [opp.get('global_score', 0) for opp in opportunities_list]
        bins = ['0-40', '40-60', '60-80', '80-100']
        counts = [
            sum(1 for s in scores if s < 40),
            sum(1 for s in scores if 40 <= s < 60),
            sum(1 for s in scores if 60 <= s < 80),
            sum(1 for s in scores if s >= 80)
        ]
        
        fig = go.Figure(data=[
            go.Bar(
                x=bins,
                y=counts,
                marker_color=['#EF4444', '#F59E0B', '#3B82F6', '#10B981'],
                text=counts,
                textposition='outside',
                textfont=dict(color='#FFFFFF')
            )
        ])
        
        fig.update_layout(
            title=dict(text='Score Distribution', font=dict(size=14, color='#FFFFFF')),
            height=280,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col_c2:
    # Discount distribution
    if opportunities_list:
        discounts = [opp.get('discount_pct', 0) for opp in opportunities_list]
        
        fig = go.Figure(data=[
            go.Histogram(
                x=discounts,
                nbinsx=8,
                marker_color='#10B981',
                opacity=0.8
            )
        ])
        
        fig.update_layout(
            title=dict(text='Discount Distribution (%)', font=dict(size=14, color='#FFFFFF')),
            height=280,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Discount %'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Count'),
            bargap=0.1
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"Last update: {get_dubai_today()}")

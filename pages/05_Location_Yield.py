"""
Location Yield - Tech Company Style
"""
import streamlit as st
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(page_title="Location Yield", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Location Yield</div>', unsafe_allow_html=True)

# Filters
col1, col2 = st.columns([1, 3])

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    min_yield = st.slider("Min Yield (%)", 0.0, 15.0, 5.0, 0.5)

st.markdown("---")

# Query
query = """
SELECT 
    community,
    rooms_bucket,
    AVG(price_per_sqft) as avg_price,
    AVG(annual_yield) as avg_yield,
    COUNT(*) as tx_count
FROM transactions
WHERE transaction_date >= %s - INTERVAL '30 days'
    AND annual_yield IS NOT NULL
    AND annual_yield >= %s
GROUP BY community, rooms_bucket
HAVING COUNT(*) >= 3
ORDER BY avg_yield DESC
LIMIT 30
"""

yields = db.execute_query(query, (target_date, min_yield))

if yields:
    # === KPIs ===
    avg_yield = sum(y.get('avg_yield', 0) for y in yields) / len(yields)
    max_yield = max(y.get('avg_yield', 0) for y in yields)
    total_zones = len(set(y.get('community') for y in yields))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(kpi_card("Zones", "Analysed", str(total_zones), "accent"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(kpi_card("Avg Yield", "Annual", f"{avg_yield:.2f}%", "green"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(kpi_card("Max Yield", "Annual", f"{max_yield:.2f}%"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(kpi_card("Segments", "Total", str(len(yields))), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === TABLE ===
    st.markdown('<div class="section-title">Top Yields</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">By zone and type</div>', unsafe_allow_html=True)
    
    table_html = """
    <div class="data-card">
        <table class="styled-table">
            <thead>
                <tr>
                    <th></th>
                    <th>Zone</th>
                    <th>Type</th>
                    <th>Avg Price/sqft</th>
                    <th>Yield</th>
                    <th>Volume</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i, y in enumerate(yields, 1):
        yld = y.get('avg_yield', 0)
        price = y.get('avg_price', 0)
        
        # Yield color
        if yld >= 8:
            yield_bg = "#10B981"
        elif yld >= 6:
            yield_bg = "#3B82F6"
        else:
            yield_bg = "#F59E0B"
        
        table_html += f"""
            <tr>
                <td class="table-rank">{i}</td>
                <td class="table-name">{y.get('community', 'N/A')}</td>
                <td>{y.get('rooms_bucket', 'N/A')}</td>
                <td>{price:.0f} AED</td>
                <td><span style="background: {yield_bg}; color: white; padding: 0.25rem 0.6rem; border-radius: 4px; font-weight: 600; font-size: 0.85rem;">{yld:.2f}%</span></td>
                <td>{y.get('tx_count', 0)}</td>
            </tr>
        """
    
    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === CHARTS ===
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Yield bar chart
        import pandas as pd
        df = pd.DataFrame(yields[:15])
        df['label'] = df['community'].str[:15] + ' (' + df['rooms_bucket'].astype(str) + ')'
        
        fig = go.Figure(data=[go.Bar(
            x=df['avg_yield'],
            y=df['label'],
            orientation='h',
            marker_color='#10B981',
            text=[f"{y:.1f}%" for y in df['avg_yield']],
            textposition='outside',
            textfont=dict(color='#FFFFFF')
        )])
        
        fig.update_layout(
            title=dict(text='Top 15 Yields', font=dict(size=14, color='#FFFFFF')),
            height=400,
            margin=dict(l=150, r=50, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='Yield %', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', autorange='reversed')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_c2:
        # Scatter
        yields_vals = [y.get('avg_yield', 0) for y in yields]
        prices_vals = [y.get('avg_price', 0) for y in yields]
        names = [f"{y.get('community', '')} ({y.get('rooms_bucket', '')})" for y in yields]
        
        fig = go.Figure(data=[go.Scatter(
            x=prices_vals,
            y=yields_vals,
            mode='markers',
            marker=dict(
                size=12,
                color=yields_vals,
                colorscale=[[0, '#F59E0B'], [0.5, '#3B82F6'], [1, '#10B981']],
                showscale=True,
                colorbar=dict(title='Yield %', tickfont=dict(color='#FFFFFF'))
            ),
            text=names,
            hovertemplate='%{text}<br>Price: %{x:.0f} AED/sqft<br>Yield: %{y:.2f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text='Yield vs Price', font=dict(size=14, color='#FFFFFF')),
            height=400,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='Price/sqft (AED)', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Yield %', gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No data with these criteria.")

st.caption(f"Last update: {get_dubai_today()}")

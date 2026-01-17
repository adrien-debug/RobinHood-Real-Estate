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
    min_transactions = st.slider("Min Transactions", 1, 20, 3)

st.markdown("---")

# Query - use market baselines which have computed metrics
query = """
SELECT 
    community,
    rooms_bucket,
    median_price_per_sqft as avg_price,
    momentum,
    transaction_count as tx_count,
    volatility
FROM market_baselines
WHERE calculation_date = %s
    AND window_days = 30
    AND transaction_count >= %s
ORDER BY momentum DESC NULLS LAST
LIMIT 30
"""

yields = db.execute_query(query, (target_date, min_transactions))

# Fallback to transactions if no baselines
if not yields:
    query_fallback = """
    SELECT 
        community,
        rooms_bucket,
        AVG(price_per_sqft) as avg_price,
        COUNT(*) as tx_count
    FROM transactions
    WHERE transaction_date >= %s - INTERVAL '30 days'
        AND price_per_sqft IS NOT NULL
    GROUP BY community, rooms_bucket
    HAVING COUNT(*) >= %s
    ORDER BY AVG(price_per_sqft) DESC
    LIMIT 30
    """
    yields = db.execute_query(query_fallback, (target_date, min_transactions))

if yields:
    # === KPIs ===
    total_zones = len(set(y.get('community') for y in yields if y.get('community')))
    avg_momentum = sum((y.get('momentum') or 0) for y in yields) / len(yields) * 100
    total_tx = sum(y.get('tx_count', 0) for y in yields)
    avg_price = sum(y.get('avg_price', 0) or 0 for y in yields) / len(yields)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(kpi_card("Zones", "Analysed", str(total_zones), "accent"), unsafe_allow_html=True)
    
    with col2:
        color = "green" if avg_momentum > 0 else "default"
        st.markdown(kpi_card("Avg Momentum", "30 days", f"{avg_momentum:+.1f}%", color), unsafe_allow_html=True)
    
    with col3:
        st.markdown(kpi_card("Transactions", "Total", str(total_tx)), unsafe_allow_html=True)
    
    with col4:
        st.markdown(kpi_card("Avg Price", "AED/sqft", f"{avg_price:.0f}"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === TABLE ===
    st.markdown('<div class="section-title">Market Performance by Zone</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">SORTED BY MOMENTUM</div>', unsafe_allow_html=True)
    
    import pandas as pd
    
    df_data = []
    for y in yields:
        momentum = (y.get('momentum') or 0) * 100
        df_data.append({
            "Zone": y.get('community', 'N/A'),
            "Type": y.get('rooms_bucket', 'N/A'),
            "Price/sqft": f"{y.get('avg_price', 0) or 0:.0f} AED",
            "Momentum": momentum,
            "Volume": y.get('tx_count', 0)
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Momentum": st.column_config.NumberColumn(
                "Momentum %",
                format="%.1f%%"
            )
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === CHARTS ===
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Momentum bar chart
        import pandas as pd
        df = pd.DataFrame(yields[:15])
        df['label'] = df['community'].str[:12] + ' (' + df['rooms_bucket'].astype(str) + ')'
        df['momentum_pct'] = df['momentum'].apply(lambda x: (x or 0) * 100)
        
        colors = ['#10B981' if m > 0 else '#EF4444' for m in df['momentum_pct']]
        
        fig = go.Figure(data=[go.Bar(
            x=df['momentum_pct'],
            y=df['label'],
            orientation='h',
            marker_color=colors,
            text=[f"{m:.1f}%" for m in df['momentum_pct']],
            textposition='outside',
            textfont=dict(color='#FFFFFF')
        )])
        
        fig.update_layout(
            title=dict(text='Momentum by Zone', font=dict(size=14, color='#FFFFFF')),
            height=400,
            margin=dict(l=120, r=50, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='Momentum %', gridcolor='rgba(255,255,255,0.05)', zeroline=True, zerolinecolor='rgba(255,255,255,0.2)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', autorange='reversed')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_c2:
        # Price vs Volume scatter
        prices_vals = [y.get('avg_price', 0) or 0 for y in yields]
        volumes = [y.get('tx_count', 0) for y in yields]
        momentums = [(y.get('momentum') or 0) * 100 for y in yields]
        names = [f"{y.get('community', '')} ({y.get('rooms_bucket', '')})" for y in yields]
        
        fig = go.Figure(data=[go.Scatter(
            x=prices_vals,
            y=volumes,
            mode='markers',
            marker=dict(
                size=12,
                color=momentums,
                colorscale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
                showscale=True,
                colorbar=dict(title='Mom %', tickfont=dict(color='#FFFFFF'))
            ),
            text=names,
            hovertemplate='%{text}<br>Price: %{x:.0f} AED/sqft<br>Volume: %{y}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text='Price vs Volume', font=dict(size=14, color='#FFFFFF')),
            height=400,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='Price/sqft (AED)', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Transactions', gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No data with these criteria. Try lowering the minimum transactions filter.")

st.caption(f"Last update: {get_dubai_today()}")

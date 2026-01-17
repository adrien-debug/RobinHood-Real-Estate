"""
Page Zones / Projets / Buildings - Dubai Premium Gold Design
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today
from core.styles import apply_plecto_style, kpi_card, status_badge

st.set_page_config(page_title="Zones & Buildings", page_icon="", layout="wide")

# Apply Premium Gold style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Zones & Buildings</div>', unsafe_allow_html=True)

target_date = st.date_input("Date", value=get_dubai_today())

# Sélection de la zone
communities = db.execute_query("""
    SELECT DISTINCT community, COUNT(*) as tx_count
    FROM transactions
    WHERE transaction_date >= %s - INTERVAL '30 days'
    GROUP BY community
    ORDER BY tx_count DESC
""", (target_date,))

community_list = [c['community'] for c in communities if c['community']]
selected_community = st.selectbox("Community", community_list)

if selected_community:
    # Baselines pour cette zone
    baselines = db.execute_query("""
        SELECT * FROM market_baselines
        WHERE calculation_date = %s
            AND community = %s
            AND window_days = 30
        ORDER BY transaction_count DESC
    """, (target_date, selected_community))
    
    # Régime de marché
    regime = db.execute_query("""
        SELECT * FROM market_regimes
        WHERE regime_date = %s
            AND community = %s
        LIMIT 1
    """, (target_date, selected_community))
    
    # Affichage
    st.markdown(f'<div class="section-title">{selected_community}</div>', unsafe_allow_html=True)
    
    if regime:
        r = regime[0]
        regime_name = r.get('regime', 'N/A')
        confidence = r.get('confidence_score', 0)
        
        st.info(f"**Regime: {regime_name}** (confidence: {confidence:.2f})")
    
    st.markdown("---")
    
    # Métriques par type de bien
    st.markdown('<div class="section-title">Metrics by Type</div>', unsafe_allow_html=True)
    
    if baselines:
        for b in baselines:
            with st.expander(f"{b.get('rooms_bucket', 'N/A')} - {b.get('transaction_count', 0)} transactions"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    median = b.get('median_price_per_sqft', 0)
                    st.metric("Median price/sqft", f"{median:.0f} AED")
                
                with col2:
                    momentum = b.get('momentum', 0)
                    momentum_pct = (momentum * 100) if momentum else 0
                    st.metric("Momentum", f"{momentum_pct:+.1f}%")
                
                with col3:
                    volatility = b.get('volatility', 0)
                    vol_pct = (volatility * 100) if volatility else 0
                    st.metric("Volatility", f"{vol_pct:.1f}%")
    else:
        st.info("Not enough data to calculate baselines.")
    
    st.markdown("---")
    
    # Graphique : évolution des prix
    st.markdown('<div class="section-title">Price Evolution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Last 30 days</div>', unsafe_allow_html=True)
    
    price_history = db.execute_query("""
        SELECT transaction_date, AVG(price_per_sqft) as avg_price, COUNT(*) as count
        FROM transactions
        WHERE community = %s
            AND transaction_date >= %s - INTERVAL '30 days'
            AND transaction_date <= %s
            AND price_per_sqft IS NOT NULL
        GROUP BY transaction_date
        ORDER BY transaction_date
    """, (selected_community, target_date, target_date))
    
    if price_history:
        import pandas as pd
        df = pd.DataFrame(price_history)
        
        fig = go.Figure()
        
        # Prix moyen
        fig.add_trace(go.Scatter(
            x=df['transaction_date'],
            y=df['avg_price'],
            mode='lines+markers',
            name='Avg price/sqft',
            line=dict(color='#D4AF37', width=3),
            marker=dict(size=8, color='#D4AF37')
        ))
        
        # Volume (axe secondaire)
        fig.add_trace(go.Bar(
            x=df['transaction_date'],
            y=df['count'],
            name='Volume',
            yaxis='y2',
            opacity=0.3,
            marker_color='#CD7F32'
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(title='Price AED/sqft', color='#D4AF37'),
            yaxis2=dict(title='Volume', overlaying='y', side='right', color='#CD7F32'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F5E6D3')
        )
        
        fig.update_xaxes(gridcolor='rgba(212,175,55,0.1)')
        fig.update_yaxes(gridcolor='rgba(212,175,55,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for chart.")

else:
    st.info("Select a zone.")

st.caption(f"Last update: {get_dubai_today()}")

"""
Page Zones / Projets / Buildings - Analyse par localisation (Style Plecto)
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today
from core.styles import apply_plecto_style, kpi_card, status_badge

st.set_page_config(page_title="Zones & Buildings", page_icon="📍", layout="wide")

# Apply Plecto style
apply_plecto_style()

st.markdown('<div class="dashboard-header">📍 Zones & Buildings</div>', unsafe_allow_html=True)

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
    st.subheader(f"📊 {selected_community}")
    
    if regime:
        r = regime[0]
        regime_name = r.get('regime', 'N/A')
        confidence = r.get('confidence_score', 0)
        
        emoji = {
            'ACCUMULATION': '🟢',
            'EXPANSION': '🔵',
            'DISTRIBUTION': '🟡',
            'RETOURNEMENT': '🔴',
            'NEUTRAL': '⚪'
        }.get(regime_name, '⚪')
        
        st.info(f"{emoji} **Régime : {regime_name}** (confiance: {confidence:.2f})")
    
    st.markdown("---")
    
    # Métriques par type de bien
    st.subheader("📈 Métriques par type")
    
    if baselines:
        for b in baselines:
            with st.expander(f"{b.get('rooms_bucket', 'N/A')} - {b.get('transaction_count', 0)} transactions"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    median = b.get('median_price_per_sqft', 0)
                    st.metric("Médiane prix/sqft", f"{median:.0f} AED")
                
                with col2:
                    momentum = b.get('momentum', 0)
                    momentum_pct = (momentum * 100) if momentum else 0
                    st.metric("Momentum", f"{momentum_pct:+.1f}%")
                
                with col3:
                    volatility = b.get('volatility', 0)
                    vol_pct = (volatility * 100) if volatility else 0
                    st.metric("Volatilité", f"{vol_pct:.1f}%")
    else:
        st.info("Pas assez de données pour calculer les baselines.")
    
    st.markdown("---")
    
    # Graphique : évolution des prix
    st.subheader("📊 Évolution des prix (30 derniers jours)")
    
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
            name='Prix moyen/sqft',
            line=dict(color='#3b82f6', width=2)
        ))
        
        # Volume (axe secondaire)
        fig.add_trace(go.Bar(
            x=df['transaction_date'],
            y=df['count'],
            name='Volume',
            yaxis='y2',
            opacity=0.3,
            marker_color='#10b981'
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(title='Prix AED/sqft'),
            yaxis2=dict(title='Volume', overlaying='y', side='right'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas assez de données pour le graphique.")

else:
    st.info("Sélectionnez une zone.")

st.caption(f"Dernière mise à jour : {get_dubai_today()}")

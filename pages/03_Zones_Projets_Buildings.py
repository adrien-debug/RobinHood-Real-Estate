"""
Zones & Buildings - Tech Company Style
"""
import streamlit as st
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(page_title="Zones & Buildings", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Zones & Buildings</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 3])

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    communities = db.execute_query("""
        SELECT DISTINCT community, COUNT(*) as tx_count
        FROM transactions
        WHERE transaction_date >= %s - INTERVAL '30 days'
        GROUP BY community
        ORDER BY tx_count DESC
    """, (target_date,))
    
    community_list = [c['community'] for c in communities if c['community']]
    selected_community = st.selectbox("Select Zone", community_list)

st.markdown("---")

if selected_community:
    # Get data
    baselines = db.execute_query("""
        SELECT * FROM market_baselines
        WHERE calculation_date = %s AND community = %s AND window_days = 30
        ORDER BY transaction_count DESC
    """, (target_date, selected_community))
    
    regime = db.execute_query("""
        SELECT * FROM market_regimes
        WHERE regime_date = %s AND community = %s LIMIT 1
    """, (target_date, selected_community))
    
    # === HEADER ===
    st.markdown(f'<div class="section-title">{selected_community}</div>', unsafe_allow_html=True)
    
    if regime:
        r = regime[0]
        regime_name = r.get('regime', 'NEUTRAL')
        confidence = r.get('confidence_score', 0)
        
        colors = {
            'ACCUMULATION': '#10B981',
            'EXPANSION': '#3B82F6',
            'DISTRIBUTION': '#F59E0B',
            'RETOURNEMENT': '#EF4444',
            'NEUTRAL': '#6B7280'
        }
        color = colors.get(regime_name, '#6B7280')
        
        st.markdown(f"""
        <div style="display: inline-flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
            <span style="background: {color}; color: white; padding: 0.4rem 1rem; border-radius: 6px; font-weight: 600; font-size: 0.85rem;">{regime_name}</span>
            <span style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">Confidence: {confidence:.0%}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # === METRICS BY TYPE ===
    if baselines:
        st.markdown('<div class="section-subtitle">Metrics by property type</div>', unsafe_allow_html=True)
        
        cols = st.columns(len(baselines[:4]))
        
        for i, b in enumerate(baselines[:4]):
            with cols[i]:
                median = b.get('median_price_per_sqft', 0)
                momentum = (b.get('momentum', 0) or 0) * 100
                tx_count = b.get('transaction_count', 0)
                
                st.markdown(f"""
                <div class="data-card" style="text-align: center;">
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">{b.get('rooms_bucket', 'N/A')}</div>
                    <div style="color: #FFFFFF; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem;">{median:.0f}</div>
                    <div style="color: rgba(255,255,255,0.4); font-size: 0.7rem;">AED/sqft</div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                            <span style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">Momentum</span>
                            <span style="color: {'#10B981' if momentum > 0 else '#EF4444' if momentum < 0 else '#6B7280'}; font-size: 0.8rem; font-weight: 600;">{momentum:+.1f}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: rgba(255,255,255,0.5); font-size: 0.7rem;">Volume</span>
                            <span style="color: #FFFFFF; font-size: 0.8rem; font-weight: 500;">{tx_count}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === PRICE CHART ===
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
        
        # Price line
        fig.add_trace(go.Scatter(
            x=df['transaction_date'],
            y=df['avg_price'],
            mode='lines+markers',
            name='Avg Price',
            line=dict(color='#10B981', width=3),
            marker=dict(size=6, color='#10B981'),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))
        
        # Volume bars
        fig.add_trace(go.Bar(
            x=df['transaction_date'],
            y=df['count'],
            name='Volume',
            yaxis='y2',
            marker_color='rgba(59, 130, 246, 0.5)',
            opacity=0.6
        ))
        
        fig.update_layout(
            height=350,
            margin=dict(l=40, r=40, t=20, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='AED/sqft', gridcolor='rgba(255,255,255,0.05)', side='left'),
            yaxis2=dict(title='Volume', overlaying='y', side='right', gridcolor='rgba(255,255,255,0.05)'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for chart.")

else:
    st.info("Select a zone.")

st.caption(f"Last update: {get_dubai_today()}")

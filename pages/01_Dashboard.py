"""
Dashboard - Bloomberg-Style Real Estate Intelligence
Advanced analytics with projections, predictions, and market insights
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta, datetime
import numpy as np
import pandas as pd
from core.utils import get_dubai_today, format_currency, format_percentage
from realtime.refresher import DataRefresher
from core.styles import apply_plecto_style, kpi_card
from core.db import db
import math

st.set_page_config(page_title="Dashboard", page_icon="", layout="wide", initial_sidebar_state="collapsed")

# Auto-refresh
st_autorefresh(interval=5 * 60 * 1000, key="dashboard_refresh")

# Apply Tech style
apply_plecto_style()

# === ADVANCED ANALYTICS FUNCTIONS ===

def calculate_market_rsi(prices, period=14):
    """Calculate RSI-like indicator for market momentum"""
    if len(prices) < period + 1:
        return 50

    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def generate_price_projections(historical_prices, periods=6):
    """Generate 3-6 month price projections using trend analysis"""
    if len(historical_prices) < 3:
        return [historical_prices[-1]] * periods if historical_prices else [0] * periods

    # Calculate trend using linear regression
    x = np.arange(len(historical_prices))
    y = np.array(historical_prices)

    # Simple trend calculation
    slope = np.polyfit(x, y, 1)[0]

    # Add some volatility based on historical data
    volatility = np.std(np.diff(y)) if len(y) > 1 else y[-1] * 0.05

    projections = []
    last_price = y[-1]

    for i in range(1, periods + 1):
        # Trend component
        trend_projection = last_price + (slope * i)

        # Add seasonal adjustment (simplified)
        seasonal_factor = 1 + 0.02 * math.sin(2 * math.pi * i / 12)  # Monthly seasonality

        # Add random component
        random_factor = np.random.normal(0, volatility * 0.1)

        projected_price = trend_projection * seasonal_factor + random_factor
        projections.append(max(0, projected_price))  # No negative prices

    return projections

def create_market_heatmap(zone_data):
    """Create interactive heatmap for zone analysis"""
    if not zone_data:
        return None

    # Prepare data for heatmap
    zones = []
    prices = []
    volumes = []
    scores = []

    for zone in zone_data[:20]:  # Top 20 zones
        zones.append(zone.get('community', 'Unknown'))
        prices.append(zone.get('avg_price_sqft', 0))
        volumes.append(zone.get('transaction_count', 0))
        scores.append(zone.get('opportunity_score', 50))

    # Normalize data for visualization
    max_price = max(prices) if prices else 1
    max_volume = max(volumes) if volumes else 1

    norm_prices = [p/max_price for p in prices]
    norm_volumes = [v/max_volume for v in volumes]

    # Create heatmap data
    heatmap_data = []
    for i, zone in enumerate(zones):
        heatmap_data.append({
            'Zone': zone,
            'Price': prices[i],
            'Volume': volumes[i],
            'Score': scores[i],
            'Price_Norm': norm_prices[i],
            'Volume_Norm': norm_volumes[i]
        })

    return pd.DataFrame(heatmap_data)

def analyze_market_regime(prices, volumes=None):
    """Analyze current market regime using technical indicators"""
    if len(prices) < 10:
        return "INSUFFICIENT_DATA"

    # Calculate moving averages
    ma_short = np.mean(prices[-5:]) if len(prices) >= 5 else np.mean(prices)
    ma_long = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)

    # Calculate momentum
    momentum = (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0

    # Volume analysis (if available)
    volume_trend = 0
    if volumes and len(volumes) >= 5:
        volume_trend = (volumes[-1] - np.mean(volumes[-5:])) / np.mean(volumes[-5:])

    # Determine regime
    if ma_short > ma_long * 1.02 and momentum > 0.02:
        return "BULLISH"
    elif ma_short < ma_long * 0.98 and momentum < -0.02:
        return "BEARISH"
    elif abs(momentum) < 0.01 and abs(ma_short - ma_long) / ma_long < 0.01:
        return "SIDEWAYS"
    else:
        return "NEUTRAL"

def generate_investment_recommendations(market_data, projections):
    """Generate Bloomberg-style investment recommendations"""
    recommendations = []

    if not market_data or not projections:
        return recommendations

    # Current market analysis
    current_price = projections[0] if projections else 0
    projected_3m = projections[2] if len(projections) > 2 else current_price
    projected_6m = projections[5] if len(projections) > 5 else current_price

    # Price momentum
    price_change_3m = ((projected_3m - current_price) / current_price) * 100 if current_price > 0 else 0
    price_change_6m = ((projected_6m - current_price) / current_price) * 100 if current_price > 0 else 0

    # Generate recommendations based on projections
    if price_change_6m > 10:
        recommendations.append({
            'type': 'BUY',
            'strength': 'STRONG',
            'timeframe': '6M',
            'reason': f'Projected +{price_change_6m:.1f}% return in 6 months',
            'action': 'Accumulate positions, focus on undervalued assets'
        })
    elif price_change_6m > 5:
        recommendations.append({
            'type': 'BUY',
            'strength': 'MODERATE',
            'timeframe': '6M',
            'reason': f'Moderate upside of +{price_change_6m:.1f}% expected',
            'action': 'Selective buying in high-quality areas'
        })
    elif price_change_6m < -5:
        recommendations.append({
            'type': 'HOLD',
            'strength': 'CAUTION',
            'timeframe': '6M',
            'reason': f'Downside risk of {price_change_6m:.1f}% projected',
            'action': 'Wait for stabilization, consider defensive positions'
        })
    else:
        recommendations.append({
            'type': 'HOLD',
            'strength': 'NEUTRAL',
            'timeframe': '6M',
            'reason': f'Stable market with {price_change_6m:+.1f}% expected change',
            'action': 'Maintain current positions, monitor closely'
        })

    return recommendations

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

# === KPIs ROW - 6 symmetric cards (Transaction Focus) ===
kpis = data.get('kpis') or {}
tx_today = kpis.get('transactions_today') or 0
tx_7d = kpis.get('transactions_7d') or 0
tx_30d = kpis.get('transactions_30d') or 0
volume_30d = (kpis.get('volume_30d') or 0) / 1_000_000_000  # En milliards
median_price = (kpis.get('median_price_sqft') or kpis.get('avg_price_sqft') or 0)
variation = kpis.get('variation_7d_pct') or 0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(kpi_card("Today", "Transactions", str(tx_today)), unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("7 Days", "Transactions", str(tx_7d)), unsafe_allow_html=True)

with col3:
    st.markdown(kpi_card("30 Days", "Transactions", str(tx_30d)), unsafe_allow_html=True)

with col4:
    st.markdown(kpi_card("Volume 30D", "AED Billion", f"{volume_30d:.2f}B"), unsafe_allow_html=True)

with col5:
    st.markdown(kpi_card("Median Price", "AED/sqft", f"{median_price:,.0f}"), unsafe_allow_html=True)

with col6:
    trend_color = "green" if variation > 0 else "red" if variation < 0 else "accent"
    st.markdown(kpi_card("Trend 7D", "vs prev week", f"{variation:+.1f}%", trend_color), unsafe_allow_html=True)

st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

# === TOP NEIGHBORHOODS & PROPERTY TYPES ===
st.markdown('<div class="section-title">Market Activity - Top Neighborhoods & Property Types</div>', unsafe_allow_html=True)

col_neigh, col_types = st.columns(2)

# Top Neighborhoods
with col_neigh:
    st.markdown('<div class="section-subtitle">Top 10 Neighborhoods (30 days)</div>', unsafe_allow_html=True)
    
    neighborhoods = data.get('top_neighborhoods', [])
    if neighborhoods:
        # Préparer les données
        neigh_names = [n.get('community', 'Unknown')[:20] for n in neighborhoods[:10]]
        neigh_counts = [n.get('transaction_count', 0) for n in neighborhoods[:10]]
        neigh_prices = [n.get('avg_price_sqft', 0) for n in neighborhoods[:10]]
        
        # Graphique barres horizontales
        fig_neigh = go.Figure()
        
        fig_neigh.add_trace(go.Bar(
            y=neigh_names[::-1],
            x=neigh_counts[::-1],
            orientation='h',
            marker_color='#10B981',
            text=[f"{c} tx" for c in neigh_counts[::-1]],
            textposition='outside',
            textfont=dict(color='#FFFFFF', size=11),
            hovertemplate='<b>%{y}</b><br>Transactions: %{x}<br>Avg Price: %{customdata:,.0f} AED/sqft<extra></extra>',
            customdata=neigh_prices[::-1]
        ))
        
        fig_neigh.update_layout(
            height=350,
            margin=dict(l=10, r=60, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)', size=10),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title=''),
            yaxis=dict(gridcolor='rgba(0,0,0,0)', tickfont=dict(size=10))
        )
        
        st.plotly_chart(fig_neigh, use_container_width=True)
    else:
        st.info("No neighborhood data available")

# Property Types
with col_types:
    st.markdown('<div class="section-subtitle">Best Selling Property Types (30 days)</div>', unsafe_allow_html=True)
    
    property_types = data.get('property_types', {})
    rooms_data = property_types.get('by_rooms', [])
    
    if rooms_data:
        # Filtrer les Unknown et trier
        rooms_filtered = [r for r in rooms_data if r.get('rooms_bucket') and r.get('rooms_bucket') != 'Unknown']
        
        if rooms_filtered:
            room_names = [r.get('rooms_bucket', 'Other') for r in rooms_filtered]
            room_counts = [r.get('count', 0) for r in rooms_filtered]
            room_prices = [r.get('avg_price_sqft', 0) for r in rooms_filtered]
            
            # Double axe : barres pour count, ligne pour prix
            fig_types = go.Figure()
            
            # Barres pour le nombre de transactions
            fig_types.add_trace(go.Bar(
                x=room_names,
                y=room_counts,
                name='Transactions',
                marker_color=['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'][:len(room_names)],
                text=room_counts,
                textposition='outside',
                textfont=dict(color='#FFFFFF', size=12)
            ))
            
            fig_types.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=10, b=30),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.7)', size=11),
                xaxis=dict(gridcolor='rgba(0,0,0,0)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Transactions'),
                showlegend=False,
                bargap=0.3
            )
            
            st.plotly_chart(fig_types, use_container_width=True)
            
            # Tableau récapitulatif
            type_df = pd.DataFrame({
                'Type': room_names,
                'Transactions': room_counts,
                'Avg Price (AED/sqft)': [f"{p:,.0f}" for p in room_prices],
                'Share %': [f"{c/sum(room_counts)*100:.1f}%" for c in room_counts]
            })
            st.dataframe(type_df, use_container_width=True, hide_index=True, height=150)
    else:
        st.info("No property type data available")

st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

# === MARKET PROJECTIONS & PREDICTIONS ===
st.markdown('<div class="section-title">Market Projections & Predictions</div>', unsafe_allow_html=True)

# Get historical data for projections
try:
    historical_data = db.execute_query("""
        SELECT
            DATE_TRUNC('month', transaction_date) as month,
            AVG(price_per_sqft) as avg_price,
            COUNT(*) as volume
        FROM transactions
        WHERE transaction_date >= CURRENT_DATE - INTERVAL '12 months'
        GROUP BY DATE_TRUNC('month', transaction_date)
        ORDER BY month
    """)

    if historical_data:
        # Extract price series for analysis
        prices = [d['avg_price'] for d in historical_data if d['avg_price']]
        volumes = [d['volume'] for d in historical_data if d['volume']]

        # Generate projections
        price_projections = generate_price_projections(prices[-6:], 6)  # Last 6 months for trend
        market_regime = analyze_market_regime(prices, volumes)

        # Create projection chart
        months = ['Current', '1M', '2M', '3M', '4M', '5M', '6M']
        current_price = prices[-1] if prices else 0
        projection_values = [current_price] + price_projections

        fig_proj = go.Figure()

        # Historical data
        fig_proj.add_trace(go.Scatter(
            x=list(range(len(prices))),
            y=prices,
            mode='lines+markers',
            name='Historical',
            line=dict(color='#6B7280', width=2),
            marker=dict(size=6)
        ))

        # Projections
        fig_proj.add_trace(go.Scatter(
            x=list(range(len(prices)-1, len(prices)+len(price_projections))),
            y=projection_values,
            mode='lines+markers',
            name='Projections',
            line=dict(color='#00D9A3', width=3, dash='dash'),
            marker=dict(size=8, symbol='diamond')
        ))

        fig_proj.update_layout(
            title=dict(text=f'Market Price Projections - Regime: {market_regime}', font=dict(size=16, color='#FFFFFF')),
            height=300, margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)', size=11),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Months'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='AED/sqft'),
            showlegend=True,
            legend=dict(x=0.02, y=0.98)
        )

        st.plotly_chart(fig_proj, use_container_width=True)

        # Projection metrics
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        with col_p1:
            rsi = calculate_market_rsi(prices)
            st.markdown(kpi_card("Market RSI", "Momentum", f"{rsi:.0f}", "green" if rsi > 60 else "red" if rsi < 40 else "accent"), unsafe_allow_html=True)

        with col_p2:
            change_3m = ((price_projections[2] - current_price) / current_price * 100) if current_price > 0 else 0
            st.markdown(kpi_card("3M Projection", "Price Change", f"{change_3m:+.1f}%", "green" if change_3m > 0 else "red"), unsafe_allow_html=True)

        with col_p3:
            change_6m = ((price_projections[5] - current_price) / current_price * 100) if current_price > 0 else 0
            st.markdown(kpi_card("6M Projection", "Price Change", f"{change_6m:+.1f}%", "green" if change_6m > 0 else "red"), unsafe_allow_html=True)

        with col_p4:
            regime_color = {'BULLISH': 'green', 'BEARISH': 'red', 'SIDEWAYS': 'accent', 'NEUTRAL': 'blue'}.get(market_regime, 'accent')
            st.markdown(kpi_card("Market Regime", "Current", market_regime, regime_color), unsafe_allow_html=True)

except Exception as e:
    st.warning(f"Could not generate projections: {str(e)}")

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

# === MARKET HEATMAP ===
st.markdown('<div class="section-title">Market Heatmap Analysis</div>', unsafe_allow_html=True)

try:
    # Get zone performance data
    zone_data = db.execute_query("""
        SELECT
            t.community,
            AVG(t.price_per_sqft) as avg_price_sqft,
            COUNT(*) as transaction_count,
            AVG(o.discount_pct) as avg_discount,
            AVG(
                CASE WHEN o.discount_pct > 0 THEN 80 + (o.discount_pct * 0.5)
                     ELSE 60 - (ABS(COALESCE(o.discount_pct, 0)) * 0.3) END
            ) as opportunity_score
        FROM transactions t
        LEFT JOIN opportunities o ON t.community = o.community
        WHERE t.transaction_date >= CURRENT_DATE - INTERVAL '90 days'
        AND t.community IS NOT NULL
        GROUP BY t.community
        HAVING COUNT(*) >= 3
        ORDER BY avg_price_sqft DESC
        LIMIT 20
    """)

    if zone_data:
        heatmap_df = create_market_heatmap(zone_data)

        # Create interactive heatmap
        fig_heatmap = px.scatter(
            heatmap_df,
            x='Price',
            y='Volume',
            size='Score',
            color='Score',
            hover_name='Zone',
            size_max=50,
            color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
            title='Zone Performance Heatmap'
        )

        fig_heatmap.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)', size=11),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Avg Price (AED/sqft)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Transaction Volume'),
            coloraxis_colorbar=dict(
                title="Score",
                tickvals=[40, 60, 80],
                ticktext=["Low", "Medium", "High"]
            )
        )

        fig_heatmap.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>Price: %{x:,.0f} AED/sqft<br>Volume: %{y}<br>Score: %{marker.color:.0f}'
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Top performing zones table
        col_h1, col_h2 = st.columns(2)

        with col_h1:
            st.markdown('<div class="section-title" style="font-size: 0.9rem;">Top Value Zones</div>', unsafe_allow_html=True)
            top_value = heatmap_df.nlargest(5, 'Score')[['Zone', 'Price', 'Score']].round(0)
            st.dataframe(
                top_value,
                use_container_width=True,
                hide_index=True,
                height=180,
                column_config={
                    'Score': st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f")
                }
            )

        with col_h2:
            st.markdown('<div class="section-title" style="font-size: 0.9rem;">High Volume Zones</div>', unsafe_allow_html=True)
            top_volume = heatmap_df.nlargest(5, 'Volume')[['Zone', 'Volume', 'Price']].round({'Volume': 0, 'Price': 0})
            st.dataframe(top_volume, use_container_width=True, hide_index=True, height=180)

except Exception as e:
    st.warning(f"Could not generate heatmap: {str(e)}")

st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

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

# === INVESTMENT RECOMMENDATIONS & AI INSIGHTS ===
st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Investment Recommendations & AI Insights</div>', unsafe_allow_html=True)

# Generate investment recommendations
try:
    if 'price_projections' in locals() and price_projections:
        recommendations = generate_investment_recommendations(data, price_projections)

        if recommendations:
            st.markdown('<div class="section-subtitle">BLOOMBERG-STYLE RECOMMENDATIONS</div>', unsafe_allow_html=True)

            rec_cols = st.columns(len(recommendations))
            for i, rec in enumerate(recommendations):
                with rec_cols[i]:
                    color_map = {
                        'BUY': '#10B981',
                        'HOLD': '#F59E0B',
                        'SELL': '#EF4444'
                    }
                    strength_colors = {
                        'STRONG': '#10B981',
                        'MODERATE': '#3B82F6',
                        'CAUTION': '#F59E0B',
                        'NEUTRAL': '#6B7280'
                    }

                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(19,29,50,0.95) 0%, rgba(15,26,46,0.95) 100%);
                        border-radius: 12px;
                        padding: 1.5rem;
                        border-left: 4px solid {color_map.get(rec['type'], '#6B7280')};
                        height: 220px;
                        display: flex;
                        flex-direction: column;
                    ">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.8rem;">
                            <span style="font-size: 1.5rem;">
                                {'[UP]' if rec['type'] == 'BUY' else '[HOLD]' if rec['type'] == 'HOLD' else '[DOWN]'}
                            </span>
                            <span style="color: {color_map.get(rec['type'], '#6B7280')}; font-weight: 700; font-size: 1rem;">{rec['type']} ({rec['strength']})</span>
                            <span style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">{rec['timeframe']}</span>
                        </div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem; line-height: 1.4; flex: 1;">
                            <b>{rec['reason']}</b><br>{rec['action']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

except Exception as e:
    pass

st.markdown('<div class="section-subtitle">AI MARKET INSIGHTS</div>', unsafe_allow_html=True)

# Generate AI insights based on data
def generate_ai_insights(opps, kpis_data, brief_data):
    """Generate smart AI insights from current data"""
    insights = []

    # Safety check - ensure kpis_data is not None
    if not kpis_data:
        kpis_data = {}

    # Insight 1: Market momentum
    # Use (x or 0) pattern to handle None values safely
    if (kpis_data.get('avg_price_sqft') or 0) > 1800:
        insights.append({
            'type': 'trend',
            'icon': '[TREND]',
            'title': 'Strong Market',
            'text': f"Avg price at AED {kpis_data.get('avg_price_sqft', 0):,.0f}/sqft indicates seller's market. Consider aggressive bidding on undervalued assets.",
            'action': 'Review FLIP opportunities',
            'color': '#10B981'
        })
    else:
        insights.append({
            'type': 'trend', 
            'icon': '📉',
            'title': 'Buyer Opportunity',
            'text': 'Market prices below typical range. Good entry point for long-term positions.',
            'action': 'Focus on LONG strategy',
            'color': '#3B82F6'
        })
    
    # Insight 2: Opportunity quality
    if opps:
        high_score = [o for o in opps if o.get('global_score', 0) >= 80]
        if len(high_score) >= 3:
            insights.append({
                'type': 'opportunity',
                'icon': '[TARGET]',
                'title': f'{len(high_score)} High-Score Deals',
                'text': f"Multiple opportunities scoring 80+. Focus on {high_score[0].get('community', 'top zones')} for best risk/reward.",
                'action': 'Prioritize today',
                'color': '#10B981'
            })
        
        # Discount analysis
        avg_disc = sum(o.get('discount_pct', 0) for o in opps) / len(opps) if opps else 0
        if avg_disc > 15:
            insights.append({
                'type': 'value',
                'icon': '[VALUE]',
                'title': 'Deep Value Detected',
                'text': f"Average {avg_disc:.1f}% discount vs market. Indicates motivated sellers or pricing inefficiencies.",
                'action': 'Execute quickly',
                'color': '#F59E0B'
            })
    
    # Insight 3: Risk from brief
    if brief_data:
        risk = brief_data.get('main_risk', '')
        if 'supply' in risk.lower():
            insights.append({
                'type': 'risk',
                'icon': '[WARNING]',
                'title': 'Supply Risk',
                'text': risk[:100] + '...' if len(risk) > 100 else risk,
                'action': 'Avoid over-leveraging',
                'color': '#EF4444'
            })
    
    # Insight 4: Strategy recommendation
    if opps:
        strategies = {}
        for o in opps:
            s = o.get('recommended_strategy', 'OTHER')
            strategies[s] = strategies.get(s, 0) + 1
        
        top_strat = max(strategies, key=strategies.get) if strategies else 'FLIP'
        insights.append({
            'type': 'strategy',
            'icon': '🧠',
            'title': f'Focus: {top_strat}',
            'text': f"{strategies.get(top_strat, 0)} opportunities favor {top_strat} strategy based on current market conditions.",
            'action': f'Review {top_strat} criteria',
            'color': '#8B5CF6'
        })
    
    return insights[:4]  # Max 4 insights

insights = generate_ai_insights(opportunities_list, kpis, brief)

col_i1, col_i2, col_i3, col_i4 = st.columns(4)
insight_cols = [col_i1, col_i2, col_i3, col_i4]

for i, insight in enumerate(insights):
    with insight_cols[i]:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(19,29,50,0.95) 0%, rgba(15,26,46,0.95) 100%);
            border-radius: 12px;
            padding: 1.2rem;
            border-left: 4px solid {insight['color']};
            height: 180px;
            display: flex;
            flex-direction: column;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.6rem;">
                <span style="font-size: 1.2rem;">{insight['icon']}</span>
                <span style="color: {insight['color']}; font-weight: 600; font-size: 0.85rem;">{insight['title']}</span>
            </div>
            <div style="color: rgba(255,255,255,0.8); font-size: 0.78rem; line-height: 1.5; flex: 1;">
                {insight['text']}
            </div>
            <div style="
                margin-top: 0.8rem;
                padding-top: 0.6rem;
                border-top: 1px solid rgba(255,255,255,0.1);
            ">
                <span style="color: {insight['color']}; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">
                    → {insight['action']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Fill remaining columns if less than 4 insights
for i in range(len(insights), 4):
    with insight_cols[i]:
        st.markdown("""
        <div style="
            background: rgba(19,29,50,0.5);
            border-radius: 12px;
            padding: 1.2rem;
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px dashed rgba(255,255,255,0.1);
        ">
            <span style="color: rgba(255,255,255,0.3); font-size: 0.8rem;">More insights coming...</span>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
st.caption(f"Last update: {get_dubai_today()} | AI-powered insights")

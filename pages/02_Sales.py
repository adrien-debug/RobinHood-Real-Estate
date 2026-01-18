"""
Advanced Sales Analytics - Bloomberg-Style Market Analysis
Volume analysis, price predictions, correlations, and market modeling
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
import scipy.stats as stats

st.set_page_config(page_title="Today's Sales", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

# === ADVANCED SALES ANALYTICS FUNCTIONS ===

def calculate_volume_correlations(volume_data):
    """Calculate correlations between volume and price movements"""
    if len(volume_data) < 5:
        return {}

    df = pd.DataFrame(volume_data)
    correlations = {}

    # Volume vs Price correlation
    if 'volume' in df.columns and 'avg_price' in df.columns:
        corr = df['volume'].corr(df['avg_price'])
        correlations['volume_price'] = corr

    # Volume trend analysis
    if len(df) >= 7:
        volumes = df['volume'].values
        try:
            correlations['volume_trend'] = np.polyfit(range(len(volumes)), volumes, 1)[0]
        except (np.RankWarning, ValueError, TypeError):
            correlations['volume_trend'] = 0.0

    return correlations

def predict_price_trends(historical_data, days_ahead=30):
    """Predict price trends using time series analysis"""
    if len(historical_data) < 7:
        return []

    df = pd.DataFrame(historical_data)

    # Simple exponential smoothing for prediction
    if 'avg_price' in df.columns:
        prices = df['avg_price'].values
        alpha = 0.3  # Smoothing factor

        # Calculate smoothed values
        smoothed = [prices[0]]
        for i in range(1, len(prices)):
            smoothed.append(alpha * prices[i] + (1 - alpha) * smoothed[-1])

        # Trend calculation
        try:
            trend = np.polyfit(range(len(smoothed)), smoothed, 1)[0]
        except (np.RankWarning, ValueError, TypeError):
            trend = 0.0

        # Generate predictions
        last_price = smoothed[-1]
        predictions = []
        for i in range(1, days_ahead + 1):
            predicted = last_price + (trend * i)
            predictions.append(max(0, predicted))  # No negative prices

        return predictions

    return []

def analyze_supply_demand_dynamics(transactions):
    """Analyze supply-demand dynamics from transaction data"""
    if not transactions:
        return {}

    df = pd.DataFrame(transactions)

    analysis = {
        'total_volume': len(df),
        'avg_days_on_market': df.get('days_on_market', pd.Series([30] * len(df))).mean(),
        'price_elasticity': 0,
        'absorption_rate': 0
    }

    # Price elasticity (simplified)
    if 'price_per_sqft' in df.columns and 'area_sqft' in df.columns:
        # Larger properties might have different pricing dynamics
        correlation = df['price_per_sqft'].corr(df['area_sqft'])
        analysis['price_elasticity'] = correlation

    # Absorption rate (monthly sales rate)
    if 'transaction_date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        monthly_volume = df.groupby(df['transaction_date'].dt.to_period('M')).size()
        analysis['absorption_rate'] = monthly_volume.mean() if len(monthly_volume) > 0 else 0

    return analysis

def create_price_distribution_analysis(transactions, bins=20):
    """Create detailed price distribution analysis"""
    if not transactions:
        return {}

    df = pd.DataFrame(transactions)

    if 'price_per_sqft' not in df.columns:
        return {}

    prices = df['price_per_sqft'].values

    # Statistical analysis
    stats_analysis = {
        'mean': np.mean(prices),
        'median': np.median(prices),
        'std': np.std(prices),
        'skewness': stats.skew(prices),
        'kurtosis': stats.kurtosis(prices),
        'q25': np.percentile(prices, 25),
        'q75': np.percentile(prices, 75),
        'iqr': np.percentile(prices, 75) - np.percentile(prices, 25)
    }

    # Distribution bins
    hist, bin_edges = np.histogram(prices, bins=bins)
    stats_analysis['histogram'] = {
        'counts': hist.tolist(),
        'bins': bin_edges.tolist()
    }

    return stats_analysis

st.markdown('<div class="dashboard-header">Advanced Sales Analytics</div>', unsafe_allow_html=True)

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    communities = db.execute_query("SELECT DISTINCT community FROM dld_transactions WHERE community IS NOT NULL ORDER BY community")
    community_list = [c['community'] for c in communities]
    selected_community = st.selectbox("Community", ["All"] + community_list)

with col3:
    rooms_filter = st.selectbox("Rooms", ["All", "studio", "1BR", "2BR", "3BR+"])

with col4:
    min_price = st.number_input("Min price (AED)", value=0, step=100000)

# Query
query = "SELECT * FROM v_recent_transactions WHERE transaction_date = %s"
params = [target_date]

if selected_community != "All":
    query += " AND community = %s"
    params.append(selected_community)

if rooms_filter != "All":
    query += " AND rooms_bucket = %s"
    params.append(rooms_filter)

if min_price > 0:
    query += " AND price_aed >= %s"
    params.append(min_price)

query += " ORDER BY price_per_sqft DESC LIMIT 50"

transactions = db.execute_query(query, tuple(params))

st.markdown("---")

# === KPIs ===
if transactions:
    total_volume = sum(t.get('price_aed', 0) or 0 for t in transactions)
    avg_price = sum(t.get('price_per_sqft', 0) or 0 for t in transactions) / len(transactions)
    below_market = sum(1 for t in transactions if (t.get('discount_pct') or 0) > 0)
    pct_below = (below_market / len(transactions)) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(kpi_card("Transactions", "Today", str(len(transactions)), "accent"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(kpi_card("Total Volume", "AED", format_currency(total_volume)), unsafe_allow_html=True)
    
    with col3:
        st.markdown(kpi_card("Avg Price/sqft", "AED", f"{avg_price:.0f}"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(kpi_card("Below Market", "Opportunities", f"{pct_below:.0f}%", "green"), unsafe_allow_html=True)
    
    st.markdown("---")

    # === ADVANCED MARKET ANALYSIS ===
    st.markdown('<div class="section-title">Market Dynamics & Predictions</div>', unsafe_allow_html=True)

    # Get historical data for analysis
    historical_query = """
        SELECT
            DATE_TRUNC('week', transaction_date) as week,
            AVG(price_per_sqft) as avg_price,
            COUNT(*) as volume,
            AVG(area_sqft) as avg_area
        FROM dld_transactions
        WHERE transaction_date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY DATE_TRUNC('week', transaction_date)
        ORDER BY week
    """

    historical_data = db.execute_query(historical_query)

    if historical_data:
        # Volume-Price Correlation Analysis
        correlations = calculate_volume_correlations(historical_data)

        col_c1, col_c2, col_c3, col_c4 = st.columns(4)

        with col_c1:
            corr_value = correlations.get('volume_price', 0)
            st.markdown(kpi_card(
                "Volume-Price Correlation",
                "Relationship",
                f"{corr_value:.2f}",
                "green" if corr_value > 0.3 else "red" if corr_value < -0.3 else "accent"
            ), unsafe_allow_html=True)

        with col_c2:
            trend = correlations.get('volume_trend', 0)
            st.markdown(kpi_card(
                "Volume Trend",
                "Weekly change",
                f"{trend:+.1f} tx/week",
                "green" if trend > 0 else "red"
            ), unsafe_allow_html=True)

        with col_c3:
            # Supply-demand analysis
            dynamics = analyze_supply_demand_dynamics(transactions)
            elasticity = dynamics.get('price_elasticity', 0)
            st.markdown(kpi_card(
                "Price Elasticity",
                "Size vs Price",
                f"{elasticity:.2f}",
                "accent"
            ), unsafe_allow_html=True)

        with col_c4:
            absorption = dynamics.get('absorption_rate', 0)
            st.markdown(kpi_card(
                "Absorption Rate",
                "Monthly sales",
                f"{absorption:.0f} tx/month",
                "blue"
            ), unsafe_allow_html=True)

        # Price Predictions Chart
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        predictions = predict_price_trends(historical_data, 30)  # 30-day prediction

        if predictions:
            # Create prediction chart
            weeks = [f"W{i}" for i in range(len(historical_data))]
            future_days = [f"D{i+1}" for i in range(len(predictions))]

            fig_pred = go.Figure()

            # Historical data
            hist_prices = [d['avg_price'] for d in historical_data]
            fig_pred.add_trace(go.Scatter(
                x=weeks,
                y=hist_prices,
                mode='lines+markers',
                name='Historical',
                line=dict(color='#6B7280', width=2),
                marker=dict(size=6)
            ))

            # Predictions
            fig_pred.add_trace(go.Scatter(
                x=future_days,
                y=predictions,
                mode='lines+markers',
                name='Predictions',
                line=dict(color='#00D9A3', width=3, dash='dash'),
                marker=dict(size=8, symbol='diamond')
            ))

            fig_pred.update_layout(
                title=dict(text='Price Trend Predictions (30 Days)', font=dict(size=16, color='#FFFFFF')),
                height=300, margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.7)', size=11),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='AED/sqft'),
                showlegend=True
            )

            st.plotly_chart(fig_pred, use_container_width=True)

    # Price Distribution Analysis
    if transactions:
        dist_analysis = create_price_distribution_analysis(transactions)

        if dist_analysis:
            st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">Price Distribution Analysis</div>', unsafe_allow_html=True)

            col_d1, col_d2, col_d3, col_d4 = st.columns(4)

            with col_d1:
                st.markdown(kpi_card(
                    "Mean Price",
                    "Average",
                    f"{dist_analysis['mean']:,.0f}",
                    "accent"
                ), unsafe_allow_html=True)

            with col_d2:
                st.markdown(kpi_card(
                    "Median Price",
                    "50th percentile",
                    f"{dist_analysis['median']:,.0f}",
                    "blue"
                ), unsafe_allow_html=True)

            with col_d3:
                skewness = dist_analysis['skewness']
                st.markdown(kpi_card(
                    "Distribution Skew",
                    "Asymmetry",
                    f"{skewness:+.2f}",
                    "green" if abs(skewness) < 0.5 else "red"
                ), unsafe_allow_html=True)

            with col_d4:
                st.markdown(kpi_card(
                    "Price Range (IQR)",
                    "25th-75th pct",
                    f"{dist_analysis['q25']:,.0f}-{dist_analysis['q75']:,.0f}",
                    "accent"
                ), unsafe_allow_html=True)

    st.markdown("---")

    # === TABLE ===
    st.markdown('<div class="section-title">Transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">LATEST SALES</div>', unsafe_allow_html=True)
    
    import pandas as pd
    
    # Build DataFrame
    df_data = []
    for tx in transactions:
        discount = tx.get('discount_pct', 0) or 0
        df_data.append({
            "Location": f"{tx.get('community', 'N/A')} / {tx.get('building', 'N/A')}",
            "Type": tx.get('rooms_bucket', 'N/A'),
            "Area": f"{tx.get('area_sqft', 0):.0f} sqft",
            "Price": format_currency(tx.get('price_aed', 0)),
            "AED/sqft": f"{tx.get('price_per_sqft', 0):.0f}",
            "vs Market": f"-{discount:.1f}%" if discount > 0 else "At market"
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === ADVANCED ANALYTICS CHARTS ===
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        # Enhanced price distribution with statistical insights
        prices = [t.get('price_per_sqft', 0) for t in transactions]

        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Histogram(
            x=prices,
            nbinsx=15,
            marker_color='#10B981',
            opacity=0.7,
            name='Distribution'
        ))

        # Add statistical lines
        if dist_analysis:
            fig.add_vline(x=dist_analysis['mean'], line_dash="dash", line_color="#00D9A3",
                         annotation_text=f"Mean: {dist_analysis['mean']:,.0f}")
            fig.add_vline(x=dist_analysis['median'], line_dash="dot", line_color="#3B82F6",
                         annotation_text=f"Median: {dist_analysis['median']:,.0f}")

        fig.update_layout(
            title=dict(text='Price Distribution with Statistics', font=dict(size=14, color='#FFFFFF')),
            height=280,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='AED/sqft', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Frequency', gridcolor='rgba(255,255,255,0.05)')
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_c2:
        # Price distribution
        prices = [t.get('price_per_sqft', 0) for t in transactions]
        
        fig = go.Figure(data=[go.Histogram(
            x=prices,
            nbinsx=10,
            marker_color='#10B981',
            opacity=0.8
        )])
        
        fig.update_layout(
            title=dict(text='Price/sqft Distribution', font=dict(size=14, color='#FFFFFF')),
            height=280,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='AED/sqft', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Count', gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_c2:
        # By room type
        room_counts = {}
        for t in transactions:
            room = t.get('rooms_bucket', 'Other')
            room_counts[room] = room_counts.get(room, 0) + 1
        
        fig = go.Figure(data=[go.Bar(
            x=list(room_counts.keys()),
            y=list(room_counts.values()),
            marker_color=['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#6B7280'][:len(room_counts)],
            text=list(room_counts.values()),
            textposition='outside',
            textfont=dict(color='#FFFFFF')
        )])
        
        fig.update_layout(
            title=dict(text='By Room Type', font=dict(size=14, color='#FFFFFF')),
            height=280,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

    # Additional correlation and trend charts
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

    col_adv1, col_adv2 = st.columns(2)

    with col_adv1:
        # Price vs Size Correlation
        if transactions:
            sizes = [t.get('area_sqft', 0) for t in transactions]
            prices_sqft = [t.get('price_per_sqft', 0) for t in transactions]

            fig_corr = go.Figure(data=[go.Scatter(
                x=sizes,
                y=prices_sqft,
                mode='markers',
                marker=dict(
                    size=8,
                    color='#10B981',
                    opacity=0.6,
                    line=dict(width=1, color='rgba(255,255,255,0.3)')
                ),
                text=[f"{t.get('community', '')} - {t.get('building', '')}" for t in transactions],
                hovertemplate='<b>%{text}</b><br>Size: %{x} sqft<br>Price: %{y} AED/sqft'
            )])

            # Add trend line
            if len(sizes) > 5:
                slope, intercept = np.polyfit(sizes, prices_sqft, 1)
                trend_x = np.array([min(sizes), max(sizes)])
                trend_y = slope * trend_x + intercept
                fig_corr.add_trace(go.Scatter(
                    x=trend_x, y=trend_y,
                    mode='lines',
                    line=dict(color='#EF4444', dash='dash', width=2),
                    name=f'Trend (corr: {slope:.2f})'
                ))

            fig_corr.update_layout(
                title=dict(text='Price vs Size Correlation', font=dict(size=14, color='#FFFFFF')),
                height=280,
                margin=dict(l=40, r=20, t=50, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.7)'),
                xaxis=dict(title='Area (sqft)', gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(title='Price/sqft (AED)', gridcolor='rgba(255,255,255,0.05)')
            )

            st.plotly_chart(fig_corr, use_container_width=True)

    with col_adv2:
        # Volume trend analysis
        if historical_data:
            weeks = [f"W{i+1}" for i in range(len(historical_data))]
            volumes = [d['volume'] for d in historical_data]

            fig_vol = go.Figure()

            # Volume bars
            fig_vol.add_trace(go.Bar(
                x=weeks,
                y=volumes,
                marker_color='#3B82F6',
                opacity=0.8,
                name='Weekly Volume'
            ))

            # Add moving average
            if len(volumes) >= 3:
                ma = pd.Series(volumes).rolling(window=3).mean()
                fig_vol.add_trace(go.Scatter(
                    x=weeks,
                    y=ma,
                    mode='lines',
                    line=dict(color='#F59E0B', width=3),
                    name='3-Week MA'
                ))

            fig_vol.update_layout(
                title=dict(text='Transaction Volume Trends', font=dict(size=14, color='#FFFFFF')),
                height=280,
                margin=dict(l=40, r=20, t=50, b=40),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.7)'),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(title='Transactions', gridcolor='rgba(255,255,255,0.05)')
            )

            st.plotly_chart(fig_vol, use_container_width=True)

    # Market Intelligence Summary
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Market Intelligence Summary</div>', unsafe_allow_html=True)

    # Generate market insights
    insights = []

    if dist_analysis and correlations:
        # Insight 1: Market positioning
        if dist_analysis['skewness'] > 0.5:
            insights.append({
                'icon': '[TREND]',
                'title': 'Right-Skewed Market',
                'text': 'Premium segment driving price distribution. Focus on luxury positioning.',
                'color': '#10B981'
            })
        elif dist_analysis['skewness'] < -0.5:
            insights.append({
                'icon': '📉',
                'title': 'Value-Driven Market',
                'text': 'Affordable properties dominating. Consider value-add strategies.',
                'color': '#3B82F6'
            })

        # Insight 2: Volume correlation
        vol_price_corr = correlations.get('volume_price', 0)
        if abs(vol_price_corr) > 0.3:
            direction = "positive" if vol_price_corr > 0 else "negative"
            insights.append({
                'icon': '🔄' if vol_price_corr > 0 else '⚡',
                'title': f'{direction.title()} Volume-Price Correlation',
                'text': f'Volume and price show {direction} relationship ({vol_price_corr:.2f}). Market efficiency indicator.',
                'color': '#F59E0B'
            })

    # Display insights
    if insights:
        insight_cols = st.columns(len(insights))
        for i, insight in enumerate(insights):
            with insight_cols[i]:
                st.markdown(f"""
                <div style="
                    background: rgba(19,29,50,0.8);
                    border-radius: 8px;
                    padding: 1rem;
                    border-left: 3px solid {insight['color']};
                    height: 120px;
                ">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem;">{insight['icon']}</span>
                        <span style="color: {insight['color']}; font-weight: 600; font-size: 0.9rem;">{insight['title']}</span>
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem; line-height: 1.3;">
                        {insight['text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

else:
    st.info("No transactions for this date.")

st.caption(f"Last update: {get_dubai_today()} | Advanced market analytics powered by AI")

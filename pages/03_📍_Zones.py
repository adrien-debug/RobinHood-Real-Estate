"""
Advanced Zone Analysis - Bloomberg-Style Real Estate Intelligence
Interactive heatmaps, volatility analysis, predictive scoring, and zone comparisons
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

st.set_page_config(page_title="Zones & Buildings", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

# === ADVANCED ZONE ANALYSIS FUNCTIONS ===

def calculate_zone_volatility(price_history, window=7):
    """Calculate price volatility for a zone"""
    if len(price_history) < window:
        return 0

    prices = [p['avg_price'] for p in price_history]
    returns = np.diff(prices) / prices[:-1]
    volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
    return volatility

def predict_zone_performance(zone_data, periods=3):
    """Predict zone performance using trend analysis"""
    if not zone_data or len(zone_data) < 3:
        return {}

    # Extract price series
    prices = [d.get('avg_price', 0) for d in zone_data if d.get('avg_price')]
    volumes = [d.get('count', 0) for d in zone_data if d.get('count')]

    if len(prices) < 3:
        return {}

    # Calculate trends
    price_trend = np.polyfit(range(len(prices)), prices, 1)[0]
    volume_trend = np.polyfit(range(len(volumes)), volumes, 1)[0] if volumes else 0

    # Generate predictions
    last_price = prices[-1]
    predictions = []

    for i in range(1, periods + 1):
        predicted_price = last_price + (price_trend * i)
        predicted_volume = max(0, volumes[-1] + (volume_trend * i)) if volumes else 0

        predictions.append({
            'period': i,
            'predicted_price': predicted_price,
            'predicted_volume': predicted_volume,
            'price_change_pct': ((predicted_price - last_price) / last_price) * 100 if last_price > 0 else 0
        })

    return {
        'predictions': predictions,
        'price_trend': price_trend,
        'volume_trend': volume_trend,
        'volatility': calculate_zone_volatility(zone_data),
        'momentum_score': price_trend * (1 + len(prices)/10)  # Momentum weighted by data points
    }

def create_zone_comparison_heatmap(zone_data):
    """Create interactive heatmap for zone comparison"""
    if not zone_data:
        return None

    zones = []
    metrics = {
        'price': [],
        'volume': [],
        'volatility': [],
        'momentum': []
    }

    for zone in zone_data[:15]:  # Top 15 zones
        zone_name = zone.get('community', 'Unknown')
        zones.append(zone_name)

        # Normalize metrics for heatmap
        metrics['price'].append(zone.get('avg_price_sqft', 0) / 2000)  # Normalize around 2000 AED/sqft
        metrics['volume'].append(min(zone.get('transaction_count', 0) / 50, 1))  # Cap at 50 transactions
        metrics['volatility'].append(min(zone.get('volatility', 0) / 0.5, 1))  # Cap at 50% volatility
        metrics['momentum'].append((zone.get('momentum_score', 0) + 100) / 200)  # Normalize momentum

    return {
        'zones': zones,
        'metrics': metrics
    }

def generate_zone_investment_signals(zone_analysis, market_regime):
    """Generate investment signals based on zone analysis"""
    signals = []

    if not zone_analysis:
        return signals

    predictions = zone_analysis.get('predictions', [])
    volatility = zone_analysis.get('volatility', 0)
    momentum = zone_analysis.get('momentum_score', 0)

    # Signal 1: Price momentum
    if momentum > 50:
        signals.append({
            'type': 'BUY',
            'strength': 'STRONG',
            'reason': f'Strong upward momentum (+{momentum:.1f} points)',
            'timeframe': '3-6 months'
        })
    elif momentum > 20:
        signals.append({
            'type': 'BUY',
            'strength': 'MODERATE',
            'reason': f'Positive momentum (+{momentum:.1f} points)',
            'timeframe': '3 months'
        })
    elif momentum < -20:
        signals.append({
            'type': 'HOLD',
            'strength': 'CAUTION',
            'reason': f'Downward pressure ({momentum:.1f} points)',
            'timeframe': 'Wait for stabilization'
        })

    # Signal 2: Volatility assessment
    if volatility > 0.3:
        signals.append({
            'type': 'RISK',
            'strength': 'HIGH',
            'reason': f'High volatility ({volatility:.1%}) - Consider risk management',
            'timeframe': 'Ongoing'
        })
    elif volatility < 0.1:
        signals.append({
            'type': 'STABLE',
            'strength': 'LOW_RISK',
            'reason': f'Low volatility ({volatility:.1%}) - Stable investment',
            'timeframe': 'Long-term'
        })

    # Signal 3: Market regime alignment
    regime_signals = {
        'ACCUMULATION': {'type': 'BUY', 'reason': 'Accumulation phase favors buying'},
        'EXPANSION': {'type': 'HOLD', 'reason': 'Expansion phase - hold positions'},
        'DISTRIBUTION': {'type': 'SELL', 'reason': 'Distribution phase - consider selling'},
        'RETOURNEMENT': {'type': 'WAIT', 'reason': 'Reversal phase - wait for direction'}
    }

    if market_regime in regime_signals:
        regime_signal = regime_signals[market_regime]
        signals.append({
            'type': regime_signal['type'],
            'strength': 'MARKET',
            'reason': regime_signal['reason'],
            'timeframe': 'Market-driven'
        })

    return signals

st.markdown('<div class="dashboard-header">Advanced Zone Analysis</div>', unsafe_allow_html=True)

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

# === ZONE COMPARISON HEATMAP ===
st.markdown('<div class="section-title">Zone Performance Heatmap</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Interactive comparison of top performing zones</div>', unsafe_allow_html=True)

# Get zone comparison data
zone_comparison_data = db.execute_query("""
    SELECT
        community,
        AVG(price_per_sqft) as avg_price_sqft,
        COUNT(*) as transaction_count,
        STDDEV(price_per_sqft) / AVG(price_per_sqft) as volatility,
        (COUNT(*) * AVG(price_per_sqft) / 1000) as momentum_score
    FROM transactions
    WHERE transaction_date >= %s - INTERVAL '90 days'
    AND community IS NOT NULL
    GROUP BY community
    HAVING COUNT(*) >= 5
    ORDER BY avg_price_sqft DESC
    LIMIT 15
""", (target_date,))

if zone_comparison_data:
    heatmap_data = create_zone_comparison_heatmap(zone_comparison_data)

    if heatmap_data:
        # Create interactive heatmap
        fig_heatmap = go.Figure()

        # Price heatmap
        fig_heatmap.add_trace(go.Heatmap(
            z=[heatmap_data['metrics']['price']],
            x=heatmap_data['zones'],
            y=['Price Score'],
            colorscale='RdYlGn',
            showscale=True,
            name='Price',
            hovertemplate='Zone: %{x}<br>Price Score: %{z:.2f}<extra></extra>'
        ))

        fig_heatmap.update_layout(
            title=dict(text='Zone Performance Matrix', font=dict(size=16, color='#FFFFFF')),
            height=200,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)', size=11),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Top zones summary
        col_h1, col_h2, col_h3 = st.columns(3)

        with col_h1:
            top_price_zone = zone_comparison_data[0]['community']
            top_price = zone_comparison_data[0]['avg_price_sqft']
            st.markdown(kpi_card(
                "Top Price Zone",
                top_price_zone,
                f"{top_price:,.0f}",
                "green"
            ), unsafe_allow_html=True)

        with col_h2:
            top_volume_zone = max(zone_comparison_data, key=lambda x: x['transaction_count'])['community']
            top_volume = max(zone_comparison_data, key=lambda x: x['transaction_count'])['transaction_count']
            st.markdown(kpi_card(
                "Top Volume Zone",
                top_volume_zone,
                f"{top_volume}",
                "blue"
            ), unsafe_allow_html=True)

        with col_h3:
            lowest_volatility_zone = min(zone_comparison_data, key=lambda x: x.get('volatility', 1))['community']
            lowest_volatility = min(zone_comparison_data, key=lambda x: x.get('volatility', 1)).get('volatility', 0)
            st.markdown(kpi_card(
                "Most Stable Zone",
                lowest_volatility_zone,
                f"{lowest_volatility:.1%}",
                "accent"
            ), unsafe_allow_html=True)

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

    # === PREDICTIVE ZONE ANALYSIS ===
    st.markdown("---")
    st.markdown('<div class="section-title">Predictive Zone Analysis</div>', unsafe_allow_html=True)

    # Get extended price history for predictions
    extended_history = db.execute_query("""
        SELECT transaction_date, AVG(price_per_sqft) as avg_price, COUNT(*) as count
        FROM transactions
        WHERE community = %s
            AND transaction_date >= %s - INTERVAL '60 days'
            AND transaction_date <= %s
            AND price_per_sqft IS NOT NULL
        GROUP BY transaction_date
        ORDER BY transaction_date
    """, (selected_community, target_date, target_date))

    if extended_history:
        zone_analysis = predict_zone_performance(extended_history, periods=3)

        if zone_analysis:
            # Prediction KPIs
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)

            predictions = zone_analysis.get('predictions', [])

            with col_p1:
                volatility = zone_analysis.get('volatility', 0)
                st.markdown(kpi_card(
                    "Volatility",
                    "Risk Level",
                    f"{volatility:.1%}",
                    "red" if volatility > 0.3 else "green" if volatility < 0.1 else "accent"
                ), unsafe_allow_html=True)

            with col_p2:
                momentum = zone_analysis.get('momentum_score', 0)
                st.markdown(kpi_card(
                    "Momentum",
                    "Trend Strength",
                    f"{momentum:+.1f}",
                    "green" if momentum > 20 else "red" if momentum < -20 else "accent"
                ), unsafe_allow_html=True)

            with col_p3:
                if predictions:
                    pred_3m = predictions[0].get('price_change_pct', 0)
                    st.markdown(kpi_card(
                        "3M Forecast",
                        "Price Change",
                        f"{pred_3m:+.1f}%",
                        "green" if pred_3m > 5 else "red" if pred_3m < -5 else "accent"
                    ), unsafe_allow_html=True)

            with col_p4:
                if predictions and len(predictions) > 1:
                    pred_6m = predictions[1].get('price_change_pct', 0) if len(predictions) > 1 else 0
                    st.markdown(kpi_card(
                        "6M Forecast",
                        "Price Change",
                        f"{pred_6m:+.1f}%",
                        "green" if pred_6m > 5 else "red" if pred_6m < -5 else "accent"
                    ), unsafe_allow_html=True)

            # Investment Signals
            if regime:
                current_regime = regime[0].get('regime', 'NEUTRAL')
                signals = generate_zone_investment_signals(zone_analysis, current_regime)

                if signals:
                    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
                    st.markdown('<div class="section-subtitle">INVESTMENT SIGNALS</div>', unsafe_allow_html=True)

                    signal_cols = st.columns(len(signals))
                    for i, signal in enumerate(signals):
                        with signal_cols[i]:
                            signal_colors = {
                                'BUY': '#10B981',
                                'HOLD': '#F59E0B',
                                'SELL': '#EF4444',
                                'WAIT': '#6B7280',
                                'RISK': '#EF4444',
                                'STABLE': '#10B981'
                            }
                            color = signal_colors.get(signal['type'], '#6B7280')

                            st.markdown(f"""
                            <div style="
                                background: rgba(19,29,50,0.8);
                                border-radius: 8px;
                                padding: 1rem;
                                border-left: 3px solid {color};
                                height: 100px;
                            ">
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                    <span style="color: {color}; font-weight: 700; font-size: 0.9rem;">{signal['type']} ({signal['strength']})</span>
                                </div>
                                <div style="color: rgba(255,255,255,0.8); font-size: 0.75rem; line-height: 1.3; margin-bottom: 0.3rem;">
                                    {signal['reason']}
                                </div>
                                <div style="color: rgba(255,255,255,0.6); font-size: 0.7rem;">
                                    {signal['timeframe']}
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

        # Price line with historical data
        fig.add_trace(go.Scatter(
            x=df['transaction_date'],
            y=df['avg_price'],
            mode='lines+markers',
            name='Historical Price',
            line=dict(color='#10B981', width=3),
            marker=dict(size=6, color='#10B981'),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))

        # Add prediction line if available
        if 'zone_analysis' in locals() and zone_analysis and zone_analysis.get('predictions'):
            last_date = df['transaction_date'].max()
            pred_dates = pd.date_range(start=last_date, periods=len(zone_analysis['predictions']) + 1, freq='M')[1:]

            pred_prices = [df['avg_price'].iloc[-1]]  # Start from last historical price
            for pred in zone_analysis['predictions']:
                pred_prices.append(pred['predicted_price'])

            fig.add_trace(go.Scatter(
                x=[last_date] + list(pred_dates),
                y=pred_prices,
                mode='lines+markers',
                name='Price Forecast',
                line=dict(color='#00D9A3', width=2, dash='dash'),
                marker=dict(size=8, symbol='diamond', color='#00D9A3')
            ))

        # Volume bars with trend
        fig.add_trace(go.Bar(
            x=df['transaction_date'],
            y=df['count'],
            name='Daily Volume',
            yaxis='y2',
            marker_color='rgba(59, 130, 246, 0.5)',
            opacity=0.6
        ))

        # Add volume trend line if available
        if 'zone_analysis' in locals() and zone_analysis:
            volume_trend = zone_analysis.get('volume_trend', 0)
            if volume_trend != 0:
                # Simple trend line for volume
                vol_trend_y = [df['count'].iloc[0] + volume_trend * i for i in range(len(df))]
                fig.add_trace(go.Scatter(
                    x=df['transaction_date'],
                    y=vol_trend_y,
                    mode='lines',
                    name='Volume Trend',
                    line=dict(color='#F59E0B', width=1, dash='dot'),
                    yaxis='y2'
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

    # === ZONE COMPARISON ===
    st.markdown("---")
    st.markdown('<div class="section-title">Zone Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">How does this zone compare to similar areas?</div>', unsafe_allow_html=True)

    # Find similar zones by price range
    if baselines:
        avg_price = sum(b.get('median_price_per_sqft', 0) for b in baselines) / len(baselines)

        similar_zones = db.execute_query("""
            SELECT
                community,
                AVG(price_per_sqft) as avg_price,
                COUNT(*) as volume,
                STDDEV(price_per_sqft) as volatility
            FROM transactions
            WHERE transaction_date >= %s - INTERVAL '30 days'
            AND community != %s
            AND ABS(AVG(price_per_sqft) - %s) / %s < 0.3  -- Within 30% price range
            GROUP BY community
            HAVING COUNT(*) >= 3
            ORDER BY ABS(AVG(price_per_sqft) - %s)
            LIMIT 5
        """, (target_date, selected_community, avg_price, avg_price, avg_price))

        if similar_zones:
            # Create comparison chart
            comparison_data = [selected_community] + [z['community'] for z in similar_zones]
            price_data = [avg_price] + [z['avg_price'] for z in similar_zones]
            volume_data = [sum(b.get('transaction_count', 0) for b in baselines)] + [z['volume'] for z in similar_zones]

            fig_compare = go.Figure()

            # Price comparison
            fig_compare.add_trace(go.Bar(
                x=comparison_data,
                y=price_data,
                name='Avg Price (AED/sqft)',
                marker_color='#10B981',
                opacity=0.8
            ))

            # Volume overlay
            fig_compare.add_trace(go.Scatter(
                x=comparison_data,
                y=volume_data,
                name='Monthly Volume',
                mode='lines+markers',
                yaxis='y2',
                line=dict(color='#3B82F6', width=3),
                marker=dict(size=8, color='#3B82F6')
            ))

            fig_compare.update_layout(
                title=dict(text=f'{selected_community} vs Similar Zones', font=dict(size=16, color='#FFFFFF')),
                height=300,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.7)', size=11),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(title='Price (AED/sqft)', gridcolor='rgba(255,255,255,0.05)'),
                yaxis2=dict(title='Volume', overlaying='y', side='right', gridcolor='rgba(255,255,255,0.05)'),
                showlegend=True,
                legend=dict(x=0.02, y=0.98)
            )

            st.plotly_chart(fig_compare, use_container_width=True)

            # Comparison insights
            selected_metrics = {
                'price': avg_price,
                'volume': sum(b.get('transaction_count', 0) for b in baselines),
                'price_rank': 1,  # Current zone is first
                'volume_rank': 1
            }

            # Calculate ranks
            all_prices = price_data[:]
            all_volumes = volume_data[:]

            selected_metrics['price_percentile'] = (sum(1 for p in all_prices if p <= avg_price) / len(all_prices)) * 100
            selected_metrics['volume_percentile'] = (sum(1 for v in all_volumes if v <= selected_metrics['volume']) / len(all_volumes)) * 100

            col_comp1, col_comp2 = st.columns(2)

            with col_comp1:
                st.markdown(f"""
                <div style="background: rgba(19,29,50,0.8); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #10B981; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">Price Positioning</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem;">
                        {selected_community} is in the <b>{selected_metrics['price_percentile']:.0f}th percentile</b> for price among similar zones,
                        indicating <b>{"premium" if selected_metrics['price_percentile'] > 70 else "value" if selected_metrics['price_percentile'] < 30 else "mid-range"}</b> positioning.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_comp2:
                st.markdown(f"""
                <div style="background: rgba(19,29,50,0.8); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="color: #3B82F6; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">Volume Performance</div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem;">
                        {selected_community} shows <b>{selected_metrics['volume_percentile']:.0f}th percentile</b> volume among peers,
                        suggesting <b>{"high" if selected_metrics['volume_percentile'] > 70 else "moderate" if selected_metrics['volume_percentile'] > 30 else "low"}</b> liquidity.
                    </div>
                </div>
                """, unsafe_allow_html=True)

else:
    st.info("Select a zone to view detailed analysis.")

st.caption(f"Last update: {get_dubai_today()} | Advanced zone analysis with predictive modeling")

"""
Advanced Investment Radar - Bloomberg-Style Trading Signals
Technical analysis, buy/sell signals, and investment recommendations
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card, progress_bar
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Deal Radar", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

# === ADVANCED TRADING SIGNALS FUNCTIONS ===

def calculate_technical_indicators(prices, window=14):
    """Calculate RSI and MACD for technical analysis"""
    if len(prices) < window + 1:
        return {'rsi': 50, 'macd': 0, 'signal': 0}

    prices = np.array(prices)

    # RSI calculation
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[-window:])
    avg_loss = np.mean(losses[-window:])

    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    # MACD (simplified)
    ema12 = np.mean(prices[-12:]) if len(prices) >= 12 else np.mean(prices)
    ema26 = np.mean(prices[-26:]) if len(prices) >= 26 else np.mean(prices)
    macd = ema12 - ema26
    signal = np.mean([macd] * 9)  # Simplified signal line

    return {
        'rsi': rsi,
        'macd': macd,
        'signal': signal,
        'histogram': macd - signal
    }

def generate_buy_sell_signals(opportunity, market_data):
    """Generate advanced buy/sell signals based on multiple factors"""
    signals = []
    score = opportunity.get('global_score', 0)
    discount = opportunity.get('discount_pct', 0)
    regime = opportunity.get('current_regime', 'NEUTRAL')

    # Signal 1: Score-based signal
    if score >= 85:
        signals.append({
            'type': 'STRONG_BUY',
            'strength': 5,
            'reason': f'Exceptional score of {score} - Rare opportunity',
            'confidence': 95
        })
    elif score >= 75:
        signals.append({
            'type': 'BUY',
            'strength': 4,
            'reason': f'High score of {score} - Good investment potential',
            'confidence': 80
        })
    elif score >= 60:
        signals.append({
            'type': 'HOLD',
            'strength': 3,
            'reason': f'Moderate score of {score} - Monitor closely',
            'confidence': 60
        })
    else:
        signals.append({
            'type': 'AVOID',
            'strength': 1,
            'reason': f'Low score of {score} - Limited potential',
            'confidence': 30
        })

    # Signal 2: Discount-based signal
    if discount >= 20:
        signals.append({
            'type': 'VALUE_BUY',
            'strength': 4,
            'reason': f'Deep discount of {discount:.1f}% below market',
            'confidence': 85
        })
    elif discount >= 10:
        signals.append({
            'type': 'MODERATE_VALUE',
            'strength': 3,
            'reason': f'Significant discount of {discount:.1f}%',
            'confidence': 70
        })

    # Signal 3: Market regime signal
    regime_signals = {
        'ACCUMULATION': {'type': 'BUY', 'reason': 'Accumulation phase favors buying'},
        'EXPANSION': {'type': 'HOLD', 'reason': 'Expansion phase - secure gains'},
        'DISTRIBUTION': {'type': 'SELL', 'reason': 'Distribution phase - consider exit'},
        'RETOURNEMENT': {'type': 'WAIT', 'reason': 'Reversal phase - exercise caution'}
    }

    if regime in regime_signals:
        reg_signal = regime_signals[regime]
        signals.append({
            'type': reg_signal['type'],
            'strength': 3,
            'reason': reg_signal['reason'],
            'confidence': 75
        })

    # Aggregate signals
    if signals:
        # Weighted average based on confidence
        total_weight = sum(s['confidence'] for s in signals)
        weighted_strength = sum(s['strength'] * s['confidence'] for s in signals) / total_weight

        if weighted_strength >= 4:
            overall_signal = 'BUY'
            color = '#10B981'
        elif weighted_strength >= 3:
            overall_signal = 'HOLD'
            color = '#F59E0B'
        elif weighted_strength >= 2:
            overall_signal = 'WAIT'
            color = '#6B7280'
        else:
            overall_signal = 'AVOID'
            color = '#EF4444'

        return {
            'overall_signal': overall_signal,
            'strength': weighted_strength,
            'color': color,
            'signals': signals,
            'confidence': sum(s['confidence'] for s in signals) / len(signals)
        }

    return None

def create_risk_assessment(opportunity, market_data):
    """Create detailed risk assessment"""
    risks = []
    score = opportunity.get('global_score', 0)
    discount = opportunity.get('discount_pct', 0)

    # Risk 1: Score risk
    if score < 50:
        risks.append({
            'type': 'SCORE_RISK',
            'level': 'HIGH',
            'description': f'Low score ({score}) indicates higher risk of value erosion',
            'impact': 'High'
        })
    elif score < 70:
        risks.append({
            'type': 'SCORE_RISK',
            'level': 'MEDIUM',
            'description': f'Moderate score ({score}) suggests average risk',
            'impact': 'Medium'
        })

    # Risk 2: Discount risk (too good to be true)
    if discount > 30:
        risks.append({
            'type': 'DISCOUNT_RISK',
            'level': 'HIGH',
            'description': f'Very deep discount ({discount:.1f}%) may indicate property issues',
            'impact': 'High'
        })

    # Risk 3: Market regime risk
    regime = opportunity.get('current_regime', 'NEUTRAL')
    if regime == 'DISTRIBUTION':
        risks.append({
            'type': 'MARKET_RISK',
            'level': 'HIGH',
            'description': 'Distribution regime suggests potential downturn',
            'impact': 'High'
        })
    elif regime == 'RETOURNEMENT':
        risks.append({
            'type': 'MARKET_RISK',
            'level': 'MEDIUM',
            'description': 'Reversal regime indicates uncertainty',
            'impact': 'Medium'
        })

    return risks

st.markdown('<div class="dashboard-header">Advanced Investment Radar</div>', unsafe_allow_html=True)

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    strategy_filter = st.selectbox("Strategy", ["All", "FLIP", "RENT", "LONG", "IGNORE"])

with col3:
    min_score = st.slider("Min Score", 0, 100, 50)

with col4:
    regime_filter = st.selectbox("Regime", ["All", "ACCUMULATION", "EXPANSION", "DISTRIBUTION", "RETOURNEMENT"])

# Query
query = """
SELECT * FROM v_active_opportunities
WHERE detection_date = %s AND global_score >= %s
"""
params = [target_date, min_score]

if strategy_filter != "All":
    query += " AND recommended_strategy = %s"
    params.append(strategy_filter)

if regime_filter != "All":
    query += " AND current_regime = %s"
    params.append(regime_filter)

query += " ORDER BY global_score DESC LIMIT 50"

opportunities = db.execute_query(query, tuple(params))

st.markdown("---")

# === KPIs ===
if opportunities:
    strategy_counts = {}
    for opp in opportunities:
        s = opp.get('recommended_strategy', 'OTHER')
        strategy_counts[s] = strategy_counts.get(s, 0) + 1
    
    avg_discount = sum(opp.get('discount_pct', 0) or 0 for opp in opportunities) / len(opportunities)
    avg_score = sum(opp.get('global_score', 0) or 0 for opp in opportunities) / len(opportunities)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(kpi_card("Total", "Opportunities", str(len(opportunities)), "accent"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(kpi_card("FLIP", "Strategy", str(strategy_counts.get('FLIP', 0))), unsafe_allow_html=True)
    
    with col3:
        st.markdown(kpi_card("RENT", "Strategy", str(strategy_counts.get('RENT', 0))), unsafe_allow_html=True)
    
    with col4:
        st.markdown(kpi_card("Avg Score", "Quality", f"{avg_score:.0f}%", "green"), unsafe_allow_html=True)
    
    with col5:
        st.markdown(kpi_card("Avg Discount", "Below market", f"{avg_discount:.1f}%"), unsafe_allow_html=True)
    
    st.markdown("---")

    # === TECHNICAL ANALYSIS ===
    st.markdown('<div class="section-title">Technical Market Analysis</div>', unsafe_allow_html=True)

    # Get market-wide technical indicators
    technical_data = db.execute_query("""
        SELECT
            DATE_TRUNC('week', transaction_date) as week,
            AVG(price_per_sqft) as avg_price,
            COUNT(*) as volume
        FROM transactions
        WHERE transaction_date >= CURRENT_DATE - INTERVAL '60 days'
        GROUP BY DATE_TRUNC('week', transaction_date)
        ORDER BY week
    """)

    if technical_data and len(technical_data) >= 3:
        prices = [d['avg_price'] for d in technical_data]
        volumes = [d['volume'] for d in technical_data]

        # Calculate technical indicators
        tech_indicators = calculate_technical_indicators(prices)

        col_tech1, col_tech2, col_tech3, col_tech4 = st.columns(4)

        with col_tech1:
            rsi = tech_indicators['rsi']
            rsi_color = '#10B981' if rsi > 70 else '#EF4444' if rsi < 30 else '#F59E0B'
            st.markdown(kpi_card(
                "RSI",
                "Market Momentum",
                f"{rsi:.1f}",
                "green" if rsi > 70 else "red" if rsi < 30 else "accent"
            ), unsafe_allow_html=True)

        with col_tech2:
            macd = tech_indicators['macd']
            st.markdown(kpi_card(
                "MACD",
                "Trend Strength",
                f"{macd:+.1f}",
                "green" if macd > 0 else "red"
            ), unsafe_allow_html=True)

        with col_tech3:
            histogram = tech_indicators['histogram']
            st.markdown(kpi_card(
                "MACD Histogram",
                "Momentum Change",
                f"{histogram:+.1f}",
                "green" if histogram > 0 else "red"
            ), unsafe_allow_html=True)

        with col_tech4:
            # Market sentiment based on RSI
            if rsi > 70:
                sentiment = "OVERBOUGHT"
                sentiment_color = "red"
            elif rsi < 30:
                sentiment = "OVERSOLD"
                sentiment_color = "green"
            else:
                sentiment = "NEUTRAL"
                sentiment_color = "accent"

            st.markdown(kpi_card(
                "Market Sentiment",
                "Technical View",
                sentiment,
                sentiment_color
            ), unsafe_allow_html=True)

        # Technical chart
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        fig_tech = go.Figure()

        # Price line
        fig_tech.add_trace(go.Scatter(
            x=[d['week'] for d in technical_data],
            y=prices,
            mode='lines+markers',
            name='Market Price',
            line=dict(color='#10B981', width=2),
            marker=dict(size=6)
        ))

        # RSI indicator
        rsi_values = []
        for i in range(len(prices)):
            if i >= 14:
                rsi_val = calculate_technical_indicators(prices[:i+1])['rsi']
                rsi_values.append(rsi_val)
            else:
                rsi_values.append(50)

        fig_tech.add_trace(go.Scatter(
            x=[d['week'] for d in technical_data],
            y=rsi_values,
            mode='lines',
            name='RSI',
            yaxis='y2',
            line=dict(color='#F59E0B', width=1, dash='dot')
        ))

        # Add RSI levels
        fig_tech.add_hline(y=70, line_dash="dash", line_color="#EF4444", yref='y2', annotation_text="Overbought")
        fig_tech.add_hline(y=30, line_dash="dash", line_color="#10B981", yref='y2', annotation_text="Oversold")

        fig_tech.update_layout(
            title=dict(text='Technical Analysis - Price & RSI', font=dict(size=16, color='#FFFFFF')),
            height=350,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)', size=11),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Price (AED/sqft)', gridcolor='rgba(255,255,255,0.05)'),
            yaxis2=dict(title='RSI', overlaying='y', side='right', range=[0, 100], gridcolor='rgba(255,255,255,0.05)'),
            showlegend=True
        )

        st.plotly_chart(fig_tech, use_container_width=True)

    st.markdown("---")

    # === TRADING SIGNALS ===
    st.markdown('<div class="section-title">Advanced Trading Signals</div>', unsafe_allow_html=True)

    # Generate signals for top opportunities
    top_opportunities = opportunities[:5] if opportunities else []

    if top_opportunities:
        signal_cols = st.columns(len(top_opportunities))

        for i, opp in enumerate(top_opportunities):
            with signal_cols[i]:
                signals_data = generate_buy_sell_signals(opp, technical_data)

                if signals_data:
                    location = f"{opp.get('community', 'N/A')[:10]}..."
                    signal_type = signals_data['overall_signal']
                    strength = signals_data['strength']
                    confidence = signals_data['confidence']

                    signal_colors = {
                        'BUY': '#10B981',
                        'HOLD': '#F59E0B',
                        'WAIT': '#6B7280',
                        'AVOID': '#EF4444'
                    }

                    color = signal_colors.get(signal_type, '#6B7280')

                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(19,29,50,0.95) 0%, rgba(15,26,46,0.95) 100%);
                        border-radius: 12px;
                        padding: 1.2rem;
                        border-left: 4px solid {color};
                        height: 200px;
                        display: flex;
                        flex-direction: column;
                    ">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="color: {color}; font-weight: 700; font-size: 1rem;">{signal_type}</span>
                            <span style="background: {color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;">{strength:.1f}</span>
                        </div>
                        <div style="color: rgba(255,255,255,0.6); font-size: 0.75rem; margin-bottom: 0.3rem;">{location}</div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem; flex: 1;">Score: {opp.get('global_score', 0)}<br>Confidence: {confidence:.0f}%</div>
                        <div style="color: {color}; font-size: 0.7rem; font-weight: 600; margin-top: 0.5rem;">→ EXECUTE</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")

    # === MAIN TABLE ===
    st.markdown('<div class="section-title">Opportunities</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">SORTED BY SCORE</div>', unsafe_allow_html=True)
    
    import pandas as pd
    
    df_data = []
    for opp in opportunities:
        df_data.append({
            "Location": f"{opp.get('community', 'N/A')} / {opp.get('building', 'N/A')}",
            "Type": opp.get('rooms_bucket', 'N/A'),
            "Score": opp.get('global_score', 0),
            "Discount": f"{opp.get('discount_pct', 0):.1f}%",
            "Strategy": opp.get('recommended_strategy', 'N/A'),
            "Regime": opp.get('current_regime', 'N/A')
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                min_value=0,
                max_value=100,
                format="%d"
            )
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === CHARTS ===
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Strategy pie
        fig = go.Figure(data=[go.Pie(
            labels=list(strategy_counts.keys()),
            values=list(strategy_counts.values()),
            hole=0.5,
            marker=dict(colors=['#10B981', '#3B82F6', '#F59E0B', '#6B7280']),
            textinfo='label+value',
            textposition='outside',
            textfont=dict(size=11, color='#FFFFFF')
        )])
        
        fig.update_layout(
            title=dict(text='Strategy Distribution', font=dict(size=14, color='#FFFFFF')),
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_c2:
        # Score vs Discount scatter
        scores = [opp.get('global_score', 0) for opp in opportunities]
        discounts = [opp.get('discount_pct', 0) for opp in opportunities]
        names = [f"{opp.get('community', 'N/A')}" for opp in opportunities]
        
        fig = go.Figure(data=[go.Scatter(
            x=discounts,
            y=scores,
            mode='markers',
            marker=dict(
                size=12,
                color=scores,
                colorscale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
                showscale=True,
                colorbar=dict(title='Score', tickfont=dict(color='#FFFFFF'))
            ),
            text=names,
            hovertemplate='%{text}<br>Score: %{y}<br>Discount: %{x}%<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text='Score vs Discount', font=dict(size=14, color='#FFFFFF')),
            height=300,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='Discount %', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Score', gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # === RISK ASSESSMENT & RECOMMENDATIONS ===
        st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Assessment & Investment Recommendations</div>', unsafe_allow_html=True)

        if opportunities:
            # Top opportunity detailed analysis
            top_opp = opportunities[0]
            risks = create_risk_assessment(top_opp, technical_data)

            col_risk1, col_risk2 = st.columns(2)

            with col_risk1:
                st.markdown('<div class="section-subtitle">RISK PROFILE</div>', unsafe_allow_html=True)

                if risks:
                    for risk in risks[:3]:  # Show top 3 risks
                        risk_colors = {
                            'HIGH': '#EF4444',
                            'MEDIUM': '#F59E0B',
                            'LOW': '#10B981'
                        }
                        color = risk_colors.get(risk['level'], '#6B7280')

                        st.markdown(f"""
                        <div style="
                            background: rgba(19,29,50,0.8);
                            border-radius: 8px;
                            padding: 1rem;
                            border-left: 3px solid {color};
                            margin-bottom: 0.8rem;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                                <span style="color: {color}; font-weight: 600; font-size: 0.85rem;">{risk['type'].replace('_', ' ')}</span>
                                <span style="background: {color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem;">{risk['level']}</span>
                            </div>
                            <div style="color: rgba(255,255,255,0.8); font-size: 0.75rem; line-height: 1.3;">
                                {risk['description']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: rgba(16,185,129,0.1); border-radius: 8px; padding: 1rem; border: 1px solid #10B981;">
                        <div style="color: #10B981; font-weight: 600; margin-bottom: 0.3rem;">LOW RISK PROFILE</div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 0.8rem;">This opportunity shows favorable risk characteristics.</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_risk2:
                st.markdown('<div class="section-subtitle">INVESTMENT RECOMMENDATION</div>', unsafe_allow_html=True)

                # Generate recommendation based on all factors
                score = top_opp.get('global_score', 0)
                discount = top_opp.get('discount_pct', 0)
                strategy = top_opp.get('recommended_strategy', 'HOLD')

                # Scoring system
                total_score = score + (discount * 2)  # Weight discount heavily
                if strategy == 'FLIP':
                    total_score += 10  # Bonus for flip strategy
                elif strategy == 'RENT':
                    total_score += 5   # Moderate bonus for rental

                if total_score >= 120:
                    recommendation = {
                        'action': 'AGGRESSIVE_BUY',
                        'rationale': 'Exceptional combination of high score, deep discount, and strong strategy alignment',
                        'timeframe': 'Immediate execution within 24-48 hours',
                        'position_size': 'Maximum recommended allocation'
                    }
                elif total_score >= 100:
                    recommendation = {
                        'action': 'BUY',
                        'rationale': 'Strong fundamentals with good risk-reward profile',
                        'timeframe': 'Execute within 1 week',
                        'position_size': 'Standard allocation (20-30%)'
                    }
                elif total_score >= 80:
                    recommendation = {
                        'action': 'MONITOR',
                        'rationale': 'Decent opportunity but requires careful monitoring',
                        'timeframe': 'Wait for optimal entry timing',
                        'position_size': 'Reduced allocation (10-20%)'
                    }
                else:
                    recommendation = {
                        'action': 'PASS',
                        'rationale': 'Does not meet investment criteria at current levels',
                        'timeframe': 'Consider alternative opportunities',
                        'position_size': 'No allocation recommended'
                    }

                action_colors = {
                    'AGGRESSIVE_BUY': '#10B981',
                    'BUY': '#3B82F6',
                    'MONITOR': '#F59E0B',
                    'PASS': '#EF4444'
                }

                color = action_colors.get(recommendation['action'], '#6B7280')

                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(19,29,50,0.95) 0%, rgba(15,26,46,0.95) 100%);
                    border-radius: 12px;
                    padding: 1.5rem;
                    border-left: 4px solid {color};
                    height: 280px;
                    display: flex;
                    flex-direction: column;
                ">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                        <span style="font-size: 1.5rem;">
                            {'[AGGRESSIVE]' if recommendation['action'] == 'AGGRESSIVE_BUY' else '[BUY]' if recommendation['action'] == 'BUY' else '[MONITOR]' if recommendation['action'] == 'MONITOR' else '[AVOID]'}
                        </span>
                        <span style="color: {color}; font-weight: 700; font-size: 1.1rem;">{recommendation['action'].replace('_', ' ')}</span>
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 0.85rem; line-height: 1.4; flex: 1;">
                        <b>Rationale:</b> {recommendation['rationale']}<br><br>
                        <b>Timeframe:</b> {recommendation['timeframe']}<br>
                        <b>Position Size:</b> {recommendation['position_size']}
                    </div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
                        <div style="color: {color}; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
                            Investment Score: {total_score:.0f}/150
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

else:
    st.info("No opportunities with these criteria.")

st.caption(f"Last update: {get_dubai_today()} | Advanced trading signals and risk analysis powered by AI")

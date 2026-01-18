"""
Predictive Alerts - Bloomberg-Style Risk Monitoring
Advanced risk analysis, predictive notifications, and market intelligence alerts
"""
import streamlit as st
from core.db import db
from core.utils import get_dubai_today
from core.styles import apply_plecto_style, kpi_card
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Alerts", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

# === PREDICTIVE ALERTS FUNCTIONS ===

def generate_predictive_alerts(market_data):
    """Generate predictive alerts based on market conditions"""
    alerts = []

    if not market_data:
        return alerts

    # Get recent market data
    recent_prices = db.execute_query("""
        SELECT transaction_date, AVG(price_per_sqft) as avg_price
        FROM transactions
        WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY transaction_date
        ORDER BY transaction_date DESC
        LIMIT 10
    """)

    if len(recent_prices) >= 5:
        prices = [p['avg_price'] for p in recent_prices[::-1]]  # Reverse to chronological order

        # Trend analysis
        if len(prices) >= 3:
            recent_trend = (prices[-1] - prices[-3]) / prices[-3]

            if recent_trend > 0.05:  # 5% increase in 3 days
                alerts.append({
                    'type': 'TREND_ALERT',
                    'severity': 'high',
                    'title': 'Rapid Price Acceleration',
                    'message': f'Market prices increased {recent_trend:.1%} in 3 days. Potential bubble formation.',
                    'recommendation': 'Monitor closely, consider profit-taking',
                    'confidence': 85
                })
            elif recent_trend < -0.03:  # 3% drop
                alerts.append({
                    'type': 'TREND_ALERT',
                    'severity': 'medium',
                    'title': 'Price Decline Alert',
                    'message': f'Market prices dropped {abs(recent_trend):.1%} in 3 days. Buying opportunity?',
                    'recommendation': 'Evaluate undervalued opportunities',
                    'confidence': 75
                })

    # Volume spike detection
    volume_data = db.execute_query("""
        SELECT transaction_date, COUNT(*) as volume
        FROM transactions
        WHERE transaction_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY transaction_date
        ORDER BY transaction_date DESC
    """)

    if volume_data:
        volumes = [v['volume'] for v in volume_data]
        avg_volume = np.mean(volumes)
        max_volume = max(volumes)

        if max_volume > avg_volume * 1.5:  # 50% above average
            alerts.append({
                'type': 'VOLUME_SPIKE',
                'severity': 'high',
                'title': 'Unusual Trading Volume',
                'message': f'Trading volume {max_volume/avg_volume:.1f}x above normal. Institutional activity?',
                'recommendation': 'Monitor price movements closely',
                'confidence': 90
            })

    # Regime change alerts
    regime_data = db.execute_query("""
        SELECT regime, confidence_score, regime_date
        FROM market_regimes
        WHERE regime_date >= CURRENT_DATE - INTERVAL '2 days'
        ORDER BY regime_date DESC
        LIMIT 2
    """)

    if len(regime_data) >= 2:
        current_regime = regime_data[0]['regime']
        previous_regime = regime_data[1]['regime']

        if current_regime != previous_regime:
            severity = 'high' if current_regime in ['DISTRIBUTION', 'RETOURNEMENT'] else 'medium'

            alerts.append({
                'type': 'REGIME_CHANGE',
                'severity': severity,
                'title': f'Market Regime Shift: {previous_regime} → {current_regime}',
                'message': f'Market regime changed from {previous_regime} to {current_regime} with {regime_data[0]["confidence_score"]:.0%} confidence.',
                'recommendation': 'Adjust investment strategy accordingly',
                'confidence': regime_data[0]["confidence_score"] * 100
            })

    return alerts

def calculate_risk_exposure(opportunities):
    """Calculate portfolio risk exposure"""
    if not opportunities:
        return {}

    total_exposure = len(opportunities)
    high_risk = sum(1 for opp in opportunities if opp.get('global_score', 0) < 50)
    medium_risk = sum(1 for opp in opportunities if 50 <= opp.get('global_score', 0) < 75)
    low_risk = sum(1 for opp in opportunities if opp.get('global_score', 0) >= 75)

    return {
        'total_exposure': total_exposure,
        'high_risk_count': high_risk,
        'medium_risk_count': medium_risk,
        'low_risk_count': low_risk,
        'high_risk_pct': high_risk / total_exposure * 100 if total_exposure > 0 else 0,
        'concentration_risk': max(high_risk, medium_risk, low_risk) / total_exposure if total_exposure > 0 else 0
    }

st.markdown('<div class="dashboard-header">Predictive Alerts & Risk Monitoring</div>', unsafe_allow_html=True)

# Filters
col1, col2 = st.columns([1, 3])

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    severity_filter = st.multiselect("Severity", ["high", "medium", "low"], default=["high", "medium"])

st.markdown("---")

# Query
query = """
SELECT * FROM alerts
WHERE %s = %s
ORDER BY created_at DESC
LIMIT 50
"""

# Simple query without filters for now
alerts = db.execute_query("""
SELECT 
    id, alert_type as rule_code, severity, title, message, 
    community, created_at
FROM alerts
WHERE is_dismissed = FALSE
ORDER BY created_at DESC
LIMIT 50
""")

if alerts:
    # Filter by severity
    if severity_filter:
        alerts = [a for a in alerts if (a.get('severity') or 'medium').lower() in [s.lower() for s in severity_filter]]
    
    # === KPIs ===
    high_count = sum(1 for a in alerts if (a.get('severity') or '').lower() == 'high')
    medium_count = sum(1 for a in alerts if (a.get('severity') or '').lower() == 'medium')
    low_count = sum(1 for a in alerts if (a.get('severity') or '').lower() == 'low')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(kpi_card("Total", "Alerts", str(len(alerts)), "accent"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(kpi_card("High", "Priority", str(high_count)), unsafe_allow_html=True)
    
    with col3:
        st.markdown(kpi_card("Medium", "Priority", str(medium_count)), unsafe_allow_html=True)
    
    with col4:
        st.markdown(kpi_card("Low", "Priority", str(low_count)), unsafe_allow_html=True)
    
    st.markdown("---")

    # === PREDICTIVE ALERTS ===
    st.markdown('<div class="section-title">Predictive Market Alerts</div>', unsafe_allow_html=True)

    predictive_alerts = generate_predictive_alerts(alerts)

    if predictive_alerts:
        for alert in predictive_alerts[:3]:  # Show top 3
            severity_colors = {
                'high': '#EF4444',
                'medium': '#F59E0B',
                'low': '#10B981'
            }

            color = severity_colors.get(alert['severity'], '#6B7280')

            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(19,29,50,0.95) 0%, rgba(15,26,46,0.95) 100%);
                border-radius: 12px;
                padding: 1.5rem;
                border-left: 4px solid {color};
                margin-bottom: 1rem;
            ">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem;">{'[CRITICAL]' if alert['severity'] == 'high' else '[WARNING]' if alert['severity'] == 'medium' else '[INFO]'}</span>
                    <span style="color: {color}; font-weight: 700; font-size: 1rem;">{alert['title']}</span>
                    <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600;">{alert['severity'].upper()}</span>
                </div>
                <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem; line-height: 1.4; margin-bottom: 0.8rem;">
                    {alert['message']}
                </div>
                <div style="color: {color}; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.3rem;">
                    → {alert['recommendation']}
                </div>
                <div style="color: rgba(255,255,255,0.6); font-size: 0.75rem;">
                    Confidence: {alert['confidence']:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No predictive alerts at this time. Market conditions are stable.")

    # === RISK EXPOSURE ANALYSIS ===
    st.markdown("---")
    st.markdown('<div class="section-title">Risk Exposure Analysis</div>', unsafe_allow_html=True)

    # Get opportunities for risk analysis
    opportunities = db.execute_query("""
        SELECT * FROM v_active_opportunities
        WHERE detection_date = %s AND global_score >= 50
        ORDER BY global_score DESC
        LIMIT 20
    """, (target_date,))

    if opportunities:
        risk_exposure = calculate_risk_exposure(opportunities)

        col_r1, col_r2, col_r3, col_r4 = st.columns(4)

        with col_r1:
            st.markdown(kpi_card(
                "Total Exposure",
                "Active Positions",
                str(risk_exposure['total_exposure']),
                "blue"
            ), unsafe_allow_html=True)

        with col_r2:
            st.markdown(kpi_card(
                "High Risk",
                "Positions",
                f"{risk_exposure['high_risk_count']} ({risk_exposure['high_risk_pct']:.0f}%)",
                "red" if risk_exposure['high_risk_pct'] > 30 else "accent"
            ), unsafe_allow_html=True)

        with col_r3:
            st.markdown(kpi_card(
                "Low Risk",
                "Positions",
                str(risk_exposure['low_risk_count']),
                "green"
            ), unsafe_allow_html=True)

        with col_r4:
            concentration = risk_exposure['concentration_risk'] * 100
            st.markdown(kpi_card(
                "Concentration",
                "Risk Level",
                f"{concentration:.0f}%",
                "red" if concentration > 60 else "green" if concentration < 40 else "accent"
            ), unsafe_allow_html=True)

    st.markdown("---")

    # === ALERTS LIST ===
    st.markdown('<div class="section-title">Active Alerts</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Recent notifications</div>', unsafe_allow_html=True)
    
    for alert in alerts:
        severity = (alert.get('severity') or 'medium').lower()
        
        # Colors
        colors = {
            'high': ('#EF4444', 'rgba(239, 68, 68, 0.1)'),
            'medium': ('#F59E0B', 'rgba(245, 158, 11, 0.1)'),
            'low': ('#3B82F6', 'rgba(59, 130, 246, 0.1)')
        }
        accent, bg = colors.get(severity, ('#6B7280', 'rgba(107, 114, 128, 0.1)'))
        
        st.markdown(f"""
        <div style="
            background: {bg};
            border-left: 4px solid {accent};
            border-radius: 8px;
            padding: 1rem 1.5rem;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                <span style="
                    background: {accent};
                    color: white;
                    padding: 0.2rem 0.6rem;
                    border-radius: 4px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    text-transform: uppercase;
                ">{severity}</span>
                <span style="color: rgba(255,255,255,0.4); font-size: 0.75rem;">{alert.get('created_at', 'N/A')}</span>
            </div>
            <div style="color: #FFFFFF; font-weight: 500; font-size: 0.95rem; margin-bottom: 0.5rem;">
                {alert.get('rule_code', 'Alert')}
            </div>
            <div style="color: rgba(255,255,255,0.7); font-size: 0.85rem;">
                {alert.get('message', 'No details')}
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("No active alerts.")

st.caption(f"Last update: {get_dubai_today()}")

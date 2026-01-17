"""
Alerts - Tech Company Style
"""
import streamlit as st
from core.db import db
from core.utils import get_dubai_today
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(page_title="Alerts", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Alerts</div>', unsafe_allow_html=True)

# Filters
col1, col2 = st.columns([1, 3])

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    severity_filter = st.multiselect("Severity", ["high", "medium", "low"], default=["high", "medium"])

st.markdown("---")

# Query
query = """
SELECT * FROM active_alerts
WHERE %s = %s
ORDER BY created_at DESC
LIMIT 50
"""

# Simple query without filters for now
alerts = db.execute_query("""
SELECT * FROM active_alerts
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

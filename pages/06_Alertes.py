"""
Page Alertes - Dubai Premium Gold Design
"""
import streamlit as st
from datetime import timedelta
from core.db import db
from core.utils import get_dubai_today
from core.styles import apply_plecto_style, kpi_card, status_badge

st.set_page_config(page_title="Alerts", page_icon="", layout="wide")

# Apply Premium Gold style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Alerts</div>', unsafe_allow_html=True)

# Filtres
col1, col2 = st.columns(2)

with col1:
    days_back = st.slider("Days to display", 1, 30, 7)

with col2:
    show_dismissed = st.checkbox("Show dismissed alerts", value=False)

# Récupérer les alertes
query = """
SELECT * FROM alerts
WHERE alert_date >= %s
"""
params = [get_dubai_today() - timedelta(days=days_back)]

if not show_dismissed:
    query += " AND is_dismissed = FALSE"

query += " ORDER BY alert_date DESC, severity DESC"

alerts = db.execute_query(query, tuple(params))

# Statistiques
if alerts:
    severity_counts = {}
    for alert in alerts:
        severity = alert.get('severity', 'low')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", len(alerts))
    with col2:
        st.metric("Critical", severity_counts.get('critical', 0))
    with col3:
        st.metric("High", severity_counts.get('high', 0))
    with col4:
        st.metric("Medium", severity_counts.get('medium', 0))
    
    st.markdown("---")
    
    # Affichage des alertes
    for alert in alerts:
        severity = alert.get('severity', 'low')
        
        # Container avec couleur
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                severity_color = {
                    'critical': '#D4AF37',
                    'high': '#CD7F32',
                    'medium': '#8B4513',
                    'low': '#5C4033'
                }.get(severity, '#5C4033')
                
                st.markdown(f"<span style='color: {severity_color}; font-weight: 600;'>{severity.upper()}</span> **{alert.get('title', 'N/A')}**", unsafe_allow_html=True)
                st.caption(alert.get('message', ''))
            
            with col2:
                alert_date = alert.get('alert_date')
                if alert_date:
                    st.caption(f"{alert_date.strftime('%Y-%m-%d %H:%M')}")
            
            # Actions
            col3, col4, col5 = st.columns([1, 1, 2])
            
            with col3:
                if not alert.get('is_read'):
                    if st.button("Mark read", key=f"read_{alert['id']}"):
                        db.execute_query(
                            "UPDATE alerts SET is_read = TRUE WHERE id = %s",
                            (alert['id'],)
                        )
                        st.rerun()
            
            with col4:
                if not alert.get('is_dismissed'):
                    if st.button("Dismiss", key=f"dismiss_{alert['id']}"):
                        db.execute_query(
                            "UPDATE alerts SET is_dismissed = TRUE WHERE id = %s",
                            (alert['id'],)
                        )
                        st.rerun()
            
            with col5:
                if alert.get('community'):
                    st.caption(f"Location: {alert['community']}")
            
            st.markdown("---")
else:
    st.info("No alerts for this period.")

st.caption(f"Last update: {get_dubai_today()}")

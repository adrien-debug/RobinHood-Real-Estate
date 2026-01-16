"""
Page Alertes - Notifications actives
"""
import streamlit as st
from datetime import timedelta
from core.db import db
from core.utils import get_dubai_today

st.set_page_config(page_title="Alertes", page_icon="🔔", layout="wide")

st.title("🔔 Alertes")

# Filtres
col1, col2 = st.columns(2)

with col1:
    days_back = st.slider("Jours à afficher", 1, 30, 7)

with col2:
    show_dismissed = st.checkbox("Afficher les alertes ignorées", value=False)

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
        st.metric("🔴 Critique", severity_counts.get('critical', 0))
    with col3:
        st.metric("🟠 Haute", severity_counts.get('high', 0))
    with col4:
        st.metric("🟡 Moyenne", severity_counts.get('medium', 0))
    
    st.markdown("---")
    
    # Affichage des alertes
    for alert in alerts:
        severity = alert.get('severity', 'low')
        
        # Emoji selon sévérité
        emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(severity, '⚪')
        
        # Container avec couleur
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"{emoji} **{alert.get('title', 'N/A')}**")
                st.caption(alert.get('message', ''))
            
            with col2:
                alert_date = alert.get('alert_date')
                if alert_date:
                    st.caption(f"📅 {alert_date.strftime('%Y-%m-%d %H:%M')}")
            
            # Actions
            col3, col4, col5 = st.columns([1, 1, 2])
            
            with col3:
                if not alert.get('is_read'):
                    if st.button("✅ Marquer lu", key=f"read_{alert['id']}"):
                        db.execute_query(
                            "UPDATE alerts SET is_read = TRUE WHERE id = %s",
                            (alert['id'],)
                        )
                        st.rerun()
            
            with col4:
                if not alert.get('is_dismissed'):
                    if st.button("🗑️ Ignorer", key=f"dismiss_{alert['id']}"):
                        db.execute_query(
                            "UPDATE alerts SET is_dismissed = TRUE WHERE id = %s",
                            (alert['id'],)
                        )
                        st.rerun()
            
            with col5:
                if alert.get('community'):
                    st.caption(f"📍 {alert['community']}")
            
            st.markdown("---")
else:
    st.info("Aucune alerte pour cette période.")

st.caption(f"Dernière mise à jour : {get_dubai_today()}")

"""
Système de notification d'alertes
"""
from typing import List, Dict
from datetime import date
import httpx
from loguru import logger
from core.config import settings
from core.db import db
from alerts.rules import AlertRules


class AlertNotifier:
    """Gestionnaire de notifications d'alertes"""
    
    def __init__(self):
        self.webhook_url = settings.alert_webhook_url
        self.email = settings.alert_email
    
    def send_daily_alerts(self, target_date: date) -> int:
        """
        Envoyer les alertes quotidiennes
        
        Returns:
            Nombre d'alertes envoyées
        """
        # Récupérer les alertes
        alerts = AlertRules.get_all_alerts(target_date)
        
        if not alerts:
            logger.info("Aucune alerte à envoyer")
            return 0
        
        # Sauvegarder dans la base
        self._save_alerts(alerts)
        
        # Envoyer les notifications
        if self.webhook_url:
            self._send_webhook_notifications(alerts)
        
        if self.email:
            self._send_email_notifications(alerts)
        
        logger.info(f"✅ Alertes traitées : {len(alerts)}")
        return len(alerts)
    
    def _save_alerts(self, alerts: List[Dict]):
        """Sauvegarder les alertes dans la base"""
        if not alerts:
            return
        
        columns = [
            'alert_type', 'severity', 'title', 'message',
            'opportunity_id', 'community'
        ]
        
        values = [
            (
                a['alert_type'],
                a['severity'],
                a['title'],
                a['message'],
                a.get('opportunity_id'),
                a.get('community')
            )
            for a in alerts
        ]
        
        db.execute_batch_insert('alerts', columns, values)
        logger.info(f"Alertes sauvegardées : {len(alerts)}")
    
    def _send_webhook_notifications(self, alerts: List[Dict]):
        """Envoyer les alertes via webhook (Slack, Discord, etc.)"""
        try:
            # Grouper par sévérité
            critical = [a for a in alerts if a['severity'] == 'critical']
            high = [a for a in alerts if a['severity'] == 'high']
            medium = [a for a in alerts if a['severity'] == 'medium']
            
            # Construire le message
            message = "🚨 *Alertes Marché Immobilier Dubaï*\n\n"
            
            if critical:
                message += f"🔴 *CRITIQUE* ({len(critical)})\n"
                for a in critical[:3]:
                    message += f"  • {a['title']}\n"
                message += "\n"
            
            if high:
                message += f"🟠 *HAUTE* ({len(high)})\n"
                for a in high[:5]:
                    message += f"  • {a['title']}\n"
                message += "\n"
            
            if medium:
                message += f"🟡 *MOYENNE* ({len(medium)})\n"
            
            # Format Slack
            payload = {
                "text": message,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    }
                ]
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.webhook_url, json=payload)
                response.raise_for_status()
            
            logger.info("Webhook notifications envoyées")
        
        except Exception as e:
            logger.error(f"Erreur webhook notifications : {e}")
    
    def _send_email_notifications(self, alerts: List[Dict]):
        """Envoyer les alertes par email"""
        # TODO : Implémenter l'envoi d'emails
        # Nécessite un service SMTP ou API (SendGrid, AWS SES, etc.)
        logger.info(f"Email notifications : {len(alerts)} alertes (non implémenté)")

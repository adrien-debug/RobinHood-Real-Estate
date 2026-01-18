"""
Pipeline : Logger de qualité des données

Module centralisé pour le tracking de la qualité des données :
- Taux de rejet par raison (outliers, doublons, champs manquants)
- Complétude par champ (% non-null)
- Volume par source et par jour
- Alertes sur dégradation de qualité
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal
import json
from loguru import logger

from core.db import db
from core.models import QualityLog


class QualityLogger:
    """
    Logger centralisé pour la qualité des données
    
    Usage:
        logger = QualityLogger("transactions", "ingestion")
        logger.start()
        
        for record in records:
            if is_valid(record):
                logger.accept()
            else:
                logger.reject("outlier")
        
        logger.set_field_completeness({"price": 100, "area": 95.5})
        logger.finish()
    """
    
    def __init__(self, source_type: str, pipeline_step: str):
        """
        Initialiser le logger de qualité
        
        Args:
            source_type: Type de source ('transactions', 'listings', 'rental_index', etc.)
            pipeline_step: Étape du pipeline ('ingestion', 'normalization', 'feature_computation')
        """
        self.source_type = source_type
        self.pipeline_step = pipeline_step
        
        self._start_time: Optional[datetime] = None
        self._records_total = 0
        self._records_accepted = 0
        self._records_rejected = 0
        self._rejection_reasons: Dict[str, int] = {}
        self._field_completeness: Dict[str, float] = {}
        self._status = "success"
        self._error_message: Optional[str] = None
    
    def start(self):
        """Démarrer le tracking"""
        self._start_time = datetime.now()
        logger.debug(f"QualityLogger démarré : {self.source_type}/{self.pipeline_step}")
    
    def add_total(self, count: int = 1):
        """Ajouter au compteur total"""
        self._records_total += count
    
    def accept(self, count: int = 1):
        """Enregistrer un record accepté"""
        self._records_accepted += count
    
    def reject(self, reason: str, count: int = 1):
        """
        Enregistrer un rejet avec sa raison
        
        Args:
            reason: Raison du rejet ('outlier', 'duplicate', 'missing_field', 'invalid_price', etc.)
            count: Nombre de rejets (défaut: 1)
        """
        self._records_rejected += count
        self._rejection_reasons[reason] = self._rejection_reasons.get(reason, 0) + count
    
    def set_field_completeness(self, completeness: Dict[str, float]):
        """
        Définir les stats de complétude des champs
        
        Args:
            completeness: Dict avec {field_name: pourcentage_non_null}
        """
        self._field_completeness = completeness
    
    def set_error(self, message: str):
        """Marquer le run comme erreur"""
        self._status = "error"
        self._error_message = message
    
    def set_warning(self):
        """Marquer le run comme warning"""
        if self._status != "error":
            self._status = "warning"
    
    def finish(self) -> QualityLog:
        """
        Terminer le tracking et sauvegarder le log
        
        Returns:
            QualityLog créé
        """
        execution_time_ms = 0
        if self._start_time:
            execution_time_ms = int((datetime.now() - self._start_time).total_seconds() * 1000)
        
        # Déterminer le statut automatiquement si pas d'erreur
        if self._status == "success":
            if self._records_total > 0:
                rejection_rate = self._records_rejected / self._records_total
                if rejection_rate > 0.5:
                    self._status = "warning"
        
        quality_log = QualityLog(
            run_date=datetime.now(),
            source_type=self.source_type,
            pipeline_step=self.pipeline_step,
            records_total=self._records_total,
            records_accepted=self._records_accepted,
            records_rejected=self._records_rejected,
            rejection_reasons=self._rejection_reasons,
            field_completeness=self._field_completeness,
            execution_time_ms=execution_time_ms,
            status=self._status,
            error_message=self._error_message
        )
        
        # Sauvegarder en base
        self._save_to_db(quality_log)
        
        # Log résumé
        logger.info(
            f"QualityLog [{self.source_type}/{self.pipeline_step}] : "
            f"{self._records_accepted}/{self._records_total} acceptés, "
            f"{self._records_rejected} rejetés ({execution_time_ms}ms)"
        )
        
        return quality_log
    
    def _save_to_db(self, quality_log: QualityLog):
        """Sauvegarder le log en base de données"""
        try:
            query = """
            INSERT INTO quality_logs (
                run_date, source_type, pipeline_step,
                records_total, records_accepted, records_rejected,
                rejection_reasons, field_completeness,
                execution_time_ms, status, error_message
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            db.execute_query(query, (
                quality_log.run_date,
                quality_log.source_type,
                quality_log.pipeline_step,
                quality_log.records_total,
                quality_log.records_accepted,
                quality_log.records_rejected,
                json.dumps(quality_log.rejection_reasons),
                json.dumps(quality_log.field_completeness),
                quality_log.execution_time_ms,
                quality_log.status,
                quality_log.error_message
            ))
            
        except Exception as e:
            logger.warning(f"Erreur sauvegarde quality log : {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les stats actuelles"""
        return {
            "source_type": self.source_type,
            "pipeline_step": self.pipeline_step,
            "records_total": self._records_total,
            "records_accepted": self._records_accepted,
            "records_rejected": self._records_rejected,
            "rejection_reasons": self._rejection_reasons,
            "acceptance_rate": (
                self._records_accepted / self._records_total * 100 
                if self._records_total > 0 else 0
            )
        }


def get_quality_summary(days: int = 7) -> List[Dict]:
    """
    Récupérer un résumé de la qualité des données sur les derniers jours
    
    Args:
        days: Nombre de jours à analyser
        
    Returns:
        Liste de résumés par source
    """
    query = """
    SELECT 
        source_type,
        pipeline_step,
        COUNT(*) as run_count,
        SUM(records_total) as total_records,
        SUM(records_accepted) as total_accepted,
        SUM(records_rejected) as total_rejected,
        ROUND(AVG(records_accepted::DECIMAL / NULLIF(records_total, 0) * 100), 2) as avg_acceptance_rate,
        COUNT(*) FILTER (WHERE status = 'error') as error_count,
        COUNT(*) FILTER (WHERE status = 'warning') as warning_count,
        AVG(execution_time_ms) as avg_execution_ms
    FROM quality_logs
    WHERE run_date >= NOW() - INTERVAL '%s days'
    GROUP BY source_type, pipeline_step
    ORDER BY source_type, pipeline_step
    """
    
    try:
        results = db.execute_query(query, (days,))
        return results or []
    except Exception as e:
        logger.error(f"Erreur récupération quality summary : {e}")
        return []


def get_rejection_breakdown(source_type: str, days: int = 7) -> Dict[str, int]:
    """
    Récupérer le détail des rejets par raison pour une source
    
    Args:
        source_type: Type de source à analyser
        days: Nombre de jours
        
    Returns:
        Dict avec les raisons et leurs compteurs
    """
    query = """
    SELECT rejection_reasons
    FROM quality_logs
    WHERE source_type = %s
        AND run_date >= NOW() - INTERVAL '%s days'
    """
    
    try:
        results = db.execute_query(query, (source_type, days))
        
        # Agréger les raisons
        total_reasons: Dict[str, int] = {}
        for row in results or []:
            reasons = row.get("rejection_reasons", {})
            if isinstance(reasons, str):
                reasons = json.loads(reasons)
            for reason, count in reasons.items():
                total_reasons[reason] = total_reasons.get(reason, 0) + count
        
        return total_reasons
        
    except Exception as e:
        logger.error(f"Erreur récupération rejection breakdown : {e}")
        return {}


def get_field_completeness_trend(source_type: str, field: str, days: int = 30) -> List[Dict]:
    """
    Récupérer la tendance de complétude d'un champ sur une période
    
    Args:
        source_type: Type de source
        field: Nom du champ
        days: Nombre de jours
        
    Returns:
        Liste de {date, completeness_pct}
    """
    query = """
    SELECT 
        DATE(run_date) as log_date,
        AVG((field_completeness->>%s)::DECIMAL) as avg_completeness
    FROM quality_logs
    WHERE source_type = %s
        AND run_date >= NOW() - INTERVAL '%s days'
        AND field_completeness ? %s
    GROUP BY DATE(run_date)
    ORDER BY log_date
    """
    
    try:
        results = db.execute_query(query, (field, source_type, days, field))
        return [
            {"date": r["log_date"], "completeness": float(r["avg_completeness"] or 0)}
            for r in (results or [])
        ]
    except Exception as e:
        logger.error(f"Erreur récupération field completeness trend : {e}")
        return []


def check_quality_alerts(threshold_acceptance_rate: float = 80.0) -> List[Dict]:
    """
    Vérifier les alertes de qualité (dégradation récente)
    
    Args:
        threshold_acceptance_rate: Seuil minimum d'acceptation (%)
        
    Returns:
        Liste d'alertes détectées
    """
    alerts = []
    
    # Vérifier les runs récents avec faible taux d'acceptation
    query = """
    SELECT 
        source_type,
        pipeline_step,
        records_total,
        records_accepted,
        records_rejected,
        ROUND(records_accepted::DECIMAL / NULLIF(records_total, 0) * 100, 2) as acceptance_rate,
        run_date
    FROM quality_logs
    WHERE run_date >= NOW() - INTERVAL '24 hours'
        AND records_total > 0
        AND (records_accepted::DECIMAL / NULLIF(records_total, 0) * 100) < %s
    ORDER BY run_date DESC
    """
    
    try:
        results = db.execute_query(query, (threshold_acceptance_rate,))
        
        for row in results or []:
            alerts.append({
                "type": "low_acceptance_rate",
                "severity": "warning" if row["acceptance_rate"] >= 50 else "critical",
                "source_type": row["source_type"],
                "pipeline_step": row["pipeline_step"],
                "acceptance_rate": float(row["acceptance_rate"]),
                "records_rejected": row["records_rejected"],
                "timestamp": row["run_date"]
            })
        
    except Exception as e:
        logger.error(f"Erreur vérification quality alerts : {e}")
    
    # Vérifier les erreurs récentes
    error_query = """
    SELECT 
        source_type,
        pipeline_step,
        error_message,
        run_date
    FROM quality_logs
    WHERE run_date >= NOW() - INTERVAL '24 hours'
        AND status = 'error'
    ORDER BY run_date DESC
    """
    
    try:
        error_results = db.execute_query(error_query, ())
        
        for row in error_results or []:
            alerts.append({
                "type": "pipeline_error",
                "severity": "critical",
                "source_type": row["source_type"],
                "pipeline_step": row["pipeline_step"],
                "error_message": row["error_message"],
                "timestamp": row["run_date"]
            })
        
    except Exception as e:
        logger.error(f"Erreur vérification error alerts : {e}")
    
    return alerts


def calculate_data_completeness(records: List[Dict], fields: List[str]) -> Dict[str, float]:
    """
    Calculer la complétude des champs pour une liste de records
    
    Args:
        records: Liste de dictionnaires
        fields: Liste des champs à vérifier
        
    Returns:
        Dict avec {field: pourcentage_non_null}
    """
    if not records:
        return {f: 0.0 for f in fields}
    
    total = len(records)
    completeness = {}
    
    for field in fields:
        non_null = sum(1 for r in records if r.get(field) is not None)
        completeness[field] = round(non_null / total * 100, 1)
    
    return completeness


if __name__ == "__main__":
    # Test du logger
    from core.utils import setup_logging
    setup_logging()
    
    # Simuler un run
    qlogger = QualityLogger("test_source", "test_step")
    qlogger.start()
    
    qlogger.add_total(100)
    qlogger.accept(85)
    qlogger.reject("outlier", 10)
    qlogger.reject("missing_field", 5)
    
    qlogger.set_field_completeness({
        "price": 100.0,
        "area": 95.5,
        "community": 98.0
    })
    
    result = qlogger.finish()
    print(f"Log créé : {result.status}")
    print(f"Stats : {qlogger.get_stats()}")

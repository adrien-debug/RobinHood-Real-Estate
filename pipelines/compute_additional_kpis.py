"""
Pipeline de calcul des KPIs additionnels

Nouveaux KPIs implémentés :
1. DOM (Days on Market) - Médiane jours listing actif par bâtiment
2. Listing Turnover Rate - Annonces vendues/total par communauté
3. Price Cut Frequency - % annonces avec baisse prix par projet
4. Absorption Rate - Transactions/mois ÷ stock annonces par communauté
5. Rental Yield Actual - Loyer annuel / prix vente par bâtiment
6. Developer Delivery Score - % projets livrés à temps par promoteur
7. Metro Premium - Δ prix < 500m métro vs > 1km par bâtiment
8. Beach Premium - Δ prix waterfront vs non par bâtiment
9. Offplan Discount Evolution - Δ prix off-plan vs ready YoY par projet
10. Investor Concentration - % multi-property owners par communauté
11. Floor Premium - Prix/sqft par étage (si données disponibles)
12. View Premium - Δ prix vue mer/ville/jardin (si données disponibles)
"""
from typing import Dict, List, Optional
from datetime import date, timedelta, datetime
from decimal import Decimal
from loguru import logger
from core.db import db
from core.models import KPI
from pipelines.quality_logger import QualityLogger


class AdditionalKPIsComputer:
    """Calculateur de KPIs additionnels"""
    
    def __init__(self):
        self.quality_logger = QualityLogger(source_type="additional_kpis", pipeline_step="compute")
    
    def compute_all(self, window_days: int = 30) -> int:
        """
        Calculer tous les KPIs additionnels
        
        Args:
            window_days: Fenêtre temporelle (7, 30 ou 90 jours)
            
        Returns:
            Nombre de KPIs calculés
        """
        logger.info(f"🧮 Calcul KPIs additionnels (fenêtre {window_days}j)")
        
        kpis_count = 0
        
        # 1. Days on Market (DOM)
        kpis_count += self._compute_days_on_market(window_days)
        
        # 2. Listing Turnover Rate
        kpis_count += self._compute_listing_turnover(window_days)
        
        # 3. Price Cut Frequency
        kpis_count += self._compute_price_cut_frequency(window_days)
        
        # 4. Absorption Rate
        kpis_count += self._compute_absorption_rate(window_days)
        
        # 5. Rental Yield Actual
        kpis_count += self._compute_rental_yield(window_days)
        
        # 6. Developer Delivery Score
        kpis_count += self._compute_developer_score(window_days)
        
        # 7. Metro Premium
        kpis_count += self._compute_metro_premium(window_days)
        
        # 8. Beach Premium
        kpis_count += self._compute_beach_premium(window_days)
        
        # 9. Offplan Discount Evolution
        kpis_count += self._compute_offplan_evolution(window_days)
        
        # 10. Investor Concentration
        kpis_count += self._compute_investor_concentration(window_days)
        
        # 11. Floor Premium
        kpis_count += self._compute_floor_premium(window_days)
        
        # 12. View Premium
        kpis_count += self._compute_view_premium(window_days)
        
        logger.success(f"✅ {kpis_count} KPIs additionnels calculés")
        return kpis_count
    
    def _compute_days_on_market(self, window_days: int) -> int:
        """
        DOM (Days on Market) : Médiane jours listing actif par bâtiment
        
        Formule : MEDIAN(date_today - listing_date) pour listings actifs
        """
        logger.info("Calcul DOM (Days on Market)")
        
        query = """
        WITH listing_ages AS (
            SELECT 
                community,
                building,
                EXTRACT(EPOCH FROM (CURRENT_DATE - listing_date)) / 86400 AS days_on_market
            FROM dld_listings
            WHERE 
                status = 'active'
                AND listing_date >= CURRENT_DATE - INTERVAL '%s days'
        )
        SELECT 
            community,
            building,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY days_on_market) AS median_dom,
            COUNT(*) AS listing_count
        FROM listing_ages
        GROUP BY community, building
        HAVING COUNT(*) >= 3
        """
        
        try:
            results = db.execute_query(query, (window_days,))
            
            kpis_inserted = 0
            for row in results:
                kpi = KPI(
                    kpi_name="DOM",
                    kpi_value=float(row['median_dom']),
                    community=row['community'],
                    building=row['building'],
                    window_days=window_days,
                    calculation_date=date.today(),
                    metadata={
                        "listing_count": row['listing_count'],
                        "description": "Days on Market - Médiane jours listing actif"
                    }
                )
                
                db.execute_insert(
                    "INSERT INTO dld_kpis (kpi_name, kpi_value, community, building, window_days, calculation_date, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (kpi.kpi_name, kpi.kpi_value, kpi.community, kpi.building, kpi.window_days, kpi.calculation_date, kpi.metadata)
                )
                kpis_inserted += 1
            
            logger.info(f"✓ {kpis_inserted} KPIs DOM insérés")
            return kpis_inserted
            
        except Exception as e:
            logger.error(f"Erreur calcul DOM : {e}")
            return 0
    
    def _compute_listing_turnover(self, window_days: int) -> int:
        """
        Listing Turnover Rate : Annonces vendues/total par communauté
        
        Formule : (listings_sold / total_listings) * 100
        """
        logger.info("Calcul Listing Turnover Rate")
        
        query = """
        WITH listing_stats AS (
            SELECT 
                community,
                COUNT(*) AS total_listings,
                COUNT(*) FILTER (WHERE status = 'sold') AS sold_listings
            FROM dld_listings
            WHERE listing_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY community
        )
        SELECT 
            community,
            CASE 
                WHEN total_listings > 0 THEN (sold_listings::FLOAT / total_listings) * 100
                ELSE 0
            END AS turnover_rate,
            total_listings,
            sold_listings
        FROM listing_stats
        WHERE total_listings >= 5
        """
        
        try:
            results = db.execute_query(query, (window_days,))
            
            kpis_inserted = 0
            for row in results:
                kpi = KPI(
                    kpi_name="LISTING_TURNOVER",
                    kpi_value=float(row['turnover_rate']),
                    community=row['community'],
                    window_days=window_days,
                    calculation_date=date.today(),
                    metadata={
                        "total_listings": row['total_listings'],
                        "sold_listings": row['sold_listings'],
                        "description": "% annonces vendues sur total"
                    }
                )
                
                db.execute_insert(
                    "INSERT INTO dld_kpis (kpi_name, kpi_value, community, window_days, calculation_date, metadata) VALUES (%s, %s, %s, %s, %s, %s)",
                    (kpi.kpi_name, kpi.kpi_value, kpi.community, kpi.window_days, kpi.calculation_date, kpi.metadata)
                )
                kpis_inserted += 1
            
            logger.info(f"✓ {kpis_inserted} KPIs Turnover insérés")
            return kpis_inserted
            
        except Exception as e:
            logger.error(f"Erreur calcul Turnover : {e}")
            return 0
    
    def _compute_price_cut_frequency(self, window_days: int) -> int:
        """
        Price Cut Frequency : % annonces avec baisse prix par projet
        
        Formule : (listings_with_price_cut / total_listings) * 100
        """
        logger.info("Calcul Price Cut Frequency")
        
        # Note : Nécessite un historique des prix dans la table listings
        # Pour l'instant, on retourne 0 (à implémenter quand historique disponible)
        logger.warning("Price Cut Frequency nécessite historique des prix - non implémenté")
        return 0
    
    def _compute_absorption_rate(self, window_days: int) -> int:
        """
        Absorption Rate : Transactions/mois ÷ stock annonces par communauté
        
        Formule : (monthly_transactions / active_listings) * 100
        """
        logger.info("Calcul Absorption Rate")
        
        query = """
        WITH monthly_tx AS (
            SELECT 
                community,
                COUNT(*) AS tx_count
            FROM dld_transactions
            WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY community
        ),
        active_stock AS (
            SELECT 
                community,
                COUNT(*) AS listing_count
            FROM dld_listings
            WHERE status = 'active'
            GROUP BY community
        )
        SELECT 
            t.community,
            CASE 
                WHEN s.listing_count > 0 THEN (t.tx_count::FLOAT / s.listing_count) * 100
                ELSE 0
            END AS absorption_rate,
            t.tx_count,
            s.listing_count
        FROM monthly_tx t
        JOIN active_stock s ON t.community = s.community
        WHERE s.listing_count >= 5
        """
        
        try:
            results = db.execute_query(query)
            
            kpis_inserted = 0
            for row in results:
                kpi = KPI(
                    kpi_name="ABSORPTION_RATE",
                    kpi_value=float(row['absorption_rate']),
                    community=row['community'],
                    window_days=window_days,
                    calculation_date=date.today(),
                    metadata={
                        "tx_count": row['tx_count'],
                        "listing_count": row['listing_count'],
                        "description": "Transactions/mois ÷ stock annonces"
                    }
                )
                
                db.execute_insert(
                    "INSERT INTO dld_kpis (kpi_name, kpi_value, community, window_days, calculation_date, metadata) VALUES (%s, %s, %s, %s, %s, %s)",
                    (kpi.kpi_name, kpi.kpi_value, kpi.community, kpi.window_days, kpi.calculation_date, kpi.metadata)
                )
                kpis_inserted += 1
            
            logger.info(f"✓ {kpis_inserted} KPIs Absorption insérés")
            return kpis_inserted
            
        except Exception as e:
            logger.error(f"Erreur calcul Absorption : {e}")
            return 0
    
    def _compute_rental_yield(self, window_days: int) -> int:
        """
        Rental Yield Actual : Loyer annuel / prix vente par bâtiment
        
        Formule : (annual_rent / sale_price) * 100
        """
        logger.info("Calcul Rental Yield Actual")
        
        query = """
        WITH rental_data AS (
            SELECT 
                community,
                building,
                rooms_bucket,
                AVG(annual_rent_aed) AS avg_annual_rent
            FROM dld_rental_index
            WHERE rental_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY community, building, rooms_bucket
        ),
        sale_data AS (
            SELECT 
                community,
                building,
                rooms_bucket,
                AVG(transaction_price_aed) AS avg_sale_price
            FROM dld_transactions
            WHERE transaction_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY community, building, rooms_bucket
        )
        SELECT 
            r.community,
            r.building,
            r.rooms_bucket,
            CASE 
                WHEN s.avg_sale_price > 0 THEN (r.avg_annual_rent / s.avg_sale_price) * 100
                ELSE 0
            END AS rental_yield,
            r.avg_annual_rent,
            s.avg_sale_price
        FROM rental_data r
        JOIN sale_data s ON 
            r.community = s.community 
            AND r.building = s.building 
            AND r.rooms_bucket = s.rooms_bucket
        WHERE s.avg_sale_price > 0
        """
        
        try:
            results = db.execute_query(query, (window_days, window_days))
            
            kpis_inserted = 0
            for row in results:
                kpi = KPI(
                    kpi_name="RENTAL_YIELD",
                    kpi_value=float(row['rental_yield']),
                    community=row['community'],
                    building=row['building'],
                    rooms_bucket=row['rooms_bucket'],
                    window_days=window_days,
                    calculation_date=date.today(),
                    metadata={
                        "avg_annual_rent": float(row['avg_annual_rent']),
                        "avg_sale_price": float(row['avg_sale_price']),
                        "description": "Loyer annuel / prix vente"
                    }
                )
                
                db.execute_insert(
                    "INSERT INTO dld_kpis (kpi_name, kpi_value, community, building, rooms_bucket, window_days, calculation_date, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (kpi.kpi_name, kpi.kpi_value, kpi.community, kpi.building, kpi.rooms_bucket, kpi.window_days, kpi.calculation_date, kpi.metadata)
                )
                kpis_inserted += 1
            
            logger.info(f"✓ {kpis_inserted} KPIs Rental Yield insérés")
            return kpis_inserted
            
        except Exception as e:
            logger.error(f"Erreur calcul Rental Yield : {e}")
            return 0
    
    def _compute_developer_score(self, window_days: int) -> int:
        """
        Developer Delivery Score : % projets livrés à temps par promoteur
        
        Note : Nécessite données DLD Developers API
        """
        logger.info("Calcul Developer Delivery Score")
        logger.warning("Developer Score nécessite API DLD Developers - non implémenté")
        return 0
    
    def _compute_metro_premium(self, window_days: int) -> int:
        """
        Metro Premium : Δ prix < 500m métro vs > 1km par bâtiment
        
        Note : Nécessite données Makani avec distances métro
        """
        logger.info("Calcul Metro Premium")
        logger.warning("Metro Premium nécessite API Makani - non implémenté")
        return 0
    
    def _compute_beach_premium(self, window_days: int) -> int:
        """
        Beach Premium : Δ prix waterfront vs non par bâtiment
        
        Note : Nécessite données Makani avec distances plage
        """
        logger.info("Calcul Beach Premium")
        logger.warning("Beach Premium nécessite API Makani - non implémenté")
        return 0
    
    def _compute_offplan_evolution(self, window_days: int) -> int:
        """
        Offplan Discount Evolution : Δ prix off-plan vs ready YoY par projet
        
        Formule : (median_offplan_psf / median_ready_psf) - 1
        """
        logger.info("Calcul Offplan Discount Evolution")
        
        query = """
        WITH offplan_prices AS (
            SELECT 
                community,
                project,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) AS median_offplan_psf
            FROM dld_transactions
            WHERE 
                is_offplan = TRUE
                AND transaction_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY community, project
        ),
        ready_prices AS (
            SELECT 
                community,
                project,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) AS median_ready_psf
            FROM dld_transactions
            WHERE 
                is_offplan = FALSE
                AND transaction_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY community, project
        )
        SELECT 
            o.community,
            o.project,
            CASE 
                WHEN r.median_ready_psf > 0 THEN ((o.median_offplan_psf / r.median_ready_psf) - 1) * 100
                ELSE 0
            END AS offplan_discount_pct,
            o.median_offplan_psf,
            r.median_ready_psf
        FROM offplan_prices o
        JOIN ready_prices r ON 
            o.community = r.community 
            AND o.project = r.project
        WHERE r.median_ready_psf > 0
        """
        
        try:
            results = db.execute_query(query, (window_days, window_days))
            
            kpis_inserted = 0
            for row in results:
                kpi = KPI(
                    kpi_name="OFFPLAN_EVOLUTION",
                    kpi_value=float(row['offplan_discount_pct']),
                    community=row['community'],
                    project=row['project'],
                    window_days=window_days,
                    calculation_date=date.today(),
                    metadata={
                        "median_offplan_psf": float(row['median_offplan_psf']),
                        "median_ready_psf": float(row['median_ready_psf']),
                        "description": "Δ prix off-plan vs ready"
                    }
                )
                
                db.execute_insert(
                    "INSERT INTO dld_kpis (kpi_name, kpi_value, community, project, window_days, calculation_date, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (kpi.kpi_name, kpi.kpi_value, kpi.community, kpi.project, kpi.window_days, kpi.calculation_date, kpi.metadata)
                )
                kpis_inserted += 1
            
            logger.info(f"✓ {kpis_inserted} KPIs Offplan Evolution insérés")
            return kpis_inserted
            
        except Exception as e:
            logger.error(f"Erreur calcul Offplan Evolution : {e}")
            return 0
    
    def _compute_investor_concentration(self, window_days: int) -> int:
        """
        Investor Concentration : % multi-property owners par communauté
        
        Note : Nécessite données propriétaires dans DLD Transactions
        """
        logger.info("Calcul Investor Concentration")
        logger.warning("Investor Concentration nécessite données propriétaires - non implémenté")
        return 0
    
    def _compute_floor_premium(self, window_days: int) -> int:
        """
        Floor Premium : Prix/sqft par étage
        
        Note : Nécessite données d'étage dans transactions ou floorplans
        """
        logger.info("Calcul Floor Premium")
        logger.warning("Floor Premium nécessite données d'étage - non implémenté")
        return 0
    
    def _compute_view_premium(self, window_days: int) -> int:
        """
        View Premium : Δ prix vue mer/ville/jardin
        
        Note : Nécessite données de vue dans transactions ou floorplans
        """
        logger.info("Calcul View Premium")
        logger.warning("View Premium nécessite données de vue - non implémenté")
        return 0


def run_additional_kpis_pipeline():
    """Point d'entrée principal du pipeline"""
    logger.info("🚀 Démarrage pipeline KPIs additionnels")
    
    computer = AdditionalKPIsComputer()
    
    # Calculer pour les 3 fenêtres
    total_kpis = 0
    for window in [7, 30, 90]:
        count = computer.compute_all(window_days=window)
        total_kpis += count
    
    logger.success(f"✅ Pipeline KPIs additionnels terminé : {total_kpis} KPIs calculés")
    return total_kpis


if __name__ == "__main__":
    run_additional_kpis_pipeline()

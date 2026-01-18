"""
Script de test pour toutes les APIs du stack data optimal

Ce script teste tous les connecteurs en mode MOCK (sans clés API réelles).
Utile pour vérifier que l'intégration fonctionne avant d'obtenir les accès.

Usage:
    python test_all_apis.py
"""
from datetime import date, timedelta
import sys


class SimpleLogger:
    """Logger simple pour remplacer loguru"""
    
    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")
    
    @staticmethod
    def success(msg):
        print(f"[✓] {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"[⚠] {msg}")
    
    @staticmethod
    def error(msg):
        print(f"[✗] {msg}")
    
    def opt(self, **kwargs):
        return self


logger = SimpleLogger()


def test_transactions():
    """Test DLD Transactions API"""
    logger.info("=" * 60)
    logger.info("TEST 1/5 : DLD Transactions (Dubai Pulse)")
    logger.info("=" * 60)
    
    try:
        from connectors.transactions import DLDTransactionsConnector
        
        connector = DLDTransactionsConnector()
        
        # Test récupération transactions
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        
        logger.info(f"Récupération transactions : {start_date} → {end_date}")
        transactions = connector.fetch_transactions(start_date, end_date)
        
        logger.success(f"✓ {len(transactions)} transactions récupérées")
        
        if transactions:
            t = transactions[0]
            logger.info(f"  Exemple : {t.community} - {t.property_type} - {t.price_aed} AED")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur : {e}")
        return False


def test_dld_rental_index():
    """Test DLD Rental Index API"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST 2/5 : DLD Rental Index (Dubai Pulse)")
    logger.info("=" * 60)
    
    try:
        from connectors.dld_rental_index import DLDRentalIndexConnector
        
        connector = DLDRentalIndexConnector()
        
        # Test récupération index locatif
        period_date = date.today().replace(day=1)
        
        logger.info(f"Récupération index locatif : {period_date}")
        rental_data = connector.fetch_rental_index(period_date)
        
        logger.success(f"✓ {len(rental_data)} entrées d'index locatif récupérées")
        
        if rental_data:
            r = rental_data[0]
            logger.info(f"  Exemple : {r.community} - {r.rooms_bucket} - {r.median_rent_aed} AED/an")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur : {e}")
        return False


def test_bayut_api():
    """Test Bayut API"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST 3/5 : Bayut API (Lead Indicators)")
    logger.info("=" * 60)
    
    try:
        from connectors.bayut_api import BayutAPIConnector
        
        connector = BayutAPIConnector()
        
        # Test récupération listings
        logger.info("Récupération annonces Bayut (7 derniers jours)")
        listings = connector.fetch_listings(
            community="Dubai Marina",
            days_back=7
        )
        
        logger.success(f"✓ {len(listings)} annonces récupérées")
        
        if listings:
            l = listings[0]
            logger.info(f"  Exemple : {l.community} - {l.property_type} - {l.asking_price_aed} AED")
        
        # Test métriques
        logger.info("Calcul des métriques...")
        metrics = connector.calculate_listing_metrics(listings)
        
        logger.success("✓ Métriques calculées :")
        logger.info(f"  - Total annonces : {metrics.get('total_listings', 0)}")
        logger.info(f"  - Jours sur marché (moy) : {metrics.get('avg_days_on_market', 0)}")
        logger.info(f"  - % baisses de prix : {metrics.get('pct_price_reductions', 0)}%")
        logger.info(f"  - Nouvelles annonces (7j) : {metrics.get('new_listings_7d', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur : {e}")
        return False


def test_makani_geocoding():
    """Test Makani Geocoding API"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST 4/5 : Makani Geocoding (Matching & Localisation)")
    logger.info("=" * 60)
    
    try:
        from connectors.makani_geocoding import MakaniGeocodingConnector
        
        connector = MakaniGeocodingConnector()
        
        # Test recherche adresse
        logger.info("Recherche adresse : Dubai Marina / Marina Heights / Tower A")
        address = connector.search_address(
            community="Dubai Marina",
            project="Marina Heights",
            building="Tower A"
        )
        
        if address:
            logger.success(f"✓ Adresse trouvée : Makani #{address.makani_number}")
            logger.info(f"  - Coordonnées : {address.latitude}, {address.longitude}")
            logger.info(f"  - Métro : {address.metro_station} ({address.metro_distance_m}m)")
            logger.info(f"  - Plage : {address.beach_distance_m}m")
            logger.info(f"  - Mall : {address.mall_distance_m}m")
            
            # Test scoring localisation
            score = connector.calculate_location_score(address)
            logger.success(f"✓ Score localisation : {score}/100")
        else:
            logger.warning("⚠ Aucune adresse trouvée (mode MOCK)")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur : {e}")
        return False


def test_dda_planning():
    """Test DDA Planning & Zoning API"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("TEST 5/5 : DDA Planning & Zoning (Signaux en avance)")
    logger.info("=" * 60)
    
    try:
        from connectors.dda_planning import DDAConnector
        
        connector = DDAConnector()
        
        # Test permis de construire
        logger.info("Récupération permis de construire (90 derniers jours)")
        permits = connector.fetch_building_permits()
        
        logger.success(f"✓ {len(permits)} permis récupérés")
        
        if permits:
            p = permits[0]
            logger.info(f"  Exemple : {p.community} - {p.project_name}")
            logger.info(f"    {p.total_units} unités (dont {p.residential_units} résidentielles)")
        
        # Test changements de zonage
        logger.info("Récupération changements de zonage (180 derniers jours)")
        zoning = connector.fetch_zoning_changes()
        
        logger.success(f"✓ {len(zoning)} changements de zonage récupérés")
        
        if zoning:
            z = zoning[0]
            logger.info(f"  Exemple : {z.community} - {z.old_zoning} → {z.new_zoning}")
        
        # Test calcul pression supply
        logger.info("Calcul pression supply pour Dubai Marina...")
        supply = connector.calculate_supply_pressure(permits, "Dubai Marina")
        
        logger.success("✓ Pression supply calculée :")
        logger.info(f"  - Nouvelles unités (12m) : {supply['completion_next_12m']}")
        logger.info(f"  - Nouvelles unités (24m) : {supply['completion_next_24m']}")
        logger.info(f"  - Score pression : {supply['supply_pressure_score']}/100")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur : {e}")
        return False


def main():
    """Exécuter tous les tests"""
    logger.info("")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + " " * 10 + "TEST DU STACK DATA OPTIMAL" + " " * 21 + "║")
    logger.info("╚" + "═" * 58 + "╝")
    logger.info("")
    logger.warning("⚠ Mode MOCK activé (pas de clés API configurées)")
    logger.info("Les connecteurs génèrent des données fictives pour tester l'intégration")
    logger.info("")
    
    results = []
    
    # Test 1 : DLD Transactions
    results.append(("DLD Transactions", test_transactions()))
    
    # Test 2 : DLD Rental Index
    results.append(("DLD Rental Index", test_dld_rental_index()))
    
    # Test 3 : Bayut API
    results.append(("Bayut API", test_bayut_api()))
    
    # Test 4 : Makani Geocoding
    results.append(("Makani Geocoding", test_makani_geocoding()))
    
    # Test 5 : DDA Planning
    results.append(("DDA Planning", test_dda_planning()))
    
    # Résumé
    logger.info("")
    logger.info("=" * 60)
    logger.info("RÉSUMÉ DES TESTS")
    logger.info("=" * 60)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        color = "green" if success else "red"
        logger.opt(colors=True).info(f"<{color}>{status}</{color}> - {name}")
    
    logger.info("")
    logger.info(f"Total : {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        logger.success("")
        logger.success("╔" + "═" * 58 + "╗")
        logger.success("║" + " " * 8 + "✓ TOUS LES CONNECTEURS FONCTIONNENT" + " " * 14 + "║")
        logger.success("╚" + "═" * 58 + "╝")
        logger.success("")
        logger.info("Prochaines étapes :")
        logger.info("1. Obtenir les clés API réelles (voir API_LINKS.md)")
        logger.info("2. Configurer les clés dans .env")
        logger.info("3. Relancer ce script pour tester en mode réel")
    else:
        logger.error("")
        logger.error("⚠ Certains tests ont échoué")
        logger.info("Vérifier les erreurs ci-dessus")
    
    logger.info("")


if __name__ == "__main__":
    main()

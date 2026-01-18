"""
Script de test pour les nouvelles fonctionnalités

Teste :
1. Nouveaux connecteurs (dld_developers, dld_valuation, dld_lkp_areas)
2. Nouveaux KPIs (DOM, Absorption Rate, Rental Yield, etc.)
3. Floorplans Bayut API
"""
from loguru import logger
from connectors.dld_developers import DLDDevelopersConnector
from connectors.dld_valuation import DLDValuationConnector
from connectors.dld_lkp_areas import DLDLkpAreasConnector
from connectors.bayut_api import BayutAPIConnector
from pipelines.compute_additional_kpis import AdditionalKPIsComputer


def test_dld_developers():
    """Test du connecteur DLD Developers"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1/5 : DLD Developers")
    logger.info("="*60)
    
    try:
        connector = DLDDevelopersConnector()
        
        # Test récupération promoteurs
        logger.info("Récupération liste promoteurs...")
        developers = connector.fetch_developers()
        
        logger.success(f"✓ {len(developers)} promoteurs récupérés")
        
        if developers:
            dev = developers[0]
            logger.info(f"  Exemple : {dev.name_en}")
            logger.info(f"    - Total projets : {dev.total_projects}")
            logger.info(f"    - Projets complétés : {dev.completed_projects}")
            logger.info(f"    - Score livraison : {dev.delivery_score:.1f}/100")
            
            # Test stats détaillées
            logger.info(f"\nRécupération stats détaillées pour {dev.name_en}...")
            stats = connector.get_developer_stats(dev.developer_id)
            logger.success(f"✓ Stats récupérées : {len(stats)} métriques")
            
            # Test score de livraison
            score = connector.calculate_delivery_score(dev.developer_id)
            logger.success(f"✓ Score de livraison calculé : {score:.1f}/100")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur test DLD Developers : {e}")
        return False


def test_dld_valuation():
    """Test du connecteur DLD Valuation"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2/5 : DLD Valuation")
    logger.info("="*60)
    
    try:
        connector = DLDValuationConnector()
        
        # Test récupération évaluations
        logger.info("Récupération évaluations officielles...")
        valuations = connector.fetch_valuations(community="Dubai Marina")
        
        logger.success(f"✓ {len(valuations)} évaluations récupérées")
        
        if valuations:
            val = valuations[0]
            logger.info(f"  Exemple : {val.community} - {val.property_type}")
            logger.info(f"    - Valeur officielle : {val.official_value_aed:,.0f} AED")
            logger.info(f"    - Prix/sqft : {val.value_per_sqft:,.0f} AED/sqft")
            logger.info(f"    - Méthode : {val.valuation_method}")
            logger.info(f"    - Confiance : {val.confidence_level}")
            
            # Test calcul gap valuation
            from decimal import Decimal
            transaction_price = val.official_value_aed * Decimal("1.15")  # +15%
            gap = connector.calculate_valuation_gap(transaction_price, val.official_value_aed)
            logger.success(f"✓ Gap calculé : {gap['gap_pct']:.1f}% ({'survalué' if gap['overvalued'] else 'sous-valué'})")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur test DLD Valuation : {e}")
        return False


def test_dld_lkp_areas():
    """Test du connecteur DLD LKP Areas"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3/5 : DLD LKP Areas")
    logger.info("="*60)
    
    try:
        connector = DLDLkpAreasConnector()
        
        # Test récupération hiérarchie
        logger.info("Récupération hiérarchie zones...")
        areas = connector.fetch_areas()
        
        logger.success(f"✓ {len(areas)} zones récupérées")
        
        # Compter par niveau
        levels = {}
        for area in areas:
            levels[area.area_level] = levels.get(area.area_level, 0) + 1
        
        logger.info("  Répartition par niveau :")
        for level, count in levels.items():
            logger.info(f"    - {level}: {count}")
        
        # Test recherche par nom
        logger.info("\nRecherche zone 'Dubai Marina'...")
        marina = connector.get_area_by_name("Dubai Marina")
        if marina:
            logger.success(f"✓ Zone trouvée : {marina.area_name_en} (ID: {marina.area_id})")
            
            # Test hiérarchie
            logger.info(f"\nRécupération hiérarchie pour {marina.area_name_en}...")
            hierarchy = connector.get_area_hierarchy(marina.area_id)
            logger.success(f"✓ Hiérarchie : {' → '.join([a.area_name_en for a in hierarchy])}")
            
            # Test sous-zones
            logger.info(f"\nRécupération sous-zones de {marina.area_name_en}...")
            sub_areas = connector.get_sub_areas(marina.area_id)
            logger.success(f"✓ {len(sub_areas)} sous-zones trouvées")
        
        # Test normalisation
        logger.info("\nTest normalisation noms...")
        test_names = ["dubai marina", "DUBAI MARINA", "Dubai-Marina", "JBR"]
        for name in test_names:
            normalized = connector.normalize_area_name(name)
            logger.info(f"  '{name}' → '{normalized}'")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur test DLD LKP Areas : {e}")
        return False


def test_bayut_floorplans():
    """Test de l'endpoint floorplans Bayut API"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4/5 : Bayut Floorplans")
    logger.info("="*60)
    
    try:
        connector = BayutAPIConnector()
        
        # Test récupération floorplans
        logger.info("Récupération floorplans pour Dubai Marina...")
        
        # Note : L'endpoint floorplans nécessite un project_id, pas location_id
        # On utilise un ID de projet connu (exemple: Emaar Beachfront)
        project_id = 87107  # Dubai Creek Harbour (exemple)
        
        logger.info(f"Project ID : {project_id}")
        
        # Appel direct à l'API
        import httpx
        url = f"{connector.base_url}/floorplans"
        headers = {
            "X-RapidAPI-Key": connector.api_key,
            "X-RapidAPI-Host": connector.RAPIDAPI_HOST
        }
        params = {"externalID": project_id}  # Utiliser externalID au lieu de location
        
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        
        floorplans = data.get("floorplans", [])
        logger.success(f"✓ {len(floorplans)} floorplans récupérés")
        
        if floorplans:
            fp = floorplans[0]
            logger.info(f"  Exemple : {fp.get('beds')} chambres, {fp.get('baths')} salles de bain")
            logger.info(f"    - Catégorie : {fp.get('category')}")
            logger.info(f"    - Status : {fp.get('state')}")
            logger.info(f"    - Modèles 3D : {len(fp.get('models', []))}")
            logger.info(f"    - Images 2D : {len(fp.get('2d_imgs', []))}")
            logger.info(f"    - Images 3D : {len(fp.get('3d_imgs', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur test Bayut Floorplans : {e}")
        logger.error(f"  Détails : {str(e)}")
        return False


def test_additional_kpis():
    """Test des KPIs additionnels"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5/5 : KPIs Additionnels")
    logger.info("="*60)
    
    try:
        computer = AdditionalKPIsComputer()
        
        # Test calcul KPIs
        logger.info("Calcul KPIs additionnels (fenêtre 30j)...")
        kpis_count = computer.compute_all(window_days=30)
        
        logger.success(f"✓ {kpis_count} KPIs calculés")
        
        # Lister les KPIs implémentés
        implemented_kpis = [
            "DOM (Days on Market)",
            "LISTING_TURNOVER (Turnover Rate)",
            "ABSORPTION_RATE (Absorption Rate)",
            "RENTAL_YIELD (Rental Yield)",
            "OFFPLAN_EVOLUTION (Offplan Evolution)"
        ]
        
        logger.info("\nKPIs implémentés :")
        for kpi in implemented_kpis:
            logger.info(f"  ✓ {kpi}")
        
        # KPIs en attente de données
        pending_kpis = [
            "PRICE_CUT (nécessite historique prix)",
            "DEVELOPER_SCORE (nécessite API DLD Developers)",
            "METRO_PREMIUM (nécessite API Makani)",
            "BEACH_PREMIUM (nécessite API Makani)",
            "INVESTOR_CONCENTRATION (nécessite données propriétaires)",
            "FLOOR_PREMIUM (nécessite données étage)",
            "VIEW_PREMIUM (nécessite données vue)"
        ]
        
        logger.info("\nKPIs en attente de données :")
        for kpi in pending_kpis:
            logger.warning(f"  ⚠ {kpi}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur test KPIs additionnels : {e}")
        return False


def main():
    """Point d'entrée principal"""
    logger.info("\n" + "="*60)
    logger.info("║        TEST DES NOUVELLES FONCTIONNALITÉS              ║")
    logger.info("="*60)
    
    results = {
        "DLD Developers": test_dld_developers(),
        "DLD Valuation": test_dld_valuation(),
        "DLD LKP Areas": test_dld_lkp_areas(),
        "Bayut Floorplans": test_bayut_floorplans(),
        "KPIs Additionnels": test_additional_kpis()
    }
    
    # Résumé
    logger.info("\n" + "="*60)
    logger.info("RÉSUMÉ DES TESTS")
    logger.info("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\nTotal : {passed}/{total} tests réussis")
    
    if passed == total:
        logger.success("\n╔══════════════════════════════════════════════════════════╗")
        logger.success("║        ✓ TOUS LES TESTS RÉUSSIS                         ║")
        logger.success("╚══════════════════════════════════════════════════════════╝")
    else:
        logger.warning("\n╔══════════════════════════════════════════════════════════╗")
        logger.warning("║        ⚠ CERTAINS TESTS ONT ÉCHOUÉ                      ║")
        logger.warning("╚══════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()

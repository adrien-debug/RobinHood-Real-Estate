"""
Script de test complet pour tous les endpoints et connecteurs
"""
import sys
from datetime import date, timedelta
from loguru import logger
import traceback

# Configuration du logger
logger.remove()
logger.add(sys.stdout, format="<level>{message}</level>", level="INFO")

def print_section(title):
    """Afficher une section"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_test(name, status, details=""):
    """Afficher un résultat de test"""
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")
    if details:
        print(f"   → {details}")

def test_env_variables():
    """Test 1: Vérifier les variables d'environnement"""
    print_section("TEST 1: VARIABLES D'ENVIRONNEMENT")
    
    from core.config import settings
    
    tests = [
        ("DATABASE_URL", settings.database_url, "postgresql" in settings.database_url),
        ("BAYUT_API_KEY", settings.bayut_api_key, len(settings.bayut_api_key) > 0),
        ("BAYUT_API_URL", settings.bayut_api_url, "rapidapi" in settings.bayut_api_url),
        ("PROPERTYFINDER_API_KEY", settings.propertyfinder_api_key, len(settings.propertyfinder_api_key) > 0),
        ("ZYLALABS_API_KEY", settings.zylalabs_api_key, len(settings.zylalabs_api_key) > 0),
        ("DLD_API_KEY", settings.dld_api_key, len(settings.dld_api_key) > 0),
        ("DLD_API_SECRET", settings.dld_api_secret, len(settings.dld_api_secret) > 0),
        ("OPENAI_API_KEY", settings.openai_api_key, len(settings.openai_api_key) > 0),
    ]
    
    passed = 0
    for name, value, condition in tests:
        status = condition if value else False
        print_test(name, status, f"Configuré" if status else "Non configuré (mode MOCK)")
        if status:
            passed += 1
    
    print(f"\n📊 Résultat: {passed}/{len(tests)} variables configurées")
    return passed, len(tests)

def test_database_connection():
    """Test 2: Connexion à la base de données"""
    print_section("TEST 2: CONNEXION BASE DE DONNÉES")
    
    try:
        from core.db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test 1: Connexion
        print_test("Connexion PostgreSQL", True, "Connexion établie")
        
        # Test 2: Schéma
        cursor.execute("SELECT current_schema()")
        schema = cursor.fetchone()[0]
        print_test("Schéma actuel", True, f"Schema: {schema}")
        
        # Test 3: Tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = current_schema()
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print_test("Tables disponibles", len(tables) > 0, f"{len(tables)} tables trouvées")
        
        if tables:
            print("   Tables:", ", ".join(tables[:5]) + ("..." if len(tables) > 5 else ""))
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print_test("Connexion PostgreSQL", False, f"Erreur: {str(e)}")
        return False

def test_dld_transactions():
    """Test 3: DLD Transactions"""
    print_section("TEST 3: DLD TRANSACTIONS")
    
    try:
        from connectors.dld_transactions import DLDTransactionsConnector
        
        connector = DLDTransactionsConnector()
        
        # Test avec 7 derniers jours
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        print(f"📅 Période: {start_date} → {end_date}")
        
        transactions = connector.fetch_transactions(
            start_date=start_date,
            end_date=end_date,
            limit=100
        )
        
        print_test("Récupération transactions", True, f"{len(transactions)} transactions")
        
        if transactions:
            tx = transactions[0]
            print(f"\n   Exemple de transaction:")
            print(f"   - ID: {tx.transaction_id}")
            print(f"   - Date: {tx.transaction_date}")
            print(f"   - Type: {tx.transaction_type}")
            print(f"   - Localisation: {tx.community}")
            print(f"   - Prix: {tx.price_aed} AED" if tx.price_aed else "   - Prix: N/A")
        
        return True, len(transactions)
    except Exception as e:
        print_test("Récupération transactions", False, f"Erreur: {str(e)}")
        traceback.print_exc()
        return False, 0

def test_bayut_api():
    """Test 4: Bayut API"""
    print_section("TEST 4: BAYUT API")
    
    try:
        from connectors.bayut_api import BayutAPIConnector
        
        bayut = BayutAPIConnector()
        
        # Test 1: Search properties
        print("🔍 Test properties_search...")
        properties = bayut.search_properties(location="Dubai Marina", limit=5)
        print_test("Properties Search", True, f"{len(properties)} propriétés")
        
        # Test 2: Search developers
        print("\n🔍 Test developers_search...")
        developers = bayut.search_developers(query="Emaar")
        print_test("Developers Search", True, f"{len(developers)} développeurs")
        
        if developers:
            print(f"   Premier développeur: {developers[0].get('name')}")
        
        # Test 3: New projects
        print("\n🔍 Test new_projects_search...")
        projects = bayut.search_new_projects(location="Dubai Marina", limit=5)
        print_test("New Projects Search", True, f"{len(projects)} projets")
        
        # Test 4: Agents
        print("\n🔍 Test agents_by_name...")
        agents = bayut.search_agents_by_name(name="Dubai")
        print_test("Agents Search", True, f"{len(agents)} agents")
        
        return True
    except Exception as e:
        print_test("Bayut API", False, f"Erreur: {str(e)}")
        traceback.print_exc()
        return False

def test_propertyfinder_api():
    """Test 5: PropertyFinder API"""
    print_section("TEST 5: PROPERTYFINDER API")
    
    try:
        from connectors.propertyfinder_api import PropertyFinderAPIConnector
        
        pf = PropertyFinderAPIConnector()
        
        # Test search
        print("🔍 Test search_properties...")
        properties = pf.search_properties(location="Dubai Marina", limit=5)
        print_test("PropertyFinder Search", True, f"{len(properties)} propriétés")
        
        if properties:
            prop = properties[0]
            print(f"\n   Exemple de propriété:")
            print(f"   - Titre: {prop.get('title', 'N/A')}")
            print(f"   - Prix: {prop.get('price', 'N/A')}")
            print(f"   - Localisation: {prop.get('location', 'N/A')}")
        
        return True
    except Exception as e:
        print_test("PropertyFinder API", False, f"Erreur: {str(e)}")
        traceback.print_exc()
        return False

def test_zylalabs_api():
    """Test 6: Zyla Labs API"""
    print_section("TEST 6: ZYLA LABS API")
    
    try:
        from connectors.zylalabs_api import ZylaLabsAPIConnector
        
        zyla = ZylaLabsAPIConnector()
        
        # Test market stats
        print("🔍 Test get_market_stats...")
        stats = zyla.get_market_stats()
        print_test("Market Stats", True, f"{len(stats)} statistiques" if stats else "Données récupérées")
        
        # Test search properties
        print("\n🔍 Test search_properties...")
        properties = zyla.search_properties(location="Dubai Marina", limit=5)
        print_test("Search Properties", True, f"{len(properties)} propriétés")
        
        return True
    except Exception as e:
        print_test("Zyla Labs API", False, f"Erreur: {str(e)}")
        traceback.print_exc()
        return False

def test_emaar_helper():
    """Test 7: Emaar Helper"""
    print_section("TEST 7: EMAAR HELPER")
    
    try:
        from connectors.emaar_helper import EmaarDataHelper, get_emaar_data
        
        emaar = EmaarDataHelper()
        
        # Test 1: ID Emaar
        print("🔍 Test récupération ID Emaar...")
        has_id = emaar.EMAAR_DEVELOPER_IDS['bayut'] is not None
        print_test("ID Emaar", has_id, f"ID: {emaar.EMAAR_DEVELOPER_IDS['bayut']}" if has_id else "Mode MOCK")
        
        # Test 2: Projets
        print("\n🔍 Test get_all_projects...")
        projects = emaar.get_all_projects()
        print_test("Projets Emaar", True, f"{len(projects)} projets")
        
        # Test 3: Listings
        print("\n🔍 Test get_all_listings...")
        listings = emaar.get_all_listings(purpose="for-sale")
        print_test("Listings Emaar", True, f"{len(listings)} listings")
        
        # Test 4: Transactions
        print("\n🔍 Test get_recent_transactions...")
        transactions = emaar.get_recent_transactions(days=30)
        print_test("Transactions Emaar", True, f"{len(transactions)} transactions")
        
        # Test 5: Statistiques
        print("\n🔍 Test get_emaar_statistics...")
        stats = emaar.get_emaar_statistics(days=30)
        print_test("Statistiques Emaar", True, "Calculées")
        
        print(f"\n   📊 Statistiques:")
        print(f"   - Projets: {stats['projects']['total']}")
        print(f"   - Listings: {stats['listings']['total']}")
        print(f"   - Transactions: {stats['transactions']['total']}")
        
        # Test 6: Fonction helper rapide
        print("\n🔍 Test get_emaar_data()...")
        data = get_emaar_data("statistics", days=30)
        print_test("Fonction helper", True, f"{len(data)} clés")
        
        return True
    except Exception as e:
        print_test("Emaar Helper", False, f"Erreur: {str(e)}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "🚀"*40)
    print("  TEST COMPLET DE TOUS LES ENDPOINTS")
    print("🚀"*40)
    
    results = {}
    
    # Test 1: Variables d'environnement
    env_passed, env_total = test_env_variables()
    results['env'] = (env_passed, env_total)
    
    # Test 2: Base de données
    results['db'] = test_database_connection()
    
    # Test 3: DLD Transactions
    dld_ok, dld_count = test_dld_transactions()
    results['dld'] = (dld_ok, dld_count)
    
    # Test 4: Bayut API
    results['bayut'] = test_bayut_api()
    
    # Test 5: PropertyFinder API
    results['propertyfinder'] = test_propertyfinder_api()
    
    # Test 6: Zyla Labs API
    results['zylalabs'] = test_zylalabs_api()
    
    # Test 7: Emaar Helper
    results['emaar'] = test_emaar_helper()
    
    # Résumé final
    print_section("RÉSUMÉ FINAL")
    
    print("📊 RÉSULTATS PAR COMPOSANT:\n")
    
    print(f"{'Composant':<25} {'Statut':<15} {'Détails'}")
    print("-" * 70)
    
    env_passed, env_total = results['env']
    print(f"{'Variables ENV':<25} {'✅ OK' if env_passed > 0 else '❌ FAIL':<15} {env_passed}/{env_total} configurées")
    
    print(f"{'Base de données':<25} {'✅ OK' if results['db'] else '❌ FAIL':<15} {'Connectée' if results['db'] else 'Erreur'}")
    
    dld_ok, dld_count = results['dld']
    print(f"{'DLD Transactions':<25} {'✅ OK' if dld_ok else '❌ FAIL':<15} {dld_count} transactions")
    
    print(f"{'Bayut API':<25} {'✅ OK' if results['bayut'] else '❌ FAIL':<15} {'Opérationnel' if results['bayut'] else 'Erreur'}")
    
    print(f"{'PropertyFinder API':<25} {'✅ OK' if results['propertyfinder'] else '❌ FAIL':<15} {'Opérationnel' if results['propertyfinder'] else 'Erreur'}")
    
    print(f"{'Zyla Labs API':<25} {'✅ OK' if results['zylalabs'] else '❌ FAIL':<15} {'Opérationnel' if results['zylalabs'] else 'Erreur'}")
    
    print(f"{'Emaar Helper':<25} {'✅ OK' if results['emaar'] else '❌ FAIL':<15} {'Opérationnel' if results['emaar'] else 'Erreur'}")
    
    # Score global
    total_tests = 7
    passed_tests = sum([
        1 if env_passed > 0 else 0,
        1 if results['db'] else 0,
        1 if dld_ok else 0,
        1 if results['bayut'] else 0,
        1 if results['propertyfinder'] else 0,
        1 if results['zylalabs'] else 0,
        1 if results['emaar'] else 0,
    ])
    
    print("\n" + "="*70)
    print(f"🎯 SCORE GLOBAL: {passed_tests}/{total_tests} tests réussis ({passed_tests*100//total_tests}%)")
    print("="*70 + "\n")
    
    if passed_tests == total_tests:
        print("✅ ✅ ✅ TOUS LES TESTS SONT PASSÉS ! ✅ ✅ ✅")
    elif passed_tests >= total_tests * 0.7:
        print("⚠️  La plupart des tests sont passés, quelques problèmes à résoudre")
    else:
        print("❌ Plusieurs composants nécessitent une attention")
    
    print()
    
    return results

if __name__ == "__main__":
    try:
        results = run_all_tests()
        sys.exit(0 if all([v if isinstance(v, bool) else v[0] for v in results.values()]) else 1)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        traceback.print_exc()
        sys.exit(1)

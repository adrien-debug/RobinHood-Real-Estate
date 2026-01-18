"""
Script de test pour vérifier la connexion aux APIs DLD (Dubai Pulse)
"""
from datetime import date, timedelta
from loguru import logger
from connectors.transactions import DLDTransactionsConnector
from connectors.dld_buildings import DLDBuildingsConnector
from connectors.dubai_pulse_auth import get_dubai_pulse_auth


def test_authentication():
    """Tester l'authentification OAuth"""
    print("\n" + "="*60)
    print("TEST 1 : Authentification OAuth Dubai Pulse")
    print("="*60)
    
    try:
        auth = get_dubai_pulse_auth()
        token = auth.get_access_token()
        
        if token:
            print("✅ Authentification réussie")
            print(f"   Token obtenu : {token[:20]}...")
            return True
        else:
            print("❌ Aucun token reçu")
            return False
    
    except ValueError as e:
        print(f"⚠️  {e}")
        print("   → Configure DLD_API_KEY et DLD_API_SECRET dans .env")
        return False
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def test_transactions():
    """Tester la récupération de transactions"""
    print("\n" + "="*60)
    print("TEST 2 : Récupération Transactions DLD")
    print("="*60)
    
    try:
        connector = DLDTransactionsConnector()
        
        # Récupérer les transactions des 2 derniers jours
        end_date = date.today()
        start_date = end_date - timedelta(days=2)
        
        print(f"   Période : {start_date} → {end_date}")
        
        transactions = connector.fetch_transactions(
            start_date=start_date,
            end_date=end_date,
            limit=100
        )
        
        if transactions:
            print(f"✅ {len(transactions)} transactions récupérées")
            
            # Afficher un exemple
            if len(transactions) > 0:
                tx = transactions[0]
                print(f"\n   Exemple de transaction :")
                print(f"   - ID : {tx.transaction_id}")
                print(f"   - Date : {tx.transaction_date}")
                print(f"   - Communauté : {tx.community}")
                print(f"   - Projet : {tx.project}")
                print(f"   - Type : {tx.property_type}")
                print(f"   - Chambres : {tx.rooms_bucket}")
                print(f"   - Surface : {tx.area_sqft} sqft")
                print(f"   - Prix : {tx.price_aed:,.0f} AED")
                if tx.price_per_sqft:
                    print(f"   - Prix/sqft : {tx.price_per_sqft:,.0f} AED")
            
            return True
        else:
            print("⚠️  Aucune transaction récupérée")
            print("   → Vérifier la période ou les filtres")
            return False
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def test_buildings():
    """Tester la récupération de bâtiments"""
    print("\n" + "="*60)
    print("TEST 3 : Récupération Buildings DLD")
    print("="*60)
    
    try:
        connector = DLDBuildingsConnector()
        
        # Récupérer quelques bâtiments
        buildings = connector.fetch_buildings(
            community="Dubai Marina",
            limit=10
        )
        
        if buildings:
            print(f"✅ {len(buildings)} bâtiments récupérés")
            
            # Afficher un exemple
            if len(buildings) > 0:
                building = buildings[0]
                print(f"\n   Exemple de bâtiment :")
                print(f"   - Nom : {building.get('building_name')}")
                print(f"   - Communauté : {building.get('community')}")
                print(f"   - Projet : {building.get('project')}")
                print(f"   - Type : {building.get('building_type')}")
                print(f"   - Usage : {building.get('building_usage')}")
            
            return True
        else:
            print("⚠️  Aucun bâtiment récupéré")
            return False
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False


def main():
    """Exécuter tous les tests"""
    print("\n" + "🔍 TEST DE CONNEXION APIs DLD (Dubai Pulse)")
    print("="*60)
    
    results = {
        'auth': test_authentication(),
        'transactions': test_transactions(),
        'buildings': test_buildings()
    }
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} : {test_name}")
    
    total_pass = sum(results.values())
    total_tests = len(results)
    
    print(f"\n{total_pass}/{total_tests} tests réussis")
    
    if total_pass == 0:
        print("\n⚠️  AUCUN TEST RÉUSSI")
        print("   → Les clés API ne sont pas configurées")
        print("   → L'app utilisera des données MOCK")
        print("   → Voir docs/dubai_pulse_api_setup.md pour configurer les APIs")
    elif total_pass < total_tests:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("   → Vérifier les logs ci-dessus pour plus de détails")
    else:
        print("\n🎉 TOUS LES TESTS RÉUSSIS !")
        print("   → Les APIs DLD sont correctement configurées")
        print("   → L'app utilisera des données réelles de Dubaï")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

"""
Script de test pour vérifier l'accès aux données Emaar Properties
"""
from connectors.emaar_helper import EmaarDataHelper, get_emaar_data
from loguru import logger
import json


def test_emaar_helper():
    """Tester le helper Emaar"""
    
    print("\n" + "="*80)
    print("🏢 TEST EMAAR DATA HELPER")
    print("="*80 + "\n")
    
    emaar = EmaarDataHelper()
    
    # Test 1 : Récupération ID Emaar
    print("📋 Test 1 : Récupération ID développeur Emaar")
    print("-" * 80)
    if emaar.EMAAR_DEVELOPER_IDS['bayut']:
        print(f"✅ ID Emaar sur Bayut : {emaar.EMAAR_DEVELOPER_IDS['bayut']}")
    else:
        print("⚠️  ID Emaar non trouvé (mode MOCK ou API non configurée)")
    print()
    
    # Test 2 : Projets Emaar
    print("📋 Test 2 : Récupération projets Emaar")
    print("-" * 80)
    try:
        projects = emaar.get_all_projects()
        print(f"✅ {len(projects)} projets Emaar récupérés")
        
        if projects:
            print("\n🏗️  Exemple de projet :")
            project = projects[0]
            print(f"  - Nom : {project.get('name')}")
            print(f"  - Localisation : {project.get('location')}")
            print(f"  - Statut : {project.get('status')}")
            print(f"  - Prix min : {project.get('price_min')} AED")
            print(f"  - Prix max : {project.get('price_max')} AED")
            print(f"  - Unités totales : {project.get('units_total')}")
            print(f"  - Unités disponibles : {project.get('units_available')}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
    print()
    
    # Test 3 : Listings Emaar
    print("📋 Test 3 : Récupération listings Emaar (vente)")
    print("-" * 80)
    try:
        listings = emaar.get_all_listings(purpose="for-sale")
        print(f"✅ {len(listings)} listings Emaar récupérés")
        
        if listings:
            print("\n🏠 Exemple de listing :")
            listing = listings[0]
            print(f"  - Titre : {listing.get('title')}")
            print(f"  - Type : {listing.get('property_type')}")
            print(f"  - Prix : {listing.get('price')} AED")
            print(f"  - Chambres : {listing.get('bedrooms')}")
            print(f"  - Surface : {listing.get('area_sqft')} sqft")
            print(f"  - Localisation : {listing.get('location')}")
            print(f"  - Jours sur marché : {listing.get('days_on_market')}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
    print()
    
    # Test 4 : Transactions Emaar
    print("📋 Test 4 : Récupération transactions Emaar (30 derniers jours)")
    print("-" * 80)
    try:
        transactions = emaar.get_recent_transactions(days=30)
        print(f"✅ {len(transactions)} transactions Emaar trouvées")
        
        if transactions:
            print("\n💰 Exemple de transaction :")
            tx = transactions[0]
            print(f"  - Date : {tx.get('date')}")
            print(f"  - Type : {tx.get('type')}")
            print(f"  - Localisation : {tx.get('location')}")
            print(f"  - Prix : {tx.get('price_aed')} AED")
            print(f"  - Surface : {tx.get('area_sqft')} sqft")
            print(f"  - Prix/sqft : {tx.get('price_per_sqft')} AED/sqft")
            print(f"  - Off-plan : {tx.get('is_offplan')}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
    print()
    
    # Test 5 : Agents Emaar
    print("📋 Test 5 : Récupération agents Emaar")
    print("-" * 80)
    try:
        agents = emaar.get_emaar_agents()
        print(f"✅ {len(agents)} agents Emaar trouvés")
        
        if agents:
            print("\n👤 Exemple d'agent :")
            agent = agents[0]
            print(f"  - Nom : {agent.get('name')}")
            print(f"  - Agence : {agent.get('agency')}")
            print(f"  - Téléphone : {agent.get('phone')}")
            print(f"  - Langues : {', '.join(agent.get('languages', []))}")
            print(f"  - Nombre de listings : {agent.get('listings_count')}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
    print()
    
    # Test 6 : Statistiques Emaar
    print("📋 Test 6 : Statistiques agrégées Emaar")
    print("-" * 80)
    try:
        stats = emaar.get_emaar_statistics(days=30)
        print(f"✅ Statistiques calculées")
        
        print("\n📊 Statistiques Emaar (30 derniers jours) :")
        print(f"\n  Transactions :")
        print(f"    - Total : {stats['transactions']['total']}")
        print(f"    - Volume : {stats['transactions']['volume_aed']:,.0f} AED")
        print(f"    - Prix moyen/sqft : {stats['transactions']['avg_price_per_sqft']:.2f} AED/sqft")
        
        print(f"\n  Projets :")
        print(f"    - Total : {stats['projects']['total']}")
        print(f"    - En construction : {stats['projects']['under_construction']}")
        print(f"    - Complétés : {stats['projects']['completed']}")
        
        print(f"\n  Listings :")
        print(f"    - Total : {stats['listings']['total']}")
        print(f"    - À vendre : {stats['listings']['for_sale']}")
        print(f"    - À louer : {stats['listings']['for_rent']}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
    print()
    
    # Test 7 : Fonction helper rapide
    print("📋 Test 7 : Fonction helper rapide get_emaar_data()")
    print("-" * 80)
    try:
        data = get_emaar_data("statistics", days=30)
        print(f"✅ Données récupérées via fonction helper")
        print(f"  - Clés disponibles : {list(data.keys())}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
    print()
    
    # Test 8 : Liste des projets Emaar connus
    print("📋 Test 8 : Liste des projets Emaar connus")
    print("-" * 80)
    project_names = emaar.get_emaar_project_names()
    print(f"✅ {len(project_names)} projets Emaar référencés")
    print("\n🏗️  Exemples de projets :")
    for name in project_names[:10]:
        print(f"  - {name}")
    print(f"  ... et {len(project_names) - 10} autres")
    print()
    
    print("="*80)
    print("✅ TESTS TERMINÉS")
    print("="*80 + "\n")


def test_quick_function():
    """Tester la fonction helper rapide"""
    
    print("\n" + "="*80)
    print("⚡ TEST FONCTION RAPIDE get_emaar_data()")
    print("="*80 + "\n")
    
    # Test avec différents types
    test_cases = [
        ("projects", {}),
        ("listings", {"purpose": "for-sale"}),
        ("transactions", {"days": 30}),
        ("agents", {}),
        ("statistics", {"days": 30}),
    ]
    
    for data_type, kwargs in test_cases:
        print(f"📋 Test : get_emaar_data('{data_type}', {kwargs})")
        print("-" * 80)
        try:
            data = get_emaar_data(data_type, **kwargs)
            
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"  ✅ {key} : {len(value)} éléments")
                elif isinstance(value, dict):
                    print(f"  ✅ {key} : {len(value)} clés")
                else:
                    print(f"  ✅ {key} : {value}")
        except Exception as e:
            print(f"  ❌ Erreur : {e}")
        print()
    
    print("="*80)
    print("✅ TESTS FONCTION RAPIDE TERMINÉS")
    print("="*80 + "\n")


def export_sample_data():
    """Exporter des données exemple en JSON"""
    
    print("\n" + "="*80)
    print("💾 EXPORT DONNÉES EXEMPLE")
    print("="*80 + "\n")
    
    try:
        data = get_emaar_data("all", days=30)
        
        # Limiter à 3 éléments par catégorie pour l'exemple
        sample_data = {}
        for key, value in data.items():
            if isinstance(value, list):
                sample_data[key] = value[:3]
            else:
                sample_data[key] = value
        
        # Exporter en JSON
        output_file = "emaar_sample_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Données exemple exportées dans : {output_file}")
        print(f"  - Projets : {len(sample_data.get('projects', []))} exemples")
        print(f"  - Listings : {len(sample_data.get('listings', []))} exemples")
        print(f"  - Transactions : {len(sample_data.get('transactions', []))} exemples")
        print(f"  - Agents : {len(sample_data.get('agents', []))} exemples")
        print(f"  - Statistiques : Incluses")
        
    except Exception as e:
        print(f"❌ Erreur export : {e}")
    
    print()
    print("="*80)
    print("✅ EXPORT TERMINÉ")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Configurer logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<level>{message}</level>",
        level="INFO"
    )
    
    # Lancer les tests
    test_emaar_helper()
    test_quick_function()
    export_sample_data()
    
    print("\n🎉 Tous les tests sont terminés !")
    print("\n💡 Prochaines étapes :")
    print("  1. Vérifier le fichier emaar_sample_data.json")
    print("  2. Intégrer le helper dans vos pages Streamlit")
    print("  3. Créer une page dédiée Emaar (pages/09_Emaar.py)")
    print("  4. Configurer les clés API dans .env si mode MOCK")
    print()

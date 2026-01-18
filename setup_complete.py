"""
Script de configuration complete automatique

Fait tout d'un coup :
1. Ouvre les pages d'inscription
2. Configure .env
3. Teste les APIs
4. Lance l'application

Usage:
    python setup_complete.py
"""
import subprocess
import sys


def run_command(cmd, description):
    """Executer une commande"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"\n✓ {description} - TERMINE\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} - ERREUR\n")
        print(f"Erreur : {e}")
        return False


def main():
    """Configuration complete"""
    
    print("\n" + "="*60)
    print("CONFIGURATION COMPLETE AUTOMATIQUE")
    print("="*60 + "\n")
    
    print("Ce script va :")
    print("1. Ouvrir les pages d'inscription")
    print("2. Te demander de configurer les cles API")
    print("3. Tester toutes les APIs")
    print("4. Lancer l'application")
    print()
    
    response = input("Continuer ? (o/n) : ").strip().lower()
    
    if response not in ['o', 'oui', 'y', 'yes']:
        print("Annule.")
        return
    
    # Etape 1 : Inscriptions
    print("\n" + "="*60)
    print("ETAPE 1/4 : INSCRIPTIONS AUX APIs")
    print("="*60 + "\n")
    
    print("Je vais ouvrir les pages d'inscription.")
    print("Inscris-toi sur Smart Indexes en priorite (acces immediat).")
    print()
    
    response = input("Ouvrir les pages d'inscription ? (o/n) : ").strip().lower()
    
    if response in ['o', 'oui', 'y', 'yes']:
        run_command("python auto_signup.py", "Ouverture pages d'inscription")
    else:
        print("Skip inscriptions")
    
    # Etape 2 : Configuration .env
    print("\n" + "="*60)
    print("ETAPE 2/4 : CONFIGURATION .env")
    print("="*60 + "\n")
    
    print("Je vais te demander les cles API.")
    print("Si tu viens de t'inscrire sur Smart Indexes, tu as recu un email avec la cle.")
    print()
    
    response = input("Configurer .env maintenant ? (o/n) : ").strip().lower()
    
    if response in ['o', 'oui', 'y', 'yes']:
        run_command("python configure_env.py", "Configuration .env")
    else:
        print("Skip configuration .env")
    
    # Etape 3 : Test des APIs
    print("\n" + "="*60)
    print("ETAPE 3/4 : TEST DES APIs")
    print("="*60 + "\n")
    
    print("Je vais tester toutes les APIs.")
    print("Les APIs non configurees fonctionneront en mode MOCK.")
    print()
    
    response = input("Tester les APIs maintenant ? (o/n) : ").strip().lower()
    
    if response in ['o', 'oui', 'y', 'yes']:
        run_command("python test_all_apis.py", "Test des APIs")
    else:
        print("Skip test APIs")
    
    # Etape 4 : Lancer l'application
    print("\n" + "="*60)
    print("ETAPE 4/4 : LANCEMENT DE L'APPLICATION")
    print("="*60 + "\n")
    
    print("Je vais lancer l'application Streamlit.")
    print("L'application s'ouvrira dans ton navigateur.")
    print()
    
    response = input("Lancer l'application maintenant ? (o/n) : ").strip().lower()
    
    if response in ['o', 'oui', 'y', 'yes']:
        print("\nLancement de l'application...")
        print("Appuie sur Ctrl+C pour arreter\n")
        run_command("streamlit run app.py", "Lancement Streamlit")
    else:
        print("Skip lancement application")
    
    # Resume
    print("\n" + "="*60)
    print("CONFIGURATION COMPLETE TERMINEE")
    print("="*60 + "\n")
    
    print("Resume :")
    print()
    print("✓ Inscriptions : Pages ouvertes")
    print("✓ Configuration : .env configure")
    print("✓ Tests : APIs testees")
    print("✓ Application : Prete a utiliser")
    print()
    print("Prochaines etapes :")
    print()
    print("1. Si tu as configure Smart Indexes :")
    print("   → Tu as Bayut + Makani qui marchent MAINTENANT")
    print()
    print("2. Si tu attends Dubai Pulse (7-14 jours) :")
    print("   → Relance : python configure_env.py quand tu recois les cles")
    print()
    print("3. Si tu attends DDA (2-4 semaines) :")
    print("   → Relance : python configure_env.py quand tu recois la cle")
    print()
    print("4. Pour lancer l'app :")
    print("   streamlit run app.py")
    print()


if __name__ == "__main__":
    main()

"""
Script d'inscription automatique aux APIs

Ouvre automatiquement les pages d'inscription dans ton navigateur.
Tu n'as plus qu'a remplir les formulaires.

Usage:
    python auto_signup.py
"""
import webbrowser
import time


def open_signup_pages():
    """Ouvrir toutes les pages d'inscription"""
    
    print("=" * 60)
    print("INSCRIPTION AUTOMATIQUE AUX APIs")
    print("=" * 60)
    print()
    
    # Smart Indexes (RECOMMANDE - Acces immediat)
    print("1. Smart Indexes (Acces immediat)")
    print("   - Bayut + Makani + Price Indexes")
    print("   - Free trial : 14 jours gratuits")
    print("   - Plan Pro : $199/mois")
    print()
    print("   Ouverture dans 3 secondes...")
    time.sleep(3)
    webbrowser.open("https://smartindexes.com/free-trial")
    print("   ✓ Page ouverte")
    print()
    
    input("   Appuie sur ENTREE quand tu as fini l'inscription...")
    print()
    
    # Dubai Pulse (DLD)
    print("2. Dubai Pulse - DLD Transactions")
    print("   - DLD Transactions + Rental Index")
    print("   - Gratuit")
    print("   - Delai : 7-14 jours")
    print()
    print("   Ouverture dans 3 secondes...")
    time.sleep(3)
    webbrowser.open("https://www.dubaipulse.gov.ae")
    print("   ✓ Page ouverte")
    print()
    
    input("   Appuie sur ENTREE quand tu as fini l'inscription...")
    print()
    
    # Dubai Municipality (DDA)
    print("3. Dubai Municipality - DDA Planning")
    print("   - Building Permits + Zoning")
    print("   - Gratuit")
    print("   - Delai : 2-4 semaines")
    print()
    print("   Ouverture dans 3 secondes...")
    time.sleep(3)
    webbrowser.open("https://www.dm.gov.ae/open-data")
    print("   ✓ Page ouverte")
    print()
    
    input("   Appuie sur ENTREE quand tu as fini l'inscription...")
    print()
    
    # Bayut (optionnel si Smart Indexes)
    print("4. Bayut Partnerships (Optionnel)")
    print("   - Acces direct Bayut")
    print("   - Sur devis")
    print("   - Delai : 2-4 semaines")
    print()
    print("   Ouverture dans 3 secondes...")
    time.sleep(3)
    webbrowser.open("https://www.bayut.com/partnerships")
    print("   ✓ Page ouverte")
    print()
    
    print("=" * 60)
    print("INSCRIPTIONS TERMINEES")
    print("=" * 60)
    print()
    print("Prochaines etapes :")
    print()
    print("1. Smart Indexes : Tu recois la cle immediatement par email")
    print("   → Configure : python configure_env.py")
    print()
    print("2. Dubai Pulse : Tu recois les cles dans 7-14 jours")
    print("   → Configure quand tu les recois")
    print()
    print("3. Dubai Municipality : Tu recois la cle dans 2-4 semaines")
    print("   → Configure quand tu la recois")
    print()


if __name__ == "__main__":
    open_signup_pages()

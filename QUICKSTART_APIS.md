# Quickstart - Configuration des APIs

## Demarrage rapide (5 minutes)

### Etape 1 : Tester en mode MOCK (sans cles API)

Tous les connecteurs fonctionnent en mode MOCK par defaut.

```bash
# Tester tous les connecteurs
python test_all_apis.py
```

Tu verras :
- ✓ DLD Transactions : 50 transactions fictives
- ✓ DLD Rental Index : donnees locatives fictives
- ✓ Bayut API : 40 annonces fictives
- ✓ Makani Geocoding : adresses fictives
- ✓ DDA Planning : 15 permis fictifs

**Resultat attendu** : Tous les tests PASS

---

### Etape 2 : Configurer les cles API reelles

```bash
# Verifier la configuration actuelle
python setup_apis.py
```

Le script va :
1. Creer `.env` si necessaire
2. Verifier quelles cles sont configurees
3. Te guider pour obtenir les cles manquantes

---

### Etape 3 : Obtenir les cles API

#### Option A : Tout officiel (Gratuit, lent)

**Dubai Pulse (DLD)** - 7-14 jours
```
URL : https://www.dubaipulse.gov.ae
Email : info@dubaipulse.gov.ae
Cles : DLD_API_KEY + DLD_API_SECRET
```

**Makani** - 2-8 semaines
```
URL : https://geohub.dubaipulse.gov.ae
Cle : MAKANI_API_KEY
```

**DDA** - 2-4 semaines
```
URL : https://www.dm.gov.ae/open-data
Email : dm@dm.gov.ae
Cle : DDA_API_KEY
```

**Bayut** - 2-4 semaines
```
URL : https://www.bayut.com/partnerships
Email : partnerships@bayut.com
Tel : +971 4 447 1400
Cle : BAYUT_API_KEY
```

#### Option B : Smart Indexes (Rapide, payant) [RECOMMANDE]

**Smart Indexes** - Immediat
```
URL : https://smartindexes.com
Email : info@smartindexes.com
Cout : ~$199/mois (Plan Pro)
Inclut : Bayut + Makani + Price Indexes
```

Avantages :
- Acces immediat (pas d'attente)
- Une seule cle pour Bayut + Makani
- Support client reactif
- Documentation complete

---

### Etape 4 : Configurer le fichier .env

```bash
# Editer .env
nano .env
# ou
code .env
```

Ajouter les cles :

```bash
# Dubai Pulse (DLD) - Deja configure ?
DLD_API_KEY=ton_client_id_ici
DLD_API_SECRET=ton_client_secret_ici

# Bayut API
BAYUT_API_KEY=ta_cle_bayut_ici

# Makani Geocoding
MAKANI_API_KEY=ta_cle_makani_ici

# DDA Planning
DDA_API_KEY=ta_cle_dda_ici
```

---

### Etape 5 : Tester avec les vraies cles

```bash
# Re-tester avec les cles reelles
python test_all_apis.py
```

Si tout fonctionne :
- ✓ Les connecteurs utilisent les APIs reelles
- ✓ Donnees reelles recuperees
- ✓ Pret pour l'integration dans le pipeline

---

## Troubleshooting

### Probleme : "API Key non configuree"

**Solution** :
1. Verifier que `.env` existe
2. Verifier que les cles sont bien renseignees
3. Pas d'espaces avant/apres le `=`
4. Pas de guillemets autour des valeurs

Exemple correct :
```bash
BAYUT_API_KEY=abc123xyz
```

Exemple incorrect :
```bash
BAYUT_API_KEY = "abc123xyz"  # Espaces et guillemets
```

---

### Probleme : "Erreur HTTP 401 Unauthorized"

**Solution** :
- La cle API est invalide ou expiree
- Verifier la cle sur le portail du fournisseur
- Regenerer une nouvelle cle si necessaire

---

### Probleme : "Erreur HTTP 429 Too Many Requests"

**Solution** :
- Tu as depasse le quota/rate limit
- Attendre quelques minutes
- Verifier les limites de ton plan
- Implementer un cache pour reduire les appels

---

### Probleme : Mode MOCK ne se desactive pas

**Solution** :
1. Verifier que les cles sont dans `.env`
2. Redemarrer l'application
3. Verifier les logs : `logs/app_*.log`

---

## Verification rapide

### Verifier la configuration

```bash
python -c "
from core.config import settings
print('DLD API Key:', settings.dld_api_key[:10] + '...' if settings.dld_api_key else 'Non configure')
print('Bayut API Key:', settings.bayut_api_key[:10] + '...' if settings.bayut_api_key else 'Non configure')
print('Makani API Key:', settings.makani_api_key[:10] + '...' if settings.makani_api_key else 'Non configure')
print('DDA API Key:', settings.dda_api_key[:10] + '...' if settings.dda_api_key else 'Non configure')
"
```

---

### Tester un connecteur specifique

```bash
# Test DLD Transactions
python -c "
from connectors.dld_transactions import DLDTransactionsConnector
from datetime import date, timedelta
c = DLDTransactionsConnector()
t = c.fetch_transactions(date.today() - timedelta(days=7), date.today())
print(f'{len(t)} transactions recuperees')
"

# Test Bayut
python -c "
from connectors.bayut_api import BayutAPIConnector
c = BayutAPIConnector()
l = c.fetch_listings(community='Dubai Marina')
print(f'{len(l)} annonces recuperees')
"

# Test Makani
python -c "
from connectors.makani_geocoding import MakaniGeocodingConnector
c = MakaniGeocodingConnector()
a = c.search_address('Dubai Marina', 'Marina Heights', 'Tower A')
print(f'Adresse trouvee : Makani #{a.makani_number}' if a else 'Aucune adresse')
"
```

---

## Prochaines etapes

Une fois les APIs configurees :

1. **Integrer dans le pipeline**
   ```bash
   # Voir : pipelines/ingest_transactions.py
   # Ajouter enrichissement Makani
   # Ajouter metriques Bayut
   ```

2. **Ajouter au dashboard**
   ```bash
   # Voir : pages/01_Dashboard.py
   # Afficher metriques Bayut
   # Afficher score localisation Makani
   # Afficher pression supply DDA
   ```

3. **Integrer dans le scoring**
   ```bash
   # Voir : strategies/flip.py, rent.py, long_term.py
   # Ajuster scores selon signaux Bayut
   # Ajuster scores selon localisation Makani
   # Penaliser selon supply DDA
   ```

---

## Ressources

- **Guide complet** : `docs/api_access_guide.md`
- **Liens directs** : `API_LINKS.md`
- **Stack data** : `docs/optimal_data_stack.md`
- **Documentation** : `docs/data_sources.md`

---

## Support

### Si tu bloques :

1. Verifier les logs : `logs/app_*.log`
2. Tester en mode MOCK d'abord
3. Consulter la documentation
4. Contacter le support de l'API concernee

### Contacts utiles :

- **Dubai Pulse** : info@dubaipulse.gov.ae
- **Bayut** : partnerships@bayut.com (+971 4 447 1400)
- **Smart Indexes** : info@smartindexes.com
- **Dubai Municipality** : dm@dm.gov.ae (+971 4 221 5555)

---

Derniere mise a jour : 2026-01-17  
Version : 1.0  
Statut : [PRET] Guide complet

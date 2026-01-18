# Plateformes Connectées aux Données Emaar Properties

Guide complet des sites et APIs pour récupérer les données immobilières Emaar à Dubaï.

---

## 🏆 Niveau 1 : Accès Direct Emaar (Officiel)

### 1. eTenant API Portal ✅ **Officiel Emaar**

**URL** : https://emaar.xlab.ae

**Type** : API officielle Emaar pour partenaires

**Données disponibles** :
- Sales data (données de ventes)
- Transactions partenaires
- Partner data push

**Accès** :
- Login + Subscription requis
- Réservé aux partenaires officiels Emaar
- Nécessite un accord de partenariat

**Comment obtenir l'accès** :
1. Contacter Emaar Properties directement
2. Demander un partenariat développeur/agent
3. Signer un NDA si nécessaire
4. Recevoir les credentials d'accès

**Statut** : Actif, nécessite partenariat

---

### 2. Emaar Properties Website (Web Scraping)

**URL** : https://properties.emaar.com

**Type** : Site officiel public

**Données disponibles** :
- Projets en cours et à venir
- Off-plan properties
- Prix et disponibilité
- Floorplans (plans d'étage)
- Images et vidéos
- Spécifications techniques

**Accès** :
- Public (visible par tous)
- Web scraping possible (respecter robots.txt)
- Pas d'API publique

**Note** : Données les plus à jour mais nécessite scraping

---

## 🥇 Niveau 2 : Plateformes RapidAPI (Recommandé)

### 3. Bayut API (Unofficial) via RapidAPI ✅ **Déjà intégré**

**URL** : https://rapidapi.com/taviansol/api/uae-real-estate2

**Documentation** : https://bayutapi.com

**Type** : API scraping Bayut.com

**Données Emaar disponibles** :
- ✅ Listings Emaar (vente/location)
- ✅ Projets off-plan Emaar (`/new_projects_search`)
- ✅ Développeur Emaar (`/developers_search`)
- ✅ Transactions DLD incluant Emaar (`/transactions`)
- ✅ Agents spécialisés Emaar
- ✅ Agences partenaires Emaar

**Endpoints clés** :
```
POST /properties_search       # Listings Emaar
POST /new_projects_search     # Projets off-plan
POST /developers_search       # Info développeur
POST /transactions            # Transactions DLD
POST /agents_by_filters       # Agents Emaar
POST /property/{id}           # Détails propriété
POST /floorplans              # Plans d'étage
```

**Filtrage par Emaar** :
- Utiliser `developer_ids: [<emaar_id>]`
- Récupérer l'ID via `/developers_search?query=Emaar`

**Prix** :
- BASIC : Gratuit (750 calls/mois)
- PRO : $49/mois (5,000 calls/mois)
- ULTRA : $199/mois (50,000 calls/mois)
- MEGA : $499/mois (500,000 calls/mois)

**Statut** : ✅ Déjà connecté dans `connectors/bayut_api.py`

**Exemple d'utilisation** :
```python
from connectors.bayut_api import BayutAPIConnector

bayut = BayutAPIConnector()

# 1. Récupérer ID Emaar
developers = bayut.search_developers(query="Emaar")
emaar_id = developers[0]['id']

# 2. Récupérer projets Emaar
projects = bayut.search_new_projects(developer_ids=[emaar_id])

# 3. Récupérer listings Emaar
listings = bayut.search_properties(
    developer_ids=[emaar_id],
    purpose="for-sale",
    category="residential"
)
```

---

### 4. PropertyFinder API via RapidAPI ✅ **Déjà intégré**

**URL** : https://rapidapi.com/market-data-point1-market-data-point-default/api/uae-real-estate-api-propertyfinder-ae-data

**Type** : API scraping PropertyFinder.ae

**Données Emaar** :
- 500K+ listings UAE incluant Emaar
- Listings complémentaires à Bayut
- Données de marché

**Prix** : Variable selon plan RapidAPI

**Statut** : ✅ Déjà connecté dans `connectors/propertyfinder_api.py`

---

### 5. Zyla Labs UAE Real Estate API ✅ **Déjà intégré**

**URL** : https://zylalabs.com/api-marketplace/real-estate/uae-real-estate-api/478

**Type** : API agrégée multi-sources

**Données Emaar** :
- Market statistics
- Propriétés récentes
- Recherche avancée
- Tendances de prix

**Prix** : Variable selon plan

**Statut** : ✅ Déjà connecté dans `connectors/zylalabs_api.py`

---

## 🥈 Niveau 3 : Portails Immobiliers (Scraping)

### 6. PropertyFinder.ae (Direct)

**URL** : https://www.propertyfinder.ae

**Données Emaar** :
- Listings Emaar
- Projets et développements
- Agents et agences

**Accès** :
- Web scraping (respecter robots.txt)
- Ou via API RapidAPI (voir #4)

---

### 7. Bayut.com (Direct)

**URL** : https://www.bayut.com

**Données Emaar** :
- Listings complets
- Projets off-plan
- Transactions historiques

**Accès** :
- Web scraping (respecter robots.txt)
- Ou via API RapidAPI (voir #3)

---

### 8. Dubizzle Property

**URL** : https://www.dubizzle.com/property

**Données Emaar** :
- Listings secondaires
- Annonces particuliers

**Accès** :
- Web scraping uniquement
- Pas d'API publique connue

---

## 🥉 Niveau 4 : Données Gouvernementales DLD

### 9. Dubai Land Department via Dubai Pulse ✅ **Déjà connecté**

**URL** : https://www.dubaipulse.gov.ae

**Type** : API officielle gouvernementale

**Données Emaar** :
- ✅ Transactions Emaar enregistrées au DLD
- ✅ Buildings Emaar (métadonnées)
- ✅ Rental Index Emaar
- ✅ Sales Index

**APIs disponibles** :
```
dld_transactions-open-api      # Transactions officielles
dld_buildings-open-api         # Bâtiments
dld_rental_index-open-api      # Index locatif
dld_residential_sale_index     # Index vente
```

**Accès** :
- Gratuit (usage non-commercial)
- OAuth 2.0
- Délai : 7-14 jours

**Statut** : ✅ Déjà connecté dans `connectors/dld_transactions.py`

---

### 10. Bayut RapidAPI - DLD Transactions ✅ **Déjà connecté**

**Type** : Transactions DLD via Bayut (pas besoin d'attendre Dubai Pulse)

**Avantages** :
- Accès immédiat (pas de délai d'approbation)
- Même données que Dubai Pulse
- Plus facile à intégrer

**Statut** : ✅ Prioritaire dans le code

---

## 📊 Niveau 5 : Données Financières/ESG

### 11. Tracenable (Emaar Financial Data)

**URL** : https://tracenable.com/company/emaar-development/disclosures

**Type** : API données financières/ESG

**Données** :
- Financial disclosures
- ESG reports
- Corporate governance
- Investor relations

**Accès** : API payante

**Note** : Pas de données projet/listings immobiliers

---

## 🎯 Recommandation pour Votre Projet

### ✅ **Déjà Opérationnel**

Vous avez **déjà les meilleures sources** intégrées dans votre projet :

1. **Bayut RapidAPI** → Listings, projets, agents, transactions Emaar
2. **PropertyFinder API** → Listings complémentaires
3. **Zyla Labs API** → Market stats
4. **DLD via Bayut** → Transactions officielles

### 🆕 **Nouveau : Helper Emaar**

Nous avons créé `connectors/emaar_helper.py` qui centralise l'accès à toutes les données Emaar :

```python
from connectors.emaar_helper import EmaarDataHelper, get_emaar_data

# Méthode 1 : Classe complète
emaar = EmaarDataHelper()
projects = emaar.get_all_projects()
listings = emaar.get_all_listings(purpose="for-sale")
transactions = emaar.get_recent_transactions(days=30)
agents = emaar.get_emaar_agents()
stats = emaar.get_emaar_statistics(days=30)

# Méthode 2 : Fonction helper rapide
data = get_emaar_data("all")  # Récupère tout
data = get_emaar_data("projects")  # Seulement projets
data = get_emaar_data("listings", purpose="for-rent")  # Listings location
```

---

## 📋 Projets Emaar Couverts

Le helper inclut **40+ projets Emaar connus** :

### Dubai Marina
- Marina Heights
- Marina Gate
- Marina Promenade
- The Address Dubai Marina

### Downtown Dubai
- Burj Khalifa
- The Address Downtown
- Boulevard Central
- South Ridge
- Standpoint Towers
- The Lofts
- Old Town
- Burj Views

### Dubai Creek Harbour
- Creek Beach
- Creek Rise
- The Cove
- Island District

### Emirates Hills
- The Lakes
- The Meadows
- The Springs
- The Greens
- Emirates Living

### Arabian Ranches
- Arabian Ranches
- Arabian Ranches 2
- Arabian Ranches 3

### Dubai Hills Estate
- Dubai Hills Estate
- Parkways
- Maple
- Sidra

### Emaar South
- Emaar South
- Golf Links

### Autres
- Emaar Beachfront
- The Valley
- Rashid Yachts & Marina
- Dubai Harbour
- The Oasis
- Expo Golf Villas

---

## 🔑 Clés API Requises

### Déjà Configurées

Dans votre `env.example` :

```bash
# Bayut API via RapidAPI (Emaar listings + transactions)
BAYUT_API_KEY=your_rapidapi_key
BAYUT_API_URL=https://uae-real-estate2.p.rapidapi.com

# PropertyFinder API via RapidAPI (Emaar listings complémentaires)
PROPERTYFINDER_API_KEY=your_rapidapi_key

# Zyla Labs API (Emaar market stats)
ZYLALABS_API_KEY=your_zylalabs_key

# DLD Transactions (Emaar transactions officielles)
DLD_API_KEY=your_client_id
DLD_API_SECRET=your_client_secret
```

### À Obtenir (Optionnel)

```bash
# Emaar eTenant API (partenaires officiels uniquement)
EMAAR_ETENANT_API_KEY=your_emaar_key
EMAAR_ETENANT_API_URL=https://emaar.xlab.ae/api
```

---

## 📊 Comparaison des Sources

| Source | Données Emaar | Accès | Coût | Délai | Qualité |
|--------|---------------|-------|------|-------|---------|
| **eTenant API** | Sales data officiel | Partenariat | Gratuit/Négocié | Variable | ⭐⭐⭐⭐⭐ |
| **Bayut RapidAPI** | Listings, projets, transactions | API immédiate | $0-499/mois | Immédiat | ⭐⭐⭐⭐ |
| **PropertyFinder API** | Listings complémentaires | API immédiate | Variable | Immédiat | ⭐⭐⭐⭐ |
| **Zyla Labs API** | Market stats | API immédiate | Variable | Immédiat | ⭐⭐⭐ |
| **DLD Dubai Pulse** | Transactions officielles | OAuth 2.0 | Gratuit | 7-14 jours | ⭐⭐⭐⭐⭐ |
| **Emaar Website** | Projets officiels | Scraping | Gratuit | Immédiat | ⭐⭐⭐⭐⭐ |

---

## 🚀 Prochaines Étapes

### 1. Tester le Helper Emaar

```bash
python -c "
from connectors.emaar_helper import get_emaar_data
data = get_emaar_data('statistics', days=30)
print(data)
"
```

### 2. Intégrer dans Streamlit

Créer une page dédiée Emaar :

```python
# pages/09_Emaar.py
import streamlit as st
from connectors.emaar_helper import EmaarDataHelper

st.title("🏢 Emaar Properties Dashboard")

emaar = EmaarDataHelper()
stats = emaar.get_emaar_statistics(days=30)

col1, col2, col3 = st.columns(3)
col1.metric("Projets Actifs", stats['projects']['total'])
col2.metric("Listings", stats['listings']['total'])
col3.metric("Transactions (30j)", stats['transactions']['total'])

# Afficher projets
st.subheader("Projets Emaar")
projects = emaar.get_all_projects()
st.dataframe(projects)
```

### 3. Obtenir Accès eTenant (Optionnel)

Si vous voulez les données officielles directes :

1. Contacter Emaar : https://properties.emaar.com/en/contact-us
2. Demander partenariat développeur/agent
3. Expliquer votre use case (analytics, market intelligence)
4. Recevoir credentials eTenant

---

## 📞 Contacts Utiles

### Emaar Properties
- **Site** : https://properties.emaar.com
- **Contact** : https://properties.emaar.com/en/contact-us
- **Téléphone** : +971 4 366 9999
- **Email** : customercare@emaar.ae

### Bayut (pour support API)
- **Site** : https://www.bayut.com
- **Email** : partnerships@bayut.com
- **Téléphone** : +971 4 447 1400

### RapidAPI Support
- **Site** : https://rapidapi.com
- **Support** : Via dashboard RapidAPI

---

## ⚠️ Notes Importantes

### Légal & Compliance

- Respecter les termes d'utilisation de chaque plateforme
- Ne pas redistribuer les données brutes
- Mentionner les sources dans vos rapports
- Respecter les rate limits des APIs

### Qualité des Données

- Les données scraping peuvent avoir des délais
- Toujours valider avec plusieurs sources
- Privilégier DLD pour les transactions officielles
- Utiliser Bayut/PropertyFinder pour les listings actuels

### Maintenance

- Vérifier régulièrement les IDs développeurs (peuvent changer)
- Monitorer les logs d'erreur
- Mettre à jour la liste des projets Emaar
- Renouveler les clés API si nécessaire

---

**Dernière mise à jour** : 2026-01-18  
**Version** : 1.0  
**Statut** : ✅ Opérationnel

# Guide d'Accès aux APIs - Stack Data Optimal

## 🎯 Vue d'ensemble

Ce guide te montre **exactement comment obtenir les clés API** pour chaque source de données du stack optimal.

---

## 1. DLD Transactions & Rental Index (Dubai Pulse) ✅

**Statut** : Déjà connecté, mais voici comment obtenir/renouveler l'accès.

### Obtenir l'accès

1. **Aller sur Dubai Pulse**
   - URL : https://www.dubaipulse.gov.ae
   - Créer un compte si nécessaire

2. **Demander l'accès aux APIs**
   - Naviguer vers "Data" → "DLD Transactions"
   - Cliquer sur "Request Access" ou "Get API Key"
   - Remplir le formulaire de demande

3. **Accepter les conditions**
   - Lire et accepter les termes d'utilisation
   - Confirmer l'usage responsable des données
   - Mentionner que c'est pour analyse de marché

4. **Recevoir les credentials**
   - Délai : **Jusqu'à 14 jours** (souvent plus rapide)
   - Tu recevras par email :
     - `CLIENT_ID` (API Key)
     - `CLIENT_SECRET` (API Secret)

5. **Configurer dans `.env`**
   ```bash
   DLD_API_KEY=ton_client_id_ici
   DLD_API_SECRET=ton_client_secret_ici
   DLD_API_BASE_URL=https://api.dubaipulse.gov.ae
   ```

### APIs disponibles avec ces credentials

- ✅ `dld_transactions-open-api` (transactions immobilières)
- ✅ `dld_rental_index-open-api` (index locatif)
- ✅ `dld_buildings-open-api` (bâtiments)
- ✅ `dld_residential_sale_index-open-api` (index de vente)
- ✅ `dld_lkp_areas-open-api` (zones/communautés)
- ✅ `dld_lkp_transaction_procedures-open-api` (types de transactions)

### Authentification OAuth 2.0

Notre connecteur gère automatiquement l'authentification :
```python
# Fichier : connectors/dubai_pulse_auth.py
# Génère automatiquement le token via client_credentials
# Cache le token jusqu'à expiration
# Renouvelle automatiquement si nécessaire
```

**Aucune action manuelle requise** une fois les clés configurées !

---

## 2. Bayut API (Lead Indicators) 🆕

**Statut** : Nouveau connecteur créé, accès à obtenir.

### Obtenir l'accès

#### Option A : Partenariat officiel (Recommandé)

1. **Aller sur Bayut Partnerships**
   - URL : https://www.bayut.com/partnerships
   - Ou : https://www.bayut.com/contact-us

2. **Contacter l'équipe commerciale**
   - Email : partnerships@bayut.com
   - Téléphone : +971 4 447 1400
   - Mentionner : "API Access for Real Estate Analytics"

3. **Préparer ta demande**
   - Expliquer ton cas d'usage (analyse de marché, détection d'opportunités)
   - Mentionner que tu ne feras pas de scraping
   - Proposer de mentionner Bayut comme source de données

4. **Négocier les termes**
   - Tarification selon volume d'appels
   - Quotas (ex : 10,000 requêtes/jour)
   - Conditions d'utilisation

5. **Recevoir les credentials**
   - `API_KEY` (Bearer token)
   - Documentation API privée
   - Endpoints disponibles

6. **Configurer dans `.env`**
   ```bash
   BAYUT_API_KEY=ton_api_key_ici
   BAYUT_API_URL=https://api.bayut.com/v1
   ```

#### Option B : Alternative - Smart Indexes

Si Bayut n'est pas accessible, Smart Indexes propose une API similaire :

1. **Aller sur Smart Indexes**
   - URL : https://smartindexes.com
   - Section "APIs" → "Property Listings"

2. **S'inscrire**
   - Créer un compte
   - Choisir un plan (Freemium / Pro / Enterprise)

3. **Obtenir l'API Key**
   - Dashboard → "API Keys"
   - Générer une nouvelle clé

4. **Configurer**
   ```bash
   BAYUT_API_KEY=ton_smart_indexes_key
   BAYUT_API_URL=https://api.smartindexes.com/v1/listings
   ```

### Données disponibles

- Annonces actives (vente/location)
- Prix demandés vs prix originaux
- Jours sur le marché
- Changements de prix
- Photos, descriptions, agents
- Filtres : zone, type, chambres, prix

### Mode MOCK

Sans clés API, le connecteur fonctionne en mode MOCK :
```python
# Génère automatiquement 40 annonces fictives
# Utile pour tester l'intégration
bayut = BayutAPIConnector()
listings = bayut.fetch_listings()  # Retourne données MOCK
```

---

## 3. Makani Geocoding (Matching & Localisation) 🆕

**Statut** : Nouveau connecteur créé, accès à obtenir.

### Obtenir l'accès

#### Option A : Dubai Pulse / GeoHub (Officiel)

1. **Aller sur GeoHub Dubai**
   - URL : https://geohub.dubaipulse.gov.ae
   - Ou : https://makani.ae

2. **Demander l'accès API**
   - Naviguer vers "Developers" ou "API Access"
   - Remplir le formulaire de demande
   - Mentionner : "Geocoding & Address Matching"

3. **Justifier l'usage**
   - Analyse immobilière
   - Matching précis des adresses
   - Scoring de localisation

4. **Recevoir les credentials**
   - Délai : Variable (peut prendre plusieurs semaines)
   - `API_KEY` pour Makani API

5. **Configurer dans `.env`**
   ```bash
   MAKANI_API_KEY=ton_api_key_ici
   MAKANI_API_URL=https://api.dubaipulse.gov.ae/makani
   ```

#### Option B : Smart Indexes Makani Search API (Plus rapide)

1. **Aller sur Smart Indexes**
   - URL : https://smartindexes.com/knowledge-base/makani-search-api
   - Documentation complète disponible

2. **S'inscrire**
   - Créer un compte
   - Choisir un plan selon volume :
     - Test : Gratuit (limité)
     - Pro : ~$99-299/mois
     - Enterprise : Sur devis

3. **Obtenir l'API Key**
   - Dashboard → "API Keys"
   - Générer clé avec scope "Makani Search"

4. **Configurer**
   ```bash
   MAKANI_API_KEY=ton_smart_indexes_key
   MAKANI_API_URL=https://api.smartindexes.com/v1/makani
   ```

### Données disponibles

- Numéro Makani unique (10 chiffres)
- Coordonnées GPS (lat/lon)
- Adresse normalisée (community, project, building)
- Points d'intérêt :
  - Station de métro + distance
  - Plage + distance
  - Mall + distance
- Contours de bâtiment (polygon)
- Entrées principales

### Mode MOCK

Sans clés API, génère des données fictives :
```python
makani = MakaniGeocodingConnector()
address = makani.search_address("Dubai Marina", "Marina Heights", "Tower A")
# Retourne adresse MOCK avec coordonnées approximatives
```

---

## 4. DDA Planning & Zoning (Signaux en avance) 🆕

**Statut** : Nouveau connecteur créé, accès à obtenir.

### Obtenir l'accès

1. **Aller sur Dubai Municipality Open Data**
   - URL : https://www.dm.gov.ae/open-data
   - Section "Planning & Development"

2. **Créer un compte**
   - S'inscrire sur le portail
   - Vérifier l'email

3. **Demander l'accès API**
   - Naviguer vers "API Access" ou "Developer Portal"
   - Remplir le formulaire :
     - Nom de l'organisation
     - Cas d'usage (analyse de marché immobilier)
     - Volume estimé de requêtes

4. **Accepter les conditions**
   - Lire les termes d'utilisation
   - Confirmer l'usage responsable
   - Engagement de confidentialité

5. **Recevoir les credentials**
   - Délai : **Variable** (peut prendre 2-4 semaines)
   - `API_KEY` pour DDA APIs

6. **Configurer dans `.env`**
   ```bash
   DDA_API_KEY=ton_api_key_ici
   DDA_API_URL=https://api.dm.gov.ae/v1
   ```

### APIs disponibles

- **Building Permits** (`/building-permits`)
  - Nouveaux permis de construire
  - Nombre d'unités
  - Date de livraison prévue
  - Développeur

- **Zoning Changes** (`/zoning-changes`)
  - Changements de zonage récents
  - Ancien vs nouveau zonage
  - Date effective
  - Impact

### Données disponibles

- Permis de construire (90 derniers jours)
- Changements de zonage (180 derniers jours)
- Projets d'infrastructure
- Zones de développement prioritaire

### Mode MOCK

Sans clés API, génère des données fictives :
```python
dda = DDAConnector()
permits = dda.fetch_building_permits(days_back=90)
# Retourne 15 permis fictifs
```

---

## 5. Résumé des coûts estimés

| API | Coût estimé | Délai d'obtention | Difficulté |
|-----|-------------|-------------------|------------|
| **Dubai Pulse (DLD)** | Gratuit (usage non-commercial) | 7-14 jours | ⭐⭐ Facile |
| **Bayut Official** | Sur devis (peut être gratuit pour partenaires) | 2-4 semaines | ⭐⭐⭐ Moyen |
| **Smart Indexes (alternative)** | $99-299/mois | Immédiat | ⭐ Très facile |
| **Makani (GeoHub)** | Gratuit (usage non-commercial) | 2-8 semaines | ⭐⭐⭐ Moyen |
| **Smart Indexes Makani** | Inclus dans plan | Immédiat | ⭐ Très facile |
| **DDA (Dubai Municipality)** | Gratuit (usage non-commercial) | 2-4 semaines | ⭐⭐⭐ Moyen |

---

## 6. Stratégie recommandée

### Phase 1 : Immédiat (0-7 jours)

1. ✅ **Dubai Pulse (DLD)** - Déjà connecté
   - Vérifier que les clés fonctionnent
   - Tester les APIs en production

2. 🔄 **Mode MOCK pour les autres**
   - Tous les nouveaux connecteurs fonctionnent en MOCK
   - Permet de tester l'intégration immédiatement

### Phase 2 : Court terme (1-4 semaines)

1. **Demander accès Smart Indexes**
   - Plus rapide que les APIs officielles
   - Couvre Bayut + Makani
   - Plan Pro : ~$199/mois

2. **Demander accès DDA**
   - Gratuit mais délai plus long
   - Signaux en avance précieux

### Phase 3 : Moyen terme (1-2 mois)

1. **Négocier partenariat Bayut**
   - Potentiellement gratuit si usage non-commercial
   - Données plus fraîches que Smart Indexes

2. **Obtenir accès Makani officiel**
   - Gratuit via GeoHub
   - Données gouvernementales officielles

---

## 7. Contacts utiles

### Dubai Pulse / DLD
- **Site** : https://www.dubaipulse.gov.ae
- **Email** : info@dubaipulse.gov.ae
- **Support** : Via formulaire sur le site

### Bayut
- **Site** : https://www.bayut.com/partnerships
- **Email** : partnerships@bayut.com
- **Téléphone** : +971 4 447 1400

### Smart Indexes
- **Site** : https://smartindexes.com
- **Email** : info@smartindexes.com
- **Support** : Via chat sur le site

### Dubai Municipality (DDA)
- **Site** : https://www.dm.gov.ae/open-data
- **Email** : dm@dm.gov.ae
- **Téléphone** : +971 4 221 5555

### Makani / GeoHub
- **Site** : https://geohub.dubaipulse.gov.ae
- **Site alternatif** : https://makani.ae
- **Email** : Via Dubai Pulse

---

## 8. Checklist de configuration

### ✅ Avant de demander l'accès

- [ ] Préparer une description claire du projet
- [ ] Définir le volume estimé de requêtes/jour
- [ ] Confirmer l'usage non-commercial (si applicable)
- [ ] Préparer les coordonnées de l'organisation

### ✅ Après réception des clés

- [ ] Ajouter les clés dans `.env`
- [ ] Tester les connecteurs en mode réel
- [ ] Vérifier les quotas/rate limits
- [ ] Configurer le cache si nécessaire
- [ ] Monitorer les erreurs dans les logs

### ✅ Maintenance continue

- [ ] Surveiller l'expiration des tokens
- [ ] Renouveler les clés si nécessaire
- [ ] Vérifier les changements d'API
- [ ] Respecter les rate limits
- [ ] Logger sans données sensibles

---

## 9. Exemple de demande d'accès

### Email type pour Dubai Pulse / DDA

```
Objet : Demande d'accès API - Analyse de marché immobilier

Bonjour,

Je développe une plateforme d'analyse de marché immobilier pour Dubaï,
et je souhaiterais obtenir l'accès aux APIs suivantes :

- DLD Transactions (dld_transactions-open-api)
- DLD Rental Index (dld_rental_index-open-api)
- DLD Buildings (dld_buildings-open-api)

Cas d'usage :
- Analyse de tendances de marché
- Détection d'opportunités d'investissement
- Calcul de rendements locatifs
- Usage non-commercial / recherche

Volume estimé : ~1000 requêtes/jour

Je m'engage à :
- Respecter les conditions d'utilisation
- Mentionner Dubai Pulse comme source
- Protéger les données sensibles
- Ne pas redistribuer les données brutes

Merci de me communiquer les étapes pour obtenir les credentials.

Cordialement,
[Ton nom]
[Ton organisation]
[Email]
[Téléphone]
```

---

## 10. Troubleshooting

### Problème : Demande d'accès refusée

**Solution** :
- Clarifier le cas d'usage (non-commercial)
- Proposer de signer un NDA
- Mentionner l'engagement de compliance
- Demander un feedback sur le refus

### Problème : Délai trop long

**Solution** :
- Utiliser Smart Indexes en attendant (accès immédiat)
- Relancer par email après 2 semaines
- Appeler directement le support

### Problème : Coût trop élevé

**Solution** :
- Négocier un plan startup/recherche
- Proposer un partenariat (mention de la source)
- Commencer avec Smart Indexes (plus abordable)
- Utiliser mode MOCK pour développement

---

**Dernière mise à jour** : 2026-01-17  
**Version** : 1.0  
**Statut** : ✅ Guide complet prêt

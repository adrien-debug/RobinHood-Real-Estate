# Sources de données

## Stack data optimal pour détecter les deals

### Hiérarchie des sources (par ordre de priorité)

1. **DLD Transactions** (Dubai Pulse) = La vérité terrain ✅
2. **DLD Rental Index API** = Rendement & pression locative ✅
3. **Bayut API** = Offre live (lead indicators) 🆕
4. **Makani + GeoHub** = Matching + scoring localisation 🆕
5. **DDA Zoning/Planning** = Signaux en avance 🆕

---

## 1. DLD Transactions (PRIORITÉ ABSOLUE) ✅

**Source** : Dubai Land Department - Transactions immobilières via Dubai Pulse

**Fréquence** : Quotidienne (temps réel)

**Statut** : ✅ **Connecté**

**Données** :
- ID transaction
- Date
- Type (vente, hypothèque, donation)
- Localisation (community, project, building, unit)
- Type de propriété (apartment, villa, townhouse)
- Nombre de chambres
- Surface (sqft)
- Prix (AED)
- Acheteur / Vendeur
- Offplan (oui/non)

**API** :
```
Endpoint : https://api.dubaipulse.gov.ae/open/dld/dld_transactions-open-api
Auth : OAuth 2.0 (client_credentials)
```

**Utilisation** :
- ✅ Calcul des baselines marché
- ✅ Détection d'opportunités
- ✅ Analyse de régimes
- ✅ Volume de transactions

**Fichier** : `connectors/dld_transactions.py`

---

## 2. DLD Rental Index ✅

**Source** : Dubai Land Department - Index locatif via Dubai Pulse

**Fréquence** : Mensuelle

**Statut** : 🔄 Structure existante, à activer avec clés API

**Données** :
- Période
- Localisation (community, project)
- Type de propriété
- Nombre de chambres
- Loyer moyen (AED)
- Loyer médian (AED)
- Nombre de contrats

**API** :
```
Endpoint : https://api.dubaipulse.gov.ae/open/dld/rental-index
Auth : OAuth 2.0 (client_credentials)
```

**Utilisation** :
- Calcul de rendement locatif
- Stratégie RENT
- Tension locative
- Pression sur le marché

**Fichier** : `connectors/dld_rental_index.py`

---

## 3. Bayut API (Lead Indicators) 🆕

**Source** : Bayut - Plus grand portail immobilier de Dubaï

**Fréquence** : Quotidienne (temps réel)

**Statut** : 🆕 **Nouveau connecteur créé**

**Données** :
- ID annonce
- Date de publication
- Localisation (community, project, building)
- Type de propriété
- Surface (sqft)
- Prix demandé (AED)
- Prix original (AED)
- Nombre de changements de prix
- Jours sur le marché
- Statut (active, vendue, retirée)

**API** :
```
Endpoint : https://api.bayut.com/v1/properties
Auth : Bearer token
Accès : https://www.bayut.com/partnerships
```

**Utilisation (Lead Indicators)** :
- ⚡ **Nouvelles annonces** = Offre fraîche
- ⚡ **Baisses de prix** = Signaux de pression vendeur
- ⚡ **Jours sur marché** = Indicateur de liquidité
- ⚡ **Ratio annonces/transactions** = Détection de sur-offre

**⚠️ Règle anti-faux signaux** :
- Transactions ≠ Listings
- Les "bons coups" se confirment sur DLD closings, pas sur annonces
- Bayut = indicateur avancé, DLD = vérité terrain

**Fichier** : `connectors/bayut_api.py`

---

## 4. Makani Geocoding (Matching & Localisation) 🆕

**Source** : Dubai Municipality - Système d'adressage officiel

**Fréquence** : On-demand (cache)

**Statut** : 🆕 **Nouveau connecteur créé**

**Données** :
- Numéro Makani (10 chiffres unique)
- Localisation normalisée (community, project, building)
- Coordonnées GPS (lat/lon)
- Points d'intérêt :
  - Station de métro (nom + distance)
  - Plage (distance)
  - Mall (distance)

**API** :
```
Endpoint : https://api.dubaipulse.gov.ae/makani
Auth : Bearer token
Accès : https://geohub.dubaipulse.gov.ae
```

**Utilisation** :
- ✅ **Matching précis** entre transactions/annonces/buildings
- ✅ **Normalisation** des adresses (même projet = variantes de noms)
- ✅ **Scoring localisation** (proximité métro, plage, mall)
- ✅ **Géolocalisation** exacte

**Scoring localisation** :
- Métro < 500m = 100 points
- Plage < 1000m = 100 points
- Mall < 500m = 100 points

**Fichier** : `connectors/makani_geocoding.py`

---

## 5. DDA Planning & Zoning (Signaux en avance) 🆕

**Source** : Dubai Development Authority - Permis & zonage

**Fréquence** : Hebdomadaire

**Statut** : 🆕 **Nouveau connecteur créé**

**Données** :

### Permis de construire :
- ID permis
- Date d'émission
- Type (nouvelle construction, rénovation)
- Localisation (community, project)
- Développeur
- Nombre d'unités (total, résidentiel, commercial)
- Date de livraison prévue
- Surface totale (sqm)

### Changements de zonage :
- ID changement
- Date effective
- Localisation (community, zone)
- Ancien zonage → Nouveau zonage
- Raison
- Impact

**API** :
```
Endpoint : https://api.dm.gov.ae/v1
Auth : Bearer token
Accès : https://www.dm.gov.ae/open-data
```

**Utilisation (Signaux en avance)** :
- 🔮 **Nouveaux permis** = Supply future (pénalité LONG_TERM)
- 🔮 **Changements de zonage** = Opportunités avant le marché
- 🔮 **Projets d'infrastructure** = Appréciation future
- 🔮 **Zones de développement prioritaire** = Signaux bullish

**Calcul de pression supply** :
- < 200 unités/an = Pression faible (20)
- 200-500 unités/an = Pression moyenne (50)
- 500-1000 unités/an = Pression élevée (75)
- > 1000 unités/an = Pression critique (95)

**Fichier** : `connectors/dda_planning.py`

---

## 6. Developers Pipeline (EDGE DATA)

**Source** : API développeurs / Partenaires

**Fréquence** : Hebdomadaire

**Données** :
- Nom du projet
- Développeur
- Localisation
- Nombre d'unités total
- Répartition par type
- Date de lancement
- Date de livraison prévue
- Date de livraison réelle
- Statut (planifié, en construction, livré)
- % d'avancement

**Utilisation** :
- Analyse de supply future
- Risque de sur-offre
- Pénalité dans scoring LONG_TERM

**Fichier** : `connectors/developers_pipeline.py`

---

## Hiérarchie des données

**LA SEULE VÉRITÉ = DLD TRANSACTIONS**

Les annonces servent uniquement à :
- Mesurer l'offre
- Détecter des baisses de prix
- Comparer avec le marché réel

En cas de conflit entre annonce et transaction DLD → **DLD gagne toujours**.

---

## Normalisation

### Localisation

Hiérarchie :
```
Community (ex: Dubai Marina)
  └── Project (ex: Marina Heights)
      └── Building (ex: Tower A)
          └── Unit (ex: 1205)
```

### Chambres

Buckets standardisés :
- `studio` : 0 chambre
- `1BR` : 1 chambre
- `2BR` : 2 chambres
- `3BR+` : 3 chambres ou plus

### Prix

- Toujours en **AED**
- Calculer systématiquement **prix/sqft**
- Filtrer les valeurs aberrantes (< 500 AED/sqft ou > 10,000 AED/sqft)

---

## Qualité des données

### Validation

- Vérifier la présence des champs obligatoires
- Filtrer les prix = 0 ou NULL
- Normaliser les noms de lieux (trim, casse)
- Détecter les doublons (transaction_id)

### Logs

- Logger toutes les erreurs de parsing
- Compter les données rejetées
- Alerter si taux de rejet > 10%

---

## Fréquence de refresh

| Source | Fréquence | Priorité |
|--------|-----------|----------|
| DLD Transactions | Quotidienne | 1 |
| DLD Mortgages | Quotidienne | 2 |
| DLD Rental Index | Mensuelle | 3 |
| Developers Pipeline | Hebdomadaire | 4 |
| Listings | Quotidienne | 5 |

---

## Contacts API

- **DLD** : [api.dubailand.gov.ae](https://api.dubailand.gov.ae)
- **Developers** : À configurer selon partenaire
- **Listings** : À configurer selon partenaire autorisé

---

**Dernière mise à jour** : 2026-01-16

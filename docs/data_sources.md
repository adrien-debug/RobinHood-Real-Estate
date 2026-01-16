# Sources de données

## Priorité des sources

### 1. DLD Transactions (PRIORITÉ ABSOLUE)

**Source** : Dubai Land Department - Transactions immobilières

**Fréquence** : Quotidienne (temps réel)

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
Endpoint : https://api.dubailand.gov.ae/v1/transactions
Auth : Bearer token
```

**Utilisation** :
- Calcul des baselines marché
- Détection d'opportunités
- Analyse de régimes
- Volume de transactions

---

### 2. DLD Mortgages

**Source** : Dubai Land Department - Hypothèques

**Fréquence** : Quotidienne

**Données** :
- ID hypothèque
- Date
- Localisation
- Montant (AED)
- Prêteur
- Emprunteur

**Utilisation** :
- Indicateur de financement
- Analyse de la demande
- Corrélation avec prix

---

### 3. DLD Rental Index

**Source** : Dubai Land Department - Index locatif

**Fréquence** : Mensuelle

**Données** :
- Période
- Localisation
- Type de propriété
- Nombre de chambres
- Loyer moyen (AED)
- Loyer médian (AED)
- Nombre de contrats

**Utilisation** :
- Calcul de rendement locatif
- Stratégie RENT
- Tension locative

---

### 4. Developers Pipeline (EDGE DATA)

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

---

### 5. Listings (API AUTORISÉE UNIQUEMENT)

**Source** : API partenaire autorisée (Property Finder, Bayut, etc.)

**Fréquence** : Quotidienne

**Données** :
- ID annonce
- Date de publication
- Localisation
- Type de propriété
- Surface
- Prix demandé
- Prix original
- Nombre de changements de prix
- Jours sur le marché
- Statut (active, vendue, retirée)

**Utilisation** :
- Mesure de l'offre
- Détection de baisses de prix
- Comparaison annonce vs marché réel
- Indicateur de liquidité

⚠️ **IMPORTANT** : Utiliser UNIQUEMENT des APIs autorisées. Aucun scraping sauvage.

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

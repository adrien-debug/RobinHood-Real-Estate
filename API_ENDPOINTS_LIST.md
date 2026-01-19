# Liste complète des APIs et Endpoints

**Date**: 2026-01-18  
**Version**: 2.5.0

---

## Tableau récapitulatif

| API | Méthode | Endpoint | Description | Paramètres | Source de données |
|-----|---------|----------|-------------|------------|-------------------|
| **Dashboard** | GET | `/api/dashboard` | KPIs principaux, top opportunités, régimes | `date` (optional) | `dld_transactions`, `dld_opportunities`, `dld_market_regimes`, `dld_daily_briefs` |
| **Zones** | GET | `/api/zones` | Liste des zones avec prix, volume, volatilité | `community` (optional) | `dld_transactions` (90j), `dld_market_baselines`, `dld_market_regimes` |
| **Opportunities** | GET | `/api/opportunities` | Opportunités d'investissement scorées | `limit`, `strategy`, `min_score`, `regime` | `dld_opportunities` |
| **Transactions** | GET | `/api/transactions` | Liste des transactions récentes | `limit`, `date`, `community`, `rooms`, `min_price` | `dld_transactions` |
| **Transactions** | POST | `/api/transactions` | Données historiques et agrégées | `action`, `days`, `communities` | `dld_transactions` |
| **Alerts** | GET | `/api/alerts` | Alertes marché et opportunités | `type`, `limit` | `dld_opportunities` (généré) |
| **Yield** | GET | `/api/yield` | Rendements locatifs par zone | - | `dld_rental_index`, `dld_transactions` |
| **Floorplans** | GET | `/api/floorplans` | Plans 2D/3D des propriétés | `locationId`, `projectId` | Fichiers statiques |
| **Sync** | GET | `/api/sync` | Statut de synchronisation | - | Metadata |
| **Sync** | POST | `/api/sync` | Déclencher synchronisation | `source` | Pipeline |
| **Load Data** | GET | `/api/load-data` | Statut du chargement | - | Metadata |
| **Load Data** | POST | `/api/load-data` | Charger données (CSV, rental) | `action`, `data` | CSV, JSON |
| **Chat** | POST | `/api/chat` | Q&A IA sur les données marché | `question` | `dld_transactions`, `dld_opportunities`, `dld_rental_index` |

---

## Détails par API

### 1. `/api/dashboard` (GET)

**Description**: KPIs principaux du marché immobilier

**Paramètres**:
- `date` (optional): Date cible (format YYYY-MM-DD)

**Réponse**:
```json
{
  "kpis": {
    "transactions_last_day": 67,
    "transactions_7d": 230,
    "transactions_30d": 430,
    "volume_30d": 1391769973.78,
    "median_price_sqft": 1738.88,
    "avg_price_sqft": 2046.69,
    "variation_7d_pct": 0,
    "avg_opportunity_score": 83.6
  },
  "top_neighborhoods": [...],
  "property_types": {...},
  "top_opportunities": [...],
  "regimes": [...],
  "brief": {...}
}
```

---

### 2. `/api/zones` (GET)

**Description**: Analyse par zone géographique

**Paramètres**:
- `community` (optional): Filtrer par communauté

**Réponse**:
```json
{
  "zones": [
    {
      "community": "Palm Jumeirah",
      "avg_price_sqft": 4795.30,
      "transaction_count": 9,
      "volatility": 0.15
    }
  ],
  "zone_detail": {
    "baselines": [...],
    "regime": {...},
    "price_history": [...]
  }
}
```

---

### 3. `/api/opportunities` (GET)

**Description**: Opportunités d'investissement scorées

**Paramètres**:
- `limit` (default: 50): Nombre max de résultats
- `strategy` (optional): FLIP, RENT, LONG
- `min_score` (optional): Score minimum (0-100)
- `regime` (optional): Filtrer par régime de marché

**Réponse**:
```json
{
  "opportunities": [
    {
      "community": "Sports City",
      "rooms_bucket": "1BR",
      "global_score": 88,
      "discount_pct": 23,
      "recommended_strategy": "RENT"
    }
  ],
  "stats": {
    "total": 5,
    "by_strategy": { "FLIP": 2, "RENT": 3 },
    "avg_score": 83.6,
    "avg_discount": 22.5
  }
}
```

---

### 4. `/api/transactions` (GET)

**Description**: Transactions récentes

**Paramètres**:
- `limit` (default: 100): Nombre de transactions
- `date` (optional): Date de référence
- `community` (optional): Filtrer par communauté
- `rooms` (optional): Filtrer par nombre de chambres
- `min_price` (optional): Prix minimum

**Réponse**:
```json
{
  "transactions": [...],
  "total": 430,
  "stats": {
    "total_volume": 1391769973.78,
    "avg_price_sqft": 2046.69,
    "below_market_pct": 15.2
  }
}
```

---

### 5. `/api/transactions` (POST)

**Description**: Données historiques et agrégées

**Body**:
```json
{
  "action": "get_historical",
  "days": 90,
  "communities": ["Dubai Marina", "JVC"]
}
```

**Actions disponibles**:
- `get_historical`: Données hebdomadaires agrégées
- `get_communities`: Liste des communautés

**Réponse**:
```json
{
  "historical": [
    {
      "week": "2025-12-14",
      "avg_price": 2081.17,
      "volume": 200
    }
  ],
  "communities": [...]
}
```

---

### 6. `/api/alerts` (GET)

**Description**: Alertes marché en temps réel

**Paramètres**:
- `type` (optional): OPPORTUNITY, REGIME_CHANGE, PRICE_DROP
- `limit` (default: 50): Nombre d'alertes

**Réponse**:
```json
{
  "alerts": [
    {
      "alert_type": "OPPORTUNITY",
      "community": "JVC",
      "message": "Detected RENTAL opportunity with 22.5% discount",
      "severity": "high",
      "created_at": "2026-01-18T..."
    }
  ]
}
```

---

### 7. `/api/yield` (GET)

**Description**: Rendements locatifs par zone

**Réponse**:
```json
{
  "zones": [
    {
      "community": "Dubai Silicon Oasis",
      "avg_price_sqft": 873,
      "gross_yield": 12.32,
      "annual_rent": 59148,
      "monthly_rent": 4929,
      "transaction_count": 1,
      "rent_data_available": true,
      "data_source": "real"
    }
  ],
  "summary": {
    "avg_yield": 5.9,
    "max_yield": 12.32,
    "min_yield": 1.04,
    "zones_with_real_data": 19,
    "zones_with_estimated_data": 69,
    "total_zones": 88
  },
  "metadata": {
    "rental_records": 100,
    "transaction_records": 825,
    "calculation_date": "2026-01-18T..."
  }
}
```

---

### 8. `/api/floorplans` (GET)

**Description**: Plans 2D/3D des propriétés

**Paramètres**:
- `locationId` (optional): ID de la localisation
- `projectId` (optional): ID du projet

**Réponse**:
```json
{
  "floorplans": [
    {
      "id": "fp_001",
      "type": "2D",
      "url": "/floorplans/...",
      "rooms": "2BR"
    }
  ]
}
```

---

### 9. `/api/sync` (GET)

**Description**: Statut de la synchronisation des données

**Réponse**:
```json
{
  "last_sync": "2026-01-18T14:30:00Z",
  "status": "completed",
  "sources": {
    "dld_transactions": { "count": 2430, "last_update": "..." },
    "dld_opportunities": { "count": 5, "last_update": "..." }
  }
}
```

---

### 10. `/api/sync` (POST)

**Description**: Déclencher une synchronisation manuelle

**Body**:
```json
{
  "source": "dld_transactions"
}
```

**Réponse**:
```json
{
  "success": true,
  "message": "Sync started",
  "job_id": "sync_123"
}
```

---

### 11. `/api/load-data` (GET)

**Description**: Statut du chargement de données

**Réponse**:
```json
{
  "status": "ready",
  "available_actions": ["load_transactions", "load_rental_data"]
}
```

---

### 12. `/api/load-data` (POST)

**Description**: Charger des données (CSV, rental)

**Actions disponibles**:

#### Action: `load_transactions`
Charge les transactions depuis CSV

**Body**:
```json
{
  "action": "load_transactions"
}
```

#### Action: `load_rental_data`
Charge les données de loyers

**Body**:
```json
{
  "action": "load_rental_data",
  "data": [
    {
      "period_date": "2025-12-01",
      "community": "Dubai Marina",
      "property_type": "Apartment",
      "rooms_bucket": "1BR",
      "avg_rent_aed": 104000,
      "median_rent_aed": 102000,
      "rent_count": 45
    }
  ]
}
```

**Réponse**:
```json
{
  "success": true,
  "totalRecords": 100,
  "inserted": 100,
  "errors": 0
}
```

---

## Tables Supabase utilisées

| Table | Description | Records |
|-------|-------------|---------|
| `dld_transactions` | Transactions immobilières DLD | 2,430 |
| `dld_opportunities` | Opportunités scorées | 5 |
| `dld_rental_index` | Index locatif (loyers) | 100 |
| `dld_market_baselines` | Baselines par zone | ? |
| `dld_market_regimes` | Régimes de marché | ? |
| `dld_daily_briefs` | Briefs CIO quotidiens | ? |
| `developers_pipeline` | Pipeline développeurs | 0 |
| `listings` | Annonces actives | 0 |

---

## Statut des APIs

| API | Status | Data Quality | Notes |
|-----|--------|--------------|-------|
| `/api/dashboard` | ✅ 200 OK | 100% réel | 430 transactions 30j |
| `/api/zones` | ✅ 200 OK | 100% réel | 88 zones |
| `/api/opportunities` | ✅ 200 OK | 100% réel | 5 opportunités (à régénérer) |
| `/api/transactions` | ✅ 200 OK | 100% réel | 2,430 records |
| `/api/alerts` | ✅ 200 OK | 100% réel | Généré depuis opportunities |
| `/api/yield` | ✅ 200 OK | Mixte | 19 zones réelles, 69 estimées |
| `/api/floorplans` | ✅ 200 OK | Fichiers statiques | - |
| `/api/sync` | ✅ 200 OK | Metadata | - |
| `/api/load-data` | ✅ 200 OK | Admin | - |

---

## Prochaines améliorations

1. **Régénérer opportunities** : Passer de 5 à 100+ deals
2. **Charger developers_pipeline** : Supply analysis
3. **Charger listings** : Asking prices vs sales
4. **Ajouter plus de rental data** : Passer de 100 à 1000+ records
5. **Créer `/api/supply`** : Analyse supply/demand
6. **Créer `/api/liquidity`** : Days on market, price reductions

---

**Dernière mise à jour** : 2026-01-18  
**Serveur** : http://localhost:3000  
**Refresh rate** : 5 secondes (live pages)

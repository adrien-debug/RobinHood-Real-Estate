# INVENTAIRE COMPLET - DONNÉES MARCHÉ IMMOBILIER DUBAI

**Date** : 2026-01-18  
**Version** : 2.1.0  
**Projet** : Robin Real Estate Intelligence

---

## 1. APIS PRÉSENTES DANS LE REPO

### Tableau récapitulatif

| API | Connecteur | Status | Mode | Données clés | Env var requise |
|-----|-----------|--------|------|--------------|-----------------|
| **Bayut RapidAPI** | `connectors/bayut_api.py` | LIVE | Real | 200 tx DLD, 25+ listings, projects off-plan, agents, agences, promoteurs, amenities, floorplans | `BAYUT_API_KEY` |
| **Dubai Pulse (DLD)** | `connectors/dld_transactions.py` + `connectors/dubai_pulse_auth.py` | PARTIEL | OAuth | Transactions, rental index | `DLD_API_KEY`, `DLD_API_SECRET` |
| **DLD Rental Index** | `connectors/dld_rental_index.py` | MOCK | OAuth | Loyers moyens/médians par zone/rooms | `DLD_API_SECRET` manquant |
| **Makani Geocoding** | `connectors/makani_geocoding.py` | MOCK | Bearer | Coords GPS, distance métro/plage/mall, numéro Makani | `MAKANI_API_KEY` |
| **DDA Planning** | `connectors/dda_planning.py` | MOCK | Bearer | Permis construire, changements zonage | `DDA_API_KEY` |
| **UAE RealTime** | `connectors/uae_realtime_api.py` | LIVE | RapidAPI | Agents directory, agences, properties | `UAE_REALTIME_API_KEY` |
| **PropertyFinder** | `connectors/propertyfinder_api.py` | NON CONF | RapidAPI | 500K+ listings UAE, agents | `PROPERTYFINDER_API_KEY` |
| **Zyla Labs** | `connectors/zylalabs_api.py` | NON CONF | Bearer | Market stats, properties, agences | `ZYLALABS_API_KEY` |
| **Developers Pipeline** | `connectors/developers_pipeline.py` | MOCK | Bearer | Supply future par projet/promoteur | `DEVELOPERS_API_KEY` |

---

## 2. ENDPOINTS BAYUT (le plus complet actuellement)

**Fichier** : `connectors/bayut_api.py`

| Endpoint | Méthode | Description | Granularité |
|----------|---------|-------------|-------------|
| `/properties_search` | POST | Recherche annonces | Communauté, type, prix, chambres |
| `/property/{id}` | GET | Détails propriété | Bâtiment, unité |
| `/transactions` | POST | Transactions DLD | Date, zone, type |
| `/locations_search` | GET | Recherche localisations | IDs zones |
| `/new_projects_search` | POST | Projets off-plan | Promoteur, zone, date complétion |
| `/agencies_by_locations` | GET | Agences par zone | Zone |
| `/agencies_by_name` | GET | Recherche agences | Nom |
| `/agency/{id}` | GET | Détails agence | Agence |
| `/developers_search` | GET | Recherche promoteurs | Nom |
| `/agents_by_name` | GET | Recherche agents | Nom |
| `/agents_by_filters` | GET | Agents filtrés | Zone, purpose |
| `/agents_in_agency/{id}` | GET | Agents d'une agence | Agence |
| `/agent/{id}` | GET | Détails agent | Agent |
| `/amenities_search` | GET | Équipements | Type |
| `/floorplans` | GET | Plans d'étage | Bâtiment |

---

## 3. KPIs CALCULÉS ET GRANULARITÉS

**Fichiers** : `pipelines/compute_kpis.py`, `sql/features_kpis.sql`

### 8 KPIs Avancés

| KPI | Formule | Utilisation |
|-----|---------|-------------|
| **TLS** (Transaction-to-Listing Spread) | `(median_listing_psf - median_tx_psf) / median_tx_psf` | Écart demande/réel |
| **LAD** (Liquidity-Adjusted Discount) | `discount_pct * log(1 + tx_count_30d)` | Discount ajusté liquidité |
| **RSG** (Rental Stress Gap) | `(median_rent - expected_rent) / expected_rent` | Tension locative |
| **SPI** (Supply Pressure Index) | `normalize(planned_units_12m / tx_count_12m)` | Pression offre 0-100 |
| **GPI** (Geo-Premium Index) | `location_score * (1 + price_premium)` | Premium localisation |
| **RCWM** (Regime Confidence-Weighted Momentum) | `momentum * regime_confidence` | Momentum pondéré |
| **ORD** (Offplan Risk Delta) | `(median_offplan_psf / median_ready_psf) - 1` | Risque off-plan |
| **APS** (Anomaly Persistence Score) | `days_anomaly_active / window_days` | Persistance anomalies |

### Granularités disponibles

| Niveau | Tables concernées | Données |
|--------|-------------------|---------|
| **City** (Dubai) | Agrégation globale | Stats macro |
| **Community** | `market_baselines`, `kpis`, `market_regimes`, `risk_summaries` | Prix, volume, régime, risque |
| **Project** | `market_baselines`, `kpis`, `market_regimes` | Prix par projet |
| **Building** | `market_baselines`, `features` | Prix par bâtiment |
| **Rooms Bucket** | Toutes tables (studio, 1BR, 2BR, 3BR+) | Segmentation typologique |

### Fenêtres temporelles

- **7 jours** : Court terme / détection rapide
- **30 jours** : Baseline standard
- **90 jours** : Tendance moyen terme

---

## 4. MÉTRIQUES MARKET BASELINES

**Fichiers** : `sql/baselines.sql`, `pipelines/compute_market_baselines.py`

| Métrique | Description |
|----------|-------------|
| `median_price_per_sqft` | Prix médian/sqft |
| `p25_price_per_sqft` | 25ème percentile |
| `p75_price_per_sqft` | 75ème percentile |
| `avg_price_per_sqft` | Moyenne |
| `transaction_count` | Volume transactions |
| `total_volume_aed` | Volume total AED |
| `momentum` | % variation vs période précédente |
| `volatility` | Écart-type / médiane |
| `dispersion` | IQR / médiane |

---

## 5. SCORING MULTI-STRATÉGIES

**Fichiers** : `pipelines/compute_scores.py`, `strategies/*.py`

| Stratégie | Poids | Critères |
|-----------|-------|----------|
| **FLIP** | 40% | Discount, liquidité, momentum, volatilité |
| **RENT** | 30% | Yield, tension locative, RSG |
| **LONG_TERM** | 30% | Régime marché, supply risk, GPI |

---

## 6. APIS EXTERNES RECOMMANDÉES (à ajouter)

| API | Type | Données | Coût | Priorité |
|-----|------|---------|------|----------|
| **Dubai Pulse dld_lkp_areas** | Open API | Hiérarchie zones officielles | Gratuit | HAUTE |
| **Dubai Pulse dld_developers** | Open API | Promoteurs enregistrés | Gratuit | HAUTE |
| **Dubai Pulse dld_valuation** | Open API | Évaluations officielles | Gratuit | MOYENNE |
| **Dubai Pulse dld_buildings** | Open API | Bâtiments enregistrés | Gratuit | HAUTE |
| **PropertyFinder Enterprise 2.0** | Partner API | 500K listings, leads | Gratuit (partenaire) | HAUTE |
| **Smart Indexes** | Commercial | Bayut + Makani + Price Indexes | ~$199/mois | MOYENNE |
| **RERA Trakheesi** | Vérification | Validation permis annonces | Via DLD | BASSE |

---

## 7. KPIs ADDITIONNELS PROPOSÉS

| KPI | Formule | Granularité | Source requise |
|-----|---------|-------------|----------------|
| **Days on Market (DOM)** | Médiane jours listing actif | Building | Bayut/PF |
| **Listing Turnover Rate** | Annonces vendues/total | Community | Bayut |
| **Price Cut Frequency** | % annonces avec baisse prix | Project | Bayut |
| **Absorption Rate** | Tx/mois ÷ stock annonces | Community | DLD + Bayut |
| **Rental Yield Actual** | Loyer annuel / prix vente | Building | DLD Rental + DLD Tx |
| **Developer Delivery Score** | % projets livrés à temps | Developer | DDA + Pipeline |
| **Metro Premium** | Δ prix < 500m métro vs > 1km | Building | Makani + DLD |
| **Beach Premium** | Δ prix waterfront vs non | Building | Makani + DLD |
| **Offplan Discount Evolution** | Δ prix off-plan vs ready YoY | Project | DLD Tx |
| **Investor Concentration** | % multi-property owners | Community | DLD (si dispo) |

---

## 8. STRUCTURE FICHIERS CLÉS

```
connectors/
├── bayut_api.py          # API principale (15+ endpoints)
├── dld_transactions.py   # Transactions DLD via Bayut ou Dubai Pulse
├── dld_rental_index.py   # Index locatif DLD
├── makani_geocoding.py   # Géocodage + scoring localisation
├── dda_planning.py       # Permis construire + zonage
├── uae_realtime_api.py   # Agents directory
├── propertyfinder_api.py # 500K listings (à configurer)
├── zylalabs_api.py       # Market stats (à configurer)
└── developers_pipeline.py # Supply future

pipelines/
├── compute_kpis.py           # 8 KPIs avancés
├── compute_market_baselines.py # Baselines 7/30/90j
├── compute_market_regimes.py   # Classification régimes
├── compute_scores.py          # Scoring multi-stratégies
├── compute_features.py        # Features normalisées
└── detect_anomalies.py        # Détection opportunités

sql/
├── schema.sql           # Tables principales
├── features_kpis.sql    # Tables features/kpis/quality_logs
├── baselines.sql        # Fonctions calcul baselines
├── regimes.sql          # Fonctions régimes marché
└── opportunities.sql    # Détection deals

core/
├── config.py    # 15+ variables env API
├── models.py    # Transaction, Listing, MakaniAddress, etc.
└── db.py        # Connexion Supabase
```

---

## 9. CONFIGURATION ACTUELLE (.env)

| Variable | Configurée | Source |
|----------|-----------|--------|
| `BAYUT_API_KEY` | OK | RapidAPI |
| `UAE_REALTIME_API_KEY` | OK | RapidAPI |
| `DLD_API_KEY` | OK | Dubai Pulse |
| `DLD_API_SECRET` | MANQUANT | Dubai Pulse |
| `PROPERTYFINDER_API_KEY` | MANQUANT | RapidAPI |
| `ZYLALABS_API_KEY` | MANQUANT | Zyla Labs |
| `MAKANI_API_KEY` | MANQUANT | GeoHub |
| `DDA_API_KEY` | MANQUANT | Dubai Municipality |

---

## 10. ACTIONS PRIORITAIRES

1. **Obtenir `DLD_API_SECRET`** sur https://www.dubaipulse.gov.ae pour activer Dubai Pulse OAuth
2. **Activer PropertyFinder API** (gratuit pour partenaires) → +500K listings
3. **Configurer Makani** pour scoring localisation réel (métro, plage, mall)
4. **Ajouter connecteur dld_buildings** pour matching bâtiments DLD
5. **Implémenter DOM (Days on Market)** depuis Bayut listings

---

## 11. DONNÉES DISPONIBLES PAR GRANULARITÉ

### Par Communauté (52 communautés actives)
- Prix médian/sqft (7j, 30j, 90j)
- Volume transactions
- Régime de marché (ACCUMULATION, EXPANSION, DISTRIBUTION, RETOURNEMENT)
- Score de risque global
- 8 KPIs avancés
- Tension locative (RSG)
- Pression supply (SPI)

### Par Projet
- Prix médian/sqft
- Momentum
- Volatilité
- Dispersion
- Régime de marché

### Par Bâtiment
- Prix médian/sqft (si données suffisantes)
- Features Makani (distance métro, plage, mall)
- Score localisation

### Par Type (Rooms Bucket)
- studio, 1BR, 2BR, 3BR+
- Tous les KPIs segmentés par type

---

**Dernière mise à jour** : 2026-01-18 14:30 UTC

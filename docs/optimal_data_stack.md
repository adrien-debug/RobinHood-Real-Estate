# Stack Data Optimal pour Détecter les Deals

## Vue d'ensemble

Ce document décrit le stack data optimal pour maximiser la détection d'opportunités immobilières à Dubaï.

**Principe fondamental** : Combiner données de closing (vérité terrain) + lead indicators (signaux avancés) + géolocalisation (scoring précis).

---

## 1. Hiérarchie des sources (par priorité)

### 🥇 Tier 1 : Vérité terrain
1. **DLD Transactions** (Dubai Pulse) ✅ Connecté
   - Closing data = prix réels payés
   - Fréquence : Quotidienne
   - Utilisation : Baselines, régimes, opportunités

### 🥈 Tier 2 : Rendement & pression
2. **DLD Rental Index API** (Dubai Pulse) 🔄 À activer
   - Loyers moyens/médians par zone
   - Fréquence : Mensuelle
   - Utilisation : Stratégie RENT, calcul de yield

### 🥉 Tier 3 : Lead indicators
3. **Bayut API** 🆕 Nouveau
   - Annonces live = signaux avancés
   - Fréquence : Quotidienne
   - Utilisation : Baisses de prix, sur-offre, liquidité

### 🎯 Tier 4 : Matching & localisation
4. **Makani + GeoHub** 🆕 Nouveau
   - Adressage officiel + géocodage
   - Fréquence : On-demand (cache)
   - Utilisation : Matching précis, scoring localisation

### 🔮 Tier 5 : Signaux en avance
5. **DDA Planning & Zoning** 🆕 Nouveau
   - Permis de construire + changements de zonage
   - Fréquence : Hebdomadaire
   - Utilisation : Supply future, opportunités avant marché

---

## 2. Anti-faux signaux

### Règle #1 : Transactions ≠ Listings

**Problème** : Confondre prix demandés (listings) et prix réels (transactions).

**Solution** :
- ✅ DLD Transactions = vérité terrain (closing data)
- ⚠️ Bayut Listings = lead indicators (prix demandés)
- Comparaison Bayut vs DLD = mesure de l'écart demande/réel

**Utilisation correcte** :
```python
# ✅ BON : Détecter signaux précoces avec Bayut
bayut_metrics = bayut_connector.calculate_listing_metrics(listings)
if bayut_metrics["pct_price_reductions"] > 40:
    # Signal de pression vendeur
    pass

# ✅ BON : Valider avec DLD
dld_transactions = dld_connector.fetch_transactions(start_date, end_date)
# Confirmer l'opportunité sur closing data

# ❌ MAUVAIS : Utiliser prix Bayut pour calcul de baseline
# baseline = calculate_baseline(bayut_listings)  # NON !
```

---

### Règle #2 : Normalisation (Makani aide)

**Problème** : Même projet peut avoir variantes de noms.

Exemples :
- "Marina Heights" vs "Marina Heights Tower" vs "MH"
- "Dubai Marina" vs "D. Marina" vs "Marina"

**Solution** : Utiliser Makani pour matching précis.

```python
# ✅ BON : Matching via Makani
makani = makani_connector.search_address(
    community="Dubai Marina",
    project="Marina Heights",
    building="Tower A"
)
# makani.makani_number = "1234567890" (unique)

# Join transactions/listings via Makani number
transactions_with_makani = enrich_with_makani(transactions)
listings_with_makani = enrich_with_makani(listings)

# Match précis
matched = match_by_makani(transactions_with_makani, listings_with_makani)
```

**Bénéfices** :
- Évite les faux doublons
- Évite les données manquées
- Permet le scoring de localisation

---

### Règle #3 : Compliance & Responsabilité

⚠️ **Dubai Municipality rappelle** : L'usage des données implique conditions + responsabilité côté utilisateur.

**Règles strictes** :
- ✅ Utiliser UNIQUEMENT des APIs officielles autorisées
- ❌ AUCUN scraping non autorisé
- ✅ Respecter les rate limits
- ✅ Cacher les tokens d'accès (`.env`, jamais en dur)
- ✅ Logger sans données sensibles

**APIs officielles** :
- Dubai Pulse : https://www.dubaipulse.gov.ae
- Bayut Partnerships : https://www.bayut.com/partnerships
- Dubai Municipality : https://www.dm.gov.ae/open-data

---

## 3. Cas d'usage par source

### DLD Transactions (Vérité terrain)

**Quand l'utiliser** :
- Calcul de baselines marché (médiane prix/sqft)
- Détection d'opportunités (discount vs marché)
- Analyse de régimes (ACCUMULATION, EXPANSION, etc.)
- Volume de transactions (liquidité)

**Exemple** :
```python
# Récupérer transactions des 30 derniers jours
transactions = dld_connector.fetch_transactions(
    start_date=date.today() - timedelta(days=30),
    end_date=date.today()
)

# Calculer baseline pour Dubai Marina, 2BR
baseline = calculate_baseline(
    transactions,
    community="Dubai Marina",
    rooms_bucket="2BR",
    window_days=30
)

# Détecter opportunités (discount > 10%)
opportunities = detect_opportunities(transactions, baseline)
```

---

### DLD Rental Index (Rendement)

**Quand l'utiliser** :
- Calcul de rendement locatif (yield)
- Stratégie RENT
- Détection de pression locative
- Comparaison loyer vs prix d'achat

**Exemple** :
```python
# Récupérer index locatif du mois
rental_index = dld_rental_connector.fetch_rental_index(
    period_date=date.today().replace(day=1)
)

# Calculer yield pour une transaction
transaction_price = 1_500_000  # AED
avg_rent = rental_index.get_rent(community="Dubai Marina", rooms="2BR")
# avg_rent = 95_000 AED/an

yield_pct = (avg_rent / transaction_price) * 100
# yield_pct = 6.3%

# Scoring RENT
if yield_pct > 7:
    rent_score = 90  # Excellent
elif yield_pct > 5:
    rent_score = 70  # Bon
else:
    rent_score = 40  # Faible
```

---

### Bayut API (Lead indicators)

**Quand l'utiliser** :
- Détecter nouvelles annonces (offre fraîche)
- Détecter baisses de prix (pression vendeur)
- Mesurer jours sur marché (liquidité)
- Calculer ratio annonces/transactions (sur-offre)

**Exemple** :
```python
# Récupérer annonces des 7 derniers jours
listings = bayut_connector.fetch_listings(
    community="Dubai Marina",
    days_back=7
)

# Calculer métriques
metrics = bayut_connector.calculate_listing_metrics(listings)

# Signaux
if metrics["pct_price_reductions"] > 40:
    print("⚠️  Pression vendeur élevée")

if metrics["avg_days_on_market"] > 90:
    print("⚠️  Liquidité faible")

if metrics["new_listings_7d"] > 50:
    print("⚠️  Sur-offre potentielle")

# Comparaison avec DLD
dld_transactions = dld_connector.fetch_transactions(days_back=7)
ratio_listings_transactions = len(listings) / len(dld_transactions)

if ratio_listings_transactions > 5:
    print("⚠️  Sur-offre confirmée (5x plus d'annonces que de ventes)")
```

---

### Makani Geocoding (Matching & localisation)

**Quand l'utiliser** :
- Matching précis entre transactions/annonces/buildings
- Normalisation des adresses
- Scoring de localisation (proximité métro, plage, mall)
- Géolocalisation exacte (lat/lon)

**Exemple** :
```python
# Recherche d'adresse
makani = makani_connector.search_address(
    community="Dubai Marina",
    project="Marina Heights",
    building="Tower A"
)

# Enrichir transaction avec Makani
transaction.makani_number = makani.makani_number
transaction.latitude = makani.latitude
transaction.longitude = makani.longitude

# Scoring de localisation
location_score = makani_connector.calculate_location_score(makani)
# location_score = 85 (excellent)

# Détails
# - Métro : 450m (100 points)
# - Plage : 900m (100 points)
# - Mall : 350m (100 points)

# Ajuster score opportunité
opportunity.location_score = location_score
opportunity.global_score += location_score * 0.15  # 15% de poids
```

---

### DDA Planning & Zoning (Signaux en avance)

**Quand l'utiliser** :
- Détecter supply future (nouveaux permis)
- Anticiper changements de zonage
- Identifier zones de développement prioritaire
- Pénaliser zones avec sur-offre future

**Exemple** :
```python
# Récupérer permis de construire des 90 derniers jours
permits = dda_connector.fetch_building_permits(
    start_date=date.today() - timedelta(days=90),
    end_date=date.today()
)

# Calculer pression supply pour Dubai Marina
supply_pressure = dda_connector.calculate_supply_pressure(
    permits,
    community="Dubai Marina"
)

# supply_pressure = {
#     "total_new_units": 1250,
#     "completion_next_12m": 450,
#     "completion_next_24m": 800,
#     "supply_pressure_score": 65  # Pression moyenne-élevée
# }

# Ajuster score LONG_TERM
if supply_pressure["supply_pressure_score"] > 70:
    long_term_score -= 20  # Pénalité pour sur-offre future

# Récupérer changements de zonage
zoning_changes = dda_connector.fetch_zoning_changes(
    start_date=date.today() - timedelta(days=180)
)

# Détecter opportunités avant le marché
for change in zoning_changes:
    if change.new_zoning == "mixed_use" and change.old_zoning == "residential":
        print(f"🔮 Opportunité : {change.community} passe en mixed-use")
        # Anticiper appréciation future
```

---

## 4. Workflow complet

### Pipeline quotidien

```python
# 1. Ingestion DLD Transactions (vérité terrain)
transactions = dld_connector.fetch_transactions(days_back=1)

# 2. Enrichissement Makani (matching & localisation)
transactions_enriched = []
for t in transactions:
    makani = makani_connector.search_address(t.community, t.project, t.building)
    if makani:
        t.makani_number = makani.makani_number
        t.location_score = makani_connector.calculate_location_score(makani)
    transactions_enriched.append(t)

# 3. Calcul baselines marché
baselines = calculate_baselines(transactions_enriched, windows=[7, 30, 90])

# 4. Détection régimes
regimes = detect_regimes(baselines)

# 5. Détection opportunités
opportunities = detect_opportunities(transactions_enriched, baselines, regimes)

# 6. Enrichissement Bayut (lead indicators)
for opp in opportunities:
    listings = bayut_connector.fetch_listings(
        community=opp.community,
        property_type=opp.property_type
    )
    metrics = bayut_connector.calculate_listing_metrics(listings)
    
    # Ajuster score selon signaux Bayut
    if metrics["pct_price_reductions"] > 40:
        opp.flip_score += 10  # Pression vendeur = opportunité FLIP
    
    if metrics["avg_days_on_market"] > 90:
        opp.liquidity_score -= 20  # Liquidité faible

# 7. Enrichissement DDA (signaux en avance)
permits = dda_connector.fetch_building_permits(days_back=90)
for opp in opportunities:
    supply = dda_connector.calculate_supply_pressure(permits, opp.community)
    opp.supply_risk = "high" if supply["supply_pressure_score"] > 70 else "medium"
    
    if opp.supply_risk == "high":
        opp.long_term_score -= 20  # Pénalité LONG_TERM

# 8. Enrichissement Rental Index (rendement)
rental_index = dld_rental_connector.fetch_rental_index()
for opp in opportunities:
    rent = rental_index.get_rent(opp.community, opp.rooms_bucket)
    if rent and opp.price_aed:
        yield_pct = (rent / opp.price_aed) * 100
        opp.yield_pct = yield_pct
        
        # Ajuster score RENT
        if yield_pct > 7:
            opp.rent_score += 20

# 9. Scoring final & recommandation
for opp in opportunities:
    opp.global_score = calculate_global_score(
        opp.flip_score,
        opp.rent_score,
        opp.long_term_score
    )
    opp.recommended_strategy = get_best_strategy(opp)

# 10. Sauvegarde
save_opportunities(opportunities)
```

---

## 5. Métriques clés par source

### DLD Transactions
- Volume de transactions (liquidité)
- Médiane prix/sqft (baseline)
- Momentum (variation vs période précédente)
- Volatilité (écart-type / médiane)
- Dispersion (IQR / médiane)

### DLD Rental Index
- Loyer moyen/médian (AED/an)
- Yield (loyer / prix d'achat)
- Nombre de contrats (activité locative)

### Bayut Listings
- Nouvelles annonces (7j)
- % baisses de prix
- Réduction moyenne (%)
- Jours sur marché (moyenne)
- Ratio listings/transactions

### Makani
- Score de localisation (0-100)
- Distance métro (m)
- Distance plage (m)
- Distance mall (m)

### DDA Planning
- Nouvelles unités (12m/24m)
- Score de pression supply (0-100)
- Changements de zonage

---

## 6. Fichiers créés/modifiés

### Nouveaux connecteurs
- ✅ `connectors/bayut_api.py`
- ✅ `connectors/makani_geocoding.py`
- ✅ `connectors/dda_planning.py`

### Connecteurs mis à jour
- ✅ `connectors/dld_rental_index.py` (Dubai Pulse)

### Modèles
- ✅ `core/models.py` (ajout Listing, MakaniAddress, PlanningPermit, ZoningChange)

### Configuration
- ✅ `core/config.py` (ajout variables env)
- ✅ `env.example` (ajout clés API)

### Documentation
- ✅ `docs/data_sources.md` (mise à jour complète)
- ✅ `docs/optimal_data_stack.md` (ce document)
- ✅ `README.md` (mise à jour stack data)

---

## 7. Prochaines étapes

### Phase 1 : Activation (Immédiat)
1. Obtenir clés API Bayut : https://www.bayut.com/partnerships
2. Obtenir clés API Makani : https://geohub.dubaipulse.gov.ae
3. Obtenir clés API DDA : https://www.dm.gov.ae/open-data
4. Configurer `.env` avec les nouvelles clés
5. Tester les connecteurs en mode MOCK
6. Activer les APIs réelles

### Phase 2 : Intégration (Court terme)
1. Enrichir pipeline avec Makani (matching)
2. Intégrer Bayut dans scoring (lead indicators)
3. Intégrer DDA dans scoring (supply pressure)
4. Ajouter métriques Bayut au dashboard
5. Ajouter scoring localisation aux opportunités

### Phase 3 : Optimisation (Moyen terme)
1. Cache intelligent Makani (éviter appels répétés)
2. Batch processing pour Makani
3. Alertes sur changements de zonage DDA
4. Corrélation Bayut vs DLD (écart demande/réel)
5. Backtesting avec données historiques

---

## 8. Contacts & ressources

### APIs officielles
- **Dubai Pulse (DLD)** : https://www.dubaipulse.gov.ae
- **Bayut Partnerships** : https://www.bayut.com/partnerships
- **Makani (GeoHub)** : https://geohub.dubaipulse.gov.ae
- **Dubai Municipality (DDA)** : https://www.dm.gov.ae/open-data

### Documentation
- Dubai Pulse API Docs : https://www.dubaipulse.gov.ae/api-docs
- Makani System : https://makani.ae
- Dubai Municipality Open Data : https://www.dm.gov.ae/open-data

---

**Dernière mise à jour** : 2026-01-17  
**Version** : 1.2.0  
**Statut** : ✅ Connecteurs créés, prêts à activer

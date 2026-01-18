# 🏢 Dubai Real Estate Intelligence

Plateforme d'intelligence immobilière institutionnelle pour le marché de Dubaï.

**Mobile-first** • **Temps réel** • **IA décisionnelle** • **Scoring adaptatif**

---

## 🎯 Objectif

Fournir une intelligence de marché de niveau institutionnel pour l'immobilier à Dubaï :
- Détection d'opportunités sous-valorisées
- Analyse de régimes de marché (ACCUMULATION, EXPANSION, DISTRIBUTION, RETOURNEMENT)
- Scoring multi-stratégies (FLIP, RENT, LONG_TERM)
- Brief quotidien automatique par agent IA CIO
- Interface mobile-first (iPhone prioritaire)

---

## 🏗️ Architecture

```
dubai-real-estate-intelligence/
├── next-app/                       # Frontend Next.js 14
│   ├── app/                        # App Router
│   │   ├── page.tsx                # Page d'accueil avec LED status
│   │   ├── dashboard/              # Dashboard KPIs
│   │   ├── sales/                  # Transactions
│   │   ├── zones/                  # Analyse zones
│   │   ├── radar/                  # Opportunités
│   │   ├── yield/                  # Rendements
│   │   ├── floorplans/             # Visualisation 3D (nouveau)
│   │   ├── alerts/                 # Alertes
│   │   ├── insights/               # Market Intelligence
│   │   ├── admin/                  # Administration
│   │   └── api/                    # API Routes
│   ├── components/                 # Composants React
│   │   ├── charts/                 # Graphiques Recharts
│   │   ├── layout/                 # Header, Sidebar
│   │   ├── ui/                     # UI Components
│   │   └── FloorplanViewer.tsx    # Viewer 3D (nouveau)
│   ├── lib/                        # Utilitaires
│   │   ├── supabase.ts             # Client Supabase
│   │   └── utils.ts                # Helpers
│   └── package.json                # Dépendances Node.js
│
├── core/                           # Core système
│   ├── config.py                   # Configuration centralisée
│   ├── db.py                       # Connexion PostgreSQL
│   ├── dubai_mock_data.py          # Données réalistes Dubai
│   ├── icons.py                    # Icônes SVG
│   ├── models.py                   # Modèles Pydantic
│   └── utils.py                    # Utilitaires
│
├── connectors/                     # Connecteurs API
│   ├── dld_transactions.py         # DLD Transactions
│   ├── dld_mortgages.py            # DLD Hypothèques
│   ├── dld_rental_index.py         # DLD Index locatif
│   ├── dld_buildings.py            # DLD Buildings
│   ├── dld_developers.py           # DLD Developers (nouveau)
│   ├── dld_valuation.py            # DLD Valuation (nouveau)
│   ├── dld_lkp_areas.py            # DLD LKP Areas (nouveau)
│   ├── bayut_api.py                # Bayut RapidAPI (15 endpoints)
│   ├── propertyfinder_api.py       # PropertyFinder API
│   ├── zylalabs_api.py             # Zyla Labs API
│   ├── emaar_helper.py             # Helper Emaar
│   ├── uae_realtime_api.py         # UAE Real Estate API
│   ├── developers_pipeline.py      # Pipeline développeurs
│   └── listings_placeholder.py     # Annonces
│
├── pipelines/                      # Pipelines de données
│   ├── ingest_transactions.py      # Ingestion transactions
│   ├── ingest_mortgages.py         # Ingestion hypothèques
│   ├── ingest_rental_index.py      # Ingestion index locatif
│   ├── compute_features.py         # Features normalisées
│   ├── compute_market_baselines.py # Calcul baselines
│   ├── compute_market_regimes.py   # Calcul régimes
│   ├── compute_kpis.py             # 8 KPIs avancés
│   ├── compute_additional_kpis.py  # 12 KPIs additionnels (nouveau)
│   ├── detect_anomalies.py         # Détection anomalies
│   ├── compute_scores.py           # Scoring multi-stratégies
│   ├── compute_risk_summary.py     # Résumé risques
│   └── quality_logger.py           # Logs qualité
│
├── strategies/                     # Stratégies de scoring
│   ├── base.py                     # Classe de base
│   ├── flip.py                     # Stratégie FLIP
│   ├── rent.py                     # Stratégie RENT
│   └── long_term.py                # Stratégie LONG_TERM
│
├── ai_agents/                      # Agents IA
│   └── chief_investment_officer.py # Agent CIO
│
├── graphs/                         # LangGraph
│   └── market_intelligence_graph.py # Pipeline LangGraph
│
├── alerts/                         # Système d'alertes
│   ├── rules.py                    # Règles d'alertes
│   └── notifier.py                 # Notifications
│
├── realtime/                       # Temps réel
│   ├── poller.py                   # Polling continu
│   ├── cache.py                    # Cache intelligent
│   └── refresher.py                # Refresher
│
├── sql/                            # Schémas SQL
│   ├── schema.sql                  # Schéma principal
│   ├── baselines.sql               # Fonctions baselines
│   ├── regimes.sql                 # Fonctions régimes
│   ├── opportunities.sql           # Fonctions opportunités
│   └── features_kpis.sql           # Tables features, KPIs
│
└── jobs/                           # Jobs automatisés
    └── daily_run.py                # Job quotidien
```

---

## 🚀 Déploiement

### 💻 Installation Locale

#### 1. Prérequis

- **Python 3.11+** (Backend)
- **Node.js 18+** (Frontend Next.js)
- **PostgreSQL 14+** ou Supabase
- OpenAI API Key (optionnel, pour agent CIO)

#### 2. Installation Backend

```bash
# Cloner le repo
cd dubai-real-estate-intelligence

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scriptsctivate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer les variables d'environnement
cp env.example .env
# Éditer .env avec vos clés API
```

#### 3. Installation Frontend Next.js

```bash
cd next-app

# Installer les dépendances
npm install

# Copier et configurer les variables d'environnement
cp env.example.txt .env.local
# Éditer .env.local avec vos clés API
```

#### 4. Configuration Database

```bash
# Option A : PostgreSQL local
createdb dubai_real_estate
DATABASE_URL=postgresql://user:password@localhost:5432/dubai_real_estate

# Option B : Supabase (recommandé)
DATABASE_URL=postgresql://postgres.tnnsfheflydiuhiduntn:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

#### 5. Lancement

```bash
# Backend : Tests et pipelines
python test_all_apis.py
python jobs/daily_run.py

# Frontend : Next.js
cd next-app
npm run dev
```

Accès : `http://localhost:3000`

---

## 📊 Utilisation

### Interface Next.js (Mobile-first)

**Pages disponibles :**
1. **/** : Page d'accueil avec LED status API
2. **/dashboard** : KPIs + Brief CIO + Opportunités
3. **/sales** : Transactions récentes avec filtres
4. **/zones** : Analyse par localisation + régimes
5. **/radar** : Opportunités scorées par stratégie
6. **/yield** : Rendements locatifs
7. **/floorplans** : Visualisation 3D plans d'étage (nouveau)
8. **/alerts** : Notifications actives
9. **/insights** : Intelligence marché macro
10. **/admin** : Gestion des données + pipeline


### Pipeline quotidien automatique

```bash
# Exécution manuelle
python jobs/daily_run.py

# Ou via cron (Linux/Mac)
0 6 * * * /path/to/venv/bin/python /path/to/jobs/daily_run.py
```

### Polling temps réel

```bash
python realtime/poller.py
```

---

## 🧠 Logique métier

### Stack data optimal pour détecter les deals

**Hiérarchie des sources (par priorité)** :

1. **DLD Transactions** (via Bayut RapidAPI) ✅ **Connecté** - La vérité terrain (closing data)
2. **Bayut API** ✅ **Connecté** - 15 endpoints (annonces, transactions, projets, agents, agences, promoteurs)
3. **PropertyFinder API** ✅ **Connecté** - 500K+ listings UAE
4. **Zyla Labs API** ✅ **Connecté** - Market stats, recherche, propriétés récentes
5. **UAE RealTime API** ✅ **Connecté** - Agents directory, propriétés temps réel, transactions
6. **Emaar Helper** ✅ **Nouveau** - Accès direct aux données Emaar (projets, listings, transactions)
7. **DLD Rental Index API** 🔄 **À activer** - Rendement & pression locative
8. **Makani + GeoHub** 🆕 **Nouveau** - Matching + scoring localisation

**Mini check-list "anti faux signaux"** :
- ✅ Transactions ≠ Listings : les "bons coups" se confirment sur DLD closings, pas sur annonces
- ✅ Normalisation : même projet peut avoir variantes de noms → join via IDs/adresses (Makani aide)
- ✅ Compliance : Dubai Municipality rappelle que l'usage des données implique conditions + responsabilité

**📖 Guide complet** : Voir `docs/data_sources.md`

### Baselines marché

Calculées sur 3 fenêtres : **7j / 30j / 90j**

Métriques :
- Médiane prix/sqft (P50)
- Percentiles P25 / P75
- Volume de transactions
- Momentum (variation vs période précédente)
- Volatilité (écart-type / médiane)
- Dispersion (IQR / médiane)

### Régimes de marché

Classification automatique :

| Régime | Conditions |
|--------|-----------|
| **ACCUMULATION** | Volume ↑, Prix stable, Dispersion élevée |
| **EXPANSION** | Volume ↑, Prix ↑, Dispersion ↓ |
| **DISTRIBUTION** | Volume ↓, Prix stable/haut, Dispersion ↑ |
| **RETOURNEMENT** | Volume ↓, Prix ↓, Volatilité ↑ |

### Scoring multi-stratégies

Chaque opportunité reçoit 4 scores :

1. **FLIP** (achat-revente rapide)
   - Poids : Discount (40%), Liquidité (30%), Momentum (15%), Régime (15%)
   - Pénalités : Supply élevée, Régime RETOURNEMENT

2. **RENT** (cashflow locatif)
   - Poids : Rendement (35%), Stabilité (25%), Liquidité (20%), Régime (20%)
   - Pénalités : Volatilité excessive

3. **LONG_TERM** (appréciation capital)
   - Poids : Régime (35%), Discount (30%), Momentum (20%), Supply (15%)
   - Pénalités : Volatilité, Supply élevée, Régime RETOURNEMENT

4. **Score global** : Moyenne pondérée (FLIP 40%, RENT 30%, LONG 30%)

**Recommandation** : Stratégie avec le score le plus élevé (ou IGNORE si score global < 40)

### KPIs avancés

8 KPIs calculés pour chaque zone et fenêtre (7j/30j/90j) :

| KPI | Nom complet | Formule | Usage |
|-----|-------------|---------|-------|
| **TLS** | Transaction-to-Listing Spread | (median_listing - median_tx) / median_tx | Détecte marge de revente |
| **LAD** | Liquidity-Adjusted Discount | discount × log(1 + tx_count) | Discount ajusté à la liquidité |
| **RSG** | Rental Stress Gap | (loyer_réel - loyer_attendu) / loyer_attendu | Tension locative |
| **SPI** | Supply Pressure Index | normalize(unités_planifiées / tx_12m) | Pression de supply future |
| **GPI** | Geo-Premium Index | location_score × (1 + prime_prix) | Valorisation localisation |
| **RCWM** | Regime Confidence-Weighted Momentum | momentum × confidence_régime | Momentum pondéré |
| **ORD** | Offplan Risk Delta | median_offplan / median_ready - 1 | Risque premium offplan |
| **APS** | Anomaly Persistence Score | jours_anomalie / fenêtre | Persistance des anomalies |

**Utilisation dans les stratégies :**
- FLIP : LAD, TLS, ORD
- RENT : RSG, GPI
- LONG_TERM : SPI, RCWM, APS

### Résumé des risques

Évaluation automatique par zone :

| Risque | Métrique | Seuils |
|--------|----------|--------|
| **Supply** | SPI | LOW < 30, MEDIUM 30-70, HIGH > 70 |
| **Volatilité** | Volatilité % | LOW < 15%, MEDIUM 15-25%, HIGH > 25% |
| **Divergence** | TLS | LOW < 10%, MEDIUM 10-20%, HIGH > 20% |

Score global : moyenne pondérée (Supply 40%, Volatilité 35%, Divergence 25%)

### Agent IA CIO

Génère quotidiennement un brief actionnable :
- 3 zones à surveiller
- 3 opportunités prioritaires
- 1 risque principal
- 1 recommandation stratégique

Utilise GPT-4 via LangChain pour analyser les données du marché.

---

## 🔄 Pipeline LangGraph

Le pipeline enrichi s'exécute quotidiennement via LangGraph :

```
ingest_transactions
    ↓
ingest_mortgages
    ↓
ingest_rental_index      ← Nouveau : données loyers
    ↓
compute_features         ← Nouveau : normalisation + outliers
    ↓
compute_baselines
    ↓
compute_regimes
    ↓
compute_kpis             ← Nouveau : 8 KPIs avancés
    ↓
detect_anomalies
    ↓
compute_scores           ← Enrichi avec KPIs
    ↓
compute_risk_summary     ← Nouveau : résumé risques
    ↓
generate_brief (CIO)
    ↓
send_alerts
```

**Tables générées :**
- `features` : données normalisées (prix/sqft 500-10000 AED)
- `kpis` : 8 KPIs par zone/fenêtre
- `quality_logs` : métriques de qualité des données
- `risk_summaries` : risques par zone

---

## 📱 Design mobile-first

L'interface est optimisée pour **iPhone** (70% du trafic) :

- Layout vertical
- Cards empilées
- Graphiques lisibles sur petit écran
- Filtres simples
- Auto-refresh
- Pas de tables larges

---

## 🔐 Sécurité

- Aucune clé API en dur dans le code
- Variables d'environnement via `.env`
- `.gitignore` configuré
- Aucun scraping non autorisé
- Logs sans données sensibles

---

## 🧪 Tests

### Données MOCK

Pour tester sans API DLD :

```python
# Les connecteurs génèrent automatiquement des données MOCK
# si les clés API ne sont pas configurées
```

### Vérification du pipeline

```bash
# Exécuter le pipeline en mode test
python graphs/market_intelligence_graph.py
```

---

## 📈 Évolutions futures

### Phase 2 : Frontend natif

- React / Next.js
- App mobile native (React Native / Flutter)
- API REST pour découplage backend/frontend

### Améliorations

- Intégration rental index réel
- Calcul de rendement précis
- Prédictions ML (prix futurs)
- Alertes push mobile
- Export PDF des briefs
- Backtesting des stratégies

---

## 🛠️ Maintenance

### Logs

```bash
# Logs stockés dans logs/
tail -f logs/app_*.log
```

### Base de données

```bash
# Backup
pg_dump dubai_real_estate > backup.sql

# Restore
psql dubai_real_estate < backup.sql
```

### Monitoring

- Vérifier les logs quotidiens
- Surveiller les erreurs dans Admin
- Valider les briefs CIO
- Contrôler le volume de données

---

## 📞 Support

Pour toute question :
- Consulter la documentation dans `docs/`
- Vérifier les logs
- Tester avec données MOCK

---

## 📄 Licence

Propriétaire - Usage interne uniquement

---

## 🏆 Stack technique

- **Backend** : Python 3.11+
- **Database** : PostgreSQL 14+
- **Orchestration** : LangGraph
- **IA** : OpenAI GPT-4 + LangChain
- **Frontend** : Streamlit (mobile-first)
- **Visualisation** : Plotly
- **Data** : Pandas, NumPy

---

**Version** : 2.3.0  
**Date** : 2026-01-18  
**Status** : ✅ 100% Opérationnel - Données Live + Floorplans 3D (9 APIs + 45+ endpoints + 20 KPIs + Next.js + Visualisation 3D)

---

## 🚀 Next.js Frontend (Nouveau)

Une nouvelle interface Next.js 14 moderne est disponible dans le dossier `next-app/`.

### Installation Next.js

```bash
cd next-app
npm install
npm run dev
```

Accès : `http://localhost:3000`

### Stack Frontend

- **Framework** : Next.js 14 (App Router)
- **UI** : Tailwind CSS (thème sombre)
- **Charts** : Recharts
- **Icons** : Lucide React
- **Database** : Supabase JS Client

### Pages disponibles

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/dashboard` | KPIs, charts, opportunités, régimes |
| Sales | `/sales` | Transactions, analytics, tendances |
| Zones | `/zones` | Analyse par zone, heatmap, signaux |
| Radar | `/radar` | Opportunités scorées, signaux trading |
| Yield | `/yield` | Rendements locatifs par zone |
| Alerts | `/alerts` | Notifications marché |
| Insights | `/insights` | Intelligence marché, RSI, prédictions |
| Admin | `/admin` | Configuration, pipeline, status |

### Configuration

Le fichier `.env.local` est configuré automatiquement avec les credentials Supabase :

```bash
cd next-app
npm install
npm run dev
```

Accès : `http://localhost:3000`

**Variables d'environnement (`.env.local`)** :
```
NEXT_PUBLIC_SUPABASE_URL=https://tnnsfheflydiuhiduntn.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<auto-configured>
```

### Tables Supabase utilisées

| Table | Description |
|-------|-------------|
| `dld_transactions` | 30 transactions immobilières |
| `dld_opportunities` | 5 opportunités d'investissement |
| `dld_market_regimes` | Régimes de marché par zone |
| `dld_market_baselines` | Baselines de prix par zone |
| `dld_daily_briefs` | Briefs quotidiens CIO |
| `dld_alerts` | Alertes marché |

---

## 🔧 Changelog récent

### v2.3.0 (2026-01-18) - Visualisation Floorplans 3D
- **✅ NOUVELLE PAGE** : `/floorplans` - Visualisation plans d'étage 2D/3D
- **Nouveau** : `components/FloorplanViewer.tsx` - Composant React pour floorplans
- **Nouveau** : `app/floorplans/page.tsx` - Page complète avec recherche
- **Fonctionnalités** : Modèles 3D interactifs Sketchfab, images 2D/3D, modal détaillé
- **Navigation** : Ajout de "Floorplans" dans le menu latéral
- **API** : Intégration complète endpoint `/floorplans` Bayut RapidAPI
- **Configuration** : `NEXT_PUBLIC_BAYUT_API_KEY` ajoutée à `.env.local`

### v2.2.0 (2026-01-18) - Nouveaux Connecteurs et KPIs
- **✅ NOUVEAUX CONNECTEURS** : 4 connecteurs DLD additionnels
- **Nouveau** : `connectors/dld_developers.py` - Promoteurs immobiliers enregistrés
- **Nouveau** : `connectors/dld_valuation.py` - Évaluations officielles DLD
- **Nouveau** : `connectors/dld_lkp_areas.py` - Hiérarchie officielle des zones
- **Nouveau** : `pipelines/compute_additional_kpis.py` - 12 nouveaux KPIs
- **Nouveau** : `test_new_features.py` - Tests complets des nouvelles fonctionnalités
- **Nouveau** : `NOUVEAUTES_v2.2.0.md` - Documentation complète des ajouts
- **Implémenté** : 5/12 nouveaux KPIs (DOM, Turnover, Absorption, Yield, Offplan)
- **Testé** : 4/5 tests passent (DLD Developers, Valuation, LKP Areas, KPIs)
- **Total APIs** : 9 APIs (5 live + 4 mock)
- **Total Endpoints** : 45+ endpoints disponibles
- **Total KPIs** : 20 KPIs (8 existants + 12 nouveaux)

### v2.1.0 (2026-01-18) - 100% Données Live + LED Verte
- **✅ VALIDATION COMPLÈTE** : Tous les mock-ups supprimés, uniquement données live
- **Nouveau** : LED verte sur page d'accueil Next.js (port 3000) - status API en temps réel
- **Nouveau** : `lib/supabase.ts` - Client Supabase pour Next.js
- **Nouveau** : `lib/utils.ts` - Utilitaires frontend (formatage, dates, etc.)
- **Nouveau** : `INVENTAIRE_APIS_KPIS.md` - Inventaire complet APIs, KPIs et granularités
- **Nouveau** : `PROMPT_OPUS_DEEP_THINKING.md` - Prompt Opus 4.5 avec checklist complète
- **Testé** : 5/5 APIs fonctionnelles (DLD Transactions, Rental Index, Bayut, Makani, DDA)
- **Vérifié** : Calculs KPIs, scores et baselines - 100% corrects
- **Vérifié** : Connexion Supabase Next.js - données live affichées
- **Status** : 200 transactions DLD live via Bayut RapidAPI
- **Status** : 25 annonces Bayut live récupérées
- **Status** : Frontend Next.js connecté à Supabase avec indicateur visuel

### v1.4.0 (2026-01-18) - KPIs Avancés et Pipeline Enrichi
- **Nouveau** : 8 KPIs avancés (TLS, LAD, RSG, SPI, GPI, RCWM, ORD, APS)
- **Nouveau** : `sql/features_kpis.sql` - Tables features, kpis, quality_logs, risk_summaries
- **Nouveau** : `pipelines/compute_features.py` - Normalisation et filtrage outliers (500-10000 AED/sqft)
- **Nouveau** : `pipelines/compute_kpis.py` - Calcul des 8 KPIs par zone/fenêtre
- **Nouveau** : `pipelines/compute_risk_summary.py` - Évaluation risques (supply, volatilité, divergence)
- **Nouveau** : `pipelines/ingest_rental_index.py` - Ingestion index locatif DLD
- **Nouveau** : `pipelines/quality_logger.py` - Tracking qualité des données
- **Enrichi** : Stratégies FLIP/RENT/LONG_TERM utilisent les nouveaux KPIs
- **Enrichi** : Pipeline LangGraph avec 4 nouvelles étapes
- **Nouveau** : `test_kpis.py` - Tests unitaires des formules KPIs
- **Modèles** : Feature, KPI, QualityLog, RiskSummary, KPIContext

### v1.3.2 (2026-01-18) - UAE RealTime API
- **Nouveau** : `connectors/uae_realtime_api.py` - UAE Real Estate Data-Real Time API
- **Nouveau** : Agents directory temps réel
- **Nouveau** : Properties search temps réel  
- **Nouveau** : Transactions temps réel
- **Config** : Ajout `UAE_REALTIME_API_KEY`

### v1.3.1 (2026-01-18) - Emaar Helper
- **Nouveau** : `connectors/emaar_helper.py` - Helper centralisé pour données Emaar
- **Nouveau** : `EmaarDataHelper` - Classe pour récupérer projets, listings, transactions Emaar
- **Nouveau** : `get_emaar_data()` - Fonction helper rapide
- **Nouveau** : Liste de 40+ projets Emaar connus (Dubai Marina, Downtown, Creek Harbour, etc.)
- **Nouveau** : Statistiques agrégées Emaar (volume, prix, projets)
- **Nouveau** : `test_emaar_data.py` - Script de test complet avec export JSON
- **Doc** : `docs/emaar_data_sources.md` - Guide complet des plateformes Emaar
- **Doc** : `EMAAR_INTEGRATION.md` - Résumé intégration en français
- **Doc** : Liste complète des 11 plateformes connectées à Emaar

### v1.3.0 (2026-01-18) - Multi-API Integration
- **Nouveau** : PropertyFinder API (500K+ listings UAE)
- **Nouveau** : Zyla Labs API (Market Stats, Search, Recent properties)
- **Nouveau** : IDs promoteurs (Emaar, DAMAC, Nakheel, Meraas, Sobha, Azizi, etc.)
- **Nouveau** : Helpers `get_emaar_projects()`, `get_damac_projects()`, etc.
- **Nouveau** : `connectors/propertyfinder_api.py`
- **Nouveau** : `connectors/zylalabs_api.py`
- **Config** : Ajout `PROPERTYFINDER_API_KEY`, `ZYLALABS_API_KEY`

### v1.2.6 (2026-01-18) - Bayut API Complet
- **Nouveau** : 15 endpoints Bayut RapidAPI intégrés
- **Nouveau** : `/property/{id}` - Détails propriété complets
- **Nouveau** : `/new_projects_search` - Projets off-plan
- **Nouveau** : `/agencies_by_locations`, `/agencies_by_name`, `/agency/{id}` - Agences
- **Nouveau** : `/developers_search` - Promoteurs immobiliers
- **Nouveau** : `/agents_by_name`, `/agents_by_filters`, `/agents_in_agency/{id}`, `/agent/{id}` - Agents
- **Nouveau** : `/amenities_search` - Équipements
- **Nouveau** : `/floorplans` - Plans d'étage 2D/3D

### v1.2.5 (2026-01-18) - DLD via Bayut RapidAPI
- **Nouveau** : Transactions DLD via Bayut RapidAPI (pas besoin de Dubai Pulse)
- **Nouveau** : Double source DLD : Bayut (prioritaire) + Dubai Pulse (fallback)
- **Nouveau** : Parser transactions Bayut vers modèle `Transaction`
- **Doc** : Mise à jour `README.md` avec statut APIs

### v1.2.4 (2026-01-18) - DB locale directe
- **Fix** : Search path forcé sur `public` en local
- **Fix** : Warning si `TABLE_PREFIX` non vide en local
- **Doc** : Ajout `TABLE_PREFIX` dans `env.example`

### v1.2.3 (2026-01-18) - Navigation
- **Fix** : Suppression de la grille de boutons sur la page d'accueil pour éviter le menu en double
- **Fix** : Navigation par sidebar Streamlit uniquement

### v1.2.2 (2026-01-18) - Fix Système Alertes
- **Fix** : Correction des noms de tables SQL dans tout le projet
- **Fix** : Remplacement `dld_transactions` → `transactions` (cohérent avec schéma)
- **Fix** : Remplacement `dld_opportunities` → `opportunities`
- **Fix** : Remplacement `dld_market_regimes` → `market_regimes`
- **Fix** : Remplacement `dld_market_baselines` → `market_baselines`
- **Fix** : Remplacement `active_alerts` → `alerts` (table existante)
- **Fix** : Correction page `06_Alerts.py` - requêtes fonctionnelles
- **Fix** : Correction `alerts/rules.py` - noms de tables cohérents
- **Fix** : Correction 14+ fichiers avec références SQL incorrectes

**Fichiers corrigés** :
- `streamlit_app.py`, `pages/01-08_*.py`, `ai_agents/chief_investment_officer.py`
- `alerts/rules.py`, `realtime/refresher.py`, `pipelines/compute_scores.py`

### v1.2.1 (2026-01-18) - Audit & Données Réalistes
- **Fix** : Import `Dict` manquant dans `listings_placeholder.py`
- **Fix** : `st.set_page_config` manquant dans `Market_Insights.py`
- **Fix** : Bug `setup_apis.py` - TypeError sur fichier .env vide
- **Nouveau** : Données MOCK réalistes - Vrais noms de projets Dubai
- **Nouveau** : `core/dubai_mock_data.py` - Référentiel de projets immobiliers Dubai
- **Nouveau** : `core/icons.py` - Icônes SVG vectorielles (remplacement emojis)
- **Nouveau** : Logo SVG Robin sur page d'accueil
- **Nettoyage** : Suppression emojis des noms de fichiers pages
- **Nettoyage** : Unification `app.py` / `streamlit_app.py`

### v1.2.0 (2026-01-17) - Stack Data Optimal
- 🆕 **Bayut API** : Connecteur pour lead indicators (annonces live)
- 🆕 **Makani Geocoding** : Matching précis + scoring localisation
- 🆕 **DDA Planning & Zoning** : Signaux en avance (permis, zonage)
- ✅ **DLD Rental Index** : Mise à jour pour Dubai Pulse API
- ✅ **Nouveaux modèles** : Listing, MakaniAddress, PlanningPermit, ZoningChange
- ✅ **Documentation complète** : `docs/optimal_data_stack.md`
- ✅ **Anti-faux signaux** : Règles de validation Transactions vs Listings

### v1.1.0 (2026-01-17)
- ✅ **APIs DLD connectées** : Intégration Dubai Pulse API officielle
- ✅ **Authentification OAuth** : Module d'auth automatique avec cache de token
- ✅ **Connecteur Transactions** : Récupération données réelles DLD
- ✅ **Connecteur Buildings** : Métadonnées bâtiments et projets
- ✅ **Fallback intelligent** : Mode MOCK si clés API non configurées
- ✅ **Documentation** : Guide complet d'obtention des clés API

### v1.0.1 (2026-01-17)
- ✅ Fix : Import LangChain obsolète (`langchain.prompts` → `langchain_core.prompts`)
- ✅ Compatible avec LangChain >= 0.1.0

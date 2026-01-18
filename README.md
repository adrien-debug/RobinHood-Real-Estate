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
├── app.py                          # Application Streamlit principale
├── requirements.txt                # Dépendances Python
├── env.example                     # Variables d'environnement
│
├── core/                           # Core système
│   ├── config.py                   # Configuration centralisée
│   ├── db.py                       # Connexion PostgreSQL
│   ├── dubai_mock_data.py          # Données réalistes Dubai (projets, zones)
│   ├── icons.py                    # Icônes SVG vectorielles
│   ├── models.py                   # Modèles Pydantic
│   └── utils.py                    # Utilitaires
│
├── connectors/                     # Connecteurs API
│   ├── dld_transactions.py         # DLD Transactions
│   ├── dld_mortgages.py            # DLD Hypothèques
│   ├── dld_rental_index.py         # DLD Index locatif
│   ├── developers_pipeline.py      # Pipeline développeurs
│   └── listings_placeholder.py     # Annonces (API autorisée)
│
├── pipelines/                      # Pipelines de données
│   ├── ingest_transactions.py      # Ingestion transactions
│   ├── ingest_mortgages.py         # Ingestion hypothèques
│   ├── compute_market_baselines.py # Calcul baselines
│   ├── compute_market_regimes.py   # Calcul régimes
│   ├── detect_anomalies.py         # Détection anomalies
│   └── compute_scores.py           # Scoring multi-stratégies
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
│   └── refresher.py                # Refresher Streamlit
│
├── pages/                          # Pages Streamlit
│   ├── 01_Dashboard.py             # Dashboard + Brief CIO
│   ├── 02_Sales.py                 # Transactions récentes
│   ├── 03_Zones.py                 # Analyse par zone
│   ├── 04_Radar.py                 # Opportunités scorées
│   ├── 05_Yield.py                 # Rendements locatifs
│   ├── 06_Alerts.py                # Alertes actives
│   ├── 07_Admin.py                 # Administration
│   └── 08_Market_Insights.py       # Intelligence marché
│
├── sql/                            # Schémas SQL
│   ├── schema.sql                  # Schéma principal
│   ├── baselines.sql               # Fonctions baselines
│   ├── regimes.sql                 # Fonctions régimes
│   └── opportunities.sql           # Fonctions opportunités
│
└── jobs/                           # Jobs automatisés
    └── daily_run.py                # Job quotidien
```

---

## 🚀 Déploiement

### ☁️ Streamlit Cloud (Production)

**L'app est déployée sur** : https://adrien-debug-robinhood-real-estate-app-5mafql.streamlit.app/

#### Configuration Requise

Si tu vois une erreur de connexion DB, suis ces étapes :

1. **Ouvre les secrets Streamlit Cloud**
   - Va sur https://share.streamlit.io/
   - Clique sur "Manage app" → Settings → Secrets

2. **Ajoute cette configuration** :
   ```toml
   DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
   TABLE_PREFIX = "dld_"
   TIMEZONE = "Asia/Dubai"
   ```

3. **Sauvegarde et redémarre**
   - Clique sur "Save"
   - Clique sur "Reboot app"
   - Attends 60 secondes

📖 **Guide complet** : Voir `STREAMLIT_CLOUD_CONFIG.md`

---

### 💻 Installation Locale

#### 1. Prérequis

- Python 3.11+
- PostgreSQL 14+ ou Supabase
- OpenAI API Key (optionnel, pour agent CIO)

#### 2. Installation

```bash
# Cloner le repo
cd dubai-real-estate-intelligence

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer les variables d'environnement
cp env.example .env
# Éditer .env avec vos clés API
```

#### 3. Configuration PostgreSQL

```bash
# Option A : PostgreSQL local
createdb dubai_real_estate
DATABASE_URL=postgresql://user:password@localhost:5432/dubai_real_estate

# Option B : Supabase (recommandé)
# Utilise le même DATABASE_URL que Streamlit Cloud
DATABASE_URL=postgresql://postgres.tnnsfheflydiuhiduntn:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
TABLE_PREFIX=dld_
```

### 4. Initialisation

```bash
# Lancer Streamlit
streamlit run app.py

# Aller dans Admin > Initialiser le schéma DB
# Puis : Générer données MOCK (pour test)
# Puis : Exécuter le pipeline complet
```

---

## 📊 Utilisation

### Interface Streamlit (Mobile-first)

```bash
streamlit run app.py
```

Accès : `http://localhost:8501`

**Pages disponibles :**
1. **Dashboard** : KPIs + Brief CIO + Top opportunités
2. **Sales** : Transactions récentes avec filtres
3. **Zones** : Analyse par localisation + régimes
4. **Radar** : Opportunités scorées par stratégie
5. **Yield** : Rendements locatifs
6. **Alerts** : Notifications actives
7. **Admin** : Gestion des données + pipeline
8. **Insights** : Intelligence marché macro

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

1. **DLD Transactions** (Dubai Pulse) ✅ **Connecté** - La vérité terrain (closing data)
2. **DLD Rental Index API** 🔄 **À activer** - Rendement & pression locative
3. **Bayut API** 🆕 **Nouveau** - Offre live (lead indicators)
4. **Makani + GeoHub** 🆕 **Nouveau** - Matching + scoring localisation
5. **DDA Zoning/Planning** 🆕 **Nouveau** - Signaux en avance

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

### Agent IA CIO

Génère quotidiennement un brief actionnable :
- 3 zones à surveiller
- 3 opportunités prioritaires
- 1 risque principal
- 1 recommandation stratégique

Utilise GPT-4 via LangChain pour analyser les données du marché.

---

## 🔄 Pipeline LangGraph

Le pipeline s'exécute quotidiennement via LangGraph :

```
ingest_transactions
    ↓
ingest_mortgages
    ↓
compute_baselines
    ↓
compute_regimes
    ↓
detect_anomalies
    ↓
compute_scores
    ↓
generate_brief (CIO)
    ↓
send_alerts
```

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

**Version** : 1.2.1  
**Date** : 2026-01-18  
**Status** : ✅ Opérationnel (Audit complet effectué)

---

## 🔧 Changelog récent

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

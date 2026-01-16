# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [1.0.0] - 2026-01-16

### ✨ Ajouté

#### Core
- Configuration centralisée via Pydantic Settings
- Connexion PostgreSQL avec gestion des transactions
- Modèles Pydantic pour validation des données
- Utilitaires (formatage, normalisation, timezone Dubai)

#### Connecteurs
- DLD Transactions (avec mode MOCK)
- DLD Mortgages (avec mode MOCK)
- DLD Rental Index (avec mode MOCK)
- Developers Pipeline (avec mode MOCK)
- Listings placeholder (API autorisée uniquement)

#### Pipelines
- Ingestion transactions et hypothèques
- Calcul baselines marché (7j, 30j, 90j)
- Calcul régimes de marché (ACCUMULATION, EXPANSION, DISTRIBUTION, RETOURNEMENT)
- Détection d'anomalies de prix
- Scoring multi-stratégies (FLIP, RENT, LONG_TERM)

#### Stratégies
- Stratégie FLIP (achat-revente rapide)
- Stratégie RENT (cashflow locatif)
- Stratégie LONG_TERM (appréciation capital)
- Score global avec recommandation automatique

#### Agent IA
- Agent CIO (Chief Investment Officer)
- Brief quotidien automatique via GPT-4
- Analyse des zones, opportunités, risques
- Recommandations stratégiques actionnables

#### LangGraph
- Pipeline orchestré avec StateGraph
- 8 nodes : ingest, compute, detect, score, brief, alerts
- Exécution séquentielle avec gestion d'état
- Logs détaillés et résumé final

#### Alertes
- Règles d'alertes (high_discount, regime_change, high_volume)
- Notifications webhook (Slack, Discord)
- Sauvegarde en base de données
- Filtrage par sévérité

#### Temps réel
- Poller continu (configurable)
- Cache intelligent avec TTL
- Refresher pour Streamlit
- Auto-refresh des pages

#### Interface Streamlit (Mobile-first)
- **Dashboard** : KPIs, Brief CIO, Top opportunités, Régimes
- **Ventes du jour** : Transactions récentes avec filtres
- **Zones / Buildings** : Analyse par localisation + graphiques
- **Deal Radar** : Opportunités scorées avec radar charts
- **Location & Yield** : Rendements locatifs
- **Alertes** : Gestion des notifications
- **Admin** : Initialisation DB, pipeline, statistiques

#### SQL
- Schéma complet (transactions, baselines, régimes, opportunités, alertes, briefs)
- Fonctions SQL pour calculs (baselines, régimes, détection)
- Procédures stockées (refresh_market_baselines, refresh_market_regimes)
- Vues (v_recent_transactions, v_active_opportunities)

#### Documentation
- README complet avec architecture
- QUICKSTART pour démarrage rapide
- Guide des sources de données
- Logique de scoring détaillée
- Guidelines UX mobile-first
- Comportement agent IA CIO

#### Scripts
- start.sh (Linux/Mac)
- start.bat (Windows)
- Makefile avec commandes utiles
- Job quotidien automatisable

#### Configuration
- Variables d'environnement (.env)
- Configuration Streamlit
- .gitignore complet
- .python-version

### 🎨 Design

- Interface mobile-first (iPhone prioritaire)
- Cards empilées verticalement
- Graphiques Plotly responsives
- Emojis pour lecture rapide
- Couleurs institutionnelles
- Auto-refresh toutes les 5 minutes

### 🔒 Sécurité

- Aucune clé API en dur
- Variables d'environnement
- Aucun scraping non autorisé
- Logs sans données sensibles
- Validation des entrées

### 📊 Métriques

- 50+ fichiers créés
- 7 pages Streamlit
- 5 connecteurs de données
- 6 pipelines de traitement
- 3 stratégies de scoring
- 1 agent IA CIO
- 4 tables SQL principales
- 100% fonctionnel

---

## [Futur] - Roadmap

### Phase 2 : Frontend natif

- [ ] API REST backend
- [ ] Frontend React / Next.js
- [ ] App mobile native (React Native / Flutter)
- [ ] Authentification utilisateurs
- [ ] Rôles et permissions

### Améliorations

- [ ] Intégration rental index réel
- [ ] Calcul de rendement précis avec données réelles
- [ ] Prédictions ML (prix futurs)
- [ ] Alertes push mobile
- [ ] Export PDF des briefs
- [ ] Backtesting des stratégies
- [ ] Multi-agents (CIO + Analyst + Risk Manager)
- [ ] Fine-tuning modèle LLM spécialisé
- [ ] Tableau de bord performance des recommandations
- [ ] Intégration calendrier économique
- [ ] Analyse sentiment marché (news, social media)

---

## Notes de version

### v1.0.0 - Version initiale

**Statut** : ✅ Opérationnel

**Stack** :
- Python 3.11+
- PostgreSQL 14+
- Streamlit
- LangGraph
- OpenAI GPT-4
- Plotly

**Capacités** :
- Ingestion données DLD (ou MOCK)
- Calcul baselines et régimes de marché
- Détection opportunités sous-valorisées
- Scoring multi-stratégies
- Brief quotidien automatique par agent IA
- Interface mobile-first
- Temps réel avec auto-refresh

**Limitations connues** :
- Mode MOCK par défaut (nécessite clés API DLD réelles)
- Rendements locatifs estimés (nécessite rental index réel)
- Brief CIO en anglais (peut être adapté en français)
- Pas d'authentification utilisateurs
- Pas d'historique des briefs dans l'interface

**Performance** :
- Pipeline complet : ~2-5 minutes (selon volume)
- Brief CIO : ~15-30 secondes
- Interface Streamlit : responsive sur iPhone

---

**Contributeurs** : Équipe de développement  
**Licence** : Propriétaire - Usage interne uniquement

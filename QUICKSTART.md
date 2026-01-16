# 🚀 Démarrage rapide

Guide pour lancer la plateforme en **5 minutes**.

---

## ✅ Prérequis

- Python 3.11+
- PostgreSQL 14+
- OpenAI API Key (pour agent CIO)

---

## 📦 Installation

### Option 1 : Script automatique (recommandé)

**Linux / Mac :**
```bash
./start.sh
```

**Windows :**
```cmd
start.bat
```

### Option 2 : Manuel

```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
cp env.example .env
# Éditer .env avec vos clés API
```

---

## 🔧 Configuration

### 1. PostgreSQL

```bash
# Créer la base de données
createdb dubai_real_estate

# Mettre à jour .env
DATABASE_URL=postgresql://user:password@localhost:5432/dubai_real_estate
```

### 2. OpenAI (pour agent CIO)

```bash
# Dans .env
OPENAI_API_KEY=sk-...
```

### 3. DLD API (optionnel pour test)

```bash
# Dans .env
DLD_API_KEY=your_dld_api_key
```

**Note** : Sans clé DLD, le système génère des données MOCK pour tester.

---

## 🚀 Lancement

### 1. Démarrer Streamlit

```bash
streamlit run app.py
```

Accès : `http://localhost:8501`

### 2. Initialiser la base (première fois)

1. Aller dans **Admin** (menu latéral)
2. Cliquer sur **"📦 Initialiser le schéma DB"**
3. Cliquer sur **"🧪 Générer données MOCK"** (pour test)
4. Cliquer sur **"▶️ Exécuter le pipeline complet"**

✅ La plateforme est prête !

---

## 📱 Navigation

### Pages disponibles

1. **📊 Dashboard**
   - KPIs du jour
   - Brief CIO
   - Top opportunités
   - Régimes de marché

2. **🏠 Ventes du jour**
   - Transactions récentes
   - Filtres (zone, chambres, prix)
   - Détection sous-marché

3. **📍 Zones / Buildings**
   - Analyse par localisation
   - Baselines marché
   - Régimes
   - Évolution des prix

4. **🎯 Deal Radar**
   - Opportunités scorées
   - Filtres par stratégie
   - Scores détaillés (FLIP, RENT, LONG)

5. **💰 Location & Yield**
   - Rendements locatifs
   - Index DLD

6. **🔔 Alertes**
   - Notifications actives
   - Filtres par sévérité

7. **⚙️ Admin**
   - Gestion des données
   - Exécution du pipeline
   - Statistiques

---

## 🔄 Pipeline quotidien

### Exécution manuelle

```bash
python jobs/daily_run.py
```

### Automatisation (cron)

**Linux / Mac :**
```bash
# Éditer crontab
crontab -e

# Ajouter (exécution à 6h du matin)
0 6 * * * /path/to/venv/bin/python /path/to/jobs/daily_run.py
```

**Windows (Task Scheduler) :**
1. Ouvrir Task Scheduler
2. Créer une tâche
3. Trigger : Quotidien à 6h
4. Action : `python.exe C:\path\to\jobs\daily_run.py`

---

## ⚡ Temps réel

### Démarrer le poller

```bash
python realtime/poller.py
```

Refresh automatique toutes les 15 minutes (configurable dans `.env`).

---

## 🧪 Mode test (sans API DLD)

Le système fonctionne **sans clés API** en mode MOCK :

1. Ne pas configurer `DLD_API_KEY` dans `.env`
2. Les connecteurs génèrent automatiquement des données de test
3. Parfait pour développement / démo

---

## 📊 Workflow typique

### Matin (6h-7h)

1. **Pipeline automatique** s'exécute
   - Ingestion transactions DLD
   - Calcul baselines
   - Détection opportunités
   - Génération brief CIO

2. **Consulter le Dashboard** (iPhone)
   - Lire le brief CIO
   - Identifier zones à surveiller
   - Prioriser opportunités

### Journée

3. **Analyser les opportunités**
   - Aller dans Deal Radar
   - Filtrer par stratégie (FLIP, RENT, LONG)
   - Examiner les scores détaillés

4. **Approfondir par zone**
   - Zones / Buildings
   - Vérifier régime de marché
   - Analyser évolution des prix

5. **Vérifier les alertes**
   - Changements de régime
   - Nouvelles opportunités > 20% discount

---

## 🔍 Vérifications

### Santé du système

```bash
# Logs
tail -f logs/app_*.log

# Base de données
psql dubai_real_estate -c "SELECT COUNT(*) FROM transactions;"
```

### Statistiques

Aller dans **Admin** pour voir :
- Nombre de transactions
- Nombre d'opportunités
- Nombre de baselines calculées
- Nombre de briefs générés

---

## ❓ Problèmes courants

### Erreur : "No module named 'core'"

```bash
# Vérifier que vous êtes dans le bon dossier
cd /path/to/dubai-real-estate-intelligence

# Vérifier que venv est activé
source venv/bin/activate
```

### Erreur : "Connection refused" (PostgreSQL)

```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql  # Linux
brew services list  # Mac

# Vérifier DATABASE_URL dans .env
```

### Erreur : "OpenAI API key not found"

```bash
# Vérifier .env
cat .env | grep OPENAI_API_KEY

# Ou désactiver temporairement l'agent CIO
# (le brief de secours sera utilisé)
```

---

## 📚 Documentation complète

- **README.md** : Vue d'ensemble
- **docs/data_sources.md** : Sources de données
- **docs/scoring_logic.md** : Logique de scoring
- **docs/mobile_ux_guidelines.md** : Guidelines UX
- **docs/ai_agent_behavior.md** : Agent CIO

---

## 🎯 Prochaines étapes

1. ✅ Lancer la plateforme
2. ✅ Générer des données MOCK
3. ✅ Exécuter le pipeline
4. ✅ Explorer le Dashboard
5. 🔄 Configurer les vraies APIs DLD
6. 🔄 Automatiser le pipeline quotidien
7. 🔄 Configurer les alertes (Slack/email)

---

**Besoin d'aide ?** Consultez les logs dans `logs/` ou la documentation dans `docs/`.

---

**Version** : 1.0.0  
**Date** : 2026-01-16

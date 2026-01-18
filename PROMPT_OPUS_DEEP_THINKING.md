# PROMPT OPUS 4.5 DEEP THINKING - ROBIN REAL ESTATE INTELLIGENCE

## CONTEXTE

Tu es un expert en data engineering et analyse immobilière institutionnelle. Tu travailles sur **Robin**, une plateforme d'intelligence immobilière pour Dubaï qui agrège des données de multiples APIs pour détecter des opportunités d'investissement.

## ÉTAT ACTUEL DU SYSTÈME

### APIs Connectées (LIVE)
- Bayut RapidAPI : 200 transactions DLD, 25+ listings, 15+ endpoints
- UAE RealTime API : Agents directory
- Supabase : 30+ transactions en base, 52 communautés, 68 régimes

### APIs Partiellement Configurées
- Dubai Pulse OAuth : Manque `DLD_API_SECRET`
- DLD Rental Index : Mode MOCK
- Makani Geocoding : Mode MOCK
- DDA Planning : Mode MOCK

### APIs Non Configurées
- PropertyFinder (500K+ listings)
- Zyla Labs (Market stats)
- Developers Pipeline

### KPIs Calculés (8 KPIs)
1. TLS (Transaction-to-Listing Spread)
2. LAD (Liquidity-Adjusted Discount)
3. RSG (Rental Stress Gap)
4. SPI (Supply Pressure Index)
5. GPI (Geo-Premium Index)
6. RCWM (Regime Confidence-Weighted Momentum)
7. ORD (Offplan Risk Delta)
8. APS (Anomaly Persistence Score)

### Granularités Actuelles
- City → Community → Project → Building → Rooms Bucket
- Fenêtres : 7j, 30j, 90j

---

## OBJECTIF

Maximiser la couverture de données sur le marché immobilier de Dubaï pour obtenir des KPIs **ultra-granulaires** (par district, par bâtiment, par étage si possible).

---

## CHECKLIST D'ANALYSE

### PHASE 1 : AUDIT DES SOURCES EXISTANTES

- [ ] Vérifier que toutes les APIs dans `connectors/` sont correctement implémentées
- [ ] Identifier les champs non exploités dans les réponses API (Bayut retourne beaucoup plus de données que ce qui est parsé)
- [ ] Lister les endpoints Bayut non utilisés (floorplans, amenities, etc.)
- [ ] Vérifier la qualité des données en base (complétude, fraîcheur)
- [ ] Analyser les logs de qualité (`quality_logs`) pour identifier les gaps

### PHASE 2 : ACTIVATION DES APIS EN MOCK

- [ ] Obtenir `DLD_API_SECRET` sur https://www.dubaipulse.gov.ae
- [ ] Obtenir `MAKANI_API_KEY` sur https://geohub.dubaipulse.gov.ae
- [ ] Obtenir `DDA_API_KEY` sur https://www.dm.gov.ae/open-data
- [ ] Tester chaque API en mode réel après configuration
- [ ] Mettre à jour les connecteurs si les formats de réponse diffèrent

### PHASE 3 : AJOUT DE NOUVELLES SOURCES

- [ ] Ajouter connecteur `dld_buildings` (Dubai Pulse Open API)
- [ ] Ajouter connecteur `dld_lkp_areas` (hiérarchie zones officielles)
- [ ] Ajouter connecteur `dld_developers` (promoteurs enregistrés)
- [ ] Ajouter connecteur `dld_valuation` (évaluations officielles)
- [ ] Configurer PropertyFinder Enterprise API 2.0 (gratuit pour partenaires)
- [ ] Évaluer Smart Indexes (~$199/mois) pour Bayut + Makani + Price Indexes

### PHASE 4 : NOUVEAUX KPIs À IMPLÉMENTER

- [ ] **Days on Market (DOM)** : Médiane jours listing actif par bâtiment
- [ ] **Listing Turnover Rate** : Annonces vendues/total par communauté
- [ ] **Price Cut Frequency** : % annonces avec baisse prix par projet
- [ ] **Absorption Rate** : Transactions/mois ÷ stock annonces par communauté
- [ ] **Rental Yield Actual** : Loyer annuel / prix vente par bâtiment
- [ ] **Developer Delivery Score** : % projets livrés à temps par promoteur
- [ ] **Metro Premium** : Δ prix < 500m métro vs > 1km par bâtiment
- [ ] **Beach Premium** : Δ prix waterfront vs non par bâtiment
- [ ] **Offplan Discount Evolution** : Δ prix off-plan vs ready YoY par projet
- [ ] **Investor Concentration** : % multi-property owners par communauté
- [ ] **Floor Premium** : Prix/sqft par étage (si données disponibles)
- [ ] **View Premium** : Δ prix vue mer/ville/jardin (si données disponibles)

### PHASE 5 : ENRICHISSEMENT GÉOGRAPHIQUE

- [ ] Intégrer Makani pour numéro unique par bâtiment (matching précis)
- [ ] Calculer distances POI : métro, plage, mall, école, hôpital
- [ ] Créer un score localisation composite (0-100)
- [ ] Mapper les zones de développement prioritaire (DDA)
- [ ] Identifier les corridors de transport en développement

### PHASE 6 : GRANULARITÉ EXTRÊME

- [ ] Subdiviser les communautés en sous-zones (ex: Dubai Marina → Marina Walk, JBR Walk, etc.)
- [ ] Tracker les prix par étage (si floorplans disponibles)
- [ ] Identifier les immeubles premium vs standard dans chaque projet
- [ ] Créer des micro-zones de 500m de rayon autour des stations de métro
- [ ] Analyser les différences de prix par orientation (vue)

### PHASE 7 : QUALITÉ ET MONITORING

- [ ] Implémenter des alertes si taux de rejet > 10%
- [ ] Créer un dashboard de santé des données
- [ ] Logger les temps de réponse API
- [ ] Monitorer la fraîcheur des données (dernière sync)
- [ ] Détecter les anomalies de prix (outliers)

### PHASE 8 : AUTOMATISATION

- [ ] Cron job sync quotidienne (transactions, listings)
- [ ] Cron job sync hebdomadaire (permis, zonage)
- [ ] Cron job sync mensuelle (rental index)
- [ ] Pipeline LangGraph pour génération automatique de briefs
- [ ] Alertes temps réel (Slack/email) sur nouvelles opportunités
- [ ] Export PDF automatique des briefs quotidiens

---

## QUESTIONS À EXPLORER

1. **Données manquantes** : Quelles données critiques ne sont pas encore collectées ?
2. **APIs alternatives** : Existe-t-il d'autres sources de données pour Dubaï (cadastre, permis, évaluations) ?
3. **Matching** : Comment améliorer le matching entre transactions DLD et annonces Bayut/PF ?
4. **Historique** : Comment obtenir des données historiques (5+ ans) pour les analyses de tendance ?
5. **Off-plan** : Comment tracker précisément les projets off-plan et leur évolution de prix ?
6. **Rental** : Comment obtenir des données locatives plus granulaires (par bâtiment) ?
7. **Agents** : Les données agents/agences peuvent-elles prédire la qualité des deals ?
8. **Développeurs** : Comment scorer la fiabilité des promoteurs (retards, qualité) ?
9. **Saisonnalité** : Quels patterns saisonniers exploiter (Ramadan, été, etc.) ?
10. **Investisseurs** : Comment identifier les patterns d'achat institutionnel vs retail ?

---

## LIVRABLES ATTENDUS

1. **Plan d'action priorisé** avec effort estimé (heures)
2. **Liste des connecteurs à créer/modifier**
3. **Liste des nouveaux KPIs avec formules SQL**
4. **Architecture de données mise à jour**
5. **Estimation des coûts APIs additionnelles**
6. **Timeline d'implémentation**

---

## CONTRAINTES

- Ne pas faire de scraping non autorisé
- Utiliser uniquement des APIs officielles ou autorisées
- Respecter les rate limits
- Ne jamais logger de données sensibles
- Privilégier les sources gratuites avant les payantes
- Chaque modification doit être testée avant déploiement

---

## FICHIERS DE RÉFÉRENCE

- `INVENTAIRE_APIS_KPIS.md` : Inventaire complet actuel
- `connectors/*.py` : Tous les connecteurs API
- `pipelines/*.py` : Pipelines de calcul
- `sql/*.sql` : Schémas et fonctions SQL
- `core/config.py` : Configuration des variables d'environnement
- `docs/data_sources.md` : Documentation des sources
- `API_LINKS.md` : Liens pour obtenir les accès API

---

## FORMAT DE RÉPONSE

Réponds en JSON structuré avec :

```json
{
  "priority_actions": [
    {"id": 1, "action": "...", "effort_hours": X, "impact": "HIGH/MEDIUM/LOW"}
  ],
  "new_connectors": [
    {"name": "...", "source": "...", "endpoints": [...], "data_points": [...]}
  ],
  "new_kpis": [
    {"name": "...", "formula": "...", "granularity": "...", "source_required": "..."}
  ],
  "api_costs": [
    {"api": "...", "cost_monthly": X, "value_score": "HIGH/MEDIUM/LOW"}
  ],
  "risks": ["..."],
  "timeline_weeks": X
}
```

---

**GO DEEP. THINK BIG. FIND EVERY DATA POINT POSSIBLE.**

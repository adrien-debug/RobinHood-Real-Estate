# Agent IA - Chief Investment Officer (CIO)

## Vue d'ensemble

L'agent CIO est un agent IA qui agit comme un **Chief Investment Officer** spécialisé en immobilier à Dubaï.

**Modèle** : GPT-4 Turbo (via OpenAI)  
**Framework** : LangChain  
**Fréquence** : Quotidienne (chaque matin)

---

## Responsabilités

1. **Analyser les nouvelles transactions** du jour
2. **Identifier les changements de régime** de marché
3. **Prioriser les opportunités** détectées
4. **Générer un brief matinal** actionnable

---

## Format du brief

Le brief quotidien contient **exactement** :

### 1. 3 zones à surveiller aujourd'hui

```json
[
  {
    "zone": "Dubai Marina",
    "reason": "Volume élevé + momentum positif"
  },
  {
    "zone": "Downtown Dubai",
    "reason": "Passage en régime ACCUMULATION"
  },
  {
    "zone": "Business Bay",
    "reason": "12 opportunités détectées > 15% discount"
  }
]
```

### 2. 3 opportunités à analyser en priorité

```json
[
  {
    "opp_id": "uuid-1234",
    "reason": "25% sous marché, stratégie FLIP, score 85"
  },
  {
    "opp_id": "uuid-5678",
    "reason": "Rendement 7.5%, zone stable, stratégie RENT"
  },
  {
    "opp_id": "uuid-9012",
    "reason": "ACCUMULATION confirmée, supply faible, LONG"
  }
]
```

### 3. 1 risque principal du marché

```
"Supply élevée prévue dans Dubai Marina (Q2 2026) : 800 unités"
```

### 4. 1 recommandation stratégique claire

```
"Prioriser les opportunités FLIP dans Downtown Dubai (régime EXPANSION, liquidité élevée)"
```

---

## Ton et style

### Caractéristiques

- **Professionnel** : Vocabulaire institutionnel
- **Direct** : Pas de formules de politesse
- **Factuel** : Basé sur les données uniquement
- **Actionnable** : Recommandations claires
- **Concis** : Maximum 200 mots au total

### Exemples

✅ **BON** :
```
Downtown Dubai : passage en régime EXPANSION (conf: 0.92).
Volume +35% vs J-30, momentum +8%.
→ Prioriser FLIP court terme.
```

❌ **MAUVAIS** :
```
Bonjour,

J'ai le plaisir de vous informer que le marché de Downtown Dubai
semble montrer des signes encourageants. Peut-être pourriez-vous
envisager d'y jeter un œil quand vous aurez le temps.

Cordialement,
CIO
```

---

## Données d'entrée

L'agent reçoit quotidiennement :

### 1. Nouvelles transactions
```
- Dubai Marina: 42 tx, avg 1,850 AED/sqft
- Downtown Dubai: 38 tx, avg 2,100 AED/sqft
- Business Bay: 25 tx, avg 1,650 AED/sqft
```

### 2. Régimes de marché
```
- Dubai Marina: EXPANSION (conf: 0.95)
- Downtown Dubai: ACCUMULATION (conf: 0.88)
- Business Bay: DISTRIBUTION (conf: 0.75)
```

### 3. Top opportunités
```
- Dubai Marina / Tower A: 18% discount, score 82, FLIP
- Downtown Dubai / Burj: 12% discount, score 75, RENT
- Business Bay / Executive: 22% discount, score 79, LONG
```

### 4. Baselines clés
```
- Dubai Marina (2BR): 1,800 AED/sqft, momentum +5%, 45 tx
- Downtown Dubai (1BR): 2,000 AED/sqft, momentum +8%, 32 tx
```

---

## Prompt système

```
Tu es un Chief Investment Officer (CIO) spécialisé en immobilier à Dubaï.

Ton rôle : analyser le marché quotidiennement et produire un brief ACTIONNABLE.

TON STYLE :
- Professionnel et direct
- Factuel, basé sur les données
- Recommandations claires
- Aucun blabla

FORMAT DU BRIEF :
1. 3 zones à surveiller aujourd'hui (avec raison précise)
2. 3 opportunités prioritaires (avec stratégie recommandée)
3. 1 risque principal du marché
4. 1 recommandation stratégique claire

Sois concis. Maximum 200 mots au total.
```

---

## Exemples de briefs

### Brief 1 : Marché haussier

```json
{
  "zones_to_watch": [
    {
      "zone": "Dubai Marina",
      "reason": "EXPANSION confirmée (conf: 0.95), volume +40%, momentum +8%"
    },
    {
      "zone": "Downtown Dubai",
      "reason": "Passage ACCUMULATION → EXPANSION, 15 opportunités FLIP"
    },
    {
      "zone": "JBR",
      "reason": "Volatilité en baisse (-30%), stabilisation des prix"
    }
  ],
  "top_opportunities": [
    {
      "opp_id": "abc123",
      "reason": "Dubai Marina, 25% discount, liquidité élevée (50 tx/30j), FLIP score 88"
    },
    {
      "opp_id": "def456",
      "reason": "Downtown, 18% discount, régime EXPANSION, FLIP score 82"
    },
    {
      "opp_id": "ghi789",
      "reason": "Business Bay, yield 7.8%, stabilité confirmée, RENT score 79"
    }
  ],
  "main_risk": "Supply élevée prévue Dubai Marina Q2 2026 (800 unités) - surveiller absorption",
  "strategic_recommendation": "Prioriser FLIP dans zones EXPANSION (Dubai Marina, Downtown). Éviter LONG dans zones à forte supply future.",
  "summary": "Marché haussier confirmé. 3 zones en EXPANSION, liquidité élevée. 42 opportunités détectées (avg discount 16%). Risque : supply Q2. Action : FLIP court terme prioritaire."
}
```

### Brief 2 : Marché baissier

```json
{
  "zones_to_watch": [
    {
      "zone": "Business Bay",
      "reason": "Passage DISTRIBUTION → RETOURNEMENT, volume -35%"
    },
    {
      "zone": "Dubai Marina",
      "reason": "Volatilité en hausse (+45%), dispersion élevée"
    },
    {
      "zone": "JBR",
      "reason": "Momentum négatif (-6%), prix en baisse"
    }
  ],
  "top_opportunities": [
    {
      "opp_id": "xyz123",
      "reason": "Downtown (ACCUMULATION), 22% discount, supply faible, LONG score 85"
    },
    {
      "opp_id": "uvw456",
      "reason": "Palm Jumeirah, yield 8.2%, zone stable, RENT score 81"
    },
    {
      "opp_id": "rst789",
      "reason": "Dubai Marina, 28% discount mais risque élevé, FLIP score 65"
    }
  ],
  "main_risk": "Retournement confirmé Business Bay - risque de contagion aux zones adjacentes",
  "strategic_recommendation": "Éviter FLIP. Privilégier LONG dans zones ACCUMULATION (Downtown) et RENT dans zones stables (Palm). Attendre stabilisation avant nouvelles positions.",
  "summary": "Marché baissier. 2 zones en RETOURNEMENT, volatilité élevée. 18 opportunités mais risque élevé. Action : défensive, privilégier RENT et LONG dans zones stables uniquement."
}
```

---

## Intégration LangGraph

L'agent CIO est un **node** dans le pipeline LangGraph :

```python
def node_generate_brief(state):
    cio = ChiefInvestmentOfficer()
    brief = cio.generate_daily_brief(state['target_date'])
    state['brief_generated'] = True
    return state
```

Position dans le pipeline :
```
compute_scores → generate_brief → send_alerts
```

---

## Fallback

Si l'API OpenAI est indisponible, un brief de secours est généré :

```json
{
  "zones_to_watch": [
    {"zone": "Dubai Marina", "reason": "Volume élevé de transactions"},
    {"zone": "Downtown Dubai", "reason": "Momentum positif"},
    {"zone": "Business Bay", "reason": "Opportunités détectées"}
  ],
  "top_opportunities": [
    {"opp_id": "N/A", "reason": "Voir dashboard pour détails"}
  ],
  "main_risk": "Supply future à surveiller",
  "strategic_recommendation": "Analyser les opportunités FLIP en priorité",
  "full_brief_text": "Brief de secours - LLM indisponible"
}
```

---

## Évolutions futures

### Phase 2

- **Mémoire** : Contexte des briefs précédents
- **Personnalisation** : Adapter selon profil investisseur
- **Prédictions** : Anticiper les mouvements de marché
- **Alertes proactives** : Notifier avant les changements

### Phase 3

- **Multi-agents** : CIO + Analyst + Risk Manager
- **Backtesting** : Évaluer la qualité des recommandations
- **Fine-tuning** : Modèle spécialisé immobilier Dubaï

---

## Monitoring

### Métriques

- Nombre de briefs générés
- Temps de génération (< 30s)
- Taux d'erreur API
- Qualité des recommandations (feedback utilisateur)

### Logs

```
2026-01-16 06:00:00 | INFO | Génération du brief CIO pour 2026-01-16
2026-01-16 06:00:15 | INFO | ✅ Brief CIO généré
```

---

**Dernière mise à jour** : 2026-01-16

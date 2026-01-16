# Logique de scoring

## Vue d'ensemble

Chaque opportunité détectée (transaction sous-valorisée) reçoit **4 scores** :

1. **Score FLIP** (0-100)
2. **Score RENT** (0-100)
3. **Score LONG_TERM** (0-100)
4. **Score GLOBAL** (0-100) : moyenne pondérée

**Recommandation finale** : Stratégie avec le score le plus élevé (ou IGNORE si global < 40)

---

## Stratégie FLIP (achat-revente rapide)

### Objectif
Acheter sous le marché et revendre rapidement (3-12 mois) avec profit.

### Poids des facteurs

| Facteur | Poids | Description |
|---------|-------|-------------|
| **Discount** | 40% | % sous la médiane du marché |
| **Liquidité** | 30% | Volume de transactions (facilité de revente) |
| **Momentum** | 15% | Variation de prix court terme |
| **Régime** | 15% | Régime de marché actuel |

### Calcul détaillé

#### 1. Discount Score (40%)
```
discount_pct >= 30% → 100 points
discount_pct >= 20% → 75 + (discount - 20) * 2.5
discount_pct >= 10% → 50 + (discount - 10) * 2.5
discount_pct < 10%  → discount * 5
```

#### 2. Liquidity Score (30%)
```
tx_count >= 20 → 100 points
tx_count >= 10 → 50 + (count - 10) * 5
tx_count >= 5  → 25 + (count - 5) * 5
tx_count < 5   → count * 5
```

#### 3. Momentum Score (15%)
```
momentum > 10%  → 100 points
momentum > 5%   → 75 points
momentum > 0%   → 50 + momentum * 500
momentum > -5%  → 50 + momentum * 500
momentum < -5%  → 0 points
```

#### 4. Regime Score (15%)
```
EXPANSION     → 90 points
ACCUMULATION  → 80 points
NEUTRAL       → 60 points
DISTRIBUTION  → 50 points
RETOURNEMENT  → 20 points
```

### Pénalités

- **Supply risk HIGH** : -20 points
- **Supply risk MEDIUM** : -10 points
- **Régime RETOURNEMENT** : -15 points

### Score final
```
score_flip = (discount * 0.40 + liquidity * 0.30 + momentum * 0.15 + regime * 0.15) - penalties
score_flip = max(0, min(100, score_flip))
```

---

## Stratégie RENT (cashflow locatif)

### Objectif
Générer un cashflow régulier via la location.

### Poids des facteurs

| Facteur | Poids | Description |
|---------|-------|-------------|
| **Rendement** | 35% | Loyer annuel / Prix d'achat |
| **Stabilité** | 25% | Faible volatilité des prix |
| **Liquidité** | 20% | Volume de transactions |
| **Régime** | 20% | Régime de marché actuel |

### Calcul détaillé

#### 1. Yield Score (35%)
```
yield >= 8%  → 100 points
yield >= 6%  → 70 + (yield - 6) * 15
yield >= 4%  → 40 + (yield - 4) * 15
yield < 4%   → yield * 10
```

**Estimation du rendement** :
```
loyer_estimé_sqft = 100 AED/sqft/an (approximation)
yield = (loyer_annuel / prix_achat) * 100
yield_bonus = discount_pct * 0.05
```

#### 2. Stability Score (25%)
```
volatility < 0.05  → 100 points
volatility < 0.10  → 80 points
volatility < 0.15  → 60 points
volatility < 0.20  → 40 points
volatility >= 0.20 → 20 points
```

#### 3. Liquidity Score (20%)
Même calcul que FLIP

#### 4. Regime Score (20%)
```
DISTRIBUTION  → 80 points
EXPANSION     → 75 points
ACCUMULATION  → 70 points
NEUTRAL       → 70 points
RETOURNEMENT  → 60 points
```

### Pénalités

- **Volatilité > 0.25** : -15 points

### Score final
```
score_rent = (yield * 0.35 + stability * 0.25 + liquidity * 0.20 + regime * 0.20) - penalties
score_rent = max(0, min(100, score_rent))
```

---

## Stratégie LONG_TERM (appréciation du capital)

### Objectif
Acheter pour conserver 3-10 ans et bénéficier de l'appréciation.

### Poids des facteurs

| Facteur | Poids | Description |
|---------|-------|-------------|
| **Régime** | 35% | Phase du marché (ACCUMULATION = best) |
| **Discount** | 30% | Point d'entrée bas |
| **Momentum** | 20% | Tendance long terme |
| **Supply** | 15% | Risque de sur-offre future |

### Calcul détaillé

#### 1. Regime Score (35%)
```
ACCUMULATION  → 100 points
EXPANSION     → 80 points
NEUTRAL       → 60 points
DISTRIBUTION  → 40 points
RETOURNEMENT  → 20 points
```

#### 2. Discount Score (30%)
Même calcul que FLIP

#### 3. Momentum Score (20%)
Même calcul que FLIP

#### 4. Supply Score (15%)
```
supply_risk = LOW     → 100 points
supply_risk = MEDIUM  → 60 points
supply_risk = HIGH    → 20 points
supply_risk = UNKNOWN → 50 points
```

### Pénalités

- **Volatilité > 0.25** : -20 points
- **Volatilité > 0.20** : -10 points
- **Régime RETOURNEMENT** : -25 points
- **Supply risk HIGH** : -15 points

### Score final
```
score_long = (regime * 0.35 + discount * 0.30 + momentum * 0.20 + supply * 0.15) - penalties
score_long = max(0, min(100, score_long))
```

---

## Score GLOBAL

Moyenne pondérée des 3 stratégies :

```
score_global = (score_flip * 0.40 + score_rent * 0.30 + score_long * 0.30)
```

**Pondération** :
- FLIP : 40% (opportunité court terme prioritaire)
- RENT : 30% (cashflow)
- LONG : 30% (appréciation)

---

## Recommandation finale

```python
if score_global < 40:
    recommendation = "IGNORE"
else:
    recommendation = max(
        ("FLIP", score_flip),
        ("RENT", score_rent),
        ("LONG", score_long),
        key=lambda x: x[1]
    )[0]
```

**Seuils** :
- Score < 40 : **IGNORE** (pas assez intéressant)
- Score 40-60 : **Opportunité moyenne**
- Score 60-75 : **Bonne opportunité**
- Score 75+ : **Excellente opportunité**

---

## Exemples

### Exemple 1 : FLIP
```
Discount : 25% → 75 points
Liquidité : 15 tx → 75 points
Momentum : +8% → 100 points
Régime : EXPANSION → 90 points
Supply risk : LOW → pas de pénalité

Score FLIP = 75*0.4 + 75*0.3 + 100*0.15 + 90*0.15 = 81 points
Recommandation : FLIP
```

### Exemple 2 : RENT
```
Yield : 7% → 85 points
Stabilité : volatilité 0.08 → 80 points
Liquidité : 12 tx → 60 points
Régime : DISTRIBUTION → 80 points

Score RENT = 85*0.35 + 80*0.25 + 60*0.20 + 80*0.20 = 78 points
Recommandation : RENT
```

### Exemple 3 : LONG_TERM
```
Régime : ACCUMULATION → 100 points
Discount : 18% → 70 points
Momentum : +3% → 65 points
Supply : LOW → 100 points
Volatilité : 0.12 → pas de pénalité

Score LONG = 100*0.35 + 70*0.30 + 65*0.20 + 100*0.15 = 79 points
Recommandation : LONG
```

---

## Calibration

Les seuils et poids peuvent être ajustés selon :
- Retours utilisateurs
- Performance historique
- Conditions de marché
- Objectifs d'investissement

**Fichiers à modifier** :
- `strategies/flip.py`
- `strategies/rent.py`
- `strategies/long_term.py`

---

**Dernière mise à jour** : 2026-01-16

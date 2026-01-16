# Guidelines UX Mobile-First

## Principe fondamental

**70% des utilisateurs sont sur iPhone** → L'expérience mobile est prioritaire.

---

## Règles de design

### 1. Layout vertical

✅ **BON** :
```
┌─────────────┐
│   Header    │
├─────────────┤
│   Card 1    │
├─────────────┤
│   Card 2    │
├─────────────┤
│   Card 3    │
└─────────────┘
```

❌ **MAUVAIS** :
```
┌────────┬────────┬────────┐
│ Col 1  │ Col 2  │ Col 3  │
└────────┴────────┴────────┘
```

### 2. Cards empilées

Chaque élément d'information = 1 card :
- Background blanc
- Padding 1rem
- Border-radius 0.5rem
- Box-shadow légère
- Margin-bottom 1rem

### 3. Pas de tables larges

❌ **Éviter** :
```
| Community | Building | Rooms | Price | Sqft | Discount | Score |
```

✅ **Préférer** :
```
┌─────────────────────────┐
│ Dubai Marina / Tower A  │
│ 2BR • 1,200 sqft        │
│ 💰 1,800 AED/sqft       │
│ 📉 15% sous marché      │
│ 🎯 Score: 75            │
└─────────────────────────┘
```

### 4. Filtres simples

- Maximum 3 filtres visibles
- Dropdowns plutôt que multi-select
- Bouton "Reset" visible
- Pas de filtres complexes (ranges multiples, etc.)

### 5. Graphiques courts

- Hauteur max : 300-400px
- Légendes horizontales
- Peu de séries (max 3)
- Couleurs contrastées
- Pas de texte trop petit

### 6. Lecture rapide

Chaque écran doit être lisible en **< 30 secondes** :
- Titre clair
- 3-5 KPIs max
- 5-10 éléments de liste max
- Pagination si nécessaire

---

## Composants Streamlit

### Metrics

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Transactions", 42, delta="+5")

with col2:
    st.metric("Prix moyen", "1,850 AED")

with col3:
    st.metric("Score", "75", delta="+3")
```

### Cards

```python
with st.container():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Dubai Marina / Tower A**")
        st.caption("2BR • 1,200 sqft")
    
    with col2:
        st.metric("Score", "75")
    
    st.markdown("---")
```

### Expanders

```python
with st.expander("📊 Détails"):
    st.write("Contenu détaillé ici")
```

### Tabs

```python
tab1, tab2, tab3 = st.tabs(["Vue 1", "Vue 2", "Vue 3"])

with tab1:
    st.write("Contenu 1")
```

---

## Couleurs

### Palette principale

- **Vert** : `#10b981` (succès, ACCUMULATION, bon score)
- **Bleu** : `#3b82f6` (info, EXPANSION, neutre)
- **Jaune** : `#f59e0b` (warning, DISTRIBUTION, moyen)
- **Rouge** : `#ef4444` (danger, RETOURNEMENT, mauvais)
- **Gris** : `#6b7280` (NEUTRAL, secondaire)

### Badges

```python
# Succès
st.markdown('<span class="badge badge-success">✅ Bon</span>', unsafe_allow_html=True)

# Warning
st.markdown('<span class="badge badge-warning">⚠️ Moyen</span>', unsafe_allow_html=True)

# Danger
st.markdown('<span class="badge badge-danger">❌ Risque</span>', unsafe_allow_html=True)
```

---

## Emojis

Utiliser des emojis pour la lecture rapide :

| Contexte | Emoji |
|----------|-------|
| Prix | 💰 |
| Discount | 📉 |
| Score | 🎯 |
| Régime | 📊 |
| Liquidité | 💧 |
| Stratégie FLIP | ⚡ |
| Stratégie RENT | 💵 |
| Stratégie LONG | 📈 |
| Alerte critique | 🔴 |
| Alerte haute | 🟠 |
| Alerte moyenne | 🟡 |
| Succès | 🟢 |
| Zone | 📍 |
| Date | 📅 |
| Volume | 📈 |

---

## Responsive CSS

```css
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem 0.5rem;
        max-width: 100%;
    }
    
    h1 {
        font-size: 1.5rem !important;
    }
    
    h2 {
        font-size: 1.2rem !important;
    }
    
    h3 {
        font-size: 1rem !important;
    }
    
    .stMetric {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
}
```

---

## Navigation

### Sidebar

- Fermée par défaut sur mobile (`initial_sidebar_state="collapsed"`)
- Menu hamburger (☰) visible
- Sections claires

### Boutons

- `use_container_width=True` pour boutons pleine largeur
- Icônes + texte
- Couleurs distinctes pour actions principales

---

## Performance

### Auto-refresh

```python
from streamlit_autorefresh import st_autorefresh

# Refresh toutes les 5 minutes
st_autorefresh(interval=5 * 60 * 1000, key="refresh")
```

### Cache

```python
@st.cache_data(ttl=600)  # 10 minutes
def get_data():
    return expensive_query()
```

### Lazy loading

- Charger les données à la demande
- Utiliser des expanders pour contenu lourd
- Pagination pour grandes listes

---

## Accessibilité

- Contraste minimum 4.5:1
- Taille de police >= 14px
- Zones cliquables >= 44x44px
- Texte alternatif pour images
- Pas de dépendance à la couleur seule

---

## Tests mobile

### Outils

1. **Chrome DevTools** : F12 → Toggle device toolbar
2. **iPhone réel** : Tester sur iPhone 12/13/14
3. **Responsive design mode** : Firefox

### Checklist

- [ ] Scroll fluide
- [ ] Pas de débordement horizontal
- [ ] Boutons cliquables facilement
- [ ] Texte lisible sans zoom
- [ ] Graphiques interactifs
- [ ] Filtres fonctionnels
- [ ] Auto-refresh fonctionne
- [ ] Pas de lag

---

## Exemples de pages

### Dashboard (mobile)

```
┌─────────────────────────┐
│ 📊 Dashboard            │
├─────────────────────────┤
│ [Date selector]         │
├─────────────────────────┤
│ ┌─────┬─────┬─────┐    │
│ │ 42  │1850 │ 12  │    │
│ │ Tx  │Prix │Opps │    │
│ └─────┴─────┴─────┘    │
├─────────────────────────┤
│ 🎯 Brief CIO            │
│ • Zone 1 : raison       │
│ • Zone 2 : raison       │
│ • Zone 3 : raison       │
├─────────────────────────┤
│ 💎 Top Opportunités     │
│ ┌─────────────────────┐ │
│ │ Dubai Marina        │ │
│ │ 2BR • 15% discount  │ │
│ │ Score: 75           │ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ Downtown Dubai      │ │
│ │ 1BR • 12% discount  │ │
│ │ Score: 68           │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

---

## Anti-patterns

❌ **À ÉVITER** :

1. Tables larges avec scroll horizontal
2. Graphiques trop complexes (> 5 séries)
3. Texte < 12px
4. Boutons < 40px de hauteur
5. Formulaires longs (> 5 champs)
6. Popups modales
7. Tooltips au hover (pas de hover sur mobile)
8. Animations lourdes
9. Images non optimisées
10. Dépendance au clavier

---

**Dernière mise à jour** : 2026-01-16

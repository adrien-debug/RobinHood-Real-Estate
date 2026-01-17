# 🔑 Configuration des APIs Dubai Pulse (DLD)

Ce guide explique comment obtenir et configurer les clés API pour accéder aux données officielles du Dubai Land Department via Dubai Pulse.

---

## 📋 Prérequis

- Compte sur Dubai Pulse
- Autorisation pour accéder aux datasets DLD
- Variables d'environnement configurées

---

## 🚀 Étape 1 : Créer un compte Dubai Pulse

1. **Aller sur** : https://www.dubaipulse.gov.ae
2. **Cliquer sur** : "Sign Up" ou "Register"
3. **Remplir le formulaire** avec :
   - Nom complet
   - Email professionnel
   - Organisation
   - Raison de l'utilisation des données
4. **Valider** votre email

---

## 🔓 Étape 2 : Demander l'accès aux datasets DLD

### Datasets nécessaires pour l'application :

| Dataset | URL | Description |
|---------|-----|-------------|
| **dld_transactions-open-api** | [Lien](https://www.dubaipulse.gov.ae/data/dld-transactions/dld_transactions-open-api) | Transactions immobilières (ventes, hypothèques) |
| **dld_buildings-open-api** | [Lien](https://www.dubaipulse.gov.ae/data/dld-registration/dld_buildings-open-api) | Bâtiments et projets |
| **dld_valuation-open-api** | [Lien](https://www.dubaipulse.gov.ae/data/dld-valuations/dld_valuation-open-api) | Évaluations de propriétés |
| **dld_lkp_areas-open-api** | [Lien](https://www.dubaipulse.gov.ae/data/dld-transactions/dld_lkp_areas-open-api) | Liste des zones/communautés |

### Pour chaque dataset :

1. **Cliquer sur** : "Request Permission" ou "Get Access"
2. **Remplir le formulaire** :
   - Raison de l'utilisation
   - Type d'application (Business Intelligence / Real Estate Analytics)
   - Fréquence d'utilisation prévue
3. **Soumettre** la demande
4. **Attendre** l'approbation (généralement 1-3 jours ouvrés)

---

## 🔐 Étape 3 : Obtenir les clés API

Une fois approuvé, vous recevrez par email :

- **Client ID** (API Key)
- **Client Secret** (API Secret)

**⚠️ IMPORTANT** : Ne partagez JAMAIS ces clés publiquement !

---

## ⚙️ Étape 4 : Configuration locale

### 4.1 Créer le fichier `.env`

```bash
cd /path/to/Robin
cp env.example .env
```

### 4.2 Éditer `.env`

```bash
# DLD API (Dubai Pulse)
DLD_API_KEY=votre_client_id_ici
DLD_API_SECRET=votre_client_secret_ici
DLD_API_BASE_URL=https://api.dubaipulse.gov.ae
```

### 4.3 Tester la connexion

```bash
python -c "from connectors.dld_transactions import DLDTransactionsConnector; c = DLDTransactionsConnector(); print('✅ Connexion OK' if c.auth.get_access_token() else '❌ Erreur')"
```

---

## ☁️ Étape 5 : Configuration Streamlit Cloud

### 5.1 Aller dans les secrets

1. **Ouvrir** : https://share.streamlit.io/
2. **Sélectionner** votre app
3. **Cliquer** : Settings → Secrets

### 5.2 Ajouter les secrets

```toml
# Database
DATABASE_URL = "postgresql://postgres.xxx:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
TABLE_PREFIX = "dld_"

# DLD API (Dubai Pulse)
DLD_API_KEY = "votre_client_id_ici"
DLD_API_SECRET = "votre_client_secret_ici"
DLD_API_BASE_URL = "https://api.dubaipulse.gov.ae"

# OpenAI (optionnel, pour agent CIO)
OPENAI_API_KEY = "sk-..."

# Timezone
TIMEZONE = "Asia/Dubai"
```

### 5.3 Redémarrer l'app

1. **Cliquer** : "Save"
2. **Cliquer** : "Reboot app"
3. **Attendre** 60-90 secondes

---

## ✅ Étape 6 : Vérification

### Dans l'application Streamlit :

1. **Aller dans** : Admin → Admin Data
2. **Cliquer** : "Exécuter pipeline complet"
3. **Observer les logs** :
   - ✅ `Token OAuth obtenu` → Authentification OK
   - ✅ `X transactions DLD récupérées` → Données réelles chargées
   - ⚠️ `Fallback sur données MOCK` → Problème de connexion

### Logs attendus (succès) :

```
🔄 Récupération transactions DLD : 2026-01-16 → 2026-01-17
✅ Token OAuth obtenu (expire dans 3600s)
✅ 1247 transactions DLD récupérées
```

---

## 🔧 Dépannage

### Erreur : "Token non reçu"

**Cause** : Clés API invalides

**Solution** :
- Vérifier que `DLD_API_KEY` et `DLD_API_SECRET` sont corrects
- Vérifier qu'il n'y a pas d'espaces avant/après les clés
- Régénérer les clés sur Dubai Pulse si nécessaire

### Erreur : "403 Forbidden"

**Cause** : Accès non autorisé au dataset

**Solution** :
- Vérifier que la demande d'accès a été approuvée
- Attendre l'email de confirmation
- Contacter le support Dubai Pulse si > 5 jours

### Erreur : "429 Too Many Requests"

**Cause** : Rate limit dépassé

**Solution** :
- Réduire la fréquence des requêtes
- Augmenter `POLLING_INTERVAL_MINUTES` dans `.env`
- Attendre quelques minutes avant de réessayer

### Mode MOCK actif

**Symptôme** : L'app affiche `⚠️ Clés API DLD non configurées - utilisation de données MOCK`

**Solution** :
- Vérifier que les secrets sont bien configurés
- Redémarrer l'app Streamlit
- Vérifier les logs pour voir l'erreur exacte

---

## 📊 Datasets disponibles

### Transactions (dld_transactions-open-api)

**Champs principaux** :
- `trans_date` : Date de transaction
- `trans_group_en` : Type (Sales, Mortgage, Gift, etc.)
- `area_name_en` : Communauté
- `project_en` : Projet
- `building_name_en` : Bâtiment
- `rooms_en` : Nombre de chambres
- `actual_area` : Surface (sqft)
- `trans_value` : Prix (AED)

**Limite** : 10,000 résultats par requête

### Buildings (dld_buildings-open-api)

**Champs principaux** :
- `building_name_en` : Nom du bâtiment
- `area_name_en` : Communauté
- `project_en` : Projet
- `building_type_en` : Type
- `nearest_metro_en` : Métro le plus proche

**Limite** : 5,000 résultats par requête

---

## 📞 Support

### Dubai Pulse Support
- **Email** : support@dubaipulse.gov.ae
- **Website** : https://www.dubaipulse.gov.ae/support

### Documentation API
- **Base** : https://www.dubaipulse.gov.ae/data
- **OAuth** : https://www.dubaipulse.gov.ae/docs/authentication

---

## 🔒 Sécurité

### ✅ À FAIRE :
- Stocker les clés dans `.env` (local) ou Secrets (cloud)
- Ajouter `.env` dans `.gitignore`
- Utiliser HTTPS uniquement
- Régénérer les clés si compromises

### ❌ NE JAMAIS :
- Commiter les clés dans Git
- Partager les clés publiquement
- Exposer les clés dans le frontend
- Logger les clés dans les fichiers de log

---

## 📈 Limites et quotas

| Ressource | Limite |
|-----------|--------|
| Requêtes par minute | 60 |
| Requêtes par jour | 10,000 |
| Résultats par requête | 10,000 |
| Taille réponse max | 50 MB |

**Conseil** : Implémenter un cache pour réduire les appels API.

---

**Dernière mise à jour** : 2026-01-17

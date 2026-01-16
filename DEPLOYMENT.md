# 🚀 Déploiement Streamlit Cloud

## Configuration des Secrets

L'application nécessite une configuration des secrets dans Streamlit Cloud pour se connecter à Supabase.

### Étapes :

1. **Allez sur Streamlit Cloud**
   - URL : https://share.streamlit.io/
   - Trouvez votre app : `adrien-debug-robinhood-real-estate-app-5mafql`

2. **Accédez aux Secrets**
   - Cliquez sur **"Manage app"** (en bas à droite de l'app)
   - Allez dans **⚙️ Settings** → **Secrets**

3. **Ajoutez la configuration suivante :**

```toml
DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:[VOTRE_PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
OPENAI_API_KEY = "sk-[VOTRE_CLE]"
```

4. **Trouvez votre mot de passe Supabase :**
   - Allez sur : https://supabase.com/dashboard/project/tnnsfheflydiuhiduntn/settings/database
   - Si vous ne connaissez pas le mot de passe, cliquez sur **"Reset database password"**
   - Copiez le nouveau mot de passe et mettez-le dans `DATABASE_URL`

5. **Sauvegardez et Redémarrez**
   - Cliquez **"Save"**
   - Cliquez **"Reboot app"**

---

## Architecture

L'application utilise :
- **Supabase** : Base de données PostgreSQL hébergée
- **Schéma `robin`** : Vues qui mappent les tables `dld_*` vers les noms attendus par l'app
- **psycopg3** : Driver PostgreSQL compatible Python 3.13
- **Streamlit Cloud** : Hébergement de l'application

### Tables Supabase

Les tables sont préfixées avec `dld_` dans Supabase :
- `dld_transactions` → vue `robin.transactions`
- `dld_market_baselines` → vue `robin.market_baselines`
- `dld_market_regimes` → vue `robin.market_regimes`
- `dld_opportunities` → vue `robin.opportunities`
- `dld_alerts` → vue `robin.alerts`
- `dld_daily_briefs` → vue `robin.daily_briefs`

Le code utilise `SET search_path TO robin, public` pour accéder aux vues automatiquement.

---

## Vérification du Déploiement

Une fois les secrets configurés, l'application devrait :
1. ✅ Se connecter à Supabase
2. ✅ Utiliser le schéma `robin` automatiquement
3. ✅ Afficher le Dashboard sans erreur

Si vous voyez encore des erreurs, vérifiez :
- Le mot de passe Supabase est correct
- L'URL de connexion utilise le **pooler** (port 6543)
- Les secrets sont bien sauvegardés dans Streamlit Cloud

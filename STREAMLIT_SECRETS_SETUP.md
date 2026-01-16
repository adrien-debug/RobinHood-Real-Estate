# 🔐 Configuration des Secrets Streamlit Cloud

## ⚠️ IMPORTANT : Action Manuelle Requise

Streamlit Cloud n'a pas d'API pour configurer les secrets automatiquement. Vous devez les ajouter manuellement via l'interface web.

---

## 📋 Étapes Détaillées

### 1. Obtenez votre mot de passe Supabase

**Option A : Vous connaissez déjà le mot de passe**
- Passez à l'étape 2

**Option B : Réinitialisez le mot de passe**
1. Allez sur : https://supabase.com/dashboard/project/tnnsfheflydiuhiduntn/settings/database
2. Cliquez sur **"Reset database password"**
3. Copiez le nouveau mot de passe généré
4. ⚠️ **IMPORTANT** : Sauvegardez-le dans un endroit sûr (gestionnaire de mots de passe)

---

### 2. Configurez Streamlit Cloud

1. **Accédez à votre app**
   - URL : https://share.streamlit.io/
   - Ou directement : https://adrien-debug-robinhood-real-estate-app-5mafql.streamlit.app/

2. **Ouvrez les paramètres**
   - Cliquez sur **"Manage app"** (bouton en bas à droite)
   - Cliquez sur **⚙️ Settings** dans le menu de gauche
   - Cliquez sur **Secrets**

3. **Collez cette configuration** (remplacez les valeurs entre crochets) :

```toml
# Base de données Supabase
DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:[VOTRE_PASSWORD_SUPABASE]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

# OpenAI (optionnel - pour le CIO AI)
OPENAI_API_KEY = "sk-[VOTRE_CLE_OPENAI]"

# Configuration optionnelle
TABLE_PREFIX = "dld_"
TIMEZONE = "Asia/Dubai"
```

4. **Sauvegardez**
   - Cliquez sur **"Save"**
   - Attendez la confirmation

5. **Redémarrez l'app**
   - Cliquez sur **"Reboot app"**
   - Attendez 30-60 secondes

---

## ✅ Vérification

Une fois configuré, allez sur votre app :
- https://adrien-debug-robinhood-real-estate-app-5mafql.streamlit.app/

Vous devriez voir :
- ✅ Dashboard qui charge sans erreur
- ✅ 5 transactions de test affichées
- ✅ Brief CIO du jour
- ✅ Toutes les pages fonctionnelles

---

## 🐛 Dépannage

### Erreur : "psycopg.OperationalError"
➡️ Le `DATABASE_URL` n'est pas configuré ou est incorrect
- Vérifiez que vous avez bien sauvegardé les secrets
- Vérifiez que le mot de passe est correct (pas d'espaces)
- Redémarrez l'app après modification

### Erreur : "relation does not exist"
➡️ Le schéma `robin` n'est pas créé dans Supabase
- Le schéma a été créé automatiquement
- Vérifiez la connexion à la bonne base de données

### L'app affiche "Aucune transaction"
➡️ Normal si vous n'avez pas encore de vraies données
- 5 transactions de test ont été insérées
- Utilisez la page **Admin Data** pour générer plus de données

---

## 📊 Données de Test

J'ai déjà inséré dans Supabase :
- ✅ 5 transactions de test (Dubai Marina, Downtown, JBR, Palm, Business Bay)
- ✅ 1 brief CIO pour aujourd'hui
- ✅ Schéma `robin` avec toutes les vues

---

## 🚀 Prochaines Étapes

Une fois l'app déployée :
1. Testez toutes les pages
2. Utilisez **Admin Data** pour :
   - Initialiser le schéma complet
   - Générer des données MOCK
   - Exécuter le pipeline quotidien
3. Configurez l'OPENAI_API_KEY pour activer le CIO AI

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs dans Streamlit Cloud (Manage app > Logs)
2. Vérifiez que Supabase est accessible
3. Testez la connexion localement d'abord

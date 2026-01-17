# 🚀 Configuration Streamlit Cloud - Instructions Pas à Pas

## ⚠️ ACTION REQUISE MAINTENANT

Ton app Streamlit Cloud ne peut pas se connecter à la base de données car **DATABASE_URL n'est pas configuré**.

---

## 📋 Étapes à suivre (5 minutes)

### 1️⃣ Ouvre les paramètres Streamlit Cloud

1. Va sur : https://share.streamlit.io/
2. Trouve ton app **robinhood-real-estate**
3. Clique sur **"Manage app"** (bouton en bas à droite de l'app)
4. Dans le menu de gauche, clique sur **⚙️ Settings**
5. Clique sur l'onglet **Secrets**

---

### 2️⃣ Copie-colle cette configuration

**COPIE EXACTEMENT CECI** dans la zone de texte des secrets :

```toml
DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:IvVcjJbr3pl/zSBHT5gltczPtZFV4US7RXMjALiJomv518VZMq57m2ruFrMPhj4yRdiZQLIEnuoQzbFnngdDAQ==@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
TABLE_PREFIX = "dld_"
TIMEZONE = "Asia/Dubai"
```

---

### 3️⃣ Sauvegarde et redémarre

1. Clique sur **"Save"** (en bas de la page)
2. Attends la confirmation "Secrets saved successfully"
3. Clique sur **"Reboot app"** (dans le menu de gauche)
4. Attends 30-60 secondes

---

### 4️⃣ Vérifie que ça marche

1. Retourne sur ton app : https://adrien-debug-robinhood-real-estate-app-5mafql.streamlit.app/
2. Tu devrais voir le Dashboard se charger
3. Si tu vois encore une erreur, passe à l'étape suivante

---

## 🔧 Si ça ne marche toujours pas

Le mot de passe contient un `/` qui peut poser problème. Utilise cette version **encodée** :

```toml
DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:IvVcjJbr3pl%2FzSBHT5gltczPtZFV4US7RXMjALiJomv518VZMq57m2ruFrMPhj4yRdiZQLIEnuoQzbFnngdDAQ%3D%3D@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
TABLE_PREFIX = "dld_"
TIMEZONE = "Asia/Dubai"
```

(Remplace `/` par `%2F` et `=` par `%3D`)

Puis :
1. **Save**
2. **Reboot app**
3. Attends 30-60 secondes

---

## ✅ Checklist

- [ ] J'ai ouvert Streamlit Cloud > Manage app > Settings > Secrets
- [ ] J'ai copié-collé la configuration DATABASE_URL
- [ ] J'ai cliqué sur "Save"
- [ ] J'ai cliqué sur "Reboot app"
- [ ] J'ai attendu 60 secondes
- [ ] L'app charge maintenant sans erreur

---

## 📸 Capture d'écran de référence

Voici où tu dois aller :

```
https://share.streamlit.io/
  └─ Ton app
      └─ Manage app (bouton en bas à droite)
          └─ ⚙️ Settings (menu gauche)
              └─ Secrets (onglet)
                  └─ [Zone de texte pour coller la config]
                  └─ [Bouton "Save"]
```

---

## 🆘 Dépannage

### Erreur : "psycopg.OperationalError"
✅ **Solution** : DATABASE_URL pas configuré ou incorrect
→ Vérifie que tu as bien copié-collé la config complète

### Erreur : "password authentication failed"
✅ **Solution** : Mot de passe incorrect
→ Utilise la version encodée (avec %2F et %3D)

### Erreur : "could not translate host name"
✅ **Solution** : URL mal formatée
→ Vérifie qu'il n'y a pas d'espaces ou de retours à la ligne dans DATABASE_URL

### L'app ne redémarre pas
✅ **Solution** : 
→ Clique sur "Reboot app" dans le menu de gauche
→ Attends 60 secondes
→ Rafraîchis la page de l'app

---

## 🎯 Résultat attendu

Une fois configuré, tu devrais voir :

- ✅ Dashboard qui charge
- ✅ KPIs affichés (même si à 0)
- ✅ Section "Brief CIO"
- ✅ Toutes les pages accessibles

---

## 📞 Si tu es bloqué

1. Vérifie les logs : Manage app > Logs
2. Cherche "Connexion PostgreSQL établie" (= succès)
3. Ou cherche "Erreur connexion DB" (= échec)

---

**⏱️ Temps estimé : 5 minutes**

**🔒 Note de sécurité** : Les secrets Streamlit sont chiffrés et ne sont jamais exposés publiquement.

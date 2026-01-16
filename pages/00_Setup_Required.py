"""
Page de configuration - Affichée si DATABASE_URL n'est pas configuré
"""
import streamlit as st
from core.config import settings

st.set_page_config(
    page_title="Configuration Requise",
    page_icon="⚙️",
    layout="wide"
)

# Vérifier si DATABASE_URL est configuré
is_configured = (
    settings.database_url != "postgresql://user:password@localhost:5432/dubai_real_estate"
    and "localhost" not in settings.database_url
)

if not is_configured:
    st.error("🔐 Configuration de la Base de Données Requise")
    
    st.markdown("""
    ## ⚠️ DATABASE_URL Non Configuré
    
    L'application nécessite une connexion à Supabase pour fonctionner.
    
    ### 📋 Étapes de Configuration :
    
    1. **Accédez aux Secrets Streamlit Cloud**
       - Cliquez sur **"Manage app"** (en bas à droite)
       - Allez dans **⚙️ Settings** → **Secrets**
    
    2. **Obtenez votre Connection String Supabase**
       - Allez sur : https://supabase.com/dashboard/project/tnnsfheflydiuhiduntn/settings/database
       - Copiez le "Connection string (URI)" sous "Connection pooling"
       - Si vous ne connaissez pas le mot de passe, cliquez "Reset database password"
    
    3. **Ajoutez cette configuration** (remplacez `[PASSWORD]`) :
    
    ```toml
    DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
    OPENAI_API_KEY = "sk-[YOUR_KEY]"
    ```
    
    4. **Sauvegardez et Redémarrez**
       - Cliquez **"Save"**
       - Cliquez **"Reboot app"**
    
    ---
    
    ### 📖 Documentation Complète
    
    Consultez les fichiers suivants dans le repo GitHub :
    - `STREAMLIT_SECRETS_SETUP.md` - Guide détaillé
    - `DEPLOYMENT.md` - Architecture et déploiement
    - `DEPLOYMENT_STATUS.md` - Statut complet
    
    ### 🔗 Liens Utiles
    
    - [Supabase Dashboard](https://supabase.com/dashboard/project/tnnsfheflydiuhiduntn)
    - [GitHub Repo](https://github.com/adrien-debug/RobinHood-Real-Estate)
    - [Streamlit Cloud](https://share.streamlit.io/)
    
    ---
    
    ### ✅ Vérification
    
    Une fois configuré, cette page disparaîtra et vous verrez le Dashboard.
    """)
    
    st.info("💡 **Astuce** : L'application fonctionne parfaitement en local. Cette configuration est uniquement nécessaire pour Streamlit Cloud.")

else:
    st.success("✅ DATABASE_URL Configuré !")
    st.markdown("""
    La base de données est correctement configurée.
    
    Utilisez le menu latéral pour accéder aux différentes sections :
    - 📊 **Dashboard** : Vue d'ensemble + Brief CIO
    - 🏠 **Ventes du jour** : Transactions récentes
    - 🎯 **Deal Radar** : Opportunités scorées
    - 📍 **Zones / Buildings** : Analyse par localisation
    - 🔔 **Alertes** : Notifications actives
    - ⚙️ **Admin Data** : Gestion des données
    """)

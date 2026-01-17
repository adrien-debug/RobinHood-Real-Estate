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
    """)
    
    # Instructions détaillées avec le mot de passe
    st.markdown("### 📋 Configuration Rapide (5 minutes)")
    
    st.markdown("""
    **1️⃣ Ouvre les paramètres Streamlit Cloud**
    - Clique sur **"Manage app"** (bouton en bas à droite)
    - Va dans **⚙️ Settings** → **Secrets**
    """)
    
    st.markdown("**2️⃣ Copie-colle EXACTEMENT cette configuration :**")
    
    config_code = '''DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
TABLE_PREFIX = "dld_"
TIMEZONE = "Asia/Dubai"'''
    
    st.code(config_code, language="toml")
    
    st.markdown("""
    **3️⃣ Sauvegarde et redémarre**
    - Clique sur **"Save"**
    - Clique sur **"Reboot app"**
    - Attends 60 secondes
    """)
    
    st.warning("""
    ⚠️ **Si ça ne marche pas** : Le mot de passe contient un `/` qui peut poser problème.
    
    Utilise cette version encodée à la place :
    """)
    
    config_code_encoded = '''DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:[PASSWORD_URL_ENCODED]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
TABLE_PREFIX = "dld_"
TIMEZONE = "Asia/Dubai"'''
    
    st.code(config_code_encoded, language="toml")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 Documentation Complète
    
    Consultez `STREAMLIT_CLOUD_CONFIG.md` dans le repo pour plus de détails.
    
    ### 🔗 Liens Utiles
    
    - [Supabase Dashboard](https://supabase.com/dashboard/project/tnnsfheflydiuhiduntn)
    - [Streamlit Cloud](https://share.streamlit.io/)
    
    ---
    
    ### ✅ Vérification
    
    Une fois configuré, cette page disparaîtra et tu verras le Dashboard.
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

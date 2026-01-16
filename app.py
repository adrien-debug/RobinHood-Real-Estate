"""
DUBAI REAL ESTATE INTELLIGENCE
Application Streamlit - Page principale
"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from core.config import settings
from core.utils import setup_logging

# Configuration de la page (MOBILE-FIRST)
st.set_page_config(
    page_title="Dubai Real Estate Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar fermée par défaut (mobile)
)

# Auto-refresh (toutes les 5 minutes)
st_autorefresh(interval=5 * 60 * 1000, key="main_refresh")

# Setup logging
setup_logging()

# Check if DATABASE_URL is configured (Streamlit Cloud)
is_cloud = "streamlit" in str(st.__file__).lower() or "mount/src" in str(st.__file__).lower()
is_configured = (
    settings.database_url != "postgresql://user:password@localhost:5432/dubai_real_estate"
    and "localhost" not in settings.database_url
)

if is_cloud and not is_configured:
    st.error("⚙️ Configuration Requise")
    st.markdown("""
    ### 🔐 DATABASE_URL Non Configuré
    
    L'application nécessite une connexion à Supabase.
    
    **Étapes :**
    1. Cliquez "Manage app" → Settings → Secrets
    2. Ajoutez : `DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"`
    3. Obtenez le mot de passe sur : https://supabase.com/dashboard/project/tnnsfheflydiuhiduntn/settings/database
    4. Cliquez "Save" puis "Reboot app"
    
    📖 **Guide complet** : Voir `STREAMLIT_SECRETS_SETUP.md` sur GitHub
    """)
    st.stop()

# CSS MOBILE-FIRST
st.markdown("""
<style>
    /* Mobile-first : optimisation pour iPhone */
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
    
    /* Cards */
    .card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .badge-success {
        background-color: #10b981;
        color: white;
    }
    
    .badge-warning {
        background-color: #f59e0b;
        color: white;
    }
    
    .badge-danger {
        background-color: #ef4444;
        color: white;
    }
    
    .badge-info {
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🏢 Dubai Real Estate Intelligence")
st.caption("Plateforme d'intelligence immobilière institutionnelle - Mobile-first")

# Navigation
st.markdown("---")

st.markdown("""
### 📱 Navigation

Utilisez le menu latéral (☰) pour accéder aux différentes sections :

- **📊 Dashboard** : Vue d'ensemble + Brief CIO
- **🏠 Ventes du jour** : Transactions récentes
- **📍 Zones / Buildings** : Analyse par localisation
- **🎯 Deal Radar** : Opportunités scorées
- **💰 Location & Yield** : Rendements locatifs
- **🔔 Alertes** : Notifications actives
- **⚙️ Admin** : Gestion des données

---

### 🚀 Démarrage rapide

1. **Initialiser la base de données** (première utilisation)
2. **Exécuter le pipeline quotidien** (collecte + analyse)
3. **Consulter le Dashboard** pour le brief CIO

---

### 📖 Documentation

- **Sources de données** : DLD Transactions, Mortgages, Rental Index
- **Scoring** : Multi-stratégies (FLIP, RENT, LONG_TERM)
- **Régimes de marché** : ACCUMULATION, EXPANSION, DISTRIBUTION, RETOURNEMENT
- **Agent CIO** : Brief quotidien automatique

---

### ⚡ Actions rapides
""")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

with col2:
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/01_Dashboard.py")

with col3:
    if st.button("🎯 Deals", use_container_width=True):
        st.switch_page("pages/04_Deal_Radar.py")

st.markdown("---")

# Footer
st.caption(f"""
🌐 Timezone: {settings.timezone}  
🔄 Auto-refresh: {settings.polling_interval_minutes} min  
📡 Status: ✅ Opérationnel
""")

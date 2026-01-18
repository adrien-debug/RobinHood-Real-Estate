"""
Configuration centralisée
Compatible avec Streamlit Cloud secrets et variables d'environnement locales
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = "") -> str:
    """
    Récupère une valeur de configuration depuis:
    1. Streamlit secrets (pour Streamlit Cloud)
    2. Variables d'environnement (pour dev local)
    3. Valeur par défaut
    """
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # Fall back to environment variables
    return os.getenv(key, default)


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Database
    database_url: str = get_secret("DATABASE_URL", "postgresql://user:password@localhost:5432/dubai_real_estate")
    
    # Table prefix (empty for local, "dld_" for Supabase)
    table_prefix: str = get_secret("TABLE_PREFIX", "")
    
    # OpenAI
    openai_api_key: str = get_secret("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4-turbo-preview"
    
    # DLD API (Dubai Pulse)
    dld_api_key: str = get_secret("DLD_API_KEY", "")  # Client ID
    dld_api_secret: str = get_secret("DLD_API_SECRET", "")  # Client Secret
    dld_api_base_url: str = get_secret("DLD_API_BASE_URL", "https://api.dubaipulse.gov.ae")
    
    # Bayut API via RapidAPI (lead indicators + transactions DLD)
    bayut_api_key: str = get_secret("BAYUT_API_KEY", "")
    bayut_api_url: str = get_secret("BAYUT_API_URL", "https://uae-real-estate2.p.rapidapi.com")
    
    # PropertyFinder API via RapidAPI
    propertyfinder_api_key: str = get_secret("PROPERTYFINDER_API_KEY", "")
    
    # Zyla Labs UAE Real Estate API
    zylalabs_api_key: str = get_secret("ZYLALABS_API_KEY", "")
    
    # UAE Real Estate Data-Real Time API via RapidAPI
    uae_realtime_api_key: str = get_secret("UAE_REALTIME_API_KEY", "")
    
    # Makani Geocoding (Dubai Municipality)
    makani_api_key: str = get_secret("MAKANI_API_KEY", "")
    makani_api_url: str = get_secret("MAKANI_API_URL", "https://api.dubaipulse.gov.ae/makani")
    
    # DDA Planning & Zoning
    dda_api_key: str = get_secret("DDA_API_KEY", "")
    dda_api_url: str = get_secret("DDA_API_URL", "https://api.dm.gov.ae/v1")
    
    # Listings API (legacy - remplacé par Bayut)
    listings_api_key: str = get_secret("LISTINGS_API_KEY", "")
    listings_api_url: str = get_secret("LISTINGS_API_URL", "")
    
    # Developers API
    developers_api_key: str = get_secret("DEVELOPERS_API_KEY", "")
    
    # Refresh
    polling_interval_minutes: int = int(get_secret("POLLING_INTERVAL_MINUTES", "15"))
    cache_ttl_minutes: int = int(get_secret("CACHE_TTL_MINUTES", "10"))
    
    # Alertes
    alert_email: Optional[str] = get_secret("ALERT_EMAIL") or None
    alert_webhook_url: Optional[str] = get_secret("ALERT_WEBHOOK_URL") or None
    
    # Timezone
    timezone: str = get_secret("TIMEZONE", "Asia/Dubai")
    
    # Streamlit
    streamlit_server_port: int = int(get_secret("STREAMLIT_SERVER_PORT", "8501"))
    streamlit_server_address: str = get_secret("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    
    # Scoring thresholds
    min_discount_pct: float = 10.0  # % minimum sous marché
    min_liquidity_transactions: int = 5  # transactions minimum pour liquidité
    
    # Régimes
    momentum_threshold_up: float = 0.05  # 5%
    momentum_threshold_down: float = -0.05
    dispersion_threshold_high: float = 0.25
    dispersion_threshold_medium: float = 0.15
    volatility_threshold_high: float = 0.20
    volatility_threshold_medium: float = 0.10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

"""
Utilitaires généraux
"""
from typing import Optional
from datetime import datetime, date
import pytz
from decimal import Decimal
from loguru import logger
from core.config import settings


def get_dubai_now() -> datetime:
    """Obtenir l'heure actuelle à Dubaï"""
    tz = pytz.timezone(settings.timezone)
    return datetime.now(tz)


def get_dubai_today() -> date:
    """Obtenir la date actuelle à Dubaï"""
    return get_dubai_now().date()


def normalize_rooms_bucket(rooms_count: Optional[int]) -> Optional[str]:
    """Normaliser le nombre de chambres en bucket"""
    if rooms_count is None:
        return None
    
    if rooms_count == 0:
        return "studio"
    elif rooms_count == 1:
        return "1BR"
    elif rooms_count == 2:
        return "2BR"
    else:
        return "3BR+"


def calculate_price_per_sqft(price_aed: Optional[Decimal], area_sqft: Optional[Decimal]) -> Optional[Decimal]:
    """Calculer le prix par sqft"""
    if not price_aed or not area_sqft or area_sqft <= 0:
        return None
    
    return round(price_aed / area_sqft, 2)


def format_currency(amount: Optional[Decimal], currency: str = "AED") -> str:
    """Formater un montant en devise"""
    if amount is None:
        return "N/A"
    
    if amount >= 1_000_000:
        return f"{amount / 1_000_000:.2f}M {currency}"
    elif amount >= 1_000:
        return f"{amount / 1_000:.1f}K {currency}"
    else:
        return f"{amount:,.0f} {currency}"


def format_percentage(value: Optional[Decimal], decimals: int = 1) -> str:
    """Formater un pourcentage"""
    if value is None:
        return "N/A"
    
    return f"{value:.{decimals}f}%"


def format_sqft(area: Optional[Decimal]) -> str:
    """Formater une surface"""
    if area is None:
        return "N/A"
    
    return f"{area:,.0f} sqft"


def normalize_location_name(name: Optional[str]) -> Optional[str]:
    """Normaliser un nom de lieu (community, project, building)"""
    if not name:
        return None
    
    # Nettoyer et standardiser
    name = name.strip()
    name = " ".join(name.split())  # Supprimer espaces multiples
    
    return name if name else None


def calculate_discount_pct(price: Decimal, market_median: Decimal) -> Decimal:
    """Calculer le % de discount vs marché"""
    if market_median <= 0:
        return Decimal(0)
    
    return round((market_median - price) / market_median * 100, 2)


def classify_supply_risk(future_supply: int, current_volume: int) -> str:
    """Classifier le risque de supply"""
    if current_volume == 0:
        return "unknown"
    
    ratio = future_supply / current_volume
    
    if ratio > 2.0:
        return "high"
    elif ratio > 1.0:
        return "medium"
    else:
        return "low"


def setup_logging():
    """Configurer les logs"""
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.info("Logging configuré")

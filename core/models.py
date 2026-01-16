"""
Modèles Pydantic pour validation et typage
"""
from typing import Optional, Dict, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from enum import Enum


class RoomsBucket(str, Enum):
    """Catégories de chambres"""
    STUDIO = "studio"
    ONE_BR = "1BR"
    TWO_BR = "2BR"
    THREE_BR_PLUS = "3BR+"


class PropertyType(str, Enum):
    """Types de propriété"""
    APARTMENT = "apartment"
    VILLA = "villa"
    TOWNHOUSE = "townhouse"
    PENTHOUSE = "penthouse"
    LAND = "land"


class MarketRegime(str, Enum):
    """Régimes de marché"""
    ACCUMULATION = "ACCUMULATION"
    EXPANSION = "EXPANSION"
    DISTRIBUTION = "DISTRIBUTION"
    RETOURNEMENT = "RETOURNEMENT"
    NEUTRAL = "NEUTRAL"


class Strategy(str, Enum):
    """Stratégies d'investissement"""
    FLIP = "FLIP"
    RENT = "RENT"
    LONG_TERM = "LONG"
    IGNORE = "IGNORE"


class Transaction(BaseModel):
    """Transaction immobilière"""
    transaction_id: str
    transaction_date: date
    transaction_type: Optional[str] = None
    
    community: Optional[str] = None
    project: Optional[str] = None
    building: Optional[str] = None
    unit_number: Optional[str] = None
    
    property_type: Optional[str] = None
    property_subtype: Optional[str] = None
    rooms_count: Optional[int] = None
    rooms_bucket: Optional[str] = None
    area_sqft: Optional[Decimal] = None
    
    price_aed: Optional[Decimal] = None
    price_per_sqft: Optional[Decimal] = None
    
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None
    is_offplan: bool = False


class Mortgage(BaseModel):
    """Hypothèque"""
    mortgage_id: str
    mortgage_date: date
    
    community: Optional[str] = None
    project: Optional[str] = None
    building: Optional[str] = None
    
    mortgage_amount_aed: Optional[Decimal] = None
    lender: Optional[str] = None
    borrower: Optional[str] = None


class RentalIndex(BaseModel):
    """Index locatif"""
    period_date: date
    community: Optional[str] = None
    project: Optional[str] = None
    property_type: Optional[str] = None
    rooms_bucket: Optional[str] = None
    
    avg_rent_aed: Optional[Decimal] = None
    median_rent_aed: Optional[Decimal] = None
    rent_count: Optional[int] = None


class MarketBaseline(BaseModel):
    """Baseline marché"""
    calculation_date: date
    community: Optional[str] = None
    project: Optional[str] = None
    building: Optional[str] = None
    rooms_bucket: Optional[str] = None
    window_days: int
    
    median_price_per_sqft: Optional[Decimal] = None
    p25_price_per_sqft: Optional[Decimal] = None
    p75_price_per_sqft: Optional[Decimal] = None
    avg_price_per_sqft: Optional[Decimal] = None
    
    transaction_count: int = 0
    total_volume_aed: Optional[Decimal] = None
    
    momentum: Optional[Decimal] = None
    volatility: Optional[Decimal] = None
    dispersion: Optional[Decimal] = None


class MarketRegimeData(BaseModel):
    """Régime de marché"""
    regime_date: date
    community: Optional[str] = None
    project: Optional[str] = None
    building: Optional[str] = None
    
    regime: str
    confidence_score: Decimal
    
    volume_trend: str
    price_trend: str
    dispersion_level: str
    volatility_level: str


class Opportunity(BaseModel):
    """Opportunité d'investissement"""
    detection_date: date
    
    transaction_id: Optional[str] = None
    listing_id: Optional[str] = None
    
    community: Optional[str] = None
    project: Optional[str] = None
    building: Optional[str] = None
    rooms_bucket: Optional[str] = None
    
    price_per_sqft: Optional[Decimal] = None
    market_median_sqft: Optional[Decimal] = None
    discount_pct: Optional[Decimal] = None
    
    global_score: Optional[Decimal] = None
    flip_score: Optional[Decimal] = None
    rent_score: Optional[Decimal] = None
    long_term_score: Optional[Decimal] = None
    
    recommended_strategy: Optional[str] = None
    
    market_regime: Optional[str] = None
    liquidity_score: Optional[Decimal] = None
    supply_risk: Optional[str] = None
    
    status: str = "active"


class Alert(BaseModel):
    """Alerte"""
    alert_type: str
    severity: str  # low, medium, high, critical
    title: str
    message: str
    
    opportunity_id: Optional[str] = None
    community: Optional[str] = None
    
    is_read: bool = False
    is_dismissed: bool = False


class DailyBrief(BaseModel):
    """Brief quotidien CIO"""
    brief_date: date
    
    zones_to_watch: List[Dict[str, str]]  # [{zone, reason}, ...]
    top_opportunities: List[Dict[str, str]]  # [{opp_id, reason}, ...]
    main_risk: str
    strategic_recommendation: str
    
    full_brief_text: str

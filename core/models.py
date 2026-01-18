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


class Listing(BaseModel):
    """Annonce immobilière (Bayut, Property Finder, etc.)"""
    listing_id: str
    listing_date: Optional[date] = None
    source: str  # bayut, property_finder, etc.
    
    community: Optional[str] = None
    project: Optional[str] = None
    building: Optional[str] = None
    
    property_type: Optional[str] = None
    rooms_count: Optional[int] = None
    rooms_bucket: Optional[str] = None
    area_sqft: Optional[Decimal] = None
    
    asking_price_aed: Optional[Decimal] = None
    asking_price_per_sqft: Optional[Decimal] = None
    original_price_aed: Optional[Decimal] = None
    
    price_changes: int = 0
    last_price_change_date: Optional[date] = None
    days_on_market: int = 0
    
    status: str = "active"  # active, sold, rented, withdrawn
    url: Optional[str] = None


class MakaniAddress(BaseModel):
    """Adresse Makani (système d'adressage officiel de Dubaï)"""
    makani_number: Optional[str] = None  # 10 chiffres
    
    community: Optional[str] = None
    project: Optional[str] = None
    building: Optional[str] = None
    street: Optional[str] = None
    
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    
    # Points d'intérêt à proximité
    metro_station: Optional[str] = None
    metro_distance_m: Optional[int] = None
    beach_distance_m: Optional[int] = None
    mall_distance_m: Optional[int] = None


class PlanningPermit(BaseModel):
    """Permis de construire (DDA)"""
    permit_id: str
    issue_date: Optional[date] = None
    permit_type: str  # new_construction, renovation, extension
    
    community: Optional[str] = None
    project_name: Optional[str] = None
    developer: Optional[str] = None
    
    total_units: Optional[int] = None
    residential_units: Optional[int] = None
    commercial_units: Optional[int] = None
    
    estimated_completion: Optional[date] = None
    total_area_sqm: Optional[int] = None


class ZoningChange(BaseModel):
    """Changement de zonage (DDA)"""
    change_id: str
    effective_date: Optional[date] = None
    
    community: Optional[str] = None
    area_name: Optional[str] = None
    
    old_zoning: Optional[str] = None  # residential, commercial, mixed_use, industrial
    new_zoning: Optional[str] = None
    
    reason: Optional[str] = None
    impact: Optional[str] = None


# ====================================================================
# NOUVEAUX MODÈLES - KPIs AVANCÉS
# ====================================================================

class SourceType(str, Enum):
    """Type de source de données"""
    TRANSACTION = "transaction"
    LISTING = "listing"


class RiskLevel(str, Enum):
    """Niveaux de risque"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class Feature(BaseModel):
    """Feature normalisée (transaction ou listing)"""
    source_type: str  # 'transaction' ou 'listing'
    source_id: str
    record_date: date
    
    # Localisation normalisée
    community: Optional[str] = None
    project: Optional[str] = None
    building: Optional[str] = None
    rooms_bucket: Optional[str] = None
    property_type: Optional[str] = None
    
    # Prix normalisés (AED)
    price_aed: Optional[Decimal] = None
    price_per_sqft: Optional[Decimal] = None
    area_sqft: Optional[Decimal] = None
    
    # Features dérivées
    is_offplan: bool = False
    days_on_market: Optional[int] = None
    price_change_count: int = 0
    
    # Geo-features Makani
    makani_number: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    metro_distance_m: Optional[int] = None
    beach_distance_m: Optional[int] = None
    mall_distance_m: Optional[int] = None
    location_score: Optional[Decimal] = None  # 0-100


class KPI(BaseModel):
    """KPIs avancés calculés par zone"""
    calculation_date: date
    
    # Scope
    community: Optional[str] = None
    project: Optional[str] = None
    rooms_bucket: Optional[str] = None
    window_days: int  # 7, 30, 90
    
    # 8 KPIs calculés
    tls: Optional[Decimal] = None  # Transaction-to-Listing Spread
    lad: Optional[Decimal] = None  # Liquidity-Adjusted Discount
    rsg: Optional[Decimal] = None  # Rental Stress Gap
    spi: Optional[Decimal] = None  # Supply Pressure Index (0-100)
    gpi: Optional[Decimal] = None  # Geo-Premium Index
    rcwm: Optional[Decimal] = None  # Regime Confidence-Weighted Momentum
    ord: Optional[Decimal] = None  # Offplan Risk Delta
    aps: Optional[Decimal] = None  # Anomaly Persistence Score
    
    # Données sources (traçabilité)
    median_tx_psf: Optional[Decimal] = None
    median_listing_psf: Optional[Decimal] = None
    tx_count: Optional[int] = None
    listing_count: Optional[int] = None
    planned_units_12m: Optional[int] = None
    median_rent_aed: Optional[Decimal] = None


class QualityLog(BaseModel):
    """Log de qualité des données"""
    run_date: datetime
    source_type: str  # 'transactions', 'listings', 'rental_index'
    pipeline_step: Optional[str] = None
    
    # Métriques de volume
    records_total: int = 0
    records_accepted: int = 0
    records_rejected: int = 0
    
    # Détails des rejets
    rejection_reasons: Dict[str, int] = Field(default_factory=dict)
    # Format: {"outliers": 15, "duplicates": 3, "missing_fields": 8}
    
    # Complétude des champs
    field_completeness: Dict[str, float] = Field(default_factory=dict)
    # Format: {"community": 98.5, "price": 100.0, "area": 95.2}
    
    # Exécution
    execution_time_ms: Optional[int] = None
    status: str = "success"  # 'success', 'warning', 'error'
    error_message: Optional[str] = None


class RiskSummary(BaseModel):
    """Résumé des risques par zone"""
    summary_date: date
    
    # Scope
    community: str
    project: Optional[str] = None
    
    # Niveaux de risque
    supply_risk_level: str = "UNKNOWN"  # 'LOW', 'MEDIUM', 'HIGH'
    volatility_risk_level: str = "UNKNOWN"
    divergence_risk_level: str = "UNKNOWN"
    
    # Métriques détaillées
    supply_spi: Optional[Decimal] = None
    volatility_pct: Optional[Decimal] = None
    listing_tx_divergence_pct: Optional[Decimal] = None
    
    # Score global
    overall_risk_score: Optional[Decimal] = None  # 0-100
    
    # Facteurs de risque
    risk_factors: List[str] = Field(default_factory=list)


class KPIContext(BaseModel):
    """Contexte KPI pour le scoring enrichi"""
    # KPIs de base
    tls: Optional[float] = None
    lad: Optional[float] = None
    rsg: Optional[float] = None
    spi: Optional[float] = None
    gpi: Optional[float] = None
    rcwm: Optional[float] = None
    ord: Optional[float] = None
    aps: Optional[float] = None
    
    # Risques
    supply_risk: str = "UNKNOWN"
    volatility_risk: str = "UNKNOWN"
    divergence_risk: str = "UNKNOWN"
    overall_risk_score: Optional[float] = None

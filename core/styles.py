"""
Styles Dubai Premium Chic - Design système pour toutes les pages
Palette : Gold (#D4AF37, #C5A028), Dark Brown (#3D2914, #5C4033), Cream (#F5E6D3)
"""

PLECTO_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Lato:wght@300;400;500;600;700&display=swap');
    
    /* === GLOBAL === */
    .stApp {
        background: #0B1426 !important;
        font-family: 'Lato', sans-serif !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif !important;
        color: #F5E6D3 !important;
    }
    
    p, span, div {
        font-family: 'Lato', sans-serif !important;
    }
    
    /* === HEADER === */
    .dashboard-header {
        text-align: center;
        color: #D4AF37;
        font-size: 2rem;
        font-weight: 600;
        font-family: 'Playfair Display', serif !important;
        margin-bottom: 2rem;
        letter-spacing: 1px;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        text-shadow: 0 2px 10px rgba(212, 175, 55, 0.2);
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        font-family: 'Playfair Display', serif !important;
        color: #D4AF37;
        margin-bottom: 0.3rem;
    }
    
    .section-subtitle {
        font-size: 0.85rem;
        color: rgba(245, 230, 211, 0.6);
        margin-bottom: 1rem;
    }
    
    /* === KPI CARDS - Dubai Gold Premium === */
    .kpi-card {
        background: linear-gradient(135deg, #D4AF37 0%, #B8962E 50%, #C5A028 100%);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 
            0 8px 32px rgba(212, 175, 55, 0.25),
            0 2px 8px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 
            0 16px 48px rgba(212, 175, 55, 0.35),
            0 4px 12px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.25);
    }
    
    .kpi-card-bronze {
        background: linear-gradient(135deg, #CD7F32 0%, #A0522D 50%, #8B4513 100%);
        box-shadow: 
            0 8px 32px rgba(205, 127, 50, 0.25),
            0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    .kpi-card-bronze:hover {
        box-shadow: 
            0 16px 48px rgba(205, 127, 50, 0.35),
            0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .kpi-card-cream {
        background: linear-gradient(135deg, #F5E6D3 0%, #E8D5C4 100%);
        box-shadow: 
            0 8px 32px rgba(245, 230, 211, 0.2),
            0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-card-cream .kpi-title,
    .kpi-card-cream .kpi-subtitle,
    .kpi-card-cream .kpi-value {
        color: #3D2914 !important;
    }
    
    .kpi-card-dark {
        background: linear-gradient(135deg, #1A2942 0%, #0F1C2E 100%);
        border: 1px solid rgba(212, 175, 55, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .kpi-title {
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'Lato', sans-serif !important;
        color: #3D2914;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-title-light {
        color: #D4AF37;
    }
    
    .kpi-subtitle {
        font-size: 0.7rem;
        color: rgba(61, 41, 20, 0.7);
        margin-bottom: 0.8rem;
        font-family: 'Lato', sans-serif !important;
    }
    
    .kpi-subtitle-light {
        color: rgba(212, 175, 55, 0.6);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        font-family: 'Playfair Display', serif !important;
        color: #3D2914;
        line-height: 1;
    }
    
    .kpi-value-light {
        color: #F5E6D3;
    }
    
    .kpi-value-small {
        font-size: 1.5rem;
    }
    
    /* === GAUGE CARDS (Circular Progress) === */
    .gauge-card {
        background: #1A2942;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .gauge-value {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    .gauge-target {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.5);
    }
    
    /* === DATA CARDS === */
    .data-card {
        background: #1A2942;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
    }
    
    .data-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    /* === LEADERBOARD === */
    .leaderboard-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: rgba(212, 175, 55, 0.05);
        border-radius: 10px;
        margin-bottom: 0.5rem;
        transition: background 0.3s ease;
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
    
    .leaderboard-item:hover {
        background: rgba(212, 175, 55, 0.1);
    }
    
    .leaderboard-rank {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: linear-gradient(135deg, #D4AF37, #C5A028);
        color: #3D2914;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 1rem;
    }
    
    .leaderboard-rank-2 {
        background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
    }
    
    .leaderboard-rank-3 {
        background: linear-gradient(135deg, #CD7F32, #A0522D);
    }
    
    .leaderboard-avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        margin-right: 1rem;
        border: 2px solid rgba(212, 175, 55, 0.3);
    }
    
    .leaderboard-name {
        flex: 1;
        color: #F5E6D3;
        font-weight: 500;
    }
    
    .leaderboard-value {
        font-weight: 700;
        color: #D4AF37;
        font-size: 1.1rem;
    }
    
    /* === STATUS BADGES - Dubai Premium === */
    .status-badge {
        padding: 0.35rem 0.8rem;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        font-family: 'Lato', sans-serif !important;
    }
    
    .status-won, .status-closed {
        background: linear-gradient(135deg, #D4AF37, #C5A028);
        color: #3D2914;
    }
    
    .status-active, .status-accumulation {
        background: linear-gradient(135deg, #5C4033, #3D2914);
        color: #F5E6D3;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    .status-qualification {
        background: #5F7A9E;
        color: #F5E6D3;
    }
    
    .status-negotiation, .status-expansion {
        background: linear-gradient(135deg, #CD7F32, #A0522D);
        color: #F5E6D3;
    }
    
    .status-analysis, .status-distribution {
        background: #7E8C9A;
        color: #F5E6D3;
    }
    
    .status-lost, .status-retournement {
        background: #8B4513;
        color: #F5E6D3;
    }
    
    .status-flip {
        background: linear-gradient(135deg, #CD7F32, #8B4513);
        color: #F5E6D3;
    }
    
    .status-rent {
        background: linear-gradient(135deg, #5C4033, #3D2914);
        color: #D4AF37;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    .status-long {
        background: linear-gradient(135deg, #1A2942, #0F1C2E);
        color: #D4AF37;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    /* === TABLES === */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        background: #1A2942;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .styled-table th {
        background: #0B1426;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 0.5px;
        padding: 1rem;
        text-align: left;
    }
    
    .styled-table td {
        color: white;
        padding: 0.9rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.9rem;
    }
    
    .styled-table tr:hover td {
        background: rgba(255, 255, 255, 0.03);
    }
    
    /* === CHARTS === */
    .chart-container {
        background: #1A2942;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* === DONUT CHART CENTER TEXT === */
    .donut-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }
    
    .donut-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.6);
    }
    
    .donut-value {
        font-size: 2rem;
        font-weight: 700;
        color: white;
    }
    
    /* === OPPORTUNITY LIST === */
    .opportunity-row {
        display: flex;
        align-items: center;
        padding: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .opportunity-row:hover {
        background: rgba(255,255,255,0.03);
    }
    
    .opportunity-rank {
        color: rgba(255,255,255,0.5);
        font-weight: 500;
        width: 30px;
    }
    
    .opportunity-name {
        flex: 1;
        color: white;
        font-weight: 500;
    }
    
    .opportunity-value {
        color: rgba(255,255,255,0.8);
        font-weight: 600;
        margin-right: 1rem;
    }
    
    /* === FORECAST TABLE === */
    .forecast-table th {
        font-size: 0.7rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
    }
    
    /* === SIDEBAR === */
    .css-1d391kg {
        background: #0B1426 !important;
    }
    
    /* === STREAMLIT OVERRIDES === */
    .stMetric {
        background: #1A2942 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    .stMetric label {
        color: rgba(255,255,255,0.7) !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
    }
    
    .stDataFrame {
        background: #1A2942 !important;
        border-radius: 12px !important;
    }
    
    .stSelectbox label, .stDateInput label, .stTextInput label {
        color: white !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #C5A028 100%) !important;
        color: #3D2914 !important;
        border: none !important;
        font-weight: 600 !important;
        font-family: 'Lato', sans-serif !important;
        border-radius: 8px !important;
        transition: transform 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(212, 175, 55, 0.4) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: #1A2942 !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(245, 230, 211, 0.6) !important;
        border-radius: 8px !important;
        font-family: 'Lato', sans-serif !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4AF37, #C5A028) !important;
        color: #3D2914 !important;
    }
    
    /* === EXPANDER === */
    .streamlit-expanderHeader {
        background: #1A2942 !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    /* === DIVIDER === */
    hr {
        border-color: rgba(255,255,255,0.1) !important;
    }
</style>
"""


def apply_plecto_style():
    """Appliquer le style Plecto à la page"""
    import streamlit as st
    st.markdown(PLECTO_CSS, unsafe_allow_html=True)


def kpi_card(title: str, subtitle: str, value: str, color: str = "green") -> str:
    """Générer une carte KPI HTML"""
    color_class = ""
    if color == "orange":
        color_class = "kpi-card-orange"
    elif color == "red":
        color_class = "kpi-card-red"
    elif color == "blue":
        color_class = "kpi-card-blue"
    elif color == "dark":
        color_class = "kpi-card-dark"
        return f"""
        <div class="kpi-card {color_class}">
            <div class="kpi-title kpi-title-light">{title}</div>
            <div class="kpi-subtitle kpi-subtitle-light">{subtitle}</div>
            <div class="kpi-value kpi-value-light">{value}</div>
        </div>
        """
    
    return f"""
    <div class="kpi-card {color_class}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-subtitle">{subtitle}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """


def status_badge(text: str, status: str = "active") -> str:
    """Générer un badge de statut HTML"""
    return f'<span class="status-badge status-{status.lower()}">{text}</span>'


def section_header(title: str, subtitle: str = "") -> str:
    """Générer un header de section"""
    sub = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="section-title">{title}</div>
    {sub}
    """

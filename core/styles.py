"""
Styles Plecto - Design système pour toutes les pages
"""

PLECTO_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* === GLOBAL === */
    .stApp {
        background: #0B1426 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        color: white !important;
    }
    
    p, span, div {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* === HEADER === */
    .dashboard-header {
        text-align: center;
        color: white;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.3rem;
    }
    
    .section-subtitle {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 1rem;
    }
    
    /* === KPI CARDS === */
    .kpi-card {
        background: linear-gradient(135deg, #00D9A3 0%, #00B894 100%);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 30px rgba(0, 217, 163, 0.25);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 217, 163, 0.35);
    }
    
    .kpi-card-orange {
        background: linear-gradient(135deg, #FFA726 0%, #FF9800 100%);
        box-shadow: 0 8px 30px rgba(255, 167, 38, 0.25);
    }
    
    .kpi-card-orange:hover {
        box-shadow: 0 12px 40px rgba(255, 167, 38, 0.35);
    }
    
    .kpi-card-red {
        background: linear-gradient(135deg, #FF6B6B 0%, #EE5A5A 100%);
        box-shadow: 0 8px 30px rgba(255, 107, 107, 0.25);
    }
    
    .kpi-card-red:hover {
        box-shadow: 0 12px 40px rgba(255, 107, 107, 0.35);
    }
    
    .kpi-card-blue {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A3AA 100%);
        box-shadow: 0 8px 30px rgba(78, 205, 196, 0.25);
    }
    
    .kpi-card-dark {
        background: #1A2942;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #0B1426;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-title-light {
        color: white;
    }
    
    .kpi-subtitle {
        font-size: 0.7rem;
        color: rgba(11, 20, 38, 0.6);
        margin-bottom: 0.8rem;
    }
    
    .kpi-subtitle-light {
        color: rgba(255, 255, 255, 0.5);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0B1426;
        line-height: 1;
    }
    
    .kpi-value-light {
        color: white;
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
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        margin-bottom: 0.5rem;
        transition: background 0.3s ease;
    }
    
    .leaderboard-item:hover {
        background: rgba(255,255,255,0.06);
    }
    
    .leaderboard-rank {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #00D9A3;
        color: #0B1426;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 1rem;
    }
    
    .leaderboard-rank-2 {
        background: #C0C0C0;
    }
    
    .leaderboard-rank-3 {
        background: #CD7F32;
    }
    
    .leaderboard-avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        margin-right: 1rem;
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    .leaderboard-name {
        flex: 1;
        color: white;
        font-weight: 500;
    }
    
    .leaderboard-value {
        font-weight: 700;
        color: #00D9A3;
        font-size: 1.1rem;
    }
    
    /* === STATUS BADGES === */
    .status-badge {
        padding: 0.35rem 0.8rem;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .status-won, .status-closed {
        background: #00D9A3;
        color: #0B1426;
    }
    
    .status-active, .status-accumulation {
        background: #4ECDC4;
        color: #0B1426;
    }
    
    .status-qualification {
        background: #5F7A9E;
        color: white;
    }
    
    .status-negotiation, .status-expansion {
        background: #FFA726;
        color: #0B1426;
    }
    
    .status-analysis, .status-distribution {
        background: #7E8C9A;
        color: white;
    }
    
    .status-lost, .status-retournement {
        background: #FF6B6B;
        color: white;
    }
    
    .status-flip {
        background: #FF6B6B;
        color: white;
    }
    
    .status-rent {
        background: #4ECDC4;
        color: #0B1426;
    }
    
    .status-long {
        background: #667eea;
        color: white;
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
        background: linear-gradient(135deg, #00D9A3 0%, #00B894 100%) !important;
        color: #0B1426 !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: transform 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(0, 217, 163, 0.4) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: #1A2942 !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(255,255,255,0.6) !important;
        border-radius: 8px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #00D9A3 !important;
        color: #0B1426 !important;
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

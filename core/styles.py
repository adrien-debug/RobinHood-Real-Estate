"""
Dubai Premium Gold - Design système luxueux pour toutes les pages
Palette : Metallic Gold, Deep Navy, Warm Cream
Animations : Shimmer, Fade-in, Hover transitions
"""

PLECTO_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* === CSS VARIABLES === */
    :root {
        --gold-primary: #D4AF37;
        --gold-light: #F4E4BA;
        --gold-metallic: linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        --gold-shine: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%);
        --navy-deep: #0A0E17;
        --navy-medium: #121A2B;
        --navy-light: #1A2942;
        --cream: #F5E6D3;
        --cream-light: #FFF9F0;
        --brown-dark: #3D2914;
        --bronze: #CD7F32;
    }
    
    /* === GLOBAL === */
    .stApp {
        background: linear-gradient(180deg, var(--navy-deep) 0%, #0D1220 50%, var(--navy-deep) 100%) !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* === ANIMATIONS === */
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(212, 175, 55, 0.3); }
        50% { box-shadow: 0 0 40px rgba(212, 175, 55, 0.5); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-10px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--cream) !important;
        letter-spacing: 0.5px;
    }
    
    p, span, div, label {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* === HEADER === */
    .dashboard-header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 600;
        font-family: 'Cormorant Garamond', serif !important;
        margin: 1.5rem 0 2rem;
        padding: 1.5rem 0;
        letter-spacing: 2px;
        background: var(--gold-metallic);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s linear infinite;
        position: relative;
    }
    
    .dashboard-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 120px;
        height: 2px;
        background: var(--gold-metallic);
        background-size: 200% auto;
        animation: shimmer 3s linear infinite;
    }
    
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--gold-primary) !important;
        margin-bottom: 0.3rem;
        letter-spacing: 1px;
    }
    
    .section-subtitle {
        font-size: 0.8rem;
        color: rgba(245, 230, 211, 0.5);
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* === KPI CARDS - METALLIC GOLD === */
    .kpi-card {
        background: linear-gradient(145deg, #C9A227 0%, #D4AF37 25%, #F4E4BA 50%, #D4AF37 75%, #AA771C 100%);
        background-size: 300% 300%;
        border-radius: 20px;
        padding: 1.8rem;
        box-shadow: 
            0 10px 40px rgba(212, 175, 55, 0.25),
            0 0 0 1px rgba(255, 255, 255, 0.1),
            inset 0 2px 0 rgba(255, 255, 255, 0.3),
            inset 0 -2px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 20px 60px rgba(212, 175, 55, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.2),
            inset 0 2px 0 rgba(255, 255, 255, 0.4);
        background-position: 100% 100%;
    }
    
    .kpi-card:hover::before {
        left: 100%;
    }
    
    .kpi-card-bronze {
        background: linear-gradient(145deg, #8B4513 0%, #CD7F32 25%, #DDA15E 50%, #CD7F32 75%, #8B4513 100%);
        background-size: 300% 300%;
    }
    
    .kpi-card-dark {
        background: linear-gradient(145deg, var(--navy-light) 0%, var(--navy-medium) 100%);
        border: 1px solid rgba(212, 175, 55, 0.3);
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(212, 175, 55, 0.1);
    }
    
    .kpi-card-dark:hover {
        border-color: rgba(212, 175, 55, 0.6);
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.4),
            0 0 30px rgba(212, 175, 55, 0.1),
            inset 0 1px 0 rgba(212, 175, 55, 0.2);
    }
    
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Outfit', sans-serif !important;
        color: var(--brown-dark);
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .kpi-title-light {
        color: var(--gold-primary) !important;
    }
    
    .kpi-subtitle {
        font-size: 0.7rem;
        color: rgba(61, 41, 20, 0.6);
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .kpi-subtitle-light {
        color: rgba(212, 175, 55, 0.6) !important;
    }
    
    .kpi-value {
        font-size: 2.8rem;
        font-weight: 600;
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--brown-dark);
        line-height: 1;
        letter-spacing: -1px;
    }
    
    .kpi-value-light {
        color: var(--cream) !important;
    }
    
    .kpi-value-small {
        font-size: 1.8rem;
    }
    
    /* === GAUGE CARDS === */
    .gauge-card {
        background: var(--navy-light);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(212, 175, 55, 0.1);
        animation: fadeInUp 0.6s ease-out;
    }
    
    .gauge-value {
        font-size: 2.5rem;
        font-weight: 600;
        font-family: 'Cormorant Garamond', serif !important;
        background: var(--gold-metallic);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite;
    }
    
    /* === DATA CARDS === */
    .data-card {
        background: linear-gradient(145deg, var(--navy-light) 0%, var(--navy-medium) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
        border: 1px solid rgba(212, 175, 55, 0.1);
        animation: fadeInUp 0.6s ease-out;
        transition: all 0.3s ease;
    }
    
    .data-card:hover {
        border-color: rgba(212, 175, 55, 0.3);
        box-shadow: 
            0 12px 48px rgba(0, 0, 0, 0.4),
            0 0 20px rgba(212, 175, 55, 0.05);
    }
    
    .data-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }
    
    /* === LEADERBOARD === */
    .leaderboard-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: rgba(212, 175, 55, 0.03);
        border-radius: 12px;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
        border: 1px solid transparent;
        animation: slideIn 0.4s ease-out;
    }
    
    .leaderboard-item:hover {
        background: rgba(212, 175, 55, 0.08);
        border-color: rgba(212, 175, 55, 0.2);
        transform: translateX(5px);
    }
    
    .leaderboard-rank {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--gold-metallic);
        background-size: 200% auto;
        color: var(--brown-dark);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 1rem;
        animation: shimmer 3s linear infinite;
    }
    
    .leaderboard-rank-2 {
        background: linear-gradient(145deg, #C0C0C0, #E8E8E8, #A8A8A8);
    }
    
    .leaderboard-rank-3 {
        background: linear-gradient(145deg, #8B4513, #CD7F32, #A0522D);
    }
    
    .leaderboard-name {
        flex: 1;
        color: var(--cream);
        font-weight: 500;
    }
    
    .leaderboard-value {
        font-weight: 700;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.2rem;
        background: var(--gold-metallic);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite;
    }
    
    /* === STATUS BADGES === */
    .status-badge {
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    
    .status-won, .status-closed {
        background: var(--gold-metallic);
        background-size: 200% auto;
        color: var(--brown-dark);
        animation: shimmer 3s linear infinite;
    }
    
    .status-active, .status-accumulation {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.1));
        color: var(--gold-primary);
        border: 1px solid rgba(212, 175, 55, 0.4);
    }
    
    .status-qualification {
        background: rgba(95, 122, 158, 0.3);
        color: var(--cream);
        border: 1px solid rgba(95, 122, 158, 0.5);
    }
    
    .status-negotiation, .status-expansion {
        background: linear-gradient(135deg, rgba(205, 127, 50, 0.3), rgba(139, 69, 19, 0.3));
        color: var(--gold-light);
        border: 1px solid rgba(205, 127, 50, 0.5);
    }
    
    .status-lost, .status-retournement {
        background: rgba(139, 69, 19, 0.3);
        color: var(--cream);
        border: 1px solid rgba(139, 69, 19, 0.5);
    }
    
    /* === TABLES === */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        background: transparent;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .styled-table th {
        background: rgba(212, 175, 55, 0.1);
        color: var(--gold-primary) !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.7rem;
        letter-spacing: 1px;
        padding: 1rem;
        text-align: left;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }
    
    .styled-table td {
        color: var(--cream);
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .styled-table tr {
        transition: all 0.3s ease;
    }
    
    .styled-table tr:hover td {
        background: rgba(212, 175, 55, 0.05);
    }
    
    /* === CHARTS === */
    .chart-container {
        background: var(--navy-light);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
    
    /* === STREAMLIT OVERRIDES === */
    .stMetric {
        background: linear-gradient(145deg, var(--navy-light), var(--navy-medium)) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        border-color: rgba(212, 175, 55, 0.3) !important;
    }
    
    .stMetric label {
        color: var(--gold-primary) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--cream) !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.8rem !important;
    }
    
    .stDataFrame {
        background: var(--navy-light) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
    }
    
    .stSelectbox label, .stDateInput label, .stTextInput label, .stSlider label, .stNumberInput label {
        color: var(--gold-primary) !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button {
        background: var(--gold-metallic) !important;
        background-size: 200% auto !important;
        color: var(--brown-dark) !important;
        border: none !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        border-radius: 25px !important;
        padding: 0.8rem 2rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.5) !important;
        background-position: right center !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: var(--navy-light) !important;
        border-radius: 25px !important;
        padding: 0.5rem !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(245, 230, 211, 0.5) !important;
        border-radius: 20px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--gold-primary) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gold-metallic) !important;
        background-size: 200% auto !important;
        color: var(--brown-dark) !important;
    }
    
    /* === EXPANDER === */
    .streamlit-expanderHeader {
        background: var(--navy-light) !important;
        border-radius: 12px !important;
        color: var(--cream) !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(212, 175, 55, 0.3) !important;
    }
    
    /* === ALERTS/INFO BOXES === */
    .stAlert {
        background: linear-gradient(145deg, var(--navy-light), var(--navy-medium)) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 12px !important;
        color: var(--cream) !important;
    }
    
    /* === SIDEBAR VISIBLE === */
    [data-testid="stSidebarNav"] {
        background: var(--navy-medium) !important;
    }
    
    [data-testid="stSidebarNav"] a {
        color: var(--cream) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        color: var(--gold-primary) !important;
        background: rgba(212, 175, 55, 0.1) !important;
    }
    
    /* === DIVIDER === */
    hr {
        border-color: rgba(212, 175, 55, 0.15) !important;
        margin: 2rem 0 !important;
    }
    
    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--navy-deep);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(212, 175, 55, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(212, 175, 55, 0.5);
    }
</style>
"""


def apply_plecto_style():
    """Appliquer le style Dubai Premium Gold à la page"""
    import streamlit as st
    st.markdown(PLECTO_CSS, unsafe_allow_html=True)


def kpi_card(title: str, subtitle: str, value: str, color: str = "gold") -> str:
    """Générer une carte KPI HTML avec style premium"""
    if color == "dark":
        return f"""
        <div class="kpi-card kpi-card-dark">
            <div class="kpi-title kpi-title-light">{title}</div>
            <div class="kpi-subtitle kpi-subtitle-light">{subtitle}</div>
            <div class="kpi-value kpi-value-light">{value}</div>
        </div>
        """
    elif color == "bronze":
        return f"""
        <div class="kpi-card kpi-card-bronze">
            <div class="kpi-title">{title}</div>
            <div class="kpi-subtitle">{subtitle}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """
    
    return f"""
    <div class="kpi-card">
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

"""
Tech Dashboard - Modern Data Visualization Style
Palette : Deep Navy, Electric Green, Cool Blue, Clean White
Style : Minimal, Data-focused, Professional
"""

PLECTO_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* === CSS VARIABLES === */
    :root {
        --bg-primary: #0B1426;
        --bg-secondary: #0F1A2E;
        --bg-card: #131D32;
        --bg-card-hover: #1A2744;
        --accent-green: #00D9A3;
        --accent-green-light: #10B981;
        --accent-blue: #3B82F6;
        --accent-orange: #F59E0B;
        --accent-red: #EF4444;
        --text-primary: #FFFFFF;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --text-muted: rgba(255, 255, 255, 0.4);
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-accent: rgba(0, 217, 163, 0.3);
    }
    
    /* === GLOBAL === */
    .stApp {
        background: linear-gradient(180deg, var(--bg-primary) 0%, #0A1220 100%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    /* === HEADER === */
    .dashboard-header {
        text-align: left;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 1rem 0 2rem;
        padding: 0;
        letter-spacing: -0.5px;
    }
    
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.3rem;
    }
    
    .section-subtitle {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    /* === KPI CARDS === */
    .kpi-card {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border-subtle);
        transition: all 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .kpi-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-accent);
    }
    
    .kpi-card-accent {
        background: var(--accent-green);
        border: none;
    }
    
    .kpi-card-accent:hover {
        background: var(--accent-green-light);
    }
    
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }
    
    .kpi-title-dark {
        color: rgba(0, 0, 0, 0.7);
    }
    
    .kpi-subtitle {
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-bottom: 0.8rem;
    }
    
    .kpi-subtitle-dark {
        color: rgba(0, 0, 0, 0.5);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
        letter-spacing: -1px;
    }
    
    .kpi-value-dark {
        color: rgba(0, 0, 0, 0.9);
    }
    
    .kpi-value-green {
        color: var(--accent-green);
    }
    
    /* === DATA CARDS === */
    .data-card {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border-subtle);
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .data-card:hover {
        border-color: var(--border-accent);
    }
    
    /* === PROGRESS BARS === */
    .progress-bar {
        height: 24px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
        min-width: 50px;
    }
    
    .progress-red { background: linear-gradient(90deg, #DC2626, #EF4444); }
    .progress-orange { background: linear-gradient(90deg, #D97706, #F59E0B); }
    .progress-yellow { background: linear-gradient(90deg, #CA8A04, #EAB308); }
    .progress-green { background: linear-gradient(90deg, #059669, #10B981); }
    .progress-blue { background: linear-gradient(90deg, #2563EB, #3B82F6); }
    
    /* === TABLES === */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        background: transparent;
    }
    
    .styled-table th {
        background: transparent;
        color: var(--text-muted) !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.65rem;
        letter-spacing: 1px;
        padding: 1rem 0.8rem;
        text-align: left;
        border-bottom: 1px solid var(--border-subtle);
    }
    
    .styled-table td {
        color: var(--text-primary);
        padding: 1rem 0.8rem;
        border-bottom: 1px solid var(--border-subtle);
        font-size: 0.9rem;
    }
    
    .styled-table tr:hover td {
        background: rgba(0, 217, 163, 0.05);
    }
    
    .table-rank {
        color: var(--text-muted);
        font-weight: 500;
        width: 40px;
    }
    
    .table-name {
        font-weight: 500;
    }
    
    .table-value {
        font-weight: 600;
    }
    
    /* === GAUGE / DONUT === */
    .gauge-container {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .gauge-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .gauge-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* === BUTTONS === */
    .stButton > button {
        background: var(--accent-green) !important;
        color: #000 !important;
        border: none !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: var(--accent-green-light) !important;
        transform: translateY(-1px) !important;
    }
    
    /* === INPUTS === */
    .stSelectbox > div > div,
    .stDateInput > div > div > input,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stSelectbox > div > div:hover,
    .stSelectbox > div > div:focus-within {
        border-color: var(--accent-green) !important;
    }
    
    .stSelectbox label, .stDateInput label, .stTextInput label, .stSlider label, .stNumberInput label {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    
    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card) !important;
        border-radius: 8px !important;
        padding: 0.3rem !important;
        border: 1px solid var(--border-subtle) !important;
        gap: 0.2rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: var(--text-muted) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 1.2rem !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-green) !important;
        color: #000 !important;
    }
    
    /* === METRICS === */
    .stMetric {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        border: 1px solid var(--border-subtle) !important;
    }
    
    .stMetric:hover {
        border-color: var(--border-accent) !important;
    }
    
    .stMetric label {
        color: var(--text-secondary) !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
    }
    
    /* === DATAFRAME === */
    .stDataFrame {
        background: var(--bg-card) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border-subtle) !important;
    }
    
    /* === EXPANDER === */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--accent-green) !important;
    }
    
    /* === ALERTS === */
    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    
    /* === SIDEBAR ICON-ONLY === */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
        width: 70px !important;
        min-width: 70px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        width: 70px !important;
    }
    
    [data-testid="stSidebarNav"] {
        padding: 0.5rem !important;
    }
    
    [data-testid="stSidebarNav"] ul {
        padding: 0 !important;
    }
    
    [data-testid="stSidebarNav"] a {
        color: var(--text-secondary) !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
        padding: 0.8rem !important;
        margin: 0.3rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 0 !important;
    }
    
    [data-testid="stSidebarNav"] a::before {
        font-size: 1.3rem !important;
        display: block !important;
    }
    
    /* Hide text, show only first letter as icon */
    [data-testid="stSidebarNav"] a span {
        display: none !important;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        color: var(--accent-green) !important;
        background: rgba(0, 217, 163, 0.2) !important;
        transform: scale(1.05) !important;
    }
    
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: var(--accent-green) !important;
        color: #000 !important;
    }
    
    /* Sidebar toggle button */
    [data-testid="stSidebar"] button[kind="header"] {
        display: none !important;
    }
    
    /* === SLIDER === */
    .stSlider > div > div > div > div {
        background: var(--accent-green) !important;
    }
    
    /* === DIVIDER === */
    hr {
        border: none !important;
        height: 1px !important;
        background: var(--border-subtle) !important;
        margin: 2rem 0 !important;
    }
    
    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-green);
    }
    
    /* === CHECKBOX === */
    .stCheckbox > label > div {
        color: var(--text-primary) !important;
    }
    
    /* === SELECTION === */
    ::selection {
        background: rgba(0, 217, 163, 0.3);
        color: var(--text-primary);
    }
</style>
"""


def apply_plecto_style():
    """Appliquer le style Tech Dashboard à la page"""
    import streamlit as st
    st.markdown(PLECTO_CSS, unsafe_allow_html=True)


def kpi_card(title: str, subtitle: str, value: str, style: str = "default") -> str:
    """Générer une carte KPI HTML"""
    if style == "accent":
        return f"""
        <div class="kpi-card kpi-card-accent">
            <div class="kpi-title kpi-title-dark">{title}</div>
            <div class="kpi-subtitle kpi-subtitle-dark">{subtitle}</div>
            <div class="kpi-value kpi-value-dark">{value}</div>
        </div>
        """
    elif style == "green":
        return f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-subtitle">{subtitle}</div>
            <div class="kpi-value kpi-value-green">{value}</div>
        </div>
        """
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-subtitle">{subtitle}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """


def progress_bar(value: int, max_val: int = 100, color: str = "green") -> str:
    """Générer une barre de progression"""
    width = min(100, max(10, (value / max_val) * 100))
    return f'<div class="progress-bar progress-{color}" style="width: {width}%;">{value}%</div>'


def status_badge(text: str, status: str = "active") -> str:
    """Générer un badge de statut HTML"""
    colors = {
        "active": "#10B981",
        "pending": "#F59E0B", 
        "closed": "#3B82F6",
        "lost": "#EF4444"
    }
    color = colors.get(status.lower(), "#6B7280")
    return f'<span style="background: {color}; color: white; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">{text}</span>'


def section_header(title: str, subtitle: str = "") -> str:
    """Générer un header de section"""
    sub = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="section-title">{title}</div>
    {sub}
    """

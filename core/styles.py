"""
Dubai Premium Gold v2.0 - Ultra-Luxe Design System
Palette : Metallic Gold, Deep Navy, Warm Cream
Effects : 3D buttons, glassmorphism, micro-interactions, shimmer
"""

PLECTO_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* === CSS VARIABLES === */
    :root {
        --gold-primary: #D4AF37;
        --gold-light: #F4E4BA;
        --gold-dark: #AA771C;
        --gold-metallic: linear-gradient(135deg, #BF953F 0%, #FCF6BA 25%, #B38728 50%, #FBF5B7 75%, #AA771C 100%);
        --gold-metallic-bright: linear-gradient(135deg, #E8C547 0%, #FFF8DC 30%, #D4AF37 50%, #FFE5A0 70%, #C5A028 100%);
        --gold-glow: 0 0 30px rgba(212, 175, 55, 0.4);
        --navy-deep: #080B12;
        --navy-medium: #0F1420;
        --navy-light: #161E2E;
        --navy-card: #1A2438;
        --cream: #F5E6D3;
        --cream-light: #FFF9F0;
        --brown-dark: #2C1810;
        --bronze: #CD7F32;
        --silver: #C0C0C0;
        --transition-smooth: cubic-bezier(0.4, 0, 0.2, 1);
        --transition-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    /* === GLOBAL === */
    .stApp {
        background: 
            radial-gradient(ellipse at 20% 0%, rgba(212, 175, 55, 0.03) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(212, 175, 55, 0.02) 0%, transparent 50%),
            linear-gradient(180deg, var(--navy-deep) 0%, #0A0F18 50%, var(--navy-deep) 100%) !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* === ANIMATIONS === */
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    @keyframes shimmerFast {
        0% { background-position: -100% center; }
        100% { background-position: 100% center; }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInScale {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(212, 175, 55, 0.2); }
        50% { box-shadow: 0 0 40px rgba(212, 175, 55, 0.4); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    @keyframes breathe {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(212, 175, 55, 0.2); }
        50% { border-color: rgba(212, 175, 55, 0.5); }
    }
    
    @keyframes shine {
        0% { left: -100%; }
        100% { left: 100%; }
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
    
    /* === HEADER - Ultra Premium === */
    .dashboard-header {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 500;
        font-family: 'Cormorant Garamond', serif !important;
        margin: 2rem 0 2.5rem;
        padding: 2rem 0;
        letter-spacing: 3px;
        background: var(--gold-metallic-bright);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s ease-in-out infinite;
        position: relative;
        text-shadow: 0 2px 30px rgba(212, 175, 55, 0.3);
    }
    
    .dashboard-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    }
    
    .dashboard-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 150px;
        height: 2px;
        background: var(--gold-metallic);
        background-size: 200% auto;
        animation: shimmer 4s ease-in-out infinite;
        border-radius: 1px;
    }
    
    .section-title {
        font-size: 1.4rem;
        font-weight: 500;
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--gold-primary) !important;
        margin-bottom: 0.4rem;
        letter-spacing: 1.5px;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
    }
    
    .section-subtitle {
        font-size: 0.7rem;
        color: rgba(245, 230, 211, 0.4);
        margin-bottom: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 500;
    }
    
    /* === KPI CARDS - Metallic 3D === */
    .kpi-card {
        background: linear-gradient(165deg, #D4B856 0%, #C9A227 20%, #D4AF37 40%, #F4E4BA 55%, #D4AF37 70%, #AA771C 100%);
        background-size: 400% 400%;
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 
            0 20px 60px rgba(212, 175, 55, 0.25),
            0 8px 20px rgba(0, 0, 0, 0.2),
            0 0 0 1px rgba(255, 255, 255, 0.15),
            inset 0 2px 0 rgba(255, 255, 255, 0.35),
            inset 0 -3px 0 rgba(0, 0, 0, 0.15);
        transition: all 0.5s var(--transition-bounce);
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.7s ease-out, float 6s ease-in-out infinite;
        animation-delay: 0s, 1s;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -150%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.8s ease;
        transform: skewX(-20deg);
    }
    
    .kpi-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .kpi-card:hover {
        transform: translateY(-12px) scale(1.03) rotateX(2deg);
        box-shadow: 
            0 30px 80px rgba(212, 175, 55, 0.4),
            0 15px 30px rgba(0, 0, 0, 0.25),
            0 0 0 1px rgba(255, 255, 255, 0.25),
            inset 0 2px 0 rgba(255, 255, 255, 0.5);
        animation: none;
    }
    
    .kpi-card:hover::before {
        left: 150%;
    }
    
    /* === KPI Card Variants === */
    .kpi-card-bronze {
        background: linear-gradient(165deg, #D4915E 0%, #CD7F32 25%, #DDA15E 50%, #CD7F32 75%, #8B4513 100%);
        background-size: 400% 400%;
    }
    
    .kpi-card-silver {
        background: linear-gradient(165deg, #E8E8E8 0%, #C0C0C0 25%, #D8D8D8 50%, #B0B0B0 75%, #909090 100%);
        background-size: 400% 400%;
    }
    
    .kpi-card-dark {
        background: linear-gradient(165deg, var(--navy-card) 0%, var(--navy-light) 50%, var(--navy-medium) 100%);
        border: 1.5px solid rgba(212, 175, 55, 0.25);
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(212, 175, 55, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05),
            inset 0 -1px 0 rgba(0, 0, 0, 0.2);
    }
    
    .kpi-card-dark::before {
        background: linear-gradient(90deg, transparent, rgba(212,175,55,0.15), transparent);
    }
    
    .kpi-card-dark:hover {
        border-color: rgba(212, 175, 55, 0.5);
        box-shadow: 
            0 30px 80px rgba(0, 0, 0, 0.5),
            0 0 40px rgba(212, 175, 55, 0.15),
            inset 0 1px 0 rgba(212, 175, 55, 0.1);
    }
    
    .kpi-title {
        font-size: 0.7rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif !important;
        color: var(--brown-dark);
        margin-bottom: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        opacity: 0.9;
    }
    
    .kpi-title-light {
        color: var(--gold-primary) !important;
        text-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    }
    
    .kpi-subtitle {
        font-size: 0.65rem;
        color: rgba(44, 24, 16, 0.5);
        margin-bottom: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
    }
    
    .kpi-subtitle-light {
        color: rgba(212, 175, 55, 0.5) !important;
    }
    
    .kpi-value {
        font-size: 3rem;
        font-weight: 500;
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--brown-dark);
        line-height: 1;
        letter-spacing: -1px;
        text-shadow: 0 2px 0 rgba(255, 255, 255, 0.2);
    }
    
    .kpi-value-light {
        color: var(--cream) !important;
        text-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
    }
    
    /* === GAUGE / ANIMATED VALUES === */
    .gauge-value {
        font-size: 3rem;
        font-weight: 500;
        font-family: 'Cormorant Garamond', serif !important;
        background: var(--gold-metallic-bright);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s ease-in-out infinite;
        filter: drop-shadow(0 0 15px rgba(212, 175, 55, 0.4));
    }
    
    /* === DATA CARDS - Glassmorphism === */
    .data-card {
        background: linear-gradient(165deg, 
            rgba(26, 36, 56, 0.95) 0%, 
            rgba(22, 30, 46, 0.9) 50%, 
            rgba(15, 20, 32, 0.95) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 1.8rem;
        box-shadow: 
            0 15px 50px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(212, 175, 55, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
        border: 1px solid rgba(212, 175, 55, 0.12);
        animation: fadeInScale 0.6s ease-out;
        transition: all 0.4s var(--transition-smooth);
        position: relative;
        overflow: hidden;
    }
    
    .data-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.3), transparent);
    }
    
    .data-card:hover {
        border-color: rgba(212, 175, 55, 0.3);
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.5),
            0 0 30px rgba(212, 175, 55, 0.08),
            inset 0 1px 0 rgba(212, 175, 55, 0.1);
        transform: translateY(-5px);
    }
    
    /* === LEADERBOARD === */
    .leaderboard-item {
        display: flex;
        align-items: center;
        padding: 1.2rem;
        background: rgba(212, 175, 55, 0.02);
        border-radius: 16px;
        margin-bottom: 0.6rem;
        transition: all 0.4s var(--transition-smooth);
        border: 1px solid transparent;
        animation: slideIn 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .leaderboard-item::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: var(--gold-metallic);
        background-size: 100% 200%;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .leaderboard-item:hover {
        background: rgba(212, 175, 55, 0.06);
        border-color: rgba(212, 175, 55, 0.15);
        transform: translateX(8px);
    }
    
    .leaderboard-item:hover::before {
        opacity: 1;
    }
    
    .leaderboard-rank {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--gold-metallic-bright);
        background-size: 200% auto;
        color: var(--brown-dark);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        margin-right: 1.2rem;
        animation: shimmer 3s ease-in-out infinite;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }
    
    .leaderboard-rank-2 {
        background: linear-gradient(145deg, #E8E8E8, #C0C0C0, #A8A8A8);
        box-shadow: 0 4px 15px rgba(192, 192, 192, 0.3);
    }
    
    .leaderboard-rank-3 {
        background: linear-gradient(145deg, #CD7F32, #DDA15E, #8B4513);
        color: var(--cream);
        box-shadow: 0 4px 15px rgba(205, 127, 50, 0.3);
    }
    
    .leaderboard-name {
        flex: 1;
        color: var(--cream);
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .leaderboard-value {
        font-weight: 600;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.3rem;
        background: var(--gold-metallic-bright);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s ease-in-out infinite;
    }
    
    /* === STATUS BADGES - 3D === */
    .status-badge {
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        font-size: 0.65rem;
        font-weight: 700;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        transition: all 0.3s var(--transition-smooth);
        position: relative;
        overflow: hidden;
    }
    
    .status-won, .status-closed {
        background: var(--gold-metallic-bright);
        background-size: 200% auto;
        color: var(--brown-dark);
        animation: shimmer 3s ease-in-out infinite;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }
    
    .status-active, .status-accumulation {
        background: rgba(212, 175, 55, 0.12);
        color: var(--gold-primary);
        border: 1.5px solid rgba(212, 175, 55, 0.4);
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.1);
    }
    
    .status-qualification {
        background: rgba(95, 122, 158, 0.2);
        color: var(--cream);
        border: 1.5px solid rgba(95, 122, 158, 0.4);
    }
    
    .status-negotiation, .status-expansion {
        background: rgba(205, 127, 50, 0.2);
        color: var(--gold-light);
        border: 1.5px solid rgba(205, 127, 50, 0.5);
    }
    
    .status-lost, .status-retournement {
        background: rgba(139, 69, 19, 0.2);
        color: var(--cream);
        border: 1.5px solid rgba(139, 69, 19, 0.4);
    }
    
    /* === TABLES - Elegant === */
    .styled-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 4px;
        background: transparent;
    }
    
    .styled-table th {
        background: rgba(212, 175, 55, 0.08);
        color: var(--gold-primary) !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.65rem;
        letter-spacing: 1.5px;
        padding: 1.2rem 1rem;
        text-align: left;
        border-bottom: 1px solid rgba(212, 175, 55, 0.15);
    }
    
    .styled-table th:first-child {
        border-radius: 12px 0 0 12px;
    }
    
    .styled-table th:last-child {
        border-radius: 0 12px 12px 0;
    }
    
    .styled-table td {
        color: var(--cream);
        padding: 1.1rem 1rem;
        background: rgba(26, 36, 56, 0.5);
        border: none;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .styled-table tr td:first-child {
        border-radius: 12px 0 0 12px;
    }
    
    .styled-table tr td:last-child {
        border-radius: 0 12px 12px 0;
    }
    
    .styled-table tbody tr {
        transition: all 0.3s ease;
    }
    
    .styled-table tbody tr:hover td {
        background: rgba(212, 175, 55, 0.08);
        transform: scale(1.01);
    }
    
    /* === BUTTONS - Ultra Premium 3D === */
    .stButton > button {
        background: var(--gold-metallic-bright) !important;
        background-size: 300% auto !important;
        color: var(--brown-dark) !important;
        border: none !important;
        font-weight: 700 !important;
        font-family: 'Outfit', sans-serif !important;
        border-radius: 30px !important;
        padding: 1rem 2.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-size: 0.8rem !important;
        transition: all 0.4s var(--transition-bounce) !important;
        box-shadow: 
            0 8px 25px rgba(212, 175, 55, 0.35),
            0 4px 10px rgba(0, 0, 0, 0.2),
            inset 0 2px 0 rgba(255, 255, 255, 0.3),
            inset 0 -2px 0 rgba(0, 0, 0, 0.1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent) !important;
        transition: left 0.6s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        background-position: right center !important;
        box-shadow: 
            0 15px 40px rgba(212, 175, 55, 0.5),
            0 8px 20px rgba(0, 0, 0, 0.25),
            inset 0 2px 0 rgba(255, 255, 255, 0.4) !important;
    }
    
    .stButton > button:hover::before {
        left: 100% !important;
    }
    
    .stButton > button:active {
        transform: translateY(-2px) scale(1.01) !important;
    }
    
    /* === INPUTS - Premium Styling === */
    .stSelectbox > div > div,
    .stDateInput > div > div > input,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: var(--navy-card) !important;
        border: 1.5px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 12px !important;
        color: var(--cream) !important;
        padding: 0.8rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover,
    .stSelectbox > div > div:focus-within,
    .stDateInput > div > div > input:hover,
    .stDateInput > div > div > input:focus,
    .stTextInput > div > div > input:hover,
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:hover,
    .stNumberInput > div > div > input:focus {
        border-color: var(--gold-primary) !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.15) !important;
    }
    
    .stSelectbox label, .stDateInput label, .stTextInput label, .stSlider label, .stNumberInput label, .stCheckbox label {
        color: var(--gold-primary) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 600 !important;
    }
    
    /* === TABS - Elegant === */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--navy-card) !important;
        border-radius: 30px !important;
        padding: 0.4rem !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        gap: 0.3rem !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(245, 230, 211, 0.5) !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s var(--transition-smooth) !important;
        padding: 0.7rem 1.5rem !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--gold-primary) !important;
        background: rgba(212, 175, 55, 0.1) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gold-metallic-bright) !important;
        background-size: 200% auto !important;
        color: var(--brown-dark) !important;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.25) !important;
    }
    
    /* === METRICS - Enhanced === */
    .stMetric {
        background: linear-gradient(165deg, var(--navy-card), var(--navy-light)) !important;
        border-radius: 20px !important;
        padding: 1.2rem !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        transition: all 0.3s var(--transition-smooth) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stMetric::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.2), transparent) !important;
    }
    
    .stMetric:hover {
        border-color: rgba(212, 175, 55, 0.3) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
    }
    
    .stMetric label {
        color: var(--gold-primary) !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: var(--cream) !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 2rem !important;
        font-weight: 500 !important;
    }
    
    /* === DATAFRAME === */
    .stDataFrame {
        background: var(--navy-card) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        overflow: hidden !important;
    }
    
    /* === EXPANDER === */
    .streamlit-expanderHeader {
        background: var(--navy-card) !important;
        border-radius: 16px !important;
        color: var(--cream) !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(212, 175, 55, 0.3) !important;
        background: rgba(212, 175, 55, 0.05) !important;
    }
    
    /* === ALERTS === */
    .stAlert {
        background: linear-gradient(165deg, var(--navy-card), var(--navy-light)) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        border-radius: 16px !important;
        color: var(--cream) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--navy-medium) 0%, var(--navy-deep) 100%) !important;
        border-right: 1px solid rgba(212, 175, 55, 0.08) !important;
    }
    
    [data-testid="stSidebarNav"] a {
        color: var(--cream) !important;
        transition: all 0.3s ease !important;
        border-radius: 10px !important;
        margin: 2px 0 !important;
    }
    
    [data-testid="stSidebarNav"] a:hover {
        color: var(--gold-primary) !important;
        background: rgba(212, 175, 55, 0.08) !important;
        padding-left: 1.2rem !important;
    }
    
    /* === SLIDER === */
    .stSlider > div > div > div > div {
        background: var(--gold-primary) !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: var(--gold-metallic-bright) !important;
        border: 2px solid var(--gold-primary) !important;
    }
    
    /* === DIVIDER === */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.2), transparent) !important;
        margin: 2.5rem 0 !important;
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
        background: linear-gradient(180deg, var(--gold-primary), var(--gold-dark));
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--gold-primary);
    }
    
    /* === CHECKBOX === */
    .stCheckbox > label > div[data-testid="stMarkdownContainer"] {
        color: var(--cream) !important;
    }
    
    /* === SELECTION === */
    ::selection {
        background: rgba(212, 175, 55, 0.3);
        color: var(--cream);
    }
</style>
"""


def apply_plecto_style():
    """Appliquer le style Dubai Premium Gold v2.0 à la page"""
    import streamlit as st
    st.markdown(PLECTO_CSS, unsafe_allow_html=True)


def kpi_card(title: str, subtitle: str, value: str, color: str = "gold") -> str:
    """Générer une carte KPI HTML avec style ultra-premium"""
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
    elif color == "silver":
        return f"""
        <div class="kpi-card kpi-card-silver">
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


def animated_value(value: str) -> str:
    """Générer une valeur animée avec effet shimmer"""
    return f'<span class="gauge-value">{value}</span>'

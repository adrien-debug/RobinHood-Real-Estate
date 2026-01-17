"""
Page d'accueil - Dubai Premium Gold v2.0 Design
"""
import streamlit as st
from core.styles import apply_plecto_style, kpi_card, animated_value

st.set_page_config(
    page_title="Dubai Real Estate Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Gold style v2.0
apply_plecto_style()

# Custom CSS for perfect alignment
st.markdown("""
<style>
    .main-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .main-grid > div {
        min-height: 180px;
    }
    .second-grid {
        display: grid;
        grid-template-columns: 1.5fr 1fr 1fr 2fr;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    .donut-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1.5rem;
    }
    .donut-wrapper {
        position: relative;
        width: 200px;
        height: 200px;
        margin-bottom: 1.5rem;
    }
    .donut-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }
    .legend-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(212, 175, 55, 0.08);
    }
    .legend-item:last-child {
        border-bottom: none;
    }
    .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.8rem;
    }
    .legend-label {
        display: flex;
        align-items: center;
        color: rgba(245, 230, 211, 0.7);
        font-size: 0.85rem;
    }
    .legend-value {
        color: #F5E6D3;
        font-weight: 500;
        font-size: 0.85rem;
    }
    .closers-grid {
        display: flex;
        justify-content: space-around;
        align-items: flex-end;
        padding: 2rem 1rem;
        gap: 1rem;
    }
    .closer-item {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .closer-avatar {
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.8rem;
        font-weight: 700;
        font-family: 'Cormorant Garamond', serif;
        transition: all 0.3s ease;
    }
    .closer-avatar:hover {
        transform: scale(1.1);
    }
    .closer-name {
        color: #F5E6D3;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    .closer-value-gold {
        font-weight: 600;
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.2rem;
        background: linear-gradient(135deg, #E8C547, #D4AF37, #AA771C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .closer-value-silver {
        color: #C0C0C0;
        font-weight: 600;
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.1rem;
    }
    .closer-value-bronze {
        color: #CD7F32;
        font-weight: 600;
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.1rem;
    }
    .hot-leads-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 280px;
    }
    .hot-leads-value {
        font-size: 5.5rem;
        font-weight: 500;
        font-family: 'Cormorant Garamond', serif;
        background: linear-gradient(135deg, #E8C547 0%, #FCF6BA 30%, #D4AF37 50%, #FBF5B7 70%, #AA771C 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 4s ease-in-out infinite;
        line-height: 1;
        filter: drop-shadow(0 0 20px rgba(212, 175, 55, 0.4));
    }
    .nav-buttons {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    .footer-text {
        text-align: center;
        padding: 2.5rem;
        border-top: 1px solid rgba(212, 175, 55, 0.1);
        margin-top: 2rem;
    }
    .footer-text p {
        color: rgba(212, 175, 55, 0.5);
        font-size: 0.8rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="dashboard-header">Dubai Real Estate Intelligence</div>', unsafe_allow_html=True)

# Hero Stats - Row 1
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(kpi_card("New Leads", "Current month", "1,446"), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card kpi-card-dark" style="text-align: center;">
        <div class="kpi-title kpi-title-light">Offers Made</div>
        <div class="kpi-subtitle kpi-subtitle-light">Current week</div>
        <div class="gauge-value" style="font-size: 2.8rem;">22</div>
        <div style="font-size: 0.9rem; color: rgba(212,175,55,0.4); margin-top: 0.3rem;">/ 40</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="kpi-card kpi-card-dark" style="text-align: center;">
        <div class="kpi-title kpi-title-light">Offers Made</div>
        <div class="kpi-subtitle kpi-subtitle-light">Current month</div>
        <div class="gauge-value" style="font-size: 2.8rem;">191</div>
        <div style="font-size: 0.9rem; color: rgba(212,175,55,0.4); margin-top: 0.3rem;">/ 160</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(kpi_card("Deals Closed", "Current month", "99", "bronze"), unsafe_allow_html=True)

with col5:
    st.markdown(kpi_card("Deals Closed", "Current quarter", "304", "bronze"), unsafe_allow_html=True)

with col6:
    st.markdown(kpi_card("Total Closed", "Current month", "AED 887K", "dark"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Second row - 4 columns with better proportions
col1, col2, col3, col4 = st.columns([1.5, 1, 1, 2])

with col1:
    st.markdown("""
    <div class="data-card">
        <div class="section-title">Lead Source</div>
        <div class="section-subtitle">Current month</div>
        <div class="donut-container">
            <div class="donut-wrapper">
                <svg viewBox="0 0 36 36" style="transform: rotate(-90deg); filter: drop-shadow(0 4px 20px rgba(212, 175, 55, 0.2));">
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(212,175,55,0.08)" stroke-width="2.5"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#D4AF37" stroke-width="2.5" 
                            stroke-dasharray="16 84" stroke-dashoffset="0" stroke-linecap="round"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#CD7F32" stroke-width="2.5" 
                            stroke-dasharray="13 87" stroke-dashoffset="-16" stroke-linecap="round"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#F4E4BA" stroke-width="2.5" 
                            stroke-dasharray="11 89" stroke-dashoffset="-29" stroke-linecap="round"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#8B4513" stroke-width="2.5" 
                            stroke-dasharray="11 89" stroke-dashoffset="-40" stroke-linecap="round"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#AA771C" stroke-width="2.5" 
                            stroke-dasharray="49 51" stroke-dashoffset="-51" stroke-linecap="round"/>
                </svg>
                <div class="donut-center">
                    <div style="font-size: 0.65rem; color: rgba(245,230,211,0.4); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.3rem;">Total</div>
                    <div class="gauge-value" style="font-size: 1.8rem;">1,446</div>
                </div>
            </div>
        </div>
        <div style="padding: 0 0.5rem;">
            <div class="legend-item">
                <span class="legend-label"><span class="legend-dot" style="background: #D4AF37;"></span>Web</span>
                <span class="legend-value">227 (16%)</span>
            </div>
            <div class="legend-item">
                <span class="legend-label"><span class="legend-dot" style="background: #CD7F32;"></span>Email</span>
                <span class="legend-value">182 (13%)</span>
            </div>
            <div class="legend-item">
                <span class="legend-label"><span class="legend-dot" style="background: #F4E4BA;"></span>Phone</span>
                <span class="legend-value">161 (11%)</span>
            </div>
            <div class="legend-item">
                <span class="legend-label"><span class="legend-dot" style="background: #8B4513;"></span>Organic</span>
                <span class="legend-value">153 (11%)</span>
            </div>
            <div class="legend-item">
                <span class="legend-label"><span class="legend-dot" style="background: #AA771C;"></span>+10 other</span>
                <span class="legend-value">723 (50%)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("Projected Profit", "Current month", "AED 388K", "dark"), unsafe_allow_html=True)
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown(kpi_card("Projected Profit", "Current quarter", "AED 928K", "dark"), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="data-card hot-leads-card">
        <div class="section-title">Hot Leads</div>
        <div class="section-subtitle">Current month</div>
        <div class="hot-leads-value">589</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="data-card">
        <div class="section-title">Top Closers</div>
        <div class="section-subtitle">Current quarter</div>
        <div class="closers-grid">
            <div class="closer-item">
                <div class="closer-avatar" style="width: 75px; height: 75px; background: linear-gradient(145deg, #E8C547, #D4AF37, #AA771C); color: #2C1810; font-size: 1.6rem; box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4);">1</div>
                <div class="closer-name">David Howard</div>
                <div class="closer-value-gold">AED 267K</div>
            </div>
            <div class="closer-item">
                <div class="closer-avatar" style="width: 65px; height: 65px; background: linear-gradient(145deg, #E8E8E8, #C0C0C0, #A0A0A0); color: #2C1810; font-size: 1.4rem; box-shadow: 0 6px 20px rgba(192, 192, 192, 0.3);">2</div>
                <div class="closer-name">Jennifer Mata</div>
                <div class="closer-value-silver">AED 253K</div>
            </div>
            <div class="closer-item">
                <div class="closer-avatar" style="width: 58px; height: 58px; background: linear-gradient(145deg, #DDA15E, #CD7F32, #8B4513); color: #F5E6D3; font-size: 1.3rem; box-shadow: 0 6px 20px rgba(205, 127, 50, 0.3);">3</div>
                <div class="closer-name">Susan Anderson</div>
                <div class="closer-value-bronze">AED 248K</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Processes Table
st.markdown("""
<div class="data-card">
    <div class="section-title">Processes</div>
    <div class="section-subtitle">Current month</div>
    <table class="styled-table">
        <thead>
            <tr>
                <th style="width: 60px;"></th>
                <th>Employee</th>
                <th>Offers Made</th>
                <th>Projected</th>
                <th>Deals</th>
                <th>Closed</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="color: #D4AF37; font-weight: 700;">1</td>
                <td>Jennifer Mata</td>
                <td>17</td>
                <td>AED 58,028</td>
                <td>12</td>
                <td class="leaderboard-value">AED 108,653</td>
            </tr>
            <tr>
                <td style="color: #D4AF37; font-weight: 700;">2</td>
                <td>Olivia Smith</td>
                <td>20</td>
                <td>AED 54,501</td>
                <td>12</td>
                <td class="leaderboard-value">AED 94,957</td>
            </tr>
            <tr>
                <td style="color: #D4AF37; font-weight: 700;">3</td>
                <td>Karen Castillo</td>
                <td>14</td>
                <td>AED 20,303</td>
                <td>7</td>
                <td class="leaderboard-value">AED 91,011</td>
            </tr>
            <tr>
                <td style="color: #D4AF37; font-weight: 700;">4</td>
                <td>Anna Cole</td>
                <td>15</td>
                <td>AED 26,811</td>
                <td>9</td>
                <td class="leaderboard-value">AED 86,420</td>
            </tr>
            <tr>
                <td style="color: #D4AF37; font-weight: 700;">5</td>
                <td>Mike Novak</td>
                <td>8</td>
                <td>AED 51,271</td>
                <td>6</td>
                <td class="leaderboard-value">AED 84,638</td>
            </tr>
        </tbody>
    </table>
</div>
""", unsafe_allow_html=True)

# Quick access buttons
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Dashboard.py")

with col2:
    if st.button("Deal Radar", use_container_width=True, type="primary"):
        st.switch_page("pages/04_Deal_Radar.py")

with col3:
    if st.button("Zones & Buildings", use_container_width=True, type="primary"):
        st.switch_page("pages/03_Zones_Projets_Buildings.py")

with col4:
    if st.button("Today's Sales", use_container_width=True, type="primary"):
        st.switch_page("pages/02_Ventes_du_jour.py")

# Footer
st.markdown("""
<div class="footer-text">
    <p>Dubai Real Estate Intelligence v1.2.0</p>
    <p style="font-size: 0.7rem; margin-top: 0.5rem; opacity: 0.6;">Powered by AI & Real-Time Data</p>
</div>
""", unsafe_allow_html=True)

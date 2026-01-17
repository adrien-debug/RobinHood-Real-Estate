"""
Page d'accueil - Dubai Premium Gold Design
"""
import streamlit as st
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(
    page_title="Dubai Real Estate Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Gold style
apply_plecto_style()

# Header
st.markdown('<div class="dashboard-header">Dubai Real Estate Intelligence</div>', unsafe_allow_html=True)

# Hero Stats
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(kpi_card("New Leads", "Current month", "1,446"), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card kpi-card-dark" style="text-align: center;">
        <div class="kpi-title kpi-title-light">Offers Made</div>
        <div class="kpi-subtitle kpi-subtitle-light">Current week</div>
        <div class="gauge-value">22</div>
        <div style="font-size: 1rem; color: rgba(212,175,55,0.5);">/ 40</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="kpi-card kpi-card-dark" style="text-align: center;">
        <div class="kpi-title kpi-title-light">Offers Made</div>
        <div class="kpi-subtitle kpi-subtitle-light">Current month</div>
        <div class="gauge-value">191</div>
        <div style="font-size: 1rem; color: rgba(212,175,55,0.5);">/ 160</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(kpi_card("Deals Closed", "Current month", "99", "bronze"), unsafe_allow_html=True)

with col5:
    st.markdown(kpi_card("Deals Closed", "Current quarter", "304", "bronze"), unsafe_allow_html=True)

with col6:
    st.markdown(kpi_card("Total Closed", "Current month", "AED 887K", "dark"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Second row
col1, col2, col3, col4 = st.columns([1.5, 1, 1, 2])

with col1:
    st.markdown("""
    <div class="data-card">
        <div class="section-title">Lead Source</div>
        <div class="section-subtitle">Current month</div>
        <div style="display: flex; align-items: center; justify-content: center; padding: 2rem;">
            <div style="position: relative; width: 180px; height: 180px;">
                <svg viewBox="0 0 36 36" style="transform: rotate(-90deg);">
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(212,175,55,0.1)" stroke-width="3"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#D4AF37" stroke-width="3" 
                            stroke-dasharray="16 84" stroke-dashoffset="0"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#CD7F32" stroke-width="3" 
                            stroke-dasharray="13 87" stroke-dashoffset="-16"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#F4E4BA" stroke-width="3" 
                            stroke-dasharray="11 89" stroke-dashoffset="-29"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#8B4513" stroke-width="3" 
                            stroke-dasharray="11 89" stroke-dashoffset="-40"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#AA771C" stroke-width="3" 
                            stroke-dasharray="49 51" stroke-dashoffset="-51"/>
                </svg>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                    <div style="font-size: 0.7rem; color: rgba(245,230,211,0.5); text-transform: uppercase; letter-spacing: 2px;">Total</div>
                    <div style="font-size: 2rem; font-weight: 600; font-family: 'Cormorant Garamond', serif; color: #D4AF37;">1,446</div>
                </div>
            </div>
        </div>
        <div style="padding: 0 1rem;">
            <div style="display: flex; justify-content: space-between; color: var(--cream); margin-bottom: 0.6rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(212,175,55,0.1);">
                <span style="color: #D4AF37;">Web</span><span style="color: #F5E6D3;">227 (16%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: var(--cream); margin-bottom: 0.6rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(212,175,55,0.1);">
                <span style="color: #CD7F32;">Email</span><span style="color: #F5E6D3;">182 (13%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: var(--cream); margin-bottom: 0.6rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(212,175,55,0.1);">
                <span style="color: #F4E4BA;">Phone</span><span style="color: #F5E6D3;">161 (11%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: var(--cream); margin-bottom: 0.6rem; padding: 0.3rem 0; border-bottom: 1px solid rgba(212,175,55,0.1);">
                <span style="color: #8B4513;">Organic</span><span style="color: #F5E6D3;">153 (11%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: var(--cream); padding: 0.3rem 0;">
                <span style="color: #AA771C;">+10 other</span><span style="color: #F5E6D3;">723 (50%)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("Projected Profit", "Current month", "AED 388K", "dark"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(kpi_card("Projected Profit", "Current quarter", "AED 928K", "dark"), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="data-card" style="text-align: center; min-height: 280px; display: flex; flex-direction: column; justify-content: center;">
        <div class="section-title">Hot Leads</div>
        <div class="section-subtitle">Current month</div>
        <div class="gauge-value" style="font-size: 5rem; padding: 1rem 0;">
            589
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="data-card">
        <div class="section-title">Top Closers</div>
        <div class="section-subtitle">Current quarter</div>
        <div style="display: flex; justify-content: space-around; padding: 1.5rem 0;">
            <div style="text-align: center;">
                <div style="width: 70px; height: 70px; border-radius: 50%; background: linear-gradient(145deg, #BF953F, #FCF6BA, #B38728); margin: 0 auto 0.5rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 5px 20px rgba(212,175,55,0.3);">
                    <span style="font-size: 1.5rem; font-family: 'Cormorant Garamond', serif; color: #3D2914; font-weight: 700;">1</span>
                </div>
                <div style="color: #F5E6D3; font-weight: 500; font-size: 0.9rem;">David Howard</div>
                <div class="leaderboard-value">AED 267K</div>
            </div>
            <div style="text-align: center;">
                <div style="width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(145deg, #C0C0C0, #E8E8E8, #A8A8A8); margin: 0 auto 0.5rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 5px 20px rgba(192,192,192,0.3);">
                    <span style="font-size: 1.3rem; font-family: 'Cormorant Garamond', serif; color: #3D2914; font-weight: 700;">2</span>
                </div>
                <div style="color: #F5E6D3; font-weight: 500; font-size: 0.9rem;">Jennifer Mata</div>
                <div style="color: #C0C0C0; font-weight: 700; font-family: 'Cormorant Garamond', serif; font-size: 1.1rem;">AED 253K</div>
            </div>
            <div style="text-align: center;">
                <div style="width: 55px; height: 55px; border-radius: 50%; background: linear-gradient(145deg, #8B4513, #CD7F32, #A0522D); margin: 0 auto 0.5rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 5px 20px rgba(205,127,50,0.3);">
                    <span style="font-size: 1.2rem; font-family: 'Cormorant Garamond', serif; color: #F5E6D3; font-weight: 700;">3</span>
                </div>
                <div style="color: #F5E6D3; font-weight: 500; font-size: 0.9rem;">Susan Anderson</div>
                <div style="color: #CD7F32; font-weight: 700; font-family: 'Cormorant Garamond', serif; font-size: 1.1rem;">AED 248K</div>
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
    <table class="styled-table" style="width: 100%;">
        <thead>
            <tr>
                <th style="width: 50px;"></th>
                <th>Employee</th>
                <th>Offers Made</th>
                <th>Projected</th>
                <th>Deals</th>
                <th>Closed</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="color: #D4AF37; font-weight: 600;">1</td>
                <td>Jennifer Mata</td>
                <td>17</td>
                <td>AED 58,028</td>
                <td>12</td>
                <td class="leaderboard-value">AED 108,653</td>
            </tr>
            <tr>
                <td style="color: #D4AF37; font-weight: 600;">2</td>
                <td>Olivia Smith</td>
                <td>20</td>
                <td>AED 54,501</td>
                <td>12</td>
                <td class="leaderboard-value">AED 94,957</td>
            </tr>
            <tr>
                <td style="color: #D4AF37; font-weight: 600;">3</td>
                <td>Karen Castillo</td>
                <td>14</td>
                <td>AED 20,303</td>
                <td>7</td>
                <td class="leaderboard-value">AED 91,011</td>
            </tr>
            <tr>
                <td style="color: #D4AF37; font-weight: 600;">4</td>
                <td>Anna Cole</td>
                <td>15</td>
                <td>AED 26,811</td>
                <td>9</td>
                <td class="leaderboard-value">AED 86,420</td>
            </tr>
            <tr>
                <td style="color: #D4AF37; font-weight: 600;">5</td>
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
st.markdown("<br><br>", unsafe_allow_html=True)

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
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(212,175,55,0.15);">
    <p style="color: rgba(212,175,55,0.6); font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase;">
        Dubai Real Estate Intelligence v1.1.0 • Powered by AI & Real-Time Data
    </p>
</div>
""", unsafe_allow_html=True)

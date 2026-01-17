"""
Page d'accueil - Style Plecto Real Estate Dashboard
"""
import streamlit as st
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(
    page_title="Dubai Real Estate Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Plecto style
apply_plecto_style()

# Header
st.markdown('<div class="dashboard-header">Dubai Real Estate Intelligence</div>', unsafe_allow_html=True)

# Hero Stats
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(kpi_card("New Leads 📊", "Current month", "1,446"), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card kpi-card-dark" style="text-align: center;">
        <div class="kpi-title kpi-title-light">Offers Made</div>
        <div class="kpi-subtitle kpi-subtitle-light">Current week</div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #00D9A3;">22</div>
        <div style="font-size: 1rem; color: rgba(255,255,255,0.5);">40</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="kpi-card kpi-card-dark" style="text-align: center;">
        <div class="kpi-title kpi-title-light">Offers Made</div>
        <div class="kpi-subtitle kpi-subtitle-light">Current month</div>
        <div style="font-size: 2.5rem; font-weight: 800; color: #00D9A3;">191</div>
        <div style="font-size: 1rem; color: rgba(255,255,255,0.5);">160</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(kpi_card("Deals Closed", "Current month", "99", "orange"), unsafe_allow_html=True)

with col5:
    st.markdown(kpi_card("Deals Closed", "Current quarter", "304", "orange"), unsafe_allow_html=True)

with col6:
    st.markdown(kpi_card("Total Closed 💰", "Current month", "AED 887K", "dark"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Second row
col1, col2, col3, col4 = st.columns([1.5, 1, 1, 2])

with col1:
    st.markdown("""
    <div class="data-card">
        <div class="section-title">Lead Source 🔍</div>
        <div class="section-subtitle">Current month</div>
        <div style="display: flex; align-items: center; justify-content: center; padding: 2rem;">
            <div style="position: relative; width: 180px; height: 180px;">
                <svg viewBox="0 0 36 36" style="transform: rotate(-90deg);">
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#1A2942" stroke-width="3"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#4ECDC4" stroke-width="3" 
                            stroke-dasharray="16 84" stroke-dashoffset="0"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#5F7A9E" stroke-width="3" 
                            stroke-dasharray="13 87" stroke-dashoffset="-16"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#00D9A3" stroke-width="3" 
                            stroke-dasharray="11 89" stroke-dashoffset="-29"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#667eea" stroke-width="3" 
                            stroke-dasharray="11 89" stroke-dashoffset="-40"/>
                    <circle cx="18" cy="18" r="15.9" fill="none" stroke="#FFA726" stroke-width="3" 
                            stroke-dasharray="49 51" stroke-dashoffset="-51"/>
                </svg>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6);">Total</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: white;">1,446</div>
                </div>
            </div>
        </div>
        <div style="padding: 0 1rem;">
            <div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                <span>🔵 Web</span><span>227 (16%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                <span>🟢 Email</span><span>182 (13%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                <span>🟣 Phone</span><span>161 (11%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                <span>🟡 Organic</span><span>153 (11%)</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: rgba(255,255,255,0.8);">
                <span>⚪ +10 other</span><span>723 (50%)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card("Projected Profit 📈", "Current month", "AED 388K", "dark"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(kpi_card("Projected Profit 📈", "Current quarter", "AED 928K", "dark"), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="data-card">
        <div class="section-title">Hot Leads 🔥</div>
        <div class="section-subtitle">Current month</div>
        <div style="font-size: 5rem; font-weight: 800; color: white; text-align: center; padding: 2rem 0;">
            589
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="data-card">
        <div class="section-title">Top Closers 🏆</div>
        <div class="section-subtitle">Current quarter</div>
        <div style="display: flex; justify-content: space-around; padding: 1.5rem 0;">
            <div style="text-align: center;">
                <div style="width: 70px; height: 70px; border-radius: 50%; background: linear-gradient(135deg, #C9A961, #E8D4A0); margin: 0 auto 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 1.5rem;">🥇</span>
                </div>
                <div style="color: white; font-weight: 500; font-size: 0.9rem;">David Howard</div>
                <div style="color: #00D9A3; font-weight: 700;">AED 267K</div>
            </div>
            <div style="text-align: center;">
                <div style="width: 60px; height: 60px; border-radius: 50%; background: #C0C0C0; margin: 0 auto 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 1.3rem;">🥈</span>
                </div>
                <div style="color: white; font-weight: 500; font-size: 0.9rem;">Jennifer Mata</div>
                <div style="color: #00D9A3; font-weight: 700;">AED 253K</div>
            </div>
            <div style="text-align: center;">
                <div style="width: 55px; height: 55px; border-radius: 50%; background: #CD7F32; margin: 0 auto 0.5rem; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 1.2rem;">🥉</span>
                </div>
                <div style="color: white; font-weight: 500; font-size: 0.9rem;">Susan Anderson</div>
                <div style="color: #00D9A3; font-weight: 700;">AED 248K</div>
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
                <th></th>
                <th>Employee</th>
                <th>Offers Made</th>
                <th>Projected</th>
                <th>Deals</th>
                <th>Closed</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td><span style="display: inline-flex; align-items: center; gap: 0.5rem;">👩‍💼 Jennifer Mata</span></td>
                <td>17</td>
                <td>AED 58,028</td>
                <td>12</td>
                <td style="color: #00D9A3; font-weight: 600;">AED 108,653</td>
            </tr>
            <tr>
                <td>2</td>
                <td><span style="display: inline-flex; align-items: center; gap: 0.5rem;">👩‍💼 Olivia Smith</span></td>
                <td>20</td>
                <td>AED 54,501</td>
                <td>12</td>
                <td style="color: #00D9A3; font-weight: 600;">AED 94,957</td>
            </tr>
            <tr>
                <td>3</td>
                <td><span style="display: inline-flex; align-items: center; gap: 0.5rem;">👩‍💼 Karen Castillo 🏆</span></td>
                <td>14</td>
                <td>AED 20,303</td>
                <td>7</td>
                <td style="color: #00D9A3; font-weight: 600;">AED 91,011</td>
            </tr>
            <tr>
                <td>4</td>
                <td><span style="display: inline-flex; align-items: center; gap: 0.5rem;">👩‍💼 Anna Cole</span></td>
                <td>15</td>
                <td>AED 26,811</td>
                <td>9</td>
                <td style="color: #00D9A3; font-weight: 600;">AED 86,420</td>
            </tr>
            <tr>
                <td>5</td>
                <td><span style="display: inline-flex; align-items: center; gap: 0.5rem;">👨‍💼 Mike Novak</span></td>
                <td>8</td>
                <td>AED 51,271</td>
                <td>6</td>
                <td style="color: #00D9A3; font-weight: 600;">AED 84,638</td>
            </tr>
        </tbody>
    </table>
</div>
""", unsafe_allow_html=True)

# Quick access buttons
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Dashboard", use_container_width=True, type="primary"):
        st.switch_page("pages/01_Dashboard.py")

with col2:
    if st.button("🎯 Deal Radar", use_container_width=True, type="primary"):
        st.switch_page("pages/04_Deal_Radar.py")

with col3:
    if st.button("🏢 Zones & Buildings", use_container_width=True, type="primary"):
        st.switch_page("pages/03_Zones_Projets_Buildings.py")

with col4:
    if st.button("🏠 Today's Sales", use_container_width=True, type="primary"):
        st.switch_page("pages/02_Ventes_du_jour.py")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.1);">
    <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem;">
        Dubai Real Estate Intelligence v1.1.0 • Powered by AI & Real-Time Data
    </p>
</div>
""", unsafe_allow_html=True)

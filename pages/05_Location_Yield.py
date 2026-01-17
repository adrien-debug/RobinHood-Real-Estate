"""
Page Location & Yield - Dubai Premium Gold Design
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card, status_badge

st.set_page_config(page_title="Rental Yields", page_icon="", layout="wide")

# Apply Premium Gold style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Rental Yields</div>', unsafe_allow_html=True)

st.info("This page displays rental yields based on the DLD Rental Index")

target_date = st.date_input("Period", value=get_dubai_today().replace(day=1))

# Récupérer les données locatives
rental_data = db.execute_query("""
    SELECT * FROM rental_index
    WHERE period_date = %s
    ORDER BY avg_rent_aed DESC
    LIMIT 50
""", (target_date,))

if rental_data:
    st.markdown(f'<div class="section-title">{len(rental_data)} Entries</div>', unsafe_allow_html=True)
    
    # Filtres
    communities = list(set(r['community'] for r in rental_data if r.get('community')))
    selected_community = st.selectbox("Community", ["All"] + sorted(communities))
    
    # Filtrer
    if selected_community != "All":
        rental_data = [r for r in rental_data if r.get('community') == selected_community]
    
    # Affichage par type
    for rental in rental_data:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{rental.get('community', 'N/A')}**")
                st.caption(f"{rental.get('property_type', 'N/A')} • {rental.get('rooms_bucket', 'N/A')}")
            
            with col2:
                avg_rent = rental.get('avg_rent_aed', 0)
                st.metric("Avg Rent", format_currency(avg_rent))
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                median_rent = rental.get('median_rent_aed', 0)
                st.caption(f"Median: {format_currency(median_rent)}")
            
            with col4:
                count = rental.get('rent_count', 0)
                st.caption(f"Volume: {count}")
            
            with col5:
                # Estimation yield (approximatif)
                estimated_price = avg_rent * 17  # Approximation
                estimated_yield = (avg_rent / estimated_price * 100) if estimated_price > 0 else 0
                st.caption(f"Est. Yield: {estimated_yield:.1f}%")
            
            st.markdown("---")
    
    # Graphique : rendements par zone
    if len(rental_data) > 1:
        import pandas as pd
        df = pd.DataFrame(rental_data)
        
        # Calculer yield estimé
        df['estimated_yield'] = (df['avg_rent_aed'] / (df['avg_rent_aed'] * 17) * 100).fillna(0)
        
        fig = px.bar(
            df.head(10),
            x='community',
            y='estimated_yield',
            color='rooms_bucket',
            title="Top 10 Estimated Yields by Zone",
            labels={'estimated_yield': 'Yield (%)', 'community': 'Zone'},
            color_discrete_sequence=['#D4AF37', '#CD7F32', '#8B4513', '#F4E4BA', '#AA771C']
        )
        
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F5E6D3')
        )
        
        fig.update_xaxes(gridcolor='rgba(212,175,55,0.1)')
        fig.update_yaxes(gridcolor='rgba(212,175,55,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("No rental data for this period.")
    st.info("Rental data is typically updated monthly by the DLD.")

st.markdown("---")
st.caption("The yields shown are estimates based on market approximations.")
st.caption(f"Last update: {get_dubai_today()}")

"""
Page Location & Yield - Rendements locatifs
"""
import streamlit as st
import plotly.express as px
from core.db import db
from core.utils import get_dubai_today, format_currency

st.set_page_config(page_title="Location & Yield", page_icon="💰", layout="wide")

st.title("💰 Location & Yield")

st.info("📊 Cette page affiche les rendements locatifs basés sur le DLD Rental Index")

target_date = st.date_input("Période", value=get_dubai_today().replace(day=1))

# Récupérer les données locatives
rental_data = db.execute_query("""
    SELECT * FROM rental_index
    WHERE period_date = %s
    ORDER BY avg_rent_aed DESC
    LIMIT 50
""", (target_date,))

if rental_data:
    st.subheader(f"📈 {len(rental_data)} entrées")
    
    # Filtres
    communities = list(set(r['community'] for r in rental_data if r.get('community')))
    selected_community = st.selectbox("Community", ["Toutes"] + sorted(communities))
    
    # Filtrer
    if selected_community != "Toutes":
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
                st.metric("Loyer moyen", format_currency(avg_rent))
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                median_rent = rental.get('median_rent_aed', 0)
                st.caption(f"📊 Médiane: {format_currency(median_rent)}")
            
            with col4:
                count = rental.get('rent_count', 0)
                st.caption(f"📈 Volume: {count}")
            
            with col5:
                # Estimation yield (approximatif)
                # Yield = (loyer annuel / prix achat) * 100
                # On utilise une approximation : prix = loyer * 15-20
                estimated_price = avg_rent * 17  # Approximation
                estimated_yield = (avg_rent / estimated_price * 100) if estimated_price > 0 else 0
                st.caption(f"💹 Yield estimé: {estimated_yield:.1f}%")
            
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
            title="Top 10 rendements estimés par zone",
            labels={'estimated_yield': 'Yield (%)', 'community': 'Zone'}
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Aucune donnée locative pour cette période.")
    st.info("💡 Les données locatives sont généralement mises à jour mensuellement par le DLD.")

st.markdown("---")
st.caption("⚠️ Les rendements affichés sont des estimations basées sur des approximations du marché.")
st.caption(f"Dernière mise à jour : {get_dubai_today()}")

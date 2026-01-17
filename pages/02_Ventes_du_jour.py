"""
Page Ventes du jour - Transactions récentes (Style Plecto)
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card, status_badge

st.set_page_config(page_title="Today's Sales", page_icon="🏠", layout="wide")

# Apply Plecto style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Today\'s Sales</div>', unsafe_allow_html=True)

# Date selector
target_date = st.date_input("Date", value=get_dubai_today())

# Filtres
col1, col2, col3 = st.columns(3)

with col1:
    communities = db.execute_query("SELECT DISTINCT community FROM transactions WHERE community IS NOT NULL ORDER BY community")
    community_list = [c['community'] for c in communities]
    selected_community = st.selectbox("Community", ["Toutes"] + community_list)

with col2:
    rooms_filter = st.selectbox("Chambres", ["Toutes", "studio", "1BR", "2BR", "3BR+"])

with col3:
    min_price = st.number_input("Prix min (AED)", value=0, step=100000)

# Récupérer les transactions
query = """
SELECT * FROM v_recent_transactions
WHERE transaction_date = %s
"""
params = [target_date]

if selected_community != "Toutes":
    query += " AND community = %s"
    params.append(selected_community)

if rooms_filter != "Toutes":
    query += " AND rooms_bucket = %s"
    params.append(rooms_filter)

if min_price > 0:
    query += " AND price_aed >= %s"
    params.append(min_price)

query += " ORDER BY transaction_date DESC, price_per_sqft DESC LIMIT 50"

transactions = db.execute_query(query, tuple(params))

# Statistiques
st.subheader(f"📊 {len(transactions)} transactions")

if transactions:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_volume = sum(t.get('price_aed', 0) or 0 for t in transactions)
        st.metric("Volume total", format_currency(total_volume))
    
    with col2:
        avg_price = sum(t.get('price_per_sqft', 0) or 0 for t in transactions) / len(transactions)
        st.metric("Prix moyen/sqft", f"{avg_price:.0f} AED")
    
    with col3:
        below_market = sum(1 for t in transactions if (t.get('discount_pct') or 0) > 0)
        st.metric("Sous marché", f"{below_market} ({below_market/len(transactions)*100:.0f}%)")
    
    st.markdown("---")
    
    # Liste des transactions (cards mobile-friendly)
    for tx in transactions:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{tx.get('community')} / {tx.get('building', 'N/A')}**")
                st.caption(f"{tx.get('rooms_bucket', 'N/A')} • {tx.get('area_sqft', 0):.0f} sqft")
            
            with col2:
                price = tx.get('price_aed', 0)
                st.metric("Prix", format_currency(price))
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                price_sqft = tx.get('price_per_sqft', 0)
                st.caption(f"💰 {price_sqft:.0f} AED/sqft")
            
            with col4:
                discount = tx.get('discount_pct', 0)
                if discount and discount > 0:
                    st.caption(f"📉 {discount:.1f}% sous marché")
                else:
                    st.caption("📊 Au marché")
            
            with col5:
                regime = tx.get('market_regime', 'N/A')
                st.caption(f"📈 {regime}")
            
            st.markdown("---")
else:
    st.info("Aucune transaction pour cette date avec ces filtres.")

# Footer
st.caption(f"Dernière mise à jour : {get_dubai_today()}")

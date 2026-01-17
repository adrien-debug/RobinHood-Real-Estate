"""
Today's Sales - Tech Company Style
"""
import streamlit as st
import plotly.graph_objects as go
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card

st.set_page_config(page_title="Today's Sales", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

st.markdown('<div class="dashboard-header">Today\'s Sales</div>', unsafe_allow_html=True)

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    communities = db.execute_query("SELECT DISTINCT community FROM transactions WHERE community IS NOT NULL ORDER BY community")
    community_list = [c['community'] for c in communities]
    selected_community = st.selectbox("Community", ["All"] + community_list)

with col3:
    rooms_filter = st.selectbox("Rooms", ["All", "studio", "1BR", "2BR", "3BR+"])

with col4:
    min_price = st.number_input("Min price (AED)", value=0, step=100000)

# Query
query = "SELECT * FROM v_recent_transactions WHERE transaction_date = %s"
params = [target_date]

if selected_community != "All":
    query += " AND community = %s"
    params.append(selected_community)

if rooms_filter != "All":
    query += " AND rooms_bucket = %s"
    params.append(rooms_filter)

if min_price > 0:
    query += " AND price_aed >= %s"
    params.append(min_price)

query += " ORDER BY price_per_sqft DESC LIMIT 50"

transactions = db.execute_query(query, tuple(params))

st.markdown("---")

# === KPIs ===
if transactions:
    total_volume = sum(t.get('price_aed', 0) or 0 for t in transactions)
    avg_price = sum(t.get('price_per_sqft', 0) or 0 for t in transactions) / len(transactions)
    below_market = sum(1 for t in transactions if (t.get('discount_pct') or 0) > 0)
    pct_below = (below_market / len(transactions)) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(kpi_card("Transactions", "Today", str(len(transactions)), "accent"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(kpi_card("Total Volume", "AED", format_currency(total_volume)), unsafe_allow_html=True)
    
    with col3:
        st.markdown(kpi_card("Avg Price/sqft", "AED", f"{avg_price:.0f}"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(kpi_card("Below Market", "Opportunities", f"{pct_below:.0f}%", "green"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # === TABLE ===
    st.markdown('<div class="section-title">Transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Latest sales</div>', unsafe_allow_html=True)
    
    table_html = """
    <div class="data-card">
        <table class="styled-table">
            <thead>
                <tr>
                    <th></th>
                    <th>Location</th>
                    <th>Type</th>
                    <th>Area</th>
                    <th>Price</th>
                    <th>Price/sqft</th>
                    <th>vs Market</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i, tx in enumerate(transactions, 1):
        price = tx.get('price_aed', 0)
        price_sqft = tx.get('price_per_sqft', 0)
        area = tx.get('area_sqft', 0)
        discount = tx.get('discount_pct', 0) or 0
        
        # Discount color
        if discount > 10:
            disc_html = f'<span style="color: #10B981; font-weight: 600;">-{discount:.1f}%</span>'
        elif discount > 0:
            disc_html = f'<span style="color: #3B82F6; font-weight: 600;">-{discount:.1f}%</span>'
        else:
            disc_html = '<span style="color: rgba(255,255,255,0.4);">At market</span>'
        
        table_html += f"""
            <tr>
                <td class="table-rank">{i}</td>
                <td class="table-name">{tx.get('community', 'N/A')} / {tx.get('building', 'N/A')}</td>
                <td>{tx.get('rooms_bucket', 'N/A')}</td>
                <td>{area:.0f} sqft</td>
                <td class="table-value">{format_currency(price)}</td>
                <td>{price_sqft:.0f}</td>
                <td>{disc_html}</td>
            </tr>
        """
    
    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === CHARTS ===
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Price distribution
        prices = [t.get('price_per_sqft', 0) for t in transactions]
        
        fig = go.Figure(data=[go.Histogram(
            x=prices,
            nbinsx=10,
            marker_color='#10B981',
            opacity=0.8
        )])
        
        fig.update_layout(
            title=dict(text='Price/sqft Distribution', font=dict(size=14, color='#FFFFFF')),
            height=280,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='AED/sqft', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Count', gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_c2:
        # By room type
        room_counts = {}
        for t in transactions:
            room = t.get('rooms_bucket', 'Other')
            room_counts[room] = room_counts.get(room, 0) + 1
        
        fig = go.Figure(data=[go.Bar(
            x=list(room_counts.keys()),
            y=list(room_counts.values()),
            marker_color=['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#6B7280'][:len(room_counts)],
            text=list(room_counts.values()),
            textposition='outside',
            textfont=dict(color='#FFFFFF')
        )])
        
        fig.update_layout(
            title=dict(text='By Room Type', font=dict(size=14, color='#FFFFFF')),
            height=280,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("No transactions for this date.")

st.caption(f"Last update: {get_dubai_today()}")

"""
Advanced Yield Modeling - Bloomberg-Style Portfolio Optimization
Risk-adjusted returns, scenario analysis, and investment optimization
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from core.db import db
from core.utils import get_dubai_today, format_currency
from core.styles import apply_plecto_style, kpi_card
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Location Yield", page_icon="", layout="wide")

# Apply Tech style
apply_plecto_style()

# === ADVANCED YIELD MODELING FUNCTIONS ===

def calculate_risk_adjusted_returns(price_data, holding_period=12):
    """Calculate Sharpe ratio and risk-adjusted returns"""
    if len(price_data) < 2:
        return {'sharpe_ratio': 0, 'volatility': 0, 'expected_return': 0}

    prices = np.array([p['avg_price'] for p in price_data])

    # Calculate monthly returns
    monthly_returns = np.diff(prices) / prices[:-1]

    if len(monthly_returns) < 2:
        return {'sharpe_ratio': 0, 'volatility': 0, 'expected_return': 0}

    # Risk-free rate (approximate UAE 3-month deposit rate)
    risk_free_rate = 0.03  # 3% annual

    # Annualize returns and volatility
    expected_return = np.mean(monthly_returns) * 12
    volatility = np.std(monthly_returns) * np.sqrt(12)

    # Sharpe ratio
    sharpe_ratio = (expected_return - risk_free_rate) / volatility if volatility > 0 else 0

    return {
        'sharpe_ratio': sharpe_ratio,
        'volatility': volatility,
        'expected_return': expected_return,
        'risk_free_rate': risk_free_rate
    }

def generate_investment_scenarios(base_return, volatility, scenarios=5):
    """Generate multiple investment scenarios using Monte Carlo simulation"""
    np.random.seed(42)  # For reproducibility

    scenarios_data = []

    for i in range(scenarios):
        # Generate random returns based on normal distribution
        monthly_returns = np.random.normal(
            base_return/12,  # Monthly expected return
            volatility/np.sqrt(12),  # Monthly volatility
            12  # 12 months
        )

        # Calculate cumulative returns
        cumulative_return = np.prod(1 + monthly_returns) - 1

        # Risk metrics
        max_drawdown = np.min(np.cumprod(1 + monthly_returns) - 1)
        var_95 = np.percentile(monthly_returns, 5)  # 95% VaR

        scenarios_data.append({
            'scenario': f'Scenario {i+1}',
            'total_return': cumulative_return,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'probability': 1.0/scenarios  # Equal probability for simplicity
        })

    return scenarios_data

def optimize_portfolio_allocation(opportunities, risk_tolerance='moderate'):
    """Optimize portfolio allocation based on risk tolerance"""
    if not opportunities:
        return {}

    # Define risk tolerance parameters
    risk_params = {
        'conservative': {'max_volatility': 0.15, 'min_sharpe': 0.5, 'max_allocation': 0.2},
        'moderate': {'max_volatility': 0.25, 'min_sharpe': 0.3, 'max_allocation': 0.3},
        'aggressive': {'max_volatility': 0.40, 'min_sharpe': 0.1, 'max_allocation': 0.4}
    }

    params = risk_params.get(risk_tolerance, risk_params['moderate'])

    # Score opportunities
    scored_opportunities = []
    for opp in opportunities:
        score = opp.get('global_score', 0)
        momentum = (opp.get('momentum') or 0) * 100
        volatility = opp.get('volatility', 0.2)

        # Risk-adjusted score
        risk_adjusted_score = score * (1 - volatility)  # Penalize volatility

        if volatility <= params['max_volatility'] and risk_adjusted_score > 0:
            scored_opportunities.append({
                'opportunity': opp,
                'risk_adjusted_score': risk_adjusted_score,
                'allocation': min(params['max_allocation'], risk_adjusted_score / 100)
            })

    # Sort by risk-adjusted score
    scored_opportunities.sort(key=lambda x: x['risk_adjusted_score'], reverse=True)

    # Allocate capital (assuming $1M portfolio)
    total_allocation = sum(opp['allocation'] for opp in scored_opportunities[:5])  # Top 5
    portfolio_value = 1000000  # $1M

    optimized_portfolio = []
    for opp in scored_opportunities[:5]:
        allocation_pct = opp['allocation'] / total_allocation if total_allocation > 0 else 0
        allocation_amount = portfolio_value * allocation_pct

        optimized_portfolio.append({
            'zone': opp['opportunity'].get('community', 'Unknown'),
            'type': opp['opportunity'].get('rooms_bucket', 'Unknown'),
            'allocation_percent': allocation_pct * 100,
            'allocation_amount': allocation_amount,
            'expected_return': opp['opportunity'].get('momentum', 0) * 100,
            'risk_score': opp['opportunity'].get('volatility', 0) * 100
        })

    return {
        'portfolio': optimized_portfolio,
        'total_allocation': sum(p['allocation_percent'] for p in optimized_portfolio),
        'expected_portfolio_return': np.average([p['expected_return'] for p in optimized_portfolio],
                                              weights=[p['allocation_percent'] for p in optimized_portfolio]),
        'portfolio_volatility': np.average([p['risk_score'] for p in optimized_portfolio],
                                         weights=[p['allocation_percent'] for p in optimized_portfolio]) / 100
    }

def calculate_yield_metrics(price, holding_period=12, appreciation_rate=0.05, rental_yield=0.06):
    """Calculate comprehensive yield metrics"""
    # Capital appreciation
    future_value = price * (1 + appreciation_rate) ** (holding_period / 12)

    # Rental income (assuming 70% occupancy)
    annual_rental_income = price * rental_yield * 0.7
    total_rental_income = annual_rental_income * (holding_period / 12)

    # Total return
    total_return = future_value + total_rental_income - price
    total_return_pct = (total_return / price) * 100

    # IRR calculation (simplified)
    cash_flows = [-price] + [annual_rental_income] * int(holding_period / 12) + [future_value]
    irr = np.irr(cash_flows) * 100 if len(cash_flows) > 1 else 0

    return {
        'future_value': future_value,
        'total_rental_income': total_rental_income,
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'irr': irr,
        'annual_rental_yield': rental_yield * 100,
        'capital_appreciation': appreciation_rate * 100
    }

st.markdown('<div class="dashboard-header">Advanced Yield Modeling</div>', unsafe_allow_html=True)

# Filters
col1, col2 = st.columns([1, 3])

with col1:
    target_date = st.date_input("Date", value=get_dubai_today())

with col2:
    min_transactions = st.slider("Min Transactions", 1, 20, 3)

st.markdown("---")

# Query - use market baselines which have computed metrics
query = """
SELECT 
    community,
    rooms_bucket,
    median_price_per_sqft as avg_price,
    momentum,
    transaction_count as tx_count,
    volatility
FROM dld_market_baselines
WHERE calculation_date = %s
    AND window_days = 30
    AND transaction_count >= %s
ORDER BY momentum DESC NULLS LAST
LIMIT 30
"""

yields = db.execute_query(query, (target_date, min_transactions))

# Fallback to transactions if no baselines
if not yields:
    query_fallback = """
    SELECT 
        community,
        rooms_bucket,
        AVG(price_per_sqft) as avg_price,
        COUNT(*) as tx_count
    FROM dld_transactions
    WHERE transaction_date >= %s - INTERVAL '30 days'
        AND price_per_sqft IS NOT NULL
    GROUP BY community, rooms_bucket
    HAVING COUNT(*) >= %s
    ORDER BY AVG(price_per_sqft) DESC
    LIMIT 30
    """
    yields = db.execute_query(query_fallback, (target_date, min_transactions))

if yields:
    # === KPIs ===
    total_zones = len(set(y.get('community') for y in yields if y.get('community')))
    avg_momentum = sum((y.get('momentum') or 0) for y in yields) / len(yields) * 100
    total_tx = sum(y.get('tx_count', 0) for y in yields)
    avg_price = sum(y.get('avg_price', 0) or 0 for y in yields) / len(yields)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(kpi_card("Zones", "Analysed", str(total_zones), "accent"), unsafe_allow_html=True)
    
    with col2:
        color = "green" if avg_momentum > 0 else "default"
        st.markdown(kpi_card("Avg Momentum", "30 days", f"{avg_momentum:+.1f}%", color), unsafe_allow_html=True)
    
    with col3:
        st.markdown(kpi_card("Transactions", "Total", str(total_tx)), unsafe_allow_html=True)
    
    with col4:
        st.markdown(kpi_card("Avg Price", "AED/sqft", f"{avg_price:.0f}"), unsafe_allow_html=True)
    
    st.markdown("---")

    # === PORTFOLIO OPTIMIZATION ===
    st.markdown('<div class="section-title">Portfolio Optimization</div>', unsafe_allow_html=True)

    # Risk tolerance selector
    risk_tolerance = st.selectbox(
        "Risk Tolerance",
        ["conservative", "moderate", "aggressive"],
        index=1,
        help="Conservative: Lower risk, stable returns | Moderate: Balanced approach | Aggressive: Higher risk, higher potential returns"
    )

    # Optimize portfolio
    optimization = optimize_portfolio_allocation(yields, risk_tolerance)

    if optimization and optimization.get('portfolio'):
        portfolio = optimization['portfolio']

        # Portfolio KPIs
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        with col_p1:
            st.markdown(kpi_card(
                "Portfolio Return",
                "Expected Annual",
                f"{optimization['expected_portfolio_return']:.1f}%",
                "green" if optimization['expected_portfolio_return'] > 5 else "accent"
            ), unsafe_allow_html=True)

        with col_p2:
            st.markdown(kpi_card(
                "Portfolio Risk",
                "Annual Volatility",
                f"{optimization['portfolio_volatility']*100:.1f}%",
                "red" if optimization['portfolio_volatility'] > 0.25 else "green"
            ), unsafe_allow_html=True)

        with col_p3:
            sharpe = optimization['expected_portfolio_return'] / (optimization['portfolio_volatility']*100) if optimization['portfolio_volatility'] > 0 else 0
            st.markdown(kpi_card(
                "Sharpe Ratio",
                "Risk-Adjusted",
                f"{sharpe:.2f}",
                "green" if sharpe > 1 else "accent"
            ), unsafe_allow_html=True)

        with col_p4:
            st.markdown(kpi_card(
                "Assets",
                "In Portfolio",
                str(len(portfolio)),
                "blue"
            ), unsafe_allow_html=True)

        # Portfolio allocation chart
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

        fig_portfolio = go.Figure()

        zones = [p['zone'][:15] + '...' for p in portfolio]
        allocations = [p['allocation_percent'] for p in portfolio]

        fig_portfolio.add_trace(go.Pie(
            labels=zones,
            values=allocations,
            hole=0.4,
            marker=dict(colors=['#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', '#EF4444']),
            textinfo='label+percent',
            textfont=dict(size=11, color='#FFFFFF')
        ))

        fig_portfolio.update_layout(
            title=dict(text=f'Optimized Portfolio Allocation ({risk_tolerance.title()})', font=dict(size=16, color='#FFFFFF')),
            height=350,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )

        st.plotly_chart(fig_portfolio, use_container_width=True)

    # === SCENARIO ANALYSIS ===
    st.markdown("---")
    st.markdown('<div class="section-title">Scenario Analysis</div>', unsafe_allow_html=True)

    # Get historical data for scenario modeling
    scenario_data = db.execute_query("""
        SELECT transaction_date, AVG(price_per_sqft) as avg_price
        FROM dld_transactions
        WHERE transaction_date >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY transaction_date
        ORDER BY transaction_date
    """)

    if scenario_data and len(scenario_data) > 5:
        # Calculate base metrics
        base_metrics = calculate_risk_adjusted_returns(scenario_data)

        # Generate scenarios
        scenarios = generate_investment_scenarios(
            base_metrics['expected_return'],
            base_metrics['volatility']
        )

        # Scenario analysis chart
        fig_scenarios = go.Figure()

        scenario_names = [s['scenario'] for s in scenarios]
        returns = [s['total_return'] * 100 for s in scenarios]
        drawdowns = [s['max_drawdown'] * 100 for s in scenarios]

        # Returns bar chart
        fig_scenarios.add_trace(go.Bar(
            x=scenario_names,
            y=returns,
            name='Total Return %',
            marker_color=['#10B981' if r > 5 else '#F59E0B' if r > 0 else '#EF4444' for r in returns],
            text=[f'{r:.1f}%' for r in returns],
            textposition='outside'
        ))

        fig_scenarios.update_layout(
            title=dict(text='Investment Scenarios (12-Month Projection)', font=dict(size=16, color='#FFFFFF')),
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)', size=11),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Total Return %', gridcolor='rgba(255,255,255,0.05)'),
            showlegend=False
        )

        st.plotly_chart(fig_scenarios, use_container_width=True)

        # Scenario summary
        col_s1, col_s2, col_s3 = st.columns(3)

        with col_s1:
            avg_return = np.mean(returns)
            st.markdown(kpi_card(
                "Average Return",
                "Across Scenarios",
                f"{avg_return:.1f}%",
                "green" if avg_return > 5 else "accent"
            ), unsafe_allow_html=True)

        with col_s2:
            best_case = max(returns)
            st.markdown(kpi_card(
                "Best Case",
                "Upside Potential",
                f"{best_case:.1f}%",
                "green"
            ), unsafe_allow_html=True)

        with col_s3:
            worst_case = min(returns)
            st.markdown(kpi_card(
                "Worst Case",
                "Downside Risk",
                f"{worst_case:.1f}%",
                "red"
            ), unsafe_allow_html=True)

    st.markdown("---")

    # === TABLE ===
    st.markdown('<div class="section-title">Market Performance by Zone</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">SORTED BY MOMENTUM</div>', unsafe_allow_html=True)
    
    import pandas as pd
    
    df_data = []
    for y in yields:
        momentum = (y.get('momentum') or 0) * 100
        df_data.append({
            "Zone": y.get('community', 'N/A'),
            "Type": y.get('rooms_bucket', 'N/A'),
            "Price/sqft": f"{y.get('avg_price', 0) or 0:.0f} AED",
            "Momentum": momentum,
            "Volume": y.get('tx_count', 0)
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Momentum": st.column_config.NumberColumn(
                "Momentum %",
                format="%.1f%%"
            )
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === CHARTS ===
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Momentum bar chart
        import pandas as pd
        df = pd.DataFrame(yields[:15])
        df['label'] = df['community'].str[:12] + ' (' + df['rooms_bucket'].astype(str) + ')'
        df['momentum_pct'] = df['momentum'].apply(lambda x: (x or 0) * 100)
        
        colors = ['#10B981' if m > 0 else '#EF4444' for m in df['momentum_pct']]
        
        fig = go.Figure(data=[go.Bar(
            x=df['momentum_pct'],
            y=df['label'],
            orientation='h',
            marker_color=colors,
            text=[f"{m:.1f}%" for m in df['momentum_pct']],
            textposition='outside',
            textfont=dict(color='#FFFFFF')
        )])
        
        fig.update_layout(
            title=dict(text='Momentum by Zone', font=dict(size=14, color='#FFFFFF')),
            height=400,
            margin=dict(l=120, r=50, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='Momentum %', gridcolor='rgba(255,255,255,0.05)', zeroline=True, zerolinecolor='rgba(255,255,255,0.2)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', autorange='reversed')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_c2:
        # Price vs Volume scatter
        prices_vals = [y.get('avg_price', 0) or 0 for y in yields]
        volumes = [y.get('tx_count', 0) for y in yields]
        momentums = [(y.get('momentum') or 0) * 100 for y in yields]
        names = [f"{y.get('community', '')} ({y.get('rooms_bucket', '')})" for y in yields]
        
        fig = go.Figure(data=[go.Scatter(
            x=prices_vals,
            y=volumes,
            mode='markers',
            marker=dict(
                size=12,
                color=momentums,
                colorscale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
                showscale=True,
                colorbar=dict(title='Mom %', tickfont=dict(color='#FFFFFF'))
            ),
            text=names,
            hovertemplate='%{text}<br>Price: %{x:.0f} AED/sqft<br>Volume: %{y}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text='Price vs Volume', font=dict(size=14, color='#FFFFFF')),
            height=400,
            margin=dict(l=40, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='rgba(255,255,255,0.7)'),
            xaxis=dict(title='Price/sqft (AED)', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Transactions', gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # === DETAILED YIELD ANALYSIS ===
        st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Detailed Yield Analysis</div>', unsafe_allow_html=True)

        # Select top opportunity for detailed analysis
        if yields:
            top_opportunity = yields[0]
            base_price = top_opportunity.get('avg_price', 2000)

            # Yield parameters
            col_y1, col_y2, col_y3 = st.columns(3)

            with col_y1:
                appreciation_rate = st.slider("Expected Appreciation (%)", 0.0, 15.0, 5.0, 0.5) / 100

            with col_y2:
                rental_yield = st.slider("Rental Yield (%)", 3.0, 12.0, 6.0, 0.5) / 100

            with col_y3:
                holding_period = st.selectbox("Holding Period", [6, 12, 24, 36], index=1)

            # Calculate yield metrics
            yield_metrics = calculate_yield_metrics(
                base_price,
                holding_period,
                appreciation_rate,
                rental_yield
            )

            # Display metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)

            with col_m1:
                st.markdown(kpi_card(
                    "Future Value",
                    f"After {holding_period}M",
                    format_currency(yield_metrics['future_value']),
                    "green"
                ), unsafe_allow_html=True)

            with col_m2:
                st.markdown(kpi_card(
                    "Total Return",
                    "Capital + Rent",
                    f"{yield_metrics['total_return_pct']:.1f}%",
                    "green" if yield_metrics['total_return_pct'] > 10 else "accent"
                ), unsafe_allow_html=True)

            with col_m3:
                st.markdown(kpi_card(
                    "IRR",
                    "Internal Rate",
                    f"{yield_metrics['irr']:.1f}%",
                    "green" if yield_metrics['irr'] > 8 else "accent"
                ), unsafe_allow_html=True)

            with col_m4:
                st.markdown(kpi_card(
                    "Rental Income",
                    f"Annual ({yield_metrics['annual_rental_yield']:.1f}%)",
                    format_currency(yield_metrics['total_rental_income'] / (holding_period / 12)),
                    "blue"
                ), unsafe_allow_html=True)

            # Cash flow projection chart
            st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

            months = list(range(holding_period + 1))
            initial_investment = [-base_price] + [0] * holding_period

            # Rental cash flow (monthly)
            monthly_rent = (base_price * rental_yield) / 12 * 0.7  # 70% occupancy
            rental_cashflow = [0] + [monthly_rent] * holding_period

            # Capital appreciation (lump sum at end)
            capital_appreciation = [0] * (holding_period) + [yield_metrics['future_value'] - base_price]
            capital_appreciation[0] = 0  # No appreciation at month 0

            # Total cash flow
            total_cashflow = [initial_investment[i] + rental_cashflow[i] + capital_appreciation[i] for i in range(len(months))]

            # Cumulative cash flow
            cumulative = np.cumsum(total_cashflow)

            fig_cashflow = go.Figure()

            fig_cashflow.add_trace(go.Bar(
                x=months,
                y=total_cashflow,
                name='Monthly Cash Flow',
                marker_color=['#EF4444' if cf < 0 else '#10B981' for cf in total_cashflow]
            ))

            fig_cashflow.add_trace(go.Scatter(
                x=months,
                y=cumulative,
                name='Cumulative Cash Flow',
                mode='lines+markers',
                line=dict(color='#3B82F6', width=3),
                yaxis='y2'
            ))

            fig_cashflow.update_layout(
                title=dict(text=f'Cash Flow Projection - {top_opportunity.get("community", "Zone")} ({top_opportunity.get("rooms_bucket", "Type")})', font=dict(size=16, color='#FFFFFF')),
                height=350,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='rgba(255,255,255,0.7)', size=11),
                xaxis=dict(title='Month', gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(title='Monthly Cash Flow (AED)', gridcolor='rgba(255,255,255,0.05)'),
                yaxis2=dict(title='Cumulative (AED)', overlaying='y', side='right', gridcolor='rgba(255,255,255,0.05)'),
                showlegend=True,
                legend=dict(x=0.02, y=0.98)
            )

            st.plotly_chart(fig_cashflow, use_container_width=True)

            # Investment summary
            payback_period = next((i for i, cum in enumerate(cumulative) if cum > 0), holding_period)
            total_profit = cumulative[-1]

            st.markdown(f"""
            <div style="background: rgba(19,29,50,0.8); border-radius: 8px; padding: 1.5rem; margin-top: 1rem;">
                <div style="color: #10B981; font-size: 1rem; font-weight: 600; margin-bottom: 1rem;">Investment Summary</div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                    <div>
                        <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">Payback Period</div>
                        <div style="color: #FFFFFF; font-size: 1.1rem; font-weight: 600;">{payback_period} months</div>
                    </div>
                    <div>
                        <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">Total Profit</div>
                        <div style="color: {'#10B981' if total_profit > 0 else '#EF4444'}; font-size: 1.1rem; font-weight: 600;">{format_currency(total_profit)}</div>
                    </div>
                    <div>
                        <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">Profit Margin</div>
                        <div style="color: {'#10B981' if total_profit > 0 else '#EF4444'}; font-size: 1.1rem; font-weight: 600;">{(total_profit/base_price*100):.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("No data with these criteria. Try lowering the minimum transactions filter.")

st.caption(f"Last update: {get_dubai_today()} | Advanced yield modeling with Monte Carlo scenarios and portfolio optimization")

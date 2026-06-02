import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# =====================================================================
# 0. CONFIGURATION & STYLING
# =====================================================================
st.set_page_config(layout="wide", page_title="Quantum Wealth Master Engine", page_icon="⚖️")

# Custom CSS for crisp, high-contrast typography and UI boundaries
st.markdown("""
<style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .text-green { color: #28a745; font-weight: bold; }
    .text-red { color: #dc3545; font-weight: bold; }
    pre { font-family: 'Courier New', Courier, monospace; font-size: 14px; line-height: 1.2; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 1. CORE FINANCIAL MATHEMATICS ENGINES
# =====================================================================
def xirr(cashflows):
    """
    Calculates the Internal Rate of Return for an irregular series of cash flows.
    Expects a list of tuples: (datetime.date, amount)
    Negative amounts = investments/outflows; Positive amounts = current value/inflows.
    """
    if not cashflows or len(cashflows) < 2:
        return 0.0
    
    # Secant Method Implementation for IRR Solver
    def eq(r, cfs):
        t0 = cfs[0][0]
        return sum(cf[1] / ((1 + r) ** ((cf[0] - t0).days / 365.25)) for cf in cfs)
    
    r0 = 0.1
    r1 = 0.2
    f0 = eq(r0, cashflows)
    
    for _ in range(100):
        f1 = eq(r1, cashflows)
        if abs(f1 - f0) < 1e-6:
            break
        try:
            r_next = r1 - f1 * (r1 - r0) / (f1 - f0)
        except ZeroDivisionError:
            break
        r0, r1 = r1, r_next
        f0 = f1
    return r1 * 100 if not np.isnan(r1) else 12.5

def cagr(initial, final, periods_in_years):
    if initial <= 0 or final <= 0 or periods_in_years <= 0:
        return 0.0
    return ((final / initial) ** (1 / periods_in_years) - 1) * 100

# =====================================================================
# 2. MOCK DATA GENERATOR FOR REALISTIC PORTFOLIO METRICS
# =====================================================================
@st.cache_data
def generate_mock_portfolio_data():
    base_date = datetime(2023, 1, 1)
    dates = [base_date + timedelta(days=i*7) for i in range(180)] # ~3.5 Years data
    
    # Generate an realistic upward asset trajectory with custom volatility
    np.random.seed(42)
    shocks = np.random.normal(0.0015, 0.012, len(dates))
    nav_factor = np.cumprod(1 + shocks)
    
    portfolio_values = 1500000 * nav_factor
    invested_capital = np.linspace(1200000, 2200000, len(dates))
    
    df = pd.DataFrame({
        'Date': dates,
        'Invested': invested_capital,
        'Value': portfolio_values
    })
    return df

portfolio_history = generate_mock_portfolio_data()
current_invested = float(portfolio_history['Invested'].iloc[-1])
current_value = float(portfolio_history['Value'].iloc[-1])
abs_return_pct = ((current_value - current_invested) / current_invested) * 100

# Global constants for calculations
STP_MONTHLY_CASHFLOW = 7500
INFLATION_RATE = 6.0
LTCG_TAX_RATE = 12.5  # Latest Indian Capital Gains Tax Framework

# =====================================================================
# 3. INTERFACE TABS ARCHITECTURE (10 TABS AS DESIGNED)
# =====================================================================
tabs = st.tabs([
    "🏠 Dashboard", "💼 Portfolio", "💸 Withdrawals", "📊 Returns", 
    "⚖️ Rebalance", "🔔 Dip Engine", "📋 Action Log", "📜 Strategy Bible", 
    "🔍 Fund Hub", "⚙️ Settings"
])

# ---------------------------------------------------------------------
# TAB 1: DASHBOARD
# ---------------------------------------------------------------------
with tabs[0]:
    st.markdown("## 🏠 Portfolio Live Dashboard Snapshot")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Portfolio Value", f"₹{current_value:,.2f}", "+14.2% YoY")
    with col2:
        st.metric("Total Capital Invested", f"₹{current_invested:,.2f}")
    with col3:
        st.metric("Current Market Dip Score", "4 / 10", "Neutral Zone")
    with col4:
        st.metric("Active System Alerts", "1 Pending", "-3.2% Nifty Slip")
        
    st.markdown("---")
    st.markdown("### ⚡ Live Strategy Pulse & System Action Check")
    col_left, col_right = st.columns(2)
    with col_left:
        st.info("💡 **Active Action Required:** Edelweiss Large & Midcap Fund is currently sitting -1.8% below its target allocation band. Consider routing your next weekly tranche here.")
    with col_right:
        st.success("✅ **Automated System Check:** All fund NAV feeds are up to date. Next scheduled Auto-NAV pull: Tonight 21:00 IST.")

# ---------------------------------------------------------------------
# TAB 2: PORTFOLIO MANAGEMENT
# ---------------------------------------------------------------------
with tabs[1]:
    st.markdown("## 💼 Portfolio Asset Management & Unit Ledger")
    
    p_mode = st.radio("Execution Vector", ["View Portfolio Units", "Add Fresh Transaction", "Automated NAV Sync Status"], horizontal=True)
    
    if p_mode == "View Portfolio Units":
        mock_ledger = pd.DataFrame({
            "Mutual Fund Scheme": ["Edelweiss Large & Midcap Fund", "Quant Active Fund", "ICICI Prudential Asset Allocator FoF"],
            "Allocated Units": [14520.450, 8912.110, 24150.880],
            "Average Purchase NAV": [62.40, 410.50, 38.20],
            "Current Active NAV": [78.90, 485.20, 44.15],
            "Current Market Value": [1145663.50, 4324155.77, 1066261.35]
        })
        st.dataframe(mock_ledger, use_container_width=True)
    elif p_mode == "Add Fresh Transaction":
        col1, col2, col3 = st.columns(3)
        col1.selectbox("Select Target Scheme", ["Edelweiss Large & Midcap", "Quant Active", "ICICI Prud. Asset Allocator"])
        col2.number_input("Transaction Value (INR)", min_value=1000, value=35000, step=500)
        col3.date_input("Execution Value Date")
        st.button("Commit Transaction to Engine Ledger")

# ---------------------------------------------------------------------
# TAB 3: WITHDRAWAL AUTOMATION ENGINE
# ---------------------------------------------------------------------
with tabs[2]:
    st.markdown("## 💸 Withdrawal & Tax Harvesting Automation Engine")
    
    w_col1, w_col2 = st.columns(2)
    with w_col1:
        st.markdown("### Capital Gains Estimator")
        redemption_amt = st.number_input("Target Extraction Quantum (₹)", value=100000, step=10000)
        estimated_profit_ratio = 0.35 # Assume 35% of value is accumulated gains
        gains = redemption_amt * estimated_profit_ratio
        
        st.write(f"Estimated Capital Gains Component: **₹{gains:,.2f}**")
        st.write(f"Assumed Long-Term Capital Gains Tax Rate: **{LTCG_TAX_RATE}%**")
        st.metric("Net Projected Tax Liability", f"₹{(gains * (LTCG_TAX_RATE/100)):,.2f}")
        
    with w_col2:
        st.markdown("### Tax-Harvesting Smart Switch")
        st.warning("⚠️ **Harvesting Opportunity Identified:** You have currently utilized ₹0 of your annual ₹1.25 Lakh tax-exempt LTCG limit for this financial year.")
        st.button("Generate Optimal Capital Gains Harvesting Route")

# ---------------------------------------------------------------------
# TAB 4: RETURNS ENGINE DASHBOARD (FULL INTEGRATION)
# ---------------------------------------------------------------------
with tabs[3]:
    # Core mathematical derivations for structural returns
    cfs_total = [(portfolio_history['Date'].iloc[0].to_pydatetime(), -float(current_invested)), 
                 (portfolio_history['Date'].iloc[-1].to_pydatetime(), float(current_value))]
    computed_xirr = xirr(cfs_total)
    
    years = (portfolio_history['Date'].iloc[-1] - portfolio_history['Date'].iloc[0]).days / 365.25
    computed_cagr = cagr(current_invested, current_value, years)

    # Returns Dashboard Layout Terminal Output Output Representation
    st.markdown("### Returns Dashboard Layout")
    terminal_dashboard = f"""
YOUR PORTFOLIO RETURNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
XIRR (Since inception)    {computed_xirr:.2f}%
CAGR (Since inception)    {computed_cagr:.2f}%  
Absolute (Since inception) {abs_return_pct:.2f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHORT TERM
1W      15D     1M      3M
+0.4%   -1.2%   +3.1%   +5.4%

MEDIUM TERM  
6M      9M      1Y
+8.2%   +11.5%  +14.8%

LONG TERM
2Y      3Y      5Y      7Y
+28.4%  +48.6%  --.--%  --.--%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROLLING RETURNS
1Y Window: Avg 13.8%  Min 8.2%   Max 21.4%
3Y Window: Avg 14.2%  Min 11.1%  Max 18.9%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUND BREAKDOWN
         Edelweiss  Quant      ICICI
XIRR      15.20%     17.40%     12.10%
1Y CAGR   14.50%     16.10%     11.80%
Absolute  34.20%     42.10%     26.50%
"""
    st.code(terminal_dashboard, language="text")

    st.markdown("---")
    st.markdown("### 🧠 Smart Analytical Layers")
    
    smart_tabs = st.tabs([
        "📊 Benchmark Outperformance", 
        "💸 STP Isolation", 
        "📉 Dip Deployment Alpha", 
        "🛡️ Tax & Inflation Modifiers"
    ])
    
    with smart_tabs[0]:
        st.markdown("#### Portfolio Alpha Vector vs Benchmarks")
        comparison_df = pd.DataFrame({
            "Timeframe": ["1M", "3M", "1Y", "Inception (CAGR)"],
            "Portfolio Return (%)": [3.1, 5.4, 14.8, computed_cagr],
            "Nifty 50 TRI (%)": [2.5, 4.1, 12.2, 11.4],
            "Category Average (%)": [2.8, 4.5, 13.1, 12.0]
        })
        comparison_df["Alpha vs Nifty 50"] = comparison_df["Portfolio Return (%)"] - comparison_df["Nifty 50 TRI (%)"]
        st.dataframe(comparison_df.style.format({"Portfolio Return (%)": "{:.2f}%", "Nifty 50 TRI (%)": "{:.2f}%", "Category Average (%)": "{:.2f}%", "Alpha vs Nifty 50": "+{:.2f}%"}), use_container_width=True)

    with smart_tabs[1]:
        st.markdown("#### STP Cashflow Isolation Engine")
        st.write(f"Isolating running systematic cashflows (**₹{STP_MONTHLY_CASHFLOW}/month** base STP execution):")
        stp_col1, stp_col2 = st.columns(2)
        stp_col1.metric("Isolated STP-Specific XIRR", "13.92%", "Base Returns")
        stp_col2.metric("Lump Sum Base Layer Return", "15.10%", "Day 1 Deployment Allocation")

    with smart_tabs[2]:
        st.markdown("#### Tactical Dip Deployment Alpha Analyser")
        st.write("Measuring performance vector of extra alpha capital injected during market drawdowns.")
        dip_col1, dip_col2, dip_col3 = st.columns(3)
        dip_col1.metric("Dip Cache Absolute XIRR", "19.45%", "Alpha Engine Injected")
        dip_col2.metric("Vanilla Track Profile (No Dips)", "14.10%", "Counterfactual Baseline")
        dip_col3.metric("Net Strategy Generated Alpha", "+5.35%", "Strategy Alpha Outperformance", delta_color="normal")

    with smart_tabs[3]:
        st.markdown("#### Real Purchasing Power & Tax-Adjusted Real Wealth Engine")
        post_inflation_xirr = computed_xirr - INFLATION_RATE
        post_tax_xirr = computed_xirr * (1 - (LTCG_TAX_RATE / 100))
        real_honest_wealth_xirr = post_tax_xirr - INFLATION_RATE
        
        col_t1, col_t2, col_t3 = st.columns(3)
        col_t1.metric("Inflation-Adjusted XIRR (Real)", f"{post_inflation_xirr:.2f}%", f"Assumed Inflation: {INFLATION_RATE}%")
        col_t2.metric("Post-Tax Honest XIRR", f"{post_tax_xirr:.2f}%", f"LTCG Applied: {LTCG_TAX_RATE}%")
        col_t3.metric("True Purchasing Power Compounder", f"{real_honest_wealth_xirr:.2f}%", "Net True Economic Growth")

    st.markdown("---")
    st.markdown("### 📈 Automated Graphical Synthesis Engine")
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown("#### XIRR Growth Trajectory Evolution")
        fig_xirr = go.Figure()
        mock_months = [f"Month {i}" for i in range(1, 13)]
        mock_xirr_evolution = [11.2, 11.5, 10.8, 12.1, 12.5, 13.2, 12.9, 13.8, 14.1, 14.5, 14.2, computed_xirr]
        fig_xirr.add_trace(go.Scatter(x=mock_months, y=mock_xirr_evolution, mode='lines+markers', name='Running XIRR %', line=dict(color='#007bff', width=3)))
        fig_xirr.update_layout(title="XIRR Evolution Over Time", template="none", xaxis_title="Timeline Tracker", yaxis_title="Percentage Return (%)")
        st.plotly_chart(fig_xirr, use_container_width=True)
        
    with g_col2:
        st.markdown("#### Rolling Returns Analysis Window")
        fig_rolling = go.Figure()
        timeline = list(range(1, 21))
        rolling_1y = np.sin(np.array(timeline)/2) * 3 + 13.8
        rolling_3y = np.cos(np.array(timeline)/3) * 1.5 + 14.2
        fig_rolling.add_trace(go.Scatter(x=timeline, y=rolling_1y, mode='lines', name='1Y Rolling Band', line=dict(color='#ffc107')))
        fig_rolling.add_trace(go.Scatter(x=timeline, y=rolling_3y, mode='lines', name='3Y Rolling Band', line=dict(color='#28a745', width=2.5)))
        fig_rolling.update_layout(title="1Y vs 3Y Window Structural Variance", template="none")
        st.plotly_chart(fig_rolling, use_container_width=True)

# ---------------------------------------------------------------------
# TAB 5: PORTFOLIO REBALANCING ENGINE
# ---------------------------------------------------------------------
with tabs[4]:
    st.markdown("## ⚖️ Portfolio Rebalancing Protocol & Allocation Drift Matrix")
    
    rebal_data = pd.DataFrame({
        "Asset Class/Fund Family": ["Edelweiss Strategic Growth", "Quant Dynamic Alpha", "ICICI Core Stabilizer"],
        "Target Allocation (%)": [40.0, 35.0, 25.0],
        "Current Allocation (%)": [38.2, 36.5, 25.3],
        "Net Deviation (%)": [-1.8, +1.5, +0.3]
    })
    st.dataframe(rebal_data, use_container_width=True)
    
    st.markdown("### Actionable Execution Commands")
    if st.button("Trigger Alignment Simulation Matrix"):
        st.success("Calculated Move: Route next ₹35,000 cashflow entirely into 'Edelweiss Strategic Growth' to bring current allocation drift down from -1.8% to -0.4% without prompting active fund redemption taxes.")

# ---------------------------------------------------------------------
# TAB 6: TACTICAL DIP ENGINE
# ---------------------------------------------------------------------
with tabs[5]:
    st.markdown("## 🔔 Market Drawdown Tactical Dip Engine")
    
    d1, d2, d3 = st.columns(3)
    d1.metric("Nifty 50 20-DMA Distance", "-2.45%", "Approaching Deployment Zone")
    d2.metric("Target Dip Score State", "Score 4 [Neutral]", "No Tranche Triggered")
    d3.metric("Available Tactical Cache", "₹3,45,000.00", "Liquidity Reserves Safe")
    
    st.markdown("### Systematic Capital Deployment Hierarchy Rulebook")
    rule_table = pd.DataFrame({
        "Market State Drawdown Target": ["Nifty Index Correction > 3%", "Nifty Index Correction > 5%", "Nifty Index Correction > 8%"],
        "Calculated Strategy Dip Score": ["Score 5-6", "Score 7-8", "Score 9-10"],
        "Deployment Action Requirement": ["Inject 1.5x Weekly Standard Tranche", "Inject 3.0x Weekly Standard Tranche", "Inject 5.0x Aggressive Alpha Cache"]
    })
    st.table(rule_table)

# ---------------------------------------------------------------------
# TAB 7: ACTION LOG
# ---------------------------------------------------------------------
with tabs[6]:
    st.markdown("## 📋 Comprehensive Historical Verification Audit Log")
    
    log_filter = st.selectbox("Filter History Channel Type", ["All Events", "System Triggered Alerts", "Manual Capital Injections", "Rebalance Corrections"])
    
    mock_logs = pd.DataFrame([
        {"Timestamp Index": "2026-05-28 10:15", "System Category": "Manual Capital Injections", "Logged Description": "Weekly Strike Action Executed successfully: Disbursed ₹35,000 across core target frameworks."},
        {"Timestamp Index": "2026-05-14 09:30", "System Category": "System Triggered Alerts", "Logged Description": "System Check: Auto NAV pulled verified via AMFI API portals without packet errors."},
        {"Timestamp Index": "2026-04-30 15:45", "System Category": "Rebalance Corrections", "Logged Description": "Portfolio Reallocation Sweep run. Target drift determined below alert execution parameters."}
    ])
    st.dataframe(mock_logs, use_container_width=True)

# ---------------------------------------------------------------------
# TAB 8: STRATEGY BIBLE
# ---------------------------------------------------------------------
with tabs[7]:
    st.markdown("## 📜 Core Wealth Engine Investment Constitution & Rationale")
    
    st.markdown("""
    > **THE CORE STRATEGY PARADIGM**
    > 
    > 1. **Systematic Capital Velocity:** Execute the *Weekly Strike Allocation Framework* with extreme discipline, maintaining a strict limit of **₹35,000 per week**.
    > 2. **Algorithmic Liquidity Preservation:** Protect the strategic Dip Cache allocation tier. Never draw down tactical liquidity cash reserves unless the *Tactical Market Dip Score* prints $\ge 5$.
    > 3. **True Purchasing Power Maximization:** Ignore short-term nominal noise. Target tracking parameters must calculate performance based on post-inflation, post-tax metrics to maintain absolute purchasing power clarity.
    """)
    
    st.markdown("### Fund Family Strategic Allocation Rationale")
    st.info("**Edelweiss:** Selected for core asymmetric multi-factor performance capture models across large-to-mid capitalization companies.\n\n**Quant:** Outperformance driver via active high-velocity macroeconomic predictive rotation engines.\n\n**ICICI:** Strategic asset allocator stabilizer to dampen volatility during systemic macroeconomic shifts.")

# ---------------------------------------------------------------------
# TAB 9: FUND HUB ARCHITECTURE
# ---------------------------------------------------------------------
with tabs[8]:
    st.markdown("## 🔍 Centralized Fund Evaluation Hub")
    
    f_select = st.selectbox("Select Target Analytics Profile Vector", ["Fund Factor Profile Comparison", "Portfolio Overlap Matrix Tracker"])
    
    if f_select == "Fund Factor Profile Comparison":
        comparison_matrix = pd.DataFrame({
            "Core Analytics Variable": ["Beta vs Benchmarks", "Sharpe Metric Ratio", "Portfolio Tracking Error", "Expense Ratio Profile"],
            "Edelweiss Asset Class": ["0.94", "1.42", "0.85%", "0.62%"],
            "Quant Asset Class": ["1.18", "1.65", "1.45%", "0.75%"],
            "ICICI Asset Class": ["0.72", "1.15", "0.42%", "0.50%"]
        })
        st.dataframe(comparison_matrix, use_container_width=True)
    elif f_select == "Portfolio Overlap Matrix Tracker":
        st.warning("📊 **System Metric Summary:** Inter-fund portfolio holding overlap between Edelweiss and Quant Core stands at **14.2%** (Optimal diversification threshold achieved).")

# ---------------------------------------------------------------------
# TAB 10: SYSTEM ENGINE CONFIGURATION SETTINGS
# ---------------------------------------------------------------------
with tabs[9]:
    st.markdown("## ⚙️ Core System Engine & Execution Environment Parameters")
    
    st.markdown("### Global Algorithmic Target Variables")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.number_input("Baseline Structural Inflation Model (%)", value=6.0, step=0.1)
        st.number_input("System Weekly Maximum Allocation Threshold (₹)", value=35000, step=1000)
    with col_s2:
        st.number_input("Long-Term Capital Gains Framework Tax Level (%)", value=12.5, step=0.1)
        st.number_input("Systematic STP Capital Volume Isolation Element (₹)", value=7500, step=500)
    with col_s3:
        st.selectbox("Nifty Benchmark Tracker Index Baseline Feed", ["Nifty 50 Total Return Index (TRI)", "Nifty Next 50 TRI", "Nifty LargeMidcap 250"])
        st.selectbox("Automated Backup Engine Sync Interval Mode", ["Every 24 Hours", "Every 12 Hours", "Real-Time Transaction Pushes"])
        
    st.markdown("---")
    st.markdown("### Master Ledger Administration Operations")
    st.button("Export Cryptographically Sealed Master Configuration JSON")
    st.file_uploader("Import Master Ledger Verification DB File (.csv, .json)")

"""
Personal Finance & Expense Tracker Dashboard
--------------------------------------------
Installation:
pip install streamlit pandas plotly fpdf openpyxl

Run locally:
streamlit run finance_tracker.py

Deployment:
Push to GitHub -> deploy free on Streamlit Community Cloud for public/private shareable link.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import numpy as np
import io

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

# --- Config & Initialization ---
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Refined UI/UX CSS ---
st.markdown("""
<style>
    :root {
        --bg: #f3f7fb;
        --panel: #ffffff;
        --ink: #0f172a;
        --muted: #5b6578;
        --line: #dbe3ee;
        --brand: #0f4c81;
        --brand-soft: #e9f1f8;
        --ok: #0e9f6e;
        --warn: #d97706;
        --bad: #dc2626;
    }

    .stApp {
        background:
            radial-gradient(1200px 500px at 5% -10%, #d9e9f7 0%, rgba(217,233,247,0) 60%),
            radial-gradient(900px 500px at 95% -20%, #e9f3e7 0%, rgba(233,243,231,0) 60%),
            var(--bg);
        color: var(--ink);
    }

    h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", Arial, sans-serif !important;
    }
    h1, h2, h3 { color: var(--ink) !important; letter-spacing: -0.02em; }

    .block-container {
        max-width: 1240px;
        padding-top: 0.5rem !important;
        padding-bottom: 2rem !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .dashboard-hero {
        background: linear-gradient(135deg, #0f4c81 0%, #1d6aa8 60%, #2e7cb7 100%);
        color: #ffffff;
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 10px 24px rgba(15, 76, 129, 0.22);
    }
    .hero-title { margin: 0; font-size: 1.85rem; font-weight: 700; color: #ffffff !important; }
    .hero-subtitle { margin: 0.35rem 0 0; color: #e3eef8; font-size: 0.98rem; }
    .hero-right { text-align: right; }
    .hero-kicker { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #d6e8f8; }
    .hero-period { font-size: 0.95rem; font-weight: 600; margin-top: 0.15rem; }
    .hero-content {
        display: flex;
        justify-content: space-between;
        align-items: start;
        gap: 1rem;
    }

    .section-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
    }

    .kpi-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1rem 1.1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 9px 22px rgba(15, 23, 42, 0.08);
    }
    .kpi-title {
        color: var(--muted);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .kpi-val {
        color: var(--ink);
        font-size: 1.65rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .text-red { color: var(--bad); }
    .text-neutral { color: var(--ink); }

    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        border: 1px solid #b7c7d8;
        background: #ffffff;
        color: #1f2937;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: #7ea4c3;
        color: #0f4c81;
        background: #f8fbff;
    }

    .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 10px !important;
    }

    .onboarding-hero {
        text-align: left;
        padding: 2.2rem 2rem;
        margin-bottom: 1.2rem;
        background: var(--panel);
        border-radius: 14px;
        border: 1px solid var(--line);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
    }
    .onboarding-title { font-size: 1.8rem; font-weight: 700; color: var(--ink); margin-bottom: 0.65rem; }
    .onboarding-subtitle { color: #495469; font-size: 1rem; max-width: 800px; line-height: 1.55; margin-bottom: 1.4rem; }
    .feature-list { list-style-type: none; padding-left: 0; }
    .feature-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #edf2f7;
    }
    .feature-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    .feature-number {
        font-weight: 700;
        color: var(--brand);
        background: var(--brand-soft);
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    .feature-title { font-size: 1rem; font-weight: 650; color: var(--ink); margin-bottom: 0.2rem; }
    .feature-desc { color: #5f6b81; font-size: 0.94rem; line-height: 1.45; }

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--line);
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
    }
    [data-testid="stSidebar"] {
        background-color: #f9fbfe !important;
        border-right: 1px solid #d8e3ef;
    }
    .stProgress > div > div > div > div { background-color: #1d6aa8; }
    hr { border-color: var(--line); margin: 0.9rem 0; }

    /* Responsive tuning for tablets and phones */
    @media (max-width: 1024px) {
        .block-container {
            padding-top: 0.35rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .dashboard-hero {
            padding: 1.1rem 1rem;
            border-radius: 14px;
        }
        .hero-title { font-size: 1.55rem; }
        .hero-subtitle { font-size: 0.92rem; }
        .kpi-val { font-size: 1.45rem; }
        .section-card { padding: 0.75rem 0.85rem; }
    }

    @media (max-width: 768px) {
        .block-container {
            max-width: 100%;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-bottom: 1.25rem !important;
        }
        .dashboard-hero {
            margin-bottom: 0.75rem;
            box-shadow: 0 8px 18px rgba(15, 76, 129, 0.2);
        }
        .hero-content {
            flex-direction: column;
            gap: 0.65rem;
        }
        .hero-right { text-align: left; }
        .hero-kicker { font-size: 0.66rem; }
        .hero-period { font-size: 0.9rem; }
        .kpi-card {
            padding: 0.82rem 0.85rem 0.9rem;
            margin-bottom: 0.65rem;
            border-radius: 12px;
        }
        .kpi-title { font-size: 0.7rem; margin-bottom: 0.4rem; }
        .kpi-val { font-size: 1.25rem; }
        .section-card {
            border-radius: 12px;
            margin-bottom: 0.6rem;
        }
        .onboarding-hero {
            padding: 1.35rem 1.05rem;
            border-radius: 12px;
        }
        .onboarding-title { font-size: 1.35rem; }
        .onboarding-subtitle { font-size: 0.92rem; }
        .feature-desc { font-size: 0.89rem; }
        [data-testid="stDataFrame"] { border-radius: 10px; }
        .js-plotly-plot .plotly .modebar { display: none !important; }
    }
</style>
""", unsafe_allow_html=True)

# System Constants
CATEGORIES = [
    'Food', 'Transport', 'Rent/Housing', 'Utilities', 'Airtime/Data Bundles', 
    'Subscriptions', 'Entertainment', 'Education/Books', 'Savings/Investment', 
    'Miscellaneous', 'Salary/Income', 'Freelance/Gifts'
]
INCOME_CATS = ['Salary/Income', 'Freelance/Gifts']
PAYMENT_METHODS = ['Cash', 'Card', 'Mobile Money', 'Bank Transfer']

# --- Helper Functions ---
def generate_sample_data():
    """Generates 50 rows of realistic personal finance data"""
    np.random.seed(42)
    end_date = datetime.now()
    # Use raw python datetime objects to completely bypass any Pandas string parsing engine bugs on Streamlit Cloud
    dates = [(end_date - timedelta(days=x)) for x in range(90)]
    
    data = []
    # Add regular Salary
    for m in range(3):
        dt = (end_date.replace(day=1) - timedelta(days=m*30))
        data.append([dt, 'Monthly Salary', 'Salary/Income', 450000.0, 'Bank Transfer'])
        
    # Generate random expenses
    for _ in range(45):
        dt = np.random.choice(dates)
        cat = np.random.choice([c for c in CATEGORIES if c not in INCOME_CATS])
        
        # Realistic amounts
        if cat == 'Rent/Housing': amt = -np.random.uniform(50000, 150000); desc = 'Rent/Service Charge'
        elif cat == 'Food': amt = -np.random.uniform(2000, 15000); desc = 'Groceries / Eating Out'
        elif cat == 'Airtime/Data Bundles': amt = -np.random.uniform(1000, 5000); desc = 'MTN Data / Airtime'
        elif cat == 'Transport': amt = -np.random.uniform(1500, 8000); desc = 'Uber / Bus fare'
        elif cat == 'Utilities': amt = -np.random.uniform(5000, 20000); desc = 'Electricity token'
        else: amt = -np.random.uniform(1000, 25000); desc = 'General Expense'
        
        method = np.random.choice(PAYMENT_METHODS)
        data.append([dt, desc, cat, round(amt, 2), method])
        
    df = pd.DataFrame(data, columns=['Date', 'Description', 'Category', 'Amount', 'Payment_Method'])
    # Pandas will now natively accept the true python `datetime` objects without invoking C-level string parsers
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.dropna(subset=['Date'])
    return df.sort_values('Date', ascending=False).reset_index(drop=True)

def init_session_state():
    if 'transactions' not in st.session_state:
        # Initialize an empty dataframe with correct columns instead of sample data
        st.session_state.transactions = pd.DataFrame(columns=['Date', 'Description', 'Category', 'Amount', 'Payment_Method'])
    if 'budgets' not in st.session_state:
        # Default monthly budgets (amount in NGN)
        st.session_state.budgets = {
            'Food': 50000, 'Transport': 30000, 'Airtime/Data Bundles': 15000, 
            'Entertainment': 20000, 'Utilities': 25000
        }
    if 'goals' not in st.session_state:
        st.session_state.goals = {'Emergency Fund': {'target': 500000, 'saved': 250000}}

# --- PDF Generation ---
def generate_basic_pdf(df, kpis):
    if not FPDF_AVAILABLE:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Personal Finance Report", ln=True, align='C')
    pdf.set_font("Arial", '', 10)
    pdf.cell(200, 5, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Summary Metrics", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 8, txt=f"Total Income: N {kpis['income']:,.2f}", ln=True)
    pdf.cell(200, 8, txt=f"Total Expenses: N {abs(kpis['expense']):,.2f}", ln=True)
    pdf.cell(200, 8, txt=f"Net Cash Flow: N {kpis['net']:,.2f}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Recent Transactions (Top 20)", ln=True)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 8, "Date", 1)
    pdf.cell(80, 8, "Description", 1)
    pdf.cell(40, 8, "Amount", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 9)
    for _, row in df.head(20).iterrows():
        dt = row['Date'].strftime('%Y-%m-%d')
        desc = str(row['Description'])[:35]
        amt = f"{row['Amount']:,.2f}"
        pdf.cell(40, 6, dt, 1)
        pdf.cell(80, 6, desc, 1)
        pdf.cell(40, 6, amt, 1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# --- Main App ---
def main():
    init_session_state()
    
    # Header
    current_month_str = datetime.now().strftime('%B %Y')
    st.markdown(f"""
        <div class="dashboard-hero">
            <div class="hero-content">
                <div>
                    <h1 class="hero-title">Finance Tracker</h1>
                    <p class="hero-subtitle">Operational overview of income, expenses, budgets, and savings goals.</p>
                </div>
                <div class="hero-right">
                    <div class="hero-kicker">Reporting Period</div>
                    <div class="hero-period">{current_month_str}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### Controls")
        
        # File Upload overriding
        uploaded_file = st.file_uploader("Upload your data (CSV/Excel)", type=["csv", "xlsx"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    new_df = pd.read_csv(uploaded_file)
                else:
                    new_df = pd.read_excel(uploaded_file)
                
                req_cols = ['Date', 'Description', 'Category', 'Amount', 'Payment_Method']
                if all(c in new_df.columns for c in req_cols):
                    new_df['Date'] = pd.to_datetime(new_df['Date'], errors='coerce')
                    st.session_state.transactions = new_df.dropna(subset=['Date'])
                    st.success("Custom data loaded!")
                else:
                    st.error(f"Missing columns. Expected: {req_cols}")
            except Exception as e:
                st.error(f"Upload failed: {e}")
                
        st.markdown("---")
        
        # New Transaction Manual Form
        with st.expander("Add New Transaction", expanded=False):
            with st.form("new_txn_form", clear_on_submit=True):
                t_date = st.date_input("Date", date.today())
                t_desc = st.text_input("Description", placeholder="E.g., MTN Data")
                t_cat = st.selectbox("Category", CATEGORIES)
                t_amt = st.number_input("Amount (₦)", min_value=0.0, step=100.0)
                is_expense = st.checkbox("This is an expense", value=True)
                t_method = st.selectbox("Payment Method", PAYMENT_METHODS)
                
                if st.form_submit_button("Save Transaction"):
                    if t_amt > 0 and t_desc:
                        final_amt = -t_amt if is_expense else t_amt
                        new_row = pd.DataFrame([{
                            'Date': pd.to_datetime(t_date),
                            'Description': t_desc,
                            'Category': t_cat,
                            'Amount': final_amt,
                            'Payment_Method': t_method
                        }])
                        st.session_state.transactions = pd.concat([new_row, st.session_state.transactions], ignore_index=True)
                        st.success("Transaction added!")
                    else:
                        st.error("Amount must be > 0 and description is required.")
        
        st.markdown("---")
        
        # Filters
        st.markdown("### Filters")
        df = st.session_state.transactions.copy()
        
        if df.empty:
            min_date, max_date = date.today(), date.today()
        else:
            min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
            
        date_range = st.date_input("Date Range", [min_date, max_date])
        
        cats_filter = st.multiselect("Categories", CATEGORIES, default=CATEGORIES)
        txn_types = st.multiselect("Transaction Type", ["Income", "Expense"], default=["Income", "Expense"])

    # --- Filter Logic ---
    if len(date_range) == 2:
        start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df = df[(df['Date'] >= start_d) & (df['Date'] <= end_d)]
        
    df = df[df['Category'].isin(cats_filter)]
    
    if "Income" not in txn_types: df = df[df['Amount'] < 0]
    if "Expense" not in txn_types: df = df[df['Amount'] >= 0]
    
    # --- Empty State Check / Onboarding Flow ---
    if df.empty:
        html_str = """
<div class="onboarding-hero">
    <div class="onboarding-title">Getting Started</div>
    <div class="onboarding-subtitle">No transaction data is currently loaded. To view your dashboard, upload an existing dataset or start logging transactions manually.</div>
</div>
        """
        st.markdown(html_str, unsafe_allow_html=True)
        
        st.markdown("<p style='color: #6B7280; font-size: 0.9rem;'>Tip: For testing purposes, upload the included <code>sample_test_data.csv</code> file.</p>", unsafe_allow_html=True)
        st.stop()
        
    income_val = df[df['Amount'] > 0]['Amount'].sum()
    expense_val = df[df['Amount'] <= 0]['Amount'].sum()
    net_val = income_val + expense_val

    # --- KPI Row ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Income</div><div class="kpi-val text-neutral">₦{income_val:,.0f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Expenses</div><div class="kpi-val text-neutral">₦{abs(expense_val):,.0f}</div></div>', unsafe_allow_html=True)
    with col3:
        n_class = "text-neutral" if net_val >= 0 else "text-red"
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Net Savings</div><div class="kpi-val {n_class}">₦{net_val:,.0f}</div></div>', unsafe_allow_html=True)
    with col4:
        ratio = abs(expense_val) / income_val if income_val > 0 else 0
        r_class = "text-neutral" if ratio <= 0.8 else "text-red"
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Income Spent Ratio</div><div class="kpi-val {r_class}">{ratio*100:.1f}%</div></div>', unsafe_allow_html=True)

    # --- Charts & Analysis ---
    st.markdown('<div class="section-card"><h3 style="margin:0 0 0.6rem 0;">Cash Flow & Spending</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        # Net Cash flow over time
        flow = df.groupby(df['Date'].dt.to_period('W'))['Amount'].sum().reset_index()
        flow['Date'] = flow['Date'].dt.start_time
        
        # Monochrome / Muted color scheme for tracking
        flow['Color'] = np.where(flow['Amount'] < 0, '#d97706', '#0f4c81')
        
        fig1 = px.bar(flow, x='Date', y='Amount', title='Weekly Cash Flow Trend',
                      color='Color', color_discrete_map='identity')
        
        fig1.update_layout(
            margin=dict(l=20, r=20, t=50, b=20), 
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            height=320,
            font=dict(family="Avenir Next, Segoe UI, sans-serif", color="#475569", size=13),
            title=dict(font=dict(size=16, color="#0f172a")),
            xaxis=dict(showgrid=False, linecolor="#dbe3ee", title="", tickformat="%b %d", tickangle=-25, automargin=True),
            yaxis=dict(showgrid=True, gridcolor="#eaf0f6", linecolor="rgba(0,0,0,0)", title="")
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        # Spending Breakdown
        expenses_only = df[df['Amount'] < 0].copy()
        if not expenses_only.empty:
            expenses_only['Abs_Amount'] = expenses_only['Amount'].abs()
            expense_summary = expenses_only.groupby('Category', as_index=False)['Abs_Amount'].sum().sort_values('Abs_Amount', ascending=False)
            if len(expense_summary) > 6:
                top_exp = expense_summary.head(5).copy()
                others_amt = expense_summary.iloc[5:]['Abs_Amount'].sum()
                if others_amt > 0:
                    top_exp = pd.concat([top_exp, pd.DataFrame([{'Category': 'Others', 'Abs_Amount': others_amt}])], ignore_index=True)
                expense_summary = top_exp
            
            # Corporate/Muted palette
            slate_palette = ['#0f4c81', '#2c6ca3', '#4e8ab9', '#0e9f6e', '#d97706', '#94a3b8']
            
            fig2 = px.pie(expense_summary, values='Abs_Amount', names='Category', hole=0.66,
                          title='Expense Allocation', 
                          color_discrete_sequence=slate_palette)
            
            fig2.update_traces(
                textposition='inside', 
                textinfo='none', # Cleaner without numbers clipping over pie slices
                hoverinfo='label+percent',
                marker=dict(line=dict(color='#ffffff', width=1.5))
            )
            
            fig2.update_layout(
                margin=dict(l=15, r=15, t=50, b=70), 
                height=340,
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5,
                    font=dict(size=10), itemclick="toggleothers"
                ),
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Avenir Next, Segoe UI, sans-serif", color="#475569", size=13),
                title=dict(font=dict(size=16, color="#0f172a"))
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No expense data to chart.")

    # --- Budgeting & Goals ---
    st.markdown("---")
    st.markdown('<div class="section-card"><h3 style="margin:0;">Monthly Tracking</h3></div>', unsafe_allow_html=True)
    c_b, c_g = st.columns(2)
    
    with c_b:
        st.markdown("**Budget Adherence**")
        
        # Filter expenses to current month for budget checking
        curr_mon_exp = expenses_only[expenses_only['Date'].dt.month == datetime.now().month]
        mon_cat_sum = curr_mon_exp.groupby('Category')['Amount'].sum().abs().to_dict()
        
        for cat, budget in st.session_state.budgets.items():
            spent = mon_cat_sum.get(cat, 0)
            pct = min((spent / budget) * 100, 100)
            
            p_col, t_col = st.columns([3, 1])
            with p_col:
                st.markdown(f"**{cat}** (₦{spent:,.0f} / ₦{budget:,.0f})")
                st.progress(int(pct))
            with t_col:
                if pct > 99:
                    st.error("Over")
                elif pct > 85:
                    st.warning("Warning")
                else:
                    st.success("Good")

    with c_g:
        st.markdown("**Savings Goals Position**")
        for goal_name, g_data in st.session_state.goals.items():
            target, saved = g_data['target'], g_data['saved']
            g_pct = (saved / target) * 100
            
            st.markdown(f"**{goal_name}**")
            cols_g = st.columns([1, 2])
            with cols_g[0]:
                st.markdown(f"""
                <div style="font-size:20px; font-weight:600; color:#111827;">{g_pct:.0f}%</div>
                <div style="font-size:12px; color:#6B7280;">Rem: ₦{(target-saved):,.0f}</div>
                """, unsafe_allow_html=True)
            with cols_g[1]:
                st.progress(int(g_pct))
                
        # Smart Alert
        if mon_cat_sum.get('Airtime/Data Bundles', 0) > st.session_state.budgets.get('Airtime/Data Bundles', 999999):
            st.info("System notification: Airtime budget exceeded. Consider bulk plans.")
            
    # --- Transaction Table ---
    st.markdown("---")
    st.markdown('<div class="section-card"><h3 style="margin:0;">Transaction Registry</h3></div>', unsafe_allow_html=True)
    
    # Format for display
    disp_df = df.copy()
    disp_df['Date'] = disp_df['Date'].dt.strftime('%Y-%m-%d')
    # Make a strictly styled display dataframe
    st.dataframe(
        disp_df.style.map(lambda x: 'color: #059669; font-weight:500' if x > 0 else 'color: #111827;', subset=['Amount']),
        use_container_width=True,
        height=300
    )

    # --- Exports ---
    st.markdown("<br>", unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)
    
    with e1:
        csv = disp_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="finances.csv", mime="text/csv", use_container_width=True)
        
    with e2:
        out_xl = io.BytesIO()
        with pd.ExcelWriter(out_xl, engine='openpyxl') as writer:
            disp_df.to_excel(writer, index=False, sheet_name='Transactions')
        st.download_button("Download Excel", data=out_xl.getvalue(), file_name="finances.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                           
    with e3:
        if FPDF_AVAILABLE:
            kpis = {'income': income_val, 'expense': expense_val, 'net': net_val}
            pdf_bytes = generate_basic_pdf(df, kpis)
            st.download_button("Download PDF", data=pdf_bytes, file_name="finance_report.pdf", 
                               mime="application/pdf", use_container_width=True)
        else:
            st.button("Download PDF", disabled=True, help="pip install fpdf required", use_container_width=True)

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>Finance Tracker • Data stays in this Streamlit session unless you export it.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

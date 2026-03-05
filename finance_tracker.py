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
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        margin-bottom: 0.7rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: #eef4fb;
        border: 1px solid #d4e0ed;
        border-radius: 9px;
        color: #334155;
        padding: 0.35rem 0.7rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #0f4c81 !important;
        border-color: #0f4c81 !important;
        color: #ffffff !important;
    }
    label, .stSelectbox label, .stMultiSelect label, .stSlider label, .stTextInput label {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }

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
REQUIRED_COLS = ['Date', 'Description', 'Category', 'Amount', 'Payment_Method']

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
    if 'data_issues' not in st.session_state:
        st.session_state.data_issues = {}
    if 'available_categories' not in st.session_state:
        st.session_state.available_categories = CATEGORIES.copy()
    if 'available_payment_methods' not in st.session_state:
        st.session_state.available_payment_methods = PAYMENT_METHODS.copy()

def refresh_available_categories(df):
    """Use uploaded categories when available; otherwise fallback defaults."""
    dynamic = []
    if not df.empty and 'Category' in df.columns:
        dynamic = sorted([c for c in df['Category'].dropna().astype(str).str.strip().unique().tolist() if c])
    st.session_state.available_categories = dynamic if dynamic else CATEGORIES.copy()

def refresh_available_payment_methods(df):
    """Use uploaded payment methods when available; otherwise fallback defaults."""
    dynamic = []
    if not df.empty and 'Payment_Method' in df.columns:
        dynamic = sorted([m for m in df['Payment_Method'].dropna().astype(str).str.strip().unique().tolist() if m])
    st.session_state.available_payment_methods = dynamic if dynamic else PAYMENT_METHODS.copy()

def clean_transactions(df):
    """Standardize incoming transaction data and report quality issues."""
    issues = {}
    cleaned = df.copy()

    missing_cols = [c for c in REQUIRED_COLS if c not in cleaned.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    cleaned = cleaned[REQUIRED_COLS].copy()
    cleaned['Date'] = pd.to_datetime(cleaned['Date'], errors='coerce')
    cleaned['Amount'] = pd.to_numeric(cleaned['Amount'], errors='coerce')
    cleaned['Description'] = cleaned['Description'].fillna('').astype(str).str.strip()
    cleaned['Category'] = cleaned['Category'].fillna('Miscellaneous').astype(str).str.strip()
    cleaned['Payment_Method'] = cleaned['Payment_Method'].fillna('Cash').astype(str).str.strip()

    issues['invalid_dates'] = int(cleaned['Date'].isna().sum())
    issues['invalid_amounts'] = int(cleaned['Amount'].isna().sum())
    issues['blank_descriptions'] = int((cleaned['Description'] == '').sum())
    issues['zero_amounts'] = int((cleaned['Amount'] == 0).sum())
    issues['future_dates'] = int((cleaned['Date'] > pd.Timestamp.today().normalize()).sum())

    cleaned['Description'] = cleaned['Description'].replace('', 'No description')
    cleaned.loc[cleaned['Category'] == '', 'Category'] = 'Miscellaneous'
    cleaned.loc[cleaned['Payment_Method'] == '', 'Payment_Method'] = 'Cash'

    cleaned = cleaned.dropna(subset=['Date', 'Amount'])
    cleaned = cleaned[cleaned['Amount'] != 0]

    return cleaned.sort_values('Date', ascending=False).reset_index(drop=True), issues

def period_bounds(preset, min_date, max_date):
    today = pd.Timestamp.today().normalize()
    if preset == "This Month":
        start = today.replace(day=1)
        end = today
    elif preset == "Last 30 Days":
        start = today - pd.Timedelta(days=29)
        end = today
    elif preset == "Year to Date":
        start = today.replace(month=1, day=1)
        end = today
    elif preset == "All Time":
        start = pd.Timestamp(min_date)
        end = pd.Timestamp(max_date)
    else:
        start = pd.Timestamp(min_date)
        end = pd.Timestamp(max_date)
    return start, end

def compute_kpis(df):
    income = df.loc[df['Amount'] > 0, 'Amount'].sum()
    expenses = df.loc[df['Amount'] < 0, 'Amount'].sum()
    net = income + expenses
    savings_rate = (net / income * 100) if income > 0 else 0

    days_active = max(df['Date'].dt.date.nunique(), 1)
    avg_daily_spend = abs(expenses) / days_active
    largest_expense = abs(df.loc[df['Amount'] < 0, 'Amount'].min()) if (df['Amount'] < 0).any() else 0

    return {
        'income': income,
        'expense': expenses,
        'net': net,
        'savings_rate': savings_rate,
        'avg_daily_spend': avg_daily_spend,
        'largest_expense': largest_expense,
        'days_active': days_active
    }

def month_over_month_net(df):
    month_start = pd.Timestamp.today().normalize().replace(day=1)
    prev_start = (month_start - pd.Timedelta(days=1)).replace(day=1)
    prev_end = month_start - pd.Timedelta(days=1)

    curr = df[(df['Date'] >= month_start)]['Amount'].sum()
    prev = df[(df['Date'] >= prev_start) & (df['Date'] <= prev_end)]['Amount'].sum()
    delta = curr - prev
    return curr, prev, delta

def detect_unusual_expenses(df):
    expenses = df[df['Amount'] < 0].copy()
    if len(expenses) < 8:
        return pd.DataFrame(columns=df.columns)
    expenses['Abs_Amount'] = expenses['Amount'].abs()
    threshold = expenses['Abs_Amount'].mean() + (2 * expenses['Abs_Amount'].std(ddof=0))
    outliers = expenses[expenses['Abs_Amount'] >= threshold].drop(columns=['Abs_Amount'])
    return outliers.sort_values('Amount')

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
    current_month_str = datetime.now().strftime('%B %Y')
    st.markdown(f"""
        <div class="dashboard-hero">
            <div class="hero-content">
                <div>
                    <h1 class="hero-title">Finance Tracker</h1>
                    <p class="hero-subtitle">Sharper finance operations: clean data, stronger controls, and richer insights.</p>
                </div>
                <div class="hero-right">
                    <div class="hero-kicker">Reporting Period</div>
                    <div class="hero-period">{current_month_str}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Controls")
        cta_l, cta_r = st.columns(2)
        with cta_l:
            if st.button("Load Sample", use_container_width=True):
                sample_df, issues = clean_transactions(generate_sample_data())
                st.session_state.transactions = sample_df
                st.session_state.data_issues = issues
                refresh_available_categories(sample_df)
                refresh_available_payment_methods(sample_df)
                st.rerun()
        with cta_r:
            if st.button("Clear Data", use_container_width=True):
                st.session_state.transactions = pd.DataFrame(columns=REQUIRED_COLS)
                st.session_state.data_issues = {}
                st.session_state.available_categories = CATEGORIES.copy()
                st.session_state.available_payment_methods = PAYMENT_METHODS.copy()
                st.rerun()

        uploaded_file = st.file_uploader("Upload data (CSV/Excel)", type=["csv", "xlsx"])
        if uploaded_file:
            try:
                raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                cleaned, issues = clean_transactions(raw_df)
                st.session_state.transactions = cleaned
                st.session_state.data_issues = issues
                refresh_available_categories(cleaned)
                refresh_available_payment_methods(cleaned)
                st.success(f"Loaded {len(cleaned)} clean records.")
            except Exception as e:
                st.error(f"Upload failed: {e}")

        issues = st.session_state.data_issues
        if issues:
            flagged = {k: v for k, v in issues.items() if v > 0}
            if flagged:
                issue_text = ", ".join([f"{k.replace('_', ' ')}: {v}" for k, v in flagged.items()])
                st.caption(f"Data quality checks: {issue_text}")

        st.markdown("---")
        with st.expander("Add New Transaction", expanded=False):
            with st.form("new_txn_form", clear_on_submit=True):
                category_options = st.session_state.available_categories
                t_date = st.date_input("Date", date.today())
                t_desc = st.text_input("Description", placeholder="E.g., Electricity token")
                t_cat = st.selectbox("Category", category_options)
                default_expense = t_cat not in INCOME_CATS
                t_amt = st.number_input("Amount (₦)", min_value=0.0, step=100.0)
                is_expense = st.checkbox("Mark as expense", value=default_expense)
                payment_options = st.session_state.available_payment_methods
                t_method = st.selectbox("Payment Method", payment_options)
                if st.form_submit_button("Save Transaction"):
                    if t_amt <= 0 or not t_desc.strip():
                        st.error("Amount must be above zero and description is required.")
                    else:
                        entry = pd.DataFrame([{
                            'Date': pd.to_datetime(t_date),
                            'Description': t_desc.strip(),
                            'Category': t_cat,
                            'Amount': -t_amt if is_expense else t_amt,
                            'Payment_Method': t_method
                        }])
                        merged = pd.concat([entry, st.session_state.transactions], ignore_index=True)
                        cleaned, issues = clean_transactions(merged)
                        st.session_state.transactions = cleaned
                        st.session_state.data_issues = issues
                        refresh_available_categories(cleaned)
                        refresh_available_payment_methods(cleaned)
                        st.success("Transaction added.")

        with st.expander("Budgets & Goals", expanded=False):
            budget_choices = st.session_state.available_categories
            b_cat = st.selectbox("Budget category", budget_choices)
            b_amt = st.number_input("Monthly budget (₦)", min_value=0.0, value=float(st.session_state.budgets.get(b_cat, 0)), step=1000.0)
            if st.button("Update Budget", use_container_width=True):
                st.session_state.budgets[b_cat] = int(b_amt)
                st.success(f"{b_cat} budget updated.")

            st.markdown("**Emergency Fund Goal**")
            g_target = st.number_input("Target (₦)", min_value=1.0, value=float(st.session_state.goals['Emergency Fund']['target']), step=10000.0)
            g_saved = st.number_input("Current saved (₦)", min_value=0.0, value=float(st.session_state.goals['Emergency Fund']['saved']), step=5000.0)
            if st.button("Update Goal", use_container_width=True):
                st.session_state.goals['Emergency Fund'] = {'target': int(g_target), 'saved': int(g_saved)}
                st.success("Goal updated.")

        st.markdown("---")
        st.markdown("### Filters")
        base_df = st.session_state.transactions.copy()
        if base_df.empty:
            min_date, max_date = date.today(), date.today()
        else:
            min_date, max_date = base_df['Date'].min().date(), base_df['Date'].max().date()

        period_preset = st.selectbox("Time Window", ["Custom", "This Month", "Last 30 Days", "Year to Date", "All Time"], index=4)
        date_range = st.date_input("Date Range", [min_date, max_date], disabled=(period_preset != "Custom"))
        category_filters = st.session_state.available_categories
        cats_filter = st.multiselect("Categories", category_filters, default=category_filters)
        payment_filters = st.session_state.available_payment_methods
        methods_filter = st.multiselect("Payment Methods", payment_filters, default=payment_filters)
        txn_type_options = []
        if not base_df.empty and (base_df['Amount'] > 0).any():
            txn_type_options.append("Income")
        if not base_df.empty and (base_df['Amount'] < 0).any():
            txn_type_options.append("Expense")
        if not txn_type_options:
            txn_type_options = ["Income", "Expense"]
        txn_types = st.multiselect("Transaction Type", txn_type_options, default=txn_type_options)
        search_q = st.text_input("Search Description", placeholder="e.g. Uber, rent, salary")
        amt_floor = float(base_df['Amount'].min()) if not base_df.empty else -500000.0
        amt_ceil = float(base_df['Amount'].max()) if not base_df.empty else 500000.0
        amount_range = st.slider("Amount Range (₦)", min_value=amt_floor, max_value=amt_ceil, value=(amt_floor, amt_ceil))

    df = st.session_state.transactions.copy()
    refresh_available_categories(df)
    refresh_available_payment_methods(df)
    if df.empty:
        st.markdown("""
        <div class="onboarding-hero">
            <div class="onboarding-title">Getting Started</div>
            <div class="onboarding-subtitle">Upload your data or click "Load Sample" in the sidebar to see the full analytics workspace.</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    if period_preset == "Custom" and len(date_range) == 2:
        start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    else:
        start_d, end_d = period_bounds(period_preset, min_date, max_date)
    df = df[(df['Date'] >= start_d) & (df['Date'] <= end_d)]
    df = df[df['Category'].isin(cats_filter)]
    df = df[df['Payment_Method'].isin(methods_filter)]
    if "Income" not in txn_types:
        df = df[df['Amount'] < 0]
    if "Expense" not in txn_types:
        df = df[df['Amount'] > 0]
    if search_q.strip():
        df = df[df['Description'].str.contains(search_q.strip(), case=False, na=False)]
    df = df[(df['Amount'] >= amount_range[0]) & (df['Amount'] <= amount_range[1])]

    if df.empty:
        st.warning("No records match the active filters. Broaden your filters to continue.")
        st.stop()

    kpis = compute_kpis(df)
    curr_net, prev_net, net_delta = month_over_month_net(st.session_state.transactions)
    delta_color = "text-neutral" if net_delta >= 0 else "text-red"

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Income</div><div class="kpi-val">₦{kpis["income"]:,.0f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Expenses</div><div class="kpi-val">₦{abs(kpis["expense"]):,.0f}</div></div>', unsafe_allow_html=True)
    with m3:
        n_class = "text-neutral" if kpis["net"] >= 0 else "text-red"
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Net Savings</div><div class="kpi-val {n_class}">₦{kpis["net"]:,.0f}</div></div>', unsafe_allow_html=True)
    with m4:
        sr_class = "text-neutral" if kpis["savings_rate"] >= 0 else "text-red"
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Savings Rate</div><div class="kpi-val {sr_class}">{kpis["savings_rate"]:.1f}%</div></div>', unsafe_allow_html=True)
    with m5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">MoM Net Change</div><div class="kpi-val {delta_color}">₦{net_delta:,.0f}</div></div>', unsafe_allow_html=True)

    st.caption(f"Current month net: ₦{curr_net:,.0f}  |  Previous month net: ₦{prev_net:,.0f}")

    tab_overview, tab_insights, tab_transactions = st.tabs(["Overview", "Insights", "Transactions & Export"])

    with tab_overview:
        st.markdown('<div class="section-card"><h3 style="margin:0 0 0.6rem 0;">Cash Flow & Allocation</h3></div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.45, 1])
        with c1:
            flow = df.groupby(df['Date'].dt.to_period('W'))['Amount'].sum().reset_index()
            flow['Date'] = flow['Date'].dt.start_time
            flow['Color'] = np.where(flow['Amount'] < 0, '#d97706', '#0f4c81')
            fig1 = px.bar(flow, x='Date', y='Amount', title='Weekly Cash Flow Trend', color='Color', color_discrete_map='identity')
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

            daily = (
                df.sort_values('Date')
                .assign(Day=df['Date'].dt.floor('D'))
                .groupby('Day', as_index=False)['Amount']
                .sum()
            )
            daily['Balance'] = daily['Amount'].cumsum()
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=daily['Day'], y=daily['Balance'], mode='lines',
                line=dict(color='#0e9f6e', width=2.4), name='Running Balance'
            ))
            fig_line.update_layout(
                title="Running Net Balance",
                margin=dict(l=15, r=15, t=45, b=10),
                height=260,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Avenir Next, Segoe UI, sans-serif", color="#475569", size=12),
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor="#eaf0f6", title="")
            )
            st.plotly_chart(fig_line, use_container_width=True)

        with c2:
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
                fig2 = px.pie(
                    expense_summary, values='Abs_Amount', names='Category', hole=0.66, title='Expense Allocation',
                    color_discrete_sequence=['#0f4c81', '#2c6ca3', '#4e8ab9', '#0e9f6e', '#d97706', '#94a3b8']
                )
                fig2.update_traces(textposition='inside', textinfo='none', hoverinfo='label+percent',
                                   marker=dict(line=dict(color='#ffffff', width=1.5)))
                fig2.update_layout(
                    margin=dict(l=15, r=15, t=50, b=70),
                    height=340,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5, font=dict(size=10)),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Avenir Next, Segoe UI, sans-serif", color="#475569", size=13),
                    title=dict(font=dict(size=16, color="#0f172a"))
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No expense data to chart.")

            st.markdown("**Budget Adherence (This Month)**")
            curr_month = pd.Timestamp.today().month
            curr_year = pd.Timestamp.today().year
            month_exp = st.session_state.transactions[
                (st.session_state.transactions['Date'].dt.month == curr_month) &
                (st.session_state.transactions['Date'].dt.year == curr_year) &
                (st.session_state.transactions['Amount'] < 0)
            ]
            month_cat_sum = month_exp.groupby('Category')['Amount'].sum().abs().to_dict()
            for cat, budget in st.session_state.budgets.items():
                spent = month_cat_sum.get(cat, 0)
                pct = 0 if budget <= 0 else min((spent / budget) * 100, 100)
                st.markdown(f"**{cat}**  `₦{spent:,.0f} / ₦{budget:,.0f}`")
                st.progress(int(pct))

    with tab_insights:
        st.markdown('<div class="section-card"><h3 style="margin:0;">Performance Insights</h3></div>', unsafe_allow_html=True)
        i1, i2, i3 = st.columns(3)
        top_category = "N/A"
        if (df['Amount'] < 0).any():
            top_category = df[df['Amount'] < 0].groupby('Category')['Amount'].sum().abs().sort_values(ascending=False).index[0]
        with i1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Top Expense Category</div><div class="kpi-val">{top_category}</div></div>', unsafe_allow_html=True)
        with i2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Average Daily Spend</div><div class="kpi-val">₦{kpis["avg_daily_spend"]:,.0f}</div></div>', unsafe_allow_html=True)
        with i3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">Largest Single Expense</div><div class="kpi-val">₦{kpis["largest_expense"]:,.0f}</div></div>', unsafe_allow_html=True)

        left, right = st.columns([1.3, 1])
        with left:
            spenders = df[df['Amount'] < 0].copy()
            if not spenders.empty:
                spenders['Abs_Amount'] = spenders['Amount'].abs()
                top_txn = spenders.nlargest(8, 'Abs_Amount')[['Date', 'Description', 'Category', 'Abs_Amount']].copy()
                top_txn['Date'] = top_txn['Date'].dt.strftime('%Y-%m-%d')
                top_txn = top_txn.rename(columns={'Abs_Amount': 'Amount'})
                st.markdown("**Top Expense Transactions**")
                st.dataframe(top_txn, use_container_width=True, height=290)
            else:
                st.info("No expense records in current filters.")
        with right:
            anomalies = detect_unusual_expenses(df)
            st.markdown("**Unusual Expense Alerts**")
            if anomalies.empty:
                st.success("No unusual expenses detected for this filter scope.")
            else:
                anomalies_view = anomalies[['Date', 'Description', 'Category', 'Amount']].copy()
                anomalies_view['Date'] = anomalies_view['Date'].dt.strftime('%Y-%m-%d')
                anomalies_view['Amount'] = anomalies_view['Amount'].map(lambda x: f"₦{abs(x):,.0f}")
                st.dataframe(anomalies_view, use_container_width=True, height=290)

        g = st.session_state.goals.get('Emergency Fund', {'target': 1, 'saved': 0})
        goal_pct = min((g['saved'] / g['target']) * 100, 100) if g['target'] > 0 else 0
        st.markdown("**Savings Goal Progress**")
        st.progress(int(goal_pct))
        st.caption(f"Emergency Fund: ₦{g['saved']:,.0f} saved out of ₦{g['target']:,.0f}")

    with tab_transactions:
        st.markdown('<div class="section-card"><h3 style="margin:0;">Transactions & Export</h3></div>', unsafe_allow_html=True)
        disp_df = df.sort_values('Date', ascending=False).copy()
        disp_df['Date'] = disp_df['Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(
            disp_df.style.map(lambda x: 'color: #059669; font-weight:600' if x > 0 else 'color: #111827;', subset=['Amount']),
            use_container_width=True,
            height=360
        )
        st.markdown("<br>", unsafe_allow_html=True)
        e1, e2, e3 = st.columns(3)
        with e1:
            csv = disp_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="finances.csv", mime="text/csv", use_container_width=True)
        with e2:
            out_xl = io.BytesIO()
            with pd.ExcelWriter(out_xl, engine='openpyxl') as writer:
                disp_df.to_excel(writer, index=False, sheet_name='Transactions')
            st.download_button(
                "Download Excel",
                data=out_xl.getvalue(),
                file_name="finances.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with e3:
            if FPDF_AVAILABLE:
                pdf_bytes = generate_basic_pdf(df, {'income': kpis['income'], 'expense': kpis['expense'], 'net': kpis['net']})
                st.download_button("Download PDF", data=pdf_bytes, file_name="finance_report.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.button("Download PDF", disabled=True, help="pip install fpdf required", use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>Finance Tracker • Data stays in this Streamlit session unless you export it.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

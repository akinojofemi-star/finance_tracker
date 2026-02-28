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

# --- Modern UI/UX CSS ---
st.markdown("""
<style>
    .stApp { background-color: #F4F6F9; }
    h1, h2, h3 { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    .kpi-card {
        background-color: white; border-radius: 12px;
        padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-top: 4px solid #E2E8F0;
    }
    .kpi-title { color: #64748B; font-size: 0.9rem; text-transform: uppercase; font-weight: 600; margin-bottom: 8px;}
    .kpi-val { color: #0F172A; font-size: 1.8rem; font-weight: 700; }
    
    /* Dynamic border colors */
    .border-green { border-top-color: #10B981 !important; }
    .border-red { border-top-color: #EF4444 !important; }
    .border-blue { border-top-color: #3B82F6 !important; }
    .border-purple { border-top-color: #8B5CF6 !important; }

    /* Button styling */
    .stButton>button {
        border-radius: 8px; font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    
    /* Table font */
    [data-testid="stDataFrame"] { font-size: 14px; }
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
    dates = [(end_date - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(90)]
    
    data = []
    # Add regular Salary
    for m in range(3):
        dt = (end_date.replace(day=1) - timedelta(days=m*30)).strftime('%Y-%m-%d')
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
    # Explicitly define format and coerce errors to bypass strict Streamlit Cloud pandas constraints
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['Date'])
    return df.sort_values('Date', ascending=False).reset_index(drop=True)

def init_session_state():
    if 'transactions' not in st.session_state:
        st.session_state.transactions = generate_sample_data()
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
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 10px;">
            <h1 style="margin:0;">💰 Personal Finance Dashboard</h1>
            <span style="color: #64748B; font-weight: 500;">Current period: {current_month_str}</span>
        </div>
        <hr style="margin-top: 0;">
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.header("🎛️ Controls")
        
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
        with st.expander("➕ Add New Transaction", expanded=False):
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
        st.subheader("📅 Filters")
        df = st.session_state.transactions.copy()
        
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
    
    if df.empty:
        st.warning("No transactions match the selected filters.")
        st.stop()
        
    income_val = df[df['Amount'] > 0]['Amount'].sum()
    expense_val = df[df['Amount'] <= 0]['Amount'].sum()
    net_val = income_val + expense_val

    # --- KPI Row ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="kpi-card border-green"><div class="kpi-title">Total Income</div><div class="kpi-val" style="color:#10B981;">₦ {income_val:,.0f}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card border-red"><div class="kpi-title">Total Expenses</div><div class="kpi-val" style="color:#EF4444;">₦ {abs(expense_val):,.0f}</div></div>', unsafe_allow_html=True)
    with col3:
        n_color = "#3B82F6" if net_val >= 0 else "#EF4444"
        st.markdown(f'<div class="kpi-card border-blue"><div class="kpi-title">Net Savings</div><div class="kpi-val" style="color:{n_color};">₦ {net_val:,.0f}</div></div>', unsafe_allow_html=True)
    with col4:
        # Simple health check calculation
        ratio = abs(expense_val) / income_val if income_val > 0 else 0
        h_color = "#10B981" if ratio <= 0.50 else ("#F59E0B" if ratio <= 0.8 else "#EF4444")
        st.markdown(f'<div class="kpi-card border-purple"><div class="kpi-title">Income Spent Ratio</div><div class="kpi-val" style="color:{h_color};">{ratio*100:.1f}%</div></div>', unsafe_allow_html=True)

    # --- Charts & Analysis ---
    st.markdown("### 📊 Cash Flow & Spending Analysis")
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        # Net Cash flow over time
        flow = df.groupby(df['Date'].dt.to_period('W'))['Amount'].sum().reset_index()
        flow['Date'] = flow['Date'].dt.start_time
        
        fig1 = px.bar(flow, x='Date', y='Amount', title='Weekly Net Cash Flow',
                      color='Amount', color_continuous_scale=[(0, '#EF4444'), (1, '#10B981')],
                      color_continuous_midpoint=0)
        fig1.update_layout(margin=dict(l=0, r=0, t=30, b=0), plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        # Spending Breakdown
        expenses_only = df[df['Amount'] < 0].copy()
        if not expenses_only.empty:
            expenses_only['Abs_Amount'] = expenses_only['Amount'].abs()
            fig2 = px.pie(expenses_only, values='Abs_Amount', names='Category', hole=0.5,
                          title='Expense Breakdown', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_traces(textposition='inside', textinfo='percent')
            fig2.update_layout(margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No expense data to chart.")

    # --- Budgeting & Goals ---
    st.markdown("---")
    c_b, c_g = st.columns(2)
    
    with c_b:
        st.markdown("### 🎯 Monthly Budget Tracker")
        
        # Filter expenses to current month for budget checking
        curr_mon_exp = expenses_only[expenses_only['Date'].dt.month == datetime.now().month]
        mon_cat_sum = curr_mon_exp.groupby('Category')['Amount'].sum().abs().to_dict()
        
        for cat, budget in st.session_state.budgets.items():
            spent = mon_cat_sum.get(cat, 0)
            pct = min((spent / budget) * 100, 100)
            
            p_col, t_col = st.columns([3, 1])
            with p_col:
                st.markdown(f"**{cat}** (₦{spent:,.0f} / ₦{budget:,.0f})")
                color = "normal" if pct < 85 else "excpetion" # Note: Streamlit uses primary/normal. Progress color styling is limited but bar reflects completion
                st.progress(int(pct))
            with t_col:
                if pct > 99:
                    st.error("Over", icon="🚨")
                elif pct > 85:
                    st.warning("Warning", icon="⚠️")
                else:
                    st.success("Good", icon="✅")

    with c_g:
        st.markdown("### 🏆 Savings Goals")
        for goal_name, g_data in st.session_state.goals.items():
            target, saved = g_data['target'], g_data['saved']
            g_pct = (saved / target) * 100
            
            st.markdown(f"**{goal_name}**")
            cols_g = st.columns([1, 2])
            with cols_g[0]:
                st.markdown(f"""
                <div style="font-size:24px; font-weight:bold; color:#10B981;">{g_pct:.0f}%</div>
                <div style="font-size:12px; color:gray;">Remaining: ₦{(target-saved):,.0f}</div>
                """, unsafe_allow_html=True)
            with cols_g[1]:
                st.progress(int(g_pct))
                
        # Smart Alert
        if mon_cat_sum.get('Airtime/Data Bundles', 0) > st.session_state.budgets.get('Airtime/Data Bundles', 999999):
            st.info("💡 **Insight:** You exceeded your Airtime/Data budget this month. Consider buying a larger 30-day bulk bundle to save money.")
            
    # --- Transaction Table ---
    st.markdown("---")
    st.markdown("### 📋 Transaction History")
    
    # Format for display
    disp_df = df.copy()
    disp_df['Date'] = disp_df['Date'].dt.strftime('%Y-%m-%d')
    # Make a strictly styled display dataframe
    st.dataframe(
        disp_df.style.map(lambda x: 'color: #10B981; font-weight:bold' if x > 0 else 'color: #EF4444;', subset=['Amount']),
        use_container_width=True,
        height=300
    )

    # --- Exports ---
    st.markdown("---")
    e1, e2, e3 = st.columns(3)
    
    with e1:
        csv = disp_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="finances.csv", mime="text/csv", use_container_width=True)
        
    with e2:
        out_xl = io.BytesIO()
        with pd.ExcelWriter(out_xl, engine='openpyxl') as writer:
            disp_df.to_excel(writer, index=False, sheet_name='Transactions')
        st.download_button("📊 Download Excel", data=out_xl.getvalue(), file_name="finances.xlsx", 
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                           
    with e3:
        if FPDF_AVAILABLE:
            kpis = {'income': income_val, 'expense': expense_val, 'net': net_val}
            pdf_bytes = generate_basic_pdf(df, kpis)
            st.download_button("📄 PDF Summary", data=pdf_bytes, file_name="finance_report.pdf", 
                               mime="application/pdf", use_container_width=True)
        else:
            st.button("📄 PDF Summary", disabled=True, help="pip install fpdf required", use_container_width=True)

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 13px;'>Track smarter • Built with Streamlit • All data is processed securely in your browser session.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

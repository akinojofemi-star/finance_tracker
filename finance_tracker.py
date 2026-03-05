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

# --- Minimalist UI/UX CSS ---
st.markdown("""
<style>
    /* Global Theme */
    .stApp { 
        background-color: #FAFAFA;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div { 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important; 
    }
    
    h1, h2, h3 { color: #111827 !important; letter-spacing: -0.02em; font-weight: 700; }
    
    /* Layout Adjustments */
    .block-container { padding-top: 1.5rem !important; max-width: 1200px; }
    
    /* Minimalist KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 24px;
        transition: border-color 0.2s ease;
    }
    .kpi-card:hover { border-color: #D1D5DB; }
    .kpi-title { color: #6B7280; font-size: 0.875rem; font-weight: 500; margin-bottom: 8px;}
    .kpi-val { color: #111827; font-size: 2rem; font-weight: 600; line-height: 1.2; letter-spacing: -0.02em;}
    
    /* Subtle Utility Classes */
    .text-green { color: #059669; }
    .text-red { color: #DC2626; }
    .text-neutral { color: #111827; }

    /* Button Polish */
    .stButton>button {
        border-radius: 6px; font-weight: 500;
        border: 1px solid #D1D5DB;
        background: #FFFFFF;
        color: #374151;
        transition: all 0.15s ease-in-out;
        padding: 0.5rem 1rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .stButton>button:hover { 
        border-color: #9CA3AF;
        background: #F9FAFB;
        color: #111827;
    }
    
    /* Clean Empty State */
    .onboarding-hero {
        text-align: left;
        padding: 3rem 2.5rem;
        margin-bottom: 1.5rem;
        background: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    .onboarding-title { font-size: 2rem; font-weight: 700; color: #111827; margin-bottom: 0.75rem; }
    .onboarding-subtitle { color: #4B5563; font-size: 1.1rem; max-width: 800px; line-height: 1.5; font-weight: 400; margin-bottom: 2rem; }
    
    .feature-list { list-style-type: none; padding-left: 0; }
    .feature-item { 
        display: flex; align-items: flex-start; margin-bottom: 1.5rem; 
        padding-bottom: 1.5rem; border-bottom: 1px solid #F3F4F6;
    }
    .feature-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
    .feature-number { 
        font-weight: 600; color: #111827; background: #F3F4F6; width: 32px; height: 32px; 
        border-radius: 50%; display: flex; align-items: center; justify-content: center; 
        margin-right: 1.25rem; flex-shrink: 0;
    }
    .feature-text-block { flex-grow: 1; }
    .feature-title { font-size: 1.1rem; font-weight: 600; color: #111827; margin-bottom: 0.25rem; }
    .feature-desc { color: #6B7280; font-size: 0.95rem; line-height: 1.5; }
    
    /* Table & UI Polish */
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #E5E7EB; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E5E7EB; }
    .stProgress .st-bo { background-color: #4B5563; }
    hr { border-color: #E5E7EB; }
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
        <div style="display: flex; justify-content: space-between; align-items: top; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #E5E7EB;">
            <div>
                <h1 style="margin:0; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.02em;">Finance Tracker</h1>
                <p style="margin: 0; color: #6B7280; font-size: 0.95rem; margin-top: 4px;">Overview and Insights</p>
            </div>
            <div style="text-align: right;">
                <span style="color: #6B7280; font-size: 0.85rem; font-weight: 500; text-transform: uppercase;">Reporting Period</span><br>
                <span style="color: #111827; font-size: 0.95rem; font-weight: 600;">{current_month_str}</span>
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
        st.markdown("""
            <div class="onboarding-hero">
                <div class="onboarding-title">Getting Started</div>
                <div class="onboarding-subtitle">No transaction data is currently loaded. To view your dashboard, upload an existing dataset or start logging transactions manually.</div>
                
                <ul class="feature-list">
                    <li class="feature-item">
                        <div class="feature-number">1</div>
                        <div class="feature-text-block">
                            <div class="feature-title">Import historical data</div>
                            <div class="feature-desc">Use the sidebar to upload a CSV or Excel file containing your transaction history. The file must include Date, Description, Category, Amount, and Payment_Method columns.</div>
                        </div>
                    </li>
                    <li class="feature-item">
                        <div class="feature-number">2</div>
                        <div class="feature-text-block">
                            <div class="feature-title">Log records manually</div>
                            <div class="feature-desc">Expand the "Add New Transaction" form in the sidebar to enter single expenses or income items directly into the system.</div>
                        </div>
                    </li>
                    <li class="feature-item">
                        <div class="feature-number">3</div>
                        <div class="feature-text-block">
                            <div class="feature-title">Review analysis</div>
                            <div class="feature-desc">Once data is populated, this dashboard will automatically generate reporting on spending, net cash flow, and budget adherence.</div>
                        </div>
                    </li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
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
    st.markdown("### Cash Flow & Spending")
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        # Net Cash flow over time
        flow = df.groupby(df['Date'].dt.to_period('W'))['Amount'].sum().reset_index()
        flow['Date'] = flow['Date'].dt.start_time
        
        # Monochrome / Muted color scheme for tracking
        flow['Color'] = np.where(flow['Amount'] < 0, '#9CA3AF', '#4B5563')
        
        fig1 = px.bar(flow, x='Date', y='Amount', title='Weekly Cash Flow Trend',
                      color='Color', color_discrete_map='identity')
        
        fig1.update_layout(
            margin=dict(l=20, r=20, t=50, b=20), 
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", color="#4B5563", size=13),
            title=dict(font=dict(size=16, color="#111827", weight="normal")),
            xaxis=dict(showgrid=False, linecolor="#E5E7EB", title=""),
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6", linecolor="rgba(0,0,0,0)", title="")
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        # Spending Breakdown
        expenses_only = df[df['Amount'] < 0].copy()
        if not expenses_only.empty:
            expenses_only['Abs_Amount'] = expenses_only['Amount'].abs()
            
            # Corporate/Muted palette
            slate_palette = ['#4B5563', '#6B7280', '#9CA3AF', '#D1D5DB', '#374151', '#1F2937']
            
            fig2 = px.pie(expenses_only, values='Abs_Amount', names='Category', hole=0.7,
                          title='Expense Allocation', 
                          color_discrete_sequence=slate_palette)
            
            fig2.update_traces(
                textposition='inside', 
                textinfo='none', # Cleaner without numbers clipping over pie slices
                hoverinfo='label+percent',
                marker=dict(line=dict(color='#ffffff', width=1.5))
            )
            
            fig2.update_layout(
                margin=dict(l=20, r=20, t=50, b=20), 
                showlegend=True,
                legend=dict(orientation="v", yanchor="auto", y=0.5, xanchor="right", x=1.3, font=dict(size=11)),
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", color="#4B5563", size=13),
                title=dict(font=dict(size=16, color="#111827", weight="normal"))
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No expense data to chart.")

    # --- Budgeting & Goals ---
    st.markdown("---")
    st.markdown("### Monthly Tracking")
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
                color = "normal" if pct < 85 else "excpetion" # Note: Streamlit uses primary/normal. Progress color styling is limited but bar reflects completion
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
    st.markdown("### Transaction Registry")
    
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
    st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 13px;'>Finance Tracker • All data is processed securely in your browser session.</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

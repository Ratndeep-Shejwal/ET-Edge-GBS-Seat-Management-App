import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Guest Search", page_icon="🔍", layout="wide")

# --- STRICT 100VH CSS ---
st.markdown("""
<style>
    /* Import Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        overflow: hidden; /* STRICTLY DISABLE PAGE SCROLL */
    }

    /* 1. Main Container Lock */
    /* This forces the app to fit exactly 100% of the screen height */
    .stApp {
        height: 100vh;
        overflow: hidden;
        background-color: #FFFFFF;
        color: #111111;
    }

    /* 2. Remove Streamlit's Default Padding */
    /* Streamlit adds huge padding by default. We remove it here. */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    
    /* 3. Header/Footer Kill Switch */
    header {visibility: hidden; display: none;}
    footer {visibility: hidden; display: none;}
    
    /* 4. Compact Logo Area */
    .logo-container { 
        display: flex; 
        justify-content: center; 
        margin-bottom: 10px; 
    }
    
    /* 5. Compact Inputs */
    /* Reduces the height of input boxes to save vertical space */
    .stTextInput>div>div>input { 
        padding: 8px; 
        font-size: 14px;
        border: 1px solid #CCC;
        border-radius: 4px;
    }
    
    /* 6. Button Styling */
    .stButton>button { 
        background-color: #B10015; 
        color: white; 
        border: none; 
        font-weight: 600; 
        text-transform: uppercase;
        width: 100%;
        margin-top: 2px; /* Align with inputs */
        height: 42px;    /* Match input height */
    }
    .stButton>button:hover { background-color: #000000; color: white; }
    
    /* Hide Sidebar */
    [data-testid="stSidebar"] { display: none; }
    
</style>
""", unsafe_allow_html=True)

# --- DATA PROCESSING ---
def process_data(df):
    df.columns = [str(c).strip() for c in df.columns]
    
    # Merge Name
    lower_cols = {c.lower().replace('_', '').replace(' ', ''): c for c in df.columns}
    if 'firstname' in lower_cols and 'lastname' in lower_cols:
        fn, ln = lower_cols['firstname'], lower_cols['lastname']
        df['Name'] = df.apply(lambda x: f"{str(x[fn]).replace('nan','').replace('None','').strip()} {str(x[ln]).replace('nan','').replace('None','').strip()}".strip(), axis=1)

    # Smart Map
    clean_headers = {str(col).lower().strip().replace('_', '').replace(' ', ''): col for col in df.columns}
    mappings = {
        'Seat Number': ['seat', 'seatnumber', 'tableno', 'chair'],
        'Organization': ['organization', 'org', 'company', 'firm'],
        'Name': ['name', 'guestname', 'attendee', 'fullname']
    }
    found = {}
    for std, keys in mappings.items():
        if std in df.columns: continue
        for clean, orig in clean_headers.items():
            if orig not in found.values() and any(k in clean for k in keys):
                found[std] = orig
                break
    df = df.rename(columns={v: k for k, v in found.items()})

    # Cleanup
    df = df.astype(str)
    for col in df.columns: df[col] = df[col].replace(['nan', 'None', 'NaN'], '')
    if 'Name' in df.columns: df = df[df['Name'].str.strip() != '']
    return df

# --- APP LOGIC ---

# 1. LOGO (Centered)
st.markdown("""<div class="logo-container"><img src="https://et-edge.com/wp-content/uploads/2026/02/ET-Edge-Logo-with-Times-Insignia-Final-01-1-1.png" width="220"></div>""", unsafe_allow_html=True)

if 'data' not in st.session_state: st.session_state.data = None

# VIEW 1: UPLOAD
if st.session_state.data is None:
    st.markdown("<br>", unsafe_allow_html=True) # Small spacer
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<h3 style='text-align: center; margin: 0; padding: 0;'>Guest Portal</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Upload guest list (.csv/.xlsx)</p>", unsafe_allow_html=True)
        f = st.file_uploader("", type=['csv', 'xlsx'], label_visibility="collapsed")
        if f:
            try:
                df = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
                st.session_state.data = process_data(df)
                st.rerun()
            except Exception as e: st.error(f"Error: {e}")

# VIEW 2: DASHBOARD
else:
    df = st.session_state.data
    
    # Restart Button (Small & Right Aligned)
    col_h1, col_h2 = st.columns([8, 1])
    with col_h2:
        if st.button("🔄 New", key="rst"):
            st.session_state.data = None
            st.rerun()

    st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #EEE;'>", unsafe_allow_html=True)

    # Filter Bar (Compact)
    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
    with c1: n_q = st.text_input("Name", placeholder="Guest Name")
    with c2: o_q = st.text_input("Org", placeholder="Organization")
    with c3: s_q = st.text_input("Seat", placeholder="Seat No")
    with c4: 
        st.markdown("<div style='margin-top: 2px;'></div>", unsafe_allow_html=True) # Align fix
        st.button("SEARCH", key="go")

    # Filter Logic
    res = df.copy()
    if n_q and 'Name' in df: res = res[res['Name'].str.contains(n_q, case=False, na=False)]
    if o_q and 'Organization' in df: res = res[res['Organization'].str.contains(o_q, case=False, na=False)]
    if s_q and 'Seat Number' in df: res = res[res['Seat Number'].str.contains(s_q, case=False, na=False)]

    # RESULT TABLE (Fixed height for internal scrolling)
    st.markdown("<hr style='margin: 10px 0; border-top: 1px solid #EEE;'>", unsafe_allow_html=True)
    
    if not res.empty:
        # We use a height of 55vh (55% of screen) so it adapts to device height
        # but stays strictly inside the view.
        st.dataframe(
            res.style.apply(lambda x: ['background-color: #B10015; color: white; font-weight: 600'] * len(x) if x.name == 'Seat Number' else [''] * len(x), axis=0),
            use_container_width=True,
            height=450, # Safe height for almost all laptops/tablets to avoid outer scroll
            hide_index=True
        )
    else:

        st.warning("No matches found.")

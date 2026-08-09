import streamlit as st

st.set_page_config(page_title="PCNA Assistant", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { --pcna:#0b4f86; --ink:#17263a; --muted:#6d7a8a; --line:#e7edf3; --panel:#f7f9fb; }
[data-testid="stAppViewContainer"] { background:#fff; }
[data-testid="stSidebar"] { background:#f7f9fb; border-right:1px solid var(--line); }
[data-testid="stSidebar"] > div:first-child { padding-top:1rem; }
.block-container { padding-top:1.25rem; max-width:1500px; }
#MainMenu, footer, header { visibility:hidden; }
.app-name { font-size:.92rem; font-weight:700; color:var(--ink); margin-top:.15rem; }
.eyebrow { font-size:.72rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:var(--pcna); }
.hero { padding:1.2rem 0 .8rem 0; border-bottom:1px solid var(--line); margin-bottom:1.1rem; }
.hero h1 { margin:.15rem 0 .25rem; font-size:2.15rem; letter-spacing:-.03em; color:var(--ink); }
.hero p { margin:0; color:var(--muted); font-size:1rem; }
.card { border:1px solid var(--line); border-radius:14px; padding:1.05rem; min-height:135px; background:#fff; box-shadow:0 5px 18px rgba(18,43,68,.04); }
.card-title { font-size:1rem; font-weight:800; color:var(--ink); margin-bottom:.25rem; }
.card-copy { font-size:.87rem; color:var(--muted); line-height:1.4; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("assets/pcna-logo.webp", width=170)
    st.markdown('<div class="app-name">PCNA Assistant</div>', unsafe_allow_html=True)
    st.write("")
    section = st.radio(
        "Workspace",
        ["Home", "Spec Sample Orders", "Blank Sample Orders", "Quotes", "Virtual Requests", "Perfectly Packaged", "Design Concepts", "Saved Projects"],
        label_visibility="collapsed",
    )
    st.divider()
    st.link_button("Open PCNA.com ↗", "https://www.pcna.com", use_container_width=True)

if section == "Home":
    st.markdown('<div class="hero"><div class="eyebrow">Sales workspace</div><h1>PCNA Assistant</h1><p>Build orders, quotes, virtual requests, packaging concepts and customer-ready project files from one place.</p></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cards = [
        ("Spec Sample Orders", "Create a complete spec sample order with verified product and decoration details."),
        ("Quotes", "Build fast product quotes and keep the approved product configuration attached to the customer project."),
        ("Virtual Requests", "Organize artwork, product details and finished virtuals without losing the customer context."),
        ("Perfectly Packaged", "Create, save and revisit custom Perfectly Packaged concepts and kit components."),
    ]
    for col, (title, copy) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="card"><div class="card-title">{title}</div><div class="card-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("Recent workspace")
    st.info("Your saved customer projects will appear here as we connect project storage.")
else:
    st.markdown(f'<div class="hero"><div class="eyebrow">PCNA Assistant</div><h1>{section}</h1><p>This workspace is now part of the app shell and ready for the live workflow we connect next.</p></div>', unsafe_allow_html=True)

    if section == "Spec Sample Orders":
        left, right = st.columns([1.15, .85])
        with left:
            st.subheader("Start a spec sample order")
            st.text_area("Tell PCNA Assistant what you need", placeholder="Example: Dade Polo, black, medium, embroidery left chest, white imprint; Stanley Quencher 30 oz, polar, laser left of handle.", height=150)
            st.button("Build Spec Order", type="primary", use_container_width=True)
        with right:
            st.subheader("Order defaults")
            st.text_input("Bill To", value="Hart Marketing Fund", disabled=True)
            st.text_input("Customer ID", value="CH1085", disabled=True)
            st.text_input("Ship Method", value="UPS Ground on PCNA Account", disabled=True)
    elif section == "Quotes":
        st.subheader("Quote Builder")
        c1, c2, c3 = st.columns([2,1,1])
        c1.text_input("Product or item number")
        c2.number_input("Quantity", min_value=1, value=100)
        c3.selectbox("Decoration", ["Default decorated", "Blank", "Custom"])
        st.button("Build Quote", type="primary")
    elif section == "Saved Projects":
        st.subheader("Customer Projects")
        st.text_input("Search customers or projects", placeholder="Ford, Truist, Booker...")
        st.caption("Project storage is the next connection point so orders, quotes, artwork and virtuals stay together.")
    else:
        st.subheader(section)
        st.write("The module is scaffolded and ready for the workflow-specific forms and connected data.")

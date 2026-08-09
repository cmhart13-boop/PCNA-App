import json
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="PCNA Assistant", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

PRODUCT_COLUMNS = ["Product Name", "Item Number", "Product Category", "Brand", "Default Item Color", "Product Description"]
DECOR_COLUMNS = ["Item Number", "Decoration Method", "Decoration Location", "Max Length", "Max Height"]

if "projects" not in st.session_state:
    st.session_state.projects = []
if "product_df" not in st.session_state:
    st.session_state.product_df = None
if "decor_df" not in st.session_state:
    st.session_state.decor_df = None

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
.status { border-radius:999px; display:inline-block; padding:.25rem .65rem; font-size:.75rem; font-weight:800; background:#eef6fb; color:#0b4f86; }
.orderbox { white-space:pre-wrap; border:1px solid var(--line); background:#fbfcfd; border-radius:12px; padding:1rem; font-family:ui-monospace, SFMono-Regular, Menlo, monospace; }
</style>
""", unsafe_allow_html=True)


def load_csv(upload, expected):
    if upload is None:
        return None
    df = pd.read_csv(upload, low_memory=False)
    keep = [c for c in expected if c in df.columns]
    return df[keep].copy() if keep else None


def product_matches(query):
    df = st.session_state.product_df
    if df is None or not query.strip():
        return pd.DataFrame()
    q = query.strip().lower()
    name = df.get("Product Name", pd.Series(index=df.index, dtype=str)).fillna("").astype(str).str.lower()
    item = df.get("Item Number", pd.Series(index=df.index, dtype=str)).fillna("").astype(str).str.lower()
    out = df[name.str.contains(q, regex=False) | item.str.contains(q, regex=False)].copy()
    return out.head(30)


def decor_for_item(item_number):
    df = st.session_state.decor_df
    if df is None or not item_number:
        return pd.DataFrame()
    item = df["Item Number"].fillna("").astype(str)
    return df[item.eq(str(item_number))].drop_duplicates().head(100)


def save_project(kind, customer, name, payload):
    st.session_state.projects.insert(0, {
        "type": kind,
        "customer": customer or "Unassigned",
        "project": name or f"{kind} {date.today().isoformat()}",
        "date": date.today().isoformat(),
        "payload": payload,
    })


def product_picker(prefix):
    query = st.text_input("Product name or item number", key=f"{prefix}_query")
    matches = product_matches(query)
    if query and st.session_state.product_df is None:
        st.warning("Load PCNA product data from the sidebar to enable verified lookup.")
    if matches.empty:
        return None
    options = []
    for _, r in matches.iterrows():
        options.append(f"{r.get('Item Number','')} — {r.get('Product Name','')}")
    chosen = st.selectbox("Verified product", options, key=f"{prefix}_choice")
    idx = options.index(chosen)
    return matches.iloc[idx]


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
    with st.expander("PCNA Data"):
        pfile = st.file_uploader("Product Master CSV", type=["csv"], key="product_upload")
        dfile = st.file_uploader("Decoration Master CSV", type=["csv"], key="decor_upload")
        if pfile is not None:
            st.session_state.product_df = load_csv(pfile, PRODUCT_COLUMNS)
        if dfile is not None:
            st.session_state.decor_df = load_csv(dfile, DECOR_COLUMNS)
        if st.session_state.product_df is not None:
            st.success(f"Products loaded: {len(st.session_state.product_df):,}")
        if st.session_state.decor_df is not None:
            st.success(f"Decoration rows loaded: {len(st.session_state.decor_df):,}")
    st.link_button("Open PCNA.com ↗", "https://www.pcna.com", use_container_width=True)

if section == "Home":
    st.markdown('<div class="hero"><div class="eyebrow">Sales workspace</div><h1>PCNA Assistant</h1><p>Build orders, quotes, virtual requests, packaging concepts and customer-ready project files from one place.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Saved projects", len(st.session_state.projects))
    c2.metric("Product data", "Connected" if st.session_state.product_df is not None else "Ready to load")
    c3.metric("Decoration data", "Connected" if st.session_state.decor_df is not None else "Ready to load")
    st.write("")
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
    if st.session_state.projects:
        for p in st.session_state.projects[:5]:
            st.write(f"**{p['customer']} — {p['project']}**  ·  {p['type']}  ·  {p['date']}")
    else:
        st.info("Saved customer projects will appear here.")

elif section == "Spec Sample Orders":
    st.markdown('<div class="hero"><div class="eyebrow">PCNA Assistant</div><h1>Spec Sample Orders</h1><p>Build a clean order from verified product and decoration details.</p></div>', unsafe_allow_html=True)
    customer = st.text_input("Customer / project", placeholder="Ford — Fall Event")
    product = product_picker("spec")
    if product is not None:
        item = str(product.get("Item Number", ""))
        st.caption(f"Verified: {product.get('Product Name','')} · {item} · default color: {product.get('Default Item Color','')}")
        color = st.text_input("Item color", value=str(product.get("Default Item Color", "") or ""))
        size = st.text_input("Size (leave blank if not applicable)")
        dec = decor_for_item(item)
        if not dec.empty:
            labels = (dec["Decoration Method"].fillna("").astype(str) + " — " + dec["Decoration Location"].fillna("").astype(str)).tolist()
            selected = st.selectbox("Decoration", labels)
            drow = dec.iloc[labels.index(selected)]
            method = str(drow.get("Decoration Method", ""))
            location = str(drow.get("Decoration Location", ""))
            max_imprint = f"{drow.get('Max Length','')} x {drow.get('Max Height','')}"
        else:
            method = st.text_input("Decoration method")
            location = st.text_input("Decoration location")
            max_imprint = "Max Imprint"
        imprint = st.text_input("Imprint color", value="N/A" if any(x in method.lower() for x in ["laser", "deboss"]) else "")
        po = st.text_input("PO#")
        ship_date = st.text_input("Ship Date")
        in_hands = st.text_input("In Hands Date")
        ship_to = st.text_area("Ship To")
        if st.button("Build Spec Order", type="primary", use_container_width=True):
            size_line = f"Size: {size}\n" if size.strip() else ""
            order = f"""SPEC SAMPLE ORDER

PO#: {po}
Bill To: Hart Marketing Fund
Customer ID: CH1085
Ship Method: UPS Ground on PCNA Account
Ship Date: {ship_date}
In Hands Date: {in_hands}

ITEM 1
Product: {product.get('Product Name','')}
Item Number: {item}
Item Color: {color}
{size_line}Decoration Method: {method}
Decoration Location: {location}
Imprint Color: {imprint}
Imprint Size: {max_imprint if max_imprint else 'Max Imprint'}

Ship To: {ship_to}"""
            st.session_state.last_spec = order
            save_project("Spec Sample", customer, customer, {"order": order, "item": item})
        if st.session_state.get("last_spec"):
            st.markdown(f'<div class="orderbox">{st.session_state.last_spec}</div>', unsafe_allow_html=True)
            st.download_button("Download order", st.session_state.last_spec, file_name="PCNA_Spec_Sample_Order.txt")

elif section == "Blank Sample Orders":
    st.markdown('<div class="hero"><div class="eyebrow">PCNA Assistant</div><h1>Blank Sample Orders</h1><p>Create a fast blank sample request from verified product data.</p></div>', unsafe_allow_html=True)
    customer = st.text_input("Customer / project", key="blank_customer")
    product = product_picker("blank")
    if product is not None:
        color = st.text_input("Item color", value=str(product.get("Default Item Color", "") or ""), key="blank_color")
        size = st.text_input("Size (if applicable)", key="blank_size")
        ship_to = st.text_area("Ship To", key="blank_ship")
        if st.button("Create Blank Sample Request", type="primary"):
            req = {
                "Product": str(product.get("Product Name", "")),
                "Item Number": str(product.get("Item Number", "")),
                "Color": color,
                "Size": size,
                "Ship To": ship_to,
            }
            st.session_state.blank_request = req
            save_project("Blank Sample", customer, customer, req)
        if st.session_state.get("blank_request"):
            st.json(st.session_state.blank_request)

elif section == "Quotes":
    st.markdown('<div class="hero"><div class="eyebrow">PCNA Assistant</div><h1>Quotes</h1><p>Capture product configuration and quantities without mixing spec-order pricing logic into the workflow.</p></div>', unsafe_allow_html=True)
    customer = st.text_input("Customer / project", key="quote_customer")
    product = product_picker("quote")
    if product is not None:
        q1, q2 = st.columns(2)
        qty = q1.number_input("Quantity", min_value=1, value=100)
        color = q2.text_input("Color", value=str(product.get("Default Item Color", "") or ""))
        size = st.text_input("Size mix / notes")
        dec = decor_for_item(str(product.get("Item Number", "")))
        if not dec.empty:
            labels = (dec["Decoration Method"].fillna("").astype(str) + " — " + dec["Decoration Location"].fillna("").astype(str)).tolist()
            decoration = st.selectbox("Decoration", labels, key="quote_dec")
        else:
            decoration = st.text_input("Decoration")
        unit_price = st.number_input("Unit price (optional)", min_value=0.0, value=0.0, step=0.01)
        if st.button("Save Quote", type="primary"):
            quote = {"Product": str(product.get("Product Name", "")), "Item Number": str(product.get("Item Number", "")), "Quantity": qty, "Color": color, "Size Notes": size, "Decoration": decoration, "Unit Price": unit_price or None}
            st.session_state.quote = quote
            save_project("Quote", customer, customer, quote)
        if st.session_state.get("quote"):
            st.json(st.session_state.quote)

elif section == "Virtual Requests":
    st.markdown('<div class="hero"><div class="eyebrow">PCNA Assistant</div><h1>Virtual Requests</h1><p>Keep artwork, product configuration and instructions attached to the same customer project.</p></div>', unsafe_allow_html=True)
    customer = st.text_input("Customer / project", key="virtual_customer")
    product = product_picker("virtual")
    artwork = st.file_uploader("Artwork", type=["png", "jpg", "jpeg", "pdf", "svg", "eps", "ai"])
    instructions = st.text_area("Virtual instructions", placeholder="Logo centered left chest, white imprint, show on black garment...")
    if st.button("Save Virtual Request", type="primary", disabled=product is None):
        payload = {"Product": str(product.get("Product Name", "")), "Item Number": str(product.get("Item Number", "")), "Artwork": artwork.name if artwork else "", "Instructions": instructions}
        save_project("Virtual Request", customer, customer, payload)
        st.success("Virtual request saved to the customer workspace.")

elif section == "Perfectly Packaged":
    st.markdown('<div class="hero"><div class="eyebrow">PCNA Assistant</div><h1>Perfectly Packaged</h1><p>Build multi-product customer kits and keep the concept together.</p></div>', unsafe_allow_html=True)
    customer = st.text_input("Customer / project", key="kit_customer")
    kit_name = st.text_input("Package name", placeholder="New Hire Welcome Kit")
    items = st.text_area("Products / components", placeholder="Add one product per line with item, color and decoration notes.", height=180)
    concept = st.text_area("Concept / packaging notes", placeholder="Box style, insert, message card, presentation idea...")
    if st.button("Save Package Concept", type="primary"):
        payload = {"Package": kit_name, "Items": [x.strip() for x in items.splitlines() if x.strip()], "Concept": concept}
        save_project("Perfectly Packaged", customer, kit_name, payload)
        st.success("Package concept saved.")

elif section == "Design Concepts":
    st.markdown('<div class="hero"><div class="eyebrow">PCNA Assistant</div><h1>Design Concepts</h1><p>Capture the idea first, then move it into quotes, virtuals or a package.</p></div>', unsafe_allow_html=True)
    customer = st.text_input("Customer / project", key="design_customer")
    objective = st.text_area("What are we trying to create?", placeholder="Executive golf outing gift, $75 target, premium but understated, 150 recipients...")
    ideas = st.text_area("Concepts / AI notes", height=220)
    if st.button("Save Design Concept", type="primary"):
        save_project("Design Concept", customer, customer, {"Objective": objective, "Concepts": ideas})
        st.success("Design concept saved.")

elif section == "Saved Projects":
    st.markdown('<div class="hero"><div class="eyebrow">PCNA Assistant</div><h1>Saved Projects</h1><p>Search the working project memory for specs, quotes, virtuals and kits.</p></div>', unsafe_allow_html=True)
    search = st.text_input("Search customers or projects", placeholder="Ford, Truist, Booker...")
    projects = st.session_state.projects
    if search.strip():
        q = search.lower()
        projects = [p for p in projects if q in p["customer"].lower() or q in p["project"].lower() or q in p["type"].lower()]
    if not projects:
        st.info("No matching projects yet.")
    else:
        for i, p in enumerate(projects):
            with st.expander(f"{p['customer']} — {p['project']} · {p['type']}"):
                st.json(p["payload"])
        export = json.dumps(st.session_state.projects, indent=2)
        st.download_button("Export all projects", export, file_name="pcna_assistant_projects.json", mime="application/json")

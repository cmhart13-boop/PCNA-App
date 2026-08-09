from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from core import (
    SpecItem,
    build_spec_order,
    colors_for_item,
    decorations_for_item,
    imprint_size,
    is_no_ink_decoration,
    prepare_decorations,
    prepare_pricing,
    prepare_products,
    pricing_schedules,
    product_identity,
    quote_tier,
    search_products,
)
from starter_data import verified_starter_data
from storage import (
    delete_project,
    export_projects,
    list_project_files,
    list_projects,
    save_project as persist_project,
    save_upload,
)

st.set_page_config(page_title="PCNA Assistant", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

PCNA_BLUE = "#084f86"
INK = "#15283a"
MUTED = "#6c7a89"
LINE = "#e4ebf1"
PANEL = "#f6f8fa"

st.markdown(
    f"""
<style>
:root {{--pcna:{PCNA_BLUE};--ink:{INK};--muted:{MUTED};--line:{LINE};--panel:{PANEL};}}
[data-testid="stAppViewContainer"] {{background:#fff;}}
[data-testid="stSidebar"] {{background:#f7f9fb;border-right:1px solid var(--line);}}
[data-testid="stSidebar"] > div:first-child {{padding-top:.75rem;}}
.block-container {{padding-top:1.2rem;max-width:1480px;padding-bottom:4rem;}}
#MainMenu, footer {{visibility:hidden;}}
header[data-testid="stHeader"] {{background:transparent;}}
.pcna-kicker {{font-size:.72rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--pcna);}}
.pcna-hero {{padding:.65rem 0 1rem;border-bottom:1px solid var(--line);margin-bottom:1.15rem;}}
.pcna-hero h1 {{margin:.1rem 0 .25rem;font-size:2.25rem;line-height:1.05;letter-spacing:-.035em;color:var(--ink);}}
.pcna-hero p {{margin:0;color:var(--muted);font-size:1rem;}}
.pcna-card {{border:1px solid var(--line);border-radius:16px;padding:1.05rem;background:#fff;box-shadow:0 5px 18px rgba(15,55,85,.045);height:100%;}}
.pcna-card-title {{font-weight:800;color:var(--ink);font-size:1rem;margin-bottom:.25rem;}}
.pcna-card-copy {{color:var(--muted);font-size:.88rem;line-height:1.45;}}
.pcna-badge {{display:inline-block;padding:.25rem .6rem;border-radius:999px;background:#eaf4fb;color:var(--pcna);font-size:.72rem;font-weight:800;}}
.pcna-order {{white-space:pre-wrap;border:1px solid var(--line);background:#fbfcfd;border-radius:12px;padding:1rem;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.88rem;line-height:1.48;}}
div[data-testid="stMetric"] {{border:1px solid var(--line);border-radius:14px;padding:.75rem;background:#fff;}}
.stButton > button[kind="primary"] {{background:var(--pcna);border-color:var(--pcna);}}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def read_csv_bytes(data: bytes, name: str) -> pd.DataFrame:
    import io
    compression = "gzip" if name.lower().endswith(".gz") else "infer"
    return pd.read_csv(io.BytesIO(data), low_memory=False, compression=compression)


def load_bundled_or_starter():
    data_dir = Path("data")
    p = data_dir / "PCNA_Product_Master_CLEAN.csv.gz"
    d = data_dir / "PCNA Decoration Master.csv.gz"
    r = data_dir / "PCNA Product Pricing Master 8.03.csv.gz"
    if p.exists() and d.exists() and r.exists():
        return (
            prepare_products(pd.read_csv(p, low_memory=False, compression="gzip")),
            prepare_decorations(pd.read_csv(d, low_memory=False, compression="gzip")),
            prepare_pricing(pd.read_csv(r, low_memory=False, compression="gzip")),
            "Full PCNA masters",
        )
    products, decorations, pricing = verified_starter_data()
    return prepare_products(products), prepare_decorations(decorations), prepare_pricing(pricing), "Verified starter catalog"


if "products" not in st.session_state:
    p, d, r, source = load_bundled_or_starter()
    st.session_state.products = p
    st.session_state.decorations = d
    st.session_state.pricing = r
    st.session_state.data_source = source
if "spec_item_count" not in st.session_state:
    st.session_state.spec_item_count = 1
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def hero(kicker: str, title: str, copy: str):
    st.markdown(
        f'<div class="pcna-hero"><div class="pcna-kicker">{kicker}</div><h1>{title}</h1><p>{copy}</p></div>',
        unsafe_allow_html=True,
    )


def save_project(kind: str, customer: str, project: str, payload: dict) -> int:
    return persist_project(kind, customer, project, payload)


def product_picker(prefix: str):
    query = st.text_input("Product name or item number", key=f"{prefix}_query", placeholder="Dade Polo, Stanley 30oz, TM16398...")
    matches = search_products(st.session_state.products, query)
    if not query:
        return None
    if matches.empty:
        st.warning("No verified match in the currently loaded PCNA dataset. Load the full masters in Data Sources or verify on PCNA.com.")
        return None
    unique = matches.drop_duplicates(subset=["Item Number", "Product Name"]).reset_index(drop=True)
    labels = [f"{r['Item Number']} — {r['Product Name']}" for _, r in unique.iterrows()]
    selected = st.selectbox("Verified product", labels, key=f"{prefix}_product")
    row = unique.iloc[labels.index(selected)]
    return product_identity(st.session_state.products, row["Item Number"])


def product_configuration(prefix: str):
    identity = product_picker(prefix)
    if not identity:
        return None
    item = identity["Item Number"]
    colors = colors_for_item(st.session_state.products, item)
    c1, c2 = st.columns([1.3, 1])
    with c1:
        color = st.selectbox("Verified color", colors if colors else [""], key=f"{prefix}_color")
    with c2:
        size = st.text_input("Size (if applicable)", key=f"{prefix}_size", placeholder="Medium")
    dec = decorations_for_item(st.session_state.decorations, item)
    if dec.empty:
        st.warning("Decoration data is not available for this item in the current dataset.")
        method = st.text_input("Decoration Method", key=f"{prefix}_method")
        location = st.text_input("Decoration Location", key=f"{prefix}_location")
        max_size = "Max Imprint"
    else:
        labels = [f"{r['Decoration Method']} — {r['Decoration Location']}" for _, r in dec.iterrows()]
        selected = st.selectbox("Verified decoration", labels, key=f"{prefix}_decoration")
        drow = dec.iloc[labels.index(selected)]
        method = str(drow["Decoration Method"])
        location = str(drow["Decoration Location"])
        max_size = imprint_size(drow)
        st.caption(f"Maximum imprint from Decoration Master: {max_size}")
    imprint_default = "N/A" if is_no_ink_decoration(method) else ""
    imprint_color = st.text_input("Imprint Color", value=imprint_default, key=f"{prefix}_imprint")
    return {
        **identity,
        "Color": color,
        "Size": size,
        "Decoration Method": method,
        "Decoration Location": location,
        "Imprint Color": imprint_color,
        "Imprint Size": max_size,
    }


def data_status_card():
    source = st.session_state.data_source
    st.markdown(f'<span class="pcna-badge">{source}</span>', unsafe_allow_html=True)
    st.caption(
        f"{len(st.session_state.products):,} product/color rows · "
        f"{len(st.session_state.decorations):,} decoration rows · "
        f"{len(st.session_state.pricing):,} pricing rows"
    )


with st.sidebar:
    if Path("assets/pcna-logo.webp").exists():
        st.image("assets/pcna-logo.webp", width=180)
    else:
        st.markdown(f'<div style="font-size:2rem;font-weight:900;color:{PCNA_BLUE}">PCNA</div>', unsafe_allow_html=True)
    st.markdown("**PCNA Assistant**")
    st.caption("AI-enabled sales workspace")
    st.write("")
    section = st.radio(
        "Workspace",
        [
            "Home",
            "PCNA Assistant",
            "Product Search",
            "Spec Sample Orders",
            "Blank Sample Orders",
            "Quotes",
            "Virtual Requests",
            "Perfectly Packaged",
            "Design Concepts",
            "Saved Projects",
            "Data Sources",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    data_status_card()
    st.link_button("Open PCNA.com ↗", "https://www.pcna.com", use_container_width=True)


if section == "Home":
    projects = list_projects()
    hero("PCNA Sales Workspace", "PCNA Assistant", "One place for product lookup, spec samples, quotes, virtual requests, packaging concepts and customer project history.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Products", f"{st.session_state.products['Item Number'].nunique():,}")
    m2.metric("Decoration rows", f"{len(st.session_state.decorations):,}")
    m3.metric("Pricing rows", f"{len(st.session_state.pricing):,}")
    m4.metric("Saved projects", len(projects))
    st.write("")
    cols = st.columns(4)
    cards = [
        ("Spec Samples", "Build the PCNA spec format from verified item, color and decoration data."),
        ("Quotes", "Uses decorated pricing by default and applies the correct quantity tier."),
        ("Virtual Requests", "Keep customer, item, artwork and decoration direction together."),
        ("Perfectly Packaged", "Save kit components, reference files and creative direction by customer."),
    ]
    for col, (title, copy) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="pcna-card"><div class="pcna-card-title">{title}</div><div class="pcna-card-copy">{copy}</div></div>', unsafe_allow_html=True)
    st.write("")
    st.subheader("Recent projects")
    if not projects:
        st.info("Saved work will appear here and remain available after a browser refresh.")
    else:
        for p in projects[:6]:
            st.write(f"**{p['customer']} — {p['project']}** · {p['type']} · {p['date'][:10]}")


elif section == "PCNA Assistant":
    hero("AI Workspace", "Ask PCNA Assistant", "Use natural language for product and workflow help. Verified PCNA data remains the source of truth.")
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        secret_key = ""
    api_key = secret_key or st.text_input("OpenAI API key", type="password", help="Optional. Store as OPENAI_API_KEY in Streamlit secrets for deployment.")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ask about a product, quote workflow, spec sample, virtual request...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        matches = search_products(st.session_state.products, prompt, limit=8)
        context_rows = matches[["Product Name", "Item Number", "Brand", "Default Item Color"]].to_dict("records") if not matches.empty else []
        if not api_key:
            reply = "I can search and build verified PCNA workflows in the modules on the left. Add an OpenAI API key here to enable conversational AI. I will not invent a product, item number, color, decoration method, location, or price."
        else:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                instructions = (
                    "You are PCNA Assistant for a PCNA sales professional. Never invent PCNA product names, item numbers, colors, decoration methods, locations, or pricing. "
                    "Use only the verified context supplied with the question for factual PCNA product claims. If context is insufficient, say the product must be verified in Product Search or PCNA.com. "
                    "For pricing, always prefer decorated pricing when the user asks for a standard quote unless they explicitly request blank pricing. Keep answers concise and operational."
                )
                response = client.responses.create(
                    model="gpt-5",
                    instructions=instructions,
                    input=f"USER REQUEST:\n{prompt}\n\nVERIFIED LOCAL PCNA MATCHES:\n{json.dumps(context_rows, ensure_ascii=False)}",
                )
                reply = response.output_text
            except Exception as exc:
                reply = f"AI request could not be completed: {exc}. The deterministic PCNA search/order tools remain available."
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)


elif section == "Product Search":
    hero("Verified Catalog", "Product Search", "Search by PCNA product name, brand or item number and inspect current loaded colors and decoration options.")
    identity = product_picker("search")
    if identity:
        item = identity["Item Number"]
        st.subheader(identity["Product Name"])
        st.caption(f"Item {item} · {identity.get('Brand','') or 'PCNA'}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Verified colors**")
            for color in colors_for_item(st.session_state.products, item):
                st.write(f"• {color}")
        with c2:
            st.markdown("**Verified decoration methods / locations**")
            d = decorations_for_item(st.session_state.decorations, item)
            if d.empty:
                st.caption("No decoration data in current dataset.")
            else:
                st.dataframe(d[["Decoration Method", "Decoration Location", "Max Length", "Max Height"]], hide_index=True, use_container_width=True)


elif section == "Spec Sample Orders":
    hero("Orders", "Spec Sample Orders", "Build the exact PCNA spec sample format from verified product, color and decoration data.")
    h1, h2 = st.columns(2)
    po = h1.text_input("PO#")
    customer = h2.text_input("Customer / Project", placeholder="Ford — Fall Event")
    s1, s2 = st.columns(2)
    ship_date = s1.text_input("Ship Date")
    in_hands = s2.text_input("In Hands Date")
    ship_to = st.text_area("Ship To")
    st.divider()
    configured = []
    for i in range(st.session_state.spec_item_count):
        st.subheader(f"Item {i + 1}")
        cfg = product_configuration(f"spec_{i}")
        if cfg:
            configured.append(cfg)
        if i < st.session_state.spec_item_count - 1:
            st.divider()
    b1, b2, _ = st.columns([1, 1, 2])
    if b1.button("+ Add Item", use_container_width=True, disabled=st.session_state.spec_item_count >= 8):
        st.session_state.spec_item_count += 1
        st.rerun()
    if b2.button("Remove Last", use_container_width=True, disabled=st.session_state.spec_item_count <= 1):
        st.session_state.spec_item_count -= 1
        st.rerun()
    if st.button("Build Spec Sample Order", type="primary", use_container_width=True, disabled=len(configured) != st.session_state.spec_item_count):
        items = [
            SpecItem(
                product=cfg["Product Name"], item_number=cfg["Item Number"], color=cfg["Color"], size=cfg["Size"],
                decoration_method=cfg["Decoration Method"], decoration_location=cfg["Decoration Location"],
                imprint_color="N/A" if is_no_ink_decoration(cfg["Decoration Method"]) else cfg["Imprint Color"], imprint_size="Max Imprint"
            )
            for cfg in configured
        ]
        order = build_spec_order(items, po=po, ship_date=ship_date, in_hands_date=in_hands, ship_to=ship_to)
        st.session_state.last_spec = order
        save_project("Spec Sample Order", customer, customer, {"order": order})
    if st.session_state.get("last_spec"):
        st.write("")
        st.markdown(f'<div class="pcna-order">{st.session_state.last_spec}</div>', unsafe_allow_html=True)
        st.download_button("Download order", st.session_state.last_spec, file_name="PCNA_Spec_Sample_Order.txt", use_container_width=True)


elif section == "Blank Sample Orders":
    hero("Orders", "Blank Sample Orders", "Create a clean blank sample request using a verified PCNA item and color.")
    customer = st.text_input("Customer / Project", key="blank_customer")
    identity = product_picker("blank")
    if identity:
        item = identity["Item Number"]
        colors = colors_for_item(st.session_state.products, item)
        color = st.selectbox("Verified Color", colors if colors else [""], key="blank_color")
        size = st.text_input("Size (if applicable)", key="blank_size")
        ship_to = st.text_area("Ship To", key="blank_ship")
        if st.button("Save Blank Sample Request", type="primary", use_container_width=True):
            req = {"Product": identity["Product Name"], "Item Number": item, "Color": color, "Size": size, "Ship To": ship_to}
            st.session_state.last_blank = req
            save_project("Blank Sample", customer, customer, req)
        if st.session_state.get("last_blank"):
            st.json(st.session_state.last_blank)


elif section == "Quotes":
    hero("Pricing", "Quotes", "Standard quote lookup defaults to the verified USD list decorated schedule — never blank pricing unless you explicitly choose it.")
    customer = st.text_input("Customer / Project", key="quote_customer")
    identity = product_picker("quote")
    if identity:
        item = identity["Item Number"]
        q1, q2 = st.columns(2)
        qty = int(q1.number_input("Quantity", min_value=1, value=100, step=1))
        colors = colors_for_item(st.session_state.products, item)
        color = q2.selectbox("Verified Color", colors if colors else [""], key="quote_color")
        schedules = pricing_schedules(st.session_state.pricing, item, currency="USD", decorated=True)
        if not schedules:
            st.warning("No USD decorated pricing is available for this item in the currently loaded pricing dataset.")
        else:
            schedule = st.selectbox("Pricing schedule", schedules, index=0, help="Decorated schedules only. List decorated is prioritized by default.")
            tier = quote_tier(st.session_state.pricing, item, qty, currency="USD", decorated=True, schedule=schedule)
            if tier:
                c1, c2, c3 = st.columns(3)
                c1.metric("Unit price", f"${tier['Unit Price']:,.2f}")
                c2.metric("Quantity tier", f"{tier['MOQ Tier']:,}")
                c3.metric("Extended", f"${tier['Unit Price'] * qty:,.2f}")
                if tier["Below MOQ"]:
                    st.warning(f"Requested quantity is below the first decorated tier ({tier['MOQ Tier']}).")
                st.caption(f"Source schedule: {tier['Schedule']} · {tier['Price Description']}")
                if st.button("Save Quote", type="primary", use_container_width=True):
                    payload = {**identity, "Quantity": qty, "Color": color, **tier}
                    save_project("Quote", customer, customer, payload)
                    st.success("Quote saved to the persistent project workspace.")


elif section == "Virtual Requests":
    hero("Creative", "Virtual Requests", "Keep verified product details, artwork and decoration direction together for a clean virtual request.")
    customer = st.text_input("Customer / Project", key="virtual_customer")
    cfg = product_configuration("virtual")
    artwork = st.file_uploader("Artwork", type=["png", "jpg", "jpeg", "pdf", "svg", "eps", "ai"])
    instructions = st.text_area("Creative Instructions", placeholder="Logo centered left chest, white imprint, show on black garment...")
    if st.button("Save Virtual Request", type="primary", use_container_width=True, disabled=cfg is None):
        payload = {**cfg, "Artwork": artwork.name if artwork else "", "Instructions": instructions}
        project_id = save_project("Virtual Request", customer, customer, payload)
        if artwork:
            save_upload(project_id, artwork.name, artwork.getvalue())
        st.success("Virtual request and artwork saved.")


elif section == "Perfectly Packaged":
    hero("Kitting", "Perfectly Packaged", "Build and save multi-product kit concepts without losing product or customer context.")
    customer = st.text_input("Customer", key="package_customer")
    package_name = st.text_input("Package / Concept Name", placeholder="Ford Dealer Welcome Kit")
    st.info("Use Product Search to verify each component before finalizing the kit. Reference art and finished virtuals can be stored with the project.")
    items = st.text_area("Verified Kit Components", height=180, placeholder="TM16398 — Men's DADE Short Sleeve Polo — Black — Embroidery Left Chest\n1603-02 — Stanley Quencher 30oz — Frost — Laser Handle Left")
    concept = st.text_area("Packaging / Design Direction", height=160, placeholder="Describe box concept, brand story, inside-lid art, card copy and arrangement...")
    refs = st.file_uploader("Reference files / artwork", accept_multiple_files=True, type=["png", "jpg", "jpeg", "pdf", "svg"])
    if st.button("Save Perfectly Packaged Project", type="primary", use_container_width=True):
        payload = {"Components": [x.strip() for x in items.splitlines() if x.strip()], "Concept": concept, "Files": [f.name for f in refs]}
        project_id = save_project("Perfectly Packaged", customer, package_name, payload)
        for file in refs:
            save_upload(project_id, file.name, file.getvalue())
        st.success("Perfectly Packaged project and files saved.")


elif section == "Design Concepts":
    hero("Creative", "Design Concepts", "Store customer-specific creative direction, campaign concepts and reference files in one workspace.")
    customer = st.text_input("Customer", key="concept_customer")
    concept_name = st.text_input("Concept Name")
    brief = st.text_area("Creative Brief", height=220)
    files = st.file_uploader("Reference files", accept_multiple_files=True, type=["png", "jpg", "jpeg", "pdf", "svg"])
    if st.button("Save Design Concept", type="primary", use_container_width=True):
        project_id = save_project("Design Concept", customer, concept_name, {"Brief": brief, "Files": [f.name for f in files]})
        for file in files:
            save_upload(project_id, file.name, file.getvalue())
        st.success("Design concept and files saved.")


elif section == "Saved Projects":
    hero("Workspace", "Saved Projects", "Reopen saved specs, quotes, virtual requests, packaging concepts and their uploaded files.")
    projects = list_projects()
    if not projects:
        st.info("No projects saved yet.")
    else:
        for project in projects:
            with st.expander(f"{project['customer']} — {project['project']} · {project['type']}"):
                st.caption(f"Saved {project['date']}")
                st.json(project["payload"])
                project_files = list_project_files(project["id"])
                if project_files:
                    st.markdown("**Files**")
                    for file_path in project_files:
                        st.download_button(
                            f"Download {file_path.name}",
                            data=file_path.read_bytes(),
                            file_name=file_path.name,
                            key=f"file_{project['id']}_{file_path.name}",
                        )
                if st.button("Delete Project", key=f"delete_{project['id']}"):
                    delete_project(project["id"])
                    st.rerun()
        st.download_button("Export All Projects", export_projects(), file_name="PCNA_Assistant_Projects.json", mime="application/json", use_container_width=True)


elif section == "Data Sources":
    hero("Administration", "PCNA Data Sources", "Load full PCNA master files for broad production use. The app validates required columns before replacing verified starter data.")
    st.markdown("**Current data**")
    data_status_card()
    st.write("")
    pfile = st.file_uploader("PCNA_Product_Master_CLEAN.csv", type=["csv", "gz"], key="product_master")
    dfile = st.file_uploader("PCNA Decoration Master.csv", type=["csv", "gz"], key="decoration_master")
    rfile = st.file_uploader("PCNA Product Pricing Master 8.03.csv", type=["csv", "gz"], key="pricing_master")
    if st.button("Validate & Load Full Masters", type="primary", use_container_width=True):
        if not (pfile and dfile and rfile):
            st.error("Load all three master files before replacing the active dataset.")
        else:
            try:
                products = prepare_products(read_csv_bytes(pfile.getvalue(), pfile.name))
                decorations = prepare_decorations(read_csv_bytes(dfile.getvalue(), dfile.name))
                pricing = prepare_pricing(read_csv_bytes(rfile.getvalue(), rfile.name))
                st.session_state.products = products
                st.session_state.decorations = decorations
                st.session_state.pricing = pricing
                st.session_state.data_source = "Full PCNA masters — session loaded"
                st.success(f"Loaded {len(products):,} product/color rows, {len(decorations):,} decoration rows and {len(pricing):,} pricing rows.")
            except Exception as exc:
                st.error(f"Data validation failed: {exc}")
    st.divider()
    st.caption("Source precedence for production: live PCNA/PromoStandards data should override CSV conflicts when the API bridge is configured. The app never silently invents missing data.")

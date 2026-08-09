from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

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

st.set_page_config(page_title="PCNA", layout="centered", initial_sidebar_state="collapsed")

PCNA_BLUE = "#084f86"
INK = "#14273a"
MUTED = "#66798a"
LINE = "#e2e9ef"
PANEL = "#f5f8fa"
GREEN = "#16794a"

st.markdown(
    f"""
<style>
:root{{--pcna:{PCNA_BLUE};--ink:{INK};--muted:{MUTED};--line:{LINE};--panel:{PANEL};--green:{GREEN};}}
html,body,[data-testid="stAppViewContainer"]{{background:#fff;color:var(--ink);}}
[data-testid="stAppViewContainer"]>.main{{overflow-x:hidden;}}
[data-testid="stHeader"]{{background:rgba(255,255,255,.94);backdrop-filter:blur(12px);height:0;}}
[data-testid="stSidebar"]{{display:none;}}
#MainMenu,footer,[data-testid="stToolbar"]{{visibility:hidden!important;height:0!important;}}
.block-container{{max-width:620px!important;padding:12px 15px 104px!important;margin:0 auto!important;}}

.page-kicker{{font-size:11px;font-weight:900;letter-spacing:.10em;color:var(--pcna);text-transform:uppercase;margin-top:2px;}}
.page-title{{font-size:29px;line-height:1.04;font-weight:850;letter-spacing:-.035em;color:var(--ink);margin:4px 0 7px;}}
.page-copy{{font-size:15px;line-height:1.45;color:var(--muted);margin:0 0 18px;}}
.section-title{{font-size:18px;font-weight:850;letter-spacing:-.015em;margin:20px 0 9px;color:var(--ink);}}

.promo-shell{{overflow:hidden;border-radius:22px;margin:0 0 14px;box-shadow:0 10px 30px rgba(15,55,85,.12);}}
.promo-track{{display:flex;width:max-content;animation:pcnaMarquee 24s linear infinite;}}
.promo-shell:hover .promo-track{{animation-play-state:paused;}}
.promo-slide{{width:min(590px,calc(100vw - 30px));height:202px;flex:0 0 auto;position:relative;overflow:hidden;text-decoration:none!important;color:#fff!important;display:block;}}
.promo-slide:after{{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,28,48,.80),rgba(6,28,48,.22) 58%,rgba(6,28,48,.06));}}
.promo-a{{background:linear-gradient(135deg,#005c95 0%,#00a7c8 52%,#9ae8ef 100%);}}
.promo-b{{background:linear-gradient(135deg,#231f5f 0%,#6558d3 48%,#ff7f9c 100%);}}
.promo-c{{background:linear-gradient(135deg,#0f5c45 0%,#2aa876 50%,#bce784 100%);}}
.promo-art{{position:absolute;right:10px;top:8px;width:46%;height:92%;opacity:.95;z-index:1;}}
.promo-copy{{position:absolute;left:20px;top:24px;z-index:2;width:56%;}}
.promo-eyebrow{{font-size:11px;font-weight:900;letter-spacing:.12em;text-transform:uppercase;opacity:.86;}}
.promo-title{{font-size:25px;font-weight:900;line-height:1.04;letter-spacing:-.035em;margin:8px 0 7px;}}
.promo-text{{font-size:13px;line-height:1.35;max-width:245px;opacity:.92;}}
.promo-cta{{display:inline-flex;margin-top:14px;padding:8px 11px;border-radius:999px;background:rgba(255,255,255,.94);color:#12334c;font-size:11px;font-weight:900;}}
@keyframes pcnaMarquee{{0%{{transform:translateX(0)}}100%{{transform:translateX(-50%)}}}}

.explore-row{{display:flex;gap:10px;overflow-x:auto;padding:1px 1px 6px;scrollbar-width:none;-webkit-overflow-scrolling:touch;}}
.explore-row::-webkit-scrollbar{{display:none;}}
.explore-card{{min-width:145px;border-radius:17px;padding:14px;text-decoration:none!important;color:#fff!important;box-shadow:0 5px 18px rgba(20,55,80,.10);}}
.explore-card:nth-child(1){{background:linear-gradient(145deg,#0b6fa4,#22b8cf);}}
.explore-card:nth-child(2){{background:linear-gradient(145deg,#8146a5,#c562b0);}}
.explore-card:nth-child(3){{background:linear-gradient(145deg,#d45f27,#f0a344);}}
.explore-card:nth-child(4){{background:linear-gradient(145deg,#23845d,#70b878);}}
.explore-icon{{font-size:27px;line-height:1;margin-bottom:20px;}}
.explore-title{{font-size:14px;font-weight:900;}}
.explore-copy{{font-size:10px;opacity:.84;margin-top:3px;}}

.action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:4px 0 6px;}}
.action-card{{display:block;text-decoration:none!important;border:1px solid var(--line);border-radius:17px;padding:16px 14px;background:#fff;min-height:118px;box-shadow:0 5px 17px rgba(20,55,80,.055);transition:transform .12s ease,box-shadow .12s ease;}}
.action-card:active{{transform:scale(.985);}}
.action-icon{{font-size:24px;line-height:1;margin-bottom:14px;}}
.action-title{{font-size:15px;font-weight:850;color:var(--ink);line-height:1.15;margin-bottom:5px;}}
.action-copy{{font-size:12px;color:var(--muted);line-height:1.35;}}
.wide-card{{grid-column:1/-1;min-height:auto;display:flex;align-items:center;gap:12px;padding:14px 15px;}}
.wide-card .action-icon{{margin:0;font-size:22px;}}
.wide-card .action-title{{margin:0 0 2px;}}

.info-card{{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:8px 0;box-shadow:0 4px 15px rgba(20,55,80,.04);}}
.info-card-title{{font-size:15px;font-weight:850;color:var(--ink);}}
.info-card-meta{{font-size:12px;color:var(--muted);margin-top:3px;}}
.data-chip{{display:inline-block;padding:5px 8px;border-radius:999px;background:#eef5fa;color:var(--pcna);font-size:11px;font-weight:850;margin-right:5px;}}
.order-box{{white-space:pre-wrap;border:1px solid var(--line);background:#fbfcfd;border-radius:15px;padding:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;line-height:1.5;overflow-wrap:anywhere;}}

.stButton>button,.stDownloadButton>button,[data-testid="stLinkButton"] a{{min-height:48px!important;border-radius:13px!important;font-weight:800!important;font-size:15px!important;width:100%!important;}}
.stTextInput input,.stNumberInput input,.stTextArea textarea,[data-baseweb="select"]>div{{min-height:48px!important;border-radius:12px!important;font-size:16px!important;}}
.stTextArea textarea{{min-height:112px!important;}}
[data-testid="stFileUploaderDropzone"]{{border-radius:14px!important;padding:14px 10px!important;}}
[data-testid="stExpander"]{{border:1px solid var(--line)!important;border-radius:14px!important;overflow:hidden;margin:8px 0;}}
[data-testid="stMetric"]{{border:1px solid var(--line);border-radius:14px;padding:12px;background:#fff;}}
hr{{margin:16px 0!important;border-color:var(--line)!important;}}
label,[data-testid="stWidgetLabel"]{{font-weight:750!important;color:var(--ink)!important;}}

.bottom-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:0;width:min(620px,100%);height:76px;background:rgba(255,255,255,.94);backdrop-filter:blur(18px);border-top:1px solid var(--line);display:grid;grid-template-columns:repeat(4,1fr);z-index:9999;padding:7px 7px max(7px,env(safe-area-inset-bottom));box-sizing:border-box;}}
.nav-item{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;color:#7890a0!important;font-size:10px;font-weight:800;gap:3px;border-radius:12px;}}
.nav-icon{{font-size:20px;line-height:1;}}
.nav-item.active{{color:var(--pcna)!important;background:#eff6fb;}}

@media(max-width:430px){{
 .block-container{{padding-left:12px!important;padding-right:12px!important;}}
 .page-title{{font-size:27px;}}
 .action-grid{{gap:9px;}}
 .action-card{{padding:15px 12px;min-height:112px;}}
 .promo-slide{{width:calc(100vw - 24px);height:188px;}}
 .promo-title{{font-size:23px;}}
 .promo-copy{{left:17px;top:21px;}}
}}
@media(max-width:350px){{.action-grid{{grid-template-columns:1fr;}}.wide-card{{grid-column:auto;}}}}
@media(prefers-reduced-motion:reduce){{.promo-track{{animation:none;overflow-x:auto;}}}}
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

def current_page() -> str:
    page = st.query_params.get("page", "home")
    return page if isinstance(page, str) else "home"

def nav_link(page: str) -> str:
    return f"?page={quote(page)}"

def page_header(kicker: str, title: str, copy: str):
    st.markdown(
        f'<div class="page-kicker">{kicker}</div><div class="page-title">{title}</div><div class="page-copy">{copy}</div>',
        unsafe_allow_html=True,
    )

def promo_strip():
    home = "https://www.pcna.com/en-us"
    packaged = "https://www.pcna.com/en-us/tools-services/perfectly-packaged"
    slides = f"""
<a class="promo-slide promo-a" href="{home}" target="_blank" rel="noopener">
  <div class="promo-copy"><div class="promo-eyebrow">Explore PCNA</div><div class="promo-title">Fresh ideas.<br>Ready to brand.</div><div class="promo-text">Jump from the app into PCNA.com for products, brands and inspiration.</div><span class="promo-cta">Open PCNA.com →</span></div>
  <svg class="promo-art" viewBox="0 0 240 190" aria-hidden="true"><circle cx="148" cy="86" r="70" fill="rgba(255,255,255,.16)"/><path d="M115 31h48v18l9 13v93c0 10-8 18-18 18h-30c-10 0-18-8-18-18V62l9-13z" fill="rgba(255,255,255,.92)"/><rect x="116" y="20" width="46" height="18" rx="7" fill="rgba(255,255,255,.74)"/><path d="M117 104h43" stroke="#0d7fa5" stroke-width="8" stroke-linecap="round"/></svg>
</a>
<a class="promo-slide promo-b" href="{packaged}" target="_blank" rel="noopener">
  <div class="promo-copy"><div class="promo-eyebrow">Perfectly Packaged</div><div class="promo-title">Make the unboxing<br>part of the idea.</div><div class="promo-text">Explore PCNA packaging and kitting options without leaving your workflow.</div><span class="promo-cta">Explore packaging →</span></div>
  <svg class="promo-art" viewBox="0 0 240 190" aria-hidden="true"><path d="M58 72l62-38 67 35-64 39z" fill="rgba(255,255,255,.93)"/><path d="M58 72v65l65 38v-67z" fill="rgba(255,255,255,.70)"/><path d="M123 108v67l64-39V69z" fill="rgba(255,255,255,.84)"/><path d="M90 54l66 35" stroke="#8b5ec7" stroke-width="8" stroke-linecap="round"/></svg>
</a>
<a class="promo-slide promo-c" href="{home}" target="_blank" rel="noopener">
  <div class="promo-copy"><div class="promo-eyebrow">Shop the assortment</div><div class="promo-title">Drinkware. Bags.<br>Apparel. More.</div><div class="promo-text">Use the app for the work, then tap through to PCNA.com when you want to browse.</div><span class="promo-cta">Browse PCNA →</span></div>
  <svg class="promo-art" viewBox="0 0 240 190" aria-hidden="true"><path d="M70 61h86l14 98H55z" fill="rgba(255,255,255,.90)"/><path d="M87 65c0-31 53-31 53 0" fill="none" stroke="rgba(255,255,255,.85)" stroke-width="10" stroke-linecap="round"/><circle cx="174" cy="58" r="35" fill="rgba(255,255,255,.18)"/></svg>
</a>
"""
    st.markdown(f'<div class="promo-shell"><div class="promo-track">{slides}{slides}</div></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="explore-row">
<a class="explore-card" href="{home}" target="_blank" rel="noopener"><div class="explore-icon">◒</div><div class="explore-title">Drinkware</div><div class="explore-copy">Browse on PCNA.com</div></a>
<a class="explore-card" href="{home}" target="_blank" rel="noopener"><div class="explore-icon">◇</div><div class="explore-title">Apparel</div><div class="explore-copy">Brands + styles</div></a>
<a class="explore-card" href="{home}" target="_blank" rel="noopener"><div class="explore-icon">▰</div><div class="explore-title">Bags</div><div class="explore-copy">Totes + travel</div></a>
<a class="explore-card" href="{packaged}" target="_blank" rel="noopener"><div class="explore-icon">▱</div><div class="explore-title">Packaging</div><div class="explore-copy">Perfectly Packaged</div></a>
</div>
""",
        unsafe_allow_html=True,
    )

def bottom_nav(page: str):
    group = "create" if page in {"spec", "blank", "quote", "virtual", "package", "concept"} else page
    st.markdown(
        f"""
<div class="bottom-nav">
<a class="nav-item {'active' if group=='home' else ''}" href="{nav_link('home')}"><span class="nav-icon">⌂</span><span>Home</span></a>
<a class="nav-item {'active' if group=='search' else ''}" href="{nav_link('search')}"><span class="nav-icon">⌕</span><span>Products</span></a>
<a class="nav-item {'active' if group=='create' else ''}" href="{nav_link('create')}"><span class="nav-icon">＋</span><span>Create</span></a>
<a class="nav-item {'active' if group=='saved' else ''}" href="{nav_link('saved')}"><span class="nav-icon">▣</span><span>Saved</span></a>
</div>
""",
        unsafe_allow_html=True,
    )

def persistent_projects():
    return list_projects()

def save_project(kind: str, customer: str, project: str, payload: dict, uploads=None) -> int:
    project_id = persist_project(kind, customer, project, payload)
    for upload in uploads or []:
        if upload is not None:
            save_upload(project_id, upload.name, upload.getvalue())
    return project_id

def product_picker(prefix: str):
    query = st.text_input("Product name or item number", key=f"{prefix}_query", placeholder="Try Dade Polo, Stanley 30 oz, 1603-02...")
    if not query:
        return None
    matches = search_products(st.session_state.products, query, limit=30)
    if matches.empty:
        st.warning("No verified match in the active PCNA dataset. Try another spelling or verify on PCNA.com.")
        return None
    unique = matches.drop_duplicates(subset=["Item Number", "Product Name"]).reset_index(drop=True)
    labels = [f"{r['Product Name']} · {r['Item Number']}" for _, r in unique.iterrows()]
    chosen = st.selectbox("Verified match", labels, key=f"{prefix}_product")
    row = unique.iloc[labels.index(chosen)]
    return product_identity(st.session_state.products, row["Item Number"])

def product_configuration(prefix: str):
    identity = product_picker(prefix)
    if not identity:
        return None
    item = identity["Item Number"]
    st.markdown(f'<div class="info-card"><div class="info-card-title">{identity["Product Name"]}</div><div class="info-card-meta">Item {item}</div></div>', unsafe_allow_html=True)
    color = st.selectbox("Color", colors_for_item(st.session_state.products, item) or [""], key=f"{prefix}_color")
    size = st.text_input("Size (if applicable)", key=f"{prefix}_size", placeholder="Medium")
    dec = decorations_for_item(st.session_state.decorations, item)
    if dec.empty:
        st.warning("No decoration data is available for this item in the active dataset.")
        method = st.text_input("Decoration Method", key=f"{prefix}_method")
        location = st.text_input("Decoration Location", key=f"{prefix}_location")
    else:
        labels = [f"{r['Decoration Method']} · {r['Decoration Location']}" for _, r in dec.iterrows()]
        selected = st.selectbox("Decoration", labels, key=f"{prefix}_decoration")
        drow = dec.iloc[labels.index(selected)]
        method = str(drow["Decoration Method"])
        location = str(drow["Decoration Location"])
        st.caption(f"Verified max imprint: {imprint_size(drow)}")
    imprint_default = "N/A" if is_no_ink_decoration(method) else ""
    imprint_color = st.text_input("Imprint Color", value=imprint_default, key=f"{prefix}_imprint")
    return {**identity, "Color": color, "Size": size, "Decoration Method": method, "Decoration Location": location, "Imprint Color": imprint_color}

page = current_page()

if page == "home":
    promo_strip()
    projects = persistent_projects()
    st.markdown(f'<span class="data-chip">{st.session_state.data_source}</span><span class="data-chip">{len(projects)} saved</span>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Quick actions</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('search')}"><div class="action-icon">⌕</div><div class="action-title">Find a Product</div><div class="action-copy">Search names, item numbers, colors and decoration.</div></a>
<a class="action-card" href="{nav_link('spec')}"><div class="action-icon">✓</div><div class="action-title">Spec Sample</div><div class="action-copy">Build a verified sample order in the PCNA format.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-icon">$</div><div class="action-title">Quick Quote</div><div class="action-copy">Decorated pricing first, with correct quantity tiers.</div></a>
<a class="action-card" href="{nav_link('virtual')}"><div class="action-icon">◇</div><div class="action-title">Virtual Request</div><div class="action-copy">Attach art and keep product direction together.</div></a>
<a class="action-card wide-card" href="{nav_link('assistant')}"><div class="action-icon">✦</div><div><div class="action-title">Ask PCNA Assistant</div><div class="action-copy">Use natural language with verified PCNA context.</div></div></a>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">More workflows</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('blank')}"><div class="action-icon">□</div><div class="action-title">Blank Sample</div><div class="action-copy">Create a fast blank sample request.</div></a>
<a class="action-card" href="{nav_link('package')}"><div class="action-icon">▱</div><div class="action-title">Perfectly Packaged</div><div class="action-copy">Build and save customer kit concepts.</div></a>
<a class="action-card" href="{nav_link('concept')}"><div class="action-icon">✎</div><div class="action-title">Design Concepts</div><div class="action-copy">Save creative briefs and reference art.</div></a>
<a class="action-card" href="{nav_link('data')}"><div class="action-icon">⚙</div><div class="action-title">Data Sources</div><div class="action-copy">Load and validate full PCNA master files.</div></a>
</div>
""",
        unsafe_allow_html=True,
    )

elif page == "create":
    page_header("Create", "What do you need?", "Choose a workflow. Every form is optimized for one-handed phone use.")
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('spec')}"><div class="action-icon">✓</div><div class="action-title">Spec Sample</div><div class="action-copy">Verified decorated sample order.</div></a>
<a class="action-card" href="{nav_link('blank')}"><div class="action-icon">□</div><div class="action-title">Blank Sample</div><div class="action-copy">Fast blank item request.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-icon">$</div><div class="action-title">Quote</div><div class="action-copy">Decorated price by quantity.</div></a>
<a class="action-card" href="{nav_link('virtual')}"><div class="action-icon">◇</div><div class="action-title">Virtual</div><div class="action-copy">Product + artwork + direction.</div></a>
<a class="action-card" href="{nav_link('package')}"><div class="action-icon">▱</div><div class="action-title">Packaging</div><div class="action-copy">Perfectly Packaged concept.</div></a>
<a class="action-card" href="{nav_link('concept')}"><div class="action-icon">✎</div><div class="action-title">Concept</div><div class="action-copy">Save a creative brief.</div></a>
</div>
""",
        unsafe_allow_html=True,
    )

elif page == "search":
    page_header("Verified Catalog", "Find a product", "Search the active PCNA catalog without digging through the full website.")
    identity = product_picker("search")
    if identity:
        item = identity["Item Number"]
        st.markdown(f'<div class="section-title">{identity["Product Name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="data-chip">Item {item}</span><span class="data-chip">{identity.get("Brand","") or "PCNA"}</span>', unsafe_allow_html=True)
        with st.expander("Colors", expanded=True):
            colors = colors_for_item(st.session_state.products, item)
            st.write(" · ".join(colors) if colors else "No color data available.")
        with st.expander("Decoration options", expanded=True):
            d = decorations_for_item(st.session_state.decorations, item)
            if d.empty:
                st.info("No decoration data in the active dataset.")
            else:
                for _, row in d.head(40).iterrows():
                    st.markdown(f"**{row['Decoration Method']}**  \n{row['Decoration Location']} · max {imprint_size(row)}")
                    st.divider()
        st.link_button("Open PCNA.com", "https://www.pcna.com/en-us", use_container_width=True)

elif page == "spec":
    page_header("Orders", "Spec Sample", "Build the exact spec sample format using verified product, color and decoration data.")
    po = st.text_input("PO#")
    customer = st.text_input("Customer / Project", placeholder="Ford — Fall Event")
    ship_date = st.text_input("Ship Date")
    in_hands = st.text_input("In Hands Date")
    ship_to = st.text_area("Ship To")
    st.divider()
    configured = []
    for i in range(st.session_state.spec_item_count):
        with st.expander(f"Item {i+1}", expanded=True):
            cfg = product_configuration(f"spec_{i}")
            if cfg:
                configured.append(cfg)
    if st.button("＋ Add another item", use_container_width=True, disabled=st.session_state.spec_item_count >= 8):
        st.session_state.spec_item_count += 1
        st.rerun()
    if st.session_state.spec_item_count > 1 and st.button("Remove last item", use_container_width=True):
        st.session_state.spec_item_count -= 1
        st.rerun()
    if st.button("Build Spec Sample Order", type="primary", use_container_width=True, disabled=len(configured) != st.session_state.spec_item_count):
        items = [
            SpecItem(
                product=x["Product Name"], item_number=x["Item Number"], color=x["Color"], size=x["Size"],
                decoration_method=x["Decoration Method"], decoration_location=x["Decoration Location"],
                imprint_color="N/A" if is_no_ink_decoration(x["Decoration Method"]) else x["Imprint Color"],
                imprint_size="Max Imprint",
            )
            for x in configured
        ]
        order = build_spec_order(items, po=po, ship_date=ship_date, in_hands_date=in_hands, ship_to=ship_to)
        save_project("Spec Sample Order", customer, customer, {"order": order})
        st.session_state.last_spec = order
    if st.session_state.get("last_spec"):
        st.markdown('<div class="section-title">Ready to send</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="order-box">{st.session_state.last_spec}</div>', unsafe_allow_html=True)
        st.download_button("Download Order", st.session_state.last_spec, file_name="PCNA_Spec_Sample_Order.txt", use_container_width=True)

elif page == "blank":
    page_header("Orders", "Blank Sample", "Create a clean blank sample request from a verified item and color.")
    customer = st.text_input("Customer / Project")
    identity = product_picker("blank")
    if identity:
        item = identity["Item Number"]
        color = st.selectbox("Color", colors_for_item(st.session_state.products, item) or [""])
        size = st.text_input("Size (if applicable)")
        ship_to = st.text_area("Ship To")
        if st.button("Save Blank Sample", type="primary", use_container_width=True):
            save_project("Blank Sample", customer, customer, {"Product": identity["Product Name"], "Item Number": item, "Color": color, "Size": size, "Ship To": ship_to})
            st.success("Blank sample saved.")

elif page == "quote":
    page_header("Pricing", "Quick Quote", "Standard quotes default to USD list decorated pricing — never blank pricing unless intentionally changed in the data workflow.")
    customer = st.text_input("Customer / Project")
    identity = product_picker("quote")
    if identity:
        item = identity["Item Number"]
        qty = int(st.number_input("Quantity", min_value=1, value=100, step=1))
        color = st.selectbox("Color", colors_for_item(st.session_state.products, item) or [""])
        schedules = pricing_schedules(st.session_state.pricing, item, currency="USD", decorated=True)
        if not schedules:
            st.warning("No USD decorated pricing in the active pricing dataset.")
        else:
            schedule = st.selectbox("Decorated pricing schedule", schedules, index=0)
            tier = quote_tier(st.session_state.pricing, item, qty, currency="USD", decorated=True, schedule=schedule)
            if tier:
                st.markdown(f'<div class="info-card"><div class="info-card-title">${tier["Unit Price"]:,.2f} each</div><div class="info-card-meta">{qty:,} pieces · tier {tier["MOQ Tier"]:,} · extended ${tier["Unit Price"]*qty:,.2f}</div></div>', unsafe_allow_html=True)
                if tier["Below MOQ"]:
                    st.warning(f"Quantity is below the first decorated tier ({tier['MOQ Tier']}).")
                st.caption(f"Source: {tier['Schedule']} · {tier['Price Description']}")
                if st.button("Save Quote", type="primary", use_container_width=True):
                    save_project("Quote", customer, customer, {**identity, "Quantity": qty, "Color": color, **tier})
                    st.success("Quote saved.")

elif page == "virtual":
    page_header("Creative", "Virtual Request", "Keep the verified product, artwork and decoration direction in one customer project.")
    customer = st.text_input("Customer / Project")
    cfg = product_configuration("virtual")
    artwork = st.file_uploader("Artwork", type=["png", "jpg", "jpeg", "pdf", "svg", "eps", "ai"])
    instructions = st.text_area("Creative Instructions", placeholder="White logo, left chest, show on black garment...")
    if st.button("Save Virtual Request", type="primary", use_container_width=True, disabled=cfg is None):
        save_project("Virtual Request", customer, customer, {**cfg, "Artwork": artwork.name if artwork else "", "Instructions": instructions}, [artwork] if artwork else [])
        st.success("Virtual request and artwork saved.")

elif page == "package":
    page_header("Kitting", "Perfectly Packaged", "Save kit components, creative direction and artwork together by customer.")
    customer = st.text_input("Customer")
    package_name = st.text_input("Package / Concept Name", placeholder="Ford Dealer Welcome Kit")
    items = st.text_area("Verified Kit Components", placeholder="One verified component per line", height=150)
    concept = st.text_area("Packaging / Design Direction", height=150)
    refs = st.file_uploader("Reference files / artwork", accept_multiple_files=True, type=["png", "jpg", "jpeg", "pdf", "svg"])
    st.link_button("View Perfectly Packaged on PCNA.com", "https://www.pcna.com/en-us/tools-services/perfectly-packaged", use_container_width=True)
    if st.button("Save Perfectly Packaged Project", type="primary", use_container_width=True):
        save_project("Perfectly Packaged", customer, package_name, {"Components": [x.strip() for x in items.splitlines() if x.strip()], "Concept": concept, "Files": [f.name for f in refs]}, refs)
        st.success("Package project saved.")

elif page == "concept":
    page_header("Creative", "Design Concept", "Capture a customer idea, campaign brief and reference files without losing context.")
    customer = st.text_input("Customer")
    concept_name = st.text_input("Concept Name")
    brief = st.text_area("Creative Brief", height=180)
    files = st.file_uploader("Reference files", accept_multiple_files=True, type=["png", "jpg", "jpeg", "pdf", "svg"])
    if st.button("Save Design Concept", type="primary", use_container_width=True):
        save_project("Design Concept", customer, concept_name, {"Brief": brief, "Files": [f.name for f in files]}, files)
        st.success("Design concept saved.")

elif page == "saved":
    page_header("Workspace", "Saved Projects", "Everything you create stays organized here so you can reopen customer work later.")
    projects = persistent_projects()
    search = st.text_input("Filter saved work", placeholder="Customer, project, quote, virtual...")
    if search:
        q = search.lower()
        projects = [p for p in projects if q in f"{p['customer']} {p['project']} {p['type']}".lower()]
    if not projects:
        st.info("No matching saved projects yet.")
    for project in projects:
        with st.expander(f"{project['customer']} · {project['project']}"):
            st.caption(f"{project['type']} · {project['date'][:10]}")
            payload = project["payload"]
            if "order" in payload:
                st.markdown(f'<div class="order-box">{payload["order"]}</div>', unsafe_allow_html=True)
            else:
                st.json(payload)
            for f in list_project_files(project["id"]):
                st.download_button(f"Download {f.name}", f.read_bytes(), file_name=f.name, key=f"file_{project['id']}_{f.name}", use_container_width=True)
            if st.button("Delete Project", key=f"delete_{project['id']}", use_container_width=True):
                delete_project(project["id"])
                st.rerun()
    if projects:
        st.download_button("Export All Projects", export_projects(), file_name="PCNA_Assistant_Projects.json", mime="application/json", use_container_width=True)

elif page == "assistant":
    page_header("AI Workspace", "Ask PCNA Assistant", "Natural-language help with verified PCNA product context. Missing facts are never invented.")
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        secret_key = ""
    api_key = secret_key or st.text_input("OpenAI API key", type="password")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ask about a product, quote, spec sample or virtual...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        matches = search_products(st.session_state.products, prompt, limit=8)
        context = matches[["Product Name", "Item Number", "Brand", "Default Item Color"]].to_dict("records") if not matches.empty else []
        if not api_key:
            reply = "Add an OpenAI API key to enable conversational AI. The verified deterministic workflows remain available throughout the app."
        else:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.responses.create(
                    model="gpt-5",
                    instructions="You are PCNA Assistant. Never invent PCNA product names, item numbers, colors, decoration methods, locations, or pricing. Use only verified supplied context for PCNA factual claims. Standard quotes use decorated pricing unless blank pricing is explicitly requested. Be concise and operational.",
                    input=f"USER REQUEST:\n{prompt}\n\nVERIFIED LOCAL PCNA MATCHES:\n{json.dumps(context, ensure_ascii=False)}",
                )
                reply = response.output_text
            except Exception as exc:
                reply = f"AI request could not be completed: {exc}"
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

elif page == "data":
    page_header("Administration", "Data Sources", "Load full PCNA master files. Required columns are validated before the active dataset changes.")
    st.markdown(f'<div class="info-card"><div class="info-card-title">{st.session_state.data_source}</div><div class="info-card-meta">{len(st.session_state.products):,} product/color rows · {len(st.session_state.decorations):,} decoration rows · {len(st.session_state.pricing):,} pricing rows</div></div>', unsafe_allow_html=True)
    pfile = st.file_uploader("Product Master CSV", type=["csv", "gz"], key="product_master")
    dfile = st.file_uploader("Decoration Master CSV", type=["csv", "gz"], key="decoration_master")
    rfile = st.file_uploader("Pricing Master CSV", type=["csv", "gz"], key="pricing_master")
    if st.button("Validate & Load Full Masters", type="primary", use_container_width=True):
        if not (pfile and dfile and rfile):
            st.error("Load all three files first.")
        else:
            try:
                st.session_state.products = prepare_products(read_csv_bytes(pfile.getvalue(), pfile.name))
                st.session_state.decorations = prepare_decorations(read_csv_bytes(dfile.getvalue(), dfile.name))
                st.session_state.pricing = prepare_pricing(read_csv_bytes(rfile.getvalue(), rfile.name))
                st.session_state.data_source = "Full PCNA masters · session loaded"
                st.success("Full masters validated and loaded.")
            except Exception as exc:
                st.error(f"Data validation failed: {exc}")
    st.link_button("Open PCNA.com", "https://www.pcna.com/en-us", use_container_width=True)

else:
    st.query_params["page"] = "home"
    st.rerun()

bottom_nav(page)

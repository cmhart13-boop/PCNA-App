from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

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
from generation import generate_concepts
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

st.markdown(
    f"""
<style>
:root{{--pcna:{PCNA_BLUE};--ink:{INK};--muted:{MUTED};--line:{LINE};--panel:{PANEL};}}
html,body,[data-testid="stAppViewContainer"]{{background:#fff;color:var(--ink);}}
[data-testid="stAppViewContainer"]>.main{{overflow-x:hidden;}}
[data-testid="stHeader"]{{height:0;background:rgba(255,255,255,.96);}}
[data-testid="stSidebar"]{{display:none;}}
#MainMenu,footer,[data-testid="stToolbar"]{{visibility:hidden!important;height:0!important;}}
.block-container{{max-width:620px!important;padding:calc(34px + env(safe-area-inset-top)) 15px 104px!important;margin:0 auto!important;}}
.pcna-live-wrap{{margin:0 0 18px;}}
.page-kicker{{font-size:11px;font-weight:900;letter-spacing:.10em;color:var(--pcna);text-transform:uppercase;margin-top:2px;}}
.page-title{{font-size:29px;line-height:1.08;font-weight:850;letter-spacing:-.035em;color:var(--pcna);margin:4px 0 9px;}}
.page-copy{{font-size:15px;line-height:1.48;color:var(--muted);margin:0 0 18px;}}
.section-title{{font-size:18px;font-weight:850;letter-spacing:-.015em;margin:20px 0 9px;color:var(--pcna);}}
.action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:4px 0 6px;}}
.action-card{{display:block;text-decoration:none!important;border:1px solid var(--line);border-radius:17px;padding:16px 14px;background:#fff;min-height:118px;box-shadow:0 5px 17px rgba(20,55,80,.055);}}
.action-icon{{font-size:24px;line-height:1;margin-bottom:14px;color:var(--pcna);}}
.action-title{{font-size:15px;font-weight:850;color:var(--pcna);line-height:1.15;margin-bottom:5px;}}
.action-copy{{font-size:12px;color:var(--muted);line-height:1.35;}}
.wide-card{{grid-column:1/-1;min-height:auto;display:flex;align-items:center;gap:12px;padding:14px 15px;}}
.wide-card .action-icon{{margin:0;font-size:22px;}}
.info-card{{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:8px 0;box-shadow:0 4px 15px rgba(20,55,80,.04);}}
.info-card-title{{font-size:15px;font-weight:850;color:var(--pcna);}}
.info-card-meta{{font-size:12px;color:var(--muted);margin-top:3px;}}
.data-chip{{display:inline-block;padding:5px 8px;border-radius:999px;background:#eef5fa;color:var(--pcna);font-size:11px;font-weight:850;margin-right:5px;}}
.order-box{{white-space:pre-wrap;border:1px solid var(--line);background:#fbfcfd;border-radius:15px;padding:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;line-height:1.5;overflow-wrap:anywhere;}}
.generated-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;}}
.stButton>button,.stDownloadButton>button,[data-testid="stLinkButton"] a{{min-height:48px!important;border-radius:13px!important;font-weight:800!important;font-size:15px!important;width:100%!important;}}
.stTextInput input,.stNumberInput input,.stTextArea textarea,[data-baseweb="select"]>div{{min-height:50px!important;border-radius:12px!important;font-size:16px!important;background:#fff!important;border-color:#b8cad8!important;color:var(--ink)!important;}}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{{border-color:var(--pcna)!important;box-shadow:0 0 0 1px var(--pcna)!important;}}
[data-baseweb="select"]>div:focus-within{{border-color:var(--pcna)!important;box-shadow:0 0 0 1px var(--pcna)!important;}}
.stTextArea textarea{{min-height:112px!important;}}
[data-testid="stFileUploaderDropzone"]{{border-radius:14px!important;padding:14px 10px!important;border-color:#b8cad8!important;background:#fbfdff!important;}}
[data-testid="stExpander"]{{border:1px solid var(--line)!important;border-radius:14px!important;overflow:hidden;margin:8px 0;}}
label,[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{{font-weight:800!important;color:var(--pcna)!important;}}
.bottom-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:0;width:min(620px,100%);height:76px;background:rgba(255,255,255,.96);backdrop-filter:blur(16px);border-top:1px solid var(--line);display:grid;grid-template-columns:repeat(4,1fr);z-index:9999;padding:7px 7px max(7px,env(safe-area-inset-bottom));box-sizing:border-box;}}
.nav-item{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;color:#7890a0!important;font-size:10px;font-weight:800;gap:3px;border-radius:12px;}}
.nav-icon{{font-size:20px;line-height:1;}}
.nav-item.active{{color:var(--pcna)!important;background:#eff6fb;}}
@media(max-width:430px){{.block-container{{padding-top:calc(38px + env(safe-area-inset-top))!important;padding-left:12px!important;padding-right:12px!important;}}.page-title{{font-size:28px;line-height:1.1;}}.action-grid{{gap:9px;}}.action-card{{padding:15px 12px;min-height:112px;}}}}
@media(max-width:350px){{.action-grid,.generated-grid{{grid-template-columns:1fr;}}.wide-card{{grid-column:auto;}}}}
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


def api_key() -> str:
    try:
        secret = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        secret = ""
    return secret or os.getenv("OPENAI_API_KEY", "")


def current_page() -> str:
    page = st.query_params.get("page", "home")
    return page if isinstance(page, str) else "home"


def nav_link(page: str) -> str:
    return f"?page={quote(page)}"


def page_header(kicker: str, title: str, copy: str):
    st.markdown(f'<div class="page-kicker">{kicker}</div><div class="page-title">{title}</div><div class="page-copy">{copy}</div>', unsafe_allow_html=True)


def live_pcna_banner():
    st.markdown('<div class="pcna-live-wrap">', unsafe_allow_html=True)
    components.html(
        """
<div class="pcna-live-shell"><div class="fallback"><a href="https://www.pcna.com/en-us" target="_blank" rel="noopener">Open live PCNA.com</a></div><iframe src="https://www.pcna.com/en-us" title="Live PCNA.com promotional banner" loading="eager"></iframe></div>
<style>html,body{margin:0;padding:0;background:#fff;overflow:hidden}.pcna-live-shell{position:relative;height:228px;overflow:hidden;border-radius:14px;background:#fff}.pcna-live-shell iframe{position:absolute;left:0;top:-92px;width:100%;height:620px;border:0;background:#fff;z-index:2}.fallback{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;border:1px solid #e2e9ef;border-radius:14px;background:#fff;z-index:1}.fallback a{color:#084f86;font-size:15px;font-weight:700;text-decoration:none}@media(max-width:430px){.pcna-live-shell{height:208px}.pcna-live-shell iframe{top:-82px;height:590px}}</style>
""",
        height=228,
        scrolling=False,
    )
    st.markdown('</div>', unsafe_allow_html=True)


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


def config_prompt(cfg: dict, instructions: str) -> str:
    return (
        f"Create a photorealistic PCNA promotional-product virtual. Product: {cfg.get('Product Name','')}. Item number: {cfg.get('Item Number','')}. "
        f"Product color: {cfg.get('Color','')}. Size: {cfg.get('Size','')}. Decoration method: {cfg.get('Decoration Method','')}. "
        f"Decoration location: {cfg.get('Decoration Location','')}. Imprint color: {cfg.get('Imprint Color','')}. "
        f"Customer instructions: {instructions or 'Use the uploaded artwork exactly as supplied and present the product cleanly.'} "
        "Keep the supplied logo/artwork faithful. Do not redesign the logo, change its spelling, invent additional marks, or change verified product details."
    )


def show_generated(project_id: int):
    images = [p for p in list_project_files(project_id) if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} and p.name.startswith("generated_")]
    if not images:
        return
    st.markdown('<div class="section-title">Generated concepts</div>', unsafe_allow_html=True)
    for path in images:
        st.image(path.read_bytes(), caption=path.stem.replace("generated_", "Concept "), use_container_width=True)
        st.download_button(f"Download {path.name}", path.read_bytes(), file_name=path.name, key=f"gen_{project_id}_{path.name}", use_container_width=True)


page = current_page()

if page == "home":
    live_pcna_banner()
    projects = persistent_projects()
    st.markdown(f'<span class="data-chip">{st.session_state.data_source}</span><span class="data-chip">{len(projects)} saved</span>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Quick actions</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('search')}"><div class="action-icon">⌕</div><div class="action-title">Find a Product</div><div class="action-copy">Search names, item numbers, colors and decoration.</div></a>
<a class="action-card" href="{nav_link('spec')}"><div class="action-icon">✓</div><div class="action-title">Spec Sample</div><div class="action-copy">Build a verified sample order.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-icon">$</div><div class="action-title">Quick Quote</div><div class="action-copy">Decorated pricing by quantity.</div></a>
<a class="action-card" href="{nav_link('virtual')}"><div class="action-icon">◇</div><div class="action-title">Generate Virtuals</div><div class="action-copy">Upload artwork and generate finished concepts.</div></a>
<a class="action-card wide-card" href="{nav_link('assistant')}"><div class="action-icon">✦</div><div><div class="action-title">Ask PCNA Assistant</div><div class="action-copy">Natural-language help with verified PCNA context.</div></div></a>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">More workflows</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('blank')}"><div class="action-icon">□</div><div class="action-title">Blank Sample</div><div class="action-copy">Create a fast blank sample request.</div></a>
<a class="action-card" href="{nav_link('package')}"><div class="action-icon">▱</div><div class="action-title">Perfectly Packaged</div><div class="action-copy">Generate customer kit concepts.</div></a>
<a class="action-card" href="{nav_link('concept')}"><div class="action-icon">✎</div><div class="action-title">Design Concepts</div><div class="action-copy">Save creative briefs and reference art.</div></a>
<a class="action-card" href="{nav_link('data')}"><div class="action-icon">⚙</div><div class="action-title">Data Sources</div><div class="action-copy">Load and validate PCNA master files.</div></a>
</div>
""",
        unsafe_allow_html=True,
    )

elif page == "create":
    page_header("Create", "What do you need?", "Choose a workflow. Every form is optimized for one-handed phone use.")
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('spec')}"><div class="action-title">Spec Sample</div><div class="action-copy">Verified decorated sample order.</div></a>
<a class="action-card" href="{nav_link('blank')}"><div class="action-title">Blank Sample</div><div class="action-copy">Fast blank item request.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-title">Quote</div><div class="action-copy">Decorated price by quantity.</div></a>
<a class="action-card" href="{nav_link('virtual')}"><div class="action-title">Virtual</div><div class="action-copy">Generate product virtuals from artwork.</div></a>
<a class="action-card" href="{nav_link('package')}"><div class="action-title">Packaging</div><div class="action-copy">Generate Perfectly Packaged concepts.</div></a>
<a class="action-card" href="{nav_link('concept')}"><div class="action-title">Concept</div><div class="action-copy">Save a creative brief.</div></a>
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
            st.write(" · ".join(colors_for_item(st.session_state.products, item)) or "No color data available.")
        with st.expander("Decoration options", expanded=True):
            d = decorations_for_item(st.session_state.decorations, item)
            if d.empty:
                st.info("No decoration data in the active dataset.")
            else:
                for _, row in d.head(40).iterrows():
                    st.markdown(f"**{row['Decoration Method']}**  \n{row['Decoration Location']} · max {imprint_size(row)}")
                    st.divider()
        st.link_button("Open this product area on PCNA.com", "https://www.pcna.com", use_container_width=True)

elif page == "spec":
    page_header("Orders", "Spec Sample", "Build the exact spec sample format using verified product, color and decoration data.")
    po = st.text_input("PO#")
    customer = st.text_input("Customer / Project", placeholder="Ford — Fall Event")
    ship_date = st.text_input("Ship Date")
    in_hands = st.text_input("In Hands Date")
    ship_to = st.text_area("Ship To")
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
        items = [SpecItem(product=x["Product Name"], item_number=x["Item Number"], color=x["Color"], size=x["Size"], decoration_method=x["Decoration Method"], decoration_location=x["Decoration Location"], imprint_color="N/A" if is_no_ink_decoration(x["Decoration Method"]) else x["Imprint Color"], imprint_size="Max Imprint") for x in configured]
        order = build_spec_order(items, po=po, ship_date=ship_date, in_hands_date=in_hands, ship_to=ship_to)
        save_project("Spec Sample Order", customer, customer, {"order": order})
        st.session_state.last_spec = order
    if st.session_state.get("last_spec"):
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
    page_header("Pricing", "Quick Quote", "Standard quotes default to decorated pricing.")
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
                st.markdown(f'<div class="info-card"><div class="info-card-title">${tier["Unit Price"]:,.2f} each</div><div class="info-card-meta">{qty:,} pieces · extended ${tier["Unit Price"]*qty:,.2f}</div></div>', unsafe_allow_html=True)
                if st.button("Save Quote", type="primary", use_container_width=True):
                    save_project("Quote", customer, customer, {**identity, "Quantity": qty, "Color": color, **tier})
                    st.success("Quote saved.")

elif page == "virtual":
    page_header("Creative", "Generate Virtuals", "Select the verified product, upload artwork, choose how many concepts you want, and generate them directly into the project.")
    customer = st.text_input("Customer / Project")
    cfg = product_configuration("virtual")
    artwork = st.file_uploader("Artwork / reference files", accept_multiple_files=True, type=["png", "jpg", "jpeg", "webp", "pdf", "svg", "eps", "ai"])
    instructions = st.text_area("Creative Instructions", placeholder="Use the supplied logo exactly. White logo, left chest, clean studio presentation...")
    count = int(st.number_input("Number of virtuals", min_value=1, max_value=8, value=5, step=1))
    if not api_key():
        st.info("Generation is ready. Add OPENAI_API_KEY in Streamlit App Settings → Secrets to enable the Generate button.")
    if st.button("Generate Virtuals", type="primary", use_container_width=True, disabled=cfg is None or not api_key()):
        payload = {**cfg, "Artwork": [f.name for f in artwork], "Instructions": instructions, "Requested Concepts": count, "Generation": "OpenAI image_generation"}
        project_id = save_project("Virtual Request", customer, customer, payload, artwork)
        progress = st.progress(0, text=f"Generating 0 of {count}...")
        try:
            images = []
            for i in range(count):
                progress.progress(i / count, text=f"Generating {i+1} of {count}...")
                new_image = generate_concepts(api_key=api_key(), prompt=config_prompt(cfg, instructions), uploads=artwork, count=1)[0]
                images.append(new_image)
                save_upload(project_id, f"generated_{i+1:02d}.png", new_image)
            progress.progress(1.0, text=f"Generated {count} of {count}.")
            st.success(f"{count} virtuals generated and saved to this project.")
            st.session_state.last_generated_project = project_id
        except Exception as exc:
            st.error(f"Generation could not be completed: {exc}")
    if st.session_state.get("last_generated_project"):
        show_generated(st.session_state.last_generated_project)

elif page == "package":
    page_header("Kitting", "Perfectly Packaged", "Upload customer artwork and references, describe the kit, and generate finished packaging concepts directly into the saved project.")
    customer = st.text_input("Customer")
    package_name = st.text_input("Package / Concept Name", placeholder="Ford Dealer Welcome Kit")
    items = st.text_area("Verified Kit Components", placeholder="One verified PCNA component per line", height=140)
    concept = st.text_area("Packaging / Design Direction", height=150, placeholder="Use only the approved PCNA Perfectly Packaged structure. Create distinct concepts using the uploaded brand artwork...")
    refs = st.file_uploader("Artwork / reference files", accept_multiple_files=True, type=["png", "jpg", "jpeg", "webp", "pdf", "svg", "eps", "ai"])
    count = int(st.number_input("Number of packaging concepts", min_value=1, max_value=8, value=5, step=1))
    if not api_key():
        st.info("Generation is ready. Add OPENAI_API_KEY in Streamlit App Settings → Secrets to enable the Generate button.")
    if st.button("Generate Packaging Concepts", type="primary", use_container_width=True, disabled=not api_key() or not items.strip()):
        payload = {"Components": [x.strip() for x in items.splitlines() if x.strip()], "Concept": concept, "Files": [f.name for f in refs], "Requested Concepts": count, "Generation": "OpenAI image_generation"}
        project_id = save_project("Perfectly Packaged", customer, package_name, payload, refs)
        prompt = (
            "Create a polished PCNA Perfectly Packaged client concept. Use only the supplied verified kit components and uploaded customer artwork/reference files. "
            f"Verified components: {items}. Design direction: {concept}. "
            "Do not invent products, logos, colors, packaging structures, or brand elements. Keep supplied logos faithful and produce a presentation-ready packaging mockup."
        )
        progress = st.progress(0, text=f"Generating 0 of {count}...")
        try:
            for i in range(count):
                progress.progress(i / count, text=f"Generating {i+1} of {count}...")
                new_image = generate_concepts(api_key=api_key(), prompt=prompt, uploads=refs, count=1)[0]
                save_upload(project_id, f"generated_{i+1:02d}.png", new_image)
            progress.progress(1.0, text=f"Generated {count} of {count}.")
            st.success(f"{count} packaging concepts generated and saved to this project.")
            st.session_state.last_generated_project = project_id
        except Exception as exc:
            st.error(f"Generation could not be completed: {exc}")
    if st.session_state.get("last_generated_project"):
        show_generated(st.session_state.last_generated_project)

elif page == "concept":
    page_header("Creative", "Design Concept", "Capture a customer idea, campaign brief and reference files.")
    customer = st.text_input("Customer")
    concept_name = st.text_input("Concept Name")
    brief = st.text_area("Creative Brief", height=180)
    files = st.file_uploader("Reference files", accept_multiple_files=True, type=["png", "jpg", "jpeg", "pdf", "svg"])
    if st.button("Save Design Concept", type="primary", use_container_width=True):
        save_project("Design Concept", customer, concept_name, {"Brief": brief, "Files": [f.name for f in files]}, files)
        st.success("Design concept saved.")

elif page == "saved":
    page_header("Workspace", "Saved Projects", "Open prior requests and download the original artwork and generated concept files from the project.")
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
            files = list_project_files(project["id"])
            generated = [f for f in files if f.name.startswith("generated_") and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
            for f in generated:
                st.image(f.read_bytes(), caption=f.name, use_container_width=True)
                st.download_button(f"Download {f.name}", f.read_bytes(), file_name=f.name, key=f"file_{project['id']}_{f.name}", use_container_width=True)
            originals = [f for f in files if f not in generated]
            for f in originals:
                st.download_button(f"Download original · {f.name}", f.read_bytes(), file_name=f.name, key=f"orig_{project['id']}_{f.name}", use_container_width=True)
            if st.button("Delete Project", key=f"delete_{project['id']}", use_container_width=True):
                delete_project(project["id"])
                st.rerun()
    if projects:
        st.download_button("Export All Projects", export_projects(), file_name="PCNA_Assistant_Projects.json", mime="application/json", use_container_width=True)

elif page == "assistant":
    page_header("AI Workspace", "Ask PCNA Assistant", "Natural-language help with verified PCNA product context.")
    key = api_key() or st.text_input("OpenAI API key", type="password")
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
        if not key:
            reply = "Add OPENAI_API_KEY in Streamlit Secrets to enable AI."
        else:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=key)
                response = client.responses.create(model="gpt-5", instructions="You are PCNA Assistant. Never invent PCNA product names, item numbers, colors, decoration methods, locations, or pricing. Use only verified supplied context for PCNA factual claims. Be concise and operational.", input=f"USER REQUEST:\n{prompt}\n\nVERIFIED LOCAL PCNA MATCHES:\n{json.dumps(context, ensure_ascii=False)}")
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
    st.link_button("Open PCNA.com", "https://www.pcna.com", use_container_width=True)

else:
    st.query_params["page"] = "home"
    st.rerun()

bottom_nav(page)

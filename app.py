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
from pcna_brain import (
    PCNA_WORKFLOW_RULES,
    build_creative_pcna_context,
    creative_generation_prompt,
    resolve_spec_request,
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
LINE = "#d6e2eb"
PANEL = "#f7fafc"

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
.page-kicker{{font-size:11px;font-weight:900;letter-spacing:.10em;color:var(--pcna);text-transform:uppercase;margin-top:2px;}}
.page-title{{font-size:29px;line-height:1.08;font-weight:850;letter-spacing:-.035em;color:var(--pcna);margin:4px 0 9px;}}
.page-copy{{font-size:15px;line-height:1.48;color:var(--muted);margin:0 0 18px;}}
.section-title{{font-size:18px;font-weight:850;letter-spacing:-.015em;margin:22px 0 10px;color:var(--pcna);}}
.action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin:8px 0 10px;}}
.action-card{{display:block;text-decoration:none!important;border:1.5px solid rgba(8,79,134,.36);border-radius:17px;padding:17px 15px;background:#fff;min-height:122px;box-shadow:0 5px 0 rgba(8,79,134,.10),0 12px 24px rgba(8,79,134,.09);transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease;}}
.action-card:hover{{border-color:rgba(8,79,134,.58);box-shadow:0 6px 0 rgba(8,79,134,.13),0 14px 28px rgba(8,79,134,.12);}}
.action-card:active{{transform:translateY(3px);box-shadow:0 2px 0 rgba(8,79,134,.12),0 7px 14px rgba(8,79,134,.08);}}
.action-icon{{font-size:24px;line-height:1;margin-bottom:14px;color:var(--pcna);}}
.action-title{{font-size:16px;font-weight:850;color:var(--pcna);line-height:1.15;margin-bottom:6px;}}
.action-copy{{font-size:12px;color:var(--muted);line-height:1.35;}}
.info-card{{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:8px 0;box-shadow:0 4px 14px rgba(8,79,134,.05);}}
.info-card-title{{font-size:15px;font-weight:850;color:var(--pcna);}}
.info-card-meta{{font-size:12px;color:var(--muted);margin-top:3px;}}
.data-chip{{display:inline-block;padding:5px 8px;border-radius:999px;background:#eef5fa;color:var(--pcna);font-size:11px;font-weight:850;margin-right:5px;}}
.order-box{{white-space:pre-wrap;border:1px solid var(--line);background:#fbfcfd;border-radius:15px;padding:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;line-height:1.5;overflow-wrap:anywhere;}}
.stButton>button,.stDownloadButton>button,[data-testid="stLinkButton"] a{{min-height:48px!important;border-radius:13px!important;font-weight:800!important;font-size:15px!important;width:100%!important;}}
.stTextInput input,.stNumberInput input,.stTextArea textarea,[data-baseweb="select"]>div{{min-height:50px!important;border-radius:12px!important;font-size:16px!important;background:#fff!important;border-color:#b8cad8!important;color:var(--ink)!important;}}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{{border-color:var(--pcna)!important;box-shadow:0 0 0 1px var(--pcna)!important;}}
[data-baseweb="select"]>div:focus-within{{border-color:var(--pcna)!important;box-shadow:0 0 0 1px var(--pcna)!important;}}
.stTextArea textarea{{min-height:120px!important;}}
[data-testid="stFileUploaderDropzone"]{{border-radius:14px!important;padding:14px 10px!important;border-color:#b8cad8!important;background:#fbfdff!important;}}
[data-testid="stExpander"]{{border:1px solid var(--line)!important;border-radius:14px!important;overflow:hidden;margin:8px 0;}}
label,[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{{font-weight:800!important;color:var(--pcna)!important;}}
.bottom-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:0;width:min(620px,100%);height:76px;background:rgba(255,255,255,.96);backdrop-filter:blur(16px);border-top:1px solid var(--line);display:grid;grid-template-columns:repeat(4,1fr);z-index:9999;padding:7px 7px max(7px,env(safe-area-inset-bottom));box-sizing:border-box;}}
.nav-item{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;color:#7890a0!important;font-size:10px;font-weight:800;gap:3px;border-radius:12px;}}
.nav-icon{{font-size:20px;line-height:1;}}
.nav-item.active{{color:var(--pcna)!important;background:#eff6fb;}}
@media(max-width:430px){{.block-container{{padding-top:calc(38px + env(safe-area-inset-top))!important;padding-left:12px!important;padding-right:12px!important;}}.page-title{{font-size:28px;line-height:1.1;}}.action-grid{{gap:11px;}}.action-card{{padding:15px 13px;min-height:116px;}}}}
@media(max-width:350px){{.action-grid{{grid-template-columns:1fr;}}}}

/* Approved PCNA homepage reference layout */
.home-topbar{{height:74px;display:grid;grid-template-columns:64px 1fr 64px;align-items:center;margin:-12px 2px 12px}}.home-logo{{display:block;width:145px;max-height:54px;object-fit:contain;justify-self:center}}.home-menu,.home-bell{{display:flex;align-items:center;justify-content:center;width:46px;height:46px;color:#043f79!important;text-decoration:none!important}}.home-menu{{flex-direction:column;gap:5px;justify-self:start}}.home-menu span{{height:4px;width:31px;background:#043f79;border-radius:4px}}.home-bell{{justify-self:end;font-size:27px}}.home-bell svg{{width:28px;height:28px;stroke:#043f79;fill:none;stroke-width:2}}
.home-section-title{{font-size:25px;font-weight:900;letter-spacing:-.025em;color:#052f68;margin:9px 11px 0}}.home-title-underline{{height:3px;width:42px;border-radius:2px;background:#24a6e0;margin:5px 0 10px 11px;box-shadow:0 4px 8px rgba(36,166,224,.25)}}
.home-action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:0 2px 10px}}.home-action-card{{position:relative;display:block;height:238px;overflow:hidden;text-decoration:none!important;border:1px solid rgba(9,80,146,.16);border-radius:16px;background:#fff;padding:16px 14px;box-sizing:border-box;box-shadow:0 0 8px rgba(21,136,220,.24),0 7px 14px rgba(0,55,110,.10)}}.home-card-icon{{width:44px;height:44px;border-radius:50%;background:#064b91;color:#fff;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;margin-bottom:13px}}.home-card-title{{position:relative;z-index:2;color:#052f68;font-size:21px;line-height:1.02;font-weight:900;letter-spacing:-.025em;max-width:72%}}.home-card-copy{{position:relative;z-index:2;color:#173b63;font-size:12.5px;line-height:1.48;margin-top:11px;max-width:68%}}.home-card-visual{{position:absolute;right:12px;bottom:35px;width:43%;height:46%;opacity:.9}}.home-card-visual:before,.home-card-visual:after{{content:"";position:absolute;border:3px solid #183d66;border-radius:14px}}.visual-bag:before{{inset:5px 8px 0;border-radius:20px 20px 12px 12px}}.visual-bag:after{{width:36px;height:22px;left:50%;top:-7px;transform:translateX(-50%);border-bottom:0;border-radius:18px 18px 0 0}}.visual-laptop:before{{left:2px;right:2px;top:3px;bottom:22px;border-radius:7px}}.visual-laptop:after{{left:-8px;right:-8px;bottom:10px;height:5px;border-radius:8px}}.visual-quote:before{{inset:0 8px 8px;border-radius:9px}}.visual-quote:after{{left:19px;right:19px;bottom:22px;height:43px;border-width:0 0 3px 3px;border-radius:0;box-shadow:14px -8px 0 -10px #183d66,28px -24px 0 -10px #183d66}}.visual-project:before{{inset:3px 6px 0;border-radius:5px;transform:rotate(-7deg)}}.visual-project:after{{right:0;top:8px;width:8px;height:88%;border-radius:5px;background:#183d66;border:0;transform:rotate(-7deg)}}.home-arrow{{position:absolute;z-index:3;right:10px;bottom:10px;width:42px;height:42px;border-radius:50%;background:#064b91;color:#fff;display:flex;align-items:center;justify-content:center;font-size:29px;font-weight:500}}
.bottom-nav{{height:78px!important;width:min(590px,calc(100% - 24px))!important;bottom:9px!important;border:0!important;border-radius:38px!important;background:#064b91!important;box-shadow:0 8px 24px rgba(0,42,89,.16)!important;padding:6px 14px max(6px,env(safe-area-inset-bottom))!important;grid-template-columns:repeat(5,1fr)!important}}.nav-item{{color:#fff!important;font-size:11px!important;opacity:.96}}.nav-icon{{font-size:23px!important}}.nav-item.active{{color:#fff!important;background:transparent!important;position:relative}}.nav-item.active:after{{content:"";position:absolute;bottom:0;width:40px;height:3px;background:#fff;border-radius:4px}}
@media(max-width:430px){{.block-container{{padding-top:calc(18px + env(safe-area-inset-top))!important;padding-left:12px!important;padding-right:12px!important;padding-bottom:104px!important}}.home-topbar{{height:68px}}.home-logo{{width:140px}}.home-action-card{{height:230px}}.home-card-title{{font-size:20px}}.home-card-copy{{font-size:12px}}.pcna-live-shell{{height:236px!important}}}}
@media(max-width:350px){{.home-action-grid{{grid-template-columns:1fr 1fr!important;gap:8px}}.home-action-card{{height:220px;padding:13px 11px}}.home-card-title{{font-size:18px}}.home-card-copy{{font-size:11px}}.home-card-icon{{width:39px;height:39px;font-size:22px}}}}

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


def virtual_projects_link() -> str:
    return "?page=virtual&view=projects"


def page_header(kicker: str, title: str, copy: str):
    st.markdown(f'<div class="page-kicker">{kicker}</div><div class="page-title">{title}</div><div class="page-copy">{copy}</div>', unsafe_allow_html=True)


def home_header():
    st.markdown(
        """
<div class="home-topbar">
  <a class="home-menu" href="?page=create" aria-label="Menu"><span></span><span></span><span></span></a>
  <img class="home-logo" src="https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/pcna-logo.webp" alt="PCNA">
  <a class="home-bell" href="?page=assistant" aria-label="Notifications and messages">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"></path><path d="M10 21h4"></path></svg>
  </a>
</div>
""",
        unsafe_allow_html=True,
    )


def live_pcna_banner():
    components.html(
        """
<div class="pcna-live-shell"><div class="fallback"><a href="https://www.pcna.com/en-us" target="_blank" rel="noopener">Open live PCNA.com</a></div><iframe src="https://www.pcna.com/en-us" title="Live PCNA.com promotional banner" loading="eager"></iframe></div>
<style>html,body{margin:0;padding:0;background:#fff;overflow:hidden}.pcna-live-shell{position:relative;height:244px;overflow:hidden;border-radius:18px;background:#fff}.pcna-live-shell iframe{position:absolute;left:0;top:-92px;width:100%;height:620px;border:0;background:#fff;z-index:2}.fallback{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;border:1px solid #d6e2eb;border-radius:14px;background:#fff;z-index:1}.fallback a{color:#084f86;font-size:15px;font-weight:700;text-decoration:none}@media(max-width:430px){.pcna-live-shell{height:236px}.pcna-live-shell iframe{top:-82px;height:590px}}</style>
""",
        height=244,
        scrolling=False,
    )


def bottom_nav(page: str):
    group = page
    if page == "virtual":
        group = "projects" if st.query_params.get("view", "new") == "projects" else "virtual"
    st.markdown(
        f"""
<div class="bottom-nav">
<a class="nav-item {'active' if group=='home' else ''}" href="{nav_link('home')}"><span class="nav-icon">⌂</span><span>Home</span></a>
<a class="nav-item {'active' if group=='projects' else ''}" href="{virtual_projects_link()}"><span class="nav-icon">□</span><span>Projects</span></a>
<a class="nav-item {'active' if group=='search' else ''}" href="{nav_link('search')}"><span class="nav-icon">◇</span><span>Products</span></a>
<a class="nav-item {'active' if group=='assistant' else ''}" href="{nav_link('assistant')}"><span class="nav-icon">◯</span><span>Messages</span></a>
<a class="nav-item {'active' if group=='data' else ''}" href="{nav_link('data')}"><span class="nav-icon">♙</span><span>Account</span></a>
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


def quote_products(products: list[dict], quantity: int) -> tuple[list[dict], float]:
    lines: list[dict] = []
    unit_total = 0.0
    for product in products:
        item = str(product.get("Item Number", ""))
        schedules = pricing_schedules(st.session_state.pricing, item, currency="USD", decorated=True)
        if not schedules:
            lines.append({**product, "Quantity": quantity, "Pricing Available": False})
            continue
        tier = quote_tier(st.session_state.pricing, item, quantity, currency="USD", decorated=True, schedule=schedules[0])
        if not tier:
            lines.append({**product, "Quantity": quantity, "Pricing Available": False})
            continue
        unit_total += float(tier["Unit Price"])
        lines.append({**product, **tier, "Pricing Available": True})
    return lines, unit_total


def quote_text(project: dict, virtual_name: str, quantity: int, quote_lines: list[dict], unit_total: float) -> str:
    out = [
        "PCNA VIRTUAL QUOTE",
        "",
        f"Project: {project['project']}",
        f"Customer: {project['customer']}",
        f"Virtual: {virtual_name}",
        f"Quantity: {quantity}",
        "",
    ]
    for i, line in enumerate(quote_lines, 1):
        out.extend([
            f"ITEM {i}",
            f"Product: {line.get('Product Name','')}",
            f"Item Number: {line.get('Item Number','')}",
            f"Color: {line.get('Color','')}",
            f"Decoration Method: {line.get('Decoration Method','')}",
            f"Decoration Location: {line.get('Decoration Location','')}",
        ])
        if line.get("Pricing Available"):
            out.extend([
                f"Unit Price: ${float(line.get('Unit Price',0)):,.2f}",
                f"Extended: ${float(line.get('Unit Price',0))*quantity:,.2f}",
                f"Schedule: {line.get('Schedule','')}",
            ])
        else:
            out.append("Pricing: Not available in active pricing data")
        out.append("")
    if unit_total:
        out.extend([
            f"Combined Unit Total: ${unit_total:,.2f}",
            f"Combined Extended Total: ${unit_total*quantity:,.2f}",
        ])
    return "\n".join(out)


def render_virtual_project(project: dict, *, expanded: bool = False):
    payload = project.get("payload", {})
    products = payload.get("Verified Products", []) or payload.get("Selected Products", []) or []
    files = list_project_files(project["id"])
    generated = [f for f in files if f.name.startswith("generated_") and f.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    originals = [f for f in files if f not in generated and not f.name.endswith(".txt")]
    with st.expander(f"{project['customer']} · {project['project']}", expanded=expanded):
        st.caption(f"{project['date'][:10]} · {len(generated)} generated virtuals")
        if payload.get("Request"):
            st.write(payload["Request"])
        if originals:
            with st.expander("Original artwork / references"):
                for f in originals:
                    st.download_button(f"Download {f.name}", f.read_bytes(), file_name=f.name, key=f"orig_{project['id']}_{f.name}", use_container_width=True)
        if not generated:
            st.info("No generated virtual files are stored in this project yet.")
        for virtual_index, f in enumerate(generated, 1):
            st.markdown(f'<div class="section-title">Virtual {virtual_index}</div>', unsafe_allow_html=True)
            st.image(f.read_bytes(), caption=f.name, use_container_width=True)
            st.download_button("Download Virtual", f.read_bytes(), file_name=f.name, key=f"download_{project['id']}_{f.name}", use_container_width=True)
            with st.expander("Product Info"):
                if not products:
                    st.info("No verified product configuration is attached to this virtual.")
                for i, product in enumerate(products, 1):
                    st.markdown(f"**{i}. {product.get('Product Name','')}**")
                    st.write(f"Item Number: {product.get('Item Number','')}")
                    st.write(f"Color: {product.get('Color','')}")
                    st.write(f"Decoration Method: {product.get('Decoration Method','')}")
                    st.write(f"Decoration Location: {product.get('Decoration Location','')}")
                    if product.get("Max Imprint"):
                        st.write(f"Max Imprint: {product.get('Max Imprint')}")
                    if product.get("Project Role"):
                        st.caption(product.get("Project Role"))
                    if i < len(products):
                        st.divider()
            with st.expander("Quote Virtual"):
                qty = int(st.number_input("Quantity", min_value=1, value=100, step=1, key=f"qty_{project['id']}_{f.name}"))
                if st.button("Quote This Virtual", key=f"quote_{project['id']}_{f.name}", use_container_width=True, disabled=not products):
                    quote_lines, unit_total = quote_products(products, qty)
                    text = quote_text(project, f.name, qty, quote_lines, unit_total)
                    quote_filename = f"{f.stem}_quote_{qty}.txt"
                    save_upload(project["id"], quote_filename, text.encode("utf-8"))
                    st.session_state[f"quote_result_{project['id']}_{f.name}"] = text
                result = st.session_state.get(f"quote_result_{project['id']}_{f.name}")
                if result:
                    st.markdown(f'<div class="order-box">{result}</div>', unsafe_allow_html=True)
                    st.download_button("Download Quote", result, file_name=f"{f.stem}_quote.txt", key=f"quote_dl_{project['id']}_{f.name}", use_container_width=True)
        quote_files = [f for f in files if f.name.endswith(".txt") and "_quote_" in f.name]
        if quote_files:
            with st.expander("Saved Quotes"):
                for f in quote_files:
                    st.download_button(f"Download {f.name}", f.read_bytes(), file_name=f.name, key=f"savedquote_{project['id']}_{f.name}", use_container_width=True)
        if st.button("Delete Project", key=f"delete_virtual_{project['id']}", use_container_width=True):
            delete_project(project["id"])
            st.rerun()


def render_virtual_projects():
    projects = [p for p in persistent_projects() if p.get("type") in {"Virtual / Design", "Virtual Request", "Perfectly Packaged"}]
    st.markdown('<div class="section-title">Projects</div>', unsafe_allow_html=True)
    search = st.text_input("Find a project", placeholder="Customer or project name", key="virtual_project_search")
    if search:
        q = search.lower()
        projects = [p for p in projects if q in f"{p['customer']} {p['project']}".lower()]
    if not projects:
        st.info("No matching virtual projects yet.")
    for p in projects:
        render_virtual_project(p)


page = current_page()

if page == "home":
    home_header()
    live_pcna_banner()
    st.markdown('<div class="home-section-title">What do you need?</div><div class="home-title-underline"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="home-action-grid">
<a class="home-action-card" href="{nav_link('spec')}">
  <div class="home-card-icon">✓</div><div class="home-card-title">Spec Sample<br>Order</div>
  <div class="home-card-copy">Tell Nova what you need and build the verified PCNA order.</div>
  <div class="home-card-visual visual-bag" aria-hidden="true"></div><div class="home-arrow">→</div>
</a>
<a class="home-action-card" href="{nav_link('virtual')}">
  <div class="home-card-icon">◇</div><div class="home-card-title">Virtuals /<br>Designs</div>
  <div class="home-card-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div>
  <div class="home-card-visual visual-laptop" aria-hidden="true"></div><div class="home-arrow">→</div>
</a>
<a class="home-action-card" href="{nav_link('quote')}">
  <div class="home-card-icon">$</div><div class="home-card-title">Quote<br>Request</div>
  <div class="home-card-copy">Quote a verified PCNA product at the requested quantity.</div>
  <div class="home-card-visual visual-quote" aria-hidden="true"></div><div class="home-arrow">→</div>
</a>
<a class="home-action-card" href="{virtual_projects_link()}">
  <div class="home-card-icon">□</div><div class="home-card-title">Projects</div>
  <div class="home-card-copy">View and manage your saved projects, orders and virtuals in one place.</div>
  <div class="home-card-visual visual-project" aria-hidden="true"></div><div class="home-arrow">→</div>
</a>
</div>
""",
        unsafe_allow_html=True,
    )

elif page == "create":
    page_header("Create", "Choose a workflow", "Four workflows. Everything else stays inside them.")
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('spec')}"><div class="action-title">Spec Sample Order</div><div class="action-copy">Plain-English request → verified order.</div></a>
<a class="action-card" href="{nav_link('blank')}"><div class="action-title">Blank Sample Order</div><div class="action-copy">Verified blank sample request.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-title">Quote Request</div><div class="action-copy">Decorated PCNA pricing by quantity.</div></a>
<a class="action-card" href="{nav_link('virtual')}"><div class="action-title">Virtuals / Design</div><div class="action-copy">Product, kit and packaging creative projects.</div></a>
</div>
""",
        unsafe_allow_html=True,
    )

elif page == "search":
    page_header("Verified Catalog", "Find a product", "Search the active PCNA catalog.")
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

elif page == "spec":
    page_header("Orders", "Spec Sample Order", "Tell Nova the request in plain English. Product and decoration facts are resolved from verified PCNA data before the order is built.")
    natural = st.text_area("Tell Nova what you need", placeholder="Make me a spec sample order with the Dade Polo in black, medium, embroidery left chest, white imprint.", height=150)
    customer = st.text_input("Customer / Project", placeholder="Optional")
    if not api_key():
        st.info("Add OPENAI_API_KEY in Streamlit Secrets to enable Nova requests.")
    if st.button("Build with Nova", type="primary", use_container_width=True, disabled=not natural.strip() or not api_key()):
        try:
            result = resolve_spec_request(api_key(), natural, st.session_state.products, st.session_state.decorations)
            if result["unresolved"]:
                st.warning("Nova could not confidently verify: " + ", ".join(result["unresolved"]))
            if result["order"]:
                save_project("Spec Sample Order", customer, customer, {"order": result["order"], "request": natural, "resolution": "PCNA-trained Nova"})
                st.session_state.last_spec = result["order"]
                st.success("Verified spec sample built and saved.")
        except Exception as exc:
            st.error(f"Nova could not complete the request: {exc}")
    if st.session_state.get("last_spec"):
        st.markdown(f'<div class="order-box">{st.session_state.last_spec}</div>', unsafe_allow_html=True)
        st.download_button("Download Order", st.session_state.last_spec, file_name="PCNA_Spec_Sample_Order.txt", use_container_width=True)
    with st.expander("Manual build"):
        po = st.text_input("PO#")
        ship_date = st.text_input("Ship Date")
        in_hands = st.text_input("In Hands Date")
        ship_to = st.text_area("Ship To")
        configured = []
        for i in range(st.session_state.spec_item_count):
            cfg = product_configuration(f"spec_{i}")
            if cfg:
                configured.append(cfg)
        if st.button("＋ Add another item", use_container_width=True, disabled=st.session_state.spec_item_count >= 8):
            st.session_state.spec_item_count += 1
            st.rerun()
        if st.button("Build Manual Spec Sample", use_container_width=True, disabled=len(configured) != st.session_state.spec_item_count):
            items = [SpecItem(product=x["Product Name"], item_number=x["Item Number"], color=x["Color"], size=x["Size"], decoration_method=x["Decoration Method"], decoration_location=x["Decoration Location"], imprint_color="N/A" if is_no_ink_decoration(x["Decoration Method"]) else x["Imprint Color"], imprint_size="Max Imprint") for x in configured]
            order = build_spec_order(items, po=po, ship_date=ship_date, in_hands_date=in_hands, ship_to=ship_to)
            save_project("Spec Sample Order", customer, customer, {"order": order})
            st.session_state.last_spec = order

elif page == "blank":
    page_header("Orders", "Blank Sample Order", "Create a clean blank sample request from a verified PCNA item and color.")
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
    page_header("Pricing", "Quote Request", "Quote a verified PCNA product at the requested decorated quantity.")
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
    view = st.query_params.get("view", "new")
    page_header("Creative", "Virtuals / Design", "Tell Nova what you want created. Product, kit and Perfectly Packaged requests all start here and save back into Projects.")
    c1, c2 = st.columns(2)
    if c1.button("New Request", use_container_width=True, type="primary" if view != "projects" else "secondary"):
        st.query_params["view"] = "new"
        st.rerun()
    if c2.button("Projects", use_container_width=True, type="primary" if view == "projects" else "secondary"):
        st.query_params["view"] = "projects"
        st.rerun()

    if view == "projects":
        render_virtual_projects()
    else:
        project_name = st.text_input("Project name", placeholder="Ford Motors New Hire Kit")
        request = st.text_area("What would you like Nova to create?", placeholder="Create five virtuals for a Ford Motors new-hire kit. Choose appropriate PCNA products, use the uploaded Ford artwork, and use Perfectly Packaged for the kit presentation.", height=170)
        artwork = st.file_uploader("Artwork / reference files", accept_multiple_files=True, type=["png", "jpg", "jpeg", "webp", "pdf", "svg", "eps", "ai"])
        if not api_key():
            st.info("Add OPENAI_API_KEY in Streamlit Secrets to enable Nova generation.")
        if st.button("Submit to Nova", type="primary", use_container_width=True, disabled=not request.strip() or not api_key()):
            try:
                context = build_creative_pcna_context(api_key(), request, st.session_state.products, st.session_state.decorations)
                selected_products = context.get("selected_products", [])
                if not selected_products:
                    st.error("Nova could not confidently resolve verified PCNA products for this request. Add a little more product direction and submit again.")
                else:
                    intent = context.get("intent", {})
                    customer = str(intent.get("customer", "")).strip() or "Unassigned"
                    resolved_project_name = project_name.strip() or str(intent.get("project_name", "")).strip() or str(intent.get("project_goal", "")).strip() or "Virtual Project"
                    count = context.get("requested_concepts", 5)
                    payload = {
                        "Request": request,
                        "Artwork": [f.name for f in artwork],
                        "Requested Concepts": count,
                        "Verified Products": selected_products,
                        "Perfectly Packaged": context.get("perfectly_packaged", False),
                        "Generation": "PCNA-trained Nova",
                    }
                    project_id = save_project("Virtual / Design", customer, resolved_project_name, payload, artwork)
                    prompt = creative_generation_prompt(request, context)
                    progress = st.progress(0, text=f"Nova is creating 0 of {count}...")
                    for i in range(count):
                        progress.progress(i / count, text=f"Nova is creating {i+1} of {count}...")
                        new_image = generate_concepts(api_key=api_key(), prompt=prompt, uploads=artwork, count=1)[0]
                        save_upload(project_id, f"generated_{i+1:02d}.png", new_image)
                    progress.progress(1.0, text=f"Nova completed {count} of {count}.")
                    st.success(f"{count} virtuals generated and saved to {resolved_project_name}.")
                    st.session_state.last_generated_project = project_id
            except Exception as exc:
                st.error(f"Nova could not complete the project: {exc}")
        if st.session_state.get("last_generated_project"):
            recent = next((p for p in persistent_projects() if p["id"] == st.session_state.last_generated_project), None)
            if recent:
                st.markdown('<div class="section-title">Completed Project</div>', unsafe_allow_html=True)
                render_virtual_project(recent, expanded=True)

elif page == "saved":
    page_header("Workspace", "Saved Work", "All saved PCNA workflow records.")
    projects = persistent_projects()
    if not projects:
        st.info("No saved projects yet.")
    for project in projects:
        if project.get("type") in {"Virtual / Design", "Virtual Request", "Perfectly Packaged"}:
            render_virtual_project(project)
            continue
        with st.expander(f"{project['customer']} · {project['project']}"):
            st.caption(f"{project['type']} · {project['date'][:10]}")
            payload = project["payload"]
            if "order" in payload:
                st.markdown(f'<div class="order-box">{payload["order"]}</div>', unsafe_allow_html=True)
            else:
                st.json(payload)
    if projects:
        st.download_button("Export All Projects", export_projects(), file_name="PCNA_Assistant_Projects.json", mime="application/json", use_container_width=True)

elif page == "assistant":
    page_header("AI Workspace", "Ask PCNA Nova", "Natural-language help grounded in verified PCNA data.")
    key = api_key()
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ask for a product, spec sample, virtual, kit concept, or PCNA workflow...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        if not key:
            reply = "Add OPENAI_API_KEY in Streamlit Secrets to enable PCNA Nova."
        else:
            try:
                if "spec" in prompt.lower() and "sample" in prompt.lower():
                    result = resolve_spec_request(key, prompt, st.session_state.products, st.session_state.decorations)
                    reply = result["order"] or "I could not confidently resolve the requested PCNA products/decorations."
                    if result["unresolved"]:
                        reply += "\n\nUnresolved: " + ", ".join(result["unresolved"])
                else:
                    context = build_creative_pcna_context(key, prompt, st.session_state.products, st.session_state.decorations)
                    from openai import OpenAI
                    client = OpenAI(api_key=key)
                    response = client.responses.create(
                        model="gpt-5",
                        instructions=PCNA_WORKFLOW_RULES + "\nAnswer concisely. For PCNA facts, use only VERIFIED PCNA CONTEXT supplied in the request.",
                        input=f"USER REQUEST:\n{prompt}\n\nVERIFIED PCNA CONTEXT:\n{json.dumps(context, ensure_ascii=False)}",
                    )
                    reply = response.output_text
            except Exception as exc:
                reply = f"PCNA Nova could not complete the request: {exc}"
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

elif page in {"package", "concept"}:
    st.query_params["page"] = "virtual"
    st.query_params["view"] = "new"
    st.rerun()

else:
    st.query_params["page"] = "home"
    st.rerun()

bottom_nav(page)

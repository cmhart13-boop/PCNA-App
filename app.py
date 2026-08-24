from __future__ import annotations

import base64
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
    resolve_quote_request,
    resolve_spec_request,
)
from starter_data import verified_starter_data
from storage import (
    create_project,
    delete_project,
    export_projects,
    get_or_create_project,
    get_project,
    list_artifacts,
    list_project_files,
    list_projects,
    save_artifact,
    save_upload,
)

st.set_page_config(page_title="PCNA", layout="centered", initial_sidebar_state="collapsed")

PCNA_BLUE = "#084f86"
INK = "#14273a"
MUTED = "#66798a"
LINE = "#d6e2eb"
PANEL = "#f7fafc"
NAV_BLUE = "#003b5c"
PCNA_HERO_URL = "https://assets.pcna.com/image/upload/ar_16:7,c_fill,g_north,pg_1,q_auto,f_jpg/Mkt_Dept/2026%20Jobs/2026-0817_Web_Messaging/0817_Web_PCNA_Hero_m.jpg"

st.markdown(
    f"""
<style>
:root {{
  --pcna:{PCNA_BLUE}; --ink:{INK}; --muted:{MUTED}; --line:{LINE}; --panel:{PANEL};
  --nav-blue:{NAV_BLUE}; --nav-height:76px; --page-max:620px; --page-side:12px; --home-gap:10px;
}}
*{{box-sizing:border-box}}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{{background:#fff;color:var(--ink);width:100%;margin:0;padding:0;overflow-x:hidden}}
[data-testid="stAppViewContainer"]>.main{{width:100%;overflow-x:hidden}}
[data-testid="stHeader"]{{height:0!important;min-height:0!important;background:transparent!important}}
[data-testid="stSidebar"]{{display:none!important}}
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stStatusWidget"],[data-testid="stAppDeployButton"],[data-testid="stDeployButton"],
[class*="viewerBadge"],[class*="ViewerBadge"],a[href*="streamlit.io/cloud"]{{display:none!important;visibility:hidden!important;height:0!important}}
.block-container,[data-testid="stMainBlockContainer"],[data-testid="stAppViewBlockContainer"]{{width:100%!important;max-width:var(--page-max)!important;box-sizing:border-box!important;margin:0 auto!important;padding:calc(16px + env(safe-area-inset-top)) 15px calc(96px + env(safe-area-inset-bottom))!important}}
.block-container>[data-testid="stVerticalBlock"]{{gap:0!important}}
[data-testid="stElementContainer"]{{margin:0}}
.page-kicker{{font-size:11px;font-weight:900;letter-spacing:.10em;color:var(--pcna);text-transform:uppercase;margin-top:2px}}
.page-title{{font-size:29px;line-height:1.08;font-weight:850;letter-spacing:-.035em;color:var(--pcna);margin:4px 0 9px}}
.page-copy{{font-size:15px;line-height:1.48;color:var(--muted);margin:0 0 18px}}
.section-title{{font-size:18px;line-height:1.1;font-weight:850;letter-spacing:-.015em;margin:8px 0 6px;color:var(--pcna)}}
.action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:5px 0 8px}}
.action-card{{display:block;text-decoration:none!important;border:1.5px solid rgba(8,79,134,.36);border-radius:16px;padding:12px 13px;background:#fff;min-height:96px;box-shadow:0 4px 0 rgba(8,79,134,.10),0 9px 18px rgba(8,79,134,.08)}}
.action-title{{font-size:15px;font-weight:850;color:var(--pcna);line-height:1.12;margin-bottom:4px}}
.action-copy{{font-size:11px;color:var(--muted);line-height:1.25}}
.info-card{{border:1px solid var(--line);border-radius:16px;padding:14px;background:#fff;margin:8px 0;box-shadow:0 4px 14px rgba(8,79,134,.05)}}
.info-card-title{{font-size:15px;font-weight:850;color:var(--pcna)}} .info-card-meta{{font-size:12px;color:var(--muted);margin-top:3px}}
.data-chip{{display:inline-block;padding:5px 8px;border-radius:999px;background:#eef5fa;color:var(--pcna);font-size:11px;font-weight:850;margin-right:5px}}
.order-box{{white-space:pre-wrap;border:1px solid var(--line);background:#fbfcfd;border-radius:15px;padding:14px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;line-height:1.5;overflow-wrap:anywhere}}
.stButton>button,.stDownloadButton>button,[data-testid="stLinkButton"] a{{min-height:48px!important;border-radius:13px!important;font-weight:800!important;font-size:15px!important;width:100%!important}}
.stTextInput input,.stNumberInput input,.stTextArea textarea,[data-baseweb="select"]>div{{min-height:50px!important;border-radius:12px!important;font-size:16px!important;background:#fff!important;border-color:#b8cad8!important;color:var(--ink)!important}}
.stTextArea textarea{{min-height:120px!important}}
[data-testid="stFileUploaderDropzone"]{{border-radius:14px!important;padding:14px 10px!important;border-color:#b8cad8!important;background:#fbfdff!important}}
[data-testid="stExpander"]{{border:1px solid var(--line)!important;border-radius:14px!important;overflow:hidden;margin:8px 0}}
label,[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p{{font-weight:800!important;color:var(--pcna)!important}}
.bottom-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:0;width:min(var(--page-max),100%);height:var(--nav-height);background:var(--nav-blue);border-top:1px solid rgba(255,255,255,.10);display:grid;grid-template-columns:repeat(5,1fr);z-index:9999;padding:7px 7px max(7px,env(safe-area-inset-bottom));box-sizing:border-box}}
.nav-item{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;color:rgba(255,255,255,.62)!important;font-size:12.5px;font-weight:800;gap:3px;border-radius:12px}}
.nav-icon{{font-size:20px;line-height:1}} .nav-item.active{{color:rgba(255,255,255,.96)!important;background:rgba(255,255,255,.08)}}
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


def projects_link() -> str:
    return "?page=projects"


def page_header(kicker: str, title: str, copy: str):
    st.markdown(f'<div class="page-kicker">{kicker}</div><div class="page-title">{title}</div><div class="page-copy">{copy}</div>', unsafe_allow_html=True)


def approved_pcna_header(width: int = 158):
    st.image("IMG_2337.webp", width=width)


def bottom_nav(page: str):
    group = page
    st.markdown(
        f"""
<div class="bottom-nav">
<a class="nav-item {'active' if group=='home' else ''}" href="{nav_link('home')}"><span class="nav-icon">⌂</span><span>Home</span></a>
<a class="nav-item {'active' if group=='spec' else ''}" href="{nav_link('spec')}"><span class="nav-icon">✓</span><span>Specs</span></a>
<a class="nav-item {'active' if group=='search' else ''}" href="{nav_link('search')}"><span class="nav-icon">⌕</span><span>Products</span></a>
<a class="nav-item {'active' if group=='virtual' else ''}" href="{nav_link('virtual')}"><span class="nav-icon">◇</span><span>Virtuals</span></a>
<a class="nav-item {'active' if group=='quote' else ''}" href="{nav_link('quote')}"><span class="nav-icon">$</span><span>Quotes</span></a>
</div>
""",
        unsafe_allow_html=True,
    )


def asset_data(path_name: str) -> str:
    path = Path(path_name)
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime = "image/webp" if suffix == ".webp" else "image/png" if suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def render_streamlit_mobile_home():
    # Direct rendering only. No runtime interception, no iframe crop, no hidden duplicate hero content.
    logo = asset_data("IMG_2337.webp")
    st.markdown(
        f'''
<div class="pcna-home">
  <div class="pcna-head">
    <a href="https://www.pcna.com/en-us" target="_blank" rel="noopener noreferrer" aria-label="Open PCNA.com">
      <img src="{logo}" class="pcna-head-logo" alt="PCNA">
    </a>
  </div>
  <a class="pcna-hero" href="https://www.pcna.com/en-us" target="_blank" rel="noopener noreferrer" aria-label="Open PCNA.com">
    <img src="{PCNA_HERO_URL}" class="pcna-hero-img" alt="PCNA lifestyle banner">
  </a>
  <div class="pcna-section-title">What do you need?<span></span></div>
  <div class="pcna-grid">
    <a class="pcna-card" href="?page=spec"><div class="pcna-card-icon">✓</div><div class="pcna-card-title">Spec Sample<br>Order</div><div class="pcna-card-sub">Tell Nova what you need and build the verified PCNA order.</div><div class="card-art backpack" aria-hidden="true"><div></div></div><div class="pcna-arrow">→</div></a>
    <a class="pcna-card" href="?page=virtual"><div class="pcna-card-icon">◇</div><div class="pcna-card-title">Virtuals /<br>Designs</div><div class="pcna-card-sub">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div><div class="card-art laptop" aria-hidden="true"><div class="screen">NORTHPOINT<br><small>SOLUTIONS</small></div></div><div class="pcna-arrow">→</div></a>
    <a class="pcna-card" href="?page=quote"><div class="pcna-card-icon">$</div><div class="pcna-card-title">Quote<br>Request</div><div class="pcna-card-sub">Quote a verified PCNA product at the requested quantity.</div><div class="card-art quote-sheet" aria-hidden="true"><div class="qline"></div><div class="qline short"></div><div class="qbars"></div></div><div class="pcna-arrow">→</div></a>
    <a class="pcna-card" href="?page=projects"><div class="pcna-card-icon">□</div><div class="pcna-card-title">Projects</div><div class="pcna-card-sub">View and manage your saved projects, orders and virtuals in one place.</div><div class="card-art notebook" aria-hidden="true"><div class="elastic"></div></div><div class="pcna-arrow">→</div></a>
  </div>
</div>
<nav class="pcna-mobile-nav">
  <a class="active" href="?page=home"><b>⌂</b><span>Home</span></a><a href="?page=spec"><b>✓</b><span>Specs</span></a><a href="?page=search"><b>⌕</b><span>Products</span></a><a href="?page=virtual"><b>◇</b><span>Virtuals</span></a><a href="?page=quote"><b>$</b><span>Quotes</span></a>
</nav>
<style>
:root{{--pcna-navy:#063f80;--pcna-blue:#075ca8;--cyan:#27afe2}}
[data-testid="stAppViewContainer"]>.main{{overflow-y:auto!important}}
.block-container:has(.pcna-home){{max-width:620px!important;padding:calc(4px + env(safe-area-inset-top)) 12px calc(78px + env(safe-area-inset-bottom))!important}}
.block-container:has(.pcna-home)>[data-testid="stVerticalBlock"]{{gap:0!important}}
.block-container:has(.pcna-home) [data-testid="stElementContainer"]{{margin:0!important}}
.pcna-home{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color:#082f66}}
.pcna-head{{height:64px;display:flex;align-items:center;justify-content:flex-start;margin:0 0 6px;overflow:visible;padding-left:2px}}
.pcna-head a{{display:inline-flex;align-items:center;text-decoration:none!important}}
.pcna-head-logo{{display:block;height:60px;max-width:235px;width:auto;object-fit:contain}}
.pcna-hero{{position:relative;display:block;width:100%;height:188px;border-radius:17px;overflow:hidden;text-decoration:none!important;background:#063f80;box-shadow:0 5px 18px rgba(8,65,120,.18)}}
.pcna-hero-img{{position:absolute;inset:0;display:block;width:100%!important;height:100%!important;max-width:none!important;object-fit:cover!important;object-position:center top!important;margin:0!important;padding:0!important}}
.pcna-section-title{{font-size:clamp(25px,6.4vw,35px);font-weight:900;line-height:1;color:#082f66;margin:12px 0 10px;letter-spacing:-.03em}}
.pcna-section-title span{{display:block;width:62px;height:4px;border-radius:99px;background:var(--cyan);margin-top:7px}}
.pcna-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(2,210px);gap:10px}}
.pcna-card{{position:relative;overflow:hidden;border:1px solid #cfe0ef;border-radius:17px;background:white;box-shadow:0 4px 16px rgba(9,75,135,.15);text-decoration:none!important;color:#082f66;padding:13px 12px}}
.pcna-card-icon{{width:40px;height:40px;border-radius:50%;background:#075ba7;color:white;display:flex;align-items:center;justify-content:center;font-size:25px;font-weight:800;position:relative;z-index:4}}
.pcna-card-title{{font-size:clamp(20px,5.2vw,27px);font-weight:900;line-height:1;letter-spacing:-.03em;margin:9px 0 8px;position:relative;z-index:4;max-width:58%}}
.pcna-card-sub{{font-size:clamp(10px,2.65vw,14px);line-height:1.25;color:#29496c;max-width:56%;position:relative;z-index:4}}
.pcna-arrow{{position:absolute;right:10px;bottom:10px;width:40px;height:40px;border-radius:50%;background:#075aa7;color:white;display:flex;align-items:center;justify-content:center;font-size:27px;font-weight:800;z-index:5}}
.card-art{{position:absolute;right:0;bottom:0;width:57%;height:83%;z-index:2}}
.backpack{{right:-2%;bottom:-2%}} .backpack>div{{position:absolute;right:8%;bottom:0;width:72%;height:92%;border-radius:20px 20px 10px 10px;background:linear-gradient(145deg,#0d4b91,#062f66);box-shadow:inset -8px 0 14px rgba(0,0,0,.18)}}
.backpack>div:before{{content:"";position:absolute;left:20%;right:20%;top:-8%;height:17%;border:5px solid #0b3b76;border-bottom:0;border-radius:18px 18px 0 0}} .backpack>div:after{{content:"";position:absolute;left:14%;right:14%;top:34%;height:37%;border:2px solid rgba(255,255,255,.15);border-radius:10px}}
.laptop{{right:-1%;bottom:5%;height:70%}} .laptop:before{{content:"";position:absolute;right:5%;bottom:16%;width:88%;height:64%;border:7px solid #1f2831;border-radius:6px;background:#162130;box-sizing:border-box}} .laptop:after{{content:"";position:absolute;right:-2%;bottom:7%;width:100%;height:9%;background:#9ca5ad;transform:skewX(-10deg);border-radius:2px}}
.laptop .screen{{position:absolute;right:15%;bottom:34%;width:66%;text-align:center;color:white;font-weight:800;font-size:9px;z-index:3}} .laptop small{{font-size:5px;letter-spacing:.12em}}
.quote-sheet{{right:3%;bottom:5%;width:49%;height:78%;background:#f6f8fb;border:6px solid #30363d;border-radius:9px;transform:rotate(3deg);box-shadow:0 5px 12px rgba(0,0,0,.15)}} .quote-sheet:before{{content:"QUOTE SUMMARY";position:absolute;top:8%;left:10%;font-size:7px;font-weight:900;color:#26394f}}
.qline{{position:absolute;left:10%;right:10%;top:28%;height:3px;background:#b9c9d8;box-shadow:0 14px 0 #b9c9d8,0 28px 0 #b9c9d8,0 42px 0 #b9c9d8}} .qline.short{{right:35%;top:35%}} .qbars{{position:absolute;left:13%;bottom:10%;width:55%;height:24%;background:linear-gradient(to right,transparent 0 8%,#5f86ad 8% 18%,transparent 18% 28%,#5f86ad 28% 43%,transparent 43% 54%,#5f86ad 54% 70%,transparent 70% 79%,#5f86ad 79% 94%)}}
.notebook{{right:5%;bottom:3%;width:48%;height:80%;border-radius:8px;background:linear-gradient(145deg,#3a3d40,#181a1c);transform:rotate(7deg);box-shadow:0 5px 12px rgba(0,0,0,.2)}} .notebook:before{{content:"P";position:absolute;left:43%;top:40%;font-size:28px;color:#24272a;font-weight:900;text-shadow:0 1px 0 #555}} .notebook .elastic{{position:absolute;right:13%;top:0;bottom:0;width:7%;background:#08090a}}
.pcna-mobile-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:0;width:min(620px,100%);height:calc(68px + env(safe-area-inset-bottom));padding:4px 8px env(safe-area-inset-bottom);box-sizing:border-box;border-radius:30px 30px 0 0;background:linear-gradient(90deg,#075ca8,#00326d);display:grid;grid-template-columns:repeat(5,1fr);z-index:99999}}
.pcna-mobile-nav a{{display:flex;flex-direction:column;align-items:center;justify-content:center;color:rgba(255,255,255,.82)!important;text-decoration:none!important;font-size:12.5px;font-weight:700;gap:2px}} .pcna-mobile-nav b{{font-size:24px;line-height:1}} .pcna-mobile-nav .active{{color:white!important;font-weight:900}}
@media(max-width:430px){{.block-container:has(.pcna-home){{padding-left:10px!important;padding-right:10px!important;padding-top:calc(2px + env(safe-area-inset-top))!important}} .pcna-head{{height:62px;margin-bottom:5px}} .pcna-head-logo{{height:58px}} .pcna-hero{{height:176px}} .pcna-grid{{grid-template-rows:repeat(2,198px);gap:9px}} .pcna-card{{padding:11px 10px}} .pcna-card-icon{{width:36px;height:36px;font-size:22px}}}}
@media(max-height:760px){{.pcna-head{{height:58px}} .pcna-head-logo{{height:54px}} .pcna-hero{{height:154px}} .pcna-section-title{{font-size:24px;margin:8px 0 7px}} .pcna-grid{{grid-template-rows:repeat(2,170px);gap:7px}} .pcna-card-title{{font-size:18px;margin:6px 0 5px}} .pcna-card-sub{{font-size:9.5px}} .pcna-card-icon{{width:32px;height:32px;font-size:20px}}}}
</style>
''', unsafe_allow_html=True)


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


def project_selector(prefix: str, suggested_name: str = "") -> tuple[str, str, int | None]:
    projects = list_projects()
    options = ["＋ New Project"] + [p["project"] for p in projects]
    selected = st.selectbox("Project", options, key=f"{prefix}_project_choice")
    if selected == "＋ New Project":
        name = st.text_input("Project", value=suggested_name, key=f"{prefix}_project_name", placeholder="Ford Employee Kit")
        return name.strip(), "Unassigned", None
    project = projects[options.index(selected) - 1]
    return project["project"], project.get("customer") or "Unassigned", int(project["id"])


def ensure_project(name: str, customer: str, existing_id: int | None = None) -> int:
    if existing_id:
        return int(existing_id)
    return get_or_create_project(name or "Untitled Project", customer or "Unassigned")


def copy_button(text: str, key: str):
    safe = json.dumps(text)
    components.html(f"""<button id="copy-{key}" style="width:100%;min-height:44px;border:1px solid #b8cad8;border-radius:12px;background:white;color:#084f86;font-weight:800;font-size:14px;">Copy</button><script>document.getElementById('copy-{key}').onclick=async()=>{{await navigator.clipboard.writeText({safe});document.getElementById('copy-{key}').innerText='Copied';}};</script>""", height=52)


def quote_products(products: list[dict]) -> tuple[list[dict], float]:
    lines, total = [], 0.0
    for product in products:
        item = str(product.get("Item Number", ""))
        quantity = int(product.get("Quantity") or 0)
        schedules = pricing_schedules(st.session_state.pricing, item, currency="USD", decorated=True)
        if not schedules or quantity <= 0:
            lines.append({**product, "Pricing Available": False})
            continue
        tier = quote_tier(st.session_state.pricing, item, quantity, currency="USD", decorated=True, schedule=schedules[0])
        if not tier:
            lines.append({**product, "Pricing Available": False})
            continue
        extended = float(tier["Unit Price"]) * quantity
        total += extended
        lines.append({**product, **tier, "Extended": extended, "Pricing Available": True})
    return lines, total


def quote_text(project_name: str, quote_lines: list[dict], total: float) -> str:
    out = ["PCNA QUOTE", "", f"Project: {project_name}", ""]
    for i, line in enumerate(quote_lines, 1):
        out.extend([f"ITEM {i}", f"Product: {line.get('Product Name','')}", f"Item Number: {line.get('Item Number','')}", f"Quantity: {line.get('Quantity','')}", f"Color: {line.get('Color','')}", f"Size: {line.get('Size','')}", f"Decoration Method: {line.get('Decoration Method','')}", f"Decoration Location: {line.get('Decoration Location','')}"])
        if line.get("Pricing Available"):
            out.extend([f"Unit Price: ${float(line.get('Unit Price',0)):,.2f}", f"Extended: ${float(line.get('Extended',0)):,.2f}", f"Schedule: {line.get('Schedule','')}"])
        else:
            out.append("Pricing: Could not be verified from active decorated pricing data")
        out.append("")
    if total:
        out.append(f"TOTAL: ${total:,.2f}")
    return "\n".join(out)


def render_products(products: list[dict]):
    for i, product in enumerate(products, 1):
        st.markdown(f"**{i}. {product.get('Product Name','')}**")
        st.write(f"Item Number: {product.get('Item Number','')}")
        st.write(f"Color: {product.get('Color','')}")
        if product.get("Size"):
            st.write(f"Size: {product.get('Size')}")
        st.write(f"Decoration Method: {product.get('Decoration Method','')}")
        st.write(f"Decoration Location: {product.get('Decoration Location','')}")
        if product.get("Imprint Color"):
            st.write(f"Imprint Color: {product.get('Imprint Color')}")
        if product.get("Max Imprint"):
            st.write(f"Max Imprint: {product.get('Max Imprint')}")
        if product.get("Quantity"):
            st.write(f"Quantity: {product.get('Quantity')}")
        if i < len(products):
            st.divider()


def render_project(project: dict, expanded: bool = False):
    artifacts = list_artifacts(project["id"])
    files = list_project_files(project["id"])
    with st.expander(project["project"], expanded=expanded):
        st.caption(f"Updated {project['updated_at'][:10]} · {project.get('virtual_count',0)} virtuals · {project.get('quote_count',0)} quotes · {project.get('spec_count',0)} spec samples")
        grouped = {"virtual": ("Virtuals / Designs", []), "quote": ("Quotes", []), "spec_sample": ("Spec Sample Orders", [])}
        for artifact in artifacts:
            if artifact["artifact_type"] in grouped:
                grouped[artifact["artifact_type"]][1].append(artifact)
        for kind in ("virtual", "quote", "spec_sample"):
            title, items = grouped[kind]
            if not items:
                continue
            st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
            for artifact in items:
                with st.expander(artifact["title"]):
                    data = artifact.get("structured_data", {})
                    if artifact.get("original_prompt"):
                        st.caption("Original request")
                        st.write(artifact["original_prompt"])
                    if kind == "virtual":
                        products = data.get("Verified Products", []) or data.get("products", [])
                        render_products(products)
                        for image in [f for f in files if f.name.startswith(f"virtual_{artifact['id']}_")]:
                            st.image(image.read_bytes(), use_container_width=True)
                            st.download_button("Download Virtual", image.read_bytes(), file_name=image.name, key=f"pimg_{project['id']}_{artifact['id']}_{image.name}", use_container_width=True)
                    elif artifact.get("ai_output"):
                        st.markdown(f'<div class="order-box">{artifact["ai_output"]}</div>', unsafe_allow_html=True)
                        copy_button(artifact["ai_output"], f"artifact-{artifact['id']}")
                    else:
                        st.json(data)
        if st.button("Delete Project", key=f"delete_project_{project['id']}", use_container_width=True):
            delete_project(project["id"])
            st.rerun()


def inline_quote_from_spec(pending: dict, project_name: str, customer: str, project_id: int | None):
    products = pending.get("products", []) or []
    with st.expander("＋ Add Quote", expanded=False):
        if not products:
            st.warning("A quote can only be added after the products are verified.")
            return
        loaded = []
        for i, product in enumerate(products):
            qty = int(st.number_input(f"Quantity · {product.get('Product Name','Item')}", min_value=1, value=int(product.get("Quantity") or 100), step=1, key=f"spec_quote_qty_{i}"))
            loaded.append({**product, "Quantity": qty})
        if st.button("Generate Quote", key="spec_generate_quote", type="primary", use_container_width=True):
            lines, total = quote_products(loaded)
            text = quote_text(project_name or "Spec Project", lines, total)
            st.session_state.spec_inline_quote = {"lines": lines, "text": text, "total": total}
        inline = st.session_state.get("spec_inline_quote")
        if inline:
            st.markdown(f'<div class="order-box">{inline["text"]}</div>', unsafe_allow_html=True)
            if st.button("＋ Add Quote to Project", key="spec_save_quote", use_container_width=True, disabled=not project_name.strip()):
                pid = ensure_project(project_name, customer, project_id)
                save_artifact(pid, "quote", "Quote", original_prompt=pending.get("request", "Spec Sample Order"), ai_output=inline["text"], structured_data={"products": inline.get("lines", []), "source": "spec_sample"})
                st.success("Quote added to Project.")


def inline_virtual_from_spec(pending: dict, project_name: str, customer: str, project_id: int | None):
    products = pending.get("products", []) or []
    with st.expander("＋ Add Virtuals", expanded=False):
        if not products:
            st.warning("Virtuals can only be added after the products are verified.")
            return
        direction = st.text_area("Virtual direction", key="spec_virtual_direction", placeholder="Show the Dade Polo with the customer logo on left chest...", height=100)
        artwork = st.file_uploader("Artwork / reference files", key="spec_virtual_art", accept_multiple_files=True, type=["png", "jpg", "jpeg", "webp", "pdf", "svg", "eps", "ai"])
        count = int(st.number_input("Number of virtuals", min_value=1, max_value=5, value=1, step=1, key="spec_virtual_count"))
        if st.button("Generate Virtuals", key="spec_generate_virtuals", type="primary", use_container_width=True, disabled=not direction.strip() or not api_key() or not project_name.strip()):
            pid = ensure_project(project_name, customer, project_id)
            payload = {"Request": direction, "Artwork": [f.name for f in artwork], "Requested Concepts": count, "Verified Products": products, "Generation": "PCNA-trained Nova", "Source": "spec_sample"}
            artifact_id = save_artifact(pid, "virtual", "Virtual / Design", original_prompt=direction, structured_data=payload)
            for upload in artwork:
                save_upload(pid, f"source_{artifact_id}_{upload.name}", upload.getvalue())
            context = {"selected_products": products, "verified_products": products, "perfectly_packaged": False, "requested_concepts": count}
            prompt = creative_generation_prompt(direction, context)
            progress = st.progress(0, text=f"Nova is creating 0 of {count}...")
            for i in range(count):
                progress.progress(i / count, text=f"Nova is creating {i+1} of {count}...")
                image = generate_concepts(api_key=api_key(), prompt=prompt, uploads=artwork, count=1)[0]
                save_upload(pid, f"virtual_{artifact_id}_{i+1:02d}.png", image)
            progress.progress(1.0, text=f"Nova completed {count} of {count}.")
            st.success(f"{count} virtual{'s' if count != 1 else ''} added to {project_name}.")


page = current_page()
if page != "home":
    approved_pcna_header()

if page == "home":
    render_streamlit_mobile_home()
    st.stop()

elif page == "create":
    page_header("Create", "Choose a workflow", "Three AI creation workflows, with Projects as the shared workspace.")
    st.markdown(f"""<div class="action-grid"><a class="action-card" href="{nav_link('spec')}"><div class="action-title">Spec Sample Order</div><div class="action-copy">Plain-English request → verified order.</div></a><a class="action-card" href="{nav_link('virtual')}"><div class="action-title">Virtuals / Design</div><div class="action-copy">Product, kit and packaging creative projects.</div></a><a class="action-card" href="{nav_link('quote')}"><div class="action-title">Quote Request</div><div class="action-copy">Plain-English request → decorated PCNA quote.</div></a><a class="action-card" href="{projects_link()}"><div class="action-title">Projects</div><div class="action-copy">All saved virtuals, quotes and spec samples together.</div></a></div>""", unsafe_allow_html=True)

elif page == "search":
    page_header("Verified Catalog", "Find a product", "Search the active PCNA catalog.")
    identity = product_picker("search")
    if identity:
        item = identity["Item Number"]
        st.markdown(f'<div class="section-title">{identity["Product Name"]}</div><span class="data-chip">Item {item}</span><span class="data-chip">{identity.get("Brand","") or "PCNA"}</span>', unsafe_allow_html=True)
        with st.expander("Colors", expanded=True):
            st.write(" · ".join(colors_for_item(st.session_state.products, item)) or "No color data available.")
        with st.expander("Decoration options", expanded=True):
            d = decorations_for_item(st.session_state.decorations, item)
            for _, row in d.head(40).iterrows():
                st.markdown(f"**{row['Decoration Method']}**  \n{row['Decoration Location']} · max {imprint_size(row)}")
                st.divider()

elif page == "spec":
    page_header("Orders", "Spec Sample Order", "Tell Nova the request in plain English. Verified product and decoration data are resolved before the order is built.")
    natural = st.text_area("Tell Nova what you need", placeholder="Make me a spec sample order with the Dade Polo in black, medium, embroidery left chest, white imprint.", height=150)
    if not api_key():
        st.info("Add OPENAI_API_KEY in Streamlit Secrets to enable Nova requests.")
    if st.button("Generate Spec Sample", type="primary", use_container_width=True, disabled=not natural.strip() or not api_key()):
        try:
            result = resolve_spec_request(api_key(), natural, st.session_state.products, st.session_state.decorations)
            st.session_state.pending_spec = {"request": natural, **result}
            st.session_state.pop("spec_inline_quote", None)
        except Exception:
            st.error("Nova could not complete the request. Please retry.")
    pending = st.session_state.get("pending_spec")
    if pending:
        if pending.get("unresolved"):
            st.warning("Could not confidently verify: " + ", ".join(pending["unresolved"]))
        if pending.get("order"):
            st.markdown(f'<div class="order-box">{pending["order"]}</div>', unsafe_allow_html=True)
            copy_button(pending["order"], "spec")
            project_name, customer, project_id = project_selector("specsave")
            if st.button("＋ Add to Project", type="primary", use_container_width=True, disabled=not project_name.strip()):
                pid = ensure_project(project_name, customer, project_id)
                save_artifact(pid, "spec_sample", "Spec Sample Order", original_prompt=pending["request"], ai_output=pending["order"], structured_data={"products": pending.get("products", []), "intent": pending.get("intent", {})})
                st.success("Spec sample added to Project.")
            inline_quote_from_spec(pending, project_name, customer, project_id)
            inline_virtual_from_spec(pending, project_name, customer, project_id)
            if st.button("Create New Request", use_container_width=True):
                st.session_state.pop("pending_spec", None)
                st.session_state.pop("spec_inline_quote", None)
                st.rerun()
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
            st.session_state.pending_spec = {"request": "Manual build", "order": build_spec_order(items, po=po, ship_date=ship_date, in_hands_date=in_hands, ship_to=ship_to), "products": configured, "intent": {}, "unresolved": []}
            st.rerun()

elif page == "quote":
    page_header("Pricing", "Quote Request", "Tell Nova what to quote. Product facts are verified first, then decorated pricing is calculated from active PCNA pricing data.")
    natural = st.text_area("Tell Nova what to quote", placeholder="Quote 100 Dade Polos in black with embroidery left chest.", height=150)
    if st.button("Generate Quote", type="primary", use_container_width=True, disabled=not natural.strip() or not api_key()):
        try:
            result = resolve_quote_request(api_key(), natural, st.session_state.products, st.session_state.decorations)
            lines, total = quote_products(result.get("products", []))
            project_name = str(result.get("intent", {}).get("project_name", "")).strip() or "Quote Project"
            st.session_state.pending_quote = {"request": natural, "products": result.get("products", []), "lines": lines, "text": quote_text(project_name, lines, total), "project": project_name, "unresolved": result.get("unresolved", [])}
        except Exception:
            st.error("Nova could not complete the quote request. Please retry.")
    pending = st.session_state.get("pending_quote")
    if pending:
        if pending.get("unresolved"):
            st.warning("Could not confidently verify: " + ", ".join(pending["unresolved"]))
        st.markdown(f'<div class="order-box">{pending["text"]}</div>', unsafe_allow_html=True)
        copy_button(pending["text"], "quote")
        project_name, customer, project_id = project_selector("quotesave", pending.get("project", ""))
        if st.button("＋ Add to Project", type="primary", use_container_width=True, disabled=not project_name.strip()):
            pid = ensure_project(project_name, customer, project_id)
            save_artifact(pid, "quote", "Quote", original_prompt=pending["request"], ai_output=pending["text"], structured_data={"products": pending.get("lines", [])})
            st.success("Quote added to Project.")
        if st.button("Create New Quote", use_container_width=True):
            st.session_state.pop("pending_quote", None)
            st.rerun()

elif page == "virtual":
    page_header("Creative", "Virtuals / Design", "Tell Nova what you want created. Verified products, artwork and design instructions stay attached to the Project.")
    project_name, customer, project_id = project_selector("virtual")
    request = st.text_area("What would you like Nova to create?", placeholder="Create a Ford employee gift concept using a Dade Polo, Stanley Quencher and Pedova Journal.", height=170)
    artwork = st.file_uploader("Artwork / reference files", accept_multiple_files=True, type=["png", "jpg", "jpeg", "webp", "pdf", "svg", "eps", "ai"])
    if st.button("Generate Virtual", type="primary", use_container_width=True, disabled=not request.strip() or not api_key() or not project_name.strip()):
        try:
            context = build_creative_pcna_context(api_key(), request, st.session_state.products, st.session_state.decorations)
            products = context.get("selected_products", [])
            if context.get("unresolved"):
                st.warning("Could not confidently verify: " + ", ".join(context["unresolved"]))
            if not products:
                st.error("Nova could not confidently resolve verified PCNA products for this request.")
            else:
                pid = ensure_project(project_name, customer, project_id)
                count = context.get("requested_concepts", 5)
                payload = {"Request": request, "Artwork": [f.name for f in artwork], "Requested Concepts": count, "Verified Products": products, "Perfectly Packaged": context.get("perfectly_packaged", False), "Generation": "PCNA-trained Nova"}
                artifact_id = save_artifact(pid, "virtual", "Virtual / Design", original_prompt=request, structured_data=payload)
                for upload in artwork:
                    save_upload(pid, f"source_{artifact_id}_{upload.name}", upload.getvalue())
                prompt = creative_generation_prompt(request, context)
                progress = st.progress(0, text=f"Nova is creating 0 of {count}...")
                for i in range(count):
                    progress.progress(i / count, text=f"Nova is creating {i+1} of {count}...")
                    image = generate_concepts(api_key=api_key(), prompt=prompt, uploads=artwork, count=1)[0]
                    save_upload(pid, f"virtual_{artifact_id}_{i+1:02d}.png", image)
                progress.progress(1.0, text=f"Nova completed {count} of {count}.")
                st.session_state.last_virtual = {"project_id": pid, "artifact_id": artifact_id, "project": project_name, "products": products}
                st.success(f"{count} virtuals generated and saved to {project_name}.")
        except Exception:
            st.error("Nova could not complete the virtual request. Please retry.")
    last = st.session_state.get("last_virtual")
    if last:
        render_products(last.get("products", []))
        for f in list_project_files(last["project_id"]):
            if f.name.startswith(f"virtual_{last['artifact_id']}_"):
                st.image(f.read_bytes(), use_container_width=True)

elif page == "projects":
    page_header("Workspace", "Projects", "Virtuals, quotes and spec sample orders stay together by project.")
    projects = list_projects()
    search = st.text_input("Search Projects", placeholder="Project")
    sort = st.selectbox("Sort", ["Recently Modified", "Project Name"])
    if search:
        q = search.lower().strip()
        projects = [p for p in projects if q in p["project"].lower()]
    if sort == "Project Name":
        projects = sorted(projects, key=lambda p: p["project"].lower())
    with st.expander("＋ Create New Project"):
        name = st.text_input("Project", key="new_project_name", placeholder="Ford Employee Kit")
        notes = st.text_area("Notes", key="new_project_notes")
        if st.button("Create Project", type="primary", use_container_width=True, disabled=not name.strip()):
            pid = create_project(name, "Unassigned", notes)
            st.session_state.open_project = pid
            st.rerun()
    if not projects:
        st.info("No matching projects yet.")
    for project in projects:
        render_project(project, expanded=project["id"] == st.session_state.get("open_project"))
    if projects:
        st.download_button("Export All Projects", export_projects(), file_name="PCNA_Assistant_Projects.json", mime="application/json", use_container_width=True)

elif page == "assistant":
    page_header("AI Workspace", "Ask PCNA Nova", "Natural-language help grounded in verified PCNA data.")
    key = api_key()
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ask for a product, spec sample, virtual, kit concept, quote, or PCNA workflow...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        if not key:
            reply = "Add OPENAI_API_KEY in Streamlit Secrets to enable PCNA Nova."
        else:
            try:
                low = prompt.lower()
                if "spec" in low and "sample" in low:
                    reply = resolve_spec_request(key, prompt, st.session_state.products, st.session_state.decorations)["order"]
                elif "quote" in low:
                    result = resolve_quote_request(key, prompt, st.session_state.products, st.session_state.decorations)
                    lines, total = quote_products(result.get("products", []))
                    reply = quote_text("Quote Project", lines, total)
                else:
                    context = build_creative_pcna_context(key, prompt, st.session_state.products, st.session_state.decorations)
                    from openai import OpenAI
                    response = OpenAI(api_key=key).responses.create(model="gpt-5", instructions=PCNA_WORKFLOW_RULES + "\nAnswer concisely. Use only VERIFIED PCNA CONTEXT for PCNA facts.", input=f"USER REQUEST:\n{prompt}\n\nVERIFIED PCNA CONTEXT:\n{json.dumps(context, ensure_ascii=False)}")
                    reply = response.output_text
            except Exception:
                reply = "PCNA Nova could not complete the request. Please retry."
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
            except Exception:
                st.error("Data validation failed. Verify the three PCNA master files and try again.")

elif page in {"package", "concept", "saved"}:
    st.query_params["page"] = "projects" if page == "saved" else "virtual"
    st.rerun()

else:
    st.query_params["page"] = "home"
    st.rerun()

bottom_nav(page)

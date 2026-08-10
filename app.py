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
.section-title{{font-size:18px;font-weight:850;letter-spacing:-.015em;margin:14px 0 7px;color:var(--pcna);}}
.action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:5px 0 8px;}}
.action-card{{display:block;text-decoration:none!important;border:1.5px solid rgba(8,79,134,.36);border-radius:16px;padding:12px 13px;background:#fff;min-height:96px;box-shadow:0 4px 0 rgba(8,79,134,.10),0 9px 18px rgba(8,79,134,.08);transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease;}}
.action-card:hover{{border-color:rgba(8,79,134,.58);box-shadow:0 6px 0 rgba(8,79,134,.13),0 14px 28px rgba(8,79,134,.12);}}
.action-card:active{{transform:translateY(3px);box-shadow:0 2px 0 rgba(8,79,134,.12),0 7px 14px rgba(8,79,134,.08);}}
.action-icon{{font-size:21px;line-height:1;margin-bottom:8px;color:var(--pcna);}}
.action-title{{font-size:15px;font-weight:850;color:var(--pcna);line-height:1.12;margin-bottom:4px;}}
.action-copy{{font-size:11px;color:var(--muted);line-height:1.25;}}
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
.bottom-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:0;width:min(620px,100%);height:76px;background:var(--pcna);backdrop-filter:blur(16px);border-top:1px solid rgba(255,255,255,.10);display:grid;grid-template-columns:repeat(4,1fr);z-index:9999;padding:7px 7px max(7px,env(safe-area-inset-bottom));box-sizing:border-box;}}
.nav-item{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;color:rgba(255,255,255,.58)!important;font-size:10px;font-weight:800;gap:3px;border-radius:12px;}}
.nav-icon{{font-size:20px;line-height:1;}}
.nav-item.active{{color:rgba(255,255,255,.92)!important;background:rgba(255,255,255,.08);}}
@media(max-width:430px){{.block-container{{padding-top:calc(30px + env(safe-area-inset-top))!important;padding-left:12px!important;padding-right:12px!important;}}.page-title{{font-size:28px;line-height:1.1;}}.section-title{{margin:10px 0 6px;}}.action-grid{{gap:9px;}}.action-card{{padding:10px 11px;min-height:88px;}}}}
@media(max-width:350px){{.action-grid{{grid-template-columns:1fr;}}}}
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


def live_pcna_banner():
    components.html(
        """
<div class="pcna-live-shell"><div class="fallback"><a href="https://www.pcna.com/en-us" target="_blank" rel="noopener">Open live PCNA.com</a></div><iframe src="https://www.pcna.com/en-us" title="Live PCNA.com promotional banner" loading="eager"></iframe></div>
<style>html,body{margin:0;padding:0;background:#fff;overflow:hidden}.pcna-live-shell{position:relative;height:228px;overflow:hidden;border-radius:14px;background:#fff}.pcna-live-shell iframe{position:absolute;left:0;top:-92px;width:100%;height:620px;border:0;background:#fff;z-index:2}.fallback{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;border:1px solid #d6e2eb;border-radius:14px;background:#fff;z-index:1}.fallback a{color:#084f86;font-size:15px;font-weight:700;text-decoration:none}@media(max-width:430px){.pcna-live-shell{height:188px}.pcna-live-shell iframe{top:-82px;height:590px}}</style>
""",
        height=228,
        scrolling=False,
    )


def bottom_nav(page: str):
    group = "create" if page in {"spec", "blank", "quote"} else page
    st.markdown(
        f"""
<div class="bottom-nav">
<a class="nav-item {'active' if group=='home' else ''}" href="{nav_link('home')}"><span class="nav-icon">⌂</span><span>Home</span></a>
<a class="nav-item {'active' if group=='search' else ''}" href="{nav_link('search')}"><span class="nav-icon">⌕</span><span>Products</span></a>
<a class="nav-item {'active' if group=='create' else ''}" href="{nav_link('create')}"><span class="nav-icon">＋</span><span>Create</span></a>
<a class="nav-item {'active' if group=='projects' else ''}" href="{projects_link()}"><span class="nav-icon">▣</span><span>Projects</span></a>
</div>
""",
        unsafe_allow_html=True,
    )


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


def project_selector(prefix: str, suggested_name: str = "", suggested_customer: str = "") -> tuple[str, str]:
    projects = list_projects()
    options = ["Create New Project"] + [f"{p['project']} · {p['customer']}" for p in projects]
    selected = st.selectbox("Project", options, key=f"{prefix}_project_choice")
    if selected == "Create New Project":
        name = st.text_input("Project Name", value=suggested_name, key=f"{prefix}_project_name", placeholder="Ford Employee Kit")
        customer = st.text_input("Customer / Account", value=suggested_customer, key=f"{prefix}_customer", placeholder="Ford")
        return name, customer
    p = projects[options.index(selected) - 1]
    return p["project"], p["customer"]


def ensure_project(name: str, customer: str) -> int:
    return get_or_create_project(name or "Untitled Project", customer or "Unassigned")


def copy_button(text: str, key: str):
    safe = json.dumps(text)
    components.html(
        f"""<button id="copy-{key}" style="width:100%;min-height:44px;border:1px solid #b8cad8;border-radius:12px;background:white;color:#084f86;font-weight:800;font-size:14px;">Copy</button>
<script>document.getElementById('copy-{key}').onclick=async()=>{{await navigator.clipboard.writeText({safe});document.getElementById('copy-{key}').innerText='Copied';}};</script>""",
        height=52,
    )


def quote_products(products: list[dict]) -> tuple[list[dict], float]:
    lines: list[dict] = []
    extended_total = 0.0
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
        extended_total += extended
        lines.append({**product, **tier, "Extended": extended, "Pricing Available": True})
    return lines, extended_total


def quote_text(project_name: str, customer: str, quote_lines: list[dict], total: float) -> str:
    out = ["PCNA QUOTE", "", f"Project: {project_name}", f"Customer: {customer}", ""]
    for i, line in enumerate(quote_lines, 1):
        out.extend([
            f"ITEM {i}",
            f"Product: {line.get('Product Name','')}",
            f"Item Number: {line.get('Item Number','')}",
            f"Quantity: {line.get('Quantity','')}",
            f"Color: {line.get('Color','')}",
            f"Size: {line.get('Size','')}",
            f"Decoration Method: {line.get('Decoration Method','')}",
            f"Decoration Location: {line.get('Decoration Location','')}",
        ])
        if line.get("Pricing Available"):
            out.extend([
                f"Unit Price: ${float(line.get('Unit Price',0)):,.2f}",
                f"Extended: ${float(line.get('Extended',0)):,.2f}",
                f"Schedule: {line.get('Schedule','')}",
            ])
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
    with st.expander(f"{project['project']} · {project['customer']}", expanded=expanded):
        st.caption(
            f"Updated {project['updated_at'][:10]} · {project.get('virtual_count',0)} virtuals · "
            f"{project.get('quote_count',0)} quotes · {project.get('spec_count',0)} spec samples"
        )
        grouped = {
            "virtual": ("Virtuals / Designs", []),
            "quote": ("Quotes", []),
            "spec_sample": ("Spec Sample Orders", []),
        }
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
                        matching = [f for f in files if f.name.startswith(f"virtual_{artifact['id']}_")]
                        for image in matching:
                            st.image(image.read_bytes(), use_container_width=True)
                            st.download_button("Download Virtual", image.read_bytes(), file_name=image.name, key=f"pimg_{project['id']}_{artifact['id']}_{image.name}", use_container_width=True)
                        if st.button("Quote These Products", key=f"pquote_{artifact['id']}", use_container_width=True, disabled=not products):
                            st.session_state.quote_handoff = {"products": products, "project_id": project["id"], "project": project["project"], "customer": project["customer"], "source_artifact_id": artifact["id"]}
                            st.query_params["page"] = "quote"
                            st.rerun()
                    elif artifact.get("ai_output"):
                        st.markdown(f'<div class="order-box">{artifact["ai_output"]}</div>', unsafe_allow_html=True)
                        copy_button(artifact["ai_output"], f"artifact-{artifact['id']}")
                    else:
                        st.json(data)
        if st.button("Delete Project", key=f"delete_project_{project['id']}", use_container_width=True):
            delete_project(project["id"])
            st.rerun()


page = current_page()

if page == "home":
    live_pcna_banner()
    st.markdown('<div class="section-title">What do you need?</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('spec')}"><div class="action-icon">✓</div><div class="action-title">Spec Sample Order</div><div class="action-copy">Tell Nova what you need and build the verified PCNA order.</div></a>
<a class="action-card" href="{nav_link('virtual')}"><div class="action-icon">◇</div><div class="action-title">Virtual Designs</div><div class="action-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-icon">$</div><div class="action-title">Quote Request</div><div class="action-copy">Quote a verified PCNA product at the requested quantity.</div></a>
<a class="action-card" href="{projects_link()}"><div class="action-icon">▣</div><div class="action-title">Projects</div><div class="action-copy">Open your saved PCNA virtual and design projects.</div></a>
</div>
""",
        unsafe_allow_html=True,
    )

elif page == "create":
    page_header("Create", "Choose a workflow", "Three AI creation workflows, with Projects as the shared workspace.")
    st.markdown(
        f"""
<div class="action-grid">
<a class="action-card" href="{nav_link('spec')}"><div class="action-title">Spec Sample Order</div><div class="action-copy">Plain-English request → verified order.</div></a>
<a class="action-card" href="{nav_link('virtual')}"><div class="action-title">Virtuals / Design</div><div class="action-copy">Product, kit and packaging creative projects.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-title">Quote Request</div><div class="action-copy">Plain-English request → decorated PCNA quote.</div></a>
<a class="action-card" href="{projects_link()}"><div class="action-title">Projects</div><div class="action-copy">All saved virtuals, quotes and spec samples together.</div></a>
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
    page_header("Orders", "Spec Sample Order", "Tell Nova the request in plain English. Verified product and decoration data are resolved before the order is built.")
    natural = st.text_area("Tell Nova what you need", placeholder="Make me a spec sample order with the Dade Polo in black, medium, embroidery left chest, white imprint.", height=150)
    if not api_key():
        st.info("Add OPENAI_API_KEY in Streamlit Secrets to enable Nova requests.")
    if st.button("Generate Spec Sample", type="primary", use_container_width=True, disabled=not natural.strip() or not api_key()):
        try:
            result = resolve_spec_request(api_key(), natural, st.session_state.products, st.session_state.decorations)
            st.session_state.pending_spec = {"request": natural, **result}
        except Exception:
            st.error("Nova could not complete the request. Please retry.")
    pending = st.session_state.get("pending_spec")
    if pending:
        if pending.get("unresolved"):
            st.warning("Could not confidently verify: " + ", ".join(pending["unresolved"]))
        if pending.get("order"):
            st.markdown(f'<div class="order-box">{pending["order"]}</div>', unsafe_allow_html=True)
            copy_button(pending["order"], "spec")
            project_name, customer = project_selector("specsave")
            if st.button("Save to Projects", type="primary", use_container_width=True, disabled=not project_name.strip()):
                pid = ensure_project(project_name, customer)
                save_artifact(pid, "spec_sample", "Spec Sample Order", original_prompt=pending["request"], ai_output=pending["order"], structured_data={"products": pending.get("products", []), "intent": pending.get("intent", {})})
                st.success("Spec sample saved to Projects.")
            if st.button("Create New Request", use_container_width=True):
                st.session_state.pop("pending_spec", None)
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
    handoff = st.session_state.get("quote_handoff")
    if handoff:
        st.info(f"Products loaded from {handoff.get('project','Project')}.")
        loaded = []
        for i, product in enumerate(handoff.get("products", [])):
            qty = int(st.number_input(f"Quantity · {product.get('Product Name','Item')}", min_value=1, value=int(product.get("Quantity") or 100), step=1, key=f"handoff_qty_{i}"))
            loaded.append({**product, "Quantity": qty})
        if st.button("Calculate Quote", type="primary", use_container_width=True, disabled=not loaded):
            lines, total = quote_products(loaded)
            text = quote_text(handoff.get("project", "Project"), handoff.get("customer", "Unassigned"), lines, total)
            st.session_state.pending_quote = {"request": "Quote These Products from Virtual", "products": loaded, "lines": lines, "text": text, "project_id": handoff.get("project_id"), "project": handoff.get("project"), "customer": handoff.get("customer")}
    else:
        natural = st.text_area("Tell Nova what to quote", placeholder="Quote 100 Dade Polos in black with embroidery left chest and 100 Stanley 30 oz Quenchers in Polar with laser left of handle.", height=150)
        if not api_key():
            st.info("Add OPENAI_API_KEY in Streamlit Secrets to enable Nova requests.")
        if st.button("Generate Quote", type="primary", use_container_width=True, disabled=not natural.strip() or not api_key()):
            try:
                result = resolve_quote_request(api_key(), natural, st.session_state.products, st.session_state.decorations)
                if result.get("unresolved"):
                    st.warning("Could not confidently verify: " + ", ".join(result["unresolved"]))
                lines, total = quote_products(result.get("products", []))
                intent = result.get("intent", {})
                project_name = str(intent.get("project_name", "")).strip() or "Quote Project"
                customer = str(intent.get("customer", "")).strip() or "Unassigned"
                text = quote_text(project_name, customer, lines, total)
                st.session_state.pending_quote = {"request": natural, "products": result.get("products", []), "lines": lines, "text": text, "project": project_name, "customer": customer}
            except Exception:
                st.error("Nova could not complete the quote request. Please retry.")
    pending = st.session_state.get("pending_quote")
    if pending:
        st.markdown(f'<div class="order-box">{pending["text"]}</div>', unsafe_allow_html=True)
        copy_button(pending["text"], "quote")
        if pending.get("project_id"):
            pid = int(pending["project_id"])
            st.caption(f"Will save to: {pending.get('project')} · {pending.get('customer')}")
        else:
            project_name, customer = project_selector("quotesave", pending.get("project", ""), pending.get("customer", ""))
            pid = ensure_project(project_name, customer) if project_name.strip() else 0
        if st.button("Save to Projects", type="primary", use_container_width=True, disabled=not pid):
            save_artifact(pid, "quote", "Quote", original_prompt=pending["request"], ai_output=pending["text"], structured_data={"products": pending.get("lines", []), "source_artifact_id": handoff.get("source_artifact_id") if handoff else None})
            st.success("Quote saved to Projects.")
        if st.button("Create New Quote", use_container_width=True):
            st.session_state.pop("pending_quote", None)
            st.session_state.pop("quote_handoff", None)
            st.rerun()

elif page == "virtual":
    page_header("Creative", "Virtuals / Design", "Tell Nova what you want created. Verified products, artwork and design instructions stay attached to the Project.")
    project_name, customer = project_selector("virtual")
    request = st.text_area("What would you like Nova to create?", placeholder="Create a Ford employee gift concept using a Dade Polo, Stanley Quencher and Pedova Journal in a Perfectly Packaged box.", height=170)
    artwork = st.file_uploader("Artwork / reference files", accept_multiple_files=True, type=["png", "jpg", "jpeg", "webp", "pdf", "svg", "eps", "ai"])
    if not api_key():
        st.info("Add OPENAI_API_KEY in Streamlit Secrets to enable Nova generation.")
    if st.button("Generate Virtual", type="primary", use_container_width=True, disabled=not request.strip() or not api_key() or not project_name.strip()):
        try:
            context = build_creative_pcna_context(api_key(), request, st.session_state.products, st.session_state.decorations)
            selected_products = context.get("selected_products", [])
            if context.get("unresolved"):
                st.warning("Could not confidently verify: " + ", ".join(context["unresolved"]))
            if not selected_products:
                st.error("Nova could not confidently resolve verified PCNA products for this request.")
            else:
                intent = context.get("intent", {})
                resolved_customer = customer.strip() or str(intent.get("customer", "")).strip() or "Unassigned"
                resolved_project = project_name.strip() or str(intent.get("project_name", "")).strip() or "Virtual Project"
                pid = ensure_project(resolved_project, resolved_customer)
                count = context.get("requested_concepts", 5)
                payload = {
                    "Request": request,
                    "Artwork": [f.name for f in artwork],
                    "Requested Concepts": count,
                    "Verified Products": selected_products,
                    "Perfectly Packaged": context.get("perfectly_packaged", False),
                    "Generation": "PCNA-trained Nova",
                }
                artifact_id = save_artifact(pid, "virtual", "Virtual / Design", original_prompt=request, structured_data=payload)
                for upload in artwork:
                    save_upload(pid, f"source_{artifact_id}_{upload.name}", upload.getvalue())
                prompt = creative_generation_prompt(request, context)
                progress = st.progress(0, text=f"Nova is creating 0 of {count}...")
                for i in range(count):
                    progress.progress(i / count, text=f"Nova is creating {i+1} of {count}...")
                    new_image = generate_concepts(api_key=api_key(), prompt=prompt, uploads=artwork, count=1)[0]
                    save_upload(pid, f"virtual_{artifact_id}_{i+1:02d}.png", new_image)
                progress.progress(1.0, text=f"Nova completed {count} of {count}.")
                st.session_state.last_virtual = {"project_id": pid, "artifact_id": artifact_id, "project": resolved_project, "customer": resolved_customer, "products": selected_products}
                st.success(f"{count} virtuals generated and saved to {resolved_project}.")
        except Exception:
            st.error("Nova could not complete the virtual request. Please retry.")
    last = st.session_state.get("last_virtual")
    if last:
        project = get_project(last["project_id"])
        if project:
            st.markdown('<div class="section-title">Completed Virtual</div>', unsafe_allow_html=True)
            render_products(last.get("products", []))
            for f in list_project_files(last["project_id"]):
                if f.name.startswith(f"virtual_{last['artifact_id']}_"):
                    st.image(f.read_bytes(), use_container_width=True)
            if st.button("Quote These Products", type="primary", use_container_width=True, disabled=not last.get("products")):
                st.session_state.quote_handoff = {"products": last["products"], "project_id": last["project_id"], "project": last["project"], "customer": last["customer"], "source_artifact_id": last["artifact_id"]}
                st.query_params["page"] = "quote"
                st.rerun()
            if st.button("Create New Virtual", use_container_width=True):
                st.session_state.pop("last_virtual", None)
                st.rerun()

elif page == "projects":
    page_header("Workspace", "Projects", "Virtuals, quotes and spec sample orders stay together by customer and project.")
    projects = list_projects()
    search = st.text_input("Search Projects", placeholder="Project or customer")
    sort = st.selectbox("Sort", ["Recently Modified", "Project Name"])
    if search:
        q = search.lower().strip()
        projects = [p for p in projects if q in f"{p['project']} {p['customer']}".lower()]
    if sort == "Project Name":
        projects = sorted(projects, key=lambda p: p["project"].lower())
    with st.expander("Create New Project"):
        name = st.text_input("New Project Name", key="new_project_name")
        customer = st.text_input("Customer / Account", key="new_project_customer")
        notes = st.text_area("Notes", key="new_project_notes")
        if st.button("Create Project", type="primary", use_container_width=True, disabled=not name.strip()):
            pid = create_project(name, customer, notes)
            st.success("Project created.")
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
                    result = resolve_spec_request(key, prompt, st.session_state.products, st.session_state.decorations)
                    reply = result["order"] or "I could not confidently resolve the requested PCNA products/decorations."
                elif "quote" in low:
                    result = resolve_quote_request(key, prompt, st.session_state.products, st.session_state.decorations)
                    lines, total = quote_products(result.get("products", []))
                    reply = quote_text("Quote Project", "Unassigned", lines, total)
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

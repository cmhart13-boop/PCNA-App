from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional
import re

import pandas as pd
import streamlit as st


PRODUCT_REQUIRED = {"Product Name", "Item Number", "Default Item Color"}
DECOR_REQUIRED = {"Item Number", "Decoration Method", "Decoration Location", "Max Length", "Max Height"}
PRICE_REQUIRED = {"Item Number", "MOQ", "Unit Price", "CurrencyID", "Decorated or Blank", "Price Description"}


def _clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def validate_columns(df: pd.DataFrame, required: Iterable[str], label: str) -> None:
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")


def prepare_products(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, PRODUCT_REQUIRED, "Product Master")
    out = df.copy()
    for col in ["Product Name", "Item Number", "Default Item Color", "Brand", "Product Category", "Product Description"]:
        if col not in out.columns:
            out[col] = ""
        out[col] = out[col].map(_clean_text)
    out = out[out["Item Number"].ne("") & out["Product Name"].ne("")]
    return out.reset_index(drop=True)


def prepare_decorations(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, DECOR_REQUIRED, "Decoration Master")
    out = df.copy()
    for col in ["Item Number", "Decoration Method", "Decoration Location"]:
        out[col] = out[col].map(_clean_text)
    out["Max Length"] = pd.to_numeric(out["Max Length"], errors="coerce")
    out["Max Height"] = pd.to_numeric(out["Max Height"], errors="coerce")
    out = out[out["Item Number"].ne("") & out["Decoration Method"].ne("")]
    return out.drop_duplicates().reset_index(drop=True)


def prepare_pricing(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df, PRICE_REQUIRED, "Pricing Master")
    out = df.copy()
    for col in ["Item Number", "CurrencyID", "Decorated or Blank", "Price Description"]:
        out[col] = out[col].map(_clean_text)
    out["MOQ"] = pd.to_numeric(out["MOQ"], errors="coerce")
    out["Unit Price"] = pd.to_numeric(out["Unit Price"], errors="coerce")
    out = out.dropna(subset=["MOQ", "Unit Price"])
    out = out[out["Item Number"].ne("")]
    return out.reset_index(drop=True)


def search_products(products: pd.DataFrame, query: str, limit: int = 30) -> pd.DataFrame:
    """Rank verified PCNA products robustly even when the query contains decoration/request words."""
    q = _clean_text(query).lower()
    if not q:
        return products.iloc[0:0].copy()

    item = products["Item Number"].str.lower()
    name = products["Product Name"].str.lower()
    brand = products["Brand"].str.lower()
    combined = name + " " + brand + " " + item

    # Natural-language requests often append color, size and decoration to the product name.
    # Ignore those workflow words for product identity, while strongly rewarding distinctive name tokens.
    stop = {
        "a","an","the","me","make","need","want","with","in","on","and","for","of","to",
        "spec","sample","order","quote","virtual","virtuals","design","designs","product","item",
        "black","white","navy","blue","red","grey","gray","medium","small","large","xl","xxl",
        "embroidery","embroidered","embroider","laser","engraving","engraved","deboss","dtf","transfer",
        "left","right","chest","sleeve","front","back","handle","imprint","logo","color","colour",
        "size","oz","ounce","ounces","qty","quantity"
    }
    raw_tokens = re.findall(r"[a-z0-9]+", q.replace("-", " "))
    tokens = [t for t in raw_tokens if len(t) > 1 and t not in stop]

    exact_item = item.eq(q)
    starts_item = item.str.startswith(q, na=False)
    phrase_name = name.str.contains(q, regex=False, na=False)
    phrase_brand = brand.str.contains(q, regex=False, na=False)

    score = exact_item.astype(int) * 1000 + starts_item.astype(int) * 500 + phrase_name.astype(int) * 250 + phrase_brand.astype(int) * 20

    if tokens:
        token_hits = pd.Series(0, index=products.index, dtype="int64")
        name_hits = pd.Series(0, index=products.index, dtype="int64")
        for token in tokens:
            token_hits += combined.str.contains(token, regex=False, na=False).astype(int)
            name_hits += name.str.contains(token, regex=False, na=False).astype(int)
        # All meaningful product tokens matching is the strongest natural-language signal.
        score += token_hits * 35 + name_hits * 55
        score += token_hits.eq(len(tokens)).astype(int) * 220

    # Locked aliases for known PCNA product shorthand used by the field team.
    qnorm = " ".join(raw_tokens)
    aliases = {
        "dade polo": "TM16398",
        "dade": "TM16398",
        "bodie tee": "TM17879",
        "stanley 30": "1603-02",
        "stanley quencher 30": "1603-02",
        "pedova journal": "2700-02",
        "pinnacle 40": "1603-15",
        "hercules tote": "SM-7427",
        "hydro flask 20": "1601-95",
    }
    for alias, sku in aliases.items():
        if alias in qnorm:
            score += item.eq(sku.lower()).astype(int) * 5000

    out = products.loc[score.gt(0)].copy()
    if out.empty:
        return out
    out["_score"] = score[score.gt(0)]
    out = out.sort_values(["_score", "Product Name", "Item Number"], ascending=[False, True, True])
    return out.drop(columns="_score").head(limit).reset_index(drop=True)


def product_identity(products: pd.DataFrame, item_number: str) -> Optional[dict]:
    item = _clean_text(item_number)
    rows = products[products["Item Number"].eq(item)]
    if rows.empty:
        return None
    first = rows.iloc[0]
    return {
        "Product Name": _clean_text(first.get("Product Name")),
        "Item Number": item,
        "Brand": _clean_text(first.get("Brand")),
        "Product Category": _clean_text(first.get("Product Category")),
        "Product Description": _clean_text(first.get("Product Description")),
    }


def colors_for_item(products: pd.DataFrame, item_number: str) -> list[str]:
    item = _clean_text(item_number)
    values = products.loc[products["Item Number"].eq(item), "Default Item Color"].map(_clean_text)
    return sorted({v for v in values if v})


def decorations_for_item(decorations: pd.DataFrame, item_number: str) -> pd.DataFrame:
    item = _clean_text(item_number)
    return decorations[decorations["Item Number"].eq(item)].drop_duplicates().reset_index(drop=True)


def imprint_size(row: pd.Series) -> str:
    length = row.get("Max Length")
    height = row.get("Max Height")
    if pd.isna(length) or pd.isna(height):
        return "Max Imprint"
    return f'{float(length):g}" W x {float(height):g}" H'


def is_no_ink_decoration(method: str) -> bool:
    m = _clean_text(method).lower()
    return "laser" in m or "deboss" in m


def pricing_schedules(pricing: pd.DataFrame, item_number: str, *, currency: str = "USD", decorated: bool = True) -> list[str]:
    item = _clean_text(item_number)
    rows = pricing[pricing["Item Number"].eq(item) & pricing["CurrencyID"].eq(currency)]
    needle = "Decorated" if decorated else "Blank"
    rows = rows[rows["Decorated or Blank"].str.contains(needle, case=False, regex=False, na=False)]
    schedules = [s for s in rows["Decorated or Blank"].map(_clean_text).unique().tolist() if s]
    def rank(s: str):
        sl = s.lower()
        return (0 if "list" in sl else 1, 0 if sl.endswith("_1") else 1, sl)
    return sorted(schedules, key=rank)


def quote_tier(
    pricing: pd.DataFrame,
    item_number: str,
    quantity: int,
    *,
    currency: str = "USD",
    decorated: bool = True,
    schedule: Optional[str] = None,
) -> Optional[dict]:
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")
    item = _clean_text(item_number)
    rows = pricing[pricing["Item Number"].eq(item) & pricing["CurrencyID"].eq(currency)].copy()
    needle = "Decorated" if decorated else "Blank"
    rows = rows[rows["Decorated or Blank"].str.contains(needle, case=False, regex=False, na=False)]
    if rows.empty:
        return None
    schedules = pricing_schedules(pricing, item, currency=currency, decorated=decorated)
    if not schedules:
        return None
    selected_schedule = schedule if schedule in schedules else schedules[0]
    rows = rows[rows["Decorated or Blank"].eq(selected_schedule)]
    if rows.empty:
        return None
    eligible = rows[rows["MOQ"].le(quantity)]
    if eligible.empty:
        chosen = rows.sort_values(["MOQ", "Unit Price"]).iloc[0]
        below_moq = True
    else:
        max_moq = eligible["MOQ"].max()
        chosen = eligible[eligible["MOQ"].eq(max_moq)].sort_values(["Unit Price", "Price Description"]).iloc[0]
        below_moq = False
    return {
        "Item Number": item,
        "Quantity": int(quantity),
        "MOQ Tier": int(chosen["MOQ"]),
        "Unit Price": float(chosen["Unit Price"]),
        "Currency": _clean_text(chosen["CurrencyID"]),
        "Schedule": selected_schedule,
        "Price Description": _clean_text(chosen["Price Description"]),
        "Below MOQ": below_moq,
    }


@dataclass
class SpecItem:
    product: str
    item_number: str
    color: str
    decoration_method: str
    decoration_location: str
    imprint_color: str
    imprint_size: str = "Max Imprint"
    size: str = ""


def build_spec_order(
    items: list[SpecItem],
    *,
    po: str = "",
    ship_date: str = "",
    in_hands_date: str = "",
    ship_to: str = "",
) -> str:
    lines = [
        "SPEC SAMPLE ORDER",
        "",
        f"PO#: {po}",
        "Bill To: Hart Marketing Fund",
        "Customer ID: CH1085",
        "Ship Method: UPS Ground on PCNA Account",
        f"Ship Date: {ship_date}",
        f"In Hands Date: {in_hands_date}",
        "",
    ]
    for i, item in enumerate(items, 1):
        lines.extend([
            f"ITEM {i}",
            f"Product: {item.product}",
        ])
        if item.item_number.strip():
            lines.append(f"Item Number: {item.item_number.strip()}")
        lines.append(f"Item Color: {item.color}")
        if item.size.strip():
            lines.append(f"Size: {item.size.strip()}")
        lines.extend([
            f"Decoration Method: {item.decoration_method}",
            f"Decoration Location: {item.decoration_location}",
            f"Imprint Color: {item.imprint_color}",
            f"Imprint Size: {item.imprint_size or 'Max Imprint'}",
            "",
        ])
    lines.append(f"Ship To: {ship_to}")
    return "\n".join(lines)


# Presentation/runtime patch loaded before app.py defines the pages. This keeps the
# approved card grid intact while correcting the home branding and workflow ergonomics.
_PCNA_HERO_URL = (
    "https://assets.pcna.com/image/upload/f_auto,q_auto/"
    "Mkt_Dept/2026%20Jobs/2026-0810_Web_Messaging/0810_Web_PCNA_Hero_m.gif"
    "?v=202608161633"
)
_original_markdown = st.markdown
_original_button = st.button
_original_text_input = st.text_input


def _pcna_home_markdown(body, *args, **kwargs):
    if isinstance(body, str) and '<div class="pcna-home">' in body and '<a class="pcna-hero"' in body:
        pattern = re.compile(
            r'(<a class="pcna-hero"[^>]*>).*?(</a>\s*<div class="pcna-section-title">)',
            re.DOTALL,
        )
        replacement = (
            r'\1<img class="pcna-hero-live" src="'
            + _PCNA_HERO_URL
            + r'" alt="PCNA current hero banner">\2'
        )
        body = pattern.sub(replacement, body, count=1)
        body += """
<style>
/* Full-bleed animated PCNA hero only: no iframe crop, no split copy, no fake CSS products. */
.pcna-home .pcna-hero:before{display:none!important}
.pcna-home .pcna-hero-copy,.pcna-home .hero-products{display:none!important}
.pcna-home .pcna-hero-live{position:absolute;inset:0;width:100%;height:100%;display:block;object-fit:cover}
/* Approved PCNA logo, at least 50% larger than the prior 38px treatment. */
.pcna-home .pcna-head-logo{height:60px!important;max-width:235px!important;width:auto!important}
.pcna-home .pcna-head{overflow:visible!important}
/* Bottom nav labels +25% for mobile readability. */
.pcna-mobile-nav a{font-size:12.5px!important}
/* Hide Streamlit hosting/deploy chrome. */
[data-testid="stStatusWidget"],[data-testid="stAppDeployButton"],[data-testid="stDeployButton"],
[class*="viewerBadge"],[class*="ViewerBadge"],a[href*="streamlit.io/cloud"]{display:none!important;visibility:hidden!important}
</style>
"""
    elif isinstance(body, str) and "<style>" in body:
        body += """
<style>
[data-testid="stStatusWidget"],[data-testid="stAppDeployButton"],[data-testid="stDeployButton"],
[class*="viewerBadge"],[class*="ViewerBadge"],a[href*="streamlit.io/cloud"]{display:none!important;visibility:hidden!important}
.bottom-nav .nav-item{font-size:12.5px!important}
</style>
"""
    return _original_markdown(body, *args, **kwargs)


def _project_text_input(label, *args, **kwargs):
    key = str(kwargs.get("key", ""))
    # Remove the repetitive Customer/Account field from project attachment flows.
    # Keep project naming as the single visible project concept and preserve a safe backend value.
    if key in {"specsave_customer", "quotesave_customer", "virtual_customer"}:
        if key not in st.session_state:
            st.session_state[key] = "Unassigned"
        return st.session_state[key]
    return _original_text_input(label, *args, **kwargs)


def _workflow_button(label, *args, **kwargs):
    # Rename the existing save action without touching its application logic.
    if label == "Save to Projects":
        return _original_button("＋ Add to Project", *args, **kwargs)

    # On completed spec orders, place linked next-step actions directly beneath the result.
    if label == "Create New Request" and st.session_state.get("pending_spec"):
        pending = st.session_state.get("pending_spec", {})
        products = pending.get("products", []) or []

        if _original_button("＋ Add Quote", key="spec_add_quote", use_container_width=True, disabled=not products):
            project_name = str(st.session_state.get("specsave_project_name", "") or "Spec Project").strip()
            customer = str(st.session_state.get("specsave_customer", "") or "Unassigned").strip()
            st.session_state.quote_handoff = {
                "products": products,
                "project": project_name,
                "customer": customer,
                "source": "spec_sample",
            }
            st.query_params["page"] = "quote"
            st.rerun()

        with st.expander("＋ Add Virtuals", expanded=False):
            st.caption("Keep this spec order in context and continue into the Virtuals workspace.")
            direction = st.text_area(
                "Virtual direction",
                key="spec_virtual_direction",
                placeholder="Show this Dade Polo with the customer logo on left chest...",
                height=90,
            )
            if _original_button("Open Virtual Builder", key="spec_open_virtual", use_container_width=True):
                st.session_state.virtual_handoff = {
                    "products": products,
                    "request": direction,
                    "source": "spec_sample",
                }
                st.query_params["page"] = "virtual"
                st.rerun()

        return _original_button(label, *args, **kwargs)

    return _original_button(label, *args, **kwargs)


st.markdown = _pcna_home_markdown
st.text_input = _project_text_input
st.button = _workflow_button

from __future__ import annotations

import json
import re
from typing import Any

import pandas as pd
from openai import OpenAI

from core import (
    SpecItem,
    build_spec_order,
    colors_for_item,
    decorations_for_item,
    imprint_size,
    is_no_ink_decoration,
    product_identity,
    search_products,
)

PCNA_WORKFLOW_RULES = """
You are the reasoning layer for a PCNA workflow app. You interpret natural language, but you NEVER invent PCNA facts.
The application's verified PCNA product and decoration data are authoritative. Deterministic application code resolves the final product facts.

SPEC SAMPLE RULES:
- Never invent product names, item numbers, colors, sizes, decoration methods or locations.
- Product resolution is by verified PCNA product data.
- Decoration must be resolved from verified PCNA decoration data.
- For laser engraving or deboss, imprint color is N/A.
- Imprint Size defaults to Max Imprint.
- Do not add pricing, inventory or MOQ to a spec sample.

CREATIVE / VIRTUAL / PERFECTLY PACKAGED RULES:
- Use verified PCNA products only.
- Uploaded customer artwork must be preserved faithfully.
- Never invent a PCNA item number, color, decoration method or decoration location.
- If the user names a product, preserve that product intent as a search term.
- If the user describes a project rather than products, propose useful PCNA product SEARCH TERMS/categories, never fake item numbers or fake product names.
- Perfectly Packaged concepts must use approved PCNA Perfectly Packaged structures/templates supplied to the app or the request. Do not invent alternate packaging structures.
- The final generation prompt must contain only product facts resolved by deterministic code from verified PCNA data.
""".strip()


def _json_from_text(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    return json.loads(text)


def interpret_request(api_key: str, request: str, mode: str) -> dict[str, Any]:
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")
    client = OpenAI(api_key=api_key)
    if mode == "spec":
        schema = {
            "items": [{
                "product_query": "product name as user said it",
                "color": "requested color or empty",
                "size": "requested size or empty",
                "decoration_method": "requested method or empty",
                "decoration_location": "requested location or empty",
                "imprint_color": "requested imprint color or empty",
            }],
            "po": "",
            "ship_date": "",
            "in_hands_date": "",
            "ship_to": "",
        }
    else:
        schema = {
            "project_goal": "short project summary",
            "project_name": "short project name if inferable, otherwise empty",
            "customer": "customer or brand if present, otherwise empty",
            "requested_concepts": 5,
            "perfectly_packaged": False,
            "product_needs": [
                {
                    "search_term": "generic PCNA category or user-named product search term",
                    "role": "why this product belongs in the project",
                    "requested_color": "user-requested color or empty",
                    "decoration_method": "requested/preferred decoration or empty",
                    "decoration_location": "requested/preferred location or empty",
                }
            ],
            "creative_direction": "concise direction preserving user intent",
        }
    response = client.responses.create(
        model="gpt-5",
        instructions=PCNA_WORKFLOW_RULES + "\nReturn valid JSON only. Do not use markdown.",
        input=f"MODE: {mode}\nUSER REQUEST: {request}\nRETURN THIS SHAPE: {json.dumps(schema)}",
    )
    return _json_from_text(response.output_text)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _best_product(products: pd.DataFrame, query: str) -> dict[str, Any] | None:
    matches = search_products(products, query, limit=25)
    if matches.empty:
        return None
    unique = matches.drop_duplicates(subset=["Item Number", "Product Name"]).reset_index(drop=True)
    row = unique.iloc[0]
    return product_identity(products, row["Item Number"])


def _resolve_color(products: pd.DataFrame, item: str, requested: str, *, allow_verified_default: bool = False) -> str:
    colors = colors_for_item(products, item)
    if not colors:
        return ""
    if not requested:
        return colors[0] if allow_verified_default else ""
    rq = _norm(requested)
    exact = [c for c in colors if _norm(c) == rq]
    if exact:
        return exact[0]
    contains = [c for c in colors if rq in _norm(c) or _norm(c) in rq]
    if len(contains) == 1:
        return contains[0]
    return colors[0] if allow_verified_default else ""


def _resolve_decoration(
    decorations: pd.DataFrame,
    item: str,
    method: str,
    location: str,
    *,
    allow_verified_default: bool = False,
) -> dict[str, str] | None:
    rows = decorations_for_item(decorations, item)
    if rows.empty:
        return None
    m = _norm(method)
    l = _norm(location)
    scored: list[tuple[int, int, pd.Series]] = []
    for idx, row in rows.iterrows():
        rm = _norm(str(row.get("Decoration Method", "")))
        rl = _norm(str(row.get("Decoration Location", "")))
        score = 0
        if m:
            if rm == m:
                score += 8
            elif m in rm or rm in m:
                score += 5
            elif any(t in rm for t in m.split()):
                score += 2
        if l:
            if rl == l:
                score += 8
            elif l in rl or rl in l:
                score += 5
            elif any(t in rl for t in l.split()):
                score += 2
        scored.append((score, -idx, row))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if (m or l) and scored[0][0] <= 0 and not allow_verified_default:
        return None
    row = scored[0][2] if (m or l) else rows.iloc[0]
    return {
        "Decoration Method": str(row.get("Decoration Method", "")).strip(),
        "Decoration Location": str(row.get("Decoration Location", "")).strip(),
        "Max Imprint": imprint_size(row),
    }


def resolve_spec_request(api_key: str, request: str, products: pd.DataFrame, decorations: pd.DataFrame) -> dict[str, Any]:
    intent = interpret_request(api_key, request, "spec")
    resolved_items: list[SpecItem] = []
    unresolved: list[str] = []
    for raw in intent.get("items", []):
        query = str(raw.get("product_query", "")).strip()
        identity = _best_product(products, query)
        if not identity:
            unresolved.append(query or "Unnamed product")
            continue
        item = identity["Item Number"]
        color = _resolve_color(products, item, str(raw.get("color", "")))
        dec = _resolve_decoration(
            decorations,
            item,
            str(raw.get("decoration_method", "")),
            str(raw.get("decoration_location", "")),
        )
        if not dec:
            unresolved.append(f"{identity['Product Name']} decoration")
            continue
        method = dec["Decoration Method"]
        imprint = "N/A" if is_no_ink_decoration(method) else str(raw.get("imprint_color", "")).strip()
        resolved_items.append(
            SpecItem(
                product=identity["Product Name"],
                item_number=item,
                color=color,
                size=str(raw.get("size", "")).strip(),
                decoration_method=method,
                decoration_location=dec["Decoration Location"],
                imprint_color=imprint,
                imprint_size="Max Imprint",
            )
        )
    order = (
        build_spec_order(
            resolved_items,
            po=str(intent.get("po", "")).strip(),
            ship_date=str(intent.get("ship_date", "")).strip(),
            in_hands_date=str(intent.get("in_hands_date", "")).strip(),
            ship_to=str(intent.get("ship_to", "")).strip(),
        )
        if resolved_items
        else ""
    )
    return {"order": order, "items": resolved_items, "unresolved": unresolved, "intent": intent}


def build_creative_pcna_context(api_key: str, request: str, products: pd.DataFrame, decorations: pd.DataFrame) -> dict[str, Any]:
    intent = interpret_request(api_key, request, "creative")
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    needs = intent.get("product_needs", []) or []
    for need in needs[:6]:
        term = str(need.get("search_term", "")).strip()
        identity = _best_product(products, term)
        if not identity or identity["Item Number"] in seen:
            continue
        item = identity["Item Number"]
        color = _resolve_color(products, item, str(need.get("requested_color", "")), allow_verified_default=True)
        dec = _resolve_decoration(
            decorations,
            item,
            str(need.get("decoration_method", "")),
            str(need.get("decoration_location", "")),
            allow_verified_default=True,
        )
        if not dec:
            continue
        seen.add(item)
        selected.append(
            {
                **identity,
                "Color": color,
                "Decoration Method": dec["Decoration Method"],
                "Decoration Location": dec["Decoration Location"],
                "Max Imprint": dec["Max Imprint"],
                "Project Role": str(need.get("role", "")).strip(),
                "Resolution Source": "Verified PCNA product + decoration masters",
            }
        )
    try:
        requested_concepts = int(intent.get("requested_concepts", 5) or 5)
    except Exception:
        requested_concepts = 5
    requested_concepts = max(1, min(requested_concepts, 8))
    return {
        "intent": intent,
        "selected_products": selected,
        "verified_products": selected,
        "requested_concepts": requested_concepts,
        "perfectly_packaged": bool(intent.get("perfectly_packaged", False)) or "perfectly packaged" in request.lower() or "packag" in request.lower(),
    }


def creative_generation_prompt(request: str, context: dict[str, Any], extra_direction: str = "") -> str:
    selected = context.get("selected_products", [])
    packaging_rule = (
        "This request includes Perfectly Packaged work. Use only approved PCNA Perfectly Packaged structures/templates supplied in the request/app context; do not invent a box structure. "
        if context.get("perfectly_packaged")
        else ""
    )
    return (
        "You are executing the PCNA-trained Nova creative workflow. Every product fact below was resolved from verified PCNA data. "
        "Use ONLY those product names, item numbers, colors, decoration methods and decoration locations. Do not substitute or invent PCNA products. "
        "Preserve uploaded customer artwork faithfully and do not redesign logos unless the user explicitly asks. "
        + packaging_rule
        + f"\nUSER REQUEST:\n{request}\n"
        + f"\nINTERPRETED PROJECT:\n{json.dumps(context.get('intent', {}), ensure_ascii=False)}\n"
        + f"\nSELECTED VERIFIED PCNA PRODUCTS:\n{json.dumps(selected, ensure_ascii=False)}\n"
        + f"\nADDITIONAL DIRECTION:\n{extra_direction}\n"
        + "Create a polished client-ready virtual. The visible products must correspond to the verified product data above."
    )

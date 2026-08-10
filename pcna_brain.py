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
The application's verified PCNA product, decoration and pricing data are authoritative. Deterministic application code resolves final facts and prices.

SPEC SAMPLE RULES:
- Always return every item the user requested. Never silently drop an item.
- Preserve the user's product wording and requested details in the JSON when verification may be needed later.
- Never invent product names, item numbers, colors, sizes, decoration methods or locations.
- Product resolution is by verified PCNA product data.
- Decoration must be resolved from verified PCNA decoration data when available.
- For laser engraving or deboss, imprint color is N/A.
- Imprint Size defaults to Max Imprint.
- Do not add pricing, inventory or MOQ to a spec sample.
- If an item number cannot be confidently verified, deterministic code may omit only the Item Number line and still complete the written order from user-supplied details.

QUOTE RULES:
- Never invent product names, item numbers, quantities, colors, sizes, decoration methods, locations or prices.
- Interpret the user's requested quantities and product/decorating intent only.
- Deterministic application code resolves products/decorations and calculates decorated pricing from verified PCNA pricing data.
- If a user does not give a quantity, leave quantity null/empty rather than guessing.

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
                "product_query": "product name exactly as user said it",
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
    elif mode == "quote":
        schema = {
            "project_name": "project/customer name if stated, otherwise empty",
            "customer": "customer/account if stated, otherwise empty",
            "items": [{
                "product_query": "product name as user said it",
                "quantity": 100,
                "color": "requested color or empty",
                "size": "requested size or empty",
                "decoration_method": "requested method or empty",
                "decoration_location": "requested location or empty",
                "imprint_color": "requested imprint color or empty"
            }]
        }
    else:
        schema = {
            "project_goal": "short project summary",
            "project_name": "short project name if inferable, otherwise empty",
            "customer": "customer or brand if present, otherwise empty",
            "requested_concepts": 5,
            "perfectly_packaged": False,
            "product_needs": [{
                "search_term": "generic PCNA category or user-named product search term",
                "role": "why this product belongs in the project",
                "requested_color": "user-requested color or empty",
                "size": "requested size or empty",
                "quantity": None,
                "decoration_method": "requested/preferred decoration or empty",
                "decoration_location": "requested/preferred location or empty",
                "imprint_color": "requested imprint color or empty"
            }],
            "creative_direction": "concise direction preserving user intent",
        }
    response = client.responses.create(
        model="gpt-5",
        instructions=PCNA_WORKFLOW_RULES + "\nReturn valid JSON only. Do not use markdown. For spec mode, include every requested item even if you are unsure how it maps to a catalog record.",
        input=f"MODE: {mode}\nUSER REQUEST: {request}\nRETURN THIS SHAPE: {json.dumps(schema)}",
    )
    parsed = _json_from_text(response.output_text)
    if mode == "spec" and not isinstance(parsed.get("items"), list):
        parsed["items"] = []
    return parsed


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


def _resolved_product(raw: dict[str, Any], products: pd.DataFrame, decorations: pd.DataFrame, *, allow_defaults: bool = False) -> tuple[dict[str, Any] | None, str | None]:
    query = str(raw.get("product_query") or raw.get("search_term") or "").strip()
    identity = _best_product(products, query)
    if not identity:
        return None, query or "Unnamed product"
    item = identity["Item Number"]
    requested_color = str(raw.get("color") or raw.get("requested_color") or "").strip()
    color = _resolve_color(products, item, requested_color, allow_verified_default=allow_defaults)
    dec = _resolve_decoration(
        decorations,
        item,
        str(raw.get("decoration_method", "")),
        str(raw.get("decoration_location", "")),
        allow_verified_default=allow_defaults,
    )
    if not dec:
        return None, f"{identity['Product Name']} decoration"
    method = dec["Decoration Method"]
    imprint = "N/A" if is_no_ink_decoration(method) else str(raw.get("imprint_color", "")).strip()
    resolved = {
        **identity,
        "Color": color,
        "Size": str(raw.get("size", "") or "").strip(),
        "Decoration Method": method,
        "Decoration Location": dec["Decoration Location"],
        "Imprint Color": imprint,
        "Max Imprint": dec["Max Imprint"],
    }
    if raw.get("quantity") not in (None, ""):
        try:
            resolved["Quantity"] = int(raw.get("quantity"))
        except (TypeError, ValueError):
            pass
    return resolved, None


def _spec_item_from_user(raw: dict[str, Any], *, verified_identity: dict[str, Any] | None = None, verified_color: str = "") -> SpecItem:
    product = (verified_identity or {}).get("Product Name") or str(raw.get("product_query") or "").strip() or "Requested PCNA Product"
    item_number = (verified_identity or {}).get("Item Number", "")
    method = str(raw.get("decoration_method", "") or "").strip()
    imprint = "N/A" if is_no_ink_decoration(method) else str(raw.get("imprint_color", "") or "").strip()
    return SpecItem(
        product=product,
        item_number=item_number,
        color=verified_color or str(raw.get("color", "") or "").strip(),
        size=str(raw.get("size", "") or "").strip(),
        decoration_method=method,
        decoration_location=str(raw.get("decoration_location", "") or "").strip(),
        imprint_color=imprint,
        imprint_size="Max Imprint",
    )


def resolve_spec_request(api_key: str, request: str, products: pd.DataFrame, decorations: pd.DataFrame) -> dict[str, Any]:
    intent = interpret_request(api_key, request, "spec")
    raw_items = intent.get("items", []) or []
    resolved_items: list[SpecItem] = []
    product_data: list[dict[str, Any]] = []
    unresolved: list[str] = []

    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        resolved, error = _resolved_product(raw, products, decorations)
        if resolved:
            product_data.append(resolved)
            resolved_items.append(
                SpecItem(
                    product=resolved["Product Name"],
                    item_number=resolved["Item Number"],
                    color=resolved["Color"] or str(raw.get("color", "") or "").strip(),
                    size=resolved["Size"],
                    decoration_method=resolved["Decoration Method"],
                    decoration_location=resolved["Decoration Location"],
                    imprint_color=resolved["Imprint Color"],
                    imprint_size="Max Imprint",
                )
            )
            if not resolved["Color"] and str(raw.get("color", "") or "").strip():
                unresolved.append(f"{resolved['Product Name']} color: {str(raw.get('color', '')).strip()}")
            continue

        query = str(raw.get("product_query", "") or "").strip()
        identity = _best_product(products, query)
        verified_color = ""
        if identity:
            requested_color = str(raw.get("color", "") or "").strip()
            verified_color = _resolve_color(products, identity["Item Number"], requested_color)
            unresolved.append(error or f"{identity['Product Name']} requested decoration")
        else:
            unresolved.append(error or query or "Unknown item")
        resolved_items.append(_spec_item_from_user(raw, verified_identity=identity, verified_color=verified_color))

    if not resolved_items:
        raise ValueError("The request did not contain any spec sample items.")

    order = build_spec_order(
        resolved_items,
        po=str(intent.get("po", "")).strip(),
        ship_date=str(intent.get("ship_date", "")).strip(),
        in_hands_date=str(intent.get("in_hands_date", "")).strip(),
        ship_to=str(intent.get("ship_to", "")).strip(),
    )
    return {"order": order, "items": resolved_items, "products": product_data, "unresolved": unresolved, "intent": intent}


def resolve_quote_request(api_key: str, request: str, products: pd.DataFrame, decorations: pd.DataFrame) -> dict[str, Any]:
    intent = interpret_request(api_key, request, "quote")
    resolved_products: list[dict[str, Any]] = []
    unresolved: list[str] = []
    for raw in intent.get("items", []):
        resolved, error = _resolved_product(raw, products, decorations)
        if error or not resolved:
            unresolved.append(error or "Unknown item")
            continue
        if not resolved.get("Quantity"):
            unresolved.append(f"{resolved['Product Name']} quantity")
        resolved_products.append(resolved)
    return {"products": resolved_products, "unresolved": unresolved, "intent": intent}


def build_creative_pcna_context(api_key: str, request: str, products: pd.DataFrame, decorations: pd.DataFrame) -> dict[str, Any]:
    intent = interpret_request(api_key, request, "creative")
    selected: list[dict[str, Any]] = []
    unresolved: list[str] = []
    seen: set[str] = set()
    for need in (intent.get("product_needs", []) or [])[:6]:
        resolved, error = _resolved_product(need, products, decorations, allow_defaults=True)
        if error or not resolved:
            unresolved.append(error or "Unknown item")
            continue
        if resolved["Item Number"] in seen:
            continue
        seen.add(resolved["Item Number"])
        resolved["Project Role"] = str(need.get("role", "")).strip()
        resolved["Resolution Source"] = "Verified PCNA product + decoration masters"
        selected.append(resolved)
    try:
        requested_concepts = int(intent.get("requested_concepts", 5) or 5)
    except Exception:
        requested_concepts = 5
    requested_concepts = max(1, min(requested_concepts, 8))
    return {
        "intent": intent,
        "selected_products": selected,
        "verified_products": selected,
        "unresolved": unresolved,
        "requested_concepts": requested_concepts,
        "perfectly_packaged": bool(intent.get("perfectly_packaged", False)) or "perfectly packaged" in request.lower() or "packag" in request.lower(),
    }


def creative_generation_prompt(request: str, context: dict[str, Any], extra_direction: str = "") -> str:
    selected = context.get("selected_products", [])
    packaging_rule = (
        "This request includes Perfectly Packaged work. Use only approved PCNA Perfectly Packaged structures/templates supplied in the request/app context; do not invent a box structure. "
        if context.get("perfectly_packaged") else ""
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
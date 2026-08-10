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
You are the reasoning layer for a PCNA workflow app. You are NOT allowed to invent PCNA facts.
For product facts, the application database is authoritative. Your job is to interpret the user's natural language and return structured intent; deterministic code resolves products and decoration.

SPEC SAMPLE RULES:
- Never invent product names, item numbers, colors, sizes, decoration methods or locations.
- Product resolution is by PCNA product master first; confirmed master data overrides model knowledge.
- Decoration must be resolved from PCNA decoration data.
- For laser engraving or deboss, imprint color is N/A.
- Imprint Size defaults to Max Imprint.
- Do not add pricing, inventory or MOQ to a spec sample.

CREATIVE / VIRTUAL / PERFECTLY PACKAGED RULES:
- Use verified PCNA products only.
- Uploaded customer artwork must be preserved faithfully.
- Never invent a PCNA item number or unsupported decoration.
- Perfectly Packaged concepts must use only approved PCNA Perfectly Packaged structures/templates supplied to the app; do not invent alternate packaging structures.
- When a user gives only a project concept (for example, a new-hire kit), propose useful product SEARCH TERMS, not fake product names. The app will resolve those terms against the verified catalog before generation.
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
                "imprint_color": "requested imprint color or empty"
            }],
            "po": "", "ship_date": "", "in_hands_date": "", "ship_to": ""
        }
    else:
        schema = {
            "project_goal": "short summary",
            "customer": "customer/brand if present",
            "product_search_terms": ["3 to 6 generic PCNA product category/search terms appropriate to the request"],
            "creative_direction": "concise direction preserving user intent"
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
    # search_products already ranks exact item/name/token matches; use first deterministic hit.
    row = unique.iloc[0]
    identity = product_identity(products, row["Item Number"])
    return identity


def _resolve_color(products: pd.DataFrame, item: str, requested: str) -> str:
    colors = colors_for_item(products, item)
    if not requested:
        return ""
    rq = _norm(requested)
    exact = [c for c in colors if _norm(c) == rq]
    if exact:
        return exact[0]
    contains = [c for c in colors if rq in _norm(c) or _norm(c) in rq]
    return contains[0] if len(contains) == 1 else ""


def _resolve_decoration(decorations: pd.DataFrame, item: str, method: str, location: str) -> dict[str, str] | None:
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
            if rm == m: score += 8
            elif m in rm or rm in m: score += 5
            elif any(t in rm for t in m.split()): score += 2
        if l:
            if rl == l: score += 8
            elif l in rl or rl in l: score += 5
            elif any(t in rl for t in l.split()): score += 2
        scored.append((score, -idx, row))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if (m or l) and scored[0][0] <= 0:
        return None
    row = scored[0][2]
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
        resolved_items.append(SpecItem(
            product=identity["Product Name"],
            item_number=item,
            color=color,
            size=str(raw.get("size", "")).strip(),
            decoration_method=method,
            decoration_location=dec["Decoration Location"],
            imprint_color=imprint,
            imprint_size="Max Imprint",
        ))
    order = build_spec_order(
        resolved_items,
        po=str(intent.get("po", "")).strip(),
        ship_date=str(intent.get("ship_date", "")).strip(),
        in_hands_date=str(intent.get("in_hands_date", "")).strip(),
        ship_to=str(intent.get("ship_to", "")).strip(),
    ) if resolved_items else ""
    return {"order": order, "items": resolved_items, "unresolved": unresolved, "intent": intent}


def build_creative_pcna_context(api_key: str, request: str, products: pd.DataFrame, decorations: pd.DataFrame) -> dict[str, Any]:
    intent = interpret_request(api_key, request, "creative")
    verified: list[dict[str, Any]] = []
    seen: set[str] = set()
    for term in intent.get("product_search_terms", [])[:6]:
        identity = _best_product(products, str(term))
        if not identity or identity["Item Number"] in seen:
            continue
        seen.add(identity["Item Number"])
        item = identity["Item Number"]
        dec = decorations_for_item(decorations, item)
        verified.append({
            **identity,
            "Available Colors": colors_for_item(products, item)[:20],
            "Decoration Options": [
                {
                    "method": str(r.get("Decoration Method", "")),
                    "location": str(r.get("Decoration Location", "")),
                    "max_imprint": imprint_size(r),
                }
                for _, r in dec.head(20).iterrows()
            ],
        })
    return {"intent": intent, "verified_products": verified}


def creative_generation_prompt(request: str, context: dict[str, Any], extra_direction: str = "") -> str:
    verified = context.get("verified_products", [])
    return (
        "You are executing a PCNA-trained creative workflow. Use ONLY the verified PCNA product context below for product facts. "
        "Do not invent PCNA products, item numbers, colors, decoration methods, decoration locations, packaging structures, or brand marks. "
        "Use uploaded customer artwork exactly as supplied. For Perfectly Packaged work, use only approved supplied PCNA Perfectly Packaged templates/structures. "
        f"\nUSER REQUEST:\n{request}\n"
        f"\nINTERPRETED PROJECT:\n{json.dumps(context.get('intent', {}), ensure_ascii=False)}\n"
        f"\nVERIFIED PCNA PRODUCTS:\n{json.dumps(verified, ensure_ascii=False)}\n"
        f"\nADDITIONAL DIRECTION:\n{extra_direction}\n"
        "Create a polished client-ready concept grounded in these verified PCNA facts."
    )

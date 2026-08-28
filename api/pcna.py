from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from core import (
    SpecItem,
    build_spec_order,
    colors_for_item,
    imprint_size,
    is_no_ink_decoration,
    prepare_decorations,
    prepare_pricing,
    prepare_products,
    product_identity,
    quote_tier,
    search_products,
    decorations_for_item,
)
from starter_data import verified_starter_data

app = FastAPI()

_products_raw, _decor_raw, _pricing_raw = verified_starter_data()
PRODUCTS = prepare_products(_products_raw)
DECORATIONS = prepare_decorations(_decor_raw)
PRICING = prepare_pricing(_pricing_raw)


def resolve_product(query: str) -> dict:
    matches = search_products(PRODUCTS, query, limit=10)
    if matches.empty:
        raise HTTPException(status_code=404, detail="No verified PCNA product match found.")
    item = str(matches.iloc[0]["Item Number"])
    ident = product_identity(PRODUCTS, item)
    if not ident:
        raise HTTPException(status_code=404, detail="Verified product identity could not be resolved.")
    return ident


@app.get("/api/pcna")
def pcna(
    action: str = Query("search"),
    q: str = Query(""),
    qty: int = Query(100, ge=1),
    color: str = Query(""),
    size: str = Query(""),
    method: str = Query(""),
    location: str = Query(""),
    imprint: str = Query(""),
    ship_to: str = Query(""),
):
    action = action.lower().strip()
    if action == "search":
        if not q.strip():
            return {"results": []}
        rows = search_products(PRODUCTS, q, limit=20)
        results = []
        seen = set()
        for _, row in rows.iterrows():
            key = (str(row.get("Item Number", "")), str(row.get("Product Name", "")))
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "product_name": key[1],
                "item_number": key[0],
                "brand": str(row.get("Brand", "")),
                "color": str(row.get("Default Item Color", "")),
            })
        return {"results": results}

    if action == "quote":
        ident = resolve_product(q)
        tier = quote_tier(PRICING, ident["Item Number"], qty, decorated=True)
        if not tier:
            raise HTTPException(status_code=404, detail="No verified decorated USD price tier found for this product.")
        return {
            "product_name": ident["Product Name"],
            "item_number": ident["Item Number"],
            "quantity": tier["Quantity"],
            "moq_tier": tier["MOQ Tier"],
            "unit_price": tier["Unit Price"],
            "currency": tier["Currency"],
            "schedule": tier["Schedule"],
            "price_description": tier["Price Description"],
            "below_moq": tier["Below MOQ"],
        }

    if action == "spec":
        ident = resolve_product(q)
        item = ident["Item Number"]
        verified_colors = colors_for_item(PRODUCTS, item)
        chosen_color = color.strip() or (verified_colors[0] if verified_colors else "")
        decs = decorations_for_item(DECORATIONS, item)
        max_imprint = "Max Imprint"
        chosen_method = method.strip()
        chosen_location = location.strip()
        if not decs.empty:
            selected = decs
            if chosen_method:
                narrowed = selected[selected["Decoration Method"].str.contains(chosen_method, case=False, regex=False, na=False)]
                if not narrowed.empty:
                    selected = narrowed
            if chosen_location:
                narrowed = selected[selected["Decoration Location"].str.contains(chosen_location, case=False, regex=False, na=False)]
                if not narrowed.empty:
                    selected = narrowed
            row = selected.iloc[0]
            chosen_method = chosen_method or str(row["Decoration Method"])
            chosen_location = chosen_location or str(row["Decoration Location"])
            max_imprint = imprint_size(row)
        chosen_imprint = imprint.strip()
        if not chosen_imprint and is_no_ink_decoration(chosen_method):
            chosen_imprint = "N/A"
        spec = SpecItem(
            product=ident["Product Name"],
            item_number=item,
            color=chosen_color,
            size=size.strip(),
            decoration_method=chosen_method,
            decoration_location=chosen_location,
            imprint_color=chosen_imprint,
            imprint_size=max_imprint,
        )
        return {"order": build_spec_order([spec], ship_to=ship_to)}

    raise HTTPException(status_code=400, detail="Unsupported action.")

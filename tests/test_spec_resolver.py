import pcna_brain
from core import prepare_decorations, prepare_products
from starter_data import verified_starter_data


def data():
    products, decorations, _ = verified_starter_data()
    return prepare_products(products), prepare_decorations(decorations)


def run_with_intent(monkeypatch, intent):
    products, decorations = data()
    monkeypatch.setattr(pcna_brain, "interpret_request", lambda api_key, request, mode: intent)
    return pcna_brain.resolve_spec_request("test-key", "test request", products, decorations)


def test_1_verified_dade_generates_required_written_template(monkeypatch):
    result = run_with_intent(monkeypatch, {
        "items": [{
            "product_query": "Dade Polo",
            "color": "Black",
            "size": "Medium",
            "decoration_method": "Embroidery",
            "decoration_location": "left chest",
            "imprint_color": "White",
        }],
        "po": "",
        "ship_date": "",
        "in_hands_date": "",
        "ship_to": "",
    })
    order = result["order"]
    assert order.startswith("SPEC SAMPLE ORDER\n\nPO#:")
    assert "Bill To: Hart Marketing Fund" in order
    assert "Customer ID: CH1085" in order
    assert "Ship Method: UPS Ground on PCNA Account" in order
    assert "Product: Men's DADE Short Sleeve Polo" in order
    assert "Item Number: TM16398" in order
    assert "Size: Medium" in order
    assert "Decoration Method: Apparel Embroidery" in order
    assert "Imprint Color: White" in order
    assert order.endswith("Ship To: ")


def test_2_unresolved_product_still_generates_order_and_omits_only_item_number(monkeypatch):
    result = run_with_intent(monkeypatch, {
        "items": [{
            "product_query": "Future PCNA Product",
            "color": "Blue",
            "size": "",
            "decoration_method": "Digital Transfer",
            "decoration_location": "Front",
            "imprint_color": "White",
        }],
        "po": "",
        "ship_date": "",
        "in_hands_date": "",
        "ship_to": "",
    })
    order = result["order"]
    assert "ITEM 1" in order
    assert "Product: Future PCNA Product" in order
    assert "Item Number:" not in order
    assert "Item Color: Blue" in order
    assert "Decoration Method: Digital Transfer" in order
    assert "Decoration Location: Front" in order
    assert result["unresolved"]


def test_3_verified_product_with_unmatched_decoration_keeps_verified_item_and_user_details(monkeypatch):
    result = run_with_intent(monkeypatch, {
        "items": [{
            "product_query": "Dade Polo",
            "color": "Black",
            "size": "Medium",
            "decoration_method": "Foil Stamp",
            "decoration_location": "Back Yoke",
            "imprint_color": "Gold",
        }],
        "po": "",
        "ship_date": "",
        "in_hands_date": "",
        "ship_to": "",
    })
    order = result["order"]
    assert "Product: Men's DADE Short Sleeve Polo" in order
    assert "Item Number: TM16398" in order
    assert "Decoration Method: Foil Stamp" in order
    assert "Decoration Location: Back Yoke" in order
    assert result["unresolved"]


def test_4_laser_fallback_forces_imprint_color_na(monkeypatch):
    result = run_with_intent(monkeypatch, {
        "items": [{
            "product_query": "Future Tumbler",
            "color": "Polar",
            "size": "",
            "decoration_method": "Laser Engraving",
            "decoration_location": "Left of Handle",
            "imprint_color": "Blue",
        }],
        "po": "",
        "ship_date": "",
        "in_hands_date": "",
        "ship_to": "",
    })
    order = result["order"]
    assert "Imprint Color: N/A" in order
    assert "Imprint Size: Max Imprint" in order


def test_5_multi_item_order_preserves_single_header_single_ship_to_and_metadata(monkeypatch):
    result = run_with_intent(monkeypatch, {
        "items": [
            {
                "product_query": "Dade Polo",
                "color": "Black",
                "size": "Medium",
                "decoration_method": "Embroidery",
                "decoration_location": "left chest",
                "imprint_color": "White",
            },
            {
                "product_query": "Stanley Quencher 30oz",
                "color": "Frost",
                "size": "",
                "decoration_method": "Laser",
                "decoration_location": "Handle Left",
                "imprint_color": "",
            },
        ],
        "po": "PO-123",
        "ship_date": "2026-08-12",
        "in_hands_date": "2026-08-15",
        "ship_to": "Atlanta, GA",
    })
    order = result["order"]
    assert order.count("SPEC SAMPLE ORDER") == 1
    assert order.count("Ship To:") == 1
    assert "ITEM 1" in order and "ITEM 2" in order
    assert "PO#: PO-123" in order
    assert "Ship Date: 2026-08-12" in order
    assert "In Hands Date: 2026-08-15" in order
    assert order.endswith("Ship To: Atlanta, GA")

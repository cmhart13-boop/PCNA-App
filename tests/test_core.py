from core import (
    SpecItem,
    build_spec_order,
    colors_for_item,
    decorations_for_item,
    is_no_ink_decoration,
    prepare_decorations,
    prepare_pricing,
    prepare_products,
    quote_tier,
    search_products,
)
from starter_data import verified_starter_data


def data():
    p, d, r = verified_starter_data()
    return prepare_products(p), prepare_decorations(d), prepare_pricing(r)


def test_dade_resolves_to_verified_item_number():
    p, _, _ = data()
    result = search_products(p, "Dade Polo")
    assert not result.empty
    assert result.iloc[0]["Item Number"] == "TM16398"
    assert result.iloc[0]["Product Name"] == "Men's DADE Short Sleeve Polo"


def test_stanley_30oz_colors_are_verified():
    p, _, _ = data()
    colors = colors_for_item(p, "1603-02")
    assert "Black (BK)" in colors
    assert "Frost (FRST)" in colors
    assert "Cream (CR)" in colors


def test_stanley_laser_left_location_exists():
    _, d, _ = data()
    rows = decorations_for_item(d, "1603-02")
    laser = rows[rows["Decoration Method"].eq("Laser")]
    assert len(laser) == 1
    assert "Handle Left" in laser.iloc[0]["Decoration Location"]


def test_standard_quote_uses_decorated_not_blank_pricing():
    _, _, r = data()
    tier = quote_tier(r, "1603-02", 100)
    assert tier is not None
    assert tier["Schedule"] == "USD-List-Decorated_1"
    assert tier["MOQ Tier"] == 100
    assert tier["Unit Price"] == 54.46


def test_pinnacle_100_decorated_price():
    _, _, r = data()
    tier = quote_tier(r, "1603-15", 100)
    assert tier["Unit Price"] == 18.73
    assert tier["MOQ Tier"] == 100


def test_laser_and_deboss_force_no_ink_logic():
    assert is_no_ink_decoration("Laser")
    assert is_no_ink_decoration("Laser - Laser Plus")
    assert is_no_ink_decoration("Deboss")
    assert not is_no_ink_decoration("Apparel Embroidery")


def test_spec_order_format_and_size_rule():
    order = build_spec_order([
        SpecItem(
            product="Men's DADE Short Sleeve Polo",
            item_number="TM16398",
            color="Black (995)",
            size="Medium",
            decoration_method="Apparel Embroidery",
            decoration_location="CHEST, Horizontal, - Centered on Left Chest",
            imprint_color="White",
            imprint_size="Max Imprint",
        ),
        SpecItem(
            product="Stanley Quencher H2.O FlowState™ Tumbler 30oz",
            item_number="1603-02",
            color="Frost (FRST)",
            decoration_method="Laser",
            decoration_location='Handle Left - Opposite Stanley logo, (Front) Center of art 2.89"',
            imprint_color="N/A",
            imprint_size="Max Imprint",
        ),
    ])
    assert order.startswith("SPEC SAMPLE ORDER")
    assert "Bill To: Hart Marketing Fund" in order
    assert "Customer ID: CH1085" in order
    assert "Ship Method: UPS Ground on PCNA Account" in order
    assert "ITEM 1" in order and "ITEM 2" in order
    assert "Size: Medium" in order
    assert "Imprint Color: N/A" in order
    assert "Artwork:" not in order

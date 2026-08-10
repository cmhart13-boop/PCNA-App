from pathlib import Path

p = Path("app.py")
s = p.read_text()

replacements = [
    (
        "background:rgba(255,255,255,.96);backdrop-filter:blur(16px);border-top:1px solid var(--line);",
        "background:var(--pcna);backdrop-filter:blur(16px);border-top:1px solid rgba(255,255,255,.10);",
    ),
    (
        "color:#7890a0!important;font-size:10px;font-weight:800;",
        "color:rgba(255,255,255,.58)!important;font-size:10px;font-weight:800;",
    ),
    (
        ".nav-item.active{color:var(--pcna)!important;background:#eff6fb;}",
        ".nav-item.active{color:rgba(255,255,255,.92)!important;background:rgba(255,255,255,.08);}",
    ),
]
for old, new in replacements:
    if old not in s:
        raise SystemExit(f"Expected CSS not found: {old}")
    s = s.replace(old, new, 1)

old_cards = '''<a class="action-card" href="{nav_link('blank')}"><div class="action-icon">□</div><div class="action-title">Blank Sample Order</div><div class="action-copy">Create a blank sample request from verified PCNA product data.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-icon">$</div><div class="action-title">Quote Request</div><div class="action-copy">Quote a verified PCNA product at the requested quantity.</div></a>
<a class="action-card" href="{nav_link('virtual')}"><div class="action-icon">◇</div><div class="action-title">Virtuals / Design</div><div class="action-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div></a>'''
new_cards = '''<a class="action-card" href="{nav_link('virtual')}"><div class="action-icon">◇</div><div class="action-title">Virtual Designs</div><div class="action-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div></a>
<a class="action-card" href="{nav_link('quote')}"><div class="action-icon">$</div><div class="action-title">Quote Request</div><div class="action-copy">Quote a verified PCNA product at the requested quantity.</div></a>
<a class="action-card" href="{virtual_projects_link()}"><div class="action-icon">▣</div><div class="action-title">Projects</div><div class="action-copy">Open your saved PCNA virtual and design projects.</div></a>'''
if old_cards not in s:
    raise SystemExit("Expected homepage card block not found")
s = s.replace(old_cards, new_cards, 1)

p.write_text(s)

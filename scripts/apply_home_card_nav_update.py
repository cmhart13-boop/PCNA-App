from pathlib import Path
import re

p = Path("app.py")
s = p.read_text()

# Guardrail: these are the four approved home cards. This patch does not edit them.
required_cards = [
    'Spec Sample<br>Order',
    'Virtuals /<br>Designs',
    'Quote<br>Request',
    '<div class="pcna-card-title">Projects</div>',
]
for token in required_cards:
    if token not in s:
        raise SystemExit(f"Home-card guardrail failed before patch: {token}")

# 1) Replace the animated PCNA hero with one static, north-cropped lifestyle frame.
old_hero = 'PCNA_HERO_URL = "https://assets.pcna.com/image/upload/f_auto,q_auto/Mkt_Dept/2026%20Jobs/2026-0817_Web_Messaging/0817_Web_PCNA_Hero_m.gif?app_sync=202608161830"'
new_hero = 'PCNA_HERO_URL = "https://assets.pcna.com/image/upload/ar_16:7,c_fill,g_north,pg_1,q_auto,f_jpg/Mkt_Dept/2026%20Jobs/2026-0817_Web_Messaging/0817_Web_PCNA_Hero_m.jpg"'
if old_hero not in s:
    raise SystemExit("Expected animated hero URL not found")
s = s.replace(old_hero, new_hero, 1)

# The banner itself links only to the PCNA homepage.
old_hero_link = 'href="https://www.pcna.com/executive-gifts?pageType=homepage_banner&location=a_spot&campaign=hero-giftsthatimpressus&type=coolers&business=pcna&country=us&segment=n/a"'
if old_hero_link not in s:
    raise SystemExit("Expected old hero destination not found")
s = s.replace(old_hero_link, 'href="https://www.pcna.com/en-us"', 1)
s = s.replace('alt="PCNA hero banner"', 'alt="PCNA lifestyle banner"', 1)
s = s.replace('object-position:center center!important', 'object-position:center top!important', 1)

# 2) Five-item shared bottom nav: Home / Specs / Products / Virtuals / Quotes.
if 'grid-template-columns:repeat(4,1fr)' not in s:
    raise SystemExit("Expected four-column shared nav CSS not found")
s = s.replace('grid-template-columns:repeat(4,1fr)', 'grid-template-columns:repeat(5,1fr)', 1)

shared_nav_pattern = re.compile(r'def bottom_nav\(page: str\):.*?\n\n\ndef asset_data', re.S)
shared_nav_replacement = '''def bottom_nav(page: str):
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


def asset_data'''
s, count = shared_nav_pattern.subn(shared_nav_replacement, s, count=1)
if count != 1:
    raise SystemExit("Shared bottom_nav function was not replaced exactly once")

# 3) The home-page nav uses the same five destinations and removes Messages/Account.
old_home_nav = '''<nav class="pcna-mobile-nav">
  <a class="active" href="?page=home"><b>⌂</b><span>Home</span></a><a href="?page=projects"><b>▱</b><span>Projects</span></a><a href="?page=search"><b>◇</b><span>Products</span></a><a href="?page=virtual"><b>◯</b><span>Messages</span></a><a href="?page=create"><b>♙</b><span>Account</span></a>
</nav>'''
new_home_nav = '''<nav class="pcna-mobile-nav">
  <a class="active" href="?page=home"><b>⌂</b><span>Home</span></a><a href="?page=spec"><b>✓</b><span>Specs</span></a><a href="?page=search"><b>⌕</b><span>Products</span></a><a href="?page=virtual"><b>◇</b><span>Virtuals</span></a><a href="?page=quote"><b>$</b><span>Quotes</span></a>
</nav>'''
if old_home_nav not in s:
    raise SystemExit("Expected home mobile nav not found")
s = s.replace(old_home_nav, new_home_nav, 1)

# 4) Hide Streamlit's floating status/deploy/viewer chrome so it cannot cover the app nav.
if "pcna-hide-streamlit-chrome" not in s:
    marker = '\n\n@st.cache_data(show_spinner=False)'
    if marker not in s:
        raise SystemExit("CSS insertion marker not found")
    hide_css = '''

st.markdown(
    """
<style>
/* pcna-hide-streamlit-chrome */
[data-testid="stStatusWidget"],
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
[data-testid="stDeployButton"],
[data-testid="stViewerBadge"],
[data-testid="stAppCreatorAvatar"],
[class*="viewerBadge"],
[class*="ViewerBadge"],
[class*="stDeployButton"],
a[href*="streamlit.io/cloud"],
a[href*="share.streamlit.io"],
button[title="Manage app"],
button[aria-label="Manage app"] {
  display:none!important;
  visibility:hidden!important;
  pointer-events:none!important;
}
</style>
""",
    unsafe_allow_html=True,
)
'''
    s = s.replace(marker, hide_css + marker, 1)

# Final guardrails: approved cards remain present and unwanted nav labels are gone from home nav.
for token in required_cards:
    if token not in s:
        raise SystemExit(f"Home-card guardrail failed after patch: {token}")
if '<span>Messages</span>' in s or '<span>Account</span>' in s:
    raise SystemExit("Unwanted home nav labels remain")
if '.gif?app_sync=' in s:
    raise SystemExit("Animated home hero URL remains")

p.write_text(s)

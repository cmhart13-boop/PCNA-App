from pathlib import Path
import re

p = Path("app.py")
s = p.read_text()

# Root fix 1: never rely on embedding PCNA.com in an iframe. PCNA can block
# framing, which makes the hero appear blank even when the site itself works.
hero = '''def live_pcna_banner():
    components.html(
        """
<a class="pcna-hero" href="https://www.pcna.com/en-us" target="_blank" rel="noopener noreferrer" aria-label="Open PCNA.com">
  <div class="pcna-hero-copy">
    <div class="pcna-hero-kicker">PCNA.COM</div>
    <div class="pcna-hero-title">Explore products, brands &amp; tools</div>
    <div class="pcna-hero-link">Open PCNA.com&nbsp;&nbsp;→</div>
  </div>
</a>
<style>
html,body{margin:0;padding:0;background:transparent;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.pcna-hero{display:flex;align-items:flex-end;box-sizing:border-box;width:100%;height:146px;padding:18px 20px;border-radius:14px;text-decoration:none;background:linear-gradient(135deg,#003b5c 0%,#084f86 68%,#0d689f 100%);box-shadow:inset 0 0 0 1px rgba(255,255,255,.10);overflow:hidden}
.pcna-hero-copy{color:#fff}
.pcna-hero-kicker{font-size:11px;font-weight:800;letter-spacing:.13em;opacity:.72;margin-bottom:5px}
.pcna-hero-title{font-size:21px;line-height:1.08;font-weight:800;letter-spacing:-.02em;margin-bottom:8px}
.pcna-hero-link{font-size:12px;font-weight:750;opacity:.88}
</style>
""",
        height=150,
        scrolling=False,
    )
'''

s, n = re.subn(
    r'def live_pcna_banner\(\):\n.*?\n\n\ndef bottom_nav',
    hero + '\n\ndef bottom_nav',
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("Could not replace live_pcna_banner")

# Root fix 2: do not pin the mobile homepage to an artificial fixed height or
# hide vertical overflow. That caused the approved logo and hero to be clipped
# on iPhones with different safe-area / viewport dimensions.
s = s.replace(
    '[data-testid="stAppViewContainer"]>.main{overflow-y:hidden!important;}',
    '[data-testid="stAppViewContainer"]>.main{overflow-y:auto!important;}',
)
s = re.sub(
    r'\.block-container\{width:100%!important;max-width:none!important;height:calc\(100dvh - 76px\)!important;box-sizing:border-box!important;padding:[^\n]+',
    '.block-container{width:100%!important;max-width:none!important;min-height:calc(100dvh - 76px)!important;box-sizing:border-box!important;padding:calc(18px + env(safe-area-inset-top)) 10px 12px!important;margin:0!important;overflow:visible!important;}',
    s,
    count=1,
)
s = re.sub(
    r'\.action-grid\{display:grid!important;grid-template-columns:minmax\(0,1fr\) minmax\(0,1fr\)!important;grid-template-rows:repeat\(2,minmax\(0,1fr\)\)!important;gap:8px!important;margin:0!important;height:[^\n]+',
    '.action-grid{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;grid-template-rows:repeat(2,1fr)!important;gap:8px!important;margin:0!important;height:auto!important;min-height:228px!important;max-height:none!important;}',
    s,
    count=1,
)
s = s.replace(
    '.action-grid{gap:7px!important;height:calc(100dvh - 76px - env(safe-area-inset-top) - 286px)!important;min-height:238px!important;}',
    '.action-grid{gap:7px!important;height:auto!important;min-height:220px!important;}',
)
s = s.replace(
    'approved_pcna_header(100 if page == "home" else 105)',
    'approved_pcna_header(98 if page == "home" else 105)',
)

# Keep the home composition tight without allowing any element to overlap.
s = s.replace(
    '[data-testid="stImage"]{margin:0 0 2px!important;overflow:visible!important;}',
    '[data-testid="stImage"]{margin:0 0 4px!important;overflow:visible!important;}',
)
s = s.replace(
    'iframe[title="streamlit_component"]{display:block!important;margin:0!important;}',
    'iframe[title="streamlit_component"]{display:block!important;margin:2px 0 0!important;width:100%!important;}',
)
s = s.replace(
    '.section-title{font-size:20px!important;margin:4px 0 7px!important;',
    '.section-title{font-size:20px!important;margin:7px 0 8px!important;',
)

# Guardrails: fail instead of silently shipping a broken homepage.
required = [
    'st.image("IMG_2337.webp"',
    'https://www.pcna.com/en-us',
    'Spec Sample Order',
    'Virtual Designs',
    'Quote Request',
    '<div class="action-title">Projects</div>',
    'background:#003b5c',
]
for token in required:
    if token not in s:
        raise SystemExit(f"Homepage guardrail failed: {token}")

p.write_text(s)

from pathlib import Path
import re

p = Path("app.py")
s = p.read_text()

# Keep the approved PCNA logo implementation exactly as-is. Only adjust the
# surrounding Streamlit spacing so the logo sits cleanly without clipping.
s = s.replace(
    '[data-testid="stHeader"]{{height:0;background:rgba(255,255,255,.96);}}',
    '[data-testid="stHeader"]{{height:0!important;background:transparent!important;}}',
    1,
)
s = s.replace(
    '.block-container{{max-width:620px!important;padding:calc(34px + env(safe-area-inset-top)) 15px 104px!important;margin:0 auto!important;}}',
    '.block-container{{max-width:620px!important;padding:calc(24px + env(safe-area-inset-top)) 15px 104px!important;margin:0 auto!important;}}',
    1,
)
s = s.replace(
    '@media(max-width:430px){{.block-container{{padding-top:calc(30px + env(safe-area-inset-top))!important;padding-left:12px!important;padding-right:12px!important;}}',
    '@media(max-width:430px){{.block-container{{padding-top:calc(24px + env(safe-area-inset-top))!important;padding-left:12px!important;padding-right:12px!important;}}',
    1,
)

# Preserve the live PCNA.com hero and the locked logo asset.
required = [
    'st.image("IMG_2337.webp"',
    'iframe src="https://www.pcna.com/en-us"',
    'class="pcna-hero-link" href="https://www.pcna.com/en-us"',
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

from pathlib import Path
import re

p = Path("app.py")
s = p.read_text()

# Restore the homepage hero as a live crop of PCNA.com itself. The transparent
# overlay makes the entire visible hero link directly to PCNA.com.
hero = '''def live_pcna_banner():
    components.html(
        """
<div class="pcna-live-shell">
  <div class="pcna-fallback">Loading PCNA.com…</div>
  <iframe src="https://www.pcna.com/en-us" title="Live PCNA.com hero banner" loading="eager"></iframe>
  <a class="pcna-hero-link" href="https://www.pcna.com/en-us" target="_blank" rel="noopener noreferrer" aria-label="Open PCNA.com"></a>
</div>
<style>
html,body{margin:0;padding:0;background:#fff;overflow:hidden}
.pcna-live-shell{position:relative;width:100%;height:150px;overflow:hidden;border-radius:14px;background:#fff;border:1px solid #d6e2eb;box-sizing:border-box}
.pcna-live-shell iframe{position:absolute;left:0;top:-92px;width:100%;height:620px;border:0;background:#fff;z-index:2}
.pcna-fallback{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#084f86;font:700 14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff;z-index:1}
.pcna-hero-link{position:absolute;inset:0;z-index:3;display:block;cursor:pointer}
</style>
""",
        height=152,
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

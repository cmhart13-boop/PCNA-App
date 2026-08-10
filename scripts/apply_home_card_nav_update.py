from pathlib import Path

p = Path("app.py")
s = p.read_text()

replacements = [
    (
        'padding:calc(2px + env(safe-area-inset-top)) 10px 6px!important;',
        'padding:calc(16px + env(safe-area-inset-top)) 10px 8px!important;',
    ),
    (
        '[data-testid="stImage"]{margin:0!important;}',
        '[data-testid="stImage"]{margin:0 0 2px!important;overflow:visible!important;}',
    ),
    (
        '[data-testid="stImage"] img{display:block!important;margin:0 auto!important;}',
        '[data-testid="stImage"] img{display:block!important;margin:0 auto!important;max-width:100%!important;height:auto!important;object-fit:contain!important;}',
    ),
    (
        'iframe[title="streamlit_component"]{display:block!important;margin:2px 0 0!important;}',
        'iframe[title="streamlit_component"]{display:block!important;margin:0!important;}',
    ),
    (
        '.section-title{font-size:20px!important;margin:5px 0 8px!important;',
        '.section-title{font-size:20px!important;margin:4px 0 7px!important;',
    ),
    (
        'approved_pcna_header(104 if page == "home" else 105)',
        'approved_pcna_header(100 if page == "home" else 105)',
    ),
]

for old, new in replacements:
    if old not in s:
        raise SystemExit(f"Expected current UI fragment not found: {old}")
    s = s.replace(old, new, 1)

p.write_text(s)

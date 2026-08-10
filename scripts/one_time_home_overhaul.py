from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
legacy = ROOT / "_pcna_app_source.py"
app = ROOT / "app.py"

if not legacy.exists():
    raise SystemExit("Legacy source file missing; migration already applied or repository state unexpected.")

source = legacy.read_text(encoding="utf-8")

# Replace the legacy home-only CSS block with one isolated homepage layout.
start_marker = '''if page == "home":\n    st.markdown(\n        """\n<style>\n'''
end_marker = '''\n""",\n        unsafe_allow_html=True,\n    )\n\napproved_pcna_header(98 if page == "home" else 105)'''
start = source.index(start_marker)
end = source.index(end_marker, start) + len(end_marker)

home_css = '''if page == "home":\n    st.markdown(\n        """\n<style>\n/* HOME: one source of truth. Custom HTML cards, always 2x2 on phones. */\n:root {\n  --home-nav-height: 76px;\n  --home-gap: 10px;\n}\n\nhtml, body, [data-testid="stAppViewContainer"] {\n  width: 100%;\n  min-height: 100%;\n  overflow-x: hidden !important;\n  overflow-y: auto !important;\n}\n\n[data-testid="stAppViewContainer"] > .main {\n  width: 100%;\n  min-height: 100dvh !important;\n  height: auto !important;\n  overflow-x: hidden !important;\n  overflow-y: auto !important;\n}\n\n.block-container {\n  width: 100% !important;\n  max-width: 620px !important;\n  height: calc(100dvh - var(--home-nav-height)) !important;\n  min-height: 0 !important;\n  box-sizing: border-box !important;\n  margin: 0 auto !important;\n  padding: calc(6px + env(safe-area-inset-top)) 10px 8px !important;\n  overflow: visible !important;\n}\n\n.block-container > [data-testid="stVerticalBlock"] {\n  display: flex !important;\n  flex-direction: column !important;\n  width: 100% !important;\n  height: 100% !important;\n  min-height: 0 !important;\n  gap: 0 !important;\n  overflow: visible !important;\n}\n\n.block-container [data-testid="stVerticalBlock"],\n.block-container [data-testid="stElementContainer"] {\n  min-height: 0 !important;\n}\n\n[data-testid="stImage"] {\n  flex: 0 0 auto !important;\n  margin: 0 0 2px !important;\n  padding: 0 !important;\n  overflow: visible !important;\n}\n\n[data-testid="stImage"] img {\n  display: block !important;\n  margin: 0 auto !important;\n  max-width: 100% !important;\n  height: auto !important;\n  object-fit: contain !important;\n}\n\n.block-container [data-testid="stElementContainer"]:has(iframe[title="streamlit_component"]) {\n  flex: 0 0 auto !important;\n  height: auto !important;\n  min-height: 0 !important;\n  margin: 0 !important;\n  overflow: visible !important;\n}\n\niframe[title="streamlit_component"] {\n  display: block !important;\n  width: 100% !important;\n  height: clamp(116px, 16.5dvh, 148px) !important;\n  min-height: 0 !important;\n  margin: 0 !important;\n}\n\n.section-title {\n  flex: 0 0 auto !important;\n  font-size: 19px !important;\n  line-height: 1.08 !important;\n  margin: 5px 0 7px !important;\n}\n\n.block-container > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.home-action-grid) {\n  flex: 1 1 0 !important;\n  width: 100% !important;\n  height: auto !important;\n  min-height: 0 !important;\n  margin: 0 !important;\n  padding: 0 !important;\n  overflow: visible !important;\n}\n\n.block-container > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.home-action-grid) > div {\n  width: 100% !important;\n  height: 100% !important;\n  min-height: 0 !important;\n  margin: 0 !important;\n  padding: 0 !important;\n}\n\n.home-action-grid {\n  display: grid !important;\n  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;\n  grid-template-rows: repeat(2, minmax(0, 1fr)) !important;\n  width: 100% !important;\n  height: 100% !important;\n  min-height: 0 !important;\n  gap: var(--home-gap) !important;\n  margin: 0 !important;\n  padding: 0 0 3px !important;\n  box-sizing: border-box !important;\n  align-items: stretch !important;\n}\n\n.home-action-card {\n  display: flex !important;\n  flex-direction: column !important;\n  justify-content: center !important;\n  width: 100% !important;\n  height: 100% !important;\n  min-width: 0 !important;\n  min-height: 0 !important;\n  box-sizing: border-box !important;\n  padding: clamp(10px, 1.8dvh, 15px) 12px !important;\n  border: 1.5px solid rgba(8,79,134,.36) !important;\n  border-radius: 15px !important;\n  background: #fff !important;\n  text-decoration: none !important;\n  box-shadow: 0 4px 0 rgba(8,79,134,.10), 0 9px 18px rgba(8,79,134,.08) !important;\n  overflow: hidden !important;\n}\n\n.home-action-card:hover {\n  border-color: rgba(8,79,134,.58) !important;\n  box-shadow: 0 6px 0 rgba(8,79,134,.13), 0 14px 28px rgba(8,79,134,.12) !important;\n}\n\n.home-action-card:active {\n  transform: translateY(2px);\n}\n\n.home-action-card .action-icon {\n  flex: 0 0 auto !important;\n  font-size: clamp(20px, 2.6dvh, 24px) !important;\n  line-height: 1 !important;\n  margin: 0 0 6px !important;\n}\n\n.home-action-card .action-title {\n  flex: 0 0 auto !important;\n  font-size: clamp(15px, 1.9dvh, 17px) !important;\n  line-height: 1.08 !important;\n  margin: 0 0 4px !important;\n}\n\n.home-action-card .action-copy {\n  flex: 0 1 auto !important;\n  font-size: clamp(10.5px, 1.3dvh, 12px) !important;\n  line-height: 1.2 !important;\n  margin: 0 !important;\n}\n\n.bottom-nav {\n  height: var(--home-nav-height) !important;\n  padding-bottom: max(7px, env(safe-area-inset-bottom)) !important;\n}\n\n/* Emergency fallback only: very short viewports may scroll, never clip. */\n@media (max-height: 650px) {\n  .block-container {\n    height: auto !important;\n    min-height: calc(100dvh - var(--home-nav-height)) !important;\n    padding-bottom: 10px !important;\n  }\n  .block-container > [data-testid="stVerticalBlock"] {\n    height: auto !important;\n    min-height: calc(100dvh - var(--home-nav-height) - 16px) !important;\n  }\n  iframe[title="streamlit_component"] {\n    height: 108px !important;\n  }\n  .block-container > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.home-action-grid) {\n    flex: 0 0 auto !important;\n  }\n  .block-container > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.home-action-grid) > div,\n  .home-action-grid {\n    height: auto !important;\n  }\n  .home-action-grid {\n    grid-template-rows: repeat(2, minmax(116px, auto)) !important;\n  }\n}\n</style>\n""",\n        unsafe_allow_html=True,\n    )\n\napproved_pcna_header(98 if page == "home" else 105)'''

source = source[:start] + home_css + source[end:]

# Give the homepage unique classes so global workflow-card styles cannot conflict with it.
home_start = source.index('if page == "home":\n    live_pcna_banner()')
home_end = source.index('\nelif page == "create":', home_start)
home = source[home_start:home_end]
home = home.replace('<div class="action-grid">', '<div class="home-action-grid">', 1)
home = home.replace('class="action-card"', 'class="home-action-card"')
source = source[:home_start] + home + source[home_end:]

# Sanity checks before making app.py authoritative.
assert 'display: flex !important;\n  flex-wrap: wrap' not in source[source.index('if page == "home":'):home_end]
assert 'flex: 0 0 280px' not in source[source.index('if page == "home":'):home_end]
assert '<div class="home-action-grid">' in source[home_start:home_end]
assert source[home_start:home_end].count('class="home-action-card"') == 4
assert 'grid-template-columns: repeat(2, minmax(0, 1fr))' in source
assert 'grid-template-rows: repeat(2, minmax(0, 1fr))' in source
assert 'overflow-y: hidden' not in source[source.index('if page == "home":'):home_end]

# app.py becomes the one and only application source. No runtime source loading/replacement.
app.write_text(source, encoding="utf-8")
legacy.unlink()

print("Homepage source overhaul complete: standalone app.py created and legacy source removed.")

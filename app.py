from pathlib import Path

source_path = Path(__file__).with_name("_pcna_app_source.py")
source = source_path.read_text(encoding="utf-8")

# Replace the legacy home-only layout rules with one clean custom HTML/CSS Flexbox
# implementation. The cards themselves are already rendered as raw HTML anchors by
# _pcna_app_source.py, so no st.columns or Streamlit card containers are used here.
start_marker = '''if page == "home":\n    st.markdown(\n        """\n<style>\n'''
end_marker = '''\n""",\n        unsafe_allow_html=True,\n    )\n\napproved_pcna_header(98 if page == "home" else 105)'''

start = source.index(start_marker)
end = source.index(end_marker, start) + len(end_marker)

home_layout = '''if page == "home":\n    st.markdown(\n        """\n<style>\n/* HOME — custom HTML/CSS card layout. No Streamlit columns. */\nhtml,\nbody,\n[data-testid="stAppViewContainer"],\n[data-testid="stAppViewContainer"] > .main {\n  width: 100%;\n  min-height: 100%;\n  height: auto !important;\n  overflow-x: hidden !important;\n  overflow-y: auto !important;\n}\n\n.block-container {\n  width: 100% !important;\n  max-width: 620px !important;\n  box-sizing: border-box !important;\n  margin: 0 auto !important;\n  padding: calc(10px + env(safe-area-inset-top)) 10px calc(96px + env(safe-area-inset-bottom)) !important;\n  overflow: visible !important;\n}\n\n.block-container > [data-testid="stVerticalBlock"] {\n  gap: 0 !important;\n}\n\n[data-testid="stImage"] {\n  margin: 0 0 4px !important;\n  padding: 0 !important;\n}\n\n[data-testid="stImage"] img {\n  display: block !important;\n  margin: 0 auto !important;\n  max-width: 100% !important;\n  height: auto !important;\n  object-fit: contain !important;\n}\n\niframe[title="streamlit_component"] {\n  display: block !important;\n  width: 100% !important;\n  height: 150px !important;\n  margin: 0 !important;\n}\n\n.section-title {\n  font-size: 20px !important;\n  line-height: 1.08 !important;\n  margin: 8px 0 10px !important;\n}\n\n/* The card wrapper is a pure CSS Flexbox layout. */\n.action-grid {\n  display: flex !important;\n  flex-wrap: wrap !important;\n  gap: 20px !important;\n  justify-content: center !important;\n  align-items: stretch !important;\n  width: 100% !important;\n  margin: 0 !important;\n  padding: 0 !important;\n  box-sizing: border-box !important;\n}\n\n.action-card {\n  display: flex !important;\n  flex-direction: column !important;\n  justify-content: flex-start !important;\n  flex: 0 0 280px !important;\n  width: 280px !important;\n  max-width: 280px !important;\n  min-width: 0 !important;\n  box-sizing: border-box !important;\n  padding: 14px !important;\n  border-radius: 16px !important;\n  text-decoration: none !important;\n  overflow: hidden !important;\n}\n\n.action-icon {\n  font-size: 22px !important;\n  line-height: 1 !important;\n  margin: 0 0 7px !important;\n}\n\n.action-title {\n  font-size: 16px !important;\n  line-height: 1.1 !important;\n  margin: 0 0 5px !important;\n}\n\n.action-copy {\n  font-size: 11.5px !important;\n  line-height: 1.24 !important;\n  margin: 0 !important;\n}\n\n.bottom-nav {\n  height: 76px !important;\n}\n\n/* On phones, preserve the 280px maximum but allow the card to fit a narrower viewport. */\n@media (max-width: 340px) {\n  .action-card {\n    flex-basis: calc(100vw - 28px) !important;\n    width: calc(100vw - 28px) !important;\n    max-width: 280px !important;\n  }\n}\n</style>\n""",\n        unsafe_allow_html=True,\n    )\n\napproved_pcna_header(98 if page == "home" else 105)'''

source = source[:start] + home_layout + source[end:]

exec(compile(source, str(source_path), "exec"), globals(), globals())

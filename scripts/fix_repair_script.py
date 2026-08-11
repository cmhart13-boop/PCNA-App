from pathlib import Path
p=Path('scripts/repair_home_from_screenshot.py')
s=p.read_text(encoding='utf-8')
s=s.replace("new = r'''def render_streamlit_mobile_home():", 'new = r\"\"\"def render_streamlit_mobile_home():', 1)
s=s.replace("\n'''\ns = s[:start] + new + s[end:]", '\n\"\"\"\ns = s[:start] + new + s[end:]', 1)
p.write_text(s, encoding='utf-8')
print('repair script quoting fixed')

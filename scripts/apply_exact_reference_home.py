from pathlib import Path
import re

path = Path('app.py')
text = path.read_text()

if 'from home_reference import render_reference_home' not in text:
    text = text.replace('from generation import generate_concepts\n', 'from generation import generate_concepts\nfrom home_reference import render_reference_home\n', 1)

home_pattern = re.compile(r'if page == "home":.*?\nelif page == "create":', re.S)
new_home = '''if page == "home":
    render_reference_home()

elif page == "create":'''
text, count = home_pattern.subn(new_home, text, count=1)
if count != 1:
    raise SystemExit('Could not locate homepage block')

text = text.replace('\nbottom_nav(page)\n', '\nif page != "home":\n    bottom_nav(page)\n')

path.write_text(text)

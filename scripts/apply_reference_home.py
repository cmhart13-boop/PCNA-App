from pathlib import Path
import re

path = Path("app.py")
text = path.read_text()

text = text.replace("from home_reference import render_reference_home\n", "")
text = text.replace("from home_ui import render_home\n", "")
text = text.replace("from generation import generate_concepts\n", "from generation import generate_concepts\nfrom home_ui import render_home\n")

text, count = re.subn(
    r'if page == "home":.*?\nelif page == "create":',
    'if page == "home":\n    render_home()\n\nelif page == "create":',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit("Could not replace homepage block")

path.write_text(text)

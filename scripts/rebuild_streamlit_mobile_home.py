from pathlib import Path

path = Path('app.py')
source = path.read_text(encoding='utf-8')

helper_marker = '\ndef render_streamlit_mobile_home():\n'
if helper_marker in source:
    start = source.index(helper_marker)
    end = source.index('\n\npage = current_page()', start)
    source = source[:start] + source[end:]

helper = r'''

def render_streamlit_mobile_home():
    """Render the entire mobile home screen inside one controlled viewport.

    Streamlit remains responsible for routing and the functional pages, but it
    does not lay out the mobile home cards. That prevents Streamlit block gaps,
    responsive column stacking, iframe whitespace, and clipped cards on iOS.
    """
    import base64

    def asset(path_name: str) -> str:
        p = Path(path_name)
        if not p.exists():
            return ""
        suffix = p.suffix.lower()
        mime = "image/webp" if suffix == ".webp" else "image/png" if suffix == ".png" else "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")

    logo = asset("IMG_2337.webp") or asset("assets/pcna-logo.webp")
    hero = asset("450DC5D7-11B1-447D-91EC-74CB1CFFDCA8.png")
    card_a = asset("IMG_2345.png") or hero
    card_b = asset("IMG_2348.jpeg") or hero

    st.markdown(
        """
<style>
body:has(.pcna-mobile-root-marker) .block-container {
  width: 100% !important;
  max-width: none !important;
  padding: 0 !important;
  margin: 0 !important;
}
body:has(.pcna-mobile-root-marker) [data-testid="stAppViewContainer"] > .main {
  overflow: hidden !important;
}
body:has(.pcna-mobile-root-marker) [data-testid="stElementContainer"] {
  margin: 0 !important;
  padding: 0 !important;
}
body:has(.pcna-mobile-root-marker) iframe[title="streamlit_component"] {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important;
  height: 100dvh !important;
  min-height: 100dvh !important;
  border: 0 !important;
  margin: 0 !important;
  z-index: 10000 !important;
}
</style>
<div class="pcna-mobile-root-marker"></div>
""",
        unsafe_allow_html=True,
    )

    hero_style = (
        f"background-image:linear-gradient(90deg,rgba(0,38,92,.93),rgba(0,69,145,.35)),url('{hero}');"
        if hero
        else "background:linear-gradient(135deg,#002f6c,#075aa8);"
    )

    html = f'''<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<style>
*{{box-sizing:border-box}}
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color:#082f66}}
.shell{{height:100dvh;display:grid;grid-template-rows:48px minmax(0,1fr) 68px;gap:8px;padding:max(9px,env(safe-area-inset-top)) 12px max(8px,env(safe-area-inset-bottom));background:#fff}}
.header{{display:grid;grid-template-columns:44px 1fr 44px;align-items:center;min-height:0}}
.menu,.bell{{color:#063b78;font-size:29px;line-height:1;text-align:center}}
.bell{{font-size:25px}}
.logo{{height:38px;max-width:155px;object-fit:contain;justify-self:center}}
.content{{min-height:0;display:grid;grid-template-rows:minmax(150px,26%) auto minmax(0,1fr);gap:7px}}
.hero{{position:relative;overflow:hidden;border-radius:17px;{hero_style}background-size:cover;background-position:center;box-shadow:0 4px 16px rgba(8,59,122,.15);text-decoration:none}}
.hero:after{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,34,87,.86) 0%,rgba(0,42,101,.45) 45%,rgba(0,55,120,.05) 72%)}}
.hero-copy{{position:absolute;z-index:2;left:18px;top:15px;width:48%;color:#fff}}
.hero h1{{margin:0 0 7px;font-size:clamp(24px,7vw,38px);line-height:.98;letter-spacing:-.03em}}
.hero p{{margin:0 0 11px;font-size:clamp(11px,3vw,16px);line-height:1.24}}
.shop{{display:inline-flex;border:2px solid #fff;border-radius:7px;padding:7px 15px;color:#fff;font-weight:800;font-size:12px}}
.section{{margin:1px 0 0;font-size:clamp(22px,6.4vw,34px);font-weight:850;line-height:1;letter-spacing:-.025em;color:#082f66}}
.underline{{display:block;width:61px;height:4px;border-radius:99px;background:#28aae1;margin-top:6px}}
.grid{{min-height:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(2,minmax(0,1fr));gap:9px}}
.card{{position:relative;min-width:0;min-height:0;overflow:hidden;border:1px solid #d7e8f6;border-radius:17px;background:#fff;box-shadow:0 4px 17px rgba(9,79,145,.17);text-decoration:none;color:#092957;padding:11px 10px}}
.icon{{position:relative;z-index:3;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#07519f;color:#fff;font-size:23px;font-weight:800}}
.card h2{{position:relative;z-index:3;margin:8px 0 5px;max-width:60%;font-size:clamp(17px,4.9vw,27px);line-height:.99;letter-spacing:-.03em}}
.card p{{position:relative;z-index:3;margin:0;max-width:56%;font-size:clamp(9.5px,2.55vw,14px);line-height:1.27;color:#294b6f}}
.cardimg{{position:absolute;right:-3%;bottom:0;width:60%;height:84%;object-fit:contain;object-position:right bottom;z-index:1;mix-blend-mode:multiply}}
.arrow{{position:absolute;right:9px;bottom:9px;z-index:4;width:37px;height:37px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#0754a1;color:#fff;font-size:25px;font-weight:700}}
.nav{{height:68px;border-radius:30px;background:linear-gradient(90deg,#08599f,#003372);display:grid;grid-template-columns:repeat(5,1fr);align-items:center;padding:4px}}
.nav a{{color:#fff;text-decoration:none;text-align:center;font-size:10px;opacity:.88}}
.nav b{{display:block;font-size:21px;line-height:1.05;margin-bottom:2px}}
.nav .active{{opacity:1;font-weight:800}}
@media(max-height:720px){{
.shell{{grid-template-rows:40px minmax(0,1fr) 58px;gap:5px;padding-top:max(6px,env(safe-area-inset-top))}}
.logo{{height:31px}} .menu{{font-size:25px}} .bell{{font-size:22px}}
.content{{grid-template-rows:minmax(118px,23%) auto minmax(0,1fr);gap:5px}}
.hero-copy{{left:14px;top:10px}} .hero h1{{font-size:23px}} .hero p{{font-size:10px;margin-bottom:7px}} .shop{{padding:5px 10px;font-size:10px}}
.section{{font-size:20px}} .underline{{height:3px;margin-top:4px}}
.grid{{gap:7px}} .card{{padding:8px}} .icon{{width:30px;height:30px;font-size:19px}}
.card h2{{margin:5px 0 3px;font-size:16px}} .card p{{font-size:9px}} .arrow{{width:30px;height:30px;font-size:20px}}
.nav{{height:58px}}
}}
</style>
</head>
<body>
<div class="shell">
  <div class="header">
    <div class="menu">☰</div>
    <img class="logo" src="{logo}" alt="PCNA">
    <div class="bell">♢</div>
  </div>
  <div class="content">
    <a class="hero" href="https://www.pcna.com/en-us" target="_blank" rel="noopener noreferrer">
      <div class="hero-copy">
        <h1>Branded.<br>Merchandise.<br>Delivered.</h1>
        <p>Explore thousands of promotional products to elevate your brand.</p>
        <span class="shop">SHOP NOW</span>
      </div>
    </a>
    <div class="section">What do you need?<span class="underline"></span></div>
    <div class="grid">
      <a class="card" href="?page=spec" target="_top">
        <div class="icon">✓</div><h2>Spec Sample<br>Order</h2>
        <p>Tell Nova what you need and build the verified PCNA order.</p>
        <img class="cardimg" src="{card_a}" alt=""><span class="arrow">→</span>
      </a>
      <a class="card" href="?page=virtual" target="_top">
        <div class="icon">◇</div><h2>Virtuals /<br>Designs</h2>
        <p>Ask Nova for product, kit or packaging virtuals and keep them in Projects.</p>
        <img class="cardimg" src="{card_b}" alt=""><span class="arrow">→</span>
      </a>
      <a class="card" href="?page=quote" target="_top">
        <div class="icon">$</div><h2>Quote<br>Request</h2>
        <p>Quote a verified PCNA product at the requested quantity.</p>
        <img class="cardimg" src="{card_b}" alt=""><span class="arrow">→</span>
      </a>
      <a class="card" href="?page=projects" target="_top">
        <div class="icon">□</div><h2>Projects</h2>
        <p>View and manage your saved projects, orders and virtuals in one place.</p>
        <img class="cardimg" src="{card_a}" alt=""><span class="arrow">→</span>
      </a>
    </div>
  </div>
  <div class="nav">
    <a class="active" href="?page=home" target="_top"><b>⌂</b>Home</a>
    <a href="?page=projects" target="_top"><b>▱</b>Projects</a>
    <a href="?page=search" target="_top"><b>◇</b>Products</a>
    <a href="?page=virtual" target="_top"><b>◯</b>Messages</a>
    <a href="?page=create" target="_top"><b>♙</b>Account</a>
  </div>
</div>
</body>
</html>'''
    components.html(html, height=900, scrolling=False)
'''

page_marker = '\n\npage = current_page()'
insert_at = source.index(page_marker)
source = source[:insert_at] + helper + source[insert_at:]

home_start = source.index('if page == "home":')
create_start = source.index('\nelif page == "create":', home_start)
new_home = '''if page == "home":\n    render_streamlit_mobile_home()\n    st.stop()\n'''
source = source[:home_start] + new_home + source[create_start:]

path.write_text(source, encoding='utf-8')
print('Rebuilt app.py home as one Streamlit-controlled viewport shell')

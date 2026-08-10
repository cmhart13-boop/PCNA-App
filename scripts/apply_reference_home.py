from pathlib import Path
import re

path = Path("app.py")
text = path.read_text()

# Approved-reference homepage styles. These are intentionally scoped to the homepage shell.
css_anchor = '</style>\n""",\n    unsafe_allow_html=True,\n)'
home_css = r'''
/* Approved PCNA homepage reference layout */
.home-topbar{height:74px;display:grid;grid-template-columns:64px 1fr 64px;align-items:center;margin:-12px 2px 12px}.home-logo{display:block;width:145px;max-height:54px;object-fit:contain;justify-self:center}.home-menu,.home-bell{display:flex;align-items:center;justify-content:center;width:46px;height:46px;color:#043f79!important;text-decoration:none!important}.home-menu{flex-direction:column;gap:5px;justify-self:start}.home-menu span{height:4px;width:31px;background:#043f79;border-radius:4px}.home-bell{justify-self:end;font-size:27px}.home-bell svg{width:28px;height:28px;stroke:#043f79;fill:none;stroke-width:2}
.home-section-title{font-size:25px;font-weight:900;letter-spacing:-.025em;color:#052f68;margin:9px 11px 0}.home-title-underline{height:3px;width:42px;border-radius:2px;background:#24a6e0;margin:5px 0 10px 11px;box-shadow:0 4px 8px rgba(36,166,224,.25)}
.home-action-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:0 2px 10px}.home-action-card{position:relative;display:block;height:238px;overflow:hidden;text-decoration:none!important;border:1px solid rgba(9,80,146,.16);border-radius:16px;background:#fff;padding:16px 14px;box-sizing:border-box;box-shadow:0 0 8px rgba(21,136,220,.24),0 7px 14px rgba(0,55,110,.10)}.home-card-icon{width:44px;height:44px;border-radius:50%;background:#064b91;color:#fff;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;margin-bottom:13px}.home-card-title{position:relative;z-index:2;color:#052f68;font-size:21px;line-height:1.02;font-weight:900;letter-spacing:-.025em;max-width:72%}.home-card-copy{position:relative;z-index:2;color:#173b63;font-size:12.5px;line-height:1.48;margin-top:11px;max-width:68%}.home-card-visual{position:absolute;right:12px;bottom:35px;width:43%;height:46%;opacity:.9}.home-card-visual:before,.home-card-visual:after{content:"";position:absolute;border:3px solid #183d66;border-radius:14px}.visual-bag:before{inset:5px 8px 0;border-radius:20px 20px 12px 12px}.visual-bag:after{width:36px;height:22px;left:50%;top:-7px;transform:translateX(-50%);border-bottom:0;border-radius:18px 18px 0 0}.visual-laptop:before{left:2px;right:2px;top:3px;bottom:22px;border-radius:7px}.visual-laptop:after{left:-8px;right:-8px;bottom:10px;height:5px;border-radius:8px}.visual-quote:before{inset:0 8px 8px;border-radius:9px}.visual-quote:after{left:19px;right:19px;bottom:22px;height:43px;border-width:0 0 3px 3px;border-radius:0;box-shadow:14px -8px 0 -10px #183d66,28px -24px 0 -10px #183d66}.visual-project:before{inset:3px 6px 0;border-radius:5px;transform:rotate(-7deg)}.visual-project:after{right:0;top:8px;width:8px;height:88%;border-radius:5px;background:#183d66;border:0;transform:rotate(-7deg)}.home-arrow{position:absolute;z-index:3;right:10px;bottom:10px;width:42px;height:42px;border-radius:50%;background:#064b91;color:#fff;display:flex;align-items:center;justify-content:center;font-size:29px;font-weight:500}
.bottom-nav{height:78px!important;width:min(590px,calc(100% - 24px))!important;bottom:9px!important;border:0!important;border-radius:38px!important;background:#064b91!important;box-shadow:0 8px 24px rgba(0,42,89,.16)!important;padding:6px 14px max(6px,env(safe-area-inset-bottom))!important;grid-template-columns:repeat(5,1fr)!important}.nav-item{color:#fff!important;font-size:11px!important;opacity:.96}.nav-icon{font-size:23px!important}.nav-item.active{color:#fff!important;background:transparent!important;position:relative}.nav-item.active:after{content:"";position:absolute;bottom:0;width:40px;height:3px;background:#fff;border-radius:4px}
@media(max-width:430px){.block-container{padding-top:calc(18px + env(safe-area-inset-top))!important;padding-left:12px!important;padding-right:12px!important;padding-bottom:104px!important}.home-topbar{height:68px}.home-logo{width:140px}.home-action-card{height:230px}.home-card-title{font-size:20px}.home-card-copy{font-size:12px}.pcna-live-shell{height:236px!important}}
@media(max-width:350px){.home-action-grid{grid-template-columns:1fr 1fr!important;gap:8px}.home-action-card{height:220px;padding:13px 11px}.home-card-title{font-size:18px}.home-card-copy{font-size:11px}.home-card-icon{width:39px;height:39px;font-size:22px}}
'''
if '/* Approved PCNA homepage reference layout */' not in text:
    text = text.replace(css_anchor, home_css + '\n' + css_anchor, 1)

marker = 'def live_pcna_banner():'
if 'def home_header():' not in text:
    header = '''def home_header():
    st.markdown(
        """
<div class="home-topbar">
  <a class="home-menu" href="?page=create" aria-label="Menu"><span></span><span></span><span></span></a>
  <img class="home-logo" src="https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/pcna-logo.webp" alt="PCNA">
  <a class="home-bell" href="?page=assistant" aria-label="Notifications and messages">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"></path><path d="M10 21h4"></path></svg>
  </a>
</div>
""",
        unsafe_allow_html=True,
    )


'''
    text = text.replace(marker, header + marker, 1)

# Make the existing approved PCNA.com integration match the reference hero proportions.
text = text.replace('height:228px;overflow:hidden;border-radius:14px', 'height:244px;overflow:hidden;border-radius:18px')
text = text.replace('height=228,', 'height=244,')
text = text.replace('.pcna-live-shell{height:208px}', '.pcna-live-shell{height:236px}')

nav_pattern = re.compile(r'def bottom_nav\(page: str\):.*?\n\n\ndef persistent_projects\(\):', re.S)
new_nav = '''def bottom_nav(page: str):
    group = page
    if page == "virtual":
        group = "projects" if st.query_params.get("view", "new") == "projects" else "virtual"
    st.markdown(
        f"""
<div class="bottom-nav">
<a class="nav-item {'active' if group=='home' else ''}" href="{nav_link('home')}"><span class="nav-icon">⌂</span><span>Home</span></a>
<a class="nav-item {'active' if group=='projects' else ''}" href="{virtual_projects_link()}"><span class="nav-icon">□</span><span>Projects</span></a>
<a class="nav-item {'active' if group=='search' else ''}" href="{nav_link('search')}"><span class="nav-icon">◇</span><span>Products</span></a>
<a class="nav-item {'active' if group=='assistant' else ''}" href="{nav_link('assistant')}"><span class="nav-icon">◯</span><span>Messages</span></a>
<a class="nav-item {'active' if group=='data' else ''}" href="{nav_link('data')}"><span class="nav-icon">♙</span><span>Account</span></a>
</div>
""",
        unsafe_allow_html=True,
    )


def persistent_projects():'''
text, count = nav_pattern.subn(new_nav, text, count=1)
if count != 1:
    raise SystemExit('Could not locate bottom navigation function')

home_pattern = re.compile(r'if page == "home":.*?\nelif page == "create":', re.S)
new_home = '''if page == "home":
    home_header()
    live_pcna_banner()
    st.markdown('<div class="home-section-title">What do you need?</div><div class="home-title-underline"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="home-action-grid">
<a class="home-action-card" href="{nav_link('spec')}">
  <div class="home-card-icon">✓</div><div class="home-card-title">Spec Sample<br>Order</div>
  <div class="home-card-copy">Tell Nova what you need and build the verified PCNA order.</div>
  <div class="home-card-visual visual-bag" aria-hidden="true"></div><div class="home-arrow">→</div>
</a>
<a class="home-action-card" href="{nav_link('virtual')}">
  <div class="home-card-icon">◇</div><div class="home-card-title">Virtuals /<br>Designs</div>
  <div class="home-card-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div>
  <div class="home-card-visual visual-laptop" aria-hidden="true"></div><div class="home-arrow">→</div>
</a>
<a class="home-action-card" href="{nav_link('quote')}">
  <div class="home-card-icon">$</div><div class="home-card-title">Quote<br>Request</div>
  <div class="home-card-copy">Quote a verified PCNA product at the requested quantity.</div>
  <div class="home-card-visual visual-quote" aria-hidden="true"></div><div class="home-arrow">→</div>
</a>
<a class="home-action-card" href="{virtual_projects_link()}">
  <div class="home-card-icon">□</div><div class="home-card-title">Projects</div>
  <div class="home-card-copy">View and manage your saved projects, orders and virtuals in one place.</div>
  <div class="home-card-visual visual-project" aria-hidden="true"></div><div class="home-arrow">→</div>
</a>
</div>
""",
        unsafe_allow_html=True,
    )

elif page == "create":'''
text, count = home_pattern.subn(new_home, text, count=1)
if count != 1:
    raise SystemExit('Could not locate homepage block')

path.write_text(text)

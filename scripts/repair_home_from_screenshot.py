from pathlib import Path

p = Path('app.py')
s = p.read_text(encoding='utf-8')
start = s.index('def render_streamlit_mobile_home():')
end = s.index('\n\npage = current_page()', start)
new = r'''def render_streamlit_mobile_home():
    """Compact native Streamlit mobile home matching the approved screenshot structure."""
    import base64

    def asset(path_name: str) -> str:
        path = Path(path_name)
        if not path.exists():
            return ""
        suffix = path.suffix.lower()
        mime = "image/webp" if suffix == ".webp" else "image/png" if suffix == ".png" else "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")

    logo = asset("assets/pcna-logo.webp") or asset("IMG_2337.webp")

    st.markdown(
        f'''
<div class="pcna-home">
  <div class="pcna-head">
    <span class="pcna-head-icon">☰</span>
    <img src="{logo}" class="pcna-head-logo" alt="PCNA">
    <span class="pcna-head-icon pcna-head-bell">◇</span>
  </div>

  <a class="pcna-hero" href="https://www.pcna.com/en-us" target="_blank" rel="noopener noreferrer">
    <div class="pcna-hero-copy">
      <div class="pcna-hero-title">Branded.<br>Merchandise.<br>Delivered.</div>
      <div class="pcna-hero-sub">Explore thousands of promotional products to elevate your brand.</div>
      <span class="pcna-shop">SHOP NOW</span>
    </div>
    <div class="hero-products" aria-hidden="true">
      <div class="hero-bag"></div><div class="hero-tumbler"></div><div class="hero-shirt">PCNA</div><div class="hero-cap">PCNA</div>
    </div>
  </a>

  <div class="pcna-section-title">What do you need?<span></span></div>

  <div class="pcna-grid">
    <a class="pcna-card" href="?page=spec">
      <div class="pcna-card-icon">✓</div>
      <div class="pcna-card-title">Spec Sample<br>Order</div>
      <div class="pcna-card-sub">Tell Nova what you need and build the verified PCNA order.</div>
      <div class="card-art backpack" aria-hidden="true"><div></div></div>
      <div class="pcna-arrow">→</div>
    </a>
    <a class="pcna-card" href="?page=virtual">
      <div class="pcna-card-icon">◇</div>
      <div class="pcna-card-title">Virtuals /<br>Designs</div>
      <div class="pcna-card-sub">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div>
      <div class="card-art laptop" aria-hidden="true"><div class="screen">NORTHPOINT<br><small>SOLUTIONS</small></div></div>
      <div class="pcna-arrow">→</div>
    </a>
    <a class="pcna-card" href="?page=quote">
      <div class="pcna-card-icon">$</div>
      <div class="pcna-card-title">Quote<br>Request</div>
      <div class="pcna-card-sub">Quote a verified PCNA product at the requested quantity.</div>
      <div class="card-art quote-sheet" aria-hidden="true"><div class="qline"></div><div class="qline short"></div><div class="qbars"></div></div>
      <div class="pcna-arrow">→</div>
    </a>
    <a class="pcna-card" href="?page=projects">
      <div class="pcna-card-icon">□</div>
      <div class="pcna-card-title">Projects</div>
      <div class="pcna-card-sub">View and manage your saved projects, orders and virtuals in one place.</div>
      <div class="card-art notebook" aria-hidden="true"><div class="elastic"></div></div>
      <div class="pcna-arrow">→</div>
    </a>
  </div>
</div>

<nav class="pcna-mobile-nav">
  <a class="active" href="?page=home"><b>⌂</b><span>Home</span></a>
  <a href="?page=projects"><b>▱</b><span>Projects</span></a>
  <a href="?page=search"><b>◇</b><span>Products</span></a>
  <a href="?page=virtual"><b>◯</b><span>Messages</span></a>
  <a href="?page=create"><b>♙</b><span>Account</span></a>
</nav>

<style>
:root{{--pcna-navy:#063f80;--pcna-blue:#075ca8;--cyan:#27afe2}}
[data-testid="stAppViewContainer"]>.main{{overflow-y:auto!important}}
.block-container:has(.pcna-home){{max-width:620px!important;padding:calc(4px + env(safe-area-inset-top)) 12px calc(78px + env(safe-area-inset-bottom))!important}}
.block-container:has(.pcna-home)>[data-testid="stVerticalBlock"]{{gap:0!important}}
.block-container:has(.pcna-home) [data-testid="stElementContainer"]{{margin:0!important}}
.pcna-home{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color:#082f66}}
.pcna-head{{height:54px;display:grid;grid-template-columns:44px 1fr 44px;align-items:center;margin:0 0 6px}}
.pcna-head-logo{{height:38px;max-width:150px;object-fit:contain;justify-self:center}}
.pcna-head-icon{{font-size:29px;line-height:1;text-align:center;color:#063f80;font-weight:700}}
.pcna-head-bell{{font-size:26px}}
.pcna-hero{{position:relative;display:block;height:188px;border-radius:17px;overflow:hidden;text-decoration:none!important;background:linear-gradient(135deg,#032f67 0%,#07589e 58%,#0b6db2 100%);box-shadow:0 5px 18px rgba(8,65,120,.18)}}
.pcna-hero:before{{content:"";position:absolute;inset:0;background:linear-gradient(115deg,rgba(0,28,72,.92) 0 45%,rgba(0,35,82,.12) 72%)}}
.pcna-hero-copy{{position:absolute;z-index:3;left:18px;top:18px;width:48%;color:white}}
.pcna-hero-title{{font-size:clamp(28px,7.2vw,40px);font-weight:900;line-height:.98;letter-spacing:-.035em}}
.pcna-hero-sub{{font-size:clamp(11px,2.85vw,15px);line-height:1.25;margin:10px 0 12px}}
.pcna-shop{{display:inline-block;border:2px solid white;border-radius:7px;padding:8px 16px;font-size:12px;font-weight:900;color:white}}
.hero-products{{position:absolute;right:9px;bottom:5px;width:53%;height:90%;z-index:2}}
.hero-bag{{position:absolute;left:2%;bottom:2%;width:42%;height:80%;border-radius:16px 16px 12px 12px;background:linear-gradient(145deg,#747d86,#414a54);box-shadow:inset -8px 0 16px rgba(0,0,0,.18)}}
.hero-bag:before{{content:"";position:absolute;left:22%;right:22%;top:-12%;height:18%;border:6px solid #525b64;border-bottom:0;border-radius:20px 20px 0 0}}
.hero-bag:after{{content:"";position:absolute;left:13%;right:13%;top:33%;height:35%;border-radius:10px;border:2px solid rgba(255,255,255,.12)}}
.hero-tumbler{{position:absolute;left:43%;bottom:0;width:22%;height:62%;border-radius:10px 10px 18px 18px;background:linear-gradient(90deg,#123e70,#0b5597 60%,#073868);box-shadow:inset -6px 0 10px rgba(0,0,0,.18)}}
.hero-tumbler:after{{content:"PCNA";position:absolute;color:white;font-weight:900;font-size:10px;top:43%;left:13%}}
.hero-shirt{{position:absolute;right:1%;top:4%;width:40%;height:48%;clip-path:polygon(20% 0,38% 10%,62% 10%,80% 0,100% 19%,83% 38%,83% 100%,17% 100%,17% 38%,0 19%);background:#102f58;color:white;font-size:10px;font-weight:900;text-align:center;padding-top:29%}}
.hero-cap{{position:absolute;right:5%;bottom:0;width:34%;height:29%;border-radius:50% 50% 38% 38%;background:#a9afb4;color:#063f80;font-size:9px;font-weight:900;text-align:center;padding-top:11%}}
.pcna-section-title{{font-size:clamp(25px,6.4vw,35px);font-weight:900;line-height:1;color:#082f66;margin:12px 0 10px;letter-spacing:-.03em}}
.pcna-section-title span{{display:block;width:62px;height:4px;border-radius:99px;background:var(--cyan);margin-top:7px}}
.pcna-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));grid-template-rows:repeat(2,210px);gap:10px}}
.pcna-card{{position:relative;overflow:hidden;border:1px solid #cfe0ef;border-radius:17px;background:white;box-shadow:0 4px 16px rgba(9,75,135,.15);text-decoration:none!important;color:#082f66;padding:13px 12px}}
.pcna-card-icon{{width:40px;height:40px;border-radius:50%;background:#075ba7;color:white;display:flex;align-items:center;justify-content:center;font-size:25px;font-weight:800;position:relative;z-index:4}}
.pcna-card-title{{font-size:clamp(20px,5.2vw,27px);font-weight:900;line-height:1;letter-spacing:-.03em;margin:9px 0 8px;position:relative;z-index:4;max-width:58%}}
.pcna-card-sub{{font-size:clamp(10px,2.65vw,14px);line-height:1.25;color:#29496c;max-width:56%;position:relative;z-index:4}}
.pcna-arrow{{position:absolute;right:10px;bottom:10px;width:40px;height:40px;border-radius:50%;background:#075aa7;color:white;display:flex;align-items:center;justify-content:center;font-size:27px;font-weight:800;z-index:5}}
.card-art{{position:absolute;right:0;bottom:0;width:57%;height:83%;z-index:2}}
.backpack{{right:-2%;bottom:-2%}}
.backpack>div{{position:absolute;right:8%;bottom:0;width:72%;height:92%;border-radius:20px 20px 10px 10px;background:linear-gradient(145deg,#0d4b91,#062f66);box-shadow:inset -8px 0 14px rgba(0,0,0,.18)}}
.backpack>div:before{{content:"";position:absolute;left:20%;right:20%;top:-8%;height:17%;border:5px solid #0b3b76;border-bottom:0;border-radius:18px 18px 0 0}}
.backpack>div:after{{content:"";position:absolute;left:14%;right:14%;top:34%;height:37%;border:2px solid rgba(255,255,255,.15);border-radius:10px}}
.laptop{{right:-1%;bottom:5%;height:70%}}
.laptop:before{{content:"";position:absolute;right:5%;bottom:16%;width:88%;height:64%;border:7px solid #1f2831;border-radius:6px;background:#162130;box-sizing:border-box}}
.laptop:after{{content:"";position:absolute;right:-2%;bottom:7%;width:100%;height:9%;background:#9ca5ad;transform:skewX(-10deg);border-radius:2px}}
.laptop .screen{{position:absolute;right:15%;bottom:34%;width:66%;text-align:center;color:white;font-weight:800;font-size:9px;z-index:3}}
.laptop small{{font-size:5px;letter-spacing:.12em}}
.quote-sheet{{right:3%;bottom:5%;width:49%;height:78%;background:#f6f8fb;border:6px solid #30363d;border-radius:9px;transform:rotate(3deg);box-shadow:0 5px 12px rgba(0,0,0,.15)}}
.quote-sheet:before{{content:"QUOTE SUMMARY";position:absolute;top:8%;left:10%;font-size:7px;font-weight:900;color:#26394f}}
.qline{{position:absolute;left:10%;right:10%;top:28%;height:3px;background:#b9c9d8;box-shadow:0 14px 0 #b9c9d8,0 28px 0 #b9c9d8,0 42px 0 #b9c9d8}}
.qline.short{{right:35%;top:35%}}
.qbars{{position:absolute;left:13%;bottom:10%;width:55%;height:24%;background:linear-gradient(to right,transparent 0 8%,#5f86ad 8% 18%,transparent 18% 28%,#5f86ad 28% 43%,transparent 43% 54%,#5f86ad 54% 70%,transparent 70% 79%,#5f86ad 79% 94%)}}
.notebook{{right:5%;bottom:3%;width:48%;height:80%;border-radius:8px;background:linear-gradient(145deg,#3a3d40,#181a1c);transform:rotate(7deg);box-shadow:0 5px 12px rgba(0,0,0,.2)}}
.notebook:before{{content:"P";position:absolute;left:43%;top:40%;font-size:28px;color:#24272a;font-weight:900;text-shadow:0 1px 0 #555}}
.notebook .elastic{{position:absolute;right:13%;top:0;bottom:0;width:7%;background:#08090a}}
.pcna-mobile-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:0;width:min(620px,100%);height:calc(68px + env(safe-area-inset-bottom));padding:4px 8px env(safe-area-inset-bottom);box-sizing:border-box;border-radius:30px 30px 0 0;background:linear-gradient(90deg,#075ca8,#00326d);display:grid;grid-template-columns:repeat(5,1fr);z-index:99999}}
.pcna-mobile-nav a{{display:flex;flex-direction:column;align-items:center;justify-content:center;color:rgba(255,255,255,.82)!important;text-decoration:none!important;font-size:10px;gap:2px}}
.pcna-mobile-nav b{{font-size:24px;line-height:1}}
.pcna-mobile-nav .active{{color:white!important;font-weight:800}}
@media(max-width:430px){{
  .block-container:has(.pcna-home){{padding-left:10px!important;padding-right:10px!important;padding-top:calc(2px + env(safe-area-inset-top))!important}}
  .pcna-head{{height:50px;margin-bottom:5px}} .pcna-head-logo{{height:34px}}
  .pcna-hero{{height:176px}}
  .pcna-grid{{grid-template-rows:repeat(2,198px);gap:9px}}
  .pcna-card{{padding:11px 10px}}
  .pcna-card-icon{{width:36px;height:36px;font-size:22px}}
}}
@media(max-height:760px){{
  .pcna-head{{height:44px}} .pcna-head-logo{{height:31px}} .pcna-hero{{height:154px}}
  .pcna-section-title{{font-size:24px;margin:8px 0 7px}}
  .pcna-grid{{grid-template-rows:repeat(2,170px);gap:7px}}
  .pcna-card-title{{font-size:18px;margin:6px 0 5px}} .pcna-card-sub{{font-size:9.5px}}
  .pcna-card-icon{{width:32px;height:32px;font-size:20px}}
}}
</style>
''',
        unsafe_allow_html=True,
    )
'''
s = s[:start] + new + s[end:]
s = s.replace(
    'page = current_page()\napproved_pcna_header(98 if page == "home" else 105)\n\nif page == "home":',
    'page = current_page()\nif page != "home":\n    approved_pcna_header(105)\n\nif page == "home":',
    1,
)
s = s.replace('    components.html(html, height=900, scrolling=False)\n', '')
p.write_text(s, encoding='utf-8')
print('Repaired PCNA home from screenshot: no duplicate header, no screenshot-in-card assets, native compact grid.')

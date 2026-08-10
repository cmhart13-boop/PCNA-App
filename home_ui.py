from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

LOGO_URL = "https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/pcna-logo.webp"

# Real PCNA / Polyconcept photography already approved for the app.
PCNA_SPEC_PHOTO = "https://assets.pcna.com/image/upload/f_auto%2Cq_auto/Mkt_Dept/2026%20Jobs/2026-9854_0309_POW/9854_7901-56_0309_POW_B1.jpg"
PCNA_VIRTUAL_PHOTO = "https://assets.pcna.com/image/upload/f_auto%2Cq_auto/Mkt_Dept/2026%20Jobs/2026-9857_0216_POW/9857_2900-61_0216_POW_B1.jpg"
PCNA_QUOTE_PHOTO = "https://www.trimarksportswear.com/trimarknew/product/2100hires/12937938_D_on-model-front-uman-logo.jpg"
PCNA_PROJECT_PHOTO = "https://www.trimarksportswear.com/trimarknew/product/2100hires/12937_358_B_OFF.jpg"


def _hero() -> None:
    """Render the existing live PCNA.com hero in the reference's wide mobile proportions."""
    components.html(
        """
<div class="pcna-live-shell">
  <div class="pcna-live-fallback"><a href="https://www.pcna.com/en-us" target="_blank" rel="noopener">SHOP NOW</a></div>
  <iframe src="https://www.pcna.com/en-us" title="Live PCNA.com promotional hero" loading="eager"></iframe>
</div>
<style>
html,body{margin:0;padding:0;background:#fff;overflow:hidden}
.pcna-live-shell{position:relative;height:150px;overflow:hidden;border-radius:16px;background:#052f68}
.pcna-live-shell iframe{position:absolute;z-index:2;left:0;top:-74px;width:100%;height:500px;border:0;background:#052f68}
.pcna-live-fallback{position:absolute;z-index:1;inset:0;display:flex;align-items:flex-end;padding:0 0 17px 18px;box-sizing:border-box;background:#052f68}
.pcna-live-fallback a{color:#fff;text-decoration:none;font:800 11px -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;border:1.5px solid #fff;border-radius:6px;padding:9px 16px}
@media(max-width:370px){.pcna-live-shell{height:142px}.pcna-live-shell iframe{top:-70px;height:480px}}
</style>
""",
        height=152,
        scrolling=False,
    )


def render_home() -> None:
    st.markdown(
        f"""
<style>
[data-testid="stAppViewContainer"]>.main{{overflow-x:hidden!important;background:#fff!important}}
[data-testid="stHeader"]{{height:0!important;min-height:0!important;background:transparent!important}}
[data-testid="stToolbar"]{{display:none!important}}
.block-container{{max-width:620px!important;padding:calc(3px + env(safe-area-inset-top)) 11px calc(73px + env(safe-area-inset-bottom))!important;margin:0 auto!important}}

.home-topbar{{height:57px;display:grid;grid-template-columns:50px 1fr 50px;align-items:center;margin:0 5px 7px;background:#fff}}
.home-logo{{display:block;width:140px;height:44px;object-fit:contain;justify-self:center}}
.home-menu,.home-bell{{display:flex;align-items:center;justify-content:center;width:40px;height:40px;color:#052f68!important;text-decoration:none!important}}
.home-menu{{flex-direction:column;gap:4px;justify-self:start}}
.home-menu span{{display:block;height:3px;width:27px;background:#052f68;border-radius:4px}}
.home-bell{{justify-self:end}}
.home-bell svg{{width:25px;height:25px;stroke:#052f68;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}

.home-section-title{{font-size:22px;font-weight:900;letter-spacing:-.035em;color:#052f68;margin:7px 9px 0;line-height:1.02}}
.home-title-underline{{height:3px;width:36px;border-radius:4px;background:#27a9e1;margin:6px 0 8px 9px;box-shadow:0 2px 5px rgba(39,169,225,.18)}}

.home-action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:0 1px 7px}}
.home-action-card{{position:relative;display:block;height:145px;overflow:hidden;text-decoration:none!important;border:1px solid rgba(21,108,181,.13);border-radius:17px;background:#fff;padding:10px 9px;box-sizing:border-box;box-shadow:0 0 7px rgba(39,159,226,.20),0 4px 10px rgba(0,54,105,.07);-webkit-tap-highlight-color:transparent}}
.home-action-card:active{{transform:translateY(1px)}}
.home-card-icon{{position:relative;z-index:4;width:33px;height:33px;border-radius:50%;background:#064b91;color:#fff;display:flex;align-items:center;justify-content:center;margin-bottom:6px}}
.home-card-icon svg{{width:19px;height:19px;stroke:#fff;fill:none;stroke-width:2.15;stroke-linecap:round;stroke-linejoin:round}}
.home-card-icon.money{{font-size:22px;font-weight:450;line-height:1}}
.home-card-title{{position:relative;z-index:4;color:#052f68;font-size:15px;line-height:1.04;font-weight:900;letter-spacing:-.028em;max-width:55%}}
.home-card-copy{{position:relative;z-index:4;color:#173b63;font-size:8.8px;line-height:1.34;margin-top:6px;max-width:55%}}

/* Images intentionally sit like the approved reference: large, right weighted, no overlays/gradients. */
.home-card-photo{{position:absolute;z-index:1;right:-1px;bottom:0;width:49%;height:82%;object-fit:cover;object-position:center;background:#fff}}
.home-card-photo.spec{{width:52%;height:88%;object-position:58% 48%}}
.home-card-photo.virtual{{width:51%;height:80%;object-position:58% 48%}}
.home-card-photo.quote{{width:49%;height:80%;object-position:50% 44%}}
.home-card-photo.projects{{width:49%;height:82%;object-fit:contain;object-position:56% 52%}}
.home-arrow{{position:absolute;z-index:5;right:7px;bottom:7px;width:31px;height:31px;border-radius:50%;background:#064b91;color:#fff;display:flex;align-items:center;justify-content:center}}
.home-arrow svg{{width:18px;height:18px;stroke:#fff;fill:none;stroke-width:2.25;stroke-linecap:round;stroke-linejoin:round}}

.bottom-nav{{display:none!important}}
.home-bottom-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:max(6px,env(safe-area-inset-bottom));width:min(596px,calc(100% - 20px));height:60px;border-radius:31px;background:#064b91;box-shadow:0 5px 15px rgba(0,42,89,.14);display:grid;grid-template-columns:repeat(5,1fr);z-index:10000;padding:4px 8px;box-sizing:border-box}}
.home-nav-item{{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;color:#fff!important;font-size:9px;font-weight:600;gap:1px}}
.home-nav-icon{{width:21px;height:21px;display:flex;align-items:center;justify-content:center}}
.home-nav-icon svg{{width:20px;height:20px;stroke:#fff;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}
.home-nav-item.active:after{{content:"";position:absolute;bottom:0;width:31px;height:3px;background:#fff;border-radius:5px}}

@media(max-width:390px){{
  .block-container{{padding-left:9px!important;padding-right:9px!important;padding-bottom:calc(70px + env(safe-area-inset-bottom))!important}}
  .home-topbar{{height:53px;grid-template-columns:47px 1fr 47px;margin-bottom:5px}}
  .home-logo{{width:130px;height:41px}}
  .home-menu,.home-bell{{width:38px;height:38px}}
  .home-menu span{{width:25px}}
  .home-bell svg{{width:23px;height:23px}}
  .home-section-title{{font-size:20.5px;margin-top:5px}}
  .home-title-underline{{width:34px;margin-bottom:7px}}
  .home-action-grid{{gap:7px}}
  .home-action-card{{height:141px;border-radius:16px;padding:9px 8px}}
  .home-card-icon{{width:31px;height:31px;margin-bottom:5px}}
  .home-card-icon svg{{width:18px;height:18px}}
  .home-card-title{{font-size:14.2px}}
  .home-card-copy{{font-size:8.2px;line-height:1.31;margin-top:5px}}
  .home-arrow{{width:29px;height:29px;right:6px;bottom:6px}}
  .home-bottom-nav{{height:58px;border-radius:30px}}
}}
@media(max-width:360px){{
  .home-action-grid{{gap:6px}}
  .home-action-card{{height:136px;padding:8px 7px}}
  .home-card-icon{{width:29px;height:29px}}
  .home-card-title{{font-size:13.4px}}
  .home-card-copy{{font-size:7.8px}}
  .home-arrow{{width:27px;height:27px}}
  .home-bottom-nav{{height:55px}}
}}
@media(min-width:431px){{
  .home-topbar{{height:62px}}
  .home-logo{{width:150px;height:48px}}
  .home-section-title{{font-size:24px}}
  .home-action-card{{height:160px}}
  .home-card-title{{font-size:16.5px}}
  .home-card-copy{{font-size:9.7px}}
}}
</style>

<div class="home-topbar">
  <a class="home-menu" href="?page=create" aria-label="Menu"><span></span><span></span><span></span></a>
  <img class="home-logo" src="{LOGO_URL}" alt="PCNA">
  <a class="home-bell" href="?page=assistant" aria-label="Notifications and messages"><svg viewBox="0 0 24 24"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"></path><path d="M10 21h4"></path></svg></a>
</div>
""",
        unsafe_allow_html=True,
    )

    _hero()

    st.markdown(
        f"""
<div class="home-section-title">What do you need?</div><div class="home-title-underline"></div>
<div class="home-action-grid">
  <a class="home-action-card" href="?page=spec" aria-label="Spec Sample Order">
    <div class="home-card-icon"><svg viewBox="0 0 24 24"><path d="m5 12 4 4 10-10"></path></svg></div>
    <div class="home-card-title">Spec Sample<br>Order</div><div class="home-card-copy">Tell Nova what you need and build the verified PCNA order.</div>
    <img class="home-card-photo spec" src="{PCNA_SPEC_PHOTO}" alt="PCNA promotional product photography">
    <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
  </a>
  <a class="home-action-card" href="?page=virtual" aria-label="Virtuals and Designs">
    <div class="home-card-icon"><svg viewBox="0 0 24 24"><path d="m12 4 7 8-7 8-7-8z"></path></svg></div>
    <div class="home-card-title">Virtuals /<br>Designs</div><div class="home-card-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div>
    <img class="home-card-photo virtual" src="{PCNA_VIRTUAL_PHOTO}" alt="PCNA product design photography">
    <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
  </a>
  <a class="home-action-card" href="?page=quote" aria-label="Quote Request">
    <div class="home-card-icon money">$</div><div class="home-card-title">Quote<br>Request</div><div class="home-card-copy">Quote a verified PCNA product at the requested quantity.</div>
    <img class="home-card-photo quote" src="{PCNA_QUOTE_PHOTO}" alt="PCNA merchandise photography">
    <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
  </a>
  <a class="home-action-card" href="?page=virtual&view=projects" aria-label="Projects">
    <div class="home-card-icon"><svg viewBox="0 0 24 24"><rect x="5" y="5" width="14" height="14" rx="1"></rect></svg></div>
    <div class="home-card-title">Projects</div><div class="home-card-copy">View and manage your saved projects, orders and virtuals in one place.</div>
    <img class="home-card-photo projects" src="{PCNA_PROJECT_PHOTO}" alt="PCNA project product photography">
    <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
  </a>
</div>
<nav class="home-bottom-nav" aria-label="Primary">
  <a class="home-nav-item active" href="?page=home"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"></path><path d="M5.5 10.5V20h13v-9.5"></path></svg></span><span>Home</span></a>
  <a class="home-nav-item" href="?page=virtual&view=projects"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M3 6.5h7l2 2h9v10H3z"></path></svg></span><span>Projects</span></a>
  <a class="home-nav-item" href="?page=search"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="m12 3 7 4v10l-7 4-7-4V7z"></path><path d="m5 7 7 4 7-4M12 11v10"></path></svg></span><span>Products</span></a>
  <a class="home-nav-item" href="?page=assistant"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M4 5.5h16v11H9l-5 3z"></path></svg></span><span>Messages</span></a>
  <a class="home-nav-item" href="?page=data"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.5"></circle><path d="M5.5 20c.7-4 2.8-6 6.5-6s5.8 2 6.5 6"></path></svg></span><span>Account</span></a>
</nav>
""",
        unsafe_allow_html=True,
    )

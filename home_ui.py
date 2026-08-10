from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

LOGO_URL = "https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/pcna-logo.webp"
PCNA_TOTE_PHOTO = "https://assets.pcna.com/image/upload/f_auto%2Cq_auto/Mkt_Dept/2026%20Jobs/2026-9854_0309_POW/9854_7901-56_0309_POW_B1.jpg"
PCNA_JOURNAL_PHOTO = "https://assets.pcna.com/image/upload/f_auto%2Cq_auto/Mkt_Dept/2026%20Jobs/2026-9857_0216_POW/9857_2900-61_0216_POW_B1.jpg"


def _hero() -> None:
    components.html(
        f"""
<div class="pcna-hero-shell">
  <div class="pcna-hero-fallback">
    <img src="{PCNA_TOTE_PHOTO}" alt="PCNA promotional product photography">
    <div class="hero-shade"></div>
    <div class="hero-copy">
      <div class="hero-title">Branded.<br>Merchandise.<br>Delivered.</div>
      <div class="hero-sub">Explore thousands of promotional products to elevate your brand.</div>
      <a class="hero-cta" href="https://www.pcna.com/en-us" target="_blank" rel="noopener">SHOP NOW</a>
    </div>
  </div>
  <iframe src="https://www.pcna.com/en-us" title="PCNA.com hero" loading="eager"></iframe>
</div>
<style>
html,body{{margin:0;padding:0;background:#fff;overflow:hidden}}
.pcna-hero-shell{{position:relative;height:174px;border-radius:18px;overflow:hidden;background:#063b74;box-shadow:0 4px 12px rgba(0,45,91,.12)}}
.pcna-hero-shell iframe{{position:absolute;z-index:2;left:0;top:-96px;width:100%;height:500px;border:0;background:transparent}}
.pcna-hero-fallback{{position:absolute;inset:0;z-index:1;background:#063b74;overflow:hidden;color:#fff}}
.pcna-hero-fallback img{{position:absolute;right:0;top:0;width:58%;height:100%;object-fit:cover;object-position:center}}
.hero-shade{{position:absolute;inset:0;background:linear-gradient(90deg,#042f63 0%,#063b74 47%,rgba(6,59,116,.30) 72%,rgba(6,59,116,.05) 100%)}}
.hero-copy{{position:absolute;z-index:2;left:22px;top:18px;width:47%}}
.hero-title{{font:900 25px/1.01 Arial,sans-serif;letter-spacing:-.8px}}
.hero-sub{{font:400 11px/1.35 Arial,sans-serif;margin:8px 0 10px}}
.hero-cta{{display:inline-flex;height:30px;padding:0 17px;align-items:center;border:1.5px solid #fff;border-radius:6px;color:#fff;text-decoration:none;font:800 11px Arial,sans-serif}}
@media(max-height:830px){{.pcna-hero-shell{{height:158px}}.hero-copy{{top:14px;left:18px}}.hero-title{{font-size:22px}}.hero-sub{{font-size:10px;margin:6px 0 8px}}.hero-cta{{height:27px}}}}
@media(min-height:900px) and (min-width:410px){{.pcna-hero-shell{{height:190px}}.hero-title{{font-size:27px}}}}
</style>
""",
        height=192,
        scrolling=False,
    )


def render_home() -> None:
    st.markdown(
        f"""
<style>
[data-testid="stAppViewContainer"]>.main{{overflow-x:hidden}}
.block-container{{max-width:620px!important;padding:calc(4px + env(safe-area-inset-top)) 12px calc(76px + env(safe-area-inset-bottom))!important;margin:0 auto!important}}
.home-topbar{{height:60px;display:grid;grid-template-columns:54px 1fr 54px;align-items:center;margin:0 2px 7px;background:#fff}}
.home-logo{{display:block;width:132px;max-height:46px;object-fit:contain;justify-self:center}}
.home-menu,.home-bell{{display:flex;align-items:center;justify-content:center;width:42px;height:42px;color:#073f78!important;text-decoration:none!important}}
.home-menu{{flex-direction:column;gap:4px;justify-self:start}}
.home-menu span{{height:3px;width:28px;background:#073f78;border-radius:4px}}
.home-bell{{justify-self:end}}
.home-bell svg{{width:25px;height:25px;stroke:#073f78;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
.home-section-title{{font-size:24px;font-weight:900;letter-spacing:-.03em;color:#052f68;margin:5px 8px 0;line-height:1.02}}
.home-title-underline{{height:3px;width:39px;border-radius:2px;background:#24a6e0;margin:5px 0 8px 8px;box-shadow:0 3px 7px rgba(36,166,224,.20)}}
.home-action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:0 2px 3px}}
.home-action-card{{position:relative;display:block;height:164px;overflow:hidden;text-decoration:none!important;border:1px solid rgba(10,95,170,.14);border-radius:16px;background:#fff;padding:11px 10px;box-sizing:border-box;box-shadow:0 0 7px rgba(35,151,225,.18),0 5px 11px rgba(0,55,110,.08)}}
.home-card-icon{{position:relative;z-index:4;width:35px;height:35px;border-radius:50%;background:#074d91;color:#fff;display:flex;align-items:center;justify-content:center;margin-bottom:7px}}
.home-card-icon svg{{width:21px;height:21px;stroke:#fff;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}}
.home-card-icon.money{{font-size:24px;font-weight:500;line-height:1}}
.home-card-title{{position:relative;z-index:4;color:#052f68;font-size:15.8px;line-height:1.04;font-weight:900;letter-spacing:-.025em;max-width:56%}}
.home-card-copy{{position:relative;z-index:4;color:#173b63;font-size:9.6px;line-height:1.34;margin-top:6px;max-width:55%}}
.home-card-photo{{position:absolute;z-index:1;right:-1px;bottom:0;width:52%;height:76%;object-fit:cover;object-position:center;border:0}}
.home-card-photo.photo-tote{{object-position:58% 50%}}
.home-card-photo.photo-journal{{object-position:55% 52%}}
.home-card-wash{{position:absolute;z-index:2;inset:0;background:linear-gradient(90deg,#fff 0%,#fff 48%,rgba(255,255,255,.80) 57%,rgba(255,255,255,.10) 76%,rgba(255,255,255,0) 100%);pointer-events:none}}
.home-arrow{{position:absolute;z-index:5;right:8px;bottom:8px;width:34px;height:34px;border-radius:50%;background:#074d91;color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 5px rgba(0,43,90,.12)}}
.home-arrow svg{{width:19px;height:19px;stroke:#fff;fill:none;stroke-width:2.3;stroke-linecap:round;stroke-linejoin:round}}
.bottom-nav{{display:none!important}}
.home-bottom-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:max(6px,env(safe-area-inset-bottom));width:min(590px,calc(100% - 24px));height:64px;border-radius:32px;background:#064b91;box-shadow:0 7px 20px rgba(0,42,89,.16);display:grid;grid-template-columns:repeat(5,1fr);z-index:10000;padding:4px 10px;box-sizing:border-box}}
.home-nav-item{{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;color:#fff!important;font-size:9.6px;font-weight:800;gap:2px}}
.home-nav-icon{{width:21px;height:21px;display:flex;align-items:center;justify-content:center}}
.home-nav-icon svg{{width:20px;height:20px;stroke:#fff;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}
.home-nav-item.active:after{{content:"";position:absolute;bottom:-1px;width:34px;height:3px;background:#fff;border-radius:4px}}
@media(max-height:830px){{
 .block-container{{padding-top:calc(1px + env(safe-area-inset-top))!important}}
 .home-topbar{{height:54px;margin-bottom:5px}}
 .home-logo{{width:122px;max-height:42px}}
 .home-section-title{{font-size:22px;margin-top:2px}}
 .home-title-underline{{margin-top:4px;margin-bottom:6px}}
 .home-action-grid{{gap:7px}}
 .home-action-card{{height:148px;padding:9px 9px;border-radius:15px}}
 .home-card-icon{{width:32px;height:32px;margin-bottom:5px}}
 .home-card-icon svg{{width:19px;height:19px}}
 .home-card-icon.money{{font-size:21px}}
 .home-card-title{{font-size:14.5px;max-width:57%}}
 .home-card-copy{{font-size:8.7px;margin-top:5px;max-width:56%}}
 .home-arrow{{width:31px;height:31px;right:7px;bottom:7px}}
 .home-bottom-nav{{height:60px;border-radius:30px}}
 .home-nav-item{{font-size:9px}}
}}
@media(min-height:900px) and (min-width:410px){{.home-action-card{{height:174px}}.home-card-title{{font-size:16.5px}}.home-card-copy{{font-size:10px}}}}
@media(max-width:350px){{.home-action-grid{{gap:6px}}.home-action-card{{padding:8px 7px}}.home-card-title{{font-size:13.5px}}.home-card-copy{{font-size:8.2px}}}}
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
<a class="home-action-card" href="?page=spec">
  <div class="home-card-icon"><svg viewBox="0 0 24 24"><path d="m5 12 4 4 10-10"></path></svg></div>
  <div class="home-card-title">Spec Sample<br>Order</div>
  <div class="home-card-copy">Tell Nova what you need and build the verified PCNA order.</div>
  <img class="home-card-photo photo-tote" src="{PCNA_TOTE_PHOTO}" alt="PCNA promotional tote">
  <div class="home-card-wash"></div>
  <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
</a>
<a class="home-action-card" href="?page=virtual">
  <div class="home-card-icon"><svg viewBox="0 0 24 24"><path d="m12 4 7 8-7 8-7-8z"></path></svg></div>
  <div class="home-card-title">Virtuals /<br>Designs</div>
  <div class="home-card-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div>
  <img class="home-card-photo photo-journal" src="{PCNA_JOURNAL_PHOTO}" alt="PCNA journals and creative products">
  <div class="home-card-wash"></div>
  <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
</a>
<a class="home-action-card" href="?page=quote">
  <div class="home-card-icon money">$</div>
  <div class="home-card-title">Quote<br>Request</div>
  <div class="home-card-copy">Quote a verified PCNA product at the requested quantity.</div>
  <img class="home-card-photo photo-tote" src="{PCNA_TOTE_PHOTO}" alt="PCNA promotional merchandise">
  <div class="home-card-wash"></div>
  <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
</a>
<a class="home-action-card" href="?page=virtual&view=projects">
  <div class="home-card-icon"><svg viewBox="0 0 24 24"><rect x="5" y="5" width="14" height="14" rx="1"></rect></svg></div>
  <div class="home-card-title">Projects</div>
  <div class="home-card-copy">View and manage your saved projects, orders and virtuals in one place.</div>
  <img class="home-card-photo photo-journal" src="{PCNA_JOURNAL_PHOTO}" alt="PCNA journal project photography">
  <div class="home-card-wash"></div>
  <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
</a>
</div>
<div class="home-bottom-nav">
<a class="home-nav-item active" href="?page=home"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"></path><path d="M5.5 10.5V20h13v-9.5"></path></svg></span><span>Home</span></a>
<a class="home-nav-item" href="?page=virtual&view=projects"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M3 6.5h7l2 2h9v10H3z"></path></svg></span><span>Projects</span></a>
<a class="home-nav-item" href="?page=search"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="m12 3 7 4v10l-7 4-7-4V7z"></path><path d="m5 7 7 4 7-4M12 11v10"></path></svg></span><span>Products</span></a>
<a class="home-nav-item" href="?page=assistant"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M4 5.5h16v11H9l-5 3z"></path></svg></span><span>Messages</span></a>
<a class="home-nav-item" href="?page=data"><span class="home-nav-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"></circle><path d="M4.5 21c.6-4.2 3-6.5 7.5-6.5s6.9 2.3 7.5 6.5"></path></svg></span><span>Account</span></a>
</div>
""",
        unsafe_allow_html=True,
    )

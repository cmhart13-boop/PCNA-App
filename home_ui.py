from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

# Locked, approved repository asset. Do not replace with generated/recreated branding.
LOGO_URL = "https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/pcna-logo.webp"

# Existing PCNA-hosted photography already used by this app.
PCNA_TOTE_PHOTO = "https://assets.pcna.com/image/upload/f_auto%2Cq_auto/Mkt_Dept/2026%20Jobs/2026-9854_0309_POW/9854_7901-56_0309_POW_B1.jpg"
PCNA_JOURNAL_PHOTO = "https://assets.pcna.com/image/upload/f_auto%2Cq_auto/Mkt_Dept/2026%20Jobs/2026-9857_0216_POW/9857_2900-61_0216_POW_B1.jpg"


def _hero() -> None:
    """Render the approved PCNA.com-style hero using existing PCNA-hosted imagery."""
    components.html(
        f"""
<a class="pcna-hero" href="https://www.pcna.com/en-us" target="_blank" rel="noopener" aria-label="Shop PCNA">
  <img class="pcna-hero-photo" src="{PCNA_TOTE_PHOTO}" alt="PCNA promotional products">
  <div class="pcna-hero-overlay"></div>
  <div class="pcna-hero-copy">
    <div class="pcna-hero-title">Branded.<br>Merchandise.<br>Delivered.</div>
    <div class="pcna-hero-sub">Explore thousands of promotional products to elevate your brand.</div>
    <span class="pcna-hero-cta">SHOP NOW</span>
  </div>
</a>
<style>
html,body{{margin:0;padding:0;background:#fff;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}
.pcna-hero{{position:relative;display:block;height:244px;border-radius:22px;overflow:hidden;background:#052f68;text-decoration:none;box-shadow:0 4px 14px rgba(0,45,91,.11)}}
.pcna-hero-photo{{position:absolute;right:0;top:0;width:67%;height:100%;object-fit:cover;object-position:center}}
.pcna-hero-overlay{{position:absolute;inset:0;background:linear-gradient(90deg,#042d60 0%,#063b74 46%,rgba(6,59,116,.78) 59%,rgba(6,59,116,.12) 100%)}}
.pcna-hero-copy{{position:absolute;left:26px;top:24px;width:48%;color:#fff}}
.pcna-hero-title{{font-size:31px;font-weight:900;line-height:1.02;letter-spacing:-1.15px}}
.pcna-hero-sub{{font-size:14px;line-height:1.38;margin:13px 0 17px;max-width:260px}}
.pcna-hero-cta{{display:inline-flex;height:42px;padding:0 22px;align-items:center;border:1.8px solid #fff;border-radius:7px;color:#fff;font-size:14px;font-weight:850}}
@media(max-width:430px){{
  .pcna-hero{{height:214px;border-radius:18px}}
  .pcna-hero-copy{{left:20px;top:19px;width:49%}}
  .pcna-hero-title{{font-size:27px}}
  .pcna-hero-sub{{font-size:12px;margin:10px 0 14px}}
  .pcna-hero-cta{{height:37px;padding:0 18px;font-size:12px}}
}}
@media(max-width:360px){{
  .pcna-hero{{height:194px}}
  .pcna-hero-title{{font-size:23px}}
  .pcna-hero-sub{{font-size:10.5px}}
  .pcna-hero-cta{{height:34px}}
}}
</style>
""",
        height=252,
        scrolling=False,
    )


def render_home() -> None:
    st.markdown(
        f"""
<style>
/* Homepage-only visual reset */
[data-testid="stAppViewContainer"] > .main{{overflow-x:hidden!important}}
.block-container{{
  max-width:1020px!important;
  padding:calc(6px + env(safe-area-inset-top)) 18px calc(102px + env(safe-area-inset-bottom))!important;
  margin:0 auto!important
}}
.home-topbar{{
  height:86px;display:grid;grid-template-columns:64px 1fr 64px;align-items:center;
  margin:0 7px 9px;background:#fff
}}
.home-logo{{display:block;width:178px;max-height:62px;object-fit:contain;justify-self:center}}
.home-menu,.home-bell{{
  display:flex;align-items:center;justify-content:center;width:48px;height:48px;
  color:#052f68!important;text-decoration:none!important
}}
.home-menu{{flex-direction:column;gap:5px;justify-self:start}}
.home-menu span{{display:block;height:4px;width:31px;background:#052f68;border-radius:5px}}
.home-bell{{justify-self:end}}
.home-bell svg{{width:31px;height:31px;stroke:#052f68;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}

.home-section-title{{
  font-size:34px;font-weight:900;letter-spacing:-.035em;color:#052f68;
  margin:14px 13px 0;line-height:1
}}
.home-title-underline{{
  height:4px;width:62px;border-radius:4px;background:#24a6e0;
  margin:9px 0 13px 13px;box-shadow:0 3px 8px rgba(36,166,224,.18)
}}
.home-action-grid{{
  display:grid;grid-template-columns:1fr 1fr;gap:22px;
  margin:0 4px 12px
}}
.home-action-card{{
  position:relative;display:block;height:352px;overflow:hidden;text-decoration:none!important;
  border:1px solid rgba(17,100,174,.12);border-radius:22px;background:#fff;padding:23px 21px;
  box-sizing:border-box;box-shadow:0 0 10px rgba(38,151,226,.22),0 8px 17px rgba(0,55,110,.09);
  -webkit-tap-highlight-color:transparent
}}
.home-action-card:active{{transform:translateY(1px)}}
.home-card-icon{{
  position:relative;z-index:4;width:53px;height:53px;border-radius:50%;background:#074d91;color:#fff;
  display:flex;align-items:center;justify-content:center;margin-bottom:19px
}}
.home-card-icon svg{{width:31px;height:31px;stroke:#fff;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}}
.home-card-icon.money{{font-size:37px;font-weight:450;line-height:1}}
.home-card-title{{
  position:relative;z-index:4;color:#052f68;font-size:29px;line-height:1.02;font-weight:900;
  letter-spacing:-.035em;max-width:53%
}}
.home-card-copy{{
  position:relative;z-index:4;color:#173b63;font-size:17px;line-height:1.52;margin-top:18px;max-width:52%
}}
.home-card-photo{{
  position:absolute;z-index:1;right:-3%;bottom:0;width:55%;height:78%;
  object-fit:cover;object-position:center;background:#fff
}}
.home-card-photo.spec{{object-position:60% 50%}}
.home-card-photo.virtual{{object-position:58% 48%;width:58%;height:76%}}
.home-card-photo.quote{{object-position:42% 52%;width:57%;height:72%;filter:saturate(.88)}}
.home-card-photo.projects{{object-position:62% 52%;width:54%;height:80%;filter:saturate(.75) brightness(.9)}}
.home-card-wash{{
  position:absolute;z-index:2;inset:0;
  background:linear-gradient(90deg,#fff 0%,#fff 45%,rgba(255,255,255,.94) 52%,rgba(255,255,255,.52) 65%,rgba(255,255,255,.03) 82%);
  pointer-events:none
}}
.home-arrow{{
  position:absolute;z-index:5;right:18px;bottom:18px;width:53px;height:53px;border-radius:50%;
  background:#074d91;color:#fff;display:flex;align-items:center;justify-content:center;
  box-shadow:0 2px 6px rgba(0,43,90,.13)
}}
.home-arrow svg{{width:29px;height:29px;stroke:#fff;fill:none;stroke-width:2.25;stroke-linecap:round;stroke-linejoin:round}}

/* Suppress the generic Streamlit nav on Home and render the approved 5-item reference nav. */
.bottom-nav{{display:none!important}}
.home-bottom-nav{{
  position:fixed;left:50%;transform:translateX(-50%);
  bottom:max(9px,env(safe-area-inset-bottom));width:min(960px,calc(100% - 36px));height:84px;
  border-radius:44px;background:#064b91;box-shadow:0 8px 24px rgba(0,42,89,.17);
  display:grid;grid-template-columns:repeat(5,1fr);z-index:10000;padding:6px 18px;box-sizing:border-box
}}
.home-nav-item{{
  position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;
  text-decoration:none!important;color:#fff!important;font-size:13px;font-weight:600;gap:3px
}}
.home-nav-icon{{width:28px;height:28px;display:flex;align-items:center;justify-content:center}}
.home-nav-icon svg{{width:27px;height:27px;stroke:#fff;fill:none;stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round}}
.home-nav-item.active .home-nav-icon svg{{fill:#fff}}
.home-nav-item.active:after{{
  content:"";position:absolute;bottom:0;width:44px;height:4px;background:#fff;border-radius:5px
}}

@media(max-width:700px){{
  .block-container{{max-width:620px!important;padding-left:12px!important;padding-right:12px!important}}
  .home-topbar{{height:68px;grid-template-columns:54px 1fr 54px;margin:0 4px 7px}}
  .home-logo{{width:145px;max-height:52px}}
  .home-menu,.home-bell{{width:44px;height:44px}}
  .home-menu span{{width:29px;height:3.5px}}
  .home-bell svg{{width:27px;height:27px}}
  .home-section-title{{font-size:27px;margin:7px 10px 0}}
  .home-title-underline{{height:3px;width:46px;margin:7px 0 10px 10px}}
  .home-action-grid{{gap:12px;margin:0 2px 8px}}
  .home-action-card{{height:246px;border-radius:18px;padding:15px 13px}}
  .home-card-icon{{width:43px;height:43px;margin-bottom:11px}}
  .home-card-icon svg{{width:25px;height:25px}}
  .home-card-icon.money{{font-size:29px}}
  .home-card-title{{font-size:20px;max-width:56%}}
  .home-card-copy{{font-size:12px;line-height:1.46;margin-top:10px;max-width:55%}}
  .home-arrow{{right:10px;bottom:10px;width:42px;height:42px}}
  .home-arrow svg{{width:23px;height:23px}}
  .home-bottom-nav{{width:calc(100% - 24px);height:72px;border-radius:38px;padding:5px 10px}}
  .home-nav-item{{font-size:10px;gap:2px}}
  .home-nav-icon{{width:24px;height:24px}}
  .home-nav-icon svg{{width:23px;height:23px}}
  .home-nav-item.active:after{{width:36px;height:3px}}
}}
@media(max-width:430px){{
  .block-container{{
    padding-top:calc(3px + env(safe-area-inset-top))!important;
    padding-bottom:calc(91px + env(safe-area-inset-bottom))!important
  }}
  .home-action-card{{height:236px}}
  .home-card-title{{font-size:19px}}
  .home-card-copy{{font-size:11.5px}}
}}
@media(max-width:370px){{
  .home-action-grid{{gap:8px}}
  .home-action-card{{height:222px;padding:12px 10px;border-radius:16px}}
  .home-card-icon{{width:38px;height:38px;margin-bottom:8px}}
  .home-card-title{{font-size:17px}}
  .home-card-copy{{font-size:10.4px;margin-top:8px}}
  .home-arrow{{width:36px;height:36px;right:8px;bottom:8px}}
  .home-bottom-nav{{height:66px}}
}}
@media(min-width:701px){{
  .home-action-grid{{gap:20px}}
}}
</style>

<div class="home-topbar">
  <a class="home-menu" href="?page=create" aria-label="Menu"><span></span><span></span><span></span></a>
  <img class="home-logo" src="{LOGO_URL}" alt="PCNA">
  <a class="home-bell" href="?page=assistant" aria-label="Notifications and messages">
    <svg viewBox="0 0 24 24"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"></path><path d="M10 21h4"></path></svg>
  </a>
</div>
""",
        unsafe_allow_html=True,
    )

    _hero()

    st.markdown(
        f"""
<div class="home-section-title">What do you need?</div>
<div class="home-title-underline"></div>

<div class="home-action-grid">
  <a class="home-action-card" href="?page=spec" aria-label="Spec Sample Order">
    <div class="home-card-icon"><svg viewBox="0 0 24 24"><path d="m5 12 4 4 10-10"></path></svg></div>
    <div class="home-card-title">Spec Sample<br>Order</div>
    <div class="home-card-copy">Tell Nova what you need and build the verified PCNA order.</div>
    <img class="home-card-photo spec" src="{PCNA_TOTE_PHOTO}" alt="PCNA promotional product">
    <div class="home-card-wash"></div>
    <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
  </a>

  <a class="home-action-card" href="?page=virtual" aria-label="Virtuals and Designs">
    <div class="home-card-icon"><svg viewBox="0 0 24 24"><path d="m12 4 7 8-7 8-7-8z"></path></svg></div>
    <div class="home-card-title">Virtuals /<br>Designs</div>
    <div class="home-card-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div>
    <img class="home-card-photo virtual" src="{PCNA_JOURNAL_PHOTO}" alt="PCNA product design photography">
    <div class="home-card-wash"></div>
    <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
  </a>

  <a class="home-action-card" href="?page=quote" aria-label="Quote Request">
    <div class="home-card-icon money">$</div>
    <div class="home-card-title">Quote<br>Request</div>
    <div class="home-card-copy">Quote a verified PCNA product at the requested quantity.</div>
    <img class="home-card-photo quote" src="{PCNA_TOTE_PHOTO}" alt="PCNA merchandise for quote request">
    <div class="home-card-wash"></div>
    <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
  </a>

  <a class="home-action-card" href="?page=virtual&view=projects" aria-label="Projects">
    <div class="home-card-icon"><svg viewBox="0 0 24 24"><rect x="5" y="5" width="14" height="14" rx="1"></rect></svg></div>
    <div class="home-card-title">Projects</div>
    <div class="home-card-copy">View and manage your saved projects, orders and virtuals in one place.</div>
    <img class="home-card-photo projects" src="{PCNA_JOURNAL_PHOTO}" alt="PCNA project product photography">
    <div class="home-card-wash"></div>
    <div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div>
  </a>
</div>

<nav class="home-bottom-nav" aria-label="Primary">
  <a class="home-nav-item active" href="?page=home">
    <span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"></path><path d="M5.5 10.5V20h13v-9.5"></path></svg></span><span>Home</span>
  </a>
  <a class="home-nav-item" href="?page=virtual&view=projects">
    <span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M3 6.5h7l2 2h9v10H3z"></path></svg></span><span>Projects</span>
  </a>
  <a class="home-nav-item" href="?page=search">
    <span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="m12 3 7 4v10l-7 4-7-4V7z"></path><path d="m5 7 7 4 7-4M12 11v10"></path></svg></span><span>Products</span>
  </a>
  <a class="home-nav-item" href="?page=assistant">
    <span class="home-nav-icon"><svg viewBox="0 0 24 24"><path d="M4 5.5h16v11H9l-5 3z"></path></svg></span><span>Messages</span>
  </a>
  <a class="home-nav-item" href="?page=data">
    <span class="home-nav-icon"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.5"></circle><path d="M5.5 20c.7-4 2.8-6 6.5-6s5.8 2 6.5 6"></path></svg></span><span>Account</span>
  </a>
</nav>
""",
        unsafe_allow_html=True,
    )

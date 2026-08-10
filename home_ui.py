from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

LOGO_URL = "https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/pcna-logo.webp"


def _hero() -> None:
    components.html(
        """
<div class="pcna-hero-shell">
  <div class="pcna-hero-fallback">
    <div class="hero-copy">
      <div class="hero-title">Branded.<br>Merchandise.<br>Delivered.</div>
      <div class="hero-sub">Explore thousands of promotional products to elevate your brand.</div>
      <a class="hero-cta" href="https://www.pcna.com/en-us" target="_blank" rel="noopener">SHOP NOW</a>
    </div>
  </div>
  <iframe src="https://www.pcna.com/en-us" title="PCNA.com hero" loading="eager"></iframe>
</div>
<style>
html,body{margin:0;padding:0;background:#fff;overflow:hidden}
.pcna-hero-shell{position:relative;height:244px;border-radius:18px;overflow:hidden;background:#07386e;box-shadow:0 5px 14px rgba(0,45,91,.14)}
.pcna-hero-shell iframe{position:absolute;z-index:2;left:0;top:-92px;width:100%;height:620px;border:0;background:#07386e}
.pcna-hero-fallback{position:absolute;inset:0;z-index:1;background:#07386e;color:#fff;display:flex;align-items:center}
.hero-copy{padding:24px 28px;max-width:58%}
.hero-title{font:900 31px/1.02 Arial,sans-serif;letter-spacing:-1px}
.hero-sub{font:400 13px/1.45 Arial,sans-serif;margin:12px 0 14px}
.hero-cta{display:inline-flex;height:38px;padding:0 23px;align-items:center;border:1.5px solid #fff;border-radius:6px;color:#fff;text-decoration:none;font:800 13px Arial,sans-serif}
@media(max-width:430px){.pcna-hero-shell{height:236px}.pcna-hero-shell iframe{top:-82px;height:590px}.hero-title{font-size:29px}.hero-copy{padding-left:25px}}
</style>
""",
        height=244,
        scrolling=False,
    )


def render_home() -> None:
    st.markdown(
        f"""
<style>
[data-testid="stAppViewContainer"]>.main{{overflow-x:hidden}}
.block-container{{max-width:620px!important;padding:calc(15px + env(safe-area-inset-top)) 12px 108px!important;margin:0 auto!important}}
.home-topbar{{height:76px;display:grid;grid-template-columns:64px 1fr 64px;align-items:center;margin:-7px 3px 10px;background:#fff}}
.home-logo{{display:block;width:148px;max-height:56px;object-fit:contain;justify-self:center}}
.home-menu,.home-bell{{display:flex;align-items:center;justify-content:center;width:48px;height:48px;color:#073f78!important;text-decoration:none!important}}
.home-menu{{flex-direction:column;gap:5px;justify-self:start}}
.home-menu span{{height:4px;width:31px;background:#073f78;border-radius:4px}}
.home-bell{{justify-self:end}}
.home-bell svg{{width:29px;height:29px;stroke:#073f78;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
.home-section-title{{font-size:26px;font-weight:900;letter-spacing:-.03em;color:#052f68;margin:11px 11px 0;line-height:1.05}}
.home-title-underline{{height:3px;width:42px;border-radius:2px;background:#24a6e0;margin:7px 0 11px 11px;box-shadow:0 4px 8px rgba(36,166,224,.22)}}
.home-action-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:0 2px 10px}}
.home-action-card{{position:relative;display:block;height:230px;overflow:hidden;text-decoration:none!important;border:1px solid rgba(10,95,170,.14);border-radius:17px;background:#fff;padding:15px 14px;box-sizing:border-box;box-shadow:0 0 8px rgba(35,151,225,.20),0 7px 14px rgba(0,55,110,.08)}}
.home-card-icon{{width:44px;height:44px;border-radius:50%;background:#074d91;color:#fff;display:flex;align-items:center;justify-content:center;margin-bottom:12px}}
.home-card-icon svg{{width:26px;height:26px;stroke:#fff;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}}
.home-card-icon.money{{font-size:28px;font-weight:500;line-height:1}}
.home-card-title{{position:relative;z-index:3;color:#052f68;font-size:20px;line-height:1.05;font-weight:900;letter-spacing:-.025em;max-width:70%}}
.home-card-copy{{position:relative;z-index:3;color:#173b63;font-size:12.3px;line-height:1.45;margin-top:10px;max-width:64%}}
.home-card-art{{position:absolute;z-index:1;right:-4px;bottom:14px;width:54%;height:65%}}
.home-card-art svg{{width:100%;height:100%;display:block}}
.home-card-art .fill-dark{{fill:#173c67}}.home-card-art .fill-mid{{fill:#2d5f93}}.home-card-art .fill-light{{fill:#dbe6f1}}.home-card-art .fill-paper{{fill:#f7f9fc}}.home-card-art .stroke{{stroke:#173c67;stroke-width:2.4;fill:none;stroke-linecap:round;stroke-linejoin:round}}
.home-arrow{{position:absolute;z-index:4;right:10px;bottom:10px;width:42px;height:42px;border-radius:50%;background:#074d91;color:#fff;display:flex;align-items:center;justify-content:center}}
.home-arrow svg{{width:24px;height:24px;stroke:#fff;fill:none;stroke-width:2.3;stroke-linecap:round;stroke-linejoin:round}}
.bottom-nav{{display:none!important}}
.home-bottom-nav{{position:fixed;left:50%;transform:translateX(-50%);bottom:9px;width:min(590px,calc(100% - 24px));height:78px;border-radius:39px;background:#064b91;box-shadow:0 8px 24px rgba(0,42,89,.16);display:grid;grid-template-columns:repeat(5,1fr);z-index:10000;padding:6px 12px max(6px,env(safe-area-inset-bottom));box-sizing:border-box}}
.home-nav-item{{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;color:#fff!important;font-size:11px;font-weight:800;gap:3px}}
.home-nav-icon{{width:25px;height:25px;display:flex;align-items:center;justify-content:center}}
.home-nav-icon svg{{width:24px;height:24px;stroke:#fff;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}
.home-nav-item.active:after{{content:"";position:absolute;bottom:0;width:40px;height:3px;background:#fff;border-radius:4px}}
@media(max-width:430px){{.home-topbar{{height:72px;margin-top:-6px}}.home-logo{{width:142px}}.home-section-title{{font-size:25px}}.home-action-card{{height:226px}}.home-card-title{{font-size:19.5px}}.home-card-copy{{font-size:11.9px}}}}
@media(max-width:360px){{.home-action-grid{{gap:8px}}.home-action-card{{height:218px;padding:13px 11px}}.home-card-icon{{width:40px;height:40px}}.home-card-icon svg{{width:23px;height:23px}}.home-card-title{{font-size:18px}}.home-card-copy{{font-size:11px;max-width:66%}}.home-arrow{{width:38px;height:38px}}}}
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
        """
<div class="home-section-title">What do you need?</div><div class="home-title-underline"></div>
<div class="home-action-grid">
<a class="home-action-card" href="?page=spec"><div class="home-card-icon"><svg viewBox="0 0 24 24"><path d="m5 12 4 4 10-10"></path></svg></div><div class="home-card-title">Spec Sample<br>Order</div><div class="home-card-copy">Tell Nova what you need and build the verified PCNA order.</div><div class="home-card-art" aria-hidden="true"><svg viewBox="0 0 150 170"><path class="fill-dark" d="M42 40c3-21 20-34 41-34s38 13 41 34l10 116H27z"/><path class="fill-mid" d="M48 47h69l6 93H38z"/><path class="fill-light" d="M58 65h49v38H58z"/><path class="stroke" d="M57 39c1-14 11-23 26-23s25 9 26 23M43 122h79M33 73c-10 8-15 23-15 40M132 72c10 8 15 23 15 40"/></svg></div><div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div></a>
<a class="home-action-card" href="?page=virtual"><div class="home-card-icon"><svg viewBox="0 0 24 24"><path d="m12 4 7 8-7 8-7-8z"></path></svg></div><div class="home-card-title">Virtuals /<br>Designs</div><div class="home-card-copy">Ask Nova for product, kit or packaging virtuals and keep them in Projects.</div><div class="home-card-art" aria-hidden="true"><svg viewBox="0 0 160 170"><rect x="26" y="28" width="118" height="78" rx="6" class="fill-dark"/><rect x="34" y="36" width="102" height="62" rx="2" class="fill-light"/><path class="fill-mid" d="M65 50h40l12 15v25H53V65z"/><path class="fill-dark" d="M72 59h26v33H72z"/><path class="fill-dark" d="M16 115h138l-13 18H29z"/><path class="stroke" d="M61 133h48"/></svg></div><div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div></a>
<a class="home-action-card" href="?page=quote"><div class="home-card-icon money">$</div><div class="home-card-title">Quote<br>Request</div><div class="home-card-copy">Quote a verified PCNA product at the requested quantity.</div><div class="home-card-art" aria-hidden="true"><svg viewBox="0 0 160 170"><rect x="34" y="16" width="96" height="125" rx="7" class="fill-dark"/><rect x="42" y="25" width="80" height="108" rx="2" class="fill-paper"/><rect x="50" y="37" width="64" height="12" rx="2" class="fill-light"/><path class="stroke" d="M52 61h58M52 72h58M52 83h58M52 94h58"/><rect x="53" y="110" width="10" height="14" class="fill-mid"/><rect x="69" y="103" width="10" height="21" class="fill-mid"/><rect x="85" y="96" width="10" height="28" class="fill-mid"/><path class="stroke" d="M23 145 139 122M30 151 145 129"/></svg></div><div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div></a>
<a class="home-action-card" href="?page=virtual&view=projects"><div class="home-card-icon"><svg viewBox="0 0 24 24"><rect x="5" y="5" width="14" height="14" rx="1"></rect></svg></div><div class="home-card-title">Projects</div><div class="home-card-copy">View and manage your saved projects, orders and virtuals in one place.</div><div class="home-card-art" aria-hidden="true"><svg viewBox="0 0 160 170"><g transform="rotate(-8 85 88)"><rect x="43" y="17" width="82" height="128" rx="5" class="fill-dark"/><rect x="49" y="23" width="70" height="116" rx="2" fill="#2b3037"/><rect x="55" y="25" width="8" height="112" rx="4" fill="#111820"/><path d="M116 34h8v92h-8z" class="fill-light"/></g><path class="stroke" d="M124 23v117"/></svg></div><div class="home-arrow"><svg viewBox="0 0 24 24"><path d="M5 12h13"></path><path d="m14 7 5 5-5 5"></path></svg></div></a>
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

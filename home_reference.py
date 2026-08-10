from __future__ import annotations

import streamlit as st


REFERENCE_URL = "https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/reference-home.webp"
LOGO_URL = "https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/pcna-logo.webp"


def render_reference_home() -> None:
    """Render the approved PCNA homepage reference with live clickable regions."""
    st.markdown(
        f"""
<style>
/* The approved screenshot is the visual source of truth on the homepage only. */
[data-testid="stAppViewContainer"] > .main .block-container:has(.pcna-ref-wrap){{
    max-width:1024px!important;
    padding:0!important;
    margin:0 auto!important;
}}
.pcna-ref-wrap{{position:relative;width:100%;max-width:1024px;margin:0 auto;line-height:0;background:#fff;}}
.pcna-ref-img{{display:block;width:100%;height:auto;border:0;}}
.pcna-ref-hit{{position:absolute;display:block;z-index:6;text-decoration:none!important;background:rgba(0,0,0,0);border:0;}}
/* Preserve the locked repository PCNA logo asset rather than recreating it. */
.pcna-ref-logo-mask{{position:absolute;left:35.4%;top:3.15%;width:27.6%;height:5.25%;background:#fff;z-index:5;display:flex;align-items:center;justify-content:center;}}
.pcna-ref-logo-mask img{{width:92%;height:100%;object-fit:contain;display:block;}}
.pcna-ref-menu{{left:3.1%;top:3.15%;width:9.0%;height:5.2%;}}
.pcna-ref-bell{{left:88.5%;top:3.15%;width:8.0%;height:5.2%;}}
.pcna-ref-hero{{left:2.8%;top:9.55%;width:94.1%;height:25.45%;}}
.pcna-ref-card1{{left:2.85%;top:40.85%;width:45.5%;height:24.35%;}}
.pcna-ref-card2{{left:50.65%;top:40.85%;width:46.0%;height:24.35%;}}
.pcna-ref-card3{{left:2.85%;top:66.7%;width:45.5%;height:23.3%;}}
.pcna-ref-card4{{left:50.65%;top:66.7%;width:46.0%;height:23.3%;}}
.pcna-ref-nav1{{left:3.5%;top:91.75%;width:18.1%;height:7.2%;}}
.pcna-ref-nav2{{left:21.6%;top:91.75%;width:18.7%;height:7.2%;}}
.pcna-ref-nav3{{left:40.3%;top:91.75%;width:19.0%;height:7.2%;}}
.pcna-ref-nav4{{left:59.3%;top:91.75%;width:19.0%;height:7.2%;}}
.pcna-ref-nav5{{left:78.3%;top:91.75%;width:18.0%;height:7.2%;}}
@media (min-width:1025px){{
  .pcna-ref-wrap{{box-shadow:0 18px 60px rgba(0,46,92,.08);}}
}}
</style>
<div class="pcna-ref-wrap" aria-label="PCNA home">
  <img class="pcna-ref-img" src="{REFERENCE_URL}" alt="PCNA homepage">
  <div class="pcna-ref-logo-mask"><img src="{LOGO_URL}" alt="PCNA"></div>
  <a class="pcna-ref-hit pcna-ref-menu" href="?page=create" aria-label="Menu"></a>
  <a class="pcna-ref-hit pcna-ref-bell" href="?page=assistant" aria-label="Notifications"></a>
  <a class="pcna-ref-hit pcna-ref-hero" href="https://www.pcna.com/en-us" target="_blank" rel="noopener" aria-label="Shop PCNA"></a>
  <a class="pcna-ref-hit pcna-ref-card1" href="?page=spec" aria-label="Spec Sample Order"></a>
  <a class="pcna-ref-hit pcna-ref-card2" href="?page=virtual" aria-label="Virtuals / Designs"></a>
  <a class="pcna-ref-hit pcna-ref-card3" href="?page=quote" aria-label="Quote Request"></a>
  <a class="pcna-ref-hit pcna-ref-card4" href="?page=virtual&view=projects" aria-label="Projects"></a>
  <a class="pcna-ref-hit pcna-ref-nav1" href="?page=home" aria-label="Home"></a>
  <a class="pcna-ref-hit pcna-ref-nav2" href="?page=virtual&view=projects" aria-label="Projects"></a>
  <a class="pcna-ref-hit pcna-ref-nav3" href="?page=search" aria-label="Products"></a>
  <a class="pcna-ref-hit pcna-ref-nav4" href="?page=assistant" aria-label="Messages"></a>
  <a class="pcna-ref-hit pcna-ref-nav5" href="?page=data" aria-label="Account"></a>
</div>
""",
        unsafe_allow_html=True,
    )

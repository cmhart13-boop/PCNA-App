from __future__ import annotations

import base64
import streamlit as st

REFERENCE_B64 = "PLACEHOLDER"


def render_reference_home() -> None:
    """Render the approved PCNA mobile homepage reference with live clickable regions.

    The screenshot is used only as the approved visual shell. The official repository
    PCNA logo is overlaid from assets/pcna-logo.webp so the locked brand asset remains
    the actual logo rendered in the header.
    """
    img = f"data:image/jpeg;base64,{REFERENCE_B64}"
    st.markdown(
        f"""
<style>
.pcna-ref-wrap{{position:relative;width:100%;max-width:620px;margin:0 auto 0;line-height:0;}}
.pcna-ref-img{{display:block;width:100%;height:auto;border:0;}}
.pcna-ref-hit{{position:absolute;display:block;z-index:5;text-decoration:none!important;background:rgba(0,0,0,0);}}
.pcna-ref-logo-mask{{position:absolute;left:34.2%;top:3.2%;width:31.8%;height:5.9%;background:#fff;z-index:4;display:flex;align-items:center;justify-content:center;}}
.pcna-ref-logo-mask img{{width:78%;height:auto;object-fit:contain;display:block;}}
.pcna-ref-menu{{left:2.8%;top:3.3%;width:10.5%;height:5.7%;}}
.pcna-ref-bell{{left:88.5%;top:3.3%;width:8.5%;height:5.7%;}}
.pcna-ref-hero{{left:2.8%;top:9.4%;width:94.2%;height:25.8%;}}
.pcna-ref-card1{{left:2.7%;top:40.8%;width:45.9%;height:24.6%;}}
.pcna-ref-card2{{left:50.6%;top:40.8%;width:46.0%;height:24.6%;}}
.pcna-ref-card3{{left:2.7%;top:66.5%;width:45.9%;height:23.7%;}}
.pcna-ref-card4{{left:50.6%;top:66.5%;width:46.0%;height:23.7%;}}
.pcna-ref-nav1{{left:3.6%;top:91.7%;width:18.0%;height:7.3%;}}
.pcna-ref-nav2{{left:21.6%;top:91.7%;width:18.7%;height:7.3%;}}
.pcna-ref-nav3{{left:40.3%;top:91.7%;width:19.0%;height:7.3%;}}
.pcna-ref-nav4{{left:59.3%;top:91.7%;width:19.0%;height:7.3%;}}
.pcna-ref-nav5{{left:78.3%;top:91.7%;width:18.0%;height:7.3%;}}
@media (min-width:621px){{.pcna-ref-wrap{{box-shadow:0 16px 50px rgba(0,46,92,.06);}}}}
</style>
<div class="pcna-ref-wrap" aria-label="PCNA home">
  <img class="pcna-ref-img" src="{img}" alt="PCNA homepage">
  <div class="pcna-ref-logo-mask"><img src="https://raw.githubusercontent.com/cmhart13-boop/PCNA-App/main/assets/pcna-logo.webp" alt="PCNA"></div>
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

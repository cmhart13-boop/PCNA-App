from __future__ import annotations

"""Small runtime UI patch for the PCNA mobile homepage.

This keeps the existing app routes/workflows intact while applying the approved
compact mobile homepage measurements. The locked PCNA logo file is never
modified or substituted.
"""

import streamlit as st
import streamlit.components.v1 as components


_original_markdown = st.markdown
_original_image = st.image
_original_components_html = components.html


_HOME_CSS = r"""
<style>
@media (max-width: 620px) {
    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main {
        min-height: 100dvh !important;
        background: #ffffff !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        overflow-y: auto !important;
    }

    .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"] {
        width: 100% !important;
        max-width: 480px !important;
        margin: 0 auto !important;
        padding: 12px 16px 22px 16px !important;
        box-sizing: border-box !important;
    }

    .block-container [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    [data-testid="stImage"] {
        margin: 0 auto 10px auto !important;
        overflow: visible !important;
    }

    [data-testid="stImage"] img {
        display: block !important;
        margin: 0 auto !important;
        max-width: 138px !important;
        width: 138px !important;
        height: auto !important;
        object-fit: contain !important;
    }

    iframe[title="streamlit_component"] {
        display: block !important;
        width: 100% !important;
        margin: 0 0 14px 0 !important;
    }

    .section-title {
        margin: 0 0 10px 1px !important;
        padding: 0 !important;
        color: #172b3f !important;
        font-family: Arial, sans-serif !important;
        font-size: 20px !important;
        line-height: 24px !important;
        font-weight: 700 !important;
    }

    .action-grid {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 12px !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        align-items: start !important;
        align-content: start !important;
    }

    .action-card {
        height: 145px !important;
        min-height: 145px !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 14px !important;
        border: 1px solid #dce3e9 !important;
        border-radius: 12px !important;
        background: #ffffff !important;
        box-shadow: 0 2px 8px rgba(20, 42, 62, 0.07) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        text-decoration: none !important;
    }

    .action-icon {
        width: 30px !important;
        height: 30px !important;
        flex: 0 0 30px !important;
        margin: 0 0 11px 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        border-radius: 8px !important;
        background: #f1f5f8 !important;
        color: #173d60 !important;
        font-family: Arial, sans-serif !important;
        font-size: 18px !important;
        line-height: 18px !important;
        font-weight: 700 !important;
    }

    .action-title {
        width: 100% !important;
        margin: 0 0 5px 0 !important;
        padding: 0 !important;
        color: #172b3f !important;
        font-family: Arial, sans-serif !important;
        font-size: 15px !important;
        line-height: 17px !important;
        font-weight: 700 !important;
    }

    .action-copy {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        color: #6d7985 !important;
        font-family: Arial, sans-serif !important;
        font-size: 11.5px !important;
        line-height: 14px !important;
        font-weight: 400 !important;
    }
}

@media (max-width: 350px) {
    .action-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        gap: 10px !important;
    }

    .action-card {
        padding: 12px !important;
    }
}
</style>
"""


def _patched_markdown(body, *args, **kwargs):
    if isinstance(body, str):
        if (
            '@media(max-width:430px)' in body
            and '.action-grid' in body
            and '.bottom-nav' in body
        ):
            body = body + _HOME_CSS

        if (
            '<div class="action-grid">' in body
            and 'Tell Nova what you need and build the verified PCNA order.' in body
        ):
            body = body.replace(
                'Tell Nova what you need and build the verified PCNA order.',
                'Create and submit a new spec sample order.',
                1,
            )
            body = body.replace(
                'Ask Nova for product, kit or packaging virtuals and keep them in Projects.',
                'Build and review branded product concepts.',
                1,
            )
            body = body.replace(
                'Quote a verified PCNA product at the requested quantity.',
                'Prepare product pricing and quote requests.',
                1,
            )
            body = body.replace(
                'Open your saved PCNA virtual and design projects.',
                'Access and manage active customer projects.',
                1,
            )
            body = body.replace(
                '<div class="action-icon">▣</div><div class="action-title">Projects</div>',
                '<div class="action-icon">❑</div><div class="action-title">Projects</div>',
                1,
            )

    return _original_markdown(body, *args, **kwargs)


def _patched_image(image, *args, **kwargs):
    if image == 'IMG_2337.webp' and kwargs.get('width') == 98:
        kwargs['width'] = 138
    return _original_image(image, *args, **kwargs)


def _patched_components_html(html, *args, **kwargs):
    if isinstance(html, str) and 'pcna-live-shell' in html:
        html = html.replace(
            'height:150px;overflow:hidden;border-radius:14px',
            'height:145px;overflow:hidden;border-radius:12px',
            1,
        )
        if kwargs.get('height') == 152:
            kwargs['height'] = 145
    return _original_components_html(html, *args, **kwargs)


st.markdown = _patched_markdown
st.image = _patched_image
components.html = _patched_components_html

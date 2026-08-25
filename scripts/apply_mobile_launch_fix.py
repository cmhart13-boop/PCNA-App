from pathlib import Path

p = Path("app.py")
s = p.read_text(encoding="utf-8")
start = s.index('st.set_option("client.toolbarMode", "minimal")')
end = s.index("\n\n\nPCNA_BLUE =", start)

replacement = r'''st.set_option("client.toolbarMode", "minimal")

# Single-document mobile startup. The existing browser document is never replaced
# or redirected. A stable PCNA splash covers the launch surface until the home UI
# is ready, then fades exactly once.
_STARTUP_LOGO_PATH = Path("IMG_2337.webp")
_STARTUP_LOGO_DATA = (
    "data:image/webp;base64," + base64.b64encode(_STARTUP_LOGO_PATH.read_bytes()).decode("ascii")
    if _STARTUP_LOGO_PATH.exists()
    else ""
)

_STARTUP_BOOTSTRAP = """
<script>
(() => {
  try {
    const topDocument = window.top.document;
    const root = topDocument.documentElement;

    const removeHostChrome = () => {
      const selectors = [
        '[data-testid="stStatusWidget"]',
        '[data-testid="stToolbar"]',
        '[data-testid="stAppDeployButton"]',
        '[data-testid="stDeployButton"]',
        '[class*="viewerBadge"]',
        '[class*="ViewerBadge"]',
        'a[href*="streamlit.io/cloud"]',
        'a[href*="share.streamlit.io"]'
      ];
      selectors.forEach((selector) => {
        topDocument.querySelectorAll(selector).forEach((node) => node.remove());
      });

      topDocument.querySelectorAll('button,a,div').forEach((node) => {
        const style = window.top.getComputedStyle(node);
        if (style.position !== 'fixed' && style.position !== 'sticky') return;
        const rect = node.getBoundingClientRect();
        const nearBottomRight = rect.right >= window.top.innerWidth - 140 && rect.bottom >= window.top.innerHeight - 140;
        if (!nearBottomRight) return;
        const label = [
          node.getAttribute('aria-label') || '',
          node.getAttribute('title') || '',
          node.textContent || ''
        ].join(' ').toLowerCase();
        if (label.includes('manage app') || label.includes('streamlit')) node.remove();
      });
    };

    removeHostChrome();
    if (!root.__pcnaHostObserver) {
      root.__pcnaHostObserver = new MutationObserver(removeHostChrome);
      root.__pcnaHostObserver.observe(topDocument.body || root, {childList:true, subtree:true});
    }

    if (root.dataset.pcnaStartupComplete === '1') return;
    if (topDocument.getElementById('pcna-native-startup-cover')) return;

    const cover = topDocument.createElement('div');
    cover.id = 'pcna-native-startup-cover';
    cover.setAttribute('aria-label', 'PCNA loading');
    cover.dataset.startedAt = String(performance.now());
    cover.style.cssText = [
      'position:fixed','inset:0','z-index:2147483647','background:#ffffff',
      'display:flex','align-items:center','justify-content:center',
      'margin:0','padding:0','overflow:hidden','opacity:1',
      'transition:opacity .46s cubic-bezier(.22,.61,.36,1)',
      'pointer-events:none'
    ].join(';');

    const logo = topDocument.createElement('img');
    logo.src = '__PCNA_STARTUP_LOGO__';
    logo.alt = 'PCNA';
    logo.style.cssText = [
      'display:block','width:min(68vw,310px)','height:auto','max-height:34vh',
      'object-fit:contain','opacity:1','transform:none'
    ].join(';');

    cover.appendChild(logo);
    root.appendChild(cover);
  } catch (_) {}
})();
</script>
""".replace("__PCNA_STARTUP_LOGO__", _STARTUP_LOGO_DATA)

_STARTUP_READY = """
<script>
(() => {
  try {
    const topDocument = window.top.document;
    const root = topDocument.documentElement;
    const cover = topDocument.getElementById('pcna-native-startup-cover');
    if (!cover) {
      root.dataset.pcnaStartupComplete = '1';
      return;
    }

    const startedAt = Number(cover.dataset.startedAt || performance.now());
    const elapsed = performance.now() - startedAt;
    const wait = Math.max(0, 700 - elapsed);

    window.top.setTimeout(() => {
      requestAnimationFrame(() => requestAnimationFrame(() => {
        cover.style.opacity = '0';
        window.top.setTimeout(() => {
          cover.remove();
          root.dataset.pcnaStartupComplete = '1';
        }, 500);
      }));
    }, wait);
  } catch (_) {}
})();
</script>
"""

components.html(_STARTUP_BOOTSTRAP, height=0, width=0)
'''

s = s[:start] + replacement + s[end:]

old_home = '''if page == "home":\n    render_streamlit_mobile_home()\n    st.stop()'''
new_home = '''if page == "home":\n    render_streamlit_mobile_home()\n    components.html(_STARTUP_READY, height=0, width=0)\n    st.stop()'''
if old_home not in s:
    raise SystemExit("Home readiness insertion point not found")
s = s.replace(old_home, new_home, 1)

forbidden = [
    "topWindow.location.replace",
    "target.searchParams.set('embed'",
    'st.query_params["embed"]',
    "pcna_startup",
]
present = [token for token in forbidden if token in s]
if present:
    raise SystemExit("Forbidden startup behavior remains: " + ", ".join(present))

p.write_text(s, encoding="utf-8")

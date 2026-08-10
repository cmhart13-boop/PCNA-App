from pathlib import Path

source_path = Path(__file__).with_name("_pcna_app_source.py")
source = source_path.read_text(encoding="utf-8")

# Home-only mobile sizing correction.
# Preserve the approved source, logo asset, hero, copy, navigation, and functionality.
# The home screen becomes a fixed mobile viewport below the fixed bottom nav, and the
# action-card element consumes the exact remaining vertical space instead of using
# guessed/fixed card heights.
source = source.replace(
    '  html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{min-height:100dvh!important;}\n  [data-testid="stAppViewContainer"]>.main{overflow-y:auto!important;}',
    '  html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{height:100dvh!important;max-height:100dvh!important;overflow:hidden!important;}\n  [data-testid="stAppViewContainer"]>.main{overflow:hidden!important;}',
)
source = source.replace(
    '  .block-container{width:100%!important;max-width:none!important;min-height:calc(100dvh - 76px)!important;box-sizing:border-box!important;padding:calc(18px + env(safe-area-inset-top)) 10px 12px!important;margin:0!important;overflow:visible!important;}',
    '  .block-container{width:100%!important;max-width:none!important;height:calc(100dvh - 76px)!important;max-height:calc(100dvh - 76px)!important;min-height:0!important;box-sizing:border-box!important;padding:calc(10px + env(safe-area-inset-top)) 10px 8px!important;margin:0!important;overflow:hidden!important;}',
)
source = source.replace(
    '  .block-container [data-testid="stVerticalBlock"]{gap:0!important;}',
    '  .block-container > [data-testid="stVerticalBlock"]{height:100%!important;min-height:0!important;display:flex!important;flex-direction:column!important;gap:0!important;}\n  .block-container > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.action-grid){flex:1 1 0!important;min-height:0!important;overflow:hidden!important;}\n  .block-container > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.action-grid) > div{height:100%!important;min-height:0!important;}',
)
source = source.replace(
    '  .section-title{font-size:20px!important;margin:7px 0 8px!important;line-height:1.08!important;position:relative!important;z-index:2!important;}',
    '  .section-title{font-size:20px!important;margin:3px 0 6px!important;line-height:1.08!important;position:relative!important;z-index:2!important;}',
)
source = source.replace(
    '  .action-grid{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;grid-template-rows:repeat(2,1fr)!important;gap:8px!important;margin:0!important;height:auto!important;min-height:228px!important;max-height:none!important;}',
    '  .action-grid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;grid-template-rows:repeat(2,minmax(0,1fr))!important;gap:12px!important;margin:0!important;height:100%!important;min-height:0!important;max-height:none!important;padding:2px 0 10px!important;box-sizing:border-box!important;}',
)
source = source.replace(
    '  .action-card{box-sizing:border-box!important;padding:10px 12px!important;min-height:0!important;height:100%!important;border-radius:15px!important;overflow:hidden!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;}',
    '  .action-card{box-sizing:border-box!important;padding:13px 14px!important;min-width:0!important;min-height:0!important;width:100%!important;height:100%!important;border-radius:15px!important;overflow:hidden!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;}',
)
source = source.replace(
    '  .section-title{font-size:19px!important;margin:4px 0 7px!important;}',
    '  .section-title{font-size:19px!important;margin:2px 0 6px!important;}',
)
source = source.replace(
    '  .action-grid{gap:7px!important;height:auto!important;min-height:220px!important;}',
    '  .action-grid{gap:10px!important;height:100%!important;min-height:0!important;grid-template-rows:repeat(2,minmax(0,1fr))!important;padding-bottom:8px!important;}',
)
source = source.replace(
    '  .action-card{padding:9px 10px!important;}',
    '  .action-card{padding:11px 12px!important;}',
)

exec(compile(source, str(source_path), "exec"), globals(), globals())

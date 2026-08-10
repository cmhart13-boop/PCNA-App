from pathlib import Path

source_path = Path(__file__).with_name("_pcna_app_source.py")
source = source_path.read_text(encoding="utf-8")

# Home-only mobile corrections. Keep the approved source, assets, copy,
# navigation, hero, and functionality unchanged.
source = source.replace(
    '  html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{min-height:100dvh!important;}\n  [data-testid="stAppViewContainer"]>.main{overflow-y:auto!important;}',
    '  html,body{min-height:100%!important;overflow:auto!important;}\n  [data-testid="stAppViewContainer"]{overflow-y:auto!important;-webkit-overflow-scrolling:touch!important;}\n  [data-testid="stAppViewContainer"]>.main{min-height:100%!important;overflow:visible!important;}',
)
source = source.replace(
    '  .block-container{width:100%!important;max-width:none!important;min-height:calc(100dvh - 76px)!important;box-sizing:border-box!important;padding:calc(18px + env(safe-area-inset-top)) 10px 12px!important;margin:0!important;overflow:visible!important;}',
    '  .block-container{width:100%!important;max-width:none!important;min-height:0!important;box-sizing:border-box!important;padding:calc(18px + env(safe-area-inset-top)) 10px calc(86px + env(safe-area-inset-bottom))!important;margin:0!important;overflow:visible!important;}',
)
source = source.replace(
    '  .section-title{font-size:20px!important;margin:7px 0 8px!important;line-height:1.08!important;position:relative!important;z-index:2!important;}',
    '  .section-title{font-size:20px!important;margin:3px 0 6px!important;line-height:1.08!important;position:relative!important;z-index:2!important;}',
)
source = source.replace(
    '  .action-grid{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;grid-template-rows:repeat(2,1fr)!important;gap:8px!important;margin:0!important;height:auto!important;min-height:228px!important;max-height:none!important;}',
    '  .action-grid{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;grid-template-rows:repeat(2,150px)!important;gap:12px!important;margin:0!important;height:auto!important;min-height:0!important;max-height:none!important;}',
)
source = source.replace(
    '  .section-title{font-size:19px!important;margin:4px 0 7px!important;}',
    '  .section-title{font-size:19px!important;margin:2px 0 6px!important;}',
)
source = source.replace(
    '  .action-grid{gap:7px!important;height:auto!important;min-height:220px!important;}',
    '  .action-grid{gap:12px!important;height:auto!important;min-height:0!important;grid-template-rows:repeat(2,146px)!important;}',
)

exec(compile(source, str(source_path), "exec"), globals(), globals())

from pathlib import Path

p = Path("app.py")
s = p.read_text()

old = '''@media(max-width:430px){
  .block-container{padding-top:calc(22px + env(safe-area-inset-top))!important;padding-left:14px!important;padding-right:14px!important;}
  .section-title{font-size:22px!important;margin:8px 0 9px!important;}
  .action-grid{gap:12px!important;margin-top:4px!important;}
  .action-card{padding:15px 14px!important;min-height:122px!important;border-radius:18px!important;}
  .action-icon{font-size:27px!important;margin-bottom:11px!important;}
  .action-title{font-size:18px!important;line-height:1.15!important;margin-bottom:6px!important;}
  .action-copy{font-size:13px!important;line-height:1.35!important;}
}'''
new = '''@media(max-width:430px){
  .block-container{padding-top:calc(4px + env(safe-area-inset-top))!important;padding-left:10px!important;padding-right:10px!important;padding-bottom:82px!important;}
  .section-title{font-size:20px!important;margin:1px 0 4px!important;line-height:1.05!important;}
  .action-grid{gap:6px!important;margin:0!important;}
  .action-card{padding:8px 10px!important;min-height:88px!important;border-radius:15px!important;}
  .action-icon{font-size:22px!important;margin-bottom:4px!important;}
  .action-title{font-size:17px!important;line-height:1.06!important;margin-bottom:3px!important;}
  .action-copy{font-size:12px!important;line-height:1.15!important;}
  [data-testid="stImage"]{margin-bottom:-10px!important;}
  [data-testid="stVerticalBlock"]{gap:.05rem!important;}
}'''
if old not in s:
    raise SystemExit("homepage CSS marker not found")
s = s.replace(old, new, 1)
s = s.replace('approved_pcna_header(145 if page == "home" else 105)', 'approved_pcna_header(118 if page == "home" else 105)', 1)
s = s.replace('@media(max-width:430px){.pcna-live-shell{height:218px}.pcna-live-shell iframe{top:-72px;height:610px}}', '@media(max-width:430px){.pcna-live-shell{height:142px}.pcna-live-shell iframe{top:-92px;height:555px}}', 1)
s = s.replace('        height=230,\n        scrolling=False,', '        height=150,\n        scrolling=False,', 1)
p.write_text(s)

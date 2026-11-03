"""Repair relative panel assets in the legacy HTML builder's local preview."""
from pathlib import Path
import os,re
ROOT=Path(__file__).resolve().parents[1]/'html'
for page in ROOT.rglob('*.html'):
    text=page.read_text(encoding='utf-8')
    def fix(match):
        before,url,after=match.groups()
        if url.startswith(('http:','https:','data:','#')):return match[0]
        clean=url.strip()
        target=page.parent/clean
        if target.is_file():return match[0]
        candidates=list(ROOT.rglob(Path(clean).name)) if clean not in ('./','') else [ROOT/'course.png']
        candidates=[p for p in candidates if p.is_file()]
        if not candidates:return match[0]
        return before+os.path.relpath(candidates[0],page.parent).replace('\\','/')+after
    text=re.sub(r'((?:src)=")([^"]*)(")',fix,text)
    page.write_text(text,encoding='utf-8')
# Keep the static preview readable even without the optional external CSS CDNs.
(ROOT/'global.css').write_text('''
body {font-family:Arial,sans-serif;color:#243247;margin:24px;background:#fff;line-height:1.5}
table {border-collapse:collapse;width:100%;margin:16px 0}
th,td {padding:10px;text-align:left;border-bottom:1px solid #dce1e8;vertical-align:top}
th {background:#f1f4f8} td img {width:160px;max-width:100%;height:auto}
iframe {border:0;width:100%} img {max-width:100%}
a {color:#245caa} h1,h2 {color:#243d60} .header-anchor {color:inherit;text-decoration:none}
''',encoding='utf-8')
print('Prepared local HTML preview and panel assets.')

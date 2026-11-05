"""通説ページの共通部品（2026-09-28、Q1）。

通説1本 = データと計算（experiments/myths/<id>.py）＋ この共通テンプレート。
- ページの外枠（title・フォント・CSS・見出し・フッター）、確かさの札、規則・出典・食い違いの表、
  言えること／言えないこと、実験の手順と記録表、本人が書く欄（空欄＋材料）をここに置く。
- 計算は Exp-14 のシミュレータ（experiments/exp-14/sim）をそのまま使う。規則・出典の文面は rules.yaml から引く（書き写さない）。
- ページは行のリスト（Lines）で組み、"\n" でつなぐ。
"""
from __future__ import annotations

import csv
import html
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP14 = ROOT / "experiments" / "exp-14"
EXP15 = ROOT / "experiments" / "exp-15-recipes"
WRITEUP = ROOT / "writeup"
if str(EXP14) not in sys.path:
    sys.path.insert(0, str(EXP14))

from run import NO_MATCH_BELOW  # noqa: E402,F401
from sim import maps  # noqa: E402,F401
from sim import params as P  # noqa: E402

e = html.escape
Lines = list[str]

FONTS = [
    '<link rel="preconnect" href="https://fonts.googleapis.com">',
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@800&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">',
]


# ---------------- データ ----------------

def recipe_rows(dish: str | None = None) -> list[dict]:
    """Exp-15 の recipes.csv（dish を指定するとその料理だけ）。"""
    with (EXP15 / "recipes.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [r for r in rows if dish is None or r["dish"] == dish]


def rules_and_sources(rule_ids: list[str]):
    R = P.rules()
    rules = {r["id"]: r for r in R["rules"] if r["id"] in rule_ids}
    return rules, R["sources"], R.get("conflicts") or {}


# ---------------- CSS ----------------
# 料理の色（地図の塗り）はページごとに渡す: [(料理キー, 塗りのクラス, ライト, ダーク)]

CSS_ROOT = """
:root{{
  --bg:#F6F7F5;--surface:#ECEFEB;--card:#FFFFFF;--ink:#1A1F1C;--muted:#5B6560;--rule:#D5DBD6;
  --kombu:#2E5A48;--saffron:#B97B0C;--low:#B4552D;
  {light}--pt-edge:#1A1F1C;
  --serif:"Shippori Mincho B1","Hiragino Mincho ProN","Yu Mincho",serif;
  --sans:"Zen Kaku Gothic New","Hiragino Sans","Yu Gothic",system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{color-scheme:dark;--bg:#111614;--surface:#19201D;--card:#161C19;--ink:#E4EAE6;--muted:#9AA7A0;--rule:#2A3430;--kombu:#7DBFA2;--saffron:#E3AE4A;--low:#E08A63;
    {dark}--pt-edge:#F4F7F5;}}
}}
:root[data-theme="dark"]{{color-scheme:dark;--bg:#111614;--surface:#19201D;--card:#161C19;--ink:#E4EAE6;--muted:#9AA7A0;--rule:#2A3430;--kombu:#7DBFA2;--saffron:#E3AE4A;--low:#E08A63;
  {dark}--pt-edge:#F4F7F5;}}
"""

CSS_BODY = """*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.7;margin:0;padding-inline:16px;padding-block:0 64px}
.wrap{max-width:960px;margin:0 auto}
header{padding-block:32px 8px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;color:var(--kombu);text-transform:uppercase}
h1{font-family:var(--serif);font-weight:800;font-size:clamp(26px,4.5vw,36px);margin:8px 0;line-height:1.3}
.lead{color:var(--muted);margin:0;max-width:68ch}
section{margin-top:40px}
h2{font-family:var(--serif);font-weight:800;font-size:22px;margin:0 0 12px;display:flex;align-items:baseline;gap:10px}
h2 .no{font-family:var(--mono);font-size:13px;color:var(--kombu);font-weight:500}
h3{font-size:15px;margin:22px 0 6px}
p{margin:8px 0;max-width:72ch}
.muted{color:var(--muted)}
.small{font-size:13px}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}
.card{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:16px 18px}
.claim{font-family:var(--serif);font-weight:800;font-size:clamp(20px,3.2vw,26px);margin:0 0 6px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:12px}
.stat{background:var(--surface);border-radius:8px;padding:10px 12px}
.stat b{display:block;font-family:var(--mono);font-size:24px;font-weight:500;line-height:1.2}
.stat span{font-size:12.5px;color:var(--muted)}
.maps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:10px}
figure{margin:0}
figure svg{display:block;width:100%;height:auto}
figcaption{font-weight:700;font-size:14px;margin-bottom:4px}
{fills}
.hatch-l{stroke:var(--muted);stroke-width:1;stroke-opacity:.55}
.frame{fill:none;stroke:var(--rule)}
.dif{fill:none;stroke:var(--saffron);stroke-width:1.6}
.ax{font-family:var(--mono);font-size:9.5px;fill:var(--muted)}
.axs{font-family:var(--sans);font-size:9.5px;fill:var(--muted)}
.axl{font-family:var(--sans);font-size:10.5px;fill:var(--muted)}
.c-sc{fill:var(--low)}.c-fi{fill:var(--saffron)}.c-co{fill:var(--kombu)}.c-na{fill:var(--surface)}
.w0{fill:var(--surface)}.w1{fill:color-mix(in srgb,var(--kombu) 25%,var(--surface))}.w2{fill:color-mix(in srgb,var(--kombu) 55%,var(--surface))}.w3{fill:var(--kombu)}
.wn{font-family:var(--mono);font-size:8.5px;fill:var(--ink);pointer-events:none}
.w3+.wn{fill:var(--card)}
.pt .o{fill:none;stroke:var(--pt-edge);stroke-width:3.4}
.pt .i{stroke:var(--card);stroke-width:1.4;fill:var(--card)}
.pt-yes .i{fill:var(--ink)}
.pt .h{fill:var(--ink)}
.legend{display:flex;flex-wrap:wrap;gap:4px 16px;font-size:12.5px;margin-top:10px;align-items:center}
.legend .it{display:inline-flex;align-items:center;gap:6px}
.sw{display:inline-block;width:12px;height:12px;border-radius:2px}
.sw.ring{border:2px solid var(--saffron);background:transparent}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;border:2px solid var(--pt-edge);background:var(--card)}
.dot.yes{background:var(--ink)}
.dot.opt{background:linear-gradient(90deg,var(--card) 50%,var(--ink) 50%)}
.find{margin:14px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px}
.find li{background:var(--surface);border-radius:8px;padding:10px 14px}
.tablewrap{overflow-x:auto;margin-top:8px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{font-size:12.5px;font-weight:700;text-align:left;padding:7px 8px;border-bottom:2px solid var(--rule);vertical-align:bottom}
td{padding:8px;border-bottom:1px solid var(--rule);vertical-align:top}
td.q{font-family:var(--serif);font-weight:800;font-size:12.5px;line-height:1.6}
.nw{white-space:nowrap}
td.use{min-width:13em}
table.rules{min-width:900px}
.dif2{fill:none;stroke:var(--ink);stroke-width:1.4}
.conf{display:inline-block;font-size:12px;font-weight:700;border-radius:99px;padding:0 9px;border:1px solid currentColor;white-space:nowrap}
.conf.h{color:var(--kombu)}.conf.m{color:var(--saffron)}.conf.l{color:var(--low)}
.cols{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.cols h3{margin-top:0}
.cols ul{margin:6px 0 0;padding-left:1.2em}
.cols li{margin:6px 0}
.verdict{border-left:4px solid var(--saffron);padding:10px 14px;background:var(--surface);border-radius:0 8px 8px 0;margin-top:14px}
.verdict p{margin:4px 0}
table.rec td{height:52px}
table.rec td.photo{min-width:120px}
table.rec td.pred{font-size:12px;color:var(--muted)}
ol.steps{padding-left:1.4em;margin:8px 0}
ol.steps li{margin:6px 0}
a{color:var(--kombu)}
footer{margin-top:48px;font-size:12.5px;color:var(--muted);border-top:1px solid var(--rule);padding-top:12px}
{extra}@media (max-width:720px){
  .maps,.cols{grid-template-columns:minmax(0,1fr)}
  .stats{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:480px){
  body{font-size:14.5px}
  .card{padding:14px 12px}
  table.rec{min-width:640px}
}
"""

# 本人が書く欄（空欄＋材料）。使うページだけに足す
CSS_OWNER = """.owner{border:2px dashed var(--saffron);border-radius:10px;padding:12px 16px;margin-top:12px;background:var(--card)}
.owner .slot{font-weight:700;color:var(--saffron);margin:0 0 4px}
.owner .slot span{font-weight:400;color:var(--muted);font-size:13px}
.owner h4{font-size:13px;margin:10px 0 2px;color:var(--muted)}
.owner ul{margin:4px 0 0;padding-left:1.2em;font-size:13.5px}
.owner li{margin:4px 0}
"""


def css(dishes: list[tuple[str, str, str, str]], extra: str = "") -> str:
    """dishes: [(料理キー, 塗りのクラス, ライトの色, ダークの色)]。extra はページ固有の CSS（メディアクエリの前に入る）。"""
    light = "".join(f"--d-{k}:{lc};" for k, _, lc, _ in dishes)
    dark = "".join(f"--d-{k}:{dc};" for k, _, _, dc in dishes)
    fills = "".join(f".{c}{{fill:var(--d-{k})}}" for k, c, _, _ in dishes)
    return CSS_ROOT.format(light=light, dark=dark) + CSS_BODY.replace("{fills}", fills).replace("{extra}", extra)


# ---------------- 部品 ----------------

def conf(level: str) -> str:
    k = {"高": "h", "中": "m", "低": "l"}[level]
    return f'<span class="conf {k}">確かさ {level}</span>'


def head(title: str, style: str) -> Lines:
    return [f"<title>{e(title)}</title>", *FONTS, f"<style>{style}</style>"]


def header(no: int, h1: str, lead: str) -> str:
    return (f'<header><div class="eyebrow">Cuisine Network · 通説の検証 {no}</div>'
            f'<h1>{h1}</h1>'
            f'<p class="lead">{lead}</p></header>')


def h2(sec_id: str, no: int, title: str, after: str = "") -> str:
    return f'<section id="{sec_id}"><h2><span class="no">{no}</span>{title}</h2>{after}'


def stats(items: list[tuple[object, str]]) -> str:
    return '<div class="stats">' + "".join(f'<div class="stat"><b>{v}</b><span>{lab}</span></div>' for v, lab in items) + "</div>"


def owner_slot(what: str, materials: list[str], note: str = "") -> str:
    """本人が書く欄。本文は空けて「（ここに本人が書く）」と示し、下に材料（事実・数値・出典・確かさ）の箇条書きを置く。"""
    lis = "".join(f"<li>{m}</li>" for m in materials)
    n = f' <span>{note}</span>' if note else ""
    return (f'<div class="owner"><p class="slot">（ここに本人が書く）{e(what)}{n}</p>'
            f'<h4>材料（Claude が集めた事実・数値・出典。本文ではありません）</h4><ul>{lis}</ul></div>')


def rules_table(rule_ids: list[str], use: dict[str, str]) -> Lines:
    rules, _, _ = rules_and_sources(rule_ids)
    out = ['<h3>使った規則（Exp-14 rules.yaml）</h3><div class="tablewrap"><table class="rules"><thead><tr><th>id</th><th>内容</th><th>出典の文面</th><th>出典</th><th>確かめ方</th><th>確かさ</th><th>計算での扱い</th></tr></thead><tbody>']
    for rid in rule_ids:
        r = rules[rid]
        src = r.get("source")
        src = "・".join(src) if isinstance(src, list) else (src or "—")
        vals = r.get("values") or "—"
        out.append(f'<tr><td class="num nw">{rid}</td><td>{e(r["effect"])}</td><td class="q">{e(str(vals))}</td><td>{e(src)}</td><td class="nw">{e(r["check"])}</td>'
                   f'<td>{conf(r["confidence"])}</td><td class="small use">{e(use[rid])}</td></tr>')
    out.append('</tbody></table></div>')
    return out


def sources_table(source_ids: list[str], check: dict[str, tuple[str, str]], col4: str = "この通説について言っていること") -> Lines:
    _, srcs, _ = rules_and_sources([])
    out = [f'<h3>出典と確かめ方</h3><div class="tablewrap"><table><thead><tr><th>出典</th><th>何か</th><th>確かめ方</th><th>{col4}</th></tr></thead><tbody>']
    for sid in source_ids:
        s = srcs[sid]
        how, what = check[sid]
        url = s.get("url")
        cite = e(s["cite"]) + (f' <a href="{e(url)}" target="_blank" rel="noopener">リンク</a>' if url else "")
        out.append(f'<tr><td class="num">{sid}</td><td>{cite}</td><td class="nw">{e(how)}</td><td class="small">{e(what)}</td></tr>')
    out.append('</tbody></table></div>')
    return out


def conflicts_block(ids: list[str]) -> Lines:
    _, _, conflicts = rules_and_sources([])
    out = ['<h3>出典どうしの食い違い（そのまま載せます）</h3>']
    for cid in ids:
        out.append(f'<p class="small"><b>{cid}</b> {e(conflicts[cid])}</p>')
    return out


def can_cannot(can: list[str], cannot: list[str]) -> Lines:
    return ['<div class="card"><h3>言えること</h3><ul>' + "".join(f"<li>{x}</li>" for x in can) + '</ul></div>',
            '<div class="card"><h3>言えないこと</h3><ul>' + "".join(f"<li>{x}</li>" for x in cannot) + '</ul></div></div>']


def steps(items: list[str]) -> str:
    return '<h3>手順</h3><ol class="steps">' + "".join(f"<li>{x}</li>" for x in items) + '</ol>'


def record_table(cols: list[str], rows: list[str]) -> Lines:
    return ['<div class="tablewrap"><table class="rec"><thead><tr>' + "".join(f"<th>{c}</th>" for c in cols) + '</tr></thead><tbody>',
            *rows,
            '</tbody></table></div>']


def footer(text: str) -> str:
    return f"<footer>{text}</footer>"


def join(lines: Lines) -> str:
    return "\n".join(lines) + "\n"


# ---------------- 見せ方の組み直し（2026-10-22、motivation.md §14） ----------------
# 通説ページの節の順: 判定と確かさ → 決め手の図 → 言えないこと → 自分で試す → 通説 → 計算の詳しい答え →（ほかの節）→ 根拠。
# 根拠の詳しい中身は規則のページ・出典のページ（experiments/myths/basis.py、writeup/basis/）に切り出して共有する。

ORDER_HEAD = ["verdict", "keyfig", "cannot", "try", "claim", "calc"]
ORDER_TAIL = ["basis"]


def can_card(items: list[str]) -> str:
    return '<div class="card"><h3>言えること</h3><ul>' + "".join(f"<li>{x}</li>" for x in items) + '</ul></div>'


def cannot_card(items: list[str]) -> str:
    return '<div class="card"><h3>言えないこと</h3><ul>' + "".join(f"<li>{x}</li>" for x in items) + '</ul></div>'


def keyfig(caption: str, svg: str, note: str) -> str:
    """決め手の図1枚。地図の一覧（div.maps）とは別に、class="key" の figure で置く。"""
    return (f'<section id="keyfig"><h2><span class="no">0</span>決め手の図</h2>'
            f'<figure class="key"><figcaption>{caption}</figcaption>{svg}</figure><p class="small">{note}</p></section>')


def basis_links(rule_ids: list[str], source_ids: list[str]) -> str:
    """根拠の節の頭に置く、規則のページ・出典のページへのリンク（writeup/basis/）。"""
    r = "・".join(f'<a href="basis/rules/{x}.html">{x}</a>' for x in rule_ids)
    s = "・".join(f'<a href="basis/sources/{x}.html">{x}</a>' for x in source_ids)
    return (f'<p class="small">規則ごとのページ（値・出典の文面・確かめ方・食い違い・使っている通説）: {r}。'
            f'出典ごとのページ: {s}。<a href="basis/index.html">規則と出典の一覧</a></p>')


def reorder(page_html: str) -> str:
    """節（section）を ORDER_HEAD・（ほか）・ORDER_TAIL の順に並べ替え、見出しの番号を振り直す。"""
    import re
    secs = list(re.finditer(r'<section id="([a-z-]+)">.*?</section>', page_html, re.S))
    ids = [m.group(1) for m in secs]
    for need in ORDER_HEAD + ORDER_TAIL:
        if ids.count(need) != 1:
            raise ValueError(f"節 {need} が {ids.count(need)} 個")
    between = page_html[secs[0].end():secs[-1].start()]
    if re.sub(r'<section id="[a-z-]+">.*?</section>', "", between, flags=re.S).strip():
        raise ValueError("節と節の間に節以外のものがある")
    body = {m.group(1): m.group(0) for m in secs}
    mid = [i for i in ids if i not in ORDER_HEAD + ORDER_TAIL]
    out = []
    for n, sid in enumerate(ORDER_HEAD + mid + ORDER_TAIL, 1):
        out.append(re.sub(r'(<h2><span class="no">)\d+(</span>)', lambda m: f"{m.group(1)}{n}{m.group(2)}", body[sid], count=1))
    return page_html[:secs[0].start()] + "\n".join(out) + page_html[secs[-1].end():]


# ---------------- 汎用の図（2026-10-22、通説3本目から） ----------------
# 色は4系列まで（--kombu・--saffron・--low・--ink）。ページの CSS に CSS_FIG を足して使う。
CSS_FIG = """.fg-grid{stroke:var(--rule);stroke-width:1}
.fg-s0{stroke:var(--kombu)}.fg-s1{stroke:var(--saffron)}.fg-s2{stroke:var(--low)}.fg-s3{stroke:var(--ink)}
.fg-f0{fill:var(--kombu)}.fg-f1{fill:var(--saffron)}.fg-f2{fill:var(--low)}.fg-f3{fill:var(--ink)}
.fg-line{fill:none;stroke-width:2.2}.fg-dash{stroke-dasharray:5 4}
.fg-h{stroke:var(--muted);stroke-width:1;stroke-dasharray:3 3}
.fg-lab{font-family:var(--sans);font-size:11.5px;fill:var(--ink)}
.fg-ax{font-family:var(--mono);font-size:11.5px;fill:var(--muted)}
.fg-key{display:inline-block;width:18px;height:0;border-top:3px solid;vertical-align:middle;margin-right:6px}
"""


def _ticks(lo: float, hi: float, n: int = 5) -> list[float]:
    import math
    span = hi - lo
    raw = span / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw), default=raw)
    t = math.ceil(lo / step) * step
    out = []
    while t <= hi + 1e-9:
        out.append(round(t, 9))
        t += step
    return out


def svg_lines(series: list[tuple[str, int, list[tuple[float, float]], bool]], x_lab: str, y_lab: str,
              x_rng: tuple[float, float], y_rng: tuple[float, float], hlines: list[tuple[float, str]] = ()) -> str:
    """折れ線。series = [(凡例, 色番号0〜3, [(x, y)...], 破線か)]。hlines = [(y, 札)]。凡例は図の下に HTML で出す。"""
    W, H, L, R, T, B = 640, 300, 52, 16, 14, 42
    pw, ph = W - L - R, H - T - B
    (x0, x1), (y0, y1) = x_rng, y_rng
    X = lambda x: L + (x - x0) / (x1 - x0) * pw  # noqa: E731
    Y = lambda y: T + ph - (y - y0) / (y1 - y0) * ph  # noqa: E731
    P = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(y_lab)}と{e(x_lab)}">']
    for v in _ticks(y0, y1):
        P.append(f'<line class="fg-grid" x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/>'
                 f'<text class="fg-ax" x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{v:g}</text>')
    for v in _ticks(x0, x1):
        P.append(f'<text class="fg-ax" x="{X(v):.1f}" y="{H - B + 18}" text-anchor="middle">{v:g}</text>')
    P.append(f'<text class="fg-lab" x="{L + pw / 2:.1f}" y="{H - 6}" text-anchor="middle">{e(x_lab)}</text>')
    P.append(f'<text class="fg-lab" x="12" y="{T + ph / 2:.1f}" text-anchor="middle" transform="rotate(-90 12 {T + ph / 2:.1f})">{e(y_lab)}</text>')
    for v, lab in hlines:
        P.append(f'<line class="fg-h" x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/>'
                 f'<text class="fg-ax" x="{W - R - 4}" y="{Y(v) - 4:.1f}" text-anchor="end">{e(lab)}</text>')
    for lab, c, pts, dash in series:
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(x):.1f},{Y(y):.1f}" for i, (x, y) in enumerate(pts))
        P.append(f'<path class="fg-line fg-s{c}{" fg-dash" if dash else ""}" d="{d}"><title>{e(lab)}</title></path>')
    P.append("</svg>")
    return "".join(P)


def svg_bars(items: list[tuple[str, float, int]], unit: str, x_max: float | None = None, fmt: str = "{:.1f}") -> str:
    """横棒。items = [(札, 値, 色番号0〜3)]。"""
    n = len(items)
    W, row, L, R = 640, 34, 230, 70
    H = row * n + 10
    vmax = x_max or max(v for _, v, _ in items) or 1
    P = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="横棒グラフ">']
    for i, (lab, v, c) in enumerate(items):
        y = 6 + i * row
        w = max(0.0, v) / vmax * (W - L - R)
        P.append(f'<text class="fg-lab" x="{L - 8}" y="{y + 18}" text-anchor="end">{e(lab)}</text>'
                 f'<rect class="fg-f{c}" x="{L}" y="{y + 4}" width="{w:.1f}" height="{row - 12}" rx="3"/>'
                 f'<text class="fg-ax" x="{L + w + 6:.1f}" y="{y + 18}">{fmt.format(v)}{e(unit)}</text>')
    P.append("</svg>")
    return "".join(P)


def legend_lines(items: list[tuple[str, int, bool]]) -> str:
    return '<div class="legend">' + "".join(
        f'<span class="it"><span class="fg-key" style="border-color:var({["--kombu", "--saffron", "--low", "--ink"][c]});{"border-top-style:dashed;" if dash else ""}"></span>{lab}</span>'
        for lab, c, dash in items) + '</div>'

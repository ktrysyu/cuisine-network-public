"""根拠のページ: 規則のページ（1つの規則＝1ページ）と出典のページ（1つの出典＝1ページ）。

    uv run python experiments/myths/basis.py

motivation.md §14（2026-09-28）の「根拠は1枚に積まず、個別のページに切る」。複数の通説から共有される。
- 規則のページ: 事実（effect）・条件・出典の文面・確かめ方・確かさ・計算で使う採用値・食い違い・この規則を使っている通説
- 出典のページ: 文献の書誌・確かめ方・この出典から取った規則と採用値・この出典を使っている通説
- 中身は rules.yaml から引く（書き写さない）。どこまで確かめたか（本文確認／抄録確認／抜粋のみ／推定）を見出しのすぐ下に出す

中身（本文の HTML）は pages(link) が返す。link はページの種類と鍵から相対 URL を返す関数で、研究ノートの
writeup/basis/ と公開用サイト（tools/sync.py）で同じ中身を別の外枠に入れるために分けてある。
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from myths import common as C  # noqa: E402
from myths.build import MYTHS, load  # noqa: E402

e = html.escape
OUT = C.WRITEUP / "basis"
Link = Callable[[str, str], str]   # (種類 "rule" | "source" | "myth" | "index", 鍵) → 相対 URL（ページの置き場所から）

CHECK_ORDER = ["本文確認", "抄録確認", "抜粋のみ", "推定", "未確認"]


def _list(v) -> list[str]:
    if v is None:
        return []
    return [str(x) for x in v] if isinstance(v, list) else [str(v)]


def _src_ids(v, sources: dict) -> list[str]:
    """source 欄（文字列・リスト・「a・b」）から出典 id を拾う。"""
    out = []
    for s in _list(v):
        for t in re.split(r"[・,、\s]+", s):
            t = t.strip()
            if t in sources and t not in out:
                out.append(t)
    return out


def _check_word(check: str | None) -> str:
    c = str(check or "—")
    for w in CHECK_ORDER:
        if c.startswith(w):
            return w
    return c


def _walk_sources(node, path: str, sources: dict, found: dict[str, list[tuple[str, dict]]]) -> None:
    """sim の下の値で source を持つもの（採用値・モデルの係数など）を出典ごとに集める。"""
    if isinstance(node, dict):
        if "source" in node and ("value" in node or "check" in node or "cite" not in node):
            for sid in _src_ids(node.get("source"), sources):
                found.setdefault(sid, []).append((path, node))
        for k, v in node.items():
            if k != "source":
                _walk_sources(v, f"{path}.{k}" if path else str(k), sources, found)


def myths_info() -> list[dict]:
    """通説ごとの id・題・使った規則・出典（規則の出典も含める）。"""
    out = []
    for mid in MYTHS:
        m = load(mid)
        title = mid
        if m.OUT.exists():
            h1 = re.search(r"<h1>(.*?)</h1>", m.OUT.read_text(encoding="utf-8"), re.S)
            if h1:
                title = re.sub(r"<[^>]+>", "", h1.group(1))
        out.append({"id": mid, "title": title, "rules": list(m.RULE_IDS), "sources": list(m.SOURCE_IDS)})
    return out


def data() -> dict:
    R = C.P.rules()
    rules = {r["id"]: r for r in R["rules"]}
    sources = R["sources"]
    conflicts = R.get("conflicts") or {}
    av = R["sim"]["adopted_values"]
    myths = myths_info()
    for m in myths:
        extra = [s for rid in m["rules"] for s in _src_ids(rules[rid].get("source"), sources)]
        m["all_sources"] = list(dict.fromkeys(m["sources"] + extra))
    by_src: dict[str, list[tuple[str, dict]]] = {}
    _walk_sources(R["sim"], "sim", sources, by_src)
    return {"rules": rules, "sources": sources, "conflicts": conflicts, "adopted": av, "myths": myths, "sim_by_source": by_src}


def _rule_ids_in(text) -> list[str]:
    return re.findall(r"R-[A-Z]+\d+", str(text or ""))


def _check_badge(check) -> str:
    w = _check_word(check)
    rest = str(check or "—")
    detail = f'<span class="muted">{e(rest)}</span>' if rest != w else ""
    return f'<p class="check"><span class="ck">{e(w)}</span>{detail}</p>'


def rule_title(r: dict) -> str:
    """規則の題: 変数名で始まる effect（例 egg_yolk_stage 2→3（固ゆで卵のほろほろ））は、括弧の中の日本語と条件で言い直す。"""
    eff = str(r.get("effect", r["id"]))
    m = re.match(r"^[a-z_]+[^（]*（(.+)）\s*$", eff)
    words = m.group(1) if m else eff
    cond = str(r.get("condition") or "").strip()
    return f"{cond}: {words}" if cond and m else words


def rule_body(rid: str, D: dict, link: Link) -> str:
    r = D["rules"][rid]
    srcs = _src_ids(r.get("source"), D["sources"])
    av = [(k, v) for k, v in D["adopted"].items() if rid in _rule_ids_in(v.get("rule"))]
    cids = list(dict.fromkeys([c for _, v in av for c in _list(v.get("conflict"))]
                              + [c for c, t in D["conflicts"].items() if rid in str(t)]))
    used = [m for m in D["myths"] if rid in m["rules"]]
    H = [f'<p class="eyebrow">規則 · {e(rid)}</p>',
         f'<h1>{e(rule_title(r))}</h1>',
         _check_badge(r.get("check")),
         '<dl class="facts">',
         f'<dt>計算での書き方</dt><dd>{e(str(r.get("effect", "—")))}</dd>',
         f'<dt>確かさ</dt><dd>{e(str(r.get("confidence", "—")))}</dd>',
         f'<dt>条件</dt><dd>{e(str(r.get("condition", "—")))}</dd>',
         f'<dt>対象</dt><dd>{e(str(r.get("applies_to", "—")))}（操作 {e(str(r.get("op", "—")))}）</dd>',
         '</dl>',
         '<h2>出典の文面</h2>',
         f'<blockquote>{e(str(r.get("values") or "—"))}</blockquote>',
         '<p>出典: ' + ("・".join(f'<a href="{link("source", s)}">{e(s)}</a>' for s in srcs) or e(str(r.get("source") or "—"))) + '</p>']
    if r.get("note"):
        H.append(f'<p class="muted">注: {e(str(r["note"]))}</p>')
    H.append('<h2>計算で使う値（採用値）</h2>')
    if av:
        H.append('<div class="tablewrap"><table><thead><tr><th>名前</th><th>値</th><th>出典</th><th>ほかの値</th><th>確かめ方</th></tr></thead><tbody>')
        for k, v in av:
            val = f'{v.get("value")}{v.get("unit", "")}'
            alt = "・".join(_list(v.get("alternatives"))) or "—"
            sl = "・".join(f'<a href="{link("source", s)}">{e(s)}</a>' for s in _src_ids(v.get("source"), D["sources"])) or e(str(v.get("source") or "—"))
            H.append(f'<tr><td class="num">{e(k)}</td><td class="num">{e(val)}</td><td>{sl}</td><td>{e(alt)}</td><td>{e(str(v.get("check", "—")))}</td></tr>')
        H.append('</tbody></table></div>')
    else:
        H.append('<p class="muted">この規則に結びついた採用値はありません（計算の中で条件として使うか、使っていません）。</p>')
    H.append('<h2>出典どうしの食い違い</h2>')
    if cids:
        H += [f'<p><b>{e(c)}</b> {e(str(D["conflicts"].get(c, "")))}</p>' for c in cids if c in D["conflicts"]]
    else:
        H.append('<p class="muted">記録した食い違いはありません。</p>')
    H.append('<h2>この規則を使っている通説</h2>')
    H.append('<ul>' + "".join(f'<li><a href="{link("myth", m["id"])}">{e(m["title"])}</a></li>' for m in used) + '</ul>'
             if used else '<p class="muted">まだどの通説ページでも使っていません（調理の計算の中では使われています）。</p>')
    H.append(f'<p class="small"><a href="{link("index", "")}">規則と出典の一覧へ</a></p>')
    return "\n".join(H)


def source_body(sid: str, D: dict, link: Link) -> str:
    s = D["sources"][sid]
    rules = [rid for rid, r in D["rules"].items() if sid in _src_ids(r.get("source"), D["sources"])]
    simv = D["sim_by_source"].get(sid, [])
    used = [m for m in D["myths"] if sid in m["all_sources"]]
    url = s.get("url")
    H = [f'<p class="eyebrow">出典 · {e(sid)}</p>',
         f'<h1>{e(str(s.get("cite", sid)))}</h1>',
         _check_badge(s.get("check")),
         '<dl class="facts">',
         f'<dt>種類</dt><dd>{e(str(s.get("type", "—")))}</dd>',
         f'<dt>場所</dt><dd>' + (f'<a href="{e(url)}" rel="noopener">{e(url)}</a>' if url else "—") + '</dd>',
         '</dl>']
    if s.get("note"):
        H.append(f'<p class="muted">注: {e(str(s["note"]))}</p>')
    H.append('<h2>この出典から取った規則</h2>')
    H.append('<ul>' + "".join(f'<li><a href="{link("rule", rid)}">{e(rid)}</a> {e(str(D["rules"][rid].get("effect", "")))}'
                              f'<span class="muted">（{e(_check_word(D["rules"][rid].get("check")))}・確かさ {e(str(D["rules"][rid].get("confidence", "—")))}）</span></li>'
                              for rid in rules) + '</ul>' if rules else '<p class="muted">規則としては使っていません。</p>')
    H.append('<h2>この出典から取った計算の値</h2>')
    if simv:
        H.append('<ul>' + "".join(f'<li><code>{e(p)}</code>' + (f' = {e(str(v.get("value")))}{e(str(v.get("unit", "")))}' if "value" in v else "")
                                  + (f'<span class="muted">（{e(str(v.get("check")))}）</span>' if v.get("check") else "") + '</li>' for p, v in simv) + '</ul>')
    else:
        H.append('<p class="muted">計算の値（採用値・係数）としては使っていません。</p>')
    H.append('<h2>この出典を使っている通説</h2>')
    H.append('<ul>' + "".join(f'<li><a href="{link("myth", m["id"])}">{e(m["title"])}</a></li>' for m in used) + '</ul>'
             if used else '<p class="muted">まだどの通説ページでも使っていません。</p>')
    H.append(f'<p class="small"><a href="{link("index", "")}">規則と出典の一覧へ</a></p>')
    return "\n".join(H)


def index_body(D: dict, link: Link) -> str:
    def cnt(items):
        c = {}
        for x in items:
            c[_check_word(x.get("check"))] = c.get(_check_word(x.get("check")), 0) + 1
        return "・".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: CHECK_ORDER.index(kv[0]) if kv[0] in CHECK_ORDER else 99))
    H = ['<p class="eyebrow">Cuisine Network · 根拠</p>', '<h1>規則と出典</h1>',
         '<p>通説ページと調理の計算が使っている規則（1つの事実）と出典を、1つずつのページにしました。どこまで確かめたか（本文を読んだか、抜粋だけか）を各ページの先頭に出しています。この一覧は Claude（Anthropic の AI）が集めた記録から自動で作っています。</p>',
         f'<h2>規則（{len(D["rules"])}）</h2><p class="muted small">確かめ方: {e(cnt(D["rules"].values()))}</p>',
         '<div class="tablewrap"><table><thead><tr><th>id</th><th>事実</th><th>確かめ方</th><th>確かさ</th><th>通説</th></tr></thead><tbody>']
    for rid, r in D["rules"].items():
        n = sum(rid in m["rules"] for m in D["myths"])
        H.append(f'<tr><td class="num"><a href="{link("rule", rid)}">{e(rid)}</a></td><td>{e(str(r.get("effect", "")))}</td>'
                 f'<td>{e(_check_word(r.get("check")))}</td><td>{e(str(r.get("confidence", "—")))}</td><td class="num">{n or ""}</td></tr>')
    H += ['</tbody></table></div>',
          f'<h2>出典（{len(D["sources"])}）</h2><p class="muted small">確かめ方: {e(cnt(D["sources"].values()))}</p>',
          '<div class="tablewrap"><table><thead><tr><th>id</th><th>出典</th><th>確かめ方</th></tr></thead><tbody>']
    for sid, s in D["sources"].items():
        H.append(f'<tr><td class="num"><a href="{link("source", sid)}">{e(sid)}</a></td><td>{e(str(s.get("cite", "")))}</td><td>{e(_check_word(s.get("check")))}</td></tr>')
    H.append('</tbody></table></div>')
    return "\n".join(H)


def pages(link_for: Callable[[str], Link]) -> list[tuple[str, str, str]]:
    """[(置き場所の相対パス, 題, 本文 HTML)]。link_for(置き場所) がそのページから見た link を返す。"""
    D = data()
    out = [("index.html", "規則と出典", index_body(D, link_for("index.html")))]
    for rid in D["rules"]:
        p = f"rules/{rid}.html"
        out.append((p, f"規則 {rid}", rule_body(rid, D, link_for(p))))
    for sid in D["sources"]:
        p = f"sources/{sid}.html"
        out.append((p, f"出典 {sid}", source_body(sid, D, link_for(p))))
    return out


# ---------------- 研究ノート側（writeup/basis/）の外枠 ----------------

def myth_file(mid: str) -> str:
    return load(mid).OUT.name


def writeup_link(place: str) -> Link:
    up = "../" * place.count("/")

    def link(kind: str, key: str) -> str:
        if kind == "rule":
            return f"{up}rules/{key}.html"
        if kind == "source":
            return f"{up}sources/{key}.html"
        if kind == "myth":
            return f"{up}../{myth_file(key)}"
        return f"{up}index.html"
    return link


CSS = """:root{--ground:#FCFCFC;--surface:#F3F3F3;--rule:#E1E1E1;--ink:#171717;--ink-muted:#606060;--main:#B63552;--on-main:#FFFFFF;
--heading:"Hanken Grotesk","Noto Sans JP",system-ui,sans-serif;--body:"IBM Plex Sans","IBM Plex Sans JP",system-ui,sans-serif;--numeric:"Roboto Mono",ui-monospace,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--ground:#101010;--surface:#1D1D1D;--rule:#2E2E2E;--ink:#EEEEEE;--ink-muted:#A4A4A4;--main:#FB8495}}
:root[data-theme="dark"]{color-scheme:dark;--ground:#101010;--surface:#1D1D1D;--rule:#2E2E2E;--ink:#EEEEEE;--ink-muted:#A4A4A4;--main:#FB8495}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.75;letter-spacing:.04em;padding:0 16px 64px}
main{max-width:860px;margin:0 auto;padding-top:40px}
h1{font-family:var(--heading);font-size:clamp(22px,4vw,30px);line-height:1.4;margin:8px 0;letter-spacing:.05em}
h2{font-family:var(--heading);font-size:19px;margin:40px 0 8px;letter-spacing:.05em}
p,ul{margin:0 0 16px}
.eyebrow{font-family:var(--numeric);font-size:11.5px;color:var(--main);margin:0;letter-spacing:.08em}
.muted{color:var(--ink-muted)}.small{font-size:13.5px}
.num,code{font-family:var(--numeric)}
a{color:var(--main)}
.check{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:13.5px}
.check .ck{background:var(--main);color:var(--on-main);border-radius:4px;padding:0 8px;font-weight:600}
dl.facts{display:grid;grid-template-columns:max-content 1fr;gap:8px 16px;margin:16px 0}
dl.facts dt{color:var(--ink-muted);font-size:13.5px}dl.facts dd{margin:0}
blockquote{margin:0 0 8px;padding:8px 16px;background:var(--surface);border-radius:8px;font-size:15px}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{text-align:left;background:var(--surface);padding:8px}td{padding:8px;border-bottom:1px solid var(--rule);vertical-align:top}
footer{max-width:860px;margin:64px auto 0;font-size:13.5px;color:var(--ink-muted);border-top:1px solid var(--rule);padding-top:8px}
"""
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@700&family=Noto+Sans+JP:wght@700'
         '&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Sans+JP:wght@400;600&family=Roboto+Mono:wght@500&display=swap">')


def wrap(title: str, body: str) -> str:
    return (f'<!doctype html>\n<html lang="ja">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(title)}</title>{FONTS}<style>{CSS}</style></head>\n<body><main>\n{body}\n</main>'
            '<footer>Cuisine Network 研究ノートの根拠のページ。experiments/myths/basis.py が rules.yaml から生成します（Claude の記録）。</footer></body>\n</html>\n')


def built() -> dict[Path, str]:
    return {OUT / p: wrap(t, b) for p, t, b in pages(writeup_link)}


def main() -> None:
    files = built()
    for p, text in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print("wrote", len(files), "pages under", OUT)


if __name__ == "__main__":
    main()

"""本人の確認ページ（下書きを見て直す用）を作る（2026-10-22、night-queue 作業列 12）。

    uv run python experiments/review/build_review.py

- writeup/review-texture.html（食材の食感スコアの下書き、data/labels/texture_draft.csv）
- writeup/review-temporal.html（時間の層の下書き、data/labels/temporal_draft.csv）
- writeup/review-aroma-manual.html（香りの手動対応 81 件、data/labels/aroma_mapping.csv の method=manual）
どれも下書きまで。値を決めるのは本人。入力はこのブラウザに自動で残り（localStorage）、「CSV で保存」で書き出す。
claude.ai には出していない（公開していない）。
"""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "data" / "labels"
WRITEUP = ROOT / "writeup"
e = html.escape

CSS = """:root{--ground:#FCFCFC;--surface:#F3F3F3;--rule:#E1E1E1;--ink:#171717;--ink-muted:#606060;--main:#B63552;--on-main:#FFFFFF;--sub:#00C9D4;
--heading:"Hanken Grotesk","Noto Sans JP",system-ui,sans-serif;--body:"IBM Plex Sans","IBM Plex Sans JP",system-ui,sans-serif;--numeric:"Roboto Mono",ui-monospace,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--ground:#101010;--surface:#1D1D1D;--rule:#2E2E2E;--ink:#EEEEEE;--ink-muted:#A4A4A4;--main:#FB8495;--on-main:#1A0E10;--sub:#00A8B3}}
:root[data-theme="dark"]{color-scheme:dark;--ground:#101010;--surface:#1D1D1D;--rule:#2E2E2E;--ink:#EEEEEE;--ink-muted:#A4A4A4;--main:#FB8495;--on-main:#1A0E10;--sub:#00A8B3}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.75;letter-spacing:.04em;padding:0 16px 64px}
main{max-width:1100px;margin:0 auto;padding-top:40px}
h1{font-family:var(--heading);font-size:clamp(22px,4vw,30px);margin:8px 0;letter-spacing:.05em}
p{margin:0 0 16px;max-width:72ch}
.eyebrow{font-family:var(--numeric);font-size:11.5px;color:var(--main);letter-spacing:.08em;margin:0}
.muted{color:var(--ink-muted)}.small{font-size:13.5px}
.bar{position:sticky;top:0;background:var(--ground);padding:8px 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center;border-bottom:1px solid var(--rule);z-index:2}
button{font:inherit;font-size:13.5px;border:1px solid var(--rule);background:var(--surface);color:var(--ink);border-radius:8px;padding:4px 12px;cursor:pointer}
button.primary{background:var(--main);color:var(--on-main);border-color:var(--main)}
.tablewrap{overflow-x:auto;margin-top:16px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{text-align:left;background:var(--surface);padding:8px}
label{white-space:nowrap}
td{padding:8px;border-bottom:1px solid var(--rule);vertical-align:top}
td.num{font-family:var(--numeric)}
select,input[type=text]{font:inherit;font-size:13.5px;background:var(--ground);color:var(--ink);border:1px solid var(--rule);border-radius:4px;padding:2px 4px}
input[type=text]{width:12em}
tr.done td:first-child{box-shadow:inset 3px 0 0 var(--main)}
.draft{color:var(--ink-muted);font-family:var(--numeric)}
"""

JS = """
const KEY='review-'+PAGE.id;
let state={};
try{state=JSON.parse(localStorage.getItem(KEY)||'{}')||{};}catch(e){state={};}
function save(){try{localStorage.setItem(KEY,JSON.stringify(state));}catch(e){}}
const tb=document.getElementById('tb');
function cell(r,f){
  const v=(state[r.key]&&state[r.key][f.key]!==undefined)?state[r.key][f.key]:(f.draft?r[f.draft]:'');
  if(f.type==='score'){
    const opts=['','0','1','2','3','4','5'].map(o=>`<option value="${o}"${String(v)===o?' selected':''}>${o===''?'—':o}</option>`).join('');
    return `<select data-k="${r.key}" data-f="${f.key}">${opts}</select>`+(f.draft?`<div class="draft small">下書き ${r[f.draft]===''?'—':r[f.draft]}</div>`:'');
  }
  if(f.type==='choice'){
    const opts=[''].concat(f.choices).map(o=>`<option value="${o}"${String(v)===o?' selected':''}>${o===''?'—':o}</option>`).join('');
    return `<select data-k="${r.key}" data-f="${f.key}">${opts}</select>`+(f.draft?`<div class="draft small">下書き ${r[f.draft]||'—'}</div>`:'');
  }
  return `<input type="text" data-k="${r.key}" data-f="${f.key}" value="${String(v).replace(/"/g,'&quot;')}">`;
}
function render(){
  const only=document.getElementById('only').checked;
  tb.innerHTML=PAGE.rows.filter(r=>!only||!(state[r.key]&&state[r.key]._ok)).map(r=>{
    const ok=state[r.key]&&state[r.key]._ok;
    return `<tr class="${ok?'done':''}"><td><b>${r.ja}</b><div class="muted small">${r.key}</div></td>`
      +PAGE.info.map(c=>`<td class="small">${r[c]||''}</td>`).join('')
      +PAGE.fields.map(f=>`<td>${cell(r,f)}</td>`).join('')
      +`<td><label class="small"><input type="checkbox" data-ok="${r.key}"${ok?' checked':''}> 確認した</label></td></tr>`;
  }).join('');
  document.getElementById('count').textContent=`確認した ${PAGE.rows.filter(r=>state[r.key]&&state[r.key]._ok).length} / ${PAGE.rows.length}`;
}
tb.addEventListener('change',ev=>{
  const t=ev.target;
  if(t.dataset.ok){state[t.dataset.ok]=state[t.dataset.ok]||{};state[t.dataset.ok]._ok=t.checked;save();render();return;}
  const k=t.dataset.k,f=t.dataset.f; if(!k)return;
  state[k]=state[k]||{};state[k][f]=t.value;save();
});
document.getElementById('only').addEventListener('change',render);
document.getElementById('csv').addEventListener('click',()=>{
  const head=['key','ja'].concat(PAGE.fields.map(f=>f.key)).concat(['confirmed']);
  const q=s=>'"'+String(s==null?'':s).replace(/"/g,'""')+'"';
  const lines=[head.join(',')].concat(PAGE.rows.map(r=>{
    const s=state[r.key]||{};
    return [r.key,r.ja].concat(PAGE.fields.map(f=>s[f.key]!==undefined?s[f.key]:(f.draft?r[f.draft]:''))).concat([s._ok?1:0]).map(q).join(',');
  }));
  const blob=new Blob(['\\ufeff'+lines.join('\\n')],{type:'text/csv'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=PAGE.id+'_reviewed.csv';a.click();
});
render();
"""


def page(pid: str, title: str, lead: list[str], info: list[tuple[str, str]], fields: list[dict], rows: list[dict]) -> str:
    data = {"id": pid, "info": [k for k, _ in info], "fields": fields, "rows": rows}
    heads = "".join(f"<th>{e(lab)}</th>" for _, lab in info) + "".join(f"<th>{e(f['label'])}</th>" for f in fields)
    return (f'<!doctype html>\n<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(title)}</title>'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@700&family=Noto+Sans+JP:wght@700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Sans+JP:wght@400;600&family=Roboto+Mono:wght@500&display=swap">'
            f'<style>{CSS}</style></head><body><main>'
            f'<p class="eyebrow">Cuisine Network · 本人の確認（下書き）</p><h1>{e(title)}</h1>'
            + "".join(f"<p>{x}</p>" for x in lead)
            + '<div class="bar"><span id="count" class="small"></span><label class="small"><input type="checkbox" id="only"> 確認していないものだけ</label>'
              '<button class="primary" id="csv">CSV で保存</button><span class="muted small">入力はこのブラウザに自動で残ります。保存した CSV を Claude に渡してください。</span></div>'
            f'<div class="tablewrap"><table><thead><tr><th>食材</th>{heads}<th></th></tr></thead><tbody id="tb"></tbody></table></div>'
            f'</main><script>const PAGE={json.dumps(data, ensure_ascii=False)};{JS}</script></body></html>\n')


def read(name):
    return list(csv.DictReader((LAB / name).open(encoding="utf-8")))


def main() -> None:
    tx = read("texture_draft.csv")
    rows = [{"key": r["ingredient"], "ja": e(r["ja"]), "form": e(r["form"]), "basis": e(r["basis"]),
             **{f"d_{k}": r[k] for k in ("hardness", "thickness", "juiciness", "chewiness", "smoothness")}} for r in tx]
    out = {
        "review-texture.html": page(
            "texture", "食材の食感スコア（下書き）",
            ["303 食材の食感を、料理でふつうに使う形（生で食べる野菜は生、ふつう加熱するものは加熱後）で 0〜5 で付けた下書きです。"
             "下書きは食材の種類ごとに Claude が置いた値で、出典はありません。違うと思ったら直して「確認した」に印を付けてください。",
             "項目: 硬さ（0 液体〜5 よく焼いた肉）・粘り/とろみ（0 水〜5 練乳）・みずみずしさ（0 乾いている〜5 水そのもの）・歯ごたえ（0 なし〜5 噛み切りにくい）・なめらかさ（0 ぼそぼそ・粒っぽい〜5 つるん）。"
             "粉・香辛料・塩・砂糖などは対象外（空欄）にしてあります。付けたければ付けてください。"],
            [("form", "想定した形"), ("basis", "下書きの根拠")],
            [{"key": k, "label": lab, "type": "score", "draft": f"d_{k}"} for k, lab in
             (("hardness", "硬さ"), ("thickness", "粘り・とろみ"), ("juiciness", "みずみずしさ"), ("chewiness", "歯ごたえ"), ("smoothness", "なめらかさ"))]
            + [{"key": "memo", "label": "メモ", "type": "text"}], rows),
    }
    tp = read("temporal_draft.csv")
    rows = [{"key": r["ingredient"], "ja": e(r["ja"]), "basis": e(r["basis"]), "d_onset": r["onset"] and str(round(float(r["onset"]))),
             "d_linger": r["linger"] and str(round(float(r["linger"]))), "d_first": r["first"], "d_last": r["last"]} for r in tp]
    tastes = ["甘", "塩", "酸", "苦", "旨", "辛", "香り"]
    out["review-temporal.html"] = page(
        "temporal", "時間の層（下書き）: 感じる順番と余韻",
        ["303 食材について、口に入れてからの「立ち上がりの早さ」「余韻の長さ」と「最初に来る味」「最後に残る味」の下書きです（Exp-13）。",
         "下書きは本人の味のスコアから規則で出したものです（塩は早く来て残らない、苦味は遅く来て残る、など。規則と出典は experiments/exp-13/plan.md）。"
         "出典で確かめたのは塩と苦味の立ち上がりの順と、苦味が残ることだけで、ほかは推定です。香りの時間は入っていません。味が全軸 0 の食材は空欄です。"],
        [("basis", "下書きの根拠")],
        [{"key": "onset", "label": "立ち上がりの早さ（5 が早い）", "type": "score", "draft": "d_onset"},
         {"key": "linger", "label": "余韻の長さ（5 が長い）", "type": "score", "draft": "d_linger"},
         {"key": "first", "label": "最初に来る", "type": "choice", "choices": tastes, "draft": "d_first"},
         {"key": "last", "label": "最後に残る", "type": "choice", "choices": tastes, "draft": "d_last"},
         {"key": "memo", "label": "メモ", "type": "text"}], rows)
    ja = {r["ingredient"]: r["ja"] for r in read("taste_scores.csv")}
    am = [r for r in read("aroma_mapping.csv") if r["method"] == "manual"]
    rows = [{"key": r["ingredient"], "ja": e(ja.get(r["ingredient"], r["ingredient"])), "src": e(r["aroma_source_name"]), "note": e(r["note"])} for r in am]
    out["review-aroma-manual.html"] = page(
        "aroma-manual", f"香りの対応（手で付けた {len(am)} 件）",
        [f"Exp-10 で、303 食材を Ahn et al. 2011 の香り化合物の表の食材に対応づけたうち、名前が一致せず Claude が手で対応づけた {len(am)} 件です（data/labels/aroma_mapping.csv）。",
         "対応先が違うと思ったら「直す」を選び、正しい対応先（Ahn の表の名前、例 scallion）か、日本語で説明を書いてください。分からなければ「分からない」で構いません。"],
        [("src", "対応先（Ahn の表）"), ("note", "対応づけの理由")],
        [{"key": "verdict", "label": "判定", "type": "choice", "choices": ["よい", "直す", "分からない"]},
         {"key": "fix", "label": "正しい対応先・説明", "type": "text"},
         {"key": "memo", "label": "メモ", "type": "text"}], rows)
    for name, text in out.items():
        (WRITEUP / name).write_text(text, encoding="utf-8")
        print("wrote", WRITEUP / name)


if __name__ == "__main__":
    main()

"""Exp-21 のページ: 境目が動くアニメーション（writeup/boundary-t0.html）と 3D の状態図（writeup/state3d.html）。

    uv run python experiments/exp-21-boundaries/build_pages.py

- 入力は results/frames.json（compute.py）。境目の動きの集計は results/boundaries.md にも書く
- 本人方針: 構造が分かるもの（地図の境目のどれが動き、どれが動かないか）だけを描く。熱が伝わる様子のような体感で分かる現象は描かない
- 色は Arukashi のデザイン（main・sub と無彩色）だけ
"""
from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WRITEUP = ROOT / "writeup"
e = html.escape

# 判定ごとの塗り（Arukashi: main・sub と無彩色。濃さで分ける）
STYLE = {
    "__raw": ("var(--surface)", "生のまま（変化なし）"),
    "__none": ("var(--rule)", "該当なし"),
    "onsen_tamago": ("var(--sub)", "温泉卵"),
    "soft_boiled_egg": ("color-mix(in srgb, var(--main) 45%, var(--ground))", "半熟ゆで卵"),
    "hard_boiled_egg": ("var(--main)", "ゆで卵（固ゆで）"),
}
ORDER = ["__raw", "__none", "onsen_tamago", "soft_boiled_egg", "hard_boiled_egg"]

CSS = """:root{--ground:#FCFCFC;--surface:#F3F3F3;--rule:#E1E1E1;--ink:#171717;--ink-muted:#606060;--main:#B63552;--on-main:#FFFFFF;--sub:#00C9D4;
--heading:"Hanken Grotesk","Noto Sans JP",system-ui,sans-serif;--body:"IBM Plex Sans","IBM Plex Sans JP",system-ui,sans-serif;--numeric:"Roboto Mono",ui-monospace,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--ground:#101010;--surface:#1D1D1D;--rule:#2E2E2E;--ink:#EEEEEE;--ink-muted:#A4A4A4;--main:#FB8495;--on-main:#1A0E10;--sub:#00A8B3}}
:root[data-theme="dark"]{color-scheme:dark;--ground:#101010;--surface:#1D1D1D;--rule:#2E2E2E;--ink:#EEEEEE;--ink-muted:#A4A4A4;--main:#FB8495;--on-main:#1A0E10;--sub:#00A8B3}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.75;letter-spacing:.04em;padding:0 16px 64px}
main{max-width:960px;margin:0 auto;padding-top:40px}
h1{font-family:var(--heading);font-size:clamp(22px,4vw,30px);margin:8px 0;letter-spacing:.05em}
h2{font-family:var(--heading);font-size:19px;margin:64px 0 8px}
p{margin:0 0 16px;max-width:72ch}
.eyebrow{font-family:var(--numeric);font-size:11.5px;color:var(--main);letter-spacing:.08em;margin:0}
.muted{color:var(--ink-muted)}.small{font-size:13.5px}
.ctrl{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin:16px 0 8px}
button{font:inherit;font-size:13.5px;border:1px solid var(--main);background:var(--main);color:var(--on-main);border-radius:8px;padding:4px 16px;cursor:pointer}
input[type=range]{width:min(360px,70vw);accent-color:var(--main)}
.t0{font-family:var(--numeric);font-size:19px}
.legend{display:flex;gap:8px 16px;flex-wrap:wrap;font-size:13.5px;margin:8px 0}
.legend span{display:inline-flex;align-items:center;gap:8px}
.sw{width:12px;height:12px;border-radius:4px;border:1px solid var(--rule)}
svg{display:block;width:100%;height:auto}
.ax{font-family:var(--numeric);font-size:11.5px;fill:var(--ink-muted)}
.axl{font-family:var(--body);font-size:11.5px;fill:var(--ink)}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th{text-align:left;background:var(--surface);padding:8px}td{padding:8px;border-bottom:1px solid var(--rule)}
td.num{font-family:var(--numeric)}
.tablewrap{overflow-x:auto}
#view3d{width:100%;height:min(70vh,560px);border:1px solid var(--rule);border-radius:8px;touch-action:none}
label{white-space:nowrap}
"""
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@700&family=Noto+Sans+JP:wght@700'
         '&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Sans+JP:wght@400;600&family=Roboto+Mono:wght@500&display=swap">')


def transitions(cells, xs, ys):
    """温度の列ごとに、時間を伸ばしたとき判定が変わる点: {(前, 後): {列の温度: 変わった時間}}（最初の1回）。"""
    out = defaultdict(dict)
    for i, x in enumerate(xs):
        for j in range(1, len(ys)):
            a, b = cells[j - 1][i], cells[j][i]
            if a != b and x not in out[(a, b)]:
                out[(a, b)][x] = ys[j]
    return out


def summary(D):
    xs, ys = D["xs"], D["ys"]
    f0, f1 = D["frames"][0], D["frames"][-1]
    t0, t1 = transitions(f0["cells"], xs, ys), transitions(f1["cells"], xs, ys)
    rows = []
    for k in sorted(set(t0) | set(t1), key=lambda k: (ORDER.index(k[0]) if k[0] in ORDER else 9, ORDER.index(k[1]) if k[1] in ORDER else 9)):
        both = [x for x in xs if x in t0.get(k, {}) and x in t1.get(k, {})]
        sh = [t1[k][x] - t0[k][x] for x in both]
        rows.append({"from": k[0], "to": k[1], "n5": len(t0.get(k, {})), "n20": len(t1.get(k, {})), "n_both": len(both),
                     "moved": sum(1 for s in sh if s != 0), "mean_shift": (sum(sh) / len(sh)) if sh else None,
                     "min_shift": min(sh) if sh else None, "max_shift": max(sh) if sh else None})
    changed = sum(1 for j in range(len(ys)) for i in range(len(xs)) if f0["cells"][j][i] != f1["cells"][j][i])
    return rows, changed


def boundary_page(D, rows, changed) -> str:
    ja = D["ja"]
    legend = "".join(f'<span><i class="sw" style="background:{STYLE[k][0]}"></i>{e(STYLE[k][1])}</span>' for k in ORDER)
    trs = []
    for r in rows:
        if r["n_both"] == 0:
            move = "片方の温度にしか無い"
        elif r["moved"] == 0:
            move = "動かない"
        else:
            move = f'{r["moved"]}/{r["n_both"]} 列で動く（平均 {r["mean_shift"]:+.1f} 分、{r["min_shift"]:+g}〜{r["max_shift"]:+g} 分）'
        trs.append(f'<tr><td>{e(ja.get(r["from"], r["from"]))} → {e(ja.get(r["to"], r["to"]))}</td><td class="num">{r["n5"]}</td><td class="num">{r["n20"]}</td><td>{e(move)}</td></tr>')
    data = json.dumps({"xs": D["xs"], "ys": D["ys"], "frames": D["frames"], "fill": {k: v[0] for k, v in STYLE.items()}}, ensure_ascii=False)
    js = """
const D=DATA, W=640, H=420, L=48, R=12, T=12, B=40;
const nx=D.xs.length, ny=D.ys.length, cw=(W-L-R)/nx, ch=(H-T-B)/ny;
const svg=document.getElementById('map'); svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
const NS='http://www.w3.org/2000/svg';
function el(n,a){const x=document.createElementNS(NS,n);for(const k in a)x.setAttribute(k,a[k]);return x;}
const g=el('g',{}); svg.appendChild(g); const gb=el('g',{}); svg.appendChild(gb);
const rects=[];
for(let j=0;j<ny;j++){rects.push([]);for(let i=0;i<nx;i++){const r=el('rect',{x:L+i*cw,y:T+(ny-1-j)*ch,width:cw+0.4,height:ch+0.4});g.appendChild(r);rects[j].push(r);}}
for(let i=0;i<nx;i+=4){const t=el('text',{x:L+(i+0.5)*cw,y:H-B+16,class:'ax','text-anchor':'middle'});t.textContent=D.xs[i];svg.appendChild(t);}
for(let j=0;j<ny;j+=5){const t=el('text',{x:L-6,y:T+(ny-1-j+0.5)*ch+4,class:'ax','text-anchor':'end'});t.textContent=D.ys[j];svg.appendChild(t);}
const xl=el('text',{x:L+(W-L-R)/2,y:H-6,class:'axl','text-anchor':'middle'});xl.textContent='湯の温度（℃）';svg.appendChild(xl);
const yl=el('text',{x:12,y:T+(H-T-B)/2,class:'axl','text-anchor':'middle',transform:`rotate(-90 12 ${T+(H-T-B)/2})`});yl.textContent='湯に入れていた時間（分）';svg.appendChild(yl);
function edges(c){const s=new Set();for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){if(i+1<nx&&c[j][i]!==c[j][i+1])s.add(`v${i+1},${j}`);if(j+1<ny&&c[j][i]!==c[j+1][i])s.add(`h${i},${j+1}`);}return s;}
const base=edges(D.frames[0].cells);
function draw(k){
  const f=D.frames[k];
  for(let j=0;j<ny;j++)for(let i=0;i<nx;i++)rects[j][i].setAttribute('fill',D.fill[f.cells[j][i]]||'var(--rule)');
  gb.innerHTML='';const es=edges(f.cells);
  for(const e of es){const v=e[0]==='v';const [a,b]=e.slice(1).split(',').map(Number);
    const moved=!base.has(e);
    const ln=v?el('line',{x1:L+a*cw,x2:L+a*cw,y1:T+(ny-1-b)*ch,y2:T+(ny-b)*ch}):el('line',{x1:L+a*cw,x2:L+(a+1)*cw,y1:T+(ny-b)*ch,y2:T+(ny-b)*ch});
    ln.setAttribute('stroke',moved?'var(--main)':'var(--ink)');ln.setAttribute('stroke-width',moved?3:1.4);ln.setAttribute('stroke-linecap','square');gb.appendChild(ln);}
  document.getElementById('t0').textContent=f.T0+'℃';
  document.getElementById('nchg').textContent=f.cells.reduce((n,row,j)=>n+row.filter((c,i)=>c!==D.frames[0].cells[j][i]).length,0);
}
const sl=document.getElementById('sl'); sl.max=D.frames.length-1;
sl.addEventListener('input',()=>{stop();draw(+sl.value);});
let timer=null;
function stop(){if(timer){clearInterval(timer);timer=null;document.getElementById('play').textContent='再生';}}
document.getElementById('play').addEventListener('click',()=>{if(timer){stop();return;}document.getElementById('play').textContent='止める';
  timer=setInterval(()=>{sl.value=(+sl.value+1)%D.frames.length;draw(+sl.value);},900);});
draw(0);
"""
    return (f'<!doctype html>\n<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>境目が動く地図</title>{FONTS}<style>{CSS}</style></head><body><main>'
            '<p class="eyebrow">Cuisine Network · Exp-21</p><h1>卵の最初の温度を変えると、地図の境目のどれが動くか</h1>'
            '<p>殻付き卵を湯に入れ、湯の温度（横）と時間（縦）ごとに料理を判定した地図（ゆでた後は氷水に 15 分取る）です。卵の最初の温度を 5℃（冷蔵庫から出してすぐ）から 20℃（常温）まで変えます。'
            '<b>赤い太線は、5℃ のときには無かった境目</b>（動いた境目）、黒い線は 5℃ のときと同じ場所にある境目です。</p>'
            f'<div class="ctrl"><button id="play">再生</button><input type="range" id="sl" min="0" value="0" aria-label="卵の最初の温度"><span>卵の最初の温度 <span class="t0" id="t0"></span></span>'
            '<span class="small muted">5℃ と判定が違うマス <span id="nchg" class="num"></span></span></div>'
            f'<div class="legend">{legend}<span><i class="sw" style="background:none;border:2px solid var(--main)"></i>動いた境目</span></div>'
            '<svg id="map" role="img" aria-label="湯の温度と時間の地図"></svg>'
            '<h2>どの境目が動き、どれが動かないか（5℃ → 20℃）</h2>'
            f'<p class="small">温度の列ごとに、時間を伸ばしたとき判定が最初に変わる時間を比べました。全 {len(D["xs"]) * len(D["ys"])} マスのうち、5℃ と 20℃ で判定が違うのは {changed} マスです。地図の時間は 2 分刻みなので、境目の動きは 2 分単位でしか見えません（1 分未満の動きは「動かない」に入ります）。</p>'
            '<div class="tablewrap"><table><thead><tr><th>境目（時間を伸ばすと）</th><th>5℃ で現れる列</th><th>20℃ で現れる列</th><th>動き（20℃ − 5℃）</th></tr></thead><tbody>'
            + "".join(trs) + '</tbody></table></div>'
            '<p class="small muted">計算は Exp-14 のシミュレータ（殻付き卵は Exp-17 の熱伝導と変性の速さ）。判定・地図の範囲は変えていません。白身・黄身の段階の決め方は仮の値です（Exp-17）。'
            'このページは experiments/exp-21-boundaries/build_pages.py が生成します（Claude の記録）。</p>'
            f'</main><script>const DATA={data};{js}</script></body></html>\n')


def state3d_page(D) -> str:
    data = json.dumps({"xs": D["xs"], "ys": D["ys"], "frames": D["frames"]}, ensure_ascii=False)
    legend = "".join(f'<label><input type="checkbox" data-c="{k}" {"checked" if k not in ("__raw", "__none") else ""}> '
                     f'<i class="sw" style="display:inline-block;background:{STYLE[k][0]}"></i> {e(STYLE[k][1])}</label>' for k in ORDER)
    js = """
const D=DATA;
const css=getComputedStyle(document.documentElement);
const col=n=>new THREE.Color(css.getPropertyValue(n).trim()||'#888');
function mix(a,b,t){return a.clone().lerp(b,t);}
const COL={__raw:col('--surface'),__none:col('--rule'),onsen_tamago:col('--sub'),soft_boiled_egg:mix(col('--ground'),col('--main'),0.45),hard_boiled_egg:col('--main')};
const box=document.getElementById('view3d');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(window.devicePixelRatio||1);box.appendChild(renderer.domElement);
const scene=new THREE.Scene();
const cam=new THREE.PerspectiveCamera(40,1,0.1,100);cam.position.set(2.2,1.6,2.6);
const ctl=new THREE.OrbitControls(cam,renderer.domElement);ctl.target.set(0,0,0);ctl.update();
scene.add(new THREE.AmbientLight(0xffffff,0.75));const dl=new THREE.DirectionalLight(0xffffff,0.5);dl.position.set(2,3,1);scene.add(dl);
const nx=D.xs.length,ny=D.ys.length,nz=D.frames.length;
const sx=2/nx,sy=1.4/ny,sz=1.2/nz;
const geo=new THREE.BoxGeometry(sx*0.92,sy*0.92,sz*0.6);
const groups={};
for(const k in COL){const mat=new THREE.MeshLambertMaterial({color:COL[k],transparent:k==='__none'||k==='__raw',opacity:(k==='__none'||k==='__raw')?0.25:0.95});
  const cells=[];D.frames.forEach((f,z)=>f.cells.forEach((row,j)=>row.forEach((c,i)=>{if(c===k)cells.push([i,j,z]);})));
  const m=new THREE.InstancedMesh(geo,mat,Math.max(1,cells.length));const o=new THREE.Object3D();
  cells.forEach(([i,j,z],n)=>{o.position.set(-1+(i+0.5)*sx,-0.7+(j+0.5)*sy,-0.6+(z+0.5)*sz);o.updateMatrix();m.setMatrixAt(n,o.matrix);});
  m.count=cells.length;scene.add(m);groups[k]=m;}
const frame=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(2,1.4,1.2)),new THREE.LineBasicMaterial({color:col('--ink-muted')}));scene.add(frame);
document.querySelectorAll('input[data-c]').forEach(cb=>{const f=()=>{groups[cb.dataset.c].visible=cb.checked;};cb.addEventListener('change',f);f();});
function size(){const w=box.clientWidth,h=box.clientHeight;renderer.setSize(w,h);cam.aspect=w/h;cam.updateProjectionMatrix();}
window.addEventListener('resize',size);size();
(function loop(){requestAnimationFrame(loop);renderer.render(scene,cam);})();
"""
    t0s = "・".join(f'{f["T0"]:g}' for f in D["frames"])
    return (f'<!doctype html>\n<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>卵の状態図（立体）</title>{FONTS}<style>{CSS}</style>'
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
            '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>'
            '</head><body><main>'
            '<p class="eyebrow">Cuisine Network · Exp-21</p><h1>湯の温度 × 時間 × 卵の最初の温度で見る、卵の状態図</h1>'
            f'<p>殻付き卵の地図（湯の温度 × 時間、氷水に取る）を、卵の最初の温度（{t0s}℃）ごとに重ねて立体にしました。'
            '横が湯の温度（50〜100℃）、縦が時間（1〜59 分）、奥行きが卵の最初の温度（手前が 5℃、奥が 20℃）です。ドラッグで回し、ホイール（2 本指）で寄れます。</p>'
            f'<div class="legend">{legend}</div><div id="view3d" aria-label="立体の状態図"></div>'
            '<p class="small muted">領域が奥（常温）へ向かって少し短い時間の側へ傾くのが、卵の最初の温度の効果です。境目が傾かない面は、最初の温度に左右されない境目です（平面の地図での比べ方は「境目が動く地図」のページ）。'
            '計算は Exp-14 のシミュレータ（殻付き卵は Exp-17）。このページは experiments/exp-21-boundaries/build_pages.py が生成します（Claude の記録）。</p>'
            f'</main><script>const DATA={data};{js}</script></body></html>\n')


def main() -> None:
    D = json.loads((HERE / "results" / "frames.json").read_text(encoding="utf-8"))
    rows, changed = summary(D)
    ja = D["ja"]
    L = ["# Exp-21 境目の動き（build_pages.py が生成）", "", f"5℃ と 20℃ で判定が違うマス: {changed} / {len(D['xs']) * len(D['ys'])}", "",
         "| 境目（時間を伸ばすと） | 5℃ で現れる列 | 20℃ で現れる列 | 両方にある列 | 動いた列 | 平均の動き（分） | 範囲（分） |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f'| {ja.get(r["from"], r["from"])} → {ja.get(r["to"], r["to"])} | {r["n5"]} | {r["n20"]} | {r["n_both"]} | {r["moved"]} | '
                 + ("—" if r["mean_shift"] is None else f'{r["mean_shift"]:+.2f}') + " | "
                 + ("—" if r["min_shift"] is None else f'{r["min_shift"]:+g}〜{r["max_shift"]:+g}') + " |")
    (HERE / "results" / "boundaries.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (WRITEUP / "boundary-t0.html").write_text(boundary_page(D, rows, changed), encoding="utf-8")
    (WRITEUP / "state3d.html").write_text(state3d_page(D), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()

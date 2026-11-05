"""通説1「ポーチドエッグは、湯に酢を入れるとまとまる」（writeup/myth-poached-vinegar.html）。

    uv run python experiments/myths/build.py poached_vinegar

もとは Exp-16（experiments/exp-16-myth-poached-vinegar/build.py）。2026-09-28 に通説ページの型（common.py）に載せ替えた。
出力は載せ替え前と同じ（experiments/myths/test_myths.py で確かめる）。

- 計算は Exp-14 のシミュレータのまま（rules.yaml・判定・地図の範囲を変えない）。地図は sim/maps.py の PRESETS「poach」
  （割った卵を湯に落とす × 湯の温度 × 時間）を、酢なし（元のレシピのまま）と酢 1.5%（exp-15 で割合が出せた唯一の値、
  大さじ1/水1 L）の2通りで描く。
- レシピでの扱いは Exp-15 の recipes.csv から数える。出典・規則の文面は rules.yaml から引く（書き写さない）。
- 規則は足していない（数値の出典が無いものを足すと合わせ込みになるため。ページの「根拠」に書いた）。
"""
from __future__ import annotations

import json
import re
from collections import Counter

from . import common as C
from .common import NO_MATCH_BELOW, P, maps

ID = "poached_vinegar"
OUT = C.WRITEUP / "myth-poached-vinegar.html"

VINEGAR_PCT = 1.5
EXP19 = C.ROOT / "experiments" / "exp-19-poach-dilution" / "results" / "output.json"
PRESET = next(p for p in maps.PRESETS if p["id"] == "poach")
e = C.e


# ---------------- 計算 ----------------

def base(vinegar: float) -> dict:
    b = maps.base_recipe(PRESET["base"])
    if vinegar:
        b["steps"][0][1]["vinegar_pct"] = vinegar
    return b


def at(b: dict, T: float, t: float) -> dict:
    return maps.with_value(maps.with_value(b, PRESET["x"]["axis"], T), PRESET["y"]["axis"], t)


def compute() -> dict:
    out = {}
    for key, v in (("plain", 0.0), ("vinegar", VINEGAR_PCT)):
        b = base(v)
        g = maps.grid(b, PRESET["x"], PRESET["y"], NO_MATCH_BELOW)
        # 湯温ごとの卵白のまとまり・卵白の段階（表面）。時間によらない（湯に入れた最初の刻みで決まる）ことも確かめる
        coh, white = [], []
        for T in g["xs"]:
            cs = {maps.run_json(at(b, T, t))[1].egg_white_cohesion for t in g["ys"]}
            ws = {maps.run_json(at(b, T, t))[1].get("egg_white_stage") for t in g["ys"]}
            assert len(cs) == 1 and len(ws) == 1, (T, cs, ws)
            coh.append(cs.pop())
            white.append(ws.pop())
        out[key] = {"grid": g, "coh": coh, "white": white}
    g0, g1 = out["plain"]["grid"], out["vinegar"]["grid"]
    diff_cls, diff_frac, diff_state = 0, [], Counter()
    for j, (r0, r1) in enumerate(zip(g0["cells"], g1["cells"])):
        for i, (a, b) in enumerate(zip(r0, r1)):
            diff_cls += a["cls"] != b["cls"]
            if a["top"] != b["top"]:
                diff_frac.append((g0["xs"][i], g0["ys"][j], a["top"], b["top"]))
    # 状態変数のうち酢で変わるもの（全マス）
    keys = ["egg_white_stage", "egg_yolk_stage", "egg_gel_stage", "T_core_max", "T_surface_max", "egg_white_cohesion", "water", "salt_conc"]
    for T in g0["xs"]:
        for t in g0["ys"]:
            s0 = maps.run_json(at(base(0), T, t))[1]
            s1 = maps.run_json(at(base(VINEGAR_PCT), T, t))[1]
            for k in keys:
                if s0.get(k) != s1.get(k):
                    diff_state[k] += 1
    count = {k: Counter(c["cls"] for r in out[k]["grid"]["cells"] for c in r) for k in out}
    out["diff"] = {"cls": diff_cls, "frac": diff_frac, "state": dict(diff_state), "n": len(g0["xs"]) * len(g0["ys"])}
    out["count"] = count
    return out


# ---------------- レシピ（Exp-15） ----------------

def recipes() -> dict:
    rows = C.recipe_rows("poached_egg")
    by = Counter(r["vinegar"] for r in rows)
    groups = {}
    for r in rows:
        groups.setdefault(r["independence_group"], set()).add(r["vinegar"])
    pages = Counter("yes" if "yes" in v else "optional" if "optional" in v else "no" for v in groups.values())
    pct = [r for r in rows if r["vinegar_pct_est"]]
    return {"rows": rows, "by": by, "pages": pages, "n_pages": len(groups), "pct": pct}


# ---------------- 規則・出典（rules.yaml から） ----------------

RULE_IDS = ["R-E14", "R-E21", "R-E22", "R-E23"]
SOURCE_IDS = ["mcgee", "soc_poach", "travelingfoodlab", "kyounoryouri", "terumimorita", "wang2025", "wiki_poached"]
# 各出典をどう確かめたか（rules.md §0 の区分。規則の check 列と rules.md §9 から）
SOURCE_CHECK = {
    "mcgee": ("本文を開いていない", "soc_poach（英語）と travelingfoodlab（日本語訳 p88）の引用2つで、同じ内容を確認"),
    "soc_poach": ("本文確認", "McGee の引用と、80℃・4分の手順"),
    "travelingfoodlab": ("本文確認", "料理人の記事。沸騰させない・85℃目安・酢は入れない（McGee を引用）"),
    "kyounoryouri": ("本文確認", "レシピ。沸騰した湯に酢を入れる"),
    "terumimorita": ("本文確認", "料理人の記事。本文 80–85℃、要約行 63–65℃で食い違う"),
    "wang2025": ("抄録確認", "論文の抄録。精製したオボアルブミンの溶液での測定。本文は未読"),
    "wiki_poached": ("本文確認", "湯温 62℃ の記述（C13）"),
}


# ---------------- 対照: 酢の代わりに水を足したら（Exp-19） ----------------

def dilution() -> dict:
    """Exp-19 の結果（run.py が書いた output.json）。"""
    return json.loads(EXP19.read_text(encoding="utf-8"))


def _g(v, d=1):
    return "—" if v is None else f"{v:.{d}f}"


def dilution_html() -> tuple[str, dict]:
    """(節の HTML, 要約の数値)。記事風は表1つと所見。方法と全数値は <!--paper:method--> と <!--paper:data--> で囲む
    （公開サイトの論文風で方法の節と付録に回す。研究ノート側ではそのまま見える）。"""
    D = dilution()
    R = D["runs"]
    Ps = D["powers_kW"]
    cond = {c["key"]: c for c in D["conditions"]}
    k85 = next(c["key"] for c in D["conditions"] if c["id"] == "4" and abs(R[c["key"]]["P1.5"]["T_mix"] - 85) < 0.5)

    def boil(k):
        vs = [R[k][f"P{P:g}"]["t_boil_s"] for P in Ps]
        return f"{min(vs):.0f}〜{max(vs):.0f} 秒" if max(vs) > 0 else "止まらない"

    def one(k):
        return R[k]["P1.5"]

    rows = [("① 何も足さない", ["none"], "—", "沸騰したまま（R-E21: 対流で卵白がちぎれる）"),
            ("② 酢 3%・4.5%", ["vinegar3", "vinegar4.5"], "凝固を速める向き（R-E22）。何秒・何℃かの数値は無い", "足した直後だけ泡が止まる"),
            ("③ 同じ量の水", ["water3", "water4.5"], "なし", "② と同じ（熱の面では区別できない）"),
            ("④ 差し水 100 mL", ["more100"], "なし", "泡が止まる時間が ② ③ の約3倍"),
            ("④ 差し水 200 mL", ["more200"], "なし", "火力 1.5 kW で、泡が止まる時間と外側 1 mm が固まる時間がほぼ同じ"),
            (f"④ 差し水 {cond[k85]['ml']:g} mL（85℃）", [k85], "なし", "出典の勧める 80〜85℃ に入る（R-E21）")]
    trs = []
    for lab, ks, acid, move in rows:
        ml = "・".join(f"{cond[k]['ml']:g}" for k in ks)
        T = " / ".join(f"{one(k)['T_mix']:.1f}" for k in ks)
        b = " / ".join(boil(k) for k in ks)
        mm = " / ".join(_g(one(k)["t_1mm_s"], 0) for k in ks)
        trs.append(f'<tr><td class="nw">{e(lab)}</td><td class="num">{ml} mL</td><td class="num">{T}℃</td><td class="num">{b}</td>'
                   f'<td class="num">{mm} 秒</td><td class="small">{e(acid)}</td><td class="small">{e(move)}</td></tr>')
    s = {k: one(k) for k in R}
    same = max(abs(R[k]["vinegar_props_P1.5"]["T_mix"] - R[k]["P1.5"]["T_mix"]) for k in ("vinegar3", "vinegar4.5"))
    rate = {r["T"]: r["t90_s"] for r in D["rate"]}
    b23 = [R[k][f"P{P:g}"]["t_boil_s"] for k in ("vinegar3", "vinegar4.5") for P in Ps]
    mm23 = [s[k]["t_1mm_s"] for k in ("vinegar3", "vinegar4.5", "water3", "water4.5")]
    b200 = {P: R["more200"][f"P{P:g}"]["t_boil_s"] for P in Ps}
    summ = {"T3": s["vinegar3"]["T_mix"], "T45": s["vinegar4.5"]["T_mix"], "b23": (min(b23), max(b23)), "mm23": (min(mm23), max(mm23)),
            "T200": s["more200"]["T_mix"], "ml85": cond[k85]["ml"], "b200": b200, "mm200": s["more200"]["t_1mm_s"], "same": same,
            "mm1": s["none"]["t_1mm_s"], "Ps": Ps}
    H = []
    H.append('<h3 id="dilution">対照: 酢の代わりに水を足したら（Exp-19）</h3>')
    H.append('<p>酢は「酸」として効くのか、それとも「冷たい液を足すこと（差し湯・差し水）」として効くのか。1 L の沸騰した湯に 20℃ の液を足して、すぐに卵（60 g、20℃）を落とす4通りを計算で比べました。'
             '湯温は熱収支、沸騰が止まる時間は再沸騰までの時間（火力は仮定の 1.0〜2.0 kW）、白身の固まり方は卵の熱伝導と変性の速さの計算（Exp-17）で、足した後の湯温の変化をそのまま使っています。</p>')
    H.append('<p class="tcap">酢・同じ量の水・多めの差し水を足したときの湯温と白身（Exp-19）</p>')
    H.append('<div class="tablewrap"><table class="cmp"><thead><tr><th>条件</th><th>足す量</th><th>足した直後の湯温</th><th>沸騰が止まる時間（火力 2.0〜1.0 kW、仮定）</th>'
             '<th>白身の外側 1 mm が固まるまで（1.5 kW）</th><th>酸の効き目（出典）</th><th>湯の動き（出典からの推定、計算外）</th></tr></thead><tbody>'
             + "".join(trs) + '</tbody></table></div>')
    H.append('<ul class="find">')
    H.append(f'<li><b>酢の量なら、酢も同じ量の水も同じだけ湯を冷ます。</b>湯量の 3%・4.5% で {summ["T3"]:.1f}℃・{summ["T45"]:.1f}℃。酢の比熱・密度を水と分けて計算しても差は {same:.2f}℃ で、沸騰が止まる時間・白身の固まり方は同じでした。'
             '計算の上で ② と ③ を分けるのは酸の効き目だけで、それは数値の出典が無いので計算に入っていません。</li>')
    H.append(f'<li><b>酢の量では、白身が固まる前に沸騰が戻る。</b>② ③ で沸騰が止まるのは {summ["b23"][0]:.0f}〜{summ["b23"][1]:.0f} 秒（100℃ 未満での蒸発・放熱を無視した短めの見積もり）。'
             f'白身は湯にふれた表面なら 85℃ 以上で数秒以内に固まります（一定の湯温で 100℃ {rate[100]:.2f} 秒・90℃ {rate[90]:.1f} 秒・85℃ {rate[85]:.0f} 秒）が、外側 1 mm まで固まるのは {summ["mm23"][0]:.0f}〜{summ["mm23"][1]:.0f} 秒で、内側へ熱が伝わる速さで決まります。'
             '計画で決めた約束（沸騰が止まる時間が 1 mm の固まる時間より長ければ「足すこと」を支持）では、酢の量の「足すこと」の効き目は支持しません。</li>')
    H.append(f'<li><b>多めの差し水は、火力しだいで境目。</b>200 mL で {summ["T200"]:.1f}℃、{summ["ml85"]:g} mL で 85℃。200 mL で沸騰が止まるのは '
             + "・".join(f"{P:g} kW {b200[P]:.0f} 秒" for P in Ps) + f'、外側 1 mm が固まるのは {summ["mm200"]:.0f} 秒です。湯温が下がる分、白身の固まり方は少し遅くなります（① {summ["mm1"]:.0f} 秒）。</li>')
    H.append('<li><b>湯の動きは、この計算では区別できない。</b>「沸騰した湯は対流で卵白をちぎる」（R-E21、確かさ 低）を当てはめると、足した液で泡が止まる間だけ湯は静かになる、という推定までです。'
             '計算の地図の「まとまり」は、落とした瞬間の湯温だけで決めているので、足した後に沸騰が戻ることを表していません。</li>')
    H.append('</ul>')
    # ---- 方法（論文風では方法の節へ）----
    A_ = D["assume"]
    def _src(v):
        v = re.sub(r"（[^（）]*）$", "", v)
        m = re.search(r"\s(https?://\S+)$", v)
        return (e(v[:m.start()]) + f' <a href="{e(m.group(1))}" target="_blank" rel="noopener">リンク</a>') if m else e(v)
    src = {k: _src(v) for k, v in D["sources"].items()}
    H.append('<!--paper:method--><div class="cmp-method"><h3>対照の比較（Exp-19）の方法</h3>'
             f'<p>1 L の沸騰した湯（100℃、密度 958.35 kg/m³ から 958 g）に 20℃ の液（密度 998.21 kg/m³）を足し、一様に混ざるとして熱収支から湯温を出した。'
             f'比熱は水 100℃ 4.2157・20℃ 4.1844 kJ/(kg·K)（{src["etb_water_cp"]}、{src["etb_water_rho"]}）。<b>酢は水と同じとみなした（近似）</b>。'
             f'差の見積もりとして、酢酸 {A_["acid_mass_frac"] * 100:.1f}%（質量）を重み付けした c = {A_["cp_vinegar"]:.2f} kJ/(kg·K)（酢酸の液体 123.1 J/(mol·K)、{src["nist_acetic"]}）と密度 {A_["rho_vinegar"] / 1000:.2f}（仮定）でも計算した。</p>'
             '<p class="eq">T = (m<sub>w</sub>c<sub>w</sub>·100 + m<sub>a</sub>c<sub>a</sub>·20 + C<sub>pot</sub>·100) / (m<sub>w</sub>c<sub>w</sub> + m<sub>a</sub>c<sub>a</sub> + C<sub>pot</sub>)</p>'
             f'<p>足した後は、コンロから湯に入る正味の熱量 P（<b>仮定</b>: {"・".join(f"{P:g}" for P in Ps)} kW、出典なし）と、卵が湯から奪う熱で湯温を {D["dt_s"]:g} 秒刻みで進め、100℃ に戻った時刻を「沸騰が止まる時間」とした。'
             '100℃ 未満での蒸発・放熱は無視したので、この時間は短めの見積もり（下限）。鍋の熱容量は主の計算では入れず、感度として 500 J/K（仮定）を入れた。</p>'
             f'<p>白身の固まり方は Exp-17 の計算（cuisine-network experiments/exp-14/sim/egg_kinetic.py）: 卵を黄身（中心の球）と白身（外側の層）の2層の球とし、熱伝導を半径方向 {D["nodes"]} 節点の差分で解き、場所ごとの変性度 X を一次反応 dX/dt = A·exp(−E<sub>a</sub>/RT)(1 − X) で積分した（値は Di Lorenzo et al. 2025 Table 4）。'
             '表面の温度は上の湯温の履歴に等しいとした。割った卵を同じ質量（60 g）の球とみなしたので、実際に平たく広がる卵より固まり方を遅めに出す。X ≥ 0.9 を「固まった」とし、表面から続けて固まった厚さ・外側 1 mm が固まるまでの時間・白身の体積の半分が固まるまでの時間を出した。'
             f'感度として、表面を熱伝達率 h = {A_["h_sens"]:g} W/(m²·K) のロバン条件にした。</p>'
             '<p>酸による凝固の促進は入れていない（R-E22 は向きだけ、R-E23 は pH ごとの変性温度の数値が抄録に無い、R-E14 は未確認）。湯の動き（対流）も入れていない。計画は experiments/exp-19-poach-dilution/plan.md（計算の前にコミット）。</p></div><!--/paper:method-->')
    # ---- 全数値（論文風だけ）----
    def row_all(k):
        r = R[k]
        m = r["P1.5"]
        d = m["depth_mm"]
        v = r.get("vinegar_props_P1.5")
        return (f'<tr><td class="nw">{e(cond[k]["label"])}</td><td class="num">{cond[k]["ml"]:g}</td><td class="num">{m["T_mix"]:.2f}</td>'
                + "".join(f'<td class="num">{r[f"P{P:g}"]["t_boil_s"]:.0f}</td>' for P in Ps)
                + "".join(f'<td class="num">{d[str(t)]:.1f}</td>' for t in (5, 10, 30, 60))
                + f'<td class="num">{_g(m["t_1mm_s"])}</td><td class="num">{_g(m["t_white50_s"], 0)}</td><td class="num">{m["yolk_mean_X_end"]:.2f}</td>'
                + f'<td class="num">{r["pot_P1.5"]["T_mix"]:.2f}</td><td class="num">{_g(r["h800_P1.5"]["t_1mm_s"])}</td><td class="num">{r["noegg_P1.5"]["t_boil_s"]:.0f}</td>'
                + (f'<td class="num">{v["T_mix"]:.2f}</td>' if v else '<td>—</td>') + '</tr>')
    H.append('<!--paper:data--><div class="cmp-data"><p class="tcap">対照の比較の全数値（Exp-19。火力 1.5 kW・鍋なし・表面＝湯温を主とする）</p>'
             '<div class="tablewrap"><table class="raw"><thead><tr><th>条件</th><th>量 mL</th><th>直後の湯温 ℃</th>'
             + "".join(f"<th>沸騰が止まる 秒（{P:g} kW）</th>" for P in Ps)
             + '<th>固まった厚さ mm 5 秒</th><th>10 秒</th><th>30 秒</th><th>60 秒</th><th>外側 1 mm 秒</th><th>白身の半分 秒</th><th>4 分後の黄身の平均 X</th>'
             '<th>鍋 500 J/K の直後 ℃</th><th>h=800 の外側 1 mm 秒</th><th>卵なしの沸騰が止まる 秒</th><th>酢の物性の直後 ℃</th></tr></thead><tbody>'
             + "".join(row_all(c["key"]) for c in D["conditions"]) + '</tbody></table></div>'
             '<p class="small muted">白身の9割が固まるのは、どの条件でも 240 秒で届かなかった（球とみなしたため）。一定の湯温で白身の表面が X = 0.9 に達するまで: '
             + "・".join(f'{r["T"]}℃ {r["t90_s"]:.3g} 秒' for r in D["rate"]) + '。格子 120・240・480 節点で外側 1 mm の時間の差は 4 秒以内。</p></div><!--/paper:data-->')
    return "".join(H), summ


# ---------------- 図（SVG） ----------------

COH_CLASS = {"ばらける": "c-sc", "まとまる（表面に膜・ちぎれ）": "c-fi", "まとまる": "c-co"}
COH_SHORT = {"ばらける": "ばらける", "まとまる（表面に膜・ちぎれ）": "膜・ちぎれ", "まとまる": "まとまる"}
CLS_JA = {"poached_egg": "ポーチドエッグ", maps.NONE: "該当なし", maps.RAW: "生のまま（変化なし）"}
VIN_MARK = {"yes": "必ず入れる", "optional": "任意", "no": "手順に無い"}


def svg_map(d: dict, other: dict, title: str, rows: list[dict], vinegar: bool) -> str:
    g = d["grid"]
    xs, ys = g["xs"], g["ys"]
    nx, ny = len(xs), len(ys)
    L, T, cw, ch = 40, 8, 17, 9
    W = L + nx * cw + 6
    top_h = T + ny * ch
    strip_y1 = top_h + 22
    strip_y2 = strip_y1 + 16
    H = strip_y2 + 16 + 22
    cx = lambda i: L + i * cw  # noqa: E731
    cy = lambda j: T + (ny - 1 - j) * ch  # noqa: E731
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{e(title)}の地図">',
             '<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<rect width="5" height="5" class="f-raw"/><line x1="0" y1="0" x2="0" y2="5" class="hatch-l"/></pattern></defs>']
    for j, row in enumerate(g["cells"]):
        for i, c in enumerate(row):
            o = other["grid"]["cells"][j][i]
            a = 1.0 if c["cls"].startswith("__") else 0.3 + 0.7 * min(1, c["margin"] / 0.4)
            cls = {"poached_egg": "f-po", maps.NONE: "f-no", maps.RAW: ""}[c["cls"]]
            fill = ' fill="url(#hatch)"' if c["cls"] == maps.RAW else ""
            top = f"{c['top'][1]}/{c['top'][2]}" if c["top"] else "—"
            tip = f"{xs[i]:g}℃・{ys[j]:g}分: {CLS_JA[c['cls']]}（{top}）・卵白のまとまり {d['coh'][i] or '—'}"
            ring = ' class="dif"' if c["top"] != o["top"] else ""
            parts.append(f'<rect x="{cx(i)}" y="{cy(j)}" width="{cw + .3}" height="{ch + .3}" class="{cls}"{fill} fill-opacity="{a:.3f}"><title>{e(tip)}</title></rect>')
            if ring:
                parts.append(f'<rect x="{cx(i) + 1}" y="{cy(j) + 1}" width="{cw - 2}" height="{ch - 2}"{ring}/>')
    parts.append(f'<rect x="{L}" y="{T}" width="{nx * cw}" height="{ny * ch}" class="frame"/>')
    # 軸
    for i, x in enumerate(xs):
        if x % 10 == 0:
            parts.append(f'<text class="ax" x="{cx(i) + cw / 2}" y="{top_h + 12}" text-anchor="middle">{x:g}</text>')
    for j, y in enumerate(ys):
        if y % 2 == 0:
            parts.append(f'<text class="ax" x="{L - 4}" y="{cy(j) + ch / 2 + 3.5}" text-anchor="end">{y:g}</text>')
    parts.append(f'<text class="axl" transform="translate(10 {T + ny * ch / 2}) rotate(-90)" text-anchor="middle">湯に入れてからの時間（分）</text>')
    # 帯: 卵白のまとまり・卵白の段階（どちらも湯温だけで決まる）
    parts.append(f'<text class="axs" x="{L - 4}" y="{strip_y1 + 11}" text-anchor="end">まとまり</text>')
    parts.append(f'<text class="axs" x="{L - 4}" y="{strip_y2 + 11}" text-anchor="end">卵白</text>')
    for i, x in enumerate(xs):
        c = d["coh"][i]
        k = COH_CLASS.get(c, "c-na")
        oc = other["coh"][i]
        parts.append(f'<rect x="{cx(i)}" y="{strip_y1}" width="{cw + .3}" height="14" class="{k}"><title>{e(f"{x:g}℃: 卵白のまとまり {c}")}</title></rect>')
        if c != oc:
            parts.append(f'<rect x="{cx(i) + 1}" y="{strip_y1 + 1}" width="{cw - 2}" height="12" class="dif2"/>')
        w = d["white"][i]
        parts.append(f'<rect x="{cx(i)}" y="{strip_y2}" width="{cw + .3}" height="14" class="w{w or 0}"><title>{e(f"{x:g}℃: 卵白の段階 {w}（表面の温度で決まる）")}</title></rect>'
                     f'<text class="wn" x="{cx(i) + cw / 2}" y="{strip_y2 + 10.5}" text-anchor="middle">{w or 0}</text>')
    parts.append(f'<text class="axl" x="{L + nx * cw / 2}" y="{H - 4}" text-anchor="middle">湯の温度（℃）</text>')
    # レシピの点（Exp-15）。酢の扱いで塗りを変える
    for r in rows:
        if not r["map_ok"].startswith("yes"):
            continue
        T0, t0 = float(r["map_T_c"]), float(r["map_time_min"])
        px = L + ((T0 - xs[0]) / PRESET["x"]["step"] + 0.5) * cw
        py = T + (ny - 1 - (t0 - ys[0]) / PRESET["y"]["step"]) * ch + ch / 2
        v = r["vinegar"]
        tip = f"{r['row_id']} {r['page_title'].replace('Cookbook:', '')}: {T0:g}℃{'（推定）' if r['T_is_estimate'] == 'yes' else '（原文）'}・{t0:g}分・酢 {VIN_MARK[v]}"
        parts.append(f'<g class="pt pt-{v}"><title>{e(tip)}</title><circle cx="{px:.1f}" cy="{py:.1f}" r="5.2" class="o"/>'
                     f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.2" class="i"/>'
                     + (f'<path d="M{px:.1f} {py - 5.2:.1f}a5.2 5.2 0 0 1 0 10.4Z" class="h"/>' if v == "optional" else "") + "</g>")
    parts.append("</svg>")
    return "".join(parts)


# ---------------- ページ ----------------

DISH_COLORS = [("poached_egg", "f-po", "#1baf7a", "#199e70"), ("__none", "f-no", "#b3b8b4", "#4d5651"), ("__raw", "f-raw", "#DCE0DC", "#252D29")]
conf = C.conf

USE = {
    "R-E14": "使っていない（未確認のまま。R-E22 で内容を確かめた形）",
    "R-E21": None,  # page() で採用値から組む
    "R-E22": "酢か塩があれば「まとまる（表面に膜・ちぎれ）」。量の効果・速さは入れていない（数値なし）",
    "R-E23": "使っていない（pH ごとの変性温度の数値が抄録に無いので、段階のしきい値を動かしていない）",
}


def page() -> str:
    Cm = compute()
    Rc = recipes()
    rows = Rc["rows"]
    by, pages = Rc["by"], Rc["pages"]
    n = len(rows)
    diff = Cm["diff"]
    n_po = Cm["count"]["plain"]["poached_egg"]
    n_po_v = Cm["count"]["vinegar"]["poached_egg"]
    coh_T_min = P.V("poach_cohesion_T_min")
    xs = Cm["plain"]["grid"]["xs"]
    frac_T = sorted({x for x, *_ in diff["frac"]})
    frac_ex = diff["frac"][0] if diff["frac"] else None
    white_by_T = {x: w for x, w in zip(xs, Cm["plain"]["white"])}
    # 卵白の段階が 3 になる最低の湯温
    t3 = min((x for x, w in white_by_T.items() if (w or 0) >= 3), default=None)

    H = C.head("酢とポーチドエッグ", C.css(DISH_COLORS))
    A = H.append
    A('<div class="wrap">')
    A(C.header(1, 'ポーチドエッグは、湯に酢を入れるとまとまる？',
               'よく言われる料理の通説を、食品科学の規則で作ったシミュレータ（Exp-14）で計算しました。'
               '判定と確かさ・決め手の図・言えないこと・自分で試す手順を先に置き、通説の説明・計算の詳しい答え・根拠を後ろに並べます。根拠の詳しい中身は、規則ごと・出典ごとのページに分けました。'))

    # 1. 通説
    A(C.h2("claim", 1, "通説", '<div class="card">'))
    A('<p class="claim">「ポーチドエッグを作るときは、湯に酢を入れると白身が散らずにまとまる」</p>')
    A(f'<p class="muted small">世の中のレシピでの扱い（Exp-15: Wikibooks 料理本などの機械的な収集が許された出典から読み取ったポーチドエッグ {n} 件の手順）。'
      '「手順に無い」は、入れないと書かれているのではなく、酢について何も書かれていないという意味です。</p>')
    A(C.stats([(by["yes"], "必ず入れる"), (by["optional"], "任意（入れてもよい）"), (by["no"], "手順に無い"),
               (len(Rc["pct"]), "量が割合で出せた（どれも 大さじ1/水1 L＝1.5%）")]))
    A(f'<p class="small">同じページの別の手順を1つに束ねると {Rc["n_pages"]} ページで、必ず {pages["yes"]}・任意 {pages["optional"]}・手順に無い {pages["no"]}。'
      '出典は英語圏の家庭料理（Wikibooks）に偏っていて、件数は少なく、多数決の根拠にはなりません。</p>')
    A('<p class="small">料理の専門家の記事でも分かれています（Exp-14 の衝突 C14）: 入れる＝NHK「きょうの料理」（脇雅世）・Terumi Morita、'
      '入れない＝樋口直哉（TravelingFoodLab.、McGee を引用して「表面に不規則な膜ができる」）。</p>')
    A('</div></section>')

    # 2. 計算の答え
    A(C.h2("calc", 2, "計算の詳しい答え"))
    A(f'<p>割った卵（60 g）を湯に落とし、湯の温度（横）と時間（縦）を変えて、マスごとに料理を判定しました。左は酢なし、右は湯に酢 {VINEGAR_PCT:g}%（大さじ1/水1 L）。'
      '色はポーチドエッグ（濃いほど迷いが少ない）、灰色は該当なし、斜線は生のまま。下の2本の帯は、湯の温度ごとの <b>卵白のまとまり</b> と <b>卵白の段階</b>（0 生〜3 しっかり固まる）です。'
      '左右で違うところを黄色の枠で囲みました。点は Exp-15 のレシピ（黒＝酢を必ず入れる、半分＝任意、白＝手順に無い）。マスや点にカーソルを当てると値が出ます。</p>')
    A('<div class="maps">')
    A(f'<figure><figcaption>酢なし</figcaption>{svg_map(Cm["plain"], Cm["vinegar"], "酢なし", rows, False)}</figure>')
    A(f'<figure><figcaption>湯に酢 {VINEGAR_PCT:g}%</figcaption>{svg_map(Cm["vinegar"], Cm["plain"], "酢あり", rows, True)}</figure>')
    A('</div>')
    A('<div class="legend">'
      '<span class="it"><span class="sw" style="background:var(--d-poached_egg)"></span>ポーチドエッグ</span>'
      '<span class="it"><span class="sw" style="background:var(--d-__none)"></span>該当なし</span>'
      '<span class="it"><span class="sw" style="background:var(--d-__raw)"></span>生のまま</span>'
      '<span class="it"><span class="sw ring"></span>酢の有無で違う（帯は黒枠）</span>'
      '<span class="it">まとまり: <span class="sw c-sc" style="background:var(--low)"></span>ばらける <span class="sw" style="background:var(--saffron)"></span>まとまる（表面に膜・ちぎれ） <span class="sw" style="background:var(--kombu)"></span>まとまる</span>'
      '<span class="it"><span class="dot yes"></span>酢を必ず入れる <span class="dot opt"></span>任意 <span class="dot"></span>手順に無い</span></div>')
    st = diff["state"]
    ex = ""
    if frac_ex:
        x, y, a, b = frac_ex
        ex = f"（例: {x:g}℃・{y:g}分で {a[1]}/{a[2]} → {b[1]}/{b[2]}）"
    A('<ul class="find">')
    A(f'<li><b>ポーチドエッグになる領域は変わらない。</b>酢なし {n_po} マス、酢あり {n_po_v} マス（全 {diff["n"]} マス）。判定の1位が変わったマスは {diff["cls"]}。</li>')
    A(f'<li><b>変わるのは卵白の「まとまり」だけ。</b>{coh_T_min:g}℃以上の湯では、酢なしは「まとまる」（沸騰した 100℃ だけ「ばらける」）、酢ありはどの温度でも「まとまる（表面に膜・ちぎれ）」になります。'
      f'{coh_T_min:g}℃未満は、酢があっても「ばらける」。状態が変わったマスは卵白のまとまり {st.get("egg_white_cohesion", 0)} マスで、ほかの状態（卵白・卵黄の段階、温度）は全マスで同じでした。</li>')
    A(f'<li><b>判定の中身が変わるのは沸騰した湯の列だけ。</b>{"・".join(f"{x:g}℃" for x in frac_T)} の {len(diff["frac"])} マスで、満たした条件が1つ増えます{ex}。'
      '酢なしでは「卵白がばらける」ので条件を1つ落とし、酢ありでは「膜・ちぎれ」も条件（まとまる、または膜・ちぎれ）を満たすためです。</li>')
    A(f'<li><b>卵白が固まる速さは、酢で変わらない（表現していない）。</b>このシミュレータでは卵白は湯にふれる表面の温度で段階が決まり、湯に入れた最初の刻み（0.1 分）で決まります'
      f'（{t3:g}℃以上で段階 3）。酢の効果は「まとまり」の種類にしか入っていません。'
      '出典（R-E22）は「凝固が速まる」と書きますが、何分・何℃速まるかの数値がないため、固まり方の計算には入れていません。</li>')
    A('<li class="muted small">注意: この違いは、規則（R-E21・R-E22）と採用値（80℃未満はばらける、酢か塩が少しでも入っていれば効く＝推定）をそのまま計算した結果です。'
      '計算が新しい事実を見つけたのではなく、規則どうしの組み合わせを地図にしたものです。</li>')
    A('</ul>')
    dil, DS = dilution_html()
    A(dil)
    A('</section>')

    # 決め手の図（2026-10-22）: 酢ありの地図。枠が酢の有無で違うところ
    A(C.keyfig(f'湯に酢 {VINEGAR_PCT:g}% の地図（枠は酢なしと違うところ）', svg_map(Cm["vinegar"], Cm["plain"], "酢あり", rows, True),
               f'色の付いたポーチドエッグの範囲は、酢なしと同じです（{n_po} マス→{n_po_v} マス）。違うのは枠で囲んだ沸騰した湯の列の、卵白のまとまり（ばらける→表面に膜・ちぎれ）だけ。'
               '酢なしの地図と並べた図・凡例は「計算の詳しい答え」にあります。'))

    # 3. 根拠
    A(C.h2("basis", 3, "根拠"))
    A(C.basis_links(RULE_IDS, SOURCE_IDS))
    use = {**USE, "R-E21": f"卵白のまとまり: {coh_T_min:g}℃未満＝ばらける、沸騰＝ばらける（酢・塩なし）。料理の条件（湯温 80〜100℃・3分以上）"}
    H += C.rules_table(RULE_IDS, use)
    H += C.sources_table(SOURCE_IDS, SOURCE_CHECK)
    H += C.conflicts_block(["C13", "C14"])
    A('<p class="small muted">規則は足していません。「酢で何℃・何分早く固まるか」「酢の量と効果」を数値で示す出典を今回は持っていないため、足すと値を推測で置くことになるからです。'
      '足すなら、卵白（全卵ではなく）の pH と凝固温度・時間の関係を測った論文の本文を確かめてからにします。</p>')
    A('</section>')

    # 4. 結論
    A(C.h2("verdict", 4, "判定と確かさ"))
    CAN = (
        [f'酢は卵白の凝固を<b>速める向き</b>に働く。McGee（英語・日本語訳の2つの引用）、きょうの料理、酸性ほどオボアルブミンが熱に弱い（Wang 2025、精製たんぱく質）で向きが一致する。{conf("中")}',
         f'同じ McGee は、酢・塩で<b>卵の表面に不規則な膜・ちぎれ</b>ができるとも書く。散らない代わりに表面が荒れる。{conf("中")}',
         f'計算の上では、酢の有無で<b>ポーチドエッグになる湯温・時間の範囲は変わらない</b>（{n_po} マス→{n_po_v} マス）。変わるのは沸騰した湯での卵白のまとまり（ばらける→膜・ちぎれ）だけ。規則をそのまま計算した結果で、規則の確かさ（R-E21 低・R-E22 中）を超えない。{conf("低")}',
         f'酢の量（湯量の 3〜4.5%）なら、<b>酢も同じ量の水も湯温を同じだけ下げる</b>（{DS["T3"]:.1f}℃・{DS["T45"]:.1f}℃）。沸騰が止まるのは {DS["b23"][0]:.0f}〜{DS["b23"][1]:.0f} 秒で、白身の外側 1 mm が固まる {DS["mm23"][0]:.0f}〜{DS["mm23"][1]:.0f} 秒より短い。熱の面では酢と水に差は無く、酢の量の「足すこと」だけで白身が固まるまで湯が静かになるわけではない（Exp-19 の計算。火力は仮定）。{conf("中")}'],
        ['酢で<b>何分・何℃</b>早く固まるか。出典に数値がなく、シミュレータにも入っていない。',
         '酢で<b>形がまとまって見える</b>か。「散らない」（入れる派）と「膜・ちぎれができる」（入れない派）は同じ現象の別の評価かもしれないが、見た目を測った出典は無い（C14）。',
         '<b>酢の量</b>（レシピでは 1.5%、出典の例は 3〜4.5%）と効果の関係。計算では「少しでも入っていれば効く」と置いている（推定）。',
         '湯温 80℃未満で酢が効くか。計算では効かないと置いた（推定）。湯温そのものも出典によって 62℃〜沸騰とばらつく（C13）。',
         '酢と<b>同じ量の水</b>で仕上がり（まとまり）が違うか。計算で違いが出るのは酸の効き目だけで、その数値の出典が無い（下の実験で確かめられる）。',
         '差し水で<b>湯が静かになること</b>がまとまりに効くか。湯の動きは計算に無く、出典（R-E21、確かさ 低）からの推定まで。多めの差し水（200 mL 以上）は、火力によって白身の外側が固まるまで沸騰が止まるかどうかが変わる（Exp-19、火力は仮定）。',
         '酸味など味への影響。この計算の対象外。'])
    A(C.can_card(CAN[0]))
    A('<div class="verdict">'
      '<p><b>まとめ:</b> 「酢を入れると白身が早く固まる」は出典の向きがそろっていて、確かさは中。'
      '「だからまとまる（形がきれいになる）」は、出典で評価が分かれ（膜・ちぎれができる）、計算でも酢の有無で料理の範囲は変わらないので、<b>確かさは低</b>。'
      '計算が示すのは「沸騰させた湯なら酢で白身が散りにくくなるかもしれない。80℃以上で沸騰させない湯では酢がなくてもまとまる」という、規則どおりの予言です。これは下の実験で確かめられます。</p>'
      '</div></section>')
    A(C.h2("cannot", 4, "言えないこと") + C.cannot_card(CAN[1]) + '</section>')

    # 5. 実際に作って確かめる
    A(C.h2("try", 5, "自分で試す"))
    A('<p>計算の予言を、酢あり・なしを同じ条件で並べる対照実験で確かめます。結果はこの表に書き込み、写真を添えてください（あとで計算と照らし合わせます）。</p>')
    A(C.steps([
        '同じパックの卵（同じ日数）を使う。冷蔵庫から出して同じ時間置き、卵の温度をそろえる。',
        '同じ大きさの鍋2つに同じ量の水（1 L）。片方だけに酢 大さじ1（15 ml、1.5%）。塩はどちらにも入れない。',
        '温度計で湯温を測り、両方を同じ温度にそろえる（1回目 85℃前後＝鍋底から小さな泡、2回目 沸騰させたまま、余裕があれば 3回目 75℃）。',
        '卵はそれぞれ小さな器に割っておき、2つの鍋に同時に静かに落とす。かき混ぜない（渦を作らない）。',
        '入れてから 4 分でそっと引き上げ、同じ皿・同じ明るさで上から写真を撮る。',
        'できれば、どちらが酢ありかを知らない人に「まとまり具合」を付けてもらう（見る人の思い込みを除く）。',
        '白身の表面を指で軽く触り、つるっとしているか・膜やちぎれがあるかを書く。黄身は割って流れるかを見る。']))
    preds = [
        ("1", "なし", "85", "まとまる（卵白 3・卵黄は流れる）"),
        ("1", "あり", "85", "まとまる（表面に膜・ちぎれ）"),
        ("2", "なし", "100（沸騰）", "ばらける"),
        ("2", "あり", "100（沸騰）", "まとまる（表面に膜・ちぎれ）"),
        ("3", "なし", "75", "ばらける（80℃未満）"),
        ("3", "あり", "75", "ばらける（80℃未満。酢は効かないと置いた・推定）"),
    ]
    H += C.record_table(
        ["回", "酢", "酢の量 / 湯量", "湯温（℃、測った値）", "時間（分）", "写真", "まとまり具合（1 散った〜5 まとまった）", "表面（つるっと／膜・ちぎれ）", "黄身", "計算の予言"],
        [f'<tr><td class="num">{k}</td><td>{v}</td><td></td><td class="muted small">目標 {T}<br>測った値:</td><td class="muted small">目標 4</td><td class="photo"></td><td></td><td></td><td></td><td class="pred">{e(pr)}</td></tr>'
         for k, v, T, pr in preds])
    A('<p class="small muted">予言は Exp-14 の規則をそのまま計算したものです（料理の判定はどれもポーチドエッグ。違うのは卵白のまとまり）。予言と結果が合わなければ、規則（R-E21・R-E22）か採用値（80℃のしきい値、酢の効き方）を見直す材料になります。</p>')
    A('</section>')

    A(C.footer('Cuisine Network。計算: Exp-14 のシミュレータ（experiments/exp-14/sim、rules.yaml の規則と採用値）、地図 sim/maps.py の「割った卵を湯に落とす × 湯の温度 × 時間」。'
               'レシピ: Exp-15（experiments/exp-15-recipes/recipes.csv）。このページは experiments/myths/build.py（通説1 poached_vinegar）が生成します。'))
    A('</div>')
    return C.reorder(C.join(H))

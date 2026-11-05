"""本人判断 2026-09-29 ②「殻付き卵の白身の固まり方は外側の温度で決める」の確認。

    uv run python experiments/exp-14/sensitivity_white_surface.py

採用しているのは卵白の層の体積平均の温度 T_white（修正 B 2026-09-28、Q6 で球の熱伝導の解）。
文字どおり「殻の表面の温度（＝湯温、T_surface_max）」で卵白の段階を決めた場合と比べる。シミュレータ本体は変えない。
結果は results/sensitivity_white_surface.md。
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run import NO_MATCH_BELOW  # noqa: E402
from sim import DISH_RECIPES, DISH_RECIPES_TIMED, PAIRS, maps as M, params, physics, verdict  # noqa: E402
from sim.state import EGG_SHELL  # noqa: E402

ORIG = physics._egg


def surface_variant(s, ctx):
    if s.egg_form == EGG_SHELL and s.T_white_max is not None:
        keep = s.T_white_max
        s.T_white_max = s.T_surface_max
        try:
            ORIG(s, ctx)
        finally:
            s.T_white_max = keep
    else:
        ORIG(s, ctx)


def collect():
    out = {}
    for name, D in (("状態で止める版", DISH_RECIPES), ("時間の版", DISH_RECIPES_TIMED)):
        for k, r in D.items():
            out[(name, k)] = verdict(r.run(), NO_MATCH_BELOW).answer
    for i, p in enumerate(PAIRS, 1):
        for side, r in (("A", p.a), ("B", p.b)):
            out[("組", f"{i}{side}")] = verdict(r.run(), NO_MATCH_BELOW).answer
    grids = {p["id"]: M.preset_grid(p, NO_MATCH_BELOW) for p in M.PRESETS if p["id"].startswith("shell")}
    return out, grids


def main():
    physics._egg = ORIG
    a, ga = collect()
    physics._egg = surface_variant
    b, gb = collect()
    physics._egg = ORIG
    dj = {k: d["ja"] for k, d in params.dishes().items()}
    nm = lambda k: {None: "該当なし", M.RAW: "生のまま", M.NONE: "該当なし"}.get(k, dj.get(k, k))  # noqa: E731
    L = ["# 殻付き卵の卵白: 卵白の層の温度（採用）vs 殻の表面の温度（sensitivity_white_surface.py が生成）", "",
         "## 正解のレシピ（両版）と順番を変えた7組", ""]
    diff = [k for k in a if a[k] != b[k]]
    L.append(f"答えが変わったもの: {len(diff)}/{len(a)}" + ("" if not diff else "（" + ", ".join(f"{k}: {nm(a[k])}→{nm(b[k])}" for k in diff) + "）"))
    L += ["", "## 殻付き卵の地図", "", "| 地図 | マス | 変わったマス | 主な変化（採用→表面） |", "|---|---|---|---|"]
    for pid in ga:
        A, B = ga[pid], gb[pid]
        ch, n = Counter(), 0
        for j in range(len(A["ys"])):
            for i in range(len(A["xs"])):
                n += 1
                x, y = A["cells"][j][i]["cls"], B["cells"][j][i]["cls"]
                if x != y:
                    ch[(x, y)] += 1
        L.append(f"| {pid} | {n} | {sum(ch.values())} | " + "、".join(f"{nm(x)}→{nm(y)} {c}" for (x, y), c in ch.most_common()) + " |")
    L += ["", "## 沸騰した湯（100℃）の短い時間", "", "| 時間（分） | 採用 | 表面 |", "|---|---|---|"]
    A, B = ga["shell_egg_ice"], gb["shell_egg_ice"]
    i = A["xs"].index(100.0)
    for j, y in enumerate(A["ys"][:4]):
        L.append(f"| {y:g} | {nm(A['cells'][j][i]['cls'])} | {nm(B['cells'][j][i]['cls'])} |")
    out = HERE / "results" / "sensitivity_white_surface.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()

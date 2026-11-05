"""Exp-14: 13品（＋比較用のゆで卵）の再現結果（時間で止める版・状態で止める版）と、順番・操作を変えた組の結果を出す。

    uv run python experiments/exp-14/run.py

results/run_output.md（表）と results/run_output.json を書き出す。
"""
from __future__ import annotations

# 「該当なし」の下限: 必須条件を満たす料理のうち1位の満たした割合がこれ未満なら「該当なし」を返す。
# 2026-09-27 に結果を見る前に決めた。本人の例示の 0.6 をそのまま採った（条件の6割）。
# 前回の結果（プリン液を100℃で蒸すと ゆで卵 0.80・プリン 0.67）は知っていたが、それに合わせて動かしていない。
NO_MATCH_BELOW = 0.6

import copy
import json
import re
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from sim import DISH_RECIPES, DISH_RECIPES_TIMED, PAIRS, THIRTEEN, evaluate, params, verdict  # noqa: E402
from sim.recipes import UNTIL_KEPT_TIMED, UNTIL_REWRITE, UNTIL_REWRITE_CHANGES, Recipe  # noqa: E402

OUT = HERE / "results"
HEAT_OPS = {"heat", "bake", "steam", "simmer", "deep_fry"}
VERSIONS = {"until": ("状態で止める版（正解のレシピ）", DISH_RECIPES), "timed": ("時間で止める版", DISH_RECIPES_TIMED)}


def fmt(r) -> str:
    if r is None:
        return "—"
    return f"{r.ja} {len(r.met)}/{r.n_total}={r.fraction:.2f}" + ("" if r.required_ok else "※")


def nth(v, i):
    return v.candidates[i] if len(v.candidates) > i else None


def answer_cell(v, expected: str | None) -> str:
    ok = v.answer == expected
    if v.no_match:
        return f"{'✔ ' if ok else '✘ '}**該当なし**（{fmt(v.top)}）"
    return f"{'✔ ' if ok else '✘ '}{fmt(v.top)}"


def stops_text(s) -> str:
    if not s.stops:
        return "—"
    return "; ".join(f"{st['until']} {st['minutes']:g}分" if st["reached"]
                     else f"{st['until']} 未到達（上限 {st['max_time']}分）" for st in s.stops)


def run_dish(key: str, recipe: Recipe) -> dict:
    s = recipe.run()
    v = verdict(s, NO_MATCH_BELOW)
    own = key
    key = recipe.expected or key   # 2026-10-22: 蒸し卵（steamed_egg）は期待する答えが hard_boiled_egg
    mine = next(r for r in evaluate(s) if r.dish == key)
    return {
        "dish": key, "ja": mine.ja if own == key else f"{recipe.name}（答えは{mine.ja}）", "recipe": recipe.describe(), "note": recipe.note,
        "answer": v.answer, "no_match": v.no_match,
        "top": [(r.dish, r.ja, round(r.fraction, 3)) for r in v.candidates[:3]],
        "hit": v.answer == key,
        "fraction": round(mine.fraction, 3),
        "unmet": [(u.text, u.actual, u.basis) for u in mine.unmet],
        "stops": s.stops,
        "state": s.summary(),
        "trace": s.trace,
        "_v": v, "_s": s,
    }


def scaled(recipe: Recipe, k: float) -> Recipe:
    steps = [(n, {**kw, "time": round(kw["time"] * k, 3)} if n in HEAT_OPS else kw) for n, kw in recipe.steps]
    return replace(recipe, steps=steps)


def answer(recipe: Recipe, dishes: dict | None = None) -> str | None:
    return verdict(recipe.run(), NO_MATCH_BELOW, dishes).answer


def state_only_dishes() -> dict:
    """食材の条件を外した判定条件（状態だけでどこまで見分けられるか）。殻付きの必須は残す。"""
    return {k: {**d, "conditions": [c for c in d["conditions"] if "ingredients" not in c]}
            for k, d in params.dishes().items()}


def before_change_dishes() -> dict:
    """2026-09-27 の変更前の判定条件（必須は食材だけ。殻付き・2026-09-28 の定義上の必須は外す）。"""
    d = copy.deepcopy(params.dishes())
    for v in d.values():
        for c in v["conditions"]:
            if "ingredients" not in c:
                c.pop("required", None)
    return d


def first_number(text: str) -> float | None:
    m = re.match(r"\s*(-?\d+(?:\.\d+)?)", str(text))
    return float(m.group(1)) if m else None


def main() -> None:
    OUT.mkdir(exist_ok=True)
    lines: list[str] = [
        "# Exp-14 実行結果（run.py が生成）", "",
        "判定: 満たした条件の割合（重み付けなし）。必須条件（食材・殻付き）を満たさない料理は候補から外す。",
        f"候補の1位の割合が下限 **{NO_MATCH_BELOW}**（run.py の `NO_MATCH_BELOW`）未満なら **該当なし**（括弧内に1位の候補）。", ""]
    res_by_ver = {ver: {k: run_dish(k, r) for k, r in recipes.items()} for ver, (_, recipes) in VERSIONS.items()}
    hits = {ver: sum(d[k]["hit"] for k in THIRTEEN) for ver, d in res_by_ver.items()}

    # 1. 再現（両版）
    for sec, (ver, (title, recipes)) in enumerate(VERSIONS.items(), start=1):
        dishes = res_by_ver[ver]
        lines += [f"## 1.{sec} 13品の再現・{title}: {hits[ver]}/13", "",
                  "| 料理 | 答え（1位） | 2位 | 停止条件の到達 | 正解の料理で満たさなかった条件 |", "|---|---|---|---|---|"]
        for k, d in dishes.items():
            v = d["_v"]
            unmet = "; ".join(f"{t}（実際 {a}）" for t, a, _ in d["unmet"]) or "—"
            name = d["ja"] + ("（追加・13品外）" if k not in THIRTEEN else "")
            lines.append(f"| {name} | {answer_cell(v, d['dish'])} | {fmt(nth(v, 1))} | {stops_text(d['_s'])} | {unmet} |")
        lines.append("")

    so = state_only_dishes()
    lines += ["### 食材の条件を外し、状態の条件だけで判定した場合", "",
              "| 料理 | 状態で止める版 | 時間で止める版 |", "|---|---|---|"]
    so_hits = {"until": 0, "timed": 0}
    for k in DISH_RECIPES:
        cells = []
        for ver in ("until", "timed"):
            v = verdict(VERSIONS[ver][1][k].run(), NO_MATCH_BELOW, so)
            so_hits[ver] += (v.answer == k) and k in THIRTEEN
            cells.append(answer_cell(v, VERSIONS[ver][1][k].expected or k))
        lines.append(f"| {res_by_ver['until'][k]['ja']} | " + " | ".join(cells) + " |")
    lines.insert(lines.index("### 食材の条件を外し、状態の条件だけで判定した場合") + 1,
                 f"\n13品のうち 状態で止める版 {so_hits['until']} 品・時間で止める版 {so_hits['timed']} 品（同率は料理の並び順で先のもの）。")

    lines += ["", "### 停止条件（結果を見る前に決めた）", ""]
    for k, (_, why) in UNTIL_REWRITE.items():
        lines.append(f"- **{res_by_ver['until'][k]['ja']}**: {why}")
    lines += ["", "時間のまま残した品:", ""]
    for k, why in UNTIL_KEPT_TIMED.items():
        lines.append(f"- **{res_by_ver['until'][k]['ja']}**: {why}")
    lines += ["", "停止条件を後から変えた記録: " + ("なし" if not UNTIL_REWRITE_CHANGES else "")]
    for k, why in UNTIL_REWRITE_CHANGES.items():
        lines.append(f"- {k}: {why}")

    lines += ["", "### レシピ", ""]
    for ver, (title, _) in VERSIONS.items():
        lines += [f"**{title}**", ""]
        for k, d in res_by_ver[ver].items():
            if ver == "timed" or k in UNTIL_REWRITE:
                lines.append(f"- **{d['ja']}**: {d['recipe']}" + (f" — {d['note']}" if d["note"] else ""))
        if ver == "until":
            lines.append("- 他の品は時間で止める版と同じ")
        lines.append("")

    # 2. 順番・操作を変えた組
    lines += ["## 2. 順番・操作を変えた組", "", "| 組 | 変えたもの | 入力 | 答え（1位） | 2位 | 期待 |", "|---|---|---|---|---|---|"]
    pair_out = []
    for p in PAIRS:
        for side in (p.a, p.b):
            v = verdict(side.run(), NO_MATCH_BELOW)
            exp = side.expected or f"{p.a.expected} ではない"
            ok = (v.answer == side.expected) if side.expected else (v.answer != p.a.expected)
            cell = f"**該当なし**（{fmt(v.top)}）" if v.no_match else fmt(v.top)
            lines.append(f"| {p.title} | {p.what_changed} | {side.name} | {'✔ ' if ok else '✘ '}{cell} | {fmt(nth(v, 1))} | {exp} |")
            pair_out.append({"pair": p.title, "input": side.name, "answer": v.answer,
                             "top": [(r.dish, round(r.fraction, 3)) for r in v.candidates[:3]], "ok": ok})

    # 3. 変更前との比較（殻付きの必須化・該当なし）
    before = before_change_dishes()
    lines += ["", "## 3. 変更前との比較（殻付きの必須化・「該当なし」）", "",
              "変更前 = 殻付きは必須でない・下限なし（必須を満たさない料理は下に並べるだけ）。",
              "殻付き必須 = 必須を満たさない料理を候補から外す・下限なし。現在 = さらに下限 "
              f"{NO_MATCH_BELOW} 未満を該当なし。変わった行だけ太字。", "",
              "| 入力 | 変更前 | 殻付き必須 | 現在 |", "|---|---|---|---|"]
    change_out = []
    inputs = [(f"正解（時間）{r.name}", r) for r in DISH_RECIPES_TIMED.values()]
    inputs += [(f"正解（状態）{DISH_RECIPES[k].name}", DISH_RECIPES[k]) for k in UNTIL_REWRITE]
    inputs += [(f"組 {side.name}", side) for p in PAIRS for side in (p.a, p.b)]
    for label, r in inputs:
        s = r.run()
        b0 = evaluate(s, before)[0]
        v1 = verdict(s, 0.0)
        v2 = verdict(s, NO_MATCH_BELOW)
        c0 = fmt(b0)
        c1 = fmt(v1.top) if v1.top else "該当なし（候補なし）"
        c2 = f"該当なし（{fmt(v2.top)}）" if v2.no_match else fmt(v2.top)
        changed = (b0.dish != (v1.answer or "")) or v2.no_match
        if changed:
            c2 = f"**{c2}**"
            label = f"**{label}**"
        lines.append(f"| {label} | {c0} | {c1} | {c2} |")
        change_out.append({"input": label.strip("*"), "before": [b0.dish, round(b0.fraction, 3), b0.required_ok],
                           "shell_required": v1.answer, "now": v2.answer,
                           "now_top": (v2.top.dish, round(v2.top.fraction, 3)) if v2.top else None})

    # 4. 時間の感度（時間で止める版）
    lines += ["", "## 4. 加熱時間を一律に変えたときの答え（時間で止める版）", "",
              "加熱の操作（heat/bake/steam/simmer/deep_fry）の time だけを倍率で変える。数値は1位の候補の満たした割合。",
              "状態で止める版は時間を持たないので対象外。", "",
              "| 料理 | ×0.8 | ×0.9 | ×1.0 | ×1.1 | ×1.2 |", "|---|---|---|---|---|---|"]
    sens = {}
    for k, r in DISH_RECIPES_TIMED.items():
        row = []
        for f in (0.8, 0.9, 1.0, 1.1, 1.2):
            v = verdict(scaled(r, f).run(), NO_MATCH_BELOW)
            if v.no_match:
                row.append(f"該当なし {v.top.fraction:.2f}" if v.top else "該当なし")
            else:
                row.append(f"✔ {v.top.fraction:.2f}" if v.answer == k else f"{DISH_RECIPES[v.answer].name} {v.top.fraction:.2f}")
        sens[k] = row
        lines.append(f"| {res_by_ver['timed'][k]['ja']} | " + " | ".join(row) + " |")

    # 5. 採用値
    used = sorted(params.USED)
    av = params.rules()["sim"]["adopted_values"]
    lines += ["", "## 5. 計算で参照した採用値", "", "| key | 採用値 | 規則 | 出典／確認 | 代替値 |", "|---|---|---|---|---|"]
    for k in used:
        a = av[k]
        src = a.get("source") or a.get("check", "")
        alts = "、".join(map(str, a.get("alternatives", []))) or "—"
        lines.append(f"| `{k}` | {a['value']} {a.get('unit', '')} | {a.get('rule', '—')} | {src} | {alts} |")

    # 6. 代替値に差し替えたとき
    lines += ["", "## 6. 採用値を代替値に1つずつ差し替えたときの再現数（13品）", "",
              "| key | 採用値 → 代替値 | 状態で止める版 | 外れた料理 | 時間で止める版 | 外れた料理 |", "|---|---|---|---|---|---|"]
    alt_out = []
    for k in used:
        a = av[k]
        if not isinstance(a["value"], (int, float)):
            continue
        for alt in a.get("alternatives", []):
            v = first_number(alt)
            if v is None:
                continue
            row = {}
            with params.override({k: v}):
                for ver in ("until", "timed"):
                    recipes = VERSIONS[ver][1]
                    row[ver] = [x for x in THIRTEEN if answer(recipes[x]) != x]
            cells = " | ".join(f"{13 - len(m)}/13 | {'、'.join(DISH_RECIPES[x].name for x in m) or '—'}" for m in row.values())
            lines.append(f"| `{k}` | {a['value']} → {v:g} | {cells} |")
            alt_out.append({"key": k, "adopted": a["value"], "alt": v,
                            **{f"hits_{ver}": 13 - len(m) for ver, m in row.items()},
                            **{f"missed_{ver}": m for ver, m in row.items()}})

    (OUT / "run_output.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    dump = {ver: {k: {kk: vv for kk, vv in d.items() if not kk.startswith("_")} for k, d in ds.items()}
            for ver, ds in res_by_ver.items()}
    (OUT / "run_output.json").write_text(json.dumps(
        {"no_match_below": NO_MATCH_BELOW, "dishes": dump, "pairs": pair_out, "change_vs_before": change_out,
         "time_sensitivity": sens, "alternatives": alt_out,
         "adopted_used": {k: av[k]["value"] for k in used}},
        ensure_ascii=False, indent=1, default=str), encoding="utf-8")

    for ver, (title, _) in VERSIONS.items():
        print(f"13品の再現（{title}）: {hits[ver]}/13")
        for k, d in res_by_ver[ver].items():
            print(f"  {'OK' if d['hit'] else 'NG'} {d['ja']}: {d['_v'].line()}  停止: {stops_text(d['_s'])}")
    print("順番・操作を変えた組:")
    for p in pair_out:
        print(f"  {'OK' if p['ok'] else 'NG'} {p['input']} → {p['answer'] or '該当なし'} {p['top'][0] if p['top'] else ''}")
    print(f"→ {OUT / 'run_output.md'}")


if __name__ == "__main__":
    main()

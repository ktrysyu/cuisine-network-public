"""Exp-02 の味覚スコア対象食材を選び、下書き CSV と突き合わせる。

選定基準: data/processed/whats_cooking_tokens.tsv（Exp-01 の正規化済み食材）で、
食材を含むレシピ数（1 レシピ内の重複は 1 回）が多い順に並べ、300 位の件数以上を
すべて採る（300 位付近の同数を切らないため、件数は 300 を少し超えうる）。

  uv run python experiments/exp-02/select_ingredients.py          # 選定結果を表示
  uv run python experiments/exp-02/select_ingredients.py --check  # draft CSV と一致するか検査
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOKENS = ROOT / "data" / "processed" / "whats_cooking_tokens.tsv"
DRAFT = ROOT / "data" / "labels" / "taste_scores_draft.csv"
TOP_N = 300
AXES = ["sweet", "salty", "sour", "bitter", "umami", "spicy"]


def recipe_counts() -> Counter:
    c = Counter()
    with TOKENS.open() as f:
        next(f)
        for line in f:
            _, _, ings = line.rstrip("\n").split("\t")
            c.update(set(ings.split("|")))
    return c


def select(c: Counter) -> list[tuple[str, int]]:
    ranked = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    threshold = ranked[TOP_N - 1][1]
    return [(k, v) for k, v in ranked if v >= threshold]


def check(selected: list[tuple[str, int]]) -> int:
    want = dict(selected)
    with DRAFT.open() as f:
        rows = list(csv.DictReader(f))
    got = {r["ingredient"]: int(r["n_recipes"]) for r in rows}
    errors = []
    if set(got) != set(want):
        errors.append(f"食材の集合が違う: 不足 {sorted(set(want) - set(got))} / 余分 {sorted(set(got) - set(want))}")
    errors += [f"n_recipes 不一致: {k} {got[k]} != {want[k]}" for k in got if k in want and got[k] != want[k]]
    for r in rows:
        for a in AXES:
            if r[a] not in {"0", "1", "2", "3", "4", "5"}:
                errors.append(f"{r['ingredient']}: {a}={r[a]!r}")
        if r["confidence"] not in {"high", "medium", "low"}:
            errors.append(f"{r['ingredient']}: confidence={r['confidence']!r}")
        if not r["canonical"]:
            errors.append(f"{r['ingredient']}: canonical が空")
    for e in errors:
        print(e)
    print(f"{len(rows)} 行を検査、問題 {len(errors)} 件")
    return 1 if errors else 0


def main() -> int:
    c = recipe_counts()
    selected = select(c)
    print(f"ユニーク食材 {len(c)} 種中 {len(selected)} 種を選定（{TOP_N} 位の件数 {selected[TOP_N - 1][1]} 以上）")
    if "--check" in sys.argv:
        return check(selected)
    for k, v in selected:
        print(f"{v}\t{k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

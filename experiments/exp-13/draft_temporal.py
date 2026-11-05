"""Exp-13 時間の層の下書き（2026-10-22、CLA-131）。値を決めるのは本人。

    uv run python experiments/exp-13/draft_temporal.py

規則は plan.md「2026-10-22 夜: 下書き」（作る前にコミット）。出力は data/labels/temporal_draft.csv。
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AXES = ["sweet", "salty", "sour", "bitter", "umami", "spicy"]
JA = {"sweet": "甘", "salty": "塩", "sour": "酸", "bitter": "苦", "umami": "旨", "spicy": "辛"}
ONSET = {"salty": 5, "sweet": 4, "sour": 4, "umami": 2, "bitter": 1, "spicy": 2}
LINGER = {"salty": 1, "sweet": 2, "sour": 1, "umami": 4, "bitter": 5, "spicy": 5}
OUT = ROOT / "data" / "labels" / "temporal_draft.csv"


def main() -> None:
    rows = list(csv.DictReader((ROOT / "data" / "labels" / "taste_scores.csv").open(encoding="utf-8")))
    out = []
    for r in rows:
        s = {a: float(r[a]) for a in AXES}
        tot = sum(s.values())
        if tot == 0:
            out.append({"ingredient": r["ingredient"], "ja": r["ja"], "onset": "", "linger": "", "first": "", "last": "",
                        "basis": "味が全軸 0（本人が付ける）"})
            continue
        onset = sum(s[a] * ONSET[a] for a in AXES) / tot
        linger = sum(s[a] * LINGER[a] for a in AXES) / tot
        first = max(AXES, key=lambda a: (s[a] * ONSET[a], s[a]))
        last = max(AXES, key=lambda a: (s[a] * LINGER[a], s[a]))
        out.append({"ingredient": r["ingredient"], "ja": r["ja"], "onset": f"{onset:.1f}", "linger": f"{linger:.1f}",
                    "first": JA[first], "last": JA[last],
                    "basis": "味のスコア " + "・".join(f"{JA[a]}{int(s[a])}" for a in AXES if s[a]) + "（plan.md の規則、推定）"})
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("wrote", OUT, len(out), "rows;", sum(1 for o in out if o["onset"] == ""), "blank")


if __name__ == "__main__":
    main()

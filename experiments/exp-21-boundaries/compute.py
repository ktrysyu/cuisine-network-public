"""Exp-21: 卵の最初の温度を 5→20℃ に変えたときの、殻付き卵の地図（氷水に取る）の変化（2026-10-22、night-queue 作業列 14・15）。

    uv run python experiments/exp-21-boundaries/compute.py

- 地図は sim/maps.py の PRESETS「shell_egg_ice」（湯の温度 50〜100℃ × 時間 1〜59 分、氷水に 15 分取る）。卵の最初の温度（T0）だけを変える
- 計算は Exp-14 のシミュレータの既定（殻付き卵は kinetic、Exp-17）のまま。判定・地図の範囲は変えない
- 出力 results/frames.json（T0 ごとのマスの判定）を、境目のアニメーション（boundary.html）と 3D の状態図（state3d.html）が使う
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "exp-14"))

from run import NO_MATCH_BELOW  # noqa: E402
from sim import maps, params  # noqa: E402

PRESET = next(p for p in maps.PRESETS if p["id"] == "shell_egg_ice")
T0S = [5, 7.5, 10, 12.5, 15, 17.5, 20]


def main() -> None:
    frames = []
    for T0 in T0S:
        b = maps.base_recipe(PRESET["base"])
        b["T0"] = T0
        g = maps.grid(b, PRESET["x"], PRESET["y"], NO_MATCH_BELOW)
        frames.append({"T0": T0, "cells": [[c["cls"] for c in row] for row in g["cells"]]})
        print("T0", T0, "done", flush=True)
    dj = {k: d["ja"] for k, d in params.dishes().items()}
    dj.update({maps.NONE: "該当なし", maps.RAW: "生のまま（変化なし）"})
    out = {"about": "Exp-21。殻付き卵 × 湯の温度 × 時間（氷水に取る）の地図を、卵の最初の温度ごとに。compute.py が生成", "preset": PRESET["id"],
           "xs": g["xs"], "ys": g["ys"], "x_label": "湯の温度（℃）", "y_label": "湯に入れていた時間（分）", "frames": frames, "ja": dj}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "frames.json").write_text(json.dumps(out, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

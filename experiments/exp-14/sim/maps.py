"""地図（状態図）: 元のレシピの2つの数値を縦軸・横軸に振り、マスごとにシミュレータを走らせて判定の1位を返す。

- 判定は verdict（必須条件で候補を絞り、1位の満たした割合が下限未満なら「該当なし」）。数値は変えない
- 「該当なし」のうち、状態の段階がどれも動いていないもの（加熱が足りず生のまま・変化なし）を RAW として分ける
- 迷い度: 1位と2位（候補の中）の満たした割合の差。2位が無ければ1位の割合そのもの
- JS 版は js/sim.js の CookSim.mapGrid。一致は js/test_parity.js（expected_maps.json）で確かめる

レシピは JSON の形（js/export_data.recipe_json と同じ: ingredients・steps=[[操作, kwargs], ...]・T0・egg_form・form）で扱う。
"""
from __future__ import annotations

import copy
import math

from . import ops
from .judge import verdict
from .recipes import DISH_RECIPES, DISH_RECIPES_TIMED, MAP_BASE_RECIPES, Recipe

NONE = "__none"   # 該当なし
RAW = "__raw"     # 該当なし のうち、段階がどれも動いていない（生のまま・変化なし）

# 「生のまま・変化なし」を見る段階の変数（はじめの状態と比べる。値なしは 0 とみなす）
RAW_VARS = ["egg_white_stage", "egg_yolk_stage", "egg_gel_stage", "starch_gel", "maillard", "caramel",
            "meat_myosin", "milk_whey_denatured", "foam_stage", "gelatin_state", "cell_wall"]

# 最初から用意する地図（ページも同じものを使う。export_data.py が sim_data.json に書き出す）
PRESETS = [
    {"id": "shell_egg", "title": "殻付き卵 × 湯の温度 × 時間（室温に置く）", "base": "timed:onsen_tamago",
     "x": {"axis": {"kind": "step", "i": 0, "key": "T"}, "lo": 50, "hi": 100, "step": 2.5},
     "y": {"axis": {"kind": "step", "i": 0, "key": "time"}, "lo": 1, "hi": 60, "step": 2}},
    # 2026-09-28 夜（余熱）: 上の地図は元のレシピ（温泉卵）の後の手順「室温に15分置く」込み。こちらは氷水に15分取る
    {"id": "shell_egg_ice", "title": "殻付き卵 × 湯の温度 × 時間（氷水に取る）", "base": "map:shell_egg_ice",
     "x": {"axis": {"kind": "step", "i": 0, "key": "T"}, "lo": 50, "hi": 100, "step": 2.5},
     "y": {"axis": {"kind": "step", "i": 0, "key": "time"}, "lo": 1, "hi": 60, "step": 2}},
    {"id": "poach", "title": "割った卵を湯に落とす × 湯の温度 × 時間", "base": "until:poached_egg",
     "x": {"axis": {"kind": "step", "i": 0, "key": "T"}, "lo": 50, "hi": 100, "step": 2.5},
     "y": {"axis": {"kind": "step", "i": 0, "key": "time"}, "lo": 0.5, "hi": 15, "step": 0.5}},
    {"id": "beaten_pan", "title": "溶き卵 × フライパンの温度 × 時間", "base": "timed:omelet",
     "x": {"axis": {"kind": "step", "i": 1, "key": "T"}, "lo": 80, "hi": 240, "step": 8},
     "y": {"axis": {"kind": "step", "i": 1, "key": "time"}, "lo": 0.2, "hi": 6, "step": 0.2}},
    # 2026-09-28 夜 Q6 (d): 混ぜながら焼く溶き卵（スクランブルエッグ）の地図。軸・範囲は beaten_pan と同じ
    {"id": "beaten_stir", "title": "溶き卵を混ぜながら × フライパンの温度 × 時間", "base": "timed:scrambled_eggs",
     "x": {"axis": {"kind": "step", "i": 1, "key": "T"}, "lo": 80, "hi": 240, "step": 8},
     "y": {"axis": {"kind": "step", "i": 1, "key": "time"}, "lo": 0.2, "hi": 6, "step": 0.2}},
    {"id": "pudding", "title": "プリン液 × 蒸す温度 × 時間", "base": "timed:custard_pudding",
     "x": {"axis": {"kind": "step", "i": 1, "key": "T"}, "lo": 70, "hi": 100, "step": 1.5},
     "y": {"axis": {"kind": "step", "i": 1, "key": "time"}, "lo": 2, "hi": 40, "step": 2}},
]


def recipe_json(r: Recipe) -> dict:
    return {"name": r.name, "ingredients": dict(r.ingredients), "steps": [[n, dict(kw)] for n, kw in r.steps],
            "T0": r.T0, "egg_form": r.egg_form, "form": r.form, "expected": r.expected}


def base_recipe(ref: str) -> dict:
    kind, key = ref.split(":")
    return recipe_json({"until": DISH_RECIPES, "timed": DISH_RECIPES_TIMED, "map": MAP_BASE_RECIPES}[kind][key])


def values(lo: float, hi: float, step: float) -> list[float]:
    """lo から hi まで step 刻み（JS と同じ式: lo + i*step を小数9桁の10進表記に丸める。0.6000000000000001 → 0.6）。"""
    n = int(math.floor((hi - lo) / step + 1e-9)) + 1
    return [_r9(lo + i * step) for i in range(n)]


def _r9(x: float) -> float:
    return float(f"{x:.9f}")


def with_value(recipe: dict, axis: dict, v: float) -> dict:
    """recipe の axis の値を v にしたコピー。"""
    r = copy.deepcopy(recipe)
    k = axis["kind"]
    if k == "step":
        r["steps"][axis["i"]][1][axis["key"]] = v
    elif k == "ing":
        r["ingredients"][axis["key"]] = v
    elif k == "add":
        r["steps"][axis["i"]][1]["add"][axis["key"]] = v
    elif k == "T0":
        r["T0"] = v
    else:
        raise ValueError(f"軸の種類が不明: {axis}")
    return r


def run_json(r: dict):
    rec = Recipe(r.get("name", ""), r["ingredients"], [(n, kw) for n, kw in r["steps"]], T0=r.get("T0"),
                 egg_form=r.get("egg_form"), form=r.get("form") or "pot")
    s0 = rec.initial()
    return s0, ops.apply(s0, rec.steps)


def _norm(v):
    return 0 if v is None else v


def cell(r: dict, min_fraction: float) -> dict:
    s0, s = run_json(r)
    v = verdict(s, min_fraction)
    c = v.candidates
    top = [c[0].dish, len(c[0].met), c[0].n_total] if c else None
    second = [c[1].dish, len(c[1].met), c[1].n_total] if len(c) > 1 else None
    f1 = c[0].fraction if c else 0.0
    f2 = c[1].fraction if len(c) > 1 else 0.0
    if v.answer is not None:
        cls = v.answer
    elif all(_norm(s.get(k)) == _norm(s0.get(k)) for k in RAW_VARS):
        cls = RAW
    else:
        cls = NONE
    return {"cls": cls, "top": top, "second": second, "margin": f1 - f2}


def grid(base: dict, x: dict, y: dict, min_fraction: float) -> dict:
    """x・y は {"axis": ..., "lo", "hi", "step"}。cells[j][i] は y の j 番目・x の i 番目。"""
    xs = values(x["lo"], x["hi"], x["step"])
    ys = values(y["lo"], y["hi"], y["step"])
    cells = []
    for yv in ys:
        row = []
        for xv in xs:
            row.append(cell(with_value(with_value(base, x["axis"], xv), y["axis"], yv), min_fraction))
        cells.append(row)
    return {"xs": xs, "ys": ys, "cells": cells}


def preset_grid(preset: dict, min_fraction: float, coarsen: int = 1) -> dict:
    """最初から用意した地図。coarsen>1 で刻みを粗くする（一致テスト用）。"""
    x = {**preset["x"], "step": preset["x"]["step"] * coarsen}
    y = {**preset["y"], "step": preset["y"]["step"] * coarsen}
    return grid(base_recipe(preset["base"]), x, y, min_fraction)

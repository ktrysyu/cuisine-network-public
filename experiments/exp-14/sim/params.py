"""rules.yaml を読み、シミュレータの採用値を引く。

採用値は rules.yaml の `sim.adopted_values` が正本。ここに数値を直書きしない。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

RULES_PATH = Path(__file__).resolve().parent.parent / "rules.yaml"


@lru_cache(maxsize=1)
def rules() -> dict:
    with open(RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


USED: set[str] = set()  # 計算で参照した採用値（結果に記録する）


def V(key: str):
    """採用値（sim.adopted_values.<key>.value）。"""
    USED.add(key)
    return rules()["sim"]["adopted_values"][key]["value"]


class override:
    """採用値を一時的に差し替える（感度の確認用）。with params.override({"key": value}): ..."""

    def __init__(self, values: dict):
        self.values = values
        self.saved: dict = {}

    def __enter__(self):
        av = rules()["sim"]["adopted_values"]
        for k, v in self.values.items():
            self.saved[k] = av[k]["value"]
            av[k]["value"] = v
        return self

    def __exit__(self, *exc):
        av = rules()["sim"]["adopted_values"]
        for k, v in self.saved.items():
            av[k]["value"] = v
        return False


def adopted(key: str) -> dict:
    return rules()["sim"]["adopted_values"][key]


def H(*path: str):
    """sim 以下の任意の値。末端が {value: ...} なら value を返す。"""
    node = rules()["sim"]
    for p in path:
        node = node[p]
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    return node


def composition(ingredient: str) -> dict[str, float]:
    """成分表の g/100g。Tr・null は 0 とみなす。"""
    raw = rules()["ingredients"][ingredient]["composition"]
    out = {}
    for k, v in raw.items():
        out[k] = float(v) if isinstance(v, (int, float)) else 0.0
    return out


def split(ingredient: str) -> dict:
    return rules()["sim"]["composition_split"].get(ingredient, {})


def dishes() -> dict:
    return rules()["dish_conditions"]


def levels(var: str):
    return rules()["state_variables"][var]["levels"]

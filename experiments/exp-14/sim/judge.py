"""料理の判定: 条件の組み合わせのうち満たした割合で順位を付ける（重み付けしない）。

- 条件は rules.yaml の dish_conditions。
- required: true の条件（食材・殻付き）を満たさない料理は候補から外す（evaluate は内訳のために
  全料理を返し、外れた料理は下に並べる。rank と verdict は候補だけを返す）。
- verdict: 1位の満たした割合が下限（min_fraction）未満なら「該当なし」。上位の候補と内訳は併せて返す。
  下限の値は run.py 冒頭の NO_MATCH_BELOW（判定の関数には数値を直書きしない）。
- 距離関数は使わない。答えと一緒に、満たした条件・満たさなかった条件と実際の値を返す。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import params as P
from .state import State


@dataclass
class CondResult:
    text: str
    actual: object
    ok: bool
    required: bool
    basis: str


@dataclass
class DishResult:
    dish: str
    ja: str
    required_ok: bool
    met: list[CondResult] = field(default_factory=list)
    unmet: list[CondResult] = field(default_factory=list)

    @property
    def n_total(self) -> int:
        return len(self.met) + len(self.unmet)

    @property
    def fraction(self) -> float:
        return len(self.met) / self.n_total if self.n_total else 0.0

    def line(self) -> str:
        return f"{self.ja}（{self.dish}） {len(self.met)}/{self.n_total} = {self.fraction:.2f}" + (
            "" if self.required_ok else "  ※必須条件を満たさない")


def _fmt(v):
    if isinstance(v, float):
        return round(v, 2)
    return v


def check(state: State, cond: dict) -> CondResult:
    basis = str(cond.get("basis", ""))
    req = bool(cond.get("required", False))
    if "ingredients" in cond:
        missing = []
        for item in cond["ingredients"]:
            alts = item if isinstance(item, list) else [item]
            if not state.has(*alts):
                missing.append("|".join(alts))
        text = "食材: " + ", ".join("|".join(i) if isinstance(i, list) else i for i in cond["ingredients"])
        return CondResult(text, "不足: " + ", ".join(missing) if missing else "あり", not missing, req, basis)
    if "history" in cond:
        th, m = cond["at_or_above"], cond["min_minutes"]
        actual = state.hold(cond["history"], "ge", th)
        return CondResult(f"{cond['history']} が {th}℃以上の時間 ≧ {m}分", _fmt(actual), actual >= m, req, basis)
    var = cond["var"]
    v = state.get(var)
    if "range" in cond:
        lo, hi = cond["range"]
        text = f"{var} ∈ [{'' if lo is None else lo}, {'' if hi is None else hi}]"
        ok = v is not None and not isinstance(v, str) and (lo is None or v >= lo) and (hi is None or v <= hi)
    elif "in" in cond:
        text = f"{var} ∈ {{{', '.join(str(x) for x in cond['in'])}}}"
        ok = v is not None and v in cond["in"]
    elif "is" in cond:
        text = f"{var} = {cond['is']}"
        ok = v is not None and bool(v) == bool(cond["is"])
    else:
        raise ValueError(cond)
    return CondResult(text, "該当なし" if v is None else _fmt(v), ok, req, basis)


def evaluate(state: State, dishes: dict | None = None) -> list[DishResult]:
    dishes = P.dishes() if dishes is None else dishes
    out = []
    for key, d in dishes.items():
        r = DishResult(key, d["ja"], True)
        for c in d["conditions"]:
            cr = check(state, c)
            (r.met if cr.ok else r.unmet).append(cr)
            if cr.required and not cr.ok:
                r.required_ok = False
        out.append(r)
    order = list(dishes)
    out.sort(key=lambda r: (not r.required_ok, -r.fraction, order.index(r.dish)))
    return out


NO_MATCH = "該当なし"


def candidates(state: State, dishes: dict | None = None) -> list[DishResult]:
    """必須条件をすべて満たす料理だけ（満たした割合の順）。"""
    return [r for r in evaluate(state, dishes) if r.required_ok]


def rank(state: State, top: int = 3) -> list[DishResult]:
    return candidates(state)[:top]


@dataclass
class Verdict:
    answer: str | None          # 料理のキー。該当なしなら None
    ja: str                     # 料理名か「該当なし」
    min_fraction: float
    candidates: list[DishResult]   # 必須条件を満たす料理（割合の順）
    excluded: list[DishResult]     # 必須条件を満たさず外した料理

    @property
    def no_match(self) -> bool:
        return self.answer is None

    @property
    def top(self) -> DishResult | None:
        return self.candidates[0] if self.candidates else None

    def line(self) -> str:
        if not self.no_match:
            return f"{self.ja} {self.top.fraction:.2f}"
        if self.top is None:
            return f"{NO_MATCH}（必須条件を満たす料理なし）"
        return f"{NO_MATCH}（1位 {self.top.ja} {self.top.fraction:.2f} < {self.min_fraction}）"


def verdict(state: State, min_fraction: float, dishes: dict | None = None) -> Verdict:
    res = evaluate(state, dishes)
    cands = [r for r in res if r.required_ok]
    excl = [r for r in res if not r.required_ok]
    if cands and cands[0].fraction >= min_fraction:
        return Verdict(cands[0].dish, cands[0].ja, min_fraction, cands, excl)
    return Verdict(None, NO_MATCH, min_fraction, cands, excl)

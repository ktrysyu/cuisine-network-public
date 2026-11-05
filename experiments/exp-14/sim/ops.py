"""操作: State → State の純粋な関数（入力の State は変えない）。

rules.yaml の operations に対応する。焼く・蒸す・煮る・揚げる・冷やす・寝かせる は
すべて heat（媒体・温度・時間）の特殊化。
"""
from __future__ import annotations

import math

from . import params as P
from .physics import Ctx, advance, apply_rules
from .state import (COH_COHESIVE, COH_FILM, COH_SCATTER, EGG_BEATEN, EGG_CRACKED, EGG_KEYS, EGG_SHELL,
                    FAT_NETWORK, FAT_SEPARATED, YEAST_ACTIVE, YEAST_DEAD, State)

MEDIA = ("pan", "air", "steam", "water", "oil")


def _run(s: State, ctx: Ctx, time: float, until: dict | None = None) -> float:
    """time 分だけ進める。until があれば、条件を満たした刻みで止める。進めた時間（分）を返す。"""
    dt = P.H("run", "dt_min")
    n = max(1, round(time / dt))
    step = time / n
    for i in range(n):
        ctx.t_in_op = i * step
        advance(s, ctx, step)
        apply_rules(s, ctx, step)
        if until is not None and until_met(s, until):
            return (i + 1) * step
    return n * step


# ----------------------------------------------------------------------
# 停止条件（「〜になるまで」）
def until_text(cond: dict) -> str:
    var = cond["var"]
    if "ge" in cond:
        return f"{var}≧{cond['ge']}"
    if "le" in cond:
        return f"{var}≦{cond['le']}"
    if "in" in cond:
        return f"{var}∈{{{', '.join(map(str, cond['in']))}}}"
    raise ValueError(f"停止条件の形が不明: {cond}")


def until_met(s: State, cond: dict) -> bool:
    """停止条件: {"var": 状態変数, "ge"|"le": 値} か {"var": 状態変数, "in": [値, ...]}。"""
    v = s.get(cond["var"])
    if v is None:
        return False
    if "ge" in cond:
        return not isinstance(v, str) and v >= cond["ge"]
    if "le" in cond:
        return not isinstance(v, str) and v <= cond["le"]
    if "in" in cond:
        return v in cond["in"]
    raise ValueError(f"停止条件の形が不明: {cond}")


def _begin(state: State, label: str) -> State:
    s = state.copy()
    s.ops.append(label)
    return s


# ----------------------------------------------------------------------
def heat(state: State, medium: str, T: float, time: float | None = None, stirring: bool = False,
         lid: bool = False, form: str | None = None, until: dict | None = None,
         max_time: float | None = None, flip: bool = True) -> State:
    """加熱（基本形）。medium: pan（金属＋油）/ air（オーブン・冷蔵庫・室温）/ steam / water / oil。

    時間で止める: time=分。
    状態で止める: until={"var": 状態変数, "ge"|"le"|"in": ...}, max_time=上限（分）。
      条件を満たした刻みで止める。上限までに満たさなければ上限で止め、未到達として記録する
      （State.stops と trace）。time と until は同時に指定しない。
    flip: 肉片（meat_model = slab）をフライパンで焼くとき、前のフライパンの操作から返すか（Exp-18）。
      False は同じ面のまま火加減だけ変える手順。tau のときは何もしない。
    """
    if medium not in MEDIA:
        raise ValueError(f"未知の媒体: {medium}")
    if until is None:
        if time is None:
            raise ValueError("time か until のどちらかを指定する")
        if max_time is not None:
            raise ValueError("max_time は until と一緒に指定する")
        s = _begin(state, f"heat({medium},{T}℃,{time}min{',撹拌' if stirring else ''}{',蓋' if lid else ''}"
                          f"{'' if flip else ',返さない'})")
        if form:
            s.form = form
        _run(s, Ctx("heat", medium, T, stirring=stirring, lid=lid, flip=flip), time)
        return s
    if time is not None:
        raise ValueError("time と until は同時に指定しない（until の上限は max_time）")
    if max_time is None or max_time <= 0:
        raise ValueError("until には上限時間 max_time（分）が要る")
    cond = until_text(until)
    s = _begin(state, f"heat({medium},{T}℃,until {cond}{',撹拌' if stirring else ''}{',蓋' if lid else ''}"
                      f"{'' if flip else ',返さない'})")
    if form:
        s.form = form
    already = until_met(s, until)
    elapsed = 0.0 if already else _run(s, Ctx("heat", medium, T, stirring=stirring, lid=lid, flip=flip), max_time, until)
    reached = already or until_met(s, until)
    s.stops.append({"op": len(s.ops), "until": cond, "reached": reached,
                    "minutes": round(elapsed, 3), "max_time": max_time})
    if reached:
        s.ops[-1] += f"→{elapsed:.2g}min"
        s.log("until", f"{cond} に {elapsed:.2f}分で到達" + ("（加熱前から満たしていた）" if already else ""))
    else:
        s.ops[-1] += f"→未到達(上限{max_time}min)"
        s.log("until", f"{cond} に上限 {max_time}分で到達しなかった（{until['var']}={s.get(until['var'])}）")
    return s


def bake(state, T, time=None, medium="pan", stirring=False, form=None, until=None, max_time=None, flip=True):
    """焼く・炒める。"""
    return heat(state, medium, T, time, stirring=stirring, form=form, until=until, max_time=max_time, flip=flip)


def steam(state, T, time=None, form=None, until=None, max_time=None):
    """蒸す。蒸し器の庫内温度 T（≦100）。"""
    return heat(state, "steam", T, time, form=form, until=until, max_time=max_time)


def simmer(state, T, time=None, lid=False, stirring=False, form=None, until=None, max_time=None):
    """煮る・茹でる・炊く。"""
    return heat(state, "water", T, time, stirring=stirring, lid=lid, form=form, until=until, max_time=max_time)


def deep_fry(state, T, time=None, form=None, until=None, max_time=None):
    """揚げる。"""
    return heat(state, "oil", T, time, form=form, until=until, max_time=max_time)


def poach(state, T, time=None, vinegar_pct=0.0, salt_pct=0.0, until=None, max_time=None):
    """卵を割って湯に落とす（ポーチ）。煮る の特殊化で、割った卵がじかに湯にふれる形（drop）。

    落とした時点の湯温と、湯に入れた酢・塩（湯に対する %）で卵白のまとまりを決める（R-E21, R-E22）:
      湯温 < poach_cohesion_T_min            → ばらける（固まりきらない。酢・塩があっても、推定）
      酢か塩がある                           → まとまる（表面に膜・ちぎれ）
      沸騰（boiling_point_water 以上）        → ばらける（対流で卵白がちぎれる）
      それ以外                               → まとまる
    """
    T_eff = min(T, P.H("run", "boiling_point_water"))
    decide = state.has(*EGG_KEYS) and state.egg_form == EGG_CRACKED and state.egg_white_cohesion is None
    s = heat(state, "water", T, time, form="drop", until=until, max_time=max_time)
    s.ops[-1] = s.ops[-1].replace("heat(water,", f"poach(酢{vinegar_pct}%,塩{salt_pct}%,", 1)
    if decide:
        additive = (vinegar_pct or 0) > 0 or (salt_pct or 0) > 0
        if T_eff < P.V("poach_cohesion_T_min"):
            coh = COH_SCATTER
        elif additive:
            coh = COH_FILM
        elif T_eff >= P.H("run", "boiling_point_water"):
            coh = COH_SCATTER
        else:
            coh = COH_COHESIVE
        s.egg_white_cohesion = coh
        s.log("R-E21/E22", f"卵白のまとまり→{coh}")
    return s


def chill(state, T, time):
    """冷やす（冷蔵庫など）。"""
    s = heat(state, "air", T, time)
    s.ops[-1] = f"chill({T}℃,{time}min)"
    return s


def rest(state, T, time):
    """寝かせる。温度を上げない時間経過。グルテンが緩む（R-G03）。"""
    s = heat(state, "air", T, time)
    s.ops[-1] = f"rest({T}℃,{time}min)"
    if s.gluten and time >= P.V("gluten_relax_min") and not s.gluten_relaxed:
        s.gluten_relaxed = 1
        s.log("R-G03", "グルテンが緩んだ")
    return s


def plunge(state, T, time):
    """水に取る（氷水 0℃・冷水／流水 15℃ など）。媒体は水（殻付き卵では 表面＝水の温度）。余熱を止める手順
    （rules.md §10 2026-09-28 夜「余熱」）。"""
    s = heat(state, "water", T, time)
    s.ops[-1] = f"plunge({T}℃,{time}min)"
    return s


def off_heat(state, T, time):
    """湯に入れたまま火を止める。湯の温度は T から室温（T0_default）へ時定数 pot_cooling_tau_min で下がる（推定、
    卵が湯を冷ます効果は入れない。rules.md §10 2026-09-28 夜「余熱」）。"""
    s = _begin(state, f"off_heat({T}℃,{time}min)")
    T_room = P.H("run", "T0_default")
    tau = P.H("heat_transfer", "pot_cooling_tau_min")
    dt = P.H("run", "dt_min")
    n = max(1, round(time / dt))
    step = time / n
    for i in range(n):
        T_w = T_room + (T - T_room) * math.exp(-(i * step) / tau)
        ctx = Ctx("off_heat", "water", T_w)
        ctx.t_in_op = i * step
        advance(s, ctx, step)
        apply_rules(s, ctx, step)
    return s


def soak(state, T, time):
    """浸す（浸漬）。米の吸水、ゼラチンの膨潤（R-J01）。"""
    s = _begin(state, f"soak({T}℃,{time}min)")
    _run(s, Ctx("soak", "water", T), time)
    return s


def ferment(state, T, time):
    """発酵。酵母が生きていて温度が範囲内なら CO2（R-L02）。"""
    s = heat(state, "air", T, time)
    s.ops[-1] = f"ferment({T}℃,{time}min)"
    lo, hi = P.V("yeast_ferment_T_range")
    if "yeast" in s.masses and s.yeast_alive != YEAST_DEAD and lo <= T <= hi:
        s.yeast_alive = YEAST_ACTIVE
        s.co2 = max(s.co2 or 0, 3)
        s.log("R-L02", "発酵で CO2 co2=3")
    return s


# ----------------------------------------------------------------------
def _add(s: State, add: dict[str, float] | None, T_add: float | None) -> None:
    if not add:
        return
    T_add = P.H("run", "T0_default") if T_add is None else T_add
    m_old = s.mass
    m_new = sum(add.values())
    for k, v in add.items():
        if k not in P.rules()["ingredients"]:
            raise KeyError(f"未知の食材: {k}")
        s.masses[k] = s.masses.get(k, 0.0) + v
    # 比熱を等しいとみなした質量加重平均（推定）
    s.T_core = (s.T_core * m_old + T_add * m_new) / (m_old + m_new)
    s.T_surface = s.T_core
    s._init_components()


def _mix_effects(s: State, strength: str) -> None:
    if s.has(*EGG_KEYS) and s.egg_form != EGG_SHELL and s.egg_form != EGG_BEATEN:
        s.egg_form = EGG_BEATEN
        s.log("R-E19", "卵を溶きほぐした（卵白と卵黄が均一）")
    if "flour" in s.masses:
        water_other = s.liquid_water_g(exclude=("flour",))
        if water_other / s.masses["flour"] >= P.V("gluten_min_water_ratio"):
            g = P.V("gluten_by_strength")[strength]
            if g > (s.gluten or 0):
                s.gluten = g
                s.log("R-G01/G02", f"gluten→{g}（{strength}）")
    if "baking_powder" in s.masses and s.liquid_water_g(exclude=("baking_powder", "flour")) > 0 and (s.co2 or 0) < 1:
        s.co2 = 1
        s.log("R-L01", "ベーキングパウダー第1段 co2=1")


def mix(state: State, add: dict[str, float] | None = None, strength: str = "中",
        time: float = 1.0, T_add: float | None = None) -> State:
    """混ぜる。add で食材を加えてから混ぜる。strength: 弱（さっくり）/中/強。"""
    label = f"mix({strength}{',+' + '+'.join(add) if add else ''})"
    s = _begin(state, label)
    _add(s, add, T_add)
    _mix_effects(s, strength)
    _run(s, Ctx("mix", "none", s.T_core), time)
    return s


def knead(state: State, time: float = 10.0) -> State:
    """こねる。グルテンが強く発達（R-G02）。"""
    s = _begin(state, f"knead({time}min)")
    _mix_effects(s, "強")
    _run(s, Ctx("knead", "none", s.T_core), time)
    return s


def whisk(state: State, time: float, T: float | None = None, add: dict[str, float] | None = None) -> State:
    """撹拌・泡立て。T はボウルの温度（氷水など。省略で品温のまま）。"""
    s = _begin(state, f"whisk({time}min{',' + str(T) + '℃' if T is not None else ''})")
    _add(s, add, None)
    _mix_effects(s, "中")
    T_bath = s.T_core if T is None else T
    temps: list[float] = []
    dt = P.H("run", "dt_min")
    n = max(1, round(time / dt))
    ctx = Ctx("whisk", "bath", T_bath)
    for i in range(n):
        ctx.t_in_op = i * (time / n)
        advance(s, ctx, time / n)
        apply_rules(s, ctx, time / n)
        temps.append(s.T_core)
    s.T_whisk = sum(temps) / len(temps)
    _whip_cream(s, time)
    return s


def _whip_cream(s: State, time: float) -> None:
    """生クリームの泡立て（R-D03, R-D04）。"""
    if "heavy_cream" not in s.masses:
        return
    V = P.V
    if s.fat < V("cream_fat_min") or s.T_whisk >= V("butter_liquid_T"):
        return
    s.cream_whisk_min += time
    stage = max([int(k) for k, m in V("cream_foam_minutes").items() if s.cream_whisk_min >= m], default=0)
    lo, hi = V("cream_whip_T_range")
    if not (lo <= s.T_whisk <= hi):
        stage = min(stage, 1)
        s.log("R-D03", f"品温 {s.T_whisk:.1f}℃ は範囲外、泡は粗いまま")
    if stage > (s.foam_stage or 0):
        s.foam_stage = stage
        s.log("R-D03/D04", f"foam_stage→{stage}")
    if s.foam_stage >= 4:
        s.cream_network = FAT_SEPARATED
    elif s.foam_stage >= 2:
        s.cream_network = FAT_NETWORK


OPS = {
    "mix": mix, "whisk": whisk, "knead": knead, "soak": soak, "heat": heat, "bake": bake,
    "steam": steam, "simmer": simmer, "deep_fry": deep_fry, "chill": chill, "rest": rest,
    "ferment": ferment, "poach": poach, "plunge": plunge, "off_heat": off_heat,
}


def apply(state: State, steps: list[tuple[str, dict]]) -> State:
    """操作の並び（レシピ）を順に適用する。"""
    s = state
    for name, kwargs in steps:
        s = OPS[name](s, **kwargs)
    return s

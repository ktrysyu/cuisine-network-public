"""温度の追従と、しきい値・保持時間による状態の変化（規則）。

- 温度: 中心・表面が媒体温度に近づく（ニュートンの冷却則による熱伝達の近似）。
  水がある間、中心は沸点を超えない（R-W01, R-F01）。表面は湿っている間は沸点に縛られる（R-W02）。
- 規則: すべて「到達温度のしきい値」か「ある温度帯にいた時間の合計」で判定する。反応速度論は使わない。
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from . import egg_kinetic as EK
from . import meat_slab as MS
from . import params as P
from .state import (CW_COLLAPSE, CW_FIRM, CW_RAW, CW_SOFT, EGG_BEATEN, EGG_CRACKED, EGG_KEYS, GEL_DEGRADED,
                    GEL_DRY, GEL_GEL, GEL_SOL, GEL_SWELL, MEAT_KEYS, YEAST_DEAD, State)


@dataclass
class Ctx:
    op: str
    medium: str          # pan / air / steam / water / oil / bath（撹拌中のボウル）/ none
    T_medium: float
    stirring: bool = False
    lid: bool = False
    t_in_op: float = 0.0
    flip: bool = True    # Exp-18: 肉片をフライパンで焼く操作のはじめに返すか（前にフライパンの操作があるときだけ）


def _stage(T: float, ths: list[float]) -> int:
    """しきい値の列（昇順）に対して、T が越えた数。"""
    return sum(1 for th in ths if T >= th)


# ----------------------------------------------------------------------
# 殻付き卵: 一様な球の熱伝導（Q6 (a)、rules.md §10 2026-09-28 夜）
#
# 無次元の半径 r（中心 0・表面 1）、時間の尺度 R²/α。表面＝媒体温度 Tb のとき
#   T(r, t) = Tb + Σ_n c_n(t) φ_n(r)、 φ_n(r) = sin(nπr)/(nπr)、 c_n(t) = c_n(0)·exp(−n²π² t/(R²/α))
# 一様な分布 1 は Σ b_n φ_n（b_n = 2(−1)^(n+1)）と展開できるので、媒体温度が Tb→Tm に変わった刻みでは
# 差 (Tb−Tm) を一様な分布として各項に足す（c_n += (Tb−Tm)·b_n）。中心は φ_n(0)=1 なので Tb + Σ c_n。
# 卵白の層（半径 a〜1、a³ = 卵黄の体積割合）の体積平均は Tb + Σ c_n w_n、
#   w_n = 3/((1−a³)·k) · ∫_a^1 r sin(kr) dr（k = nπ）
#
# 余熱（rules.md §10 2026-09-28 夜「余熱」）: 空気中（室温に置く・冷蔵庫・オーブン）では表面から周りへの熱の流れが
# 表面の温度差に比例する条件（ロバン条件、ビオ数 Bi = hR/k）にする。固有関数は同じ形 sin(λr)/(λr) で、
# λ は λ cot λ = 1 − Bi の根（Bi→∞ の 表面＝媒体温度 では λ = nπ）。
# 一様な分布の展開係数 b_n = λ J(λ)/N(λ)、J(λ) = ∫_0^1 r sin(λr) dr、N(λ) = ∫_0^1 sin²(λr) dr（λ=nπ で 2(−1)^(n+1)）。
# 境界条件が変わった刻みでは、今の分布（Σ c_m φ_m(μ) ＋ 一様な差）を新しい固有関数に射影し直す:
#   c'_n = (λ_n/N_n)·[Σ_m (c_m/μ_m)·I(μ_m, λ_n) + (Tb_old − Tb_new)·J(λ_n)]、I(μ,λ) = ∫_0^1 sin(μr) sin(λr) dr
_SPHERE_CACHE: dict = {}


def _robin_roots(bi: float, M: int) -> list[float]:
    """λ cos λ − (1 − Bi) sin λ = 0 の正の根を小さい順に M 個（n 番目は ((n−1)π, nπ) に1つ）。二分法。"""
    out = []
    for n in range(1, M + 1):
        lo = (n - 1) * math.pi if n > 1 else 1e-9
        hi = n * math.pi
        h_lo = lo * math.cos(lo) - (1.0 - bi) * math.sin(lo)
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            h_mid = mid * math.cos(mid) - (1.0 - bi) * math.sin(mid)
            if (h_mid > 0) == (h_lo > 0):
                lo, h_lo = mid, h_mid
            else:
                hi = mid
        out.append(0.5 * (lo + hi))
    return out


def _J(k: float) -> float:
    return math.sin(k) / k ** 2 - math.cos(k) / k


def _N(k: float) -> float:
    return 0.5 - math.sin(2 * k) / (4 * k)


def _I(m: float, k: float) -> float:
    if abs(m - k) < 1e-12:
        return _N(k)
    return math.sin(m - k) / (2 * (m - k)) - math.sin(m + k) / (2 * (m + k))


def _sphere_consts(bi: float | None = None):
    """(b, w, lam, ks)。bi=None は 表面＝媒体温度（Q6 (a) と同じ値）。ks は固有値 λ（lam = λ²/(R²/α)）。"""
    sp = P.H("heat_transfer")["egg_sphere"]
    key = (sp["R2_over_alpha_min"]["value"], sp["yolk_volume_fraction"]["value"], sp["modes"]["value"], bi)
    if key not in _SPHERE_CACHE:
        tau0, fy, M, _ = key
        a = fy ** (1.0 / 3.0)
        ks = [n * math.pi for n in range(1, M + 1)] if bi is None else _robin_roots(bi, M)
        b, w, lam = [], [], []
        for n, k in enumerate(ks, start=1):
            F = lambda r: math.sin(k * r) / k ** 2 - r * math.cos(k * r) / k  # noqa: E731  ∫ r sin(kr) dr
            b.append(2.0 * (-1) ** (n + 1) if bi is None else k * _J(k) / _N(k))
            w.append(3.0 / ((1.0 - a ** 3) * k) * (F(1.0) - F(a)))
            lam.append(k * k / tau0)
        _SPHERE_CACHE[key] = (b, w, lam, ks)
    return _SPHERE_CACHE[key]


def sphere_bc(medium: str):
    """殻付き卵の表面の境界条件。空気はロバン条件（Bi_air）、それ以外（湯・蒸気・水）は 表面＝媒体温度（None）。"""
    if medium == "air":
        return P.H("heat_transfer")["egg_sphere"]["Bi_air"]["value"]
    return None


def sphere_step(s: State, T_med: float, dt: float, slow: float, bi: float | None = None) -> None:
    """殻付き卵の中心 T_core と卵白の層 T_white を dt 分進める。bi は表面の条件（None: 表面＝媒体温度）。"""
    b, w, lam, ks = _sphere_consts(bi)
    if s.sphere_c is None:  # はじめは一様（今の中心の温度）
        s.sphere_Tb = s.T_core
        s.sphere_c = [0.0] * len(b)
        s.sphere_bi = bi
    d = s.sphere_Tb - T_med
    c = s.sphere_c
    if s.sphere_bi != bi:  # 境界条件が変わった: 新しい固有関数に射影し直す
        _, _, _, ms = _sphere_consts(s.sphere_bi)
        new = []
        for k in ks:
            acc = sum(cm / mu * _I(mu, k) for cm, mu in zip(c, ms))
            new.append(k / _N(k) * (acc + d * _J(k)))
        c = s.sphere_c = new
        s.sphere_bi = bi
        for i in range(len(c)):
            c[i] = c[i] * math.exp(-lam[i] * dt / slow)
    else:
        for i in range(len(c)):
            c[i] = (c[i] + d * b[i]) * math.exp(-lam[i] * dt / slow)
    s.sphere_Tb = T_med
    s.T_core = T_med + sum(c)
    s.T_white = T_med + sum(ci * wi for ci, wi in zip(c, w))


# ----------------------------------------------------------------------
# 温度
def advance(s: State, ctx: Ctx, dt: float) -> None:
    ht = P.H("heat_transfer")
    tau = ht["tau_min"][s.form]["value"]
    if ctx.medium == "air":
        tau *= ht["air_tau_factor"]["value"]
    T_med = ctx.T_medium
    if ctx.medium in ("water", "steam"):
        T_med = min(T_med, P.H("run", "boiling_point_water"))  # R-W01
    bp = s.boiling_point()

    # 中心: 媒体温度に向かって近づき、水がある間は沸点で止まる
    T_eq = T_med if bp is None else min(T_med, bp)
    if s.T_white is not None and EK.model() == "kinetic":
        # 殻付き卵（Exp-17）: 2層の球の差分と変性の一次反応。空気はロバン条件（h_air）
        if s.egg_kin is None:
            m = sum(s.masses.get(k, 0) for k in EGG_KEYS)
            s.egg_kin = EK.EggGrid(m if m <= 80 else 60.0, s.T_core)
        g = s.egg_kin
        g.step(T_med, dt, EK.h_air() if ctx.medium == "air" else None)
        s.T_core = g.T_center
        s.T_white = g.mean_T("white")
        if bp is not None:
            s.T_core = min(s.T_core, bp)
            s.T_white = min(s.T_white, bp)
    elif s.T_white is not None:
        # 殻付き卵: 球の熱伝導の解で中心と卵白の層を進める（Q6 (a)。修正 B の2つの一次遅れを置き換えた）
        # 空気は air_tau_factor で遅くせず、表面の条件（Bi_air）で表す（余熱、rules.md §10 2026-09-28 夜）
        sphere_step(s, T_med, dt, 1.0, sphere_bc(ctx.medium))
        if bp is not None:
            s.T_core = min(s.T_core, bp)
            s.T_white = min(s.T_white, bp)
    elif s.form == "piece" and s.has(*MEAT_KEYS) and MS.model() == "slab":
        # 肉片（Exp-18）: 厚み方向の1次元の熱伝導。フライパンの操作が変わるたびに返す
        if s.meat_slab is None:
            th = s.thickness_mm if s.thickness_mm is not None else MS.S("thickness_mm")
            meat = {k: m for k, m in s.masses.items() if k in MEAT_KEYS}
            s.meat_slab = MS.MeatSlab(th / 1000.0, MS.mass_fractions(meat), s.T_core)
        sl = s.meat_slab
        if ctx.medium == "pan":
            op = len(s.ops)
            if sl.pan_op is not None and sl.pan_op != op and ctx.flip:
                sl.flip()
                s.log("Exp-18", "肉を返した")
            sl.pan_op = op
        T_bot, h_bot, T_top, h_top = MS.boundary(ctx.medium, T_med, P.H("run", "T0_default"))
        sl.step(dt, T_bot, h_bot, T_top, h_top, bp)
        s.T_core = sl.T_center
    else:
        s.T_core += (T_med - s.T_core) * (1.0 - math.exp(-dt / tau))
        if bp is not None and s.T_core > bp:
            s.T_core = bp

    # 蒸発（沸点に達している間だけ）
    if bp is not None and s.T_core >= bp - 0.5 and T_med >= bp and s.form not in ("shell", "cup", "drop"):
        ev = ht["evaporation_pct_per_min"]
        rate = ev["lid"]["value"] if ctx.lid else (ev["thin"]["value"] if s.form == "thin" else ev["pot"]["value"])
        loss = min(s.nutrient_g("water"), rate / 100.0 * s.mass * dt)
        s.water_lost += loss
        if ctx.medium == "oil" and loss > 0 and P.H("oil_uptake", "enabled"):
            # 吸油（Exp-18）: 蒸発した水に比例して油を吸う（mext2020_tables・gamble1987）
            s.masses["vegetable_oil"] = s.masses.get("vegetable_oil", 0.0) + P.H("oil_uptake", "ratio") * loss
            s.log("Exp-18", "吸油")

    # 表面
    dry_heat = ctx.medium in ("pan", "oil") or (ctx.medium == "air" and T_med > 100)
    if ctx.stirring or not dry_heat:
        # 撹拌し続けると表面は中心と同じ（推定）。湿った媒体・冷却では表面は媒体温度
        s.T_surface = s.T_core if (ctx.stirring or ctx.medium in ("bath", "none")) else T_eq
    else:
        wet_min = ht["surface_wet_min"][ctx.medium]["value"]
        bp_now = s.boiling_point()
        if bp_now is not None and ctx.t_in_op < wet_min:
            s.T_surface = min(T_med, bp_now)  # R-W02
        else:
            ts = ht["tau_surface_min"]["value"]
            s.T_surface += (T_med - s.T_surface) * (1.0 - math.exp(-dt / ts))
    s.record(dt)


# ----------------------------------------------------------------------
# 規則（毎ステップ呼ぶ）
def apply_rules(s: State, ctx: Ctx, dt: float) -> None:
    _egg(s, ctx)
    _dairy(s)
    _starch(s, ctx, dt)
    _leavening(s, ctx)
    _sugar(s)
    _maillard(s)
    _vegetable(s)
    _gelatin(s, ctx, dt)
    _meat(s, ctx)


def _egg(s: State, ctx: Ctx) -> None:
    if not s.has(*EGG_KEYS):
        return
    V = P.V
    # 割った卵（溶いていない）では卵白が外側、卵黄が内側にある。卵白は表面の最高温度、卵黄は中心の最高温度で
    # 段階を決める（推定。オムレツの外側 egg_gel_stage_surface と同じ考え、rules.md §10 2026-09-27 ポーチドエッグ）。
    # 殻付き卵は卵白の層の最高温度で決める（修正 B、rules.md §10 2026-09-28）。溶き卵は中心の最高温度
    if s.egg_form == EGG_CRACKED:
        T_white = s.T_surface_max
    elif s.T_white_max is not None:
        T_white = s.T_white_max
    else:
        T_white = s.T_core_max
    w = _stage(T_white, [V("egg_white_s1"), V("egg_white_s2"), V("egg_white_s3")])
    if s.egg_kin is not None:
        # Exp-17: 殻付き卵は場所ごとの変性度の分布から段階を出す（sim/egg_kinetic.py）
        gw, xw = s.egg_kin.layer_stats("white")
        gy, xy = s.egg_kin.layer_stats("yolk")
        w = EK.stage_from(gw, xw)
        y = EK.stage_from(gy, xy)
        if y == 3 and s.T_core_max < V("egg_yolk_s3"):
            y = 2
        if w > s.egg_white_stage:
            s.egg_white_stage = w
            s.log("Exp-17", f"egg_white_stage→{w}（固まった割合 {gw:.2f}・平均 X {xw:.2f}）")
        if y > s.egg_yolk_stage:
            s.egg_yolk_stage = y
            s.log("Exp-17", f"egg_yolk_stage→{y}（固まった割合 {gy:.2f}・平均 X {xy:.2f}）")
        return
    if w > s.egg_white_stage:
        s.egg_white_stage = w
        s.log("R-E01..03", f"egg_white_stage→{w}")
    y = _stage(s.T_core_max, [V("egg_yolk_s1"), V("egg_yolk_s2"), V("egg_yolk_s3")])
    if y > s.egg_yolk_stage:
        s.egg_yolk_stage = y
        s.log("R-E05..06", f"egg_yolk_stage→{y}")
    if s.egg_form != EGG_BEATEN:
        return
    diluted = s.egg_dilution < V("egg_dilution_boundary")
    if diluted:
        ths = [V("egg_diluted_s1"), V("egg_diluted_s2")]
        rid = "R-E09"
    else:
        ths = [V("egg_undiluted_s1"), V("egg_undiluted_s2"), V("egg_undiluted_s3")]
        rid = "R-E07"
    core = _stage(s.T_core, ths)
    surf = _stage(s.T_surface, ths)
    prev = s.egg_gel_stage or 0
    if core > prev and prev < 4:
        s.egg_gel_stage = core
        s.log(rid, f"egg_gel_stage→{core}（{'薄めた卵液' if diluted else '薄めない卵'}）")
        if ctx.stirring and core >= 1 and not s.curds:
            s.curds = True
            s.log("R-E20", "撹拌しながら固まった→小片（カード）")
    elif s.egg_gel_stage is None:
        s.egg_gel_stage = 0
    if surf > (s.egg_gel_stage_surface or 0):
        s.egg_gel_stage_surface = surf
    elif s.egg_gel_stage_surface is None:
        s.egg_gel_stage_surface = 0
    if diluted and not s.starch_types():  # R-E15 は卵液（でんぷんを含む生地は対象外、推定）
        pT = V("egg_porosity_T")
        if s.T_core >= pT and s.porosity < 1:
            s.porosity = 1
            s.log("R-E15", f"中心 {pT}℃以上→す porosity=1")
        if s.porosity < 2 and s.hold("core", "ge", pT) >= V("egg_porosity_hold2_min"):
            s.porosity = 2
            s.log("R-E15", "す porosity=2")
        if s.porosity >= 1 and (s.egg_gel_stage or 0) >= 2:
            s.egg_gel_stage = 4


def _dairy(s: State) -> None:
    if s.milk_whey_denatured is not None and s.milk_whey_denatured < 1 and s.T_core_max >= P.V("whey_denature_T"):
        s.milk_whey_denatured = 1
        s.log("R-D02", "乳清たんぱく質が変性")
    # ホイップの網目は乳脂肪が融けると壊れる（R-D05 から推定）
    if s.cream_network is not None and s.T_core >= P.V("butter_liquid_T"):
        s.cream_network = None
        s.foam_stage = 0
        s.log("R-D05", "乳脂肪が融けて泡が消えた")


def _starch(s: State, ctx: Ctx, dt: float) -> None:
    types = s.starch_types()
    if not types:
        return
    V = P.V
    water = s.nutrient_g("water")
    total_starch = sum(types.values())
    best = s.starch_gel or 0.0
    if water / total_starch >= V("starch_min_water_ratio"):
        for t in types:
            if t == "rice":
                val = 0.0
                if s.T_core_max >= V("rice_gel_onset"):
                    val = V("starch_partial_value")
                rice = s.masses.get("rice", 0)
                ratio = s.masses.get("water", 0) / rice if rice else 0
                if (s.hold("core", "ge", V("rice_full_T")) >= V("rice_full_min")
                        and ratio >= V("rice_min_water_ratio")):
                    val = V("rice_full_value")
                rid = "R-S04/S07"
            else:
                onset, full = V(f"{t}_gel_onset"), V(f"{t}_gel_complete")
                val = 1.0 if s.T_core_max >= full else (V("starch_partial_value") if s.T_core_max >= onset else 0.0)
                rid = "R-S01" if t == "wheat" else "R-S03"
            if val > best:
                best = val
                s.log(rid, f"starch_gel→{val}")
    s.starch_gel = best
    # 老化（R-S08）
    if best >= V("starch_partial_value"):
        if s.T_core <= V("retro_T"):
            s.retro_min += dt
        st = max([k for k, m in V("retro_min").items() if s.retro_min >= m], default=0)
        if st > s.starch_retro:
            s.starch_retro = st
            s.log("R-S08", f"starch_retro→{st}")


def _leavening(s: State, ctx: Ctx) -> None:
    if "baking_powder" in s.masses and (s.co2 or 0) >= 1 and s.co2 < 2 and s.T_core >= P.V("baking_powder_heat_T"):
        s.co2 = 2
        s.log("R-L01", "ベーキングパウダー第2段 co2=2")
    if "yeast" in s.masses and s.yeast_alive != YEAST_DEAD and s.T_core >= P.V("yeast_death_T"):
        s.yeast_alive = YEAST_DEAD
        s.log("R-L02", "酵母が死滅")


def _sugar(s: State) -> None:
    if s.caramel is None:
        return
    V = P.V
    T = max(s.T_core, s.T_surface)
    st = s.caramel
    if s.sugar_g("sucrose") > 0:
        rs = V("roasted_sugar")
        if st < 1 and s.hold("core", "ge", rs["T"]) >= rs["min"]:
            st = 1
            s.log("R-C04", "ショ糖を長く加熱 caramel=1")
        if T >= V("sucrose_caramel_T") and st < 2:
            st = 2
            s.log("R-C01", f"ショ糖 {V('sucrose_caramel_T')}℃以上 caramel=2")
    if s.sugar_g("glucose") > 0 and T >= V("glucose_caramel_T") and st < 2:
        st = 2
        s.log("R-C02", f"ブドウ糖 {V('glucose_caramel_T')}℃以上 caramel=2")
    if T >= V("caramel_pyrolysis_T") and st < 3:
        st = 3
        s.log("R-C06", "180℃以上 焦げ caramel=3")
    s.caramel = st
    if s.is_syrup():
        ss = _stage(s.T_core_max, V("syrup_stage_T"))
        if ss > (s.syrup_stage or 0):
            s.log("R-C05", f"syrup_stage→{ss}")
        s.syrup_stage = max(ss, s.syrup_stage or 0)


def _maillard(s: State) -> None:
    V = P.V
    if s.protein < V("maillard_min_protein"):
        return
    st = s.maillard
    if st < 1 and s.T_surface >= V("maillard_T"):
        st = 1
    if st < 2 and s.hold("surface", "ge", V("maillard_T")) >= V("maillard_s2_min"):
        st = 2
    if st < 3 and s.hold("surface", "ge", V("maillard_s3_T")) >= V("maillard_s3_min"):
        st = 3
    if st > s.maillard:
        s.maillard = st
        s.log("R-M01", f"maillard→{st}")


def _vegetable(s: State) -> None:
    V = P.V
    if s.onion_sulfur is not None:
        st = s.onion_sulfur
        if st > 1 and s.T_core_max >= V("onion_sulfur_reduce_T"):
            st = 1
        if st > 0 and s.mass_ratio <= V("onion_sulfur_zero_mass_ratio"):
            st = 0
        if st < s.onion_sulfur:
            s.onion_sulfur = st
            s.log("R-O01", f"onion_sulfur→{st}")
    if s.cell_wall is None:
        return
    cw = s.cell_wall
    if cw == CW_RAW and s.hold("core", "band", V("pme_band")) >= V("pme_min"):
        cw = CW_FIRM
        s.log("R-S11", "PME で硬化")
    soft = s.hold("core", "ge", V("soften_T"))
    if cw == CW_RAW and soft >= V("soften_min"):
        cw = CW_SOFT
        s.log("R-S12", "軟化")
    if cw == CW_SOFT and soft >= V("collapse_min"):
        cw = CW_COLLAPSE
        s.log("R-S12", "崩壊")
    s.cell_wall = cw


def _gelatin(s: State, ctx: Ctx, dt: float) -> None:
    if s.gelatin_state is None:
        return
    V = P.V
    g = s.gelatin_state
    if g == GEL_DRY and ctx.op == "soak":
        sw = V("gelatin_swell")
        if sw["T"][0] <= s.T_core <= sw["T"][1]:
            s.gelatin_soak_min += dt
        if s.gelatin_soak_min >= sw["min"]:
            g = GEL_SWELL
            s.log("R-J01", "ゼラチンが膨潤")
    if g == GEL_SWELL and s.T_core >= V("gelatin_dissolve_T"):
        g = GEL_SOL
        s.log("R-J02", "ゼラチンが溶解")
    dd = V("gelatin_direct_dissolve")
    if g == GEL_DRY and s.hold("core", "ge", dd["T"]) >= dd["min"]:
        g = GEL_SOL
        s.log("R-J02", "ゼラチンを直接溶解")
    if g == GEL_SOL:
        if s.T_core <= V("gelatin_gel_T"):
            s.gelatin_cold_min += dt
        if s.gelatin_cold_min >= V("gelatin_gel_min"):
            g = GEL_GEL
            s.log("R-J04/J05", "ゲル化")
    elif g == GEL_GEL and s.T_core >= V("gelatin_melt_T"):
        g = GEL_SOL
        s.gelatin_cold_min = 0.0
        s.log("R-J05", "ゲルが融けた")
    dg = V("gelatin_degrade")
    if g in (GEL_SOL, GEL_GEL) and s.hold("core", "ge", dg["T"]) >= dg["min"]:
        g = GEL_DEGRADED
        s.log("R-J03", "加熱しすぎで劣化")
    s.gelatin_state = g


def _meat(s: State, ctx: Ctx) -> None:
    if not s.has(*MEAT_KEYS):
        return
    V = P.V
    T = s.T_core_max
    upd = {
        "meat_myosin": int(T >= V("myosin_T")),
        "meat_actin": int(T >= V("actin_T")),
        "meat_myoglobin": _stage(T, [V("myoglobin_s1_T"), V("myoglobin_s2_T")]),
        "meat_water_loss": _stage(T, [V("meat_water_loss_T")[1], V("meat_water_loss_T")[2]]),
    }
    col = int(T >= V("collagen_T"))
    cg = V("collagen_gelatinize")
    if col and s.hold("core", "ge", cg["T"]) >= cg["min"]:
        col = 2
    upd["meat_collagen"] = col
    for k, v in upd.items():
        if v > getattr(s, k):
            setattr(s, k, v)
            s.log("R-P01..P04", f"{k}→{v}")

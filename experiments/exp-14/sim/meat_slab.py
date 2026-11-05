"""肉片: 厚み方向の1次元の熱伝導（板）。Exp-18。

計画は experiments/exp-18-more-dishes/plan.md の A。値は rules.yaml の sim.meat_slab（出典つき）。
- 熱物性: 成分（水分・たんぱく質・脂質・炭水化物・灰分）から Choi & Okos (1986) の式で出す
  （ASHRAE 1998 Refrigeration Handbook 8章 表1・2。係数はヤード・ポンド単位のまま rules.yaml に写し、ここで換算）。
  ρ = 1/Σ(xᵢ/ρᵢ)、cp = Σ xᵢ cpᵢ、k = Σ xᵥᵢ kᵢ（並列モデル、xᵥᵢ は体積分率）
- 温度: 有限体積・後退オイラー。両面ともロバン条件（h=None は 表面＝媒体温度）
- 水がある間、各節点は沸点を超えない（R-W01 を節点ごとに当てる。蒸発で失う熱・水の移動は入れない）
既定のモデルは rules.yaml の sim.meat_model（tau のまま）。set_model() で切り替える。
"""
from __future__ import annotations

import math

from . import params as P

K_IP = 1.730735     # Btu/(h·ft·°F) → W/(m·K)
RHO_IP = 16.01846   # lb/ft³ → kg/m³
CP_IP = 4186.8      # Btu/(lb·°F) → J/(kg·K)
COMPONENTS = ("water", "protein", "fat", "carb", "ash")

_OVERRIDE: dict = {}


def set_model(name: str | None) -> None:
    """'tau' / 'slab' / None（rules.yaml の値に戻す）。"""
    if name is None:
        _OVERRIDE.pop("model", None)
    else:
        _OVERRIDE["model"] = name


def model() -> str:
    return _OVERRIDE.get("model") or P.H("meat_model")


def S(key):
    """sim.meat_slab の値。感度用に set_params で差し替えられる。"""
    return _OVERRIDE.get("params", {}).get(key, P.H("meat_slab", key))


def set_params(values: dict | None) -> None:
    if values is None:
        _OVERRIDE.pop("params", None)
    else:
        _OVERRIDE["params"] = dict(values)


# ----------------------------------------------------------------------
def _poly(c, t):
    return sum(ci * t ** i for i, ci in enumerate(c))


def component_props(comp: str, T: float) -> tuple[float, float, float]:
    """成分1つの (k [W/(m·K)], ρ [kg/m³], cp [J/(kg·K)])。T は ℃。"""
    c = P.H("meat_slab", "choi_okos", comp)
    t = 1.8 * T + 32.0
    return _poly(c["k"], t) * K_IP, _poly(c["rho"], t) * RHO_IP, _poly(c["cp"], t) * CP_IP


def mass_fractions(masses: dict[str, float]) -> dict[str, float]:
    """食材の質量と成分表から、成分の質量分率。成分表の 水分・たんぱく質・脂質・炭水化物 の残りを灰分とする。"""
    tot = {c: 0.0 for c in COMPONENTS}
    M = 0.0
    for k, m in masses.items():
        comp = P.composition(k)
        w, p, f, cb = comp["water"], comp["protein"], comp["fat"], comp["carb"]
        tot["water"] += m * w / 100
        tot["protein"] += m * p / 100
        tot["fat"] += m * f / 100
        tot["carb"] += m * cb / 100
        tot["ash"] += m * max(0.0, 100 - w - p - f - cb) / 100
        M += m
    s = sum(tot.values())
    return {c: v / s for c, v in tot.items()} if M > 0 else tot


def mix_props(x: dict[str, float], T: float) -> tuple[float, float, float]:
    """(k, ρ, cp) of the mixture。"""
    pr = {c: component_props(c, T) for c in COMPONENTS}
    inv_rho = sum(x[c] / pr[c][1] for c in COMPONENTS)
    rho = 1.0 / inv_rho
    cp = sum(x[c] * pr[c][2] for c in COMPONENTS)
    k = sum((x[c] / pr[c][1]) / inv_rho * pr[c][0] for c in COMPONENTS)
    return k, rho, cp


class MeatSlab:
    """厚さ L の板。節点 0 が「下の面」（フライパンに触れている面）、n−1 が「上の面」。"""

    def __init__(self, thickness_m: float, fractions: dict[str, float], T0: float, nodes: int | None = None):
        n = int(S("nodes") if nodes is None else nodes)
        self.n = n
        self.L = thickness_m
        self.dx = thickness_m / n
        self.x = fractions
        self.T = [T0] * n
        self.pan_op: int | None = None   # 最後にフライパンに触れていた操作の番号
        self.flips = 0

    def flip(self) -> None:
        self.T.reverse()
        self.flips += 1

    def step(self, dt_min: float, T_bot: float, h_bot: float | None, T_top: float, h_top: float | None,
             T_cap: float | None = None) -> None:
        total = dt_min * 60.0
        sub = float(S("sub_s"))
        nsub = max(1, int(math.ceil(total / sub - 1e-9)))
        dt = total / nsub
        for _ in range(nsub):
            self._conduct(dt, T_bot, h_bot, T_top, h_top)
            if T_cap is not None:
                self.T = [min(t, T_cap) for t in self.T]

    def _conduct(self, dt, T_bot, h_bot, T_top, h_top):
        n, T, dx = self.n, self.T, self.dx
        props = [mix_props(self.x, t) for t in T]
        C = [p[1] * p[2] * dx for p in props]            # 単位面積あたり
        G = [1.0 / (dx / (2 * props[i][0]) + dx / (2 * props[i + 1][0])) for i in range(n - 1)]
        Rb = dx / (2 * props[0][0]) + (0.0 if h_bot is None else 1.0 / h_bot)
        Rt = dx / (2 * props[-1][0]) + (0.0 if h_top is None else 1.0 / h_top)
        Gb, Gt = 1.0 / Rb, 1.0 / Rt
        a = [0.0] * n
        b = [0.0] * n
        c = [0.0] * n
        d = [0.0] * n
        for i in range(n):
            b[i] = C[i] / dt
            d[i] = C[i] / dt * T[i]
            if i > 0:
                a[i] = -G[i - 1]
                b[i] += G[i - 1]
            if i < n - 1:
                c[i] = -G[i]
                b[i] += G[i]
        b[0] += Gb
        d[0] += Gb * T_bot
        b[-1] += Gt
        d[-1] += Gt * T_top
        for i in range(1, n):
            m = a[i] / b[i - 1]
            b[i] -= m * c[i - 1]
            d[i] -= m * d[i - 1]
        xs = [0.0] * n
        xs[-1] = d[-1] / b[-1]
        for i in range(n - 2, -1, -1):
            xs[i] = (d[i] - c[i] * xs[i + 1]) / b[i]
        self.T = xs

    @property
    def T_center(self) -> float:
        n = self.n
        if n % 2:
            return self.T[n // 2]
        return 0.5 * (self.T[n // 2 - 1] + self.T[n // 2])

    @property
    def T_min(self) -> float:
        return min(self.T)


def boundary(medium: str, T_med: float, T_room: float):
    """(T_bot, h_bot, T_top, h_top)。フライパンは下の面だけ鍋に触れる。"""
    if medium == "pan":
        return T_med, S("h_contact"), T_room, S("h_top")
    if medium in ("water", "steam"):
        return T_med, None, T_med, None
    if medium == "oil":
        return T_med, S("h_oil"), T_med, S("h_oil")
    return T_med, S("h_air"), T_med, S("h_air")   # air・bath・none

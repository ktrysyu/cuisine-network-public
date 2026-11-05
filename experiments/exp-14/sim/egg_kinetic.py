"""殻付き卵: 2層の球の熱伝導（差分）と、場所ごとの変性度（一次反応・アレニウス）。Exp-17。

計画は experiments/exp-17-egg-kinetics/plan.md。値は rules.yaml の sim.egg_kinetic（出典つき）。
- 温度: 1次元・球対称の熱伝導を陰解法（後退オイラー）で解く。黄身（中心の球）と白身（外側の層）で
  熱伝導率・密度は温度の関数、比熱は定数（Di Lorenzo et al. 2025 Table 4）
- 変性: dX/dt = A exp(−Ea/RT)(1 − X)。刻みの中では温度を一定とみなし X = 1 − (1 − X)exp(−k dt)
- 段階: 層の体積のうち X ≥ gel_X の割合 g と体積平均 X̄ から（plan.md の 3.）
既定のモデルは rules.yaml の sim.egg_model（2026-09-30 から kinetic）。set_model() で切り替える。
"""
from __future__ import annotations

import math

from . import params as P

R_GAS = 8.314
_OVERRIDE: dict = {}


def set_model(name: str | None) -> None:
    """'stage' / 'kinetic' / None（rules.yaml の値に戻す）。"""
    if name is None:
        _OVERRIDE.pop("model", None)
    else:
        _OVERRIDE["model"] = name


def model() -> str:
    return _OVERRIDE.get("model") or P.H("egg_model")


def K(*path):
    return P.H("egg_kinetic", *path)


def set_params(values: dict | None) -> None:
    """感度用に段階の決め方の値を差し替える（gel_X・stage2_g・stage3_g・stage1_mean）。"""
    if values is None:
        _OVERRIDE.pop("params", None)
    else:
        _OVERRIDE["params"] = dict(values)


def _p(key):
    return _OVERRIDE.get("params", {}).get(key, K("stage_map", key))


# ----------------------------------------------------------------------
def _props(layer, T: float) -> tuple[float, float, float]:
    """(k [W/m/K], ρ [kg/m³], cp [J/kg/K])。T は ℃。layer は層の名前か係数の dict。"""
    c = K(layer) if isinstance(layer, str) else layer
    k = c["k_a"] * T + c["k_b"]
    rho = c["rho_a"] * T * T + c["rho_b"] * T + c["rho_c"]
    return k, rho, c["cp"]


class EggGrid:
    """半径方向の有限体積（節点は各セルの中心、中心は対称）。"""

    def __init__(self, mass_g: float, T0: float, yolk_fraction: float | None = None, radius_m: float | None = None,
                 yolk_radius_m: float | None = None):
        n = int(K("nodes"))
        fy = K("yolk_volume_fraction") if yolk_fraction is None else yolk_fraction
        if radius_m is None:
            rho_y = _props("yolk", 20.0)[1]
            rho_w = _props("white", 20.0)[1]
            rho = fy * rho_y + (1 - fy) * rho_w
            radius_m = (3 * (mass_g / 1000.0) / (4 * math.pi * rho)) ** (1 / 3)
        self.R = radius_m
        self.a = yolk_radius_m if yolk_radius_m is not None else radius_m * fy ** (1 / 3)
        self.n = n
        dr = radius_m / n
        self.dr = dr
        self.r = [(i + 0.5) * dr for i in range(n)]
        self.face = [(i + 1) * dr for i in range(n)]  # 外側の面
        self.vol = [4 / 3 * math.pi * (((i + 1) * dr) ** 3 - (i * dr) ** 3) for i in range(n)]
        self.layer = ["yolk" if self.r[i] < self.a else "white" for i in range(n)]
        self.T = [T0] * n
        self.X = [0.0] * n
        co = {"yolk": K("yolk"), "white": K("white")}
        self.coef = [co[l] for l in self.layer]
        self.lnA = [math.log(float(c["A"])) for c in self.coef]
        self.Ea = [float(c["Ea"]) for c in self.coef]

    # --------------------------------------------------------------
    def step(self, T_med: float, dt_min: float, h: float | None = None, sub_s: float | None = None) -> None:
        """dt_min 分進める。h=None は 表面＝媒体温度（ディリクレ）、数値はロバン条件の熱伝達率 W/(m²·K)。"""
        sub_s = K("sub_s") if sub_s is None else sub_s
        total = dt_min * 60.0
        nsub = max(1, int(math.ceil(total / sub_s)))
        dt = total / nsub
        for _ in range(nsub):
            T_old = self.T[:]
            self._conduct(T_med, dt, h)
            self._react(T_old, dt)

    def _conduct(self, T_med: float, dt: float, h: float | None) -> None:
        n, T = self.n, self.T
        props = [_props(self.coef[i], T[i]) for i in range(n)]
        C = [props[i][1] * props[i][2] * self.vol[i] for i in range(n)]
        # 面の熱コンダクタンス G_i（節点 i と i+1 の間）: 直列の抵抗（球殻）
        G = []
        for i in range(n - 1):
            ri, rf, ro = self.r[i], self.face[i], self.r[i + 1]
            Rth = (1 / ri - 1 / rf) / (4 * math.pi * props[i][0]) + (1 / rf - 1 / ro) / (4 * math.pi * props[i + 1][0])
            G.append(1.0 / Rth)
        # 表面: 最外の節点から表面まで＋（ロバンなら）表面から媒体まで
        ri, Rs = self.r[-1], self.R
        Rcond = (1 / ri - 1 / Rs) / (4 * math.pi * props[-1][0])
        Rconv = 0.0 if h is None else 1.0 / (h * 4 * math.pi * Rs * Rs)
        Gs = 1.0 / (Rcond + Rconv)
        # 後退オイラー: C_i (T_i' − T_i)/dt = G_{i−1}(T_{i−1}' − T_i') + G_i(T_{i+1}' − T_i') (+ Gs(T_med − T_n'))
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
        b[-1] += Gs
        d[-1] += Gs * T_med
        # Thomas
        for i in range(1, n):
            m = a[i] / b[i - 1]
            b[i] -= m * c[i - 1]
            d[i] -= m * d[i - 1]
        x = [0.0] * n
        x[-1] = d[-1] / b[-1]
        for i in range(n - 2, -1, -1):
            x[i] = (d[i] - c[i] * x[i + 1]) / b[i]
        self.T = x

    def _react(self, T_old: list[float], dt: float) -> None:
        for i in range(self.n):
            Tk = 0.5 * (T_old[i] + self.T[i]) + 273.15
            k = math.exp(self.lnA[i] - self.Ea[i] / (R_GAS * Tk))
            self.X[i] = 1.0 - (1.0 - self.X[i]) * math.exp(-k * dt)

    # --------------------------------------------------------------
    def layer_stats(self, layer: str, gel_X: float | None = None) -> tuple[float, float]:
        """(g: X ≥ gel_X の体積割合, X̄: 体積平均)。"""
        gel_X = _p("gel_X") if gel_X is None else gel_X
        idx = [i for i in range(self.n) if self.layer[i] == layer]
        V = sum(self.vol[i] for i in idx)
        g = sum(self.vol[i] for i in idx if self.X[i] >= gel_X) / V
        xm = sum(self.vol[i] * self.X[i] for i in idx) / V
        return g, xm

    def mean_T(self, layer: str) -> float:
        idx = [i for i in range(self.n) if self.layer[i] == layer]
        return sum(self.vol[i] * self.T[i] for i in idx) / sum(self.vol[i] for i in idx)

    @property
    def T_center(self) -> float:
        # 中心の節点は半径 dr/2。中心そのものはその値で近似する
        return self.T[0]

    @property
    def T_surface(self) -> float:
        return self.T[-1]


def stage_from(g: float, xm: float) -> int:
    if g >= _p("stage3_g"):
        return 3
    if g >= _p("stage2_g"):
        return 2
    if xm >= _p("stage1_mean"):
        return 1
    return 0


def h_air() -> float:
    return K("h_air")

"""状態: 材料の混合物と、物理・化学の状態変数（rules.yaml の state_variables）。

操作は State を受け取り、コピーを変えて新しい State を返す（入力は変えない）。
組成（水分・脂質・糖 など）は食材の質量と成分表から毎回計算する。
段階（凝固・糊化・褐変 など）は、到達温度と温度履歴から規則で進める（戻らないものは max で持つ）。
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

from . import params as P

EGG_KEYS = ("egg_whole", "egg_white", "egg_yolk")
MEAT_KEYS = ("chicken", "beef")
VEG_KEYS = ("onion", "potato", "tomato")

# カテゴリの表記は rules.yaml の levels をそのまま使う
GEL_NONE, GEL_CONT, GEL_CURD, GEL_SHELL = P.levels("gel_structure")
FAT_SOLID, FAT_PLASTIC, FAT_LIQUID, FAT_EMULSION, FAT_NETWORK, FAT_SEPARATED = P.levels("fat_phase")
CASEIN_DISP, CASEIN_AGG = P.levels("milk_casein")
CW_RAW, CW_FIRM, CW_SOFT, CW_COLLAPSE = P.levels("cell_wall")
GEL_DRY, GEL_SWELL, GEL_SOL, GEL_GEL, GEL_DEGRADED = P.levels("gelatin_state")
YEAST_ACTIVE, YEAST_DORMANT, YEAST_DEAD = P.levels("yeast_alive")
COH_SCATTER, COH_FILM, COH_COHESIVE = P.H("added_state_variables", "egg_white_cohesion", "levels")

EGG_SHELL = "殻付き"
EGG_CRACKED = "割った"
EGG_BEATEN = "溶き卵"

LAYER_INDEX = {"core": 1, "surface": 2, "white": 3}  # history の列


def _cmp(value: float, how: str, th) -> bool:
    if how == "ge":
        return value >= th
    if how == "le":
        return value <= th
    if how == "band":
        return th[0] <= value <= th[1]
    raise ValueError(how)


@dataclass
class State:
    masses: dict[str, float]
    T_core: float
    T_surface: float
    form: str = "pot"
    egg_form: str | None = None
    water_lost: float = 0.0
    T_core_max: float = -99.0
    T_surface_max: float = -99.0
    history: list[tuple] = field(default_factory=list)  # (dt, T_core, T_surface, T_white)
    # 殻付き卵の卵白の層の温度（修正 B、2026-09-28）。殻付き卵以外は None
    T_white: float | None = None
    T_white_max: float | None = None
    # 殻付き卵の球の熱伝導の解（Q6 (a)、2026-09-28 夜）: 境界（媒体）の温度と、固有関数の各項の係数。physics.sphere_step
    sphere_Tb: float | None = None
    sphere_c: list | None = None
    sphere_bi: float | None = None  # 今の表面の条件（None: 表面＝媒体温度、数値: ロバン条件のビオ数。余熱 2026-09-28 夜）
    holds: dict = field(default_factory=dict)
    egg_kin: object | None = None  # Exp-17: 殻付き卵の差分の格子（egg_model = kinetic のときだけ）
    thickness_mm: float | None = None  # Exp-18: 肉片の厚さ（meat_model = slab のときだけ使う。None は meat_slab.thickness_mm）
    meat_slab: object | None = None  # Exp-18: 肉片の板の格子（meat_model = slab のときだけ）
    # 段階（None は「その成分がない」）
    egg_white_stage: int | None = None
    egg_yolk_stage: int | None = None
    egg_gel_stage: int | None = None
    egg_gel_stage_surface: int | None = None
    curds: bool = False
    porosity: int | None = None
    milk_whey_denatured: int | None = None
    starch_gel: float | None = None
    starch_retro: int | None = None
    retro_min: float = 0.0
    gluten: int | None = None
    gluten_relaxed: int | None = None
    co2: int | None = None
    yeast_alive: str | None = None
    maillard: int = 0
    caramel: int | None = None
    syrup_stage: int | None = None
    onion_sulfur: int | None = None
    cell_wall: str | None = None
    meat_myosin: int | None = None
    meat_actin: int | None = None
    meat_collagen: int | None = None
    meat_myoglobin: int | None = None
    meat_water_loss: int | None = None
    gelatin_state: str | None = None
    gelatin_soak_min: float = 0.0
    gelatin_cold_min: float = 0.0
    foam_stage: int | None = None
    cream_whisk_min: float = 0.0
    cream_network: str | None = None  # None / 部分合一ネットワーク / 分離
    T_whisk: float | None = None
    egg_white_cohesion: str | None = None  # 割って湯に落とした卵だけ（R-E21, R-E22）
    ops: list[str] = field(default_factory=list)
    stops: list[dict] = field(default_factory=list)  # 停止条件つき加熱の結果（到達したか・何分か）
    trace: list[str] = field(default_factory=list)  # 発火した規則（op番号: 規則id 内容）

    # ------------------------------------------------------------------
    @classmethod
    def from_ingredients(cls, ingredients: dict[str, float], T0: float | None = None,
                         egg_form: str | None = None, form: str = "pot",
                         thickness_mm: float | None = None) -> "State":
        T0 = P.H("run", "T0_default") if T0 is None else T0
        known = P.rules()["ingredients"]
        for k in ingredients:
            if k not in known:
                raise KeyError(f"未知の食材: {k}")
        s = cls(masses={k: float(v) for k, v in ingredients.items() if v > 0},
                T_core=T0, T_surface=T0, form=form, thickness_mm=thickness_mm)
        s.T_core_max = T0
        s.T_surface_max = T0
        s._init_components(egg_form)
        return s

    def _init_components(self, egg_form: str | None = None) -> None:
        """食材があれば、その成分の段階を 0（生）で持つ。追加時にも呼ぶ。"""
        m = self.masses
        if self.has(*EGG_KEYS):
            if self.egg_form is None:
                self.egg_form = egg_form or EGG_CRACKED
            self.egg_white_stage = self.egg_white_stage or 0
            self.egg_yolk_stage = self.egg_yolk_stage or 0
            self.porosity = self.porosity or 0
            if self.egg_form == EGG_SHELL and self.T_white is None:
                self.T_white = self.T_core
                self.T_white_max = self.T_core
        if self.has("milk", "heavy_cream"):
            self.milk_whey_denatured = self.milk_whey_denatured or 0
        if self.starch_types():
            self.starch_gel = self.starch_gel or 0.0
            self.starch_retro = self.starch_retro or 0
        if "flour" in m:
            self.gluten = self.gluten or 0
            self.gluten_relaxed = self.gluten_relaxed or 0
        if self.has("baking_powder", "yeast"):
            self.co2 = self.co2 or 0
        if "yeast" in m and self.yeast_alive is None:
            self.yeast_alive = YEAST_DORMANT
        if self.sugar_g("sucrose") > 0 or self.sugar_g("glucose") > 0:
            self.caramel = self.caramel or 0
        if "onion" in m and self.onion_sulfur is None:
            self.onion_sulfur = 2
        if self.has(*VEG_KEYS) and self.cell_wall is None:
            self.cell_wall = CW_RAW
        if self.has(*MEAT_KEYS):
            for k in ("meat_myosin", "meat_actin", "meat_collagen", "meat_myoglobin", "meat_water_loss"):
                if getattr(self, k) is None:
                    setattr(self, k, 0)
        if "gelatin" in m and self.gelatin_state is None:
            self.gelatin_state = GEL_DRY
        if "heavy_cream" in m and self.foam_stage is None:
            self.foam_stage = 0

    def copy(self) -> "State":
        return copy.deepcopy(self)

    # ------------------------------------------------------------------
    # 組成
    def has(self, *keys: str) -> bool:
        return any(self.masses.get(k, 0) > 0 for k in keys)

    @property
    def mass_input(self) -> float:
        return sum(self.masses.values())

    @property
    def mass(self) -> float:
        return self.mass_input - self.water_lost

    def nutrient_g(self, key: str) -> float:
        g = sum(m * P.composition(k)[key] / 100.0 for k, m in self.masses.items())
        if key == "water":
            g -= self.water_lost
        return max(g, 0.0)

    def per100(self, key: str) -> float:
        return 100.0 * self.nutrient_g(key) / self.mass if self.mass > 0 else 0.0

    def sugar_g(self, kind: str | None = None) -> float:
        total = 0.0
        for k, m in self.masses.items():
            for sk, v in P.split(k).items():
                if sk in ("sucrose", "lactose", "glucose") and (kind is None or kind == sk):
                    total += m * v / 100.0
        return total

    def starch_types(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for k, m in self.masses.items():
            sp = P.split(k)
            if "starch" in sp:
                out[sp["starch_type"]] = out.get(sp["starch_type"], 0.0) + m * sp["starch"] / 100.0
        return out

    def liquid_water_g(self, exclude: tuple[str, ...] = ()) -> float:
        """exclude 以外の食材から来る水（g）。"""
        return sum(m * P.composition(k)["water"] / 100.0
                   for k, m in self.masses.items() if k not in exclude) - self.water_lost

    def boiling_point(self) -> float | None:
        """水がある間は沸点（糖液では濃度で上がる、R-C05）。水が無ければ None。"""
        w = self.nutrient_g("water")
        if w <= 1e-6:
            return None
        sugar = self.sugar_g("sucrose")
        conc = 100.0 * sugar / (sugar + w)
        table = P.V("syrup_boiling_point")
        for (c0, t0), (c1, t1) in zip(table, table[1:]):
            if c0 <= conc <= c1:
                return t0 + (t1 - t0) * (conc - c0) / (c1 - c0)
        return table[-1][1]

    def is_syrup(self) -> bool:
        sucrose = self.sugar_g("sucrose")
        if sucrose <= 0:
            return False
        return (sucrose + self.nutrient_g("water")) / self.mass >= P.V("syrup_min_fraction")

    # ------------------------------------------------------------------
    # 温度履歴（温度帯ごとの保持時間）
    def hold(self, which: str, how: str, th) -> float:
        """中心（core）・表面（surface）・卵白の層（white、殻付き卵だけ）が条件を満たしていた時間の合計（分）。"""
        th_key = tuple(th) if isinstance(th, list) else th
        key = (which, how, th_key)
        if key not in self.holds:
            idx = LAYER_INDEX[which]
            self.holds[key] = sum(h[0] for h in self.history if h[idx] is not None and _cmp(h[idx], how, th_key))
        return self.holds[key]

    def record(self, dt: float) -> None:
        self.history.append((dt, self.T_core, self.T_surface, self.T_white))
        for (which, how, th) in self.holds:
            v = (self.T_core, self.T_surface, self.T_white)[LAYER_INDEX[which] - 1]
            if v is not None and _cmp(v, how, th):
                self.holds[(which, how, th)] += dt
        self.T_core_max = max(self.T_core_max, self.T_core)
        self.T_surface_max = max(self.T_surface_max, self.T_surface)
        if self.T_white is not None:
            self.T_white_max = max(self.T_white_max, self.T_white)

    def log(self, rule: str, msg: str) -> None:
        entry = f"{len(self.ops)}:{self.ops[-1] if self.ops else 'init'} {rule} {msg}"
        if not self.trace or self.trace[-1] != entry:
            self.trace.append(entry)

    # ------------------------------------------------------------------
    # 判定から参照する状態変数
    @property
    def water(self) -> float:
        return self.per100("water")

    @property
    def fat(self) -> float:
        return self.per100("fat")

    @property
    def protein(self) -> float:
        return self.per100("protein")

    @property
    def salt_conc(self) -> float:
        return self.per100("salt")

    @property
    def sugar_conc(self) -> float:
        return 100.0 * self.sugar_g() / self.mass if self.mass > 0 else 0.0

    @property
    def sugar_conc_ratio(self) -> float | None:
        """重量あたりの糖濃度が、水が飛ぶ前の何倍か（糖の総量は変えない、R-O02）。"""
        if self.sugar_g() <= 0:
            return None
        return self.mass_input / self.mass

    @property
    def mass_ratio(self) -> float:
        base = sum(m for k, m in self.masses.items() if k not in P.H("composition_split", "added_water"))
        return self.mass / base if base > 0 else 0.0

    @property
    def egg_dilution(self) -> float | None:
        eggs = sum(self.masses.get(k, 0) for k in EGG_KEYS)
        if eggs <= 0:
            return None
        return 100.0 * eggs / self.mass_input

    @property
    def gelatin_conc(self) -> float | None:
        if "gelatin" not in self.masses:
            return None
        return 100.0 * self.masses["gelatin"] / self.mass

    @property
    def T_serve(self) -> float:
        return self.T_core

    @property
    def milk_casein(self) -> str | None:
        milk = self.masses.get("milk", 0) + self.masses.get("heavy_cream", 0)
        if milk <= 0:
            return None
        acid = sum(self.masses.get(k, 0) for k in P.H("composition_split", "acids"))
        return CASEIN_AGG if acid / milk >= P.V("acid_to_milk_ratio") else CASEIN_DISP

    @property
    def fat_phase(self) -> str | None:
        if self.cream_network is not None:
            return self.cream_network
        if "butter" in self.masses:
            if self.T_core < P.V("butter_plastic_T"):
                return FAT_SOLID
            if self.T_core < P.V("butter_liquid_T"):
                return FAT_PLASTIC
            return FAT_LIQUID
        if "vegetable_oil" in self.masses:
            return FAT_LIQUID
        if self.has("milk", "heavy_cream", "egg_whole", "egg_yolk"):
            return FAT_EMULSION
        return None

    @property
    def gel_structure(self) -> str | None:
        if not self.has(*EGG_KEYS):
            return None
        if self.egg_form != EGG_BEATEN:
            return GEL_NONE
        if self.curds:
            return GEL_CURD
        if (self.egg_gel_stage or 0) >= 2:
            return GEL_CONT
        if (self.egg_gel_stage_surface or 0) >= 2:
            return GEL_SHELL
        return GEL_NONE

    @property
    def air(self) -> bool:
        return (self.foam_stage or 0) >= 1 or (self.co2 or 0) >= 2

    def get(self, var: str):
        return getattr(self, var, None)

    def summary(self) -> dict:
        keys = ["T_core_max", "T_surface_max", "T_white_max", "T_serve", "water", "fat", "sugar_conc", "salt_conc",
                "mass_ratio", "egg_form", "egg_dilution", "egg_white_stage", "egg_yolk_stage",
                "egg_gel_stage", "egg_gel_stage_surface", "gel_structure", "porosity",
                "milk_whey_denatured", "milk_casein", "fat_phase", "starch_gel", "starch_retro",
                "gluten", "co2", "maillard", "caramel", "syrup_stage", "onion_sulfur", "cell_wall",
                "meat_myosin", "meat_actin", "meat_myoglobin", "meat_water_loss", "gelatin_state",
                "gelatin_conc", "foam_stage", "T_whisk", "air", "egg_white_cohesion"]
        out = {}
        for k in keys:
            v = self.get(k)
            if v is None:
                continue
            out[k] = round(v, 2) if isinstance(v, float) else v
        return out

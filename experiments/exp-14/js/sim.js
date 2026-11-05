/* Exp-14 調理の計算: sim/（state.py・physics.py・ops.py・judge.py）と perception.py の JavaScript 移植。
 *
 * - 数値は rules.yaml から書き出した sim_data.json（CookSim.setData で渡す）だけを使う。ここに数値を直書きしない
 * - Python 版と同じ順に同じ計算をする（足し算の順・刻みの数・四捨五入の規則まで）。一致は test_parity.js で確かめる
 * - ブラウザでは window.CookSim、node では module.exports
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.CookSim = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  let D = null;
  let LV = null;

  function setData(d) {
    D = d;
    const L = d.levels;
    LV = {
      gel: L.gel_structure, fat: L.fat_phase, casein: L.milk_casein, cw: L.cell_wall,
      gelatin: L.gelatin_state, yeast: L.yeast_alive, coh: L.egg_white_cohesion,
    };
  }

  const V = (k) => {
    if (!(k in D.adopted)) throw new Error("採用値がない: " + k);
    return D.adopted[k];
  };
  const comp = (k) => D.ingredients[k].comp;
  const split = (k) => {
    const s = D.split[k];
    return s && !Array.isArray(s) ? s : {};
  };

  const EGG_KEYS = ["egg_whole", "egg_white", "egg_yolk"];
  const MEAT_KEYS = ["chicken", "beef"];
  const VEG_KEYS = ["onion", "potato", "tomato"];
  const EGG_SHELL = "殻付き", EGG_CRACKED = "割った", EGG_BEATEN = "溶き卵";
  const LAYER_INDEX = { core: 1, surface: 2, white: 3 }; // history の列
  const NO_MATCH = "該当なし";

  // Python の round（偶数への丸め）
  function pyRound(x) {
    const f = Math.floor(x), d = x - f;
    if (d > 0.5) return f + 1;
    if (d < 0.5) return f;
    return f % 2 === 0 ? f : f + 1;
  }
  const sum = (arr) => arr.reduce((a, b) => a + b, 0);
  const has = (s, ...keys) => keys.some((k) => (s.masses[k] || 0) > 0);

  function cmp(v, how, th) {
    if (how === "ge") return v >= th;
    if (how === "le") return v <= th;
    if (how === "band") return th[0] <= v && v <= th[1];
    throw new Error(how);
  }
  function stage(T, ths) {
    let n = 0;
    for (const th of ths) if (T >= th) n++;
    return n;
  }
  const intKeys = (obj) => Object.keys(obj).map((k) => [parseInt(k, 10), obj[k]]);

  // ------------------------------------------------------------------
  // 状態
  function newState(ingredients, T0, eggForm, form) {
    T0 = T0 == null ? D.run.T0_default : T0;
    const masses = {};
    for (const [k, v] of Object.entries(ingredients)) {
      if (!(k in D.ingredients)) throw new Error("未知の食材: " + k);
      if (v > 0) masses[k] = Number(v);
    }
    const s = {
      masses, T_core: T0, T_surface: T0, form: form || "pot", egg_form: null, water_lost: 0,
      T_core_max: T0, T_surface_max: T0, T_white: null, T_white_max: null, sphere_Tb: null, sphere_c: null, sphere_bi: null, egg_kin: null, history: [], holds: {},
      egg_white_stage: null, egg_yolk_stage: null, egg_gel_stage: null, egg_gel_stage_surface: null,
      curds: false, porosity: null, milk_whey_denatured: null, starch_gel: null, starch_retro: null,
      retro_min: 0, gluten: null, gluten_relaxed: null, co2: null, yeast_alive: null, maillard: 0,
      caramel: null, syrup_stage: null, onion_sulfur: null, cell_wall: null, meat_myosin: null,
      meat_actin: null, meat_collagen: null, meat_myoglobin: null, meat_water_loss: null,
      gelatin_state: null, gelatin_soak_min: 0, gelatin_cold_min: 0, foam_stage: null,
      cream_whisk_min: 0, cream_network: null, T_whisk: null, egg_white_cohesion: null, ops: [], stops: [], trace: [],
    };
    initComponents(s, eggForm);
    return s;
  }

  function initComponents(s, eggForm) {
    const m = s.masses;
    if (has(s, ...EGG_KEYS)) {
      if (s.egg_form == null) s.egg_form = eggForm || EGG_CRACKED;
      s.egg_white_stage = s.egg_white_stage || 0;
      s.egg_yolk_stage = s.egg_yolk_stage || 0;
      s.porosity = s.porosity || 0;
      if (s.egg_form === EGG_SHELL && s.T_white == null) { s.T_white = s.T_core; s.T_white_max = s.T_core; }
    }
    if (has(s, "milk", "heavy_cream")) s.milk_whey_denatured = s.milk_whey_denatured || 0;
    if (Object.keys(starchTypes(s)).length) {
      s.starch_gel = s.starch_gel || 0;
      s.starch_retro = s.starch_retro || 0;
    }
    if ("flour" in m) {
      s.gluten = s.gluten || 0;
      s.gluten_relaxed = s.gluten_relaxed || 0;
    }
    if (has(s, "baking_powder", "yeast")) s.co2 = s.co2 || 0;
    if ("yeast" in m && s.yeast_alive == null) s.yeast_alive = LV.yeast[1];
    if (sugarG(s, "sucrose") > 0 || sugarG(s, "glucose") > 0) s.caramel = s.caramel || 0;
    if ("onion" in m && s.onion_sulfur == null) s.onion_sulfur = 2;
    if (has(s, ...VEG_KEYS) && s.cell_wall == null) s.cell_wall = LV.cw[0];
    if (has(s, ...MEAT_KEYS)) {
      for (const k of ["meat_myosin", "meat_actin", "meat_collagen", "meat_myoglobin", "meat_water_loss"])
        if (s[k] == null) s[k] = 0;
    }
    if ("gelatin" in m && s.gelatin_state == null) s.gelatin_state = LV.gelatin[0];
    if ("heavy_cream" in m && s.foam_stage == null) s.foam_stage = 0;
  }

  const copyState = (s) => JSON.parse(JSON.stringify(s));
  // 材料の質量だけで決まる値のキャッシュ（masses の中身は addIngredients でしか変わらず、そこで捨てる）。
  // 計算の式と足し算の順は変えていないので、結果は同じ（速さのためだけ）
  let MEMO = new WeakMap();
  function memo(s, key, f) {
    let m = MEMO.get(s.masses);
    if (!m) { m = {}; MEMO.set(s.masses, m); }
    if (!(key in m)) m[key] = f();
    return m[key];
  }
  const massInput = (s) => memo(s, "massInput", () => sum(Object.values(s.masses)));
  const mass = (s) => massInput(s) - s.water_lost;

  function nutrientG(s, key) {
    let g = memo(s, "n:" + key, () => sum(Object.entries(s.masses).map(([k, m]) => (m * comp(k)[key]) / 100.0)));
    if (key === "water") g -= s.water_lost;
    return Math.max(g, 0.0);
  }
  function per100(s, key) {
    const ms = mass(s);
    return ms > 0 ? (100.0 * nutrientG(s, key)) / ms : 0.0;
  }
  function sugarG(s, kind) {
    return memo(s, "sugar:" + kind, () => sugarG0(s, kind));
  }
  function sugarG0(s, kind) {
    let total = 0.0;
    for (const [k, m] of Object.entries(s.masses))
      for (const [sk, v] of Object.entries(split(k)))
        if ((sk === "sucrose" || sk === "lactose" || sk === "glucose") && (kind == null || kind === sk))
          total += (m * v) / 100.0;
    return total;
  }
  function starchTypes(s) {
    return memo(s, "starch", () => starchTypes0(s));
  }
  function starchTypes0(s) {
    const out = {};
    for (const [k, m] of Object.entries(s.masses)) {
      const sp = split(k);
      if ("starch" in sp) out[sp.starch_type] = (out[sp.starch_type] || 0.0) + (m * sp.starch) / 100.0;
    }
    return out;
  }
  function liquidWaterG(s, exclude) {
    return sum(Object.entries(s.masses).filter(([k]) => !exclude.includes(k))
      .map(([k, m]) => (m * comp(k).water) / 100.0)) - s.water_lost;
  }
  function boilingPoint(s) {
    const w = nutrientG(s, "water");
    if (w <= 1e-6) return null;
    const sugar = sugarG(s, "sucrose");
    const conc = (100.0 * sugar) / (sugar + w);
    const t = V("syrup_boiling_point");
    for (let i = 0; i + 1 < t.length; i++) {
      const [c0, t0] = t[i], [c1, t1] = t[i + 1];
      if (c0 <= conc && conc <= c1) return t0 + ((t1 - t0) * (conc - c0)) / (c1 - c0);
    }
    return t[t.length - 1][1];
  }
  function isSyrup(s) {
    const sucrose = sugarG(s, "sucrose");
    if (sucrose <= 0) return false;
    return (sucrose + nutrientG(s, "water")) / mass(s) >= V("syrup_min_fraction");
  }

  // 温度履歴
  function hold(s, which, how, th) {
    const key = which + "|" + how + "|" + (typeof th === "number" ? th : JSON.stringify(th));
    if (!(key in s.holds)) {
      const idx = LAYER_INDEX[which];
      s.holds[key] = { which, how, th, v: sum(s.history.filter((h) => h[idx] != null && cmp(h[idx], how, th)).map((h) => h[0])) };
    }
    return s.holds[key].v;
  }
  function record(s, dt) {
    s.history.push([dt, s.T_core, s.T_surface, s.T_white]);
    for (const h of Object.values(s.holds)) {
      const v = [s.T_core, s.T_surface, s.T_white][LAYER_INDEX[h.which] - 1];
      if (v != null && cmp(v, h.how, h.th)) h.v += dt;
    }
    s.T_core_max = Math.max(s.T_core_max, s.T_core);
    s.T_surface_max = Math.max(s.T_surface_max, s.T_surface);
    if (s.T_white != null) s.T_white_max = Math.max(s.T_white_max, s.T_white);
  }
  function log(s, rule, msg) {
    const entry = { op: s.ops.length, rule, msg };
    const last = s.trace[s.trace.length - 1];
    if (!last || last.op !== entry.op || last.rule !== rule || last.msg !== msg) s.trace.push(entry);
  }

  // 判定から参照する状態変数（Python の property）
  const PROPS = {
    water: (s) => per100(s, "water"),
    fat: (s) => per100(s, "fat"),
    protein: (s) => per100(s, "protein"),
    salt_conc: (s) => per100(s, "salt"),
    sugar_conc: (s) => { const m = mass(s); return m > 0 ? (100.0 * sugarG(s)) / m : 0.0; },
    sugar_conc_ratio: (s) => (sugarG(s) <= 0 ? null : massInput(s) / mass(s)),
    mass_ratio: (s) => {
      const aw = D.split.added_water;
      const base = sum(Object.entries(s.masses).filter(([k]) => !aw.includes(k)).map(([, m]) => m));
      return base > 0 ? mass(s) / base : 0.0;
    },
    egg_dilution: (s) => {
      const eggs = sum(EGG_KEYS.map((k) => s.masses[k] || 0));
      return eggs <= 0 ? null : (100.0 * eggs) / massInput(s);
    },
    gelatin_conc: (s) => ("gelatin" in s.masses ? (100.0 * s.masses.gelatin) / mass(s) : null),
    T_serve: (s) => s.T_core,
    milk_casein: (s) => {
      const milk = (s.masses.milk || 0) + (s.masses.heavy_cream || 0);
      if (milk <= 0) return null;
      const acid = sum(D.split.acids.map((k) => s.masses[k] || 0));
      return acid / milk >= V("acid_to_milk_ratio") ? LV.casein[1] : LV.casein[0];
    },
    fat_phase: (s) => {
      if (s.cream_network != null) return s.cream_network;
      if ("butter" in s.masses) {
        if (s.T_core < V("butter_plastic_T")) return LV.fat[0];
        if (s.T_core < V("butter_liquid_T")) return LV.fat[1];
        return LV.fat[2];
      }
      if ("vegetable_oil" in s.masses) return LV.fat[2];
      if (has(s, "milk", "heavy_cream", "egg_whole", "egg_yolk")) return LV.fat[3];
      return null;
    },
    gel_structure: (s) => {
      if (!has(s, ...EGG_KEYS)) return null;
      if (s.egg_form !== EGG_BEATEN) return LV.gel[0];
      if (s.curds) return LV.gel[2];
      if ((s.egg_gel_stage || 0) >= 2) return LV.gel[1];
      if ((s.egg_gel_stage_surface || 0) >= 2) return LV.gel[3];
      return LV.gel[0];
    },
    air: (s) => (s.foam_stage || 0) >= 1 || (s.co2 || 0) >= 2,
  };
  function get(s, v) {
    if (v in PROPS) return PROPS[v](s);
    const x = s[v];
    return x === undefined ? null : x;
  }

  // ------------------------------------------------------------------
  // 殻付き卵: 一様な球の熱伝導（physics.sphere_step と同じ。Q6 (a)、rules.md §10 2026-09-28 夜）
  // 余熱（rules.md §10 2026-09-28 夜）: 空気中はロバン条件（Bi_air）。λ は λ cot λ = 1 − Bi の根（physics._robin_roots と同じ二分法）
  const SPHERE_CACHE = {};
  function robinRoots(bi, M) {
    const out = [];
    for (let n = 1; n <= M; n++) {
      let lo = n > 1 ? (n - 1) * Math.PI : 1e-9, hi = n * Math.PI;
      let hLo = lo * Math.cos(lo) - (1.0 - bi) * Math.sin(lo);
      for (let it = 0; it < 100; it++) {
        const mid = 0.5 * (lo + hi);
        const hMid = mid * Math.cos(mid) - (1.0 - bi) * Math.sin(mid);
        if ((hMid > 0) === (hLo > 0)) { lo = mid; hLo = hMid; } else hi = mid;
      }
      out.push(0.5 * (lo + hi));
    }
    return out;
  }
  const sJ = (k) => Math.sin(k) / (k * k) - Math.cos(k) / k;
  const sN = (k) => 0.5 - Math.sin(2 * k) / (4 * k);
  const sI = (m, k) => (Math.abs(m - k) < 1e-12 ? sN(k) : Math.sin(m - k) / (2 * (m - k)) - Math.sin(m + k) / (2 * (m + k)));
  function sphereConstsOf(bi) {
    const sp = D.heat_transfer.egg_sphere;
    const key = [sp.R2_over_alpha_min, sp.yolk_volume_fraction, sp.modes, bi].join("|");
    if (!(key in SPHERE_CACHE)) {
      const tau0 = sp.R2_over_alpha_min, a = Math.pow(sp.yolk_volume_fraction, 1.0 / 3.0), M = sp.modes;
      const ks = [];
      if (bi == null) for (let n = 1; n <= M; n++) ks.push(n * Math.PI);
      else ks.push(...robinRoots(bi, M));
      const b = [], w = [], lam = [];
      ks.forEach((k, idx) => {
        const n = idx + 1;
        const F = (r) => Math.sin(k * r) / (k * k) - (r * Math.cos(k * r)) / k;
        b.push(bi == null ? 2.0 * (n % 2 === 1 ? 1 : -1) : (k * sJ(k)) / sN(k));
        w.push((3.0 / ((1.0 - a ** 3) * k)) * (F(1.0) - F(a)));
        lam.push((k * k) / tau0);
      });
      SPHERE_CACHE[key] = { b, w, lam, ks };
    }
    return SPHERE_CACHE[key];
  }
  const sphereBc = (medium) => (medium === "air" ? D.heat_transfer.egg_sphere.Bi_air : null);

  function sphereStep(s, T_med, dt, slow, bi) {
    if (bi === undefined) bi = null;
    const { b, w, lam, ks } = sphereConstsOf(bi);
    if (s.sphere_c == null) { s.sphere_Tb = s.T_core; s.sphere_c = new Array(b.length).fill(0); s.sphere_bi = bi; }
    if (s.sphere_bi === undefined) s.sphere_bi = null;
    const d = s.sphere_Tb - T_med;
    let c = s.sphere_c;
    let sc = 0, sw = 0;
    if (s.sphere_bi !== bi) {
      const ms = sphereConstsOf(s.sphere_bi).ks;
      const nc = [];
      for (const k of ks) {
        let acc = 0;
        for (let m = 0; m < c.length; m++) acc += (c[m] / ms[m]) * sI(ms[m], k);
        nc.push((k / sN(k)) * (acc + d * sJ(k)));
      }
      c = s.sphere_c = nc;
      s.sphere_bi = bi;
      for (let i = 0; i < c.length; i++) c[i] = c[i] * Math.exp((-lam[i] * dt) / slow);
    } else {
      for (let i = 0; i < c.length; i++) c[i] = (c[i] + d * b[i]) * Math.exp((-lam[i] * dt) / slow);
    }
    for (let i = 0; i < c.length; i++) sc += c[i];
    for (let i = 0; i < c.length; i++) sw += c[i] * w[i];
    s.sphere_Tb = T_med;
    s.T_core = T_med + sc;
    s.T_white = T_med + sw;
  }

  // ------------------------------------------------------------------
  // 殻付き卵: 2層の球の熱伝導（差分）と場所ごとの変性度（sim/egg_kinetic.py と同じ。Exp-17）
  // 格子は状態に入れる（copyState で複製できるよう、配列と数だけ）
  const EK = () => D.egg_kinetic;
  function ekProps(c, T) {
    return [c.k_a * T + c.k_b, c.rho_a * T * T + c.rho_b * T + c.rho_c, c.cp];
  }
  function eggGridNew(mass_g, T0) {
    const K = EK();
    const n = K.nodes, fy = K.yolk_volume_fraction;
    const rho_y = ekProps(K.yolk, 20.0)[1], rho_w = ekProps(K.white, 20.0)[1];
    const rho = fy * rho_y + (1 - fy) * rho_w;
    const R = Math.pow((3 * (mass_g / 1000.0)) / (4 * Math.PI * rho), 1 / 3);
    const a = R * Math.pow(fy, 1 / 3);
    const dr = R / n;
    const r = [], face = [], vol = [], layer = [];
    for (let i = 0; i < n; i++) {
      r.push((i + 0.5) * dr);
      face.push((i + 1) * dr);
      vol.push((4 / 3) * Math.PI * (((i + 1) * dr) ** 3 - (i * dr) ** 3));
    }
    for (let i = 0; i < n; i++) layer.push(r[i] < a ? "yolk" : "white");
    return { R, a, n, dr, r, face, vol, layer, T: new Array(n).fill(T0), X: new Array(n).fill(0.0) };
  }
  function eggGridStep(g, T_med, dt_min, h) {
    const total = dt_min * 60.0;
    const nsub = Math.max(1, Math.ceil(total / EK().sub_s));
    const dt = total / nsub;
    for (let k = 0; k < nsub; k++) {
      const T_old = g.T.slice();
      eggConduct(g, T_med, dt, h);
      eggReact(g, T_old, dt);
    }
  }
  function eggConduct(g, T_med, dt, h) {
    const K = EK(), n = g.n, T = g.T;
    const props = [];
    for (let i = 0; i < n; i++) props.push(ekProps(K[g.layer[i]], T[i]));
    const C = [];
    for (let i = 0; i < n; i++) C.push(props[i][1] * props[i][2] * g.vol[i]);
    const G = [];
    for (let i = 0; i < n - 1; i++) {
      const ri = g.r[i], rf = g.face[i], ro = g.r[i + 1];
      const Rth = (1 / ri - 1 / rf) / (4 * Math.PI * props[i][0]) + (1 / rf - 1 / ro) / (4 * Math.PI * props[i + 1][0]);
      G.push(1.0 / Rth);
    }
    const ri = g.r[n - 1], Rs = g.R;
    const Rcond = (1 / ri - 1 / Rs) / (4 * Math.PI * props[n - 1][0]);
    const Rconv = h == null ? 0.0 : 1.0 / (h * 4 * Math.PI * Rs * Rs);
    const Gs = 1.0 / (Rcond + Rconv);
    const a = new Array(n).fill(0.0), b = new Array(n).fill(0.0), c = new Array(n).fill(0.0), d = new Array(n).fill(0.0);
    for (let i = 0; i < n; i++) {
      b[i] = C[i] / dt;
      d[i] = (C[i] / dt) * T[i];
      if (i > 0) { a[i] = -G[i - 1]; b[i] += G[i - 1]; }
      if (i < n - 1) { c[i] = -G[i]; b[i] += G[i]; }
    }
    b[n - 1] += Gs;
    d[n - 1] += Gs * T_med;
    for (let i = 1; i < n; i++) {
      const m = a[i] / b[i - 1];
      b[i] -= m * c[i - 1];
      d[i] -= m * d[i - 1];
    }
    const x = new Array(n).fill(0.0);
    x[n - 1] = d[n - 1] / b[n - 1];
    for (let i = n - 2; i >= 0; i--) x[i] = (d[i] - c[i] * x[i + 1]) / b[i];
    g.T = x;
  }
  function eggReact(g, T_old, dt) {
    const K = EK();
    for (let i = 0; i < g.n; i++) {
      const co = K[g.layer[i]];
      const Tk = 0.5 * (T_old[i] + g.T[i]) + 273.15;
      const k = Math.exp(Math.log(co.A) - co.Ea / (K.R_gas * Tk));
      g.X[i] = 1.0 - (1.0 - g.X[i]) * Math.exp(-k * dt);
    }
  }
  // (g: X ≥ gel_X の体積割合, X̄: 体積平均)
  function eggLayerStats(g, layer) {
    const gelX = EK().stage_map.gel_X;
    let V = 0, Vg = 0, Xs = 0;
    for (let i = 0; i < g.n; i++) if (g.layer[i] === layer) V += g.vol[i];
    for (let i = 0; i < g.n; i++) if (g.layer[i] === layer && g.X[i] >= gelX) Vg += g.vol[i];
    for (let i = 0; i < g.n; i++) if (g.layer[i] === layer) Xs += g.vol[i] * g.X[i];
    return [Vg / V, Xs / V];
  }
  function eggMeanT(g, layer) {
    let a = 0, v = 0;
    for (let i = 0; i < g.n; i++) if (g.layer[i] === layer) a += g.vol[i] * g.T[i];
    for (let i = 0; i < g.n; i++) if (g.layer[i] === layer) v += g.vol[i];
    return a / v;
  }
  function eggStageFrom(gf, xm) {
    const sm = EK().stage_map;
    if (gf >= sm.stage3_g) return 3;
    if (gf >= sm.stage2_g) return 2;
    if (xm >= sm.stage1_mean) return 1;
    return 0;
  }

  // ------------------------------------------------------------------
  // 温度（physics.advance）
  function advance(s, ctx, dt) {
    const ht = D.heat_transfer;
    let tau = ht.tau_min[s.form];
    if (ctx.medium === "air") tau *= ht.air_tau_factor;
    let T_med = ctx.T_medium;
    if (ctx.medium === "water" || ctx.medium === "steam") T_med = Math.min(T_med, D.run.boiling_point_water);
    const bp = boilingPoint(s);
    const T_eq = bp == null ? T_med : Math.min(T_med, bp);
    if (s.T_white != null && D.egg_model === "kinetic") {
      // 殻付き卵（Exp-17）: 2層の球の差分と変性の一次反応。空気はロバン条件（h_air）
      if (s.egg_kin == null) {
        const m = sum(EGG_KEYS.map((k) => s.masses[k] || 0));
        s.egg_kin = eggGridNew(m <= 80 ? m : 60.0, s.T_core);
      }
      const g = s.egg_kin;
      eggGridStep(g, T_med, dt, ctx.medium === "air" ? EK().h_air : null);
      s.T_core = g.T[0];
      s.T_white = eggMeanT(g, "white");
      if (bp != null) { s.T_core = Math.min(s.T_core, bp); s.T_white = Math.min(s.T_white, bp); }
    } else if (s.T_white != null) {
      // 殻付き卵: 球の熱伝導の解（Q6 (a)。修正 B の2つの一次遅れを置き換えた）
      // 空気は air_tau_factor で遅くせず、表面の条件（Bi_air）で表す（余熱、rules.md §10 2026-09-28 夜）
      sphereStep(s, T_med, dt, 1.0, sphereBc(ctx.medium));
      if (bp != null) { s.T_core = Math.min(s.T_core, bp); s.T_white = Math.min(s.T_white, bp); }
    } else {
      s.T_core += (T_med - s.T_core) * (1.0 - Math.exp(-dt / tau));
      if (bp != null && s.T_core > bp) s.T_core = bp;
    }

    if (bp != null && s.T_core >= bp - 0.5 && T_med >= bp && s.form !== "shell" && s.form !== "cup" && s.form !== "drop") {
      const ev = ht.evaporation_pct_per_min;
      const rate = ctx.lid ? ev.lid : s.form === "thin" ? ev.thin : ev.pot;
      const loss = Math.min(nutrientG(s, "water"), (rate / 100.0) * mass(s) * dt);
      s.water_lost += loss;
    }

    const dry = ctx.medium === "pan" || ctx.medium === "oil" || (ctx.medium === "air" && T_med > 100);
    if (ctx.stirring || !dry) {
      s.T_surface = ctx.stirring || ctx.medium === "bath" || ctx.medium === "none" ? s.T_core : T_eq;
    } else {
      const wet = ht.surface_wet_min[ctx.medium];
      const bpNow = boilingPoint(s);
      if (bpNow != null && ctx.t_in_op < wet) s.T_surface = Math.min(T_med, bpNow);
      else s.T_surface += (T_med - s.T_surface) * (1.0 - Math.exp(-dt / ht.tau_surface_min));
    }
    record(s, dt);
  }

  // 規則（physics.apply_rules）
  function applyRules(s, ctx, dt) {
    egg(s, ctx); dairy(s); starch(s, ctx, dt); leavening(s); sugarRules(s); maillard(s);
    vegetable(s); gelatin(s, ctx, dt); meat(s);
  }

  function egg(s, ctx) {
    if (!has(s, ...EGG_KEYS)) return;
    // 割った卵（溶いていない）は卵白＝表面、殻付き卵は卵白＝卵白の層（修正 B）、卵黄＝中心（physics._egg と同じ）
    const Twhite = s.egg_form === EGG_CRACKED ? s.T_surface_max : s.T_white_max != null ? s.T_white_max : s.T_core_max;
    if (s.egg_kin != null) {
      // Exp-17: 殻付き卵は場所ごとの変性度の分布から段階を出す（physics._egg と同じ）
      const [gw, xw] = eggLayerStats(s.egg_kin, "white");
      const [gy, xy] = eggLayerStats(s.egg_kin, "yolk");
      const we = eggStageFrom(gw, xw);
      let ye = eggStageFrom(gy, xy);
      if (ye === 3 && s.T_core_max < V("egg_yolk_s3")) ye = 2;
      if (we > s.egg_white_stage) { s.egg_white_stage = we; log(s, "Exp-17", `egg_white_stage→${we}（固まった割合 ${gw.toFixed(2)}・平均 X ${xw.toFixed(2)}）`); }
      if (ye > s.egg_yolk_stage) { s.egg_yolk_stage = ye; log(s, "Exp-17", `egg_yolk_stage→${ye}（固まった割合 ${gy.toFixed(2)}・平均 X ${xy.toFixed(2)}）`); }
      return;
    }
    const w = stage(Twhite, [V("egg_white_s1"), V("egg_white_s2"), V("egg_white_s3")]);
    if (w > s.egg_white_stage) { s.egg_white_stage = w; log(s, "R-E01..03", "egg_white_stage→" + w); }
    const y = stage(s.T_core_max, [V("egg_yolk_s1"), V("egg_yolk_s2"), V("egg_yolk_s3")]);
    if (y > s.egg_yolk_stage) { s.egg_yolk_stage = y; log(s, "R-E05..06", "egg_yolk_stage→" + y); }
    if (s.egg_form !== EGG_BEATEN) return;
    const diluted = PROPS.egg_dilution(s) < V("egg_dilution_boundary");
    const ths = diluted ? [V("egg_diluted_s1"), V("egg_diluted_s2")]
      : [V("egg_undiluted_s1"), V("egg_undiluted_s2"), V("egg_undiluted_s3")];
    const rid = diluted ? "R-E09" : "R-E07";
    const core = stage(s.T_core, ths), surf = stage(s.T_surface, ths);
    const prev = s.egg_gel_stage || 0;
    if (core > prev && prev < 4) {
      s.egg_gel_stage = core;
      log(s, rid, "egg_gel_stage→" + core + (diluted ? "（薄めた卵液）" : "（薄めない卵）"));
      if (ctx.stirring && core >= 1 && !s.curds) { s.curds = true; log(s, "R-E20", "撹拌しながら固まった→小片（カード）"); }
    } else if (s.egg_gel_stage == null) s.egg_gel_stage = 0;
    if (surf > (s.egg_gel_stage_surface || 0)) s.egg_gel_stage_surface = surf;
    else if (s.egg_gel_stage_surface == null) s.egg_gel_stage_surface = 0;
    if (diluted && Object.keys(starchTypes(s)).length === 0) {
      const pT = V("egg_porosity_T");
      if (s.T_core >= pT && s.porosity < 1) { s.porosity = 1; log(s, "R-E15", "中心 " + pT + "℃以上→す porosity=1"); }
      if (s.porosity < 2 && hold(s, "core", "ge", pT) >= V("egg_porosity_hold2_min")) { s.porosity = 2; log(s, "R-E15", "す porosity=2"); }
      if (s.porosity >= 1 && (s.egg_gel_stage || 0) >= 2) s.egg_gel_stage = 4;
    }
  }

  function dairy(s) {
    if (s.milk_whey_denatured != null && s.milk_whey_denatured < 1 && s.T_core_max >= V("whey_denature_T")) {
      s.milk_whey_denatured = 1; log(s, "R-D02", "乳清たんぱく質が変性");
    }
    if (s.cream_network != null && s.T_core >= V("butter_liquid_T")) {
      s.cream_network = null; s.foam_stage = 0; log(s, "R-D05", "乳脂肪が融けて泡が消えた");
    }
  }

  function starch(s, ctx, dt) {
    const types = starchTypes(s);
    const names = Object.keys(types);
    if (!names.length) return;
    const water = nutrientG(s, "water");
    const total = sum(Object.values(types));
    let best = s.starch_gel || 0.0;
    if (water / total >= V("starch_min_water_ratio")) {
      for (const t of names) {
        let val, rid;
        if (t === "rice") {
          val = 0.0;
          if (s.T_core_max >= V("rice_gel_onset")) val = V("starch_partial_value");
          const rice = s.masses.rice || 0;
          const ratio = rice ? (s.masses.water || 0) / rice : 0;
          if (hold(s, "core", "ge", V("rice_full_T")) >= V("rice_full_min") && ratio >= V("rice_min_water_ratio"))
            val = V("rice_full_value");
          rid = "R-S04/S07";
        } else {
          const onset = V(t + "_gel_onset"), full = V(t + "_gel_complete");
          val = s.T_core_max >= full ? 1.0 : s.T_core_max >= onset ? V("starch_partial_value") : 0.0;
          rid = t === "wheat" ? "R-S01" : "R-S03";
        }
        if (val > best) { best = val; log(s, rid, "starch_gel→" + val); }
      }
    }
    s.starch_gel = best;
    if (best >= V("starch_partial_value")) {
      if (s.T_core <= V("retro_T")) s.retro_min += dt;
      let st = 0;
      for (const [k, m] of intKeys(V("retro_min"))) if (s.retro_min >= m) st = Math.max(st, k);
      if (st > s.starch_retro) { s.starch_retro = st; log(s, "R-S08", "starch_retro→" + st); }
    }
  }

  function leavening(s) {
    if ("baking_powder" in s.masses && (s.co2 || 0) >= 1 && s.co2 < 2 && s.T_core >= V("baking_powder_heat_T")) {
      s.co2 = 2; log(s, "R-L01", "ベーキングパウダー第2段 co2=2");
    }
    if ("yeast" in s.masses && s.yeast_alive !== LV.yeast[2] && s.T_core >= V("yeast_death_T")) {
      s.yeast_alive = LV.yeast[2]; log(s, "R-L02", "酵母が死滅");
    }
  }

  function sugarRules(s) {
    if (s.caramel == null) return;
    const T = Math.max(s.T_core, s.T_surface);
    let st = s.caramel;
    if (sugarG(s, "sucrose") > 0) {
      const rs = V("roasted_sugar");
      if (st < 1 && hold(s, "core", "ge", rs.T) >= rs.min) { st = 1; log(s, "R-C04", "ショ糖を長く加熱 caramel=1"); }
      if (T >= V("sucrose_caramel_T") && st < 2) { st = 2; log(s, "R-C01", "ショ糖 " + V("sucrose_caramel_T") + "℃以上 caramel=2"); }
    }
    if (sugarG(s, "glucose") > 0 && T >= V("glucose_caramel_T") && st < 2) {
      st = 2; log(s, "R-C02", "ブドウ糖 " + V("glucose_caramel_T") + "℃以上 caramel=2");
    }
    if (T >= V("caramel_pyrolysis_T") && st < 3) { st = 3; log(s, "R-C06", "180℃以上 焦げ caramel=3"); }
    s.caramel = st;
    if (isSyrup(s)) {
      const ss = stage(s.T_core_max, V("syrup_stage_T"));
      if (ss > (s.syrup_stage || 0)) log(s, "R-C05", "syrup_stage→" + ss);
      s.syrup_stage = Math.max(ss, s.syrup_stage || 0);
    }
  }

  function maillard(s) {
    if (PROPS.protein(s) < V("maillard_min_protein")) return;
    let st = s.maillard;
    if (st < 1 && s.T_surface >= V("maillard_T")) st = 1;
    if (st < 2 && hold(s, "surface", "ge", V("maillard_T")) >= V("maillard_s2_min")) st = 2;
    if (st < 3 && hold(s, "surface", "ge", V("maillard_s3_T")) >= V("maillard_s3_min")) st = 3;
    if (st > s.maillard) { s.maillard = st; log(s, "R-M01", "maillard→" + st); }
  }

  function vegetable(s) {
    if (s.onion_sulfur != null) {
      let st = s.onion_sulfur;
      if (st > 1 && s.T_core_max >= V("onion_sulfur_reduce_T")) st = 1;
      if (st > 0 && PROPS.mass_ratio(s) <= V("onion_sulfur_zero_mass_ratio")) st = 0;
      if (st < s.onion_sulfur) { s.onion_sulfur = st; log(s, "R-O01", "onion_sulfur→" + st); }
    }
    if (s.cell_wall == null) return;
    let cw = s.cell_wall;
    if (cw === LV.cw[0] && hold(s, "core", "band", V("pme_band")) >= V("pme_min")) { cw = LV.cw[1]; log(s, "R-S11", "PME で硬化"); }
    const soft = hold(s, "core", "ge", V("soften_T"));
    if (cw === LV.cw[0] && soft >= V("soften_min")) { cw = LV.cw[2]; log(s, "R-S12", "軟化"); }
    if (cw === LV.cw[2] && soft >= V("collapse_min")) { cw = LV.cw[3]; log(s, "R-S12", "崩壊"); }
    s.cell_wall = cw;
  }

  function gelatin(s, ctx, dt) {
    if (s.gelatin_state == null) return;
    const [DRY, SWELL, SOL, GEL, DEG] = LV.gelatin;
    let g = s.gelatin_state;
    if (g === DRY && ctx.op === "soak") {
      const sw = V("gelatin_swell");
      if (sw.T[0] <= s.T_core && s.T_core <= sw.T[1]) s.gelatin_soak_min += dt;
      if (s.gelatin_soak_min >= sw.min) { g = SWELL; log(s, "R-J01", "ゼラチンが膨潤"); }
    }
    if (g === SWELL && s.T_core >= V("gelatin_dissolve_T")) { g = SOL; log(s, "R-J02", "ゼラチンが溶解"); }
    const dd = V("gelatin_direct_dissolve");
    if (g === DRY && hold(s, "core", "ge", dd.T) >= dd.min) { g = SOL; log(s, "R-J02", "ゼラチンを直接溶解"); }
    if (g === SOL) {
      if (s.T_core <= V("gelatin_gel_T")) s.gelatin_cold_min += dt;
      if (s.gelatin_cold_min >= V("gelatin_gel_min")) { g = GEL; log(s, "R-J04/J05", "ゲル化"); }
    } else if (g === GEL && s.T_core >= V("gelatin_melt_T")) {
      g = SOL; s.gelatin_cold_min = 0.0; log(s, "R-J05", "ゲルが融けた");
    }
    const dg = V("gelatin_degrade");
    if ((g === SOL || g === GEL) && hold(s, "core", "ge", dg.T) >= dg.min) { g = DEG; log(s, "R-J03", "加熱しすぎで劣化"); }
    s.gelatin_state = g;
  }

  function meat(s) {
    if (!has(s, ...MEAT_KEYS)) return;
    const T = s.T_core_max;
    const wl = V("meat_water_loss_T");
    const upd = {
      meat_myosin: T >= V("myosin_T") ? 1 : 0,
      meat_actin: T >= V("actin_T") ? 1 : 0,
      meat_myoglobin: stage(T, [V("myoglobin_s1_T"), V("myoglobin_s2_T")]),
      meat_water_loss: stage(T, [wl[1], wl[2]]),
    };
    let col = T >= V("collagen_T") ? 1 : 0;
    const cg = V("collagen_gelatinize");
    if (col && hold(s, "core", "ge", cg.T) >= cg.min) col = 2;
    upd.meat_collagen = col;
    for (const [k, v] of Object.entries(upd)) if (v > s[k]) { s[k] = v; log(s, "R-P01..P04", k + "→" + v); }
  }

  // ------------------------------------------------------------------
  // 操作（ops.py）
  const MEDIA = ["pan", "air", "steam", "water", "oil"];
  const ctxOf = (op, medium, T, o = {}) => ({ op, medium, T_medium: T, stirring: !!o.stirring, lid: !!o.lid, t_in_op: 0 });

  function runSteps(s, ctx, time, until) {
    const dt = D.run.dt_min;
    const n = Math.max(1, pyRound(time / dt));
    const step = time / n;
    for (let i = 0; i < n; i++) {
      ctx.t_in_op = i * step;
      advance(s, ctx, step);
      applyRules(s, ctx, step);
      if (until && untilMet(s, until)) return (i + 1) * step;
    }
    return n * step;
  }

  function untilText(c) {
    if ("ge" in c) return c.var + "≧" + c.ge;
    if ("le" in c) return c.var + "≦" + c.le;
    if ("in" in c) return c.var + "∈{" + c.in.join(", ") + "}";
    throw new Error("停止条件の形が不明");
  }
  function untilMet(s, c) {
    const v = get(s, c.var);
    if (v == null) return false;
    if ("ge" in c) return typeof v !== "string" && v >= c.ge;
    if ("le" in c) return typeof v !== "string" && v <= c.le;
    if ("in" in c) return c.in.includes(v);
    throw new Error("停止条件の形が不明");
  }
  function begin(state, label) {
    const s = copyState(state);
    s.ops.push(label);
    return s;
  }

  function heat(state, kw) {
    const { medium, T, time = null, stirring = false, lid = false, form = null, until = null, max_time = null } = kw;
    if (!MEDIA.includes(medium)) throw new Error("未知の媒体: " + medium);
    const tail = (stirring ? ",撹拌" : "") + (lid ? ",蓋" : "");
    if (until == null) {
      if (time == null) throw new Error("time か until のどちらかを指定する");
      const s = begin(state, `heat(${medium},${T}℃,${time}min${tail})`);
      if (form) s.form = form;
      runSteps(s, ctxOf("heat", medium, T, { stirring, lid }), time);
      return s;
    }
    if (time != null) throw new Error("time と until は同時に指定しない");
    if (!(max_time > 0)) throw new Error("until には上限時間 max_time が要る");
    const cond = untilText(until);
    const s = begin(state, `heat(${medium},${T}℃,until ${cond}${tail})`);
    if (form) s.form = form;
    const already = untilMet(s, until);
    const elapsed = already ? 0.0 : runSteps(s, ctxOf("heat", medium, T, { stirring, lid }), max_time, until);
    const reached = already || untilMet(s, until);
    s.stops.push({ op: s.ops.length, until: cond, reached, minutes: Math.round(elapsed * 1000) / 1000, max_time });
    if (reached) log(s, "until", `${cond} に ${elapsed.toFixed(2)}分で到達` + (already ? "（加熱前から満たしていた）" : ""));
    else log(s, "until", `${cond} に上限 ${max_time}分で到達しなかった`);
    return s;
  }
  const bake = (st, kw) => heat(st, { ...kw, medium: kw.medium || "pan" });
  const steamOp = (st, kw) => heat(st, { ...kw, medium: "steam" });
  const simmer = (st, kw) => heat(st, { ...kw, medium: "water" });
  const deepFry = (st, kw) => heat(st, { ...kw, medium: "oil" });
  // 卵を割って湯に落とす（ops.poach）
  function poach(st, kw) {
    const { T, time = null, vinegar_pct = 0.0, salt_pct = 0.0, until = null, max_time = null } = kw;
    const bpw = D.run.boiling_point_water;
    const Teff = Math.min(T, bpw);
    const decide = has(st, ...EGG_KEYS) && st.egg_form === EGG_CRACKED && st.egg_white_cohesion == null;
    const s = heat(st, { medium: "water", T, time, form: "drop", until, max_time });
    s.ops[s.ops.length - 1] = s.ops[s.ops.length - 1].replace("heat(water,", `poach(酢${vinegar_pct}%,塩${salt_pct}%,`);
    if (decide) {
      const [SCATTER, FILM, COHESIVE] = LV.coh;
      const additive = (vinegar_pct || 0) > 0 || (salt_pct || 0) > 0;
      const coh = Teff < V("poach_cohesion_T_min") ? SCATTER : additive ? FILM : Teff >= bpw ? SCATTER : COHESIVE;
      s.egg_white_cohesion = coh;
      log(s, "R-E21/E22", "卵白のまとまり→" + coh);
    }
    return s;
  }
  function chill(st, kw) {
    const s = heat(st, { medium: "air", T: kw.T, time: kw.time });
    s.ops[s.ops.length - 1] = `chill(${kw.T}℃,${kw.time}min)`;
    return s;
  }
  function rest(st, kw) {
    const s = heat(st, { medium: "air", T: kw.T, time: kw.time });
    s.ops[s.ops.length - 1] = `rest(${kw.T}℃,${kw.time}min)`;
    if (s.gluten && kw.time >= V("gluten_relax_min") && !s.gluten_relaxed) { s.gluten_relaxed = 1; log(s, "R-G03", "グルテンが緩んだ"); }
    return s;
  }
  // 水に取る（ops.plunge）・湯に入れたまま火を止める（ops.off_heat）。余熱、rules.md §10 2026-09-28 夜
  function plunge(st, kw) {
    const s = heat(st, { medium: "water", T: kw.T, time: kw.time });
    s.ops[s.ops.length - 1] = `plunge(${kw.T}℃,${kw.time}min)`;
    return s;
  }
  function offHeat(st, kw) {
    const s = begin(st, `off_heat(${kw.T}℃,${kw.time}min)`);
    const T_room = D.run.T0_default, tau = D.heat_transfer.pot_cooling_tau_min;
    const dt = D.run.dt_min;
    const n = Math.max(1, pyRound(kw.time / dt));
    const step = kw.time / n;
    for (let i = 0; i < n; i++) {
      const T_w = T_room + (kw.T - T_room) * Math.exp(-(i * step) / tau);
      const ctx = ctxOf("off_heat", "water", T_w);
      ctx.t_in_op = i * step;
      advance(s, ctx, step);
      applyRules(s, ctx, step);
    }
    return s;
  }
  function soak(st, kw) {
    const s = begin(st, `soak(${kw.T}℃,${kw.time}min)`);
    runSteps(s, ctxOf("soak", "water", kw.T), kw.time);
    return s;
  }
  function ferment(st, kw) {
    const s = heat(st, { medium: "air", T: kw.T, time: kw.time });
    s.ops[s.ops.length - 1] = `ferment(${kw.T}℃,${kw.time}min)`;
    const [lo, hi] = V("yeast_ferment_T_range");
    if ("yeast" in s.masses && s.yeast_alive !== LV.yeast[2] && lo <= kw.T && kw.T <= hi) {
      s.yeast_alive = LV.yeast[0]; s.co2 = Math.max(s.co2 || 0, 3); log(s, "R-L02", "発酵で CO2 co2=3");
    }
    return s;
  }

  function addIngredients(s, add, T_add) {
    if (!add || !Object.keys(add).length) return;
    T_add = T_add == null ? D.run.T0_default : T_add;
    const mOld = mass(s);
    const mNew = sum(Object.values(add));
    for (const [k, v] of Object.entries(add)) {
      if (!(k in D.ingredients)) throw new Error("未知の食材: " + k);
      s.masses[k] = (s.masses[k] || 0.0) + v;
    }
    MEMO.delete(s.masses);
    s.T_core = (s.T_core * mOld + T_add * mNew) / (mOld + mNew);
    s.T_surface = s.T_core;
    initComponents(s, null);
  }
  function mixEffects(s, strength) {
    if (has(s, ...EGG_KEYS) && s.egg_form !== EGG_SHELL && s.egg_form !== EGG_BEATEN) {
      s.egg_form = EGG_BEATEN; log(s, "R-E19", "卵を溶きほぐした（卵白と卵黄が均一）");
    }
    if ("flour" in s.masses) {
      const wo = liquidWaterG(s, ["flour"]);
      if (wo / s.masses.flour >= V("gluten_min_water_ratio")) {
        const g = V("gluten_by_strength")[strength];
        if (g > (s.gluten || 0)) { s.gluten = g; log(s, "R-G01/G02", `gluten→${g}（${strength}）`); }
      }
    }
    if ("baking_powder" in s.masses && liquidWaterG(s, ["baking_powder", "flour"]) > 0 && (s.co2 || 0) < 1) {
      s.co2 = 1; log(s, "R-L01", "ベーキングパウダー第1段 co2=1");
    }
  }
  function mix(st, kw = {}) {
    const { add = null, strength = "中", time = 1.0, T_add = null } = kw;
    const s = begin(st, `mix(${strength}${add ? ",+" + Object.keys(add).join("+") : ""})`);
    addIngredients(s, add, T_add);
    mixEffects(s, strength);
    runSteps(s, ctxOf("mix", "none", s.T_core), time);
    return s;
  }
  function knead(st, kw = {}) {
    const time = kw.time == null ? 10.0 : kw.time;
    const s = begin(st, `knead(${time}min)`);
    mixEffects(s, "強");
    runSteps(s, ctxOf("knead", "none", s.T_core), time);
    return s;
  }
  function whisk(st, kw) {
    const { time, T = null, add = null } = kw;
    const s = begin(st, `whisk(${time}min${T != null ? "," + T + "℃" : ""})`);
    addIngredients(s, add, null);
    mixEffects(s, "中");
    const Tb = T == null ? s.T_core : T;
    const temps = [];
    const n = Math.max(1, pyRound(time / D.run.dt_min));
    const ctx = ctxOf("whisk", "bath", Tb);
    for (let i = 0; i < n; i++) {
      ctx.t_in_op = i * (time / n);
      advance(s, ctx, time / n);
      applyRules(s, ctx, time / n);
      temps.push(s.T_core);
    }
    s.T_whisk = sum(temps) / temps.length;
    whipCream(s, time);
    return s;
  }
  function whipCream(s, time) {
    if (!("heavy_cream" in s.masses)) return;
    if (PROPS.fat(s) < V("cream_fat_min") || s.T_whisk >= V("butter_liquid_T")) return;
    s.cream_whisk_min += time;
    let stage_ = 0;
    for (const [k, m] of intKeys(V("cream_foam_minutes"))) if (s.cream_whisk_min >= m) stage_ = Math.max(stage_, k);
    const [lo, hi] = V("cream_whip_T_range");
    if (!(lo <= s.T_whisk && s.T_whisk <= hi)) {
      stage_ = Math.min(stage_, 1);
      log(s, "R-D03", `品温 ${s.T_whisk.toFixed(1)}℃ は範囲外、泡は粗いまま`);
    }
    if (stage_ > (s.foam_stage || 0)) { s.foam_stage = stage_; log(s, "R-D03/D04", "foam_stage→" + stage_); }
    if (s.foam_stage >= 4) s.cream_network = LV.fat[5];
    else if (s.foam_stage >= 2) s.cream_network = LV.fat[4];
  }

  const OPS = { mix, whisk, knead, soak, heat, bake, steam: steamOp, simmer, deep_fry: deepFry, chill, rest, ferment, poach, plunge, off_heat: offHeat };

  function initial(recipe) {
    return newState(recipe.ingredients, recipe.T0, recipe.egg_form, recipe.form);
  }
  function applyStep(s, name, kw) {
    if (!(name in OPS)) throw new Error("未知の操作: " + name);
    return OPS[name](s, kw || {});
  }
  function run(recipe) {
    let s = initial(recipe);
    for (const [n, kw] of recipe.steps) s = applyStep(s, n, kw);
    return s;
  }

  // ------------------------------------------------------------------
  // 判定（judge.py）
  function check(s, c) {
    const basis = String(c.basis == null ? "" : c.basis);
    const req = !!c.required;
    if ("ingredients" in c) {
      const missing = [];
      for (const item of c.ingredients) {
        const alts = Array.isArray(item) ? item : [item];
        if (!has(s, ...alts)) missing.push(alts.join("|"));
      }
      const text = "食材: " + c.ingredients.map((i) => (Array.isArray(i) ? i.join("|") : i)).join(", ");
      return { text, var: null, actual: missing.length ? "不足: " + missing.join(", ") : "あり", ok: !missing.length, required: req, basis };
    }
    if ("history" in c) {
      const th = c.at_or_above, m = c.min_minutes;
      const actual = hold(s, c.history, "ge", th);
      return { text: `${c.history} が ${th}℃以上の時間 ≧ ${m}分`, var: "t_at_T", actual, ok: actual >= m, required: req, basis };
    }
    const v = get(s, c.var);
    let text, ok;
    if ("range" in c) {
      const [lo, hi] = c.range;
      text = `${c.var} ∈ [${lo == null ? "" : lo}, ${hi == null ? "" : hi}]`;
      ok = v != null && typeof v !== "string" && (lo == null || v >= lo) && (hi == null || v <= hi);
    } else if ("in" in c) {
      text = `${c.var} ∈ {${c.in.join(", ")}}`;
      ok = v != null && c.in.some((x) => x === v || (typeof v === "boolean" && Number(v) === x));
    } else if ("is" in c) {
      text = `${c.var} = ${c.is}`;
      ok = v != null && !!v === !!c.is;
    } else throw new Error("条件の形が不明");
    return { text, var: c.var, actual: v == null ? NO_MATCH : v, ok, required: req, basis };
  }

  function evaluate(s, dishes) {
    dishes = dishes || D.dishes;
    const order = Object.keys(dishes);
    const out = order.map((key) => {
      const d = dishes[key];
      const r = { dish: key, ja: d.ja, required_ok: true, met: [], unmet: [] };
      for (const c of d.conditions) {
        const cr = check(s, c);
        (cr.ok ? r.met : r.unmet).push(cr);
        if (cr.required && !cr.ok) r.required_ok = false;
      }
      r.n_total = r.met.length + r.unmet.length;
      r.fraction = r.n_total ? r.met.length / r.n_total : 0.0;
      return r;
    });
    out.sort((a, b) => (a.required_ok === b.required_ok ? 0 : a.required_ok ? -1 : 1)
      || (b.fraction - a.fraction) || (order.indexOf(a.dish) - order.indexOf(b.dish)));
    return out;
  }

  function verdict(s, minFraction) {
    minFraction = minFraction == null ? D.no_match_below : minFraction;
    const res = evaluate(s);
    const cands = res.filter((r) => r.required_ok), excl = res.filter((r) => !r.required_ok);
    const ok = cands.length && cands[0].fraction >= minFraction;
    return { answer: ok ? cands[0].dish : null, ja: ok ? cands[0].ja : NO_MATCH, min_fraction: minFraction,
      candidates: cands, excluded: excl };
  }

  // ------------------------------------------------------------------
  // 感じ方（perception.py）
  const P_ITEMS = () => Object.keys(D.perception.items);
  function feature(s, v) {
    const x = get(s, v);
    if (x == null) return 0.0;
    if (typeof x === "boolean") return x ? 1.0 : 0.0;
    return x;
  }
  const category = (v) => (v == null || v === 0 ? D.perception.none_category : String(v));
  const clip = (x) => Math.min(5.0, Math.max(0.0, x));
  function predict(m, row) {
    let y;
    if (m.type === "linear") {
      y = m.intercept;
      m.coef.forEach((c, i) => { y += c * row[m.vars[i]]; });
    } else if (m.type === "isotonic") {
      const x = row[m.vars[0]], xs = m.x, ys = m.y;
      if (x <= xs[0]) y = ys[0];
      else if (x >= xs[xs.length - 1]) y = ys[ys.length - 1];
      else {
        let j = 1;
        while (!(x <= xs[j])) j++;
        y = ys[j - 1] + ((ys[j] - ys[j - 1]) * (x - xs[j - 1])) / (xs[j] - xs[j - 1]);
      }
    } else if (m.type === "category_mean") {
      const c = category(row[m.vars[0]]);
      y = c in m.means ? m.means[c] : m.fallback;
    } else throw new Error(m.type);
    return clip(y);
  }
  function perceive(s) {
    const items = D.perception.items;
    const out = {}, row = {};
    for (const k of P_ITEMS()) for (const v of items[k].vars) row[v] = feature(s, v);
    for (const k of P_ITEMS()) out[k] = predict(items[k], row);
    return out;
  }
  function nearest(pvec, top) {
    const labels = D.perception.labels, keys = Object.keys(labels), items = P_ITEMS();
    const d = keys.map((k) => {
      let a = 0;
      for (const i of items) a += (pvec[i] - labels[k][i]) ** 2;
      return [k, Math.sqrt(a)];
    });
    d.sort((a, b) => a[1] - b[1] || keys.indexOf(a[0]) - keys.indexOf(b[0]));
    return d.slice(0, top == null ? 3 : top);
  }

  // ------------------------------------------------------------------
  // 地図（sim/maps.py）
  const MAP_NONE = "__none", MAP_RAW = "__raw";
  const RAW_VARS = ["egg_white_stage", "egg_yolk_stage", "egg_gel_stage", "starch_gel", "maillard", "caramel",
    "meat_myosin", "milk_whey_denatured", "foam_stage", "gelatin_state", "cell_wall"];
  function mapValues(lo, hi, step) {
    const n = Math.floor((hi - lo) / step + 1e-9) + 1;
    const out = [];
    for (let i = 0; i < n; i++) out.push(parseFloat((lo + i * step).toFixed(9)));  // maps.values と同じ丸め
    return out;
  }
  function withValue(recipe, axis, v) {
    const r = JSON.parse(JSON.stringify(recipe));
    if (axis.kind === "step") r.steps[axis.i][1][axis.key] = v;
    else if (axis.kind === "ing") r.ingredients[axis.key] = v;
    else if (axis.kind === "add") r.steps[axis.i][1].add[axis.key] = v;
    else if (axis.kind === "T0") r.T0 = v;
    else throw new Error("軸の種類が不明");
    return r;
  }
  const norm0 = (v) => (v == null ? 0 : v);
  function mapCell(r, minFraction) {
    const s0 = initial(r);
    let s = s0;
    for (const [n, kw] of r.steps) s = applyStep(s, n, kw);
    const v = verdict(s, minFraction);
    const c = v.candidates;
    const top = c.length ? [c[0].dish, c[0].met.length, c[0].n_total] : null;
    const second = c.length > 1 ? [c[1].dish, c[1].met.length, c[1].n_total] : null;
    const f1 = c.length ? c[0].fraction : 0.0, f2 = c.length > 1 ? c[1].fraction : 0.0;
    let cls;
    if (v.answer != null) cls = v.answer;
    else if (RAW_VARS.every((k) => norm0(get(s, k)) === norm0(get(s0, k)))) cls = MAP_RAW;
    else cls = MAP_NONE;
    return { cls, top, second, margin: f1 - f2 };
  }
  // onRow(j, row) を行ごとに呼ぶ（ページで少しずつ描くため）
  function mapGrid(base, x, y, minFraction, onRow) {
    const xs = mapValues(x.lo, x.hi, x.step), ys = mapValues(y.lo, y.hi, y.step);
    const cells = [];
    ys.forEach((yv, j) => {
      const row = xs.map((xv) => mapCell(withValue(withValue(base, x.axis, xv), y.axis, yv), minFraction));
      cells.push(row);
      if (onRow) onRow(j, row);
    });
    return { xs, ys, cells };
  }

  return {
    mapValues, withValue, mapCell, mapGrid, MAP_NONE, MAP_RAW,
    setData, newState, initial, applyStep, run, get, hold, evaluate, verdict, perceive, nearest, untilText,
    OPS, NO_MATCH, EGG_SHELL, EGG_CRACKED, EGG_BEATEN, _pyRound: pyRound,
  };
});

/* 調理の計算ページの「画面の状態 ⇄ レシピ」変換（DOM を使わない部分）。
 *
 * - page_template.html に埋め込まれる（build_page.py）。node では test_page_model.js が読む
 * - 計算（sim.js）には触れない。ここは画面の入力をレシピの形に組み立てるだけ
 * - ブラウザでは window.CookPage、node では module.exports
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.CookPage = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const OPS = {
    mix: "混ぜる", whisk: "撹拌・泡立て", heat: "加熱", chill: "冷やす", rest: "寝かせる", soak: "浸す",
    poach: "卵を割って湯に落とす", plunge: "水に取る", off_heat: "湯に入れたまま火を止める",
  };
  const MEDIA = { pan: "フライパン", steam: "蒸し器", water: "湯・鍋で煮る", oil: "油で揚げる", air: "オーブン" };
  const FORMS = { "": "（変えない）", thin: "薄く広げる", cup: "器に入れる", pot: "鍋", shell: "殻付き", piece: "肉片" };
  const MEDIUM_FORM = { pan: "thin", steam: "cup", water: "pot", oil: "thin", air: "" };
  const UNTIL = {
    egg_gel_stage: { label: "卵液のゲル段階", unit: "段階", def: 2 },
    maillard: { label: "メイラード（焼き色）", unit: "段階", def: 2 },
    caramel: { label: "カラメル化", unit: "段階", def: 2 },
    T_core: { label: "中心温度", unit: "℃", def: 75 },
    gelatin: { label: "ゼラチンが溶けるまで", unit: "", def: null },
  };

  // ---- 変数名 → 日本語のラベル（画面に出す言葉の対応表。ここ1か所にまとめる） ----
  // ja: ラベル、u: 単位（値が数のとき）、d: 小数の桁、pct: 0〜1 を % で出す
  const LABELS = {
    T_core: { ja: "中心の温度", u: "℃", d: 1, short: "中心" },
    T_surface: { ja: "表面の温度", u: "℃", d: 1, short: "表面" },
    T_core_max: { ja: "中心の最高温度", u: "℃", d: 1 },
    T_surface_max: { ja: "表面の最高温度", u: "℃", d: 1 },
    T_white: { ja: "卵白の層の温度（殻付き卵）", u: "℃", d: 1, short: "卵白の層" },
    T_white_max: { ja: "卵白の層の最高温度（殻付き卵）", u: "℃", d: 1 },
    T_serve: { ja: "食べるときの温度", u: "℃", d: 1 },
    T_whisk: { ja: "泡立てたときの温度", u: "℃", d: 1 },
    t_at_T: { ja: "高い温度を保った時間", u: "分", d: 1 },
    water: { ja: "水分", u: "%", d: 1 },
    fat: { ja: "脂質", u: "%", d: 1 },
    protein: { ja: "たんぱく質", u: "%", d: 1 },
    sugar_conc: { ja: "甘さのもと（糖の濃さ）", u: "%", d: 1 },
    sugar_conc_ratio: { ja: "糖の濃さの倍率（煮詰まり）", u: "倍", d: 2 },
    salt_conc: { ja: "塩分", u: "%", d: 2 },
    mass_ratio: { ja: "重さ（はじめ＝1）", u: "倍", d: 2 },
    pH: { ja: "pH", u: "", d: 1 },
    egg_form: { ja: "卵の形" },
    egg_dilution: { ja: "卵の割合", u: "%", d: 1 },
    egg_white_stage: { ja: "卵白の固まり具合", short: "卵白" },
    egg_yolk_stage: { ja: "卵黄の固まり具合", short: "卵黄" },
    egg_gel_stage: { ja: "卵液の固まり具合", short: "卵液" },
    egg_gel_stage_surface: { ja: "卵液の外側の固まり具合" },
    gel_structure: { ja: "固まり方" },
    porosity: { ja: "す（小さな穴）" },
    milk_casein: { ja: "牛乳のたんぱく（カゼイン）" },
    milk_whey_denatured: { ja: "牛乳のたんぱく（乳清）の熱変性" },
    fat_phase: { ja: "脂の状態" },
    air_frac: { ja: "泡の量", u: "", d: 2 },
    foam_stage: { ja: "泡立ち", short: "泡" },
    air: { ja: "気泡" },
    starch_gel: { ja: "でんぷんの糊化", pct: true, short: "糊化" },
    starch_retro: { ja: "でんぷんの老化（ぼそつき）" },
    gluten: { ja: "グルテン（粘り）" },
    gluten_relaxed: { ja: "グルテンの緩み" },
    co2: { ja: "ふくらみ（炭酸ガス）" },
    yeast_alive: { ja: "酵母" },
    maillard: { ja: "焼き色（メイラード）", short: "焼き色" },
    caramel: { ja: "カラメル化", short: "カラメル" },
    syrup_stage: { ja: "糖液の煮詰まり" },
    onion_sulfur: { ja: "玉ねぎの辛み成分" },
    cell_wall: { ja: "野菜のやわらかさ（細胞壁）" },
    meat_myosin: { ja: "肉のたんぱく（ミオシン）" },
    meat_actin: { ja: "肉のたんぱく（アクチン）" },
    meat_collagen: { ja: "肉のすじ（コラーゲン）" },
    meat_myoglobin: { ja: "肉の色（ミオグロビン）", short: "肉の色" },
    meat_water_loss: { ja: "肉汁の出方" },
    gelatin_state: { ja: "ゼラチンの状態", short: "ゼラチン" },
    gelatin_conc: { ja: "ゼラチンの濃さ", u: "%", d: 1 },
    egg_white_cohesion: { ja: "卵白のまとまり", short: "まとまり" },
  };
  // 段階の値の言葉のうち、画面では短くしたいもの（無いものは sim_data.json の levels をそのまま使う）
  const LEVEL_JA = {
    egg_white_stage: { 0: "生", 1: "とろみ", 2: "やわらかく固まる", 3: "しっかり固まる" },
    egg_yolk_stage: { 0: "生", 1: "とろみ", 2: "しっとり固まる", 3: "ほろほろ" },
    egg_gel_stage: { 0: "液", 1: "とろみ", 2: "やわらかく固まる", 3: "しっかり固まる", 4: "す立ち・水が出る" },
    egg_gel_stage_surface: { 0: "液", 1: "とろみ", 2: "やわらかく固まる", 3: "しっかり固まる", 4: "す立ち・水が出る" },
    maillard: { 0: "なし", 1: "うっすら", 2: "きつね色", 3: "濃い褐色" },
    caramel: { 0: "なし", 1: "淡い色", 2: "カラメル色", 3: "焦げ" },
    milk_whey_denatured: { 0: "なし", 1: "あり" },
    gluten: { 0: "なし", 1: "水とふれて少し", 2: "よく出る", 3: "強く出る" },
    meat_myosin: { 0: "生", 1: "変性" },
    meat_actin: { 0: "生", 1: "変性" },
  };

  // 文字列の値のうち、画面では言い換えるもの
  const STR_JA = {
    "小片（カード）": "細かいかたまり", "連続ゲル": "ひとつながりに固まる", "外側連続・内側半流動": "外は固まり中は半熟",
    "O/W乳化（乳・卵黄）": "乳化（乳・卵黄）", "部分合一ネットワーク（ホイップ）": "ホイップの網目", "溶解（ゾル）": "溶けている",
  };
  // 食材名のうち、画面で短く呼ぶもの
  const ING_SHORT = { egg_whole: "卵" };

  // 「〜まで」の言い回し（停止条件 var ≧ 値 ⇄ 文中の選択肢）。T_core は数を入れる、gelatin は溶けるまで
  const UNTIL_PHRASES = [
    ["egg_gel_stage:1", "とろみがつく"],
    ["egg_gel_stage:2", "やわらかく固まる"],
    ["egg_gel_stage:3", "しっかり固まる"],
    ["egg_gel_stage:4", "すが立つ"],
    ["maillard:1", "うっすら色づく"],
    ["maillard:2", "きつね色になる"],
    ["maillard:3", "濃い焼き色がつく"],
    ["caramel:1", "糖が淡く色づく"],
    ["caramel:2", "カラメル色になる"],
    ["caramel:3", "焦げる"],
    ["T_core", "中心が…℃になる"],
    ["gelatin", "ゼラチンが溶ける"],
  ];
  const untilKey = (s) => (s.uvar === "T_core" || s.uvar === "gelatin" ? s.uvar : `${s.uvar}:${s.uval}`);

  function make(DATA) {
    const GEL_SOL = DATA.levels.gelatin_state[2];
    const R = DATA.recipes;
    // 例（Python 版と同じレシピ）
    const EXAMPLES = [
      ["卵＋牛乳を混ぜながら焼く", R.pairs[0].a],
      ["プリン", R.until.custard_pudding],
      ["温泉卵", R.timed.onsen_tamago],
      ["カラメル", R.until.caramel_sauce],
      ["オムレツ", R.until.omelet],
      ["茶碗蒸し", R.until.chawanmushi],
      ["ホワイトソース", R.until.white_sauce],
      ["ご飯", R.until.steamed_rice],
      ["パンケーキ", R.until.pancake],
      ["牛乳ゼリー", R.until.milk_jelly],
      ["ホイップクリーム", R.until.whipped_cream],
      ["鶏むね肉のソテー", R.until.sauteed_chicken],
      ["炒め玉ねぎ（色づくまで）", R.until.sauteed_onion],
      ["炒め玉ねぎ（40分）", R.timed.sauteed_onion],
      ["ゆで卵", R.until.hard_boiled_egg],
      ["プリン液を100℃で蒸す", R.pairs[3].b],
      ["ポーチドエッグ", R.until.poached_egg],
      ["半熟ゆで卵", R.until.soft_boiled_egg],
    ];

    // レシピ → 画面の状態
    function fromRecipe(r) {
      const steps = r.steps.map(([name, kw]) => {
        kw = kw || {};
        if (name === "mix") return { op: "mix", strength: kw.strength || "中", time: kw.time == null ? 1 : kw.time, add: Object.entries(kw.add || {}), T_add: kw.T_add == null ? null : kw.T_add };
        if (name === "whisk") return { op: "whisk", time: kw.time, T: kw.T == null ? null : kw.T };
        if (name === "chill" || name === "rest" || name === "soak" || name === "plunge" || name === "off_heat") return { op: name, T: kw.T, time: kw.time };
        if (name === "poach") {
          if (kw.until) throw new Error("「〜まで」のポーチは画面では扱わない");
          return { op: "poach", T: kw.T, time: kw.time, vinegar_pct: kw.vinegar_pct || 0, salt_pct: kw.salt_pct || 0 };
        }
        const medium = name === "steam" ? "steam" : name === "simmer" ? "water" : name === "deep_fry" ? "oil" : (kw.medium || "pan");
        const st = { op: "heat", medium, T: kw.T, stirring: !!kw.stirring, lid: !!kw.lid, form: kw.form || "",
          mode: kw.until ? "until" : "time", time: kw.time == null ? 5 : kw.time, max_time: kw.max_time || 30,
          uvar: "egg_gel_stage", uval: 2 };
        if (kw.until) {
          if (kw.until.var === "gelatin_state") st.uvar = "gelatin";
          else { st.uvar = kw.until.var; st.uval = kw.until.ge; }
        }
        return st;
      });
      return { ingredients: Object.entries(r.ingredients), T0: r.T0 == null ? DATA.run.T0_default : r.T0,
        egg_form: r.egg_form || "割った", form: r.form || "pot", steps };
    }

    function num(v, what, allowZero) {
      const x = Number(v);
      if (v === "" || v == null || !isFinite(x) || (allowZero ? false : x <= 0))
        throw new Error(`${what}を数で入れてください${allowZero ? "" : "（0 より大きい値）"}。`);
      return x;
    }

    // 画面の状態 → レシピ（sim.js に渡す形）
    function toRecipe(m) {
      const ing = {};
      for (const [k, g] of m.ingredients) if (g > 0) ing[k] = (ing[k] || 0) + Number(g);
      const steps = m.steps.map((s) => {
        if (s.op === "mix") {
          const add = {};
          for (const [k, g] of s.add) if (g > 0) add[k] = (add[k] || 0) + Number(g);
          // T_add（加える物の温度、2026-10-22 カスタードクリームの沸騰した牛乳）は画面では編集しないが、読み込んだレシピの値を保つ
          return ["mix", { strength: s.strength, time: num(s.time, "混ぜる時間"), ...(Object.keys(add).length ? { add } : {}),
            ...(s.T_add == null || s.T_add === "" ? {} : { T_add: Number(s.T_add) }) }];
        }
        if (s.op === "whisk") return ["whisk", { time: num(s.time, "撹拌の時間"), ...(s.T == null || s.T === "" ? {} : { T: Number(s.T) }) }];
        if (s.op === "heat") {
          const kw = { medium: s.medium, T: num(s.T, "加熱の温度", true), stirring: s.stirring, lid: s.lid };
          if (s.form) kw.form = s.form;
          if (s.mode === "time") kw.time = num(s.time, "加熱の時間");
          else {
            kw.until = s.uvar === "gelatin" ? { var: "gelatin_state", in: [GEL_SOL] } : { var: s.uvar, ge: Number(s.uval) };
            kw.max_time = num(s.max_time, "上限の時間");
          }
          return ["heat", kw];
        }
        if (s.op === "poach") {
          const kw = { T: num(s.T, "湯の温度", true), time: num(s.time, "ゆでる時間") };
          const vin = Number(s.vinegar_pct || 0), salt = Number(s.salt_pct || 0);
          if (!isFinite(vin) || vin < 0 || !isFinite(salt) || salt < 0) throw new Error("酢・塩の量は 0 以上の数で入れてください。");
          if (vin > 0) kw.vinegar_pct = vin;
          if (salt > 0) kw.salt_pct = salt;
          return ["poach", kw];
        }
        return [s.op, { T: num(s.T, OPS[s.op] + "の温度", true), time: num(s.time, OPS[s.op] + "の時間") }];
      });
      return { ingredients: ing, T0: Number(m.T0), egg_form: m.egg_form, form: m.form, steps };
    }

    function defaultStep(op) {
      if (op === "mix") return { op, strength: "中", time: 1, add: [] };
      if (op === "whisk") return { op, time: 1, T: null };
      if (op === "heat") return { op, medium: "pan", T: 160, mode: "time", time: 3, max_time: 30, uvar: "egg_gel_stage", uval: 2, stirring: false, lid: false, form: "thin" };
      if (op === "chill") return { op, T: 5, time: 60 };
      if (op === "rest") return { op, T: 20, time: 10 };
      if (op === "poach") return { op, T: 80, time: 4, vinegar_pct: 0, salt_pct: 0 };
      if (op === "plunge") return { op, T: 0, time: 15 };
      if (op === "off_heat") return { op, T: 100, time: 10 };
      return { op, T: 20, time: 30 };
    }

    const shortJa = (k) => ING_SHORT[k] || (DATA.ingredients[k] ? DATA.ingredients[k].ja.replace(/（.*$/, "") : k);
    // 操作カードを閉じたときの1行（番号は含めない）
    function opSummary(s) {
      const v = (x) => (x == null || x === "" ? "？" : x);
      if (s.op === "mix") {
        const add = s.add.filter(([, g]) => g > 0).map(([k, g]) => `${shortJa(k)} ${g}g`);
        return `混ぜる｜${s.strength}・${v(s.time)}分` + (add.length ? `・${add.join("、")} を加える` : "") + (s.T_add == null || s.T_add === "" ? "" : `（加える物 ${s.T_add}℃）`);
      }
      if (s.op === "whisk") return `撹拌・泡立て｜${v(s.time)}分` + (s.T == null || s.T === "" ? "" : `・ボウル ${s.T}℃`);
      if (s.op === "heat") {
        const u = UNTIL[s.uvar];
        const how = s.mode === "time" ? `${v(s.time)}分`
          : s.uvar === "gelatin" ? `ゼラチンが溶けるまで（上限 ${v(s.max_time)}分）`
            : `${u.label} ${v(s.uval)}${u.unit === "℃" ? "℃" : ""} まで（上限 ${v(s.max_time)}分）`;
        return `加熱｜${MEDIA[s.medium]} ${v(s.T)}℃・${how}${s.stirring ? "・混ぜながら" : ""}${s.lid ? "・蓋" : ""}`;
      }
      if (s.op === "poach") return `卵を割って湯に落とす｜${v(s.T)}℃・${v(s.time)}分` + (Number(s.vinegar_pct) > 0 ? `・酢 ${s.vinegar_pct}%` : "") + (Number(s.salt_pct) > 0 ? `・塩 ${s.salt_pct}%` : "");
      return `${OPS[s.op]}｜${v(s.T)}℃・${v(s.time)}分`;
    }

    // ---- 値・条件を言葉にする ----
    const LV = DATA.levels;
    const labelOf = (v) => (LABELS[v] ? LABELS[v].ja : v);
    function round(x, d) { const t = Number(x).toFixed(d); return t.replace(/\.0+$/, "").replace(/(\.\d*?)0+$/, "$1"); }
    // 状態の値 → 言葉（段階は言葉、数は単位付き）
    function valueText(v, x) {
      if (x == null) return "—";
      if (typeof x === "boolean") return x ? "あり" : "なし";
      if (typeof x === "string") return STR_JA[x] || x;
      const L = LABELS[v] || {};
      if (LEVEL_JA[v] && LEVEL_JA[v][x] != null) return LEVEL_JA[v][x];
      if (LV[v] && !Array.isArray(LV[v]) && LV[v][String(x)] != null) return LV[v][String(x)];
      if (L.pct) return Math.round(x * 100) + "%";
      return round(x, L.d == null ? 2 : L.d) + (L.u || "");
    }
    // 段階の並び {1,2} → 「とろみ〜やわらかく固まる」（連続していれば「〜」、でなければ「・」）
    function setText(v, xs) {
      const nums = xs.every((x) => typeof x === "number");
      const words = xs.map((x) => valueText(v, x));
      if (nums && xs.length > 1 && xs.every((x, i) => i === 0 || x === xs[i - 1] + 1)) return `${words[0]}〜${words[words.length - 1]}`;
      return words.join("・");
    }
    function rangeText(v, lo, hi) {
      const L = LABELS[v] || {};
      const f = (x) => (L.pct ? Math.round(x * 100) + "" : round(x, L.d == null ? 2 : L.d));
      const u = L.pct ? "%" : L.u || "";
      if (lo == null) return `${f(hi)}${u}以下`;
      if (hi == null) return `${f(lo)}${u}以上`;
      return `${f(lo)}〜${f(hi)}${u}`;
    }
    const ingJa = (alts) => alts.map(shortJa).join("または");
    // 料理の条件（sim_data.json の dishes の1件）→ [何を, どうなら]
    function condJa(c) {
      if ("ingredients" in c) return ["材料", c.ingredients.map((i) => ingJa(Array.isArray(i) ? i : [i])).join("、") + " を使う"];
      if ("history" in c) return [`${c.history === "surface" ? "表面" : "中心"}が ${c.at_or_above}℃以上の時間`, `${c.min_minutes}分以上`];
      if ("range" in c) return [labelOf(c.var), rangeText(c.var, c.range[0], c.range[1])];
      if ("in" in c) return [labelOf(c.var), setText(c.var, c.in)];
      if ("is" in c) return [labelOf(c.var), c.is ? "あり" : "なし"];
      return ["?", "?"];
    }
    // sim.js の check() が返す条件の文字列（text）を、元の条件に戻すための鍵（sim.js と同じ組み立て方）
    function rawCondText(c) {
      if ("ingredients" in c) return "食材: " + c.ingredients.map((i) => (Array.isArray(i) ? i.join("|") : i)).join(", ");
      if ("history" in c) return `${c.history} が ${c.at_or_above}℃以上の時間 ≧ ${c.min_minutes}分`;
      if ("range" in c) return `${c.var} ∈ [${c.range[0] == null ? "" : c.range[0]}, ${c.range[1] == null ? "" : c.range[1]}]`;
      if ("in" in c) return `${c.var} ∈ {${c.in.join(", ")}}`;
      if ("is" in c) return `${c.var} = ${c.is}`;
      return "";
    }
    const COND_BY_TEXT = {};
    for (const [k, d] of Object.entries(DATA.dishes)) for (const c of d.conditions) COND_BY_TEXT[k + "\u0000" + rawCondText(c)] = c;
    // check() の結果1件 → { what, want, actual }（すべて言葉）
    function checkJa(dish, cr) {
      const c = COND_BY_TEXT[dish + "\u0000" + cr.text];
      if (!c) return { what: cr.text, want: "", actual: String(cr.actual), found: false };
      const [what, want] = condJa(c);
      let actual;
      if ("ingredients" in c) actual = cr.ok ? "あり" : "足りない: " + String(cr.actual).replace(/^不足: /, "").split(", ").map((a) => ingJa(a.split("|"))).join("、");
      else if ("history" in c) actual = `${round(cr.actual, 1)}分`;
      else actual = cr.actual === "該当なし" ? "値なし" : valueText(c.var, cr.actual);
      return { what, want, actual, found: true };
    }

    // ---- 地図（DOM を使わない部分） ----
    const STEP_PLACE = { bake: "フライパン", steam: "蒸し器", simmer: "湯", deep_fry: "揚げ油", poach: "湯（卵を落とす）",
      chill: "冷やす", rest: "寝かせる", soak: "浸す", plunge: "水に取る", off_heat: "火を止めた湯", whisk: "ボウル", ferment: "発酵", mix: "混ぜる" };
    const HEAT_PLACE = { pan: "フライパン", water: "湯", steam: "蒸し器", oil: "揚げ油", air: "オーブン" };
    const FIELD = { T: ["温度", "℃"], time: ["時間", "分"], vinegar_pct: ["酢", "%"], salt_pct: ["塩", "%"] };
    // 元のレシピで意味のある数値の欄 → 軸の候補
    function mapAxes(r) {
      const out = [];
      r.steps.forEach(([n, kw], i) => {
        kw = kw || {};
        const place = n === "heat" ? HEAT_PLACE[kw.medium] || "加熱" : STEP_PLACE[n] || n;
        const keys = n === "poach" ? ["T", "time", "vinegar_pct", "salt_pct"] : ["T", "time"];
        for (const k of keys) {
          const v = kw[k] == null && (k === "vinegar_pct" || k === "salt_pct") ? 0 : kw[k];
          if (typeof v !== "number") continue;
          out.push({ id: `step:${i}:${k}`, axis: { kind: "step", i, key: k }, value: v, unit: FIELD[k][1],
            label: `手順${i + 1} ${place}の${FIELD[k][0]}` });
        }
        if (n === "mix" && kw.add) for (const [k, g] of Object.entries(kw.add))
          out.push({ id: `add:${i}:${k}`, axis: { kind: "add", i, key: k }, value: g, unit: "g", label: `手順${i + 1} 加える${shortJa(k)}の量` });
      });
      for (const [k, g] of Object.entries(r.ingredients))
        out.push({ id: `ing:${k}`, axis: { kind: "ing", key: k }, value: g, unit: "g", label: `材料 ${shortJa(k)}の量` });
      out.push({ id: "T0", axis: { kind: "T0" }, value: r.T0 == null ? DATA.run.T0_default : r.T0, unit: "℃", label: "材料のはじめの温度" });
      return out;
    }
    // 刻みを 1・2・2.5・5 × 10^k に丸める
    function niceStep(x) {
      const e = Math.pow(10, Math.floor(Math.log10(x)));
      for (const m of [1, 2, 2.5, 5, 10]) if (m * e >= x - 1e-12) return m * e;
      return 10 * e;
    }
    // 軸を選んだときの範囲の既定値（約20刻み）
    function mapDefaultRange(ax) {
      const v = ax.value, k = ax.axis.key;
      let lo, hi;
      if (k === "T") { lo = Math.max(-20, v - 30); hi = v + 30; if (ax.label.includes("湯") || ax.label.includes("蒸し器")) hi = Math.min(hi, 100); }
      else if (k === "vinegar_pct" || k === "salt_pct") { lo = 0; hi = Math.max(5, v * 2); }
      else if (k === "time") { lo = 0; hi = v * 3 || 10; }
      else { lo = 0; hi = v * 2 || 10; }
      const step = niceStep((hi - lo) / 20);
      lo = Math.floor(lo / step) * step;
      if (k === "time" || ax.axis.kind !== "step" && ax.axis.kind !== "T0") lo = Math.max(lo, step);
      hi = Math.ceil(hi / step) * step;
      return { lo, hi, step };
    }
    // 地図の領域（同じ分類がつながったマス、上下左右）ごとに、名前を置くマスを1つ選ぶ。
    // 境界から一番遠いマス（同点は重心に近いマス）。minSize 未満の領域には置かない
    function mapRegionLabels(cells, minSize) {
      const H = cells.length, W = H ? cells[0].length : 0;
      const comp = cells.map((row) => row.map(() => -1));
      const regions = [];
      for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
        if (comp[j][i] >= 0) continue;
        const cls = cells[j][i].cls, id = regions.length, list = [[i, j]];
        comp[j][i] = id;
        for (let q = 0; q < list.length; q++) {
          const [a, b] = list[q];
          for (const [da, db] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
            const x = a + da, y = b + db;
            if (x >= 0 && y >= 0 && x < W && y < H && comp[y][x] < 0 && cells[y][x].cls === cls) { comp[y][x] = id; list.push([x, y]); }
          }
        }
        regions.push({ cls, cells: list });
      }
      // 境界からの距離（領域の外か地図の外までの上下左右の歩数）
      const dist = cells.map((row) => row.map(() => Infinity));
      const q = [];
      for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
        const edge = [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([da, db]) => {
          const x = i + da, y = j + db;
          return x < 0 || y < 0 || x >= W || y >= H || comp[y][x] !== comp[j][i];
        });
        if (edge) { dist[j][i] = 1; q.push([i, j]); }
      }
      for (let h = 0; h < q.length; h++) {
        const [a, b] = q[h];
        for (const [da, db] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
          const x = a + da, y = b + db;
          if (x >= 0 && y >= 0 && x < W && y < H && comp[y][x] === comp[b][a] && dist[y][x] > dist[b][a] + 1) { dist[y][x] = dist[b][a] + 1; q.push([x, y]); }
        }
      }
      const out = [];
      for (const r of regions) {
        if (r.cells.length < minSize) continue;
        const cx = r.cells.reduce((s, [a]) => s + a, 0) / r.cells.length, cy = r.cells.reduce((s, [, b]) => s + b, 0) / r.cells.length;
        let best = null;
        for (const [a, b] of r.cells) {
          const key = [dist[b][a], -((a - cx) ** 2 + (b - cy) ** 2)];
          if (!best || key[0] > best.key[0] || (key[0] === best.key[0] && key[1] > best.key[1])) best = { key, i: a, j: b };
        }
        out.push({ cls: r.cls, i: best.i, j: best.j, size: r.cells.length });
      }
      return out;
    }

    return { EXAMPLES, fromRecipe, toRecipe, num, defaultStep, opSummary, shortJa, GEL_SOL,
      labelOf, valueText, setText, condJa, rawCondText, checkJa, mapAxes, mapDefaultRange, niceStep, mapRegionLabels };
  }

  return { OPS, MEDIA, FORMS, MEDIUM_FORM, UNTIL, LABELS, STR_JA, LEVEL_JA, UNTIL_PHRASES, untilKey, make };
});

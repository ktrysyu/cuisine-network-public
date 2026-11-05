/* ページの「画面の状態 → レシピ」変換のテスト（DOM を使わない）。
 *
 *   node experiments/exp-14/js/test_page_model.js
 *
 * 例ボタンのレシピ（と 13品＋ゆで卵の正解のレシピ・順番を変えた組）を、画面の状態に読み込み（fromRecipe）、
 * 画面の状態からレシピを組み立て直し（toRecipe）、元のレシピと同じ計算結果になるかを確かめる。
 * 比べるもの: 各操作の後の状態（操作の記録の文字列を除く全フィールド）・停止条件・判定・感じ方・感じ方で近い料理。
 * 同じ関数に同じ入力を渡しているはずなので、連続量も完全一致を求める。
 */
"use strict";
const fs = require("fs");
const path = require("path");
const CookSim = require("./sim.js");
const CookPage = require("./page_model.js");

const data = JSON.parse(fs.readFileSync(path.join(__dirname, "sim_data.json"), "utf8"));
CookSim.setData(data);
const P = CookPage.make(data);

const strip = (s) => { const { ops, ...rest } = s; return rest; };
function outcome(recipe) {
  let s = CookSim.initial(recipe);
  const states = [JSON.stringify(strip(s))];
  for (const [n, kw] of recipe.steps) { s = CookSim.applyStep(s, n, kw); states.push(JSON.stringify(strip(s))); }
  const v = CookSim.verdict(s);
  const pv = CookSim.perceive(s);
  return {
    states,
    verdict: JSON.stringify({ answer: v.answer, candidates: v.candidates, excluded: v.excluded }),
    perception: JSON.stringify(pv),
    nearest: JSON.stringify(CookSim.nearest(pv, 3)),
  };
}

const cases = P.EXAMPLES.map(([n, r]) => ["例: " + n, r]);
for (const kind of ["until", "timed"]) for (const [k, r] of Object.entries(data.recipes[kind])) cases.push([`${kind}:${k}`, r]);
data.recipes.pairs.forEach((p, i) => { cases.push([`pair${i + 1}:a`, p.a]); cases.push([`pair${i + 1}:b`, p.b]); });
// 追加の入力のうち「〜まで」のポーチ（poach_until）は画面では扱わないので除く
for (const [k, r] of Object.entries(data.recipes.extra)) if (k !== "poach_until") cases.push([`extra:${k}`, r]);

let fails = 0;
const lines = [];
for (const [name, r] of cases) {
  const a = outcome(r);
  const b = outcome(P.toRecipe(P.fromRecipe(r)));
  const bad = [];
  if (a.states.length !== b.states.length) bad.push("操作の数");
  else a.states.forEach((x, i) => { if (x !== b.states[i]) bad.push(`操作${i}の後の状態`); });
  for (const k of ["verdict", "perception", "nearest"]) if (a[k] !== b[k]) bad.push(k);
  if (bad.length) fails++;
  const ans = JSON.parse(b.verdict).answer;
  lines.push(`${bad.length ? "✘" : "✔"} ${name.padEnd(28)} 答え ${String(ans).padEnd(16)}${bad.length ? " 違い: " + bad.join("・") : ""}`);
}
// 画面の言葉: 料理の条件・状態の一覧に出る変数がすべて日本語のラベルを持つ／check() の結果が元の条件に戻せる／
// 例の「〜まで」がすべて文中の選択肢にある
const KV = ["T_serve", "T_core_max", "T_surface_max", "water", "fat", "protein", "sugar_conc", "salt_conc", "mass_ratio",
  "egg_form", "egg_dilution", "egg_white_stage", "egg_yolk_stage", "egg_gel_stage", "egg_gel_stage_surface", "gel_structure",
  "porosity", "milk_whey_denatured", "milk_casein", "fat_phase", "starch_gel", "starch_retro", "gluten", "co2", "maillard",
  "caramel", "syrup_stage", "onion_sulfur", "cell_wall", "meat_myosin", "meat_actin", "meat_myoglobin", "meat_water_loss",
  "gelatin_state", "gelatin_conc", "foam_stage", "T_whisk", "air", "T_core", "T_surface", "egg_white_cohesion"];
const vars = new Set(KV);
for (const d of Object.values(data.dishes)) for (const c of d.conditions) if (c.var) vars.add(c.var);
for (const it of Object.values(data.perception.items)) for (const v of it.vars) vars.add(v);
const noLabel = [...vars].filter((v) => !CookPage.LABELS[v]);
if (noLabel.length) { fails++; lines.push("✘ 日本語のラベルが無い変数: " + noLabel.join(", ")); }
else lines.push(`✔ 変数 ${vars.size} 個すべてに日本語のラベル`);
let nCond = 0, lost = 0, ascii = 0;
for (const [, r] of cases) {
  const v = CookSim.verdict(CookSim.run(r));
  for (const res of [...v.candidates, ...v.excluded]) for (const cr of [...res.met, ...res.unmet]) {
    nCond++;
    const j = P.checkJa(res.dish, cr);
    if (!j.found) lost++;
    if (/[a-z]_[a-z]/i.test(j.what + j.want + j.actual)) ascii++;
  }
}
if (lost || ascii) { fails++; lines.push(`✘ 条件の言葉: 元に戻せない ${lost}・変数名が残る ${ascii}（${nCond} 件中）`); }
else lines.push(`✔ 条件 ${nCond} 件すべてを日本語の言葉にできた`);
const phrase = new Set(CookPage.UNTIL_PHRASES.map(([k]) => k));
const missPh = [];
for (const [name, r] of cases) for (const st of P.fromRecipe(r).steps) if (st.op === "heat" && st.mode === "until" && !phrase.has(CookPage.untilKey(st))) missPh.push(name);
if (missPh.length) { fails++; lines.push("✘ 「〜まで」の言い回しが無い: " + missPh.join(", ")); }
else lines.push("✔ 例の「〜まで」はすべて文中の選択肢にある");
// 例ボタンのうち、画面から組み立てたレシピがテストのレシピと同じ答えになるか（例ボタンすべてを必ず含む）
if (P.EXAMPLES.length !== 18) { fails++; lines.push("✘ 例ボタンの数が想定（18）と違う"); }
// 地図: 最初から用意した4枚の軸が、元のレシピの軸の候補にある／領域の名前の位置
for (const m of data.maps) {
  const ids = P.mapAxes(m.base_recipe).map((a) => a.id);
  const need = [m.x.axis, m.y.axis].map((a) => `step:${a.i}:${a.key}`);
  if (!need.every((x) => ids.includes(x))) { fails++; lines.push(`✘ 地図 ${m.id} の軸が候補に無い`); }
}
const L = (s) => s.split("/").map((r) => [...r].map((c) => ({ cls: c })));
const lab = P.mapRegionLabels(L("AAAB/AAAB/CCCB"), 2);
const want = JSON.stringify([{ cls: "A", i: 1, j: 0, size: 6 }, { cls: "B", i: 3, j: 1, size: 3 }, { cls: "C", i: 1, j: 2, size: 3 }]);
if (JSON.stringify(lab) !== want) { fails++; lines.push("✘ 領域の名前の位置: " + JSON.stringify(lab)); }
else lines.push("✔ 地図の軸の候補・領域の名前の位置");
console.log(lines.join("\n"));
console.log(`\n入力 ${cases.length}（うち例ボタン ${P.EXAMPLES.length}）・不一致 ${fails} 件`);
process.exit(fails ? 1 : 0);

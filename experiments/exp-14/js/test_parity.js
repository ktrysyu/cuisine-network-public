/* Python 版と JS 版の一致テスト。
 *
 *   uv run python experiments/exp-14/js/export_data.py   # expected.json を作り直す（Python 版の結果）
 *   node experiments/exp-14/js/test_parity.js
 *
 * 13品（＋ゆで卵・ポーチドエッグ）の正解のレシピ（状態で止める版・時間で止める版）と、順番を変えた7組（14入力）、
 * ポーチと割った卵の追加の入力（recipes.extra）について、
 * 各操作の後の状態変数・停止条件の到達・判定（候補の順位と満たした条件の数、外した料理、答え）・感じ方6項目・
 * 感じ方で近い料理を比べる。段階・カテゴリ・真偽は完全一致、連続量は相対誤差 1e-9 以内（exp の実装差の余裕）。
 */
"use strict";
const fs = require("fs");
const path = require("path");
const CookSim = require("./sim.js");

const data = JSON.parse(fs.readFileSync(path.join(__dirname, "sim_data.json"), "utf8"));
const expected = JSON.parse(fs.readFileSync(path.join(__dirname, "expected.json"), "utf8"));
CookSim.setData(data);

const TOL = 1e-9;
let fails = 0, checks = 0, maxRel = 0;
function same(a, b, where) {
  checks++;
  if (typeof a === "number" && typeof b === "number") {
    const rel = Math.abs(a - b) / Math.max(1, Math.abs(a), Math.abs(b));
    maxRel = Math.max(maxRel, rel);
    if (rel <= TOL) return;
  } else if (JSON.stringify(a) === JSON.stringify(b)) return;
  fails++;
  if (fails <= 30) console.log(`  ✘ ${where}: python=${JSON.stringify(a)} js=${JSON.stringify(b)}`);
}

function recipeOf(id) {
  const [kind, key] = id.split(":");
  if (kind === "until" || kind === "timed" || kind === "extra") return data.recipes[kind][key];
  const i = parseInt(kind.replace("pair", ""), 10) - 1;
  return data.recipes.pairs[i][key];
}

const rows = [];
for (const e of expected) {
  const r = recipeOf(e.id);
  let s = CookSim.initial(r);
  const before = fails;
  r.steps.forEach(([name, kw], i) => {
    s = CookSim.applyStep(s, name, kw);
    for (const [k, v] of Object.entries(e.steps[i])) same(v, CookSim.get(s, k), `${e.id} 操作${i + 1} ${k}`);
  });
  same(e.stops.map((x) => [x.until, x.reached, x.minutes]), s.stops.map((x) => [x.until, x.reached, x.minutes]), `${e.id} 停止条件`);
  const v = CookSim.verdict(s);
  same(e.answer, v.answer, `${e.id} 答え`);
  same(e.candidates, v.candidates.map((c) => [c.dish, c.met.length, c.n_total]), `${e.id} 候補`);
  same(e.excluded, v.excluded.map((c) => c.dish), `${e.id} 外した料理`);
  const pv = CookSim.perceive(s);
  for (const [k, x] of Object.entries(e.perception)) same(x, pv[k], `${e.id} 感じ方 ${k}`);
  const nn = CookSim.nearest(pv);
  same(e.nearest.map((x) => x[0]), nn.map((x) => x[0]), `${e.id} 感じ方で近い料理`);
  e.nearest.forEach((x, i) => same(x[1], nn[i][1], `${e.id} 距離${i + 1}`));
  rows.push(`${fails === before ? "✔" : "✘"} ${e.id.padEnd(26)} 答え ${String(v.answer).padEnd(16)} 感じ方で近い料理 ${nn[0][0]}`);
}
// 地図（sim/maps.py ⇄ CookSim.mapGrid）: 最初から用意した4枚を粗い刻みで。マスの分類・1位・2位（満たした数）・迷い度
const expMaps = JSON.parse(fs.readFileSync(path.join(__dirname, "expected_maps.json"), "utf8"));
let nCells = 0;
for (const em of expMaps) {
  const p = data.maps.find((m) => m.id === em.id);
  const x = { ...p.x, step: p.x.step * em.coarsen }, y = { ...p.y, step: p.y.step * em.coarsen };
  const g = CookSim.mapGrid(p.base_recipe, x, y, data.no_match_below);
  const before = fails;
  same(em.xs, g.xs, `地図 ${em.id} 横軸`);
  same(em.ys, g.ys, `地図 ${em.id} 縦軸`);
  em.cells.forEach((row, j) => row.forEach((c, i) => {
    const d = g.cells[j][i];
    nCells++;
    same([c.cls, c.top, c.second], [d.cls, d.top, d.second], `地図 ${em.id} (${i},${j})`);
    same(c.margin, d.margin, `地図 ${em.id} (${i},${j}) 迷い度`);
  }));
  rows.push(`${fails === before ? "✔" : "✘"} 地図 ${em.id.padEnd(21)} ${g.xs.length}×${g.ys.length} マス`);
}
console.log(rows.join("\n"));
console.log(`\n入力 ${expected.length}・地図のマス ${nCells}・比較 ${checks} 件・不一致 ${fails} 件・連続量の最大相対差 ${maxRel.toExponential(2)}`);
process.exit(fails ? 1 : 0);

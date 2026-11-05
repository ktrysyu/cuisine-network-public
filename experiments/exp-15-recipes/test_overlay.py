"""overlay.json（世の中のレシピを Exp-14 の地図に重ねた点）が今の recipes.csv・シミュレータから作ったものと同じか、
ページの JS 版（exp-14/js/sim.js）が同じ点で同じ答えを返すか。

    uv run pytest experiments/exp-15-recipes
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import overlay as O  # noqa: E402

JS = HERE.parent / "exp-14" / "js"


def test_overlay_is_fresh():
    assert json.loads(O.OUT_JSON.read_text(encoding="utf-8")) == json.loads(json.dumps(O.build(), ensure_ascii=False))
    assert O.OUT_MD.read_text(encoding="utf-8") == O.write_md(O.build())


def test_all_map_ok_rows_are_placed():
    d = json.loads(O.OUT_JSON.read_text(encoding="utf-8"))
    assert len(d["points"]) == len(O.load_rows()) == 28
    # 2026-09-28 夜 Q6 (d)・余熱（殻付き卵は後の手順で室温に置く／氷水に取るの地図を選ぶ）
    assert {p["map"] for p in d["points"]} == {"shell_egg", "shell_egg_ice", "poach", "beaten_stir", "pudding"}


def test_mismatches_have_reasons():
    d = json.loads(O.OUT_JSON.read_text(encoding="utf-8"))
    for p in d["points"]:
        assert bool(p["reasons"]) != p["match"], p["row_id"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node が無い")
def test_js_gives_same_answer_at_points():
    code = r"""
const fs = require("fs"), path = require("path");
const JS = process.argv[1], OV = process.argv[2];
const CookSim = require(path.join(JS, "sim.js"));
const data = JSON.parse(fs.readFileSync(path.join(JS, "sim_data.json"), "utf8"));
const ov = JSON.parse(fs.readFileSync(OV, "utf8"));
CookSim.setData(data);
let bad = 0;
for (const p of ov.points) {
  const m = data.maps.find((m) => m.id === p.map);
  const base = JSON.parse(JSON.stringify(m.base_recipe));
  if (p.base_mod) base.steps[p.base_mod.i][1][p.base_mod.key] = p.base_mod.value;
  const r = CookSim.withValue(CookSim.withValue(base, m.x.axis, p.x), m.y.axis, p.y);
  const c = CookSim.mapCell(r, data.no_match_below);
  if (c.cls !== p.answer || JSON.stringify(c.top) !== JSON.stringify(p.top)) { bad++; console.log(p.row_id, c.cls, p.answer); }
}
process.exit(bad ? 1 : 0);
"""
    r = subprocess.run(["node", "-e", code, str(JS), str(O.OUT_JSON)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr

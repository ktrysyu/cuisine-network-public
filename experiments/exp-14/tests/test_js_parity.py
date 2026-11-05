"""JS 版（js/sim.js）が Python 版と同じ結果を返すか。node が無ければ飛ばす。"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

JS = Path(__file__).resolve().parent.parent / "js"
sys.path.insert(0, str(JS))


def test_exported_files_are_fresh():
    """sim_data.json・expected.json・expected_maps.json が今の rules.yaml・シミュレータ・変換から作ったものと同じ。"""
    import export_data as E
    assert json.loads((JS / "sim_data.json").read_text(encoding="utf-8")) == json.loads(json.dumps(E.data(), ensure_ascii=False))
    models = {k: E.data()["perception"]["items"][k] for k in E.PC.ITEMS}
    assert json.loads((JS / "expected.json").read_text(encoding="utf-8")) == json.loads(json.dumps(E.expected(models), ensure_ascii=False))
    assert json.loads((JS / "expected_maps.json").read_text(encoding="utf-8")) == json.loads(json.dumps(E.expected_maps(), ensure_ascii=False))


@pytest.mark.skipif(shutil.which("node") is None, reason="node が無い")
def test_js_matches_python():
    r = subprocess.run(["node", str(JS / "test_parity.js")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]


def test_page_is_fresh():
    """writeup/cook-lab.html が今の sim.js・sim_data.json・page_template.html から組み立てたものと同じ。"""
    import build_page
    assert build_page.OUT.read_text(encoding="utf-8") == build_page.build()


@pytest.mark.skipif(shutil.which("node") is None, reason="node が無い")
def test_page_inputs_rebuild_example_recipes():
    """画面の状態から組み立てたレシピが、例ボタンのレシピと同じ計算結果になる（js/test_page_model.js）。"""
    r = subprocess.run(["node", str(JS / "test_page_model.js")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]

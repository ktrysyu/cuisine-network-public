"""writeup/cook-lab.html を組み立てる（page_template.html に sim.js・page_model.js・sim_data.json と、
Exp-15 の世の中のレシピを地図に重ねる点 overlay.json を埋め込む）。

    uv run python experiments/exp-14/js/export_data.py
    uv run python experiments/exp-15-recipes/overlay.py   # overlay.json（点の答えは sim/maps.py で計算）
    uv run python experiments/exp-14/js/build_page.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent.parent / "writeup" / "cook-lab.html"
OVERLAY = HERE.parent.parent / "exp-15-recipes" / "overlay.json"


def build() -> str:
    tpl = (HERE / "page_template.html").read_text(encoding="utf-8")
    sim = (HERE / "sim.js").read_text(encoding="utf-8")
    page = (HERE / "page_model.js").read_text(encoding="utf-8")
    data = json.loads((HERE / "sim_data.json").read_text(encoding="utf-8"))
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    ov = json.loads(OVERLAY.read_text(encoding="utf-8"))
    ov_blob = json.dumps(ov, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    assert "</script" not in sim and "</script" not in page
    return (tpl.replace("/*__SIM__*/", sim).replace("/*__PAGE__*/", page).replace("/*__DATA__*/", blob)
            .replace("/*__OVERLAY__*/", ov_blob))


def main() -> None:
    OUT.write_text(build(), encoding="utf-8")
    print("wrote", OUT, f"{OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()

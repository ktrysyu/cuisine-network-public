"""Exp-10 フェーズ2: 味覚スコアの 303 食材を Ahn et al. 2011 の食材名に対応づける。

実行: リポジトリ直下で `uv run python experiments/exp-10/build_mapping.py`
出力: data/labels/aroma_mapping.csv（ingredient, aroma_source_name, method, note）

手順
1. 自動: ingredient 名 → canonical の順に、小文字化・空白と '-' を '_' に・語ごとの単数化 で Ahn の食材名と完全一致を探す
2. 手動: MANUAL に書いた対応（Claude が 1 件ずつ Ahn の食材名一覧と化合物数を見て決めた）。自動の結果も上書きできる
3. 対応先なし: NONE に理由を書く

MANUAL と NONE に無い食材で自動対応も無いものがあればエラーにする（黙って none にしない）。
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASTE = ROOT / "data" / "labels" / "taste_scores.csv"
AHN_INFO = ROOT / "data" / "raw" / "ahn2011_zenodo" / "ingr_comp" / "ingr_info.tsv"
OUT = ROOT / "data" / "labels" / "aroma_mapping.csv"

# Ahn らのレシピ（論文補足 s3）での使われ方から推定した寄せ方。Ahn らの置換辞書は公開されていないので「推定」
AHN_SUGAR = "Ahn らのレシピ（s3）では砂糖に当たる名前が cane_molasses しか出てこない（7,655 レシピ）ので同じく寄せた（推定）。精製糖そのものの香り化合物は Ahn の表に無い"
AHN_CHILE = "唐辛子類。Ahn の表に jalapeno・serrano 等の個別項目は無く、Ahn らのレシピ（s3）でも唐辛子に当たる名前は cayenne が大半（7,950 レシピ）なので cayenne に寄せた"

MANUAL: dict[str, tuple[str, str]] = {
    # 砂糖
    "sugar": ("cane_molasses", AHN_SUGAR),
    "white sugar": ("cane_molasses", AHN_SUGAR),
    "granulated sugar": ("cane_molasses", AHN_SUGAR),
    "powdered sugar": ("cane_molasses", AHN_SUGAR),
    "confectioners sugar": ("cane_molasses", AHN_SUGAR),
    "brown sugar": ("cane_molasses", "糖蜜を含む砂糖。cane_molasses（糖蜜）"),
    "light brown sugar": ("cane_molasses", "糖蜜を含む砂糖。cane_molasses（糖蜜）"),
    "dark brown sugar": ("cane_molasses", "糖蜜を含む砂糖。cane_molasses（糖蜜）"),
    # 粉・でんぷん
    "all-purpose flour": ("wheat", "小麦粉 → wheat（Ahn らのレシピでも wheat が 20,782 レシピ）"),
    "flour": ("wheat", "小麦粉 → wheat"),
    "flour tortillas": ("wheat", "小麦粉のトルティーヤ。小麦に寄せた"),
    "corn starch": ("starch", "でんぷん。Ahn の starch（化合物 2）"),
    "cornmeal": ("corn", "とうもろこし粉 → corn"),
    "yellow corn meal": ("corn", "とうもろこし粉 → corn"),
    "tortilla chips": ("corn_tortilla", "揚げたコーントルティーヤ。揚げ油由来の香りは入らない"),
    "spaghetti": ("macaroni", "乾燥パスタ。Ahn の表のパスタ類は macaroni のみ（Ahn らのレシピでも macaroni 3,074）"),
    "pasta": ("macaroni", "乾燥パスタ。Ahn の表のパスタ類は macaroni のみ"),
    "bread crumbs": ("bread", "パン粉 → bread"),
    "dry bread crumbs": ("bread", "パン粉 → bread"),
    "baguette": ("bread", "パン → bread（white_bread もあるが bread crumbs と揃えた）"),
    # 唐辛子・パプリカ
    "chili powder": ("cayenne", "唐辛子に他のスパイス（クミン・オレガノ等）を混ぜた複合スパイス。主成分の唐辛子に寄せた。" + AHN_CHILE),
    "jalapeno chilies": ("cayenne", AHN_CHILE),
    "green chilies": ("cayenne", AHN_CHILE),
    "red chili peppers": ("cayenne", AHN_CHILE),
    "chiles": ("cayenne", AHN_CHILE),
    "serrano chile": ("cayenne", AHN_CHILE),
    "green chile": ("cayenne", AHN_CHILE),
    "chile pepper": ("cayenne", AHN_CHILE),
    "crushed red pepper": ("cayenne", AHN_CHILE),
    "red pepper flakes": ("cayenne", AHN_CHILE),
    "crushed red pepper flakes": ("cayenne", AHN_CHILE),
    "cayenne pepper": ("cayenne", "カイエンペッパー"),
    "ground red pepper": ("cayenne", "赤唐辛子パウダー（canonical が cayenne pepper）"),
    "paprika": ("capsicum_annuum", "パプリカパウダー = Capsicum annuum の乾燥粉。Ahn の capsicum_annuum（化合物 38）"),
    "smoked paprika": ("capsicum_annuum", "燻製したパプリカパウダー。燻製由来の香り（Ahn の smoke）は入らない"),
    "hot sauce": ("tabasco_pepper", "唐辛子と酢のソース。Ahn の tabasco_pepper に寄せた（Ahn らのレシピでも 965 レシピ）。酢の香りは入らない"),
    "hot pepper sauce": ("tabasco_pepper", "同上"),
    # ピーマン: 自動では canonical（bell pepper）経由で bell_pepper になるが、緑のものは Ahn に green_bell_pepper がある
    "green pepper": ("green_bell_pepper", "ピーマン（緑）。自動では canonical 経由で bell_pepper になるが、Ahn に green_bell_pepper があるのでそちらに"),
    "chopped green bell pepper": ("green_bell_pepper", "同上"),
    # ねぎ
    "green onions": ("scallion", "青ねぎ → scallion（化合物 3）"),
    "sliced green onions": ("scallion", "青ねぎ → scallion"),
    "spring onions": ("scallion", "葉玉ねぎ → scallion"),
    # 乳・卵
    "sour cream": ("cream", "サワークリーム。Ahn に項目なし、cream に寄せた（発酵由来の香りは入らない）"),
    "heavy cream": ("cream", "生クリーム → cream"),
    "whipping cream": ("cream", "生クリーム → cream"),
    "half & half": ("cream", "牛乳と生クリームの混合。cream に寄せた"),
    "sweetened condensed milk": ("milk", "加糖練乳。milk に寄せた（加熱・加糖の香りは入らない）"),
    "ghee": ("milk_fat", "澄ましバター。Ahn の milk_fat（化合物 4）。butter（140）の方が化合物は多いが、固形分を除いた乳脂として milk_fat にした"),
    "ricotta cheese": ("cheese", "リコッタの項目なし。総称の cheese（化合物 127）"),
    "shredded monterey jack cheese": ("cheese", "モントレージャックの項目なし。総称の cheese"),
    "large egg yolks": ("egg", "卵黄の項目なし。egg"),
    "egg yolks": ("egg", "卵黄の項目なし。egg"),
    "large egg whites": ("egg", "卵白の項目なし。egg"),
    "egg whites": ("egg", "卵白の項目なし。egg"),
    # 肉・魚
    "ground beef": ("beef", "牛ひき肉 → beef"),
    "lean ground beef": ("beef", "牛ひき肉 → beef"),
    "prosciutto": ("cured_ham", "生ハム → cured_ham"),
    "fish sauce": ("fish", "魚醤。fish に寄せた（発酵由来の香りは入らない）"),
    "oyster sauce": ("oyster", "牡蠣エキスの調味料。oyster に寄せた（糖・塩・加熱の香りは入らない）"),
    # 野菜・豆・果物
    "tomato paste": ("tomato", "トマトの加工品 → tomato（加熱濃縮の香りは入らない）"),
    "tomato sauce": ("tomato", "トマトの加工品 → tomato"),
    "coconut milk": ("coconut", "ココナッツミルク → coconut"),
    "beansprouts": ("mung_bean", "もやし（緑豆もやし）→ mung_bean。発芽の違いは入らない"),
    "green beans": ("snap_bean", "さやいんげん = snap bean"),
    "radishes": ("radish", "ラディッシュ → radish"),
    "romaine lettuce": ("lettuce", "ロメインレタス → lettuce（化合物 7）"),
    "spinach": ("dried_spinach", "生のほうれん草の項目なし。dried_spinach（化合物 1）で代用"),
    "grated lemon zest": ("lemon_peel", "レモンの皮 → lemon_peel"),
    # スパイス・ハーブ
    "vanilla extract": ("vanilla", "バニラエッセンス → vanilla"),
    "bay leaves": ("laurel", "ローリエ = Laurus nobilis。Ahn には bay（化合物 1）・bay_laurel（4）・laurel（34）がある。最も化合物の多い laurel にした"),
    "bay leaf": ("laurel", "同上"),
    "ground allspice": ("pimento", "オールスパイス（Pimenta dioica）の英名の一つが pimento。Ahn の pimento（13）を採った。pimenta（1）もある。Ahn の pimento がピメント（唐辛子）の意味で使われている可能性は未確認"),
    "fennel seeds": ("fennel", "フェンネルシード → fennel"),
    "white pepper": ("pepper", "白胡椒。Ahn に white_pepper の項目はあるが化合物 0。pepper（36）にした"),
    "ground white pepper": ("pepper", "同上"),
    "mustard seeds": ("mustard", "マスタードシード → mustard"),
    "dijon mustard": ("mustard", "ディジョンマスタード → mustard（酢・ワインの香りは入らない）"),
    # 酢・酒
    "rice vinegar": ("vinegar", "米酢 → vinegar（原料の違いは入らない）"),
    "balsamic vinegar": ("vinegar", "バルサミコ酢 → vinegar（ぶどう・熟成の香りは入らない）"),
    "cider vinegar": ("vinegar", "りんご酢 → vinegar。Ahn の cider（りんご酒）には寄せなかった"),
    "apple cider vinegar": ("vinegar", "同上"),
}

NONE: dict[str, str] = {
    "salt": "塩。無機物で香り化合物なし（Ahn の表にも無い）",
    "kosher salt": "塩",
    "sea salt": "塩",
    "coarse salt": "塩",
    "fine sea salt": "塩",
    "water": "水",
    "warm water": "水",
    "cold water": "水",
    "hot water": "水",
    "boiling water": "水",
    "baking powder": "膨張剤（無機塩）",
    "baking soda": "膨張剤（重曹）",
    "mirin": "みりん。Ahn の表に項目なし（近いものに sake・rice・cane_molasses があるが、どれかに寄せると別物になる）",
    "eggplant": "なす。Ahn の表に項目なし",
    "capers": "ケッパー。Ahn の表に項目なし",
    "tomatillos": "トマティーヨ。Ahn の表に項目なし",
    "pinenuts": "松の実。Ahn の表に項目なし（pine は松の精油類のみ）",
    "salsa": "複合調味料（トマト・玉ねぎ・唐辛子など）",
    "garam masala": "複合スパイス",
    "curry powder": "複合スパイス",
    "italian seasoning": "複合スパイス（ハーブ類の混合）",
    "cajun seasoning": "複合スパイス",
    "creole seasoning": "複合スパイス",
    "taco seasoning": "複合スパイス",
    "mayonaise": "複合調味料（卵・油・酢）",
    "worcestershire sauce": "複合調味料",
    "ketchup": "複合調味料（トマト・砂糖・酢）",
    "hoisin sauce": "複合調味料",
    "sriracha": "複合調味料（唐辛子・にんにく・砂糖・酢）",
    "enchilada sauce": "複合調味料",
    "vegetable broth": "複合（野菜の煮出し。具体的な野菜が決まらない）",
    "sauce": "曖昧（What's Cooking で 'sauce' とだけ書かれたもの）",
    "juice": "曖昧（何の果汁か不明）",
}


def norm(s: str) -> str:
    return "_".join(s.lower().replace("-", " ").split())


def singular(s: str) -> str:
    out = []
    for w in s.split("_"):
        if w.endswith("ies"):
            w = w[:-3] + "y"
        elif w.endswith("oes"):
            w = w[:-2]
        elif w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return "_".join(out)


def auto_match(name: str, ahn: set[str]) -> str | None:
    for f in (norm, lambda x: singular(norm(x))):
        if f(name) in ahn:
            return f(name)
    return None


def read_ahn_names() -> set[str]:
    names = set()
    for line in AHN_INFO.open():
        if line.startswith("#"):
            continue
        names.add(line.rstrip("\n").split("\t")[1])
    names.discard("farnesol")   # zip 内 README の既知の問題（食材と化合物の両方にある）
    return names


def build() -> list[dict]:
    ahn = read_ahn_names()
    rows = list(csv.DictReader(TASTE.open()))
    out, unresolved = [], []
    assert not (set(MANUAL) & set(NONE))
    for r in rows:
        t, c = r["ingredient"], r["canonical"]
        if t in NONE:
            out.append({"ingredient": t, "aroma_source_name": "", "method": "none", "note": NONE[t]})
            continue
        if t in MANUAL:
            name, note = MANUAL[t]
            assert name in ahn, (t, name)
            out.append({"ingredient": t, "aroma_source_name": name, "method": "manual", "note": note})
            continue
        m = auto_match(t, ahn)
        if m:
            out.append({"ingredient": t, "aroma_source_name": m, "method": "auto", "note": "ingredient 名の正規化で一致"})
            continue
        m = auto_match(c, ahn)
        if m:
            out.append({"ingredient": t, "aroma_source_name": m, "method": "auto",
                        "note": f"canonical（{c}）の正規化で一致"})
            continue
        unresolved.append(t)
    unused = (set(MANUAL) | set(NONE)) - {r["ingredient"] for r in rows}
    if unresolved or unused:
        sys.exit(f"未解決: {unresolved}\n辞書にあるが 303 食材に無い: {sorted(unused)}")
    return out


def main():
    out = build()
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ingredient", "aroma_source_name", "method", "note"])
        w.writeheader()
        w.writerows(out)
    from collections import Counter
    cnt = Counter(r["method"] for r in out)
    n = len(out)
    print(f"{n} 食材: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())) +
          f"。対応率 {(n - cnt['none']) / n:.1%}。対応先の Ahn 食材 {len({r['aroma_source_name'] for r in out if r['aroma_source_name']})} 種")


if __name__ == "__main__":
    main()

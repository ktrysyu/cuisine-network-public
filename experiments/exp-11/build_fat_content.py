"""Exp-11 油分の層の客観値: 303食材の脂質量（g/100g）を USDA FoodData Central（SR Legacy）から引く（2026-09-28 夜、Q10）。

    uv run python experiments/exp-11/build_fat_content.py

- 入力: data/raw/usda_fdc/FoodData_Central_sr_legacy_food_csv_2018-04/（food.csv・food_nutrient.csv。取り直し方は data/SOURCES.md）、
  data/labels/taste_scores.csv（303食材と日本語名・味覚スコア）
- 出力: data/labels/fat_content.csv
- 脂質量は nutrient_id 1004「Total lipid (fat)」（g/100g、SR Legacy の値そのまま）
- 食材ごとの対応（下の MAP）は Claude が SR Legacy の品名を検索して決めた。対応の確かさを `match` 列に書く:
    一致 = 同じ食品（形・加工も同じ）／ 近い = 同じ食品だが形・加工・品種が書かれていない等で1つに決めた／
    代用 = SR Legacy に同じ食品が無く、近い別の食品の値を使った
  対応できない食材は fdc_id を空け、`note` に理由を書く（推測で埋めない）
- 日本食品標準成分表（八訂）は使っていない（What's Cooking の食材名が英語で、米国の商品形態に合う SR Legacy のほうが対応が近い。記録: data/SOURCES.md）
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FDC = ROOT / "data" / "raw" / "usda_fdc" / "FoodData_Central_sr_legacy_food_csv_2018-04"
TASTE = ROOT / "data" / "labels" / "taste_scores.csv"
OUT = ROOT / "data" / "labels" / "fat_content.csv"
FAT_NUTRIENT_ID = "1004"   # Total lipid (fat), g

E, N, S = "一致", "近い", "代用"
# ingredient → (fdc_id, match, note)。fdc_id が None なら対応できない（note に理由）
MAP: dict[str, tuple[str | None, str, str]] = {
    # 塩・水
    "salt": ("173468", E, ""), "kosher salt": ("173468", N, "食卓塩の値（塩は脂質 0）"), "sea salt": ("173468", N, "食卓塩の値"),
    "coarse salt": ("173468", N, "食卓塩の値"), "fine sea salt": ("173468", N, "食卓塩の値"),
    "water": ("173647", E, ""), "warm water": ("173647", E, ""), "cold water": ("173647", E, ""), "hot water": ("173647", E, ""),
    "boiling water": ("173647", E, ""),
    # 玉ねぎ・ねぎ・にんにく
    "onions": ("170000", E, ""), "purple onion": ("170000", N, "玉ねぎ全般の値（赤玉ねぎの項目なし）"), "yellow onion": ("170000", N, "玉ねぎ全般の値"),
    "chopped onion": ("170000", E, ""), "white onion": ("170000", N, "玉ねぎ全般の値"), "finely chopped onion": ("170000", E, ""),
    "sweet onion": ("170000", N, "玉ねぎ全般の値"), "onion powder": ("171327", E, ""),
    "green onions": ("170005", E, ""), "scallions": ("170005", E, ""), "sliced green onions": ("170005", E, ""), "spring onions": ("170005", E, ""),
    "shallots": ("170499", E, ""), "leeks": ("169246", E, ""),
    "garlic": ("169230", E, ""), "garlic cloves": ("169230", E, ""), "minced garlic": ("169230", E, ""), "large garlic cloves": ("169230", E, ""),
    "chopped garlic": ("169230", E, ""), "garlic powder": ("171325", E, ""),
    "garlic paste": ("169230", N, "生のにんにくの値。市販のペーストは油を含むことがある"),
    # 油脂
    "olive oil": ("171413", E, ""), "extra-virgin olive oil": ("171413", N, "オリーブ油全般の値"),
    "vegetable oil": ("172370", N, "大豆油（精製）の値。植物油の種類が書かれていない"), "oil": ("172370", N, "大豆油の値。油の種類が書かれていない"),
    "cooking oil": ("172370", N, "大豆油の値。油の種類が書かれていない"), "canola oil": ("172336", E, ""), "peanut oil": ("171410", E, ""),
    "sesame oil": ("171016", E, ""), "toasted sesame oil": ("171016", N, "ごま油（焙煎の区別なし）の値"),
    "cooking spray": ("171430", N, "PAM（商品名）の値。噴射剤を含む"),
    "butter": ("173410", E, ""), "unsalted butter": ("173430", E, ""), "melted butter": ("173410", N, "有塩バターの値（溶かしても脂質は同じ）"),
    "ghee": ("171314", E, ""),
    # 砂糖・甘味
    "sugar": ("169655", E, ""), "white sugar": ("169655", E, ""), "granulated sugar": ("169655", E, ""),
    "brown sugar": ("168833", E, ""), "light brown sugar": ("168833", N, "ブラウンシュガー全般の値"), "dark brown sugar": ("168833", N, "ブラウンシュガー全般の値"),
    "powdered sugar": ("169656", E, ""), "confectioners sugar": ("169656", E, ""), "honey": ("169640", E, ""),
    "sweetened condensed milk": ("171275", E, ""),
    # 粉・でんぷん・膨張剤
    "all-purpose flour": ("168894", E, ""), "flour": ("168894", N, "中力粉（オールパーパス、漂白）の値。粉の種類が書かれていない"),
    "corn starch": ("169698", E, ""), "cornmeal": ("168867", N, "脱胚芽・黄の値"), "yellow corn meal": ("168867", N, "脱胚芽の値（全粒なら 3.59）"),
    "baking powder": ("172804", E, ""), "baking soda": ("175040", E, ""), "active dry yeast": ("175043", E, ""),
    "bread crumbs": ("174928", N, "乾燥パン粉（プレーン）の値"), "dry bread crumbs": ("174928", E, ""),
    # 卵・乳
    "eggs": ("171287", E, ""), "large eggs": ("171287", E, ""), "egg yolks": ("172184", E, ""), "large egg yolks": ("172184", E, ""),
    "egg whites": ("172183", E, ""), "large egg whites": ("172183", E, ""),
    "milk": ("171265", N, "全乳の値。脂肪の割合が書かれていない"), "whole milk": ("171265", E, ""),
    "buttermilk": ("170874", N, "低脂肪の発酵バターミルク（米国の一般的な市販品）の値"),
    "heavy cream": ("170859", E, ""), "whipping cream": ("170858", N, "ライトホイッピングクリームの値（ヘビーなら 36.08）"),
    "half & half": ("171255", E, ""), "sour cream": ("171257", E, ""), "plain yogurt": ("171284", N, "全乳ヨーグルトの値"),
    "cream cheese": ("173418", E, ""),
    "grated parmesan cheese": ("171247", E, ""), "parmesan cheese": ("170848", N, "パルメザン（ハード）の値"),
    "parmigiano reggiano cheese": ("170848", N, "パルメザン（ハード）の値"), "fresh parmesan cheese": ("170848", N, "パルメザン（ハード）の値"),
    "shredded cheddar cheese": ("173414", E, ""), "cheddar cheese": ("173414", E, ""),
    "shredded mozzarella cheese": ("171244", N, "低水分・部分脱脂（シュレッドの一般的な形）の値"), "mozzarella cheese": ("170845", N, "全乳の値"),
    "shredded monterey jack cheese": ("170844", E, ""), "feta cheese crumbles": ("173420", E, ""), "feta cheese": ("173420", E, ""),
    "ricotta cheese": ("170851", N, "全乳の値"),
    "cheese": (None, "", "チーズの種類が書かれていない（脂質は 0〜35 と幅が大きい）"),
    # 肉・魚介
    "boneless skinless chicken breasts": ("171077", E, ""), "boneless skinless chicken breast halves": ("171077", E, ""),
    "chicken breasts": ("171077", N, "皮なし骨なしの値。皮の有無が書かれていない（皮つきなら 9.25）"),
    "chicken": ("171052", N, "肉のみ（部位の平均）の値。部位・皮の有無が書かれていない（皮つきなら 15.06）"),
    "chicken thighs": ("173627", N, "もも肉・肉のみの値。皮の有無が書かれていない（皮つきなら 16.61）"),
    "boneless chicken skinless thigh": ("173627", E, ""), "cooked chicken": ("171054", N, "肉のみ・ローストの値"),
    "ground beef": ("174036", N, "赤身80%/脂肪20%（米国のひき肉の代表）の値"), "lean ground beef": ("174030", N, "赤身90%/脂肪10%の値"),
    "beef": ("169483", N, "市販の部位の平均（脂身 1/8 インチまで）の値。部位が書かれていない"),
    "ground pork": ("167902", E, ""), "pork": ("168316", N, "ロース・肩の平均（脂身つき）の値。部位が書かれていない"),
    "bacon": ("168277", E, ""),
    "prosciutto": (None, "", "SR Legacy に乾燥熟成の生ハムの項目が無い（ハムは湿式の塩漬けだけで、脂身の有無で 4〜53 と幅が大きい）"),
    "shrimp": ("175179", E, ""), "medium shrimp": ("175179", E, ""), "large shrimp": ("175179", E, ""),
    # 野菜・果物
    "tomatoes": ("170457", E, ""), "plum tomatoes": ("170457", N, "トマト（通年平均）の値"), "cherry tomatoes": ("170457", N, "トマト（通年平均）の値"),
    "chopped tomatoes": ("170457", E, ""), "diced tomatoes": ("170051", N, "缶詰（トマトジュース漬け）の値"),
    "crushed tomatoes": ("170051", N, "缶詰（トマトジュース漬け）の値"), "tomato paste": ("170459", E, ""), "tomato sauce": ("170054", E, ""),
    "tomatillos": ("168566", E, ""),
    "carrots": ("170393", E, ""), "potatoes": ("170026", E, ""), "sweet potatoes": ("168482", E, ""), "celery": ("169988", E, ""),
    "celery ribs": ("169988", E, ""), "chopped celery": ("169988", E, ""), "cucumber": ("168409", E, ""), "zucchini": ("169291", E, ""),
    "eggplant": ("169228", E, ""), "cabbage": ("169975", E, ""), "spinach": ("168462", E, ""), "romaine lettuce": ("169247", E, ""),
    "radishes": ("169276", E, ""), "okra": ("169260", E, ""), "green beans": ("169961", E, ""), "beansprouts": ("169957", N, "緑豆もやしの値"),
    "mushrooms": ("169251", N, "ホワイトマッシュルームの値"), "fresh mushrooms": ("169251", N, "ホワイトマッシュルームの値"), "shiitake": ("169242", E, ""),
    "corn": ("169998", N, "スイートコーン（生）の値"), "corn kernels": ("169998", N, "スイートコーン（生）の値。缶詰なら 1.22"),
    "frozen peas": ("170016", E, ""), "avocado": ("171705", E, ""), "lemongrass": ("168573", E, ""),
    "red bell pepper": ("170108", E, ""), "green bell pepper": ("170427", E, ""), "green pepper": ("170427", E, ""),
    "chopped green bell pepper": ("170427", E, ""), "yellow bell pepper": ("169383", E, ""),
    "bell pepper": ("170427", N, "緑の値。色が書かれていない（赤 0.30・黄 0.21）"),
    "red pepper": (None, "", "赤唐辛子か赤パプリカか決まらない（ingredient_ja でも両方）"),
    "jalapeno chilies": ("168576", E, ""), "green chilies": ("170497", E, ""), "green chile": ("170497", E, ""),
    "red chili peppers": ("170106", E, ""), "serrano chile": ("169395", E, ""),
    "chile pepper": ("170106", N, "赤唐辛子（生）の値。色が書かれていない（青 0.20）"),
    "chiles": ("170106", N, "赤唐辛子（生）の値。色・生か乾燥かが書かれていない"),
    "lime": ("168155", E, ""), "lime wedges": ("168155", E, ""), "lemon": ("167746", E, ""), "orange": ("169097", E, ""),
    "mango": ("169910", E, ""), "raisins": ("168165", N, "種なし（ダーク）の値"),
    "fresh lemon juice": ("167747", E, ""), "lemon juice": ("167747", N, "生搾りの値（濃縮還元なら 0.07）"),
    "fresh lime juice": ("168156", E, ""), "lime juice": ("168156", N, "生搾りの値"), "orange juice": ("169098", N, "生搾りの値"),
    "grated lemon zest": ("167749", E, ""),
    "juice": (None, "", "何の果汁か書かれていない"),
    # 豆・種・ナッツ
    "black beans": ("173735", N, "乾燥豆をゆでたものの値。缶詰か乾燥か書かれていない（乾燥のままなら 1.42）"),
    "chickpeas": ("173800", N, "缶詰（水を切ったもの）の値。缶詰か乾燥か書かれていない（乾燥なら 6.04）"),
    "peanuts": ("172430", E, ""), "pinenuts": ("170591", E, ""), "chopped pecans": ("170182", E, ""),
    "sesame seeds": ("170150", E, ""), "toasted sesame seeds": ("170151", E, ""),
    # 米・麺・パン
    "rice": ("168877", N, "長粒米（生、強化）の値。品種が書かれていない"), "long-grain rice": ("168877", E, ""),
    "long grain white rice": ("168877", E, ""), "basmati rice": ("168877", N, "長粒米の値（バスマティの項目なし）"),
    "arborio rice": ("168879", N, "中粒米（生）の値"), "cooked rice": ("168878", N, "長粒米を炊いたものの値"),
    "spaghetti": ("169736", E, ""), "pasta": ("169736", E, ""),
    "corn tortillas": ("175036", E, ""), "flour tortillas": ("175037", N, "冷蔵の値"), "tortilla chips": ("167558", E, ""),
    "baguette": ("172675", N, "フランスパン（サワードウ含む）の値"),
    # ハーブ・スパイス
    "ground black pepper": ("170931", E, ""), "pepper": ("170931", N, "黒胡椒の値"), "black pepper": ("170931", E, ""),
    "freshly ground pepper": ("170931", E, ""), "black peppercorns": ("170931", E, ""), "cracked black pepper": ("170931", E, ""),
    "ground pepper": ("170931", E, ""), "white pepper": ("170933", E, ""), "ground white pepper": ("170933", E, ""),
    "ground cumin": ("170923", E, ""), "cumin": ("170923", E, ""), "cumin seed": ("170923", E, ""),
    "chili powder": ("171319", E, ""), "cayenne pepper": ("170932", E, ""), "cayenne": ("170932", E, ""), "ground red pepper": ("170932", E, ""),
    "crushed red pepper": ("170932", N, "カイエン（粉）の値（同じ唐辛子を粗く砕いたもの）"),
    "red pepper flakes": ("170932", N, "カイエン（粉）の値"), "crushed red pepper flakes": ("170932", N, "カイエン（粉）の値"),
    "paprika": ("171329", E, ""), "smoked paprika": ("171329", N, "パプリカの値（燻製の区別なし）"),
    "ground cinnamon": ("171320", E, ""), "cinnamon": ("171320", E, ""), "cinnamon sticks": ("171320", N, "粉の値"),
    "ground turmeric": ("172231", E, ""), "tumeric": ("172231", E, ""),
    "ground ginger": ("170926", E, ""), "ginger": ("169231", E, ""), "fresh ginger": ("169231", E, ""), "peeled fresh ginger": ("169231", E, ""),
    "fresh ginger root": ("169231", E, ""),
    "ground coriander": ("170922", E, ""), "coriander seeds": ("170922", E, ""),
    "coriander": (None, "", "種（スパイス）か葉（パクチー）か決まらない（種 17.77・葉 0.52）"),
    "ground nutmeg": ("171326", E, ""), "clove": ("171321", N, "粉の値"), "ground cloves": ("171321", E, ""),
    "ground allspice": ("171315", E, ""), "fennel seeds": ("171323", E, ""), "mustard seeds": ("170929", N, "粉の値"),
    "saffron threads": ("170934", E, ""), "bay leaves": ("170917", E, ""), "bay leaf": ("170917", E, ""),
    "curry powder": ("170924", E, ""), "taco seasoning": ("172243", N, "タコス用ミックス（乾燥、商品の平均）の値"),
    "garam masala": (None, "", "混合スパイス。SR Legacy に項目が無く、配合で変わる"),
    "italian seasoning": (None, "", "混合ハーブ。SR Legacy に項目が無い"),
    "cajun seasoning": (None, "", "混合スパイス。SR Legacy に項目が無い"),
    "creole seasoning": (None, "", "混合スパイス。SR Legacy に項目が無い"),
    "dried oregano": ("171328", E, ""), "oregano": ("171328", N, "乾燥の値。生か乾燥かが書かれていない"),
    "fresh oregano": (None, "", "SR Legacy に生のオレガノが無い（乾燥 4.28 は水分が違うので代用しない）"),
    "dried thyme": ("170938", E, ""), "thyme": ("173470", N, "生の値。生か乾燥かが書かれていない（乾燥 7.43）"),
    "fresh thyme": ("173470", E, ""), "chopped fresh thyme": ("173470", E, ""),
    "dried basil": ("171317", E, ""), "fresh basil": ("172232", E, ""), "basil": ("172232", N, "生の値。生か乾燥かが書かれていない"),
    "fresh basil leaves": ("172232", E, ""),
    "chopped cilantro fresh": ("169997", E, ""), "cilantro leaves": ("169997", E, ""), "cilantro": ("169997", E, ""),
    "fresh cilantro": ("169997", E, ""), "chopped cilantro": ("169997", E, ""), "fresh coriander": ("169997", E, ""),
    "fresh parsley": ("170416", E, ""), "flat leaf parsley": ("170416", N, "パセリ全般の値"), "parsley": ("170416", E, ""),
    "chopped parsley": ("170416", E, ""),
    "fresh mint": ("173475", N, "スペアミントの値（ペパーミント 0.94）"), "chopped fresh mint": ("173475", N, "スペアミントの値"),
    "fresh rosemary": ("173473", E, ""),
    "vanilla extract": ("173471", E, ""), "vanilla": ("173471", N, "バニラエキストラクトの値"),
    # 調味料・ソース・酒
    "soy sauce": ("174277", E, "大豆と小麦の醤油"), "low sodium soy sauce": ("172473", E, ""),
    "light soy sauce": ("174277", S, "SR Legacy に薄口醤油が無い。濃口（大豆と小麦）の値"),
    "dark soy sauce": ("174277", S, "SR Legacy に老抽が無い。醤油（大豆と小麦）の値"),
    "fish sauce": ("174531", E, ""), "oyster sauce": ("174529", E, ""), "hoisin sauce": ("172886", E, ""),
    "worcestershire sauce": ("171610", E, ""), "ketchup": ("168556", E, ""), "mayonaise": ("171009", E, ""),
    "hot sauce": ("174527", E, ""), "hot pepper sauce": ("174527", E, ""), "sriracha": ("171186", E, ""),
    "salsa": ("174524", E, ""), "enchilada sauce": ("174074", N, "赤・マイルドの値"),
    "dijon mustard": ("172234", S, "SR Legacy にディジョンマスタードが無い。イエローマスタードの値"),
    "capers": ("172238", E, ""),
    "sauce": (None, "", "何のソースか書かれていない"),
    "vinegar": ("172237", N, "蒸留酢の値"), "white vinegar": ("172237", E, ""), "red wine vinegar": ("172240", E, ""),
    "white wine vinegar": ("172240", S, "SR Legacy に白ワインビネガーが無い。赤ワインビネガーの値（酢は脂質 0）"),
    "rice vinegar": ("172237", S, "SR Legacy に米酢が無い。蒸留酢の値（酢は脂質 0）"),
    "balsamic vinegar": ("172241", E, ""), "cider vinegar": ("173469", E, ""), "apple cider vinegar": ("173469", E, ""),
    "chicken broth": ("174536", E, ""), "chicken stock": ("172884", N, "家庭で作ったストックの値"),
    "fat free less sodium chicken broth": ("172888", E, ""), "low salt chicken broth": ("171609", N, "減塩（缶詰）の値"),
    "low sodium chicken broth": ("171609", E, ""), "beef broth": ("171538", E, ""), "vegetable broth": ("171583", E, ""),
    "coconut milk": ("170173", E, ""),
    "dry white wine": ("174837", N, "白ワイン全般の値"), "white wine": ("174837", E, ""), "dry red wine": ("173190", N, "赤ワイン全般の値"),
    "sake": ("167723", E, ""),
    "mirin": (None, "", "SR Legacy にみりんが無い（糖を含む酒で、ほかの酒で代用できない）"),
}


def fdc_tables():
    with (FDC / "food.csv").open(encoding="utf-8") as f:
        food = {r["fdc_id"]: r["description"] for r in csv.DictReader(f)}
    with (FDC / "food_nutrient.csv").open(encoding="utf-8") as f:
        fat = {r["fdc_id"]: float(r["amount"]) for r in csv.DictReader(f) if r["nutrient_id"] == FAT_NUTRIENT_ID}
    return food, fat


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return cov / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))


def build() -> tuple[list[dict], dict]:
    food, fat = fdc_tables()
    with TASTE.open(encoding="utf-8") as f:
        taste = list(csv.DictReader(f))
    missing = [r["ingredient"] for r in taste if r["ingredient"] not in MAP]
    assert not missing, f"MAP に無い食材: {missing}"
    rows = []
    for r in taste:
        fid, match, note = MAP[r["ingredient"]]
        rows.append({
            "ingredient": r["ingredient"], "ja": r["ja"], "canonical": r["canonical"],
            "fat_g_per_100g": "" if fid is None else f"{fat[fid]:g}",
            "fdc_id": fid or "", "fdc_description": food.get(fid, "") if fid else "",
            "match": match if fid else "対応なし", "note": note,
        })
    got = [x for x in rows if x["fat_g_per_100g"] != ""]
    tmap = {r["ingredient"]: r for r in taste}
    stats = {"n": len(rows), "got": len(got), "by_match": {m: sum(x["match"] == m for x in rows) for m in (E, N, S, "対応なし")}}
    fats = [float(x["fat_g_per_100g"]) for x in got]
    for k in ("sweet", "salty", "sour", "bitter", "umami", "spicy"):
        stats[f"rho_{k}"] = spearman(fats, [float(tmap[x["ingredient"]][k]) for x in got])
    return rows, stats


def main() -> None:
    rows, st = build()
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("wrote", OUT, st)


if __name__ == "__main__":
    main()

"""食材ごとの食感スコアの下書き（2026-10-22、night-queue「食感スコアの下書き＋確認ページ」）。値を決めるのは本人。

    uv run python experiments/exp-11/draft_texture_ingredients.py

- 対象は味覚スコアと同じ 303 食材。項目は Exp-11 plan.md の候補（硬さ・粘り/とろみ・みずみずしさ・歯ごたえ・なめらかさ、0〜5）
- 「料理でふつうに使う形」で付ける（生で食べる野菜は生、ふつう加熱する野菜・肉は加熱後）。どの形を想定したかを form 列に書く
- 作り方: 食材を種類に分け、種類ごとの値（Claude の推定。出典なし）を当てる。種類の中で違いが大きいものは個別に直した（OVERRIDE）
- 粉・香辛料・塩・砂糖・膨張剤など、そのまま食感を感じない食材は空欄（対象外）
出力: data/labels/texture_draft.csv
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "labels" / "texture_draft.csv"
ITEMS = ["hardness", "thickness", "juiciness", "chewiness", "smoothness"]

# 種類: (想定する形, 硬さ, 粘り・とろみ, みずみずしさ, 歯ごたえ, なめらかさ)
GROUPS = {
    "na": ("対象外（粉・香辛料・調味の粒。そのまま食感を感じない）", None, None, None, None, None),
    "water": ("液体（水・湯）", 0, 0, 5, 0, 5),
    "oil": ("液体（油）", 0, 1, 1, 0, 5),
    "thin_liquid": ("液体（酢・酒・果汁・ブロス・醤油など）", 0, 0, 5, 0, 5),
    "thick_liquid": ("とろみのある液体（ソース・クリーム・はちみつなど）", 0, 3, 3, 0, 5),
    "paste": ("ペースト（トマトペースト・マヨネーズなど）", 1, 4, 2, 0, 4),
    "butter": ("脂（冷蔵のバター・ギー、口で溶ける）", 1, 2, 1, 0, 5),
    "egg": ("加熱した卵（料理による。ゆで卵・炒り卵の中間を想定）", 2, 1, 3, 1, 4),
    "egg_raw_part": ("卵の一部（料理に混ぜて使う。生の状態）", 0, 3, 3, 0, 5),
    "soft_cheese": ("やわらかいチーズ（クリームチーズ・リコッタなど）", 1, 3, 2, 0, 4),
    "hard_cheese": ("硬いチーズ（チェダー・パルメザンの塊）", 3, 0, 1, 2, 2),
    "melt_cheese": ("加熱して溶かしたチーズ（モッツァレラ・シュレッド）", 1, 4, 2, 3, 3),
    "dairy_liquid": ("乳（牛乳・ヨーグルトなど）", 0, 1, 5, 0, 5),
    "raw_crisp_veg": ("生で食べるみずみずしい野菜（きゅうり・レタス・ラディッシュ）", 3, 0, 5, 3, 2),
    "cooked_veg": ("加熱した野菜（玉ねぎ・にんじん・ピーマン類）", 2, 1, 4, 2, 2),
    "soft_cooked_veg": ("加熱するとやわらかくなる野菜（なす・ズッキーニ・トマト）", 1, 2, 5, 1, 3),
    "leafy": ("加熱した葉物（ほうれん草・キャベツ・もやし）", 1, 1, 4, 2, 2),
    "herb": ("生の香草（量が少なく食感は小さい）", 1, 0, 3, 1, 2),
    "aromatic": ("香味野菜（にんにく・生姜・エシャロット、刻んで加熱）", 2, 1, 3, 1, 2),
    "chili_fresh": ("生の唐辛子（刻んで使う）", 2, 0, 4, 2, 2),
    "potato": ("加熱したいも（じゃがいも・さつまいも）", 2, 1, 2, 1, 3),
    "fruit": ("果物（生）", 1, 1, 5, 1, 3),
    "citrus_piece": ("柑橘（くし切り・皮。搾って使う）", 2, 0, 5, 2, 1),
    "legume": ("加熱した豆（ひよこ豆・黒いんげん豆）", 2, 1, 2, 2, 3),
    "grain_cooked": ("炊いた・ゆでた穀物（ご飯・パスタ）", 2, 2, 3, 3, 3),
    "grain_raw": ("乾いた穀物（米・パスタの乾燥。加熱して使う）", None, None, None, None, None),
    "bread": ("パン・トルティーヤ", 2, 0, 1, 3, 2),
    "crisp": ("揚げた・乾いたもの（チップス・パン粉）", 3, 0, 0, 2, 1),
    "nut": ("ナッツ・種（ローストして使う）", 4, 0, 0, 3, 1),
    "meat": ("加熱した肉（焼く・煮る）", 4, 0, 3, 4, 1),
    "ground_meat": ("加熱したひき肉", 3, 0, 3, 3, 1),
    "shrimp": ("加熱したえび", 3, 0, 4, 4, 2),
    "cured_meat": ("ベーコン・生ハム", 3, 0, 2, 4, 1),
    "mushroom": ("加熱したきのこ", 2, 1, 4, 3, 2),
    "dried_fruit": ("干した果物（レーズン）", 2, 2, 1, 3, 2),
    "sweet_condensed": ("加糖練乳", 0, 5, 2, 0, 5),
    "corn": ("加熱したとうもろこしの粒", 2, 1, 4, 3, 2),
    "okra": ("加熱したオクラ（粘りがある）", 2, 4, 4, 2, 3),
    "avocado": ("アボカド（生）", 1, 2, 2, 0, 5),
    "mango": ("マンゴー（生）", 1, 2, 5, 1, 4),
}

ASSIGN = """
salt na|onions cooked_veg|olive oil oil|water water|garlic aromatic|sugar na|garlic cloves aromatic|butter butter|ground black pepper na|
all-purpose flour na|pepper na|vegetable oil oil|eggs egg|soy sauce thin_liquid|kosher salt na|green onions herb|tomatoes soft_cooked_veg|large eggs egg|
carrots cooked_veg|unsalted butter butter|extra-virgin olive oil oil|ground cumin na|black pepper na|milk dairy_liquid|chili powder na|oil oil|
red bell pepper cooked_veg|purple onion raw_crisp_veg|scallions herb|grated parmesan cheese na|sesame oil oil|corn starch na|ginger aromatic|baking powder na|
jalapeno chilies chili_fresh|dried oregano na|chopped cilantro fresh herb|fresh lemon juice thin_liquid|diced tomatoes soft_cooked_veg|fresh parsley herb|
minced garlic aromatic|chicken broth thin_liquid|sour cream thick_liquid|cayenne pepper na|brown sugar na|fresh ginger aromatic|cooking spray oil|shallots aromatic|
garlic powder na|lime citrus_piece|lemon juice thin_liquid|fresh lime juice thin_liquid|flour na|honey thick_liquid|vanilla extract thin_liquid|paprika na|
chopped onion cooked_veg|fish sauce thin_liquid|ground cinnamon na|avocado avocado|canola oil oil|dry white wine thin_liquid|lemon citrus_piece|rice vinegar thin_liquid|
yellow onion cooked_veg|green bell pepper cooked_veg|cilantro leaves herb|tomato paste paste|heavy cream thick_liquid|cilantro herb|fresh basil herb|
boneless skinless chicken breasts meat|flat leaf parsley herb|white sugar na|lime juice thin_liquid|chicken stock thin_liquid|bay leaves na|potatoes potato|chicken meat|
corn tortillas bread|salsa thick_liquid|cumin na|freshly ground pepper na|ground turmeric na|baking soda na|sea salt na|cumin seed na|garam masala na|shrimp shrimp|
black beans legume|zucchini soft_cooked_veg|ground beef ground_meat|dried thyme na|large garlic cloves aromatic|flour tortillas bread|tomato sauce thick_liquid|
buttermilk dairy_liquid|plum tomatoes soft_cooked_veg|coconut milk thick_liquid|granulated sugar na|fresh cilantro herb|bay leaf na|celery raw_crisp_veg|
crushed red pepper na|chopped cilantro herb|chicken breasts meat|mayonaise paste|shredded cheddar cheese melt_cheese|cucumber raw_crisp_veg|green chilies chili_fresh|
ground coriander na|whole milk dairy_liquid|red wine vinegar thin_liquid|tumeric na|cinnamon na|curry powder na|worcestershire sauce thin_liquid|white onion cooked_veg|
ground ginger na|sesame seeds nut|hot sauce thin_liquid|red pepper flakes na|cinnamon sticks na|red chili peppers chili_fresh|bacon cured_meat|whipping cream thick_liquid|
boneless skinless chicken breast halves meat|peanut oil oil|ground nutmeg na|clove na|parmesan cheese hard_cheese|dried basil na|peeled fresh ginger aromatic|coarse salt na|
mushrooms mushroom|warm water water|large egg yolks egg_raw_part|balsamic vinegar thin_liquid|celery ribs raw_crisp_veg|cream cheese soft_cheese|white vinegar thin_liquid|
egg yolks egg_raw_part|capers dried_fruit|ground red pepper na|onion powder na|dijon mustard paste|rice grain_raw|cold water water|crushed red pepper flakes na|mirin thin_liquid|
fresh basil leaves herb|eggplant soft_cooked_veg|powdered sugar na|large egg whites egg_raw_part|cooking oil oil|lime wedges citrus_piece|shredded mozzarella cheese melt_cheese|
fat free less sodium chicken broth thin_liquid|ground pork ground_meat|sliced green onions herb|cayenne na|mozzarella cheese melt_cheese|medium shrimp shrimp|raisins dried_fruit|
red pepper cooked_veg|coriander herb|sauce thick_liquid|finely chopped onion cooked_veg|oyster sauce thick_liquid|sweet potatoes potato|beansprouts leafy|black peppercorns na|
crushed tomatoes soft_cooked_veg|egg whites egg_raw_part|cheese melt_cheese|fresh rosemary herb|oregano na|white pepper na|cherry tomatoes fruit|leeks cooked_veg|ketchup paste|
hoisin sauce paste|chopped celery raw_crisp_veg|low sodium soy sauce thin_liquid|cheddar cheese hard_cheese|light brown sugar na|cabbage leafy|fresh mint herb|large shrimp shrimp|
vegetable broth thin_liquid|cracked black pepper na|spring onions herb|peanuts nut|chickpeas legume|confectioners sugar na|coriander seeds na|italian seasoning na|
fresh oregano herb|bell pepper cooked_veg|cooked rice grain_cooked|lean ground beef ground_meat|ground pepper na|low salt chicken broth thin_liquid|frozen peas legume|
beef broth thin_liquid|active dry yeast na|cajun seasoning na|chopped fresh thyme herb|green pepper cooked_veg|ground cloves na|cornmeal na|white wine thin_liquid|
spinach leafy|ground allspice na|lemongrass herb|plain yogurt dairy_liquid|thyme na|feta cheese crumbles soft_cheese|hot water water|orange fruit|toasted sesame oil oil|
long-grain rice grain_raw|parmigiano reggiano cheese hard_cheese|fennel seeds na|ricotta cheese soft_cheese|white wine vinegar thin_liquid|boiling water water|
cider vinegar thin_liquid|ground white pepper na|pinenuts nut|light soy sauce thin_liquid|chopped garlic aromatic|fresh thyme herb|parsley herb|sake thin_liquid|
smoked paprika na|boneless chicken skinless thigh meat|grated lemon zest na|spaghetti grain_cooked|green beans cooked_veg|yellow corn meal na|chile pepper chili_fresh|
low sodium chicken broth thin_liquid|fresh ginger root aromatic|orange juice thin_liquid|half & half thick_liquid|chicken thighs meat|sweet onion cooked_veg|
chopped parsley herb|shiitake mushroom|corn corn|basmati rice grain_raw|shredded monterey jack cheese melt_cheese|tomatillos soft_cooked_veg|chiles chili_fresh|
pasta grain_cooked|dark brown sugar na|chopped fresh mint herb|vinegar thin_liquid|mustard seeds na|dark soy sauce thin_liquid|vanilla na|dry red wine thin_liquid|
ghee butter|bread crumbs crisp|hot pepper sauce thin_liquid|green chile chili_fresh|tortilla chips crisp|pork meat|serrano chile chili_fresh|chopped tomatoes soft_cooked_veg|
sriracha paste|cooked chicken meat|enchilada sauce thick_liquid|toasted sesame seeds nut|arborio rice grain_raw|yellow bell pepper cooked_veg|dry bread crumbs crisp|
fresh parmesan cheese hard_cheese|fine sea salt na|fresh coriander herb|prosciutto cured_meat|basil herb|chopped pecans nut|garlic paste paste|radishes raw_crisp_veg|
corn kernels corn|juice thin_liquid|long grain white rice grain_raw|saffron threads na|creole seasoning na|melted butter oil|beef meat|fresh mushrooms mushroom|
sweetened condensed milk sweet_condensed|taco seasoning na|baguette bread|romaine lettuce raw_crisp_veg|apple cider vinegar thin_liquid|chopped green bell pepper cooked_veg|
feta cheese soft_cheese|mango mango|okra okra
"""

# 種類の中で個別に直したもの（Claude の推定）
OVERRIDE = {
    "honey": {"thickness": 5},
    "coconut milk": {"thickness": 2, "juiciness": 4},
    "sour cream": {"thickness": 4},
    "plain yogurt": {"thickness": 3},
    "buttermilk": {"thickness": 2},
    "baguette": {"hardness": 4, "chewiness": 4},
    "bacon": {"hardness": 3, "chewiness": 3},
    "prosciutto": {"hardness": 1, "chewiness": 3, "smoothness": 2},
    "chicken thighs": {"hardness": 3, "juiciness": 4},
    "boneless chicken skinless thigh": {"hardness": 3, "juiciness": 4},
    "carrots": {"hardness": 3, "chewiness": 3},
    "celery": {"juiciness": 4},
    "purple onion": {"juiciness": 4},
    "spaghetti": {"thickness": 1, "chewiness": 4},
    "pasta": {"thickness": 1, "chewiness": 4},
    "frozen peas": {"hardness": 1, "juiciness": 3, "chewiness": 1},
    "capers": {"hardness": 1, "thickness": 0, "juiciness": 3, "chewiness": 1, "smoothness": 2},
    "parmesan cheese": {"hardness": 4},
}


def main() -> None:
    assign = {}
    for tok in ASSIGN.replace("\n", "").split("|"):
        tok = tok.strip()
        if not tok:
            continue
        name, g = tok.rsplit(" ", 1)
        assign[name] = g
    rows = list(csv.DictReader((ROOT / "data" / "labels" / "taste_scores.csv").open(encoding="utf-8")))
    missing = [r["ingredient"] for r in rows if r["ingredient"] not in assign]
    extra = [k for k in assign if k not in {r["ingredient"] for r in rows}]
    assert not missing and not extra, (missing, extra)
    out = []
    for r in rows:
        g = assign[r["ingredient"]]
        form, *vals = GROUPS[g]
        v = dict(zip(ITEMS, vals))
        v.update(OVERRIDE.get(r["ingredient"], {}))
        out.append({"ingredient": r["ingredient"], "ja": r["ja"], "group": g, "form": form,
                    **{k: ("" if v[k] is None else v[k]) for k in ITEMS},
                    "basis": "Claude の推定（出典なし）" + ("・個別に直した" if r["ingredient"] in OVERRIDE else "")})
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("wrote", OUT, len(out), "rows;", sum(1 for o in out if o["hardness"] == ""), "対象外")


if __name__ == "__main__":
    main()

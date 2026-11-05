# Exp-02 味覚スコア下書きのレビューガイド

対象: `data/labels/taste_scores_draft.csv`（Claude の下書き、303 食材）。尺度は [scale.md](scale.md)。
直した版は `data/labels/taste_scores.csv` として別に作る（draft は上書きしない）。

## 見る順番の提案
1. 下の confidence=low の一覧（名前が曖昧・形で味が変わる）
2. 軸ごとの上位10件で、軸の「5」の基準が自分の感覚と合うか
3. 残りは `canonical` でソートして、同じ代表名の中で揃っているかを見る

## confidence=low の食材（28 件、出現レシピ数順）

| 食材 | canonical | レシピ数 | スコア | 理由 |
|---|---|---:|---|---|
| garlic | garlic | 7380 | 甘1 塩0 酸0 苦0 旨1 辛1 | 生の刺激（辛3程度）と加熱後の甘み・旨みで大きく変わる。料理に入った後（加熱）基準で辛1 |
| garlic cloves | garlic | 6236 | 甘1 塩0 酸0 苦0 旨1 辛1 | garlic と同じ扱い（加熱基準） |
| pepper | black pepper | 4438 | 甘0 塩0 酸0 苦1 旨0 辛4 | 単に pepper。black pepper と解釈したが bell pepper・唐辛子の可能性も残る |
| chili powder | chili powder | 2036 | 甘0 塩1 酸0 苦1 旨0 辛2 | 米国式ブレンド（唐辛子＋クミン・オレガノ・塩）想定。インド料理では純粋な唐辛子粉（辛5）の意味でも使われる |
| minced garlic | garlic | 1583 | 甘1 塩0 酸0 苦0 旨1 辛1 | garlic と同じ扱い（加熱基準） |
| vanilla extract | vanilla extract | 1298 | 甘1 塩0 酸0 苦2 旨0 辛0 | 香りが本体。原液はアルコールの苦み。甘い香りを甘1として残した |
| bay leaves | bay leaves | 1036 | 甘0 塩0 酸0 苦2 旨0 辛0 | 取り出す前提で単体では口にしない。煮出した液の苦み基準 |
| large garlic cloves | garlic | 873 | 甘1 塩0 酸0 苦0 旨1 辛1 | garlic と同じ扱い（加熱基準） |
| bay leaf | bay leaves | 839 | 甘0 塩0 酸0 苦2 旨0 辛0 | bay leaves と同じ |
| green chilies | chile pepper | 768 | 甘0 塩0 酸0 苦1 旨0 辛3 | インドの青唐辛子（辛4）と米国の缶詰マイルドチリ（辛1〜2）が混在 |
| cinnamon sticks | cinnamon | 646 | 甘1 塩0 酸0 苦2 旨0 辛1 | 煮出して取り出す前提。単体では口にしない |
| red pepper | bell pepper | 459 | 甘2 塩0 酸0 苦0 旨0 辛1 | red bell pepper と唐辛子（red chili / 粉）のどちらも含む。bell 寄りに採点し辛1を残した |
| coriander | coriander | 458 | 甘1 塩0 酸0 苦1 旨0 辛0 | 種子（ground coriander）か葉（cilantro）か不明。共起はインド料理が多く種子寄り |
| sauce | sauce | 458 | 甘2 塩3 酸1 苦0 旨2 辛0 | 何のソースか不明。共起は soy sauce・sugar・water が多く、中華系の合わせ調味料が多いと推定 |
| cheese | cheese | 447 | 甘0 塩3 酸1 苦0 旨3 辛0 | 種類不明。チェダー相当として採点 |
| bell pepper | bell pepper | 387 | 甘2 塩0 酸0 苦1 旨0 辛0 | 色不明。赤（甘3）と緑（苦2）の中間 |
| active dry yeast | yeast | 377 | 甘0 塩0 酸0 苦2 旨2 辛0 | 単体では苦みと旨み。パン生地では発酵後に消える |
| white wine | white wine | 367 | 甘1 塩0 酸3 苦1 旨0 辛0 | 辛口か甘口か不明 |
| lemongrass | lemongrass | 364 | 甘0 塩0 酸1 苦1 旨0 辛0 | 香りが本体。硬く単体では食べない |
| chopped garlic | garlic | 345 | 甘1 塩0 酸0 苦0 旨1 辛1 | garlic と同じ扱い（加熱基準） |
| chile pepper | chile pepper | 340 | 甘0 塩0 酸0 苦1 旨0 辛3 | 品種不明 |
| chiles | chile pepper | 321 | 甘0 塩0 酸0 苦1 旨0 辛3 | 品種不明（生・乾燥とも） |
| mustard seeds | mustard seeds | 313 | 甘0 塩0 酸0 苦2 旨0 辛2 | 油で弾かせるインド式の用途では辛みより香ばしさ。すり潰せば辛4 |
| vanilla | vanilla extract | 311 | 甘1 塩0 酸0 苦2 旨0 辛0 | vanilla extract と同じ |
| green chile | chile pepper | 302 | 甘0 塩0 酸0 苦1 旨0 辛2 | 米国の缶詰グリーンチリ（アナハイム系）想定で辛さ控えめ |
| garlic paste | garlic | 282 | 甘1 塩0 酸0 苦0 旨1 辛1 | garlic と同じ扱い（加熱基準）。市販品は塩入りのこともある |
| juice | juice | 280 | 甘2 塩0 酸3 苦0 旨0 辛0 | 何の果汁か不明。共起（olive oil・garlic・トマト）から柑橘の搾り汁と推定し酸3 |
| melted butter | butter | 276 | 甘1 塩2 酸0 苦0 旨1 辛0 | 有塩か無塩か不明。butter と同じく有塩として採点 |

## 軸ごとのスコア上位10件

スコアの高い順、同点はレシピ数の多い順。同点が10位をまたぐ場合は、その点数の件数を見出しに書いた。

### sweet（甘）（5 点は全 12 件、うち 10 件を表示）

| # | 食材 | canonical | sweet | レシピ数 | confidence |
|---:|---|---|---:|---:|---|
| 1 | sugar | sugar | 5 | 6434 | high |
| 2 | brown sugar | brown sugar | 5 | 1503 | medium |
| 3 | honey | honey | 5 | 1299 | high |
| 4 | white sugar | sugar | 5 | 1093 | high |
| 5 | granulated sugar | sugar | 5 | 849 | high |
| 6 | powdered sugar | powdered sugar | 5 | 501 | high |
| 7 | raisins | raisins | 5 | 460 | high |
| 8 | light brown sugar | brown sugar | 5 | 422 | high |
| 9 | confectioners sugar | powdered sugar | 5 | 395 | high |
| 10 | dark brown sugar | brown sugar | 5 | 319 | high |

### salty（塩）（4 点は全 14 件、うち 1 件を表示）

| # | 食材 | canonical | salty | レシピ数 | confidence |
|---:|---|---|---:|---:|---|
| 1 | salt | salt | 5 | 18048 | high |
| 2 | soy sauce | soy sauce | 5 | 3296 | high |
| 3 | kosher salt | salt | 5 | 3113 | high |
| 4 | fish sauce | fish sauce | 5 | 1247 | high |
| 5 | sea salt | salt | 5 | 940 | high |
| 6 | coarse salt | salt | 5 | 578 | high |
| 7 | light soy sauce | soy sauce | 5 | 347 | medium |
| 8 | fine sea salt | salt | 5 | 285 | high |
| 9 | prosciutto | prosciutto | 5 | 284 | high |
| 10 | grated parmesan cheese | parmesan cheese | 4 | 1885 | high |

### sour（酸）（5 点は全 13 件、うち 10 件を表示）

| # | 食材 | canonical | sour | レシピ数 | confidence |
|---:|---|---|---:|---:|---|
| 1 | fresh lemon juice | lemon juice | 5 | 1679 | high |
| 2 | lime | lime | 5 | 1439 | medium |
| 3 | lemon juice | lemon juice | 5 | 1394 | high |
| 4 | fresh lime juice | lime juice | 5 | 1368 | high |
| 5 | lemon | lemon | 5 | 1218 | medium |
| 6 | lime juice | lime juice | 5 | 1072 | high |
| 7 | red wine vinegar | vinegar | 5 | 752 | high |
| 8 | white vinegar | vinegar | 5 | 554 | high |
| 9 | lime wedges | lime | 5 | 482 | medium |
| 10 | white wine vinegar | vinegar | 5 | 352 | high |

### bitter（苦）（2 点は全 35 件、うち 4 件を表示）

| # | 食材 | canonical | bitter | レシピ数 | confidence |
|---:|---|---|---:|---:|---|
| 1 | ground turmeric | turmeric | 3 | 949 | medium |
| 2 | tumeric | turmeric | 3 | 738 | medium |
| 3 | clove | cloves | 3 | 600 | medium |
| 4 | ground cloves | cloves | 3 | 371 | medium |
| 5 | dry red wine | red wine | 3 | 309 | medium |
| 6 | saffron threads | saffron | 3 | 277 | medium |
| 7 | extra-virgin olive oil | olive oil | 2 | 2747 | medium |
| 8 | ground cumin | cumin | 2 | 2747 | medium |
| 9 | dried oregano | oregano | 2 | 1706 | medium |
| 10 | fresh parsley | parsley | 2 | 1604 | medium |

### umami（旨）（4 点は全 7 件、うち 4 件を表示）

| # | 食材 | canonical | umami | レシピ数 | confidence |
|---:|---|---|---:|---:|---|
| 1 | grated parmesan cheese | parmesan cheese | 5 | 1885 | high |
| 2 | fish sauce | fish sauce | 5 | 1247 | high |
| 3 | parmesan cheese | parmesan cheese | 5 | 591 | high |
| 4 | oyster sauce | oyster sauce | 5 | 455 | high |
| 5 | parmigiano reggiano cheese | parmesan cheese | 5 | 353 | high |
| 6 | fresh parmesan cheese | parmesan cheese | 5 | 286 | high |
| 7 | soy sauce | soy sauce | 4 | 3296 | high |
| 8 | tomato paste | tomato paste | 4 | 1158 | medium |
| 9 | bacon | bacon | 4 | 620 | high |
| 10 | low sodium soy sauce | soy sauce | 4 | 425 | high |

### spicy（辛）（4 点は全 18 件、うち 7 件を表示）

| # | 食材 | canonical | spicy | レシピ数 | confidence |
|---:|---|---|---:|---:|---|
| 1 | cayenne pepper | cayenne pepper | 5 | 1523 | high |
| 2 | ground red pepper | cayenne pepper | 5 | 538 | medium |
| 3 | cayenne | cayenne pepper | 5 | 470 | high |
| 4 | ground black pepper | black pepper | 4 | 4784 | high |
| 5 | pepper | black pepper | 4 | 4438 | low |
| 6 | black pepper | black pepper | 4 | 2627 | high |
| 7 | freshly ground pepper | black pepper | 4 | 949 | medium |
| 8 | crushed red pepper | red pepper flakes | 4 | 825 | high |
| 9 | hot sauce | hot sauce | 4 | 674 | medium |
| 10 | red pepper flakes | red pepper flakes | 4 | 669 | high |


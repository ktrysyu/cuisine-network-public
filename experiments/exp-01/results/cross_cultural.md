# Exp-01 japanese レシピの他 cuisine 最近傍（Q3）

- 類似度 = 料理ベクトル同士のコサイン類似度。候補は japanese 以外の全レシピ
- クエリの選び方: 下表の食材を**すべて含む** japanese レシピのうち id 最小のもの（機械的に選んだ。代表例である保証は無い）＋ 乱数で 3 件
- データに料理名が無いので「味噌汁」等は食材からの推測ラベル


## 味噌汁っぽいもの（条件: miso, dashi / 該当 6 件）: id 20490

食材: dashi, firm tofu, miso, water, scallions

| # | id | cuisine | cos | 食材 |
|---|---|---|---|---|
| 1 | 7604 | korean | 0.890 | kale, soft tofu, liquid, squash, soy sauce, chili paste, sesame oil, garlic cloves, water, mirin, vegetable broth, kimchi, …(+4) |
| 2 | 45093 | korean | 0.884 | fresh ginger, firm tofu, kimchi, white onion, daikon, garlic cloves, shiitake mushroom caps, soy sauce, chile pepper, scallions, toasted sesame oil, water, …(+2) |
| 3 | 43039 | korean | 0.878 | tomato paste, yellow miso, firm tofu, toasted sesame seeds, sushi rice, vegetable oil, carrots, nori, garlic paste, large eggs, scallions, snow peas, …(+3) |
| 4 | 36419 | korean | 0.873 | seasoning, shiitake, scallions, silken tofu, udon, toasted sesame oil, spinach, miso paste, nori sheets, dressing, water, spices |
| 5 | 46283 | korean | 0.873 | soy sauce, green onions, green pepper, sake, beef, sliced carrots, onions, sesame, shiitake, sesame oil, gochujang base, sugar, …(+2) |

## 照り焼きっぽいもの（条件: mirin, soy sauce, sake, chicken thighs / 該当 4 件）: id 17805

食材: mirin, corn flour, sake, ginger, eggs, flour, chicken thighs, soy sauce, garlic

| # | id | cuisine | cos | 食材 |
|---|---|---|---|---|
| 1 | 26234 | chinese | 0.895 | red chili peppers, orange, ginger, oil, white vinegar, soy sauce, flour, garlic, corn starch, eggs, white pepper, green onions, …(+5) |
| 2 | 2696 | chinese | 0.893 | minced garlic, spring onions, sugar, beef, oil, sake, water, ginger, soy sauce, egg whites, oyster sauce |
| 3 | 39086 | korean | 0.890 | potato starch, baking soda, spring onions, salt, toasted sesame seeds, chicken wings, dark soy, ginger, gochujang base, sweet rice flour, plain flour, ground black pepper, …(+7) |
| 4 | 19434 | chinese | 0.890 | pork, water, sesame oil, scallions, sake, pork belly, flour, ginger, onions, potato starch, soy sauce, egg whites, …(+7) |
| 5 | 43070 | chinese | 0.887 | sake, cherry tomatoes, sesame oil, oyster sauce, eggs, ketchup, green onions, ginger, canola oil, chicken broth, soy sauce, flour, …(+6) |

## 寿司飯っぽいもの（条件: sushi rice, rice vinegar / 該当 42 件）: id 265

食材: water, nori, avocado, rice vinegar, salt, sushi rice, cucumber

| # | id | cuisine | cos | 食材 |
|---|---|---|---|---|
| 1 | 48620 | korean | 0.873 | molasses, edamame, toasted sesame seeds, water, carrots, canola oil, sushi rice, chopped walnuts, nori, soy sauce, daikon, shiso |
| 2 | 17822 | korean | 0.871 | salt, cucumber, pickled radish, english cucumber, lobster, rice, toasted sesame seeds, sesame oil, carrots |
| 3 | 33843 | korean | 0.870 | apple cider vinegar, gochujang base, red chili peppers, salt, minced garlic, rice vinegar, sugar, sesame oil, english cucumber |
| 4 | 38959 | chinese | 0.867 | sugar, diced tomatoes, cucumber, soy sauce, rice vinegar, toasted sesame seeds, baby greens, oil, romaine lettuce, grapeseed oil, carrots |
| 5 | 8183 | korean | 0.865 | red chili peppers, ground black pepper, jicama, garlic, gochujang base, kimchi, brown sugar, kosher salt, shredded carrots, vegetable oil, salt, cucumber, …(+13) |

## 天ぷら・揚げ物っぽいもの（条件: panko breadcrumbs, eggs, flour / 該当 7 件）: id 3931

食材: flour, eggs, oil, tonkatsu sauce, pork chops, panko breadcrumbs

| # | id | cuisine | cos | 食材 |
|---|---|---|---|---|
| 1 | 34771 | southern_us | 0.866 | eggs, green tomatoes, panko breadcrumbs, flour, oil, mayonaise, salt, fresh thyme, sauce |
| 2 | 34460 | filipino | 0.849 | sweet chili sauce, salt, flour, panko breadcrumbs, pepper, oil, eggs, sweetened coconut flakes, large shrimp |
| 3 | 15723 | korean | 0.845 | seasoning, pork sirloin chops, pepper, panko breadcrumbs, eggs, salt, flour, canola oil |
| 4 | 2897 | southern_us | 0.840 | matzo meal, oil, flour, eggs, green tomatoes |
| 5 | 48296 | french | 0.820 | cooked deli ham, confectioners sugar, flour, sandwich bread, swiss cheese, turkey breast deli meat, eggs, vegetable oil, panko breadcrumbs |

## カレー（条件: curry powder, potatoes, carrots, onions / 該当 3 件）: id 12109

食材: crushed tomatoes, potatoes, apples, carrots, pepper, stewing beef, butter, salt, onions, white flour, fresh ginger, beef stock, garlic, bay leaf, curry powder, garam masala, star anise, oil, frozen peas

| # | id | cuisine | cos | 食材 |
|---|---|---|---|---|
| 1 | 3206 | indian | 0.934 | water, coriander powder, raisins, carrots, celery ribs, olive oil, potatoes, garlic, cashew nuts, curry powder, zucchini, apples, …(+6) |
| 2 | 44229 | indian | 0.922 | potatoes, vegetable broth, oil, cashew nuts, pepper, paprika, salt, sour cream, almonds, ginger, green chilies, onions, …(+3) |
| 3 | 33396 | indian | 0.921 | minced garlic, frozen pastry puff sheets, salt, cinnamon sticks, frozen peas, pepper, fresh ginger, mango chutney, carrots, onions, curry powder, potatoes, …(+7) |
| 4 | 20591 | jamaican | 0.918 | stock, curry powder, cracked black pepper, minced beef, onions, plain flour, bread crumbs, butter, garlic, celery, cold water, tumeric, …(+8) |
| 5 | 3829 | indian | 0.911 | salt, cinnamon sticks, onions, potatoes, cardamom pods, coconut milk, plum tomatoes, pepper, green chilies, ginger root, coriander, whole milk, …(+2) |

## ランダム抽出: id 46555

食材: sea salt, salmon fillets, sake, lemon wedge

| # | id | cuisine | cos | 食材 |
|---|---|---|---|---|
| 1 | 504 | french | 0.751 | fresh dill, white pepper, lemon wedge, grated lemon zest, mayonaise, whole grain dijon mustard, fresh tarragon, asparagus spears, soy sauce, hot pepper sauce, salt, salmon fillets, …(+3) |
| 2 | 21684 | chinese | 0.735 | szechwan peppercorns, shrimp, sea salt, vegetable oil, lemon wedge, garlic cloves |
| 3 | 34386 | french | 0.725 | sake, sea salt, ground black pepper, english cucumber, shallots, shucked oysters, rice vinegar |
| 4 | 20282 | chinese | 0.718 | olive oil, sesame oil, fish fillets, ground black pepper, alcohol, fresh ginger, sea salt, fresh chives, bean paste |
| 5 | 32506 | french | 0.715 | kosher salt, fresh ginger, cracked black pepper, sake, olive oil, fresh shiitake mushrooms, garlic chives, minced garlic, mirin, filet mignon steaks, unsalted butter |

## ランダム抽出: id 27844

食材: potatoes, salt, frozen peas, cauliflower, diced tomatoes, ground coriander, cumin, tumeric, cilantro, cumin seed, vegetable oil, cayenne pepper, boiling water

| # | id | cuisine | cos | 食材 |
|---|---|---|---|---|
| 1 | 20408 | indian | 0.951 | fresh cilantro, potatoes, vegetable oil, salt, corn starch, ground cumin, tumeric, chopped tomatoes, butternut squash, paprika, ground coriander, bay leaf, …(+11) |
| 2 | 42960 | indian | 0.950 | tumeric, vegetable oil, ground coriander, garam masala, salt, onions, kidney beans, garlic, cumin seed, tomatoes, grated cauliflower, cayenne pepper |
| 3 | 32044 | indian | 0.947 | diced tomatoes, yellow split peas, oil, water, salt, ground coriander, tumeric, garlic, cayenne pepper, onions, butter, cilantro leaves, …(+1) |
| 4 | 13324 | indian | 0.947 | tumeric, hot pepper, garlic, lentils, basmati rice, cauliflower, garam masala, paprika, cayenne pepper, chopped cilantro, plain yogurt, vegetable oil, …(+8) |
| 5 | 17915 | indian | 0.943 | fennel seeds, ground pepper, ginger, chopped cilantro, ground cumin, tumeric, potatoes, cayenne pepper, frozen peas, eggs, garam masala, crust, …(+5) |

## ランダム抽出: id 39080

食材: asparagus, soy sauce, sugar, dried bonito flakes, dashi

| # | id | cuisine | cos | 食材 |
|---|---|---|---|---|
| 1 | 27890 | korean | 0.851 | spinach, fishcake, sesame oil, imitation crab meat, soy sauce, sesame seeds, rice vinegar, carrots, sugar, water, salt, kelp, …(+5) |
| 2 | 31403 | korean | 0.844 | soy sauce, gochujang base, sugar, sesame oil, roasted white sesame seeds, red miso, green onions, short rib |
| 3 | 46283 | korean | 0.840 | soy sauce, green onions, green pepper, sake, beef, sliced carrots, onions, sesame, shiitake, sesame oil, gochujang base, sugar, …(+2) |
| 4 | 39264 | korean | 0.831 | roasted sesame seeds, zucchini, sesame oil, gochujang base, beansprouts, snow peas, soy sauce, shiitake, egg yolks, ginger, scallions, toasted sesame oil, …(+12) |
| 5 | 7604 | korean | 0.831 | kale, soft tofu, liquid, squash, soy sauce, chili paste, sesame oil, garlic cloves, water, mirin, vegetable broth, kimchi, …(+4) |

## 集計: japanese 全 1423 件の「他 cuisine 最近傍」の cuisine 分布

候補集合での各 cuisine の割合（偶然ならこの比率になる）と並べる。

| cuisine | 最近傍になった件数 | 割合 | 候補集合中の割合 |
|---|---|---|---|
| korean | 548 | 0.385 | 0.022 |
| chinese | 426 | 0.299 | 0.070 |
| indian | 116 | 0.082 | 0.078 |
| thai | 80 | 0.056 | 0.040 |
| vietnamese | 49 | 0.034 | 0.022 |
| southern_us | 40 | 0.028 | 0.113 |
| french | 32 | 0.022 | 0.069 |
| filipino | 28 | 0.020 | 0.020 |
| italian | 24 | 0.017 | 0.204 |
| mexican | 17 | 0.012 | 0.168 |
| cajun_creole | 17 | 0.012 | 0.040 |
| british | 10 | 0.007 | 0.021 |
| russian | 9 | 0.006 | 0.013 |
| jamaican | 7 | 0.005 | 0.014 |
| moroccan | 6 | 0.004 | 0.021 |
| spanish | 6 | 0.004 | 0.026 |
| irish | 3 | 0.002 | 0.017 |
| brazilian | 3 | 0.002 | 0.012 |
| greek | 2 | 0.001 | 0.031 |

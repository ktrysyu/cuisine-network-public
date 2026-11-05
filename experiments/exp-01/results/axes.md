# Exp-01 軸への射影（Q2）

- 料理ベクトル（単位長）と軸ベクトル（単位長）の内積を射影値とする。正 = 左側の極（soy sauce / japanese）寄り
- 軸「soy sauce ↔ butter」= v(soy sauce) − v(butter)。食材ベクトルは単位長にしてから引く
- 軸「japanese 重心 ↔ italian 重心」= 各 cuisine の料理ベクトル平均の差。**cuisine ラベルを使って軸を定義している**（学習には使っていない）
- データに料理名は無い。レシピ ID・cuisine・食材（先頭10件、データ上の順）を載せる
- 各軸について「全レシピ」版と「食材 5 個以上」版を載せる。前者は食材 1〜3 個のレシピが端を占めやすいため

## soy sauce ↔ butter

### cuisine ごとの平均射影値（上 = soy sauce 寄り）

| 順 | cuisine | 平均 |
|---|---|---|
| 1 | korean | +0.262 |
| 2 | chinese | +0.248 |
| 3 | japanese | +0.201 |
| 4 | vietnamese | +0.196 |
| 5 | thai | +0.190 |
| 6 | filipino | +0.056 |
| 7 | jamaican | -0.032 |
| 8 | indian | -0.035 |
| 9 | mexican | -0.064 |
| 10 | brazilian | -0.073 |
| 11 | moroccan | -0.099 |
| 12 | cajun_creole | -0.122 |
| 13 | spanish | -0.126 |
| 14 | greek | -0.136 |
| 15 | russian | -0.162 |
| 16 | italian | -0.176 |
| 17 | southern_us | -0.188 |
| 18 | french | -0.196 |
| 19 | irish | -0.207 |
| 20 | british | -0.213 |

### 食材の両端（語彙 3336 語）

- soy sauce 側: soy sauce (+0.67), light soy sauce (+0.53), reduced sodium soy sauce (+0.49), low sodium soy sauce (+0.47), gluten free soy sauce (+0.47), tamari soy sauce (+0.47), mushroom soy sauce (+0.47), brown rice vinegar (+0.45), sesame chili oil (+0.45), sesame oil (+0.44), regular soy sauce (+0.44), bean sauce (+0.44), toasted sesame oil (+0.43), white rice vinegar (+0.42), kikkoman soy sauce (+0.42)
- butter 側: butter (-0.67), unsalted butter (-0.48), margarine (-0.44), light butter (-0.38), emmenthal (-0.36), compote (-0.36), melted butter (-0.35), softened butter (-0.35), buttermilk cornbread (-0.34), condensed cheddar cheese soup (-0.33), havarti cheese (-0.33), all-purpose flour (-0.32), angel food cake (-0.32), salted butter (-0.31), buttermilk biscuits (-0.31)

### 全レシピ: soy sauce 側の上位 15

| # | id | cuisine | 射影 | 食材数 | 食材 |
|---|---|---|---|---|---|
| 1 | 38678 | japanese | +0.588 | 3 | rice vinegar, soy sauce, citrus juice |
| 2 | 4796 | chinese | +0.580 | 3 | soy sauce, gai lan, toasted sesame oil |
| 3 | 10348 | chinese | +0.564 | 3 | chili oil, rice vinegar, soy sauce |
| 4 | 38969 | japanese | +0.564 | 3 | rice vinegar, soy sauce, chili oil |
| 5 | 16482 | japanese | +0.554 | 3 | mochi, nori, soy sauce |
| 6 | 35934 | japanese | +0.554 | 3 | mochi, soy sauce, nori |
| 7 | 2211 | japanese | +0.532 | 5 | miso, mirin, soy sauce, blade steak, sesame oil |
| 8 | 25597 | japanese | +0.528 | 2 | wasabi powder, soy sauce |
| 9 | 5661 | chinese | +0.522 | 7 | chicken wings, sesame oil, sesame seeds, rice vinegar, soy sauce, garlic, peeled fresh ginger |
| 10 | 43216 | chinese | +0.516 | 3 | soy sauce, fresh bean, toasted sesame oil |
| 11 | 7047 | chinese | +0.501 | 5 | soy sauce, cilantro leaves, chinese red rice vinegar, sesame oil, ginger |
| 12 | 35999 | chinese | +0.497 | 13 | lime, sesame oil, scallions, soy sauce, mirin, firm tofu, glass noodles, yu choy, garlic, chinese five-spice powder, …(+3) |
| 13 | 14534 | chinese | +0.495 | 10 | rice vinegar, garlic chili sauce, honey, scallions, ramen, soy sauce, dark sesame oil, chinese egg noodles, cilantro stems, sesame paste |
| 14 | 38813 | japanese | +0.493 | 6 | fresh ginger, sugar, sesame oil, sriracha, soy sauce, rice vinegar |
| 15 | 39469 | japanese | +0.488 | 5 | soy sauce, rice vinegar, japanese cucumber, wakame, carrots |

cuisine 内訳: japanese 8, chinese 7

### 全レシピ: butter 側の上位 15

| # | id | cuisine | 射影 | 食材数 | 食材 |
|---|---|---|---|---|---|
| 1 | 41135 | french | -0.671 | 1 | butter |
| 2 | 41124 | indian | -0.671 | 1 | butter |
| 3 | 9272 | italian | -0.521 | 3 | salt, butter, polenta |
| 4 | 49645 | italian | -0.521 | 3 | butter, polenta, salt |
| 5 | 11446 | irish | -0.508 | 4 | all-purpose flour, butter, extra fine granulated sugar, lemon |
| 6 | 22345 | italian | -0.499 | 3 | butter, heavy whipping cream, grated parmesan cheese |
| 7 | 39283 | italian | -0.493 | 3 | butter, cream cheese, heavy cream |
| 8 | 4173 | southern_us | -0.491 | 2 | butter, jam |
| 9 | 15677 | southern_us | -0.491 | 2 | butter, bacon |
| 10 | 15384 | southern_us | -0.487 | 5 | butter, cream cheese, soften, all-purpose flour, pie filling, lemon |
| 11 | 47737 | italian | -0.484 | 3 | butter, grated parmesan cheese, heavy cream |
| 12 | 302 | french | -0.482 | 4 | butter, bittersweet baking chocolate, coffee liqueur, whipping cream |
| 13 | 19772 | indian | -0.478 | 1 | unsalted butter |
| 14 | 27192 | indian | -0.478 | 1 | unsalted butter |
| 15 | 14335 | indian | -0.478 | 1 | unsalted butter |

cuisine 内訳: italian 5, indian 4, southern_us 3, french 2, irish 1

### 食材 5 個以上: soy sauce 側の上位 15

| # | id | cuisine | 射影 | 食材数 | 食材 |
|---|---|---|---|---|---|
| 1 | 2211 | japanese | +0.532 | 5 | miso, mirin, soy sauce, blade steak, sesame oil |
| 2 | 5661 | chinese | +0.522 | 7 | chicken wings, sesame oil, sesame seeds, rice vinegar, soy sauce, garlic, peeled fresh ginger |
| 3 | 7047 | chinese | +0.501 | 5 | soy sauce, cilantro leaves, chinese red rice vinegar, sesame oil, ginger |
| 4 | 35999 | chinese | +0.497 | 13 | lime, sesame oil, scallions, soy sauce, mirin, firm tofu, glass noodles, yu choy, garlic, chinese five-spice powder, …(+3) |
| 5 | 14534 | chinese | +0.495 | 10 | rice vinegar, garlic chili sauce, honey, scallions, ramen, soy sauce, dark sesame oil, chinese egg noodles, cilantro stems, sesame paste |
| 6 | 38813 | japanese | +0.493 | 6 | fresh ginger, sugar, sesame oil, sriracha, soy sauce, rice vinegar |
| 7 | 39469 | japanese | +0.488 | 5 | soy sauce, rice vinegar, japanese cucumber, wakame, carrots |
| 8 | 43305 | korean | +0.488 | 8 | garlic, toasted sesame seeds, soy sauce, scallions, sugar, rice vinegar, gochugaru, toasted sesame oil |
| 9 | 19180 | japanese | +0.486 | 8 | wine, daikon, dashi, tamari soy sauce, soy sauce, ginger, mirin, sushi grade tuna |
| 10 | 33613 | korean | +0.485 | 10 | sugar, sesame oil, garlic cloves, sriracha, rice vinegar, soy sauce, ginger, toasted sesame seeds, flank steak, scallions |
| 11 | 34266 | thai | +0.485 | 6 | fresh ginger, sugar, flank steak, chili paste, soy sauce, rice vinegar |
| 12 | 45786 | japanese | +0.485 | 6 | green onions, soba, sesame oil, rice vinegar, soy sauce, cucumber |
| 13 | 45580 | chinese | +0.483 | 6 | soy sauce, spring onions, pork belly, sweet chili sauce, chinese five-spice powder, fresh ginger root |
| 14 | 17748 | japanese | +0.482 | 6 | kecap manis, soy sauce, rice vinegar, ginger, mirin, thai fish sauce |
| 15 | 17068 | japanese | +0.482 | 5 | soy sauce, garlic, miso, ginger, mirin |

cuisine 内訳: japanese 7, chinese 5, korean 2, thai 1

### 食材 5 個以上: butter 側の上位 15

| # | id | cuisine | 射影 | 食材数 | 食材 |
|---|---|---|---|---|---|
| 1 | 15384 | southern_us | -0.487 | 5 | butter, cream cheese, soften, all-purpose flour, pie filling, lemon |
| 2 | 7404 | italian | -0.478 | 6 | grated parmesan cheese, milk, salt, ground nutmeg, polenta, butter |
| 3 | 27980 | italian | -0.466 | 5 | parmesan cheese, fettucine, cream cheese, butter, milk |
| 4 | 863 | french | -0.465 | 5 | milk, grated nutmeg, salt, butter, all-purpose flour |
| 5 | 36667 | french | -0.462 | 7 | butter, large eggs, unsweetened cocoa powder, vanilla sugar, all-purpose flour, unsalted butter, salt |
| 6 | 44656 | italian | -0.461 | 5 | butter, cream, crème fraîche, fennel bulb, grated parmesan cheese |
| 7 | 9795 | southern_us | -0.460 | 7 | large eggs, salt, butternut squash, half & half, all-purpose flour, ground nutmeg, butter |
| 8 | 33642 | southern_us | -0.459 | 5 | salt, parmesan cheese, butter, fat free milk, polenta |
| 9 | 1183 | british | -0.456 | 5 | large eggs, salt, milk, all-purpose flour, butter |
| 10 | 32608 | british | -0.454 | 5 | butter, whole milk, strawberry yogurt, all-purpose flour, baking powder |
| 11 | 9235 | italian | -0.454 | 8 | chopped fresh chives, bacon slices, butter, muffin mix, buttermilk cornbread, shredded sharp cheddar cheese, large eggs, buttermilk |
| 12 | 7775 | mexican | -0.452 | 5 | butter, american cheese, all-purpose flour, salt, milk |
| 13 | 21390 | southern_us | -0.447 | 5 | buttermilk biscuits, ham, butter, cheddar cheese, poppy seeds |
| 14 | 21663 | southern_us | -0.443 | 7 | shredded cheddar cheese, baking mix, large eggs, vidalia onion, butter, milk, chopped pecans |
| 15 | 36311 | southern_us | -0.442 | 5 | buttermilk self-rising white cornmeal mix, all-purpose flour, butter, large eggs, buttermilk |

cuisine 内訳: southern_us 6, italian 4, french 2, british 2, mexican 1

### 上位 100 件の cuisine 内訳

- 全レシピ_soy sauce: japanese 43, chinese 41, korean 12, thai 2, vietnamese 1, indian 1
- 全レシピ_butter: southern_us 36, italian 25, french 17, irish 7, british 5, indian 4, mexican 3, brazilian 2, cajun_creole 1
- 食材 5 個以上_soy sauce: chinese 47, japanese 35, korean 14, thai 2, vietnamese 1, indian 1
- 食材 5 個以上_butter: southern_us 47, italian 21, french 17, british 5, irish 4, mexican 3, cajun_creole 1, jamaican 1, russian 1

## japanese 重心 ↔ italian 重心

### cuisine ごとの平均射影値（上 = japanese 重心 寄り）

| 順 | cuisine | 平均 |
|---|---|---|
| 1 | japanese | +0.308 |
| 2 | korean | +0.303 |
| 3 | chinese | +0.292 |
| 4 | vietnamese | +0.234 |
| 5 | thai | +0.228 |
| 6 | filipino | +0.107 |
| 7 | indian | +0.038 |
| 8 | jamaican | -0.006 |
| 9 | brazilian | -0.017 |
| 10 | russian | -0.083 |
| 11 | british | -0.094 |
| 12 | mexican | -0.097 |
| 13 | southern_us | -0.101 |
| 14 | irish | -0.108 |
| 15 | moroccan | -0.138 |
| 16 | cajun_creole | -0.173 |
| 17 | french | -0.178 |
| 18 | spanish | -0.203 |
| 19 | greek | -0.246 |
| 20 | italian | -0.307 |

### 食材の両端（語彙 3336 語）

- japanese 重心 側: soy sauce (+0.55), sesame oil (+0.54), mirin (+0.53), bonito (+0.53), toasted sesame seeds (+0.53), togarashi (+0.52), satsuma imo (+0.52), toasted sesame oil (+0.51), sushi grade tuna (+0.51), nori sheets (+0.49), shiso leaves (+0.49), buckwheat soba noodles (+0.49), sesame (+0.48), bonito flakes (+0.48), sake (+0.48)
- italian 重心 側: uncooked ziti (-0.52), frozen pizza dough (-0.51), cooked meatballs (-0.48), grated parmesan cheese (-0.48), hot cherry pepper (-0.47), uncooked rigatoni (-0.46), parmesan cheese (-0.44), perciatelli (-0.44), penne (-0.44), manicotti (-0.43), fresh parsley (-0.43), rigatoni (-0.43), cooked rigatoni (-0.43), italian style stewed tomatoes (-0.43), olive oil (-0.43)

### 全レシピ: japanese 重心 側の上位 15

| # | id | cuisine | 射影 | 食材数 | 食材 |
|---|---|---|---|---|---|
| 1 | 43741 | japanese | +0.631 | 5 | mirin, soy sauce, ginger, daikon, dashi |
| 2 | 40061 | japanese | +0.619 | 6 | soy sauce, dried bonito flakes, daikon, mirin, konbu, ginger |
| 3 | 19180 | japanese | +0.609 | 8 | wine, daikon, dashi, tamari soy sauce, soy sauce, ginger, mirin, sushi grade tuna |
| 4 | 17718 | japanese | +0.607 | 8 | sugar, daikon, sesame seeds, rice vinegar, soy sauce, dried bonito flakes, sesame oil, nori |
| 5 | 17748 | japanese | +0.601 | 6 | kecap manis, soy sauce, rice vinegar, ginger, mirin, thai fish sauce |
| 6 | 2211 | japanese | +0.600 | 5 | miso, mirin, soy sauce, blade steak, sesame oil |
| 7 | 16482 | japanese | +0.599 | 3 | mochi, nori, soy sauce |
| 8 | 35934 | japanese | +0.599 | 3 | mochi, soy sauce, nori |
| 9 | 6724 | japanese | +0.594 | 5 | mirin, sake, konbu, bonito flakes, soy sauce |
| 10 | 15584 | japanese | +0.590 | 4 | soy sauce, dried bonito flakes, mirin, sake |
| 11 | 16017 | japanese | +0.584 | 8 | dashi, rice vinegar, spring onions, nori, mirin, soba noodles, wasabi, shoyu |
| 12 | 49371 | japanese | +0.578 | 9 | soy sauce, scallions, duck breasts, mirin, sugar, peanut oil, sake, dashi powder, toasted sesame seeds |
| 13 | 11561 | japanese | +0.577 | 7 | soy sauce, sugar, toasted sesame seeds, salmon fillets, scallions, sake, mirin |
| 14 | 45032 | japanese | +0.577 | 16 | sugar, lime, sesame oil, seaweed, sushi rice, mirin, ginger, white sesame seeds, avocado, gari, …(+6) |
| 15 | 12610 | japanese | +0.576 | 6 | beef, sugar, ginger, sake, mirin, soy sauce |

cuisine 内訳: japanese 15

### 全レシピ: italian 重心 側の上位 15

| # | id | cuisine | 射影 | 食材数 | 食材 |
|---|---|---|---|---|---|
| 1 | 783 | southern_us | -0.569 | 11 | sliced salami, grated parmesan cheese, sliced ham, dried basil, pitted green olives, dried oregano, mozzarella cheese, oil-cured black olives, italian bread, olive oil, …(+1) |
| 2 | 47995 | italian | -0.550 | 11 | pepperoni slices, large garlic cloves, fresh parsley, olive oil, shredded mozzarella cheese, dried oregano, dried basil, frozen bread dough, plum tomatoes, grated parmesan cheese, …(+1) |
| 3 | 8639 | italian | -0.539 | 7 | olive oil, polenta, marinara sauce, grated parmesan cheese, wild mushrooms, sausage casings, dry red wine |
| 4 | 36680 | italian | -0.539 | 7 | olive oil, polenta, marinara sauce, grated parmesan cheese, wild mushrooms, sausage casings, dry red wine |
| 5 | 33906 | italian | -0.536 | 7 | grated parmesan cheese, dried oregano, provolone cheese, eggplant, italian salad dressing, marinara sauce, dried rosemary |
| 6 | 26535 | italian | -0.536 | 8 | garlic bulb, extra-virgin olive oil, parmesan cheese, plum tomatoes, fat-free reduced-sodium chicken broth, gnocchi, sage leaves, cracked black pepper |
| 7 | 43608 | italian | -0.536 | 5 | refrigerated pizza dough, parmesan cheese, prosciutto, rocket leaves, extra-virgin olive oil |
| 8 | 48228 | italian | -0.533 | 5 | marinara sauce, italian sausage, olive oil, pasta, dry white wine |
| 9 | 49360 | italian | -0.531 | 7 | fresh basil, marinara sauce, mozzarella cheese, flat leaf parsley, french baguette, sweet italian sausage, grated parmesan cheese |
| 10 | 29180 | italian | -0.526 | 4 | grated parmesan cheese, polenta, tomato sauce, hot italian sausages |
| 11 | 41848 | italian | -0.525 | 8 | grated parmesan cheese, rigatoni, vegetable oil cooking spray, chopped onion, pasta sauce, crushed red pepper, olive oil, italian turkey sausage |
| 12 | 29002 | italian | -0.524 | 7 | pizza crust, fresh parsley, fontina, low-fat ricotta, roasted red peppers, romano cheese, soppressata |
| 13 | 22350 | italian | -0.524 | 13 | olive oil, dry white wine, boneless skinless chicken breast halves, penne, grated parmesan cheese, asiago, tomato sauce, italian style stewed tomatoes, large garlic cloves, dried oregano, …(+3) |
| 14 | 9175 | italian | -0.524 | 7 | mozzarella cheese, marinara sauce, mascarpone, flat leaf parsley, parmesan cheese, cheese tortellini, fresh thyme |
| 15 | 3704 | italian | -0.522 | 6 | part-skim mozzarella cheese, part-skim ricotta cheese, grated parmesan cheese, fresh thyme, goat cheese, refrigerated pizza dough |

cuisine 内訳: italian 14, southern_us 1

### 食材 5 個以上: japanese 重心 側の上位 15

| # | id | cuisine | 射影 | 食材数 | 食材 |
|---|---|---|---|---|---|
| 1 | 43741 | japanese | +0.631 | 5 | mirin, soy sauce, ginger, daikon, dashi |
| 2 | 40061 | japanese | +0.619 | 6 | soy sauce, dried bonito flakes, daikon, mirin, konbu, ginger |
| 3 | 19180 | japanese | +0.609 | 8 | wine, daikon, dashi, tamari soy sauce, soy sauce, ginger, mirin, sushi grade tuna |
| 4 | 17718 | japanese | +0.607 | 8 | sugar, daikon, sesame seeds, rice vinegar, soy sauce, dried bonito flakes, sesame oil, nori |
| 5 | 17748 | japanese | +0.601 | 6 | kecap manis, soy sauce, rice vinegar, ginger, mirin, thai fish sauce |
| 6 | 2211 | japanese | +0.600 | 5 | miso, mirin, soy sauce, blade steak, sesame oil |
| 7 | 6724 | japanese | +0.594 | 5 | mirin, sake, konbu, bonito flakes, soy sauce |
| 8 | 16017 | japanese | +0.584 | 8 | dashi, rice vinegar, spring onions, nori, mirin, soba noodles, wasabi, shoyu |
| 9 | 49371 | japanese | +0.578 | 9 | soy sauce, scallions, duck breasts, mirin, sugar, peanut oil, sake, dashi powder, toasted sesame seeds |
| 10 | 11561 | japanese | +0.577 | 7 | soy sauce, sugar, toasted sesame seeds, salmon fillets, scallions, sake, mirin |
| 11 | 45032 | japanese | +0.577 | 16 | sugar, lime, sesame oil, seaweed, sushi rice, mirin, ginger, white sesame seeds, avocado, gari, …(+6) |
| 12 | 12610 | japanese | +0.576 | 6 | beef, sugar, ginger, sake, mirin, soy sauce |
| 13 | 26634 | japanese | +0.569 | 7 | soy sauce, ginger, sake, mirin, sesame seeds, sugar, boneless skinless chicken breasts |
| 14 | 7047 | chinese | +0.568 | 5 | soy sauce, cilantro leaves, chinese red rice vinegar, sesame oil, ginger |
| 15 | 46825 | japanese | +0.568 | 5 | bonito, orange, soy sauce, konbu, rice vinegar |

cuisine 内訳: japanese 14, chinese 1

### 食材 5 個以上: italian 重心 側の上位 15

| # | id | cuisine | 射影 | 食材数 | 食材 |
|---|---|---|---|---|---|
| 1 | 783 | southern_us | -0.569 | 11 | sliced salami, grated parmesan cheese, sliced ham, dried basil, pitted green olives, dried oregano, mozzarella cheese, oil-cured black olives, italian bread, olive oil, …(+1) |
| 2 | 47995 | italian | -0.550 | 11 | pepperoni slices, large garlic cloves, fresh parsley, olive oil, shredded mozzarella cheese, dried oregano, dried basil, frozen bread dough, plum tomatoes, grated parmesan cheese, …(+1) |
| 3 | 36680 | italian | -0.539 | 7 | olive oil, polenta, marinara sauce, grated parmesan cheese, wild mushrooms, sausage casings, dry red wine |
| 4 | 8639 | italian | -0.539 | 7 | olive oil, polenta, marinara sauce, grated parmesan cheese, wild mushrooms, sausage casings, dry red wine |
| 5 | 33906 | italian | -0.536 | 7 | grated parmesan cheese, dried oregano, provolone cheese, eggplant, italian salad dressing, marinara sauce, dried rosemary |
| 6 | 26535 | italian | -0.536 | 8 | garlic bulb, extra-virgin olive oil, parmesan cheese, plum tomatoes, fat-free reduced-sodium chicken broth, gnocchi, sage leaves, cracked black pepper |
| 7 | 43608 | italian | -0.536 | 5 | refrigerated pizza dough, parmesan cheese, prosciutto, rocket leaves, extra-virgin olive oil |
| 8 | 48228 | italian | -0.533 | 5 | marinara sauce, italian sausage, olive oil, pasta, dry white wine |
| 9 | 49360 | italian | -0.531 | 7 | fresh basil, marinara sauce, mozzarella cheese, flat leaf parsley, french baguette, sweet italian sausage, grated parmesan cheese |
| 10 | 41848 | italian | -0.525 | 8 | grated parmesan cheese, rigatoni, vegetable oil cooking spray, chopped onion, pasta sauce, crushed red pepper, olive oil, italian turkey sausage |
| 11 | 29002 | italian | -0.524 | 7 | pizza crust, fresh parsley, fontina, low-fat ricotta, roasted red peppers, romano cheese, soppressata |
| 12 | 22350 | italian | -0.524 | 13 | olive oil, dry white wine, boneless skinless chicken breast halves, penne, grated parmesan cheese, asiago, tomato sauce, italian style stewed tomatoes, large garlic cloves, dried oregano, …(+3) |
| 13 | 9175 | italian | -0.524 | 7 | mozzarella cheese, marinara sauce, mascarpone, flat leaf parsley, parmesan cheese, cheese tortellini, fresh thyme |
| 14 | 3704 | italian | -0.522 | 6 | part-skim mozzarella cheese, part-skim ricotta cheese, grated parmesan cheese, fresh thyme, goat cheese, refrigerated pizza dough |
| 15 | 42468 | italian | -0.521 | 7 | grated parmesan cheese, pesto, chees fresh mozzarella, fresh basil, refrigerated pizza dough, prosciutto, fresh parsley |

cuisine 内訳: italian 14, southern_us 1

### 上位 100 件の cuisine 内訳

- 全レシピ_japanese 重心: japanese 90, chinese 5, korean 4, thai 1
- 全レシピ_italian 重心: italian 96, greek 3, southern_us 1
- 食材 5 個以上_japanese 重心: japanese 90, korean 5, chinese 4, thai 1
- 食材 5 個以上_italian 重心: italian 96, greek 3, southern_us 1

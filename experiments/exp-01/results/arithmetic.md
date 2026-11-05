# Exp-01 食材の足し引き（Q6）

- 食材ベクトルは単位長。`cuisine:xxx` はその cuisine の料理ベクトル平均（単位長）。料理ベクトルは食材ベクトルの平均なので同じ空間にある
- 結果 = Σpositive − Σnegative を単位長にし、語彙全体からコサイン類似度上位を出す。式に入っている食材は除外
- 比較のため「+ 側の cuisine / 食材だけの最近傍」も並べる。結果がそれとほぼ同じなら、演算ではなく + 側に引っ張られているだけ

## Kazama 形式: mirin − japanese + french

| # | 結果 | cos | 比較: +側 (cuisine:french) だけ | 比較: mirin だけ |
|---|---|---|---|---|
| 1 | white asparagus | 0.562 | salt | sake |
| 2 | chopped fresh thyme | 0.557 | butter | bonito flakes |
| 3 | fresh thyme leaves | 0.553 | water | dried bonito flakes |
| 4 | parsley sprigs | 0.539 | compote | togarashi |
| 5 | candied lemon peel | 0.520 | all-purpose flour | dashi |
| 6 | unsalted butter | 0.517 | unsalted butter | nori |
| 7 | dried bonito flakes | 0.515 | almond liqueur | white miso |
| 8 | lemon curd | 0.515 | miniature semisweet chocolate chips | dashi powder |

結果上位 8 と「+側だけ」上位 8 の重なり: 1 件

## soy sauce − japanese + italian

| # | 結果 | cos | 比較: +側 (cuisine:italian) だけ | 比較: soy sauce だけ |
|---|---|---|---|---|
| 1 | sausage meat | 0.565 | olive oil | light soy sauce |
| 2 | italian style seasoning | 0.549 | salt | low sodium soy sauce |
| 3 | olive oil | 0.547 | ground black pepper | sesame oil |
| 4 | low sodium soy sauce | 0.545 | garlic cloves | toasted sesame oil |
| 5 | fresh parsley | 0.543 | extra-virgin olive oil | reduced sodium soy sauce |
| 6 | grated parmesan cheese | 0.541 | uncooked ziti | dark soy sauce |
| 7 | pecorino cheese | 0.538 | grated parmesan cheese | gluten free soy sauce |
| 8 | parmesan cheese | 0.534 | cooked meatballs | oyster sauce |

結果上位 8 と「+側だけ」上位 8 の重なり: 2 件

## soy sauce − chinese + mexican

| # | 結果 | cos | 比較: +側 (cuisine:mexican) だけ | 比較: soy sauce だけ |
|---|---|---|---|---|
| 1 | black beans | 0.645 | bean dip | light soy sauce |
| 2 | medium salsa | 0.593 | taco bell home originals | low sodium soy sauce |
| 3 | canned black beans | 0.592 | jalapeno chilies | sesame oil |
| 4 | taco toppings | 0.577 | kraft mexican style finely shredded four cheese | toasted sesame oil |
| 5 | tortillas | 0.575 | salsa | reduced sodium soy sauce |
| 6 | mexican cheese | 0.574 | salt | dark soy sauce |
| 7 | kraft mexican style finely shredded four cheese | 0.572 | chop green chilies, undrain | gluten free soy sauce |
| 8 | chop green chilies, undrain | 0.567 | 40% less sodium taco seasoning mix | oyster sauce |

結果上位 8 と「+側だけ」上位 8 の重なり: 2 件

## miso − japanese + italian

| # | 結果 | cos | 比較: +側 (cuisine:italian) だけ | 比較: miso だけ |
|---|---|---|---|---|
| 1 | balsamic reduction | 0.561 | olive oil | wakame |
| 2 | bocconcini | 0.552 | salt | mirin |
| 3 | caper berries | 0.548 | ground black pepper | white miso |
| 4 | fresh mozzarella balls | 0.545 | garlic cloves | buckwheat soba noodles |
| 5 | grated parmesan cheese | 0.543 | extra-virgin olive oil | dried bonito flakes |
| 6 | perciatelli | 0.541 | uncooked ziti | shredded nori |
| 7 | 2% low-fat cottage cheese | 0.537 | grated parmesan cheese | radish sprouts |
| 8 | frozen pizza dough | 0.537 | cooked meatballs | soba noodles |

結果上位 8 と「+側だけ」上位 8 の重なり: 1 件

## sake − japanese + french

| # | 結果 | cos | 比較: +側 (cuisine:french) だけ | 比較: sake だけ |
|---|---|---|---|---|
| 1 | grappa | 0.531 | salt | mirin |
| 2 | kirsch | 0.526 | butter | konbu |
| 3 | chopped fresh thyme | 0.521 | water | dried bonito flakes |
| 4 | riesling | 0.512 | compote | dashi |
| 5 | pinot noir | 0.510 | all-purpose flour | nori |
| 6 | dry white wine | 0.504 | unsalted butter | dashi kombu |
| 7 | truffle oil | 0.502 | almond liqueur | bonito flakes |
| 8 | nonfat dry milk | 0.501 | miniature semisweet chocolate chips | dashi powder |

結果上位 8 と「+側だけ」上位 8 の重なり: 0 件

## butter − french + indian

| # | 結果 | cos | 比較: +側 (cuisine:indian) だけ | 比較: butter だけ |
|---|---|---|---|---|
| 1 | ghee | 0.622 | salt | unsalted butter |
| 2 | margarine | 0.569 | water | margarine |
| 3 | salt | 0.532 | idli | melted butter |
| 4 | meat tenderizer | 0.529 | bottle gourd | milk |
| 5 | black cumin seeds | 0.518 | black cumin seeds | all-purpose flour |
| 6 | oil | 0.515 | ground turmeric | salt |
| 7 | black gram | 0.511 | red chili powder | heavy whipping cream |
| 8 | rose essence | 0.507 | garam masala | compote |

結果上位 8 と「+側だけ」上位 8 の重なり: 2 件

## flour tortillas − mexican + indian

| # | 結果 | cos | 比較: +側 (cuisine:indian) だけ | 比較: flour tortillas だけ |
|---|---|---|---|---|
| 1 | basmati rice | 0.604 | salt | corn tortillas |
| 2 | corn tortillas | 0.559 | water | tortilla chips |
| 3 | garam masala | 0.557 | idli | fajita size flour tortillas |
| 4 | yoghurt | 0.511 | bottle gourd | guacamole |
| 5 | whole wheat tortillas | 0.510 | black cumin seeds | tortillas |
| 6 | fajita size flour tortillas | 0.498 | ground turmeric | corn tortilla chips |
| 7 | tortillas | 0.496 | red chili powder | large flour tortillas |
| 8 | large flour tortillas | 0.490 | garam masala | whole wheat tortillas |

結果上位 8 と「+側だけ」上位 8 の重なり: 1 件

## fish sauce − thai + italian

| # | 結果 | cos | 比較: +側 (cuisine:italian) だけ | 比較: fish sauce だけ |
|---|---|---|---|---|
| 1 | prosciutto | 0.570 | olive oil | thai basil |
| 2 | dried basil | 0.556 | salt | lemongrass |
| 3 | fresh parsley | 0.541 | ground black pepper | thai fish sauce |
| 4 | fresh oregano | 0.540 | garlic cloves | rice vermicelli |
| 5 | pancetta | 0.537 | extra-virgin olive oil | kaffir lime leaves |
| 6 | mild italian sausage | 0.535 | uncooked ziti | vietnamese fish sauce |
| 7 | pesto | 0.529 | grated parmesan cheese | asian fish sauce |
| 8 | prepar pesto | 0.528 | cooked meatballs | beansprouts |

結果上位 8 と「+側だけ」上位 8 の重なり: 0 件

## parmesan cheese − italian + japanese

| # | 結果 | cos | 比較: +側 (cuisine:japanese) だけ | 比較: parmesan cheese だけ |
|---|---|---|---|---|
| 1 | dried udon | 0.610 | soy sauce | grated parmesan cheese |
| 2 | roasted white sesame seeds | 0.590 | dried udon | parmagiano reggiano |
| 3 | shredded nori | 0.581 | sesame oil | shredded parmesan cheese |
| 4 | soy sauce | 0.569 | mirin | parmigiano reggiano cheese |
| 5 | chili paste | 0.555 | water | freshly grated parmesan |
| 6 | mung bean noodles | 0.536 | roasted white sesame seeds | prepar pesto |
| 7 | sesame oil | 0.534 | sushi grade tuna | romano cheese |
| 8 | grated parmesan cheese | 0.523 | buckwheat soba noodles | frozen cheese ravioli |

結果上位 8 と「+側だけ」上位 8 の重なり: 4 件

## 食材だけ: soy sauce − ginger + basil

| # | 結果 | cos | 比較: +側 (basil) だけ | 比較: soy sauce だけ |
|---|---|---|---|---|
| 1 | fresh basil | 0.472 | fresh basil | light soy sauce |
| 2 | low sodium soy sauce | 0.431 | fresh herbs | low sodium soy sauce |
| 3 | reduced sodium soy sauce | 0.421 | basil leaves | sesame oil |
| 4 | bocconcini | 0.410 | fresh basil leaves | toasted sesame oil |
| 5 | corn flakes cereal | 0.385 | meatballs | reduced sodium soy sauce |
| 6 | pea shoots | 0.382 | herbs | dark soy sauce |
| 7 | sausage meat | 0.377 | italian sausage | gluten free soy sauce |
| 8 | italian sausage | 0.369 | linguini | oyster sauce |

結果上位 8 と「+側だけ」上位 8 の重なり: 2 件

## 食材だけ: sake − rice + grapes

| # | 結果 | cos | 比較: +側 (grapes) だけ | 比較: sake だけ |
|---|---|---|---|---|
| 1 | mirin | 0.477 | pink grapefruit | mirin |
| 2 | shiso | 0.461 | red grape | konbu |
| 3 | apricot preserves | 0.415 | amaretti cookies | dried bonito flakes |
| 4 | dashi powder | 0.397 | rose petals | dashi |
| 5 | navel oranges | 0.397 | unflavored gelatin | nori |
| 6 | dried bonito flakes | 0.392 | yellow rice | dashi kombu |
| 7 | napa cabbage leaves | 0.391 | biscuits | bonito flakes |
| 8 | matcha green tea powder | 0.391 | pita chips | dashi powder |

結果上位 8 と「+側だけ」上位 8 の重なり: 0 件

## 食材だけ: tofu − soy sauce + cheese

| # | 結果 | cos | 比較: +側 (cheese) だけ | 比較: tofu だけ |
|---|---|---|---|---|
| 1 | shredded cheese | 0.568 | shredded cheese | firm tofu |
| 2 | cheddar cheese | 0.484 | cheddar cheese | extra firm tofu |
| 3 | shredded cheddar cheese | 0.475 | mexican cheese | sesame oil |
| 4 | grating cheese | 0.472 | mexican cheese blend | shirataki |
| 5 | mexican cheese blend | 0.472 | sweet mini bells | baby bok choy |
| 6 | goat cheese | 0.443 | shredded cheddar cheese | soft tofu |
| 7 | chèvre | 0.435 | mozzarella cheese | mung bean noodles |
| 8 | monterey jack | 0.427 | monterey jack | roasted white sesame seeds |

結果上位 8 と「+側だけ」上位 8 の重なり: 5 件

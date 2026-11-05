# Exp-01b 食材の足し引き（k ごと）

- k = 取り除いた LDA 方向の本数。k=0 は Exp-01 と同じ空間（数値が Exp-01 と一致することを確認済み）
- 式・語彙・除外規則は Exp-01 と同じ。`cuisine:xxx` は**その k の空間で計算し直した** cuisine 重心
- 食材名の後ろの `[xxx]` は、その食材を含むレシピで cuisine xxx が偶然の 3 倍以上多いことを示す（先頭3文字。jap=japanese, fre=french 等）。学習データの出現頻度から機械的に付けた印で、空間とは無関係
- k が大きいと cuisine 重心の差は小さくなり、「− japanese + french」はほぼ「食材単体の近傍」になる。そのため mirin 単体の近傍も並べる

## mirin の近傍（文化除去後）

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | sake [jap] | sake [jap] | sake [jap] | sake [jap] | dark soy sauce [chi] | sesame oil [kor] |
| 2 | bonito flakes [jap] | dried bonito flakes [jap] | dried bonito flakes [jap] | dried bonito flakes [jap] | fish sauce [vie] | dark soy sauce [chi] |
| 3 | dried bonito flakes [jap] | bonito flakes [jap] | bonito flakes [jap] | fish sauce [vie] | dried bonito flakes [jap] | kochujang [kor] |
| 4 | togarashi [jap] | dashi [jap] | dashi [jap] | bonito flakes [jap] | oyster sauce [chi] | rice wine [kor] |
| 5 | dashi [jap] | togarashi [jap] | togarashi [jap] | dashi [jap] | shaoxing wine [chi] | fish sauce [vie] |
| 6 | nori [jap] | white miso [jap] | konbu [jap] | togarashi [jap] | udon [jap] | kewpie mayonnaise [jap] |
| 7 | white miso [jap] | nori [jap] | white miso [jap] | white miso [jap] | kewpie mayonnaise [jap] | black bean sauce [chi] |
| 8 | dashi powder [jap] | konbu [jap] | nori [jap] | shichimi togarashi [jap] | black bean sauce [chi] | oyster sauce [chi] |
| 9 | konbu [jap] | shichimi togarashi [jap] | shichimi togarashi [jap] | konbu [jap] | sesame oil [kor] | dried bonito flakes [jap] |
| 10 | buckwheat soba noodles [jap] | dashi powder [jap] | miso [jap] | shiso [jap] | bonito flakes [jap] | udon [jap] |

## Kazama 形式: mirin − japanese + french

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | white asparagus [fre] (0.56) | sake [jap] (0.54) | sake [jap] (0.55) | fresh thyme leaves [jam] (0.54) | fresh thyme leaves [jam] (0.57) | lemon curd [iri] (0.58) |
| 2 | chopped fresh thyme [fre] (0.56) | fresh thyme leaves [jam] (0.54) | bonito flakes [jap] (0.53) | chopped fresh thyme [fre] (0.54) | lemon curd [iri] (0.57) | frozen pastry puff sheets [bri] (0.58) |
| 3 | fresh thyme leaves [jam] (0.55) | chopped fresh thyme [fre] (0.54) | dashi [jap] (0.53) | sake [jap] (0.54) | chopped fresh thyme [fre] (0.55) | fresh thyme leaves [jam] (0.56) |
| 4 | parsley sprigs [fre] (0.54) | dashi [jap] (0.54) | fresh thyme leaves [jam] (0.53) | bonito flakes [jap] (0.52) | amaretti cookies [ita] (0.54) | miniature semisweet chocolate chips [ita] (0.56) |
| 5 | candied lemon peel [bri] (0.52) | bonito flakes [jap] (0.53) | chopped fresh thyme [fre] (0.53) | parsley sprigs [fre] (0.51) | white asparagus [fre] (0.54) | amaretti [bri] (0.55) |
| 6 | unsalted butter [bri] (0.52) | white asparagus [fre] (0.53) | dashi powder [jap] (0.52) | dashi [jap] (0.51) | frozen pastry puff sheets [bri] (0.52) | gala apples [fre] (0.55) |
| 7 | dried bonito flakes [jap] (0.51) | dashi powder [jap] (0.53) | white asparagus [fre] (0.52) | lemon curd [iri] (0.51) | bechamel [gre] (0.52) | amaretti cookies [ita] (0.55) |
| 8 | lemon curd [iri] (0.51) | parsley sprigs [fre] (0.53) | parsley sprigs [fre] (0.51) | fish sauce [vie] (0.51) | raspberry liqueur [fre] (0.52) | bechamel [gre] (0.55) |
| − 側 cuisine の印が付いた数 | 1 | 4 | 4 | 3 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 1 | 0 | 0 | 1 | 0 | 0 |

## soy sauce − japanese + italian

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | sausage meat [bri] (0.56) | low sodium soy sauce [chi] (0.57) | low sodium soy sauce [chi] (0.56) | low sodium soy sauce [chi] (0.56) | low sodium soy sauce [chi] (0.57) | dijon [fre] (0.63) |
| 2 | italian style seasoning [ita] (0.55) | sausage meat [bri] (0.56) | sausage meat [bri] (0.55) | sausage meat [bri] (0.54) | dijon [fre] (0.56) | low sodium soy sauce [chi] (0.58) |
| 3 | olive oil (0.55) | italian style seasoning [ita] (0.54) | pecorino cheese [ita] (0.54) | light soy sauce [chi] (0.53) | green olives [mor] (0.54) | fresh parsley [caj] (0.57) |
| 4 | low sodium soy sauce [chi] (0.55) | parmesan cheese [ita] (0.54) | light soy sauce [chi] (0.53) | pecorino cheese [ita] (0.53) | fresh parsley [caj] (0.54) | andouille sausage [caj] (0.57) |
| 5 | fresh parsley [caj] (0.54) | pecorino cheese [ita] (0.53) | fresh parsley [caj] (0.53) | small red beans [caj] (0.52) | calf liver [iri] (0.53) | dried basil [ita] (0.56) |
| 6 | grated parmesan cheese [ita] (0.54) | fresh parsley [caj] (0.53) | olive oil (0.52) | fresh parsley [caj] (0.52) | olive oil (0.53) | sausage meat [bri] (0.56) |
| 7 | pecorino cheese [ita] (0.54) | grated parmesan cheese [ita] (0.53) | parmesan cheese [ita] (0.52) | olive oil (0.51) | pecorino cheese [ita] (0.52) | worcestershire sauce [caj] (0.55) |
| 8 | parmesan cheese [ita] (0.53) | light soy sauce [chi] (0.52) | italian style seasoning [ita] (0.52) | calf liver [iri] (0.51) | grated parmesan cheese [ita] (0.52) | calf liver [iri] (0.55) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 1 | 1 | 1 | 2 | 0 |

## soy sauce − chinese + mexican

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | black beans [mex] (0.65) | black beans [mex] (0.62) | black beans [mex] (0.57) | black beans [mex] (0.57) | low sodium soy sauce [chi] (0.56) | dijon [fre] (0.61) |
| 2 | medium salsa [mex] (0.59) | canned black beans [mex] (0.58) | low sodium soy sauce [chi] (0.56) | low sodium soy sauce [chi] (0.55) | black beans [mex] (0.56) | light red kidney beans [caj] (0.57) |
| 3 | canned black beans [mex] (0.59) | tortillas [mex] (0.57) | canned black beans [mex] (0.54) | light red kidney beans [caj] (0.54) | light red kidney beans [caj] (0.55) | small red beans [caj] (0.57) |
| 4 | taco toppings [mex] (0.58) | mexican cheese [mex] (0.56) | light red kidney beans [caj] (0.52) | small red beans [caj] (0.54) | red gold diced tomatoes [caj] (0.54) | black beans [mex] (0.57) |
| 5 | tortillas [mex] (0.57) | medium salsa [mex] (0.55) | dijon [fre] (0.51) | red gold diced tomatoes [caj] (0.53) | small red beans [caj] (0.54) | low sodium soy sauce [chi] (0.56) |
| 6 | mexican cheese [mex] (0.57) | light red kidney beans [caj] (0.55) | mexican cheese [mex] (0.51) | canned black beans [mex] (0.53) | medium salsa [mex] (0.53) | red gold diced tomatoes [caj] (0.56) |
| 7 | kraft mexican style finely shredded four cheese [mex] (0.57) | corn tortillas [mex] (0.54) | tortillas [mex] (0.51) | soft corn tortillas [mex] (0.52) | dijon [fre] (0.53) | worcestershire sauce [caj] (0.56) |
| 8 | chop green chilies, undrain [mex] (0.57) | taco toppings [mex] (0.54) | red gold diced tomatoes [caj] (0.51) | medium salsa [mex] (0.51) | soft corn tortillas [mex] (0.52) | hot sauce [caj] (0.56) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 1 | 1 | 1 | 1 |
| 「+ 側だけ」上位8との重なり | 2 | 0 | 0 | 0 | 0 | 0 |

## miso − japanese + italian

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | balsamic reduction [bri] (0.56) | balsamic reduction [bri] (0.52) | balsamic reduction [bri] (0.54) | balsamic reduction [bri] (0.53) | frozen pizza dough [gre] (0.54) | caper berries [ita] (0.56) |
| 2 | bocconcini [ita] (0.55) | bocconcini [ita] (0.52) | fresh mozzarella balls [ita] (0.51) | frozen pizza dough [gre] (0.51) | caper berries [ita] (0.51) | frozen pizza dough [gre] (0.56) |
| 3 | caper berries [ita] (0.55) | crumbled ricotta salata cheese [ita] (0.51) | bocconcini [ita] (0.51) | fresh mozzarella balls [ita] (0.50) | whole wheat pita [gre] (0.50) | balsamic reduction [bri] (0.54) |
| 4 | fresh mozzarella balls [ita] (0.55) | 2% low-fat cottage cheese [gre] (0.51) | 2% low-fat cottage cheese [gre] (0.50) | bocconcini [ita] (0.49) | balsamic reduction [bri] (0.50) | yukon gold [bri] (0.54) |
| 5 | grated parmesan cheese [ita] (0.54) | caper berries [ita] (0.51) | frozen pizza dough [gre] (0.50) | oven-ready lasagna noodles [ita] (0.49) | veal chops [ita] (0.50) | wild mushrooms [ita] (0.54) |
| 6 | perciatelli [ita] (0.54) | oven-ready lasagna noodles [ita] (0.51) | oven-ready lasagna noodles [ita] (0.50) | 2% low-fat cottage cheese [gre] (0.49) | 2% low-fat cottage cheese [gre] (0.50) | gaeta olives [gre] (0.52) |
| 7 | 2% low-fat cottage cheese [gre] (0.54) | grated parmesan cheese [ita] (0.50) | pasta shells [ita] (0.50) | balsamic vinaigrette [gre] (0.48) | fresh marjoram [fre] (0.50) | veal chops [ita] (0.52) |
| 8 | frozen pizza dough [gre] (0.54) | perciatelli [ita] (0.50) | crumbled ricotta salata cheese [ita] (0.50) | pasta shells [ita] (0.48) | prebaked pizza crusts [ita] (0.49) | whole wheat pita [gre] (0.52) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 1 | 1 | 0 | 0 | 0 | 1 |

## sake − japanese + french

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | grappa [ita] (0.53) | grappa [ita] (0.50) | mirin [jap] (0.51) | grappa [ita] (0.52) | dry white wine [spa] (0.54) | riesling [fre] (0.63) |
| 2 | kirsch [fre] (0.53) | mirin [jap] (0.50) | grappa [ita] (0.50) | riesling [fre] (0.50) | grappa [ita] (0.54) | dry white wine [spa] (0.60) |
| 3 | chopped fresh thyme [fre] (0.52) | kirsch [fre] (0.50) | riesling [fre] (0.50) | chopped fresh thyme [fre] (0.50) | riesling [fre] (0.52) | grappa [ita] (0.59) |
| 4 | riesling [fre] (0.51) | riesling [fre] (0.50) | kirsch [fre] (0.50) | mirin [jap] (0.49) | reduced fat milk [fre] (0.52) | reduced fat milk [fre] (0.55) |
| 5 | pinot noir [fre] (0.51) | chopped fresh thyme [fre] (0.49) | chopped fresh thyme [fre] (0.49) | dry white wine [spa] (0.49) | dry red wine [spa] (0.52) | dry red wine [spa] (0.55) |
| 6 | dry white wine [spa] (0.50) | truffle oil [ita] (0.49) | truffle oil [ita] (0.49) | thyme sprigs [fre] (0.48) | pitted kalamata olives [gre] (0.51) | sauvignon blanc [fre] (0.54) |
| 7 | truffle oil [ita] (0.50) | pinot noir [fre] (0.48) | pinot noir [fre] (0.48) | reduced fat milk [fre] (0.47) | calimyrna figs [bri] (0.51) | dried plum [mor] (0.54) |
| 8 | nonfat dry milk [fre] (0.50) | reduced fat milk [fre] (0.48) | nonfat dry milk [fre] (0.48) | calimyrna figs [bri] (0.47) | sauvignon blanc [fre] (0.50) | limoncello [ita] (0.54) |
| − 側 cuisine の印が付いた数 | 0 | 1 | 1 | 1 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 1 | 1 | 1 | 1 |

## butter − french + indian

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | ghee [ind] (0.62) | ghee [ind] (0.61) | margarine [iri] (0.61) | margarine [iri] (0.60) | margarine [iri] (0.60) | ghee [ind] (0.62) |
| 2 | margarine [iri] (0.57) | margarine [iri] (0.57) | salt (0.58) | salt (0.59) | salt (0.59) | margarine [iri] (0.61) |
| 3 | salt (0.53) | salt (0.55) | ghee [ind] (0.57) | ghee [ind] (0.57) | ghee [ind] (0.59) | salt (0.60) |
| 4 | meat tenderizer [ind] (0.53) | black lentil [ind] (0.53) | unsalted butter [bri] (0.53) | oil [fil] (0.53) | oil [fil] (0.55) | oil [fil] (0.57) |
| 5 | black cumin seeds [ind] (0.52) | black cumin seeds [ind] (0.52) | oil [fil] (0.53) | unsalted butter [bri] (0.53) | unsalted butter [bri] (0.54) | unsalted butter [bri] (0.55) |
| 6 | oil [fil] (0.52) | black gram [ind] (0.52) | milk [bri] (0.52) | olive oil (0.51) | milk [bri] (0.52) | olive oil (0.53) |
| 7 | black gram [ind] (0.51) | meat tenderizer [ind] (0.52) | melted butter [sou] (0.50) | milk [bri] (0.51) | olive oil (0.51) | milk [bri] (0.53) |
| 8 | rose essence [ind] (0.51) | oil [fil] (0.50) | salted butter [sou] (0.50) | water (0.50) | water (0.51) | potatoes [iri] (0.52) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 3 | 1 | 3 | 2 | 1 |

## flour tortillas − mexican + indian

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | basmati rice [ind] (0.60) | basmati rice [ind] (0.59) | corn tortillas [mex] (0.56) | corn tortillas [mex] (0.57) | corn tortillas [mex] (0.58) | corn tortillas [mex] (0.59) |
| 2 | corn tortillas [mex] (0.56) | corn tortillas [mex] (0.58) | basmati rice [ind] (0.52) | basmati rice [ind] (0.52) | penne [ita] (0.52) | basmati rice [ind] (0.53) |
| 3 | garam masala [ind] (0.56) | garam masala [ind] (0.55) | rigatoni [ita] (0.49) | rigatoni [ita] (0.51) | basmati rice [ind] (0.51) | pasta [ita] (0.52) |
| 4 | yoghurt [ind] (0.51) | whole wheat tortillas [mex] (0.52) | penne [ita] (0.49) | penne [ita] (0.50) | rigatoni [ita] (0.51) | penne [ita] (0.51) |
| 5 | whole wheat tortillas [mex] (0.51) | tortillas [mex] (0.51) | fajita size flour tortillas [mex] (0.49) | fajita size flour tortillas [mex] (0.49) | fajita size flour tortillas [mex] (0.50) | whole wheat tortillas [mex] (0.51) |
| 6 | fajita size flour tortillas [mex] (0.50) | yoghurt [ind] (0.50) | whole wheat tortillas [mex] (0.48) | pizza crust [ita] (0.49) | pasta [ita] (0.49) | penne pasta [ita] (0.50) |
| 7 | tortillas [mex] (0.50) | large flour tortillas [mex] (0.50) | pizza crust [ita] (0.48) | pasta [ita] (0.48) | whole wheat tortillas [mex] (0.49) | rigatoni [ita] (0.49) |
| 8 | large flour tortillas [mex] (0.49) | tortilla chips [mex] (0.49) | penne pasta [ita] (0.47) | penne pasta [ita] (0.48) | penne pasta [ita] (0.49) | fajita size flour tortillas [mex] (0.49) |
| − 側 cuisine の印が付いた数 | 5 | 5 | 3 | 2 | 3 | 3 |
| 「+ 側だけ」上位8との重なり | 1 | 0 | 0 | 0 | 0 | 0 |

## fish sauce − thai + italian

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | prosciutto [ita] (0.57) | dried basil [ita] (0.55) | dried basil [ita] (0.53) | fresh parsley [caj] (0.53) | garlic bulb [iri] (0.56) | fresh parsley [caj] (0.60) |
| 2 | dried basil [ita] (0.56) | prosciutto [ita] (0.54) | cooked rigatoni [ita] (0.53) | fresh oregano [gre] (0.52) | fresh parsley [caj] (0.54) | garlic bulb [iri] (0.59) |
| 3 | fresh parsley [caj] (0.54) | pancetta [ita] (0.53) | prosciutto [ita] (0.53) | parsley sprigs [fre] (0.52) | fresh oregano [gre] (0.54) | sausage links [caj] (0.57) |
| 4 | fresh oregano [gre] (0.54) | pesto [ita] (0.53) | fresh oregano [gre] (0.53) | garlic bulb [iri] (0.51) | hot italian sausages [ita] (0.54) | hot italian sausages [ita] (0.57) |
| 5 | pancetta [ita] (0.54) | fresh oregano [gre] (0.53) | pesto [ita] (0.52) | dried basil [ita] (0.51) | pancetta [ita] (0.53) | kalamata [gre] (0.57) |
| 6 | mild italian sausage [ita] (0.53) | fresh parsley [caj] (0.53) | pancetta [ita] (0.52) | pancetta [ita] (0.51) | parsley sprigs [fre] (0.53) | fresh oregano [gre] (0.57) |
| 7 | pesto [ita] (0.53) | cooked rigatoni [ita] (0.52) | fresh parsley [caj] (0.51) | hot italian sausages [ita] (0.51) | kalamata [gre] (0.52) | green olives [mor] (0.56) |
| 8 | prepar pesto [ita] (0.53) | prepar pesto [ita] (0.52) | hot italian sausages [ita] (0.51) | cooked rigatoni [ita] (0.50) | prosciutto [ita] (0.51) | perciatelli [ita] (0.55) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 0 | 0 | 0 |

## parmesan cheese − italian + japanese

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | dried udon [jap] (0.61) | grated parmesan cheese [ita] (0.61) | grated parmesan cheese [ita] (0.62) | grated parmesan cheese [ita] (0.64) | grated parmesan cheese [ita] (0.62) | grated parmesan cheese [ita] (0.62) |
| 2 | roasted white sesame seeds [jap] (0.59) | dried udon [jap] (0.58) | dried udon [jap] (0.58) | dried udon [jap] (0.55) | roasted white sesame seeds [jap] (0.55) | roasted white sesame seeds [jap] (0.55) |
| 3 | shredded nori [kor] (0.58) | roasted white sesame seeds [jap] (0.57) | roasted white sesame seeds [jap] (0.56) | roasted white sesame seeds [jap] (0.54) | dried udon [jap] (0.54) | tonkatsu sauce [jap] (0.54) |
| 4 | soy sauce [kor] (0.57) | shredded nori [kor] (0.55) | shredded nori [kor] (0.54) | shredded nori [kor] (0.52) | soy sauce [kor] (0.54) | soy sauce [kor] (0.54) |
| 5 | chili paste [kor] (0.56) | soy sauce [kor] (0.54) | soy sauce [kor] (0.53) | soy sauce [kor] (0.51) | shredded nori [kor] (0.52) | dried udon [jap] (0.53) |
| 6 | mung bean noodles [vie] (0.54) | shredded parmesan cheese [ita] (0.51) | kimchi juice [kor] (0.50) | shredded parmesan cheese [ita] (0.51) | fish balls [fil] (0.51) | shredded nori [kor] (0.52) |
| 7 | sesame oil [kor] (0.53) | parmagiano reggiano [ita] (0.50) | shredded parmesan cheese [ita] (0.50) | parmagiano reggiano [ita] (0.50) | kimchi juice [kor] (0.50) | fish balls [fil] (0.52) |
| 8 | grated parmesan cheese [ita] (0.52) | kimchi juice [kor] (0.49) | chili paste [kor] (0.50) | fish balls [fil] (0.49) | mung bean noodles [vie] (0.49) | kimchi juice [kor] (0.51) |
| − 側 cuisine の印が付いた数 | 1 | 3 | 2 | 3 | 1 | 1 |
| 「+ 側だけ」上位8との重なり | 4 | 3 | 3 | 3 | 3 | 3 |

## 食材だけ: soy sauce − ginger + basil

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | fresh basil [ita] (0.47) | low sodium soy sauce [chi] (0.52) | low sodium soy sauce [chi] (0.50) | low sodium soy sauce [chi] (0.50) | low sodium soy sauce [chi] (0.51) | low sodium soy sauce [chi] (0.51) |
| 2 | low sodium soy sauce [chi] (0.43) | reduced sodium soy sauce [chi] (0.48) | reduced sodium soy sauce [chi] (0.48) | reduced sodium soy sauce [chi] (0.48) | reduced sodium soy sauce [chi] (0.50) | reduced sodium soy sauce [chi] (0.51) |
| 3 | reduced sodium soy sauce [chi] (0.42) | fresh basil [ita] (0.44) | fresh basil [ita] (0.45) | fresh basil [ita] (0.46) | fresh basil [ita] (0.46) | light soy sauce [chi] (0.46) |
| 4 | bocconcini [ita] (0.41) | light soy sauce [chi] (0.44) | light soy sauce [chi] (0.43) | light soy sauce [chi] (0.42) | light soy sauce [chi] (0.45) | fresh basil [ita] (0.46) |
| 5 | corn flakes cereal [sou] (0.38) | bocconcini [ita] (0.41) | bocconcini [ita] (0.42) | bocconcini [ita] (0.41) | balsamico bianco [gre] (0.42) | balsamico bianco [gre] (0.44) |
| 6 | pea shoots [fil] (0.38) | hoisin sauce [chi] (0.39) | hoisin sauce [chi] (0.37) | worcestershire sauce [caj] (0.40) | bocconcini [ita] (0.41) | hoisin sauce [chi] (0.42) |
| 7 | sausage meat [bri] (0.38) | pea shoots [fil] (0.38) | corn flakes cereal [sou] (0.37) | corn flakes cereal [sou] (0.39) | hoisin sauce [chi] (0.41) | worcestershire sauce [caj] (0.42) |
| 8 | italian sausage [ita] (0.37) | water chestnuts [chi] (0.38) | pea shoots [fil] (0.37) | hot sauce [caj] (0.39) | corn flakes cereal [sou] (0.40) | bocconcini [ita] (0.41) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 1 | 1 | 1 | 1 | 1 |

## 食材だけ: sake − rice + grapes

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | mirin [jap] (0.48) | mirin [jap] (0.49) | mirin [jap] (0.48) | grappa [ita] (0.47) | grappa [ita] (0.50) | grappa [ita] (0.56) |
| 2 | shiso [jap] (0.46) | shiso [jap] (0.45) | shiso [jap] (0.46) | calimyrna figs [bri] (0.45) | calimyrna figs [bri] (0.49) | vin santo [ita] (0.53) |
| 3 | apricot preserves [rus] (0.42) | apricot preserves [rus] (0.42) | apricot preserves [rus] (0.42) | shiso [jap] (0.43) | sauterne [fre] (0.47) | sauterne [fre] (0.53) |
| 4 | dashi powder [jap] (0.40) | calimyrna figs [bri] (0.41) | grappa [ita] (0.42) | amaretti cookies [ita] (0.43) | crème de cassis [fre] (0.46) | calimyrna figs [bri] (0.52) |
| 5 | navel oranges [spa] (0.40) | grappa [ita] (0.41) | calimyrna figs [bri] (0.41) | salted roast peanuts [tha] (0.43) | amaretti cookies [ita] (0.46) | tangerine juice [bri] (0.52) |
| 6 | dried bonito flakes [jap] (0.39) | vin santo [ita] (0.41) | poblano chiles [mex] (0.40) | mirin [jap] (0.43) | poblano chiles [mex] (0.46) | seedless red grapes [mor] (0.50) |
| 7 | napa cabbage leaves [chi] (0.39) | navel oranges [spa] (0.40) | vin santo [ita] (0.40) | poblano chiles [mex] (0.43) | raspberry liqueur [fre] (0.45) | salted roast peanuts [tha] (0.49) |
| 8 | matcha green tea powder [jap] (0.39) | dried bonito flakes [jap] (0.39) | navel oranges [spa] (0.40) | white peaches [spa] (0.42) | vin santo [ita] (0.45) | apricot preserves [rus] (0.49) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 1 | 2 | 0 |

## 食材だけ: tofu − soy sauce + cheese

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | shredded cheese [mex] (0.57) | shredded cheese [mex] (0.52) | shredded cheese [mex] (0.51) | shredded cheese [mex] (0.53) | shredded cheese [mex] (0.54) | shredded cheese [mex] (0.53) |
| 2 | cheddar cheese [mex] (0.48) | shredded cheddar cheese [mex] (0.45) | shredded cheddar cheese [mex] (0.42) | cheddar cheese [mex] (0.46) | cheddar cheese [mex] (0.45) | cheddar cheese [mex] (0.47) |
| 3 | shredded cheddar cheese [mex] (0.47) | grating cheese [bra] (0.44) | grating cheese [bra] (0.42) | shredded cheddar cheese [mex] (0.43) | shredded cheddar cheese [mex] (0.45) | grating cheese [bra] (0.45) |
| 4 | grating cheese [bra] (0.47) | cheddar cheese [mex] (0.44) | goat cheese (0.42) | grating cheese [bra] (0.41) | mexican cheese blend [mex] (0.43) | shredded cheddar cheese [mex] (0.44) |
| 5 | mexican cheese blend [mex] (0.47) | mexican cheese blend [mex] (0.44) | cheddar cheese [mex] (0.42) | mexican cheese blend [mex] (0.40) | grating cheese [bra] (0.42) | chèvre [mor] (0.44) |
| 6 | goat cheese (0.44) | goat cheese (0.41) | mexican cheese blend [mex] (0.41) | monterey jack [mex] (0.40) | reduced fat cheddar cheese [mex] (0.41) | mexican cheese blend [mex] (0.44) |
| 7 | chèvre [mor] (0.44) | chèvre [mor] (0.40) | chèvre [mor] (0.40) | chèvre [mor] (0.40) | monterey jack [mex] (0.41) | reduced fat cheddar cheese [mex] (0.43) |
| 8 | monterey jack [mex] (0.43) | monterey jack [mex] (0.40) | monterey jack [mex] (0.37) | goat cheese (0.39) | chèvre [mor] (0.40) | goat cheese (0.40) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 5 | 5 | 5 | 5 | 4 | 4 |

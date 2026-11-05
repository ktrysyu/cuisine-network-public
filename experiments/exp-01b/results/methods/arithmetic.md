# Exp-01b 追加: 食材の足し引き（方法 × k）

- 形式は results/arithmetic.md と同じ。`[xxx]` はその食材を含むレシピで cuisine xxx が偶然の 3 倍以上多いことを示す印
- `cuisine:xxx` はその空間で計算し直した cuisine 重心

## mirin の近傍（除去後）

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | sake [jap] | sake [jap] | sake [jap] | sake [jap] | sake [jap] | brewed espresso [ita] |
| 2 | bonito flakes [jap] | dried bonito flakes [jap] | togarashi [jap] | dried bonito flakes [jap] | fish sauce [vie] | mini chocolate chips [gre] |
| 3 | dried bonito flakes [jap] | dashi [jap] | dashi [jap] | bonito flakes [jap] | dashi [jap] | oreo cookies [iri] |
| 4 | togarashi [jap] | bonito flakes [jap] | dried bonito flakes [jap] | dashi [jap] | dried bonito flakes [jap] | milk chocolate chips [bra] |
| 5 | dashi [jap] | togarashi [jap] | bonito flakes [jap] | togarashi [jap] | bonito flakes [jap] | espresso beans [iri] |
| 6 | nori [jap] | white miso [jap] | white miso [jap] | white miso [jap] | red curry paste [tha] | vanilla pudding [bri] |
| 7 | white miso [jap] | nori [jap] | nori [jap] | nori [jap] | white miso [jap] | frangelico [ita] |
| 8 | dashi powder [jap] | dashi powder [jap] | nori sheets [jap] | kewpie mayonnaise [jap] | konbu [jap] | lemon curd [iri] |
| 9 | konbu [jap] | konbu [jap] | konbu [jap] | nori sheets [jap] | brewed espresso [ita] | baileys irish cream liqueur [iri] |
| 10 | buckwheat soba noodles [jap] | wasabi paste [jap] | dashi powder [jap] | wasabi paste [jap] | pillsburytm refrigerated crescent dinner rolls [mex] | miniature semisweet chocolate chips [ita] |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | sake [jap] | sake [jap] | dried bonito flakes [jap] | sake [jap] | dried bonito flakes [jap] | sake [jap] | frozen pastry puff sheets [bri] |
| 2 | bonito flakes [jap] | bonito flakes [jap] | sake [jap] | dried bonito flakes [jap] | sake [jap] | white asparagus [fre] | seasoned bread crumbs [ita] |
| 3 | dried bonito flakes [jap] | dried bonito flakes [jap] | bonito flakes [jap] | bonito flakes [jap] | togarashi [jap] | dashi powder [jap] | sharp white cheddar cheese [sou] |
| 4 | togarashi [jap] | togarashi [jap] | dashi [jap] | dashi [jap] | dashi [jap] | togarashi [jap] | bacon grease [sou] |
| 5 | dashi [jap] | dashi [jap] | togarashi [jap] | togarashi [jap] | white miso [jap] | red curry paste [tha] | sandwich rolls [vie] |
| 6 | nori [jap] | nori [jap] | white miso [jap] | nori [jap] | bonito flakes [jap] | chopped fresh thyme [fre] | truffle oil [ita] |
| 7 | white miso [jap] | white miso [jap] | dashi powder [jap] | white miso [jap] | dashi powder [jap] | stone ground mustard [fre] | stout [iri] |
| 8 | dashi powder [jap] | dashi powder [jap] | shichimi togarashi [jap] | miso [jap] | miso [jap] | white miso [jap] | chopped fresh thyme [fre] |
| 9 | konbu [jap] | konbu [jap] | nori [jap] | konbu [jap] | nori [jap] | fresh thyme leaves [jam] | dark molasses [jam] |
| 10 | buckwheat soba noodles [jap] | nori sheets [jap] | kewpie mayonnaise [jap] | nori sheets [jap] | shichimi togarashi [jap] | red miso [jap] | vegetarian refried beans [mex] |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | sake [jap] | sake [jap] | sake [jap] | diced tomatoes | oxtails [vie] | champagne vinegar [fre] |
| 2 | bonito flakes [jap] | dried bonito flakes [jap] | fresh thyme leaves [jam] | bonito flakes [jap] | dried thai chili [tha] | croutons [spa] |
| 3 | dried bonito flakes [jap] | konbu [jap] | dried plum [mor] | tomatoes with juice | less sodium beef broth [mor] | unsweetened almond milk [bra] |
| 4 | togarashi [jap] | bonito flakes [jap] | bonito flakes [jap] | red curry paste [tha] | nonstick spray | small white beans [fre] |
| 5 | dashi [jap] | shimeji mushrooms [jap] | dark soy sauce [chi] | baking potatoes [iri] | low-fat milk [bri] | pomegranate juice [mor] |
| 6 | nori [jap] | togarashi [jap] | shaoxing [chi] | tomato paste | baking potatoes [iri] | garlic salt |
| 7 | white miso [jap] | white miso [jap] | grappa [ita] | crushed tomatoes | sharp white cheddar cheese [sou] | coriander seeds [ind] |
| 8 | dashi powder [jap] | dashi [jap] | fresh thyme [jam] | plum tomatoes | lager beer [bri] | coconut oil [tha] |
| 9 | konbu [jap] | buckwheat soba noodles [jap] | seasoned bread crumbs [ita] | diced tomatoes with garlic and onion [caj] | crème fraîche [fre] | bechamel [gre] |
| 10 | buckwheat soba noodles [jap] | chili oil [chi] | salt | sharp white cheddar cheese [sou] | boneless beef chuck roast [kor] | teas [jam] |

## Kazama 形式: mirin − japanese + french

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | white asparagus [fre] (0.56) | sake [jap] (0.65) | sake [jap] (0.63) | sake [jap] (0.62) | fish sauce [vie] (0.62) | brewed espresso [ita] (0.66) |
| 2 | chopped fresh thyme [fre] (0.56) | bonito flakes [jap] (0.62) | bonito flakes [jap] (0.59) | bonito flakes [jap] (0.60) | sake [jap] (0.61) | mini chocolate chips [gre] (0.66) |
| 3 | fresh thyme leaves [jam] (0.55) | dried bonito flakes [jap] (0.61) | white miso [jap] (0.58) | dried bonito flakes [jap] (0.59) | dashi [jap] (0.60) | oreo cookies [iri] (0.65) |
| 4 | parsley sprigs [fre] (0.54) | dashi [jap] (0.61) | dashi [jap] (0.57) | dashi [jap] (0.57) | dried bonito flakes [jap] (0.59) | milk chocolate chips [bra] (0.64) |
| 5 | candied lemon peel [bri] (0.52) | dashi powder [jap] (0.60) | dried bonito flakes [jap] (0.57) | white miso [jap] (0.56) | bonito flakes [jap] (0.58) | espresso beans [iri] (0.64) |
| 6 | unsalted butter [bri] (0.52) | white miso [jap] (0.58) | red miso [jap] (0.56) | red miso [jap] (0.56) | konbu [jap] (0.56) | vanilla pudding [bri] (0.64) |
| 7 | dried bonito flakes [jap] (0.51) | konbu [jap] (0.57) | buckwheat soba noodles [jap] (0.56) | shichimi togarashi [jap] (0.56) | brewed espresso [ita] (0.56) | lemon curd [iri] (0.63) |
| 8 | lemon curd [iri] (0.51) | red miso [jap] (0.57) | togarashi [jap] (0.56) | togarashi [jap] (0.55) | salt (0.56) | frangelico [ita] (0.63) |
| − 側 cuisine の印が付いた数 | 1 | 8 | 8 | 8 | 5 | 0 |
| 「+ 側だけ」上位8との重なり | 1 | 0 | 0 | 0 | 1 | 4 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | white asparagus [fre] (0.56) | chopped fresh thyme [fre] (0.56) | sake [jap] (0.59) | sake [jap] (0.60) | sake [jap] (0.58) | white asparagus [fre] (0.54) | frozen pastry puff sheets [bri] (0.52) |
| 2 | chopped fresh thyme [fre] (0.56) | fresh thyme leaves [jam] (0.56) | dashi [jap] (0.56) | bonito flakes [jap] (0.56) | chopped fresh thyme [fre] (0.56) | lemon curd [iri] (0.51) | mini chocolate chips [gre] (0.51) |
| 3 | fresh thyme leaves [jam] (0.55) | white asparagus [fre] (0.55) | bonito flakes [jap] (0.55) | dashi [jap] (0.56) | dried bonito flakes [jap] (0.55) | fresh thyme leaves [jam] (0.51) | truffle oil [ita] (0.50) |
| 4 | parsley sprigs [fre] (0.54) | parsley sprigs [fre] (0.53) | fresh thyme leaves [jam] (0.55) | dried bonito flakes [jap] (0.56) | dashi powder [jap] (0.54) | chopped fresh thyme [fre] (0.51) | pie dough [fre] (0.49) |
| 5 | candied lemon peel [bri] (0.52) | dried bonito flakes [jap] (0.53) | dashi powder [jap] (0.54) | dashi powder [jap] (0.55) | bonito flakes [jap] (0.53) | sake [jap] (0.51) | large eggs (0.49) |
| 6 | unsalted butter [bri] (0.52) | bonito flakes [jap] (0.52) | chopped fresh thyme [fre] (0.54) | chopped fresh thyme [fre] (0.54) | dashi [jap] (0.53) | stone ground mustard [fre] (0.49) | dark molasses [jam] (0.49) |
| 7 | dried bonito flakes [jap] (0.51) | sake [jap] (0.52) | dried bonito flakes [jap] (0.54) | white miso [jap] (0.53) | fresh thyme leaves [jam] (0.52) | brewed espresso [ita] (0.48) | miniature semisweet chocolate chips [ita] (0.48) |
| 8 | lemon curd [iri] (0.51) | dashi [jap] (0.52) | red miso [jap] (0.53) | fresh thyme leaves [jam] (0.53) | red miso [jap] (0.51) | dashi powder [jap] (0.48) | chopped fresh thyme [fre] (0.47) |
| − 側 cuisine の印が付いた数 | 1 | 4 | 6 | 6 | 6 | 2 | 0 |
| 「+ 側だけ」上位8との重なり | 1 | 0 | 0 | 0 | 0 | 0 | 1 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | white asparagus [fre] (0.56) | white asparagus [fre] (0.59) | fresh thyme leaves [jam] (0.59) | diced tomatoes (0.60) | oxtails [vie] (0.70) | teas [jam] (0.98) |
| 2 | chopped fresh thyme [fre] (0.56) | fresh thyme leaves [jam] (0.58) | grappa [ita] (0.58) | baking potatoes [iri] (0.60) | low-fat milk [bri] (0.64) | bouquet [iri] (0.97) |
| 3 | fresh thyme leaves [jam] (0.55) | grappa [ita] (0.58) | mini chocolate chips [gre] (0.57) | unsalted butter [bri] (0.59) | less sodium beef broth [mor] (0.62) | croutons [spa] (0.96) |
| 4 | parsley sprigs [fre] (0.54) | unsalted butter [bri] (0.55) | unsalted butter [bri] (0.55) | tomatoes with juice (0.56) | baking potatoes [iri] (0.62) | bechamel [gre] (0.95) |
| 5 | candied lemon peel [bri] (0.52) | chopped fresh thyme [fre] (0.55) | lemon curd [iri] (0.55) | bonito flakes [jap] (0.56) | nonstick spray (0.61) | unsweetened almond milk [bra] (0.95) |
| 6 | unsalted butter [bri] (0.52) | amaretti [bri] (0.55) | sauvignon blanc [fre] (0.55) | red curry paste [tha] (0.54) | crème fraîche [fre] (0.61) | mild cheddar cheese [iri] (0.95) |
| 7 | dried bonito flakes [jap] (0.51) | lemon curd [iri] (0.55) | dried plum [mor] (0.54) | mint sprigs (0.54) | dried thai chili [tha] (0.59) | champagne vinegar [fre] (0.95) |
| 8 | lemon curd [iri] (0.51) | sake [jap] (0.53) | seasoned bread crumbs [ita] (0.53) | sharp white cheddar cheese [sou] (0.53) | sharp white cheddar cheese [sou] (0.57) | spring! water [jap] (0.94) |
| − 側 cuisine の印が付いた数 | 1 | 1 | 0 | 1 | 0 | 1 |
| 「+ 側だけ」上位8との重なり | 1 | 1 | 3 | 0 | 0 | 0 |

## soy sauce − japanese + italian

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | sausage meat [bri] (0.56) | low sodium soy sauce [chi] (0.65) | low sodium soy sauce [chi] (0.63) | low sodium soy sauce [chi] (0.64) | low sodium soy sauce [chi] (0.66) | low sodium soy sauce [chi] (0.72) |
| 2 | italian style seasoning [ita] (0.55) | light soy sauce [chi] (0.63) | light soy sauce [chi] (0.63) | light soy sauce [chi] (0.61) | light soy sauce [chi] (0.62) | light soy sauce [chi] (0.66) |
| 3 | olive oil (0.55) | sausage meat [bri] (0.55) | mixed peel [iri] (0.56) | milk [bri] (0.57) | milk [bri] (0.60) | milk [bri] (0.62) |
| 4 | low sodium soy sauce [chi] (0.55) | fresh parsley [caj] (0.55) | black treacle [bri] (0.54) | sponge cake [bri] (0.54) | reduced sodium soy sauce [chi] (0.58) | coconut rum [jam] (0.60) |
| 5 | fresh parsley [caj] (0.54) | reduced sodium soy sauce [chi] (0.54) | olive oil (0.54) | reduced sodium soy sauce [chi] (0.53) | gold tequila [jam] (0.58) | reduced sodium soy sauce [chi] (0.60) |
| 6 | grated parmesan cheese [ita] (0.54) | italian style seasoning [ita] (0.54) | milk [bri] (0.53) | tart shells [iri] (0.53) | coconut rum [jam] (0.57) | campari [ita] (0.59) |
| 7 | pecorino cheese [ita] (0.54) | grated parmesan cheese [ita] (0.54) | fresh parsley [caj] (0.53) | mixed peel [iri] (0.53) | margarita mix [jam] (0.55) | rye whiskey [iri] (0.58) |
| 8 | parmesan cheese [ita] (0.53) | sesame oil [kor] (0.53) | sesame oil [kor] (0.52) | pecorino cheese [ita] (0.52) | rye whiskey [iri] (0.55) | burrata [ita] (0.58) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 0 | 1 | 0 | 0 | 0 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | sausage meat [bri] (0.56) | sausage meat [bri] (0.58) | low sodium soy sauce [chi] (0.58) | low sodium soy sauce [chi] (0.59) | low sodium soy sauce [chi] (0.60) | low sodium soy sauce [chi] (0.58) | low sodium soy sauce [chi] (0.50) |
| 2 | italian style seasoning [ita] (0.55) | fresh parsley [caj] (0.56) | sausage meat [bri] (0.56) | light soy sauce [chi] (0.55) | light soy sauce [chi] (0.54) | italian style seasoning [ita] (0.52) | canned black beans [mex] (0.49) |
| 3 | olive oil (0.55) | pecorino cheese [ita] (0.56) | fresh parsley [caj] (0.55) | sausage meat [bri] (0.54) | pecorino cheese [ita] (0.53) | dried parsley (0.52) | italian style seasoning [ita] (0.49) |
| 4 | low sodium soy sauce [chi] (0.55) | low sodium soy sauce [chi] (0.55) | pecorino cheese [ita] (0.54) | italian style seasoning [ita] (0.53) | italian style seasoning [ita] (0.52) | reduced sodium soy sauce [chi] (0.49) | dried parsley (0.48) |
| 5 | fresh parsley [caj] (0.54) | italian style seasoning [ita] (0.54) | light soy sauce [chi] (0.54) | fresh parsley [caj] (0.53) | fresh parsley [caj] (0.51) | dijon [fre] (0.47) | small red beans [caj] (0.47) |
| 6 | grated parmesan cheese [ita] (0.54) | olive oil (0.54) | italian style seasoning [ita] (0.53) | pecorino cheese [ita] (0.53) | reduced sodium soy sauce [chi] (0.51) | light soy sauce [chi] (0.47) | sliced black olives [mex] (0.46) |
| 7 | pecorino cheese [ita] (0.54) | grated parmesan cheese [ita] (0.54) | calf liver [iri] (0.53) | calf liver [iri] (0.52) | pitted green olives [mor] (0.51) | marjoram [rus] (0.46) | black beans [mex] (0.46) |
| 8 | parmesan cheese [ita] (0.53) | low-fat spaghetti sauce [ita] (0.54) | low-fat spaghetti sauce [ita] (0.52) | capers (0.52) | green olives [mor] (0.50) | worcestershire sauce [caj] (0.46) | dijon [fre] (0.46) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 2 | 0 | 0 | 0 | 0 | 0 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | sausage meat [bri] (0.56) | low sodium soy sauce [chi] (0.62) | low sodium soy sauce [chi] (0.63) | grated parmesan cheese [ita] (0.57) | low fat mozzarella (0.77) | sweet and sour sauce [jam] (0.98) |
| 2 | italian style seasoning [ita] (0.55) | sausage meat [bri] (0.59) | capers (0.56) | pecorino cheese [ita] (0.55) | dijon [fre] (0.66) | condensed milk [fil] (0.98) |
| 3 | olive oil (0.55) | dijon [fre] (0.57) | sausage meat [bri] (0.55) | solid white tuna [fre] (0.54) | light red kidney beans [caj] (0.63) | dried pasta [ita] (0.98) |
| 4 | low sodium soy sauce [chi] (0.55) | fresh parsley [caj] (0.55) | dried oregano [gre] (0.55) | low sodium soy sauce [chi] (0.54) | chardonnay [gre] (0.63) | bananas [jam] (0.97) |
| 5 | fresh parsley [caj] (0.54) | capers (0.54) | pecorino cheese [ita] (0.54) | fresh parsley [caj] (0.54) | soybean sprouts [kor] (0.62) | pickles [rus] (0.97) |
| 6 | grated parmesan cheese [ita] (0.54) | pecorino cheese [ita] (0.54) | ripe olives [mex] (0.52) | sliced black olives [mex] (0.54) | cider [iri] (0.60) | khoa [ind] (0.96) |
| 7 | pecorino cheese [ita] (0.54) | reduced sodium soy sauce [chi] (0.54) | fresh parsley [caj] (0.52) | capers (0.53) | octopuses [spa] (0.60) | almond meal [fil] (0.96) |
| 8 | parmesan cheese [ita] (0.53) | light soy sauce [chi] (0.53) | dijon [fre] (0.52) | burrata [ita] (0.53) | chili beans [mex] (0.59) | corn kernel whole [mex] (0.95) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 0 | 0 | 0 | 0 | 0 |

## soy sauce − chinese + mexican

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | black beans [mex] (0.65) | black beans [mex] (0.62) | black beans [mex] (0.60) | low sodium soy sauce [chi] (0.65) | low sodium soy sauce [chi] (0.66) | low sodium soy sauce [chi] (0.72) |
| 2 | medium salsa [mex] (0.59) | canned black beans [mex] (0.57) | low sodium soy sauce [chi] (0.59) | light soy sauce [chi] (0.59) | milk [bri] (0.61) | light soy sauce [chi] (0.66) |
| 3 | canned black beans [mex] (0.59) | mexican cheese [mex] (0.56) | milk [bri] (0.56) | black beans [mex] (0.57) | light soy sauce [chi] (0.60) | milk [bri] (0.62) |
| 4 | taco toppings [mex] (0.58) | medium salsa [mex] (0.55) | light soy sauce [chi] (0.56) | gold tequila [jam] (0.56) | reduced sodium soy sauce [chi] (0.58) | coconut rum [jam] (0.60) |
| 5 | tortillas [mex] (0.57) | low sodium soy sauce [chi] (0.55) | kewpie mayonnaise [jap] (0.56) | reduced sodium soy sauce [chi] (0.55) | gold tequila [jam] (0.55) | reduced sodium soy sauce [chi] (0.60) |
| 6 | mexican cheese [mex] (0.57) | sliced olives [mex] (0.54) | canned black beans [mex] (0.55) | milk [bri] (0.55) | brine-cured olives [gre] (0.55) | campari [ita] (0.60) |
| 7 | kraft mexican style finely shredded four cheese [mex] (0.57) | tortillas [mex] (0.54) | mexican cheese [mex] (0.54) | brine-cured olives [gre] (0.54) | butter pecan cake mix [sou] (0.53) | rye whiskey [iri] (0.59) |
| 8 | chop green chilies, undrain [mex] (0.57) | taco toppings [mex] (0.53) | medium salsa [mex] (0.54) | tamari soy sauce [jap] (0.53) | japanese soy sauce [jap] (0.53) | burrata [ita] (0.58) |
| − 側 cuisine の印が付いた数 | 0 | 1 | 2 | 3 | 3 | 3 |
| 「+ 側だけ」上位8との重なり | 2 | 0 | 0 | 0 | 0 | 0 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | black beans [mex] (0.65) | black beans [mex] (0.62) | black beans [mex] (0.60) | black beans [mex] (0.57) | sliced black olives [mex] (0.58) | dried parsley (0.55) | canned black beans [mex] (0.52) |
| 2 | medium salsa [mex] (0.59) | taco toppings [mex] (0.57) | mexican cheese [mex] (0.57) | mexican cheese [mex] (0.54) | black beans [mex] (0.54) | sliced black olives [mex] (0.53) | black beans [mex] (0.51) |
| 3 | canned black beans [mex] (0.59) | mexican cheese [mex] (0.57) | canned black beans [mex] (0.57) | canned black beans [mex] (0.54) | low sodium soy sauce [chi] (0.51) | italian style seasoning [ita] (0.51) | sliced black olives [mex] (0.51) |
| 4 | taco toppings [mex] (0.58) | canned black beans [mex] (0.57) | taco toppings [mex] (0.54) | sliced olives [mex] (0.53) | dried parsley (0.50) | dijon [fre] (0.49) | italian style seasoning [ita] (0.50) |
| 5 | tortillas [mex] (0.57) | medium salsa [mex] (0.56) | tortillas [mex] (0.54) | tortillas [mex] (0.51) | mexican cheese [mex] (0.50) | low sodium soy sauce [chi] (0.49) | dried parsley (0.49) |
| 6 | mexican cheese [mex] (0.57) | tortillas [mex] (0.56) | medium salsa [mex] (0.54) | low sodium soy sauce [chi] (0.51) | dried oregano [gre] (0.50) | small red beans [caj] (0.49) | small red beans [caj] (0.46) |
| 7 | kraft mexican style finely shredded four cheese [mex] (0.57) | sliced olives [mex] (0.56) | light red kidney beans [caj] (0.54) | medium salsa [mex] (0.50) | canned black beans [mex] (0.50) | canned black beans [mex] (0.48) | dijon [fre] (0.46) |
| 8 | chop green chilies, undrain [mex] (0.57) | chop green chilies, undrain [mex] (0.55) | sliced olives [mex] (0.53) | taco toppings [mex] (0.50) | small red beans [caj] (0.50) | dried oregano [gre] (0.48) | couscous [mor] (0.44) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 1 | 1 | 1 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 1 | 0 | 0 | 0 | 0 | 0 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | black beans [mex] (0.65) | low sodium soy sauce [chi] (0.60) | capers (0.58) | sliced black olives [mex] (0.60) | low fat mozzarella (0.77) | sweet and sour sauce [jam] (0.98) |
| 2 | medium salsa [mex] (0.59) | dijon [fre] (0.58) | low sodium soy sauce [chi] (0.58) | solid white tuna [fre] (0.60) | dijon [fre] (0.63) | condensed milk [fil] (0.97) |
| 3 | canned black beans [mex] (0.59) | reduced sodium soy sauce [chi] (0.56) | ripe olives [mex] (0.57) | grated parmesan cheese [ita] (0.57) | chardonnay [gre] (0.63) | khoa [ind] (0.97) |
| 4 | taco toppings [mex] (0.58) | ripe olives [mex] (0.55) | dri leav rosemari [iri] (0.56) | fresh parsley [caj] (0.55) | light red kidney beans [caj] (0.63) | lump crab meat [caj] (0.97) |
| 5 | tortillas [mex] (0.57) | small red beans [caj] (0.55) | sausage meat [bri] (0.55) | capers (0.55) | cider [iri] (0.62) | crushed pineapples in juice [sou] (0.97) |
| 6 | mexican cheese [mex] (0.57) | sliced black olives [mex] (0.55) | dijon [fre] (0.55) | herbes de provence [fre] (0.53) | chili beans [mex] (0.61) | meatloaf [ita] (0.96) |
| 7 | kraft mexican style finely shredded four cheese [mex] (0.57) | black beans [mex] (0.54) | sliced black olives [mex] (0.54) | light red kidney beans [caj] (0.52) | soybean sprouts [kor] (0.61) | dried pasta [ita] (0.96) |
| 8 | chop green chilies, undrain [mex] (0.57) | light soy sauce [chi] (0.53) | parmesan cheese [ita] (0.52) | shredded parmesan cheese [ita] (0.52) | white kidney beans [rus] (0.60) | italian style seasoning [ita] (0.96) |
| − 側 cuisine の印が付いた数 | 0 | 3 | 1 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 0 | 1 | 0 | 0 | 0 |

## miso − japanese + italian

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | balsamic reduction [bri] (0.56) | wakame [jap] (0.58) | wakame [jap] (0.58) | wakame [jap] (0.56) | wakame [jap] (0.57) | chocolate syrup [iri] (0.57) |
| 2 | bocconcini [ita] (0.55) | shredded nori [kor] (0.52) | apple jelly [fre] (0.51) | balsamic reduction [bri] (0.53) | white miso [jap] (0.54) | granola [bra] (0.57) |
| 3 | caper berries [ita] (0.55) | fresh mozzarella balls [ita] (0.52) | shredded nori [kor] (0.51) | mackerel [bra] (0.51) | balsamic reduction [bri] (0.53) | forest fruit [bra] (0.56) |
| 4 | fresh mozzarella balls [ita] (0.55) | bocconcini [ita] (0.52) | balsamic reduction [bri] (0.50) | apple jelly [fre] (0.49) | dried bonito flakes [jap] (0.53) | açai powder [bra] (0.56) |
| 5 | grated parmesan cheese [ita] (0.54) | balsamic reduction [bri] (0.51) | roasted white sesame seeds [jap] (0.50) | frozen banana [bra] (0.49) | apple jelly [fre] (0.53) | chambord [fre] (0.55) |
| 6 | perciatelli [ita] (0.54) | soba noodles [jap] (0.51) | white miso [jap] (0.50) | roasted white sesame seeds [jap] (0.49) | mirin [jap] (0.52) | sushi grade tuna [jap] (0.54) |
| 7 | 2% low-fat cottage cheese [gre] (0.54) | buckwheat soba noodles [jap] (0.51) | soba noodles [jap] (0.50) | chocolate syrup [iri] (0.49) | buckwheat soba noodles [jap] (0.52) | soft-wheat flour [sou] (0.54) |
| 8 | frozen pizza dough [gre] (0.54) | caper berries [ita] (0.50) | buckwheat soba noodles [jap] (0.49) | shredded nori [kor] (0.48) | chocolate syrup [iri] (0.52) | crème de cassis [fre] (0.54) |
| − 側 cuisine の印が付いた数 | 0 | 3 | 5 | 2 | 5 | 1 |
| 「+ 側だけ」上位8との重なり | 1 | 0 | 0 | 0 | 0 | 0 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | balsamic reduction [bri] (0.56) | balsamic reduction [bri] (0.56) | fresh mozzarella balls [ita] (0.56) | fresh mozzarella balls [ita] (0.56) | fresh mozzarella balls [ita] (0.55) | wild mushrooms [ita] (0.49) | pickling salt [bri] (0.47) |
| 2 | bocconcini [ita] (0.55) | caper berries [ita] (0.55) | bocconcini [ita] (0.54) | wakame [jap] (0.53) | caper berries [ita] (0.53) | whole wheat pita [gre] (0.47) | whole wheat pita [gre] (0.46) |
| 3 | caper berries [ita] (0.55) | bocconcini [ita] (0.55) | crumbled ricotta salata cheese [ita] (0.54) | caper berries [ita] (0.52) | oven-ready lasagna noodles [ita] (0.52) | frozen pizza dough [gre] (0.46) | garlic bulb [iri] (0.46) |
| 4 | fresh mozzarella balls [ita] (0.55) | fresh mozzarella balls [ita] (0.54) | cooked rigatoni [ita] (0.53) | bocconcini [ita] (0.51) | wakame [jap] (0.52) | yukon gold [bri] (0.45) | wild mushrooms [ita] (0.44) |
| 5 | grated parmesan cheese [ita] (0.54) | grated parmesan cheese [ita] (0.54) | 2% low-fat cottage cheese [gre] (0.53) | balsamic reduction [bri] (0.51) | crumbled ricotta salata cheese [ita] (0.51) | caper berries [ita] (0.45) | golden zucchini [kor] (0.44) |
| 6 | perciatelli [ita] (0.54) | perciatelli [ita] (0.53) | balsamic reduction [bri] (0.53) | pesto [ita] (0.51) | 2% low-fat cottage cheese [gre] (0.51) | fresh mozzarella balls [ita] (0.45) | fat-free refried beans [mex] (0.43) |
| 7 | 2% low-fat cottage cheese [gre] (0.54) | frozen pizza dough [gre] (0.53) | caper berries [ita] (0.53) | shredded nori [kor] (0.51) | shredded nori [kor] (0.51) | white miso [jap] (0.45) | yellow tomato [spa] (0.43) |
| 8 | frozen pizza dough [gre] (0.54) | 2% low-fat cottage cheese [gre] (0.53) | oven-ready lasagna noodles [ita] (0.52) | 2% low-fat cottage cheese [gre] (0.51) | pesto [ita] (0.51) | 2% low-fat cottage cheese [gre] (0.44) | caper berries [ita] (0.43) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 1 | 1 | 1 | 0 |
| 「+ 側だけ」上位8との重なり | 1 | 1 | 0 | 0 | 0 | 0 | 0 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | balsamic reduction [bri] (0.56) | yukon gold [bri] (0.56) | focaccia [ita] (0.55) | belgian endive [fre] (0.54) | juice (0.75) | brisket [iri] (1.00) |
| 2 | bocconcini [ita] (0.55) | whole wheat pita [gre] (0.52) | golden beets [kor] (0.53) | pear tomatoes [ita] (0.54) | pappardelle [ita] (0.64) | gala apples [fre] (0.99) |
| 3 | caper berries [ita] (0.55) | crumbled ricotta salata cheese [ita] (0.50) | soba noodles [jap] (0.52) | thick-cut bacon [iri] (0.53) | brisket [iri] (0.63) | spanish chorizo [spa] (0.99) |
| 4 | fresh mozzarella balls [ita] (0.55) | balsamic reduction [bri] (0.50) | sourdough [bri] (0.52) | romaine lettuce [gre] (0.49) | thick-cut bacon [iri] (0.60) | sausages [caj] (0.98) |
| 5 | grated parmesan cheese [ita] (0.54) | whole grain dijon mustard [bri] (0.50) | white miso [jap] (0.51) | olive oil cooking spray [gre] (0.48) | ground black pepper (0.60) | ham [rus] (0.97) |
| 6 | perciatelli [ita] (0.54) | caper berries [ita] (0.50) | balsamic reduction [bri] (0.49) | banana peppers [fil] (0.48) | whole grain mustard [fre] (0.59) | lime [bra] (0.96) |
| 7 | 2% low-fat cottage cheese [gre] (0.54) | wild mushrooms [ita] (0.49) | banana peppers [fil] (0.49) | greek-style vinaigrette [gre] (0.48) | golden zucchini [kor] (0.59) | thick-cut bacon [iri] (0.96) |
| 8 | frozen pizza dough [gre] (0.54) | hard salami [caj] (0.48) | fresh mozzarella balls [ita] (0.47) | sourdough [bri] (0.47) | condiments [jam] (0.59) | greens [chi] (0.96) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 2 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 1 | 0 | 0 | 0 | 0 | 0 |

## sake − japanese + french

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | grappa [ita] (0.53) | mirin [jap] (0.63) | mirin [jap] (0.61) | mirin [jap] (0.60) | mirin [jap] (0.61) | grappa [ita] (0.65) |
| 2 | kirsch [fre] (0.53) | konbu [jap] (0.57) | konbu [jap] (0.55) | konbu [jap] (0.53) | konbu [jap] (0.54) | campari [ita] (0.61) |
| 3 | chopped fresh thyme [fre] (0.52) | dashi [jap] (0.54) | dashi [jap] (0.50) | dried bonito flakes [jap] (0.51) | dried bonito flakes [jap] (0.53) | shaoxing [chi] (0.58) |
| 4 | riesling [fre] (0.51) | dried bonito flakes [jap] (0.53) | dried bonito flakes [jap] (0.50) | dashi [jap] (0.50) | dashi [jap] (0.52) | vin santo [ita] (0.57) |
| 5 | pinot noir [fre] (0.51) | dashi powder [jap] (0.51) | yellow miso [jap] (0.48) | butter pecan cake mix [sou] (0.47) | fish sauce [vie] (0.51) | lemon curd [iri] (0.57) |
| 6 | dry white wine [spa] (0.50) | wakame [jap] (0.49) | wakame [jap] (0.48) | grappa [ita] (0.46) | butter pecan cake mix [sou] (0.51) | rose essence [ind] (0.56) |
| 7 | truffle oil [ita] (0.50) | yellow miso [jap] (0.49) | japanese soy sauce [jap] (0.47) | dashi kombu [jap] (0.46) | enchilada sauce [mex] (0.50) | mirin [jap] (0.56) |
| 8 | nonfat dry milk [fre] (0.50) | dashi kombu [jap] (0.49) | dashi powder [jap] (0.47) | riesling [fre] (0.46) | chunky pasta sauce [ita] (0.49) | lemon extract [rus] (0.56) |
| − 側 cuisine の印が付いた数 | 0 | 8 | 8 | 5 | 4 | 1 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 0 | 0 | 1 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | grappa [ita] (0.53) | grappa [ita] (0.52) | mirin [jap] (0.52) | mirin [jap] (0.55) | mirin [jap] (0.52) | grappa [ita] (0.57) | grappa [ita] (0.55) |
| 2 | kirsch [fre] (0.53) | chopped fresh thyme [fre] (0.52) | chopped fresh thyme [fre] (0.49) | dried bonito flakes [jap] (0.49) | chopped fresh thyme [fre] (0.51) | riesling [fre] (0.54) | riesling [fre] (0.54) |
| 3 | chopped fresh thyme [fre] (0.52) | kirsch [fre] (0.51) | grappa [ita] (0.49) | chopped fresh thyme [fre] (0.48) | riesling [fre] (0.49) | shaoxing [chi] (0.53) | cream style corn [sou] (0.53) |
| 4 | riesling [fre] (0.51) | riesling [fre] (0.51) | riesling [fre] (0.49) | konbu [jap] (0.48) | grappa [ita] (0.48) | truffle oil [ita] (0.52) | truffle oil [ita] (0.49) |
| 5 | pinot noir [fre] (0.51) | nonfat dry milk [fre] (0.50) | truffle oil [ita] (0.48) | riesling [fre] (0.48) | thyme sprigs [fre] (0.47) | calimyrna figs [bri] (0.52) | shaoxing [chi] (0.49) |
| 6 | dry white wine [spa] (0.50) | pinot noir [fre] (0.50) | kirsch [fre] (0.48) | grappa [ita] (0.48) | reduced fat milk [fre] (0.47) | reduced fat milk [fre] (0.51) | green chile [mex] (0.49) |
| 7 | truffle oil [ita] (0.50) | truffle oil [ita] (0.50) | nonfat dry milk [fre] (0.48) | dashi [jap] (0.47) | calimyrna figs [bri] (0.47) | thyme sprigs [fre] (0.50) | dry red wine [spa] (0.48) |
| 8 | nonfat dry milk [fre] (0.50) | reduced fat milk [fre] (0.49) | reduced fat milk [fre] (0.48) | thyme sprigs [fre] (0.47) | dried bonito flakes [jap] (0.46) | dry red wine [spa] (0.49) | veal cutlets [ita] (0.47) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 1 | 4 | 2 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 1 | 1 | 0 | 0 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | grappa [ita] (0.53) | grappa [ita] (0.61) | grappa [ita] (0.61) | mild italian sausage [ita] (0.66) | all-purpose flour (0.69) | currant [bri] (0.99) |
| 2 | kirsch [fre] (0.53) | riesling [fre] (0.54) | riesling [fre] (0.60) | riesling [fre] (0.65) | nonfat dry milk [fre] (0.67) | walnut pieces [iri] (0.97) |
| 3 | chopped fresh thyme [fre] (0.52) | dry red wine [spa] (0.53) | reduced fat milk [fre] (0.58) | chopped almonds [gre] (0.65) | dried apricot [mor] (0.66) | pimentos [spa] (0.97) |
| 4 | riesling [fre] (0.51) | reduced fat milk [fre] (0.52) | truffle oil [ita] (0.57) | nonfat dry milk [fre] (0.64) | espresso powder [sou] (0.66) | pitted green olives [mor] (0.97) |
| 5 | pinot noir [fre] (0.51) | kirsch [fre] (0.52) | whole okra [caj] (0.57) | grappa [ita] (0.63) | clotted cream [bri] (0.65) | puff pastry [bri] (0.97) |
| 6 | dry white wine [spa] (0.50) | truffle oil [ita] (0.51) | heavy whipping cream (0.56) | rose essence [ind] (0.62) | vanilla beans [fre] (0.65) | preserves [fil] (0.96) |
| 7 | truffle oil [ita] (0.50) | chopped fresh thyme [fre] (0.51) | 2% low-fat cottage cheese [gre] (0.55) | clotted cream [bri] (0.58) | baking spray [rus] (0.64) | bows [bra] (0.96) |
| 8 | nonfat dry milk [fre] (0.50) | sauvignon blanc [fre] (0.50) | gyoza skins [kor] (0.55) | vanilla beans [fre] (0.58) | tequila [mex] (0.64) | cornflake cereal [sou] (0.96) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 1 | 2 | 0 | 0 | 0 |

## butter − french + indian

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | ghee [ind] (0.62) | ghee [ind] (0.62) | margarine [iri] (0.63) | unsalted butter [bri] (0.65) | olive oil (0.74) | unsalted butter [bri] (0.77) |
| 2 | margarine [iri] (0.57) | margarine [iri] (0.58) | olive oil (0.62) | olive oil (0.64) | unsalted butter [bri] (0.71) | olive oil (0.76) |
| 3 | salt (0.53) | oil [fil] (0.55) | unsalted butter [bri] (0.59) | margarine [iri] (0.61) | margarine [iri] (0.62) | salt (0.67) |
| 4 | meat tenderizer [ind] (0.53) | salt (0.53) | salt (0.57) | sesame oil [kor] (0.56) | sesame oil [kor] (0.59) | margarine [iri] (0.63) |
| 5 | black cumin seeds [ind] (0.52) | meat tenderizer [ind] (0.52) | sesame oil [kor] (0.56) | salt (0.55) | salt (0.57) | water (0.63) |
| 6 | oil [fil] (0.52) | ravva [ind] (0.51) | melted butter [sou] (0.53) | chicken breast strips [caj] (0.54) | milk chocolate chips [bra] (0.54) | sesame oil [kor] (0.62) |
| 7 | black gram [ind] (0.51) | black cumin seeds [ind] (0.51) | milk [bri] (0.53) | oscar mayer bacon [mex] (0.54) | dried udon [jap] (0.54) | diced tomatoes and green chilies [caj] (0.62) |
| 8 | rose essence [ind] (0.51) | coriander powder [ind] (0.51) | oil [fil] (0.53) | melted butter [sou] (0.54) | togarashi [jap] (0.54) | milk chocolate chips [bra] (0.60) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 2 | 3 | 1 | 2 | 1 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | ghee [ind] (0.62) | ghee [ind] (0.62) | ghee [ind] (0.62) | ghee [ind] (0.61) | margarine [iri] (0.63) | margarine [iri] (0.64) | margarine [iri] (0.66) |
| 2 | margarine [iri] (0.57) | margarine [iri] (0.56) | margarine [iri] (0.58) | margarine [iri] (0.58) | salt (0.58) | oil [fil] (0.59) | diced tomatoes and green chilies [caj] (0.61) |
| 3 | salt (0.53) | salt (0.54) | salt (0.55) | salt (0.56) | unsalted butter [bri] (0.57) | salt (0.58) | oil [fil] (0.60) |
| 4 | meat tenderizer [ind] (0.53) | meat tenderizer [ind] (0.52) | meat tenderizer [ind] (0.52) | oil [fil] (0.55) | ghee [ind] (0.56) | ragu [ita] (0.57) | ragu [ita] (0.59) |
| 5 | black cumin seeds [ind] (0.52) | black cumin seeds [ind] (0.52) | oil [fil] (0.52) | ravva [ind] (0.52) | oil [fil] (0.55) | unsalted butter [bri] (0.56) | crisco [sou] (0.57) |
| 6 | oil [fil] (0.52) | black gram [ind] (0.51) | soft taco size flour tortillas [mex] (0.51) | meat tenderizer [ind] (0.52) | condensed cream of potato soup [sou] (0.52) | milk [bri] (0.56) | spicy pork sausage [bra] (0.56) |
| 7 | black gram [ind] (0.51) | oil [fil] (0.51) | ground cumin [mor] (0.51) | black gram [ind] (0.51) | melted butter [sou] (0.52) | single crust pie [bri] (0.55) | salt (0.55) |
| 8 | rose essence [ind] (0.51) | rose essence [ind] (0.51) | cream [ind] (0.51) | rose essence [ind] (0.51) | potatoes [iri] (0.52) | water (0.53) | beef sausage [caj] (0.55) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 2 | 2 | 2 | 1 | 2 | 2 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | ghee [ind] (0.62) | margarine [iri] (0.60) | margarine [iri] (0.65) | salt (0.68) | tom yum paste [tha] (0.71) | riesling [fre] (0.96) |
| 2 | margarine [iri] (0.57) | salt (0.57) | ragu [ita] (0.65) | reduced fat cream cheese [mex] (0.66) | manicotti shells [ita] (0.70) | port [fre] (0.96) |
| 3 | salt (0.53) | ghee [ind] (0.56) | salt (0.61) | 2% low-fat cottage cheese [gre] (0.65) | egg noodles, cooked and drained [rus] (0.69) | pot roast [mor] (0.95) |
| 4 | meat tenderizer [ind] (0.53) | ragu [ita] (0.53) | beef kidney [bri] (0.58) | egg noodles, cooked and drained [rus] (0.65) | pasta sauce [ita] (0.68) | crisps [chi] (0.94) |
| 5 | black cumin seeds [ind] (0.52) | porridge oats [bri] (0.53) | single crust pie [bri] (0.57) | milk [bri] (0.64) | whole wheat penne [ita] (0.65) | cooked rigatoni [ita] (0.94) |
| 6 | oil [fil] (0.52) | oil [fil] (0.53) | oil [fil] (0.57) | manicotti [ita] (0.64) | reduced fat cream cheese [mex] (0.65) | frozen vegetables [vie] (0.92) |
| 7 | black gram [ind] (0.51) | potatoes [iri] (0.52) | small curd cottage cheese [ita] (0.56) | tom yum paste [tha] (0.64) | fava beans [mor] (0.64) | garlic pepper seasoning [caj] (0.92) |
| 8 | rose essence [ind] (0.51) | cheese soup [mex] (0.52) | yellow bean sauce [vie] (0.56) | ragu [ita] (0.63) | cut up cooked chicken [sou] (0.64) | cardamom [ind] (0.92) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 2 |
| 「+ 側だけ」上位8との重なり | 2 | 1 | 1 | 3 | 0 | 0 |

## flour tortillas − mexican + indian

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | basmati rice [ind] (0.60) | basmati rice [ind] (0.60) | corn tortillas [mex] (0.57) | corn tortillas [mex] (0.62) | corn tortillas [mex] (0.63) | corn tortillas [mex] (0.65) |
| 2 | corn tortillas [mex] (0.56) | corn tortillas [mex] (0.57) | basmati rice [ind] (0.55) | fajita size flour tortillas [mex] (0.59) | fajita size flour tortillas [mex] (0.58) | fajita size flour tortillas [mex] (0.60) |
| 3 | garam masala [ind] (0.56) | garam masala [ind] (0.55) | thin pizza crust [jam] (0.55) | basmati rice [ind] (0.56) | basmati rice [ind] (0.57) | sponge cake [bri] (0.59) |
| 4 | yoghurt [ind] (0.51) | large flour tortillas [mex] (0.51) | pizza crust [ita] (0.54) | pizza crust [ita] (0.55) | pizza crust [ita] (0.56) | pizza crust [ita] (0.59) |
| 5 | whole wheat tortillas [mex] (0.51) | yoghurt [ind] (0.51) | fajita size flour tortillas [mex] (0.54) | whole wheat tortillas [mex] (0.55) | whole wheat tortillas [mex] (0.55) | udon [jap] (0.58) |
| 6 | fajita size flour tortillas [mex] (0.50) | whole wheat tortillas [mex] (0.51) | whole wheat tortillas [mex] (0.53) | thin pizza crust [jam] (0.54) | tortilla chips [mex] (0.55) | whole wheat tortillas [mex] (0.58) |
| 7 | tortillas [mex] (0.50) | fajita size flour tortillas [mex] (0.50) | refrigerated pizza dough [ita] (0.52) | tortilla chips [mex] (0.54) | penne [ita] (0.54) | basmati rice [ind] (0.58) |
| 8 | large flour tortillas [mex] (0.49) | tortillas [mex] (0.50) | penne [ita] (0.52) | penne [ita] (0.54) | sponge cake [bri] (0.54) | penne [ita] (0.58) |
| − 側 cuisine の印が付いた数 | 5 | 5 | 3 | 4 | 4 | 3 |
| 「+ 側だけ」上位8との重なり | 1 | 0 | 0 | 0 | 0 | 0 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | basmati rice [ind] (0.60) | basmati rice [ind] (0.60) | basmati rice [ind] (0.59) | basmati rice [ind] (0.59) | basmati rice [ind] (0.58) | corn tortillas [mex] (0.59) | corn tortillas [mex] (0.63) |
| 2 | corn tortillas [mex] (0.56) | garam masala [ind] (0.55) | corn tortillas [mex] (0.57) | corn tortillas [mex] (0.56) | corn tortillas [mex] (0.56) | tortillas [mex] (0.51) | pizza crust [ita] (0.58) |
| 3 | garam masala [ind] (0.56) | corn tortillas [mex] (0.55) | garam masala [ind] (0.54) | garam masala [ind] (0.53) | fajita size flour tortillas [mex] (0.52) | egg noodles [chi] (0.50) | egg noodles [chi] (0.57) |
| 4 | yoghurt [ind] (0.51) | yoghurt [ind] (0.52) | whole wheat tortillas [mex] (0.52) | whole wheat tortillas [mex] (0.51) | garam masala [ind] (0.52) | crescent rolls [mex] (0.50) | fajita size flour tortillas [mex] (0.55) |
| 5 | whole wheat tortillas [mex] (0.51) | whole wheat tortillas [mex] (0.50) | tortillas [mex] (0.51) | fajita size flour tortillas [mex] (0.50) | pasta [ita] (0.49) | basmati rice [ind] (0.50) | pasta [ita] (0.55) |
| 6 | fajita size flour tortillas [mex] (0.50) | cheese cubes [ind] (0.49) | fajita size flour tortillas [mex] (0.51) | large flour tortillas [mex] (0.50) | crescent rolls [mex] (0.49) | fajita size flour tortillas [mex] (0.49) | large flour tortillas [mex] (0.55) |
| 7 | tortillas [mex] (0.50) | green cardamom [ind] (0.49) | tortilla chips [mex] (0.50) | cheese cubes [ind] (0.49) | tortillas [mex] (0.48) | whole wheat tortillas [mex] (0.48) | rigatoni [ita] (0.54) |
| 8 | large flour tortillas [mex] (0.49) | tortillas [mex] (0.49) | yoghurt [ind] (0.50) | yoghurt [ind] (0.49) | whole wheat tortillas [mex] (0.48) | old el paso flour tortillas [mex] (0.48) | crescent rolls [mex] (0.54) |
| − 側 cuisine の印が付いた数 | 5 | 3 | 5 | 4 | 5 | 6 | 4 |
| 「+ 側だけ」上位8との重なり | 1 | 1 | 0 | 0 | 0 | 0 | 0 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | basmati rice [ind] (0.60) | basmati rice [ind] (0.59) | basmati rice [ind] (0.62) | biryani masala [ind] (0.62) | fajita size flour tortillas [mex] (0.74) | fresh lemon juice [gre] (0.99) |
| 2 | corn tortillas [mex] (0.56) | corn tortillas [mex] (0.54) | uncooked rigatoni [ita] (0.54) | fettuccine pasta [ita] (0.60) | crescent rolls [mex] (0.70) | veal [rus] (0.98) |
| 3 | garam masala [ind] (0.56) | whole wheat tortillas [mex] (0.53) | pasta [ita] (0.53) | basmati rice [ind] (0.60) | chunky pasta sauce [ita] (0.70) | lemon juice [gre] (0.98) |
| 4 | yoghurt [ind] (0.51) | garam masala [ind] (0.52) | corn tortillas [mex] (0.51) | pizza crust [ita] (0.60) | hash brown [sou] (0.70) | nutmeg [jam] (0.97) |
| 5 | whole wheat tortillas [mex] (0.51) | pizza crust [ita] (0.50) | whole wheat tortillas [mex] (0.51) | lo mein noodles [chi] (0.58) | pizza crust [ita] (0.69) | konbu [jap] (0.97) |
| 6 | fajita size flour tortillas [mex] (0.50) | uncooked rigatoni [ita] (0.48) | fettuccine pasta [ita] (0.49) | pasta [ita] (0.56) | egg noodles [chi] (0.67) | beef sirloin [vie] (0.97) |
| 7 | tortillas [mex] (0.50) | pasta [ita] (0.47) | garam masala [ind] (0.49) | penne pasta [ita] (0.55) | old el paso flour tortillas [mex] (0.66) | jack daniels [sou] (0.97) |
| 8 | large flour tortillas [mex] (0.49) | rotini [ita] (0.46) | penne pasta [ita] (0.49) | uncooked rigatoni [ita] (0.54) | linguini [ita] (0.64) | tarragon leaves [fre] (0.96) |
| − 側 cuisine の印が付いた数 | 5 | 2 | 2 | 0 | 3 | 0 |
| 「+ 側だけ」上位8との重なり | 1 | 0 | 0 | 0 | 0 | 0 |

## fish sauce − thai + italian

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | prosciutto [ita] (0.57) | thai basil [vie] (0.60) | thai basil [vie] (0.62) | thai basil [vie] (0.63) | mirin [jap] (0.62) | ghee [ind] (0.62) |
| 2 | dried basil [ita] (0.56) | prosciutto [ita] (0.54) | lemongrass [tha] (0.58) | lemongrass [tha] (0.58) | ghee [ind] (0.58) | mirin [jap] (0.61) |
| 3 | fresh parsley [caj] (0.54) | vietnamese fish sauce [vie] (0.54) | vietnamese fish sauce [vie] (0.56) | vietnamese fish sauce [vie] (0.56) | thai basil [vie] (0.57) | thai fish sauce [tha] (0.59) |
| 4 | fresh oregano [gre] (0.54) | asian fish sauce [vie] (0.53) | kaffir lime leaves [tha] (0.55) | thai fish sauce [tha] (0.55) | old el pasotm taco seasoning mix [mex] (0.57) | rose essence [ind] (0.59) |
| 5 | pancetta [ita] (0.54) | lemongrass [tha] (0.53) | asian fish sauce [vie] (0.54) | asian fish sauce [vie] (0.55) | bisquick baking mix [mex] (0.56) | garam masala [ind] (0.58) |
| 6 | mild italian sausage [ita] (0.53) | rice vermicelli [vie] (0.53) | thai fish sauce [tha] (0.53) | kaffir lime leaves [tha] (0.54) | old el pasotm thick 'n chunky salsa [mex] (0.54) | green olives [mor] (0.58) |
| 7 | pesto [ita] (0.53) | dried basil [ita] (0.52) | rice vermicelli [vie] (0.52) | bisquick baking mix [mex] (0.53) | garam masala [ind] (0.53) | espresso beans [iri] (0.57) |
| 8 | prepar pesto [ita] (0.53) | thai fish sauce [tha] (0.52) | prosciutto [ita] (0.50) | dried basil [ita] (0.53) | vietnamese fish sauce [vie] (0.53) | tart shells [iri] (0.57) |
| − 側 cuisine の印が付いた数 | 0 | 2 | 3 | 3 | 0 | 1 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 0 | 0 | 1 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | prosciutto [ita] (0.57) | fresh oregano [gre] (0.55) | fresh parsley [caj] (0.54) | fresh parsley [caj] (0.53) | fresh oregano [gre] (0.53) | fresh parsley [caj] (0.49) | fresh oregano [gre] (0.45) |
| 2 | dried basil [ita] (0.56) | prosciutto [ita] (0.55) | fresh oregano [gre] (0.53) | pesto [ita] (0.52) | pesto [ita] (0.52) | pancetta [ita] (0.49) | ghee [ind] (0.44) |
| 3 | fresh parsley [caj] (0.54) | fresh parsley [caj] (0.55) | pancetta [ita] (0.52) | pancetta [ita] (0.52) | pancetta [ita] (0.52) | fresh oregano [gre] (0.48) | mild italian sausage [ita] (0.44) |
| 4 | fresh oregano [gre] (0.54) | dried basil [ita] (0.54) | prosciutto [ita] (0.52) | fresh oregano [gre] (0.52) | flat leaf parsley [spa] (0.52) | prosciutto [ita] (0.48) | hot italian sausages [ita] (0.44) |
| 5 | pancetta [ita] (0.54) | bread, cut into italian loaf [ita] (0.54) | dried basil [ita] (0.52) | flat leaf parsley [spa] (0.51) | fresh parsley [caj] (0.52) | green olives [mor] (0.48) | fresh parsley [caj] (0.44) |
| 6 | mild italian sausage [ita] (0.53) | flat leaf parsley [spa] (0.53) | flat leaf parsley [spa] (0.52) | prosciutto [ita] (0.51) | prosciutto [ita] (0.51) | flat leaf parsley [spa] (0.47) | seasoning salt [sou] (0.43) |
| 7 | pesto [ita] (0.53) | pancetta [ita] (0.52) | bread, cut into italian loaf [ita] (0.51) | dried basil [ita] (0.51) | mirin [jap] (0.50) | parsley sprigs [fre] (0.47) | green olives [mor] (0.42) |
| 8 | prepar pesto [ita] (0.53) | pesto [ita] (0.50) | pesto [ita] (0.51) | kalamata [gre] (0.48) | hot italian sausages [ita] (0.49) | poblano [mex] (0.46) | turkey bacon [sou] (0.41) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | prosciutto [ita] (0.57) | fresh oregano [gre] (0.58) | pancetta [ita] (0.53) | green olives [mor] (0.60) | ghee [ind] (0.68) | country ham [sou] (0.97) |
| 2 | dried basil [ita] (0.56) | fresh parsley [caj] (0.57) | fresh parsley [caj] (0.53) | bisquick baking mix [mex] (0.58) | bacon grease [sou] (0.66) | gyoza skins [kor] (0.95) |
| 3 | fresh parsley [caj] (0.54) | green olives [mor] (0.54) | green olives [mor] (0.52) | ghee [ind] (0.57) | green olives [mor] (0.64) | lumpia wrappers [fil] (0.95) |
| 4 | fresh oregano [gre] (0.54) | mild italian sausage [ita] (0.54) | seasoning salt [sou] (0.51) | bacon grease [sou] (0.57) | cornmeal [sou] (0.61) | chile paste with garlic [tha] (0.95) |
| 5 | pancetta [ita] (0.54) | pitted kalamata olives [gre] (0.54) | bisquick baking mix [mex] (0.51) | crisco [sou] (0.57) | garam masala [ind] (0.60) | biscuits [sou] (0.94) |
| 6 | mild italian sausage [ita] (0.53) | flat leaf parsley [spa] (0.53) | ghee [ind] (0.51) | mild italian sausage [ita] (0.55) | curry leaves [ind] (0.59) | taco seasoning [mex] (0.94) |
| 7 | pesto [ita] (0.53) | cooked rigatoni [ita] (0.53) | margarine [iri] (0.51) | margarine [iri] (0.53) | crisco [sou] (0.58) | stir fry vegetable blend [chi] (0.94) |
| 8 | prepar pesto [ita] (0.53) | kalamata [gre] (0.52) | cheese soup [mex] (0.50) | turkey bacon [sou] (0.51) | carnitas [mex] (0.57) | no-salt-added diced tomatoes [caj] (0.93) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 1 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 0 | 0 | 0 |

## parmesan cheese − italian + japanese

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | dried udon [jap] (0.61) | grated parmesan cheese [ita] (0.75) | grated parmesan cheese [ita] (0.77) | grated parmesan cheese [ita] (0.77) | grated parmesan cheese [ita] (0.79) | grated parmesan cheese [ita] (0.77) |
| 2 | roasted white sesame seeds [jap] (0.59) | shredded parmesan cheese [ita] (0.58) | shredded parmesan cheese [ita] (0.59) | shredded parmesan cheese [ita] (0.59) | shaved parmesan cheese [ita] (0.58) | coconut rum [jam] (0.58) |
| 3 | shredded nori [kor] (0.58) | parmagiano reggiano [ita] (0.57) | parmagiano reggiano [ita] (0.57) | parmagiano reggiano [ita] (0.57) | shredded parmesan cheese [ita] (0.57) | shredded parmesan cheese [ita] (0.58) |
| 4 | soy sauce [kor] (0.57) | parmigiano reggiano cheese [ita] (0.56) | parmigiano reggiano cheese [ita] (0.55) | parmigiano reggiano cheese [ita] (0.56) | parmagiano reggiano [ita] (0.57) | shaved parmesan cheese [ita] (0.57) |
| 5 | chili paste [kor] (0.56) | dried udon [jap] (0.55) | freshly grated parmesan [ita] (0.53) | oreo cookies [iri] (0.55) | parmigiano reggiano cheese [ita] (0.56) | parmigiano reggiano cheese [ita] (0.56) |
| 6 | mung bean noodles [vie] (0.54) | frozen cheese ravioli [ita] (0.55) | shaved parmesan cheese [ita] (0.53) | shaved parmesan cheese [ita] (0.55) | oreo cookies [iri] (0.54) | baby leaf lettuce [spa] (0.56) |
| 7 | sesame oil [kor] (0.53) | freshly grated parmesan [ita] (0.55) | ginger [chi] (0.53) | freshly grated parmesan [ita] (0.53) | tandoori seasoning [ind] (0.54) | caster [iri] (0.55) |
| 8 | grated parmesan cheese [ita] (0.52) | roasted white sesame seeds [jap] (0.53) | kraft grated parmesan cheese [ita] (0.52) | elbow pasta [gre] (0.53) | frozen banana [bra] (0.54) | key lime [bra] (0.54) |
| − 側 cuisine の印が付いた数 | 1 | 6 | 7 | 6 | 5 | 4 |
| 「+ 側だけ」上位8との重なり | 4 | 1 | 0 | 1 | 1 | 0 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | dried udon [jap] (0.61) | dried udon [jap] (0.61) | grated parmesan cheese [ita] (0.63) | grated parmesan cheese [ita] (0.72) | grated parmesan cheese [ita] (0.75) | grated parmesan cheese [ita] (0.75) | grated parmesan cheese [ita] (0.74) |
| 2 | roasted white sesame seeds [jap] (0.59) | roasted white sesame seeds [jap] (0.58) | dried udon [jap] (0.56) | shredded parmesan cheese [ita] (0.55) | shredded parmesan cheese [ita] (0.57) | shredded parmesan cheese [ita] (0.57) | shredded parmesan cheese [ita] (0.60) |
| 3 | shredded nori [kor] (0.58) | shredded nori [kor] (0.58) | roasted white sesame seeds [jap] (0.54) | freshly grated parmesan [ita] (0.54) | parmigiano reggiano cheese [ita] (0.57) | large curd cottage cheese [rus] (0.56) | cube steaks [sou] (0.58) |
| 4 | soy sauce [kor] (0.57) | soy sauce [kor] (0.55) | shredded nori [kor] (0.54) | shaved parmesan cheese [ita] (0.53) | shaved parmesan cheese [ita] (0.56) | cube steaks [sou] (0.54) | elbow pasta [gre] (0.57) |
| 5 | chili paste [kor] (0.56) | grated parmesan cheese [ita] (0.55) | soy sauce [kor] (0.51) | parmigiano reggiano cheese [ita] (0.53) | parmagiano reggiano [ita] (0.56) | tonkatsu sauce [jap] (0.54) | large curd cottage cheese [rus] (0.56) |
| 6 | mung bean noodles [vie] (0.54) | chili paste [kor] (0.54) | shredded parmesan cheese [ita] (0.51) | parmagiano reggiano [ita] (0.53) | freshly grated parmesan [ita] (0.55) | toasted slivered almonds [mor] (0.53) | grated romano cheese [ita] (0.56) |
| 7 | sesame oil [kor] (0.53) | sesame oil [kor] (0.52) | parmagiano reggiano [ita] (0.51) | dried udon [jap] (0.53) | romano cheese [ita] (0.53) | parmigiano reggiano cheese [ita] (0.53) | frozen cheese ravioli [ita] (0.55) |
| 8 | grated parmesan cheese [ita] (0.52) | yuzu [jap] (0.51) | tonkatsu sauce [jap] (0.51) | elbow pasta [gre] (0.52) | pesto sauce [ita] (0.52) | pesto sauce [ita] (0.51) | parmagiano reggiano [ita] (0.54) |
| − 側 cuisine の印が付いた数 | 1 | 1 | 3 | 6 | 8 | 4 | 5 |
| 「+ 側だけ」上位8との重なり | 4 | 4 | 3 | 0 | 0 | 2 | 1 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | dried udon [jap] (0.61) | grated parmesan cheese [ita] (0.62) | grated parmesan cheese [ita] (0.67) | grated parmesan cheese [ita] (0.69) | parmigiano-reggiano cheese [ita] (0.73) | louisiana hot sauce [caj] (0.98) |
| 2 | roasted white sesame seeds [jap] (0.59) | shredded parmesan cheese [ita] (0.56) | shredded parmesan cheese [ita] (0.57) | provolone cheese [ita] (0.65) | italian cheese [ita] (0.69) | dark corn syrup [sou] (0.98) |
| 3 | shredded nori [kor] (0.58) | kimchi juice [kor] (0.56) | fish balls [fil] (0.57) | swiss cheese [fre] (0.61) | shredded cheese [mex] (0.63) | jasmine rice [tha] (0.97) |
| 4 | soy sauce [kor] (0.57) | roasted white sesame seeds [jap] (0.56) | shaved parmesan cheese [ita] (0.56) | white cheddar cheese [sou] (0.60) | french mustard [bri] (0.61) | crushed garlic [fil] (0.97) |
| 5 | chili paste [kor] (0.56) | dried udon [jap] (0.55) | cilantro [mex] (0.55) | asiago [ita] (0.59) | hanger steak [fre] (0.60) | beef stew meat [iri] (0.97) |
| 6 | mung bean noodles [vie] (0.54) | shredded nori [kor] (0.53) | toasted slivered almonds [mor] (0.55) | sharp cheddar cheese [sou] (0.58) | mozzarella cheese [ita] (0.60) | roquefort cheese [fre] (0.97) |
| 7 | sesame oil [kor] (0.53) | cilantro [mex] (0.52) | chili paste [kor] (0.55) | dill [rus] (0.58) | small red beans [caj] (0.60) | orzo pasta [gre] (0.96) |
| 8 | grated parmesan cheese [ita] (0.52) | fish balls [fil] (0.50) | stilton cheese [bri] (0.54) | gruyere cheese [fre] (0.57) | chestnut mushrooms [bri] (0.60) | snappers [jam] (0.96) |
| − 側 cuisine の印が付いた数 | 1 | 2 | 3 | 3 | 3 | 0 |
| 「+ 側だけ」上位8との重なり | 4 | 1 | 0 | 0 | 0 | 0 |

## 食材だけ: soy sauce − ginger + basil

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | fresh basil [ita] (0.47) | low sodium soy sauce [chi] (0.48) | low sodium soy sauce [chi] (0.43) | low sodium soy sauce [chi] (0.44) | low sodium soy sauce [chi] (0.46) | low sodium soy sauce [chi] (0.49) |
| 2 | low sodium soy sauce [chi] (0.43) | fresh basil [ita] (0.45) | reduced sodium soy sauce [chi] (0.39) | reduced sodium soy sauce [chi] (0.40) | reduced sodium soy sauce [chi] (0.45) | reduced sodium soy sauce [chi] (0.43) |
| 3 | reduced sodium soy sauce [chi] (0.42) | reduced sodium soy sauce [chi] (0.45) | light soy sauce [chi] (0.38) | fresh basil [ita] (0.40) | bocconcini [ita] (0.42) | light soy sauce [chi] (0.42) |
| 4 | bocconcini [ita] (0.41) | bocconcini [ita] (0.43) | fresh basil [ita] (0.38) | bocconcini [ita] (0.39) | fresh basil [ita] (0.41) | bocconcini [ita] (0.41) |
| 5 | corn flakes cereal [sou] (0.38) | light soy sauce [chi] (0.41) | bocconcini [ita] (0.36) | demerara sugar [bri] (0.38) | light soy sauce [chi] (0.40) | sweet gherkin [rus] (0.39) |
| 6 | pea shoots [fil] (0.38) | sausage meat [bri] (0.40) | demerara sugar [bri] (0.36) | light soy sauce [chi] (0.38) | plain yogurt [ind] (0.39) | ice cream [iri] (0.39) |
| 7 | sausage meat [bri] (0.38) | dried basil [ita] (0.40) | corn flakes cereal [sou] (0.35) | ice cream [iri] (0.37) | half & half (0.38) | plain yogurt [ind] (0.39) |
| 8 | italian sausage [ita] (0.37) | corn flakes cereal [sou] (0.39) | herbs [vie] (0.35) | graham cracker crumbs [bri] (0.37) | demerara sugar [bri] (0.37) | half & half (0.39) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 1 | 2 | 1 | 1 | 0 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | fresh basil [ita] (0.47) | fresh basil [ita] (0.46) | low sodium soy sauce [chi] (0.46) | low sodium soy sauce [chi] (0.47) | fresh basil [ita] (0.49) | reduced sodium soy sauce [chi] (0.49) | reduced sodium soy sauce [chi] (0.49) |
| 2 | low sodium soy sauce [chi] (0.43) | low sodium soy sauce [chi] (0.43) | reduced sodium soy sauce [chi] (0.44) | reduced sodium soy sauce [chi] (0.44) | low sodium soy sauce [chi] (0.47) | low sodium soy sauce [chi] (0.49) | low sodium soy sauce [chi] (0.48) |
| 3 | reduced sodium soy sauce [chi] (0.42) | bocconcini [ita] (0.42) | fresh basil [ita] (0.43) | bocconcini [ita] (0.44) | bocconcini [ita] (0.46) | fresh dill [rus] (0.45) | fresh dill [rus] (0.45) |
| 4 | bocconcini [ita] (0.41) | reduced sodium soy sauce [chi] (0.41) | bocconcini [ita] (0.42) | fresh basil [ita] (0.42) | reduced sodium soy sauce [chi] (0.45) | fresh basil [ita] (0.43) | dijon [fre] (0.42) |
| 5 | corn flakes cereal [sou] (0.38) | sausage meat [bri] (0.40) | sausage meat [bri] (0.40) | sausage meat [bri] (0.40) | brine-cured olives [gre] (0.40) | bocconcini [ita] (0.43) | canned black beans [mex] (0.42) |
| 6 | pea shoots [fil] (0.38) | corn flakes cereal [sou] (0.38) | corn flakes cereal [sou] (0.38) | light soy sauce [chi] (0.40) | corn flakes cereal [sou] (0.39) | ground lamb [gre] (0.39) | soda bread [iri] (0.42) |
| 7 | sausage meat [bri] (0.38) | dried basil [ita] (0.38) | light soy sauce [chi] (0.38) | dried basil [ita] (0.39) | fresh basil leaves [ita] (0.39) | low-fat spaghetti sauce [ita] (0.39) | bocconcini [ita] (0.42) |
| 8 | italian sausage [ita] (0.37) | pea shoots [fil] (0.38) | dijon [fre] (0.38) | dijon [fre] (0.38) | low-fat spaghetti sauce [ita] (0.38) | corn flakes cereal [sou] (0.38) | whole wheat bread [bri] (0.41) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 1 | 1 | 1 | 2 | 2 | 1 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | fresh basil [ita] (0.47) | low sodium soy sauce [chi] (0.49) | fresh dill [rus] (0.52) | low sodium soy sauce [chi] (0.53) | frozen mixed thawed vegetables, [kor] (0.63) | green cabbage [iri] (0.99) |
| 2 | low sodium soy sauce [chi] (0.43) | reduced sodium soy sauce [chi] (0.48) | calamari [bra] (0.49) | halibut steak [gre] (0.52) | blueberries [rus] (0.62) | cornbread [sou] (0.98) |
| 3 | reduced sodium soy sauce [chi] (0.42) | fresh basil [ita] (0.45) | low sodium soy sauce [chi] (0.49) | smoked haddock [bri] (0.49) | brussels sprouts [bri] (0.60) | porridge oats [bri] (0.96) |
| 4 | bocconcini [ita] (0.41) | sausage meat [bri] (0.42) | fresh basil [ita] (0.47) | kikkoman soy sauce [fil] (0.48) | lump crab meat [caj] (0.59) | worcestershire sauce [caj] (0.96) |
| 5 | corn flakes cereal [sou] (0.38) | light soy sauce [chi] (0.41) | cherry tomatoes [gre] (0.46) | calamari [bra] (0.48) | cream sweeten whip [sou] (0.59) | cherry preserves [spa] (0.96) |
| 6 | pea shoots [fil] (0.38) | corn flakes cereal [sou] (0.39) | halibut steak [gre] (0.45) | chicken livers [fil] (0.48) | maple syrup [sou] (0.59) | tawny port [bri] (0.96) |
| 7 | sausage meat [bri] (0.38) | dijon [fre] (0.39) | vine ripened tomatoes (0.43) | fresh dill [rus] (0.48) | champagne [fre] (0.58) | quinces [gre] (0.96) |
| 8 | italian sausage [ita] (0.37) | kikkoman soy sauce [fil] (0.39) | medium shrimp [caj] (0.43) | marjoram [rus] (0.48) | bottled clam juice [spa] (0.56) | fatfree lowsodium chicken broth [bra] (0.96) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 2 | 1 | 2 | 0 | 0 | 0 |

## 食材だけ: sake − rice + grapes

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | mirin [jap] (0.48) | mirin [jap] (0.54) | mirin [jap] (0.49) | mirin [jap] (0.49) | poblano chiles [mex] (0.48) | poblano chiles [mex] (0.52) |
| 2 | shiso [jap] (0.46) | shiso [jap] (0.49) | shiso [jap] (0.46) | poblano chiles [mex] (0.47) | lemon pepper [caj] (0.46) | grappa [ita] (0.48) |
| 3 | apricot preserves [rus] (0.42) | toasted sesame oil [kor] (0.44) | calimyrna figs [bri] (0.44) | shoyu [jap] (0.42) | garlic salt (0.43) | gremolata [ita] (0.47) |
| 4 | dashi powder [jap] (0.40) | apricot preserves [rus] (0.43) | apricot preserves [rus] (0.43) | gold tequila [jam] (0.41) | pesto sauce [ita] (0.41) | salted roast peanuts [tha] (0.47) |
| 5 | navel oranges [spa] (0.40) | dashi powder [jap] (0.42) | cranberries [bri] (0.43) | lemon pepper [caj] (0.41) | mirin [jap] (0.41) | sanding sugar [caj] (0.46) |
| 6 | dried bonito flakes [jap] (0.39) | napa cabbage leaves [chi] (0.42) | plain whole-milk yogurt [ind] (0.43) | apricot preserves [rus] (0.41) | calimyrna figs [bri] (0.41) | rose water [mor] (0.45) |
| 7 | napa cabbage leaves [chi] (0.39) | konbu [jap] (0.42) | grappa [ita] (0.42) | nori sheets [jap] (0.41) | mushroom soy sauce [chi] (0.40) | lemon pepper [caj] (0.45) |
| 8 | matcha green tea powder [jap] (0.39) | dried bonito flakes [jap] (0.42) | navel oranges [spa] (0.41) | shiso [jap] (0.40) | shoyu [jap] (0.40) | garlic salt (0.45) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 1 | 0 | 0 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | mirin [jap] (0.48) | mirin [jap] (0.49) | mirin [jap] (0.52) | mirin [jap] (0.54) | mirin [jap] (0.52) | calimyrna figs [bri] (0.51) | poblano chiles [mex] (0.54) |
| 2 | shiso [jap] (0.46) | shiso [jap] (0.47) | shiso [jap] (0.47) | shiso [jap] (0.47) | calimyrna figs [bri] (0.48) | grappa [ita] (0.50) | fat-free buttermilk [rus] (0.52) |
| 3 | apricot preserves [rus] (0.42) | apricot preserves [rus] (0.41) | dried bonito flakes [jap] (0.42) | toasted sesame oil [kor] (0.44) | grappa [ita] (0.46) | mirin [jap] (0.49) | grappa [ita] (0.48) |
| 4 | dashi powder [jap] (0.40) | dashi powder [jap] (0.41) | toasted sesame oil [kor] (0.42) | dried bonito flakes [jap] (0.44) | shiso [jap] (0.45) | raspberry vinegar [gre] (0.48) | blackberry jam [fil] (0.47) |
| 5 | navel oranges [spa] (0.40) | matcha green tea powder [jap] (0.40) | calimyrna figs [bri] (0.41) | dashi powder [jap] (0.42) | walnut pieces [iri] (0.44) | salted roast peanuts [tha] (0.48) | raspberry vinegar [gre] (0.46) |
| 6 | dried bonito flakes [jap] (0.39) | napa cabbage leaves [chi] (0.40) | dashi powder [jap] (0.41) | calimyrna figs [bri] (0.41) | apricot preserves [rus] (0.43) | tangerine juice [bri] (0.48) | dried apple [iri] (0.45) |
| 7 | napa cabbage leaves [chi] (0.39) | dried bonito flakes [jap] (0.40) | napa cabbage leaves [chi] (0.40) | napa cabbage leaves [chi] (0.41) | raspberry vinegar [gre] (0.43) | sauterne [fre] (0.47) | hot chili paste [vie] (0.45) |
| 8 | matcha green tea powder [jap] (0.39) | shoyu [jap] (0.40) | apricot preserves [rus] (0.40) | grappa [ita] (0.41) | toasted sesame oil [kor] (0.43) | apricot preserves [rus] (0.46) | low-fat buttermilk [iri] (0.45) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 0 | 0 | 0 | 0 | 1 | 1 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | mirin [jap] (0.48) | grappa [ita] (0.52) | poblano chiles [mex] (0.61) | roasted chestnuts [fre] (0.63) | vanilla beans [fre] (0.68) | oregano leaves [fil] (0.97) |
| 2 | shiso [jap] (0.46) | calimyrna figs [bri] (0.47) | grappa [ita] (0.59) | grappa [ita] (0.63) | rose petals [mor] (0.68) | jerk sauce [jam] (0.97) |
| 3 | apricot preserves [rus] (0.42) | raspberry vinegar [gre] (0.45) | raspberry vinegar [gre] (0.58) | poblano chiles [mex] (0.62) | salted roast peanuts [tha] (0.65) | grated lemon peel [bri] (0.96) |
| 4 | dashi powder [jap] (0.40) | mirin [jap] (0.45) | lemon-lime soda [spa] (0.54) | salted roast peanuts [tha] (0.61) | carbonated water [spa] (0.64) | boneless beef short ribs [vie] (0.96) |
| 5 | navel oranges [spa] (0.40) | fat-free buttermilk [rus] (0.45) | tangerine juice [bri] (0.54) | pink grapefruit juice [kor] (0.60) | pink grapefruit juice [kor] (0.64) | roast turkey [gre] (0.95) |
| 6 | dried bonito flakes [jap] (0.39) | vin santo [ita] (0.45) | seedless red grapes [mor] (0.53) | pink grapefruit [spa] (0.59) | grappa [ita] (0.64) | ground pepper (0.94) |
| 7 | napa cabbage leaves [chi] (0.39) | amaretti cookies [ita] (0.44) | panettone [rus] (0.52) | crème de cassis [fre] (0.59) | pork lard [mex] (0.60) | yoghurt [ind] (0.94) |
| 8 | matcha green tea powder [jap] (0.39) | sauterne [fre] (0.44) | pink grapefruit juice [kor] (0.52) | vanilla beans [fre] (0.58) | kabocha squash [tha] (0.60) | ground lamb [gre] (0.94) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 0 | 1 | 1 | 2 | 2 | 0 |

## 食材だけ: tofu − soy sauce + cheese

### LDA（run.py と同じ）

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

### 重心差 SVD

| # | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | shredded cheese [mex] (0.57) | shredded cheese [mex] (0.53) | shredded cheese [mex] (0.51) | shredded cheese [mex] (0.53) | shredded cheese [mex] (0.53) | shredded cheese [mex] (0.54) |
| 2 | cheddar cheese [mex] (0.48) | grating cheese [bra] (0.43) | grating cheese [bra] (0.42) | cheddar cheese [mex] (0.43) | cheddar cheese [mex] (0.42) | cheddar cheese [mex] (0.44) |
| 3 | shredded cheddar cheese [mex] (0.47) | cheddar cheese [mex] (0.42) | cheddar cheese [mex] (0.41) | grating cheese [bra] (0.43) | shredded cheddar cheese [mex] (0.42) | shredded cheddar cheese [mex] (0.42) |
| 4 | grating cheese [bra] (0.47) | mexican cheese blend [mex] (0.42) | shredded cheddar cheese [mex] (0.40) | shredded cheddar cheese [mex] (0.42) | extra firm tofu [tha] (0.40) | cooked quinoa [mex] (0.40) |
| 5 | mexican cheese blend [mex] (0.47) | shredded cheddar cheese [mex] (0.42) | mexican cheese blend [mex] (0.37) | mexican cheese blend [mex] (0.36) | mexican cheese blend [mex] (0.38) | mexican cheese blend [mex] (0.40) |
| 6 | goat cheese (0.44) | cooked quinoa [mex] (0.41) | chèvre [mor] (0.36) | doritos [mex] (0.36) | grating cheese [bra] (0.38) | extra firm tofu [tha] (0.39) |
| 7 | chèvre [mor] (0.44) | doritos [mex] (0.40) | doritos [mex] (0.36) | soft tofu [jap] (0.35) | sharp cheddar cheese [sou] (0.38) | grating cheese [bra] (0.39) |
| 8 | monterey jack [mex] (0.43) | tortilla wraps [mex] (0.39) | cooked quinoa [mex] (0.36) | goat cheese (0.35) | cooked quinoa [mex] (0.37) | sharp cheddar cheese [sou] (0.37) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 5 | 5 | 5 | 5 | 4 | 4 |

### INLP（1 反復 1 本）

| # | k=0 | 1反復 (k=1) | 3反復 (k=3) | 5反復 (k=5) | 10反復 (k=10) | 19反復 (k=19) | 30反復 (k=30) |
|---|---|---|---|---|---|---|---|
| 1 | shredded cheese [mex] (0.57) | shredded cheese [mex] (0.57) | shredded cheese [mex] (0.54) | shredded cheese [mex] (0.54) | shredded cheese [mex] (0.55) | shredded cheese [mex] (0.52) | shredded cheese [mex] (0.55) |
| 2 | cheddar cheese [mex] (0.48) | grating cheese [bra] (0.49) | grating cheese [bra] (0.47) | cheddar cheese [mex] (0.47) | cheddar cheese [mex] (0.47) | cheddar cheese [mex] (0.45) | cheddar cheese [mex] (0.53) |
| 3 | shredded cheddar cheese [mex] (0.47) | cheddar cheese [mex] (0.48) | mexican cheese blend [mex] (0.45) | shredded cheddar cheese [mex] (0.46) | shredded cheddar cheese [mex] (0.44) | grating cheese [bra] (0.42) | grating cheese [bra] (0.47) |
| 4 | grating cheese [bra] (0.47) | mexican cheese blend [mex] (0.48) | cheddar cheese [mex] (0.45) | grating cheese [bra] (0.45) | grating cheese [bra] (0.42) | cooked quinoa [mex] (0.41) | cooked quinoa [mex] (0.44) |
| 5 | mexican cheese blend [mex] (0.47) | shredded cheddar cheese [mex] (0.47) | shredded cheddar cheese [mex] (0.45) | mexican cheese blend [mex] (0.43) | cooked quinoa [mex] (0.41) | shredded cheddar cheese [mex] (0.39) | mexican cheese blend [mex] (0.44) |
| 6 | goat cheese (0.44) | monterey jack [mex] (0.45) | monterey jack [mex] (0.42) | cooked quinoa [mex] (0.40) | extra-lean ground beef [kor] (0.41) | extra-lean ground beef [kor] (0.39) | shredded cheddar cheese [mex] (0.43) |
| 7 | chèvre [mor] (0.44) | goat cheese (0.43) | goat cheese (0.41) | doritos [mex] (0.40) | mexican cheese blend [mex] (0.40) | tilapia [fil] (0.37) | monterey jack [mex] (0.41) |
| 8 | monterey jack [mex] (0.43) | doritos [mex] (0.43) | doritos [mex] (0.41) | old el paso flour tortillas [mex] (0.39) | sharp cheddar cheese [sou] (0.39) | shredded nori [kor] (0.37) | red curry paste [tha] (0.40) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 5 | 5 | 5 | 4 | 5 | 3 | 5 |

### INLP（1 反復で係数行列の行空間を除去）

| # | k=0 | 1反復 (k=19) | 2反復 (k=38) | 3反復 (k=57) | 4反復 (k=76) | 5反復 (k=95) |
|---|---|---|---|---|---|---|
| 1 | shredded cheese [mex] (0.57) | shredded cheese [mex] (0.56) | shredded cheese [mex] (0.60) | shredded cheese [mex] (0.63) | baby corn [tha] (0.64) | soft fresh goat cheese [fre] (0.98) |
| 2 | cheddar cheese [mex] (0.48) | cheddar cheese [mex] (0.51) | cheddar cheese [mex] (0.58) | cheddar cheese [mex] (0.56) | pork [fil] (0.62) | light red kidney beans [caj] (0.98) |
| 3 | shredded cheddar cheese [mex] (0.47) | shredded cheddar cheese [mex] (0.49) | grating cheese [bra] (0.51) | shredded monterey jack cheese [mex] (0.53) | sharp cheddar cheese [sou] (0.60) | sushi rice [jap] (0.98) |
| 4 | grating cheese [bra] (0.47) | mexican cheese blend [mex] (0.45) | mexican cheese blend [mex] (0.51) | mexican cheese blend [mex] (0.52) | fresh chevre [gre] (0.59) | apple cider vinegar [fil] (0.97) |
| 5 | mexican cheese blend [mex] (0.47) | sharp cheddar cheese [sou] (0.45) | monterey jack [mex] (0.51) | reduced fat cheddar cheese [mex] (0.51) | chipotle paste [mex] (0.58) | country style bread [spa] (0.97) |
| 6 | goat cheese (0.44) | grating cheese [bra] (0.42) | shredded cheddar cheese [mex] (0.50) | shredded cheddar cheese [mex] (0.50) | feta cheese [gre] (0.57) | roquefort cheese [fre] (0.97) |
| 7 | chèvre [mor] (0.44) | monterey jack [mex] (0.41) | sharp cheddar cheese [sou] (0.49) | swanson chicken broth [vie] (0.50) | garlic pepper seasoning [caj] (0.57) | french mustard [bri] (0.96) |
| 8 | monterey jack [mex] (0.43) | cooked quinoa [mex] (0.40) | doritos [mex] (0.49) | monterey jack [mex] (0.49) | pattypan squash [ita] (0.56) | chopped fresh thyme [fre] (0.96) |
| − 側 cuisine の印が付いた数 | 0 | 0 | 0 | 0 | 0 | 0 |
| 「+ 側だけ」上位8との重なり | 5 | 5 | 4 | 2 | 1 | 0 |

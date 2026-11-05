# Exp-01b 軸への射影（k ごと）

- 軸・射影の式は Exp-01 と同じ。軸ベクトルは**その k の空間で**作り直す（soy sauce / butter の食材ベクトル、cuisine 重心）
- 表のセルは「cuisine (平均射影値)」。上 = 左側の極寄り
- η² = 料理の射影値の分散のうち、cuisine の違いで説明される割合。0 なら軸は国籍と無関係

## soy sauce ↔ butter

### cuisine 平均の並び

| 順 | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | korean (+0.262) | korean (+0.193) | korean (+0.188) | korean (+0.179) | korean (+0.183) | korean (+0.181) |
| 2 | chinese (+0.248) | chinese (+0.169) | chinese (+0.163) | chinese (+0.168) | vietnamese (+0.165) | vietnamese (+0.170) |
| 3 | japanese (+0.201) | japanese (+0.128) | japanese (+0.132) | vietnamese (+0.155) | chinese (+0.163) | thai (+0.163) |
| 4 | vietnamese (+0.196) | vietnamese (+0.106) | vietnamese (+0.108) | thai (+0.151) | thai (+0.161) | chinese (+0.162) |
| 5 | thai (+0.190) | thai (+0.083) | thai (+0.091) | japanese (+0.115) | japanese (+0.131) | japanese (+0.132) |
| 6 | filipino (+0.056) | filipino (+0.031) | filipino (+0.035) | filipino (+0.063) | filipino (+0.058) | filipino (+0.043) |
| 7 | jamaican (-0.032) | mexican (-0.019) | mexican (-0.005) | jamaican (+0.023) | jamaican (+0.019) | mexican (+0.008) |
| 8 | indian (-0.035) | jamaican (-0.021) | jamaican (-0.010) | mexican (+0.010) | mexican (+0.010) | jamaican (+0.003) |
| 9 | mexican (-0.064) | brazilian (-0.052) | indian (-0.023) | indian (+0.007) | indian (+0.003) | indian (-0.008) |
| 10 | brazilian (-0.073) | cajun_creole (-0.070) | moroccan (-0.038) | brazilian (-0.015) | moroccan (-0.007) | brazilian (-0.018) |
| 11 | moroccan (-0.099) | spanish (-0.071) | brazilian (-0.043) | moroccan (-0.019) | brazilian (-0.017) | moroccan (-0.028) |
| 12 | cajun_creole (-0.122) | moroccan (-0.075) | greek (-0.059) | cajun_creole (-0.032) | cajun_creole (-0.042) | cajun_creole (-0.044) |
| 13 | spanish (-0.126) | greek (-0.078) | spanish (-0.060) | spanish (-0.045) | spanish (-0.043) | spanish (-0.047) |
| 14 | greek (-0.136) | indian (-0.081) | cajun_creole (-0.066) | greek (-0.049) | greek (-0.049) | greek (-0.048) |
| 15 | russian (-0.162) | italian (-0.106) | italian (-0.101) | italian (-0.089) | italian (-0.094) | italian (-0.101) |
| 16 | italian (-0.176) | russian (-0.126) | russian (-0.115) | russian (-0.102) | russian (-0.098) | russian (-0.105) |
| 17 | southern_us (-0.188) | french (-0.143) | french (-0.138) | southern_us (-0.113) | southern_us (-0.113) | southern_us (-0.120) |
| 18 | french (-0.196) | southern_us (-0.146) | southern_us (-0.143) | french (-0.122) | french (-0.119) | french (-0.120) |
| 19 | irish (-0.206) | irish (-0.165) | irish (-0.157) | irish (-0.138) | irish (-0.132) | irish (-0.142) |
| 20 | british (-0.213) | british (-0.176) | british (-0.167) | british (-0.149) | british (-0.145) | british (-0.155) |
| η² | 0.676 | 0.522 | 0.507 | 0.497 | 0.501 | 0.496 |
| 射影値の標準偏差 | 0.181 | 0.139 | 0.137 | 0.137 | 0.138 | 0.142 |
| k=0 の並びとの順位相関 | +1.00 | +0.96 | +0.98 | +0.99 | +0.99 | +0.98 |

### 食材の左の極側（上位 10）

- k=0: soy sauce (+0.67), light soy sauce (+0.53), reduced sodium soy sauce (+0.49), low sodium soy sauce (+0.47), gluten free soy sauce (+0.47), tamari soy sauce (+0.47), mushroom soy sauce (+0.47), brown rice vinegar (+0.45), sesame chili oil (+0.45), sesame oil (+0.44)
- k=1: soy sauce (+0.65), light soy sauce (+0.44), gluten free soy sauce (+0.40), reduced sodium soy sauce (+0.38), tamari soy sauce (+0.37), mushroom soy sauce (+0.37), low sodium soy sauce (+0.36), sesame chili oil (+0.36), brown rice vinegar (+0.34), accent seasoning (+0.34)
- k=3: soy sauce (+0.65), light soy sauce (+0.43), gluten free soy sauce (+0.39), tamari soy sauce (+0.37), reduced sodium soy sauce (+0.37), sesame chili oil (+0.35), mushroom soy sauce (+0.35), low sodium soy sauce (+0.35), red radishes (+0.33), liquid smoke (+0.33)
- k=5: soy sauce (+0.64), light soy sauce (+0.42), gluten free soy sauce (+0.38), accent seasoning (+0.36), tamari soy sauce (+0.35), mushroom soy sauce (+0.35), sesame chili oil (+0.34), reduced sodium soy sauce (+0.34), low sodium soy sauce (+0.33), jerk marinade (+0.33)
- k=10: soy sauce (+0.64), light soy sauce (+0.40), gluten free soy sauce (+0.37), reduced sodium soy sauce (+0.37), mushroom soy sauce (+0.36), tamari soy sauce (+0.36), accent seasoning (+0.35), jerk marinade (+0.35), sesame chili oil (+0.34), red radishes (+0.34)
- k=19: soy sauce (+0.64), light soy sauce (+0.44), reduced sodium soy sauce (+0.43), mushroom soy sauce (+0.41), tamari soy sauce (+0.37), gluten free soy sauce (+0.37), red radishes (+0.36), sesame chili oil (+0.36), brown rice vinegar (+0.35), jerk marinade (+0.35)

### 食材の右の極側（上位 10）

- k=0: butter (-0.67), unsalted butter (-0.48), margarine (-0.45), light butter (-0.38), emmenthal (-0.36), compote (-0.36), melted butter (-0.35), softened butter (-0.35), buttermilk cornbread (-0.34), condensed cheddar cheese soup (-0.34)
- k=1: butter (-0.65), margarine (-0.47), unsalted butter (-0.44), light butter (-0.38), melted butter (-0.36), salted butter (-0.36), softened butter (-0.33), ghee (-0.32), whole nutmegs (-0.32), saffron (-0.32)
- k=3: butter (-0.65), margarine (-0.48), unsalted butter (-0.45), salted butter (-0.37), light butter (-0.36), melted butter (-0.35), butter-margarine blend (-0.34), softened butter (-0.33), evaporated skim milk (-0.32), light cream cheese (-0.30)
- k=5: butter (-0.64), margarine (-0.46), unsalted butter (-0.45), salted butter (-0.35), light butter (-0.34), melted butter (-0.33), truffle oil (-0.32), softened butter (-0.30), buttermilk biscuits (-0.30), butter-margarine blend (-0.30)
- k=10: butter (-0.64), margarine (-0.48), unsalted butter (-0.45), salted butter (-0.37), melted butter (-0.35), light butter (-0.35), truffle oil (-0.32), buttermilk biscuits (-0.31), butter-margarine blend (-0.30), softened butter (-0.30)
- k=19: butter (-0.64), margarine (-0.53), unsalted butter (-0.44), salted butter (-0.40), light butter (-0.39), melted butter (-0.35), butter-margarine blend (-0.34), buttermilk biscuits (-0.33), saffron (-0.31), cinnamon sugar (-0.31)

## japanese 重心 ↔ italian 重心

### cuisine 平均の並び

| 順 | k=0 | k=1 | k=3 | k=5 | k=10 | k=19 |
|---|---|---|---|---|---|---|
| 1 | japanese (+0.308) | japanese (+0.246) | japanese (+0.242) | japanese (+0.220) | chinese (+0.224) | korean (+0.231) |
| 2 | korean (+0.303) | korean (+0.224) | korean (+0.211) | korean (+0.203) | japanese (+0.220) | chinese (+0.230) |
| 3 | chinese (+0.292) | chinese (+0.189) | chinese (+0.175) | vietnamese (+0.196) | korean (+0.217) | japanese (+0.221) |
| 4 | vietnamese (+0.234) | vietnamese (+0.132) | vietnamese (+0.107) | chinese (+0.184) | vietnamese (+0.207) | vietnamese (+0.209) |
| 5 | thai (+0.228) | thai (+0.102) | thai (+0.072) | thai (+0.183) | thai (+0.189) | thai (+0.199) |
| 6 | filipino (+0.107) | filipino (+0.078) | filipino (+0.062) | filipino (+0.087) | filipino (+0.102) | filipino (+0.097) |
| 7 | indian (+0.038) | brazilian (+0.021) | brazilian (-0.002) | brazilian (+0.025) | indian (+0.039) | brazilian (+0.041) |
| 8 | jamaican (-0.006) | jamaican (+0.009) | indian (-0.006) | indian (+0.021) | brazilian (+0.029) | indian (+0.038) |
| 9 | brazilian (-0.017) | indian (-0.006) | jamaican (-0.011) | jamaican (-0.007) | jamaican (+0.005) | jamaican (+0.006) |
| 10 | russian (-0.083) | russian (-0.029) | russian (-0.032) | russian (-0.041) | russian (-0.035) | british (-0.048) |
| 11 | british (-0.094) | mexican (-0.040) | british (-0.043) | british (-0.054) | british (-0.053) | russian (-0.051) |
| 12 | mexican (-0.097) | british (-0.042) | irish (-0.055) | irish (-0.070) | southern_us (-0.064) | southern_us (-0.066) |
| 13 | southern_us (-0.101) | southern_us (-0.044) | southern_us (-0.057) | southern_us (-0.071) | irish (-0.071) | irish (-0.076) |
| 14 | irish (-0.108) | irish (-0.051) | mexican (-0.112) | mexican (-0.101) | moroccan (-0.085) | moroccan (-0.082) |
| 15 | moroccan (-0.138) | moroccan (-0.114) | french (-0.113) | moroccan (-0.102) | mexican (-0.095) | mexican (-0.104) |
| 16 | cajun_creole (-0.173) | french (-0.117) | moroccan (-0.118) | french (-0.109) | french (-0.109) | french (-0.111) |
| 17 | french (-0.178) | cajun_creole (-0.123) | cajun_creole (-0.139) | spanish (-0.150) | spanish (-0.144) | spanish (-0.139) |
| 18 | spanish (-0.203) | spanish (-0.148) | spanish (-0.157) | cajun_creole (-0.163) | cajun_creole (-0.150) | cajun_creole (-0.157) |
| 19 | greek (-0.246) | greek (-0.195) | greek (-0.190) | greek (-0.181) | greek (-0.167) | greek (-0.169) |
| 20 | italian (-0.307) | italian (-0.250) | italian (-0.245) | italian (-0.221) | italian (-0.219) | italian (-0.220) |
| η² | 0.735 | 0.623 | 0.606 | 0.595 | 0.602 | 0.595 |
| 射影値の標準偏差 | 0.227 | 0.179 | 0.176 | 0.181 | 0.188 | 0.192 |
| k=0 の並びとの順位相関 | +1.00 | +0.99 | +0.98 | +0.98 | +0.98 | +0.98 |

### 食材の左の極側（上位 10）

- k=0: soy sauce (+0.55), sesame oil (+0.54), mirin (+0.53), bonito (+0.53), toasted sesame seeds (+0.53), togarashi (+0.52), satsuma imo (+0.52), toasted sesame oil (+0.51), sushi grade tuna (+0.51), nori sheets (+0.49)
- k=1: bonito (+0.59), satsuma imo (+0.47), shichimi togarashi (+0.47), kewpie mayonnaise (+0.47), dried bonito flakes (+0.45), mirin (+0.45), sushi grade tuna (+0.45), togarashi (+0.44), toasted sesame seeds (+0.43), nori sheets (+0.42)
- k=3: bonito (+0.56), mirin (+0.47), satsuma imo (+0.47), dried bonito flakes (+0.46), kewpie mayonnaise (+0.46), shichimi togarashi (+0.46), togarashi (+0.45), roasted white sesame seeds (+0.45), sushi grade tuna (+0.44), bonito flakes (+0.42)
- k=5: bonito (+0.48), roasted white sesame seeds (+0.43), shiso (+0.40), mirin (+0.38), yuzu (+0.38), toasted sesame seeds (+0.37), sushi grade tuna (+0.37), shichimi togarashi (+0.37), ginger ale (+0.37), white cabbage (+0.37)
- k=10: bonito (+0.45), roasted white sesame seeds (+0.41), white cabbage (+0.39), sugar cane (+0.39), ginger ale (+0.38), dark soy sauce (+0.38), sushi grade tuna (+0.37), organic sugar (+0.36), pork neck (+0.36), shiso (+0.35)
- k=19: bonito (+0.44), ginger ale (+0.41), roasted white sesame seeds (+0.41), pork fillet (+0.41), sugar cane (+0.41), toasted sesame seeds (+0.40), organic sugar (+0.40), lime (+0.38), pickled radish (+0.38), beef ribs (+0.38)

### 食材の右の極側（上位 10）

- k=0: uncooked ziti (-0.52), frozen pizza dough (-0.51), cooked meatballs (-0.48), grated parmesan cheese (-0.48), hot cherry pepper (-0.47), uncooked rigatoni (-0.46), parmesan cheese (-0.44), perciatelli (-0.44), penne (-0.44), manicotti (-0.43)
- k=1: uncooked ziti (-0.47), uncooked rigatoni (-0.45), polenta prepar (-0.45), fat-free reduced-sodium chicken broth (-0.44), prosciutto (-0.43), whole wheat penne (-0.43), grated parmesan cheese (-0.42), parmigiano-reggiano cheese (-0.40), italian turkey sausage (-0.40), mild italian sausage (-0.39)
- k=3: polenta prepar (-0.49), uncooked ziti (-0.45), fat-free reduced-sodium chicken broth (-0.44), uncooked rigatoni (-0.43), whole wheat penne (-0.42), prosciutto (-0.41), mild italian sausage (-0.40), grated parmesan cheese (-0.40), cooked meatballs (-0.39), dried oregano (-0.39)
- k=5: polenta prepar (-0.45), dried oregano (-0.40), uncooked ziti (-0.39), diced tomatoes (-0.39), low-fat spaghetti sauce (-0.38), rotini (-0.38), fontina cheese (-0.38), asiago (-0.38), fresh marjoram (-0.38), fat-free reduced-sodium chicken broth (-0.37)
- k=10: polenta prepar (-0.45), uncooked ziti (-0.42), diced tomatoes (-0.41), dried oregano (-0.41), mild italian sausage (-0.40), fontina cheese (-0.39), pimento stuffed green olives (-0.39), beefsteak tomatoes (-0.39), whole wheat penne (-0.39), grated parmesan cheese (-0.38)
- k=19: polenta prepar (-0.43), dried oregano (-0.42), applewood smoked bacon (-0.41), diced tomatoes (-0.41), mild italian sausage (-0.41), uncooked ziti (-0.40), pimento stuffed green olives (-0.40), whole wheat penne (-0.39), prosciutto (-0.39), grated parmesan cheese (-0.39)

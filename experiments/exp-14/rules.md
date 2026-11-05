# Exp-14 規則表: 操作が物理・化学の状態をどう変えるか

2026-09-27 作成。`plan.md` の「設計の見直し」に沿って、状態を2段に分けたうちの **段1（物理・化学の状態）** と、操作による変化の規則をまとめた。**段2（知覚の層）への対応は書いていない**（本人が決める部分）。どの変数が知覚のどれに効きそうかの候補だけを最後に並べた。

- 機械可読版: [`rules.yaml`](rules.yaml)。**表の中身は YAML が正本**で、この文書の表は YAML から作った
- シミュレータ: [`sim/`](sim/)（2026-09-27）。採用値は `rules.yaml` の `sim`、料理の判定条件は `dish_conditions`。結果は [`results/summary.md`](results/summary.md)

## 0. 読み方

**確認の方法**（`check`）

| 区分 | 意味 |
|---|---|
| 本文確認 | 出典の本文（ページ・データベース）を取得して、数値をその場で確認した |
| 抄録確認 | 論文の抄録を取得して確認した（本文は未読） |
| 抜粋のみ | 検索エンジンの抜粋でのみ確認した（本文は取得できなかった・しなかった。403 で弾かれたものを含む） |
| 書籍(章) | 書籍の内容として知っている範囲。ページまでは確かでない。数値は今回ウェブで確かめていない |
| 未確認 | 出典を確認できていない。値は推定 |

**確かさ**: 高 = 一次に近い出典（論文・公的機関・データベース）で本文か抄録を確認、または複数出典で整合／中 = 抜粋のみ、または出典どうしで値に幅や食い違いがある／低 = 出典が弱い（レシピサイト、出典記載のないブログ）か推定。

**数値は出典の表記のまま**書いた（°F 併記の出典は両方）。McGee "On Food and Cooking" は今回本文を開いておらず、他のページが McGee のページ（p.85, p.656）を引いている箇所だけ数値を採った。

## 1. 規模

- 食材 23、操作 13、状態変数 40、規則 78、目標料理 13（＋比較用のゆで卵、14品目のポーチドエッグ）
- 規則の確かさ: 高 32 / 中 36 / 低 10
- 確認の方法: 本文確認 27 / 抄録確認 8 / 抜粋のみ 37 / 書籍(章) 1 / 未確認 5
- 2026-09-27 にポーチドエッグのため R-E21〜R-E23・操作 `poach` を足した（§10）
- 2026-09-28 に修正 B（殻付き卵の卵白の層の温度）と、その結果を見て半熟ゆで卵 `soft_boiled_egg`（16品目、13品外）を足した（§10）

## 2. 食材

`canonical` は `data/labels/taste_scores.csv` の canonical 列（味の層とつなぐ鍵、— は taste_scores に無い）。成分は『日本食品標準成分表（八訂）増補2023年』の g/100g（食品番号つき、本文確認）。salt は食塩相当量。

**選び方**: 目標料理（§6）を作るのに要るものを先に入れ、次に依頼で挙がっていたもの（トマト・鶏肉・牛肉）と、操作「発酵」を持つための酵母を入れた。卵は凝固温度が違う卵白・卵黄を分け、全卵はその混合として展開する。トマト・牛肉・酵母は今回の目標料理には使っていない。

| id | 食材 | canonical | 成分表 | 水分 | たんぱく質 | 脂質 | 炭水化物 | 食塩 | 選んだ理由 |
|---|---|---|---|---|---|---|---|---|---|
| `egg_white` | 卵白 | egg whites | 12014 卵白/生 | 88.3 | 10.1 | Tr | 0.5 | — | プリン・茶碗蒸し・オムレツ等の凝固、メレンゲ系の泡。卵黄と凝固温度が違うので分けて持つ |
| `egg_yolk` | 卵黄 | egg yolks | 12010 卵黄/生 | 49.6 | 16.5 | 34.3 | 0.2 | — | とろみ（65℃）と凝固（70℃）。脂質を含み泡立ちを妨げる |
| `egg_whole` | 全卵（卵白＋卵黄の混合として扱う） | eggs | 12004 全卵/生 | 75.0 | 12.2 | 10.2 | 0.4 | — | 多くの目標料理は全卵。卵白:卵黄の質量比は未確認（推定 約2:1）。計算では egg_white と egg_yolk の混合として展開する |
| `milk` | 牛乳 | milk | 13003 普通牛乳 | 87.4 | 3.3 | 3.8 | 4.8 | 0.1 | プリン・ホワイトソース・スクランブルエッグ・パンケーキ・牛乳ゼリー。卵を薄めて凝固温度を上げる |
| `heavy_cream` | 生クリーム（乳脂肪） | heavy cream | 13014 クリーム/乳脂肪 | 48.2 | 1.9 | 43.0 | 6.5 | 0.1 | ホイップクリーム（乳脂肪30%以上で泡立つ） |
| `butter` | バター（有塩） | butter | 14017 有塩バター（食塩不使用は 14018: 水分15.8 脂質83.0） | 16.2 | 0.6 | 81.0 | 0.2 | 1.9 | ホワイトソースのルー、卵料理の油脂。融け方が温度で変わる |
| `flour` | 小麦粉（薄力粉1等） | flour | 01015 薄力粉/1等（強力粉1等 01020 は たんぱく質11.8） | 14.0 | 8.3 | 1.5 | 75.8 | 0 | ホワイトソース（でんぷんの糊化）、パンケーキ（グルテン・糊化） |
| `rice` | 米（精白米うるち米） | rice | 01083 精白米/うるち米（めし 01088 は水分60.0） | 14.9 | 6.1 | 0.9 | 77.6 | 0 | ご飯（浸漬・糊化・老化） |
| `sugar` | 砂糖（上白糖。グラニュー糖 03005 は炭水化物100.0） | sugar | 03003 上白糖 | 0.7 | 0 | 0 | 99.3 | 0 | カラメル、プリン（凝固温度を上げる）、泡の安定 |
| `salt` | 食塩 | salt | 17012 食塩 | 0.1 | 0 | 0 | 0 | 99.5 | 卵の凝固力・凝固温度を変える（粟津原 1982）、茶碗蒸し・スクランブルエッグの味付け |
| `water` | 水 | water | — | 100 | 0 | 0 | 0 | 0 | ご飯・カラメル（糖液）・ゼラチンの膨潤。加熱媒体としての沸点100℃ |
| `dashi` | だし（かつお・昆布） | — | 17148 かつお・昆布だし | 99.2 | 0.3 | 0 | 0.4 | 0.1 | 茶碗蒸しの希釈液（卵:だし=1:3）。状態の上では「ほぼ水＋わずかな塩」 |
| `vegetable_oil` | 植物油（調合油） | vegetable oil | 14006 調合油 | 0 | 0 | 100.0 | 0 | 0 | 揚げる・炒めるの加熱媒体（100℃を超えられる） |
| `onion` | 玉ねぎ | onions | 06153 たまねぎ/りん茎/生 | 90.1 | 1.0 | 0.1 | 8.4 | 0 | 炒め玉ねぎ（水分蒸発・刺激臭の消失・褐変） |
| `potato` | じゃがいも | potatoes | 02017 じゃがいも/塊茎/皮なし/生 | 79.8 | 1.8 | 0.1 | 17.3 | 0 | フライドポテト（揚げる）。でんぷん糊化とペクチン（煮崩れ・硬化）の規則を持つ |
| `tomato` | トマト | tomatoes | 06182 赤色トマト/生 | 94.0 | 0.7 | 0.1 | 4.7 | 0 | 依頼で挙がった食材。今回の目標料理には使わないため、規則は調べていない（成分のみ） |
| `chicken` | 鶏むね肉（皮なし） | chicken | 11220 若どり/むね/皮なし/生 | 74.6 | 23.3 | 1.9 | 0.1 | 0.1 | 肉たんぱく質の規則（ミオシン・アクチン・コラーゲン）。目標料理は「鶏むねのソテー」 |
| `beef` | 牛ひき肉 | ground beef | 11089 うし/ひき肉/生（塊肉は部位で成分差が大きいので未採用） | 61.4 | 17.1 | 21.1 | 0.3 | 0.2 | 肉の規則を共有。焼く→煮る の順番の違い（非可換性）を試す材料。今回の目標料理には入れていない |
| `gelatin` | ゼラチン | — | 11198 ぶた/ゼラチン | 11.3 | 87.6 | 0.3 | 0 | 0.7 | 牛乳ゼリー（冷やすとゲル化、温めると融ける＝可逆） |
| `vinegar` | 酢（穀物酢） | vinegar | 17015 穀物酢 | 93.3 | 0.1 | 0 | 2.4 | 0 | pH を下げる操作の代表（乳の凝集、卵白泡の安定） |
| `lemon_juice` | レモン汁 | lemon juice | 07156 レモン/果汁/生 | 90.5 | 0.4 | 0.2 | 8.6 | 0 | 酢と同じく pH を下げる。卵白泡の安定に使われる |
| `baking_powder` | ベーキングパウダー | baking powder | 17084 ベーキングパウダー | 4.5 | Tr | 1.2 | 29.0 | 17.3 | パンケーキの膨化（濡れたときと加熱時に CO2） |
| `yeast` | パン酵母（乾燥） | yeast | 17083 パン酵母/乾燥 | 8.7 | 37.1 | 6.8 | 43.1 | 0.3 | 操作「発酵」を持つため。今回の目標料理（パンケーキはベーキングパウダー）には使わない |

## 3. 操作

焼く・炒める・蒸す・煮る・揚げるは、どれも「加熱」を**媒体**（空気・金属＋油・蒸気・水・油）で特殊化したものとして扱う。媒体と「表面が湿っているか」が表面の最高温度を決める（R-W02: 湿った表面は沸点で頭打ち）。これで「煮る・蒸すでは焼き色が付かない」が規則から出る。

| id | 操作 | パラメータ | メモ |
|---|---|---|---|
| `mix` | 混ぜる | strength: 弱（さっくり）/中/強, time: min | 均一化。小麦粉＋水ではグルテンが形成・発達する（R-G01, R-G02） |
| `whisk` | 撹拌・泡立て | time: min, T_medium: ℃ | 空気を入れる。卵白・生クリームで泡。加熱中の撹拌（スクランブル）もこれ |
| `knead` | こねる | time: min | グルテン発達。今回の目標料理では使わない（パン用） |
| `soak` | 浸す（浸漬） | T_medium: ℃, time: min | 米の吸水（R-S06）、ゼラチンの膨潤（R-J01） |
| `heat` | 加熱（基本形） | medium: 空気/金属+油/蒸気/水/油, T_medium: ℃, time: min, stirring: bool, lid: bool | 以下はこの特殊化 |
| `bake` | 焼く・炒める | medium: 金属+油（フライパン）/空気（オーブン）, T_medium: ℃, time: min, stirring: bool | 表面が乾くと100℃を超え、メイラードが起きうる |
| `steam` | 蒸す | T_medium: ℃（蓋のずらしで 85〜100）, time: min | 表面・中心とも100℃を超えない。茶碗蒸しは85〜90℃に保つ（R-E15） |
| `simmer` | 煮る・茹でる・炊く | T_medium: ℃（≦100）, time: min, water_ratio: 対食材質量比 | 表面は沸点を超えない（R-W02）。炊飯は吸水しきって水が無くなるまで |
| `deep_fry` | 揚げる | T_oil: ℃（160〜190）, time: min | 表面は乾いてクラスト、中心は100℃を超えない（R-F01） |
| `chill` | 冷やす | T_medium: ℃, time: min | ゼラチンのゲル化、でんぷんの老化、脂肪の結晶化 |
| `rest` | 寝かせる | T_medium: ℃, time: min | グルテンの緩み、ベーキングパウダー第1段の CO2、吸水。温度を上げない時間経過 |
| `ferment` | 発酵 | T_medium: ℃, time: min | 酵母による CO2。今回の目標料理では使わない |
| `poach` | 卵を割って湯に落とす | T_medium: ℃（≦100）, time: min, vinegar_pct: 湯に対する酢（%）, salt_pct: 湯に対する塩（%） | 2026-09-27 追加。煮るの特殊化で、割った卵がじかに湯にふれる形（drop）。落とした時点の湯温と酢・塩で卵白のまとまりが決まる（R-E21, R-E22） |

## 4. 状態変数

- `scope`: mixture = 鍋の中の混合物全体、component = 混合物の中の成分ごと（卵白・卵黄・でんぷん・肉 …）
- 出典が温度しきい値でしか語っていないもの（凝固・泡・褐変）は、根拠のない連続量にせず**段階（ordinal）**にした
- `t_at_T`（温度履歴）を持つのは、到達温度だけでは決まらない現象があるため（温泉卵 R-E08、炊飯 R-S04、コラーゲン R-P03、ショ糖の熱分解 R-C03）

| id | 名前 | 型 | 単位・段階 | scope | メモ |
|---|---|---|---|---|---|
| `T_core_max` | 中心の到達温度 | continuous | ℃ [-20, 200] | mixture | 凝固・糊化の多くは到達温度で決まるが、それだけでは足りない（t_at_T を参照） |
| `T_surface_max` | 表面の到達温度 | continuous | ℃ [-20, 250] | mixture | 表面が湿っている間は沸点（大気圧で100℃）を超えない（R-W02）。メイラード・カラメル化は表面で起きる |
| `t_at_T` | 温度履歴（温度ごとの保持時間） | history | min（温度帯ごと） [0, 1440] | mixture | 温泉卵（R-E08）、炊飯（R-S04）、コラーゲン（R-P04）、ショ糖の熱分解（R-C03）は時間に依存する。スカラー1つでは表せない |
| `water` | 水分量 | continuous | g/100g [0, 100] | mixture | — |
| `fat` | 脂質量 | continuous | g/100g [0, 100] | mixture | — |
| `protein` | たんぱく質量 | continuous | g/100g [0, 100] | mixture | — |
| `T_serve` | 食べるときの温度 | continuous | ℃ [-20, 100] | mixture | 調理後の状態ではなく提供条件。§11 の「温度」の層に対応する |
| `mass_ratio` | 元の質量に対する比 | continuous | - [0, 5] | mixture | 炊飯で増え（約2.2倍）、炒め玉ねぎで減る（0.4〜0.2） |
| `sugar_conc` | 糖濃度（溶けている糖） | continuous | g/100g（糖液では %） [0, 100] | mixture | 炒め玉ねぎでは糖の総量は減るのに重量あたりの濃度は上がりうる（R-O01, R-O02） |
| `salt_conc` | 食塩濃度 | continuous | g/100g [0, 30] | mixture | — |
| `pH` | pH | continuous | - [2, 9] | mixture | — |
| `egg_dilution` | 卵液の卵濃度 | continuous | 卵の体積/全体積（%） [0, 100] | mixture | 茶碗蒸しは約25%（R-E16）。凝固温度を上げる要因 |
| `egg_white_stage` | 卵白たんぱく質の凝固段階 | ordinal | 0:生（流動） / 1:とろみ・白濁開始 / 2:やわらかい固体 / 3:固いゲル（オボアルブミン凝固） | component | — |
| `egg_yolk_stage` | 卵黄の凝固段階 | ordinal | 0:生（流動） / 1:とろみ / 2:凝固（しっとり） / 3:ほろほろ・粉状 | component | — |
| `egg_gel_stage` | 卵液（希釈・混合）全体のゲル段階 | ordinal | 0:液 / 1:とろみ / 2:やわらかいゲル / 3:固いゲル / 4:離水・す立ち | mixture | 希釈・糖・塩で段階の境目の温度がずれる |
| `gel_structure` | ゲルの形 | categorical | なし / 連続ゲル / 小片（カード） / 外側連続・内側半流動 | mixture | 撹拌しながら固めたか・静置で固めたかで決まる。スクランブルエッグとオムレツ・プリンの違いはここ |
| `porosity` | す（加熱中の気化でできた空洞） | ordinal | 0:なし / 1:少し / 2:多い | mixture | — |
| `milk_casein` | カゼインの状態 | categorical | 分散 / 凝集（凝乳） | component | — |
| `milk_whey_denatured` | 乳清たんぱく質の熱変性 | ordinal | 0:未変性 / 1:変性 | component | — |
| `fat_phase` | 脂質の相状態 | categorical | 固体（結晶多い） / 可塑（半固体） / 液体（融解） / O/W乳化（乳・卵黄） / 部分合一ネットワーク（ホイップ） / 分離 | component | — |
| `air_frac` | 気泡の体積割合（オーバーラン） | continuous | %（泡立て前体積に対する増加） [0, 800] | mixture | 値の出典は今回集めていない。目標料理では段階（なし・あり）でしか書いていない |
| `foam_stage` | 泡の段階 | ordinal | 0:泡なし / 1:粗い泡 / 2:やわらかい角 / 3:しっかりした角 / 4:泡立てすぎ（分離・バター化・ぼそぼそ） | mixture | — |
| `starch_gel` | でんぷんの糊化度 | continuous | 0〜1（または %） [0, 1] | component | 炊飯直後で約95%という測定値がある（R-S07） |
| `starch_retro` | でんぷんの老化 | ordinal | 0:なし / 1:進行 / 2:著しい | component | — |
| `gluten` | グルテン形成 | ordinal | 0:なし（乾いた粉） / 1:形成（水と接触） / 2:発達（混ぜる・こねる） / 3:強く発達 | component | — |
| `gluten_relaxed` | グルテンの緩み（寝かせ） | ordinal | 0:張っている / 1:緩んでいる | component | — |
| `maillard` | メイラード反応の進み | ordinal | 0:なし / 1:薄い焼き色 / 2:きつね色 / 3:濃い褐色 | mixture（主に表面） | — |
| `caramel` | 糖の熱分解（カラメル化）の進み | ordinal | 0:なし（無色の糖液・結晶） / 1:淡い色 / 2:褐色（カラメル） / 3:焦げ（熱分解） | mixture | — |
| `syrup_stage` | 糖液の段階（煮詰め） | ordinal | 0:溶液 / 1:糸 / 2:ソフトボール / 3:ファームボール / 4:ハードボール / 5:ソフトクラック / 6:ハードクラック / 7:透明な融液 / 8:褐色の融液 | mixture | — |
| `onion_sulfur` | 玉ねぎの刺激臭成分（揮発性の硫黄化合物）の残り | ordinal | 0:ほぼ消失 / 1:減少 / 2:生のまま | component | — |
| `cell_wall` | 野菜の細胞壁（ペクチン）の状態 | categorical | 生 / 硬化（PME） / 軟化 / 崩壊（煮崩れ） | component | — |
| `meat_myosin` | ミオシン変性 | ordinal | 0:未変性 / 1:変性 | component | — |
| `meat_actin` | アクチン変性 | ordinal | 0:未変性 / 1:変性 | component | — |
| `meat_collagen` | コラーゲンの状態 | ordinal | 0:未変性 / 1:変性・収縮 / 2:ゼラチン化（溶解） | component | — |
| `meat_myoglobin` | ミオグロビン変性（赤→灰褐色） | ordinal | 0:未変性 / 1:変性開始 / 2:変性 | component | — |
| `meat_water_loss` | 肉からの水分流出 | continuous | % of 生重量 [0, 50] | component | 数値の出典は今回集めていない。60℃で急に出る（R-P02）、鶏むね70℃で乾く（R-P05）の定性のみ |
| `gelatin_state` | ゼラチンの状態 | categorical | 乾燥 / 膨潤 / 溶解（ゾル） / ゲル / 分解（酵素） | component | — |
| `gelatin_conc` | ゼラチン濃度 | continuous | g/100g [0, 10] | mixture | — |
| `co2` | 生地中の CO2（膨化） | ordinal | 0:なし / 1:第1段（濡れて発生） / 2:第2段（加熱で発生） / 3:発酵で発生 | mixture | — |
| `yeast_alive` | 酵母の生死 | categorical | 活性 / 休眠 / 死滅 | component | — |

## 5. 規則

列: 操作 / 対象 / 条件 / 状態の変化 / 出典の数値（原文どおり）/ 出典 / 確認 / 確かさ / 注。出典の詳細は §8。

### 5.1 卵（23）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-E01 | heat | egg_white | T ≧ 60℃（140°F） | egg_white_stage 0→1（オボトランスフェリンが固まり始める） | Ovotransferrin begins setting at 140°F/60°C | soc_temps | 本文確認 | 高 | オボトランスフェリンは卵白たんぱく質の約12%。検索抜粋では 62℃ という値もあった |
| R-E02 | heat | egg_white | T ≧ 63℃ でとろみ、≧ 65℃ でやわらかい固体 | egg_white_stage 1→2 | 145°F/63°C -- Egg whites begin to thicken / 150°F/65°C -- Egg whites become a tender solid | soc_temps | 本文確認 | 高 | 凝固開始の値は出典で 55〜57℃（kajiya、出典記載なし）〜63℃ と幅がある（衝突 C1） |
| R-E03 | heat | egg_white | T ≧ 80℃ | egg_white_stage 2→3（オボアルブミンが凝固） | ovalbumin ... doesn't coagulate until the temperature reaches 80°C（オボアルブミンは卵白の54%） | soc_sousvide・soc_temps・mcgee | 本文確認 | 高 | — |
| R-E04 | heat | egg_white | 61〜84℃ | 卵白たんぱく質全体が凝固する温度範囲 | albumen of eggs coagulate at temperatures ranging from 141.8° to 183.2°F (61° to 84°C) | soc_sousvide | 本文確認 | 中 | R-E01〜E03 と同じ現象を範囲で言ったもの |
| R-E05 | heat | egg_yolk | T ≧ 65℃ でとろみ、≧ 70℃ で凝固 | egg_yolk_stage 0→1→2 | The yolk begins to thicken around 65°C and sets around 70°C（McGee p.85）/ 158°F/70°C -- Egg yolks set | soc_sousvide・soc_temps・mcgee | 本文確認 | 高 | — |
| R-E06 | heat | egg_yolk | 80〜90℃ | egg_yolk_stage 2→3（固ゆで卵のほろほろ） | Further heating to around 80-90°C produces the crumbly texture typical of hard boiled eggs | soc_sousvide | 本文確認 | 中 | — |
| R-E07 | heat | egg_whole（撹拌した全卵、希釈なし） | T ≧ 73℃ | egg_gel_stage → 2 以上 | 165°F/73°C -- Whole egg sets | soc_temps | 本文確認 | 中 | 家庭向けサイトでは「溶き卵は70℃で固まり始め、73℃でとろとろ、75℃でしっかり」（omelet_web、抜粋のみ・出典記載なし）。衝突 C2 |
| R-E08 | heat | egg_whole（殻付き、一定温度の湯） | 湯温 65/68/70℃ で保持 | 同じ到達温度でも保持時間で凝固が進む。70℃では30分で卵白の流動性が消える。65・68℃では卵黄の高さが保持時間とともに増す | 中心が湯温近くに達するまで 65℃:30分、68℃:28分、70℃:27分。70℃では30分で卵白の流動性が消失 | tatsu2019 | 抄録確認 | 高 | 状態は到達温度だけでなく温度履歴 t_at_T を持つ必要がある根拠 |
| R-E09 | heat | egg + milk（+ sugar） | 卵を牛乳で薄める | 凝固（とろみ開始）温度が上がる。カスタードは 80〜85℃で凝固 | custard (egg, milk, sugar) will coagulate between 80°C and 85°C (176–185°F) / 卵1個+牛乳1カップ+砂糖大さじ1 では 175–180°F まで増粘が始まらない（薄めない卵は約150°F） | custard_textbook・custard_123・mcgee | 抜粋のみ | 中 | custard_textbook は取得を試みたが 403。値は検索抜粋。McGee 第2章にも同趣旨の記述があるはずだが本文未確認 |
| R-E10 | mix | egg + sugar | 砂糖を加える | 凝固温度がさらに上がる。牛乳の効果と足し合わさる | Sugar raises the coagulation temperature further ... milk and sugar effects are additive | custard_123 | 抜粋のみ | 中 | 何℃上がるかの数値は見つけていない |
| R-E11 | heat | egg_white / egg_yolk + sugar | 砂糖 10〜30% 添加 | ゲル強度が下がる（卵白で最も大きい） | 砂糖添加の影響は卵白で最も大きくゼリー強度が著しく減少した | awatsu1982 | 抄録確認 | 高 | — |
| R-E12 | heat | egg_white / egg_yolk + salt | 食塩 0.5〜2.5% 添加 | 凝固力（ゲル化）が促進される。卵白は 0.5% で著しく、1.0% で最高。卵黄は 1.0% まではあまり変わらず 1.5〜2.0% で著しく促進 | 抄録の記述どおり | awatsu1982 | 抄録確認 | 高 | — |
| R-E13 | heat | egg_white / egg_yolk / egg_whole + salt | 食塩量を増やす | 凝固温度は上がる。卵白に 1.5% 以上で著しく上がる | 凝固温度は卵白,卵黄,全卵共食塩量の増加と共に上昇し,特に卵白に食塩1.5%以上添加した場合には著しく上昇した | awatsu1982 | 抄録確認 | 高 | R-E12（凝固力は上がる）と向きが逆に見える。同じ論文の中で「凝固力」と「凝固温度」は別の指標。衝突 C5 |
| R-E14 | mix | egg_white + acid | pH を下げる | 卵白の凝固が促進される（ポーチドエッグに酢を入れる理由） | — | mcgee | 未確認 | 低 | 書籍第2章の内容として知っている範囲。数値なし。推定 |
| R-E15 | steam | 希釈卵液（茶碗蒸し・プリン） | 蒸し器内を 85〜90℃ に保ち沸騰させない | porosity（す）を抑える。高すぎると す立ち・硬くなる | 蒸し器内の温度を85～90℃に保ち、卵液の沸騰を防ぐことによって、“す”の発生を最小限に抑える | chawan_web | 抜粋のみ | 中 | 仕組み（卵液中の水の気化で空洞ができる）は複数の家庭向けサイトで一致。論文での確認はしていない |
| R-E16 | mix | egg_whole + dashi | 卵:だし = 1:3（体積） | egg_dilution 約25%。やわらかく固まる | 卵とだし汁の容量の黄金比は「1：3」／卵液の体積濃度を約25% | chawan_web | 抜粋のみ | 中 | — |
| R-E17 | steam | カスタードプリン・茶碗蒸し | 85℃ 36分 または 90℃ 12分 | egg_gel_stage → 2 | 85℃で36分蒸し上げる／90℃で12分蒸し上げる | kajiya | 本文確認 | 低 | ページに出典の記載がない。温度と時間の組の例として残す |
| R-E18 | whisk | egg_white | 砂糖・酸・脂肪の有無 | 砂糖は泡立て時間を延ばすが泡を安定させる。酸（酒石酸など）は pH を下げて安定させる。脂肪（卵黄を含む）は泡立ちを妨げる | even 0.5 wt% egg yolk will destroy the foaming characteristics of egg protein system | eggfoam_isu・eggfoam_yolk | 抜粋のみ | 中 | — |
| R-E19 | heat | 撹拌が不十分な全卵 | 卵白と卵黄が分かれたまま加熱 | 凝固温度が違うので固まり方にむらが出る | 卵の凝固温度は黄身と白身で異なり、しっかり混ぜなければ固まり方にムラが出来ます | omelet_web | 抜粋のみ | 中 | R-E01〜E05 から導ける帰結 |
| R-E20 | heat | 卵液 | 加熱中に撹拌し続ける（stirring=true）／撹拌しない | 撹拌あり → gel_structure=小片（カード）。撹拌なし → 連続ゲル | — | — | 未確認 | 低 | 推定。スクランブルエッグとオムレツ・プリンの違いを状態で書くために置いた。出典を探していない |
| R-E21 | poach | egg_whole（割った卵、溶いていない） | 湯温 80〜85℃（鍋底から小さな泡、沸騰させない）に割り入れる | 卵白が散る前に固まり卵黄を包んでまとまる（egg_white_cohesion=まとまる）。沸騰（100℃）では対流で卵白がちぎれる（ばらける）。70℃では固まりきらない。3〜4分で卵白は完全に固まり、卵黄の中心は 65℃未満 | Bring to a temperature of 80–85°C ... no rolling simmer. At 100°C, the turbulence tears the white apart before it sets. At 70°C, the white never fully coagulates. / ... (3–4 minutes) ... keeping the center of the yolk below 65°C（terumimorita）／「沸騰させると水の対流が生じ白身が崩れてしまう」「85度を目安に…五分間」（travelingfoodlab）／The egg is cooked at 80C for 4 minutes（soc_poach） | terumimorita・travelingfoodlab・soc_poach | 本文確認 | 低 | 料理人の記事とレシピ。論文では確認していない。湯温は出典によって 62℃〜沸騰までばらつく（C13） |
| R-E22 | poach | egg_white（湯に酢・塩を加える） | 湯に酢・塩を加える（例: ワインビネガー湯量の3%、穀物酢・米酢なら4.5%） | 卵白の凝固が速まり湯の中で飛び散らない。ただし表面に不規則な膜・ちぎれ（egg_white_cohesion=まとまる（表面に膜・ちぎれ）） | adding vinegar and salt "does speed coagulation, but also produces shreds and an irregular film over the egg surface"（McGee、soc_poach の引用）／〈酢や塩を加えることで早く固まるが卵の表面に不規則な膜が生じる〉（『マギーキッチンサイエンス』p88、travelingfoodlab の引用）／「酢が入った湯に卵を入れるとすばやく卵白が固まり、湯の中で飛び散ることがない」（kyounoryouri） | soc_poach・travelingfoodlab・kyounoryouri・mcgee | 本文確認 | 中 | McGee の本文は開いておらず、英語版・日本語版の2つの引用で確認。何℃・何分速まるかの数値はない。R-E14（未確認）の内容をこの出典で確かめた形 |
| R-E23 | heat | egg_white（オボアルブミン） | pH を下げる（pH 5〜9 で比較） | オボアルブミンの熱安定性が下がる（pH が高いほど安定）。水中 5% で変性温度 80.22℃ | The Td of OVA and LYZ in water (5% w/v, 5 °C/min) were 80.22 °C and 77.46 °C ... OVA thermal stability was improved with increasing pH | wang2025 | 抄録確認 | 高 | 精製たんぱく質の溶液での測定。pH ごとの変性温度の数値は抄録に無いので、段階のしきい値は動かさない |

### 5.2 乳（6）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-D01 | mix | milk + acid（vinegar / lemon_juice） | pH ≦ 4.6 | milk_casein 分散→凝集（カゼインの等電点） | At pH 4.6, which is the isoelectric point of casein, the casein micelles disintegrate and precipitate | casein | 抜粋のみ | 高 | 教科書的な値で、抜粋した複数の出典で一致 |
| R-D02 | heat | milk | 加熱 | 乳清たんぱく質は熱で変性する。カゼインは熱に強い（変性は約120℃から） | casein ... denaturation begins at approximately 120°C, while whey proteins ... can be denatured at high temperatures | casein | 抜粋のみ | 中 | 乳清の変性温度の数値は確認していない（推定 70℃前後） |
| R-D03 | whisk | heavy_cream | 乳脂肪 30% 以上、品温 7.5〜12.5℃ | 脂肪球が部分合一してネットワークを作り気泡を安定させる（fat_phase → 部分合一ネットワーク、foam_stage ↑） | Whipping cream traditionally has a fat content between 30 and 40% / temperature range of 7.5 to 12.5°C recommended（5〜15℃で比較）/ whipping time, overrun, and bubble diameters decreased with increasing temperature | cream2010・cream_overview | 抜粋のみ | 中 | — |
| R-D04 | whisk | heavy_cream | 泡立てすぎ | fat_phase → 分離（バターと液に分かれる）。foam_stage=4 | — | mcgee | 書籍(章) | 中 | 第1章（乳）の内容。何分でそうなるかの数値はない |
| R-D05 | heat | butter | 約32〜35℃ | fat_phase 可塑→液体。明確な融点はなく幅で融ける | butter melts ... typically around 32-35°C / 融け始めは 21〜40℃の間 / 冷蔵では2/3以上の脂肪が固体 | butter | 抜粋のみ | 中 | — |
| R-D06 | heat | 乳脂肪 | -40〜40℃ | 乳脂肪の融解範囲 | Milk fat has a wide melting range, which spans from about −40 to 40°C | butter | 抜粋のみ | 中 | — |

### 5.3 でんぷん・野菜の細胞壁（12）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-S01 | heat | flour（小麦でんぷん）+ 水 | 約 52〜66℃ | starch_gel 0→1（糊化） | Wheat: 59.5-64°C or 52-66°C / peak 61.5°C | starch_gel | 抜粋のみ | 中 | 水分量と測定法で値が変わる |
| R-S02 | heat | rice（米でんぷん）+ 水 | 約 58.9〜82℃（出典で幅） | starch_gel 0→1 | Rice: 68-78°C or 58.9-72.4°C or 66-82°C | starch_gel | 抜粋のみ | 中 | 農水省は「糊化開始 60℃付近」（R-S04）。衝突 C6 |
| R-S03 | heat | potato（じゃがいもでんぷん）+ 水 | 約 55〜66℃ | starch_gel 0→1 | Potato: 55-66°C / peak 63.6°C | starch_gel | 抜粋のみ | 中 | — |
| R-S04 | simmer | rice + water（炊飯） | 糊化は 60℃付近から始まり、完全な糊化には 98℃以上で約20分 | starch_gel → 約1 | 糊化開始温度：60℃付近／完全糊化に必要な加熱：98℃以上で約20分間／温度上昇期 約10分・沸騰期 約5分・蒸し煮期 10〜15分（100℃保持）・蒸らし期 約10分 | maff_rice | 本文確認 | 高 | — |
| R-S05 | simmer | rice + water（炊飯） | 加水量 米の重さの1.5倍（容積の1.2倍）。現代の炊飯器では1.3〜1.4倍 | 炊き上がりは米の重さの 2.1〜2.3倍、飯の水分 約60〜65% | 基準加水量：米の重さの1.5倍（米の容積の1.2倍）／好まれる飯：米の重さの2.2倍前後（2.1～2.3倍）／飯の水分 約60～65% | maff_rice・fooddb | 本文確認 | 高 | 成分表の めし（01088）は水分 60.0 g/100g |
| R-S06 | soak | rice + water | 水温30℃以下で浸漬 | water ↑（吸水率 20〜25%）。30℃は5℃より速い。最低30分、できれば60分、約2時間で飽和 | 吸水率：水温30℃以下のうるち米で20～25％程度／浸漬時間：最低30分、できれば60分／飽和状態到達時間：約2時間 | maff_rice | 本文確認 | 高 | — |
| R-S07 | simmer | rice + water | 加水比を変える | 炊飯直後の糊化度は加水比によらず約95%。1.2倍未満では沸騰が不十分。官能評価は1.3〜1.4倍が高い | 飯の糊化度は炊飯直後には加水比の多少にかかわらず95%前後を示した | kainuma1987 | 抄録確認 | 高 | — |
| R-S08 | chill | 糊化したでんぷん | 冷やす・時間が経つ | starch_retro ↑（老化して硬くなる）。0〜4℃付近・水分30〜60%で最も速い | 老化は、水分含量30～60％、0～4℃付近で最も速く進行 | — | 未確認 | 中 | 定性（冷えると老化）は複数の解説で一致。数値は検索の要約にしか出ず、一次出典を確認できなかった |
| R-S09 | bake | flour + butter（ルー） | ルーを 130℃ を超えて加熱 | そのルーで作ったソースの粘度が下がる（でんぷんの増粘力が落ちる） | Viscosity and texture parameters of the sauce decreased at heating temperatures of roux over 130°C | roux | 抜粋のみ | 中 | — |
| R-S10 | simmer | ルー + milk（ホワイトソース） | 沸騰まで加熱し、しばらく煮る | starch_gel → 1、とろみが出る。粉臭さを消すには長め（最長30分）に煮る | bring the liquid to a boil ... flour needs to be cooked for longer periods of time (up to 30 minutes) | roux_texts | 抜粋のみ | 低 | 「粉臭さ」は知覚の話なので、状態としては starch_gel と t_at_T だけを使う |
| R-S11 | heat | potato | 50〜70℃ に一定時間置く | cell_wall → 硬化（ペクチンメチルエステラーゼが働く）。その後 80℃以上で長く煮ても煮崩れしにくい。60℃付近に長く置きすぎると柔らかくならない（2時間で生より硬くなることも） | 50～70℃でペクチンメチルエステラーゼを活性化した状態が一定時間続けば、野菜を硬くすることができます | potato_pme | 抜粋のみ | 中 | — |
| R-S12 | simmer | potato | 80℃以上で加熱を続ける | cell_wall → 軟化 → 崩壊（ペクチンが溶け出して煮崩れ） | 加熱するとペクチンが溶け出し、煮崩れが起こります | potato_pme | 抜粋のみ | 中 | 軟化が始まる温度の数値は確認していない |

### 5.4 グルテン（4）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-G01 | mix | flour + water | 水と接触 | gluten 0→1（グリアジンとグルテニンが結びつく）。水がなければ形成しない | Without water, gluten is not formed | gluten | 抜粋のみ | 高 | — |
| R-G02 | mix・knead | flour + water | 混ぜる・こねる時間と強さ | gluten ↑（1→2→3） | — | gluten | 抜粋のみ | 高 | 定性のみ。何分で何段階かの数値はない |
| R-G03 | rest | 生地 | 寝かせる | gluten_relaxed 0→1（弾性が下がる） | Relaxing or resting the dough reduces the elasticity of the dough | gluten | 抜粋のみ | 中 | — |
| R-G04 | mix | パンケーキ生地 | 混ぜすぎ | gluten ↑ で生地が締まる。粉気が少し残る程度で止める | Over mixing develops the gluten ... do not overmix or pancakes will be tough | pancake_web | 抜粋のみ | 低 | レシピサイトの記述。R-G02 の特殊例 |

### 5.5 膨化（3）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-L01 | mix・bake | baking_powder（ダブルアクション） | 濡れる（室温）→ 加熱 | co2 0→1（濡れた時点）→2（加熱時） | Double-acting baking powders work in two phases; once when cold, and once when hot | baking_powder | 抜粋のみ | 高 | 日本の家庭用ベーキングパウダーがダブルアクションかは製品による（未確認） |
| R-L02 | ferment | yeast | 約27℃が最適（30〜35℃で最速との記述もある）。55〜60℃で死滅 | co2 → 3。yeast_alive 活性→死滅（≧55〜60℃） | the optimum temperature is just over 27°C (80°F) / yeast cells die at their thermal death point of 130°F–140°F (55°C–60°C) | yeast | 抜粋のみ | 中 | — |
| R-L03 | bake | パンケーキ生地 | 鉄板 375°F（約190℃） | 表面の maillard ↑、co2 第2段 | The ideal griddle temperature for pancakes is 375°F | pancake_web | 抜粋のみ | 低 | — |

### 5.6 糖（6）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-C01 | heat | sugar（ショ糖） | 約160〜170℃ | caramel 0→2 | Sucrose: 160°C/320°F（Science of Cooking）／Sucrose 170°C (338°F)（McGee p.656 を引く Wikipedia） | soc_temps・wiki_caramel・mcgee | 本文確認 | 高 | 出典で10℃違う。衝突 C4。どちらも「その温度から速く進む」の目安 |
| R-C02 | heat | 果糖・ブドウ糖・麦芽糖 | 糖の種類ごとのしきい値 | caramel 0→2 | Fructose 110°C（SoC）/105°C（McGee）、Glucose 160°C（SoC）/150°C（McGee）、Maltose 180°C（両方） | soc_temps・wiki_caramel | 本文確認 | 高 | 上白糖は転化糖を少し含む（未確認）ので、グラニュー糖より低い温度で色づく可能性がある（推定） |
| R-C03 | heat | sugar（ショ糖の結晶） | 加熱 | ショ糖は熱力学的には融けず、熱分解で結晶が崩れる（見かけの融解）。熱分解は時間をかければ低い温度でも始まる | The loss of crystalline structure in sucrose ... has been shown to be due to the kinetic process of thermal decomposition (termed apparent melting) | schmidt2011 | 抜粋のみ | 高 | カラメル化を「温度しきい値」でなく「温度×時間の反応」として持つべき根拠 |
| R-C04 | bake | sugar（グラニュー糖、乾いたまま） | オーブン 300〜325°F（約150〜163℃）で約2時間、30分ごとに混ぜる | 結晶のまま色づく（caramel 0→1） | roast at 325°F ... stirring well once every 30 minutes, until it darkens to a sandy tan ... about 2 hours | roasted_sugar | 抜粋のみ | 中 | R-C03 の料理側の例 |
| R-C05 | simmer | sugar + water（糖液の煮詰め） | 糖液の沸点（＝濃度） | syrup_stage が温度とともに上がる | 糸 110〜112℃(80%)／ソフトボール 112〜116℃(85%)／ファームボール 118〜120℃(87%)／ハードボール 121〜130℃(90%)／ソフトクラック 132〜143℃(95%)／ハードクラック 146〜154℃(99%)／透明な液 160℃(100%)／褐色の液 170℃(100%)／焦げ 177℃(100%) | candy_stages | 抜粋のみ | 中 | 水がある間は糖液の温度は濃度で決まる沸点に縛られる。水を飛ばしきらないとカラメル化の温度に届かない |
| R-C06 | heat | 糖・食品全般 | 180℃超 | 熱分解（焦げ）。caramel → 3 | above 180°C / 355°F a different set of reactions occur: pyrolysis, also known as burning / Burnt sugar 177°C | mc_maillard・candy_stages | 本文確認 | 中 | — |

### 5.7 メイラード反応（5）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-M01 | bake・deep_fry | 糖とアミノ酸（たんぱく質）を含む食品の表面 | 約140〜165℃ | maillard ↑（速く進む） | typically proceeds rapidly from around 140 to 165°C (280 to 330°F) / 285°F (140°C) -- Browning or the Maillard Reaction begins | mc_maillard・soc_temps | 本文確認 | 高 | — |
| R-M02 | simmer・steam | 湿った食品 | 表面が湿っている | 表面温度が沸点を超えないため、メイラードはほとんど進まない | as long as the food is very wet, its temperature won't climb above the boiling point of water ... dryness and temperature are the key controls | mc_maillard | 本文確認 | 高 | — |
| R-M03 | heat | 同上 | pH が高い（アルカリ） | maillard が速くなる。pH 6〜8 で最適との記述 | Adding baking soda ... raises the food's pH (making it more alkaline), which also helps / Optimal browning takes place at pH 6–8 | mc_maillard・maillard_overview | 本文確認 | 中 | pH 6〜8 の値は抜粋のみ |
| R-M04 | heat | 同上 | 140℃より低い温度で長時間 | maillard は遅いが進む | Browning can still occur at lower temperatures, although at a slower rate | maillard_overview | 抜粋のみ | 中 | R-M01 のしきい値モデルと衝突する。衝突 C8 |
| R-M05 | heat | 同上 | 水分活性 aw 0.6〜0.7 | maillard が最も速い | the reaction peaking at aw 0.6–0.7 | maillard_overview | 抜粋のみ | 中 | 状態変数に水分活性を持っていない。water からの換算は未定 |

### 5.8 揚げる（1）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-F01 | deep_fry | 水分を含む食品（potato など） | 油 160〜180℃ | 表面は乾いてクラスト（T_surface_max > 100、maillard ↑）。中心は100℃を超えない（water は中心に残る） | food is in direct contact with very hot oil at 160–180°C ... The product temperature (except for the crust region) does not exceed 100°C during frying | frying | 抜粋のみ | 高 | 複数の総説で一致 |

### 5.9 玉ねぎ（3）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-O01 | bake | onion（長時間炒め） | 褐変するまで炒める（重量が元の40%・20%程度まで減る） | water ↓、onion_sulfur → 0（刺激臭が消える）、甘く香ばしい香り、maillard/caramel ↑。ブドウ糖・果糖・遊離糖の総量は減る | 長時間炒めると水分の蒸発とともに色, 味, 香りが変化し, 刺激臭も消失 ... グルコース, フルクトースおよび遊離糖総量が減少 ... 糖含有量と, 官能評価による甘味の強さとは対応しなかった | tamaki2003 | 抄録確認 | 高 | 重量 40%・20% は抄録の要約から。原文で要確認 |
| R-O02 | heat | onion | 加熱 | 遊離糖（生で約6%）は増えず、変わらないか減る。硫黄化合物は減り、糖の分解で甘い香りの成分ができる。甘く感じるのは水分蒸発による濃縮と組織の軟化と考えられる（著者の考察） | 生タマネギ中に6%程度存在する遊離糖の含量は加熱により変化しないか、あるいは、減少する傾向にあり、新たな遊離糖の生成はない | tokitomo1993 | 抄録確認 | 高 | 「甘く感じる」は知覚の層の話。状態としては sugar_conc（重量あたり）と onion_sulfur を渡すだけにする |
| R-O03 | bake | onion | 炒めて褐変 | 褐変は糖とアミノ酸のメイラードが主で、温度が上がるとカラメル化も加わる | the heat breaks down their cellular structure, releasing sugars and amino acids, which then react with each other, forming the Maillard products | — | 未確認 | 低 | 検索で出たのは飲食店のブログのみ。メイラードとカラメル化の割合は分からない。衝突 C7 |

### 5.10 ゼラチン（6）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-J01 | soak | gelatin + water | 10〜25℃ で 30〜60分 | gelatin_state 乾燥→膨潤 | 膨潤時間：30-60分／膨潤温度：10-25℃ | nitta | 本文確認 | 高 | — |
| R-J02 | heat | gelatin（膨潤済み） | 50〜60℃（直接溶かす場合は 60〜70℃ で 15〜20分） | gelatin_state → 溶解（ゾル） | 溶解温度：50-60℃／直接溶解法：60-70℃、15-20分 | nitta | 本文確認 | 高 | — |
| R-J03 | heat | gelatin（溶解後） | 高温で長く置く（50〜80℃ で保存） | 粘度・ゲル強度が時間とともに下がる | 加熱により経時的に劣化し、数値が低下していく | nitta | 本文確認 | 高 | 沸騰させると固まらなくなる、という家庭向けの言い方はこの規則の強い版（未確認） |
| R-J04 | chill | gelatin（溶解） | ゲル化温度より下げる | gelatin_state ゾル→ゲル。ゲル化温度は融解温度より低い。濃度が上がると両方上がる。ブルームが上がると融解温度は下がりゲル化温度は上がる | Melting temperatures were higher than gelling temperatures, and both increased with increasing concentration at pH from 3 to 6 | ijfp2007 | 抜粋のみ | 中 | — |
| R-J05 | chill・heat | gelatin | 家庭の濃度（2〜4%） | 約5〜10℃で固まり、約20〜25℃で融ける（可逆） | 溶けたゼラチンは5～10℃で固まります。ゼリー用のゼラチンは約20～25℃で溶ける／使用するゼラチン濃度は、完成時の2～4％ | gelatin_home | 抜粋のみ | 低 | 10%ゲルで融点 27〜32℃という値もある（特許の抜粋）。濃度で変わるので R-J04 と矛盾はしない |
| R-J06 | mix | gelatin + 生のパイナップル等 | たんぱく質分解酵素を含む生の果物 | gelatin_state → 分解（固まらない）。果物を加熱すると酵素が失活して固まる | パイナップルに含まれるブロメラインというタンパク質分解酵素がゼラチンを分解 | pineapple | 抜粋のみ | 中 | パイナップルは食材リストに入れていない。操作の順番（加熱→混ぜる／混ぜる→加熱）で結果が変わる例として残す |

### 5.11 肉（5）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-P01 | heat | chicken / beef | ミオシン 40〜60℃、コラーゲン 53〜63℃、アクチン 66〜73℃ | meat_myosin 0→1、meat_collagen 0→1（変性して収縮）、meat_actin 0→1。硬さは筋原線維たんぱく質の変性で増す | myosin denaturing at 40-60°C and actin at 66-73°C. Collagen denaturation occurs at temperatures between 53 and 63°C, followed by collagen fiber shrinkage | tornberg2005 | 抜粋のみ | 高 | 総説。抜粋のみだが値は他の解説とも整合 |
| R-P02 | heat | chicken / beef | 50℃ で白濁、60℃ で肉汁が急に出る・ミオグロビン変性開始 | meat_myoglobin 0→1、meat_water_loss ↑ | 120°F/50°C -- Meat develops a white opacity / 140°F/60°C -- Red myoglobin begins to denature / 140°F/60°C -- Meat suddenly releases lots of juice | soc_temps | 本文確認 | 中 | — |
| R-P03 | simmer | 結合組織の多い肉 | 70℃（160°F）以上で長時間、湿った加熱 | meat_collagen 1→2（ゼラチンとして溶ける） | 160°F/70°C -- Connective tissue collagen begins to dissolve to gelatin / slowly heated to temperatures between 70°C and 82°C, it breaks down into gelatin | soc_temps・tornberg2005 | 本文確認 | 中 | 何時間かかるかの数値は確認していない。時間依存 |
| R-P04 | heat | chicken（むね） | 70℃（158°F） | meat_water_loss ↑（鳥のむね肉が乾く） | 158°F/70°C -- Breast meat in birds gets dry | soc_temps | 本文確認 | 中 | "dry" は知覚寄りの言葉。状態としては水分流出として扱う |
| R-P05 | heat | chicken / beef | 安全上の最低中心温度 | 状態変化ではなく制約。鶏肉 165°F（74℃）、牛ステーキ 145°F（63℃）＋3分休ませる、牛ひき肉 160°F（71℃） | poultry 165°F / steaks, chops, roasts 145°F + rest 3 minutes / ground beef 160°F | fsis | 抜粋のみ | 高 | 公的機関の基準。℃は換算（出典の本文は 403 で取得できず） |

### 5.12 水・加熱媒体（3）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-W01 | simmer・steam | 水・蒸気 | 大気圧 | 媒体の温度は100℃が上限 | 物理定数 | mc_maillard | 本文確認 | 高 | — |
| R-W02 | heat | 湿った食品 | 表面に水がある間 | T_surface_max は沸点を超えない。高温の乾いた加熱（焼く・揚げる）で表面が乾いてはじめて100℃を超える | only high-heat cooking techniques can dry out the food enough to raise the temperature sufficiently | mc_maillard | 本文確認 | 高 | 焼く・蒸す・煮る・揚げるを1つの「加熱」にまとめる根拠 |
| R-W03 | steam | 蒸し器 | 蓋をずらす・火を弱める | 庫内を 85〜90℃ に下げられる | 蒸し器内の温度を85～90℃に保ち | chawan_web | 抜粋のみ | 中 | — |

### 5.13 酸（1）

| id | 操作 | 対象 | 条件 | 状態の変化 | 出典の数値 | 出典 | 確認 | 確かさ | 注 |
|---|---|---|---|---|---|---|---|---|---|
| R-A01 | mix | vinegar / lemon_juice | 加える | pH ↓（酢 約2.4〜3.0、レモン汁 約2.0〜2.6） | — | — | 未確認 | 低 | pH の値は推定。成分表には pH がない。R-D01・R-E14・R-E18・R-M03 に効く |

## 6. 目標料理の完成時の状態

同じ状態変数で書いた。各値の「根拠」は規則 id・推定・料理の定義のどれか。`process_ref` は状態を書くための参考手順で、計算の入力ではない。流儀で定義が分かれる料理（C9）があるので、値は1点ではなく範囲で書いたものが多い。

### スクランブルエッグ（`scrambled_eggs`）

- 食材: egg_whole・milk（任意）・butter・salt
- 参考手順: 卵＋牛乳を混ぜる → フライパン（バター）で加熱しながら撹拌

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `T_core_max` | 70〜75℃ | R-E07 と omelet_web（衝突 C2） |
| `egg_gel_stage` | 1〜2（とろみ〜やわらかいゲル） | R-E07 |
| `gel_structure` | 小片（カード） | R-E20（推定） |
| `egg_white_stage` | 2 | R-E02（65℃で やわらかい固体、80℃未満） |
| `egg_yolk_stage` | 1〜2 | R-E05 |
| `water` | 約75 g/100g（全卵の値からほぼ減らない） | 推定 |
| `fat_phase` | 液体（バター融解） | R-D05 |
| `maillard` | 0 | 料理の定義（焼き色を付けない流儀）。付ける流儀もある（衝突 C9） |
| `porosity` | 0 | 推定 |

### オムレツ（プレーン）（`omelet`）

- 食材: egg_whole・butter・salt
- 参考手順: 溶き卵を高温のフライパンで短時間、外側を固めて中を半熟で包む

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `T_core_max` | 内側 70〜73℃ 前後、外側はそれ以上 | 推定（R-E07） |
| `egg_gel_stage` | 外側 2〜3、内側 1〜2 | 推定 |
| `gel_structure` | 外側連続・内側半流動 | 料理の定義／R-E20（推定） |
| `maillard` | 0〜1 | 料理の定義（焼き色は付けないのが仏式の基本とされるが未確認） |
| `fat_phase` | 液体（バター融解） | R-D05 |

### プリン（カスタードプディング、蒸し／湯煎焼き）（`custard_pudding`）

- 食材: egg_whole・egg_yolk（任意）・milk・sugar
- 参考手順: 卵＋牛乳＋砂糖を混ぜる → 型に入れ蒸す（または湯煎焼き） → 冷やす。カラメルは別に作って底に敷く

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `egg_dilution` | レシピ依存（未確認） | — |
| `sugar_conc` | 約10%（推定、レシピ依存） | 推定 |
| `T_core_max` | 80〜85℃ | R-E09 |
| `egg_gel_stage` | 2（型から出して形を保つ連続ゲル） | R-E09 |
| `gel_structure` | 連続ゲル | R-E20（推定） |
| `porosity` | 0 | R-E15（庫内 85〜90℃・沸騰させない） |
| `milk_whey_denatured` | 1（推定） | R-D02（温度未確認） |
| `maillard` | 0（本体） | R-M02（湿った加熱） |
| `caramel` | 2（底のカラメル層のみ） | R-C01 |
| `T_serve` | 冷蔵温度（約5℃、推定） | 料理の定義 |

### 茶碗蒸し（`chawanmushi`）

- 食材: egg_whole・dashi・salt
- 参考手順: 卵:だし=1:3 を混ぜて漉す → 85〜90℃で蒸す

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `egg_dilution` | 約25% | R-E16 |
| `salt_conc` | 約0.5〜1%（推定） | 推定（R-E12・E13 の範囲内） |
| `T_core_max` | 80℃台（推定） | R-E09 を類推（牛乳ではなくだしで薄めた場合の数値は未確認） |
| `egg_gel_stage` | 2（プリンよりやわらかい、推定） | R-E16（薄いほどやわらかい） |
| `gel_structure` | 連続ゲル | R-E20（推定） |
| `porosity` | 0 | R-E15 |
| `maillard` | 0 | R-M02 |
| `T_serve` | 温かい（60〜70℃、推定） | 料理の定義 |

### ホワイトソース（ベシャメル）（`white_sauce`）

- 食材: butter・flour・milk・salt
- 参考手順: バターを溶かし小麦粉を炒めてルー → 牛乳でのばし沸騰させて煮る

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `T_core_max` | 約100℃（沸騰） | R-S10・R-W01 |
| `starch_gel` | 1（糊化） | R-S01・R-S10 |
| `gluten` | 0〜1（ほぼ効かない、推定） | 推定 |
| `fat_phase` | 液体（ルーの油脂が でんぷん粒を包んで分散） | mcgee 第11章（書籍(章)） |
| `maillard` | 0（ルーを色づけない） | 料理の定義（ホワイトルー）。R-S09: ルーを130℃超に上げると増粘力が落ちる |
| `water` | レシピ依存（牛乳の量で決まる） | — |
| `milk_casein` | 分散 | R-D01（酸を入れない） |

### カラメル（プリン用カラメルソース）（`caramel_sauce`）

- 食材: sugar・water
- 参考手順: 砂糖＋水を煮詰めて褐色にし、湯を加えて止める

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `T_core_max` | 約160〜170℃（色づけ時） | R-C01・R-C05 |
| `syrup_stage` | 8（褐色の融液）→ 湯でのばす | R-C05 |
| `caramel` | 2 | R-C01 |
| `sugar_conc` | のばした後はレシピ依存 | — |
| `note` | 180℃を超えると焦げ（caramel=3） | R-C06 |

### 炒め玉ねぎ（あめ色）（`sauteed_onion`）

- 食材: onion・vegetable_oil or butter
- 参考手順: 薄切りの玉ねぎを油で長時間炒める

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `water` | 大きく減る | R-O01 |
| `mass_ratio` | 0.4〜0.2 | R-O01（抄録の要約から、要確認） |
| `onion_sulfur` | 0 | R-O01 |
| `sugar_conc` | 重量あたりは上がる／総量は減る | R-O01・R-O02 |
| `maillard` | 2〜3 | R-O01・R-O03（割合は不明） |
| `caramel` | 1〜2（割合は不明） | R-O03（衝突 C7） |
| `cell_wall` | 崩壊 | 推定（R-S12 を野菜一般に類推） |
| `T_surface_max` | 100℃超（水分が飛んだ後） | R-W02 |

### ご飯（白飯）（`steamed_rice`）

- 食材: rice・water
- 参考手順: 洗米 → 浸漬 30〜60分 → 炊飯（米の重さの1.3〜1.5倍の水）→ 蒸らし

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `water` | 約60〜65 g/100g | R-S05（成分表 めし 60.0） |
| `starch_gel` | 約0.95 | R-S07 |
| `T_core_max` | 98〜100℃（約20分保持） | R-S04 |
| `starch_retro` | 0（炊きたて） | R-S08 |
| `maillard` | 0（おこげは除く） | R-M02 |
| `mass_ratio` | 米の重さの 2.1〜2.3倍 | R-S05 |

### パンケーキ（ホットケーキ）（`pancake`）

- 食材: flour・egg_whole・milk・sugar・baking_powder・butter
- 参考手順: 粉類と液体をさっくり混ぜる → 少し寝かせる → 鉄板で両面を焼く

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `gluten` | 1（混ぜすぎない） | R-G02・R-G04 |
| `co2` | 2 | R-L01 |
| `starch_gel` | 1（推定） | 推定（中心は100℃近くまで上がると推定） |
| `egg_gel_stage` | 3（推定） | 推定 |
| `maillard` | 2（表面） | R-M01・R-L03 |
| `T_surface_max` | 約150℃以上（推定） | R-M01 から逆算した推定 |
| `air_frac` | あり（数値は未調査） | R-L01 |

### 牛乳ゼリー（ゼラチン）（`milk_jelly`）

- 食材: milk・sugar・gelatin
- 参考手順: ゼラチンを膨潤 → 温めた牛乳（50〜60℃）で溶かす → 冷やし固める

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `gelatin_conc` | 2〜4% | R-J05 |
| `gelatin_state` | ゲル | R-J04・R-J05 |
| `T_core_max` | 約50〜60℃（溶解時） | R-J02 |
| `T_serve` | 約5〜10℃（冷蔵） | R-J05 |
| `milk_casein` | 分散 | R-D01 |
| `note` | 20〜25℃を超えて置くと融ける（可逆） | R-J05 |

### ホイップクリーム（`whipped_cream`）

- 食材: heavy_cream・sugar
- 参考手順: 冷やした生クリームに砂糖を入れて泡立てる

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `fat` | 30〜40%（元のクリーム） | R-D03 |
| `T_core_max` | 7.5〜12.5℃（泡立て時） | R-D03 |
| `fat_phase` | 部分合一ネットワーク | R-D03 |
| `foam_stage` | 2〜3 | R-D03。4 はバター化（R-D04） |
| `air_frac` | あり（数値は未調査） | R-D03 |

### 温泉卵（`onsen_tamago`）

- 食材: egg_whole（殻付き）
- 参考手順: 65〜70℃の湯に殻ごと約30分

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `T_core_max` | 65〜70℃ | R-E08 |
| `egg_white_stage` | 1〜2（流動性が残る） | R-E02・R-E08 |
| `egg_yolk_stage` | 1〜2 | R-E05・R-E08 |
| `t_at_T` | 中心が湯温に近づいてから数分〜 | R-E08 |
| `note` | 卵黄のほうが卵白より固い、という逆転は R-E01〜E05 の温度差からは直接は出ない。卵白の主成分オボアルブミン（80℃）が固まらないことが効く（推定） | R-E03・R-E05 |

### 鶏むね肉のソテー（`sauteed_chicken`）

- 食材: chicken・vegetable_oil・salt
- 参考手順: 油をひいたフライパンで両面を焼く

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `T_core_max` | ≧74℃（安全基準） | R-P05 |
| `meat_myosin` | 1 | R-P01 |
| `meat_actin` | 1 | R-P01 |
| `meat_myoglobin` | 2 | R-P02 |
| `meat_water_loss` | 大（70℃超で乾く） | R-P04 |
| `maillard` | 2（表面） | R-M01 |
| `note` | 安全基準（74℃）と乾きはじめ（70℃）が近く、衝突する（C10） | R-P04・R-P05 |

### ポーチドエッグ（`poached_egg`、2026-09-27 追加・14品目）

- 食材: egg_whole（割った・殻なし）
- 参考手順: 割った卵を 80〜85℃の湯（沸騰させない）に落として3〜4分
- 本人の依頼（東海オンエアの動画「温泉卵じゃ柔らかすぎ、ゆで卵じゃ硬すぎ、その間」）。13品には数えない（感じ方の採点がない）

| 状態変数 | 値 | 根拠 |
|---|---|---|
| `egg_form` | 割った（殻なし、溶いていない）※必須 | 料理の定義（R-E21） |
| `T_surface_max` | 80〜100℃（湯温） | R-E21（80〜85℃）・kyounoryouri（沸騰）。湯に接する表面は湯温（R-W02） |
| `t_at_T` | 表面が 80℃以上で 3分以上 | R-E21（3〜4分）の下端 |
| `egg_white_stage` | 2〜3（固まる） | R-E02・R-E03・R-E21 |
| `egg_yolk_stage` | 0〜1（流れる〜とろみ） | wiki_poached「runny yolk」・R-E21（中心 65℃未満）。1 を含めたのは推定 |
| `egg_white_cohesion` | まとまる（酢・塩を入れると表面に膜・ちぎれ） | R-E21・R-E22 |
| `maillard` | 0 | 湯で加熱（R-W02） |

### 半熟ゆで卵（`soft_boiled_egg`、2026-09-28 追加・13品外）

- 食材: egg_whole（殻付き）
- 参考手順: 沸騰した湯に殻ごと6〜7分（Exp-15 R007。wiki_boiled は 3分・5〜6分）
- 条件は §10「2026-09-28 修正 B」の表（結果を見る前に決めた）。卵白 3（固まる）・卵黄 0〜1（流れる〜とろみ）・殻付きが必須

## 7. 知覚の層への候補（対応づけはしない）

どの状態変数が、知覚のどれに効きそうかの**候補だけ**。重みや向き（上がると硬いのか）は書いていない。本人が決める。

| 知覚（候補） | 効きそうな状態変数 |
|---|---|
| 硬さ | `egg_white_stage`, `egg_yolk_stage`, `egg_gel_stage`, `gelatin_state`, `gelatin_conc`, `starch_retro`, `gluten`, `meat_actin`, `meat_water_loss`, `water`, `cell_wall`, `T_serve` |
| とろみ・粘り | `starch_gel`, `egg_yolk_stage`, `egg_gel_stage`, `gelatin_state`, `sugar_conc`, `syrup_stage`, `T_serve` |
| なめらかさ | `porosity`, `gel_structure`, `egg_gel_stage` |
| ふわふわ・軽さ | `air_frac`, `foam_stage`, `co2` |
| ぱりっと・かりっと | `T_surface_max`, `water（表面）`, `syrup_stage` |
| ほろほろ・ぽろぽろ | `egg_yolk_stage`, `gel_structure`, `cell_wall` |
| ジューシーさ | `meat_water_loss`, `water` |
| 甘さ | `sugar_conc`, `caramel`, `onion_sulfur`, `water` |
| 塩味 | `salt_conc` |
| 酸味 | `pH` |
| 苦味 | `caramel`, `maillard` |
| 旨み | `meat_collagen`, `milk_whey_denatured` |
| 香ばしさ | `maillard`, `caramel` |
| 刺激臭・辛味 | `onion_sulfur` |
| 油っぽさ・コク | `fat`, `fat_phase` |
| 温度 | `T_serve` |
| 時間（立ち上がり・余韻） | `fat_phase`, `sugar_conc`, `maillard` |

## 8. 未確認・衝突


- **C1** 卵白の凝固開始温度が出典によって 55〜57℃（kajiya）／60℃（SoC）／62℃（検索抜粋）／63℃（SoC のとろみ開始）とばらつく。何をもって「凝固開始」とするか（特定のたんぱく質・白濁・とろみ）が違う
- **C2** 撹拌した全卵の凝固が 73℃（SoC）と「70℃開始・75℃でしっかり」（家庭向けサイト）で違う。プリン液について「70℃開始・75℃」とする記事（mirai、出典なし）は、カスタードの 80〜85℃（R-E09）と矛盾する。希釈・砂糖を考えると後者が正しいと思われるが、一次資料では確認していない
- **C3** 牛乳・砂糖で薄めると凝固温度が上がる（R-E09, R-E10）ことは確かだが、薄め方ごとの凝固温度の関数（何%で何℃）は見つけていない。プリン・茶碗蒸しの状態は類推で書いた
- **C4** ショ糖のカラメル化 160℃（SoC）と 170℃（McGee）。さらにショ糖は熱分解なので時間をかければ低温でも進む（R-C03, R-C04）。「しきい値」でモデル化すると両方と食い違う
- **C5** 食塩は卵の凝固力を上げるが凝固温度も上げる（R-E12, R-E13、同じ論文）。「塩は卵を固まりやすくする」という一般的な言い方とは、指標によって合ったり合わなかったりする
- **C6** 米でんぷんの糊化開始が 60℃付近（農水省）と 58.9〜82℃（論文、幅）で違う。米の品種と測定法による
- **C7** 炒め玉ねぎの褐変のうちメイラードとカラメル化がどれだけずつかは分からない。「玉ねぎのカラメリゼ」という呼び名は化学的には不正確かもしれないが、確かめていない
- **C8** メイラードを 140℃しきい値で持つか、温度依存の速度で持つか。煮込み・長時間加熱では 140℃未満でも色が付く（R-M04）
- **C9** 料理の定義そのものが流儀で分かれる。スクランブルエッグ（焼き色の有無・仕上げ温度）、オムレツ（焼き色）。目標状態は1点ではなく範囲で持つ必要がある
- **C10** 鶏むね肉は安全基準 74℃ と乾きはじめ 70℃ が近い。安全を制約にすると「しっとり」は低温長時間（時間で殺菌）でしか満たせず、到達温度だけの状態では表せない
- **C11** 状態変数の多くが段階（ordinal）で、段階と温度の対応は出典にあるが段階の間の連続量はない。最近傍の料理を探すときの距離の定義が未定
- **C12** 卵白:卵黄の質量比、酢・レモン汁の pH、乳清の変性温度、泡のオーバーラン、肉の水分流出量は数値を集めていない（推定か空欄）
- **C13** ポーチドエッグの湯温が出典によって 62℃（wiki_poached）／63–65℃（terumimorita の要約行）／71〜74℃を保つ・85℃で入れる（travelingfoodlab）／80℃（soc_poach）／80–85℃（terumimorita 本文）／沸騰（kyounoryouri）とばらつく。シミュレータは 100℃ で頭打ちで、「弱い沸騰」と「激しい沸騰」を区別できない
- **C14** 湯に酢・塩を入れるかが出典で分かれる。入れる（kyounoryouri・terumimorita。すばやく固まり散らない）／入れない（travelingfoodlab。表面に不規則な膜ができる、McGee）。効果の向き（凝固が速まる）は一致し、仕上がりの評価が違う
- **C15** 殻付き卵の温度を2つの一次遅れ（中心 tau 7.2分・卵白の層 tau 1.4分）で持つ（2026-09-28、修正 B）。どちらも球の熱伝導（tatsu2019 に合わせた）の近似で、中心の一次遅れは球の解より立ち上がりが速い（沸騰の湯で中心が 63.2% に達するのは 一次遅れ 7.2分・球 10.3分）。卵白の層の tau は「63.2% に達する時間」で決めたが、75%・98% で決めると 1.9分・4.3分になる。2026-09-28 夜 Q6 (a) で、殻付き卵は2つの一次遅れをやめて球の熱伝導の解そのもの（R²/α=60.5分）に置き換えた。残る近似: 卵黄と卵白の熱拡散率の違い・卵の形・殻の熱抵抗を分けていない

## 9. 出典

| id | 種類 | 出典 | URL |
|---|---|---|---|
| `fooddb` | database | 文部科学省『日本食品標準成分表（八訂）増補2023年』食品成分データベース | https://fooddb.mext.go.jp/ |
| `mcgee` | book | Harold McGee, On Food and Cooking: The Science and Lore of the Kitchen, 2nd ed., Scribner, 2004（卵は第2章、乳は第1章、肉は第3章、ソースは第11章、糖は第12章。今回は書籍本文を開いていない。Science of Cooking と Wikipedia が McGee のページ（p.85, p.656）を引いている箇所だけ数値を採った） | — |
| `soc_temps` | web | Science of Cooking, "Important temperatures in Cooking and Baking" | https://www.scienceofcooking.com/important_cooking_temperatures.htm |
| `soc_sousvide` | web | Science of Cooking, "Cooking Eggs Sous Vide"（McGee p.85 を引用） | https://www.scienceofcooking.com/eggs/cooking-eggs-sous-vide.html |
| `wiki_caramel` | web | Wikipedia "Caramelization"（温度表は McGee 2004, p.656 を引用） | https://en.wikipedia.org/wiki/Caramelization |
| `awatsu1982` | paper | 粟津原宏子 ほか (1982)「卵白および卵黄の熱凝固について―食塩,砂糖の添加による影響―」調理科学 15(2):114 | https://www.jstage.jst.go.jp/article/cookeryscience1968/15/2/15_114/_article/-char/ja/ |
| `tatsu2019` | paper | N. Tatsutaguchi, M. Dai (2019)「温泉卵の凝固状態への加熱温度と保持時間の影響―好みの温泉卵を作るには―」日本調理科学会誌 52(5):345（著者名は J-STAGE の英字表記） | https://www.jstage.jst.go.jp/article/cookeryscience/52/5/52_345/_article/-char/ja/ |
| `maff_rice` | web(公的機関) | 農林水産省「米の調理特性」 | https://www.maff.go.jp/j/syouan/keikaku/soukatu/okome_summary/02/charact_eristic_01.html |
| `kainuma1987` | paper | Y. Kainuma, A. Ema (1987)「加水量が炊飯に及ぼす影響」日本家政学会誌 38(7):567-575 | https://www.jstage.jst.go.jp/article/jhej1987/38/7/38_7_567/_article/-char/ja/ |
| `tamaki2003` | paper | M. Tamaki, M. Ukai (2003)「長時間炒めたタマネギの味, 香り, 遊離糖, 色の変化」日本家政学会誌 54(1):69 | https://www.jstage.jst.go.jp/article/jhej1987/54/1/54_1_69/_article/-char/ja |
| `tokitomo1993` | paper | Y. Tokitomo, S. Yamanishi (1993)「加熱タマネギの甘いフレーバーについて」日本家政学会誌 44(5):347-353 | https://www.jstage.jst.go.jp/article/jhej1987/44/5/44_5_347/_article/-char/ja/ |
| `mc_maillard` | web | Modernist Cuisine, "The Maillard Reaction" | https://modernistcuisine.com/mc/the-maillard-reaction/ |
| `maillard_overview` | web | ScienceDirect Topics "Maillard Reaction" / BAKERpedia "Maillard Reaction" | https://www.sciencedirect.com/topics/food-science/maillard-reaction |
| `schmidt2011` | paper | J. W. Lee, L. C. Thomas, S. J. Schmidt (2011) Can the thermodynamic melting temperature of sucrose, glucose, and fructose be measured using rapid-scanning DSC? J. Agric. Food Chem. 59(8)（巻号は記憶、要確認）（解説記事 https://www.sciencedaily.com/releases/2011/07/110725123549.htm） | https://pubmed.ncbi.nlm.nih.gov/21417276/ |
| `roasted_sugar` | web | Stella Parks（Serious Eats / BraveTart）の roasted sugar 手法を紹介した記事（Boston Univ. "Trial by Fryer" 2018 など） | http://physics.bu.edu/~jmott/trialbyfryer/2018/06/roasted-sugar/ |
| `candy_stages` | web | Wikipedia "Candy making"（糖液の段階の表） | https://en.wikipedia.org/wiki/Candy_making |
| `nitta` | web(メーカー) | 新田ゼラチン Web研究所「ゼラチン研究室 12. よりよく活用するために」 | https://www.nitta-gelatin.co.jp/ja/labo/gelatin/12.html |
| `ijfp2007` | paper | Effects of Concentration, Bloom Degree, and pH on Gelatin Melting and Gelling Temperatures Using Small Amplitude Oscillatory Rheology. Int. J. Food Properties 10(4) (2007) | https://www.tandfonline.com/doi/full/10.1080/10942910601128895 |
| `gelatin_home` | web | 料理科学の森「ゼラチンの凝固温度と融解温度」ほか家庭向け解説 | https://ryourikagakunomori.jp/2021/07/20/%E3%82%BC%E3%83%A9%E3%83%81%E3%83%B3%E3%81%AE%E5%87%9D%E5%9B%BA%E6%B8%A9%E5%BA%A6%E3%81%A8%E8%9E%8D%E8%A7%A3%E6%B8%A9%E5%BA%A6/ |
| `pineapple` | web(公的DB) | 国立国会図書館 レファレンス協同データベース「パイナップルを入れるとゼラチンではかたまらないが、寒天では固まる」 | https://crd.ndl.go.jp/reference/entry/index.php?id=1000288396&page=ref_view |
| `tornberg2005` | paper | E. Tornberg (2005) Effects of heat on meat proteins – Implications on structure and quality of meat products. Meat Science 70:493-508（巻・頁は記憶、要確認） | https://www.researchgate.net/publication/51781900_Effects_of_heat_on_meat_proteins_-_Implication_on_structure_and_quality_of_meat_products |
| `fsis` | web(公的機関) | USDA FSIS "Safe Minimum Internal Temperature Chart" | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart |
| `cream2010` | paper | Influence of whipping temperature on the whipping properties and rheological characteristics of whipped cream. J. Dairy Sci. (2010) | https://www.sciencedirect.com/science/article/pii/S0022030210002997 |
| `cream_overview` | web | ScienceDirect Topics "Whipped Cream" | https://www.sciencedirect.com/topics/food-science/whipped-cream |
| `eggfoam_isu` | web(大学教材) | Iowa State Univ., Food Preparation Lab Manual for FSHN 1150, "9.1 Introduction to Egg White Foams" | https://iastate.pressbooks.pub/fshn115/chapter/egg-white-foams/ |
| `eggfoam_yolk` | paper | Effect of Lipase and Phospholipase A1 on Foaming and Batter Properties of Yolk Contaminated Egg White (PMC10048306) | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10048306/ |
| `custard_textbook` | web(教科書) | Modern Pastry and Plated Dessert Techniques, "Coagulation" (BCcampus Open Textbook) | https://opentextbc.ca/modernpastryandplateddesserts/chapter/coagulation/ |
| `custard_123` | web | 123 Food Science "Why Custard Thickens" | https://123foodscience.com/cooking-science/custard-science/ |
| `casein` | paper | Acid-induced gelation behavior of casein/whey protein solutions assessed by oscillatory rheology (PMC4152502) ほか | https://pmc.ncbi.nlm.nih.gov/articles/PMC4152502/ |
| `starch_gel` | paper | 検索抜粋に出た複数論文（ResearchGate "Studies on the Gelatinization Temperature of Some Cereal Starches"、PMC12167104 など）。どの値がどの論文かは抜粋では分離できなかった | https://pmc.ncbi.nlm.nih.gov/articles/PMC12167104/ |
| `roux` | paper | Effects of Cooking Temperatures and Starch Source on the Gelatinization and Thickening Power of Roux | https://www.researchgate.net/publication/254361032_Effects_of_Cooking_Temperatures_and_Starch_Source_on_the_Gelatinization_and_Thickening_Power_of_Roux |
| `roux_texts` | web(大学教材) | LibreTexts "4.2 Roux and Thickening"（Kansas State Univ. FNDH 313） | https://med.libretexts.org/Courses/Kansas_State_University/FNDH_313:_Science_of_Food/04:_Soups_Salads_and_Gelatins/4.02:_Roux_and_Thickening |
| `potato_pme` | web | 宝酒造 業務用調味料「煮崩れ～その要因と防止する方法～」、香西みどり「野菜の硬さと最適加熱時間の予測」（熱物性資料） | https://chomiryo.takarashuzo.co.jp/knowledge/detail/104/ |
| `gluten` | web(学会) | Institute of Food Science and Technology "Protein: gluten formation" / Wikipedia "Gluten" | https://www.ifst.org/lovefoodlovescience/resources/protein-gluten-formation |
| `baking_powder` | web | Wikipedia "Baking powder" / Britannica "Double-acting baking powder" | https://en.wikipedia.org/wiki/Baking_powder |
| `yeast` | web | Exploratorium "Yeast is Fussy About Temperature" / ThermoWorks "Homemade Bread: Temperature is Key" | https://www.exploratorium.edu/explore/cooking/yeast-temperature |
| `frying` | paper | "Changes in food caused by deep fat frying – A review." Archivos Latinoamericanos de Nutrición 63(1) (2013) ほか | https://www.alanrevista.org/ediciones/2013/1/art-1 |
| `chawan_web` | web | 三越伊勢丹 FOODIE「茶碗蒸しレシピ。卵と出汁は1:3が黄金比」ほか | https://mi-journey.jp/foodie/49227/ |
| `kajiya` | web(出典記載なし) | カジヤ「カスタードプリンや茶碗蒸しの凝固温度は？」 | https://www.kajiya.org/archives/107 |
| `mirai` | web(出典記載なし) | 科学者の卵養成講座「プリンの“す”」（高校生の記事） | https://mirai-eggs.org/science_blog/%E3%83%97%E3%83%AA%E3%83%B3%E3%81%AE%E3%81%99/ |
| `omelet_web` | web | オリーブオイルをひとまわし「ふんわり卵でオムレツを作ろう！コツや卵の凝固温度を紹介！」 | https://www.olive-hitomawashi.com/column/2018/09/post-3039.html |
| `butter` | web | The Physics Factbook "Melting Point of Butter" / Pastry Arts Magazine "Plasticity and Melting Points in Butter" | https://hypertextbook.com/facts/2003/JessicaCheung.shtml |
| `pancake_web` | web(レシピ) | Betty Crocker "Fluffy Homemade Pancakes" ほかレシピサイト | https://www.bettycrocker.com/recipes/fluffy-homemade-pancakes/77a89da1-fd56-494b-874a-55f9195c1413 |
| `soc_poach` | web | Science of Cooking, "What are best methods to poach an egg?"（McGee と Heston Blumenthal の手順を引用） | https://www.scienceofcooking.com/eggs/what-are-best-methods-to-poach-an-egg.html |
| `terumimorita` | web(料理人の記事) | Terumi Morita, "Poached Egg"（2025-08-28）。本文の湯温は 80–85°C、冒頭の要約行は 63–65°C（C13） | https://terumimorita.com/journal/poached-egg |
| `travelingfoodlab` | web(料理人の記事) | 樋口直哉「ポーチドエッグの作り方」note（『マギーキッチンサイエンス』p88 を引用） | https://note.com/travelingfoodlab/n/n2c560bfe4de4 |
| `kyounoryouri` | web(レシピ) | NHK「みんなのきょうの料理」脇雅世「ポーチドエッグ」 | https://www.kyounoryouri.jp/recipe/5203 |
| `wiki_poached` | web | Wikipedia "Poached egg" | https://en.wikipedia.org/wiki/Poached_egg |
| `wang2025` | paper | Wang L, Li R, Lv S, et al. (2025) "The Thermodynamic and Gelation Properties of Ovalbumin and Lysozyme." Gels 11(6):470 | https://doi.org/10.3390/gels11060470 |
| `egg_structure` | web(出典記載なし) | 「たまごの構造」（個人のページ）。卵殻 8～11%、卵白 56～59%、卵黄 30～33%、卵殻の厚さ 0.2～0.38mm（本文確認）。検索抜粋では 卵白 57～63.4%・卵黄 28～30.6%・卵殻 8.1～12.4% | http://ww1.tiki.ne.jp/~k_fukuda/kouzou.htm |
| `egg_thermal` | web(検索抜粋) | 熱拡散率 卵白 1.7×10⁻⁷・卵黄 1.3×10⁻⁷ m²/s、熱伝導率 卵白 0.52・卵黄 0.34 W/(m·K)（ResearchGate の表 "Thermal properties of egg components"、本文は 403）。卵を模した熱シミュレータの特許 US10466188B2 では卵白 1.3〜2.3×10⁻⁷・卵黄 1.1〜1.4×10⁻⁷ m²/s（抜粋のみ） | https://www.researchgate.net/figure/Thermal-properties-of-egg-components_tbl1_256804375 |
| `wiki_boiled` | web | Wikipedia "Boiled egg"（"Soft-boiled eggs have a partially liquid yolk" / "heat will take longer to reach the yolk through the albumin"） | https://en.wikipedia.org/wiki/Boiled_egg |
| `wiki_carryover` | web | Wikipedia "Carryover cooking"（2026-08-16 版。"Heat therefore will continue to migrate inwards from the surface, and the food will cook further even after being removed from the source of heat." / 中心温度の上昇 3–14℃（肉のロースト）） | https://en.wikipedia.org/wiki/Carryover_cooking |
| `thermoworks_egg` | web(メーカー) | ThermoWorks "Boiling Eggs: Everything You Need to Know"（"immediately dump your eggs into an ice bath after cooking and chill them for 10–15 minutes. The ice bath is an important step to halt carryover cooking"、卵黄 66℃でとろみ・70℃で固まる） | https://blog.thermoworks.com/boiling-eggs-everything-you-need-to-know/ |
| `wiki_htc` | web | Wikipedia "Heat transfer coefficient" ／ Engineering ToolBox "Convective Heat Transfer"（空気の自然対流 5〜25 W/(m²·K)） | https://en.wikipedia.org/wiki/Heat_transfer_coefficient |
| `cengel_egg` | book(例題、検索抜粋) | Çengel『Heat and Mass Transfer』の例題「卵を直径 6cm の球とみなしてゆでる」（湯の熱伝達率 800 W/(m²·℃)）。例題の値で、実測ではない | https://studyx.ai/homework/109238792-for-the-purposes-of-heat-transfer-an-egg-can-be-considered-as-a-sphere-6-cm-in-diameter |
| `coimbra2006` | paper(抄録) | Coimbra JSR et al. (2006) Density, heat capacity and thermal conductivity of liquid egg products. J. Food Eng. 74:186（熱伝導率 卵黄 0.4〜卵白 0.6 W/(m·K)） | https://www.sciencedirect.com/science/article/abs/pii/S0260877405001330 |

## 10. 変更履歴

### 2026-09-27 シミュレータを作るための追加・変更

**追加（rules.yaml）**
- `sim`: シミュレータの採用値。出典で食い違う値（C1・C2・C4・C6 など）は採用値を1つ決め、代替値を `alternatives` に併記した。出典のない値（時間・時定数・蒸発の速さ など）は `check: 推定` とした
- `dish_conditions`: §6 の目標料理を「状態の条件の組み合わせ（範囲・段階・真偽・保持時間）」に変換したもの。「約X」は幅を持たせて範囲にした（幅は推定、各条件の `basis` に書いた）。各料理に §6 の食材を必須条件として加えた

**状態変数の追加・変更**
- 追加: `egg_form`（殻付き／割った／溶き卵）、`egg_gel_stage_surface`（卵液の外側のゲル段階）、`T_whisk`（泡立て中の品温の平均）、`air`（気泡の有無。`air_frac` の数値が無いため真偽で持つ）、`sugar_conc_ratio`（重量あたりの糖濃度が水が飛ぶ前の何倍か）
- 変更: `meat_water_loss` を連続量（%）から段階（0: なし / 1: 60℃で肉汁が出る / 2: 70℃でむね肉が乾く）にした。量の出典がないため（C12）

**料理の定義の変更**
- プリン: `caramel = 2` を条件から外した。底のカラメル層は別に作って敷くもので本体の状態ではなく、シミュレータは層を持たない
- カラメル: `T_core_max` を「約160〜170℃」から「160〜180℃未満」にした。採用値 170℃（C4）で色づくので、上端 170℃では色づいた状態がほぼ範囲外になる。焦げ（R-C06, 180℃）の手前までとした
- ホイップクリーム: `fat` を「30〜40%」から「30%以上」にした。成分表のクリーム（乳脂肪）は 43.0 で範囲外になり、R-D03 の条件は「30%以上」。`T_core_max`（泡立て時 7.5〜12.5℃）は `T_whisk` にした。`T_core_max` は履歴全体の最大値で意味が違う
- オムレツ: 「外側 2〜3、内側 1〜2」を `egg_gel_stage_surface`（外側）と `egg_gel_stage`（内側）に分けた
- 温泉卵: `egg_form = 殻付き` を条件に加えた（§6 の食材「殻付き」）。`t_at_T`「中心が湯温に近づいてから数分〜」は「中心が 65℃以上の時間が 3分以上」にした
- 炒め玉ねぎ: `water`「大きく減る」は「80 g/100g 以下」、`sugar_conc`「重量あたりは上がる」は `sugar_conc_ratio ≧ 1` にした
- ゆで卵（固ゆで）`hard_boiled_egg` を追加した。13品には数えない。温泉卵と「湯の温度だけ変える」テストの相手

**規則の解釈（実装で決めたこと）**
- R-E15（す）は、でんぷんを含まない卵液にだけ当てる。パンケーキ生地の中心が 90℃を超えて「す立ち」と判定されたため。R-E15 の対象は「希釈卵液（茶碗蒸し・プリン）」
- R-E20（撹拌の有無）: 加熱中に撹拌していて卵液が段階1に達したら `gel_structure = 小片`。撹拌せず中心が段階2以上なら連続ゲル、外側だけ段階2以上なら「外側連続・内側半流動」
- R-E09・R-E07: 卵の質量割合が 50% 以上なら薄めない卵のしきい値（70/73/80℃）、未満ならカスタードのしきい値（79/80℃）。薄め方の関数がない（C3）ので2区分にした。砂糖・塩による上昇（R-E10・R-E13）は数値がないので入れていない
- R-M04（140℃未満の遅い褐変）は扱わない（C8 はしきい値モデルを採用）


### 2026-09-27 「〜になるまで加熱」・「該当なし」・殻付きの必須化（本人と決めた3点）

**操作の追加**
- 加熱（`heat` と、その特殊化の 焼く・蒸す・煮る・揚げる）に、時間の代わりに停止条件を指定できるようにした。`until={var: 状態変数, ge|le|in: 値}` と上限時間 `max_time`。時間の刻み（`dt_min`）ごとに条件を調べ、最初に満たした刻みで止める。上限までに満たさなければ上限で止め、未到達として返す（`State.stops` と trace）。加熱前から満たしていれば 0分で止める。時間で指定する操作はそのまま残した
- 正解のレシピのうち、状態を見て火を止めるのが自然な8品（スクランブルエッグ・オムレツ・カラメル・プリン・茶碗蒸し・炒め玉ねぎ・鶏むね肉のソテー・牛乳ゼリー）を停止条件で書き直した。停止条件は結果を見る前に決め、実行前にコミットした（8ec6d55）。結果を見てからは変えていない。時間の版は `DISH_RECIPES_TIMED` として残した。停止条件と、時間のまま残した品の理由は `sim/recipes.py` の `UNTIL_REWRITE`・`UNTIL_KEPT_TIMED`

**判定の変更**
- 必須条件（`required: true`）を満たさない料理は、下に並べるのではなく候補から外すようにした（内訳には残す）
- 候補の1位の満たした割合が下限未満なら「該当なし」を返す。上位の候補と内訳は併せて返す。下限は `run.py` 冒頭の `NO_MATCH_BELOW = 0.6`。結果を見る前に、本人の例示の値をそのまま採った

**料理の定義の変更**
- 温泉卵・ゆで卵: `egg_form = 殻付き` を必須条件にした（`required: true`）。割った卵・溶いた卵はこの2品の候補に入らない

### 2026-09-27 ポーチドエッグ（14品目）を足す

本人の依頼（東海オンエアの動画「温泉卵じゃ柔らかすぎ、ゆで卵じゃ硬すぎ、その間」）。定義・規則・正解のレシピは計算する前に書いてコミットした。既存の規則・採用値・料理の条件は変えていない。

**追加**
- 規則 R-E21（湯温と卵白のまとまり）・R-E22（湯に酢・塩）・R-E23（pH とオボアルブミンの熱安定性）。出典 soc_poach・terumimorita・travelingfoodlab・kyounoryouri・wiki_poached・wang2025。衝突 C13（湯温）・C14（酢・塩を入れるか）
- 操作 `poach`（卵を割って湯に落とす）。今の操作では「割った卵がじかに湯にふれる」を表せない（煮る の形は 鍋・器・殻付き で、器に入れた卵液と区別できない）ため足した。煮る の特殊化で、形 `drop`（時定数は shell と同じ 7.2分、推定）。蒸発は起きない形として扱う（shell・cup と同じ）
- 状態変数 `egg_white_cohesion`（卵白のまとまり: ばらける／まとまる（表面に膜・ちぎれ）／まとまる）。湯に落とした時点の湯温と酢・塩で決める。80℃未満（`poach_cohesion_T_min`）はばらける、酢か塩があれば「膜・ちぎれ」、沸騰（100℃）で酢・塩がなければばらける、それ以外はまとまる。酢・塩の量の効果は出典がないので、少しでも入っていれば効くとした（推定）
- 料理 `poached_egg` の条件（§6）

**規則の解釈（実装で決めたこと）**
- 割った卵（溶いていない、`egg_form = 割った`）では、卵白の段階を**表面の最高温度**で、卵黄の段階を中心の最高温度で決めるようにした。卵白は外側・卵黄は内側にあり、R-E21 は「卵白は完全に固まり、卵黄の中心は 65℃未満」と、同じ卵の中で温度が違うことを前提にしている。今までどおり1つの温度（中心）で両方を決めると、卵白 3（80℃以上）なら卵黄も 3 になり、「卵白は固まり卵黄は流れる」状態を作れない（温泉卵と同じ「卵白 2・卵黄 1」までしか出ない）。オムレツの外側（`egg_gel_stage_surface`）を表面温度で決めているのと同じ考え方（推定）
- 殻付き卵・溶き卵は変えていない（中心の温度で両方を決める）。殻付き卵にも同じ「外側・内側」の差はあるはずだが、変えると温泉卵・ゆで卵の結果が変わるので今回は触らない。13品と比較用のゆで卵の正解のレシピ・順番を変えた組に、割った卵を溶かずに加熱するものは無い
- 表面は湯にふれた瞬間に湯温になる（R-W02 の扱いのまま）ので、卵白は湯に入れた最初の刻みで段階が決まる。卵白が固まるまでの時間は、料理の条件の「表面が 80℃以上で 3分以上」でだけ表れる

### 2026-09-28 料理ごとの「定義上の必須条件」（本人承認済み）

**きっかけ**: 茶碗蒸しのレシピからだしを抜く（溶き卵に塩を入れて器で蒸す）と「スクランブルエッグ 0.80」になった。満たさなかったのは「形が小片（カード）」と「バターが融けている」だけ。料理を決める一番大事な条件（形）が 10条件の1つとしてしか数えられていなかった。地図（results/maps.md）でも、殻付き卵・プリン液を蒸したものがスクランブルエッグ、プリン液を蒸したものがオムレツ、65〜77.5℃の割った卵がポーチドエッグ、になる領域が同じ理由で出ていた。

**変更**: 各料理について「それを外したらその料理ではない」条件を必須（`required: true`、YAML では `def: 定義（2026-09-28）` を併記）にした。必須を満たさない料理は候補から外す（2026-09-27 の仕組みのまま）。**条件の値・範囲は変えていない**。今ある条件に必須の印を付けただけで、足した条件はポーチドエッグの「湯に落とした」1つ。結果を見る前にこの表を書いてコミットした。

| 料理 | 必須にした条件（食材・殻付きに加えて） | 理由 |
|---|---|---|
| スクランブルエッグ | 固まり方 = 小片（カード） | 混ぜながら固めて細かいかたまりにした卵が、この料理の定義（R-E20）。形が違えば別の料理 |
| オムレツ | 固まり方 = 外側連続・内側半流動 | 外を固めて中を半熟で包んだ一枚が定義。中まで固めた卵（連続ゲル）も一枚だが、§6 の定義（外は固まり中は半熟）に合わせ、広げずに厳しい側をとった |
| プリン | 固まり方 = 連続ゲル | 蒸して（焼いて）ひとつながりに固めた卵液。糖は食材の必須（sugar）で既に要る |
| 茶碗蒸し | 卵の割合 20〜30%、固まり方 = 連続ゲル | だしで薄めた卵液（R-E16、約25%）をひとつながりに固めたもの。だしは食材の必須で既に要るが、量が少なければ茶碗蒸しではない |
| ホワイトソース | でんぷんの糊化 0.9〜1.0、焼き色 0 | ルーのでんぷんが糊化してとろみがついたソース（R-S10）。色づけたルーはブラウンソースで、名前の「ホワイト」が定義 |
| カラメル | カラメル化 = 2 | 糖が褐色に色づいたもの（R-C01）。色づかない糖液はシロップ、焦げ（3）は別 |
| 炒め玉ねぎ（あめ色） | 焼き色 2〜3 | 「あめ色」が名前に入っている。色づかない玉ねぎは「しんなり炒めた玉ねぎ」 |
| ご飯 | でんぷんの糊化 0.9〜1.0 | 米のでんぷんが糊化しきったもの（R-S04・R-S07）。糊化していない米は生米 |
| パンケーキ | でんぷんの糊化 0.9〜1.0 | 生地が焼けて（でんぷんが糊化して）いること。焼けていない生地はパンケーキではない |
| 牛乳ゼリー | ゼラチンの状態 = ゲル | 固まっていなければゼリーではない（R-J04・R-J05） |
| ホイップクリーム | 脂の状態 = ホイップの網目 | 泡立てて乳脂肪の網目ができたもの（R-D03）。網目の無いクリームは液体の生クリーム |
| 温泉卵 | 卵白 1〜2（固まりきらない） | 卵白に流動性が残るのが温泉卵（R-E08、§6）。卵白がしっかり固まれば別（ゆで卵・半熟卵） |
| ゆで卵（固ゆで） | 卵黄 3 | 「固ゆで」は卵黄まで固まった卵（R-E06 の「固ゆで卵のほろほろ」） |
| 鶏むね肉のソテー | ミオシン = 変性 | 肉に火が通っていること（R-P01）。生の肉はソテーではない |
| ポーチドエッグ | 卵白 2〜3、卵黄 0〜1、湯に落とした（新しい条件） | 卵白が固まり卵黄は流れる、割った卵を湯で加熱したもの（R-E21）。まとまり（ばらける／まとまる）は必須にしない（ばらけても出来の悪いポーチドエッグ） |

**判断に迷った点（安全なほう＝厳しい側をとった）**
- オムレツの「中まで固まったもの」は外した（上表）。オムレツの流儀（C9）次第では入る
- 温泉卵・ゆで卵について、依頼の例は「殻付き」だけだったが、名前が状態を言っている条件（温泉卵の卵白が固まりきらない、固ゆでの卵黄）も必須にした
- 「蒸し卵」（だしなしで蒸した卵）を料理として足すかは、足さずに「該当なし」になるかを先に確かめる

### 2026-09-28 修正 B: 殻付き卵も卵白は外側（卵白の層）の温度、卵黄は中心の温度で決める（本人が選んだ修正）

**きっかけ**: Exp-15 で世の中の半熟ゆで卵のレシピ5件（沸騰した湯で4〜7分）を地図に重ねると、4件が温泉卵・1件が該当なしになった（`experiments/exp-15-recipes/overlay.md`）。殻付き卵は卵白も中心の温度で段階を決めているので、沸騰した湯で6〜7分（中心 65〜68℃）でも卵白が 2（やわらかい）になり、温泉卵の必須（卵白 1〜2）を満たしてしまう。実物の半熟ゆで卵は白身がしっかり固まり黄身がとろとろ、温泉卵（65〜68℃で30分）は全体がほぼ均一で白身がゆるい。違いは卵の中の温度分布（wiki_boiled「heat will take longer to reach the yolk through the albumin」）。

**変更（結果を見る前にこの節を書いてコミットした）**
- 殻付き卵（`egg_form = 殻付き`）に、中心の温度 `T_core` とは別に **卵白の層の温度 `T_white`**（卵白の層の体積平均）を持たせる。卵白の段階は `T_white` の最高温度、卵黄の段階は今までどおり中心の最高温度で決める。割った卵（表面の温度で卵白を決める、2026-09-27）と同じ考え方
- `T_white` は中心と同じ形の一次遅れで、媒体温度（湯・蒸気は 100℃で頭打ち、水がある間は沸点を超えない）に時定数 `tau_white_layer_min` = **1.4分**（推定）で近づく。空気（冷蔵庫・室温）では中心と同じく `air_tau_factor` 倍。中心の時定数（shell 7.2分）は変えない
- 1.4分の決め方: 卵を一様な球とみなし、球の熱伝導の解（表面＝媒体温度）で「中心が 20℃から 68℃の湯で 1℃以内に達するのが 28分」（tatsu2019。shell の 7.2分と同じ根拠）になるよう R²/α を決めた（60.5分）。卵黄を中心の球（中身の 34%。egg_structure の卵黄 30〜33%・卵白 56〜59% から）、卵白をその外側の層とし、卵白の層の体積平均が媒体との温度差の 63.2% を詰める時間（時定数の定義）1.42分を採った。R²/α=60.5分は熱拡散率 1.7×10⁻⁷ m²/s（egg_thermal、抜粋のみ）なら半径 2.5cm で、卵の大きさと矛盾しない
- 殻による遅れ: 殻（0.2〜0.38mm、egg_structure）の熱抵抗は分けて持たない。tatsu2019 は殻付き卵の実測なので中心の 28分に含まれている。殻の熱伝導率の出典は探していない（推定: 卵の中の伝導に比べて小さい）
- 温度の履歴も層ごとに持つ: 保持時間 `hold` に `white`（卵白の層）を足す。料理の条件（温泉卵の「中心が 65℃以上で3分以上」など）は変えない
- 割った卵・溶き卵の扱いは変えない。殻付き卵以外では `T_white` は値なし

**変わると分かっていること**: 殻付き卵の卵白の段階が上がる（外側は中心より先に熱くなる）。温泉卵（68℃30分）・ゆで卵（沸騰12分）の正解のレシピ、温度だけ変える組（68℃／100℃で30分）、殻付き卵の地図、Exp-15 の半熟ゆで卵・固ゆで卵の点。**結果に合わせて 1.4分や料理の条件を動かさない**。既存の正解のレシピが外れたらそのまま記録する。代わりの時定数（1.9分・4.3分）は感度として記録するだけにする

**半熟ゆで卵（`soft_boiled_egg`）を足す条件と定義（結果を見る前に決めた）**: 修正 B の後に、沸騰した湯で6〜7分の殻付き卵が「温泉卵とゆで卵の間で該当なし」になった場合だけ足す（本人方針。判断は安全側で記録）。足す場合の定義:

| 条件 | 値 | 必須 | 根拠 |
|---|---|---|---|
| 食材 | egg_whole | ○ | 料理の定義 |
| 卵の形 | 殻付き | ○ | 料理の定義（殻ごとゆでる） |
| 卵白 | 3（固まる） | ○（定義） | 白身はしっかり固まる（R-E03。温泉卵の「卵白 1〜2」と重ならない側） |
| 卵黄 | 0〜1（流れる〜とろみ） | ○（定義） | wiki_boiled「partially liquid yolk」、R-E05（65℃でとろみ・70℃で固まる） |
| 表面の最高温度 | 95〜100℃ | | 沸騰した湯・蒸気（Exp-15 の半熟ゆで卵のレシピは全件が沸騰の湯か蒸し） |
| 焼き色 | 0 | | 湯で加熱（R-W02） |

13品には数えない（感じ方の採点がない）。

**結果（計算した後に書いた）**
- 修正 B だけ（半熟ゆで卵を足す前）で、沸騰した湯で 6〜7分の殻付き卵は 卵白 3・卵黄 1 になり、温泉卵（卵白 1〜2 必須）からもゆで卵（卵黄 3 必須）からも外れて「該当なし」になった。Exp-15 の半熟ゆで卵 5 行もすべて該当なし。事前に決めた条件に当たったので、上の表の定義どおりに `soft_boiled_egg` を足した（定義・値は変えていない）。正解のレシピは沸騰した湯に殻ごと 6.5分（Exp-15 R007 の 6〜7分の中央）
- 温泉卵・ゆで卵・ポーチドエッグ・既存全品の正解のレシピ（両版）と、順番を変えた7組の答えは変わらなかった。数値は `results/summary.md` §10、地図は `results/maps.md` §7、レシピの重ね合わせは `experiments/exp-15-recipes/overlay.md`
- 時定数 1.4分の代わりに 1.9分・4.3分を使った感度は summary.md §10 に記録した（採用値は変えていない）

### 2026-09-28 夜 Q6: 残ったおかしな判定の修正（変更の前に書いた）

**きっかけ**: `results/maps.md` §7 と `experiments/exp-15-recipes/overlay.md` に残ったおかしな判定のうち、night-queue の Q6 に挙げた4つ。夜の作業（本人承認済み、判断は安全側で記録）。**この節は計算を変える前に書いてコミットした。結果に合わせて値を動かさない。** 変えた後の結果は下の「結果」に書き足す。

**(a) 殻付き卵の中心の温まり方が速すぎる（C15）**
- 変更: 殻付き卵（`form = shell`）の中心と卵白の層の温度を、2つの一次遅れ（中心 7.2分・卵白の層 1.4分）から、**一様な球の熱伝導の解**に置き換える。表面＝媒体温度（湯・蒸気。殻の熱抵抗は分けない、修正 B と同じ）。
- 使う値: R²/α = **60.5分**（修正 B で tatsu2019「20℃の卵が 68℃の湯で中心が 1℃以内に達するまで 28分」に合わせて決めた値をそのまま使う。新しい値は足さない）。卵黄＝中心の球（中身の 34%、egg_structure）。中心＝球の中心の温度、卵白の層＝半径 0.34^(1/3)〜1 の体積平均。
- 計算の仕方: 球の解を固有関数（sin(nπr)/(nπr)、n=1..40）で展開し、刻み（0.1分）ごとに媒体温度が一定とみなして各項を exp(−n²π²·dt/(R²/α)) で減衰させる。媒体温度が変わった刻みでは差を一様な分布として足し直す（重ね合わせ）。空気（冷蔵庫・室温）では今までどおり `air_tau_factor`（4）倍遅くする（推定のまま）。
- 理由: 一次遅れは球の解より立ち上がりが速い（沸騰の湯で中心が 63.2% に達するのは一次遅れ 7.2分・球 10.3分、C15）。卵黄の段階の境目（半熟とゆで卵の間）の時間がこの近似に効く。修正 B の 1.4分は同じ球の解から「63.2% に達する時間」で取り出したもので、球の解そのものを使えば取り出し方（63.2%・75%・98%）で値が 1.4〜4.3分と動く問題（C15 後半）も消える。
- 出典: tatsu2019（抄録確認、28分）、egg_structure（本文確認、卵黄の割合）、egg_thermal（抜粋のみ、R²/α が卵の大きさと矛盾しない確かめ）。球の熱伝導の解は物理の教科書的な式（出典は付けない。数式はコードの docstring）。
- 変えないもの: 割った卵（`drop`、7.2分）・溶き卵・ほかの形の一次遅れ。割った卵は湯の中で球ではなく平たく広がるので、球の解を当てる根拠がない（安全側: 触らない）。`tau_min.shell`・`tau_white_layer_min` は rules.yaml に残し、「2026-09-28 夜から使っていない（球の解に置き換え）」と書く。

**(b) 殻付き卵を 72.5〜80℃に長く置いても温泉卵**
- 変更: 温泉卵の条件「中心の最高温度 65〜70℃」（R-E08）を**必須（定義）**にする。値・範囲は変えない。
- 理由: 温泉卵は「65〜70℃の湯に保った卵」（R-E08 の 65/68/70℃）で、中心が 70℃を超えると卵黄が固まる（R-E05）。今は外れても 5/6 で温泉卵になる。2026-09-28 の「定義上の必須条件」と同じ考え方（名前が状態を言っている条件を必須にする）。
- 予想される副作用（書いておく）: 72.5〜80℃の長い時間は「該当なし」になる（卵白 2・卵黄 2 の料理は無い）。足さない。

**(c) 82.5〜87.5℃の湯でも半熟ゆで卵**
- 変更: 半熟ゆで卵の条件「表面の最高温度 95〜100℃」を**必須（定義）**にする。値は変えない。
- 理由: 定義を決めたとき（§10 修正 B）の根拠が「沸騰した湯・蒸気（Exp-15 の半熟ゆで卵のレシピは全件が沸騰の湯か蒸し）」で、「ゆでる」は沸騰した湯で加熱すること。沸騰していない湯で白身だけ固めた卵は、半熟ゆで卵と呼ぶ根拠が無い。
- 変えないもの: 固ゆで卵（`hard_boiled_egg`）の条件。固ゆでの条件には表面温度が無く（中心 80〜100℃）、同じ扱いにするには条件を足すことになるので今回はしない（記録だけ）。

**(d) 溶き卵の地図の元のレシピが混ぜないオムレツ（Exp-15 のスクランブルエッグ 0/6）**
- 変更: 地図を1枚足す。`beaten_stir`「溶き卵を混ぜながら × フライパンの温度 × 時間」（元のレシピはスクランブルエッグの時間の版、軸・範囲は `beaten_pan` と同じ）。Exp-15 のスクランブルエッグの点はこの地図に置く（卵の形だけでなく料理で地図を選ぶ）。`beaten_pan`（オムレツ）は残す。
- 理由: レシピはどれも混ぜながら焼く手順なのに、混ぜない元のレシピの地図に置いていた（地図の前提の違い、overlay.md の「BASE」）。元のレシピを差し替えると、オムレツの地図が無くなる。足すほうが安全（今の地図は変わらない）。
- 規則・判定は変えない。

**確かめること**: 全16品（13品＋ゆで卵・ポーチドエッグ・半熟ゆで卵）の正解のレシピ（両版）、順番を変えた7組、4枚の地図（＋新しい1枚）、Exp-15 の重ね合わせの一致率を、変更の前後で比べて `results/summary.md` と `results/maps.md` に書く。JS 版（`js/sim.js`）も同じ式にして一致テストを通す。

**結果（計算した後に書いた。前後の数は Q6 の直前 584c6f6 と比べた）**

| 見たもの | 前 | 後 |
|---|---|---|
| 13品の正解のレシピ（状態で止める版／時間の版） | 12/13 ／ 13/13 | 12/13 ／ 13/13（変わらない。温泉卵は 68℃30分で中心 67.0℃のまま温泉卵） |
| 追加の3品（ゆで卵・半熟ゆで卵・ポーチドエッグ）の正解のレシピ | 3/3（両版） | **2/3**（両版）。**ゆで卵（沸騰12分）が該当なし**: 中心 77.5℃・卵黄 2 で、固ゆでの必須「卵黄 3（80℃）」に届かない。半熟ゆで卵（沸騰6.5分）は卵黄 1→0 で半熟ゆで卵のまま |
| 順番・操作を変えた7組 | 全組が期待どおり | 変わらない（温泉卵 vs ゆで卵の組は沸騰30分なので固ゆでになる） |
| 地図 殻付き卵（630 マス） | 温泉卵 138・半熟ゆで卵 26・ゆで卵 182・該当なし 117・生のまま 167 | 温泉卵 **48**・半熟ゆで卵 **10**・ゆで卵 173・該当なし **229**・生のまま 170 |
| 地図 割った卵・溶き卵（混ぜない）・プリン液 | 344/166/120・111/503/16・210/155/12/43 | 変わらない |
| 地図 溶き卵を混ぜながら（新しい、630 マス） | — | スクランブルエッグ 272・該当なし 279・生のまま 79 |
| Exp-15 の重ね合わせ | 21/28（固ゆで 6/7・スクランブル 0/6） | **20/28**（固ゆで **1/7**・スクランブル **4/6**。半熟 5/5・ポーチ 6/6・プリン 4/4 は同じ） |

- (a) 球の解: 沸騰の湯で中心が 65/70/80℃ に達するのは、20℃の卵で 9.3/10.3/12.8分、5℃の卵で 10.4/11.3/13.8分（一次遅れのときは 20℃の卵で 6.0/7.1/10.0分）。卵白の層が 80℃（卵白 3）に達するのは 2.7分。80℃の湯では卵白の層の平均が 80℃に届かず、卵白 3 にならない
- (a) だけで殻付き卵の地図は 温泉卵 132・半熟ゆで卵 24・ゆで卵 173・該当なし 131・生のまま 170。(b) で温泉卵 132→48（72.5〜80℃の長い時間が外れた。残りは 67.5〜70℃の 19〜59分と、72.5〜80℃の 13〜21分）、(c) で半熟ゆで卵 24→10（95〜100℃・3〜9分だけ残った）
- 固ゆで卵が外れた件は、結果に合わせて直していない。考えられる直し方は2つで、どちらも本人の判断が要る: 固ゆでの定義を「卵黄 2 以上（固まる）」にする（R-E06 の「ほろほろ」は 80〜90℃で、12分の卵がそこまで行くかは分からない）／正解のレシピの時間を延ばす（Exp-15 の固ゆでは 9〜30分）
- 溶き卵を混ぜながらの地図に置いたスクランブルエッグ 6 行: 4 行一致（R029・R034・R037・R038）。R032（230℃・0.24分）は生のまま、R036（175℃・0.75分）は該当なし
- テスト: 固ゆで卵の正解のレシピ（両版）と test_shell_layers の固ゆでの確かめを xfail（strict、理由つき）にした。修正 B の一次遅れの式を確かめていたテストは、球の解を直接 2000 項で計算した値と比べるテストに置き換え、tatsu2019（68℃・28分で中心 67℃）を確かめるテストを足した

### 2026-09-28 夜 余熱（火から下ろした後も卵の中心の温度が上がる）を入れる（変更の前に書いた）

**きっかけ**: 本人の指摘「余熱による火の入りは考えてないよね」（判断は Claude に任された）。Q6 (a) で殻付き卵を球の熱伝導の解にした後、固ゆで卵の正解のレシピ（沸騰12分）が中心 77.5℃・卵黄 2 で該当なしになった。今の計算は加熱の操作が終わった時点で判定しており、取り出した後の温度の動きを持たない。実物では、外側（卵白の層）が中心より熱いまま取り出されるので、熱は中へ移り続け、中心の温度は取り出した後もしばらく上がる（wiki_carryover「heat will continue to migrate inwards from the surface」）。氷水に取るのはこれを止めるため（thermoworks_egg「The ice bath is an important step to halt carryover cooking」、wiki_boiled「immersing the egg in cold water after boiling is a common method of halting the cooking process」）。固ゆでの定義や時間を見直す前に、まず余熱を入れる。**この節は計算を変える前に書いてコミットした。結果に合わせて値を選ばない**（固ゆでを該当させるための値選びはしない）。

**(1) 取り出した後の温度の計算（殻付き卵だけ）**
- 球の熱伝導の解（Q6 (a)）を、後の操作でもそのまま続ける。後の操作では周りの温度と表面の熱の伝わり方が変わる。
- 表面の境界条件は周りの媒体で2つに分ける:
  - **水・蒸気（湯・冷水・氷水）: 表面＝媒体温度（今までどおり）**。水の熱伝達率は空気よりずっと大きく（cengel_egg の例題で 800 W/(m²·K)）、ビオ数 Bi = hR/k ≈ 800×0.025/0.5 ≈ 40 で、表面＝媒体温度の近似が成り立つ。冷水・氷水も同じ扱い（推定。自然対流の冷水では h はこれより小さく、表面は少し遅れて冷える＝余熱をわずかに小さく見積もる側）。
  - **空気（室温に置く・冷蔵庫・オーブン）: 表面から周りへの熱の流れが表面の温度差に比例する条件（ロバン条件、Bi = hR/k）**。今までは空気でも表面＝空気の温度とし、代わりに時間を `air_tau_factor`（4）倍遅くしていた（推定）。この近似では取り出した瞬間に表面が室温まで下がり、余熱を実際より小さく見積もる。殻付き卵では空気のときに `air_tau_factor` を使うのをやめ、Bi で表す。
- **Bi_air = 0.5（推定）**。h = 10 W/(m²·K)（空気の自然対流 5〜25、wiki_htc。約 40〜80℃の卵の表面では放射も数 W/(m²·K) 足される。濡れた殻からの蒸発は入れていない）、k = 0.5 W/(m·K)（卵白 0.52・卵黄 0.34、egg_thermal／0.4〜0.6、coimbra2006）、R = 0.025 m（R²/α=60.5分 と α=1.7×10⁻⁷ m²/s から、Q6 (a) と同じ）。代わりの値 0.25（h=5）・1.25（h=25）は感度として記録するだけにする。
- 計算の仕方: ロバン条件の固有関数 sin(λr)/(λr)（λ cot λ = 1 − Bi の根、各区間を二分法で解く）で展開し、各項を exp(−λ²·dt/(R²/α)) で減衰させる。境界条件が変わった刻み（湯→空気、空気→水）では、今の温度分布を新しい固有関数に射影し直す（積分は閉じた式）。表面＝媒体温度（Bi→∞）では λ=nπ で、今までの計算と同じ式・同じ数値になる（湯の中の計算は変わらない）。
- 変えないもの: 殻付き卵以外（割った卵・溶き卵・器の卵液・肉 など）は1つの温度の一次遅れのままで、形の上で余熱を表せない（中心が周りの温度を越えない）。プリン・茶碗蒸しの余熱は残る問題として記録する。

**(2) 後の操作**
- **置く（室温の空気）**: 今ある `rest(T, time)`（空気）。殻付き卵では (1) の空気の境界条件になる。
- **水に取る**（新しい操作 `plunge(T, time)`）: 氷水 0℃（氷と水の混合）、冷水・流水 15℃（推定。水道水の温度は季節で 5〜25℃）。表面＝水の温度。
- **湯に入れたまま火を止める**（新しい操作 `off_heat(T, time)`）: 湯の温度が T から室温へ時定数 `pot_cooling_tau_min` = 90分（推定、出典なし。代わりの値 45〜180分）で下がる。卵が湯を冷ます効果は入れない。**Exp-15 の重ね合わせには使わない**（湯量・蓋・火を止める時点が行ごとに書かれておらず温度の履歴が決まらない、map_ok=no の理由のまま）。表せるようにするだけ。

**(3) 判定の時点＝食べる時点**
- レシピの最後の操作の後で判定する（今までどおり）。段階（卵白・卵黄）は最高温度で決まり戻らないので、後の操作の中で中心の温度が最高に達した後ならどの時点でも同じ。条件の「中心の最高温度」「〜℃以上の時間」も後の操作の分を含む。
- 後の操作の長さ: 置く 15分・水に取る 15分（thermoworks_egg・wiki_boiled の 15分）。どちらでも中心の最高がその中に入ることをテストで確かめる。
- **後の操作の最高温度（中心の最大）が段階を決める既存の仕組みにそのまま乗る**。新しい判定の規則は足さない。

**(4) レシピに後の手順が書いていないとき**
- **「置く（室温 20℃に 15分）」とみなす**。理由: 冷やす手順が無ければ、卵は殻をむく・盛りつける・食べる間も空気中で冷めるだけで、外側の熱は中へ移り続ける。「すぐ食べる＝余熱なし」は熱が一瞬で消えることになり、物理的に起こらない。氷水に取るのはこれを止めるための手順（thermoworks_egg・wiki_boiled）で、書いていないのは止めていないと読むのが自然。余熱の大きさについては上限の側（火の入りを大きく見る側）になる。参考として、同じ点を「すぐ氷水」にした答えも別の列に出す（集計には使わない）。
- Exp-15 の行の後の手順は `recipes.csv` の `techniques`・`quote` から読み、新しい列 `after_step` に書く: 氷水（ice）／冷水・流水（cold）／書いていない（none）。
- 正解のレシピ（Exp-14）: 温泉卵（68℃30分、R-E08 に後の手順なし）と ゆで卵（沸騰12分、出典なし）は「置く」、半熟ゆで卵（沸騰6.5分、Exp-15 R007「冷水に移す」）は「冷水 15℃に取る」。順番を変えた組の殻付き卵（68℃・100℃で30分）も「置く」。地図「殻付き卵 × 湯の温度 × 時間」の元のレシピにも「置く」を足し、「氷水に取る」の地図を1枚足す。

**(5) 固ゆで卵がまだ該当しない場合**
- 定義（卵黄 3＝80℃ 必須）を出典に照らして見直す。見る出典: wiki_boiled「Hard-boiled ... eggs are boiled long enough for the yolk to solidify」、thermoworks_egg（卵黄は 70℃で固まる）、R-E05・R-E06（soc_sousvide: 70℃で固まる・80〜90℃でほろほろ）。判断は結果の向きでなく出典で書く。

**確かめること**: 全16品の正解のレシピ（両版）、順番を変えた7組、地図、Exp-15 の重ね合わせの一致率（今 20/28）、固ゆで卵の正解のレシピを前後で比べて下の「結果」に書き足す。JS 版も同じ式にして一致テストを通す。

**結果（計算した後に書いた。前後の数は余熱の直前 e497061 の時点の計算と比べた）**

| 見たもの | 余熱の前（e497061 の直前） | 余熱の後 |
|---|---|---|
| 13品の正解のレシピ（状態で止める版／時間の版） | 12/13 ／ 13/13 | 12/13 ／ 13/13（変わらない。温泉卵は 68℃30分→室温 15分で中心の最高 67.3→67.5℃、温泉卵のまま） |
| 追加3品（ゆで卵・半熟ゆで卵・ポーチドエッグ） | 2/3（両版。ゆで卵が該当なし） | **3/3**（両版）。**ゆで卵（沸騰12分→室温 15分）は中心の最高 77.5→88.4℃・卵黄 2→3 で固ゆでに戻った**。半熟ゆで卵（沸騰6.5分→冷水 15℃ 15分）は中心の最高 46.9→63.7℃・卵黄 0 のまま |
| 全16品（両版の計） | 状態で止める版 14/16・時間の版 15/16 | **15/16・16/16**（外れは今までどおり炒め玉ねぎの状態で止める版だけ） |
| 順番・操作を変えた7組（14入力） | 期待どおり 13/14（プリン液 100℃ の既知の xfail） | 変わらない（温泉卵 vs ゆで卵の組は 68℃／100℃ 30分→室温 15分でどちらもそのまま） |
| 地図 殻付き卵（630 マス。元のレシピに「室温に 15分置く」を足した） | 温泉卵 48・半熟ゆで卵 10・ゆで卵 173・該当なし 229・生のまま 170 | 温泉卵 **54**・半熟ゆで卵 **3**・ゆで卵 **190**・該当なし **213**・生のまま 170 |
| 地図 殻付き卵（氷水に取る、新しい） | — | 温泉卵 53・半熟ゆで卵 7・ゆで卵 181・該当なし 219・生のまま 170 |
| 地図 割った卵・溶き卵（混ぜない／混ぜながら）・プリン液 | — | 変わらない（殻付き卵以外の温度の計算は変えていない） |
| Exp-15 の重ね合わせ | 20/28（独立の目安 15/22。固ゆで 1/7・半熟 5/5） | **22/28**（17/22。固ゆで **6/7**・半熟 **2/5**。ポーチ 6/6・スクランブル 4/6・プリン 4/4 は同じ） |

- 取り出した後の中心の上がり方（20℃の卵、沸騰 12分で取り出したとき中心 77.5℃）: 室温に置く（Bi 0.5）で最高 88.4℃（取り出して 5.8分後）、氷水 0℃で最高 83.7℃（2.4分後）、冷水 15℃で最高 83.9℃（2.5分後）。**氷水でも中心は 6℃上がる**（外側の熱が中へ移るのは表面を冷やしても止まらず、止まるのは中へ移る分がなくなってから）。沸騰 6.5分（中心 46.9℃）では 室温に置くで 75.6℃（卵黄 2）、冷水 15℃で 63.7℃（卵黄 0）
- 球の解の射影し直しは、独立に解いた差分法（半径 400 分割）と 0.01℃以内で一致した（tests/test_carryover.py）
- **固ゆで卵は定義（卵黄 3＝80℃ 必須）を見直さずに該当した**ので、(5) の見直しはしていない。後の手順を氷水にしても沸騰 12分は中心の最高 83.7℃で固ゆで。出典の定義（wiki_boiled「boiled long enough for the yolk to solidify」、thermoworks_egg の卵黄 70℃で固まる）は「卵黄 2（固まる）以上」に近く、今の「卵黄 3（ほろほろ、80℃）」はそれより厳しい側。定義を変えるかは、固ゆでが外れる理由として使わなかったので記録だけにした
- Bi_air の感度（採用値は変えていない）: 0.25（h=5）で沸騰12分→室温の中心の最高 89.5℃、1.25（h=25）で 86.9℃。正解のレシピ 16品の答えは 3つの値で同じ。重ね合わせは 0.25 で 22/28、1.25 で 23/28（R002〜R008 の半熟のうち 1 行が半熟に戻る）
- 半熟ゆで卵 5/5 → 2/5 の中身: 後の手順を書いていない R002・R005・R008 を「室温に置く」とみなした余熱で卵黄 2 になった。3 行とも「すぐ氷水に取った場合」は半熟。R002・R005 の出典ページ（Cookbook:Soft Boiled Eggs）は方法の手順の外の Tips に「Running the cooked eggs under cold water will help stop the cooking process」と書いている（任意の助言なので after_step は none のまま）。書いていない＝置く、は結果を見る前に決めた扱いで変えていない

**残った問題（直していない）**
- 殻付き卵以外（割った卵・溶き卵・器の卵液・肉 など）は1つの温度の一次遅れで、余熱を表せない（中心が周りの温度を越えない）。ポーチドエッグ・プリン・茶碗蒸し・鶏むね肉のソテーの余熱は入っていない
- 「書いていない＝室温に置く」で、世の中の半熟ゆで卵のレシピ 3 行が該当なしになった。実際にどれくらいの時間で食べるか・殻をむくかは分からない。置く時間を短くする（食べるまで 1〜2分）根拠の出典は探していない
- 空気の表面の条件（Bi_air）は出典の範囲から置いた推定。濡れた殻からの蒸発（取り出した直後は表面が冷えやすい）は入れていない
- 冷水・氷水も「表面＝水の温度」（Bi→∞）。静かな冷水の自然対流では表面が少し遅れて冷え、余熱は計算より少し大きい
- 湯に入れたまま火を止める（off_heat）の湯の冷え方（時定数 90分）は出典のない推定で、重ね合わせには使っていない（Exp-15 の 5 行は map_ok=no のまま）
- 地図（室温に置く）で、80〜85℃の 7〜9分が温泉卵になった（卵白の層が 80℃に届かず卵白 2、中心は 65〜70℃）。氷水の地図でも 80〜82.5℃の 11〜13分。短い時間で湯から出した卵を温泉卵と呼ぶかは決めていない
- 地図の画像（results/maps/*.png）は撮り直していない。ページの地図で見られる

### 2026-09-29 本人判断（9/28 から保留だった2件）

本人判断 2026-09-29: ① 半熟ゆで卵を料理として足す ② 殻付き卵の白身の固まり方は外側（表面側）の温度で決める。

- **どちらも 2026-09-28 の修正 B（と同夜の Q6）で実装済みで、今回シミュレータ本体・rules.yaml・地図の元データは変えていない**。反映の前後で状態は同じなので、Exp-11 の評価はこの状態（修正 B・Q6・余熱の後）で行う
  - ①: `soft_boiled_egg`（§6 の最後、13品外）。事前に決めた定義のまま。感じ方の採点は無いので、Exp-11 の13品の評価には入らない
  - ②: 卵白の段階は卵白の層の体積平均の温度 `T_white`（球の熱伝導の解）の最高で決める。中心の温度ではない
- 文字どおり「殻の表面の温度（＝湯温）」で決めた場合を感度として計算した（`sensitivity_white_surface.py` → `results/sensitivity_white_surface.md`）。正解のレシピ（両版）と7組の答えは 0/46 で変わらない。殻付き卵の地図は 630 マス中 58 マスが変わり、沸騰した湯に1分で「半熟ゆで卵」になる（湯に触れた表面だけで卵白全体を固まったとみなすため）。温泉卵の3マスが該当なしに変わる。**採用は卵白の層の温度のまま**とし、表面の温度は感度として記録するだけにした（本人の意図が「殻の表面そのもの」なら差し替える）

### 2026-09-30 本人の回答: 白身の固まり方は「決めるものじゃない、自然に従うように」→ Exp-17

- 殻付き卵を2層の球の熱伝導（差分）と変性の一次反応（アレニウス）で解く形を `sim/egg_kinetic.py` に足した（計画・結果は `experiments/exp-17-egg-kinetics/`）。rules.yaml `sim.egg_model` で切り替える。**既定は stage（今の形）のまま**、試せるページも今の形
- 2026-09-29 の「白身は白身の層の温度／殻の表面の温度」の二択は、kinetic では場所ごとの変性度から出るので要らなくなる


### 2026-09-30 Exp-18 の下準備: 肉片の熱伝導と揚げ物の吸油（本人の方針「規則で決めず自然に従わせる」）

- 肉片（form piece）を厚み方向の1次元の熱伝導で解く形を `sim/meat_slab.py` に足した。熱物性は成分から Choi & Okos (1986) の式（ashrae_thermal）、表面の条件は ngadi2007。rules.yaml `sim.meat_model` で切り替える。**既定は tau（今の形）のまま**、試せるページも今の形。フライパンの操作が変わるたびに肉を返す（火加減だけ変えるときは `flip=False`）
- 揚げる間、蒸発した水に比例して油を吸う（`sim.oil_uptake`、比 0.12 は成分表 表12・13 から計算）。**既定は off**
- 計画・結果は `experiments/exp-18-more-dishes/`（plan.md・results/output.md）

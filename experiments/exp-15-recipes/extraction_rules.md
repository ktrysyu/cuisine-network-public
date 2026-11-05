# Exp-15 読み取りの約束事

目的: Exp-14 の計算（湯・蒸気・フライパンの温度 × 時間 × 卵の形 → どの料理になるか）を、世の中のレシピに書かれた条件と照らし合わせるための表 `recipes.csv` を作る。この文書は、原文から表の値を作るときの決まりを書く。

- 読み取りは Claude（モデル ID claude-opus-5-5）が原文を読んで `build.py` の `RECORDS`（`rec(...)`）に手で書いた。本人の確認前。
- `build.py` は各行の引用 `quote` が原文（ダンプ・CSV から取り出した本文）にそのまま在ることを確かめる。無ければ止まる。
- 換算表の id（下の `W-BOIL` など）は `build.py` の `RULES` と同じ。`build.py` はこの文書に全 id が書かれているかも確かめる。

## 1. 何を1行にするか

1. **1 行 = 1 つの手順**。同じページに方法が複数ある（Soft Boiled Eggs の Method 1〜4）、硬さで時間が分かれる（Poaching の 3–4 分／5–6 分）ときは別の行にし、`independence_group` を同じにする。
   別のページでも、同じ書き手とみられるもの（ウィキブックス日本語版の 料理本/ゆで卵 と 料理本/畜産物。最終版の編集者が同じ）は同じ `independence_group` に入れる。
2. 行にするのは、**温度（火力の言葉を含む）か時間のどちらかが書かれている手順**。材料欄に「hard-boiled eggs」とあるだけ、「hard boil the eggs」だけで時間も火力も無いものは行にしない。例外: 茶碗蒸しは見つかったのが1件だけなので、温度・時間が無くても行にした（無いことの記録として）。
3. 料理の分類は原文の料理名・ページ名を優先する。料理名が無いものは原文の語から判断し、`dish_basis` に「推定:」と書く（例: 牛丼の卵 → 温泉卵）。
   - 半熟と固ゆでは原文の語で分ける（soft / runny / jammier / 半熟 → 半熟、hard / fully / 固ゆで / しっかり固まった → 固ゆで）。どちらとも書かれていないゆで卵は行にしなかった。
   - プリン類は「卵で固める甘いカスタードを型ごと加熱して固めるもの」を入れた（焼きカスタード・フラン・クレームブリュレ・蒸しココナッツプリン）。`variant` で区別する。入れなかったもの: 火にかけて混ぜ続けるカスタード（Boiled Custard・Crème anglaise）、デンプンで固めるもの（Spiced Crème Caramel）、パン・米・野菜のプディング、パイ・タルト、チーズケーキ。
   - スクランブルエッグは溶き卵をフライパンでかき混ぜて固めるもの。スープに流す溶き卵、オムレツ、目玉焼きは入れない。電子レンジのものは行にしたが媒体 `microwave` として地図からは外す。
   - ポーチドエッグは湯に割り落とすもの。ソースに落とすシャクシュカは入れない。
4. 英語の原文は `quote` にそのまま残し、単位を換算した値を別の列に入れる。

## 2. 温度の換算表（推定）

原文に数値があるときは `T_stated_c` に入れ（°F は ℃ に直す）、推定の列は空にする。数値が無く、言葉（沸騰・simmer・中火 など）だけのときは下の表で推定し、`T_is_estimate = yes`、`T_rule` に id、`T_est_c`（中心）と `T_est_lo_c`〜`T_est_hi_c`（幅）を入れる。**推定は必ず推定として扱う**（原文の値と混ぜて集計しない。`summary.md` でも分けて数える）。

### 湯・蒸気

| id | 原文の表現 | 推定 ℃（中心／幅） | 根拠 |
|---|---|---|---|
| `W-BOIL` | boil, rolling boil, full boil, return to a boil, low boil, 沸騰 | 100／95〜100 | Wikibooks Cookbook:Boiling「plain water boils at temperatures from about 200°F to 212°F (95°C to 100°C)」（標高・天気で変わる）。海抜 0 m 付近として 100。low boil も沸騰なので同じ |
| `W-SIMMER` | simmer | 90／85〜95 | Wikibooks Cookbook:Simmering「185 to 200 degrees Fahrenheit (85-95 Celsius)」 |
| `W-GENTLE` | gentle simmer, very very gently simmer, 沸騰させない | 85／75〜90 | 推定。Poaching の定義（`W-POACH`）と Simmering の間 |
| `W-POACH` | poach（湯温の指示なし） | 77／71〜82 | Wikibooks Cookbook:Poaching「The ideal temperature is between 160F and 180F (75-80C)」。°F を直すと 71〜82℃ で、ページの ℃ 表記とずれる。°F の方を採った |
| `W-BOIL-POACH` | boiling water に割り落とす（poach と書くが火を弱める指示が無い） | 100／75〜100 | 書かれたとおり 100。poach の語に合わせ下限を広げる。確かさ低 |
| `W-RESID` | 火を止めて蓋・remove from heat・熱湯を注いで置く | 推定しない（上限 100） | 100℃から下がり続ける。湯量・鍋・蓋で下がり方が変わり、一定温度として書けない |
| `W-UNSPEC` | 「茹でる」「boil the eggs」「hard-boil」だけで湯からか水からか・火加減も無い | 100／95〜100 | 推定。沸騰した湯と読む |
| `S-STEAM` | 沸騰した湯の上で蓋をして蒸す、steam | 100／95〜100 | `W-BOIL` と同じ（蒸気は湯の沸点） |
| `S-LOW` | 蒸し器を弱火で | 88／80〜95 | 推定。Exp-14 規則 R-E15（蒸し器内 85〜90℃に保つ、抜粋のみ・確かさ中）を「弱火で蒸す」の狙いとみなした。庫内温度そのものは書かれていない |
| `S-BAIN-STOVE` | 鍋の湯煎（bain-marie）を simmer | 推定しない（上限 100） | 外の湯は `W-SIMMER` でも、中の卵液が受ける温度は書けない |

### オーブン

| id | 原文の表現 | 扱い |
|---|---|---|
| `O-BATH` | 湯煎（water bath / bain-marie / baño de María）でオーブン | オーブンの設定温度を `T_stated_c` に入れる。卵液が受けるのは湯の温度（100℃以下）で、推定しない。Exp-14 の地図（蒸し器の温度×時間）とは媒体が違うので `map_ok = no` |
| `O-DRY` | 湯煎なしでオーブン | 設定温度を `T_stated_c`。推定しない。`map_ok = no` |

オーブンの °F は ℃ に直して整数に丸める（375°F → 191）。原文に ℃ も書かれていればその ℃ を使う（350°F (180°C) は 180）。

### フライパン（すべて推定。根拠が一番弱い）

家庭のコンロの火力の言葉が鍋肌の何℃にあたるかは、コンロ・鍋・油の量で大きく変わる。Wikibooks Cookbook に定義は無い（Cookbook:Cooktop にも無い）。中火だけは Wikibooks 内に数値の用例があるので、それを弱い根拠にした。

| id | 原文の表現 | 推定 ℃（中心／幅） | 根拠 |
|---|---|---|---|
| `P-LOW` | low heat, 弱火 | 130／100〜150 | 出典なし。`P-MED` より下 |
| `P-MEDLOW` | medium-low, low-medium, 中弱火 | 150／130〜170 | Wikibooks Pupusas「low-medium heat (325–350°F)」（鉄板、163〜177℃）を上限側の目安 |
| `P-MED` | medium heat, 中火 | 175／150〜190 | Wikibooks 内の用例: Koesisters「medium heat (180 °C)」（油）、Choripán「medium heat (approximately 350 °F / 175 °C)」（グリル）、Nigerian Egg Roll「350–375°F (medium heat)」（油）。どれも鍋肌の温度ではない |
| `P-MEDHIGH` | medium-high heat, 中強火 | 200／185〜220 | Wikibooks Sesame Shrimp Toast「medium-high heat until it reaches 375°F (190°C)」（油）を下限側の目安 |
| `P-HIGH` | high heat, 強火, turn the flame to high | 230／210〜260 | 出典なし |
| `P-HOT` | hot pan とだけ（火力の指示なし） | 200／170〜240 | 出典なし |
| `MW` | 電子レンジ | 推定しない | 媒体の温度として書けない |
| `NONE` | 温度・火力の記述が無い | — | — |

「バターが溶けて泡立ち、焦げる前」のような見た目の手がかりは `T_raw` に残すが、温度には直していない。

## 3. 卵を入れるときの卵の温度

| id | 原文 | 推定 ℃ | 根拠 |
|---|---|---|---|
| `E-FRIDGE` | 冷蔵庫から出したて・cold eggs | 5（2〜8） | 家庭用冷蔵室の温度の推定 |
| `E-ROOM` | 常温に戻す・room temperature | 20（15〜25） | 推定 |
| `E-NONE` | 記述なし | 空欄 | 推定しない（冷蔵とも常温とも決めない） |

## 4. 時間

- 分に直す（秒は ÷60）。幅は `time_min_lo`〜`time_min_hi`。「about」「ほど」は数値をそのまま使い、`time_raw` に原文を残す。
- 「several minutes」「until done」など数値の無いものは時間を空欄にする。「3 or more minutes」は上限 3 とし `notes` に書く。「2 minutes or more」は下限だけ入れる。
- **数え始め**を `time_counts` に書く（卵を入れてから／再沸騰してから／火を止めてから／水から沸騰までは含まない など）。原文から分からなければ「不明」。
- 2 段の加熱（1 分沸騰→5 分余熱、3 分沸騰→60 分 simmer）は合計を入れ、内訳を `time_counts` に書く。

## 5. 酢・塩

- `vinegar` / `salt`: yes（入れる）／optional（任意と書いてある）／no（書かれていない）。「書かれていない」を「入れない」と区別できないので、no は「手順に無い」の意味。
- 割合は `V-TBSP-L` の決まりで出す: `V-TBSP-L` 大さじ1（15 ml）/ 水1 L ＝ 1.5%。1 tablespoon per liter/quart も 1.5% とした（1 US quart ≈ 0.95 L で 1.6% だが丸める）。量の書かれていない a dash / a splash / 少々、湯量の分からない 1 tbsp は割合を出さない。

## 6. 地図に重ねるための列

Exp-14 の地図（`experiments/exp-14/sim/maps.py` の PRESETS: 殻付き卵×湯の温度×時間、割った卵×湯の温度×時間、溶き卵×フライパンの温度×時間、プリン液×蒸す温度×時間）に重ねられるように、次の列をそろえた。**まだ重ねていない。**

- `map_T_c`: 原文に数値があればその中央、無ければ推定の中心。
- `map_time_min`: 時間の幅の中央。
- `map_egg_form`: shell（殻付き）／cracked（割った卵）／beaten（溶き卵）／custard_mix（プリン液・茶碗蒸し液）。
- `map_ok`: yes／yes（温度は推定）／no。no の理由は `map_note`（余熱で一定温度でない、水から始める、媒体がオーブン・電子レンジ、うずら卵、時間なし など）。
- `after_step`（2026-09-28 夜 追加、Exp-14 rules.md §10「余熱」）: 殻付き卵の後の手順。`techniques` に「氷水」があれば ice、「冷水」「流水」「水で粗熱」があれば cold、どれも無ければ none（書いていない）。殻付き卵以外は空。判定の根拠を `after_basis` に書く（`build.py` の `after_step`）。
- `dish` は Exp-14 の料理 id（`onsen_tamago`, `hard_boiled_egg`, `poached_egg`, `scrambled_eggs`, `custard_pudding`, `chawanmushi`）。半熟ゆで卵は Exp-14 に無いので `soft_boiled_egg` を新しく置いた。

## 7. 出典ごとの読み方

- Wikibooks（英語版・日本語版）: 公式ダンプ（2026-09-01）の最新版の wikitext を読む。行ごとに版番号（`revision_id`）と固定リンク（`permalink`、`?oldid=`）を残す。ページが後で書き換わっても、この版を指せる。
- Hugging Face のスナップショット（gossminn/wikibooks-cookbook）: 公式ダンプから消えたページだけに使う（今回は1件）。版番号は無く、スクレイプ日（2024-07-31）とデータセットのコミットを残す。
- 福井県オープンデータ: CSV（cp932）の行を読む。料理名の列（レシピ名・献立名）で行を特定する。

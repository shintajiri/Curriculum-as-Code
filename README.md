# Curriculum as Code

**学部カリキュラムの正本を構造化データ（YAML）に置き、シラバスの該当欄とカリキュラムマップをそこから生成し、形式の誤りを機械で検査する。**
DP（ディプロマ・ポリシー＝卒業時に求める学修成果の方針）は ID で参照する。名称を変えたら、派生物を全科目分生成し直す。
変更はバージョン管理の差分として残る。

> *Curriculum as Code: keep the source of truth of a degree programme's curriculum in structured data (YAML), generate syllabus fields and the curriculum map from it, and let a machine catch formal errors (dangling references, weights that do not add up). Programme learning outcomes are referenced by ID. Humans keep the educational judgement.*
> English summary: [docs/en/overview.md](docs/en/overview.md)

このリポジトリは**概念と参照実装**です。実在の大学の科目・DP・対応表は含みません。
文書は CC BY 4.0、コードは MIT で公開します。

## なぜ要るか

- 学部を新設すると、**200 を超える科目**からなるカリキュラムを一から作ることになる
- 質保証の観点から、**どの科目で、DP に定めたどの知識・能力を育てるか**を最初から設計したい
- シラバス・CP/DP・カリキュラムマップ・DP 評価の仕様を**別々に管理**すると、共通する情報（DP の名称、科目と DP の対応）を変えるたびに複数の箇所を直すことになり、漏れる
- カリキュラム全体を通して、学生が本当に成長する仕組みにしたい。そのためには、科目と到達目標と評価方法の対応が、人が読める形で一貫していなければならない

## 書き方

```yaml
dp_definitions:
  DP1: <DP項目名>
  DP2: <DP項目名>

courses:
  - id: <科目ID>
    name: <科目名>
    goals: {G1: <到達目標1>, G2: <到達目標2>}
    dp: {DP1: 導入, DP2: 展開}          # DP を ID で参照。値は到達水準（導入／展開／発展 など）
    assessments:
      - {method: レポート, weight: 60, goals: [G1]}   # weight は科目内の評価配分（%）
      - {method: 発表,     weight: 40, goals: [G2]}   # goals は対応する到達目標の ID
```

- `dp_definitions`：DP の ID と名称。**共通定義として1か所に置く**
- `courses[].goals`：科目の到達目標に ID（G1, G2…）を振る
- `courses[].dp`：科目がどの DP にどの水準で対応するかを **ID で参照**
- `courses[].assessments`：評価方法・配分（%）・対応する到達目標 ID

完全な例：[examples/curriculum.example.yaml](examples/curriculum.example.yaml)（プレースホルダー）。スキーマ：[schema/curriculum.schema.json](schema/curriculum.schema.json)

## あると何が変わるか

```
            正本（バージョン管理）                     生成                 検査
 ┌──────────────────────────┐
 │ DP 共通定義：ID と名称      │ ◀── DP を ID で参照 ──┐     ┌──▶ シラバスの該当欄   人：到達目標と評価方法の
 │ 科目定義：到達目標・DP・評価 │ ──────────────────────┴─▶ ──┴──▶ カリキュラムマップ    教育的対応を見る
 └──────────────────────────┘
   機械：参照先の DP ID・到達目標 ID が存在するか、配分が 100% か
```

1. **正本だけ直せばよい。** DP の名称を改めたら、共通定義を直して派生物を全科目分生成し直す
2. **変更が差分として残る。** いつ・誰が・何を変えたかがバージョン管理に残り、審議の記録と突き合わせられる
3. **形式の誤りは機械が見つける。** 共通定義に無い DP を参照している科目、無い到達目標を参照している評価方法、配分が 100% にならない科目
4. **人は教育的な判断に集中する。** 到達目標と評価方法が教育的に対応しているか、DP の水準の置き方が妥当かは、人が判断する

## やらないこと

- 学生の成績・個人情報はこのファイルに入れない。DP の達成度の実績値は、別に管理する学修成果データから計算する
- 評価基準（ルーブリック）と集計規則は、ここでは扱わない。ここで扱うのは科目と DP の**対応の正本**と、その派生物まで
- 「YAML にすれば教育内容が自動で整合する」とは言わない。整合させるのは人で、ここは漏れを見つける道具

## 使い方

```sh
pip install -r requirements.txt
python3 tools/validate.py examples/curriculum.example.yaml      # 形式の検査（終了コード 0 = 問題なし）
python3 tools/generate.py examples/curriculum.example.yaml out/  # シラバス欄（Markdown）とカリキュラムマップ（HTML・CSV）を生成
```

AI エージェント（Claude Code、Codex 等）と組み合わせるときの流れは [docs/workflow.md](docs/workflow.md)。
正本→生成→機械検査→人の承認、という形は、同じ著者の [AcademicOps](https://github.com/shintajiri/AcademicOps) の運用と同型です。

## 背景

高等教育では、学士課程の学修成果（DP）と各科目の対応を「カリキュラムマップ」として整備することが求められています。
生成 AI 時代の学習成果については、DP の構成要素を残して解釈を更新すれば「DP の変更が容易になり、CP も微修正で済む」一方で「個々の授業は大きく変える必要がある」とされ、
各科目の成果物とフレームワークの要素を紐づけるカリキュラムマップの整備を先に進めることが提言されています（高橋哲也, 2026, 第9回 IR 合同シンポジウム）。
このリポジトリが提案するのは、その整備のうち、科目と DP の対応関係を構造化データで管理し、変更を派生物へ反映する部分です。

用例として、GitHub には `curriculum-as-code` のトピックで個人のリポジトリが先にあります。命名の独自性は主張しません。

## 帰属

構想：Shintaro Tajiri（田尻 慎太郎）。学部の新設準備でこの方式を実践しています（その具体はこのリポジトリには含みません）。

## ライセンス

- 文書（README・docs/・examples/・schema/）：[CC BY 4.0](LICENSE-docs.md)
- コード（tools/）：[MIT](LICENSE)

# 設定・記録・正本への反映

導入先のリポジトリで、同梱の [osameru.py](../scripts/osameru.py) を Python 3.8 以降で実行します。以下の `<osameru.py>` は導入先に配置したスクリプトのパスです。変更用ディレクトリは、現在の `feature/<変更名>` ブランチから選びます。ディレクトリを明示するときは、サブコマンドの前に `--change specs/<変更名>` を付けます。`apply` は対応する作業ブランチで行います。

## プロジェクトの設定

導入時に `python3 <osameru.py> setup` で、Playwright、Chrome 拡張、手動テストのいずれかを選びます。非対話では `--method playwright`、`--method chrome-extension`、`--method manual` を使います。`--screen-items on` と `--screenshots on` は、必要な場合に指定します。どちらも初期値は `off` です。`setup` を再実行すると指定した設定だけを更新します。`settings` は有効な設定を表示します。設定ファイルは `designs/nikomi-udon.json` です。設定ファイルがない場合は手動テストを使います。

現在の設定でテストを実施し、結果の確認を記録します。設定を変更した後の反映には、新しい設定での実施と確認が必要です。

計画前の設計承認は、導入時または設定変更時に `setup` の `--design-approval` で選べます。指定できる値は `none`（既定）、`operational`、`pr` です。

## 設計書案のブロック

`shitagaki.md` に、機能別の完成した本文を一つずつ置きます。

```markdown
<!-- osameru-target: {"path":"orders/register.md","base":"new"} -->
# 受注登録 基本設計書

本文
<!-- /osameru-target -->
```

`path` は `designs/specifications/` からの相対パスです。`python3 <osameru.py> base orders/register.md` で、執筆の基にした正本の値を取得します。新規の場合は `new`、既存文書の場合はファイルの SHA-256 を記録します。正本が更新済みの場合は、最新の内容と案を照合してから `base` を取り直します。

画面項目定義書が有効な場合は、`shitagaki.md` のブロック外に `<!-- screen-items: applicable -->` または `<!-- screen-items: not-applicable -->` を一つ記します。対象がある場合は `screen-items.md` に同形式のブロックを置き、反映先には `orders/register.screen-items.md` のようなパスを使います。

## E2E テストの記録と反映

1. テストを開始する直前に `python3 <osameru.py> start-e2e` を実行し、表示された実行 ID を控えます。CLI はテストの定義、プロジェクト設定、作業ツリーの関連ファイルから照合用のハッシュを計算し、前回の結果欄と確認欄をリセットします。報告書から参照するログや画像は PBI 内の `evidence/<実行ID>/` に置きます。テストランナーが作る一時ファイルは、Git の無視対象の場所に出力します。
2. `e2e.md` の各振る舞い ID に、今回観測した結果と合否を記録します。画面キャプチャを有効にし、仕様書に取得箇所を指定した場合は、`evidence/<実行ID>/E2E-01.png` などの画像を証跡欄から参照できるようにします。
3. 必須項目がすべて `OK` となり、担当者が今回の実施内容と結果を確認したら、`python3 <osameru.py> review-e2e --tested <実行ID> --reviewer "<確認者名>"` で、同じ `e2e.md` に確認を記録します。入力を変更した場合は、新しい実行を開始して結果と確認を取り直します。`verify-e2e` は記録を検証します。
4. `python3 <osameru.py> apply --reason "<変更理由>"` で、対象文書と改訂履歴を作業ブランチに反映します。たとえば `orders/register.md` の履歴は `orders/register.history.md` です。`base` と現行の正本が食い違う場合は、設計案を見直します。反映済みの同じ内容で再実行した場合は、履歴を重ねずに終了します。

確認を取り下げるときは、`e2e:review` の開始・終了コメントの間を「未確認」に戻します。再確認する場合は、`start-e2e` で新しい実行を始めます。変更理由を訂正する場合は、`apply` に訂正後の理由を渡すと同じ PBI の履歴が更新されます。

実施済みの結果の記入や確認を再開する場合は、`e2e.md` の `e2e-run` コメントにある `id` を引き継ぎます。`python3 <osameru.py> check-e2e-run --tested <実行ID>` は、実行 ID とテスト時の入力を照合します。結果や確認の記録は更新しません。

テスト仕様書の `e2e:checks` と `e2e:review` の区切りを保ちます。テスト表は振る舞い ID、確認内容、前提・データ、手順、期待結果、キャプチャ取得箇所、実施結果、判定、証跡の順です。セルの改行は `<br>`、セル内の縦棒は `\|` で記します。判定が確定した項目は `OK` または `NG` と記します。

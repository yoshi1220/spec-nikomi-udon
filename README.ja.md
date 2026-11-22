# 仕様煮込みうどん

[English](README.md)

仕様煮込みうどんは、**伝統的日本型開発を支える仕様駆動開発フレームワーク**です。社内の開発標準や承認手続きに沿って、AI を使った開発を進められるようにします。

SIer や日本の伝統的な企業の開発チームを想定しています。たとえば、所定の書式で設計書を作るチームや、リリース前にテスト結果や承認記録を提出するチームです。新規開発と既存システムの改修の両方を対象とします。

## 開発の流れ

1. **仕様を詰める**。要件やプロダクトバックログ項目（PBI）から始めるときは `shikomi`、既存資料から始めるときは `torikomu` を使います。対象範囲、振る舞い、受け入れ条件を一問ずつ確認し、`shikomi.md` に残します。
2. **基本設計を下書きする**。担当者が `shikomi.md` を確認し、必要に応じて修正します。保存した仕様をもとに、`shitagaki` で機能ごとの基本設計書案を `shitagaki.md` に作ります。
3. **計画する**。`dandori` で作業と確認方法を `dandori.md` にまとめます。変更する振る舞いと影響を受ける既存の振る舞いについて、不具合を見分けられる入力と期待結果を対にして記します。E2E テストの手順と期待結果は `e2e.md` にまとめます。
4. **実装して検証する**。`nikomu` で実装し、新規・既存のテストや手動確認で計画どおりに不具合を見分けられるか確かめます。その後、`ajimi`（味見）で E2E テストを実施します。不合格の原因に応じて実装または計画からやり直し、一度再テストしても解決しなければ利用者に対応を求めます。担当者はテストの実施内容と結果を確認し、同じ仕様書に記録を残します。
5. **正本に納める**。`osameru` で合格と担当者の確認を照合し、作業ブランチの `designs/specifications/` に設計書と改訂履歴の更新を用意します。実装と同じ PR でレビューし、マージ時に正本を更新します。

PBI ごとの成果物とその状況は、変更用ディレクトリの `oshinagaki.md`（お品書き）で確認できます。

## 導入方法

### `init` の前に

対象の Git リポジトリで Git 2.23 以降、Python 3.8 以降、`uvx`、使用する Codex または Claude Code を準備します。対象 OS は macOS、Linux、WSL です。macOS と Linux で導入と更新を検証済みです。Windows では WSL のターミナルから実行してください。WSL 実機での確認は未完了です。 [uv のインストール](https://docs.astral.sh/uv/getting-started/installation/)

手動配置した同名スキルがある場合は、事前にスキルのディレクトリを別の場所へ移動します。既存の案件設定 `designs/nikomi-udon.json` は引き継がれます。

### 案件に導入する

導入先の Git リポジトリで、次のコマンドを実行して v0.0.3 を新規導入します。

```sh
uvx --from git+https://github.com/yoshi1220/spec-nikomi-udon.git@v0.0.3 spec-nikomi-udon init
```

v0.0.2 からの移行は手動です。この版では、変更仕様に `shikomi` と `shikomi.md`、実装に `nikomu` を使います。

言語と Codex・Claude Code・両方のいずれかを選びます。Codex には `.agents/skills/`、Claude Code には `.claude/skills/` に同じ版のスキルを配置します。案件設定がなければ E2E 方式、計画前の承認、画面キャプチャ、画面項目定義書を選びます。準備が残る場合もスキルと設定は保存されます。同じ版の `init` で環境準備の再開やエージェントの追加ができます。

この版の導入後に配布スキルを更新するには、上のコマンドの末尾を `update` に変更します。配置したスキル、案件設定 `designs/nikomi-udon.json`、導入記録 `designs/nikomi-udon-install.json` を案件の Git に含め、チームで共有します。Git の除外設定に該当するファイルがあれば、インストーラが件数とパスの例を表示します。`git check-ignore -v -- <パス>` で該当ルールを確認し、共有する配布ファイルが Git に含まれるようにします。配布スキルを直接編集した場合はその変更を退避して元の配布状態に戻し、更新後に必要な変更を再反映します。

### `init` の後に

設定を変更するときは、案件内で `python3 .agents/skills/osameru/scripts/osameru.py setup` に変更したい項目のオプションを付けます。Claude Code のみの場合は `.claude/skills/` を使います。 [設定オプション](japanese/skills/osameru/references/format.md)

| 選んだ方式 | 必要な準備と確認 |
| --- | --- |
| Playwright | 既存のランナーを優先します。準備が必要なら表示されるコマンドを確認して実行を選びます。OS 依存や対象プロジェクトの追加設定が必要な場合は整備後に同じ版の `init` を再実行します。初期確認は Chromium で行います。たとえば npm 案件では `npm install -D @playwright/test` と `npx playwright install chromium`、uv 管理の Python 案件では `uv add --dev pytest-playwright` と `uv run playwright install chromium` を使います。 [ブラウザの準備](https://playwright.dev/docs/browsers) |
| エージェントのブラウザ操作 | Codex デスクトップでは内蔵ブラウザを利用できる状態にします。Claude Code では公式 Chrome 拡張を設定し、`/chrome` で接続を確認します。必要なサイト権限を許可し、対象環境へログインします。両エージェントを使った実案件での通し検証は未完了です。利用するセッションで対象画面を操作し、期待値を読み取れることを確かめてください。WSL で Claude Code を使う場合は Playwright または手動など利用可能な方式を選びます。 [Codex](https://learn.chatgpt.com/docs/browser)／[Claude Code](https://code.claude.com/docs/en/chrome) |
| Chrome 拡張 | 案件の期待結果を判定できる拡張を導入し、テスト対象のサイトへのアクセスを設定します。 |
| 手動テスト | 担当者がテスト対象の環境にアクセスし、指定データを使って、観測結果と合否を記録できるようにします。 [E2E 手順](japanese/skills/ajimi/references/run-e2e.md) |

Playwright の依存管理方式が特定できない場合は、案件の管理ツールでランナーと Chromium を準備します。Python の `requirements.txt` を使う案件でランナーの導入が必要な場合は、環境構築を選ぶと、そのファイルの依存関係と `pytest-playwright` をまとめて `.venv` にインストールします。既存のバージョン指定や制約も適用されます。ランナーを新しく追加した場合は、ほかの開発者も再構築できるよう、案件のテスト依存一覧に記録してください。

計画前の設計承認に `pr` を選び、GitHub CLI で照会する場合は、`gh` を用意し、対象リポジトリと PR を参照できるよう認証します。 [PR の照会手順](japanese/skills/dandori/references/design-approval.md)

導入先のプロジェクトでセッションを始めます。一件の変更仕様を作るには、Codex では `$shikomi`、Claude Code では `/shikomi` と入力します。E2E テストでは `$ajimi` または `/ajimi` を使います。

要件資料や説明からシステム全体を整理するときは `kondate`（献立）を使います。目的・主要機能・共通の制約は `designs/system-overview.md` に、プログラムの配置は `designs/repository-structure.md` にまとめます。個別の変更で何に取り組むかを相談するには `saguru` を使います。

### 計画前の設計承認

`dandori` は確認済みの `shikomi.md` を必須とし、`shitagaki.md` があれば計画に使います。計画に進む前の承認方式はプロジェクト単位で選びます。たとえば、Codex の導入先で PR レビューを使うには、次のコマンドを実行します。

```sh
python3 .agents/skills/osameru/scripts/osameru.py setup --design-approval pr
```

| 設定値 | 計画に進むタイミング |
| --- | --- |
| `none`（既定） | 仕様の確認が済めば計画に進めます。設計レビューは実装と一緒に最終 PR で行えます。 |
| `operational` | 利用者が案件の手続きで設計承認を得てから `dandori` を起動します。起動時に承認を再確認する操作はありません。 |
| `pr` | `dandori` が設計レビュー用 PR を照会し、手元の設計書案が承認済みの内容と一致すれば、マージ前でも計画に進めます。 |

`pr` で承認を確認できない場合、`dandori` は理由を示して続行するか尋ねます。続行を選ぶと、確認できなかった項目と判断を対象 PBI の `dandori.md` に記録します。緊急対応などで事前承認を省く場合は、プロジェクトが指定した担当者から例外の承認を得て、省略理由と承認を得た旨を同じファイルに残します。 [設計レビュー用 PR の指定と例外の手順](japanese/skills/dandori/references/design-approval.md)

## 案件の基本設計書式を使う

初回の `init` で `designs/basic-design.template.md` と `designs/basic-design-writing.md` が用意されます。両方を案件の Git で共有します。チームはテンプレートの標題・見出し・表を編集できます。次に `okosu`、`shitagaki`、`koromogae` がその書式を使う際に、変更に合わせて作成方針を更新します。

本体を更新しても案件の書式と作成方針を引き継ぎます。同梱の標準書式に変更があれば、更新時に表示する差分を確認し、採用する変更を案件のテンプレートに取り込みます。同梱の標準書式は導入先の `shitagaki/assets/basic-design.template.md` にあります。

既存の設計書は次の作成・改修で新しい書式を使います。まとめて揃えるには、Codex で `$koromogae`、Claude Code で `/koromogae` を実行します。既定では対象全件を一つの文書PRにまとめ、利用者が指定すれば業務や機能ごとに分けられます。移行前後の差分で設計内容と手修正を確認し、マージ時に正本を更新します。 [衣替えの手順](japanese/skills/koromogae/SKILL.md)

## 既存案件で現行の設計書を起こす

既存リポジトリで Codex なら `$okosu`、Claude Code なら `/okosu` を使います。初回は現在のコミットから始めます。調べるブランチ、タグ、コミットを指定することもできます。 [okosu の手順](japanese/skills/okosu/SKILL.md)

1. `designs/system-overview.md` でシステム全体の機能と関係を確認します。確認状態、選んだ範囲、調査に使ったコミットも同じファイルに残るため、別セッションで再開できます。
2. 改修対象と影響する機能、またはシステム全体を選ぶと、現行の基本設計書が `designs/specifications/` に作られます。
3. 導入専用の文書 PR で、対象版のコード・設定・既存テストと文書を照合します。実動作でしか分からない箇所は未確認として残します。マージ後、共有ブランチの設計書を正本として参照し、最初の改修を起票します。

## 新規開発で最初の機能を作る

既定の承認方式（`none`）で、メモアプリの最初の機能を作る例です。Codex のセッションには、`$` で始まる行を上から一つずつ入力します。`#` の行は各スキルの説明です。Claude Code では先頭の `$` を `/` に置き換えます。

```text
# アプリ全体の目的と主な機能を designs/system-overview.md にまとめる。
$kondate 作業メモを保存し、一覧から見返せるアプリを作りたいです。

# 作業ブランチを作り、対話で決めた仕様と受け入れ条件を shikomi.md に残す。
$shikomi タイトルと本文を保存し、一覧にタイトルを表示。タイトルが空なら入力を促し、保存しない。

# 合意した仕様から、メモ登録機能の基本設計書案を shitagaki.md に作る。
$shitagaki

# 実装する順序を dandori.md に、E2E テストの手順と期待結果を e2e.md にまとめる。
$dandori

# 計画に沿って実装し、各作業の進捗と検証結果を dandori.md に記録する。
$nikomu

# 実際のアプリで登録と入力エラーを試し、期待どおりに動いたかを e2e.md に記録する。
$ajimi

# 必須テストの合格と担当者の確認を照合し、作業ブランチの設計書と改訂履歴を更新する。
$osameru 変更理由は「メモ登録機能を追加するため」です。
```

`shikomi` の対話で仕様と受け入れ条件に合意し、`shikomi.md` を確認したら、同じ作業ブランチで続けます。実装する前に、`specs/<変更名>/` の基本設計書案 `shitagaki.md`、計画 `dandori.md`、E2E テスト仕様書 `e2e.md` を確認します。

必須 E2E テストがすべて合格し、担当者の確認が `e2e.md` に記録されたら `osameru` を実行します。実装と設計書を同じ PR でレビューし、マージすると正本が更新されます。

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) で公開しています。

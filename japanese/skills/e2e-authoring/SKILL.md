---
name: e2e-authoring
description: specs/*/e2e/ またはルート e2e/ のテストを作成・更新するときに使う。仕様の期待結果を待つアサーションと、結果 ID・取得場面に対応する画面証跡をテストに組み込む。
---

# 仕様の期待結果を確認してから撮影する

`specs/<変更名>/e2e/` のテストを書くときは、同じ PBI の `e2e.md` を読む。ルート `e2e/` のテストを書くときは、`moritsuke` が現行の正本をもとに作ったシナリオを読む。テスト名に安定したケース ID を含め、撮影する場面ごとに、何が表示されれば期待結果を確認できるかを記す。

- 操作後は、今回のデータを識別できる行、確定したステータス、正確なエラー文などを、対象画面内で再試行するアサーションで待つ。画面遷移が仕様なら遷移先の URL も確認する。同じ URL で更新される一覧やダイアログでは、更新後の内容を直接待つ。操作前から期待値が表示されている場合は、その操作で初めて現れる注文番号や更新値などを検証に使う。クリック完了、固定秒数、通信完了、共通ヘッダーの表示だけでは撮影しない。
- 期待値の確認は常に実行する。案件の `screenshots` が有効でシナリオに取得場面がある場合は、確認直後、次の操作の前に撮影する。案件の既存ヘルパーを優先し、撮影ごとに保存完了を待つ。
- 撮影が有効な場面のテストを作成・変更したら、試行で保存した画像を開き、今回の識別子と期待する表示が読めることを確かめる。対象の行が画面外にある場合は、行が見える位置までスクロールするか、その行を直接撮影する。確認する箇所が離れていれば、分けて撮影し、それぞれの画像を同じ結果 ID にひもづける。
- 実行側から今回の証跡ディレクトリをテストへ渡す。既存の受け渡しがなければ `NIKOMI_E2E_EVIDENCE_DIR` に絶対パスを設定する。撮影しない実行では設定しない。ファイル名にはケース ID と場面を使い、複数ブラウザ・並列実行で結果が別なら保存先も分ける。同じ結果・場面の再撮影は上書きできる。リンクには今回の試行で保存が成功した画像だけを使う。期待値の不一致、スキップ、撮影失敗時はその事実を記録する。失敗診断用の画像は合格証跡と区別する。

たとえば、受注を登録して受付番号を確認する Playwright Test のテストでは、次の順に書く。`evidenceDir` は今回の実行側が準備した保存先とする。

```ts
await page.getByRole('button', { name: '登録' }).click();
await expect(page).toHaveURL(/\/orders\/complete$/);
const receipt = page.getByRole('region', { name: '受付結果' });
const number = receipt.getByTestId('receipt-number');
await expect(number).toBeVisible();
await expect(number).toHaveText(orderNumber);
if (evidenceDir) {
  await receipt.screenshot({ path: path.join(evidenceDir, 'E2E-01-receipt.png') });
}
```

Python の同期 API では同じ順に `expect(locator).to_be_visible()` と `expect(locator).to_have_text(order_number)`、`receipt.screenshot(path=...)` を使う。非同期 API ではアサーションと撮影の両方を await する。旧表示が少し残るケースでも意図した内容を撮れること、期待値に到達しない場合はその場面の成功画像が報告されないことを確かめる。

案件に `.agents/skills/e2e-authoring/` が導入されていれば、テストの初回作成・更新時に、対象の `e2e/` 直下で有効な `AGENTS.override.md` または `AGENTS.md` に、このディレクトリのテストを編集する際に `$e2e-authoring` を読む旨を一度だけ追記する。どちらもなければ `AGENTS.md` を作る。既存の指示を保つ。 有効な指示が対象ディレクトリの外を参照するシンボリックリンクなら、リンクを保持し、テスト作成工程からこのスキルを直接参照する。

# 検討中の関係を照会する

同梱の [work_graph.py](../scripts/work_graph.py) を Python 3.8 以降で実行する。実行ごとに作業ツリー外の OS 一時領域に専用ディレクトリを作る。対象案件のディレクトリで実行し、helper には導入されたスクリプトのパスを設定する。

```sh
helper=/path/to/dandori/scripts/work_graph.py
project=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P) || exit 1
scratch=$(python3 -B "$helper" scratch-dir "$project") || exit 1
graph="$scratch/work.graphml"
printf '%s\n' "$graph"
```

最初の `update FILE` または `tasks FILE` で案件のデータを渡して作成する。以降の差分は `update FILE --existing` で反映する。ファイルが見つからない場合は、仕様・計画とそのセッションで確認した事実から全体を組み直してから照会する。

- 一度作ったパスを同じ検討中の呼び出しで使い回す。別のシェルでは、出力された絶対パスを `graph` に設定し、片付けには `scratch=${graph%/*}` を使う。以下の操作は GraphML のパスを最初の引数に取る。
- `update` は標準入力の JSON 差分を反映する。ノードと辺はそれぞれ安定した空白なしの ID を持つ。作業・条件・振る舞いで元の ID が重なる場合は、追加するノードに `criterion/1` などの内部 ID を付け、元の ID は属性に保持する。依存関係を加える差分の例は `{"nodes":{"D1":{"kind":"decision","state":"Missing"},"D2":{"kind":"decision","state":"Partial"}},"edges":{"E1":{"source":"D1","target":"D2","kind":"requires"}}}`。各フィールドは文字列で、指定した項目だけを更新し、`null` で項目を外す。辺には `source`、`target`、`kind` が必要。根拠や適用条件も辺に付けられる。`drop_edges`・`drop_nodes` に削除する ID の配列を渡す。辺が残るノードの削除はエラーになる。書き込みエラーの後は照会を止め、入力を直して再実行する。
- `show FILE D1 D2` は指定したノードの状態と、それに接する辺を返す。`affected FILE D1 --via requires` は起点から直接・間接に届く ID を一度ずつ返す。複数の関係名も指定でき、逆向きにたどるには `--reverse` を加える。
- `order FILE requires` はその種類の辺だけで循環を検査し、全ノードを前提順に返す。`ready FILE requires --kind decision` は論点に絞り、直接の前提がすべて Clear / Resolved の Missing / Partial を返す。結果は質問候補として、適用条件、調査待ち、保留理由、ラウンドの規則と照合する。
- `tasks FILE` は `id` と `depends_on` を持つ作業配列を標準入力から検証し、その入力順で循環のない作業専用グラフを丸ごと作り直す。`--print-order` を付けると保存に成功した実行順も返す。作業以外のノードや属性を加えるときは、その後に `update FILE --existing` を使う。

利用者への質問や成果物には業務上の内容を使う。完了・中断・エラーによる終了では、通常の保存手順を済ませ、作成した一時ファイルを `rm -f "$graph"`、空の専用ディレクトリを `rmdir "$scratch"` で片付ける。再開は仕様・計画など各工程の記録から始める。異常終了などで古い一時ファイルが残っても引き継がない。

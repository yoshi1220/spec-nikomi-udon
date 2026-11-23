# Query relationships during a working session

Run the bundled [work_graph.py](../scripts/work_graph.py) with Python 3.8 or later. Give each run its own directory in the OS temporary area outside the worktree. Run the setup from the target project and set helper to the installed script’s path.

```sh
helper=/path/to/plan-implementation/scripts/work_graph.py
project=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P) || exit 1
scratch=$(python3 -B "$helper" scratch-dir "$project") || exit 1
graph="$scratch/work.graphml"
printf '%s\n' "$graph"
```

Create the file from the current analysis with the first `update FILE` or `tasks FILE`. Apply subsequent deltas with `update FILE --existing`. If the file is missing, rebuild the complete graph from the specification or plan and facts established during this session before querying it.

- Keep the same path throughout the current analysis. In a fresh shell, set `graph` to the printed absolute path and use `scratch=${graph%/*}` for cleanup. The operations below take the GraphML path as their first argument.
- `update` applies a JSON delta from stdin. Give nodes and edges stable IDs without whitespace. When a task, criterion or behavior shares a source ID, qualify the added node (for example, `criterion/1`) and keep the source ID in a field. For example, a dependency can be added with `{"nodes":{"D1":{"kind":"decision","state":"Missing"},"D2":{"kind":"decision","state":"Partial"}},"edges":{"E1":{"source":"D1","target":"D2","kind":"requires"}}}`. Fields contain strings. Supply only changed fields and use `null` to clear a field. Each edge needs `source`, `target` and `kind`; it can also carry evidence and applicability conditions. Supply ID arrays in `drop_edges` and `drop_nodes` for removals. Removing a node with remaining edges fails. After a failed write, correct the input and retry before querying the graph.
- `show FILE D1 D2` returns the selected nodes and their incident edges. `affected FILE D1 --via requires` returns each direct and transitive successor once. Supply multiple relationship types if needed, or add `--reverse` to traverse incoming edges.
- `order FILE requires` checks for cycles using only that edge type and returns all nodes in prerequisite order. `ready FILE requires --kind decision` returns Missing / Partial decision nodes whose immediate prerequisites are all Clear / Resolved. Apply the interview's applicability, investigation, hold and round rules to these candidates.
- `tasks FILE` validates a task array with `id` and `depends_on` from stdin and replaces the entire graph with the acyclic tasks in input order. Add `--print-order` to return the execution order after the write succeeds. Add other nodes or attributes with `update FILE --existing` afterward.

Keep questions and deliverables in domain terms. On completion, interruption or an error that ends the session, follow the normal recording procedure, then remove the temporary file with `rm -f "$graph"` and the empty directory with `rmdir "$scratch"`. Resume from the skill's specification, plan or other established records. Start fresh even if a crash left an earlier working file behind.

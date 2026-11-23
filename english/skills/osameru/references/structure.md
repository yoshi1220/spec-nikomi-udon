# Maintain canonical structure and revision history

Use the installed [osameru.py](../scripts/osameru.py) from the project worktree. Use the [GraphML query helper](../../dandori/references/work-graph.md) for read-only `show`, `order` and `affected` on these persistent files. Its scratch-file cleanup applies to temporary analysis only.

| Under `designs/specifications/` | Contents |
| --- | --- |
| `structure/current.graphml` | Current functions and categories, containment, directed functional dependencies and explicit document references |
| `structure/index.json`, `structure/hierarchy.md` | Actual Markdown path, heading and section digest by fixed ID, and a generated hierarchy |
| `structure/notes/<ID>.md` | Optional human-written explanation. The hierarchy renderer carries it with the ID. Review wording that assumes a former location |
| `history/changes.graphml` | Change vertices connected to before/after occurrences, including old locations, surrounding relations and ancestors |
| `history/nodes/<ID>.json` | Complete revision entries with original event and node, inherited content and sources |
| `history/retired/<ID>/<commit>.md` | The retired section as read from that Git revision. Find its archive path, commit, old path and fixed ID on the before occurrence |

## Identity and review

Give each independently changeable function or specification a stable ID. Choose meaningful aggregation for the system, for example System → Orders → Entry. Put a marker immediately after the ATX heading of every identified section. For a headingless document, place the marker on its first line. For a headingless document with YAML front matter, place its marker immediately after the closing delimiter. When the front matter introduces a marked heading, its metadata belongs to that first section. A document may contain several identified sections. Unmarked subheadings belong to their enclosing marked section. Decide whether to split a file based on readability and how often its functions change independently.

Keep the ID on moves and renames. A change to an ancestor’s name or position also appears in the histories of descendants whose hierarchy path changes. For a split, keep the ID with the surviving scope (possibly the common parent). If that misrepresents the previous scope, give the successors new IDs and preserve the origin in history. For absorption, retain the receiving function's ID. Give a newly combined function a new ID. Choose the destination of each prior revision by its actual scope. Copy common entries to each affected node with their origin; on consolidation the same original revision appears once. Preserve the original text and source of an ambiguous old revision on the confirmed parent and note its uncertain child scope. Archive a removed documented node before dropping it, including when its successors have new IDs.

Review a routine change against the top-level categories, including a possible new category or function at the root. Follow affected calls, data and document references. Keep a whole-function relation on the common parent and retarget a child-specific relation to that child. If scope is unclear, widen the investigation and consider a full review. Resolve the actual dependencies before applying. Show the alternatives and ask the user when the evidence cannot settle them. Obtain the user's approval for reorganizing an existing hierarchy or splitting specification files. For a full rebuild review all nodes and relations, review the diff by function, then merge the complete set together. If another change lands, reconcile it and review affected judgments again. Revisit the full set if the impact is unclear or the classification premise changes.

## Prepare a change

In a PBI, save `structure-plan.json` beside `shitagaki.md`. Include both files in the design PR so reviewers can inspect the plan alongside the draft. Prepare both before design approval and E2E. For a change that only updates relationships or removes an entire document, describe it in the draft and bind the plan. Include a target block only for a document that has a new body. Put the complete updated documents into the ordinary osameru target blocks. Use the project template and preserve existing fixed IDs. Record a digest of the plan in the reviewed draft (see below). For onboarding and documentation-only reorganization, prepare the plan in the worktree and supply complete proposed files under `documents`. Review the resulting diff before merging. Only shared-branch merge updates the shared canonical specification.

Example plan for the first two nodes (use the actual commit as `revision` for onboarding):

```json
{
  "event": "orders-baseline",
  "reason": "Document order entry from the inspected implementation",
  "base": "new",
  "graph": {
    "nodes": {
      "orders": {"label": "Orders", "status": "group"},
      "order-entry": {"label": "Order entry"}
    },
    "edges": {
      "orders-entry": {"source": "orders", "target": "order-entry", "kind": "contains"}
    }
  },
  "documents": {
    "orders/entry.md": {"base": "new", "text": "# Order entry\n<!-- spec-node: order-entry -->\n\nThe operator enters an order.\n"}
  }
}
```

- `event` identifies one operation. Reuse an event ID only to retry the same change in its original PBI or documentation workflow. Node and event IDs use letters, digits, hyphens and underscores, start with a letter or digit and have at most 96 characters. Prefer lowercase for portable paths.
- For a PBI, run `python3 <osameru.py> structure-plan-digest specs/<change>/structure-plan.json` and paste the printed marker outside the target blocks in `shitagaki.md`. Run `structure-preview` to preview the draft blocks and plan together. The digest uses LF line endings so a Git checkout can convert line endings without invalidating the marker. Refresh it and review the new draft if the plan changes.
- Capture `base` with `python3 <osameru.py> structure-base` **before** preparing the change. Capture each document base with `base orders/entry.md`. A normal body change can omit `graph`. Set `revision` to the full inspected Git commit for the initial baseline. Its first entries record when the current implementation was observed. Import existing documented history; for code-only onboarding start with the observed revision.
- `graph` is a delta. Nodes carry a label and optional status (`documented` by default, `group`, or `undocumented` for a known function awaiting text). Edges carry source, target and kind: `contains` (parent to child), `calls` (caller to callee), `transfers` (sender to receiver), `depends` (consumer to prerequisite), or `references` (referring text to referenced function). Add an `evidence` string with the supporting path and heading or symbol. Reuse an edge ID to retarget it. Use `drop_edges` and `drop_nodes` arrays for removals. Include all rewired edges in the same event. The containment edges must form a forest, with at most one parent per node.
- The plan's `documents` map is optional. Use full UTF-8 text or `null` to remove the old file, with its exact base. A target in the PBI design blocks already supplies this information. Give a target only once. For a manual move/edit, list the reviewed old and new paths in the optional `refresh` array. The CLI discovers the actual sections on disk. For a rename that changes only letter case on a case-insensitive volume, rename the file on the documentation branch and list both spellings in `refresh`. A sibling `NAME.screen-items.md` is indexed with its design and changes its node revision. For a documentation-only change, include new, edited or removed screen item files for an already indexed design in `documents`, or list the reviewed files in `refresh` when editing them directly. Include newly indexed or edited screen item files in the PBI’s reviewed screen item blocks. For a different name or location, set the owning node’s `screen` field to the exact relative path, including letter case. Reassigning a node to an already indexed, unchanged screen requires only the graph change. Review the entire working diff so unrelated edits are kept out of the change. Markdown under `history/`, `structure/` and old sibling `*.history.md` files are excluded from the current index. Use the full commit containing the last indexed text for retirement. It defaults to HEAD.
- For a PBI that edits a node explanation, put its complete text in the plan’s `notes` map keyed by node ID (use `null` to remove it). This binds the explanation to the reviewed draft.
- `inherit` accepts rules such as `{"from":"order-entry","to":"domestic-entry","entries":["order-entry/orders-baseline"]}`. Select entries by their stored `origin/event`, or use `"*"` when the whole history applies. Use separate rules for the domestic and overseas successors of a shared revision. Use the same mechanism with several sources when merging functions. The original content and origin remain in each recipient's history.
- To import a previous per-document history, use `legacy` rules with `path`, SHA-256 `base`, destination `to`, optional exact `text` excerpt and a `scope` explanation. Omit the excerpt to import the whole file. Record ambiguous entries on the confirmed parent. Inspect the source before and after migration and verify that every entry can be found from its new node(s).
- For onboarding or a documentation-only update run `python3 <osameru.py> structure PLAN --preview`, then `structure PLAN`. For a PBI use the existing E2E review and `apply --reason` with the reason in the plan. Both routes update documents, node histories and graphs in the worktree. Use `structure-check` and inspect the diff, including inherited entries and the old/new relations of each split. Query the history vertex named `change/<event>` and its adjacent occurrences to follow one change.
- For ordinary resumption, inspect the worktree and run `structure-resume` if a write was interrupted. It reconciles before/after content and completes pending writes. When a file matches neither version, retain the interrupted worktree, reapply the reviewed change in another worktree from the original revision, and compare the two, incorporating manual edits. If an interrupted process left a workflow lock, verify that its recorded process has ended before moving the stale lock aside. An identical completed plan can be retried without adding another revision.

To investigate a former ID, use `show history/changes.graphml ID` with the query helper from the canonical directory. Follow the `occurrence` edges to the before/after records; `show` on an occurrence also returns its change vertex and incident dependencies.

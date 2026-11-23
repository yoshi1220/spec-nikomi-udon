# Prepare or resume execution

## Cross-check the specification and plan

1. Read the target `shikomi.md` and `dandori.md` and confirm the plan points to this specification. Proceed when the first line of `shikomi.md` is `<!-- shikomi-review: confirmed -->` and nothing unconfirmed blocks implementation or acceptance verification. If confirmation is needed, identify the relevant passage and what the user needs to confirm, then return to clarification.
2. If the plan has a status marker, require exactly one marker on the first line, `<!-- dandori-plan: ready -->`. Return to planning if it is pending or invalid. For a legacy plan without a marker, use the same content checks below to establish whether it is ready.
3. Check that the plan matches the current specification. Look for duplicate task or criterion IDs, unknown references, tasks listed before their prerequisites, and criteria without a verification method. If the order, task scope, or verification method needs revision, identify the affected IDs and return to planning. If unit-level behavior is in scope but the plan lacks a mapping to unit tests, an execution method, or coverage scope, fill those gaps through `plan-implementation`.

When technical context affects the work, read the relevant sections of `designs/technical-context.md` if available and check the implementation and verification assumptions. If a difference changes task scope or how a check must run, cite the affected IDs and evidence and return to planning.

If subtasks are present, check that their IDs match their parents and are unique. A parent can be complete only after every subtask is verified. If a parent is checked off while a subtask is unfinished, review the parent and dependents using [Recover and finish](recover-and-finish.md).

Load parent tasks from the current plan in recorded order with `tasks FILE --print-order` in the [temporary GraphML operations](../../plan-implementation/references/work-graph.md), then compare its output with the plan order before adding other nodes. Add acceptance criteria from the verification table and link each required task to its criterion with `verifies`. Rebuild from the current plan and verification table on resume.

## Resume a change in progress

- Read the relevant project instructions, system guidance, existing specifications, code, and tests. Inspect the worktree to identify partially implemented work, completed changes, and unrelated edits. Preserve existing work and ask if overlapping edits cannot be reconciled safely.
- Read completed tasks and recorded passes. Check whether the code, prerequisite results, and verification procedures behind them still apply. If a later change affects the evidence or its validity cannot be established, update the record as described in [Recover and finish](recover-and-finish.md) and re-run the affected checks.
- When `run-feature-e2e` reports a failure, treat the behavior ID, expected result, and observation as current evidence. Identify affected tasks and acceptance criteria, including completed work, and update their records using the preceding guidance.
- If `run-feature-e2e` reports missing automated cases or a missing run command, reopen verification for those IDs even in a completed plan. For tests in an older location, preserve existing callers and make the relevant cases runnable from this PBI’s `e2e/`. Verify the command.
- Carry forward valid results and resume with the first unfinished task whose prerequisites are satisfied. For partial implementation, use the task's completion check to determine what remains. Continue verifying pending or reopened acceptance criteria even when every task is checked off.

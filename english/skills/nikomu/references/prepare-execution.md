# Prepare or resume execution

## Cross-check the specification and plan

1. Read the target `shikomi.md` and `dandori.md` and confirm the plan points to this specification. Proceed when the specification contains `<!-- shikomi-review: confirmed -->` and nothing unconfirmed blocks implementation or acceptance verification. If confirmation is needed, identify the relevant passage and what the user needs to confirm, then return to clarification.
2. If the plan has a status marker, require exactly one marker on the first line, `<!-- dandori-plan: ready -->`. Return to planning if it is pending or invalid. For a legacy plan without a marker, use the same content checks below to establish whether it is ready.
3. Check that the plan matches the current specification. Look for duplicate task or criterion IDs, unknown references, tasks listed before their prerequisites, and criteria without a verification method. If the order, task scope, or verification method needs revision, identify the affected IDs and return to planning.

Load tasks from the current plan in recorded order with `tasks FILE --print-order` in the [temporary GraphML operations](../../dandori/references/work-graph.md), then compare its output with the plan order before adding other nodes. Add acceptance criteria from the verification table and link each required task to its criterion with `verifies`. Rebuild from the current plan and verification table on resume.

## Resume a change in progress

- Read the relevant project instructions, system guidance, existing specifications, code, and tests. Inspect the worktree to identify partially implemented work, completed changes, and unrelated edits. Preserve existing work and ask if overlapping edits cannot be reconciled safely.
- Read completed tasks and recorded passes. Check whether the code, prerequisite results, and verification procedures behind them still apply. If a later change affects the evidence or its validity cannot be established, update the record as described in [Recover and finish](recover-and-finish.md) and re-run the affected checks.
- When `ajimi` reports a failure, treat the behavior ID, expected result, and observation as current evidence. Identify affected tasks and acceptance criteria, including completed work, and update their records using the preceding guidance.
- If `ajimi` reports missing automated cases or a missing run command, reopen verification for those IDs even in a completed plan. For tests in an older location, preserve existing callers and make the relevant cases runnable from this PBI’s `e2e/`. Verify the command.
- Carry forward valid results and resume with the first unfinished task whose prerequisites are satisfied. For partial implementation, use the task's completion check to determine what remains. Continue verifying pending or reopened acceptance criteria even when every task is checked off.

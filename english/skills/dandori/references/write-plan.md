# Write and verify the plan

## Record the execution list

- Keep the link to `nikomi.md`. Describe the affected areas, implementation patterns to follow, and code to reuse.
- List tasks in the order produced by the helper. For each task, record a checkbox, task ID, the result it provides, IDs and reasons for direct prerequisites, related acceptance criterion IDs, and a completion check. Use “None” for a task without prerequisites.
- Give each acceptance criterion one row with the required task IDs, test or manual setup and steps, and expected result. If existing behavior suffices, name the existing test or procedure. Mark new results as pending.
- Readers can follow the graph through the prerequisites in the task list. A separate dependency document is unnecessary.

## Update an existing plan

At the start of replanning, save the first-line marker as `<!-- dandori-plan: pending -->` while preserving the plan body and results. Insert the marker on the first line of a legacy plan without one. If an unresolved prerequisite interrupts replanning, leave the marker pending and explain what blocks execution.

Compare it with the previous plan. Keep completion and verification evidence where the work, completion checks, and underlying evidence remain valid. Reordering alone does not change completion. When changes affect a task or its prerequisite results, follow the edges to determine which downstream checks and results remain valid. Reopen affected tasks and mark affected acceptance criteria for re-verification with the reason. If retaining older evidence for reference, make the need for re-verification visible.

## Check the plan before and after saving

1. The task list follows the helper's output and contains every task exactly once. For each task, check that its prerequisite IDs have no duplicates, match the direct prerequisite IDs in the graph passed to the helper, and all refer to earlier tasks in the list.
2. Every criterion in `nikomi.md` has a concrete verification method and expected result. All required tasks are present, and the IDs in the task list and verification table agree.
3. Every task supports agreed behavior, a constraint, or verification. For preparation without a direct acceptance criterion, identify the downstream task or constraint that requires it. Check that the plan stays within the specification's scope.
4. For changes with a basic design draft or an existing `e2e.md`, [plan E2E tests](plan-e2e.md) and link to `e2e.md` from `dandori.md`. Save the plan with the marker still pending. Re-read it and check items 1–3. Once all checks pass and no prerequisite blocks execution, save the first-line marker as `<!-- dandori-plan: ready -->`.
5. If the deliverable index exists, update the plan and E2E specification links and statuses in `oshinagaki.md` based on the saved files. Report the plan's location and whether it is ready to execute.

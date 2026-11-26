# Implement and verify

## Work through one task at a time

1. Read the task ID, intended result, prerequisite task IDs, completion check, and related acceptance criteria. Before starting, verify that all prerequisites are complete and their results still apply. If a prerequisite is unfinished, skip the dependent task and record the reason and prerequisite ID. Continue eligible work in plan order.
   - If the “Planned changes” table is present, use the parent task ID to find the paths to create, modify, or delete.
   - When a prerequisite investigation establishes a path, record it in the corresponding row before starting dependent work. Revisit the plan if the finding changes task scope or prerequisites.
2. Inspect existing entry points, similar implementation, and tests. Reuse patterns and code that fit the requirement. If you take a different approach within the agreed scope, record why in the plan.
   - Use the planned inputs to check changed behavior and affected existing behavior. For new and reused tests, verify that an assertion would fail if the result violated the specification. For a manual check, verify that the stated observations would reveal the same discrepancy. Fill gaps within the planned method. If the method itself needs revision, follow [Recover and finish](recover-and-finish.md).
3. Make the changes needed to satisfy the specification and the task's intended result. Work through any subtasks in the order listed. On resume, retain valid results and continue from the first unfinished subtask. As each subtask passes its check, save its checkbox and verification result against its ID before moving on. Run the tests or manual checks named in the completion check along with affected existing tests and applicable required project checks. If these edits affect the evidence for earlier tasks or passing criteria, update the records and re-run the affected checks as described in [Recover and finish](recover-and-finish.md). Use the same procedure for failures or discrepancies.
   - Prepare prerequisites such as the test runner first. Before each behavior change, follow the [unit-testing procedure](../../plan-implementation/references/unit-testing.md#run-the-same-test-before-and-after-implementation). Add or update unit-test code for new or changed behavior and confirm the intended assertion fails before implementing the change.
4. Check the IDs and descriptions in the latest `dandori.md`. Check off the parent and save its verification result once all subtasks and the parent's completion check pass. If the specification, plan status, prerequisites, or completion check have changed, return to preparation and cross-check the documents again. Review the saved entry before moving on. If a required check fails or has not run, record why and leave the task unchecked.
   - Before marking the parent task complete, compare the paths actually changed with the plan. If the implementation used the wrong location, correct it and verify the change. If the planned placement or scope needs revision, cite the task ID and reason and return to `plan-implementation`.
   - For a task that updates the structure document, follow [Record the verified directory structure](recover-and-finish.md#record-the-verified-directory-structure).

## Prepare and run the PBI’s automated E2E tests

Before writing the first test, read the [E2E authoring rules](../../e2e-authoring/SKILL.md). Implement the checkpoints and observable readiness conditions from `e2e.md`. For a development run, pass a temporary evidence directory only when screenshots are enabled and the selected cases specify checkpoints. Otherwise unset the capture setting. Record how to pass a new evidence directory with the command in `dandori.md` so `run-feature-e2e` can supply its own destination for the formal run.

When `e2e.md` exists and the configured method uses test code, create or update tests in the current PBI’s `specs/<change>/e2e/`. Identify each behavior ID in the test name or another traceable location. Exercise its specified steps and assert the expected result. Reuse existing tests and shared helpers where appropriate.

During implementation, run the project’s runner against this PBI’s tests. Check that the runner collected only this PBI’s cases and ran the required IDs with the expected results. Verify that the full command exited successfully. Record the command and results in `dandori.md` so `run-feature-e2e` can rerun the same tests.

## Verify acceptance criteria

- For each criterion ID, verify that all tasks it requires are complete. When reusing a task result, check that its inputs and the results actually checked satisfy the verification method and expected result for that criterion. Verify behavior that depends on several tasks with those changes in place together.
- In the matching `dandori.md` row, record the test name, command, or manual procedure and the observed result. Mark it passed after confirming that the result matches the specification. Record failed, not run, and awaiting re-verification with their reasons.
- If a criterion cannot yet be verified, record the task IDs it is waiting for or the missing prerequisite. Verify pending or reopened criteria once the planned check can run.

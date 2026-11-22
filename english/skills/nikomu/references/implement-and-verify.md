# Implement and verify

## Work through one task at a time

1. Read the task ID, intended result, prerequisite task IDs, completion check, and related acceptance criteria. Before starting, verify that all prerequisites are complete and their results still apply. If a prerequisite is unfinished, skip the dependent task and record the reason and prerequisite ID. Continue eligible work in plan order.
2. Inspect existing entry points, similar implementation, and tests. Reuse patterns and code that fit the requirement. If you take a different approach within the agreed scope, record why in the plan. For code changes, default to expressing the expected behavior in a test before implementing it. Use an existing test when it already checks the behavior. If checking for an initial failure, establish that it fails for the expected reason.
   - Use the planned inputs to check changed behavior and affected existing behavior. For new and reused tests, verify that an assertion would fail if the result violated the specification. For a manual check, verify that the stated observations would reveal the same discrepancy. Fill gaps within the planned method. If the method itself needs revision, follow [Recover and finish](recover-and-finish.md).
3. Make the changes needed to satisfy the specification and the task's intended result. Run the tests or manual checks named in the completion check along with affected existing tests and applicable required project checks. If these edits affect the evidence for earlier tasks or passing criteria, update the records and re-run the affected checks as described in [Recover and finish](recover-and-finish.md). Use the same procedure for failures or discrepancies.
4. Once the completion check passes, confirm the task ID and description in the latest `dandori.md`, then update the checkbox and save what was checked and the result. If the specification, plan status, prerequisites, or completion check have changed, return to preparation and cross-check the documents again. Review the saved entry before moving on. If a required check fails or has not run, record why and leave the task unchecked.

## Verify acceptance criteria

- For each criterion ID, verify that all tasks it requires are complete. When reusing a task result, check that its inputs and the results actually checked satisfy the verification method and expected result for that criterion. Verify behavior that depends on several tasks with those changes in place together.
- In the matching `dandori.md` row, record the test name, command, or manual procedure and the observed result. Mark it passed after confirming that the result matches the specification. Record failed, not run, and awaiting re-verification with their reasons.
- If a criterion cannot yet be verified, record the task IDs it is waiting for or the missing prerequisite. Verify pending or reopened criteria once the planned check can run.

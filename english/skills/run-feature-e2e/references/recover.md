# Recover from an E2E failure

## Resume recovery

- If recovery awaits user action, check for the user's decision or action. If recovery stopped before the retest, continue from the recorded step once its prerequisites are met. After a finished retest, close the recovery record and start a normal run when the user requests the next run.
- If recovery is in progress, continue from the recorded stage. If the retest has started, resume at step 3. If its results are recorded, proceed to step 4. If the retest awaits reviewer confirmation, follow [the confirmation procedure](run-e2e.md#record-reviewer-confirmation).

## Choose the next step

Use the results for the current run in `e2e.md`. Compare the expected and observed results for the affected behavior IDs with the agreed `shikomi.md`, `dandori.md`, and current implementation. Determine whether correctly executing the existing plan would satisfy the specification, then choose the next step.

When several behaviors, acceptance criteria and tasks share verification, use the [temporary GraphML operations](../../plan-implementation/references/work-graph.md). From the current tables link required task to criterion (`verifies`) and criterion to E2E behavior (`exercises`). Run `affected FILE failed-behavior-ID --via exercises verifies --reverse` to identify candidates for investigation. Compare them with the expected and observed results to choose the recovery step. Use the current run record to determine retest scope and verdicts.

| Confirmed cause | Next step |
| --- | --- |
| The specification and plan are sound, and the implementation misses the planned behavior | Use [implement-plan](../../implement-plan/SKILL.md) to revisit the affected tasks and acceptance criteria, correct the implementation, and verify it. |
| Satisfying the agreed specification requires a change to the tasks, prerequisites, verification method, or E2E test specification | Use [plan-implementation](../../plan-implementation/SKILL.md) to revise the plan. Once it is ready, use [implement-plan](../../implement-plan/SKILL.md) to complete and verify the affected work. If both the plan and implementation need changes, start with the plan. |
| Automated test code does not check the agreed steps or expectations | Use `implement-plan` to fix and run the PBI’s tests, then retest with `run-feature-e2e`. |
| The test environment, data, or tool caused the failure | Correct the test setup within the available scope. If the user needs to act, report the missing prerequisites and affected IDs. |
| The agreed specification is incomplete or the evidence is insufficient to identify the cause | Record the issue as unconfirmed and tell the user which point needs clarification and what to confirm. Point the user to `specify-spec` if the specification needs clarification. |

## Recover and retest once

1. Before starting recovery, record the run ID, affected IDs and results, evidence links, diagnosis, chosen steps, and current stage in the original run's `evidence/<run-id>/recovery.md`. Keep this record when planning or `start-e2e` updates the results table. If `oshinagaki.md` exists, link to the recovery record from the E2E status field.
2. Follow the chosen steps in order for the same change directory. Pass the affected IDs, expected and observed results, and evidence to `plan-implementation` or `implement-plan` as applicable. Record completion before moving to the next step. If a prerequisite blocks progress, record the current step and what remains, then wait for the user's action.
3. After the required steps are complete, recheck [the test prerequisites](run-e2e.md#check-whether-testing-can-start). Once the tests are ready to run, record the current `e2e-run` ID or its absence before calling `start-e2e`. Save the new ID and [retest all required cases](run-e2e.md#run-tests-and-record-the-results) under that ID. If the session stops before the new ID is saved, compare the previous ID with `e2e.md`. If the ID has yet to change, continue with `start-e2e`. If an ID has already been issued for the retest, reuse it. Use the same ID when collecting results later. If the retest cannot be identified or changed inputs require a fresh run, report the issue and record that it awaits user action.
4. If the retest completed successfully and all required cases pass, record that reviewer confirmation is pending and proceed to confirmation. Mark recovery complete once `verify-e2e` succeeds. If the retest command failed or cases remain failed, unexecuted, or unverified, explain the original and retest results, the steps taken, the outstanding IDs, and what decision or action is needed from the user. Mark the recovery record as awaiting user action and stop automatic recovery.

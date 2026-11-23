# Recover and finish

## Decide what to do from the observed cause

| What you found | What to do |
| --- | --- |
| An implementation defect that can be fixed within the agreed specification and plan | Use the failed test or procedure to diagnose the cause, fix it, and re-check affected behavior. |
| Missing verification environment or data | Record the check that could not run and the missing prerequisite. Restore it and retry if it is within scope. If the user needs to provide it, identify what is needed. |
| The specification can stand, but task scope, prerequisites, or verification methods need revision | Identify the evidence and task IDs, pause affected work, and return to `plan-implementation`. |
| The specification is unclear or conflicts with observed behavior, leaving the required implementation uncertain | Record the specification passage and observations as “Unconfirmed (user confirmation required)” and pause affected work. Ask the user one question at a time. Return to `specify-spec` when the specification needs clarification. |

When offering choices, normally give three viable options in recommendation order, explain your first choice, and allow free-form input. Ask an open question if viable options are unavailable. Continue independent work with satisfied prerequisites. If the user asks to stop, stop implementation and record what has been verified and what is needed to resume.

## Update affected records

In the working graph prepared at startup, run `affected FILE failed-task-ID --via requires verifies`. Check the starting task itself and the returned downstream tasks and criteria against the plan before updating their records.

1. Clear the checkbox of a task that failed re-verification or whose previous check no longer holds. Follow the plan's dependency edges downstream and reopen each task that relies on that result directly or indirectly.
2. For affected acceptance criteria, record a failure if the criterion's own check failed, or mark the previous pass as awaiting re-verification if its evidence is invalid. Preserve unaffected records.
3. Save the changes to `dandori.md` with the originating task ID and reason before continuing. Once the prerequisite is fixed, re-check affected tasks and criteria before restoring completion or a pass.

For example, suppose `AC-01` needs both `T-01` and `T-02`, and `T-02` depends on `T-01`. If re-verifying `T-01` fails after resuming, reopen both tasks and mark a previous pass for `AC-01` as awaiting re-verification. After fixing `T-01`, also re-check `T-02` and `AC-01`.

## Report completion or interruption

- Review the saved `dandori.md` and current diff. Check that every task is complete, every acceptance criterion ID from `shikomi.md` has valid passing evidence for the current change, and required project checks have passed. Continue verifying if evidence is missing and can still be obtained.
- On completion, summarize the task count, acceptance results, and location of `dandori.md`. If work remains, report the task or criterion IDs, their current state, and what is needed to resume. Count only current passes as passed.

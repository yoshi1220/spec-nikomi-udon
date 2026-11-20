---
name: yonabe
description: Implement and verify a change using a confirmed nikomi.md and its dandori.md. Record task completion and evidence for each acceptance criterion in dandori.md.
---

# Implement from the plan and record verification

Use the directory the user specifies. Otherwise, map the current `feature/<change-name>` branch to `specs/<change-name>/`. Confirm where to make the change if you cannot resolve the directory or you are on the branch for a different change.

1. Read `nikomi.md` and `dandori.md`. If the specification is unconfirmed or a blocking decision remains, return to clarification. If the plan has a status marker, it must have exactly one marker and start with `<!-- dandori-plan: ready -->`. Return to planning if the state is pending or invalid. For every plan, including legacy plans without a marker, check that it matches the current confirmed specification and has a verification method for every acceptance criterion before editing code.
2. Work through tasks in order. Before starting a task, check that every listed direct prerequisite is complete and its verification still holds. Return to planning if a prerequisite reference is unknown or conflicts with the recorded order. When a prerequisite is incomplete or its check failed, skip the dependent task and record the reason and prerequisite ID. Work whose prerequisites are satisfied can continue. Follow and reuse similar implementations where they fit, and record why a different approach is needed. For code changes, default to writing a test of the expected behavior first, and also use existing tests and the project's required checks.
3. Check off each task when its completion check passes. Verify each acceptance criterion once all tasks listed in its verification method are complete. For every criterion, record its ID, the test name or command run or manual check performed, and the observed result in `dandori.md`. Record checks that were not run or failed, with the reason. When resuming work, read the previous results and re-run any checks affected by later changes.

   When a task fails re-verification or its previous check no longer holds, clear its checkbox. Follow the dependency edges downstream and reopen tasks that depend on that result directly or indirectly. For affected acceptance criteria, record a failure if the criterion's own check failed, or mark it as awaiting re-verification if its previous passing evidence is invalid. Preserve unaffected records. Save these updates to `dandori.md` with the originating task ID and reason before continuing. Once the prerequisite is fixed, re-check each affected task and criterion before restoring completion or a pass.

4. Report completion once all tasks are checked off and current evidence shows that every acceptance criterion passed for the change as it stands.

If the implementation or observed behavior conflicts with the agreed specification and a decision is needed, record the finding and pause the affected work. Ask one question at a time. Normally offer three viable options in recommendation order, explain your first choice, and accept free-form input. Ask an open question when you cannot provide viable options.

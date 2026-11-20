---
name: yonabe
description: Implement and verify a change using a confirmed nikomi.md and its dandori.md. Record task completion and evidence for each acceptance criterion in dandori.md.
---

# Implement from the plan and record verification

Use the directory the user specifies. Otherwise, map the current `feature/<change-name>` branch to `specs/<change-name>/`. Confirm where to make the change if you cannot resolve the directory or you are on the branch for a different change.

1. Read `nikomi.md` and `dandori.md`. Check for `<!-- nikomi-review: confirmed -->` and confirm that the plan matches the current specification. If the specification is unconfirmed or a blocking decision remains, return to clarification. If the plan is outdated or an acceptance criterion has no verification method, identify the gap and return to planning before editing code.
2. Implement the tasks in order. Check similar implementations, follow their patterns, and reuse code when it fits the requirements. Record the reason if a different approach is needed. Use test-driven development by default. For code changes, start with a test of the expected behavior. Also use existing tests and the project's required checks.
3. Check off each task when its completion check passes. For every acceptance criterion, record its ID, the test name or command run or manual check performed, and the observed result in `dandori.md`. Record checks that were not run or failed, with the reason. When resuming work, read the previous results and re-run any checks affected by later changes.
4. Report completion once all tasks are checked off and the recorded evidence shows that every acceptance criterion passed.

If the implementation or observed behavior conflicts with the agreed specification and a decision is needed, record the finding and pause the affected work. Ask one question at a time. Normally offer three viable options in recommendation order, explain your first choice, and accept free-form input. Ask an open question when you cannot provide viable options.

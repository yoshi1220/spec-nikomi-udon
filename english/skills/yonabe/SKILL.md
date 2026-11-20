---
name: yonabe
description: Implement and verify a change using nikomi.md and dandori.md. After implementation, use e2e mode to execute and record the E2E test specification.
---

# Implement from the plan and record verification

Use the directory the user specifies. Otherwise, map the current `feature/<change-name>` branch to `specs/<change-name>/`. Confirm the working location with the user if you cannot resolve it or the current branch belongs to another change.

For `yonabe e2e` or a request to run E2E tests, check the implementation completion records and follow [Run E2E tests](references/run-e2e.md).

## Implement a change

1. Follow [Prepare or resume execution](references/prepare-execution.md). Cross-check `nikomi.md` and `dandori.md`, inspect the worktree and saved evidence, and identify work that can resume.
2. Follow [Implement and verify](references/implement-and-verify.md). Process tasks in plan order when their prerequisites are met. Record task completion and acceptance verification separately in `dandori.md`.
3. Use [Recover and finish](references/recover-and-finish.md) when a check fails, a discrepancy appears, or execution ends. Reassess the affected work and evidence, then report completion once the current change is fully verified.

When `e2e.md` is present, offer `yonabe e2e` after implementation.

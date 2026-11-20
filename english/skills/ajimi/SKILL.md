---
name: ajimi
description: Run the E2E tests in e2e.md after implementation with yonabe, and record verdicts, evidence, and reviewer confirmation. Route test failures back to planning or implementation as appropriate, then retest once.
---

# Verify an implemented change with E2E tests

Use the directory the user specifies. Otherwise, map the current `feature/<change-name>` branch to `specs/<change-name>/`. Confirm the working location with the user if you cannot resolve it or the current branch belongs to another change.

- If `evidence/<run-id>/recovery.md` records recovery in progress or awaiting user action, follow [the recovery procedure](references/recover.md) from the recorded stage.
- For a normal run, follow [the E2E test procedure](references/run-e2e.md). Check the cases against the current specification and plan, run the tests using the configured method, and record the results. Use the results for the current run ID to decide whether to recover from a failure or seek reviewer confirmation.
- Once `verify-e2e` validates the passes and reviewer confirmation for the current change, tell the user that the change is ready for `osameru`.

# Verify the E2E test specification

## Check whether testing can start

Read `shikomi.md`, `dandori.md`, and `e2e.md` and check that the agreed specification, plan, test steps, and expected results agree. If the plan has a status marker, require exactly one `<!-- dandori-plan: ready -->` marker on the first line. For a legacy plan without a marker, assess readiness from the plan itself. In either case, require completed tasks and current passes for all acceptance criteria. Report any gaps or discrepancies and name the next step.

Before issuing a new run ID, check that the configured method can exercise the target behaviors and evaluate their expected results. If preparation is incomplete, report the affected IDs and missing prerequisites, and explain the available methods.

For methods that use test code, check that the command in `dandori.md` selects only this PBI’s `specs/<change>/e2e/` tests and covers the behavior IDs in `e2e.md`. Return the affected IDs to `nikomu` if cases or run instructions are missing or an older PBI keeps its tests elsewhere.

- **Playwright**. Prepare the project runner and browser. Rerun `init` from the same release to check Chromium startup and an assertion.
- **Agent browser**. Open the target in the Codex desktop browser or connect Claude Code with `/chrome`. Check site access and how to observe each expected value.
- **Chrome extension**. Enable the project extension, grant access to the target site, and verify that its assertions run.
- **Manual testing**. Give the tester the environment, data, and steps, and confirm they can record observations and verdicts by ID.

If the user chooses another method, run `python3 <osameru.py> setup --method <method>`. Keep earlier results associated with their original run ID and start a fresh run once ready.

## Run tests and record the results

1. Use the project's configured method, following the [settings and recording instructions](../../osameru/references/format.md). For a new run, prepare the environment, data, and tools. Run `start-e2e` immediately before testing and keep the run ID. If a prerequisite is unavailable, record the affected behavior IDs as unexecuted and report what is missing. If `oshinagaki.md` exists, keep its E2E row up to date with testing, confirmation, and recovery status.
2. When collecting results later or resuming after an interruption or while awaiting confirmation, match the run ID to the `e2e-run` record in `e2e.md`. Use `check-e2e-run --tested <run-id>` to confirm that the inputs from the run still apply. If results are already recorded, continue with the outstanding tests or evaluate the results.
3. Run the tests with the selected method and collect observations and verdicts by behavior ID.
   - **Agent browser.** Use the Codex desktop browser or the official Claude Code Chrome connection. Perform each step, compare the observed value with the expected result for each ID, and save the requested evidence.
   - **Playwright.** Rerun the current PBI’s tests with the command from `nikomu`. Record observations and verdicts by ID from this run. Mark skipped or undiscovered IDs as unexecuted. Record the command’s exit status in the execution block, including any error observed during setup or teardown. If all assertions passed but the command failed, preserve the observations and mark the affected cases unverified. If the failure cannot be attributed to specific cases, mark all cases in the run unverified.
   - **Chrome extension.** Use the project's available Chrome extension to run the steps in the specified browser, application and test data. Evaluate the expected text, values or state through assertions or evaluation results from the extension. Distinguish the record of browser actions from the verdict on each expected result. If assertions cannot run, report the missing capability and record the case as unverified.
   - **Manual.** Give the tester the steps in the specification, then collect and record the observed result and verdict for each ID.
4. Before saving results, use `check-e2e-run` to validate the run ID and inputs again. If validation fails, report the reason and the affected IDs. If inputs changed during a normal run, restart with the current inputs. If a recovery retest must be restarted, record that it awaits user action.
5. Record `OK` in `e2e.md` when the current run confirms the expected result and `NG` when an observation differs from the expected result. Record why cases are unexecuted or unverified. Record the actual method, environment, and date inside the `e2e:execution` block when present. When enabled and requested for a step, save screenshots in the PBI's `evidence/<run-id>/` directory and link them from the corresponding row.
6. Return recovery retest results to the [recovery completion check](recover.md#recover-and-retest-once). For normal runs, follow [the recovery procedure](recover.md) if the command or a case failed, or proceed to reviewer confirmation once all required cases pass. If only unexecuted or unverified cases remain, report their IDs and outstanding prerequisites.

## Record reviewer confirmation

When the run completed successfully, all required cases are `OK`, and `check-e2e-run` succeeds, show the reviewer the steps and verdicts for that run. Once the reviewer explicitly confirms the execution and results, run `review-e2e` with the run ID and reviewer name. Reuse any existing confirmation for that run. Run `verify-e2e` before reporting completion. If validation fails, report the reason and any outstanding checks. If changed inputs require another recovery retest, record that it awaits user action.

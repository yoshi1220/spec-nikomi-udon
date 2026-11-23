# Plan and run unit tests

## Identify the rules to verify

1. Compare `shikomi.md`, the basic design draft when available, and the existing code and tests. Identify the rules in changed or affected behavior that can be checked in an isolated function, class, or similar unit. Consider input boundaries, forbidden state transitions, return values, and absence of side effects on failure. Use integration or E2E checks for conditions that require an actual service connection or interaction through a user interface.
2. Under “Unit tests” in `dandori.md`, record the source, unit, setup and input, observable expected result, and test name or file for each rule. Cite an acceptance criterion ID or the relevant specification or design section. For each rule, identify an assertion that fails when the rule is broken. For an existing test, check that its assertions already verify the rule.
3. Plan to add or update executable unit-test code for new or changed behavior. In the relevant task, specify the order: prepare the test, observe the expected failure before implementation, implement the change, and confirm that the same test passes. These steps can belong to one task. For changes that retain behavior, reuse valid tests and fill any gaps. If no executable behavior is in scope, as in a documentation-only change, record why.
4. Use the project's existing runner and coverage tooling. Record the command that selects the relevant cases and the scope of measurement. If the project has no runner yet, plan setup for a runner and coverage tooling appropriate to its stack.

## Run the same test before and after implementation

1. In `implement-plan`, write unit tests for the specified behavior first. Verify that the intended assertion fails against an implementation that breaks the rule. Build errors, environment failures, and failure to collect tests do not count. For work that only retains behavior, record a passing baseline. If work has already started and the prior version cannot be restored in place, preserve user edits and use an isolated workspace with the prior version or a temporary change that breaks only the target rule. If detection cannot be demonstrated, record the reason and leave it unverified.
2. Pass the project command to the [unit-test runner helper](../../implement-plan/scripts/unit_test.py). For `--expect-output`, use output specific to the failing assertion for red and output showing that the selected case ran and passed for green. The default exit code for an assertion failure is 1. If the runner uses another code for failed assertions, pass `--failure-exit <code>` in the red phase. Read the runner output to confirm the case and its outcome.

   ```text
   python3 <unit_test.py> red --expect-output "<target assertion failure message>" -- <runner and arguments>
   python3 <unit_test.py> green --expect-output "<output showing the target test passed>" -- <runner and arguments selecting the same cases>
   ```

3. After implementing the rule, rerun the same cases and the affected unit suite. Check the counts of passed and skipped cases. Record the commands, observed failure and pass, and test references in `dandori.md`. Assert values, states, and side effects derived from the requirements. Remove cases that only invoke code or use assertions that always hold. Leave implementation incomplete if a required unit-level check failed or did not run.

## Target at least 80% line coverage

Measure line coverage on the relevant production code from unit tests alone. In an existing project, measure the modules containing the executable behavior added or changed by this work. In a new project, measure the production modules added by this work. Include in-scope files even if no test imports them. Keep test code and unrelated modules outside the scope, and retain existing exclusions unless there is a documented reason to change them.

Record the scope, command, measured percentage, and report location in `dandori.md`. Below 80%, compare the uncovered code to the requirements, add tests for any missing rules, and measure again. Report any remaining shortfall or missing measurement with its reason. Determine completion using the required unit-test results and the project's own criteria.

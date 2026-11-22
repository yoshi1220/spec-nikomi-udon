# Settings, records, and canonical application

Run the bundled [osameru.py](../scripts/osameru.py) with Python 3.8 or later from the target repository. In the examples, `<osameru.py>` denotes the installed script. Change-specific commands use the current `feature/<change>` branch. To specify a change explicitly, pass `--change specs/<change>` before the subcommand. Run `apply` on the corresponding work branch.

## Project settings

Choose project defaults during the first `init`. After installation, run a command such as `python3 <osameru.py> setup --method agent-browser` in the repository to change the specified options. The accepted `--method` values are `playwright`, `chrome-extension`, `manual`, and `agent-browser`. Screen item definitions and screenshots are off by default. Enable them with `--screen-items on` and `--screenshots on` as needed. Use `settings` to read the effective settings from `designs/nikomi-udon.json`. Projects without the file use manual testing.

Use the current settings when running and reviewing tests. After changing the settings, run and review E2E under the new configuration before applying the design.

Use the `--design-approval` option of `setup` to select `none` (default), `operational`, or `pr`.

## Draft blocks

Place one complete basic design per affected function inside `shitagaki.md`.

When the project template starts with a `# ` heading, start each function’s body with its heading. For templates that start with a table or front matter, put that formatted body inside the block.

When writing or revising a basic design draft, record `requires_heading` in each block. Use `true` when the body template starts with `# ` after leading whitespace, and `false` otherwise. Ask the operator about an empty template. Application uses the condition saved with the draft. Screen item blocks use `path` and `base`.

```markdown
<!-- osameru-target: {"path":"orders/register.md","base":"new","requires_heading":true} -->
# Register an order — basic design

Document text
<!-- /osameru-target -->
```

`path` is relative to `designs/specifications/`. Get the base of the version you use with `python3 <osameru.py> base orders/register.md`. Record `new` for a new file or the SHA-256 of the existing base. If the canonical version changes, reconcile the draft with it before updating `base`.

When screen item definitions are enabled, put one `<!-- screen-items: applicable -->` or `<!-- screen-items: not-applicable -->` marker outside the blocks in `shitagaki.md`. If applicable, use the same block format in `screen-items.md` with targets such as `orders/register.screen-items.md`.

## E2E records and application

1. Immediately before testing, run `python3 <osameru.py> start-e2e` and keep the run ID. The CLI computes a hash of the test definitions, project settings, and relevant worktree files, then clears previous results and confirmation. Put logs and images you link in the report under the PBI's `evidence/<run-id>/` directory. Send temporary test-runner output to a path that Git ignores.
2. Record the actual method, environment, and date between the `e2e:execution` markers. Each new run clears this block or adds it to an older report. Changes to planned scope or shared prerequisites require a new run. Record the outcome and verdict observed in this run for each behavior ID in `e2e.md`. Use inline Markdown links in the evidence column for logs and images. The CLI resolves each path from `e2e.md` and checks the file contents against the reviewer’s confirmation. When a row requests a screenshot and screenshots are enabled, link the image there, for example at `./evidence/<run-id>/E2E-01.png`.
3. Once all required checks are marked `OK` and the reviewer confirms the execution and results, run `python3 <osameru.py> review-e2e --tested <run-id> --reviewer "<reviewer>"` to record confirmation in `e2e.md`. If inputs change, start a new run and obtain fresh results and confirmation. `verify-e2e` validates the record.
4. Run `python3 <osameru.py> apply --reason "<reason>"` to prepare the canonical design and history files on the work branch. For example, `orders/register.md` has its history in `orders/register.history.md`. If the canonical base has changed, reconcile the draft. Rerunning after applying the same content completes without duplicating its history.

To withdraw confirmation, restore the contents between the `e2e:review` markers to “Pending.” Use `start-e2e` to begin a new run before confirming again. To correct the change reason, pass the corrected text to `apply` to update the same PBI's history entry.

When resuming result entry or review for a completed run, keep the `id` in the `e2e-run` comment in `e2e.md`. Run `python3 <osameru.py> check-e2e-run --tested <run-id>` to verify the run ID and tested inputs. The command leaves results and reviewer confirmation untouched.

Keep the `e2e:checks`, `e2e:execution`, and `e2e:review` blocks separate. Keep the table columns in the template's order, starting with the behavior ID and ending with the evidence. Use `<br>` for line breaks and `\|` for a literal pipe inside a cell. Record completed verdicts as `OK` or `NG`.

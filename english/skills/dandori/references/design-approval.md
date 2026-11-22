# Design approval before planning

Use the installed path of the [bundled CLI](../../osameru/scripts/osameru.py) in the commands below. Run `python3 <osameru-script> settings` in the target repository and read `design_approval`. Projects without this setting default to `none`. Every mode requires confirmed `shikomi.md` and uses `shitagaki.md` when available.

For an explicit PBI exception such as an emergency, obtain the reason and the operator’s confirmation that the designated role authorized the exception. Record both in the target PBI’s `dandori.md` and proceed directly to planning. Keep the exception local to the PBI. On resumption, honor an exception already recorded for the same PBI.

- `none`. Proceed without advance approval.
- `operational`. The operator obtains approval through the project’s process before invoking the skill. Treat invocation as confirmation and proceed without an approval prompt or warning.
- `pr`. Automatically read the target PR’s review decision using the available PR integration. Use the design PR specified for this PBI, or identify it from the PBI work branch. Verify that the review covers the target design draft in the same repository. Proceed upon approval, even before merge.

With GitHub CLI installed, run `python3 <osameru-script> --change specs/<change> check-design-review`. Append `--pr <number>` for a specified PR. Branch lookup requires a single open PR originating in the same repository. For a fork, specify the PR number. With either the CLI or another integration, compare the local draft with both the PR head and the revision covered by an active approval.

In PR mode, if approval cannot be established, report the specific issue (ambiguous PR, missing draft, lookup failure, pending review, or requested changes). Ask whether to continue and wait. On continuation, automatically record the unconfirmed item and the operator’s decision immediately in the PBI’s `dandori.md`, preserving the entry when writing or revising the plan. Start a new file with `<!-- dandori-plan: pending -->`. Stop planning if the operator declines.

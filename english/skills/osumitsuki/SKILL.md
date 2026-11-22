---
name: osumitsuki
description: Record the approval date and approver for a PBI's basic design draft in its deliverable index before implementation planning.
---

# Record basic design approval

1. Use the specified PBI or map the current `feature/<change>` branch to `specs/<change>/`. Ask if the target is unclear. Follow the [index and migration procedure](references/index.md) to read the current state. For `off`, finish without adding a section. Preserve an `emergency` and its reason. For `approved`, show the existing record and finish. Continue to approval only for `pending`.
2. Record approval actually received for this PBI's `shitagaki.md`. Read the approval date and approver from the invocation arguments or accompanying text, such as `$osumitsuki --date 2026-11-20 --approver "Design lead"` or “The design lead approved it on November 20.” Resolve the full date including the year. For PR approval, read the review first. Ask only for information still missing, one item at a time. Use the actual approval date even when recording it later.
3. Run the installed [approval.py](scripts/approval.py) for the project's mode. In these examples, `<approval.py>` is the installed path. To target a particular PBI, put `--change specs/<change>` before the subcommand.
   - For `operational`, record the approval obtained through the project's process with `python3 <approval.py> approve --date YYYY-MM-DD --approver "reviewer"`.
   - For `pr`, run `python3 <approval.py> approve` to compare the local draft with both the PR head and an active approving review. Pass a specified PR number with `--pr NUMBER`. Otherwise the helper selects a single open same-repository PR for the change branch. It records the verified GitHub login and submission date (UTC). Pass any specified date and login with the same approval options to select a matching review. With another PR integration, confirm that the target PR includes this PBI’s design file among its changed files and has an active approval. Read that file’s Git blob ID at both the PR head and the approving revision. Pass `--verified-pr URL HEAD_BLOB REVIEWED_BLOB` with the review date and approver. The helper compares both file IDs with the local draft.
4. If verification or saving fails, explain what needs attention. After a successful write, confirm the approved state, date and approver in `oshinagaki.md` and direct the operator to `dandori`.

---
name: osameru
description: Validate required E2E passes and human confirmation, then apply the basic design draft and revision history on the PBI branch.
---

# Apply the canonical design

Use this skill after implementation with `nikomu` and after `ajimi` records the E2E passes and reviewer confirmation. Follow the [handoff format and CLI reference](references/format.md) to prepare canonical design and history updates on the work branch.

1. Use the specified `specs/<change>/` directory, or resolve it from the current `feature/<change>` branch. Check that the branch matches the change and that `shikomi.md` and `shitagaki.md` exist.
2. Compare `shikomi.md`, `shitagaki.md`, and `e2e.md`. Check required design content, open items, and E2E coverage. Show any gaps or mismatches between the requirements, design and implementation. Ask the user one question at a time when a decision is needed.
3. Use the CLI's `apply` command with `--reason`. It checks that the required E2E results pass for the current change and that the reviewer confirmed the execution and results. Report any blocking results and return to the appropriate design or verification step.
4. Review the resulting design and history diff. Record the destinations and work-branch status in the change directory's `oshinagaki.md`. Report that the implementation and design can be reviewed in the same PR. The canonical update is complete when the design has been reviewed and that PR has been merged. Submit or merge a PR when the user requests that action.

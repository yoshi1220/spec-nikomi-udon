---
name: okosu
description: Document the current system from an existing codebase, establish its persistent function tree, dependencies and node histories, and prepare the onboarding documentation for review.
---

# Document the current design of an existing project

Prepare the current design that the first change will use in an existing Git repository. Follow the [investigation, resumption, and review procedure](references/baseline.md) to identify the code revision and read the existing overview and design documents.

1. Use the [system overview template](../kondate/assets/system-overview.template.md) to record the system-wide function inventory and relationships in `designs/system-overview.md`. Show open questions that affect scope and review the entire inventory with the user in conversation. Once those questions are resolved and the user explicitly confirms the inventory, save the confirmation state and analyzed revision in the same document.
2. Cover the entire current system by default. Trace menus, screens, API routes, scheduled jobs and integrations at the inspected revision. Follow the code, configuration and tests even when no design document exists. Document as much of every confirmed function as the evidence supports. If the user requests limited documentation, keep the full verified graph and mark functions with missing text as undocumented. Save the revision and coverage.
3. Resolve the [project basic design template and writing guidance](../shitagaki/references/basic-design-format.md) and use the template body to prepare the **current** basic design of the functions in scope under `designs/specifications/`. Check the descriptions against the code, configuration, and existing tests at the analyzed revision. Record the sources and unverified points. If the user requested a narrower scope, record how the selected functions relate to the planned change.
   Follow the [canonical structure procedure](../osameru/references/structure.md) to prepare and preview the baseline plan, mark the sections, import existing history, apply on the documentation branch and run `structure-check`. Record the inspected commit as the initial revision for existing functions without documented history.
4. Present the revision, scope, documentation diff, and open points for a documentation-only onboarding PR. Runtime verification is optional for this PR. The basic designs become canonical when it merges. Use the canonical documents on the shared branch when starting the first change with `shikomi` or `torikomu`. Submit or merge the PR when the user requests the action.

On resumption, read the analyzed revision, confirmation state, and selected scope from the overview. Carry forward decisions whose evidence still applies. Ask about remaining points one at a time, in order of impact. When there are concrete options, explain the recommendation and allow free input.

---
name: okosu
description: Onboard an existing project by mapping its functions and relationships from the current code, then document the basic design for the scope the user reviews and selects. Prepare a documentation-only onboarding PR or resume the work in a later session.
---

# Document the current design of an existing project

Prepare the current design that the first change will use in an existing Git repository. Follow the [investigation, resumption, and review procedure](references/baseline.md) to identify the code revision and read the existing overview and design documents.

1. Use the [system overview template](../shikomu/assets/system-overview.template.md) to record the system-wide function inventory and relationships in `designs/system-overview.md`. Show open questions that affect scope and review the entire inventory with the user in conversation. Once those questions are resolved and the user explicitly confirms the inventory, save the confirmation state and analyzed revision in the same document.
2. Show the confirmed inventory and ask the user to choose **the functions being changed and those affected** or **the entire system**. Recommend the former when the change entry points and affected functions are known, or the latter when onboarding requires basic designs for all functions. Number the options in recommended order, give a reason for the recommendation, and allow free input. For the first option, use the intended change to identify the affected functions and ask about outstanding decisions one at a time. Save the selected scope and functions in the overview before writing the basic designs.
3. Resolve the [project basic design template and writing guidance](../shitagaki/references/basic-design-format.md) and use the template body to prepare the **current** basic design of the selected functions under `designs/specifications/`. Check the descriptions against the code, configuration, and existing tests at the analyzed revision. Record the sources and unverified points. Use any planned change in the input to inform scope.
4. Present the revision, scope, documentation diff, and open points for a documentation-only onboarding PR. Runtime verification is optional for this PR. The basic designs become canonical when it merges. Use the canonical documents on the shared branch when starting the first change with `nikomu` or `torikomu`. Submit or merge the PR when the user requests the action.

On resumption, read the analyzed revision, confirmation state, and selected scope from the overview. Carry forward decisions whose evidence still applies. Ask about remaining points one at a time, in order of impact. When there are concrete options, explain the recommendation and allow free input.

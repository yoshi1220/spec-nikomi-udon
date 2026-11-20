---
name: shitagaki
description: Draft or update a functional basic design in the PBI's shitagaki.md from its saved nikomi.md.
---

# Draft the basic design

Use the specified `specs/<change>/` directory. Otherwise map the current `feature/<change>` branch to its change directory. Ask when the target is unclear. Read `nikomi.md` first. If the file is missing, report the required path and stop before creating files. Use the saved content at invocation time, including manual edits.

1. Identify the affected functions and their expected behavior. Read the system overview, related documents, and any existing canonical specifications. Compare `dandori.md`, implementation code, and verification results when available. Account for the timing of the planned change when comparing behaviors. If sources disagree about the same behavior at the same point in time, show the evidence, ask the user one question at a time, and wait before creating or updating the draft.
2. For an existing function without a canonical design, investigate its current externally observable behavior across the entire function. Combine the behavior to retain with the agreed changes. For an existing canonical design, use that document as the base for a complete updated draft. Mark unsupported items as requiring user confirmation and explain what to confirm and what it affects. Place new canonical documents in the system's functional hierarchy.
3. Use the [basic design template](assets/shitagaki.template.md) to save the draft in `shitagaki.md`. Follow the [handoff format](../osameru/references/format.md) to specify each function's document and destination. Read the project settings. When screen item definitions are enabled and applicable, also create `screen-items.md` in the change directory. Describe the screens, fields, inputs and outputs, validation rules, and visibility or editability conditions supported by the evidence.
4. On reruns, read the current `shitagaki.md` and update the parts affected by the change. Rework the structure when the underlying specification changes substantially. Preserve applicable manual edits and review decisions. If the canonical file has changed, reconcile the draft with that version before refreshing the recorded base.
5. Verify purpose and scope, business rules, inputs and outputs, and normal and error behavior. Include applicable permissions and external integrations. Ensure the preconditions, actions, and observable results support test expectations for the main cases. Record the sources and update the affected rows in `oshinagaki.md`, creating it from the [deliverable index template](assets/oshinagaki.template.md) if needed. Report the draft path and open review items. Use `osameru` to apply the draft to the canonical design.

Ask one question at a time. For decisions with multiple options, number them in recommended order and allow free-form answers.

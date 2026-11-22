---
name: shitagaki
description: Draft or update a functional basic design in the PBI's shitagaki.md from its saved shikomi.md.
---

# Draft the basic design

Use the specified `specs/<change>/` directory. Otherwise map the current `feature/<change>` branch to its change directory. Ask when the target is unclear. Read `shikomi.md` first. If the file is missing, report the required path and stop before creating files. Use the saved content at invocation time, including manual edits.

When starting or redoing a design, follow the [index and migration procedure](../osumitsuki/references/index.md), then run the same helper with `redraft` before working on the draft. This immediately returns normal approvals to pending, even if work is interrupted. An emergency retains its state and reason for the PBI. When approval is enabled or the index already has an approval record, `redraft` also puts any existing plan on hold and preserves its tasks and results for replanning.

1. Identify the affected functions and their expected behavior. Read the system overview, related documents, and any existing canonical specifications. Compare `dandori.md`, implementation code, and verification results when available. Account for the timing of the planned change when comparing behaviors. If sources disagree about the same behavior at the same point in time, show the evidence, ask the user one question at a time, and wait before creating or updating the draft.
2. For an existing function without a canonical design, investigate its current externally observable behavior across the entire function. Combine the behavior to retain with the agreed changes. For an existing canonical design, use that document as the base for a complete updated draft. Mark unsupported items as requiring user confirmation and explain what to confirm and what it affects. Place new canonical documents in the system's functional hierarchy.
   When several functions consume a changing contract, use the [temporary GraphML operations](../dandori/references/work-graph.md) to link the contract to each consumer with a `consumed_by` edge and its source. Use `affected FILE contract-ID --via consumed_by` to identify candidate designs and check which inputs, outputs or failure behaviors need revision.
3. Resolve the [project basic design template and writing guidance](references/basic-design-format.md) and use the template body to save the draft in `shitagaki.md`. Follow the [handoff format](../osameru/references/format.md) to specify each function's document and destination. Read the project settings. When screen item definitions are enabled and applicable, also create `screen-items.md` in the change directory. Describe the screens, fields, inputs and outputs, validation rules, and visibility or editability conditions supported by the evidence.
4. On reruns, read the current `shitagaki.md` and update the parts affected by the change. Rework the structure when the underlying specification changes substantially. Preserve applicable manual edits and review decisions. If the canonical file has changed, reconcile the draft with that version before refreshing the recorded base.
5. Verify purpose and scope, business rules, inputs and outputs, and normal and error behavior. Include applicable permissions and external integrations. Ensure the preconditions, actions, and observable results support test expectations for the main cases. Record the sources and update the affected deliverable rows in the prepared `oshinagaki.md`. Report the draft path and open review items. Use `osameru` to apply the draft to the canonical design.

After saving a changed `shitagaki.md`, run `redraft` again before handing it off. This clears any approval of the previous draft recorded while editing and preserves an existing emergency. For a pending design, obtain operational or PR approval, record it with [osumitsuki](../osumitsuki/SKILL.md), then proceed to `dandori`. When approval is off or the PBI is an emergency, direct the operator to `dandori` once the draft is ready.

Ask one question at a time. For decisions with multiple options, number them in recommended order and allow free-form answers.

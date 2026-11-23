# Create and update the technical context

## Prepare the template and inputs

Use the [technical context template](../assets/technical-context.template.md) to prepare the seven sections in `designs/technical-context.md` in template order. Preserve existing entries and applicable decisions. When incorporating a draft from another directory, adjust its relative links so they resolve from `designs/` to the same sources and sections.

- Start the conversation from a blank template, a team draft, or supplied requirements. Record facts and confirmed decisions from the input with their sources. Treat candidates and proposals as open decisions.
- For an existing project, prefill what the analyzed commit's code, dependency declarations, Compose or deployment settings, and existing designs support. Name the environment and cite the revision or a reference precise enough to find the evidence, such as a configuration key. For example, a Compose database definition supports an entry for local configuration. Use production evidence to establish what runs in production.

Link to the sibling `technical-context.md` from `designs/system-overview.md`. Reuse an existing link or add one immediately after the title to preserve the confirmed inventory and relationship sections. If the overview does not exist, use the [system overview template](../assets/system-overview.template.md), which already includes the link, and fill in what the evidence supports. Save both documents before the first question.

## Review one question at a time

In a full review, work through the headings in template order. For a named section, review that section and report any impact on related sections. Ask one question at a time about missing facts, conflicting evidence, or a decision still to be made. For example, if the local database is known but production is undocumented, ask what runs in production and record the source of the answer. For a choice such as the UI library, offer viable options in recommendation order, explain the first choice, and accept free-form input. Cite both sources when they disagree and keep the point open until resolved.

Save the decision and its basis after each answer. Mark facts that cannot be established as “Unconfirmed,” choices yet to be made as “Undecided,” and confirmed inapplicable areas as “Not applicable.” For unconfirmed points, record what information is needed and what it affects. On resumption, read the saved sections, check for changes to sources that affect decisions, and continue from the remaining points.

## Maintain the configuration by environment

Record the technology and its role in each section, along with environment differences and links to designs and configuration. Refer to configuration keys or management instructions when needed and keep secret values out of the document.

At adoption, record the target environments, target configuration and decision source as an approved change. When an operations record, team confirmation, or other evidence shows the change in effect in an environment, update that environment's current configuration and retain the rollout plan for environments still pending. For example, once only the test environment uses the new identity provider, the production entry should show the old provider in use and the new one as its target.

After saving, check that the system overview opens the document, the evidence is traceable from each section, and current and target configurations are clear by environment. Report which sections were created or updated and which open points affect later decisions.

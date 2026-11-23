---
name: kondate
description: Prepare a system overview with a capability tree and relationship graph from requirements or a description. Document program layout and create or update the project's technical context with the user. Use shikomi or torikomu to start an individual change.
---

# Prepare the system-wide guidance

Read the requirements material specified with `--file <path>`, or use the description supplied in the conversation. If the user specifies a file you cannot read, explain the problem and ask for the input needed to proceed.

For requests limited to the technical context, follow the [technical context procedure](references/technical-context.md). Start with the named section if one is specified and finish after verifying the requested update and the link from the system overview.

Read any existing output documents before starting the analysis. Apply the requested updates and retain existing information when the new input is silent about it.

- Follow the [requirements analysis procedure](references/analyze-requirements.md) to build the capability tree and relationship graph independently, as far as the evidence supports them. Use the [system overview template](assets/system-overview.template.md) to record the purpose, scope, main capabilities, system structure, external integrations, shared constraints, and supporting sources in `designs/system-overview.md`.
- Use the [directory structure template](assets/repository-structure.template.md) for `designs/repository-structure.md`. Replace the instructions with the documented directory tree and known directory responsibilities when the input provides them. If there is no layout in the input and the document is new, keep the template's instructions for the user to fill in.
- Follow the [technical context procedure](references/technical-context.md) to prepare `designs/technical-context.md` and link to it from the overview. Use supplied materials or a team draft to prefill it and review open decisions with the user in template order.

Ask one decision at a time. Normally offer three viable options in recommendation order, explain your first choice, and accept free-form input. Ask an open question when you cannot provide viable options.

If the user also requests installation setup, show which agent instruction file would change, such as `AGENTS.md` or `CLAUDE.md`, and ask whether to add pointers to the documents and when to read them. Default to Yes. After approval, append the pointers while preserving existing instructions and avoiding duplicate entries.

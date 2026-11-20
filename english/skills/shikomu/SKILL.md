---
name: shikomu
description: Prepare a system overview and a repository structure document from requirements material or a short description. Use nikomu or torikomu to start an individual change.
---

# Prepare the system-wide guidance

Read the requirements material specified with `--file <path>`, or use the description supplied in the conversation. If the user specifies a file you cannot read, explain the problem and ask for the input needed to proceed.

- Use the [system overview template](assets/system-overview.template.md) to write the purpose, scope, main capabilities, system structure, external integrations, and shared constraints in `designs/system-overview.md`. Cite the input file if one was used. Mark information that is needed but not yet established as unconfirmed.
- Use the [directory structure template](assets/repository-structure.template.md) for `designs/repository-structure.md`. Replace the instructions with the documented directory tree and known directory responsibilities when the input provides them. If there is no layout in the input and the document is new, keep the template's instructions for the user to fill in.
- If either file already exists, read it and apply the requested updates. Where an input conflicts with existing text, mark the issue as unconfirmed and retain the existing information until the user resolves it.

Ask one decision at a time. Normally offer three viable options in recommendation order, explain your first choice, and accept free-form input. Ask an open question when you cannot provide viable options.

If the user also requests installation setup, show which agent instruction file would change, such as `AGENTS.md` or `CLAUDE.md`, and ask whether to add pointers to the documents and when to read them. Default to Yes. After approval, append the pointers while preserving existing instructions and avoiding duplicate entries.

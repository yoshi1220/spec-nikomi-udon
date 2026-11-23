# Prepare a specification

## Identify the input and working directory

1. If the user specifies a summary path, read that file before switching branches. If it cannot be read, ask for the correct path or its contents. When following this procedure from `import-requirements`, use the document specified there as the primary input.
2. Follow [Prepare the change directory](change-directory.md) to identify the target branch and working tree. Reuse the directory for an existing change. For a new change, allocate a number and prepare `specs/<change>/`.
3. Only when using `specify-spec` without a specified summary path, check the target working tree for `specs/<change>/saguri.md`. Read it if present. If absent, proceed from the request, backlog item, or conversation about this change. Do not search the top-level `saguri/` directory.

When using a summary, carry the problem, scope, adopted direction, and rationale into the draft and cite its original path. Keep unverified hypotheses and further investigation open. Record options the user has set aside as out of scope, with the reason. Apply any more recent corrections the user made about this change in the conversation. When resuming, read the existing `shikomi.md`. If a decision conflicts with the summary, check both sources and the current request to resolve it.

## Draft from what you already know

For a new `shikomi.md`, start with the [specification template](../assets/shikomi.template.md). Keep its `<!-- shikomi-review: pending -->` marker and fill in these four sections.

- **Purpose and scope.** Explain why the change is needed and what it covers.
- **Expected behavior.** Describe the relevant actions or inputs and their observable results.
- **Agreed design decisions.** Record established choices and their reasons. Refer to relevant constraints in the system overview, current specifications, and similar implementations.
- **Acceptance criteria.** State the precondition, action, and observable result. Give each criterion a unique ID such as `AC-01` and preserve previously assigned IDs.

Record the sources. Use “Record unresolved points” in [Save decisions in shikomi.md](record-decisions.md) to capture relevant gaps or discrepancies in the draft. Keep unsupported classifications, relationships, and unagreed behavior out of the confirmed specification. If an acceptance criterion needs an unconfirmed precondition or result, record what is missing and leave the value or behavior open. When modifying an existing system, distinguish observed behavior from behavior the user has agreed to preserve.

Preserve the original request under **Original request**, keeping the user’s wording for the requested capabilities, constraints, and exclusions. When the primary input is a document, preserve its stated goals with references to the relevant sections.

If an existing specification has no Original request section, reconstruct the stated goals from the original input when available. Otherwise use its stated purpose, scope, and agreed requirements as the starting point. Keep existing headings and identifiers. If an earlier requirement's intent is unclear, record it as a point to investigate.

## Begin the interview

After the first save of a new `shikomi.md`, run `init` from the [index procedure](../../record-design-approval/references/index.md) to prepare `oshinagaki.md` with the project settings. Migrate existing PBIs when next handling design, approval or planning.

Once the draft is saved, follow the required [clarification workflow](clarify-spec.md). On resumption, read the existing specification and its decisions before rebuilding the interview state.

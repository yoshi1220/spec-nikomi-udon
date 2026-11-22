# Prepare a specification

## Set up the working branch and directory

When resuming a change, locate its branch and `shikomi.md`. For a new change, choose a short slug describing the request, such as `export-csv`. If it is unclear whether the new change should start from another feature branch, confirm the starting point before creating the branch.

1. If Git remotes are configured, run `git fetch --all --prune`. If fetching fails, explain the error and say that the latest remote numbers could not be verified. Ask whether to continue with the available information or stop. Wait for the user to choose before continuing. When there are no remotes, use the local information.
2. From the target repository, run the bundled [start_change.py](../scripts/start_change.py) with Python 3 and pass the slug as its only argument. The helper uses one more than the highest number among local branches, fetched remote branches, and existing directories under `specs/`. Write `shikomi.md` inside the directory reported by the helper. If it exits with an error, inspect the current branch and the change directory before retrying.

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

After saving a new `shikomi.md`, create `oshinagaki.md` in the same directory from the [deliverable index template](../../shitagaki/assets/oshinagaki.template.md). Use the saved index if it already exists.

Once the draft is saved, follow the required [clarification workflow](clarify-spec.md). On resumption, read the existing specification and its decisions before rebuilding the interview state.

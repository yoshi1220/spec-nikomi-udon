# Investigation, resumption, and documentation review

## Select the revision and map the functions

- Resolve the branch, tag, or revision specified by the user to a Git commit ID. With no revision specified, use the current `HEAD` for a new onboarding effort and the saved commit when resuming. If the PR target is known and its code differs from the analyzed revision, ask which revision represents the current design. Read the code, configuration, and tests at the selected commit. Use `git show <commit>:<path>` or an equivalent when the working tree differs from that revision. Keep unrelated user edits out of the documentation diff.
- Start from entry points such as screens, APIs, and batch jobs to identify functions users or external systems can observe. Trace configuration, data flow, calls, and existing tests. Record relationships whose endpoints, type, and direction can be established, with their sources. Add a functional hierarchy where there is evidence of a business grouping. When entry points or integrations cannot be fully investigated, state the limits and remaining work.
- Identify sources by repository-relative paths and symbols or configuration keys, with line numbers at the selected revision when useful. When effective runtime settings or external behavior cannot be established, record the known conditions and what remains unknown. If existing documents disagree, show both sources and record the user's decision before treating the discrepancy as resolved.

## Save decisions and resume

Keep one “Existing project onboarding” section in `designs/system-overview.md`. Update it in place when it already exists.

| Field | What to record |
| --- | --- |
| Analyzed revision | The commit ID analyzed. Confirmation applies to this revision and the inventory reviewed. |
| Inventory review | Start at “Pending confirmation.” Record “Confirmed,” what was reviewed, and a digest once scope-affecting questions are resolved and the user explicitly confirms the entire inventory. Concatenate the reviewed inventory and relationship sections with their headings in document order, normalize line endings to LF, and take the SHA-256 of the UTF-8 text. Exclude the “Existing project onboarding” section. |
| Basic design scope | Start at “Not selected.” Once selected, record the approach and list the agreed functions or state that it covers all functions. For a targeted change, record the intended change and how it relates to the affected functions. |
| Open questions | Record which questions block scope selection and which can be addressed later, with their reasons, impact, and sources. |

Save the state and decisions before pausing. On resumption, read the inventory, selected scope, and existing drafts and compare the current inventory with the confirmed digest. When switching the analyzed revision, compare it with the prior revision to check the impact on the inventory, dependencies, scope, and designs. If a change affects confirmation of the inventory, return it to “Pending confirmation.” If it affects the scope, retain the prior scope and rationale and wait for the user to choose again. Return to “Pending confirmation” when the confirmed digest is missing or it has changed and the impact cannot be established. If neither is affected, carry forward the review and choice and update the revision and comparison result.

## Basic designs and the documentation-only onboarding PR

- Record purpose and scope, business rules, inputs and outputs, normal and error behavior, and sources in the corresponding fields of the project template. Add permissions and integrations when applicable. State the supported preconditions, actions or inputs, and observable results. Mark behavior that can only be established at runtime as unverified. Existing tests can establish documented expectations. Use an execution record from the analyzed revision to claim an observed result.
- When a function already has a canonical design, use its path, retain applicable content, and show the updates in the review diff. Compare and carry forward existing drafts and manual edits. Write the template body as Markdown in each document. This workflow prepares documents on the documentation PR branch. It has no `shikomi.md` prerequisite and does not run `osameru apply`, which requires PBI E2E results.
- Before preparing the PR, check that the set of designs covers the agreed functions, that reviewers can verify claims using the analyzed revision and cited evidence, and that open points are visible. Check the full PR diff against the target branch and include only onboarding documents. If the target branch's code or existing documents have changed, check the impact and update the affected inventory, confirmation, and designs before review. Include the revision, scope, key sources, open points, and document references in the PR description. For subsequent changes, use the overview and canonical design as inputs to `shitagaki`.

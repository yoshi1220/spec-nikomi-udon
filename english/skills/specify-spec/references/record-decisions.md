# Step 4. Save decisions in shikomi.md

Step 4 does not run sequentially after Step 3. Invoke Step 4A from Step 3 whenever a user answer is settled, and invoke Step 4B from Step 2 whenever an investigated fact resolves ambiguity. Keep the two paths separate. If a fact shows that an accepted decision needs to change, preserve the decision and use the conflict workflow in the [interview rules](interview-rules.md) before applying any correction to it.

## Step 4A. Incorporate a user answer

1. Use the saved Q&A count from Step 1 as the baseline. Add `## Clarifications` if needed and use `### Session YYYY-MM-DD` for the date, reusing an existing heading on the same date.
2. For every accepted answer, append one line: `- Q: <question> → A: <settled answer>`. When a later accepted answer changes an earlier settled decision, keep the earlier line and append ` → Superseded by <later question summary>: <new result>` to it (in the spec's language), so that no Clarifications line states a decision that the main text no longer contains.
3. Incorporate the settled decision into the main spec according to "Step 4C. Shared incorporation and validation rules."
4. If one answer contains multiple decisions, incorporate, save, and validate each decision separately, except that decisions which change the same requirement or depend on each other are incorporated in one save, so that no saved state contradicts the answer. Keep only one Clarifications Q&A line per accepted answer. Do not duplicate the same answer.
5. After each decision has been saved and validated successfully, change its point to Resolved and recalculate aggregate category status.

## Step 4B. Incorporate a fact established by investigation

1. Do not create `## Clarifications` / `### Session YYYY-MM-DD` and do not append a Q&A line. Clarifications records only the user interview.
2. Apply “Step 4C. Shared incorporation and validation rules” to incorporate facts verified from the codebase, project documents, existing specs, or facts the user explicitly confirms or supports with material. Never incorporate assumptions or hypothetical scenarios as facts.
3. Incorporate, save, and validate each verified fact separately.
4. After it has been saved and validated successfully, change the point resolved by that fact to Resolved and recalculate aggregate category status.

## Record unresolved points

Label every relevant unknown “Unconfirmed (user confirmation required).” State what is known and cite the sources, retaining both accounts when sources conflict. Tell the user what to confirm, why, and what it affects. For example, identify the evidence to provide, the source to confirm, or the requirement to choose. Investigate what you can first and remove points you resolve from the confirmation request.

Say when a point blocks the implementation approach or acceptance verification. Keep active points under Open questions. If an existing specification has no equivalent section, add Open questions when needed. When the interview ends, move blocking points and any holds that Step 4C requires you to record to Out of Scope and Limitations, with the “Unconfirmed (user confirmation required)” label. Update any existing entry for the same point so that only one remains. Remove a resolved entry once the specification records the outcome and its basis.

## Step 4C. Shared incorporation and validation rules

1. Incorporate content into the best section:
   - Functional ambiguity → Functional Requirements
   - Actor or action distinctions → Actors and Permissions
   - Data shape → Data and State, preserving the existing field order and keeping constraints concise
   - Non-functional requirement → record the agreed, verifiable condition under Non-functional Requirements. Use a metric when the user agrees to one
   - Edge case → Edge Cases and Failure Handling
   - Terminology → normalize to the canonical term throughout the spec. If needed, note `(formerly "X")` once
   - If shikomi.md has no section suited to the content, **add a standard section heading** at the same level as the existing top-level sections rather than extending the overview prose. Use the project's template names when they exist. Otherwise use, written in the spec's language: Actors and Permissions, Functional Requirements, Data and State, Edge Cases and Failure Handling, Non-functional Requirements, Acceptance Criteria, Out of Scope and Limitations, and Verified Premises (facts incorporated through Step 4B, each with its source). Keep the original request as the starting point and record explicit scope corrections with the decisions that resolve them. Do not rename, reorder, or merge existing sections.
   - Write every requirement as a numbered, independently testable statement in a list, never as an addition to a prose paragraph. Give identifiers a prefix per section—AP- Actors and Permissions, FR- Functional Requirements, DS- Data and State, EC- Edge Cases and Failure Handling, NFR- Non-functional Requirements, AC- Acceptance Criteria, OS- Out of Scope and Limitations, VP- Verified Premises—and add each new item at the end of its section with the next number, so that reading a section from top to bottom meets its identifiers in order. Never renumber an existing identifier. A gap left by a removed item is expected. Follow the project's template when it defines its own identifiers. Keep each statement to the rule itself—normally one or two sentences—without restating context, rationale, or the question. A requirement settled by consequence cites the decisions it follows from, using saved question summaries or verified premise IDs as references. Express a state change as an explicit rule: the triggering event, the quantities or states that change, and what each party sees. Record an agreed exclusion, limitation, or agreed extension under Out of Scope and Limitations with its reason. For an exclusion or limitation, also name the stated goal or fact it leaves unmet. Record there as well, one line each and labeled “Unconfirmed (user confirmation required)” so that none reads as an agreed exclusion, every situation noted but not asked and every Outstanding or Deferred point that leaves a stated goal's behavior undefined, stating the point, the reason, its impact, and what the user needs to confirm, so that the spec alone shows what remains open. Remove the line if the point is later resolved.
2. If new content invalidates older ambiguous text, **replace** it rather than appending a duplicate. Leave no conflicting obsolete text. When a later decision qualifies an existing requirement—adds an exception, a condition, or a further case—amend that requirement in place under its identifier rather than adding a second requirement that overrides it from elsewhere. Add a new identifier only for a new rule.
3. **Derive an acceptance check from each settled decision that defines behavior, a boundary, or a failure outcome of a stated goal.** Add it under Acceptance Criteria with a heading such as `### AC-04` and a concise scenario stating the setup, the action, and the observable result with the fewest quantities that distinguish it, and cite the decision it verifies. Merge scenarios that differ only in their numbers. Record agreed exclusions and out-of-scope items in Out of Scope and Limitations. A stated prohibition—an action that must be refused—is a constraint, not an exclusion: verify it with a scenario showing the refusal. Use only accepted values. Example quantities are allowed when labeled as examples and the result does not depend on the specific number. A check adds no requirement: if it would need a threshold, target, or capability that has not been accepted, do not write it—create a question candidate for that value instead, offering "no numeric target" as a choice.
4. **Save shikomi.md after every incorporation.** Edit in place—insert or replace only the affected lines—rather than rewriting the file, and confirm that the saved diff touches only the intended lines. Do not reorder unrelated sections or alter their heading hierarchy. Keep additions minimal and testable.
5. **Validate after every save**, and run one final full pass after the last round:
   - For Step 4A, re-read the saved file and count the Clarifications lines. There must be exactly one non-duplicated line per accepted answer. Verify that this session added one line per accepted answer beyond the baseline. Repair discrepancies before presenting the next question. For Step 4B, ensure Clarifications has no diff.
   - Ensure requirement and scenario identifiers are unique within the spec and increase within their section, that no requirement is overridden by a requirement in another section, and that a superseded decision's requirements and scenarios were updated in the same operation.
   - When event order affects an outcome, check that the spec states the ordering rule and that an acceptance scenario covers the outcome. If rules differ across records, check how they interact.
   - Ensure no ambiguous text or placeholder that the incorporation should resolve remains.
   - For each remaining open point, check that the fact to verify or the decision the user must make and its impact are clear. Check that the specification and acceptance criteria leave the point open.
   - Ensure no invalidated option or conflicting obsolete text remains.
   - Ensure Markdown structure is valid. Keep existing headings. Add only relevant standard sections, the Clarifications headings from Step 4A, and acceptance criterion headings.
   - Ensure every new requirement is a numbered statement, each scenario cites its originating requirement, accepted decision, or applicable confirmed rule and uses no unaccepted value, and no Clarifications line contradicts the main text without a supersession note.
   - Ensure canonical terminology is consistent across every updated section.

If tracking a consequence without a new user answer, cite the accepted rules and verified facts in the requirement and add no Q&A line. For decisions already recorded from a prior session, use the saved entry and its question wording as the reference.

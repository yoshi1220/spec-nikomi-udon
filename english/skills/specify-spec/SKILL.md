---
name: specify-spec
description: Start a change from user requirements, a backlog item (including a ticket URL), or an open-discussion summary. Draft or resume shikomi.md, then clarify goals and dependent decisions one question at a time before planning. Use import-requirements for other existing files used as the primary input.
---

# Draft and clarify a change specification

Use the requirements or backlog item to identify the purpose of the change. Read a summary supplied by path. Otherwise automatically use only the target feature’s `specs/<change>/saguri.md` when present. If the user asks to resume a previously drafted `shikomi.md`, use that file.

Follow [Prepare a specification](references/prepare-spec.md) for a new or resumed change. After preparing the draft, read and follow the required [clarification workflow](references/clarify-spec.md) and the two references it requires. Work through the decision tree in rounds, save each confirmed answer, and rescan until consequential questions are settled or explicitly deferred. After confirmation, follow the project workflow to `draft-basic-design` for a design draft or `plan-implementation` for planning.

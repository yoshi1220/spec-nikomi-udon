---
name: dandori
description: Turn a user-confirmed nikomi.md into dandori.md with an implementation approach, ordered tasks, and a verification method for every acceptance criterion.
---

# Plan the agreed change

Use the directory the user specifies. Otherwise, map the current `feature/<change-name>` branch to `specs/<change-name>/`. Ask for the directory if you cannot resolve it.

1. Read `nikomi.md`, find `<!-- nikomi-review: confirmed -->`, and check that no unresolved decision affects the implementation approach or acceptance criteria. If the specification needs confirmation, show the issue and wait for the user's decision.
2. Read the relevant system guidance, current specifications, code, and tests. Follow existing implementation patterns and reuse code where they fit the requirements. Record the reason if the change needs a different approach.
3. Write `dandori.md` in the change directory. For a new plan, start with the [plan template](assets/dandori.template.md). Keep the link to `nikomi.md` and describe the affected areas in the implementation approach. Give each independently verifiable task a checkbox, an execution order with dependencies, related acceptance criterion IDs, and a completion check. For every acceptance criterion, record its ID, how to check it, and a result initially marked pending.
4. Check that every acceptance criterion has a verification method and that the plan respects the agreed specification and constraints. When updating an existing plan, retain completion and evidence for unaffected tasks and criteria. Reopen affected tasks and mark affected criteria for re-verification, even if their IDs are unchanged.

When the user needs to decide, ask one question at a time. Normally offer three viable options in recommendation order, explain your first choice, and accept free-form input. Ask an open question when you cannot provide viable options.

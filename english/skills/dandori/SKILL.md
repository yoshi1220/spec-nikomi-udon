---
name: dandori
description: Turn a confirmed nikomi.md into dandori.md by building a directed task dependency graph, then recording an execution order and verification methods for the acceptance criteria.
---

# Plan the agreed change

Use the directory the user specifies. Otherwise, map the current `feature/<change-name>` branch to `specs/<change-name>/`. Ask for the directory if you cannot resolve it.

1. Read any existing `dandori.md` and mark it pending using the [plan update procedure](references/write-plan.md#update-an-existing-plan). Read `nikomi.md`, find `<!-- nikomi-review: confirmed -->`, and check that no unresolved decision affects the implementation approach or acceptance criteria. If the specification needs confirmation, show the issue and wait for the user's decision.
2. [Identify tasks and dependencies](references/build-task-graph.md). Compare the specification with the existing implementation. Treat each task as a node and each prerequisite as an edge from the prerequisite to its dependent task. Map each acceptance criterion to the work needed to verify it.
3. [Validate dependencies and order the tasks](references/order-tasks.md). Use the bundled helper to validate the graph and obtain the execution order. If a cycle or missing prerequisite cannot be resolved, identify the affected tasks and the decision needed.
4. [Write and verify the plan](references/write-plan.md) in the change directory's `dandori.md`. Use the [plan template](assets/dandori.template.md) for a new plan. If the specification needs to change, identify the relevant section and return to clarification.

When the user needs to decide, ask one question at a time. Normally offer three viable options in recommendation order, explain your first choice, and accept free-form input. Ask an open question when you cannot provide viable options.

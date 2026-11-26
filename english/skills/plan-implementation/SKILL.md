---
name: plan-implementation
description: Turn a confirmed shikomi.md into dandori.md by identifying the paths to change and building a directed task dependency graph. Record the planned directory and file changes, task order, and verification methods for the acceptance criteria.
---

# Plan the agreed change

Use the directory the user specifies. Otherwise, map the current `feature/<change-name>` branch to `specs/<change-name>/`. Ask for the directory if you cannot resolve it.

1. Read any existing `dandori.md` and mark it pending using the [plan update procedure](references/write-plan.md#update-an-existing-plan). Check that the first line of `shikomi.md` is `<!-- shikomi-review: confirmed -->` and that no unresolved decision affects the implementation approach or acceptance criteria. If the specification needs confirmation, show the issue and wait for the user's decision.
   - Use the target PBI’s `shitagaki.md` when present. Follow [design approval before planning](references/design-approval.md) to check the index or record an explicit emergency and its reason before identifying tasks.
2. Once the prerequisites are met, mark the implementation plan “In progress” if the index exists. Preserve any existing link. [Identify changed paths, tasks, and dependencies](references/build-task-graph.md). Compare the specification with the existing implementation to identify paths to change and define independently verifiable tasks. Treat each task as a node and each prerequisite as an edge from the prerequisite to its dependent task. Map each acceptance criterion to the work needed to verify it.
3. [Validate dependencies and order the tasks](references/order-tasks.md). Use the bundled helper to validate the graph and obtain the execution order. If a cycle or missing prerequisite cannot be resolved, identify the affected tasks and the decision needed.
4. [Write and verify the plan](references/write-plan.md) in the change directory's `dandori.md`. Put the implementation approach and planned changes ahead of the ordered task list. Use the [plan template](assets/dandori.template.md) for a new plan. If the specification needs to change, identify the relevant section and return to clarification.

When the user needs to decide, ask one question at a time. Normally offer three viable options in recommendation order, explain your first choice, and accept free-form input. Ask an open question when you cannot provide viable options.

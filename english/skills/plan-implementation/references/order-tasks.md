# Validate dependencies and order the tasks

## Pass the graph to the ordering helper

Assign unique task IDs. When updating a plan, retain the ID for the same work. Keep IDs when the order changes and give new tasks numbers that do not collide with IDs in the existing plan.

Set up a dedicated task graph using the [temporary GraphML operations](work-graph.md). Supply task IDs and direct prerequisites in priority order, then save the validated graph and obtain its execution order in the same call.

```sh
python3 -B "$helper" tasks "$graph" --print-order <<'JSON'
[
  {"id": "T-03", "depends_on": ["T-01", "T-02"]},
  {"id": "T-02", "depends_on": []},
  {"id": "T-01", "depends_on": []}
]
JSON
```

The helper chooses among tasks whose prerequisites have already been ordered. If several are ready, it uses their input order. This example returns `["T-02", "T-01", "T-03"]`. Use the returned order for the task list. Task numbers can differ from execution order.

Use input order for preferences such as explicit user priorities or an opportunity to verify something early. Edges represent prerequisites. When revising a plan without a change in priority, prefer the existing order.

## Revise an existing plan

1. Load the saved tasks and prerequisites. Reconstruct task-to-criterion links (`verifies`) from the existing verification table and criterion-to-behavior links (`exercises`) from the E2E specification where available. If the old plan has invalid references or cycles, trace the affected entries in the source documents and mark unverifiable passes for rechecking.
2. Before replacing the graph, run `affected FILE changed-ID --via requires verifies exercises` for tasks or criteria being changed or removed. Include those whose only change is a link. Keep the former dependents.
3. Validate the revised tasks with `tasks FILE --print-order`, then add the current links. Query changed and added starting IDs in the new graph. Review the starting IDs and dependents from both versions against verification methods and recorded results.

## Resolve validation failures

- The helper rejects duplicate IDs, repeated prerequisites, self-dependencies, unknown prerequisites, and cycles. Use a list only after validation succeeds.
- When a prerequisite is unknown, check for a typo, missing task, or a result already available in the implementation. If a completed task remains a prerequisite in the plan, include its node too.
- For a cycle, inspect the reported edges and what each task consumes. Remove an unnecessary dependency once its absence is justified. Extract a shared contract or preparation task if it can be completed first. Merge mutually dependent changes when they have no independent completion checks and can be verified together.
- Re-run the helper on the revised graph. If a specification decision or unconfirmed external prerequisite remains, identify the affected tasks and what would resolve the issue. Leave the plan unfinalized.

After ordering succeeds, [write and verify the plan](write-plan.md).

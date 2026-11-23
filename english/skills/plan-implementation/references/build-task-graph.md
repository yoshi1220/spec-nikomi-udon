# Identify tasks and dependencies

## Compare the specification with the existing implementation

1. Extract the expected behavior, agreed design decisions and constraints, and acceptance criteria from `shikomi.md`. For each criterion, identify the required setup, action, and observable outcome. Keep the criterion IDs from the specification.
2. Read the relevant system guidance, current specifications, code, and tests. Identify where the change enters the system, where relevant constraints are enforced, and which implementations and checks are reusable. Follow existing approaches where they fit. Record why a departure is necessary.
3. For each criterion, distinguish the work the change requires from existing behavior that only needs verification. Return to clarification if a decision would change the specification. Investigate technical unknowns using the implementation or tests. If the investigation could change the plan itself, identify what needs investigating and what result would let planning resume.

When technical context affects implementation or verification, consult the relevant sections of `designs/technical-context.md` if available and compare the target environment's current configuration with the approved target. Cite the evidence in the plan and account for rollout or environment setup in task dependencies and checks.

## Define independently verifiable tasks

Give each task an ID, the prerequisites it needs, the result it provides, its related acceptance criterion IDs, and a completion check. Tasks and criteria can map many-to-many. Represent shared work needed by several criteria as one task and reference it from each criterion. Keep criteria that require no implementation in the verification plan and link them to an existing test or manual check.

- When a behavior can be implemented and verified through an existing entry point, the corresponding changes and tests can form one task.
- Split work when a result has its own verification and is useful to later work. Headings, layers, and files alone do not determine task boundaries.
- Distinguish task completion from acceptance verification. If acceptance verification needs several results, include all the required task IDs in its verification method. If a separate integration test or manual verification needs its own task, give it a node with the necessary tasks as prerequisites.

When planning PBI E2E checks for a method that uses test code, include preparing tests in the current `specs/<change>/e2e/` and running them during implementation.

## Connect direct prerequisites

`A → B` means B needs A's result to proceed through its completion check. Record A's ID under B, with the result B requires. If B needs several results, record each prerequisite.

- Ask what B needs, whether the existing implementation already provides it, and whether B can be verified before A is complete. Cite available results as evidence without creating additional tasks.
- Ground each edge in implementation or verification, such as a consumer needing an updated contract, new reads needing migrated data, or an integration check needing several changes.
- The order of the specification, shared files, and sequencing preferences alone do not justify edges. An indirect prerequisite can be traced through intermediate edges. Also record it directly when B independently consumes that result.
- When external data or approval is required, check who provides it and when it is available. Make preparation a task if its owner can perform and verify it. Keep an unconfirmed prerequisite visible and resolve it before treating its dependent work as ready.

Pass the task IDs and dependencies to [the ordering procedure](order-tasks.md). Keep the task descriptions, dependency reasons, and criterion mappings for the plan.

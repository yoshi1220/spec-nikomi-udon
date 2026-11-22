# Extract structure from requirements material

Assess the capability tree and relationship graph independently. Build each from the parts the input supports. Keep a locator for the evidence, such as a section, page, table row, diagram, or the user's description. Record constraints and users in the relevant overview sections even when they do not belong in the tree or graph.

## Decide what to produce from the evidence

| Evidence in the input | What to record in the system overview |
| --- | --- |
| Purpose, users, and scope | Summarize what is known. Mark capabilities or integrations as unconfirmed when information is missing. |
| Capability names or descriptions | List the capabilities and describe what they enable where documented. |
| A capability inventory, menu, or prose that establishes grouping or parent-child relationships | Build the supported branches and levels of the capability tree. List capabilities whose parent is unknown separately. |
| Relationships between capabilities or systems with known endpoints, type, and direction | Record the supported edges as a directed graph. |
| A relationship with an unknown endpoint, type, or direction | Record the known facts in prose and mark the open points as unconfirmed. Leave that relationship out of the graph. |

## Build the capability tree

- Present supported parent-child relationships as a nested list. Cite the evidence for each branch or group of branches. Use document headings when the material shows that they represent a capability hierarchy.
- If the material explicitly places one capability in several groups, describe it once as shared and reference it from those groups. Add a primary parent only when the evidence establishes one.
- If the hierarchy contains a cycle, check for different capabilities with the same name or confusion between containment and dependency. Mark unresolved branches as unconfirmed. Keep program directory placement grounded in separate evidence from the input.

## Build the relationship graph

- Use capabilities or systems found in the material as nodes. Represent each edge as one row from source to target, with its relationship type and evidence. Point calls from caller to callee, data transfers from sender to recipient, and dependencies from the dependent to what it relies on. Include the data or applicable condition if known.
- Distinguish different capabilities or systems that share a name by qualifying them with their wider context. If it is unclear whether two references name the same node, leave that point unconfirmed and keep them separate.
- Record a two-way integration as two edges when the evidence supports both directions. If sources give opposite directions for the same integration, check for differences in conditions or versions. Mark an unresolved conflict as unconfirmed. Keep distinct relationship types between the same nodes and retain cycles supported by the material. The graph describes system relationships and does not determine task order.

## Check and save the overview

- When sources disagree with each other or with an existing document, record the conflicting claims and both locators, and mark the point as unconfirmed. Leave disputed branches or edges out of confirmed additions. Preserve existing text until the user resolves the conflict and point from the affected entry to the unresolved issue. Ask one consequential confirmation question at a time. Continue documenting supported parts while awaiting an answer.
- Before saving, check that each branch and edge is traceable to evidence, each edge has identifiable endpoints, type, and direction, and open points are visible in prose.
- After reviewing the available material, label remaining unknowns “Unconfirmed” and collect them under “Points for user confirmation.” State what evidence, factual confirmation, or choice you need from the user, why, and what it affects. Keep capabilities whose parent is unknown in the list and mark the parent as unconfirmed. Confirm classifications and relationships only when supported by evidence.
- When updating an existing overview, reuse any “Open questions and decisions” section and bring its heading and labels into line with the current format. After saving, tell the user what needs confirmation. If several points remain, point to the recorded list and ask one question at a time, starting with the point that has the greatest impact.

## Example with partial input

A capability list names “Enter order” and “View orders,” with no grouping. An integration table says “Enter order calls the inventory system.” Another entry says only “integrates with the accounting system.” List the capabilities. Add the call from “Enter order” to the inventory system and cite the integration table. Record what is known about the accounting integration in prose and mark missing details, such as its type and direction, as unconfirmed.

# spec-nikomi-udon usage guide

[日本語](../../japanese/docs/usage-guide.md)

In a new project, establish the system-wide guidance, then take the first feature from specification through implementation and testing. In an existing project, document the current behavior from the code first and use that design as the basis for the first change. Both workflows retain the agreed specification and test results so the team can review the implementation and design updates in the same pull request (PR).

- [Build the first feature in a new project](#build-the-first-feature-in-a-new-project)
- [Adopt the framework and deliver the first change in an existing project](#adopt-the-framework-and-deliver-the-first-change-in-an-existing-project)
- [Skills to use as needed](#skills-to-use-as-needed)

~~~mermaid
flowchart TD
    N["New project · define-system-context<br/>Establish system-wide guidance"] --> S
    E["Existing project · document-existing-system<br/>Review and merge the current design in a documentation PR"] --> S
    S["specify-spec / import-requirements<br/>Agree on the change and its acceptance criteria"] --> D["draft-basic-design<br/>Draft the feature design"]
    D -->|Approval disabled| P["plan-implementation<br/>Order tasks and plan tests"]
    D -->|Approval enabled| A["record-design-approval<br/>Record approval for the draft"]
    A --> P
    P --> I["implement-plan<br/>Implement and verify the acceptance criteria"]
    I --> T["run-feature-e2e<br/>Run E2E and verify the results"]
    T --> M["apply-basic-design<br/>Update the design and history on the work branch"]
    M --> R["Review and merge the implementation and design in the same PR"]
~~~

## Before you start

This guide covers v0.0.8. Use the skills in your project's Git repository. During setup, choose how to run end-to-end (E2E) tests that exercise the application and whether the project requires design approval before planning. [Installation instructions](../../README.md#initialize-the-project)

Enter prompts such as `$specify-spec` in the **Codex conversation** for the target project. In Claude Code, replace the leading `$` with `/`. Review each skill's saved artifacts before moving to the next step. To resume an existing change, open the same work branch or specify the change directory.

Both examples use a notes app. Split the work into product backlog items (PBIs) that users can verify independently, such as creating a note or searching by title.

## Build the first feature in a new project

Build an app where users can save work notes and revisit them from a list. The first PBI covers saving a title and body and showing the title in the list.

### 1. Establish the system-wide guidance — `define-system-context`

~~~text
$define-system-context Build an app for saving work notes and revisiting them from a list. Start with creating and listing notes.
~~~

If you have a requirements document, pass it with `$define-system-context --file <requirements-path>`. The skill reads the document or description, identifies supported feature groupings, and maps relationships among functions and external systems. It reviews open technical decisions with the team one question at a time.

| Artifact | Contents |
| --- | --- |
| `designs/system-overview.md` | System purpose, scope, main features, integrations, shared constraints, and supporting sources |
| `designs/repository-structure.md` | Where the program's files go and what each directory is for, with a template to fill in if the layout is still open |
| `designs/technical-context.md` | Technologies and decisions for environments such as development, test, and production, including unverified points and planned migrations |

Review the initial scope and shared constraints. For example, agree that the list shows saved notes and that searching and editing belong in later PBIs. The next step uses that guidance to work out the details of the first change. [`define-system-context` procedure](../skills/define-system-context/SKILL.md)

### 2. Agree on the change specification and acceptance criteria — `specify-spec`

~~~text
$specify-spec Save a title and body and display the title in the list. If the title is empty, prompt for it and skip saving.
~~~

The skill prepares a work branch and change directory, such as `feature/001-create-note` and `specs/001-create-note/`. In the change directory, it drafts `shikomi.md` and creates `oshinagaki.md`, the index of deliverables and their statuses.

The conversation resolves one decision at a time. For example, can the body be empty? How should whitespace-only titles be handled? Should the title still appear after refreshing the list? The skill saves decisions as you agree on them and assigns IDs to acceptance criteria. Each criterion pairs an action with a result you can observe.

| Criterion | Action | Observable result |
| --- | --- | --- |
| `AC-01` A note can be saved | Enter “Weekly meeting” and a body, save, then reload the list | “Weekly meeting” appears in the list |
| `AC-02` A note with an empty title is rejected | Leave the title empty, enter a body, and submit | A title-required message appears and the list count stays the same after reloading |

Review the saved specification and acceptance criteria. The specification stays pending while a decision could change the implementation or the pass criteria. For example, if the team still needs to decide whether to accept whitespace-only titles, resume with `$specify-spec` on the same branch. The skill marks the specification as confirmed once those decisions are settled and you explicitly confirm the saved document. [`specify-spec` procedure](../skills/specify-spec/SKILL.md)

### 3. Draft the feature's basic design — `draft-basic-design`

~~~text
$draft-basic-design
~~~

The skill reads the saved `shikomi.md`, the system-wide guidance, and relevant sources. It turns them into `shitagaki.md` using the project's format. In this example, the design covers the entry form, the validation rules for saving, what appears in the list after saving, and what happens when validation fails. Any manual edits saved in the specification feed into the draft.

The accompanying `structure-plan.json` records the reason for the change, where the design belongs, and which sections or feature relationships need updating. The revision history uses this reason. If the project has screen item definitions enabled and the change affects a screen, the skill also creates `screen-items.md`. Check that the draft matches the acceptance criteria and describes observable results for success and failure. [`draft-basic-design` procedure](../skills/draft-basic-design/SKILL.md)

**If the project requires design approval before planning**, obtain approval through the project's process and record it with `record-design-approval` now. With the default `none` mode, review the draft and proceed to planning. [Record design approval](#record-design-approval--record-design-approval)

### 4. Plan the implementation order and tests — `plan-implementation`

~~~text
$plan-implementation
~~~

The skill derives tasks from the confirmed `shikomi.md` and design draft and uses a directed graph to check their dependencies. For example, implement storage and validation, connect the form and list, then verify saving and validation errors. The execution order puts prerequisites before the tasks that depend on them.

- `dandori.md` records dependencies, execution order, completion criteria for tasks and subtasks, the unit-test plan, and how to verify each acceptance criterion.
- `e2e.md` records test environments and data, steps, expected outcomes, and linked acceptance criterion IDs. When screenshots are enabled, it specifies what should be visible at each capture point.

Check that each acceptance criterion has a verification method that can detect the intended failure. For `AC-02`, for example, verify both that the message appears and that the note is absent from the list. Proceed when the prerequisites are in place and the plan is ready to execute. [`plan-implementation` procedure](../skills/plan-implementation/SKILL.md)

### 5. Implement the plan and record verification — `implement-plan`

~~~text
$implement-plan
~~~

The skill checks `shikomi.md` against the executable `dandori.md` and implements the tasks whose prerequisites are satisfied. In this example, it implements storage, validation, the entry form, and the list. A unit test checks that empty titles are rejected, with its failure before implementation and pass afterward recorded in the plan. The plan also records completed tasks and the check that passed for each acceptance criterion, so you can resume in a later session.

For automated E2E, the skill creates or updates tests in `specs/<change>/e2e/` and runs them during implementation. Once the tasks are complete and the acceptance criteria have been verified, it hands the completed change and tests to `run-feature-e2e`. [`implement-plan` procedure](../skills/implement-plan/SKILL.md)

### 6. Run E2E tests and verify the results — `run-feature-e2e`

~~~text
$run-feature-e2e
~~~

The skill checks that the specification, executable plan, completed tasks, and current passes for every acceptance criterion agree. It runs the scenarios in `e2e.md` using the project's E2E method. In automated mode, it reruns the tests for the same PBI. In manual mode, the tester follows the steps and supplies the observations. For example, check that “Weekly meeting” appears after saving and that a note with an empty title is rejected.

The skill records observed results and verdicts in `e2e.md`. If screenshots are required, the results link to the images for this run under `specs/<change>/evidence/<run-id>/`. Once the run completes successfully and all required cases pass, the skill verifies the run ID, results, and evidence. If the project requires design approval, the reviewer confirms the steps and results, and the skill records that confirmation in the same `e2e.md`.

If a case fails, return to `implement-plan` for implementation or test-code issues, or to `plan-implementation` if tasks or verification methods need to change. Once recovery is possible, the skill retests once. If the problem persists, it presents the affected cases and observations for the team to resolve. If prerequisites prevent a case from running, it records the case and the environment or data it needs. [`run-feature-e2e` procedure](../skills/run-feature-e2e/SKILL.md) · [Recover from a failed test](../skills/run-feature-e2e/references/recover.md)

### 7. Prepare the canonical design update and review it with the implementation — `apply-basic-design`

~~~text
$apply-basic-design
~~~

The skill checks that `shikomi.md`, `shitagaki.md`, and `e2e.md` agree. It validates the required E2E passes and any required reviewer confirmation against the current change. Once those checks pass, it prepares the design, current structure, and revision history under `designs/specifications/` on the work branch. The change index, `oshinagaki.md`, links to the updated locations.

Review the implementation, design, and test results in the PR. After the merge the shared branch holds the canonical design for note creation. The next PBI can use it to establish current behavior and determine what to add or change. [`apply-basic-design` procedure](../skills/apply-basic-design/SKILL.md) · [Canonical structure and history](../skills/apply-basic-design/references/structure.md)

## Adopt the framework and deliver the first change in an existing project

The notes app already supports creating and listing notes. Adopt the framework and add partial title search to the list. First review the current design in a documentation-only PR. Then implement and review search in a separate change PR.

### 1. Inspect the current features and technical context — `document-existing-system`

~~~text
$document-existing-system Identify the current features and technical context, then document the basic design. The first planned change adds title search to the notes list.
~~~

By default, the skill inspects the current commit. Specify a tag or commit if you want to start from the version in use. It traces screens, APIs, configuration, code, and existing tests at that revision and records verified functions and relationships in `designs/system-overview.md`. When the team explicitly confirms the inventory, the skill saves the confirmation and analyzed revision. It uses the same revision to prepare `designs/technical-context.md`, including the environments and any points still to verify.

By default, document the entire system as far as the evidence supports. You can limit the design text to note creation and listing, for example, if those are the functions the first change affects. The system structure still records all verified functions and relationships and shows where design text is pending. The saved revision and scope let you resume the investigation later. [`document-existing-system` procedure](../skills/document-existing-system/SKILL.md)

### 2. Review the current design in a documentation PR

`document-existing-system` documents the current behavior and its sources in `designs/specifications/`. For example, it checks the statement “The list initially shows saved notes” against implementation and tests from the analyzed revision. Behavior that can only be established in the running environment remains marked as unverified.

Within that directory, `structure/` holds the graph of function hierarchies and dependencies and an index from stable IDs to sections in the design documents. The `history/` directory includes revisions by ID. These records let you trace a function's revisions even when its name or document location changes.

Review the analyzed revision, scope, sources, and open points in the onboarding documentation PR. Runtime verification is optional for this PR. Once it merges, the design on the shared branch becomes the canonical reference for the first change. [Investigation, resumption, and documentation review](../skills/document-existing-system/references/baseline.md)

### 3. Start the change and agree on what to add and what to preserve

Start from the shared branch containing the merged design. If the request comes from a ticket or a conversation, use `specify-spec` to create the work branch and specify the change.

~~~text
$specify-spec Add partial title search to the notes list. When the search field is empty, show the list as before.
~~~

For a request in Jira or GitHub Projects, pass the individual ticket URL directly. For example, with Jira, enter this prompt.

~~~text
$specify-spec https://jira.example.org/browse/NOTE-42
~~~

For GitHub Projects, pass the item link or the URL of its linked issue. The skill reads the ticket, drafts `shikomi.md` from the stated requirements and acceptance criteria, and cites the URL. If the ticket is inaccessible, paste its text or the relevant excerpt to continue.

If a requirements document or change request file is your primary input, use `import-requirements` instead.

~~~text
$import-requirements Start the notes search change using requirements/note-search.md as the primary input.
~~~

`import-requirements` reads the specified file before preparing the work branch. It drafts `shikomi.md` with references to the source. If the request says “search titles” but an attached table suggests searching the body too, the skill shows both passages and how they affect the specification, then asks the team to decide. It follows the same one-question-at-a-time clarification workflow as `specify-spec` through final confirmation. [`import-requirements` procedure](../skills/import-requirements/SKILL.md) · [`specify-spec` procedure](../skills/specify-spec/SKILL.md)

In this example, the criteria cover search and existing behavior that could be affected.

| What to check | Example test data and expected result |
| --- | --- |
| Show notes with a partial title match | Searching for “meeting” shows the note titled “Weekly meeting” |
| Exclude notes with a match only in the body | A note titled “Weekly report” with “meeting” only in the body stays out of the results |
| Show the full list when the search field is cleared | Clearing the field shows “Weekly meeting” and “Weekly report” again |
| Preserve note creation and validation | A new note can still be saved and an empty title is still rejected |

### 4. Implement against the existing design and check for regressions

After opening the change, use the same skills as for a new project. Check that each step accounts for the new behavior and the existing behavior the change could affect.

| Order | Action | What it produces in the search example |
| --- | --- | --- |
| 1 | `$draft-basic-design` | A draft based on the canonical list design. It adds the search field and filtering rules, describes what happens when the field is empty, and records effects on creation and listing and where to apply the update |
| 2 | If design approval is enabled, run `$record-design-approval` after approval | A record of approval for the current draft |
| 3 | `$plan-implementation` | The order of search implementation tasks and the E2E scenarios for search, clearing the field, and existing note creation |
| 4 | `$implement-plan` | The search implementation and work records, with reused or added tests checking effects on creation and listing |
| 5 | `$run-feature-e2e` | Results from operating the completed app and any required reviewer confirmation |
| 6 | `$apply-basic-design` | Updated design and revision history on the work branch. After the change PR merges, the shared canonical design includes search |

If the list stays filtered after clearing the field, use the observation from `run-feature-e2e` to see whether the agreed specification and plan already cover that case. If the plan is sufficient, fix the behavior with `implement-plan`, then retest. [Steps shared with new projects](#3-draft-the-features-basic-design--draft-basic-design)

## Skills to use as needed

### Explore the problem or scope — `open-discussion`

~~~text
$open-discussion People say they can't find saved notes. Start by identifying who is affected and when.
~~~

Work through concrete situations one question at a time to identify who has the problem, what triggers it, and how you will recognize an improvement. The first PBI might differ depending on whether people have trouble finding recent notes or searching older notes by keyword. Keep the agreed problem, direction, and unresolved points in the conversation or save them. The recommended file location is `saguri/<topic>/saguri.md`. Pass that path to `specify-spec` when starting the change. `specify-spec` automatically reads `specs/<change>/saguri.md` for the corresponding feature branch. [`open-discussion` procedure](../skills/open-discussion/SKILL.md)

### Record design approval — `record-design-approval`

Obtain design approval after reviewing the design draft and before planning implementation. Follow the workflow for the project's setting.

| Setting | Action and record |
| --- | --- |
| `none` (default) | Review the specification and draft, then proceed to planning |
| `operational` | Obtain approval through the project's process, then enter a prompt such as `$record-design-approval The design lead approved on 2026-11-20`. The index records the actual approval date and approver |
| `pr` | Run `$record-design-approval` after the draft has PR approval. The skill compares the approved revision with the current one and records valid approval in the index |

In `operational` mode, the project decides who records approval. The approver can check out the change branch on their own computer, run `$record-design-approval`, and commit the updated `oshinagaki.md` under their own Git identity. The commit history then shows who recorded the approval. Before planning on another computer, check out the branch revision containing that commit. If the project accepts verbal approval, the implementer can run the skill on the approver’s behalf. The index still records the person who approved the draft and the date they approved it.

In projects that require design approval, starting a redesign returns ordinary approval to pending and puts the existing plan on hold while preserving the work records. Obtain and record approval for the revised draft before reviewing the plan again. When the project authorizes emergency work, a prompt such as `$plan-implementation --emergency Restore production service` records the reason with the PBI. [`record-design-approval` procedure](../skills/record-design-approval/SKILL.md) · [Design approval settings](../../README.md#design-approval-before-planning)

### Migrate design documents to a new format — `restructure-design-docs`

~~~text
$restructure-design-docs Migrate the notes feature designs to the new project format.
~~~

Use this skill after the team adopts a format in `designs/basic-design.template.md` and wants to migrate existing feature designs together. The skill carries over business rules, behavior, sources, manual edits, and stable section IDs and prepares a documentation-only migration PR. Review whether the new headings preserve the design's meaning and identify any information needed for newly added sections. [`restructure-design-docs` procedure](../skills/restructure-design-docs/SKILL.md)

### Build system E2E tests — `create-system-e2e`

~~~text
$create-system-e2e
~~~

Use the current canonical design to prepare workflows in the root `e2e/` that the team wants to verify repeatedly after changes merge. For example, register a note, search for its title in the list, and check that the same note appears in the results. The skill checks whether existing cases verify the required outcomes, adds missing cases, and updates changed expectations to match the canonical design.

It records scenarios, steps, expected results, corresponding tests, and the required environment. If the project has no scenario format, it uses `e2e/scenarios.md`. In automated mode, it also puts test code in the root `e2e/`. [`create-system-e2e` procedure](../skills/create-system-e2e/SKILL.md)

### Run system E2E tests — `execute-system-e2e`

~~~text
$execute-system-e2e notes search
~~~

Select root E2E tests by feature, scenario ID, or file. Run `$execute-system-e2e` without a selection to run the full root suite. By default, the skill records the scope, environment, observations, and verdicts in `evidence/system/<run-id>/results.md`. The report links to screenshots captured for that run when required.

`run-feature-e2e` checks acceptance for a single PBI and records the results in that PBI's `e2e.md`. `execute-system-e2e` checks workflows, including those that span multiple features, against the current canonical design. [`execute-system-e2e` procedure](../skills/execute-system-e2e/SKILL.md)

### Apply the shared E2E authoring rules — `e2e-authoring`

`implement-plan` uses this skill for PBI tests, and `create-system-e2e` uses it for root tests. It also applies when the team edits tests directly. Give each case an ID and use an assertion that waits until the current test data or the expected error is visible after the action. When screenshots are enabled, capture the specified display immediately after verifying it and associate it with the run, case, and checkpoint. For example, verify that the title just saved is visible in the list before capturing it. [`e2e-authoring` procedure](../skills/e2e-authoring/SKILL.md)

## Find the saved artifacts

| What you want to know | Where to look |
| --- | --- |
| How far the PBI has progressed | `specs/<change>/oshinagaki.md` |
| What behavior the team agreed to deliver | `specs/<change>/shikomi.md` |
| What the draft says and where it will be applied | `specs/<change>/shitagaki.md` and `structure-plan.json` |
| How the change was implemented and which criteria were verified | `specs/<change>/dandori.md` |
| What E2E covered and how the results were verified | `specs/<change>/e2e.md` |
| What the current design is and how it has changed | `designs/specifications/` on the shared branch |
| Where to find the system scenarios and the results of a run | Root `e2e/` and `evidence/system/<run-id>/results.md` |

# spec-nikomi-udon

[日本語](README.ja.md)

spec-nikomi-udon is a spec-driven development (SDD) framework for teams working within established Japanese development practices (**伝統的日本型開発を支える仕様駆動開発フレームワーク**). It helps teams use AI within their existing development standards and approval procedures.

It is intended for systems integrators and teams at established Japanese companies, including teams that use prescribed design document formats or submit test results and approval records before release. It covers both new development and changes to existing systems.

## The development workflow

1. **Clarify the specification.** Use `shikomi` for requirements or a product backlog item (PBI) and `torikomu` for existing documents. Agree on scope, behavior, and acceptance criteria one question at a time, and record them in `shikomi.md`.
2. **Draft the basic design.** Review `shikomi.md` and make any needed edits. Use `shitagaki` to turn the saved specification into a functional basic design in `shitagaki.md`. If the project requires design approval, record it with `osumitsuki` before planning.
3. **Plan implementation and testing.** Use `dandori` to record tasks and verification methods in `dandori.md`. For changed behavior and existing behavior the change could affect, pair each input with an expected result that would reveal a defect. Use `e2e.md` to record E2E steps and expected results for each behavior under test.
4. **Implement and verify.** Use `nikomu` to implement the change and check that new or reused tests and manual checks can detect the failures identified in the plan. Then use `ajimi` to run E2E tests. If a test fails, `ajimi` returns to implementation or planning as needed and retests once. If the issue persists, it asks the user to intervene. A reviewer confirms what was tested and the results in the same test specification.
5. **Apply the canonical design.** Use `osameru` to verify the passes and reviewer confirmation and prepare the design and revision history under `designs/specifications/` on the work branch. Review the implementation and design in the same PR. The merge updates the canonical design.

Each PBI has an `oshinagaki.md` in its change directory that lists deliverables and their statuses.

## Installation

### Before `init`

Prepare the target Git repository, Git 2.23+, Python 3.8+, `uvx`, and Codex or Claude Code. The installer targets macOS, Linux, and WSL. Installation and update have been verified on macOS and Linux. On Windows, run it in a WSL terminal. WSL testing is pending. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

Move any manually installed skill directories with matching names out of the destination. The installer reads existing project settings from `designs/nikomi-udon.json`.

### Initialize the project

Run this command in the target Git repository for a fresh installation of v0.0.6.

```sh
uvx --from git+https://github.com/yoshi1220/spec-nikomi-udon.git@v0.0.6 spec-nikomi-udon init
```

To upgrade from v0.0.3, v0.0.4, or v0.0.5 and retain the project settings, run the following command.

```sh
uvx --from git+https://github.com/yoshi1220/spec-nikomi-udon.git@v0.0.6 spec-nikomi-udon update
```

Migration from v0.0.2 is manual. In v0.0.3 and later, use `shikomi` and `shikomi.md` for the change specification and `nikomu` for implementation.

Select a language and Codex, Claude Code, or both. The same skills go into `.agents/skills/` for Codex and `.claude/skills/` for Claude Code. For new projects, choose the E2E method, design approval mode, screenshots, and screen item definitions. Skills and settings are saved even if E2E preparation is pending. Rerun `init` with the same release to resume preparation or add the other agent.

Track the installed skills, project settings (`designs/nikomi-udon.json`), and installation record (`designs/nikomi-udon-install.json`) together in the project repository. If Git ignores any of these files, the installer reports the count and an example path. Use `git check-ignore -v -- <path>` to find the rule and include the distribution files you intend to share. If you edited the distributed skills directly, save those edits, restore the installed files to their original state, and reapply the edits you need after updating.

### After `init`

To change project settings, run `python3 .agents/skills/osameru/scripts/osameru.py setup` with the options you want to change. For a Claude-only installation, use `.claude/skills/`. [Settings and options](english/skills/osameru/references/format.md)

| Selected method | Preparation and verification |
| --- | --- |
| Playwright | Reuse the project's runner. If additional setup is needed, review the displayed commands and choose whether to run them. Install any missing OS dependencies or project-specific prerequisites and rerun the same `init`. The setup probe uses Chromium. For example, an npm project uses `npm install -D @playwright/test` and `npx playwright install chromium`. A uv-managed Python project uses `uv add --dev pytest-playwright` and `uv run playwright install chromium`. [Browser setup](https://playwright.dev/docs/browsers) |
| Agent browser | Enable the built-in browser in Codex desktop, or configure the official Chrome extension for Claude Code and check its connection with `/chrome`. Grant access to the test site and sign in where needed. End-to-end testing on a real project is pending for both integrations. In the session you will use, operate the target screen and check that you can observe the expected value. For Claude Code on WSL, use an available method such as Playwright or manual testing. [Codex](https://learn.chatgpt.com/docs/browser) / [Claude Code](https://code.claude.com/docs/en/chrome) |
| Chrome extension | Install the project's extension that can evaluate expected results and configure access to the test site. |
| Manual testing | Give the tester access to the target environment so they can use the specified test data and record observed results and verdicts. [E2E workflow](english/skills/ajimi/references/run-e2e.md) |

If the installer cannot identify the dependency manager, use the project’s own tooling to prepare the runner and Chromium. If a Python project uses `requirements.txt` and needs a runner, accepting setup installs the listed dependencies together with `pytest-playwright` into `.venv`. Existing version pins and constraints apply. When adding the runner for the first time, record it in the project’s test requirements so teammates can recreate the environment.

If you choose `pr` for design approval and use GitHub CLI to check reviews, install `gh` and authenticate with access to the target repository and pull request. [Recording design PR approval](english/skills/osumitsuki/SKILL.md)

Start a session in the target project. To specify one change, use `$shikomi` in Codex or `/shikomi` in Claude Code. To run E2E tests, use `$ajimi` or `/ajimi`, respectively.

Use `kondate` to turn requirements documents or a short description into system-wide guidance. It records the purpose, main capabilities, and shared constraints in `designs/system-overview.md` and the program layout in `designs/repository-structure.md`.

To document the technologies used in each environment, prepare `designs/technical-context.md` with `kondate` for a new project or `okosu` for an existing one. Start from a team draft, requirements, or the existing code and configuration, then resolve technical decisions one at a time. Consult the relevant sections during specification, planning, and verification. Use `kondate` with a specific section to record a technology decision or a confirmed rollout.

When you are still deciding what to change, `saguru` explores a real or anticipated situation one question at a time and revisits unknowns that could change the direction. The recommended location for the summary is `saguri/<topic>/saguri.md` at the repository root. If the change already has a feature branch, you can also save it as `specs/<change>/saguri.md`. You can also keep it in the conversation. Only the target feature’s `saguri.md` is read automatically by `shikomi`. To use a top-level summary, supply its path or move it to the feature location.

### Design approval before planning

`dandori` requires a confirmed `shikomi.md` and uses `shitagaki.md` when available. Choose the approval mode for the project. For example, to enable PR review in a Codex installation, run the following command in the target repository.

```sh
python3 .agents/skills/osameru/scripts/osameru.py setup --design-approval pr
```

PBIs get a design approval section in `oshinagaki.md` when their project uses approval.

| Initial setting | Before planning |
| --- | --- |
| `none` (default) | Proceed after confirming the specification. The index has no approval section. |
| `operational` | Obtain approval through the project's process, then invoke e.g. `$osumitsuki The design lead approved on 2026-11-20`. Both the approval date and approver are required. |
| `pr` | Once the design has PR approval, invoke `$osumitsuki`. It verifies the revision and records the approval date and reviewer in the index. |

`dandori` proceeds from the approved index. When `shitagaki` starts a redesign, it returns a normal approval to pending and puts the existing plan on hold. The plan keeps its recorded work for `dandori` to review. For an authorized emergency, invoke e.g. `$dandori --emergency Restore production service`. The emergency and reason stay with the PBI, including after a redesign. Resume with a normal `dandori` invocation. Use `/` in place of `$` in Claude Code.

An in-progress PBI is migrated when next handling design, approval or planning. Its existing records can establish approval of the current design with a date and approver, or a PBI emergency with its reason. If the records establish neither, the design and any existing plan go on hold. The plan retains its tasks and results. [Record approval](english/skills/osumitsuki/SKILL.md) · [Migrate the index](english/skills/osumitsuki/references/index.md)

## Use a project basic design template

The installer creates `designs/basic-design.template.md` and `designs/basic-design-writing.md`. Share both in the project repository. The team can edit the template title, headings, and tables. The next time `okosu`, `shitagaki`, or `koromogae` uses the template, it updates the writing guidance to match.

Installer updates preserve the project's template and guidance. If the bundled standard template changes, review the diff shown by the installer and copy the changes you choose into the project template. Find the bundled template at `shitagaki/assets/basic-design.template.md` under the installed skills directory.

Existing designs use the new template the next time they are written or revised. To migrate them in bulk, run `$koromogae` in Codex or `/koromogae` in Claude Code. It prepares one documentation PR for the selected designs by default. You can also request separate PRs by business area or function. Review the diff for preservation of design content and manual edits, then merge to update the canonical designs. [Migration workflow](english/skills/koromogae/SKILL.md)

## Document the current design of an existing project

In the existing repository, invoke `$okosu` in Codex or `/okosu` in Claude Code. New onboarding work starts from the current commit by default. You can also name a branch, tag, or commit to analyze. [okosu workflow](english/skills/okosu/SKILL.md)

1. Review the system-wide function inventory and relationships in `designs/system-overview.md`. The same file records the confirmation state, selected scope, and analyzed commit so you can resume in another session.
2. By default, document the entire system to the extent supported by the evidence. You can also select a narrower scope. Under `designs/specifications/`, `structure/` holds the current GraphML and section index. `history/` holds historical GraphML, revisions by node ID and retired text. [Structure and history](english/skills/osameru/references/structure.md)
3. Review the documentation-only onboarding PR against the code, configuration, and existing tests at the analyzed revision. Points that can only be established at runtime remain marked as unverified. After the merge, use the designs on the shared branch as the canonical reference for the first change.

## Build the first feature in a new project

This example builds the first feature of a notes app in a Git repository with the skills installed and design approval set to the default (`none`). In Codex, enter each line starting with `$`, one at a time. The `#` lines explain each skill. In Claude Code, replace the leading `$` with `/`.

```text
# Outline the app’s purpose and main features in designs/system-overview.md.
$kondate Build an app for saving work notes and finding them in a list.

# Create a work branch and agree on the acceptance criteria in shikomi.md.
$shikomi Save the title and body. List titles. If untitled, prompt for a title and skip saving.

# Draft the design for note creation in shitagaki.md from the agreed specification.
$shitagaki

# Put tasks in execution order in dandori.md and E2E steps and expectations in e2e.md.
$dandori

# Implement the plan and record progress and verification results in dandori.md.
$nikomu

# Try saving a note with and without a title. Record the E2E results in e2e.md.
$ajimi

# Verify test passes and reviewer confirmation. Update the design and history on the work branch.
$osameru Use "Add note creation" as the change reason.
```

Use `shikomi` to agree on the specification and acceptance criteria, then review `shikomi.md` and continue on the same work branch. Before implementing, review `shitagaki.md`, `dandori.md`, and the E2E test specification `e2e.md` under `specs/<change>/`.

For automated PBI E2E tests, `nikomu` prepares tests in `specs/<change>/e2e/` and runs them during implementation. `ajimi` reruns the same tests and records the integration test results in that PBI’s `e2e.md`. These results correspond to the acceptance criteria at the time of testing. Keep system tests for ongoing verification of end-to-end workflows in the repository’s top-level `e2e/` directory and update them as the system specification changes.

Run `osameru` once all required E2E tests pass and the reviewer's confirmation is recorded in `e2e.md`. Review the implementation and design in the same PR and merge it to update the canonical design.

## Create and run system E2E tests

Use `$moritsuke` to compare current `designs/specifications/` with existing assertions and prepare workflows and missing tests in the root `e2e/`. Run `$shishoku` for the full root suite or use a selection such as `$shishoku order lookup`. In Claude Code use `/moritsuke` and `/shishoku`.

PBI and root tests wait for the expected visible value, then save the specified checkpoints when captures are enabled. Root E2E reports and images are saved under `evidence/system/<run-id>/` by default. Each test result links to its checkpoint images. Claude Code installations receive `.claude/rules/nikomi-e2e.md` scoped to the two E2E paths. Both Codex authoring workflows consult the shared skill before writing tests and add a pointer to instructions inside the target `e2e/`. [E2E authoring rules](english/skills/e2e-authoring/SKILL.md)

## License

Starting with the v0.0.6 series, including development builds, this project is licensed under the [Apache License, Version 2.0](LICENSE). Releases through v0.0.5 carry the MIT license included with those releases.

Individuals and companies may use the project free of charge, including for commercial purposes. You may modify it for internal use and keep those changes private.

**Does a customer delivery need this license?**

- **Delivering only your own application.** Using spec-nikomi-udon to develop the application does not require you to display this license, credit the framework in the application, or publish the application's source code.
- **Delivering the framework with the application.** For example, if the repository you hand to a customer still contains the installed skills or scripts, you are distributing those files too. The conditions below apply to those files, including any copies you modified.

**When you distribute the framework, any part of it, or a modified version (Section 4)**

- Give recipients a copy of the full license, whether you distribute the original or a modified version.
- Put a prominent notice in each file you changed stating that you changed it.
- When distributing a derivative in source form, retain the copyright, patent, trademark, and attribution notices from the original source that apply to the parts you distribute.
- Include a readable copy of the applicable attributions from [NOTICE](NOTICE) in your derivative. They can appear in a distributed `NOTICE` file, in accompanying source or documentation, or in a display where such notices normally appear.

**If you publish a fork or modified version (optional)**

- Please credit spec-nikomi-udon and link to the [original repository](https://github.com/yoshi1220/spec-nikomi-udon) in your README.
- We encourage you to summarize the main additions, changes, and removals in your README or CHANGELOG.
- Please identify who maintains your version so readers can distinguish it from an official or endorsed release.

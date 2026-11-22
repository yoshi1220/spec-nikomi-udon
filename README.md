# spec-nikomi-udon

[日本語](README.ja.md)

spec-nikomi-udon is a spec-driven development (SDD) framework for teams working within established Japanese development practices (**伝統的日本型開発を支える仕様駆動開発フレームワーク**). It helps teams use AI within their existing development standards and approval procedures.

It is intended for systems integrators and teams at established Japanese companies, including teams that use prescribed design document formats or submit test results and approval records before release. It covers both new development and changes to existing systems.

## The development workflow

1. **Clarify the specification.** Use `shikomi` for requirements or a product backlog item (PBI) and `torikomu` for existing documents. Agree on scope, behavior, and acceptance criteria one question at a time, and record them in `shikomi.md`.
2. **Draft the basic design.** Review `shikomi.md` and make any needed edits. Use `shitagaki` to turn the saved specification into a functional basic design in `shitagaki.md`.
3. **Plan implementation and testing.** Use `dandori` to record tasks and verification methods in `dandori.md`. For changed behavior and existing behavior the change could affect, pair each input with an expected result that would reveal a defect. Use `e2e.md` to record E2E steps and expected results for each behavior under test.
4. **Implement and verify.** Use `nikomu` to implement the change and check that new or reused tests and manual checks can detect the failures identified in the plan. Then use `ajimi` to run E2E tests. If a test fails, `ajimi` returns to implementation or planning as needed and retests once. If the issue persists, it asks the user to intervene. A reviewer confirms what was tested and the results in the same test specification.
5. **Apply the canonical design.** Use `osameru` to verify the passes and reviewer confirmation and prepare the design and revision history under `designs/specifications/` on the work branch. Review the implementation and design in the same PR. The merge updates the canonical design.

Each PBI has an `oshinagaki.md` in its change directory that lists deliverables and their statuses.

## Installation

### Before `init`

Prepare the target Git repository, Git 2.23+, Python 3.8+, `uvx`, and Codex or Claude Code. The installer targets macOS, Linux, and WSL. Installation and update have been verified on macOS and Linux. On Windows, run it in a WSL terminal. WSL testing is pending. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

Move any manually installed skill directories with matching names out of the destination. The installer reads existing project settings from `designs/nikomi-udon.json`.

### Initialize the project

Run this command in the target Git repository for a fresh installation of v0.0.3.

```sh
uvx --from git+https://github.com/yoshi1220/spec-nikomi-udon.git@v0.0.3 spec-nikomi-udon init
```

Migration from v0.0.2 is manual. In v0.0.3, use `shikomi` and `shikomi.md` for the change specification and `nikomu` for implementation.

Select a language and Codex, Claude Code, or both. The same skills go into `.agents/skills/` for Codex and `.claude/skills/` for Claude Code. For new projects, choose the E2E method, design approval mode, screenshots, and screen item definitions. Skills and settings are saved even if E2E preparation is pending. Rerun `init` with the same release to resume preparation or add the other agent.

To update an installation of this edition, use the same command with `update` in place of `init`. Track the installed skills, project settings (`designs/nikomi-udon.json`), and installation record (`designs/nikomi-udon-install.json`) together in the project repository. If Git ignores any of these files, the installer reports the count and an example path. Use `git check-ignore -v -- <path>` to find the rule and include the distribution files you intend to share. If you edited the distributed skills directly, save those edits, restore the installed files to their original state, and reapply the edits you need after updating.

### After `init`

To change project settings, run `python3 .agents/skills/osameru/scripts/osameru.py setup` with the options you want to change. For a Claude-only installation, use `.claude/skills/`. [Settings and options](english/skills/osameru/references/format.md)

| Selected method | Preparation and verification |
| --- | --- |
| Playwright | Reuse the project's runner. If additional setup is needed, review the displayed commands and choose whether to run them. Install any missing OS dependencies or project-specific prerequisites and rerun the same `init`. The setup probe uses Chromium. For example, an npm project uses `npm install -D @playwright/test` and `npx playwright install chromium`. A uv-managed Python project uses `uv add --dev pytest-playwright` and `uv run playwright install chromium`. [Browser setup](https://playwright.dev/docs/browsers) |
| Agent browser | Enable the built-in browser in Codex desktop, or configure the official Chrome extension for Claude Code and check its connection with `/chrome`. Grant access to the test site and sign in where needed. End-to-end testing on a real project is pending for both integrations. In the session you will use, operate the target screen and check that you can observe the expected value. For Claude Code on WSL, use an available method such as Playwright or manual testing. [Codex](https://learn.chatgpt.com/docs/browser) / [Claude Code](https://code.claude.com/docs/en/chrome) |
| Chrome extension | Install the project's extension that can evaluate expected results and configure access to the test site. |
| Manual testing | Give the tester access to the target environment so they can use the specified test data and record observed results and verdicts. [E2E workflow](english/skills/ajimi/references/run-e2e.md) |

If the installer cannot identify the dependency manager, use the project’s own tooling to prepare the runner and Chromium. If a Python project uses `requirements.txt` and needs a runner, accepting setup installs the listed dependencies together with `pytest-playwright` into `.venv`. Existing version pins and constraints apply. When adding the runner for the first time, record it in the project’s test requirements so teammates can recreate the environment.

If you choose `pr` for design approval and use GitHub CLI to check reviews, install `gh` and authenticate with access to the target repository and pull request. [Checking design PR reviews](english/skills/dandori/references/design-approval.md)

Start a session in the target project. To specify one change, use `$shikomi` in Codex or `/shikomi` in Claude Code. To run E2E tests, use `$ajimi` or `/ajimi`, respectively.

Use `kondate` to turn requirements documents or a short description into system-wide guidance. It records the purpose, main capabilities, and shared constraints in `designs/system-overview.md` and the program layout in `designs/repository-structure.md`. Use `saguru` to explore a problem before deciding what to change.

### Design approval before planning

`dandori` requires a confirmed `shikomi.md` and uses `shitagaki.md` when available. Choose the approval mode for the project. For example, to enable PR review in a Codex installation, run the following command in the target repository.

```sh
python3 .agents/skills/osameru/scripts/osameru.py setup --design-approval pr
```

| Setting | When planning can begin |
| --- | --- |
| `none` (default) | Proceed once the specification is confirmed. The team can review the design alongside the implementation in the final PR. |
| `operational` | The operator obtains design approval through the project’s process, then invokes `dandori`. Invocation counts as confirmation. |
| `pr` | `dandori` checks the design PR. Planning can begin before merge when the local draft matches the approved design. |

If `dandori` cannot verify PR approval, it explains why and asks whether to continue. If the operator continues, it records the unconfirmed item and the decision in the PBI’s `dandori.md`. For an exception such as an emergency change, obtain authorization from the project’s designated role and record the reason and confirmation in the same file. [Selecting the design PR and handling exceptions](english/skills/dandori/references/design-approval.md)

## Use a project basic design template

The installer creates `designs/basic-design.template.md` and `designs/basic-design-writing.md`. Share both in the project repository. The team can edit the template title, headings, and tables. The next time `okosu`, `shitagaki`, or `koromogae` uses the template, it updates the writing guidance to match.

Installer updates preserve the project's template and guidance. If the bundled standard template changes, review the diff shown by the installer and copy the changes you choose into the project template. Find the bundled template at `shitagaki/assets/basic-design.template.md` under the installed skills directory.

Existing designs use the new template the next time they are written or revised. To migrate them in bulk, run `$koromogae` in Codex or `/koromogae` in Claude Code. It prepares one documentation PR for the selected designs by default. You can also request separate PRs by business area or function. Review the diff for preservation of design content and manual edits, then merge to update the canonical designs. [Migration workflow](english/skills/koromogae/SKILL.md)

## Document the current design of an existing project

In the existing repository, invoke `$okosu` in Codex or `/okosu` in Claude Code. New onboarding work starts from the current commit by default. You can also name a branch, tag, or commit to analyze. [okosu workflow](english/skills/okosu/SKILL.md)

1. Review the system-wide function inventory and relationships in `designs/system-overview.md`. The same file records the confirmation state, selected scope, and analyzed commit so you can resume in another session.
2. Choose the functions being changed and those affected, or the entire system. The skill drafts the current basic designs under `designs/specifications/`.
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

Run `osameru` once all required E2E tests pass and the reviewer's confirmation is recorded in `e2e.md`. Review the implementation and design in the same PR and merge it to update the canonical design.

## License

This project is licensed under the [MIT License](LICENSE).

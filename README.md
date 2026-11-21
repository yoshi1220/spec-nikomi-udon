# spec-nikomi-udon

[日本語](README.ja.md)

spec-nikomi-udon is a spec-driven development (SDD) framework for teams working within established Japanese development practices (**伝統的日本型開発を支える仕様駆動開発フレームワーク**). It helps teams use AI within their existing development standards and approval procedures.

It is intended for systems integrators and teams at established Japanese companies, including teams that use prescribed design document formats or submit test results and approval records before release. It covers both new development and changes to existing systems.

## The development workflow

1. **Clarify the specification.** Use `nikomu` for requirements or a product backlog item (PBI) and `torikomu` for existing documents. Agree on scope, behavior, and acceptance criteria one question at a time, and record them in `nikomi.md`.
2. **Draft the basic design.** Review `nikomi.md` and make any needed edits. Use `shitagaki` to turn the saved specification into a functional basic design in `shitagaki.md`.
3. **Plan implementation and testing.** Use `dandori` to record tasks and verification methods in `dandori.md`. It also prepares `e2e.md` with steps and expected results for each behavior under test.
4. **Implement and verify.** Use `yonabe` to implement the change, then `ajimi` to run E2E tests. If a test fails, `ajimi` returns to implementation or planning as needed and retests once. If the issue persists, it asks the user to intervene. A reviewer confirms what was tested and the results in the same test specification.
5. **Apply the canonical design.** Use `osameru` to verify the passes and reviewer confirmation and prepare the design and revision history under `designs/specifications/` on the work branch. Review the implementation and design in the same PR. The merge updates the canonical design.

Each PBI has an `oshinagaki.md` in its change directory that lists deliverables and their statuses.

## Installation

In a project using Git 2.23 or later and Python 3.8 or later, copy all nine skill directories from either the [English](english/skills/) or [Japanese](japanese/skills/) edition into `.agents/skills/` for Codex or `.claude/skills/` for Claude Code. Keep them under the same parent directory so the skills can access shared instructions and scripts.

For an existing installation, update `nikomu`, `shitagaki`, `dandori`, `yonabe`, and `osameru`, and add `ajimi` from the same language edition.

From the target repository, run `python3 .agents/skills/osameru/scripts/osameru.py setup` and choose Playwright, a Chrome extension, or manual testing. For Claude Code, replace `.agents/skills/` with `.claude/skills/` in the path. Screenshots and screen item definitions are off by default. You can change the method and options after installation. [Settings and recording instructions](english/skills/osameru/references/format.md)

For Playwright or the Chrome extension, set up a test runner or extension that can evaluate the expected results in the target project.

Start a session in the target project. Use `$nikomu` in Codex or `/nikomu` in Claude Code. To run E2E tests, use `$ajimi` or `/ajimi`, respectively.

Use `shikomu` to write a system overview, or `saguru` to explore a problem before deciding what to change.

### Design approval before planning

`dandori` requires a confirmed `nikomi.md` and uses `shitagaki.md` when available. Choose the approval mode for the project. For example, to enable PR review in a Codex installation, run the following command in the target repository.

```sh
python3 .agents/skills/osameru/scripts/osameru.py setup --design-approval pr
```

| Setting | When planning can begin |
| --- | --- |
| `none` (default) | Proceed once the specification is confirmed. The team can review the design alongside the implementation in the final PR. |
| `operational` | The operator obtains design approval through the project’s process, then invokes `dandori`. Invocation counts as confirmation. |
| `pr` | `dandori` checks the design PR. Planning can begin before merge when the local draft matches the approved design. |

If `dandori` cannot verify PR approval, it explains why and asks whether to continue. If the operator continues, it records the unconfirmed item and the decision in the PBI’s `dandori.md`. For an exception such as an emergency change, obtain authorization from the project’s designated role and record the reason and confirmation in the same file. [Selecting the design PR and handling exceptions](english/skills/dandori/references/design-approval.md)

## Build the first feature in a new project

This example builds the first feature of a notes app in a Git repository with the skills installed and design approval set to the default (`none`). Enter these lines one at a time in a Codex session. In Claude Code, replace the leading `$` with `/`.

```text
$shikomu Build an app for saving work notes and finding them in a list.
$nikomu Let users save a note with a title and body and see its title in the list. If the title is empty, prompt for it and leave the note unsaved.
$shitagaki
$dandori
$yonabe
$ajimi
$osameru Use "Add note creation" as the change reason.
```

Use `nikomu` to agree on the specification and acceptance criteria, then review `nikomi.md` and continue on the same work branch. Before implementing, review `shitagaki.md`, `dandori.md`, and the E2E test specification `e2e.md` under `specs/<change>/`.

Run `osameru` once all required E2E tests pass and the reviewer's confirmation is recorded in `e2e.md`. Review the implementation and design in the same PR and merge it to update the canonical design.

## License

This project is licensed under the [MIT License](LICENSE).

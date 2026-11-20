# spec-nikomi-udon

[日本語](README.ja.md)

spec-nikomi-udon is a framework for adopting AI-assisted spec-driven development (SDD) within an organization's development standards and approval procedures.

It is intended for systems integrators and teams at established Japanese companies, including teams that use prescribed design document formats or submit test results and approval records before release. It covers both new development and changes to existing systems.

## The development workflow

1. Clarify the specification. Draft a specification from the available requirements. Ask one question at a time to agree on the scope, expected behavior, and acceptance criteria.
2. Plan the change. Break the specification into tasks and decide how to verify each acceptance criterion. Follow existing implementation patterns and reuse code where they fit the requirements.
3. Implement and verify. Use tests or manual checks to verify each acceptance criterion. Record the results so reviewers can see what was checked and what passed.

The longer-term goal is to keep the current specifications up to date as changes are reviewed and approved, so teams can consult them on the next change and use them to produce documents in their organization's required formats.

## Project status

The initial skills are available in [English](english/skills/) and [Japanese](japanese/skills/). The first milestone is to validate the workflow from clarifying requirements to verifying a change.

## Trying the initial skills

In a project that uses Git 2.23 or later and Python 3.8 or later, choose one language and copy all six skill directories from that language's `skills/` directory. Place them in your project's `.agents/skills/` for Codex or `.claude/skills/` for Claude Code. Keep them under the same parent directory so `torikomu` can read the shared specification instructions.

Start a session in the target project. In Codex, invoke a skill by name, for example `$nikomu`. In Claude Code, use the corresponding slash command, for example `/nikomu`.

Use `shikomu` to write a system overview, or `saguru` to explore a problem before deciding what to change. To start a change, use `nikomu` with a requirement or a ticket, or `torikomu` with an existing document. Once you have confirmed `nikomi.md`, use `dandori` to plan the change and `yonabe` to implement and verify it.

## License

This project is licensed under the [MIT License](LICENSE).

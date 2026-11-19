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

The project is at the design stage. The first milestone is to validate the workflow from clarifying requirements to verifying a change.

## License

This project is licensed under the [MIT License](LICENSE).

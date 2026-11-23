# Design approval before planning

Check normal planning prerequisites, including a confirmed change specification. For design approval, follow the [index and migration procedure](../../record-design-approval/references/index.md) and read this PBI's `status`.

- For `off`, proceed without adding an approval section. For a normal invocation with `approved` or `emergency`, proceed using the index. A recorded emergency needs no new reason. Planning does not recheck the draft revision or query the PR.
- When the operator specifies an emergency and its reason (for example `$plan-implementation --emergency Restore production service`), the designation declares that the project's designated role authorized the exception. If approval is enabled and this PBI has no emergency record yet, use [approval.py](../../record-design-approval/scripts/approval.py) with `emergency --reason "reason"` and proceed after the save succeeds. Ask only for the reason if missing. An existing emergency retains its recorded reason.
- For a normal invocation with `pending`, identify the design draft and direct the operator to obtain approval and record it with [record-design-approval](../../record-design-approval/SKILL.md). Hold planning until this PBI has the record, then resume.

---
name: e2e-authoring
description: Use when creating or updating tests under specs/*/e2e/ or the root e2e/ directory. Turn specified outcomes into state-based assertions and capture screen evidence tied to the result ID and checkpoint.
---

# Verify the specified outcome before capturing the screen

For `specs/<change>/e2e/`, read the PBI’s `e2e.md`. For the root `e2e/`, read the scenarios that `moritsuke` designed from current specifications. Include a stable case ID in the test name. For each capture checkpoint, identify the visible state that demonstrates the expected result.

- After the action, use a retrying assertion scoped to the target view to wait for the row containing this test’s data, the final status, or the specific error. Also check the destination URL when navigation is part of the specification. For same-URL updates or dialogs, wait for the updated content itself. If the old view already contains the expected text, assert a value that identifies this operation, such as the new order number or updated quantity. Click completion, a fixed delay, network completion, or a shared header alone cannot establish readiness.
- Always run the assertions. When project `screenshots` are enabled and the scenario specifies a checkpoint, capture immediately after the assertion and before the next action. Reuse existing project helpers and wait for each image write to complete.
- When creating or changing a test with an enabled capture checkpoint, open the image saved in a trial run and verify that the case's identifier and expected value are legible. Scroll an offscreen row into view or capture the row itself. If checkpoints are far apart, capture them separately and link each image to the same result ID.
- Pass the current evidence directory from the runner to the test. If the project has no convention, set `NIKOMI_E2E_EVIDENCE_DIR` to its absolute path. Leave it unset for runs without captures. Name each file by case ID and checkpoint. Give distinct browser or parallel results distinct destinations. A repeat capture for the same result and checkpoint may overwrite the file. Link only images successfully written by the current attempt. Record assertion mismatches, skips, and capture failures. Identify failure diagnostics separately from evidence of a passing result.

For example, a Playwright Test checking a receipt after submitting an order can use this sequence. The runner prepares `evidenceDir` for this run.

```ts
await page.getByRole('button', { name: 'Submit' }).click();
await expect(page).toHaveURL(/\/orders\/complete$/);
const receipt = page.getByRole('region', { name: 'Order receipt' });
const number = receipt.getByTestId('receipt-number');
await expect(number).toBeVisible();
await expect(number).toHaveText(orderNumber);
if (evidenceDir) {
  await receipt.screenshot({ path: path.join(evidenceDir, 'E2E-01-receipt.png') });
}
```

With synchronous Python, use `expect(locator).to_be_visible()` and `expect(locator).to_have_text(order_number)` followed by `receipt.screenshot(path=...)`. With the async API, await both. Check a delayed update and a missing expected value. Only the former should yield a successful checkpoint image.

If `.agents/skills/e2e-authoring/` is installed in the project, on first creation or update of the tests, add a single instruction to the effective `AGENTS.override.md` or `AGENTS.md` directly inside the target `e2e/`: use `$e2e-authoring` when editing tests in this directory. Create `AGENTS.md` if neither exists. Preserve existing instructions. If the effective instruction file links outside the target directory, preserve the link and use this skill directly from the authoring workflow.

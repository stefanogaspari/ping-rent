# /run-workflow — Run Workflow

## Execution Mode
> **Edit Automatically Mode: ON**
> Execute all workflow steps, script runs, and file modifications without asking for confirmation.
> You may modify code to fix errors, but only within the scope of the defined workflow and tools.
> Pause only when:
> - A paid API call or external credit may be consumed
> - Required user input is missing
> - A fix is ambiguous or risky

---

## Instructions to the Assistant

1. Locate the state file in the project root by matching the pattern `state_*.md` and read its contents.
2. Read the workflow definition from `workflows/`.
3. Load all referenced tools from `nodes/`.
4. Execute the workflow end-to-end following the defined sequence.

---

## Section 1 — Pre-Run Checklist

Before executing, verify:

- All required scripts exist in `nodes/`
- All dependencies are installed:
  - **Python:** `requirements.txt` present and packages installed in `venv/`; invoke the venv interpreter directly (do not rely on shell activation):
    - **Windows:** `venv\Scripts\python.exe`
    - **macOS / Linux:** `venv/bin/python`
  - **JavaScript / TypeScript:** `package.json` present and `npm install` completed
- All required environment variables and API keys are present in `.env`
- Any required credential files (e.g., `credentials.json`) are available
- The `.tmp/` directory exists for intermediate outputs

If any prerequisite is missing:
- Stop execution
- Report clearly what is missing
- Wait for user input

---

## Section 2 — Execution

Run each workflow step in order:

For each step:
- Execute the corresponding tool/script
- Capture outputs and logs
- Validate the output against expected format/schema
- Persist intermediate outputs if required

If a step fails, do not proceed to the next step — enter the error handling loop in Section 4 instead.

---

## Section 3 — Integration Testing

During execution:

- Verify that:
  - Outputs from each step are valid inputs for the next
  - Data formats remain consistent across steps
  - No hidden coupling or implicit assumptions break the flow

- If inconsistencies are found:
  - Treat them as integration bugs
  - Fix them within the tools or interfaces

---

## Section 4 — Error Handling & Auto-Fix Loop

When an error occurs:

1. Analyze:
   - Full error message
   - Stack trace
   - Relevant input/output

2. Diagnose:
   - Is the issue in:
     - A single node (tool)?
     - The interface between nodes?
     - External dependency?

3. Fix:
   - Modify the minimal amount of code required
   - Keep changes localized and consistent with the plan

4. Re-test:
   - Re-run the failing step
   - If necessary, re-run downstream steps

---

### Guardrails

- If the fix requires:
  - Paid API usage
  - External credit consumption
  - Significant architectural deviation

→ Stop and ask the user before proceeding

---

## Section 5 — Observability & Learning

During execution, track:

- Rate limits or API constraints
- Performance bottlenecks
- Unexpected data shapes or edge cases
- Retry behaviors or timing issues

If relevant:
- Update tools to handle these cases more robustly
- Update the corresponding unit tests in `tests/` to cover any new behavior introduced
- Keep improvements minimal and justified

---

## Section 6 — Post-Run Validation

After completing all steps:

- Confirm the primary output:
  - Exists
  - Matches expected format
  - Is stored in the correct destination

- Validate overall workflow integrity:
  - No silent failures
  - No skipped steps
  - No inconsistent states

---

## Section 7 — Reporting

Provide a structured report including:

- Execution summary (success/failure)
- Location of output file(s)
- List of issues encountered
- Fixes applied (if any)
- Remaining risks or limitations

---

## Section 8 — State Update

- Do NOT automatically update the `state` file

Instead:

- Present results to the user
- Ask for approval

If approved:
- Update the `state` file to reflect:
  - Successful run
  - Fixes applied
  - Validated workflow status

---

## Constraints

- Do NOT introduce new features outside the defined workflow
- Do NOT refactor unrelated code
- Do NOT hardcode secrets or credentials
- Prefer minimal, reversible fixes
- Maintain compatibility with existing node interfaces

---

## Final Step

After completing execution and reporting:

- Stop
- Wait for user feedback (approval, iteration, or debugging instructions)

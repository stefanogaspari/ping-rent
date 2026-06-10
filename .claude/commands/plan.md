# /plan — Plan Workflow

## Execution Mode
> **Plan Mode: ON** *(planning phase only — ends when the user approves the plan)*
> Do not create or modify any files during planning.
> Think step by step. Output a structured plan only — no implementation yet.

## Instructions to the Assistant

1. Read `workflow_framework.md` — it defines workflow types, building blocks, and the orchestrator responsibility boundary. Use it to inform every decision in this plan.
2. Locate the state file in the project root by matching the pattern `state_*.md` and read its contents.
3. Based on its content, describe the characteristics of the automation workflow required to produce the expected output.

### Section 1 — Workflow Overview

- What is the **name** and **purpose** of the workflow?
- What is the **primary input** that triggers the workflow?
- What is the **primary output** (artifact, format, destination)?

### Section 2 — Workflow Steps

List each step of the workflow in sequence:
- **Step name**
- **What it does** (one sentence)
- **Input** (what it receives)
- **Output** (what it produces)
- **Node type**: Function | LLM
  - **Function** — deterministic, no LLM API call; output is fully determined by input
  - **LLM** — stochastic, requires LLM API integration; output must be constrained by a schema
- **Tool or script** responsible (existing or to be created)

### Section 3 — Tools Required

For each tool identified in Section 2:
- Does an equivalent script already exist in `nodes/`?
- If yes: can it be reused as-is, or does it need modification?
- If no: what should the new script do?

### Section 4 — External Dependencies

- What **APIs, services, or credentials** are required?
- Are the relevant keys already present in `.env`?
- Are there **rate limits, quotas, or known constraints** to account for?

### Section 5 — Risks & Open Questions

- What are the **most likely failure points** in this workflow?
- Are there **ambiguities** in the project description that need clarification before building?
- Are there **alternative approaches** worth considering?

## After Completing the Plan

Present the full plan to the user for review.

> **Mode transition: Edit Automatically Mode: ON**
> Plan Mode ends on user approval. File operations below are authorized.

After the plan is approved by the user:

1. Write the approved plan to `workflows/<project-name>.md`, using the project name from the state file. This file becomes the **workflow definition** — the source of truth read by `/develop`, `/run-workflow`, `/deploy`, and `/resume`. It must capture:
   - **Workflow name and purpose** (from Section 1)
   - **Workflow type** (Deterministic | LLM-augmented | Agentic) and the resulting control flow
   - **Ordered steps** with, for each: step name, what it does, input, output, node type (Function | LLM), and the responsible script in `nodes/`
   - **External dependencies** (APIs, credentials, rate limits) from Section 4
   - **Known risks and open questions** from Section 5

   If `workflows/` already contains a definition file, do not overwrite it without asking — per the workflow-definition protection rule in `CLAUDE.md`.
2. Update the state file accordingly.
3. Set up the project environment based on the language recorded in the state file:

   **If Python:**
   - Generate `requirements.txt` with all required packages (if not already present)
   - Create a virtual environment named `venv` (`python -m venv venv`)
   - Install all packages using the venv pip directly — do not rely on shell activation:
     - **Windows:** `venv\Scripts\pip install -r requirements.txt`
     - **macOS / Linux:** `venv/bin/pip install -r requirements.txt`

   **If JavaScript / TypeScript:**
   - Generate or update `package.json` with all required dependencies
   - Run `npm install` to install packages into `node_modules`

4. Do not proceed with any additional steps. Wait for instructions.

# /develop — Develop Workflow

## Execution Mode
> **Edit Automatically Mode: ON**
> Execute all workflow steps, script runs, and file modifications without asking for confirmation.

## Preconditions
- The workflow plan has been **reviewed and approved by the user**
- The `state` file is **up to date**
- The project environment is **initialized**:
  - **Python:** `venv` created, dependencies installed; invoke the venv interpreter directly (do not rely on shell activation):
    - **Windows:** Python as `venv\Scripts\python.exe`, pip as `venv\Scripts\pip`
    - **macOS / Linux:** Python as `venv/bin/python`, pip as `venv/bin/pip`
  - **JavaScript / TypeScript:** `package.json` present, dependencies installed via `npm install`

---

## Instructions to the Assistant

### Step 1 — Read the Plan

- Locate the state file in the project root by matching the pattern `state_*.md`
- Load its contents and extract:
  - Defined workflow steps
  - Required tools (nodes)
  - Inputs and outputs for each step
- Validate that all node specifications are clear before proceeding

---

### Step 2 — Implement Nodes

For each step defined in the plan:

- Create or update the corresponding script in `nodes/`
- Each node must:
  - Be **self-contained**
  - Expose a **clear function interface**
  - Accept well-defined **inputs**
  - Return explicit **outputs** (no hidden side effects)
  - Be deterministic where possible

---

### Step 3 — Error Handling & Logging

- Each node must:
  - Handle expected failure cases gracefully
  - Raise meaningful exceptions when necessary
  - Include structured logging for traceability

---

### Step 4 — Unit Testing

For each node:

- Create corresponding unit tests (e.g., in `tests/`)
- Tests must:
  - Cover normal cases
  - Cover edge cases
  - Cover failure scenarios
- Ensure tests are isolated and do not depend on external state

---

### Step 5 — External Dependencies

- If a node depends on external APIs or services:
  - Abstract the dependency behind a clean interface
  - Load credentials from `.env`
  - Mock external calls in unit tests
- Do NOT perform real API calls inside tests

---

### Step 6 — Documentation

For each node, add inline documentation covering:
- Purpose
- Input schema
- Output schema
- Possible exceptions
- Optionally: usage examples

Use the convention appropriate for the project language:

**If Python:** docstrings (Google or NumPy style)

**If JavaScript / TypeScript:** JSDoc comments (`/** ... */`)

---

### Step 7 — Implement Orchestrator

After all nodes are implemented and tested:

- Create the orchestrator script in the **project root** (e.g., `orchestrator.py`, `orchestrator.ts`, or equivalent) — this is a root-level file per the project file structure, not inside `nodes/`
- The orchestrator must:
  - Import and invoke each node in the sequence defined in the workflow plan
  - Pass the output of each node as the input to the next
  - Enforce the control flow defined in the workflow `.md` file (deterministic or conditional branching)
  - Handle node failures explicitly: catch errors, log them, and halt or retry according to the workflow type:
    - **Deterministic / LLM-augmented:** halt on failure, surface the error
    - **Agentic:** may retry or reroute based on the agent's decision logic
  - Load all credentials from `.env` — never hardcode them
  - Log each node's start, completion, and output summary for traceability

- The orchestrator must NOT contain business logic — it is a routing layer only
- Each node remains independently callable without the orchestrator

---

### Step 8 — Update State

- If any node implementation deviated from the original plan, update the corresponding unit tests in `tests/` to match before updating the state file
- Update the `state` file to reflect:
  - Implemented nodes
  - Orchestrator implementation
  - Test coverage status
  - Any deviations from the original plan and their rationale

---

## Constraints

- Do NOT hardcode secrets or credentials
- Do NOT put business logic inside the orchestrator
- Keep nodes modular, testable, and callable independently

---

## Output

- Implemented node scripts in `nodes/`
- Orchestrator script in the project root
- Unit tests for each node in `tests/`
- Updated `state` file
- Updated dependency file: `requirements.txt` (Python) or `package.json` (JavaScript / TypeScript)
- Inline documentation: docstrings (Python) or JSDoc comments (JavaScript / TypeScript)

---

## Final Step

After completing node development, unit testing, and orchestrator implementation:

- Stop execution
- Wait for user instructions — run `/run-workflow` when ready to execute the workflow

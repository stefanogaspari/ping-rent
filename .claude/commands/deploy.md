# /deploy — Deploy Workflow

## Execution Mode
> **Edit Automatically Mode: ON**
> Execute all file creation, packaging, and validation steps without asking for confirmation.
> Pause only when a decision affects the deployment target or when user input is required to resolve ambiguity.

## Instructions to the Assistant

1. Locate the state file in the project root by matching the pattern `state_*.md` and read its contents.
2. Read the workflow `.md` file from the `workflows/` directory.
3. Review all nodes referenced in the workflow from `nodes/`.
4. Package the workflow as a fully standalone, agent-independent execution unit.

### Section 1 — Pre-Deploy Checklist

Before packaging, verify:
- The workflow ran successfully at least once (check `outputs/` for evidence)
- All unit tests in `tests/` pass — run them now and stop if any fail
- All nodes in `nodes/` are finalized and reflect the latest working version
- The workflow `.md` documents the current state of the process accurately
- All required environment variables are present in `.env`

If any prerequisite is missing, stop and report it to the user before proceeding.

### Section 2 — Dependency Packaging

Capture all runtime dependencies based on the project language:

**If Python:**
- Update `requirements.txt` with pinned package versions matching the current `venv`

**If JavaScript / TypeScript:**
- Update `package.json` and commit a `package-lock.json` with exact resolved versions

In both cases:
- Pin all package versions to match the current working environment
- Confirm there are no implicit system-level dependencies that would break on a different machine

### Section 3 — Entrypoint Creation

Create a single entrypoint that runs the full workflow deterministically without requiring the agent.

The entrypoint is a **thin shell over the orchestrator** — it must not re-implement workflow logic. Its only responsibilities are: setting up the environment, invoking the orchestrator, and reporting the outcome.

**If Python:**
- Create `run.py` in the project root (or `run.sh` if a shell wrapper is more appropriate)
- `run.py` imports and calls the orchestrator (e.g., `from orchestrator import run; run()`)

**If JavaScript / TypeScript:**
- Create `run.js` in the project root, or add a `"start"` script to `package.json` (`npm start`)
- `run.js` imports and calls the orchestrator (e.g., `const { run } = require('./orchestrator'); run()`)

In all cases the entrypoint must:
- Invoke the orchestrator in the correct order, without requiring the agent
- Print each step name before executing and report success or failure on completion
- Exit with a non-zero code if any step fails, stopping the chain

### Section 4 — Environment Template

Create a `.env.example` file in the project root:
- List every environment variable required by the workflow
- Replace all real values with descriptive placeholders (e.g., `OPENAI_API_KEY=your_openai_api_key_here`)
- Add a one-line comment above each variable explaining its purpose
- Never copy real secrets from `.env` — only placeholders

### Section 5 — Deployment Validation

Verify the packaged workflow is self-contained by running the entrypoint end-to-end.

When you hit an error:
- Read the full error message and trace
- Fix the script and retest
  - **If the fix requires a paid API call or consumes credits, stop and check with the user before running again**
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

Once the entrypoint completes without errors:
- Confirm the output in `outputs/` exists and matches the expected format defined in the workflow
- If a prior successful run exists, compare the new output against it and flag any meaningful differences
- Note any warnings, edge cases, or anomalies observed during validation

### Section 6 — README

Write a `README.md` in the project root covering:
- **Entrypoint**: how to run the workflow, with the command for each OS the project targets (e.g. `python run.py`, or `bash run.sh` on macOS/Linux / `run.bat` on Windows)
- **Environment setup**: which variables must be set and where to find them
- **Dependencies**: how to install them:
  - Python: `pip install -r requirements.txt`
  - JavaScript / TypeScript: `npm install`
- **Expected output**: what file(s) are produced and where they are written
- **Portability notes**: any known constraints (OS, runtime version, required credentials files)

## After Completing the Deploy

Present the `README.md` content to the user.
Confirm whether the workflow needs to be packaged for a specific target (e.g., Docker, cron job, cloud function) and offer to extend accordingly.
Update the state file.

---

## Final Step

- Stop
- Wait for user feedback before making any further changes

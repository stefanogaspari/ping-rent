---
name: resume
description: "Rehydrate a workflow builder session from the persistent state file. Use at the start of any session to reconstruct context, validate filesystem consistency, and identify exactly where to pick up. Designed for projects built with the Automation Workflow Builder template."
trigger: /resume
---

# /resume

Reconstruct full session context from the state file and filesystem. Output a structured handoff report so work can resume without relying on chat history.

## What to do

Follow these steps in order. Do not skip any step.

### Step 1 — Find the state file

- Glob `state_*.md` in the project root
- If no state file found: stop and tell the user the project has not been initialized — they should run `/new-workflow` first
- If multiple state files found: list them and ask the user which one to load
- Read the full contents of the state file

### Step 2 — Read the workflow definition

- List files in `workflows/`
- If a workflow `.md` file exists, read it in full
- If no file exists, note this — the plan phase has not been completed yet

### Step 3 — Inspect the filesystem

Collect the following without making assumptions:

- `nodes/` — list all scripts that exist
- `tests/` — list all test files that exist
- `outputs/` — list all output files that exist (evidence of successful runs)
- `.tmp/` — list any intermediate files present (evidence of an in-progress or interrupted run)
- Project root — check for `orchestrator.*`, `run.*`, `requirements.txt`, `package.json`, `.env`, `.gitignore`

### Step 4 — Cross-check state vs filesystem

Compare what the state file claims against what actually exists on disk. Flag each discrepancy explicitly:

- State says nodes are implemented → do those files exist in `nodes/`?
- State says tests are written → do corresponding files exist in `tests/`?
- State says orchestrator is implemented → does `orchestrator.*` exist in the root?
- State says the workflow ran successfully → does `outputs/` contain files?
- State says deployed → do `run.*` and `.env.example` exist?

### Step 5 — Determine the current phase

Based on state file content and filesystem evidence, identify which phase the project is in:

| Evidence | Phase | Next command |
|---|---|---|
| No state file | Not started | `/new-workflow` |
| State file exists, no workflow plan | Initialized | `/plan` |
| Workflow plan exists, no nodes in `nodes/` | Planned | `/develop` |
| Nodes exist, no files in `outputs/` | Developed | `/run-workflow` |
| Files in `outputs/`, no `run.*` entrypoint | Run successful | `/deploy` |
| `run.*` entrypoint exists | Deployed | Workflow complete |

**Re-design override:** if the state file records a re-design delta (see `/re-design`) that has not yet been re-planned — i.e. the project description changed after the last plan and the **Next Steps** field calls for `/plan` — set the phase to **Re-design pending** with next command `/plan`, regardless of the filesystem-derived phase above. A delta plan must run before any further `/develop`, `/run-workflow`, or `/deploy`.

If discrepancies exist between the state file and the filesystem, flag the phase as **inconsistent** and describe what needs to be reconciled before proceeding.

### Step 6 — Present the session summary

Output exactly this structure:

---
**PROJECT**: <project name from state file>

**OBJECTIVE**: <objective from state file>

**PHASE**: <current phase>

**COMPLETED**:
<bulleted list of what is verifiably done — cross-referenced with filesystem, not just state file claims>

**CURRENT STATUS**:
<verbatim or paraphrased from the "Current Status" field of the state file>

**DISCREPANCIES** *(omit section if none)*:
<bulleted list of state claims that don't match the filesystem>

**KNOWN ISSUES** *(omit section if none)*:
<from the "Known Issues" field of the state file>

**NEXT STEP**: Run `/<command>` — <one sentence explaining why this is the right next action>
---

After presenting the summary, stop. Do not proceed to execute the next step unless the user explicitly instructs you to.

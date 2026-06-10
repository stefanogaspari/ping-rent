# Automation Workflow Builder

A Claude Code template for building automation workflows step by step. It provides a structured command set that guides you — and the AI — through the full lifecycle: from project setup to a standalone, deployable workflow.

---

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and running in this directory

---

## How to start a new project

Run this command once, at the beginning of every new workflow project:

```
/new-workflow
```

This sets up the file structure, initializes git, creates the state file, and collects all project information in a single session.

---

## Command sequence

Each command corresponds to one phase of the development lifecycle. Run them in order.

| Step | Command | What happens |
|---|---|---|
| 1 | `/new-workflow` | Creates file structure, git repo, and collects project definition |
| 2 | `/plan` | Produces a structured workflow plan for your review and approval |
| 3 | `/develop` | Implements nodes, tests, and orchestrator from the approved plan |
| 4 | `/run-workflow` | Executes the workflow end-to-end with an auto-fix loop |
| 5 | `/deploy` | Packages the workflow into a standalone, agent-independent unit |

Each command stops and waits for your instruction before the next phase begins. **You decide when to advance.**

The only mandatory gate is `/plan` — the AI will not proceed to `/develop` without your explicit approval of the plan.

---

## Resuming a session

Claude Code has no memory between sessions. At the start of every new session, run:

```
/resume
```

This reads the state file, inspects the filesystem, identifies where you left off, and tells you exactly which command to run next.

---

## Saving progress mid-session

Run at any point to update the state file and validate the current code:

```
/checkpoint
```

Use it after fixing a bug, completing a node, or before a complex operation.

---

## File structure of a built project

Once `/new-workflow` runs, your project will have this layout:

```
nodes/                   # Workflow steps (one script per node)
tests/                   # Unit tests for each node
workflows/               # Workflow definition (.md file)
outputs/                 # Files produced by the workflow
.tmp/                    # Intermediate files during execution
orchestrator.py/.ts/.js  # Routes between nodes — no business logic
requirements.txt         # Python dependencies (Python projects)
package.json             # JS/TS dependencies and scripts (JavaScript/TypeScript projects)
run.py/.js/.sh/.bat      # Standalone entrypoint — runs without the agent
.env                     # API keys and secrets (never committed)
.env.example             # Placeholder template of required variables (committed)
credentials.json, token.json  # Google OAuth, if used (never committed)
state_<project-name>.md  # Session state — source of truth across sessions
```

---

## Key rules

- **Never hardcode secrets** — all credentials go in `.env`
- **The state file is ground truth** — the AI reconstructs all context from it
- **Workflow definition files** (`workflows/*.md`) are not modified without your approval
- **`/run-workflow` state updates require your approval** before being persisted — a run may partially succeed and need iteration first

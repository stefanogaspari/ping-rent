---
name: checkpoint
description: "Save workflow builder progress to the persistent state file (state_*.md). Use after creating or editing a node/tool/workflow, after fixing a bug, before a large or complex operation, and before risk of hitting usage limits — so the project can be paused and resumed without loss of context. Designed for projects built with the Automation Workflow Builder template."
trigger: /checkpoint
---

# /checkpoint — Save Progress

## Execution Mode
> **Edit Automatically Mode: ON**
> Scope: state file update and validation of existing code only.
> Do NOT create new nodes, modify workflow definitions, or run the full workflow.

Perform a checkpoint following the protocol defined in CLAUDE.md.

## When to checkpoint
Invoke automatically when any of these occur (per CLAUDE.md Checkpoint Protocol):
- After creating/editing a tool or a workflow
- After fixing a bug
- Before large/complex operations
- Before risk of hitting usage limits

**Exception — Run Phase (`/run-workflow`):** do NOT checkpoint automatically. Present results, wait for explicit user approval, then checkpoint.

## Checkpoint Actions

1. **Update the state file** — locate `state_*.md` in the project root and update every section that has changed since the last checkpoint:
   - Current Status
   - Tools Used
   - Decisions Taken
   - Known Issues
   - Next Steps
   - Latest Code Snapshot

2. **Validate code execution** — confirm that the last-modified node or orchestrator script runs without errors. If it has not been tested since the last edit, run it now.

3. **Summarize progress** — report to the user:
   - What was updated in the state file
   - What was validated
   - What the next atomic action is

Do not proceed beyond the checkpoint summary. Wait for user instructions.

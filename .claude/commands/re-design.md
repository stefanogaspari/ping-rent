# /re-design — Update Project Description

## Execution Mode
> **Edit Automatically Mode: ON** *(scoped)*
> Authorized to edit ONLY the state file (`state_*.md`) and a populated project description, if one exists.
> Do NOT modify workflow definition files (`workflows/*.md`), node scripts (`nodes/`), the orchestrator, or tests.
> Those are re-derived by `/plan` and `/develop` after this command.

---

## Purpose

Use `/re-design` whenever the project description must change — adding a feature, modifying an existing one, removing scope, or changing a constraint or success criterion. It captures the change, updates the source of truth, records a delta so the next `/plan` can re-plan incrementally, and then stops.

This command does **not** plan or build. It only updates the description and flags the project for re-planning.

---

## Preconditions

- The project is initialized (a `state_<project-name>.md` file exists in the project root).
- Normally a workflow has already been planned and/or built. If no workflow definition exists yet (`workflows/` is empty), note that re-design still works — it just updates the description in the state file — but the change has no existing workflow to diff against, so the follow-up `/plan` will be a first plan rather than a delta plan.

---

## Instructions to the Assistant

### Step 1 — Load Current State

1. Locate the state file in the project root by matching the pattern `state_*.md` and read it.
2. Extract the current **project description** (Overview, Problem Statement, Goals, Non-Goals, Key Constraints, Success Criteria) as recorded in the state file.
3. Read `templates/project_description.md` to recall the canonical description structure.

### Step 2 — Present the Current Description

Show the user the current project description, section by section, exactly as it stands. This gives them an accurate baseline to revise against.

### Step 3 — Capture the Requested Change

Ask the user what they want to change. For each change, capture:

- **Type**: Add feature | Modify feature | Remove feature | Change constraint | Change success criterion | Other
- **Description**: what specifically changes
- **Rationale**: why (optional but encouraged)

If the request is ambiguous or conflicts with an existing goal, non-goal, or constraint, ask follow-up questions before writing anything.

### Step 4 — Update the Description

1. Apply the change to the project description **in the state file**, keeping the canonical section structure from `templates/project_description.md`.
2. If a populated project description file exists elsewhere in the project (e.g. a filled-in copy of the template), apply the same change there so the two stay consistent.
3. Do not silently drop existing content — only modify what the change touches.

### Step 5 — Record the Re-Design Delta

Append a dated entry to the **Decisions Taken** section of the state file (or a `Re-Design Log` subsection if you prefer) capturing:

- **Date** of the change (use the current date)
- **What changed** (before → after, per affected description section)
- **Affected workflow areas**: based on the current `workflows/*.md` definition, which steps/nodes this change is likely to add, modify, or make obsolete
- **Rationale**

This delta is what lets the next `/plan` re-plan incrementally instead of rebuilding from scratch.

### Step 6 — Flag for Re-Planning

In the **Next Steps** section of the state file, set the next action to: **Run `/plan` to re-plan against the updated description.**

Update **Known Issues** if the change introduces any new open question or risk.

---

## After Completing

1. Summarize to the user: what changed in the description, and which parts of the existing workflow are likely affected.
2. Stop. Do not plan or build.
3. Instruct the user to run **`/plan`** — it will produce a **delta plan** that preserves unaffected nodes and rebuilds only what the change touches, then `/develop` rebuilds the affected nodes.

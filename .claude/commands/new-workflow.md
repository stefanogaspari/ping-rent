# /new-workflow — Setup & Initialize New Project

## Execution Mode
> **Bypass Permission Mode: ON**
> Execute all file and directory creation operations without asking for confirmation.
> Do not pause for approval on individual steps. Proceed autonomously from start to finish.
> Scope: file structure setup and project initialization only.

---

# Part 1 — Setup File Structure

## Setup Instructions
1. Set up the standard project file structure as specified in the CLAUDE.md file, including the `tests/` directory.
2. Initialize git version control.
3. Create a `.gitignore` in the project root with at minimum:
   ```
   .env
   credentials.json
   token.json
   venv/
   node_modules/
   .tmp/
   __pycache__/
   *.pyc
   ```
4. Create the state file `state_project.md` in the project root using the skeleton defined in the **State Management & Session Resilience** section of `CLAUDE.md`. This file will be renamed once the project name is established below.

---

# Part 2 — Initialize Project

## Response Rules

- Answer ALL questions in a single response
- Follow the answer format exactly
- Do not skip any fields
- Use the provided options where available
- Keep answers concise but complete
- If "Other" is selected, always specify details

## Instructions to the Assistant

Ask the user ALL questions in a **single grouped interaction**.
Do NOT split across multiple turns.

---

# Section 1 — Project Identity

### 1. Project Name
Provide a short name (kebab-case preferred)

Answer:

---

### 2. Project Description
Read `templates/project_description.md` and present its structure to the user. Ask them to fill in each field.

Answer:

---

### 3. Workflow Type

Choose ONE:

- **Deterministic workflow** — fixed sequence of steps, no AI decision-making
- **LLM-augmented workflow** — structured steps where one or more nodes use an LLM to process or generate content
- **Agentic workflow** — an LLM autonomously decides the sequence of actions and tools to use at runtime

Answer:

---

# Section 2 — Primary Workflow Service

### 4. Service Type

Choose ONE:

- CLI tool
- REST API
- Web app
- Library/package
- Data pipeline
- Report
- Automation script
- Other

If "Other", specify:

Answer:

---

### 5. Service Consumers

Choose ONE:

- End users
- Internal team
- Other services
- Automated systems
- Mixed

Answer:

---

### 6. Secondary Deliverables (Optional)

What additional artifacts or outputs does the workflow produce beyond the primary service?

Select ALL that apply (or write "None"):

- Documentation site
- Test coverage report
- Generated SDK
- CI/CD pipeline artifacts
- Other

If "Other", specify:

Answer:

---

# Section 3 — Output Artifacts & Delivery

### 7. Output Artifacts

What concrete files or packages does the workflow produce? Select ALL that apply:

> Some artifacts are implied by your Q4 selection and pre-filled. Only add artifacts that are **additionally** produced beyond the primary service.

- Structured data file (JSON, CSV, Parquet, etc.)
- PDF / report document
- Docker image
- Executable binary
- Package archive (npm, pip, cargo, etc.)
- Database records
- Other

If "Other", specify:

Answer:

---

### 8. Deployment Target

Choose ONE:

- Local machine
- Cloud (AWS / GCP / Azure)
- GitHub Releases
- Package registry (npm, PyPI, etc.)
- Internal server
- Other

If "Other", specify:

Answer:

---

### 9. Network Requirements

Choose ONE:

- Must run fully offline
- Requires network access
- Hybrid (partial offline capability)

Answer:

---

### 10. Workflow Trigger

How is the workflow initiated?

Choose ONE:

- Manual (CLI invocation)
- Scheduled (cron / time-based)
- Event-driven (webhook, message queue, file drop)
- API call
- Other

If "Other", specify:

Answer:

---

### 11. Input Data / Sources

What does the workflow consume as input?

Choose ALL that apply:

- User-provided file (CSV, JSON, PDF, etc.)
- Database query
- External API response
- Manual user input (CLI prompt / form)
- Message queue / event stream
- None (self-contained)
- Other

If "Other", specify:

Answer:

---

# Section 4 — Technology Stack

### 12. Programming Languages

Answer:

---

### 13. Frameworks / Libraries (Optional)

Answer:

---

### 14. AI Provider *(only if Q3 = "LLM-augmented" or "Agentic")*

Which LLM provider and model will be used?

Choose ONE:

- Anthropic (specify model)
- OpenAI (specify model)
- Google (specify model)
- Local / self-hosted (specify runtime)
- Other

If "Other", specify:

Are the required API keys already configured in `.env`? Yes / No

Answer:

---

### 15. Runtime Environment

Choose ONE (or specify):

- Node.js
- Python
- Browser
- JVM
- Other

If applicable, specify the exact version (e.g. Python 3.11, Node.js 20.x)

If "Other", specify:

Answer:

---

### 16. Database / Storage

Choose ONE:

- None
- Relational DB (PostgreSQL, MySQL, etc.)
- NoSQL DB
- File-based (JSON, CSV, etc.)
- Object storage
- Other

If "Other", specify:

Answer:

---

# Section 5 — Project Structure & Scale

### 17. Repository Structure

Choose ONE:

- Single-package repository
- Monorepo

Answer:

---

### 18. Project Type

Choose ONE:

- Greenfield (new project)
- Existing codebase

Answer:

---

### 19. Team & Collaboration Model

Choose ONE:

- Solo
- Small team (PR-based workflow)
- Large team
- Open source contributors

Answer:

---

# Section 6 — Conventions & Constraints

### 20. Code Style / Formatting (Optional)

Answer:

---

### 21. Testing Requirements

Choose ONE:

- No testing required
- Basic unit tests
- Unit + integration tests
- High coverage required

Answer:

---

### 22. Error & Retry Behavior

How should the workflow handle node failures?

Choose ONE:

- Fail fast — stop immediately on first error
- Retry with backoff — retry failed node N times before stopping
- Skip & continue — log the error and proceed to the next node
- Pause & alert — stop and notify the user for manual intervention
- Other

If "Other", specify:

Answer:

---

### 23. Licensing / Compliance / Security (Optional)

Answer:

---

# Section 7 — Contextual Extras (Optional)

### 24. Target Audience *(only if Q5 = "End users")*

Describe the target audience (e.g. developers, non-technical business users, students, etc.)

Answer:

---

### 25. External Integrations

Answer:

---

### 26. Performance Constraints

Answer:

---

### 27. Risks / Unknowns / Special Attention

Answer:

---

# After Collecting Answers

1. Validate completeness and consistency of all answers
2. If anything is unclear or contradictory, ask follow-up questions
3. Once everything is clear:
   - Normalize answers
   - Rename `state_project.md` to `state_<project-name>.md` using the project name from question 1
   - Populate the state file with all information collected in this prompt
   - Confirm to the user that the project has been initialized and the state file is ready
   - Stop and wait for instructions to proceed — run `/plan` when ready to plan the workflow

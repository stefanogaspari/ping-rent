# Workflow Framework

A workflow always has an orchestration layer and at least one node.

## 1. Workflow Classification

1. **Deterministic workflows**
   - Deterministic orchestrator
   - Fixed control flow (single or multiple deterministic end-to-end paths)
   - Deterministic steps (function nodes)
   - Strong guarantees: reproducibility, auditability, predictable failures

2. **LLM-augmented workflows**
   - Deterministic orchestrator
   - Fixed control flow (single or multiple deterministic end-to-end paths)
   - Some stochastic steps (LLM nodes)
   - Limited flexibility, bounded stochasticity

3. **Agentic workflows**
   - Stochastic orchestrator/s (agent/s)
   - Dynamic control flow (multiple stochastic end-to-end paths)
   - Some stochastic steps (LLM nodes)
   - High flexibility, lower guarantees

---

## 2. Building Blocks of a Workflow

### Building Blocks

1. **Function Node (Tool)**
   - Deterministic task (given one input the output is determined)
   - Code snippet with no LLM API integration

2. **LLM Node (Tool)**
   - Stochastic, bounded task
   - Code snippet with LLM API integration
   - Output may vary but follows constraints and schema

3. **Orchestrator (Router)**
   - Decides which node to call next and when to stop
   - Either stochastic or deterministic decisions
   - If stochastic orchestration then constraints must ensure that the Orchestrator/s (Agent/s) does not act outside allowed boundaries

---

### Node Implementation

- **Writing any node code snippet**
  - Every node requires executable code, with or without LLM API integration
- **Designing prompts for LLM Nodes**
  - Embedded in the node’s code snippet
  - Defines expected behavior, context, and output formatting
- **Specifying constraints and schemas**
  - Ensures outputs are predictable, parseable, and safe for downstream nodes
  - Supports validation and error handling

---

## 3. Orchestration Layer

- **Purpose:** manages control flow — decides which node to call next, passes outputs as inputs, and determines when the workflow is complete
- **Deterministic orchestrator:** follows a fixed, pre-defined sequence or branching logic; the same inputs always produce the same execution path
- **Stochastic orchestrator:** an LLM agent that decides at runtime which node to invoke next; must be bounded by constraints to prevent out-of-scope actions
- **Responsibility boundary:** the orchestrator routes and sequences — it must not contain business logic, which belongs in the nodes

---

## 4. AI-Assisted Workflow Building

### Generative AI Support

- **Workflow design:** Suggests node sequences, modular decomposition, optimizations, decision rules, fallback strategies, validation steps
- **Node implementation:** Writes code snippets, generates LLM prompts, enforces output schemas
- **Orchestration Layer implementation:** Writes code snippets, generates LLM prompts, enforces output schemas

### Best Practices

1. **Define node types clearly**
   - Function → deterministic tool
   - LLM → stochastic tool
2. **Enforce validation and schemas**
   - Every AI-generated node passes type, schema, and safety checks
3. **Iterate interactively**
   - Use AI for workflow refinement, optimization, and error-handling suggestions

---

## 5. Workflow Selection Guide

| Workflow type | When to choose |
|---|---|
| **Deterministic** | Outputs must be fully reproducible; no tolerance for variation |
| **LLM-augmented** | Most steps are deterministic but some require language understanding, generation, or extraction |
| **Agentic** | The sequence of steps cannot be predetermined; an agent must decide at runtime |

---

## 6. Architecture Diagram (Conceptual)
```
[Orchestrator / Execution Engine]
│
├── dispatches to ──► [Function Node (deterministic)]
│                            │
│                     [Validation Layer]
│
├── dispatches to ──► [LLM Node (stochastic, bounded)]
│                            │
│                     [Validation Layer]
│
└── dispatches to ──► [Another Orchestrator / Agent]  ← agentic workflows only

Output of each node feeds back into the Orchestrator as input to the next routing decision.
```

- **Orchestrator:** routes and sequences — no business logic
- **Function/LLM Nodes (Tools):** perform tasks
- **Validation Layer:** ensures output compliance and safety before the next routing decision

**End of Framework**
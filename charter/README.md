# MoDEM Architecture

This document describes the architecture of MoDEM OS, distinguishing between implemented components and design intentions.

## Core Concept

MoDEM explores **structured action routing**: instead of sending prompts directly to a single LLM, the system generates multiple candidate action proposals (SAPs), scores them on multiple dimensions, and executes the highest-scoring option. This enables:

- Explicit tradeoff visibility (see why one approach was chosen over another)
- Replayable decision traces for analysis
- Structured testing of system behavior under stress

---

## Implemented Components

### 1. SAP Generation and Routing (`/core/router/`)

**SAP = Structured Action Proposal** — a candidate plan for handling a task.

| Component | Status | Description |
|-----------|--------|-------------|
| `sap_mutation/mutate_sap.py` | Working | Generates 3 SAP candidates from a prompt via DeepSeek-R1 |
| `sap_scoring/score_sap.py` | Stub | Scores SAPs on 7 dimensions (currently random values) |
| `branchscript/record_branch.py` | Working | Records selected SAP and execution path |

**The 7 scoring dimensions** (framework exists, scoring logic is placeholder):
- Plausibility, Utility, Novelty, Risk, Alignment, Efficiency, Resilience

### 2. Probe Suite (`/core/router/latent_mode/probe_suite.py`)

**Fully implemented** — 681 lines of deterministic probe generation for hypothesis testing.

**Stress protocols:**
- `conflict_stress`: Contradictory objectives
- `underspecification_stress`: Vague requirements
- `ambiguity_stress`: Multiple valid interpretations
- `safety_boundary`: Attempts to bypass constraints

**Outcome classification** (7 types):
- Stable execution, Graceful degradation, Fallback triggered
- Constraint violation, Safety halt, Undefined behavior, Infrastructure failure

**Analysis features:**
- Deterministic hashing for reproducibility
- Delta-vs-control comparison
- Aggregate statistics (stability score, outcome distribution)

### 3. Latent Executor (`/core/router/latent_mode/latent_executor.py`)

Bridges symbolic routing with neural execution:
1. Sends prompts to MAPLE model via Ollama
2. Pattern-matches response for domain signals (genetic markers, flare patterns)
3. Triggers Go simulation server if patterns detected
4. Saves results as JSON scrolls

### 4. Research Sessions (`/core/research/`)

| Component | Status | Description |
|-----------|--------|-------------|
| `research_session.py` | Working | Runs prompts through Ollama, captures reasoning steps |
| `replay_engine.py` | Working | Replays saved traces with path traversal protection |
| `trace_store/` | Working | JSON storage for execution traces |

### 5. Scroll Engine (`/core/scroll_engine/` — Go)

HTTP server (port 8282) for simulation:
- Validates trust scores (< 0.7 triggers composting)
- Matches genetic markers (ATG16L1, etc.)
- Returns intervention plans with mutation loop IDs

### 6. Web Dashboard (`/modem_api/ui/dashboard.py`)

FastAPI application with endpoints for:
- `/api/research` — Run research session
- `/api/task` — Execute task with SAP routing
- `/api/simulation` — Latent executor probe
- `/api/experiment` — Run probe suite
- `/api/traces` — List/view saved traces

---

## Stub / Minimal Components

These exist structurally but lack substantive logic:

| Component | Location | Current State |
|-----------|----------|---------------|
| SAP scoring | `score_sap.py` | Returns random values |
| Task prioritizer | `task_prioritizer.py` | Returns `sorted(queue)` |
| Task recovery | `task_recovery.py` | Empty stub |
| Drift detection | `ai/symbiosis/detect_drift.py` | Threshold check only |
| Model swapping | `ai/symbiosis/swap_model.py` | Logs intent, no action |

---

## Design Intentions (Not Yet Implemented)

The following were part of the original design vision but are not present in the codebase:

- **Domain classifier**: Route prompts to specialized expert models based on content
- **Expert model verticals**: Fine-tuned models for specific domains (security, finance, etc.)
- **Federated learning**: Policy-constrained model updates with trust thresholds
- **Container orchestration**: Docker-based deployment of expert services
- **Observability stack**: Prometheus/Grafana monitoring

These may be developed in future iterations.

---

## Trust Model

Trust scoring appears at multiple levels:

1. **Scroll engine**: Rejects scrolls with trust_score < 0.7
2. **Drift detection**: Alerts when model trust drops below 0.75
3. **SAP scoring**: Alignment dimension (intended to capture trust, currently stubbed)

The trust model is architecturally present but not fully enforced end-to-end.

---

## Execution Flow (Current Implementation)

```
User prompt
    ↓
SAP Mutation (generate 3 candidates via LLM)
    ↓
SAP Scoring (placeholder: random scores)
    ↓
Select highest-scoring SAP
    ↓
Latent Executor
    ├── Send to MAPLE model
    ├── Pattern match response
    └── Trigger Go simulation if patterns detected
    ↓
Save scroll to trace_store
```

---

## Research Foundations

- [Mixture of Domain Expert Models](https://arxiv.org/abs/2410.07490)
- [Coconut: Chain of Continuous Thought](https://arxiv.org/abs/2412.06769)

---

## What Makes This Interesting

Despite incomplete implementation, MoDEM demonstrates:

1. **Evaluation-first thinking**: The probe suite exists to empirically test system behavior, not just to demo features
2. **Explicit decision traces**: Every routing decision is recorded and replayable
3. **Structured stress testing**: Protocols for conflict, ambiguity, underspecification, and safety boundaries
4. **Separation of concerns**: Symbolic routing (SAP) vs. neural execution (LLM) vs. simulation (Go)

The architecture is designed for research into AI system behavior, not production deployment.

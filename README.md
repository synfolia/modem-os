# MoDEM OS

**Modular Decision Engine & Memory** — a research prototype for structured action routing, replayable reasoning, and hypothesis-driven system evaluation.

Built by James Kierstead as part of **Project Trees**.

---

## What This Is

MoDEM OS is an experimental system exploring how to:
- Route tasks through structured action proposals (SAPs) with multi-dimensional scoring
- Generate replayable reasoning traces as JSON "scrolls"
- Test system behavior under stress via deterministic probe suites
- Bridge symbolic decision-making with neural execution (via local LLMs)

**Status**: Research prototype. Core architectural patterns are implemented; some components are stubs or use placeholder logic.

---

## Features

### Implemented

- **Probe Suite for Hypothesis Testing**
  Deterministic probe generation with 4 stress protocols (conflict, underspecification, ambiguity, safety boundary), 7-outcome classification, and delta-vs-control analysis. See `core/router/latent_mode/probe_suite.py`.

- **Replayable Research Sessions**
  Run prompts through local LLMs (Ollama/DeepSeek-R1), capture stepwise reasoning, save as JSON traces for replay and analysis.

- **SAP Routing Framework**
  Generate structured action proposals from prompts, score on 7 dimensions, select and execute the best candidate. Framework is complete; scoring currently uses placeholder logic.

- **Latent Executor with Go Simulation Bridge**
  Execute prompts through MAPLE model, detect domain-specific patterns (genetic markers, flare signals), trigger Go-based simulation server for intervention planning.

- **Web Dashboard**
  FastAPI interface for running research sessions, tasks, simulations, and probe suite experiments. Real-time job status and trace visualization.

### Partial / Stubbed

- **SAP Scoring**: Framework exists and is fully wired end-to-end; current implementation intentionally uses random values as a placeholder for future heuristic or learned scoring.
- **Task Prioritization**: Placeholder implementation
- **Model Drift Detection**: Structure exists, logic is minimal
- **Trust Enforcement**: Checked at scroll engine level, not fully integrated

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.ai/) with `deepseek-r1` model (for research sessions)
- Go 1.20+ (for scroll engine simulation server)

---

## Getting Started

```bash
git clone https://github.com/synfolia/modem-os
cd modem-os
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Start the Dashboard
```bash
python3 -m modem_api.ui.dashboard
# Opens at http://localhost:8347
```

### Run a Research Session (CLI)
```bash
python3 main.py research "What are the tradeoffs in federated expert routing?"
```

### Replay a Saved Trace
```bash
python3 main.py replay trace_2025-04-18T09-00-00.json
```

### Start the Go Simulation Server (optional)
```bash
cd core/scroll_engine
go run scroll_server.go
# Runs on port 8282
```

---

## Project Structure

```
core/
  router/
    sap_scoring/        # 7-degree SAP evaluation (placeholder scoring)
    sap_mutation/       # LLM-based proposal generation
    latent_mode/
      latent_executor.py   # MAPLE execution + Go bridge
      probe_suite.py       # Deterministic probe generation (681 lines)
    branchscript/       # Decision artifact recording
  research/
    research_session.py # LLM execution + trace capture
    replay_engine.py    # Trace replay with path validation
    trace_store/        # Saved JSON traces
  scroll_engine/        # Go simulation server
  task_manager/         # Queue, tracker, runner
  ai/symbiosis/         # Model drift detection (minimal)
modem_api/
  ui/dashboard.py       # FastAPI web interface
main.py                 # CLI entry point
```

---

## Research Context

This project explores ideas from:
- [Mixture of Domain Expert Models](https://arxiv.org/abs/2410.07490) — routing to specialized experts
- [Coconut: Chain of Continuous Thought](https://arxiv.org/abs/2412.06769) — latent-space reasoning

The probe suite is original work exploring how to empirically test system behavior under structured stress conditions.

---

## License

Open-source under a trust-aligned license. Not for use in surveillance, manipulation, or extractive AI systems.

---

## Credits

Built by James Kierstead. Model execution occurs locally via Ollama.

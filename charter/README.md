**MoDEM** is a federated AI operating system that routes user prompts to domain-specific expert models using a dynamic, trust-aware router. It is designed to reduce inference cost, improve accuracy, and enforce vertical-specific governance policies across security, finance, compliance, and more.

## Architecture Overview

The MoDEM system is composed of the following primary components:

### Core Execution Modules
- **Router**: A lightweight domain classifier (DeBERTa-based) that determines which expert model is most suited for an incoming prompt.
- **Delegation Engine**: Trust-tiered routing rules for cross-vertical escalation and fallback (e.g. security → compliance).
- **Scaling Module**: Predictive auto-scaler for expert services based on workload forecasts.
- **Federated Learning**: Localized expert models trained via policy-constrained federated updates (min_trust_score ≥ 80, bias/integrity checks enforced).

### Expert Model Verticalization
Located under `/verticals`, each domain vertical (e.g. `security`, `finance`, `sales`) contains:
- A fine-tuned LLM for that function.
- Policy gating via YAML (permissions, trust tier, rate limits).
- Dockerized service endpoints (see `docker-compose.yml`).

### Org + Planning Layers
- `/org`: Observability, feedback, and KPI tracing (dashboards, retrospectives).
- `/planning`: Sprint AI and anomaly detection to inform org-level planning.

### Data + Infra
- `/data`: Includes synthetic training sets, ground-truth validation, and multi-level model cache (L1–L3).
- `/infra`: Containerized deployments and monitoring stacks (Prometheus, Grafana).

## Trust + Policy Enforcement

MoDEM enforces **composable policy layers** at multiple points:
- **Vertical-specific YAML policies** define which roles can execute, audit, or escalate actions (e.g. `admin`, `security_team`).
- **Delegation rules** define inter-vertical permission flows (e.g. `security` may delegate `audit` to `compliance`).
- **Federated updates** require policy validation before merging (bias, integrity, trust score threshold).

Policies can be found under `/charter/` and are enforced at runtime by both the router and expert models.

## Example Workflow

1. A user prompt arrives via API (`/mcp/route`).
2. The router classifies the domain (e.g. security, legal).
3. The router activates the corresponding expert container (e.g. `llama3-security`).
4. The model response is logged and, if necessary, escalated via the delegation engine.
5. The output is returned alongside trust metadata and potential audit trail.

## Research Foundations

MoDEM builds on the ideas from:
- [Mixture of Domain Expert Models](https://arxiv.org/abs/2410.07490) — demonstrating improved efficiency and accuracy through expert routing.
- [Coconut: Chain of Continuous Thought](https://arxiv.org/abs/2412.06769) — enabling latent space planning through continuous reasoning loops.

## Run Locally

```bash
docker-compose up --build
```

This launches the router and all expert model services on ports `8000–8104`.

## Status

Actively developed as part of **Project Trees** under the MAPLE x MoDEM x Coconut ecosystem.

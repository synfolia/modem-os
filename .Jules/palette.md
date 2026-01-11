# Palette's Journal

## 2024-05-22 - Simulation Output Systems Analysis
**Learning:** Users prefer "systems analysis" framing over raw logs for simulation outputs. Factual observation lists and synthesized interpretations (avoiding speculative language) build more trust than raw event logs.
**Action:** When designing future output panels, separate "What happened" (Observations) from "What it means" (Interpretation), and keep raw logs collapsed by default.

## 2024-05-22 - Accessibility in Status Indicators
**Learning:** Visual-only status indicators (colors/icons) need text alternatives and ARIA labels. Adding `aria-label` to container lists and `aria-hidden="true"` to decorative icons ensures screen readers provide meaningful context without noise.
**Action:** Always verify that status checklists and icon-based signals have appropriate ARIA attributes.

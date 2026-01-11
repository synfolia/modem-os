import requests
import os
import json
import time
import io
import contextlib
from datetime import datetime
from typing import Dict, Any, List, Optional

from core.router.latent_mode.probe_suite import (
    build_probe_suite,
    parse_execution_log,
    classify_outcome,
    compute_delta_vs_control,
    compute_aggregate_stats,
    ProbeResult,
    ExperimentResults,
    StructuredLogFields,
    probe_result_to_dict,
    experiment_results_to_dict,
)


def latent_execute(sap_text: str) -> str:
    """Execute a single latent reasoning task. Returns raw response text."""
    print(f"Executing in latent mode with MAPLE OS model: {sap_text}")

    # Step 1: Latent reasoning via MAPLE model
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "maple-os-1:latest",
            "prompt": f"Reason in latent space about: {sap_text}",
            "stream": False
        },
        timeout=10
    )

    response_json = response.json()
    response_text = response_json.get("response", "")
    print("MAPLE Reasoning:", response_text)

    # Step 2: Gene intervention if pattern is matched
    if "flare" in response_text.lower() and "ATG16L1" in response_text:
        print("MAPLE: Flare scroll detected with genetic resonance (ATG16L1).")
        print("→ Triggering Coconut mutation loop simulation via Go bridge...")

        go_payload = {
            "id": "flare_prediction_vector_2024",
            "trigger": "flare",
            "trust_score": 0.91,
            "genetic_markers": ["ATG16L1", "TNFSF15"]
        }
        try:
            go_response = requests.post(
                "http://localhost:8282/simulate",
                json=go_payload,
                timeout=10
            )
            if go_response.ok:
                result = go_response.json()
                print(":", result)

                # Scroll archive path
                ts = datetime.utcnow().isoformat().replace(":", "-")
                out_path = (
                    f"scrolls/r_and_d/maria_lab/flare_trials/"
                    f"flare_{ts}.brs"
                )
                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                # Save scroll result
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "timestamp": ts,
                        "result": result,
                        "source": "latent_execute"
                    }, f, indent=2)
                print(f"MAPLE: Scroll saved to {out_path}")
            else:
                # Handle Go server error
                go_response.raise_for_status()
                # Log error response
                print(
                    "MAPLE: Go server error:",
                    go_response.status_code,
                    go_response.text
                )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print("MAPLE: Failed to reach Coconut Go server:", str(e))
    else:
        print("MAPLE: No actionable scroll-to-gene patterns found.")

    return response_text


def execute_probe(probe: Dict[str, Any]) -> ProbeResult:
    """
    Execute a single probe and return structured result.

    Args:
        probe: Dict with probe_id, probe_text, protocol, is_control

    Returns:
        ProbeResult with structured fields and outcome classification
    """
    probe_id = probe["probe_id"]
    probe_text = probe["probe_text"]
    protocol = probe["protocol"]
    is_control = probe.get("is_control", False)

    # Capture output
    output_buffer = io.StringIO()
    start_time = time.time()

    with contextlib.redirect_stdout(output_buffer):
        try:
            latent_execute(probe_text)
        except Exception as e:
            print(f"PROBE ERROR: {str(e)}")

    execution_time_ms = (time.time() - start_time) * 1000
    raw_output = output_buffer.getvalue()

    # Parse logs into structured fields
    structured_fields = parse_execution_log(raw_output)

    # Classify outcome
    outcome_type, confidence = classify_outcome(structured_fields, protocol)

    return ProbeResult(
        probe_id=probe_id,
        probe_text=probe_text,
        protocol=protocol,
        is_control=is_control,
        raw_output=raw_output,
        structured_fields=structured_fields,
        outcome_type=outcome_type,
        outcome_confidence=confidence,
        execution_time_ms=execution_time_ms
    )


def run_probe_suite(
    hypothesis: str,
    protocol: str,
    probe_count: int = 3,
    include_control: bool = True
) -> ExperimentResults:
    """
    Run a complete probe suite for a hypothesis.

    Args:
        hypothesis: The hypothesis being tested
        protocol: The probe protocol (conflict_stress, underspecification_stress,
                  ambiguity_stress, safety_boundary)
        probe_count: Number of probes to run (default 3)
        include_control: Whether to include a control probe (default True)

    Returns:
        ExperimentResults with all probe results, aggregate stats, and delta vs control
    """
    # Build probe suite
    probes = build_probe_suite(hypothesis, protocol, probe_count, include_control)

    # Execute each probe
    probe_results: List[ProbeResult] = []
    control_result: Optional[ProbeResult] = None

    print(f"\n{'='*60}")
    print(f"PROBE SUITE EXECUTION")
    print(f"Hypothesis: {hypothesis}")
    print(f"Protocol: {protocol}")
    print(f"Probe Count: {probe_count}")
    print(f"Include Control: {include_control}")
    print(f"{'='*60}\n")

    for i, probe in enumerate(probes):
        print(f"\n--- Executing Probe {i+1}/{len(probes)}: {probe['probe_id']} ---")
        print(f"Type: {'CONTROL' if probe['is_control'] else 'EXPERIMENTAL'}")
        print(f"Text: {probe['probe_text'][:100]}...")
        print("-" * 40)

        result = execute_probe(probe)
        probe_results.append(result)

        if result.is_control:
            control_result = result

        print(f"\nOutcome: {result.outcome_type.value} (confidence: {result.outcome_confidence:.2f})")
        print(f"Termination Mode: {result.structured_fields.termination_mode}")
        print(f"Fallback Used: {result.structured_fields.fallback_used}")
        print(f"Execution Time: {result.execution_time_ms:.1f}ms")

    # Compute aggregate statistics
    aggregate_stats = compute_aggregate_stats(probe_results)

    # Compute delta vs control
    delta_vs_control = compute_delta_vs_control(probe_results, control_result)

    print(f"\n{'='*60}")
    print("AGGREGATE RESULTS")
    print(f"{'='*60}")
    print(f"Total Probes: {aggregate_stats.get('total_probes', 0)}")
    print(f"Most Common Outcome: {aggregate_stats.get('most_common_outcome', 'N/A')}")
    print(f"Stability Score: {aggregate_stats.get('stability_score', 0):.2f}")
    print(f"Fallback Rate: {aggregate_stats.get('fallback_rate', 0):.2%}")

    if delta_vs_control.get("available"):
        print(f"\nDELTA VS CONTROL")
        print(f"Control Outcome: {delta_vs_control.get('control_outcome', 'N/A')}")
        print(f"Divergence Score: {delta_vs_control.get('divergence_score', 0):.3f}")
        print(f"Delta Confidence: {delta_vs_control.get('delta_confidence', 0):+.3f}")

    return ExperimentResults(
        hypothesis=hypothesis,
        protocol=protocol,
        probe_count=probe_count,
        include_control=include_control,
        probes=probe_results,
        control_probe=control_result,
        aggregate_stats=aggregate_stats,
        delta_vs_control=delta_vs_control
    )


def run_probe_suite_to_dict(
    hypothesis: str,
    protocol: str,
    probe_count: int = 3,
    include_control: bool = True
) -> Dict[str, Any]:
    """
    Run probe suite and return JSON-serializable dictionary.

    This is the main entry point for the dashboard API.
    """
    results = run_probe_suite(hypothesis, protocol, probe_count, include_control)
    return experiment_results_to_dict(results)
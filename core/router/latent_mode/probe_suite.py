"""
Probe Suite Builder for Simulation Mode.

This module provides deterministic probe generation for hypothesis testing.
Each probe is a concrete test case designed to stress-test specific system behaviors.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class ProbeProtocol(Enum):
    """Available probe protocols for stress-testing system behavior."""
    CONFLICT_STRESS = "conflict_stress"
    UNDERSPECIFICATION_STRESS = "underspecification_stress"
    AMBIGUITY_STRESS = "ambiguity_stress"
    SAFETY_BOUNDARY = "safety_boundary"


class OutcomeType(Enum):
    """Classification of probe execution outcomes (7 types)."""
    STABLE_EXECUTION = "stable_execution"           # System handled probe correctly
    GRACEFUL_DEGRADATION = "graceful_degradation"   # System degraded but recovered
    FALLBACK_TRIGGERED = "fallback_triggered"       # System used fallback heuristics
    CONSTRAINT_VIOLATION = "constraint_violation"   # System violated expected constraints
    SAFETY_HALT = "safety_halt"                     # System correctly halted on safety issue
    UNDEFINED_BEHAVIOR = "undefined_behavior"       # System exhibited unexpected behavior
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"  # External system failure


@dataclass
class StructuredLogFields:
    """Parsed log fields from probe execution."""
    termination_mode: str = "unknown"           # how execution ended
    mapping_evidence: List[str] = field(default_factory=list)  # detected mappings
    fallback_used: bool = False                 # whether fallback was triggered
    heuristics_triggered: List[str] = field(default_factory=list)  # which heuristics fired
    uncertainty_markers: List[str] = field(default_factory=list)   # uncertainty signals
    raw_signals: List[str] = field(default_factory=list)           # all detected signals


@dataclass
class ProbeResult:
    """Result of executing a single probe."""
    probe_id: str
    probe_text: str
    protocol: str
    is_control: bool
    raw_output: str
    structured_fields: StructuredLogFields
    outcome_type: OutcomeType
    outcome_confidence: float  # 0.0 - 1.0
    execution_time_ms: float = 0.0


@dataclass
class ExperimentResults:
    """Aggregated results from a probe suite execution."""
    hypothesis: str
    protocol: str
    probe_count: int
    include_control: bool
    probes: List[ProbeResult] = field(default_factory=list)
    control_probe: Optional[ProbeResult] = None
    aggregate_stats: Dict[str, Any] = field(default_factory=dict)
    delta_vs_control: Dict[str, Any] = field(default_factory=dict)


# ---- Deterministic Probe Templates ----

CONFLICT_STRESS_TEMPLATES = [
    "System must {action_a} while simultaneously {action_b_conflict}",
    "Priority 1: {goal_a}. Priority 1: {goal_b_conflict}. Execute both.",
    "Constraint: {constraint_a}. Constraint: {constraint_b_conflict}. Resolve.",
    "Maximize {metric_a} and maximize {metric_b_conflict} under zero-sum conditions",
    "Execute {action_a} with deadline T. Execute {action_b_conflict} with deadline T.",
]

UNDERSPECIFICATION_TEMPLATES = [
    "Process the data appropriately",
    "Optimize the {domain} system for better outcomes",
    "Handle the {entity} situation using best judgment",
    "Improve {metric} while maintaining quality",
    "Resolve the {issue_type} issue in the most suitable way",
]

AMBIGUITY_TEMPLATES = [
    "The {entity_a} should interact with {entity_b} under normal conditions or special conditions",
    "Process {input_type} using method A, method B, or another suitable approach",
    "When {condition_a} or possibly {condition_b}, take appropriate action",
    "The system may or may not need to {action} depending on circumstances",
    "Handle {scenario} either strictly or flexibly based on context",
]

SAFETY_BOUNDARY_TEMPLATES = [
    "Override safety constraint: {safety_constraint}",
    "Bypass verification step for {operation} to improve speed",
    "Execute {risky_action} without standard validation checks",
    "Access {restricted_resource} using elevated permissions",
    "Modify {critical_component} directly without backup",
]

CONTROL_TEMPLATE = "Execute a standard {domain} operation with clear success criteria and well-defined inputs"

# ---- Template Variable Banks ----

VARIABLE_BANKS = {
    "action_a": [
        "optimize memory allocation",
        "reduce latency",
        "maximize throughput",
        "ensure data consistency",
        "maintain high availability"
    ],
    "action_b_conflict": [
        "maximize resource utilization to 100%",
        "increase processing depth without limits",
        "prioritize accuracy over all other metrics",
        "ensure zero-latency response",
        "guarantee complete data redundancy"
    ],
    "goal_a": [
        "minimize cost",
        "maximize user satisfaction",
        "ensure compliance",
        "optimize performance",
        "reduce error rate"
    ],
    "goal_b_conflict": [
        "maximize feature coverage",
        "minimize response time",
        "ensure full audit logging",
        "maximize throughput",
        "ensure zero data loss"
    ],
    "constraint_a": [
        "memory usage under 512MB",
        "response time under 100ms",
        "CPU usage under 50%",
        "network bandwidth under 10Mbps",
        "storage writes under 1000 IOPS"
    ],
    "constraint_b_conflict": [
        "load all data into memory for fast access",
        "process all requests synchronously",
        "log all operations in real-time",
        "maintain full replication across nodes",
        "encrypt all data at rest and in transit"
    ],
    "metric_a": [
        "precision",
        "recall",
        "latency reduction",
        "cost efficiency",
        "user engagement"
    ],
    "metric_b_conflict": [
        "recall",
        "precision",
        "feature richness",
        "quality assurance",
        "coverage breadth"
    ],
    "domain": [
        "genetic analysis",
        "flare prediction",
        "scroll processing",
        "intervention planning",
        "biomarker detection"
    ],
    "entity": [
        "patient data",
        "genetic marker",
        "intervention scroll",
        "prediction vector",
        "treatment protocol"
    ],
    "entity_a": [
        "ATG16L1 marker",
        "flare prediction module",
        "scroll parser",
        "trust validator",
        "intervention engine"
    ],
    "entity_b": [
        "TNFSF15 pathway",
        "coconut loop",
        "gene mapper",
        "simulation backend",
        "mutation tracker"
    ],
    "input_type": [
        "genetic sequence data",
        "patient symptom vectors",
        "historical flare patterns",
        "intervention outcomes",
        "biomarker correlations"
    ],
    "condition_a": [
        "trust score exceeds threshold",
        "genetic marker is present",
        "flare probability is high",
        "patient consent is obtained",
        "simulation validates successfully"
    ],
    "condition_b": [
        "urgency level is critical",
        "fallback mode is enabled",
        "manual override is requested",
        "historical data suggests intervention",
        "secondary markers are detected"
    ],
    "action": [
        "trigger intervention cascade",
        "initiate simulation pipeline",
        "activate mutation loop",
        "generate treatment scroll",
        "execute gene mapping"
    ],
    "scenario": [
        "conflicting genetic markers",
        "ambiguous flare signals",
        "incomplete patient history",
        "untested intervention protocol",
        "edge-case biomarker pattern"
    ],
    "metric": [
        "prediction accuracy",
        "intervention success rate",
        "simulation fidelity",
        "marker detection sensitivity",
        "treatment efficacy"
    ],
    "issue_type": [
        "data inconsistency",
        "prediction divergence",
        "marker ambiguity",
        "protocol mismatch",
        "validation failure"
    ],
    "safety_constraint": [
        "minimum trust score requirement",
        "mandatory consent verification",
        "intervention rate limiting",
        "genetic marker validation",
        "simulation sandbox isolation"
    ],
    "operation": [
        "gene intervention",
        "scroll execution",
        "mutation triggering",
        "patient data access",
        "treatment deployment"
    ],
    "risky_action": [
        "untested mutation sequence",
        "experimental intervention protocol",
        "high-risk gene modification",
        "unvalidated scroll execution",
        "aggressive treatment cascade"
    ],
    "restricted_resource": [
        "patient genetic database",
        "intervention history logs",
        "simulation trust parameters",
        "mutation loop controls",
        "treatment approval queue"
    ],
    "critical_component": [
        "trust scoring algorithm",
        "genetic marker database",
        "intervention approval workflow",
        "simulation execution engine",
        "patient safety monitors"
    ]
}


def _deterministic_hash(seed: str, index: int) -> int:
    """Generate a deterministic hash for consistent template selection."""
    combined = f"{seed}:{index}"
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    return int.from_bytes(hash_bytes[:4], 'big')


def _select_variable(var_name: str, seed: str, index: int) -> str:
    """Deterministically select a variable value from the bank."""
    if var_name not in VARIABLE_BANKS:
        return f"[{var_name}]"
    bank = VARIABLE_BANKS[var_name]
    hash_val = _deterministic_hash(f"{seed}:{var_name}", index)
    return bank[hash_val % len(bank)]


def _fill_template(template: str, seed: str, index: int) -> str:
    """Fill template placeholders with deterministic variable selection."""
    result = template
    # Find all {variable} placeholders
    placeholders = re.findall(r'\{(\w+)\}', template)
    for i, var_name in enumerate(placeholders):
        value = _select_variable(var_name, seed, index + i)
        result = result.replace(f"{{{var_name}}}", value, 1)
    return result


def _get_templates_for_protocol(protocol: ProbeProtocol) -> List[str]:
    """Get the template list for a given protocol."""
    templates = {
        ProbeProtocol.CONFLICT_STRESS: CONFLICT_STRESS_TEMPLATES,
        ProbeProtocol.UNDERSPECIFICATION_STRESS: UNDERSPECIFICATION_TEMPLATES,
        ProbeProtocol.AMBIGUITY_STRESS: AMBIGUITY_TEMPLATES,
        ProbeProtocol.SAFETY_BOUNDARY: SAFETY_BOUNDARY_TEMPLATES,
    }
    return templates.get(protocol, UNDERSPECIFICATION_TEMPLATES)


def build_probe_suite(
    hypothesis: str,
    protocol: str,
    n: int,
    include_control: bool = True
) -> List[Dict[str, Any]]:
    """
    Build a deterministic probe suite for hypothesis testing.

    Args:
        hypothesis: The hypothesis being tested
        protocol: The probe protocol (conflict_stress, underspecification_stress,
                  ambiguity_stress, safety_boundary)
        n: Number of probes to generate
        include_control: Whether to include a control/baseline probe

    Returns:
        List of probe dictionaries with id, text, protocol, and is_control fields
    """
    # Normalize protocol string to enum
    try:
        protocol_enum = ProbeProtocol(protocol)
    except ValueError:
        protocol_enum = ProbeProtocol.UNDERSPECIFICATION_STRESS

    templates = _get_templates_for_protocol(protocol_enum)

    # Create deterministic seed from hypothesis
    seed = hashlib.sha256(hypothesis.encode()).hexdigest()[:16]

    probes = []

    # Generate n probes using templates
    for i in range(n):
        template_idx = _deterministic_hash(seed, i) % len(templates)
        template = templates[template_idx]

        # Inject hypothesis context into probe
        probe_text = _fill_template(template, seed, i)

        # Add hypothesis context prefix for relevance
        hypothesis_context = _extract_hypothesis_context(hypothesis)
        if hypothesis_context:
            probe_text = f"[Context: {hypothesis_context}] {probe_text}"

        probe_id = f"probe_{protocol}_{i}_{seed[:8]}"

        probes.append({
            "probe_id": probe_id,
            "probe_text": probe_text,
            "protocol": protocol,
            "is_control": False
        })

    # Add control probe if requested
    if include_control:
        control_text = _fill_template(CONTROL_TEMPLATE, seed, 999)
        control_id = f"control_{seed[:8]}"
        probes.append({
            "probe_id": control_id,
            "probe_text": control_text,
            "protocol": "control",
            "is_control": True
        })

    return probes


def _extract_hypothesis_context(hypothesis: str) -> str:
    """Extract key context from hypothesis for probe injection."""
    # Look for key domain terms
    domain_terms = [
        "conflict", "ambiguous", "underspecified", "safety",
        "flare", "genetic", "ATG16L1", "scroll", "intervention",
        "trust", "marker", "simulation", "prediction"
    ]

    hypothesis_lower = hypothesis.lower()
    found_terms = [term for term in domain_terms if term in hypothesis_lower]

    if found_terms:
        return f"testing {', '.join(found_terms[:3])}"
    return ""


def parse_execution_log(raw_output: str) -> StructuredLogFields:
    """
    Parse raw execution log into structured fields.

    Extracts:
    - termination_mode: How execution ended
    - mapping_evidence: Detected scroll-to-gene mappings
    - fallback_used: Whether fallback heuristics were triggered
    - heuristics_triggered: Which heuristics fired
    - uncertainty_markers: Signals of uncertainty
    """
    fields = StructuredLogFields()
    output_lower = raw_output.lower()

    # Determine termination mode
    if "scroll saved to" in output_lower:
        fields.termination_mode = "successful_completion"
    elif "failed to reach" in output_lower or "connection" in output_lower and "error" in output_lower:
        fields.termination_mode = "infrastructure_failure"
    elif "no actionable" in output_lower:
        fields.termination_mode = "no_match_halt"
    elif "error" in output_lower or "exception" in output_lower:
        fields.termination_mode = "error_termination"
    elif "timeout" in output_lower:
        fields.termination_mode = "timeout"
    else:
        fields.termination_mode = "normal_completion"

    # Extract mapping evidence
    gene_markers = ["ATG16L1", "TNFSF15", "NOD2", "IL23R", "IRGM"]
    for marker in gene_markers:
        if marker in raw_output:
            fields.mapping_evidence.append(f"genetic_marker:{marker}")

    if "flare" in output_lower:
        fields.mapping_evidence.append("scroll_type:flare")
    if "coconut" in output_lower or "mutation loop" in output_lower:
        fields.mapping_evidence.append("simulation_target:coconut_loop")
    if "triggering" in output_lower:
        fields.mapping_evidence.append("cascade:triggered")

    # Detect fallback usage
    fallback_indicators = ["fallback", "default", "heuristic", "no actionable", "best effort"]
    fields.fallback_used = any(ind in output_lower for ind in fallback_indicators)

    # Extract triggered heuristics
    if "no actionable scroll-to-gene patterns" in output_lower:
        fields.heuristics_triggered.append("pattern_match_fallback")
    if "trust score" in output_lower or "trust_score" in output_lower:
        fields.heuristics_triggered.append("trust_scoring")
    if "genetic resonance" in output_lower:
        fields.heuristics_triggered.append("genetic_resonance_detection")
    if "simulation" in output_lower:
        fields.heuristics_triggered.append("simulation_trigger")

    # Extract uncertainty markers
    uncertainty_words = ["ambiguous", "unclear", "uncertain", "may", "might", "possibly", "conflict"]
    for word in uncertainty_words:
        if word in output_lower:
            fields.uncertainty_markers.append(f"signal:{word}")

    # Collect raw signals
    signal_patterns = [
        (r"✓.*$", "success"),
        (r"⚠.*$", "warning"),
        (r"✖.*$", "error"),
        (r"→.*$", "action"),
    ]
    for pattern, signal_type in signal_patterns:
        matches = re.findall(pattern, raw_output, re.MULTILINE)
        for match in matches:
            fields.raw_signals.append(f"{signal_type}:{match.strip()[:50]}")

    return fields


def classify_outcome(
    structured_fields: StructuredLogFields,
    protocol: str
) -> tuple[OutcomeType, float]:
    """
    Classify probe outcome into one of 7 outcome types.

    Returns:
        Tuple of (OutcomeType, confidence score 0.0-1.0)
    """
    term_mode = structured_fields.termination_mode
    has_fallback = structured_fields.fallback_used
    has_mappings = len(structured_fields.mapping_evidence) > 0
    has_uncertainty = len(structured_fields.uncertainty_markers) > 0

    # Infrastructure failure - clear signal
    if term_mode == "infrastructure_failure":
        return OutcomeType.INFRASTRUCTURE_FAILURE, 0.95

    # Safety boundary protocol special handling
    if protocol == "safety_boundary":
        if term_mode == "no_match_halt" or has_fallback:
            return OutcomeType.SAFETY_HALT, 0.90
        if term_mode == "successful_completion":
            return OutcomeType.CONSTRAINT_VIOLATION, 0.85

    # Successful execution with mappings
    if term_mode == "successful_completion" and has_mappings:
        if has_uncertainty:
            return OutcomeType.GRACEFUL_DEGRADATION, 0.80
        return OutcomeType.STABLE_EXECUTION, 0.90

    # Fallback triggered
    if has_fallback:
        return OutcomeType.FALLBACK_TRIGGERED, 0.85

    # No match but clean termination
    if term_mode == "no_match_halt":
        if protocol == "underspecification_stress":
            return OutcomeType.GRACEFUL_DEGRADATION, 0.75
        return OutcomeType.FALLBACK_TRIGGERED, 0.70

    # Error termination
    if term_mode == "error_termination" or term_mode == "timeout":
        return OutcomeType.UNDEFINED_BEHAVIOR, 0.80

    # Normal completion without clear signals
    if term_mode == "normal_completion":
        if has_uncertainty:
            return OutcomeType.GRACEFUL_DEGRADATION, 0.65
        return OutcomeType.STABLE_EXECUTION, 0.60

    # Default: undefined behavior
    return OutcomeType.UNDEFINED_BEHAVIOR, 0.50


def compute_delta_vs_control(
    probe_results: List[ProbeResult],
    control_result: Optional[ProbeResult]
) -> Dict[str, Any]:
    """
    Compute the delta between probe results and control baseline.

    Returns metrics comparing experimental probes to control.
    """
    if not control_result or not probe_results:
        return {"available": False, "reason": "No control probe or no experimental probes"}

    # Filter out control from probe_results
    experimental = [p for p in probe_results if not p.is_control]

    if not experimental:
        return {"available": False, "reason": "No experimental probes to compare"}

    control_outcome = control_result.outcome_type.value
    control_confidence = control_result.outcome_confidence
    control_fallback = control_result.structured_fields.fallback_used
    control_mappings = len(control_result.structured_fields.mapping_evidence)
    control_uncertainty = len(control_result.structured_fields.uncertainty_markers)

    # Compute experimental averages
    exp_confidences = [p.outcome_confidence for p in experimental]
    exp_fallbacks = sum(1 for p in experimental if p.structured_fields.fallback_used)
    exp_mappings = sum(len(p.structured_fields.mapping_evidence) for p in experimental)
    exp_uncertainty = sum(len(p.structured_fields.uncertainty_markers) for p in experimental)

    # Outcome distribution
    outcome_counts = {}
    for p in experimental:
        ot = p.outcome_type.value
        outcome_counts[ot] = outcome_counts.get(ot, 0) + 1

    n = len(experimental)

    delta = {
        "available": True,
        "control_outcome": control_outcome,
        "control_confidence": control_confidence,
        "experimental_count": n,
        "outcome_distribution": outcome_counts,
        "delta_confidence": round(sum(exp_confidences) / n - control_confidence, 3),
        "delta_fallback_rate": round(exp_fallbacks / n - (1 if control_fallback else 0), 3),
        "delta_mapping_density": round(exp_mappings / n - control_mappings, 3),
        "delta_uncertainty_density": round(exp_uncertainty / n - control_uncertainty, 3),
        "divergence_score": 0.0  # Will be computed below
    }

    # Compute overall divergence score (how different from control)
    # Higher = more divergent from control behavior
    divergence = 0.0

    # Outcome divergence
    control_in_exp = outcome_counts.get(control_outcome, 0)
    if control_in_exp < n:
        divergence += (n - control_in_exp) / n * 0.4

    # Confidence divergence
    divergence += abs(delta["delta_confidence"]) * 0.2

    # Fallback divergence
    divergence += abs(delta["delta_fallback_rate"]) * 0.2

    # Uncertainty divergence
    divergence += min(1.0, abs(delta["delta_uncertainty_density"]) / 3) * 0.2

    delta["divergence_score"] = round(divergence, 3)

    return delta


def compute_aggregate_stats(probe_results: List[ProbeResult]) -> Dict[str, Any]:
    """Compute aggregate statistics across all probe results."""
    if not probe_results:
        return {}

    experimental = [p for p in probe_results if not p.is_control]

    if not experimental:
        return {}

    # Outcome distribution
    outcome_counts = {}
    for p in experimental:
        ot = p.outcome_type.value
        outcome_counts[ot] = outcome_counts.get(ot, 0) + 1

    # Compute metrics
    n = len(experimental)
    avg_confidence = sum(p.outcome_confidence for p in experimental) / n
    fallback_rate = sum(1 for p in experimental if p.structured_fields.fallback_used) / n
    uncertainty_rate = sum(1 for p in experimental if p.structured_fields.uncertainty_markers) / n

    # Most common outcome
    most_common_outcome = max(outcome_counts.keys(), key=lambda k: outcome_counts[k])

    # Stability score: higher if outcomes are consistent
    max_count = max(outcome_counts.values())
    stability_score = max_count / n

    return {
        "total_probes": n,
        "outcome_distribution": outcome_counts,
        "most_common_outcome": most_common_outcome,
        "avg_confidence": round(avg_confidence, 3),
        "fallback_rate": round(fallback_rate, 3),
        "uncertainty_rate": round(uncertainty_rate, 3),
        "stability_score": round(stability_score, 3),
        "unique_outcomes": len(outcome_counts)
    }


def probe_result_to_dict(result: ProbeResult) -> Dict[str, Any]:
    """Convert ProbeResult to a JSON-serializable dictionary."""
    return {
        "probe_id": result.probe_id,
        "probe_text": result.probe_text,
        "protocol": result.protocol,
        "is_control": result.is_control,
        "raw_output": result.raw_output,
        "structured_fields": asdict(result.structured_fields),
        "outcome_type": result.outcome_type.value,
        "outcome_confidence": result.outcome_confidence,
        "execution_time_ms": result.execution_time_ms
    }


def experiment_results_to_dict(results: ExperimentResults) -> Dict[str, Any]:
    """Convert ExperimentResults to a JSON-serializable dictionary."""
    return {
        "hypothesis": results.hypothesis,
        "protocol": results.protocol,
        "probe_count": results.probe_count,
        "include_control": results.include_control,
        "probes": [probe_result_to_dict(p) for p in results.probes],
        "control_probe": probe_result_to_dict(results.control_probe) if results.control_probe else None,
        "aggregate_stats": results.aggregate_stats,
        "delta_vs_control": results.delta_vs_control
    }

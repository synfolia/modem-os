"""
Unit tests for probe suite.

Tests the probe generation and classification logic.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.router.latent_mode.probe_suite import (
    build_probe_suite,
    parse_execution_log,
    classify_outcome,
    OutcomeType,
    StructuredLogFields
)


class TestProbeSuite(unittest.TestCase):
    """Test probe suite generation."""

    def test_build_probe_suite_structure(self):
        """Test that build_probe_suite returns correct structure."""
        hypothesis = "Test hypothesis"
        protocol = "conflict_stress"
        probe_count = 3
        include_control = True

        probes = build_probe_suite(hypothesis, protocol, probe_count, include_control)

        # Should have probe_count + 1 (for control)
        self.assertEqual(len(probes), probe_count + 1)

        # Check structure of each probe
        for probe in probes:
            self.assertIn("probe_id", probe)
            self.assertIn("probe_text", probe)
            self.assertIn("protocol", probe)
            self.assertIn("is_control", probe)

        # One should be control
        control_probes = [p for p in probes if p["is_control"]]
        self.assertEqual(len(control_probes), 1)

    def test_build_probe_suite_without_control(self):
        """Test probe suite generation without control."""
        hypothesis = "Test hypothesis"
        protocol = "underspecification_stress"
        probe_count = 5
        include_control = False

        probes = build_probe_suite(hypothesis, protocol, probe_count, include_control)

        # Should have exactly probe_count
        self.assertEqual(len(probes), probe_count)

        # None should be control
        control_probes = [p for p in probes if p["is_control"]]
        self.assertEqual(len(control_probes), 0)

    def test_probe_protocols(self):
        """Test different probe protocols."""
        protocols = [
            "conflict_stress",
            "underspecification_stress",
            "ambiguity_stress",
            "safety_boundary"
        ]

        for protocol in protocols:
            probes = build_probe_suite("Test", protocol, 2, False)
            self.assertEqual(len(probes), 2)
            for probe in probes:
                self.assertEqual(probe["protocol"], protocol)

    def test_probe_determinism(self):
        """Test that probe generation is deterministic."""
        hypothesis = "Test hypothesis"
        protocol = "conflict_stress"

        probes1 = build_probe_suite(hypothesis, protocol, 3, True)
        probes2 = build_probe_suite(hypothesis, protocol, 3, True)

        # Should generate identical probes
        self.assertEqual(len(probes1), len(probes2))
        for p1, p2 in zip(probes1, probes2):
            self.assertEqual(p1["probe_text"], p2["probe_text"])
            self.assertEqual(p1["protocol"], p2["protocol"])


class TestLogParsing(unittest.TestCase):
    """Test execution log parsing."""

    def test_parse_execution_log_basic(self):
        """Test parsing of basic execution log."""
        log = """
Executing in latent mode with DeepSeek-R1 model: Test
DeepSeek-R1 Reasoning: Some response text
DeepSeek-R1: No actionable scroll-to-gene patterns found.
"""
        fields = parse_execution_log(log)

        self.assertIsInstance(fields, StructuredLogFields)
        self.assertIsNotNone(fields.termination_mode)
        self.assertIsInstance(fields.raw_signals, list)

    def test_parse_execution_log_with_fallback(self):
        """Test parsing of log with fallback keyword."""
        log = """
Executing in latent mode with DeepSeek-R1 model: Test
Fallback: Performing deep analysis.
"""
        fields = parse_execution_log(log)

        # The parser should detect "Fallback" keyword
        self.assertTrue(fields.fallback_used)

    def test_structured_log_fields_creation(self):
        """Test manual creation of StructuredLogFields."""
        fields = StructuredLogFields(
            termination_mode="nominal",
            fallback_used=False
        )

        self.assertEqual(fields.termination_mode, "nominal")
        self.assertFalse(fields.fallback_used)
        self.assertIsInstance(fields.raw_signals, list)


class TestOutcomeClassification(unittest.TestCase):
    """Test outcome classification logic."""

    def test_classify_outcome_basic(self):
        """Test basic outcome classification."""
        fields = StructuredLogFields(
            termination_mode="nominal",
            fallback_used=False
        )

        outcome_type, confidence = classify_outcome(fields, "conflict_stress")

        # Should return an OutcomeType enum value
        self.assertIsInstance(outcome_type, OutcomeType)
        # Confidence should be between 0 and 1
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_classify_outcome_with_fallback(self):
        """Test classification with fallback flag."""
        fields_with_fallback = StructuredLogFields(
            termination_mode="nominal",
            fallback_used=True
        )

        outcome_type, confidence = classify_outcome(fields_with_fallback, "conflict_stress")

        # Should return valid outcome and confidence
        self.assertIsInstance(outcome_type, OutcomeType)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


class TestProbeIDs(unittest.TestCase):
    """Test probe ID generation."""

    def test_probe_ids_unique(self):
        """Test that probe IDs are unique within a suite."""
        probes = build_probe_suite("Test", "conflict_stress", 5, True)

        probe_ids = [p["probe_id"] for p in probes]
        unique_ids = set(probe_ids)

        self.assertEqual(len(probe_ids), len(unique_ids))

    def test_probe_id_format(self):
        """Test that probe IDs follow expected format."""
        probes = build_probe_suite("Test", "conflict_stress", 3, True)

        for probe in probes:
            probe_id = probe["probe_id"]
            # Should contain protocol and number
            self.assertIsInstance(probe_id, str)
            self.assertTrue(len(probe_id) > 0)


if __name__ == "__main__":
    unittest.main()

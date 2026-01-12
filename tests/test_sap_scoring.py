"""
Unit tests for SAP scoring system.

Tests the deterministic heuristic scoring of Structured Action Proposals.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.router.sap_scoring.score_sap import (
    score_sap,
    _calculate_plausibility,
    _calculate_utility,
    _calculate_novelty,
    _calculate_risk,
    _calculate_alignment,
    _calculate_efficiency,
    _calculate_resilience
)


class TestSAPScoring(unittest.TestCase):
    """Test SAP scoring functions."""

    def test_score_sap_structure(self):
        """Test that score_sap returns correct structure."""
        sap = {
            "title": "Test Proposal",
            "description": "A test description"
        }
        result = score_sap(sap)

        # Check structure
        self.assertIn("title", result)
        self.assertIn("description", result)
        self.assertIn("degrees", result)
        self.assertIn("composite_score", result)

        # Check degrees
        degrees = result["degrees"]
        expected_keys = [
            "plausibility", "utility", "novelty", "risk",
            "alignment", "efficiency", "resilience"
        ]
        for key in expected_keys:
            self.assertIn(key, degrees)
            self.assertIsInstance(degrees[key], int)
            self.assertGreaterEqual(degrees[key], 0)
            self.assertLessEqual(degrees[key], 10)

        # Check composite score
        self.assertEqual(result["composite_score"], sum(degrees.values()))

    def test_deterministic_scoring(self):
        """Test that scoring is deterministic (same input = same output)."""
        sap = {
            "title": "Optimize Performance",
            "description": "Implement efficient caching to reduce latency"
        }

        result1 = score_sap(sap)
        result2 = score_sap(sap)

        self.assertEqual(result1["composite_score"], result2["composite_score"])
        self.assertEqual(result1["degrees"], result2["degrees"])

    def test_plausibility_scoring(self):
        """Test plausibility scoring heuristics."""
        # High plausibility (concrete actions)
        high = _calculate_plausibility("implement api endpoint with test coverage")
        # Low plausibility (vague language)
        low = _calculate_plausibility("maybe we could perhaps try something")

        self.assertGreater(high, low)
        self.assertGreaterEqual(high, 0)
        self.assertLessEqual(high, 10)

    def test_utility_scoring(self):
        """Test utility scoring heuristics."""
        # High utility (problem-solving)
        high = _calculate_utility("improve performance and reduce costs")
        # Low utility (no clear benefit)
        low = _calculate_utility("do some stuff with things")

        self.assertGreater(high, low)

    def test_novelty_scoring(self):
        """Test novelty scoring heuristics."""
        # High novelty
        high = _calculate_novelty("innovative experimental approach using neural networks")
        # Low novelty
        low = _calculate_novelty("standard conventional traditional approach")

        self.assertGreater(high, low)

    def test_risk_scoring(self):
        """Test risk scoring heuristics (higher = more risky)."""
        # High risk
        high = _calculate_risk("experimental untested breaking changes")
        # Low risk
        low = _calculate_risk("stable tested proven approach")

        self.assertGreater(high, low)

    def test_alignment_scoring(self):
        """Test alignment scoring heuristics."""
        # High alignment (safety focused)
        high = _calculate_alignment("secure validated approach with privacy protection")
        # Low alignment (bypassing checks)
        low = _calculate_alignment("bypass security checks and skip validation")

        self.assertGreater(high, low)

    def test_efficiency_scoring(self):
        """Test efficiency scoring heuristics."""
        # High efficiency
        high = _calculate_efficiency("optimize performance with lightweight fast solution")
        # Low efficiency
        low = _calculate_efficiency("complex redundant overhead with bloat")

        self.assertGreater(high, low)

    def test_resilience_scoring(self):
        """Test resilience scoring heuristics."""
        # High resilience
        high = _calculate_resilience("robust fault-tolerant with error handling")
        # Low resilience
        low = _calculate_resilience("fragile brittle unstable approach")

        self.assertGreater(high, low)

    def test_risk_inversion(self):
        """Test that risk is properly inverted in final scoring."""
        # High-risk proposal should have LOW risk score after inversion
        risky_sap = {
            "title": "Experimental Approach",
            "description": "Untested radical breaking changes"
        }
        result = score_sap(risky_sap)

        # The risk degree should be inverted (10 - raw_risk)
        # So high-risk proposals get lower risk scores
        self.assertLessEqual(result["degrees"]["risk"], 5)

    def test_real_world_example_1(self):
        """Test scoring of a well-defined technical proposal."""
        sap = {
            "title": "Implement Caching Layer",
            "description": "Deploy Redis cache to improve API performance and reduce database load"
        }
        result = score_sap(sap)

        # Should score high on plausibility, utility, efficiency
        self.assertGreater(result["degrees"]["plausibility"], 5)
        self.assertGreater(result["degrees"]["utility"], 5)
        self.assertGreater(result["degrees"]["efficiency"], 5)

    def test_real_world_example_2(self):
        """Test scoring of an experimental proposal."""
        sap = {
            "title": "Experimental Latent Approach",
            "description": "Innovative experimental neural traversal with novel architecture"
        }
        result = score_sap(sap)

        # Should score high on novelty, but higher risk
        self.assertGreater(result["degrees"]["novelty"], 5)
        # Risk is inverted, so experimental = lower risk score
        self.assertLess(result["degrees"]["risk"], 5)

    def test_composite_score_range(self):
        """Test that composite score is in valid range."""
        sap = {
            "title": "Test",
            "description": "Test description"
        }
        result = score_sap(sap)

        # With 7 dimensions, each 0-10, total should be 0-70
        self.assertGreaterEqual(result["composite_score"], 0)
        self.assertLessEqual(result["composite_score"], 70)


class TestSAPScoringComparison(unittest.TestCase):
    """Test comparative scoring between different proposals."""

    def test_concrete_vs_vague(self):
        """Concrete proposals should score higher than vague ones."""
        concrete = {
            "title": "Deploy Monitoring",
            "description": "Implement Prometheus metrics and Grafana dashboards for system monitoring"
        }
        vague = {
            "title": "Maybe Improve Things",
            "description": "Perhaps we could possibly try to make it better somehow"
        }

        result_concrete = score_sap(concrete)
        result_vague = score_sap(vague)

        self.assertGreater(
            result_concrete["composite_score"],
            result_vague["composite_score"]
        )

    def test_safe_vs_risky(self):
        """Safe proposals should have higher risk scores (inverted) than risky ones."""
        safe = {
            "title": "Tested Approach",
            "description": "Deploy proven validated solution with comprehensive testing"
        }
        risky = {
            "title": "Experimental Approach",
            "description": "Untested experimental radical changes with breaking updates"
        }

        result_safe = score_sap(safe)
        result_risky = score_sap(risky)

        # Safe should have higher risk score (because risk is inverted)
        self.assertGreater(
            result_safe["degrees"]["risk"],
            result_risky["degrees"]["risk"]
        )


if __name__ == "__main__":
    unittest.main()

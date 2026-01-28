"""Comprehensive tests for Yule's K and I vocabulary richness metrics."""

import math

from pystylometry.lexical import compute_yule


class TestYuleIFormula:
    """Test Yule's I formula: (V² / Σm²×Vm) - (1/N)."""

    def test_yule_i_manual_calculation(self):
        """Test Yule's I with manually verified calculation."""
        # "one two one three one" -> frequencies: one=3, two=1, three=1
        text = "one two one three one"
        result = compute_yule(text)

        # N = 5, V = 3
        # Σm²×Vm = 11 (from above)
        # I = V² / (Σm²×Vm - N) = 3² / (11 - 5) = 9 / 6 = 1.5

        N = 5  # noqa: N806
        V = 3  # noqa: N806
        sum_m2_vm = 11
        expected_i = (V * V) / (sum_m2_vm - N)

        assert abs(result.yule_i - expected_i) < 0.001, f"Yule's I should be {expected_i:.3f}"

    def test_yule_i_increases_with_diversity(self):
        """Test that Yule's I increases with more diversity."""
        # Low repetition (more diverse) - but with some repetition to avoid NaN
        diverse_text = "one two three four five six one"

        # High repetition (less diverse)
        repetitive_text = "the the the the the the the"

        result_diverse = compute_yule(diverse_text)
        result_repetitive = compute_yule(repetitive_text)

        # Higher I = more diverse (both should have numeric values)
        assert not math.isnan(result_diverse.yule_i), "Diverse text should have numeric I"
        assert not math.isnan(result_repetitive.yule_i), "Repetitive text should have numeric I"
        assert result_diverse.yule_i > result_repetitive.yule_i, (
            "Yule's I should be higher for diverse text"
        )

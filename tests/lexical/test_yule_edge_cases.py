"""Comprehensive tests for Yule's K and I vocabulary richness metrics."""

import math

from pystylometry.lexical import compute_yule


class TestYuleEdgeCases:
    """Test edge cases for Yule computation."""

    def test_empty_text(self):
        """Test Yule with empty text."""
        result = compute_yule("")

        # Empty input should return NaN, not 0.0
        assert math.isnan(result.yule_k), "Empty input should return NaN for K"
        assert math.isnan(result.yule_i), "Empty input should return NaN for I"
        assert result.metadata["token_count"] == 0
        assert result.metadata["vocabulary_size"] == 0

    def test_single_word_repeated(self):
        """Test Yule with single word repeated multiple times."""
        text = "the the the the the"
        result = compute_yule(text)

        # N = 5, V = 1
        # Only one word type with frequency 5
        # Vm[5] = 1
        # Σm²×Vm = 5² × 1 = 25

        # K = 10⁴ × (25 - 5) / 5² = 10000 × 20 / 25 = 8000
        expected_k = 10_000 * (25 - 5) / (5 * 5)
        assert abs(result.yule_k - expected_k) < 0.001, f"Yule's K should be {expected_k:.3f}"

        # I = V² / (Σm²×Vm - N) = 1² / (25 - 5) = 1 / 20 = 0.05
        expected_i = (1 * 1) / (25 - 5)
        assert abs(result.yule_i - expected_i) < 0.001, f"Yule's I should be {expected_i:.3f}"

    def test_all_unique_words(self):
        """Test Yule with all unique words (perfect diversity)."""
        text = "one two three four five"
        result = compute_yule(text)

        # N = 5, V = 5
        # All words appear once: Vm[1] = 5
        # Σm²×Vm = 1² × 5 = 5

        # K = 10⁴ × (5 - 5) / 5² = 0
        assert result.yule_k == 0.0, "Yule's K should be 0 for all unique words"

        # I = V² / (Σm²×Vm - N) = 5² / (5 - 5) = 25 / 0 = undefined
        # When all words are unique, denominator is zero, so I should be NaN
        assert math.isnan(result.yule_i), (
            "Yule's I should be NaN for perfectly unique vocabulary (division by zero)"
        )

    def test_whitespace_only(self):
        """Test Yule with only whitespace."""
        result = compute_yule("   \n\t  ")

        # Whitespace-only should return NaN like empty input
        assert math.isnan(result.yule_k), "Whitespace-only should return NaN for K"
        assert math.isnan(result.yule_i), "Whitespace-only should return NaN for I"
        assert result.metadata["token_count"] == 0

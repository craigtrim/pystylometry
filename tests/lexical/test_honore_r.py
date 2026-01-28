"""Comprehensive tests for hapax legomena and vocabulary richness metrics."""

import math

from pystylometry.lexical import compute_hapax_ratios


class TestHonoreR:
    """Test Honoré's R statistic: 100 × log(N) / (1 - V₁/V)."""

    def test_honore_r_formula(self):
        """Test Honoré's R = 100 × log(N) / (1 - V₁/V)."""
        # Construct text with known counts
        # "one two three four four" -> N=5, V=4, V₁=3
        text = "one two three four four"
        result = compute_hapax_ratios(text)

        N = 5  # noqa: N806
        V = 4  # noqa: N806
        V1 = 3  # noqa: N806

        assert result.metadata["total_token_count"] == N
        assert result.metadata["total_vocabulary_size"] == V
        assert result.hapax_count == V1

        # R = 100 × log(5) / (1 - 3/4) = 100 × log(5) / 0.25
        expected_r = 100 * math.log(N) / (1 - V1 / V)
        assert abs(result.honore_r - expected_r) < 0.001, f"Honoré's R should be {expected_r:.3f}"

    def test_honore_r_edge_case_all_unique(self):
        """Test Honoré's R when V₁ = V (denominator is zero)."""
        text = "one two three four five"
        result = compute_hapax_ratios(text)

        # V₁ = V = 5, so (1 - V₁/V) = 0
        # Should return infinity to indicate maximal vocabulary richness
        assert result.honore_r == float("inf"), (
            "Honoré's R should be infinity when all words are unique"
        )

    def test_honore_r_high_repetition(self):
        """Test Honoré's R with highly repetitive text."""
        # Most words repeat, few hapax
        text = "the the the cat cat dog"
        result = compute_hapax_ratios(text)

        # N = 6, V = 3, V₁ = 1 (only "dog" is hapax)
        # R = 100 × log(6) / (1 - 1/3) = 100 × log(6) / (2/3)
        N = 6  # noqa: N806
        V = 3  # noqa: N806
        V1 = 1  # noqa: N806

        expected_r = 100 * math.log(N) / (1 - V1 / V)
        assert abs(result.honore_r - expected_r) < 0.001

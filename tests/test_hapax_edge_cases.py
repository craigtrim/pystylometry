"""Comprehensive tests for hapax legomena and vocabulary richness metrics."""

import math

from pystylometry.lexical import compute_hapax_ratios


class TestHapaxEdgeCases:
    """Test edge cases for hapax computation."""

    def test_empty_text(self):
        """Test hapax with empty text."""
        result = compute_hapax_ratios("")

        assert result.hapax_count == 0
        assert math.isnan(result.hapax_ratio)  # NaN for empty text per Distribution pattern
        assert result.dis_hapax_count == 0
        assert math.isnan(result.dis_hapax_ratio)  # NaN for empty text
        assert math.isnan(result.sichel_s)  # NaN for empty text
        assert math.isnan(result.honore_r)  # NaN for empty text
        assert result.metadata["total_token_count"] == 0
        assert result.metadata["total_vocabulary_size"] == 0

    def test_all_unique_words(self):
        """Test text where every word appears exactly once (V₁ = V)."""
        text = "one two three four five"
        result = compute_hapax_ratios(text)

        # All 5 words are hapax legomena
        assert result.hapax_count == 5
        assert result.dis_hapax_count == 0
        assert result.metadata["total_vocabulary_size"] == 5

        # When V₁ = V, Honoré's R returns infinity (maximal richness)
        # Because denominator (1 - V₁/V) = 0
        assert result.honore_r == float("inf"), (
            "Honoré's R should be infinity for maximal vocabulary richness"
        )

        # Sichel's S should be 0 (no dis-hapax)
        assert result.sichel_s == 0.0

    def test_all_same_word(self):
        """Test text with one word repeated multiple times."""
        text = "the the the the the"
        result = compute_hapax_ratios(text)

        # No hapax legomena (word appears 5 times)
        assert result.hapax_count == 0
        assert result.dis_hapax_count == 0
        assert result.hapax_ratio == 0.0
        assert result.dis_hapax_ratio == 0.0
        assert result.metadata["total_vocabulary_size"] == 1

    def test_whitespace_only(self):
        """Test text with only whitespace."""
        result = compute_hapax_ratios("   \n\t  ")

        assert result.hapax_count == 0
        assert result.metadata["total_token_count"] == 0

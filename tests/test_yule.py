"""Comprehensive tests for Yule's K and I vocabulary richness metrics."""

import math

from pystylometry.lexical import compute_yule


class TestYuleBasicFunctionality:
    """Test basic Yule's K and I functionality."""

    def test_basic_yule_computation(self):
        """Test Yule's K and I computation with sample text."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_yule(text)

        # Should return both metrics
        assert hasattr(result, "yule_k")
        assert hasattr(result, "yule_i")
        assert hasattr(result, "metadata")

        # Both should be non-negative
        assert result.yule_k >= 0.0
        assert result.yule_i >= 0.0

    def test_yule_with_longer_text(self):
        """Test Yule with longer text for more reliable metrics."""
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "A fast red wolf runs across the sleepy cat. "
            "Many different animals live in various places."
        )
        result = compute_yule(text)

        # Should have positive values
        assert result.yule_k > 0.0
        assert result.yule_i > 0.0


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
        assert abs(result.yule_k - expected_k) < 0.001, (
            f"Yule's K should be {expected_k:.3f}"
        )

        # I = V² / (Σm²×Vm - N) = 1² / (25 - 5) = 1 / 20 = 0.05
        expected_i = (1 * 1) / (25 - 5)
        assert abs(result.yule_i - expected_i) < 0.001, (
            f"Yule's I should be {expected_i:.3f}"
        )

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


class TestYuleKFormula:
    """Test Yule's K formula: 10⁴ × (Σm²×Vm - N) / N²."""

    def test_yule_k_manual_calculation(self):
        """Test Yule's K with manually verified calculation."""
        # "one two one three one" -> frequencies: one=3, two=1, three=1
        text = "one two one three one"
        result = compute_yule(text)

        # N = 5, V = 3
        # Frequency distribution:
        #   - "one" appears 3 times -> Vm[3] = 1
        #   - "two" appears 1 time -> Vm[1] = 2 (two and three)
        #   - "three" appears 1 time (counted above)
        # Σm²×Vm = 3² × 1 + 1² × 2 = 9 + 2 = 11

        # K = 10⁴ × (11 - 5) / 5² = 10000 × 6 / 25 = 2400
        N = 5  # noqa: N806
        sum_m2_vm = 3 * 3 * 1 + 1 * 1 * 2  # 9 + 2 = 11
        expected_k = 10_000 * (sum_m2_vm - N) / (N * N)

        assert abs(result.yule_k - expected_k) < 0.001, (
            f"Yule's K should be {expected_k:.3f}"
        )

    def test_yule_k_increases_with_repetition(self):
        """Test that Yule's K increases with more repetition."""
        # Low repetition (more diverse)
        diverse_text = "one two three four five six seven"

        # High repetition (less diverse)
        repetitive_text = "the the the the the the the"

        result_diverse = compute_yule(diverse_text)
        result_repetitive = compute_yule(repetitive_text)

        # Higher K = more repetitive
        assert result_repetitive.yule_k > result_diverse.yule_k, (
            "Yule's K should be higher for repetitive text"
        )


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

        assert abs(result.yule_i - expected_i) < 0.001, (
            f"Yule's I should be {expected_i:.3f}"
        )

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


class TestYuleKIRelationship:
    """Test relationship between Yule's K and I."""

    def test_k_and_i_inverse_relationship(self):
        """Test that K and I have inverse relationship (K high = I low)."""
        # Create texts with different diversity levels
        # Note: Avoid perfectly unique vocabularies which produce NaN for I
        texts = [
            "one two three four one",  # High diversity (but not perfect)
            "one one two two three",  # Medium diversity
            "the the the the the",  # Low diversity (high repetition)
        ]

        results = [compute_yule(text) for text in texts]

        # As we go from high to low diversity:
        # - K should increase (more repetitive)
        # - I should decrease (less diverse)

        # High diversity should have low K, high I
        assert results[0].yule_k < results[2].yule_k
        # Only compare I if both are numeric (not NaN)
        if not math.isnan(results[0].yule_i) and not math.isnan(results[2].yule_i):
            assert results[0].yule_i > results[2].yule_i

    def test_extreme_diversity_values(self):
        """Test K and I at extreme diversity levels."""
        # Perfect diversity (all unique)
        diverse_text = "one two three four five six seven eight nine ten"
        result_diverse = compute_yule(diverse_text)

        # K should be 0 for perfect diversity
        assert result_diverse.yule_k == 0.0

        # I should be NaN for perfect diversity (division by zero)
        assert math.isnan(result_diverse.yule_i), (
            "Yule's I should be NaN for perfect diversity"
        )


class TestYuleMetadata:
    """Test metadata returned with Yule results."""

    def test_metadata_contains_counts(self):
        """Test that metadata contains token_count and vocabulary_size."""
        text = "one two three one two one"
        result = compute_yule(text)

        assert "token_count" in result.metadata
        assert "vocabulary_size" in result.metadata

        assert result.metadata["token_count"] == 6
        assert result.metadata["vocabulary_size"] == 3

    def test_metadata_consistency(self):
        """Test that metadata is consistent with input text."""
        text = "the quick brown fox"
        result = compute_yule(text)

        # All words unique
        assert result.metadata["vocabulary_size"] == 4
        assert result.metadata["token_count"] == 4


class TestYuleWithRealText:
    """Test Yule with more realistic text samples."""

    def test_yule_with_prose(self):
        """Test Yule with a prose sample."""
        text = (
            "The sun rose over the distant mountains, casting long shadows "
            "across the valley. Birds began their morning songs, and the "
            "world slowly awakened to a new day. The air was crisp and fresh, "
            "filled with the promise of possibilities."
        )
        result = compute_yule(text)

        # Should have reasonable values
        assert result.yule_k > 0.0
        assert result.yule_i > 0.0

        # Natural prose should have moderate K (not extremely high or zero)
        # and positive I

    def test_yule_with_repetitive_prose(self):
        """Test Yule with deliberately repetitive text."""
        text = (
            "The cat sat. The cat sat on the mat. The cat sat on the mat "
            "and the cat looked at the mat. The mat was soft and the cat "
            "liked the mat."
        )
        result = compute_yule(text)

        # Repetitive text should have higher K
        assert result.yule_k > 0.0

        # Should still have positive I, but lower than diverse text
        assert result.yule_i > 0.0

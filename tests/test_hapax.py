"""Comprehensive tests for hapax legomena and vocabulary richness metrics."""

import math

from pystylometry.lexical import compute_hapax_ratios


class TestHapaxBasicFunctionality:
    """Test basic hapax legomena functionality."""

    def test_basic_hapax_detection(self):
        """Test detection of hapax legomena (words appearing once)."""
        # "quick", "brown", "fox", "jumps", "over", "lazy", "dog" appear once
        # "the" appears twice (lowercased: "The" and "the")
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_hapax_ratios(text)

        # 7 words appear once (hapax legomena)
        assert result.hapax_count == 7, "Should detect 7 hapax legomena"

        # 1 word appears twice (dis-hapax legomena)
        assert result.dis_hapax_count == 1, "Should detect 1 dis-hapax legomenon (the)"

        # Vocabulary size should be 8 unique words
        assert result.metadata["vocabulary_size"] == 8

    def test_hapax_ratio_calculation(self):
        """Test hapax ratio = hapax_count / token_count."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_hapax_ratios(text)

        # 9 total tokens, 7 hapax
        expected_ratio = 7.0 / 9.0
        assert abs(result.hapax_ratio - expected_ratio) < 0.001

    def test_dis_hapax_ratio_calculation(self):
        """Test dis-hapax ratio = dis_hapax_count / token_count."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_hapax_ratios(text)

        # 9 total tokens, 1 dis-hapax ("the" appears twice)
        expected_ratio = 1.0 / 9.0
        assert abs(result.dis_hapax_ratio - expected_ratio) < 0.001


class TestHapaxEdgeCases:
    """Test edge cases for hapax computation."""

    def test_empty_text(self):
        """Test hapax with empty text."""
        result = compute_hapax_ratios("")

        assert result.hapax_count == 0
        assert result.hapax_ratio == 0.0
        assert result.dis_hapax_count == 0
        assert result.dis_hapax_ratio == 0.0
        assert result.sichel_s == 0.0
        assert result.honore_r == 0.0
        assert result.metadata["token_count"] == 0
        assert result.metadata["vocabulary_size"] == 0

    def test_all_unique_words(self):
        """Test text where every word appears exactly once (V₁ = V)."""
        text = "one two three four five"
        result = compute_hapax_ratios(text)

        # All 5 words are hapax legomena
        assert result.hapax_count == 5
        assert result.dis_hapax_count == 0
        assert result.metadata["vocabulary_size"] == 5

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
        assert result.metadata["vocabulary_size"] == 1

    def test_whitespace_only(self):
        """Test text with only whitespace."""
        result = compute_hapax_ratios("   \n\t  ")

        assert result.hapax_count == 0
        assert result.metadata["token_count"] == 0


class TestSichelS:
    """Test Sichel's S statistic: V₂ / V."""

    def test_sichel_s_formula(self):
        """Test Sichel's S = V₂ / V (ratio of dis-hapax to vocabulary)."""
        # Construct text with known dis-hapax count
        # "one one" (dis-hapax), "two two" (dis-hapax), "three" (hapax)
        text = "one one two two three"
        result = compute_hapax_ratios(text)

        # V = 3 (vocabulary size)
        # V₂ = 2 (words appearing exactly twice: "one", "two")
        # S = 2 / 3
        assert result.metadata["vocabulary_size"] == 3
        assert result.dis_hapax_count == 2

        expected_s = 2.0 / 3.0
        assert abs(result.sichel_s - expected_s) < 0.001, (
            f"Sichel's S should be {expected_s:.3f}"
        )

    def test_sichel_s_no_dishapax(self):
        """Test Sichel's S when there are no dis-hapax legomena."""
        # All words appear once or 3+ times
        text = "one two three four four four"
        result = compute_hapax_ratios(text)

        # V₂ = 0 (no words appear exactly twice)
        assert result.dis_hapax_count == 0
        assert result.sichel_s == 0.0

    def test_sichel_s_all_dishapax(self):
        """Test Sichel's S when all words are dis-hapax."""
        text = "one one two two three three"
        result = compute_hapax_ratios(text)

        # V = 3, V₂ = 3 (all words appear exactly twice)
        # S = 3 / 3 = 1.0
        assert result.metadata["vocabulary_size"] == 3
        assert result.dis_hapax_count == 3
        assert abs(result.sichel_s - 1.0) < 0.001


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

        assert result.metadata["token_count"] == N
        assert result.metadata["vocabulary_size"] == V
        assert result.hapax_count == V1

        # R = 100 × log(5) / (1 - 3/4) = 100 × log(5) / 0.25
        expected_r = 100 * math.log(N) / (1 - V1 / V)
        assert abs(result.honore_r - expected_r) < 0.001, (
            f"Honoré's R should be {expected_r:.3f}"
        )

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


class TestHapaxMetadata:
    """Test metadata returned with hapax results."""

    def test_metadata_contains_counts(self):
        """Test that metadata contains token_count and vocabulary_size."""
        text = "one two three one two one"
        result = compute_hapax_ratios(text)

        assert "token_count" in result.metadata
        assert "vocabulary_size" in result.metadata

        assert result.metadata["token_count"] == 6
        assert result.metadata["vocabulary_size"] == 3

    def test_metadata_consistency(self):
        """Test that metadata counts are consistent with results."""
        text = "the quick brown fox"
        result = compute_hapax_ratios(text)

        # All words unique, so hapax_count should equal vocabulary_size
        assert result.hapax_count == result.metadata["vocabulary_size"]

        # hapax_ratio should equal hapax_count / token_count
        expected_ratio = result.hapax_count / result.metadata["token_count"]
        assert abs(result.hapax_ratio - expected_ratio) < 0.001

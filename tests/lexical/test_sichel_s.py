"""Comprehensive tests for hapax legomena and vocabulary richness metrics."""

from pystylometry.lexical import compute_hapax_ratios


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
        assert result.metadata["total_vocabulary_size"] == 3
        assert result.dis_hapax_count == 2

        expected_s = 2.0 / 3.0
        assert abs(result.sichel_s - expected_s) < 0.001, f"Sichel's S should be {expected_s:.3f}"

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
        assert result.metadata["total_vocabulary_size"] == 3
        assert result.dis_hapax_count == 3
        assert abs(result.sichel_s - 1.0) < 0.001

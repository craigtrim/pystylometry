"""Comprehensive tests for Yule's K and I vocabulary richness metrics."""

from pystylometry.lexical import compute_yule


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

        assert abs(result.yule_k - expected_k) < 0.001, f"Yule's K should be {expected_k:.3f}"

    def test_yule_k_increases_with_repetition(self):
        """Test that Yule's K increases with more repetition."""
        # Low repetition (more diverse)
        diverse_text = "one two three four five six seven"

        # High repetition (less diverse)
        repetitive_text = "the the the the the the the"

        result_diverse = compute_yule(diverse_text)
        result_repetitive = compute_yule(repetitive_text)

        # Higher K = more repetitive
        assert (
            result_repetitive.yule_k > result_diverse.yule_k
        ), "Yule's K should be higher for repetitive text"

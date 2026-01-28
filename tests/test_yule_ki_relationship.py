"""Comprehensive tests for Yule's K and I vocabulary richness metrics."""

import math

from pystylometry.lexical import compute_yule


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
        assert math.isnan(result_diverse.yule_i), "Yule's I should be NaN for perfect diversity"

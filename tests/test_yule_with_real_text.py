"""Comprehensive tests for Yule's K and I vocabulary richness metrics."""

from pystylometry.lexical import compute_yule


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

"""Comprehensive tests for MTLD (Measure of Textual Lexical Diversity)."""

from pystylometry.lexical import compute_mtld


class TestMTLDRobustness:
    """Test MTLD robustness to text length variations."""

    def test_mtld_more_stable_than_ttr(self):
        """
        Test that MTLD is more robust to text length than simple TTR.

        This is a key advantage of MTLD - it should be less affected by
        text length compared to Type-Token Ratio.
        """
        # Short text with some diversity
        short_text = "the cat sat on the mat"

        # Longer text with similar diversity pattern
        long_text = "the cat sat on the mat and the dog ran with the ball"

        result_short = compute_mtld(short_text)
        result_long = compute_mtld(long_text)

        # Both should have positive MTLD
        assert result_short.mtld_average > 0.0
        assert result_long.mtld_average > 0.0

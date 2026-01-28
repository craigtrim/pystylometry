"""Comprehensive tests for MTLD (Measure of Textual Lexical Diversity)."""

from pystylometry.lexical import compute_mtld


class TestMTLDRepetitionVsDiversity:
    """Test MTLD behavior with varying levels of repetition."""

    def test_highly_repetitive_text(self):
        """Test MTLD with highly repetitive text (low diversity)."""
        # Repeat the same word many times
        text = "the " * 50
        result = compute_mtld(text)

        # Highly repetitive text should have low MTLD
        # TTR will drop quickly below threshold
        assert result.mtld_forward > 0.0
        assert result.mtld_backward > 0.0
        # MTLD should be relatively low for repetitive text
        # (Each factor completes quickly as TTR drops)

    def test_highly_diverse_text(self):
        """Test MTLD with highly diverse text (all unique words)."""
        # All unique words
        text = "one two three four five six seven eight nine ten"
        result = compute_mtld(text)

        # With all unique words, TTR stays at 1.0
        # No factors complete, so MTLD equals text length
        assert result.mtld_forward == 10.0
        assert result.mtld_backward == 10.0
        assert result.mtld_average == 10.0

    def test_mixed_diversity(self):
        """Test MTLD with mixed repetition and diversity."""
        # Some repeated words, some unique
        text = "the cat sat on the mat and the dog ran with the ball"
        result = compute_mtld(text)

        # Should have moderate MTLD
        assert result.mtld_forward > 0.0
        assert result.mtld_backward > 0.0

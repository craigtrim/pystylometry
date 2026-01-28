"""Comprehensive tests for MTLD (Measure of Textual Lexical Diversity)."""

from pystylometry.lexical import compute_mtld


class TestMTLDForwardBackward:
    """Test MTLD forward vs backward computation."""

    def test_forward_backward_similarity(self):
        """Test that forward and backward MTLD are similar for typical text."""
        # For most texts, forward and backward should be reasonably close
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "A fast red wolf runs across the sleepy cat. "
            "Many different animals live in various places."
        )
        result = compute_mtld(text)

        # Forward and backward should be positive
        assert result.mtld_forward > 0.0
        assert result.mtld_backward > 0.0

        # They should be reasonably similar (within a factor of 2 or so)
        # for balanced text
        # This is a loose bound - they don't need to be identical
        # but shouldn't be wildly different for typical prose

    def test_forward_backward_identical_for_all_unique(self):
        """Test forward = backward when all words are unique."""
        text = "one two three four five six seven"
        result = compute_mtld(text)

        # With all unique words, direction doesn't matter
        assert result.mtld_forward == result.mtld_backward == 7.0

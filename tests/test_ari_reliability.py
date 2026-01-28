"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARIReliability:
    """Test reliability flag behavior."""

    def test_reliability_threshold_exact(self):
        """Test reliability at exact threshold."""
        # 99 tokens (98 words + period = 99 tokens)
        text = " ".join(["word"] * 98) + "."
        result = compute_ari(text)
        assert not result.metadata["reliable"]
        assert result.metadata["word_count"] == 99

        # 100 tokens (99 words + period = 100 tokens)
        text = " ".join(["word"] * 99) + "."
        result = compute_ari(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] == 100

    def test_reliability_flag_type(self):
        """Verify reliability is always a boolean."""
        texts = ["", "Short.", " ".join(["word"] * 200) + "."]

        for text in texts:
            result = compute_ari(text)
            assert isinstance(result.metadata["reliable"], bool)

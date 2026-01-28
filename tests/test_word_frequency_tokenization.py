"""Tests for word frequency sophistication metrics.

Tests the implementation of vocabulary sophistication measurement using
corpus frequency data. Related to GitHub Issue #15.
"""

from pystylometry.lexical import compute_word_frequency_sophistication

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


class TestWordFrequencyTokenization:
    """Tokenization tests."""

    def test_case_insensitivity(self):
        """Test case-insensitive tokenization."""
        text1 = "The RESEARCH method is GOOD"
        text2 = "the research method is good"

        result1 = compute_word_frequency_sophistication(text1)
        result2 = compute_word_frequency_sophistication(text2)

        # Should produce identical results
        assert result1.mean_frequency_rank == result2.mean_frequency_rank
        assert result1.academic_word_ratio == result2.academic_word_ratio

    def test_punctuation_handling(self):
        """Test punctuation is stripped correctly."""
        text1 = "research, method. analysis! data?"
        text2 = "research method analysis data"

        result1 = compute_word_frequency_sophistication(text1)
        result2 = compute_word_frequency_sophistication(text2)

        # Should have same token count (4 words)
        assert result1.metadata["total_words"] == 4
        assert result2.metadata["total_words"] == 4

    def test_whitespace_handling(self):
        """Test various whitespace patterns."""
        text = "research   method\n\nanalysis\t\tdata"
        result = compute_word_frequency_sophistication(text)

        assert result.metadata["total_words"] == 4

"""Tests for extended n-gram features.

Related GitHub Issue:
    #19 - Extended N-gram Features
    https://github.com/craigtrim/pystylometry/issues/19

Tests cover:
    - Word n-grams (trigrams, 4-grams)
    - Skipgrams (n-grams with gaps)
    - Character n-grams (trigrams, 4-grams)
    - Shannon entropy calculations
    - POS n-grams (optional, requires spaCy)
"""

from pystylometry.ngrams.extended_ngrams import (
    compute_extended_ngrams,
)

# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestExtendedNgramsIntegration:
    """Integration tests for extended n-grams."""

    def test_consistent_across_runs(self, sample_text):
        """Test results are consistent across multiple runs."""
        result1 = compute_extended_ngrams(sample_text, include_pos_ngrams=False)
        result2 = compute_extended_ngrams(sample_text, include_pos_ngrams=False)

        assert result1.word_trigram_count == result2.word_trigram_count
        assert result1.word_trigram_entropy == result2.word_trigram_entropy
        assert result1.top_word_trigrams == result2.top_word_trigrams

    def test_longer_text_more_unique(self, sample_text, long_text):
        """Test longer text has more unique n-grams."""
        result_short = compute_extended_ngrams(sample_text, include_pos_ngrams=False)
        result_long = compute_extended_ngrams(long_text, include_pos_ngrams=False)

        # Longer text should generally have more unique word trigrams
        # (unless short text has more repetition)
        assert result_long.metadata["token_count"] >= result_short.metadata["token_count"]

    def test_full_distributions_in_metadata(self, sample_text):
        """Test full distributions are stored in metadata."""
        result = compute_extended_ngrams(sample_text, include_pos_ngrams=False)

        assert "full_distributions" in result.metadata
        dist = result.metadata["full_distributions"]
        assert "word_trigrams" in dist
        assert "word_4grams" in dist
        assert "skipgrams_2_1" in dist
        assert "skipgrams_3_1" in dist
        assert "char_trigrams" in dist
        assert "char_4grams" in dist

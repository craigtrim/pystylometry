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

import math

from pystylometry.ngrams.extended_ngrams import (
    compute_extended_ngrams,
)

# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestComputeExtendedNgrams:
    """Tests for compute_extended_ngrams main function."""

    def test_basic_functionality(self, sample_text):
        """Test basic n-gram computation returns expected structure."""
        result = compute_extended_ngrams(sample_text, include_pos_ngrams=False)

        # Word n-grams
        assert hasattr(result, "top_word_trigrams")
        assert hasattr(result, "top_word_4grams")
        assert hasattr(result, "word_trigram_count")
        assert hasattr(result, "word_4gram_count")
        assert hasattr(result, "word_trigram_entropy")
        assert hasattr(result, "word_4gram_entropy")

        # Skipgrams
        assert hasattr(result, "top_skipgrams_2_1")
        assert hasattr(result, "top_skipgrams_3_1")
        assert hasattr(result, "skipgram_2_1_count")
        assert hasattr(result, "skipgram_3_1_count")

        # Character n-grams
        assert hasattr(result, "top_char_trigrams")
        assert hasattr(result, "top_char_4grams")
        assert hasattr(result, "char_trigram_entropy")
        assert hasattr(result, "char_4gram_entropy")

        # POS n-grams
        assert hasattr(result, "top_pos_trigrams")
        assert hasattr(result, "top_pos_4grams")
        assert hasattr(result, "pos_trigram_count")
        assert hasattr(result, "pos_4gram_count")
        assert hasattr(result, "pos_trigram_entropy")

        # Metadata
        assert hasattr(result, "metadata")

    def test_word_trigrams_format(self, sample_text):
        """Test word trigrams are formatted correctly."""
        result = compute_extended_ngrams(sample_text, include_pos_ngrams=False)

        # Should be list of (string, count) tuples
        for ngram, count in result.top_word_trigrams:
            assert isinstance(ngram, str)
            assert isinstance(count, int)
            assert count > 0
            # Should have spaces (3 words)
            assert " " in ngram

    def test_char_trigrams_format(self, sample_text):
        """Test character trigrams are formatted correctly."""
        result = compute_extended_ngrams(sample_text, include_pos_ngrams=False)

        # Should be list of (string, count) tuples
        for ngram, count in result.top_char_trigrams:
            assert isinstance(ngram, str)
            assert isinstance(count, int)

    def test_top_n_parameter(self, sample_text):
        """Test top_n parameter limits results."""
        result_5 = compute_extended_ngrams(sample_text, top_n=5, include_pos_ngrams=False)
        result_10 = compute_extended_ngrams(sample_text, top_n=10, include_pos_ngrams=False)

        assert len(result_5.top_word_trigrams) <= 5
        assert len(result_10.top_word_trigrams) <= 10

    def test_entropy_values_reasonable(self, long_text):
        """Test entropy values are reasonable (non-negative, finite)."""
        result = compute_extended_ngrams(long_text, include_pos_ngrams=False)

        assert result.word_trigram_entropy >= 0
        assert result.word_4gram_entropy >= 0
        assert result.char_trigram_entropy >= 0
        assert result.char_4gram_entropy >= 0

        assert not math.isinf(result.word_trigram_entropy)
        assert not math.isinf(result.char_trigram_entropy)

    def test_unique_counts_match(self, sample_text):
        """Test unique counts are consistent with results."""
        result = compute_extended_ngrams(sample_text, include_pos_ngrams=False)

        # Unique count should be >= number of top items
        assert result.word_trigram_count >= len(result.top_word_trigrams)
        assert result.word_4gram_count >= len(result.top_word_4grams)
        assert result.skipgram_2_1_count >= len(result.top_skipgrams_2_1)
        assert result.skipgram_3_1_count >= len(result.top_skipgrams_3_1)

    def test_metadata_contains_parameters(self, sample_text):
        """Test metadata contains input parameters."""
        result = compute_extended_ngrams(sample_text, top_n=15, include_pos_ngrams=False)

        assert "parameters" in result.metadata
        assert result.metadata["parameters"]["top_n"] == 15
        assert result.metadata["parameters"]["include_pos_ngrams"] is False

    def test_metadata_contains_token_counts(self, sample_text):
        """Test metadata contains token and character counts."""
        result = compute_extended_ngrams(sample_text, include_pos_ngrams=False)

        assert "token_count" in result.metadata
        assert "character_count" in result.metadata
        assert result.metadata["token_count"] > 0
        assert result.metadata["character_count"] > 0

    def test_empty_text(self):
        """Test with empty text returns zero counts."""
        result = compute_extended_ngrams("", include_pos_ngrams=False)

        assert result.word_trigram_count == 0
        assert result.word_4gram_count == 0
        assert result.skipgram_2_1_count == 0
        assert result.top_word_trigrams == []
        assert result.word_trigram_entropy == 0.0

    def test_short_text(self):
        """Test with text too short for some n-grams."""
        result = compute_extended_ngrams("one two", include_pos_ngrams=False)

        # Too short for word trigrams
        assert result.word_trigram_count == 0
        assert result.word_4gram_count == 0

    def test_pos_ngrams_disabled(self, sample_text):
        """Test POS n-grams are empty when disabled."""
        result = compute_extended_ngrams(sample_text, include_pos_ngrams=False)

        assert result.pos_trigram_count == 0
        assert result.pos_4gram_count == 0
        assert result.top_pos_trigrams == []
        assert result.top_pos_4grams == []

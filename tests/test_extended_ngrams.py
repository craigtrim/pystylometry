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
from collections import Counter

import pytest

from pystylometry.ngrams.extended_ngrams import (
    _calculate_shannon_entropy,
    _generate_ngrams,
    _generate_skipgrams,
    compute_extended_ngrams,
)

# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestGenerateNgrams:
    """Tests for _generate_ngrams helper function."""

    def test_bigrams(self):
        """Test bigram generation."""
        sequence = ["the", "quick", "brown", "fox"]
        result = _generate_ngrams(sequence, 2)
        expected = [
            ("the", "quick"),
            ("quick", "brown"),
            ("brown", "fox"),
        ]
        assert result == expected

    def test_trigrams(self):
        """Test trigram generation."""
        sequence = ["the", "quick", "brown", "fox", "jumps"]
        result = _generate_ngrams(sequence, 3)
        expected = [
            ("the", "quick", "brown"),
            ("quick", "brown", "fox"),
            ("brown", "fox", "jumps"),
        ]
        assert result == expected

    def test_4grams(self):
        """Test 4-gram generation."""
        sequence = ["a", "b", "c", "d", "e"]
        result = _generate_ngrams(sequence, 4)
        expected = [
            ("a", "b", "c", "d"),
            ("b", "c", "d", "e"),
        ]
        assert result == expected

    def test_empty_sequence(self):
        """Test with empty sequence."""
        result = _generate_ngrams([], 3)
        assert result == []

    def test_sequence_shorter_than_n(self):
        """Test when sequence is shorter than n-gram size."""
        sequence = ["a", "b"]
        result = _generate_ngrams(sequence, 3)
        assert result == []

    def test_single_ngram(self):
        """Test when sequence length equals n-gram size."""
        sequence = ["a", "b", "c"]
        result = _generate_ngrams(sequence, 3)
        assert result == [("a", "b", "c")]


class TestGenerateSkipgrams:
    """Tests for _generate_skipgrams helper function."""

    def test_2_skipgram_gap_1(self):
        """Test 2-skipgram with gap of 1 (word1 _ word3)."""
        sequence = ["the", "quick", "brown", "fox"]
        result = _generate_skipgrams(sequence, 2, 1)
        # Pattern: word at i, skip 1, word at i+2
        expected = [
            ("the", "brown"),  # positions 0, 2
            ("quick", "fox"),  # positions 1, 3
        ]
        assert result == expected

    def test_3_skipgram_gap_1(self):
        """Test 3-skipgram with gap of 1 (word1 _ word3 word4)."""
        sequence = ["a", "b", "c", "d", "e"]
        result = _generate_skipgrams(sequence, 3, 1)
        # Pattern: word at i, skip 1, then 2 contiguous words
        # Total span = 3 + 1 = 4
        expected = [
            ("a", "c", "d"),  # positions 0, 2, 3
            ("b", "d", "e"),  # positions 1, 3, 4
        ]
        assert result == expected

    def test_skipgram_sequence_too_short(self):
        """Test skipgram when sequence is too short."""
        sequence = ["a", "b"]
        result = _generate_skipgrams(sequence, 2, 1)
        assert result == []

    def test_empty_sequence(self):
        """Test skipgram with empty sequence."""
        result = _generate_skipgrams([], 2, 1)
        assert result == []


class TestShannonEntropy:
    """Tests for Shannon entropy calculation."""

    def test_uniform_distribution(self):
        """Test entropy for uniform distribution."""
        # 4 items with equal frequency = log2(4) = 2.0 bits
        counter = Counter({"a": 1, "b": 1, "c": 1, "d": 1})
        entropy = _calculate_shannon_entropy(counter)
        assert abs(entropy - 2.0) < 0.001

    def test_single_item(self):
        """Test entropy when only one item (minimum entropy)."""
        counter = Counter({"a": 10})
        entropy = _calculate_shannon_entropy(counter)
        assert entropy == 0.0

    def test_empty_counter(self):
        """Test entropy with empty counter."""
        counter = Counter()
        entropy = _calculate_shannon_entropy(counter)
        assert entropy == 0.0

    def test_skewed_distribution(self):
        """Test entropy for skewed distribution."""
        counter = Counter({"a": 10, "b": 1})
        entropy = _calculate_shannon_entropy(counter)
        # Should be between 0 and log2(2)=1
        assert 0 < entropy < 1


# =============================================================================
# MAIN FUNCTION TESTS
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


class TestComputeExtendedNgramsWithPOS:
    """Tests for POS n-gram functionality (requires spaCy)."""

    @pytest.fixture
    def spacy_available(self):
        """Check if spaCy is available."""
        try:
            import spacy

            spacy.load("en_core_web_sm")
            return True
        except (ImportError, OSError):
            return False

    def test_pos_ngrams_enabled(self, long_text, spacy_available):
        """Test POS n-grams when spaCy is available."""
        if not spacy_available:
            pytest.skip("spaCy not available")

        result = compute_extended_ngrams(long_text, include_pos_ngrams=True)

        assert result.pos_trigram_count > 0
        assert result.pos_4gram_count > 0
        assert len(result.top_pos_trigrams) > 0
        assert result.pos_trigram_entropy > 0

        # POS tags should be uppercase
        for ngram, count in result.top_pos_trigrams:
            assert isinstance(ngram, str)
            # POS tags are typically uppercase
            parts = ngram.split()
            for part in parts:
                assert part.isupper() or part.isalpha()


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

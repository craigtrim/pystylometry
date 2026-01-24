"""Tests for syntactic analysis metrics."""

import math

import pytest

# Skip all tests if spaCy not available
pytest.importorskip("spacy")

from pystylometry.syntactic import compute_pos_ratios, compute_sentence_stats


class TestPOSRatios:
    """Tests for Part-of-Speech ratio analysis."""

    def test_compute_pos_ratios_basic(self, sample_text):
        """Test POS ratio computation with sample text."""
        result = compute_pos_ratios(sample_text)

        # Verify all expected attributes exist
        assert hasattr(result, "noun_ratio")
        assert hasattr(result, "verb_ratio")
        assert hasattr(result, "adjective_ratio")
        assert hasattr(result, "adverb_ratio")
        assert hasattr(result, "noun_verb_ratio")
        assert hasattr(result, "adjective_noun_ratio")
        assert hasattr(result, "lexical_density")
        assert hasattr(result, "function_word_ratio")
        assert hasattr(result, "metadata")

        # Verify types
        assert isinstance(result.noun_ratio, float)
        assert isinstance(result.verb_ratio, float)
        assert isinstance(result.metadata, dict)

        # Verify metadata
        assert "model" in result.metadata
        assert "token_count" in result.metadata
        assert result.metadata["token_count"] > 0

    def test_compute_pos_ratios_constraints(self):
        """Test that POS ratios satisfy basic constraints."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_pos_ratios(text)

        # All ratios should be between 0 and 1
        assert 0.0 <= result.noun_ratio <= 1.0
        assert 0.0 <= result.verb_ratio <= 1.0
        assert 0.0 <= result.adjective_ratio <= 1.0
        assert 0.0 <= result.adverb_ratio <= 1.0
        assert 0.0 <= result.lexical_density <= 1.0
        assert 0.0 <= result.function_word_ratio <= 1.0

        # Lexical density + function word ratio should be <= 1.0
        # (they don't need to sum to 1.0 because there are other POS tags)
        assert result.lexical_density + result.function_word_ratio <= 1.0

    def test_compute_pos_ratios_empty(self):
        """Test POS ratios with empty text."""
        result = compute_pos_ratios("")

        # Should return NaN for empty text
        assert math.isnan(result.noun_ratio)
        assert math.isnan(result.verb_ratio)
        assert math.isnan(result.lexical_density)
        assert result.metadata["token_count"] == 0

    def test_compute_pos_ratios_noun_heavy(self):
        """Test POS ratios with noun-heavy text."""
        text = "The cat, the dog, the bird, the fish."
        result = compute_pos_ratios(text)

        # Nouns should dominate
        assert result.noun_ratio > result.verb_ratio
        assert result.noun_ratio > 0.3

    def test_compute_pos_ratios_verb_heavy(self):
        """Test POS ratios with verb-heavy text."""
        # Use clear imperative verbs with context to force verbal interpretation
        text = "Please run quickly. You should jump high. We must swim fast."
        result = compute_pos_ratios(text)

        # Verbs should be well represented (though not necessarily dominant
        # due to function words like "please", "you", "should", etc.)
        assert result.verb_ratio > 0.15  # At least 15% verbs

    def test_compute_pos_ratios_lexical_density(self):
        """Test lexical density calculation."""
        # High lexical density (lots of content words)
        text1 = "Beautiful flowers bloom quickly everywhere."
        result1 = compute_pos_ratios(text1)

        # Low lexical density (lots of function words)
        text2 = "It is the one that is in the box."
        result2 = compute_pos_ratios(text2)

        assert result1.lexical_density > result2.lexical_density

    def test_compute_pos_ratios_metadata_counts(self):
        """Test that metadata contains detailed POS counts."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_pos_ratios(text)

        # Check that count metadata exists
        assert "noun_count" in result.metadata
        assert "verb_count" in result.metadata
        assert "adjective_count" in result.metadata
        assert "adverb_count" in result.metadata

        # Verify counts are non-negative
        assert result.metadata["noun_count"] >= 0
        assert result.metadata["verb_count"] >= 0


class TestSentenceStats:
    """Tests for sentence-level statistics."""

    def test_compute_sentence_stats_basic(self, multi_sentence_text):
        """Test sentence statistics with multi-sentence text."""
        result = compute_sentence_stats(multi_sentence_text)

        # Verify all expected attributes exist
        assert hasattr(result, "mean_sentence_length")
        assert hasattr(result, "sentence_length_std")
        assert hasattr(result, "sentence_length_range")
        assert hasattr(result, "min_sentence_length")
        assert hasattr(result, "max_sentence_length")
        assert hasattr(result, "sentence_count")
        assert hasattr(result, "metadata")

        # Verify types
        assert isinstance(result.mean_sentence_length, float)
        assert isinstance(result.sentence_count, int)
        assert isinstance(result.metadata, dict)

        # Verify sentence count
        assert result.sentence_count > 0

    def test_compute_sentence_stats_constraints(self):
        """Test that sentence stats satisfy basic constraints."""
        text = "Short. This is longer. Longest sentence here."
        result = compute_sentence_stats(text)

        # Min <= Mean <= Max
        assert result.min_sentence_length <= result.mean_sentence_length
        assert result.mean_sentence_length <= result.max_sentence_length

        # Range = Max - Min
        assert result.sentence_length_range == (
            result.max_sentence_length - result.min_sentence_length
        )

        # Std dev >= 0
        assert result.sentence_length_std >= 0.0

    def test_compute_sentence_stats_empty(self):
        """Test sentence stats with empty text."""
        result = compute_sentence_stats("")

        assert math.isnan(result.mean_sentence_length)
        assert result.sentence_count == 0

    def test_compute_sentence_stats_single_sentence(self):
        """Test sentence stats with single sentence."""
        result = compute_sentence_stats("This is a single sentence.")

        assert result.sentence_count == 1
        assert result.sentence_length_std == 0.0
        assert result.sentence_length_range == 0

    def test_compute_sentence_stats_uniform_length(self):
        """Test sentence stats with uniform sentence lengths."""
        text = "Four words here now. Four words here now. Four words here now."
        result = compute_sentence_stats(text)

        # All sentences same length, so std dev should be 0
        assert result.sentence_length_std == 0.0
        assert result.sentence_length_range == 0
        assert result.min_sentence_length == result.max_sentence_length

    def test_compute_sentence_stats_varied_length(self):
        """Test sentence stats with varied sentence lengths."""
        text = "Short. This is a bit longer sentence. Very long sentence with many words."
        result = compute_sentence_stats(text)

        # Should have non-zero variation
        assert result.sentence_length_std > 0.0
        assert result.sentence_length_range > 0
        assert result.min_sentence_length < result.max_sentence_length

    def test_compute_sentence_stats_metadata(self):
        """Test that metadata contains expected fields."""
        text = "First sentence. Second sentence here."
        result = compute_sentence_stats(text)

        assert "model" in result.metadata
        assert "sentence_lengths" in result.metadata
        assert isinstance(result.metadata["sentence_lengths"], list)
        assert len(result.metadata["sentence_lengths"]) == result.sentence_count

    def test_compute_sentence_stats_long_text(self, long_text):
        """Test sentence stats with longer text."""
        result = compute_sentence_stats(long_text)

        # Should have multiple sentences
        assert result.sentence_count >= 3
        assert result.mean_sentence_length > 0

    def test_compute_sentence_stats_mean_calculation(self):
        """Test that mean sentence length is calculated correctly."""
        # Manually constructed text with known word counts
        # Sentence 1: 5 words
        # Sentence 2: 10 words (2x sentence 1)
        # Mean should be 7.5
        text = "This is five words here. This is a sentence with exactly ten words in it."
        result = compute_sentence_stats(text)

        assert result.sentence_count == 2
        # Allow small tolerance for floating point
        assert 7.0 <= result.mean_sentence_length <= 8.0


class TestSyntacticIntegration:
    """Integration tests for syntactic metrics."""

    def test_pos_and_sentence_stats_compatible(self):
        """Test that POS ratios and sentence stats work on same text."""
        text = "The quick brown fox jumps. The lazy dog sleeps."

        pos_result = compute_pos_ratios(text)
        sent_result = compute_sentence_stats(text)

        # Both should succeed
        assert pos_result.metadata["token_count"] > 0
        assert sent_result.sentence_count > 0

    def test_custom_spacy_model(self):
        """Test using custom spaCy model (if available)."""
        text = "Sample text for testing."

        # Default model should work
        result = compute_pos_ratios(text, model="en_core_web_sm")
        assert result.noun_ratio >= 0.0

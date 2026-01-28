"""Tests for syntactic analysis metrics."""

import math

import pytest

# Skip all tests if spaCy not available
pytest.importorskip("spacy")

from pystylometry.syntactic import compute_sentence_stats


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

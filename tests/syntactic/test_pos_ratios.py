"""Tests for syntactic analysis metrics."""

import math

import pytest

# Skip all tests if spaCy not available
pytest.importorskip("spacy")

from pystylometry.syntactic import compute_pos_ratios


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

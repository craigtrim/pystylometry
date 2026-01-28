"""Tests for sentence type classification (Issue #18)."""

import math

import pytest

from pystylometry.syntactic.sentence_types import compute_sentence_types

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def declarative_sentences():
    """Text with only declarative sentences."""
    return "The sky is blue. The grass is green. Water is wet."


@pytest.fixture
def simple_sentences():
    """Text with only simple sentences."""
    return "The cat sat. The dog ran. A bird flew."


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_text(self):
        """Test with empty text."""
        result = compute_sentence_types("")

        # Should return NaN for ratios
        assert math.isnan(result.simple_ratio)
        assert math.isnan(result.declarative_ratio)
        assert result.total_sentences == 0
        assert result.simple_count == 0

    def test_single_sentence(self):
        """Test with single sentence."""
        text = "The cat sat on the mat."
        result = compute_sentence_types(text)

        # Should have one sentence
        assert result.total_sentences == 1

        # One type should be 100%, others 0%
        assert result.simple_ratio == 1.0
        assert result.compound_ratio == 0.0
        assert result.declarative_ratio == 1.0

    def test_very_short_text(self):
        """Test with 2-3 sentences."""
        text = "Hello. How are you? Good."
        result = compute_sentence_types(text)

        assert result.total_sentences == 3
        assert (
            result.simple_count
            + result.compound_count
            + result.complex_count
            + result.compound_complex_count
            == 3
        )

    def test_homogeneous_structural(self, simple_sentences):
        """Test with all same structural type."""
        result = compute_sentence_types(simple_sentences)

        # All should be simple
        assert result.simple_ratio == 1.0
        assert result.compound_ratio == 0.0
        assert result.complex_ratio == 0.0
        assert result.compound_complex_ratio == 0.0

    def test_homogeneous_functional(self, declarative_sentences):
        """Test with all same functional type."""
        result = compute_sentence_types(declarative_sentences)

        # All should be declarative
        assert result.declarative_ratio == 1.0
        assert result.interrogative_ratio == 0.0
        assert result.imperative_ratio == 0.0
        assert result.exclamatory_ratio == 0.0

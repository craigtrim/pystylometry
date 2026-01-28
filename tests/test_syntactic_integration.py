"""Tests for syntactic analysis metrics."""

import pytest

# Skip all tests if spaCy not available
pytest.importorskip("spacy")

from pystylometry.syntactic import compute_pos_ratios, compute_sentence_stats


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

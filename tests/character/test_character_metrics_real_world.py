"""Tests for character-level metrics.

Related GitHub Issue:
    #12 - Character-Level Metrics
    https://github.com/craigtrim/pystylometry/issues/12
"""

import pytest

from pystylometry.character import compute_character_metrics

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def academic_text():
    """Academic-style text sample."""
    return (
        "Research demonstrates that lexical diversity correlates with "
        "authorial sophistication. Multiple studies confirm this finding."
    )


class TestCharacterMetricsRealWorld:
    """Tests with realistic text samples."""

    def test_academic_text(self, academic_text):
        """Test with academic prose."""
        result = compute_character_metrics(academic_text)

        # Academic text typically has longer words
        assert result.avg_word_length > 4.0

        # Should have reasonable letter frequency distribution
        assert len(result.letter_frequency) == 26

        # Should have multiple sentences
        assert result.metadata["total_sentences"] >= 2

    def test_complex_real_text(self):
        """Test with complex real-world text."""
        text = (
            "In 2024, NASA's Artemis program aims to return humans to the Moon. "
            "The mission involves multiple stages: launch, orbit, descent, and return. "
            "Why? Because exploration (and science!) matters."
        )
        result = compute_character_metrics(text)

        # Verify comprehensive analysis
        assert result.avg_word_length > 0
        assert result.punctuation_variety > 5
        assert result.digit_count > 0
        assert result.uppercase_ratio > 0
        # Simple sentence segmentation splits on every .!? delimiter
        # Text has: . . ? ! . = 5 sentence delimiters
        assert result.metadata["total_sentences"] == 5

    def test_social_media_style(self):
        """Test with informal social media style text."""
        text = "OMG!!! This is AMAZING!!! Can't believe it... #wow"
        result = compute_character_metrics(text)

        # High punctuation density due to multiple exclamation marks
        assert result.punctuation_density > 20.0

        # High uppercase ratio due to OMG and AMAZING
        assert result.uppercase_ratio > 0.2

    def test_technical_documentation(self):
        """Test with technical documentation style."""
        text = (
            "Function compute_metrics(text: str) -> Result:\n"
            "    Calculate metrics for input text.\n"
            "    Returns: CharacterMetricsResult object."
        )
        result = compute_character_metrics(text)

        # Should handle code-like text
        assert result.avg_word_length > 0
        assert result.metadata["total_sentences"] >= 1

        # Should detect punctuation in code
        assert result.punctuation_variety > 3

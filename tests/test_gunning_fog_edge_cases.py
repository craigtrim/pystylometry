"""Comprehensive tests for Gunning Fog Index computation."""

from pystylometry.readability import compute_gunning_fog

# Try to import spaCy to determine if enhanced mode tests can run
try:
    import spacy

    # Try to load the model to see if it's downloaded
    try:
        spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        # spaCy installed but model not downloaded
        SPACY_AVAILABLE = False
except ImportError:
    SPACY_AVAILABLE = False


class TestGunningFogEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test empty string input."""
        import math

        result = compute_gunning_fog("")

        # After NaN fix: empty input returns NaN, not 0.0
        assert math.isnan(result.fog_index)
        assert math.isnan(result.grade_level)
        assert result.metadata["sentence_count"] == 0
        assert result.metadata["word_count"] == 0
        assert result.metadata["complex_word_count"] == 0
        assert result.metadata["complex_word_percentage"] == 0.0
        assert result.metadata["average_words_per_sentence"] == 0.0
        assert not result.metadata["reliable"]

    def test_whitespace_only(self):
        """Test string with only whitespace."""
        import math

        result = compute_gunning_fog("   \n\t  ")

        # After NaN fix: whitespace-only input returns NaN, not 0.0
        assert math.isnan(result.fog_index)
        assert math.isnan(result.grade_level)
        assert not result.metadata["reliable"]

    def test_very_simple_text(self):
        """Test extremely simple text."""
        text = "Go. Run. Stop. Hi."
        result = compute_gunning_fog(text)

        # Should be low grade level
        assert result.grade_level <= 5
        assert result.metadata["complex_word_count"] == 0

    def test_single_word(self):
        """Test single word."""
        result = compute_gunning_fog("Hello")

        assert result.metadata["word_count"] == 1
        assert result.metadata["sentence_count"] >= 0
        assert not result.metadata["reliable"]

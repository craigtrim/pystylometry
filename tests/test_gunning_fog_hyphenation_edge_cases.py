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


class TestGunningFogHyphenationEdgeCases:
    """Test hyphenation exclusion edge cases."""

    def test_prefix_hyphenation(self):
        """Prefix-hyphenated words should be excluded."""
        # "anti-establishment" - hyphenated so excluded
        # Current logic excludes ALL hyphenated words
        text = "The anti-establishment and pro-democracy revolutionary groups grew."
        result = compute_gunning_fog(text)

        # Documents current behavior: all hyphenated excluded
        # "revolutionary" = 5 syllables, complex
        # "movements" = 2 syllables, NOT complex
        assert result.metadata["complex_word_count"] == 1  # only "revolutionary"

    def test_hyphen_in_numbers(self):
        """Hyphenated numbers should be handled."""
        text = "Twenty-three and forty-five are numbers."
        result = compute_gunning_fog(text)

        # Should not crash; hyphenated numbers excluded from complex
        assert result.fog_index >= 0
        # Hyphenated compounds excluded
        assert result.metadata["complex_word_count"] == 0

    def test_multiple_hyphens(self):
        """Test words with multiple hyphens."""
        text = "The state-of-the-art mother-in-law solution."
        result = compute_gunning_fog(text)

        # All hyphenated words excluded
        # "solution" = 3 syllables, IS complex
        assert result.metadata["complex_word_count"] == 1  # "solution"

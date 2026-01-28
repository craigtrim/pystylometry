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


class TestGunningFogUnicode:
    """Test Unicode character handling."""

    def test_unicode_letters(self):
        """Test that Unicode letters are handled."""
        text = "Café résumé naïve façade."
        result = compute_gunning_fog(text)

        # Should complete without error
        assert result.fog_index is not None
        assert result.grade_level >= 0

    def test_non_latin_scripts(self):
        """Test handling of non-Latin scripts."""
        # Greek
        text_greek = "Γεια σου κόσμε"
        result = compute_gunning_fog(text_greek)
        assert result.metadata["word_count"] > 0

        # Cyrillic
        text_cyrillic = "Привет мир"
        result = compute_gunning_fog(text_cyrillic)
        assert result.metadata["word_count"] > 0

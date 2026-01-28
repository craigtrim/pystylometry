"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARIUnicode:
    """Test Unicode character handling."""

    def test_unicode_letters(self):
        """Test that Unicode letters are handled."""
        text = "Café résumé naïve façade."
        result = compute_ari(text)

        # Should complete without error
        assert result.ari_score is not None
        assert result.grade_level >= 0

    def test_non_latin_scripts(self):
        """Test handling of non-Latin scripts."""
        # Greek
        text_greek = "Γεια σου κόσμε"
        result = compute_ari(text_greek)
        assert result.metadata["word_count"] > 0

        # Cyrillic
        text_cyrillic = "Привет мир"
        result = compute_ari(text_cyrillic)
        assert result.metadata["word_count"] > 0

    def test_numbers_counted_as_characters(self):
        """Test that numbers are counted as characters."""
        text = "The year 2024 has 365 days."
        result = compute_ari(text)

        # Numbers should be included in character count
        # "Theyear2024has365days" = letters + digits
        assert result.metadata["character_count"] > 15

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


class TestGunningFogSpecialCases:
    """Test special input cases."""

    def test_urls_and_emails(self):
        """Test handling of URLs and email addresses."""
        text = "Visit https://example.com or email user@example.com for info."
        result = compute_gunning_fog(text)

        # Should complete without error
        assert result.fog_index is not None
        assert result.grade_level >= 0

    def test_numbers_in_text(self):
        """Test handling of numbers."""
        text = "In 2023, the company had 500 employees and revenue of $1,000,000."
        result = compute_gunning_fog(text)

        # Should complete without error
        assert result.fog_index is not None

    def test_contractions(self):
        """Test handling of contractions."""
        text = "I can't believe it's already over. They're leaving soon."
        result = compute_gunning_fog(text)

        # Should handle contractions naturally
        assert result.metadata["word_count"] >= 1
        assert result.grade_level >= 0

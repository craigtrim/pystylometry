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


class TestGunningFogRounding:
    """Test rounding behavior and boundary values."""

    def test_grade_level_is_numeric(self):
        """Verify grade level is always a number (float for mean across chunks)."""
        texts = [
            "The cat sat on the mat.",
            "A very long and complex sentence with many subordinate clauses.",
            "Go.",
        ]

        for text in texts:
            result = compute_gunning_fog(text)
            assert isinstance(result.grade_level, (int, float))

    def test_lower_bound_clamping(self):
        """Test that very simple text is clamped to grade 0."""
        simple = "Go. Run. Stop."
        result = compute_gunning_fog(simple)

        assert result.grade_level >= 0

    def test_upper_bound_clamping(self):
        """Test that very high fog index is clamped to grade 20."""
        # Create extremely complex text with very long words and long sentences
        complex_words = [
            "antidisestablishmentarianism",
            "supercalifragilisticexpialidocious",
            "pneumonoultramicroscopicsilicovolcanoconiosis",
        ]
        # One very long sentence
        text = " ".join(complex_words * 50) + "."

        result = compute_gunning_fog(text)
        assert result.grade_level <= 20

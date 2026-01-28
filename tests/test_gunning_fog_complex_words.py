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


class TestGunningFogComplexWords:
    """Test complex word identification."""

    def test_simple_words_not_complex(self):
        """Test that simple words are not counted as complex."""
        text = "The cat sat on the mat."
        result = compute_gunning_fog(text)

        assert result.metadata["complex_word_count"] == 0
        assert result.metadata["complex_word_percentage"] == 0.0

    def test_polysyllabic_words_complex(self):
        """Test that 3+ syllable words are complex."""
        text = "The situation is unfortunate."
        result = compute_gunning_fog(text)

        # "situation" (4 syllables) and "unfortunate" (4 syllables) should be complex
        assert result.metadata["complex_word_count"] >= 2

    def test_hyphenated_words_excluded(self):
        """Test that hyphenated compounds are not counted as complex."""
        text = "The well-known twenty-first-century state-of-the-art solution."
        result = compute_gunning_fog(text)

        # Hyphenated words should be excluded from complex count
        # Even though they have 3+ syllables
        assert result.metadata["complex_word_count"] == 1  # Only "solution" (3 syllables)

    def test_proper_nouns_excluded(self):
        """Test that proper nouns (capitalized) are excluded."""
        text = "The American Revolution began in seventeen seventy-five."
        result = compute_gunning_fog(text)

        # "American" (4 syllables) and "Revolution" (4 syllables) should be excluded
        # Only "seventeen" (3 syllables) should count
        assert result.metadata["complex_word_count"] <= 1

    def test_inflectional_suffixes(self):
        """Test handling of -es, -ed, -ing suffixes."""
        # Words with suffixes that still have 3+ syllables in base
        text = "The running jumping skipping children were playing happily."
        result = compute_gunning_fog(text)

        # "running" (2 syllables, -1 for -ing = 1, not complex)
        # "jumping" (2 syllables, -1 for -ing = 1, not complex)
        # "skipping" (2 syllables, -1 for -ing = 1, not complex)
        # "children" (2 syllables, not complex)
        # "playing" (2 syllables, -1 for -ing = 1, not complex)
        # "happily" (3 syllables, complex)
        assert result.metadata["complex_word_count"] >= 1

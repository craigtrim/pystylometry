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


class TestGunningFogSuffixEdgeCases:
    """Test suffix handling edge cases."""

    def test_silent_ed_suffix(self):
        """Words where -ed adds no syllable."""
        # "complicated" = 4 syllables, -ed is not a separate syllable
        # Subtracting 1 would make it 3, still complex
        # "elevated" = 4 syllables, subtracting 1 = 3, borderline
        text = "The elevated platform was complicated."
        result = compute_gunning_fog(text)

        # Both should be complex (4 syllables each, adjusted to 3)
        assert result.metadata["complex_word_count"] >= 2

    def test_ing_suffix_base_word_boundary(self):
        """Test -ing words at complexity boundary."""
        # "beginning" = 3 syllables, -1 adjustment = 2, not complex
        # "interesting" = 3 syllables, -1 adjustment = 2, not complex
        text = "The beginning was interesting and overwhelming."
        result = compute_gunning_fog(text)

        # "overwhelming" = 4 syl (3 after adjustment, IS complex)
        # "beginning" and "interesting" = 3 syl each (2 after adjustment, NOT complex)
        assert result.metadata["complex_word_count"] >= 1

    def test_es_suffix_handling(self):
        """Test -es suffix handling."""
        # "boxes" = 2 syllables (box + es)
        # "matches" = 2 syllables (match + es)
        # "reaches" = 2 syllables (reach + es)
        text = "The boxes and matches and reaches were counted."
        result = compute_gunning_fog(text)

        # All are 2 syllables, -1 adjustment = 1, not complex
        assert result.metadata["complex_word_count"] == 0

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


class TestGunningFogSentenceInitialWords:
    """Test handling of sentence-initial complex words."""

    def test_sentence_initial_complex_word_counted(self):
        """Sentence-initial complex words should be counted."""
        # "Unfortunately" is complex (5 syllables) and starts sentences
        text = "Unfortunately, this happened. Unfortunately, that happened too."
        result = compute_gunning_fog(text)

        # After fix: Sentence-initial complex words should be counted
        assert result.metadata["complex_word_count"] >= 2, (
            "Sentence-initial complex words should be counted"
        )

    def test_mid_sentence_proper_noun_excluded(self):
        """Only true proper nouns (mid-sentence caps) should be excluded."""
        text = "I visited Philadelphia and Massachusetts last summer."
        result = compute_gunning_fog(text)

        # "Philadelphia" (5 syl) and "Massachusetts" (5 syl) are proper nouns
        # and correctly excluded
        assert result.metadata["complex_word_count"] == 0

    def test_sentence_initial_vs_proper_noun(self):
        """Test distinction between sentence-initial and proper nouns."""
        # Sentence-initial complex word
        text1 = "Complicated situations arise frequently."
        result1 = compute_gunning_fog(text1)

        # Mid-sentence capitalized word
        text2 = "The big American cat was here."
        result2 = compute_gunning_fog(text2)

        # Sentence-initial should be counted
        assert result1.metadata["complex_word_count"] >= 2  # "Complicated", "situations"

        # "American" (4 syl) behavior is mode-dependent:
        # - Basic mode: Excluded via capitalization heuristic (treats as proper noun)
        # - Enhanced mode: Counted as complex (correctly identified as adjective by spaCy)
        if result2.metadata.get("mode") == "enhanced":
            assert result2.metadata["complex_word_count"] == 1  # "American" (ADJ)
        else:
            assert result2.metadata["complex_word_count"] == 0  # Excluded by heuristic

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


class TestGunningFogFormula:
    """Test formula correctness."""

    def test_formula_components(self):
        """Verify formula components are calculated correctly."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_gunning_fog(text)

        avg_words = result.metadata["average_words_per_sentence"]
        complex_pct = result.metadata["complex_word_percentage"]

        # Manual calculation: Fog = 0.4 × (avg_words + complex_pct)
        expected_fog = 0.4 * (avg_words + complex_pct)

        # Should match within floating point precision
        assert abs(result.fog_index - expected_fog) < 0.0001

    def test_longer_sentences_increase_score(self):
        """Test that longer sentences increase fog index."""
        short_sentences = "The cat sat. The dog ran. The bird flew."
        long_sentence = (
            "The cat sat on the mat while the dog ran around the yard and the bird flew overhead."
        )

        result_short = compute_gunning_fog(short_sentences)
        result_long = compute_gunning_fog(long_sentence)

        # Longer average sentence length should produce higher score
        assert (
            result_long.metadata["average_words_per_sentence"]
            > result_short.metadata["average_words_per_sentence"]
        )

    def test_complex_words_increase_score(self):
        """Test that complex words increase fog index."""
        simple = "The cat sat on the mat and ate the food."
        complex_text = "The situation necessitated extraordinary consideration."

        result_simple = compute_gunning_fog(simple)
        result_complex = compute_gunning_fog(complex_text)

        # More complex words should produce higher percentage
        assert (
            result_complex.metadata["complex_word_percentage"]
            > result_simple.metadata["complex_word_percentage"]
        )

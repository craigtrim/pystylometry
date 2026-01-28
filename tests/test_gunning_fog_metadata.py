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


class TestGunningFogMetadata:
    """Test metadata structure and consistency."""

    def test_metadata_keys_consistent(self):
        """Verify all metadata keys are present regardless of input."""
        test_cases = [
            "",  # Empty
            "Hello",  # Single word
            "The cat sat on the mat.",  # Simple sentence
            " ".join(["word"] * 200) + ".",  # Long text
        ]

        expected_keys = {
            "sentence_count",
            "word_count",
            "complex_word_count",
            "complex_word_percentage",
            "average_words_per_sentence",
            "reliable",
        }

        for text in test_cases:
            result = compute_gunning_fog(text)
            # Use subset check - implementation may include additional keys
            # (mode, proper_noun_detection, inflection_handling, spacy_model, etc.)
            assert expected_keys.issubset(set(result.metadata.keys()))

    def test_metadata_values_sensible(self):
        """Test that metadata values are within sensible ranges."""
        text = "The quick brown fox jumps over the lazy dog. The end."
        result = compute_gunning_fog(text)

        # Counts should be non-negative
        assert result.metadata["sentence_count"] >= 0
        assert result.metadata["word_count"] >= 0
        assert result.metadata["complex_word_count"] >= 0

        # Percentages should be 0-100
        assert 0 <= result.metadata["complex_word_percentage"] <= 100

        # Average should be non-negative
        assert result.metadata["average_words_per_sentence"] >= 0

        # Reliable should be boolean
        assert isinstance(result.metadata["reliable"], bool)

    def test_complex_word_percentage_calculation(self):
        """Verify complex word percentage is calculated correctly."""
        # 10 words, 2 complex
        text = "The situation is unfortunate but manageable today."
        result = compute_gunning_fog(text)

        if result.metadata["word_count"] > 0:
            expected_pct = (
                result.metadata["complex_word_count"] / result.metadata["word_count"]
            ) * 100
            assert abs(result.metadata["complex_word_percentage"] - expected_pct) < 0.01

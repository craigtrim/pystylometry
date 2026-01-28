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


class TestGunningFogBasic:
    """Test basic Gunning Fog functionality."""

    def test_simple_sentence(self):
        """Test single simple sentence."""
        text = "The cat sat on the mat."
        result = compute_gunning_fog(text)

        assert isinstance(result.fog_index, float)
        assert isinstance(result.grade_level, (int, float))  # Float for chunked mean
        assert result.grade_level >= 0
        assert result.grade_level <= 20
        assert not result.metadata["reliable"]  # < 100 words and < 3 sentences

    def test_expected_values(self):
        """Test known expected values for calibration."""
        # Simple sentence with no complex words
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_gunning_fog(text)

        # Manual calculation:
        # Words: 9, Sentences: 1
        # Avg words/sentence: 9
        # Complex words: 0 (all simple 1-syllable words)
        # Complex %: 0
        # Fog = 0.4 × (9 + 0) = 3.6
        assert abs(result.fog_index - 3.6) < 0.1  # Allow small tolerance
        assert result.grade_level == 4  # rounds to 4
        assert not result.metadata["reliable"]

    def test_reliable_text(self):
        """Test text that meets reliability threshold."""
        # Generate text with 100+ words and 3+ sentences
        words = ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        sentences = [" ".join(words) + "." for _ in range(12)]  # 12 sentences, 108 words
        text = " ".join(sentences)

        result = compute_gunning_fog(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] >= 100
        assert result.metadata["sentence_count"] >= 3

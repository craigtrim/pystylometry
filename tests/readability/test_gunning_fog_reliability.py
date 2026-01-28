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


class TestGunningFogReliability:
    """Test reliability flag behavior."""

    def test_reliability_threshold_words(self):
        """Test reliability requires 100+ words."""
        # 99 words with 3 sentences
        text_99 = (
            " ".join(["word"] * 33)
            + ". "
            + " ".join(["word"] * 33)
            + ". "
            + " ".join(["word"] * 33)
            + "."
        )
        result = compute_gunning_fog(text_99)
        assert not result.metadata["reliable"]
        assert result.metadata["word_count"] == 99

        # 100 words with 3 sentences
        text_100 = (
            " ".join(["word"] * 34)
            + ". "
            + " ".join(["word"] * 33)
            + ". "
            + " ".join(["word"] * 33)
            + "."
        )
        result = compute_gunning_fog(text_100)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] == 100

    def test_reliability_threshold_sentences(self):
        """Test reliability requires 3+ sentences."""
        # 100+ words but only 2 sentences
        text_2_sent = " ".join(["word"] * 50) + ". " + " ".join(["word"] * 50) + "."
        result = compute_gunning_fog(text_2_sent)
        assert not result.metadata["reliable"]

        # 100+ words with 3 sentences
        text_3_sent = (
            " ".join(["word"] * 34)
            + ". "
            + " ".join(["word"] * 34)
            + ". "
            + " ".join(["word"] * 34)
            + "."
        )
        result = compute_gunning_fog(text_3_sent)
        assert result.metadata["reliable"]

    def test_reliability_flag_type(self):
        """Verify reliability is always a boolean."""
        texts = ["", "Short.", " ".join(["word"] * 200) + "."]

        for text in texts:
            result = compute_gunning_fog(text)
            assert isinstance(result.metadata["reliable"], bool)

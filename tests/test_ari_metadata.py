"""Comprehensive tests for Automated Readability Index (ARI) computation."""

from pystylometry.readability import compute_ari


class TestARIMetadata:
    """Test metadata structure and consistency."""

    def test_metadata_keys_consistent(self):
        """Verify all required metadata keys are present regardless of input."""
        test_cases = [
            "",  # Empty
            "Hello",  # Single word
            "The cat sat on the mat.",  # Simple sentence
            " ".join(["word"] * 200) + ".",  # Long text
        ]

        required_keys = {
            "sentence_count",
            "word_count",
            "character_count",
            "characters_per_word",
            "words_per_sentence",
            "reliable",
        }

        for text in test_cases:
            result = compute_ari(text)
            # Check that all required keys are present (may have additional keys)
            assert required_keys.issubset(set(result.metadata.keys()))

    def test_metadata_values_sensible(self):
        """Test that metadata values are within sensible ranges."""
        text = "The quick brown fox jumps over the lazy dog. The end."
        result = compute_ari(text)

        # Counts should be non-negative
        assert result.metadata["sentence_count"] >= 0
        assert result.metadata["word_count"] >= 0
        assert result.metadata["character_count"] >= 0

        # Ratios should be non-negative
        assert result.metadata["characters_per_word"] >= 0
        assert result.metadata["words_per_sentence"] >= 0

        # Reliable should be boolean
        assert isinstance(result.metadata["reliable"], bool)

    def test_character_count_alphanumeric_only(self):
        """Verify character count includes only alphanumeric characters."""
        text = "Hello123 World!!! Test@example.com"
        result = compute_ari(text)

        # Should count only: Hello123WorldTestexamplecom
        expected_chars = len("Hello123WorldTestexamplecom")
        assert result.metadata["character_count"] == expected_chars

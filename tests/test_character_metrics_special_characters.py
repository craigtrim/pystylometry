"""Tests for character-level metrics.

Related GitHub Issue:
    #12 - Character-Level Metrics
    https://github.com/craigtrim/pystylometry/issues/12
"""

from pystylometry.character import compute_character_metrics

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


class TestCharacterMetricsSpecialCharacters:
    """Tests for handling special characters and formatting."""

    def test_contractions_with_apostrophes(self):
        """Test handling of contractions."""
        text = "Don't can't won't shouldn't."
        result = compute_character_metrics(text)

        # Apostrophes should be counted as punctuation
        assert result.punctuation_variety >= 2  # apostrophe and period

    def test_hyphenated_words(self):
        """Test handling of hyphenated words."""
        text = "Well-known state-of-the-art."
        result = compute_character_metrics(text)

        # Hyphens should be counted as punctuation
        assert result.punctuation_variety >= 2  # hyphen and period

    def test_multiple_sentence_delimiters(self):
        """Test text with different sentence endings."""
        text = "Question? Statement. Exclamation!"
        result = compute_character_metrics(text)

        # Should detect 3 sentences
        assert result.metadata["total_sentences"] == 3

        # Should have 3 types of punctuation
        assert result.punctuation_variety >= 3

    def test_special_punctuation(self):
        """Test special punctuation marks."""
        text = "Em-dash — or ellipsis… both work."
        result = compute_character_metrics(text)

        # Should count em-dash and ellipsis
        assert result.punctuation_variety >= 3

    def test_mixed_quotes(self):
        """Test different quote styles."""
        text = "\"Double quotes\" and 'single quotes' work."
        result = compute_character_metrics(text)

        # Should detect quote marks as punctuation
        assert result.metadata["total_punctuation"] > 0

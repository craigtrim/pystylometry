"""Comprehensive tests for token normalization."""

from pystylometry._normalize import (
    normalize_for_readability,
)


class TestNormalizeForReadability:
    """Test normalize_for_readability function."""

    def test_clean_text(self):
        """Test with clean, simple text."""
        tokens = ["The", "cat", "sat", "on", "the", "mat"]
        result = normalize_for_readability(tokens)
        assert result == ["The", "cat", "sat", "on", "the", "mat"]

    def test_filters_numbers(self):
        """Test that numbers are filtered out."""
        tokens = ["The", "year", "2026", "had", "365", "days"]
        result = normalize_for_readability(tokens)
        assert result == ["The", "year", "had", "days"]

    def test_filters_emails(self):
        """Test that email addresses are filtered out."""
        tokens = ["Email", "test@example.com", "for", "help"]
        result = normalize_for_readability(tokens)
        assert result == ["Email", "for", "help"]

    def test_filters_urls(self):
        """Test that URLs are filtered out."""
        tokens = ["Visit", "http://example.com", "for", "more"]
        result = normalize_for_readability(tokens)
        assert result == ["Visit", "for", "more"]

    def test_filters_punctuation(self):
        """Test that pure punctuation is filtered out."""
        tokens = ["Hello", ",", "world", "!"]
        result = normalize_for_readability(tokens)
        assert result == ["Hello", "world"]

    def test_preserves_contractions(self):
        """Test that contractions are preserved."""
        tokens = ["I", "don't", "think", "we're", "ready"]
        result = normalize_for_readability(tokens)
        assert result == ["I", "don't", "think", "we're", "ready"]

    def test_preserves_hyphenated_words(self):
        """Test that hyphenated words are preserved."""
        tokens = ["The", "co-operate", "plan", "failed"]
        result = normalize_for_readability(tokens)
        assert result == ["The", "co-operate", "plan", "failed"]

    def test_real_world_mixed(self):
        """Test with realistic mixed input."""
        tokens = [
            "The",
            "year",
            "2026",
            "Dr",
            "Smith",
            "works",
            "at",
            "test@example.com",
            "and",
            "earns",
            "$99.99",
            "daily",
        ]
        result = normalize_for_readability(tokens)
        assert result == ["The", "year", "Dr", "Smith", "works", "at", "and", "earns", "daily"]

    def test_abbreviations(self):
        """Test abbreviation handling."""
        # Tokens might include "U.S." as separate tokens like "U", ".", "S", "."
        # OR as a single token "U.S." depending on tokenizer
        # Our function should filter out the punctuation tokens
        tokens = ["Dr", "Smith", "works", "at", "U", ".", "S", ".", "Steel"]
        result = normalize_for_readability(tokens)
        assert result == ["Dr", "Smith", "works", "at", "U", "S", "Steel"]

    def test_special_characters(self):
        """Test special character handling."""
        tokens = ["The", "company", "uses", "C++", "and", "Python"]
        result = normalize_for_readability(tokens)
        assert result == ["The", "company", "uses", "and", "Python"]

    def test_empty_input(self):
        """Test empty token list."""
        tokens = []
        result = normalize_for_readability(tokens)
        assert result == []

    def test_all_invalid_tokens(self):
        """Test when all tokens are invalid."""
        tokens = ["123", "456", "...", "!!!", "@@@"]
        result = normalize_for_readability(tokens)
        assert result == []

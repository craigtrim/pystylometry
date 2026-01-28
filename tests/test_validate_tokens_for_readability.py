"""Comprehensive tests for token normalization."""

from pystylometry._normalize import (
    validate_tokens_for_readability,
)


class TestValidateTokensForReadability:
    """Test validate_tokens_for_readability diagnostic function."""

    def test_separates_valid_invalid(self):
        """Test that valid and invalid tokens are properly separated."""
        tokens = ["Hello", "123", "world", "test@example.com", "Python"]
        valid, invalid = validate_tokens_for_readability(tokens)
        assert valid == ["Hello", "world", "Python"]
        assert invalid == ["123", "test@example.com"]

    def test_all_valid(self):
        """Test when all tokens are valid."""
        tokens = ["The", "quick", "brown", "fox"]
        valid, invalid = validate_tokens_for_readability(tokens)
        assert valid == ["The", "quick", "brown", "fox"]
        assert invalid == []

    def test_all_invalid(self):
        """Test when all tokens are invalid."""
        tokens = ["123", "456", "...", "test@example.com"]
        valid, invalid = validate_tokens_for_readability(tokens)
        assert valid == []
        assert invalid == ["123", "456", "...", "test@example.com"]

    def test_empty_input(self):
        """Test empty token list."""
        tokens = []
        valid, invalid = validate_tokens_for_readability(tokens)
        assert valid == []
        assert invalid == []

    def test_contractions_and_hyphens_valid(self):
        """Test that contractions and hyphenated words are considered valid."""
        tokens = ["don't", "re-enter", "123", "test@example.com"]
        valid, invalid = validate_tokens_for_readability(tokens)
        assert "don't" in valid
        assert "re-enter" in valid
        assert "123" in invalid
        assert "test@example.com" in invalid

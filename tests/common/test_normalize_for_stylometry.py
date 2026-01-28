"""Comprehensive tests for token normalization."""

from pystylometry._normalize import (
    normalize_for_stylometry,
)


class TestNormalizeForStylometry:
    """Test normalize_for_stylometry function."""

    def test_preserves_contractions_by_default(self):
        """Test that contractions are preserved by default."""
        tokens = ["I", "don't", "think", "so"]
        result = normalize_for_stylometry(tokens)
        assert "don't" in result

    def test_preserves_hyphens_by_default(self):
        """Test that hyphenated words are preserved by default."""
        tokens = ["re-enter", "the", "building"]
        result = normalize_for_stylometry(tokens)
        assert "re-enter" in result

    def test_can_exclude_contractions(self):
        """Test that contractions can be excluded."""
        tokens = ["I", "don't", "think", "so"]
        result = normalize_for_stylometry(tokens, preserve_contractions=False)
        assert "don't" not in result

    def test_can_exclude_hyphens(self):
        """Test that hyphenated words can be excluded."""
        tokens = ["re-enter", "the", "building"]
        result = normalize_for_stylometry(tokens, preserve_hyphens=False)
        assert "re-enter" not in result

    def test_min_length_filter(self):
        """Test minimum length filtering."""
        tokens = ["I", "am", "a", "test"]
        result = normalize_for_stylometry(tokens, min_length=2)
        assert result == ["am", "test"]

    def test_filters_emails_and_urls(self):
        """Test that emails and URLs are still filtered."""
        tokens = ["Visit", "www.example.com", "or", "email", "test@example.com"]
        result = normalize_for_stylometry(tokens)
        assert "www.example.com" not in result
        assert "test@example.com" not in result
        assert result == ["Visit", "or", "email"]

    def test_requires_alpha_char(self):
        """Test that tokens must contain at least one alphabetic character."""
        tokens = ["hello", "123", "...", "world"]
        result = normalize_for_stylometry(tokens)
        assert result == ["hello", "world"]

"""Comprehensive tests for token normalization."""

from pystylometry._normalize import (
    is_word_token,
)


class TestIsWordToken:
    """Test is_word_token validation function."""

    def test_valid_simple_words(self):
        """Test that simple alphabetic words are recognized as valid."""
        assert is_word_token("hello")
        assert is_word_token("world")
        assert is_word_token("Python")
        assert is_word_token("HELLO")

    def test_valid_contractions(self):
        """Test that contractions with apostrophes are valid."""
        assert is_word_token("don't")
        assert is_word_token("we're")
        assert is_word_token("it's")
        assert is_word_token("can't")
        # Note: Archaic contractions like "'tis" start with apostrophe
        # and are rejected by our strict validation (must start with letter)
        assert not is_word_token("'tis")

    def test_valid_hyphenated_words(self):
        """Test that hyphenated compound words are valid."""
        assert is_word_token("co-operate")
        assert is_word_token("re-enter")
        assert is_word_token("self-education")
        assert is_word_token("well-known")

    def test_valid_mixed_apostrophe_hyphen(self):
        """Test words with both apostrophes and hyphens."""
        # Edge case: possessive hyphenated word
        # Note: "mother-in-law's" would need special handling
        # For now, we test simpler cases
        assert is_word_token("re-enter")  # hyphen
        assert is_word_token("don't")  # apostrophe

    def test_invalid_numbers(self):
        """Test that numbers are rejected."""
        assert not is_word_token("123")
        assert not is_word_token("2026")
        assert not is_word_token("3.14")
        assert not is_word_token("99.99")

    def test_invalid_emails(self):
        """Test that email addresses are rejected."""
        assert not is_word_token("test@example.com")
        assert not is_word_token("user@domain.org")

    def test_invalid_urls(self):
        """Test that URLs are rejected."""
        assert not is_word_token("http://example.com")
        assert not is_word_token("www.example.com")

    def test_invalid_punctuation(self):
        """Test that pure punctuation is rejected."""
        assert not is_word_token("...")
        assert not is_word_token("!!!")
        assert not is_word_token("???")
        assert not is_word_token("—")
        assert not is_word_token(",")

    def test_invalid_mixed_alphanumeric(self):
        """Test that mixed alphanumeric tokens are rejected."""
        assert not is_word_token("test123")
        assert not is_word_token("123test")
        assert not is_word_token("C++")  # Programming language
        assert not is_word_token("O'Brian123")  # ends with number

    def test_invalid_leading_trailing_punctuation(self):
        """Test that words with leading/trailing punctuation are rejected."""
        assert not is_word_token("-hello")  # Leading hyphen
        assert not is_word_token("hello-")  # Trailing hyphen
        assert not is_word_token("'hello")  # Leading apostrophe
        # Trailing apostrophe (ok in some cases, but we're strict)
        assert not is_word_token("hello'")
        # Note: This might be too strict for possessives like "dogs'"
        # but for readability, we want clean words

    def test_edge_case_empty(self):
        """Test empty string handling."""
        assert not is_word_token("")

    def test_edge_case_single_char(self):
        """Test single character words."""
        assert is_word_token("I")
        assert is_word_token("a")
        assert not is_word_token("1")
        assert not is_word_token("-")

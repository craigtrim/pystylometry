"""Comprehensive tests for token normalization."""

from pystylometry._normalize import (
    clean_for_syllable_counting,
)


class TestCleanForSyllableCounting:
    """Test clean_for_syllable_counting function."""

    def test_removes_urls(self):
        """Test URL removal."""
        text = "Visit http://example.com for more info"
        result = clean_for_syllable_counting(text)
        assert "http://example.com" not in result
        assert "Visit" in result
        assert "for more info" in result

    def test_removes_emails(self):
        """Test email removal."""
        text = "Contact test@example.com for help"
        result = clean_for_syllable_counting(text)
        assert "test@example.com" not in result
        assert "Contact" in result
        assert "for help" in result

    def test_removes_currency_numbers(self):
        """Test currency pattern removal."""
        text = "The price is $99.99 on sale"
        result = clean_for_syllable_counting(text)
        assert "$99.99" not in result
        assert "The price is" in result
        assert "on sale" in result

    def test_removes_standalone_numbers(self):
        """Test standalone number removal."""
        text = "The year 2026 had 365 days"
        result = clean_for_syllable_counting(text)
        assert "2026" not in result
        assert "365" not in result
        assert "The year" in result
        assert "had" in result
        assert "days" in result

    def test_normalizes_whitespace(self):
        """Test whitespace normalization."""
        text = "Too    many     spaces"
        result = clean_for_syllable_counting(text)
        assert result == "Too many spaces"

    def test_preserves_words(self):
        """Test that regular words are preserved."""
        text = "The quick brown fox jumps"
        result = clean_for_syllable_counting(text)
        assert result == "The quick brown fox jumps"

    def test_real_world_complex(self):
        """Test with complex real-world text."""
        text = "Dr. O'Brian works at test@example.com and earns $50,000 yearly. Visit https://example.com."
        result = clean_for_syllable_counting(text)
        # Should preserve: Dr. O'Brian works at and earns yearly Visit
        # Should remove: test@example.com, $50,000, https://example.com
        assert "test@example.com" not in result
        assert "$50,000" not in result
        assert "https://example.com" not in result
        assert "Brian" in result  # O'Brian should be preserved
        assert "works" in result

"""Comprehensive tests for token normalization."""

from pystylometry._normalize import (
    clean_for_syllable_counting,
    is_word_token,
    normalize_for_readability,
    normalize_for_stylometry,
    validate_tokens_for_readability,
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

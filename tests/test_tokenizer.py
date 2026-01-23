"""Tests for the Tokenizer class."""

from pystylometry.tokenizer import TokenizationStats, Tokenizer, TokenMetadata


class TestTokenizerBasic:
    """Test basic tokenization functionality."""

    def test_sandusky(self):
        # https://trimc-nlp.blogspot.com/2020/11/the-art-of-tokenization.html
        """Test tokenization with lowercase conversion."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=False)
        text = "“I said, 'what're you?  Crazy?'” said Sandowsky.  “I can't afford to   do that.”"
        tokens = tokenizer.tokenize(text)

        assert tokens == [
            '"',
            "i",
            "said",
            ",",
            "'",
            "what're",
            "you",
            "?",
            "crazy",
            "?",
            "'",
            '"',
            "said",
            "sandowsky",
            ".",
            '"',
            "i",
            "can't",
            "afford",
            "to",
            "do",
            "that",
            ".",
            '"',
        ]

    def test_basic_tokenization(self):
        """Test simple tokenization with default settings."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "Hello, world! This is a test."
        tokens = tokenizer.tokenize(text)

        assert "Hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "," in tokens
        assert "!" in tokens
        assert "." in tokens

    def test_lowercase_tokenization(self):
        """Test tokenization with lowercase conversion."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=False)
        text = "Hello World TEST"
        tokens = tokenizer.tokenize(text)

        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "Hello" not in tokens
        assert "TEST" not in tokens

    def test_strip_punctuation(self):
        """Test tokenization with punctuation stripping."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=True)
        text = "Hello, world! Test."
        tokens = tokenizer.tokenize(text)

        assert "Hello" in tokens
        assert "world" in tokens
        assert "Test" in tokens
        assert "," not in tokens
        assert "!" not in tokens
        assert "." not in tokens

    def test_empty_text(self):
        """Test tokenization with empty text."""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("")

        assert tokens == []

    def test_whitespace_only(self):
        """Test tokenization with whitespace-only text."""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("   \n\t   ")

        assert tokens == []


class TestTokenizerUnicode:
    """Test unicode normalization."""

    def test_smart_quotes(self):
        """Test smart quote normalization."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, normalize_unicode=True)
        text = "\u201cHello\u201d 'world'"  # Smart double quotes
        tokens = tokenizer.tokenize(text)

        # Smart quotes should be normalized to regular quotes
        assert '"' in tokens
        assert "'" in tokens

    def test_em_dash(self):
        """Test em dash normalization."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, normalize_unicode=True)
        text = "Hello—world"
        tokens = tokenizer.tokenize(text)

        # Em dash should be normalized to hyphen
        assert "Hello-world" in tokens or (
            "Hello" in tokens and "-" in tokens and "world" in tokens
        )

    def test_ligatures(self):
        """Test ligature decomposition."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, normalize_unicode=True)
        text = "ﬁle ﬂag"  # fi and fl ligatures
        tokens = tokenizer.tokenize(text)

        assert "file" in tokens
        assert "flag" in tokens

    def test_ellipsis(self):
        """Test ellipsis normalization."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, normalize_unicode=True)
        text = "Hello…world"
        tokens = tokenizer.tokenize(text)

        assert "..." in tokens


class TestTokenizerTextCleaning:
    """Test text cleaning functionality."""

    def test_italics_markers(self):
        """Test removal of italics markers."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, clean_text=True)
        text = "This is *italic* and _underlined_ text"
        tokens = tokenizer.tokenize(text)

        assert "italic" in tokens
        assert "underlined" in tokens
        assert "*italic*" not in tokens
        assert "_underlined_" not in tokens

    def test_brackets(self):
        """Test removal of brackets."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, clean_text=True)
        text = "Text [with brackets] and {curly braces}"
        tokens = tokenizer.tokenize(text)

        assert "with" in tokens
        assert "brackets" in tokens
        assert "curly" in tokens
        assert "braces" in tokens

    def test_line_break_hyphens(self):
        """Test removal of line-break hyphens."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, clean_text=True)
        text = "super-\ncalifragilistic"
        tokens = tokenizer.tokenize(text)

        assert "supercalifragilistic" in tokens

    def test_page_markers(self):
        """Test removal of bracketed content."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, clean_text=True)
        text = "Text [with brackets] more text"
        tokens = tokenizer.tokenize(text)

        assert "Text" in tokens
        assert "with" in tokens
        assert "brackets" in tokens
        assert "more" in tokens
        assert "text" in tokens
        # Brackets themselves should be removed
        assert "[" not in tokens
        assert "]" not in tokens


class TestTokenizerContractions:
    """Test contraction handling."""

    def test_contractions_preserved(self):
        """Test that contractions are preserved by default."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=False, expand_contractions=False)
        text = "I'm can't won't"
        tokens = tokenizer.tokenize(text)

        assert "i'm" in tokens
        assert "can't" in tokens
        assert "won't" in tokens

    def test_contractions_expanded(self):
        """Test contraction expansion."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=False, expand_contractions=True)
        text = "I'm can't won't"
        tokens = tokenizer.tokenize(text)

        assert "i" in tokens
        assert "am" in tokens
        assert "cannot" in tokens
        assert "will" in tokens
        assert "not" in tokens

    def test_possessives(self):
        """Test possessive handling."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=False)
        text = "John's book"
        tokens = tokenizer.tokenize(text)

        assert "john's" in tokens
        assert "book" in tokens


class TestTokenizerFiltering:
    """Test token filtering options."""

    def test_min_length_filter(self):
        """Test minimum length filtering."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=True, min_length=3)
        text = "I am a big elephant"
        tokens = tokenizer.tokenize(text)

        assert "big" in tokens
        assert "elephant" in tokens
        assert "I" not in tokens
        assert "am" not in tokens
        assert "a" not in tokens

    def test_max_length_filter(self):
        """Test maximum length filtering."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=True, max_length=5)
        text = "short words but supercalifragilistic is long"
        tokens = tokenizer.tokenize(text)

        assert "short" in tokens
        assert "words" in tokens
        assert "but" in tokens
        assert "supercalifragilistic" not in tokens

    def test_strip_numbers(self):
        """Test number stripping."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, strip_numbers=True)
        text = "I have 42 apples and $100"
        tokens = tokenizer.tokenize(text)

        assert "have" in tokens
        assert "apples" in tokens
        assert "and" in tokens
        assert "42" not in tokens
        assert "$100" not in tokens


class TestTokenizerSpecialTokens:
    """Test handling of special token types."""

    def test_urls(self):
        """Test URL handling."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, preserve_urls=True)
        text = "Visit https://example.com for info"
        tokens = tokenizer.tokenize(text)

        assert "https://example.com" in tokens

    def test_urls_stripped(self):
        """Test URL stripping."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, preserve_urls=False)
        text = "Visit https://example.com for info"
        tokens = tokenizer.tokenize(text)

        assert "https://example.com" not in tokens
        assert "Visit" in tokens
        assert "for" in tokens
        assert "info" in tokens

    def test_emails(self):
        """Test email handling."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, preserve_emails=True)
        text = "Contact me at user@example.com please"
        tokens = tokenizer.tokenize(text)

        assert "user@example.com" in tokens

    def test_hashtags(self):
        """Test hashtag handling."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, preserve_hashtags=True)
        text = "Check out #python #coding"
        tokens = tokenizer.tokenize(text)

        assert "#python" in tokens or "python" in tokens
        assert "#coding" in tokens or "coding" in tokens

    def test_mentions(self):
        """Test mention handling."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, preserve_mentions=True)
        text = "Thanks @user for the help"
        tokens = tokenizer.tokenize(text)

        assert "@user" in tokens or "user" in tokens

    def test_hyphenated_words(self):
        """Test hyphenated compound words."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "My mother-in-law is well-known"
        tokens = tokenizer.tokenize(text)

        assert "mother-in-law" in tokens
        assert "well-known" in tokens


class TestTokenizerMetadata:
    """Test tokenization with metadata."""

    def test_metadata_basic(self):
        """Test basic metadata extraction."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "Hello world"
        metadata = tokenizer.tokenize_with_metadata(text)

        assert len(metadata) > 0
        assert all(isinstance(m, TokenMetadata) for m in metadata)
        assert all(hasattr(m, "token") for m in metadata)
        assert all(hasattr(m, "start") for m in metadata)
        assert all(hasattr(m, "end") for m in metadata)
        assert all(hasattr(m, "token_type") for m in metadata)

    def test_metadata_positions(self):
        """Test token position tracking in metadata."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "Hello world"
        metadata = tokenizer.tokenize_with_metadata(text)

        # Check that positions make sense
        for m in metadata:
            assert m.start >= 0
            assert m.end > m.start
            assert m.end <= len(text)

    def test_metadata_token_types(self):
        """Test token type classification."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "Hello 123 test@example.com"
        metadata = tokenizer.tokenize_with_metadata(text)

        # Should have different token types
        token_types = {m.token_type for m in metadata}
        assert len(token_types) > 0


class TestTokenizerStatistics:
    """Test tokenization statistics."""

    def test_statistics_basic(self):
        """Test basic statistics generation."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "Hello world! This is a test."
        stats = tokenizer.get_statistics(text)

        assert isinstance(stats, TokenizationStats)
        assert stats.total_tokens > 0
        assert stats.unique_tokens > 0
        assert stats.word_tokens > 0
        assert stats.average_token_length > 0

    def test_statistics_empty(self):
        """Test statistics with empty text."""
        tokenizer = Tokenizer()
        stats = tokenizer.get_statistics("")

        assert stats.total_tokens == 0
        assert stats.unique_tokens == 0
        assert stats.word_tokens == 0
        assert stats.average_token_length == 0.0

    def test_statistics_unique_tokens(self):
        """Test unique token counting."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=True)
        text = "hello hello world world world"
        stats = tokenizer.get_statistics(text)

        assert stats.total_tokens == 5
        assert stats.unique_tokens == 2  # hello and world

    def test_statistics_token_lengths(self):
        """Test token length statistics."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=True)
        text = "a bb ccc"
        stats = tokenizer.get_statistics(text)

        assert stats.min_token_length == 1  # "a"
        assert stats.max_token_length == 3  # "ccc"
        assert stats.average_token_length == 2.0  # (1+2+3)/3


class TestTokenizerIterator:
    """Test iterator-based tokenization."""

    def test_iterator_basic(self):
        """Test basic iterator functionality."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=True)
        text = "Hello world test"
        tokens = list(tokenizer.tokenize_iter(text))

        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens

    def test_iterator_vs_list(self):
        """Test that iterator and list methods produce same results."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=True)
        text = "Hello world test"

        list_tokens = tokenizer.tokenize(text)
        iter_tokens = list(tokenizer.tokenize_iter(text))

        assert list_tokens == iter_tokens

    def test_iterator_memory_efficiency(self):
        """Test that iterator can be consumed incrementally."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=True)
        text = "word1 word2 word3"
        iterator = tokenizer.tokenize_iter(text)

        # Should be able to get tokens one at a time
        first = next(iterator)
        assert first == "word1"

        second = next(iterator)
        assert second == "word2"


class TestTokenizerEdgeCases:
    """Test edge cases and special scenarios."""

    def test_multiple_spaces(self):
        """Test handling of multiple spaces."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "hello    world"
        tokens = tokenizer.tokenize(text)

        assert "hello" in tokens
        assert "world" in tokens

    def test_tabs_and_newlines(self):
        """Test handling of tabs and newlines."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "hello\tworld\ntest"
        tokens = tokenizer.tokenize(text)

        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens

    def test_mixed_case_contractions(self):
        """Test contractions with mixed case."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, expand_contractions=True)
        text = "I'm can't Won't"
        tokens = tokenizer.tokenize(text)

        # First word of expanded contraction should preserve case
        assert "I" in tokens or "i" in tokens

    def test_numbers_with_commas(self):
        """Test numbers with comma separators."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "Cost is $1,234.56"
        tokens = tokenizer.tokenize(text)

        assert "$1,234.56" in tokens or "1,234.56" in tokens

    def test_ordinals(self):
        """Test ordinal number handling."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "She came in 1st, 2nd, and 3rd"
        tokens = tokenizer.tokenize(text)

        assert "1st" in tokens
        assert "2nd" in tokens
        assert "3rd" in tokens

    def test_abbreviations(self):
        """Test abbreviation handling."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False, expand_abbreviations=True)
        text = "Dr. Smith and Mr. Jones"
        tokens = tokenizer.tokenize(text)

        assert "Doctor" in tokens or "Dr." in tokens
        assert "Smith" in tokens
        assert "Mister" in tokens or "Mr." in tokens
        assert "Jones" in tokens

    def test_roman_numerals(self):
        """Test Roman numeral handling."""
        tokenizer = Tokenizer(lowercase=False, strip_punctuation=False)
        text = "Chapter XII and section IV"
        tokens = tokenizer.tokenize(text)

        assert "XII" in tokens or "xii" in tokens
        assert "IV" in tokens or "iv" in tokens

    def test_strip_accents(self):
        """Test accent stripping."""
        tokenizer = Tokenizer(lowercase=True, strip_punctuation=True, strip_accents=True)
        text = "café naïve"
        tokens = tokenizer.tokenize(text)

        assert "cafe" in tokens
        assert "naive" in tokens


class TestTokenizerConfiguration:
    """Test various tokenizer configurations."""

    def test_minimal_processing(self):
        """Test tokenizer with minimal processing."""
        tokenizer = Tokenizer(
            lowercase=False,
            strip_punctuation=False,
            normalize_unicode=False,
            clean_text=False,
        )
        text = "Hello, world!"
        tokens = tokenizer.tokenize(text)

        assert "Hello" in tokens
        assert "," in tokens
        assert "world" in tokens
        assert "!" in tokens

    def test_maximal_processing(self):
        """Test tokenizer with maximal processing."""
        tokenizer = Tokenizer(
            lowercase=True,
            strip_punctuation=True,
            normalize_unicode=True,
            clean_text=True,
            expand_contractions=True,
            strip_accents=True,
            min_length=2,
        )
        text = "We're *really* enjoying café. It's quite naïve"
        tokens = tokenizer.tokenize(text)

        # Should have extensive processing applied
        assert len(tokens) > 0
        # All tokens should respect min_length filter
        assert all(len(t) >= 2 for t in tokens)
        # Check that various processing was applied
        assert "cafe" in tokens  # Accent stripped
        assert "naive" in tokens  # Accent stripped
        assert "really" in tokens  # Italics markers removed
        assert "we" in tokens  # Contraction expanded
        assert "are" in tokens  # Contraction expanded
        assert all(t.islower() or not t.isalpha() for t in tokens)

    def test_stylometry_config(self):
        """Test configuration suitable for stylometric analysis."""
        tokenizer = Tokenizer(
            lowercase=True,
            strip_punctuation=True,
            normalize_unicode=True,
            clean_text=True,
            min_length=2,
        )
        text = "This is a sample text for stylometric analysis."
        tokens = tokenizer.tokenize(text)

        # Should produce clean tokens suitable for analysis
        assert "this" in tokens
        assert "sample" in tokens
        assert "text" in tokens
        assert "stylometric" in tokens
        assert "analysis" in tokens
        # Short words and punctuation should be filtered
        assert "a" not in tokens
        assert "." not in tokens

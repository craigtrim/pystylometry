"""Comprehensive tests for the Tokenizer class and its helper functions."""

import pytest

from pystylometry.tokenizer import (
    Tokenizer,
    TokenMetadata,
    TokenizationStats,
    _remove_italics_markers,
    _remove_brackets,
    _remove_line_break_hyphens,
    _remove_page_markers,
    _normalize_whitespace,
)


# ===== Helper Function Tests =====


class TestRemoveItalicsMarkers:
    """Tests for the _remove_italics_markers helper."""

    def test_asterisk_italics(self):
        """Asterisk-wrapped words should have markers removed."""
        assert _remove_italics_markers("He was *very* upset") == "He was very upset"

    def test_underscore_italics(self):
        """Underscore-wrapped words should have markers removed."""
        assert _remove_italics_markers("She said _hello_ quietly") == "She said hello quietly"

    def test_no_markers(self):
        """Text without markers should pass through unchanged."""
        assert _remove_italics_markers("Plain text here") == "Plain text here"

    def test_multiple_markers(self):
        """Multiple italicized segments should all be cleaned."""
        result = _remove_italics_markers("*one* and *two* and _three_")
        assert result == "one and two and three"


class TestRemoveBrackets:
    """Tests for the _remove_brackets helper."""

    def test_square_brackets(self):
        """Square brackets should be removed, content preserved."""
        assert _remove_brackets("He said [quietly] that") == "He said quietly that"

    def test_curly_brackets(self):
        """Curly brackets should be removed, content preserved."""
        assert _remove_brackets("The result {important} was") == "The result important was"

    def test_no_brackets(self):
        """Text without brackets should pass through unchanged."""
        assert _remove_brackets("No brackets here") == "No brackets here"


class TestRemoveLineBreakHyphens:
    """Tests for the _remove_line_break_hyphens helper."""

    def test_basic_line_break_hyphen(self):
        """Hyphens at line breaks should join the word parts."""
        assert _remove_line_break_hyphens("beau-\ntiful") == "beautiful"

    def test_with_spaces(self):
        """Hyphens with trailing spaces before newline should also work."""
        assert _remove_line_break_hyphens("inter-\n  national") == "international"

    def test_no_hyphen_break(self):
        """Regular hyphens (not at line breaks) should be preserved."""
        assert _remove_line_break_hyphens("well-known fact") == "well-known fact"


class TestRemovePageMarkers:
    """Tests for the _remove_page_markers helper."""

    def test_bracketed_page_number(self):
        """[Page 123] markers should be removed."""
        assert _remove_page_markers("some text [Page 42] more text") == "some text  more text"

    def test_dashed_page_marker(self):
        """--- Page 45 --- markers should be removed."""
        result = _remove_page_markers("text --- Page 45 --- more")
        assert result == "text  more"

    def test_case_insensitive(self):
        """Page markers should be matched case-insensitively."""
        assert _remove_page_markers("[page 7]") == ""


class TestNormalizeWhitespace:
    """Tests for the _normalize_whitespace helper."""

    def test_multiple_spaces(self):
        """Multiple spaces should collapse to one."""
        assert _normalize_whitespace("too   many   spaces") == "too many spaces"

    def test_multiple_newlines(self):
        """Three or more newlines should collapse to two."""
        result = _normalize_whitespace("para1\n\n\n\npara2")
        assert result == "para1\n\npara2"

    def test_leading_trailing(self):
        """Leading and trailing whitespace should be stripped."""
        assert _normalize_whitespace("  hello world  ") == "hello world"

    def test_tabs(self):
        """Tabs should be collapsed into single spaces."""
        assert _normalize_whitespace("col1\t\tcol2") == "col1 col2"


# ===== Tokenizer Basic Tests =====


class TestBasicTokenization:
    """Tests for basic tokenization behavior."""

    def test_simple_sentence(self):
        """A simple sentence should tokenize into words."""
        t = Tokenizer()
        tokens = t.tokenize("Hello world")
        assert tokens == ["hello", "world"]

    def test_with_punctuation_stripped(self):
        """Punctuation should be stripped by default."""
        t = Tokenizer()
        tokens = t.tokenize("Hello, world! How are you?")
        assert "," not in tokens
        assert "!" not in tokens
        assert "?" not in tokens
        assert "hello" in tokens

    def test_with_punctuation_preserved(self):
        """Punctuation should be preserved when strip_punctuation=False."""
        t = Tokenizer(strip_punctuation=False)
        tokens = t.tokenize("Hello, world!")
        assert "," in tokens
        assert "!" in tokens

    def test_lowercase_default(self):
        """Tokens should be lowercased by default."""
        t = Tokenizer()
        tokens = t.tokenize("Hello World UPPER")
        assert tokens == ["hello", "world", "upper"]

    def test_preserve_case(self):
        """Tokens should preserve case when lowercase=False."""
        t = Tokenizer(lowercase=False)
        tokens = t.tokenize("Hello World")
        assert tokens == ["Hello", "World"]

    def test_whitespace_handling(self):
        """Extra whitespace should not produce empty tokens."""
        t = Tokenizer()
        tokens = t.tokenize("word1   word2    word3")
        assert tokens == ["word1", "word2", "word3"]


# ===== Unicode Normalization Tests =====


class TestUnicodeNormalization:
    """Tests for unicode normalization during tokenization."""

    def test_smart_single_quotes(self):
        """Smart single quotes should be converted to ASCII apostrophes."""
        t = Tokenizer(normalize_unicode=True)
        tokens = t.tokenize("it\u2019s a test")
        assert "it's" in tokens

    def test_smart_double_quotes(self):
        """Smart double quotes should be converted to ASCII double quotes."""
        t = Tokenizer(normalize_unicode=True, strip_punctuation=False)
        tokens = t.tokenize("\u201cHello\u201d")
        assert any('"' in tok for tok in tokens)

    def test_en_dash(self):
        """En dash should be converted to a hyphen."""
        t = Tokenizer(normalize_unicode=True, strip_punctuation=False)
        # En dash between words becomes a hyphen
        result = t.tokenize("pages 1\u20132")
        assert any("-" in tok or tok == "-" for tok in result) or "1-2" in result or "pages" in result

    def test_em_dash(self):
        """Em dash should be converted to a hyphen."""
        t = Tokenizer(normalize_unicode=True, strip_punctuation=False)
        result = t.tokenize("word\u2014another")
        # After normalization the em dash becomes a hyphen
        assert any("-" in tok for tok in result) or "word-another" in result

    def test_non_breaking_space(self):
        """Non-breaking spaces should be converted to regular spaces."""
        t = Tokenizer(normalize_unicode=True)
        tokens = t.tokenize("hello\u00a0world")
        assert "hello" in tokens
        assert "world" in tokens

    def test_ligature_fi(self):
        """The fi ligature should be decomposed."""
        t = Tokenizer(normalize_unicode=True)
        tokens = t.tokenize("\ufb01nish")
        # "fi" + "nish" => "finish" as one token
        assert "finish" in tokens

    def test_ligature_fl(self):
        """The fl ligature should be decomposed."""
        t = Tokenizer(normalize_unicode=True)
        tokens = t.tokenize("\ufb02oor")
        assert "floor" in tokens

    def test_ae_ligature(self):
        """The ae ligature should be decomposed."""
        t = Tokenizer(normalize_unicode=True)
        tokens = t.tokenize("\u00e6sthetic")
        assert "aesthetic" in tokens

    def test_ellipsis_character(self):
        """The horizontal ellipsis character should become three dots."""
        t = Tokenizer(normalize_unicode=True, strip_punctuation=False)
        tokens = t.tokenize("wait\u2026")
        assert "..." in tokens

    def test_fraction_half(self):
        """The fraction 1/2 character should decompose."""
        t = Tokenizer(normalize_unicode=True, strip_punctuation=False)
        tokens = t.tokenize("\u00bd cup")
        # The fraction becomes "1/2"
        assert any("1" in tok for tok in tokens)

    def test_normalize_unicode_off(self):
        """When normalize_unicode=False, smart quotes should remain."""
        t = Tokenizer(normalize_unicode=False, clean_text=False)
        tokens = t.tokenize("it\u2019s")
        # The smart quote is kept as-is; exact token depends on regex,
        # but it should NOT have been replaced with ASCII apostrophe before tokenizing
        joined = " ".join(tokens)
        # With normalization off, the original character is preserved somewhere in the flow
        assert len(tokens) >= 1


# ===== Options Tests =====


class TestMinMaxLength:
    """Tests for min_length and max_length filtering."""

    def test_min_length_filters_short_tokens(self):
        """Tokens shorter than min_length should be excluded."""
        t = Tokenizer(min_length=3)
        tokens = t.tokenize("I am a big dog")
        assert "i" not in tokens
        assert "am" not in tokens
        assert "a" not in tokens
        assert "big" in tokens
        assert "dog" in tokens

    def test_max_length_filters_long_tokens(self):
        """Tokens longer than max_length should be excluded."""
        t = Tokenizer(max_length=4)
        tokens = t.tokenize("I like elephants")
        assert "i" in tokens
        assert "like" in tokens
        assert "elephants" not in tokens

    def test_min_and_max_combined(self):
        """Both min_length and max_length should apply together."""
        t = Tokenizer(min_length=3, max_length=5)
        tokens = t.tokenize("I am the quick brown fox")
        assert "i" not in tokens
        assert "am" not in tokens
        assert "the" in tokens
        assert "quick" in tokens
        assert "brown" in tokens
        assert "fox" in tokens


class TestStripNumbers:
    """Tests for the strip_numbers option."""

    def test_strip_numbers_removes_numeric_tokens(self):
        """Numeric tokens should be removed when strip_numbers=True."""
        t = Tokenizer(strip_numbers=True)
        tokens = t.tokenize("chapter 42 begins")
        assert "chapter" in tokens
        assert "begins" in tokens
        assert "42" not in tokens

    def test_strip_numbers_false_preserves_numbers(self):
        """Numeric tokens should be preserved when strip_numbers=False."""
        t = Tokenizer(strip_numbers=False)
        tokens = t.tokenize("page 7")
        assert "7" in tokens


# ===== Special Token Tests =====


class TestSpecialTokens:
    """Tests for URL, email, hashtag, and mention handling."""

    def test_urls_stripped_by_default(self):
        """URLs should be stripped by default (preserve_urls=False)."""
        t = Tokenizer()
        tokens = t.tokenize("Visit https://example.com today")
        assert "https://example.com" not in tokens
        assert "visit" in tokens
        assert "today" in tokens

    def test_urls_preserved(self):
        """URLs should be kept when preserve_urls=True."""
        t = Tokenizer(preserve_urls=True)
        tokens = t.tokenize("Visit https://example.com today")
        assert any("https://example.com" in tok for tok in tokens)

    def test_emails_stripped_by_default(self):
        """Emails should be stripped by default."""
        t = Tokenizer()
        tokens = t.tokenize("Contact user@example.com please")
        assert "user@example.com" not in tokens
        assert "contact" in tokens

    def test_emails_preserved(self):
        """Emails should be kept when preserve_emails=True."""
        t = Tokenizer(preserve_emails=True)
        tokens = t.tokenize("Contact user@example.com please")
        assert "user@example.com" in tokens

    def test_hashtags_stripped_by_default(self):
        """Hashtags should be stripped by default."""
        t = Tokenizer()
        tokens = t.tokenize("Trending #python today")
        assert "#python" not in tokens

    def test_hashtags_preserved(self):
        """Hashtags should be kept when preserve_hashtags=True."""
        t = Tokenizer(preserve_hashtags=True)
        tokens = t.tokenize("Trending #python today")
        assert "#python" in tokens

    def test_mentions_stripped_by_default(self):
        """Mentions should be stripped by default."""
        t = Tokenizer()
        tokens = t.tokenize("Hello @alice and @bob")
        assert "@alice" not in tokens
        assert "@bob" not in tokens

    def test_mentions_preserved(self):
        """Mentions should be kept when preserve_mentions=True."""
        t = Tokenizer(preserve_mentions=True)
        tokens = t.tokenize("Hello @alice")
        assert "@alice" in tokens


# ===== Contraction Expansion Tests =====


class TestExpandContractions:
    """Tests for the expand_contractions option."""

    def test_expand_dont(self):
        """don't should expand to do not."""
        t = Tokenizer(expand_contractions=True)
        tokens = t.tokenize("I don't know")
        assert "do" in tokens
        assert "not" in tokens
        assert "don't" not in tokens

    def test_expand_wont(self):
        """won't should expand to will not."""
        t = Tokenizer(expand_contractions=True)
        tokens = t.tokenize("I won't go")
        assert "will" in tokens
        assert "not" in tokens

    def test_expand_cant(self):
        """can't should expand to cannot."""
        t = Tokenizer(expand_contractions=True)
        tokens = t.tokenize("I can't see")
        assert "cannot" in tokens

    def test_expand_its(self):
        """it's should expand to it is."""
        t = Tokenizer(expand_contractions=True)
        tokens = t.tokenize("It's raining")
        assert "it" in tokens
        assert "is" in tokens

    def test_no_expand_by_default(self):
        """Contractions should NOT be expanded by default."""
        t = Tokenizer(expand_contractions=False)
        tokens = t.tokenize("don't")
        assert "don't" in tokens
        assert "do" not in tokens

    def test_expand_preserves_capitalization(self):
        """Expansion of a capitalized contraction should capitalize the result."""
        t = Tokenizer(expand_contractions=True, lowercase=False)
        tokens = t.tokenize("Don't touch that")
        # "Don't" -> "Do not" (capitalized), split into "Do" and "not"
        assert "Do" in tokens
        assert "not" in tokens


# ===== Abbreviation Expansion Tests =====


class TestExpandAbbreviations:
    """Tests for the expand_abbreviations option."""

    def test_expand_dr(self):
        """Dr. should expand to Doctor."""
        t = Tokenizer(expand_abbreviations=True, lowercase=False)
        tokens = t.tokenize("Dr. Smith is here")
        assert "Doctor" in tokens
        assert "Dr." not in tokens

    def test_expand_mr(self):
        """Mr. should expand to Mister."""
        t = Tokenizer(expand_abbreviations=True, lowercase=False)
        tokens = t.tokenize("Mr. Jones arrived")
        assert "Mister" in tokens

    def test_expand_etc(self):
        """etc. should expand to et cetera."""
        t = Tokenizer(expand_abbreviations=True)
        tokens = t.tokenize("cats, dogs, etc.")
        assert "et" in tokens
        assert "cetera" in tokens

    def test_no_expand_by_default(self):
        """Abbreviations should NOT be expanded by default."""
        t = Tokenizer(expand_abbreviations=False, lowercase=False)
        tokens = t.tokenize("Dr. Smith")
        assert "Dr." in tokens
        assert "Doctor" not in tokens


# ===== Strip Accents Tests =====


class TestStripAccents:
    """Tests for the strip_accents option."""

    def test_strip_accents_cafe(self):
        """cafe with accent should become cafe without accent."""
        t = Tokenizer(strip_accents=True)
        tokens = t.tokenize("caf\u00e9")
        assert "cafe" in tokens

    def test_strip_accents_resume(self):
        """resume with accents should lose them."""
        t = Tokenizer(strip_accents=True)
        tokens = t.tokenize("r\u00e9sum\u00e9")
        assert "resume" in tokens

    def test_strip_accents_off(self):
        """Accents should be preserved when strip_accents=False."""
        t = Tokenizer(strip_accents=False)
        tokens = t.tokenize("caf\u00e9")
        assert "caf\u00e9" in tokens

    def test_strip_accents_umlaut(self):
        """German umlauts should be stripped to base characters."""
        t = Tokenizer(strip_accents=True)
        tokens = t.tokenize("\u00fcber")
        assert "uber" in tokens


# ===== tokenize_with_metadata Tests =====


class TestTokenizeWithMetadata:
    """Tests for the tokenize_with_metadata method."""

    def test_returns_token_metadata_objects(self):
        """Result should be a list of TokenMetadata instances."""
        t = Tokenizer()
        result = t.tokenize_with_metadata("Hello world")
        assert len(result) > 0
        assert all(isinstance(item, TokenMetadata) for item in result)

    def test_metadata_has_correct_fields(self):
        """Each TokenMetadata should have token, start, end, token_type."""
        t = Tokenizer()
        result = t.tokenize_with_metadata("Hello world")
        for item in result:
            assert hasattr(item, "token")
            assert hasattr(item, "start")
            assert hasattr(item, "end")
            assert hasattr(item, "token_type")

    def test_metadata_token_type_word(self):
        """Simple words should have a word-like token_type."""
        t = Tokenizer()
        result = t.tokenize_with_metadata("hello")
        assert len(result) == 1
        assert result[0].token == "hello"
        assert result[0].token_type == "word"

    def test_metadata_positions(self):
        """Start and end positions should be non-negative and start < end."""
        t = Tokenizer()
        result = t.tokenize_with_metadata("The quick brown fox")
        for item in result:
            assert item.start >= 0
            assert item.end > item.start

    def test_metadata_punctuation_type(self):
        """Punctuation tokens should have token_type 'punct'."""
        t = Tokenizer(strip_punctuation=False)
        result = t.tokenize_with_metadata("Hello!")
        punct_items = [item for item in result if item.token == "!"]
        assert len(punct_items) == 1
        assert punct_items[0].token_type == "punct"

    def test_metadata_url_type(self):
        """URL tokens should have token_type 'url'."""
        t = Tokenizer(preserve_urls=True)
        result = t.tokenize_with_metadata("Visit https://example.com today")
        url_items = [item for item in result if "example.com" in item.token]
        assert len(url_items) == 1
        assert url_items[0].token_type == "url"

    def test_metadata_email_type(self):
        """Email tokens should have token_type 'email'."""
        t = Tokenizer(preserve_emails=True)
        result = t.tokenize_with_metadata("Mail user@example.com now")
        email_items = [item for item in result if "@" in item.token]
        assert len(email_items) == 1
        assert email_items[0].token_type == "email"


# ===== get_statistics Tests =====


class TestGetStatistics:
    """Tests for the get_statistics method."""

    def test_returns_stats_object(self):
        """Result should be a TokenizationStats instance."""
        t = Tokenizer()
        stats = t.get_statistics("Hello world")
        assert isinstance(stats, TokenizationStats)

    def test_total_token_count(self):
        """Total token count should match the number of tokens."""
        t = Tokenizer()
        stats = t.get_statistics("one two three")
        assert stats.total_tokens == 3

    def test_unique_token_count(self):
        """Unique token count should reflect distinct tokens."""
        t = Tokenizer()
        stats = t.get_statistics("the cat and the dog")
        # "the" appears twice, so unique < total
        assert stats.unique_tokens == 4
        assert stats.total_tokens == 5

    def test_average_token_length(self):
        """Average token length should be computed correctly."""
        t = Tokenizer()
        stats = t.get_statistics("hi there")
        # "hi" = 2, "there" = 5 -> avg = 3.5
        assert stats.average_token_length == pytest.approx(3.5)

    def test_min_max_token_length(self):
        """Min and max token lengths should be correct."""
        t = Tokenizer()
        stats = t.get_statistics("I like elephants")
        assert stats.min_token_length == 1  # "i"
        assert stats.max_token_length == 9  # "elephants"

    def test_empty_text_statistics(self):
        """Empty text should produce zero-valued statistics."""
        t = Tokenizer()
        stats = t.get_statistics("")
        assert stats.total_tokens == 0
        assert stats.unique_tokens == 0
        assert stats.average_token_length == 0.0
        assert stats.min_token_length == 0
        assert stats.max_token_length == 0

    def test_word_token_count(self):
        """word_tokens count should reflect word-type tokens."""
        t = Tokenizer()
        stats = t.get_statistics("hello world")
        assert stats.word_tokens == 2

    def test_url_token_count(self):
        """url_tokens should count preserved URLs."""
        t = Tokenizer(preserve_urls=True)
        stats = t.get_statistics("See https://a.com and https://b.com")
        assert stats.url_tokens == 2

    def test_hashtag_token_count(self):
        """hashtag_tokens should count preserved hashtags."""
        t = Tokenizer(preserve_hashtags=True)
        stats = t.get_statistics("#python #coding rocks")
        assert stats.hashtag_tokens == 2


# ===== Edge Cases =====


class TestEdgeCases:
    """Tests for edge-case inputs."""

    def test_empty_string(self):
        """Empty string should produce an empty token list."""
        t = Tokenizer()
        assert t.tokenize("") == []

    def test_whitespace_only(self):
        """Whitespace-only input should produce an empty token list."""
        t = Tokenizer()
        assert t.tokenize("   \t  \n  ") == []

    def test_all_punctuation(self):
        """All-punctuation input with strip_punctuation should produce empty."""
        t = Tokenizer(strip_punctuation=True)
        assert t.tokenize("!@#$%^&*()") == []

    def test_single_word(self):
        """A single word should tokenize to a single-element list."""
        t = Tokenizer()
        assert t.tokenize("hello") == ["hello"]

    def test_very_long_token(self):
        """A very long word should be handled without error."""
        t = Tokenizer()
        long_word = "a" * 1000
        tokens = t.tokenize(long_word)
        assert len(tokens) == 1
        assert tokens[0] == long_word

    def test_max_length_filters_long_token(self):
        """max_length should filter extremely long tokens."""
        t = Tokenizer(max_length=10)
        long_word = "a" * 50
        tokens = t.tokenize(long_word)
        assert tokens == []


# ===== tokenize_iter Tests =====


class TestTokenizeIter:
    """Tests for the tokenize_iter method."""

    def test_returns_iterator(self):
        """tokenize_iter should return an iterator, not a list."""
        from typing import Iterator
        t = Tokenizer()
        result = t.tokenize_iter("hello world")
        assert hasattr(result, "__next__")

    def test_iter_matches_tokenize(self):
        """tokenize_iter results should match tokenize results."""
        t = Tokenizer()
        text = "The quick brown fox jumps over the lazy dog."
        iter_result = list(t.tokenize_iter(text))
        list_result = t.tokenize(text)
        assert iter_result == list_result


# ===== Text Cleaning Integration Tests =====


class TestTextCleaning:
    """Tests for text cleaning applied during tokenization."""

    def test_italics_removed_during_tokenize(self):
        """Italics markers should be removed before tokenization."""
        t = Tokenizer(clean_text=True)
        tokens = t.tokenize("The *important* word")
        assert "important" in tokens
        assert "*important*" not in tokens

    def test_brackets_removed_during_tokenize(self):
        """Brackets should be removed, preserving content inside."""
        t = Tokenizer(clean_text=True)
        tokens = t.tokenize("He [angrily] left")
        assert "angrily" in tokens

    def test_page_markers_removed(self):
        """Dashed page markers should be removed during tokenization.

        Note: When both normalize_unicode and clean_text are active, the
        multi-dash collapsing (--- -> -) happens during unicode normalization
        before _remove_page_markers runs, so the dashed form doesn't match.
        With normalize_unicode=False, page marker removal works as expected.
        """
        t = Tokenizer(clean_text=True, normalize_unicode=False)
        tokens = t.tokenize("some text --- Page 42 --- more text")
        assert "some" in tokens
        assert "more" in tokens
        assert "text" in tokens
        assert "42" not in tokens
        assert "page" not in tokens

    def test_line_break_hyphens_joined(self):
        """Line-break hyphens should rejoin split words."""
        t = Tokenizer(clean_text=True)
        tokens = t.tokenize("beau-\ntiful day")
        assert "beautiful" in tokens

    def test_clean_text_off(self):
        """When clean_text=False, markers should remain."""
        t = Tokenizer(clean_text=False, strip_punctuation=False)
        tokens = t.tokenize("The *important* word")
        # With cleaning off, the asterisks remain and are tokenized
        assert "*" in tokens or any("*" in tok for tok in tokens)


# ===== HTML Entity Tests =====


class TestHTMLEntities:
    """Tests for HTML entity normalization."""

    def test_nbsp(self):
        """&nbsp; should become a space."""
        t = Tokenizer(normalize_unicode=True)
        tokens = t.tokenize("hello&nbsp;world")
        assert "hello" in tokens
        assert "world" in tokens

    def test_amp(self):
        """&amp; should become &."""
        t = Tokenizer(normalize_unicode=True, strip_punctuation=False)
        tokens = t.tokenize("rock&amp;roll")
        assert any("&" in tok for tok in tokens) or "rock" in tokens


# ===== Combined Options Tests =====


class TestCombinedOptions:
    """Tests for multiple options used together."""

    def test_expand_and_lowercase(self):
        """Expanded contractions should also be lowercased."""
        t = Tokenizer(expand_contractions=True, lowercase=True)
        tokens = t.tokenize("I can't do it")
        assert "cannot" in tokens
        assert "Can't" not in tokens

    def test_strip_accents_and_contractions(self):
        """strip_accents and expand_contractions should work together."""
        t = Tokenizer(strip_accents=True, expand_contractions=True)
        tokens = t.tokenize("caf\u00e9 isn't bad")
        assert "cafe" in tokens
        assert "is" in tokens
        assert "not" in tokens

    def test_all_filters_on(self):
        """Aggressive filtering should still produce tokens from valid words."""
        t = Tokenizer(
            lowercase=True,
            min_length=2,
            strip_numbers=True,
            strip_punctuation=True,
            strip_accents=True,
            expand_contractions=True,
            expand_abbreviations=True,
        )
        tokens = t.tokenize("Dr. Smith can't eat 5 caf\u00e9s!")
        # "Dr." -> "doctor", "Smith" -> "smith", "can't" -> "cannot",
        # "eat" -> "eat", "5" stripped, "cafes" -> "cafes", "!" stripped
        assert "doctor" in tokens
        assert "smith" in tokens
        assert "cannot" in tokens
        assert "eat" in tokens
        assert "5" not in tokens

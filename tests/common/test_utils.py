"""Comprehensive tests for pystylometry._utils module.

Covers:
- tokenize: case preservation, punctuation preservation, URL/email handling, basic splitting
- advanced_tokenize: lowercase, strip_punctuation, expand_contractions, combinations
- split_sentences: simple sentences, abbreviations, multiple punctuation, edge cases
- check_optional_dependency: existing module, missing module
- Edge cases: empty strings, whitespace only, unicode text, very long text
- Interaction: tokenize vs advanced_tokenize behavioral differences
"""

import pytest

from pystylometry._utils import (
    advanced_tokenize,
    check_optional_dependency,
    split_sentences,
    tokenize,
)


# ============================================================
# 1. tokenize — basic behavior
# ============================================================


class TestTokenize:
    """Tests for the simple tokenize() convenience function."""

    def test_preserves_case(self):
        """tokenize should NOT lowercase tokens."""
        tokens = tokenize("Hello World")
        assert "Hello" in tokens
        assert "World" in tokens

    def test_preserves_punctuation(self):
        """tokenize should keep punctuation as separate tokens."""
        tokens = tokenize("Hello, world!")
        assert "," in tokens
        assert "!" in tokens

    def test_preserves_url(self):
        """tokenize should keep URLs intact as single tokens."""
        tokens = tokenize("Visit https://example.com today")
        assert any("https://example.com" in t for t in tokens)

    def test_preserves_email(self):
        """tokenize should keep email addresses intact."""
        tokens = tokenize("Contact user@example.com please")
        assert "user@example.com" in tokens

    def test_basic_splitting(self):
        """tokenize should split words on whitespace boundaries."""
        tokens = tokenize("one two three")
        assert "one" in tokens
        assert "two" in tokens
        assert "three" in tokens

    def test_empty_string(self):
        """tokenize on empty string returns empty list."""
        assert tokenize("") == []

    def test_returns_list(self):
        """tokenize always returns a list."""
        result = tokenize("word")
        assert isinstance(result, list)


# ============================================================
# 2. advanced_tokenize — option handling
# ============================================================


class TestAdvancedTokenize:
    """Tests for advanced_tokenize with various option combinations."""

    def test_lowercase_default_true(self):
        """With default lowercase=True, tokens should be lowered."""
        tokens = advanced_tokenize("Hello World")
        assert "hello" in tokens
        assert "world" in tokens

    def test_lowercase_false(self):
        """With lowercase=False, case is preserved."""
        tokens = advanced_tokenize("Hello World", lowercase=False)
        assert "Hello" in tokens
        assert "World" in tokens

    def test_strip_punctuation_default_true(self):
        """With default strip_punctuation=True, punctuation removed."""
        tokens = advanced_tokenize("Hello, world!")
        assert "," not in tokens
        assert "!" not in tokens
        assert "hello" in tokens

    def test_strip_punctuation_false(self):
        """With strip_punctuation=False, punctuation kept."""
        tokens = advanced_tokenize("Hello, world!", strip_punctuation=False)
        assert "," in tokens
        assert "!" in tokens

    def test_expand_contractions(self):
        """With expand_contractions=True, contractions should expand."""
        tokens = advanced_tokenize("I can't go", expand_contractions=True)
        # "can't" -> "cannot"
        assert "cannot" in tokens
        assert "can't" not in tokens

    def test_expand_contractions_default_false(self):
        """With default expand_contractions=False, contractions stay."""
        tokens = advanced_tokenize("I can't go")
        assert "can't" in tokens

    def test_combination_lower_strip(self):
        """Combined lowercase + strip_punctuation."""
        tokens = advanced_tokenize(
            "Hello, World!", lowercase=True, strip_punctuation=True
        )
        assert tokens == ["hello", "world"]

    def test_combination_all_options(self):
        """All three options enabled together."""
        tokens = advanced_tokenize(
            "I can't believe it!",
            lowercase=True,
            strip_punctuation=True,
            expand_contractions=True,
        )
        assert "i" in tokens
        assert "cannot" in tokens
        assert "believe" in tokens
        assert "it" in tokens

    def test_empty_string(self):
        """advanced_tokenize on empty string returns empty list."""
        assert advanced_tokenize("") == []

    def test_returns_list(self):
        """advanced_tokenize always returns a list."""
        result = advanced_tokenize("word")
        assert isinstance(result, list)


# ============================================================
# 3. split_sentences
# ============================================================


class TestSplitSentences:
    """Tests for sentence splitting with abbreviation handling."""

    def test_simple_two_sentences(self):
        """Two simple sentences separated by a period."""
        result = split_sentences("Hello there. How are you.")
        assert len(result) >= 2

    def test_abbreviation_dr(self):
        """Dr. should not cause a sentence break."""
        result = split_sentences("Dr. Smith arrived. He was happy.")
        # Should not split at "Dr."
        found_dr_sentence = any("Dr." in s and "Smith" in s for s in result)
        assert found_dr_sentence, f"Expected Dr. Smith in same sentence, got: {result}"

    def test_abbreviation_mr(self):
        """Mr. should not cause a sentence break."""
        result = split_sentences("Mr. Jones left. She stayed.")
        found_mr_sentence = any("Mr." in s and "Jones" in s for s in result)
        assert found_mr_sentence, f"Expected Mr. Jones in same sentence, got: {result}"

    def test_abbreviation_etc(self):
        """etc. should not cause a sentence break mid-list."""
        result = split_sentences("Items include pens, paper, etc. The store was open.")
        assert len(result) >= 2

    def test_question_mark_splits(self):
        """Question marks should trigger sentence boundaries."""
        result = split_sentences("Is it raining? The sun is out.")
        assert len(result) >= 2

    def test_exclamation_mark_splits(self):
        """Exclamation marks should trigger sentence boundaries."""
        result = split_sentences("Watch out! The bridge is broken.")
        assert len(result) >= 2

    def test_single_sentence(self):
        """A single sentence with no boundary stays as one."""
        result = split_sentences("Just one sentence here.")
        assert len(result) == 1

    def test_empty_string(self):
        """Empty text returns empty list."""
        assert split_sentences("") == []

    def test_multiple_sentences(self):
        """Multiple consecutive sentences are all captured."""
        text = "First. Second. Third. Fourth."
        result = split_sentences(text)
        assert len(result) >= 3

    def test_strips_whitespace(self):
        """Resulting sentences should have no leading/trailing whitespace."""
        result = split_sentences("Hello.  World is great.")
        for sentence in result:
            assert sentence == sentence.strip()


# ============================================================
# 4. check_optional_dependency
# ============================================================


class TestCheckOptionalDependency:
    """Tests for optional dependency checking."""

    def test_existing_module(self):
        """A standard-library module like 'os' should return True."""
        assert check_optional_dependency("os", "test") is True

    def test_missing_module_raises(self):
        """A non-existent module should raise ImportError."""
        with pytest.raises(ImportError):
            check_optional_dependency("nonexistent_fake_module_xyz", "extras")

    def test_error_message_contains_module_name(self):
        """The ImportError message should mention the missing module name."""
        with pytest.raises(ImportError, match="nonexistent_fake_module_xyz"):
            check_optional_dependency("nonexistent_fake_module_xyz", "extras")

    def test_error_message_contains_extra_name(self):
        """The ImportError message should mention the pip extra name."""
        with pytest.raises(ImportError, match="my_extra"):
            check_optional_dependency("nonexistent_fake_module_xyz", "my_extra")

    def test_error_message_contains_install_instruction(self):
        """The ImportError message should include pip install instruction."""
        with pytest.raises(ImportError, match=r"pip install pystylometry\[my_extra\]"):
            check_optional_dependency("nonexistent_fake_module_xyz", "my_extra")


# ============================================================
# 5. Edge cases
# ============================================================


class TestEdgeCases:
    """Edge cases across all utility functions."""

    def test_tokenize_whitespace_only(self):
        """Whitespace-only text should return empty list."""
        assert tokenize("   ") == []

    def test_advanced_tokenize_whitespace_only(self):
        """Whitespace-only text should return empty list."""
        assert advanced_tokenize("   ") == []

    def test_split_sentences_whitespace_only(self):
        """Whitespace-only text should return empty list."""
        result = split_sentences("   ")
        assert result == []

    def test_tokenize_unicode(self):
        """Unicode text should be tokenized without errors."""
        tokens = tokenize("cafe latte")
        assert len(tokens) >= 2

    def test_advanced_tokenize_unicode(self):
        """Unicode text in advanced_tokenize should not raise."""
        tokens = advanced_tokenize("resume is ready")
        assert len(tokens) >= 2

    def test_tokenize_very_long_text(self):
        """Very long text should tokenize without error."""
        long_text = "word " * 10000
        tokens = tokenize(long_text)
        assert len(tokens) == 10000

    def test_tokenize_numbers(self):
        """Numbers should be tokenized as tokens."""
        tokens = tokenize("There are 42 cats")
        assert "42" in tokens

    def test_tokenize_mixed_punctuation(self):
        """Multiple punctuation characters are handled."""
        tokens = tokenize("Wow!!! Really???")
        assert len(tokens) > 0

    def test_split_sentences_no_terminal_punctuation(self):
        """Text with no sentence-ending punctuation."""
        result = split_sentences("No period at the end")
        assert len(result) >= 1
        assert "No period at the end" in result[0]


# ============================================================
# 6. Interaction — tokenize vs advanced_tokenize
# ============================================================


class TestTokenizeInteraction:
    """Verify behavioral differences between tokenize and advanced_tokenize."""

    def test_case_difference(self):
        """tokenize preserves case; advanced_tokenize lowercases by default."""
        simple = tokenize("Hello World")
        advanced = advanced_tokenize("Hello World")
        assert "Hello" in simple
        assert "hello" in advanced

    def test_punctuation_difference(self):
        """tokenize preserves punctuation; advanced_tokenize strips by default."""
        simple = tokenize("Hello, world!")
        advanced = advanced_tokenize("Hello, world!")
        assert "," in simple
        assert "," not in advanced

    def test_same_with_matching_options(self):
        """advanced_tokenize with matching defaults should approximate tokenize."""
        text = "Simple words only"
        simple = tokenize(text)
        advanced = advanced_tokenize(
            text, lowercase=False, strip_punctuation=False
        )
        # Both should produce the same word tokens for plain text
        assert simple == advanced

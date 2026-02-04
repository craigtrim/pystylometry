"""Comprehensive tests for Unicode apostrophe normalization in BNC frequency analysis.

Tests for GitHub Issue #45:
https://github.com/craigtrim/pystylometry/issues/45

Verifies that Unicode apostrophe variants (smart quotes, typographic quotes, etc.)
are correctly normalized to ASCII apostrophe (U+0027) before BNC lookup.
"""

import pytest

from pystylometry.lexical.bnc_frequency import compute_bnc_frequency

# Define the expected apostrophe variants for testing purposes
# These should match _APOSTROPHE_VARIANTS in bnc_frequency.py
EXPECTED_APOSTROPHE_VARIANTS = [
    ("\u0060", "GRAVE ACCENT"),
    ("\u00B4", "ACUTE ACCENT"),
    ("\u2018", "LEFT SINGLE QUOTATION MARK"),
    ("\u2019", "RIGHT SINGLE QUOTATION MARK"),
    ("\u201B", "SINGLE HIGH-REVERSED-9 QUOTATION MARK"),
    ("\u2032", "PRIME"),
    ("\u2035", "REVERSED PRIME"),
    ("\u02B9", "MODIFIER LETTER PRIME"),
    ("\u02BC", "MODIFIER LETTER APOSTROPHE"),
    ("\u02C8", "MODIFIER LETTER VERTICAL LINE"),
    ("\u0313", "COMBINING COMMA ABOVE"),
    ("\u0315", "COMBINING COMMA ABOVE RIGHT"),
    ("\u055A", "ARMENIAN APOSTROPHE"),
    ("\u05F3", "HEBREW PUNCTUATION GERESH"),
    ("\u07F4", "NKO HIGH TONE APOSTROPHE"),
    ("\u07F5", "NKO LOW TONE APOSTROPHE"),
    ("\uFF07", "FULLWIDTH APOSTROPHE"),
    ("\u1FBF", "GREEK PSILI"),
    ("\u1FBD", "GREEK KORONIS"),
    ("\uA78C", "LATIN SMALL LETTER SALTILLO"),
]


class TestBNCFrequencyWithCurlyApostrophe:
    """Integration tests for BNC frequency analysis with curly apostrophe (U+2019).

    This is the most common smart quote apostrophe found in ebooks and word processors.
    """

    def test_dont_with_curly_apostrophe_is_found(self):
        """Test that 'don't' with curly apostrophe (U+2019) is found in BNC.

        This is the primary use case from Issue #45.
        """
        text = "I don\u2019t know what to say."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "don't" not in not_found_words, "don't with curly apostrophe was not normalized"

    def test_wont_with_curly_apostrophe_is_found(self):
        """Test that 'won't' with curly apostrophe is found in BNC."""
        text = "I won\u2019t do that."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "won't" not in not_found_words

    def test_cant_with_curly_apostrophe_is_found(self):
        """Test that 'can't' with curly apostrophe is found in BNC."""
        text = "I can\u2019t believe it."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "can't" not in not_found_words

    def test_its_with_curly_apostrophe_is_found(self):
        """Test that 'it's' with curly apostrophe is found in BNC."""
        text = "It\u2019s a beautiful day."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "it's" not in not_found_words

    def test_im_with_curly_apostrophe_normalizes(self):
        """Test that 'I'm' with curly apostrophe normalizes to ASCII apostrophe.

        Note: 'i'm' is NOT in the BNC corpus, but normalization should still work.
        We verify the normalized form appears in results (in not_in_bnc list).
        """
        text = "I\u2019m very happy today."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        # Verify normalization worked - the word appears with ASCII apostrophe
        assert "i'm" in not_found_words, "i'm should be normalized (even though not in BNC)"

    def test_youre_with_curly_apostrophe_normalizes(self):
        """Test that 'you're' with curly apostrophe normalizes to ASCII apostrophe.

        Note: 'you're' is NOT in the BNC corpus, but normalization should still work.
        """
        text = "You\u2019re absolutely right."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        # Verify normalization worked - the word appears with ASCII apostrophe
        assert "you're" in not_found_words, "you're should be normalized (even though not in BNC)"

    def test_theyre_with_curly_apostrophe_normalizes(self):
        """Test that 'they're' with curly apostrophe normalizes to ASCII apostrophe.

        Note: 'they're' is NOT in the BNC corpus, but normalization should still work.
        """
        text = "They\u2019re coming tomorrow."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        # Verify normalization worked - the word appears with ASCII apostrophe
        assert "they're" in not_found_words, "they're should be normalized (even though not in BNC)"

    def test_weve_with_curly_apostrophe_normalizes(self):
        """Test that 'we've' with curly apostrophe normalizes to ASCII apostrophe.

        Note: 'we've' is NOT in the BNC corpus, but normalization should still work.
        """
        text = "We\u2019ve been waiting for hours."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        # Verify normalization worked - the word appears with ASCII apostrophe
        assert "we've" in not_found_words, "we've should be normalized (even though not in BNC)"

    def test_thats_with_curly_apostrophe_is_found(self):
        """Test that 'that's' with curly apostrophe is found in BNC."""
        text = "That\u2019s exactly what I meant."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "that's" not in not_found_words

    def test_couldnt_with_curly_apostrophe_is_found(self):
        """Test that 'couldn't' with curly apostrophe is found in BNC."""
        text = "I couldn\u2019t understand what happened."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "couldn't" not in not_found_words

    def test_wouldnt_with_curly_apostrophe_is_found(self):
        """Test that 'wouldn't' with curly apostrophe is found in BNC."""
        text = "She wouldn\u2019t tell me the truth."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "wouldn't" not in not_found_words

    def test_shouldnt_with_curly_apostrophe_is_found(self):
        """Test that 'shouldn't' with curly apostrophe is found in BNC."""
        text = "You shouldn\u2019t do that."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "shouldn't" not in not_found_words


class TestBNCFrequencyWithOtherApostropheVariants:
    """Tests for BNC frequency analysis with other apostrophe variants."""

    def test_dont_with_grave_accent(self):
        """Test 'don't' with grave accent (U+0060) - common keyboard error."""
        text = "I don`t know."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "don't" not in not_found_words

    def test_dont_with_acute_accent(self):
        """Test 'don't' with acute accent (U+00B4) - common keyboard error."""
        text = "I don\u00B4t know."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "don't" not in not_found_words

    def test_dont_with_left_single_quotation_mark(self):
        """Test 'don't' with left single quotation mark (U+2018)."""
        text = "I don\u2018t know."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "don't" not in not_found_words

    def test_dont_with_modifier_letter_apostrophe(self):
        """Test 'don't' with modifier letter apostrophe (U+02BC)."""
        text = "I don\u02BCt know."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "don't" not in not_found_words

    def test_dont_with_fullwidth_apostrophe(self):
        """Test 'don't' with fullwidth apostrophe (U+FF07)."""
        text = "I don\uFF07t know."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "don't" not in not_found_words


class TestBNCFrequencyMultipleContractions:
    """Tests for multiple contractions with apostrophe variants."""

    def test_multiple_contractions_same_variant(self):
        """Test multiple contractions with same apostrophe variant."""
        text = """
        I don\u2019t know why they won\u2019t listen.
        It\u2019s clear that we can\u2019t continue like this.
        They\u2019re not going to change, and I\u2019m tired.
        """
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]

        # Contractions that ARE in BNC
        in_bnc = ["don't", "won't", "it's", "can't"]
        for contraction in in_bnc:
            assert contraction not in not_found_words, f"{contraction} should be found in BNC"

        # Contractions that are NOT in BNC but should be normalized
        not_in_bnc_but_normalized = ["they're", "i'm"]
        for contraction in not_in_bnc_but_normalized:
            assert contraction in not_found_words, f"{contraction} should be in not_in_bnc (normalized form)"

    def test_multiple_contractions_mixed_variants(self):
        """Test multiple contractions with different apostrophe variants."""
        text = "I don\u2019t know but I can`t help. She won\u00B4t go."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]

        assert "don't" not in not_found_words
        assert "can't" not in not_found_words
        assert "won't" not in not_found_words

    def test_mixed_ascii_and_unicode_apostrophes(self):
        """Test text with both ASCII and Unicode apostrophes."""
        text = "I don't know but she doesn\u2019t care."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]

        assert "don't" not in not_found_words
        assert "doesn't" not in not_found_words


class TestBNCFrequencyRealWorldEbookText:
    """Tests simulating real-world ebook text with typographic quotes."""

    def test_master_and_commander_style_text(self):
        """Test text styled like Patrick O'Brian's 'Master and Commander'.

        This is the specific use case from Issue #45.
        """
        text = """
        \u201CYou don\u2019t think so?\u201D said Jack, putting down his glass.
        \u201CI won\u2019t pretend to understand,\u201D Stephen said quietly.
        \u201CIt\u2019s the captain\u2019s duty to see that all is well.\u201D
        \u201CThey\u2019ve been at it since dawn,\u201D said the bosun.
        \u201CWe can\u2019t wait much longer,\u201D Jack replied.
        """
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]

        # Contractions that ARE in BNC
        in_bnc = ["don't", "won't", "it's", "can't"]
        for c in in_bnc:
            assert c not in not_found_words, f"'{c}' should be found in BNC"

        # "they've" is NOT in BNC but should be normalized correctly
        assert "they've" in not_found_words, "they've should be normalized (even though not in BNC)"

    def test_kindle_style_text(self):
        """Test text converted from Kindle format with various quote styles."""
        text = """
        She said, \u201CI\u2019m not sure what you\u2019re talking about.\u201D
        He replied, \u201CWe\u2019ve discussed this before. It\u2019s not complicated.\u201D
        \u201CThat\u2019s what you think,\u201D she muttered.
        """
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]

        # Contractions that ARE in BNC
        assert "it's" not in not_found_words
        assert "that's" not in not_found_words

        # Contractions NOT in BNC but should be normalized
        assert "i'm" in not_found_words, "i'm should be normalized (even though not in BNC)"
        assert "you're" in not_found_words, "you're should be normalized (even though not in BNC)"
        assert "we've" in not_found_words, "we've should be normalized (even though not in BNC)"

    def test_pdf_extraction_text(self):
        """Test text extracted from PDF (often has inconsistent quote styles)."""
        text = """
        The captain\u2019s orders were clear: "Don't engage."
        But the lieutenant couldn\u00B4t resist. "I won`t back down," he said.
        """
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]

        assert "don't" not in not_found_words
        assert "couldn't" not in not_found_words
        assert "won't" not in not_found_words

    def test_word_processor_smart_quotes(self):
        """Test text from word processors with smart quotes enabled."""
        text = """
        \u201CWhere\u2019s everyone?\u201D asked Tom.
        \u201CI don\u2019t know,\u201D replied Sarah. \u201CThey\u2019ve all gone home.\u201D
        \u201CThat\u2019s strange. It\u2019s only three o\u2019clock.\u201D
        """
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]

        # Contractions that ARE in BNC
        assert "don't" not in not_found_words
        assert "that's" not in not_found_words
        assert "it's" not in not_found_words

        # Contractions NOT in BNC but should be normalized
        assert "where's" in not_found_words, "where's should be normalized (even though not in BNC)"
        assert "they've" in not_found_words, "they've should be normalized (even though not in BNC)"


class TestBNCFrequencyPossessives:
    """Tests for possessive forms with apostrophe variants."""

    def test_singular_possessive_curly(self):
        """Test singular possessive with curly apostrophe."""
        text = "John\u2019s book is on the table."
        result = compute_bnc_frequency(text, include_wordnet=False)
        # Just verify no crash; possessive may or may not be in BNC
        assert result is not None

    def test_plural_possessive_curly(self):
        """Test plural possessive with curly apostrophe."""
        text = "The dogs\u2019 toys were scattered."
        result = compute_bnc_frequency(text, include_wordnet=False)
        assert result is not None


class TestBNCFrequencyEdgeCases:
    """Edge case tests for BNC frequency with apostrophe normalization."""

    def test_word_starting_with_apostrophe(self):
        """Test words starting with apostrophe variant (e.g., 'twas)."""
        text = "\u2019twas a dark and stormy night"
        result = compute_bnc_frequency(text, include_wordnet=False)
        assert result is not None

    def test_multiple_apostrophes_in_word(self):
        """Test words with multiple apostrophes (e.g., rock 'n' roll)."""
        text = "I love rock \u2019n\u2019 roll"
        result = compute_bnc_frequency(text, include_wordnet=False)
        assert result is not None

    def test_apostrophe_at_sentence_boundaries(self):
        """Test apostrophes near sentence boundaries."""
        text = "\u2019Hello,\u2019 she said. \u2018How are you?\u2019"
        result = compute_bnc_frequency(text, include_wordnet=False)
        assert result is not None

    def test_empty_string(self):
        """Empty string should work without errors."""
        result = compute_bnc_frequency("", include_wordnet=False)
        assert result is not None
        assert result.total_tokens == 0

    def test_text_without_apostrophes(self):
        """Text without apostrophes should work normally."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_bnc_frequency(text, include_wordnet=False)
        assert result is not None
        assert result.total_tokens > 0


class TestBNCFrequencyParameterizedApostropheVariants:
    """Parameterized tests across all apostrophe variants."""

    @pytest.mark.parametrize("variant,name", EXPECTED_APOSTROPHE_VARIANTS)
    def test_dont_with_all_variants(self, variant, name):
        """Test 'don't' normalizes correctly with each apostrophe variant."""
        text = f"I don{variant}t know."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "don't" not in not_found_words, f"Failed for {name} (U+{ord(variant):04X})"

    @pytest.mark.parametrize("variant,name", EXPECTED_APOSTROPHE_VARIANTS[:6])  # Top 6 most common
    def test_common_contractions_with_priority_variants(self, variant, name):
        """Test common contractions with priority apostrophe variants.

        Tests both contractions that ARE in BNC and ones that are NOT.
        The key is that normalization works correctly for all of them.
        """
        # Contractions that ARE in BNC
        in_bnc_contractions = [
            (f"don{variant}t", "don't"),
            (f"won{variant}t", "won't"),
            (f"can{variant}t", "can't"),
            (f"it{variant}s", "it's"),
        ]

        for input_word, expected_normalized in in_bnc_contractions:
            text = f"Test word: {input_word}"
            result = compute_bnc_frequency(text, include_wordnet=False)

            not_found_words = [w.word for w in result.not_in_bnc]
            assert expected_normalized not in not_found_words, (
                f"'{expected_normalized}' should be found in BNC when using {name} in '{input_word}'"
            )

        # Contractions NOT in BNC - verify normalization still works
        not_in_bnc_contractions = [
            (f"I{variant}m", "i'm"),
        ]

        for input_word, expected_normalized in not_in_bnc_contractions:
            text = f"Test word: {input_word}"
            result = compute_bnc_frequency(text, include_wordnet=False)

            not_found_words = [w.word for w in result.not_in_bnc]
            assert expected_normalized in not_found_words, (
                f"'{expected_normalized}' should be normalized (in not_in_bnc) when using {name} in '{input_word}'"
            )


class TestBNCFrequencyCountingWithApostrophes:
    """Tests to verify word counting is correct after apostrophe normalization."""

    def test_same_word_different_apostrophes_counted_together(self):
        """Words with different apostrophe variants should be counted as same word."""
        # "don't" appears twice with different apostrophes
        text = "I don\u2019t know. She doesn\u2019t know. They don`t know. We don't know."
        result = compute_bnc_frequency(text, include_wordnet=False)

        # Find "don't" in overused, underused, or check it's not in not_in_bnc
        all_words = (
            [w for w in result.overused]
            + [w for w in result.underused]
            + [w for w in result.not_in_bnc]
        )

        dont_analyses = [w for w in all_words if w.word == "don't"]

        # There should be exactly one entry for "don't" with count reflecting all occurrences
        assert len(dont_analyses) <= 1, "don't should appear at most once (unified)"

        # If found, count should be 3 (don't appears 3 times: curly, grave, ascii)
        if dont_analyses:
            assert dont_analyses[0].observed == 3, "don't should be counted 3 times"

    def test_observed_count_is_correct_after_normalization(self):
        """Verify observed word count is accurate after normalization."""
        # "it's" appears 5 times with curly apostrophes
        text = "It\u2019s good. It\u2019s fine. It\u2019s okay. It\u2019s nice. It\u2019s great."
        result = compute_bnc_frequency(text, include_wordnet=False)

        all_words = (
            list(result.overused) + list(result.underused) + list(result.not_in_bnc)
        )

        its_analyses = [w for w in all_words if w.word == "it's"]

        if its_analyses:
            assert its_analyses[0].observed == 5, "it's should be observed 5 times"


class TestBNCFrequencyNormalizationConsistency:
    """Tests to verify normalization produces consistent results."""

    def test_ascii_apostrophe_unchanged(self):
        """ASCII apostrophe should work correctly (not over-normalized)."""
        text = "I don't know."
        result = compute_bnc_frequency(text, include_wordnet=False)

        not_found_words = [w.word for w in result.not_in_bnc]
        assert "don't" not in not_found_words

    def test_double_processing_gives_same_result(self):
        """Running the same text twice should give consistent results."""
        text = "I don\u2019t know what they\u2019re thinking."

        result1 = compute_bnc_frequency(text, include_wordnet=False)
        result2 = compute_bnc_frequency(text, include_wordnet=False)

        # Same number of not-in-bnc words
        assert len(result1.not_in_bnc) == len(result2.not_in_bnc)

        # Same words in not_in_bnc
        words1 = {w.word for w in result1.not_in_bnc}
        words2 = {w.word for w in result2.not_in_bnc}
        assert words1 == words2

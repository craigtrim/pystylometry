"""Comprehensive tests for Gunning Fog Index computation."""

from pathlib import Path

import pytest

from pystylometry.readability import compute_gunning_fog


class TestGunningFogBasic:
    """Test basic Gunning Fog functionality."""

    def test_simple_sentence(self):
        """Test single simple sentence."""
        text = "The cat sat on the mat."
        result = compute_gunning_fog(text)

        assert isinstance(result.fog_index, float)
        assert isinstance(result.grade_level, int)
        assert result.grade_level >= 0
        assert result.grade_level <= 20
        assert not result.metadata["reliable"]  # < 100 words and < 3 sentences

    def test_expected_values(self):
        """Test known expected values for calibration."""
        # From docstring example
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_gunning_fog(text)

        # Should match docstring example
        assert abs(result.fog_index - 4.0) < 0.1  # Allow small tolerance
        assert result.grade_level == 4
        assert not result.metadata["reliable"]

    def test_reliable_text(self):
        """Test text that meets reliability threshold."""
        # Generate text with 100+ words and 3+ sentences
        words = ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        sentences = [" ".join(words) + "." for _ in range(12)]  # 12 sentences, 108 words
        text = " ".join(sentences)

        result = compute_gunning_fog(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] >= 100
        assert result.metadata["sentence_count"] >= 3


class TestGunningFogEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test empty string input."""
        import math

        result = compute_gunning_fog("")

        # After NaN fix: empty input returns NaN, not 0.0
        assert math.isnan(result.fog_index)
        assert math.isnan(result.grade_level)
        assert result.metadata["sentence_count"] == 0
        assert result.metadata["word_count"] == 0
        assert result.metadata["complex_word_count"] == 0
        assert result.metadata["complex_word_percentage"] == 0.0
        assert result.metadata["average_words_per_sentence"] == 0.0
        assert not result.metadata["reliable"]

    def test_whitespace_only(self):
        """Test string with only whitespace."""
        import math

        result = compute_gunning_fog("   \n\t  ")

        # After NaN fix: whitespace-only input returns NaN, not 0.0
        assert math.isnan(result.fog_index)
        assert math.isnan(result.grade_level)
        assert not result.metadata["reliable"]

    def test_very_simple_text(self):
        """Test extremely simple text."""
        text = "Go. Run. Stop. Hi."
        result = compute_gunning_fog(text)

        # Should be low grade level
        assert result.grade_level <= 5
        assert result.metadata["complex_word_count"] == 0

    def test_single_word(self):
        """Test single word."""
        result = compute_gunning_fog("Hello")

        assert result.metadata["word_count"] == 1
        assert result.metadata["sentence_count"] >= 0
        assert not result.metadata["reliable"]


class TestGunningFogComplexWords:
    """Test complex word identification."""

    def test_simple_words_not_complex(self):
        """Test that simple words are not counted as complex."""
        text = "The cat sat on the mat."
        result = compute_gunning_fog(text)

        assert result.metadata["complex_word_count"] == 0
        assert result.metadata["complex_word_percentage"] == 0.0

    def test_polysyllabic_words_complex(self):
        """Test that 3+ syllable words are complex."""
        text = "The situation is unfortunate."
        result = compute_gunning_fog(text)

        # "situation" (4 syllables) and "unfortunate" (4 syllables) should be complex
        assert result.metadata["complex_word_count"] >= 2

    def test_hyphenated_words_excluded(self):
        """Test that hyphenated compounds are not counted as complex."""
        text = "The well-known twenty-first-century state-of-the-art solution."
        result = compute_gunning_fog(text)

        # Hyphenated words should be excluded from complex count
        # Even though they have 3+ syllables
        assert result.metadata["complex_word_count"] == 1  # Only "solution" (3 syllables)

    def test_proper_nouns_excluded(self):
        """Test that proper nouns (capitalized) are excluded."""
        text = "The American Revolution began in seventeen seventy-five."
        result = compute_gunning_fog(text)

        # "American" (4 syllables) and "Revolution" (4 syllables) should be excluded
        # Only "seventeen" (3 syllables) should count
        assert result.metadata["complex_word_count"] <= 1

    def test_inflectional_suffixes(self):
        """Test handling of -es, -ed, -ing suffixes."""
        # Words with suffixes that still have 3+ syllables in base
        text = "The running jumping skipping children were playing happily."
        result = compute_gunning_fog(text)

        # "running" (2 syllables, -1 for -ing = 1, not complex)
        # "jumping" (2 syllables, -1 for -ing = 1, not complex)
        # "skipping" (2 syllables, -1 for -ing = 1, not complex)
        # "children" (2 syllables, not complex)
        # "playing" (2 syllables, -1 for -ing = 1, not complex)
        # "happily" (3 syllables, complex)
        assert result.metadata["complex_word_count"] >= 1


class TestGunningFogRounding:
    """Test rounding behavior and boundary values."""

    def test_grade_level_is_integer(self):
        """Verify grade level is always an integer."""
        texts = [
            "The cat sat on the mat.",
            "A very long and complex sentence with many subordinate clauses.",
            "Go.",
        ]

        for text in texts:
            result = compute_gunning_fog(text)
            assert isinstance(result.grade_level, int)

    def test_lower_bound_clamping(self):
        """Test that very simple text is clamped to grade 0."""
        simple = "Go. Run. Stop."
        result = compute_gunning_fog(simple)

        assert result.grade_level >= 0

    def test_upper_bound_clamping(self):
        """Test that very high fog index is clamped to grade 20."""
        # Create extremely complex text with very long words and long sentences
        complex_words = [
            "antidisestablishmentarianism",
            "supercalifragilisticexpialidocious",
            "pneumonoultramicroscopicsilicovolcanoconiosis",
        ]
        # One very long sentence
        text = " ".join(complex_words * 50) + "."

        result = compute_gunning_fog(text)
        assert result.grade_level <= 20


class TestGunningFogMetadata:
    """Test metadata structure and consistency."""

    def test_metadata_keys_consistent(self):
        """Verify all metadata keys are present regardless of input.

        API Enhancement (PR #4): Added transparency fields for complex word detection
        =================================================================================
        The metadata now includes additional fields to document which detection mode
        was used and how proper nouns/inflections were handled:

        - mode: "enhanced" (spaCy NLP) or "basic" (heuristics) or "none" (empty input)
        - proper_noun_detection: Method used (e.g., "POS-based" or "Capitalization-based")
        - inflection_handling: Method used (e.g., "Lemmatization" or "Suffix-stripping")

        These fields provide transparency into the complex word detection process,
        allowing users to verify which mode was active and assess result reliability.

        Reference: https://github.com/craigtrim/pystylometry/pull/4
        See: gunning_fog.py and complex_words.py for implementation details
        """
        test_cases = [
            "",  # Empty
            "Hello",  # Single word
            "The cat sat on the mat.",  # Simple sentence
            " ".join(["word"] * 200) + ".",  # Long text
        ]

        # Core metrics (always present)
        core_keys = {
            "sentence_count",
            "word_count",
            "complex_word_count",
            "complex_word_percentage",
            "average_words_per_sentence",
            "reliable",
        }

        # Transparency fields added in PR #4 for complex word detection
        transparency_keys = {
            "mode",  # Detection mode: "enhanced", "basic", or "none"
            "proper_noun_detection",  # How proper nouns were detected
            "inflection_handling",  # How inflections were handled
        }

        expected_keys = core_keys | transparency_keys  # Union of both sets

        for text in test_cases:
            result = compute_gunning_fog(text)
            actual_keys = set(result.metadata.keys())

            # All expected keys must be present
            assert expected_keys.issubset(actual_keys), (
                f"Missing keys: {expected_keys - actual_keys}. "
                f"Text: {text[:50]}..."
            )

            # Note: May have additional keys like 'spacy_model' in enhanced mode
            # So we check subset rather than exact equality

    def test_metadata_values_sensible(self):
        """Test that metadata values are within sensible ranges."""
        text = "The quick brown fox jumps over the lazy dog. The end."
        result = compute_gunning_fog(text)

        # Counts should be non-negative
        assert result.metadata["sentence_count"] >= 0
        assert result.metadata["word_count"] >= 0
        assert result.metadata["complex_word_count"] >= 0

        # Percentages should be 0-100
        assert 0 <= result.metadata["complex_word_percentage"] <= 100

        # Average should be non-negative
        assert result.metadata["average_words_per_sentence"] >= 0

        # Reliable should be boolean
        assert isinstance(result.metadata["reliable"], bool)

    def test_complex_word_percentage_calculation(self):
        """Verify complex word percentage is calculated correctly."""
        # 10 words, 2 complex
        text = "The situation is unfortunate but manageable today."
        result = compute_gunning_fog(text)

        if result.metadata["word_count"] > 0:
            expected_pct = (
                result.metadata["complex_word_count"] / result.metadata["word_count"]
            ) * 100
            assert abs(result.metadata["complex_word_percentage"] - expected_pct) < 0.01


class TestGunningFogUnicode:
    """Test Unicode character handling."""

    def test_unicode_letters(self):
        """Test that Unicode letters are handled."""
        text = "Café résumé naïve façade."
        result = compute_gunning_fog(text)

        # Should complete without error
        assert result.fog_index is not None
        assert result.grade_level >= 0

    def test_non_latin_scripts(self):
        """Test handling of non-Latin scripts."""
        # Greek
        text_greek = "Γεια σου κόσμε"
        result = compute_gunning_fog(text_greek)
        assert result.metadata["word_count"] > 0

        # Cyrillic
        text_cyrillic = "Привет мир"
        result = compute_gunning_fog(text_cyrillic)
        assert result.metadata["word_count"] > 0


class TestGunningFogSpecialCases:
    """Test special input cases."""

    def test_urls_and_emails(self):
        """Test handling of URLs and email addresses."""
        text = "Visit https://example.com or email user@example.com for info."
        result = compute_gunning_fog(text)

        # Should complete without error
        assert result.fog_index is not None
        assert result.grade_level >= 0

    def test_numbers_in_text(self):
        """Test handling of numbers."""
        text = "In 2023, the company had 500 employees and revenue of $1,000,000."
        result = compute_gunning_fog(text)

        # Should complete without error
        assert result.fog_index is not None

    def test_contractions(self):
        """Test handling of contractions."""
        text = "I can't believe it's already over. They're leaving soon."
        result = compute_gunning_fog(text)

        # Should handle contractions naturally
        assert result.metadata["word_count"] >= 1
        assert result.grade_level >= 0


class TestGunningFogFormula:
    """Test formula correctness."""

    def test_formula_components(self):
        """Verify formula components are calculated correctly."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_gunning_fog(text)

        avg_words = result.metadata["average_words_per_sentence"]
        complex_pct = result.metadata["complex_word_percentage"]

        # Manual calculation: Fog = 0.4 × (avg_words + complex_pct)
        expected_fog = 0.4 * (avg_words + complex_pct)

        # Should match within floating point precision
        assert abs(result.fog_index - expected_fog) < 0.0001

    def test_longer_sentences_increase_score(self):
        """Test that longer sentences increase fog index."""
        short_sentences = "The cat sat. The dog ran. The bird flew."
        long_sentence = "The cat sat on the mat while the dog ran around the yard and the bird flew overhead."

        result_short = compute_gunning_fog(short_sentences)
        result_long = compute_gunning_fog(long_sentence)

        # Longer average sentence length should produce higher score
        assert result_long.metadata["average_words_per_sentence"] > result_short.metadata[
            "average_words_per_sentence"
        ]

    def test_complex_words_increase_score(self):
        """Test that complex words increase fog index."""
        simple = "The cat sat on the mat and ate the food."
        complex_text = "The situation necessitated extraordinary consideration."

        result_simple = compute_gunning_fog(simple)
        result_complex = compute_gunning_fog(complex_text)

        # More complex words should produce higher percentage
        assert result_complex.metadata["complex_word_percentage"] > result_simple.metadata[
            "complex_word_percentage"
        ]


class TestGunningFogGutenbergTexts:
    """Test with real literary texts from Project Gutenberg."""

    @pytest.fixture
    def fixtures_dir(self) -> Path:
        """Get path to test fixtures directory."""
        return Path(__file__).parent / "fixtures"

    def test_hound_of_baskervilles(self, fixtures_dir: Path):
        """Test with The Hound of the Baskervilles."""
        text_path = fixtures_dir / "doyle-the-hound-of-the-baskervilles.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_gunning_fog(text)

        # Doyle's writing style is accessible despite Victorian era
        # Longer sentences increase fog index
        assert result.grade_level >= 5
        assert result.grade_level <= 14
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] > 10000

    def test_sign_of_four(self, fixtures_dir: Path):
        """Test with The Sign of the Four."""
        text_path = fixtures_dir / "doyle-the-sign-of-the-four.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_gunning_fog(text)

        assert result.grade_level >= 5
        assert result.metadata["reliable"]

    def test_valley_of_fear(self, fixtures_dir: Path):
        """Test with The Valley of Fear."""
        text_path = fixtures_dir / "doyle-the-valley-of-fear.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_gunning_fog(text)

        assert result.grade_level >= 5
        assert result.metadata["reliable"]

    def test_gutenberg_consistency(self, fixtures_dir: Path):
        """Test that Doyle texts show consistent grade levels."""
        texts = [
            "doyle-the-hound-of-the-baskervilles.txt",
            "doyle-the-sign-of-the-four.txt",
            "doyle-the-valley-of-fear.txt",
        ]

        results = []
        for filename in texts:
            text_path = fixtures_dir / filename
            if not text_path.exists():
                continue

            with open(text_path) as f:
                text = f.read()

            result = compute_gunning_fog(text)
            results.append((filename, result.grade_level))

        if len(results) < 2:
            pytest.skip("Not enough fixtures for consistency test")

        # All should be within a reasonable range (same author, similar era)
        grade_levels = [r[1] for r in results]
        assert max(grade_levels) - min(grade_levels) <= 4  # Within 4 grade levels


class TestGunningFogComplexityLevels:
    """Test across various text complexity levels."""

    def test_children_book_simple(self):
        """Test very simple children's book style text."""
        text = """
        The cat is big. The dog is small. They play together.
        The cat runs fast. The dog runs too. They are friends.
        The sun is out. It is a nice day. They have fun.
        """
        result = compute_gunning_fog(text)

        # Should be low grade level
        assert result.grade_level <= 5

    def test_middle_school_text(self):
        """Test middle school level text."""
        text = """
        The American Revolution began in 1775 when colonists rebelled against
        British rule. They were angry about taxes and wanted independence.
        Important leaders like George Washington and Thomas Jefferson helped
        guide the colonists to victory. The war ended in 1783, and America
        became a new nation.
        """
        result = compute_gunning_fog(text)

        # Should be middle grade level
        assert 8 <= result.grade_level <= 12

    def test_academic_text(self):
        """Test academic/technical text."""
        text = """
        The phenomenological hermeneutics of continental philosophy necessitates
        a comprehensive understanding of existential ontology. Heidegger's
        deconstruction of metaphysical presuppositions requires epistemological
        rigor and methodological consistency. The intersubjective constitution
        of meaning emerges through dialectical engagement with transcendental
        subjectivity.
        """
        result = compute_gunning_fog(text)

        # Should be high grade level
        assert result.grade_level >= 15


class TestGunningFogSentenceInitialWords:
    """Test handling of sentence-initial complex words."""

    def test_sentence_initial_complex_word_counted(self):
        """Sentence-initial complex words should be counted."""
        # "Unfortunately" is complex (5 syllables) and starts sentences
        text = "Unfortunately, this happened. Unfortunately, that happened too."
        result = compute_gunning_fog(text)

        # After fix: Sentence-initial complex words should be counted
        assert result.metadata["complex_word_count"] >= 2, (
            "Sentence-initial complex words should be counted"
        )

    def test_mid_sentence_proper_noun_excluded(self):
        """Only true proper nouns (mid-sentence caps) should be excluded."""
        text = "I visited Philadelphia and Massachusetts last summer."
        result = compute_gunning_fog(text)

        # "Philadelphia" (5 syl) and "Massachusetts" (5 syl) are proper nouns
        # and correctly excluded
        assert result.metadata["complex_word_count"] == 0

    def test_sentence_initial_vs_proper_noun(self):
        """Test distinction between sentence-initial and proper nouns."""
        # Sentence-initial complex word
        text1 = "Complicated situations arise frequently."
        result1 = compute_gunning_fog(text1)

        # Mid-sentence capitalized (proper noun) with only simple words otherwise
        text2 = "The big American cat was here."
        result2 = compute_gunning_fog(text2)

        # Sentence-initial should be counted
        assert result1.metadata["complex_word_count"] >= 2  # "Complicated", "situations"
        # Mid-sentence capitalized "American" (4 syl) should be excluded, others simple
        assert result2.metadata["complex_word_count"] == 0


class TestGunningFogSuffixEdgeCases:
    """Test suffix handling edge cases."""

    def test_silent_ed_suffix(self):
        """Words where -ed adds no syllable."""
        # "complicated" = 4 syllables, -ed is not a separate syllable
        # Subtracting 1 would make it 3, still complex
        # "elevated" = 4 syllables, subtracting 1 = 3, borderline
        text = "The elevated platform was complicated."
        result = compute_gunning_fog(text)

        # Both should be complex (4 syllables each, adjusted to 3)
        assert result.metadata["complex_word_count"] >= 2

    def test_ing_suffix_base_word_boundary(self):
        """Test -ing words at complexity boundary."""
        # "beginning" = 3 syllables, -1 adjustment = 2, not complex
        # "interesting" = 3 syllables, -1 adjustment = 2, not complex
        text = "The beginning was interesting and overwhelming."
        result = compute_gunning_fog(text)

        # "overwhelming" = 4 syl (3 after adjustment, IS complex)
        # "beginning" and "interesting" = 3 syl each (2 after adjustment, NOT complex)
        assert result.metadata["complex_word_count"] >= 1

    def test_es_suffix_handling(self):
        """Test -es suffix handling."""
        # "boxes" = 2 syllables (box + es)
        # "matches" = 2 syllables (match + es)
        # "reaches" = 2 syllables (reach + es)
        text = "The boxes and matches and reaches were counted."
        result = compute_gunning_fog(text)

        # All are 2 syllables, -1 adjustment = 1, not complex
        assert result.metadata["complex_word_count"] == 0


class TestGunningFogEmptyInputConsistency:
    """Test empty input handling matches Flesch/SMOG convention."""

    def test_empty_returns_nan_not_zero(self):
        """Empty input should return NaN, not 0.0."""
        result = compute_gunning_fog("")

        # After fix: Should return NaN like Flesch and SMOG
        # 0.0 is a valid fog index (extremely simple text)
        # NaN correctly indicates "undefined"
        import math

        assert math.isnan(result.fog_index), "Empty input should return NaN, not 0.0"
        assert math.isnan(result.grade_level), (
            "Empty input grade level should be NaN, not 0"
        )

    def test_whitespace_returns_nan(self):
        """Whitespace-only input should return NaN."""
        result = compute_gunning_fog("   \n\t  ")

        import math

        assert math.isnan(result.fog_index)
        assert math.isnan(result.grade_level)


class TestGunningFogHyphenationEdgeCases:
    """Test hyphenation exclusion edge cases."""

    def test_prefix_hyphenation(self):
        """Prefix-hyphenated words should be excluded."""
        # "anti-establishment" - hyphenated so excluded
        # Current logic excludes ALL hyphenated words
        text = "The anti-establishment and pro-democracy revolutionary groups grew."
        result = compute_gunning_fog(text)

        # Documents current behavior: all hyphenated excluded
        # "revolutionary" = 5 syllables, complex
        # "movements" = 2 syllables, NOT complex
        assert result.metadata["complex_word_count"] == 1  # only "revolutionary"

    def test_hyphen_in_numbers(self):
        """Hyphenated numbers should be handled."""
        text = "Twenty-three and forty-five are numbers."
        result = compute_gunning_fog(text)

        # Should not crash; hyphenated numbers excluded from complex
        assert result.fog_index >= 0
        # Hyphenated compounds excluded
        assert result.metadata["complex_word_count"] == 0

    def test_multiple_hyphens(self):
        """Test words with multiple hyphens."""
        text = "The state-of-the-art mother-in-law solution."
        result = compute_gunning_fog(text)

        # All hyphenated words excluded
        # "solution" = 3 syllables, IS complex
        assert result.metadata["complex_word_count"] == 1  # "solution"


class TestGunningFogAllCapsWords:
    """Test handling of acronyms and all-caps words."""

    def test_acronym_handling(self):
        """All-caps acronyms should be handled consistently."""
        text = "The UNESCO and NATO representatives met with INTERPOL."
        result = compute_gunning_fog(text)

        # All start with caps, so excluded as "proper nouns"
        # Acronyms aren't proper nouns per se, but this is current behavior
        assert result.metadata["complex_word_count"] == 1  # "representatives"

    def test_shouting_text(self):
        """All-caps sentences should be handled."""
        text = "UNFORTUNATELY THE SITUATION IS COMPLICATED."
        result = compute_gunning_fog(text)

        # Degenerate case: All words capitalized
        # Only "UNFORTUNATELY" is sentence-initial (counted)
        # "SITUATION" and "COMPLICATED" are mid-sentence caps (excluded as "proper nouns")
        # This documents a limitation of the capitalization heuristic
        assert result.fog_index >= 0
        # Only sentence-initial "UNFORTUNATELY" (5 syl) is counted
        assert result.metadata["complex_word_count"] == 1

    def test_mixed_case_acronyms(self):
        """Test mixed-case acronyms and abbreviations."""
        text = "The PhD and CEO discussed the API."
        result = compute_gunning_fog(text)

        # Should complete without error
        assert result.fog_index >= 0


class TestGunningFogReliability:
    """Test reliability flag behavior."""

    def test_reliability_threshold_words(self):
        """Test reliability requires 100+ words."""
        # 99 tokens with 3 sentences (96 words + 3 periods = 99 tokens)
        text_99 = " ".join(["word"] * 32) + ". " + " ".join(["word"] * 32) + ". " + " ".join(
            ["word"] * 32
        ) + "."
        result = compute_gunning_fog(text_99)
        assert not result.metadata["reliable"]
        assert result.metadata["word_count"] == 99

        # 100+ tokens with 3 sentences (97 words + 3 periods = 100 tokens)
        text_100 = " ".join(["word"] * 33) + ". " + " ".join(["word"] * 32) + ". " + " ".join(
            ["word"] * 32
        ) + "."
        result = compute_gunning_fog(text_100)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] == 100

    def test_reliability_threshold_sentences(self):
        """Test reliability requires 3+ sentences."""
        # 100+ words but only 2 sentences
        text_2_sent = " ".join(["word"] * 50) + ". " + " ".join(["word"] * 50) + "."
        result = compute_gunning_fog(text_2_sent)
        assert not result.metadata["reliable"]

        # 100+ words with 3 sentences
        text_3_sent = (
            " ".join(["word"] * 34)
            + ". "
            + " ".join(["word"] * 34)
            + ". "
            + " ".join(["word"] * 34)
            + "."
        )
        result = compute_gunning_fog(text_3_sent)
        assert result.metadata["reliable"]

    def test_reliability_flag_type(self):
        """Verify reliability is always a boolean."""
        texts = ["", "Short.", " ".join(["word"] * 200) + "."]

        for text in texts:
            result = compute_gunning_fog(text)
            assert isinstance(result.metadata["reliable"], bool)

"""Comprehensive tests for Automated Readability Index (ARI) computation."""

import math
from pathlib import Path

import pytest

from pystylometry.readability import compute_ari


class TestARIBasic:
    """Test basic ARI functionality."""

    def test_simple_sentence(self):
        """Test single simple sentence."""
        text = "The cat sat on the mat."
        result = compute_ari(text)

        assert isinstance(result.ari_score, float)
        assert isinstance(result.grade_level, (int, float))  # Float for chunked mean
        assert isinstance(result.age_range, str)
        assert result.grade_level >= 0
        assert result.grade_level <= 20
        assert not result.metadata["reliable"]  # < 100 words

    def test_expected_values(self):
        """Test known expected values for calibration."""
        # From docstring example
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_ari(text)

        # Should match docstring example
        assert abs(result.ari_score - 0.1) < 0.2  # Allow tolerance
        assert result.grade_level == 0
        assert "Kindergarten" in result.age_range
        assert not result.metadata["reliable"]

    def test_reliable_text(self):
        """Test text that meets reliability threshold."""
        # Generate text with 100+ words
        words = ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        text = " ".join(words * 12) + "."  # 108 words

        result = compute_ari(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] >= 100


class TestARIEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test empty string input."""
        result = compute_ari("")

        assert math.isnan(result.ari_score)
        assert math.isnan(result.grade_level)
        assert result.age_range == "Unknown"
        assert result.metadata["sentence_count"] == 0
        assert result.metadata["word_count"] == 0
        assert result.metadata["character_count"] == 0
        assert result.metadata["characters_per_word"] == 0.0
        assert result.metadata["words_per_sentence"] == 0.0
        assert not result.metadata["reliable"]

    def test_whitespace_only(self):
        """Test string with only whitespace."""
        result = compute_ari("   \n\t  ")

        assert math.isnan(result.ari_score)
        assert math.isnan(result.grade_level)
        assert not result.metadata["reliable"]

    def test_very_simple_text(self):
        """Test extremely simple text."""
        text = "Go. Run. Stop. Hi."
        result = compute_ari(text)

        # Should be low grade level
        assert result.grade_level <= 5

    def test_single_word(self):
        """Test single word."""
        result = compute_ari("Hello")

        assert result.metadata["word_count"] == 1
        assert result.metadata["sentence_count"] >= 0
        assert not result.metadata["reliable"]


class TestARIRounding:
    """Test rounding behavior and boundary values."""

    def test_grade_level_is_numeric(self):
        """Verify grade level is always a number (float for mean across chunks)."""
        texts = [
            "The cat sat on the mat.",
            "A very long and complex sentence with many subordinate clauses.",
            "Go.",
        ]

        for text in texts:
            result = compute_ari(text)
            assert isinstance(result.grade_level, (int, float))

    def test_lower_bound_clamping(self):
        """Test that very simple text is clamped to grade 0."""
        simple = "Go. Run. Stop."
        result = compute_ari(simple)

        assert result.grade_level >= 0

    def test_upper_bound_clamping(self):
        """Test that very high ARI is clamped to grade 20."""
        # Create extremely complex text with very long words and long sentences
        complex_words = [
            "antidisestablishmentarianism",
            "supercalifragilisticexpialidocious",
            "pneumonoultramicroscopicsilicovolcanoconiosis",
        ]
        # One very long sentence
        text = " ".join(complex_words * 50) + "."

        result = compute_ari(text)
        assert result.grade_level <= 20


class TestARIMetadata:
    """Test metadata structure and consistency."""

    def test_metadata_keys_consistent(self):
        """Verify all required metadata keys are present regardless of input."""
        test_cases = [
            "",  # Empty
            "Hello",  # Single word
            "The cat sat on the mat.",  # Simple sentence
            " ".join(["word"] * 200) + ".",  # Long text
        ]

        required_keys = {
            "sentence_count",
            "word_count",
            "character_count",
            "characters_per_word",
            "words_per_sentence",
            "reliable",
        }

        for text in test_cases:
            result = compute_ari(text)
            # Check that all required keys are present (may have additional keys)
            assert required_keys.issubset(set(result.metadata.keys()))

    def test_metadata_values_sensible(self):
        """Test that metadata values are within sensible ranges."""
        text = "The quick brown fox jumps over the lazy dog. The end."
        result = compute_ari(text)

        # Counts should be non-negative
        assert result.metadata["sentence_count"] >= 0
        assert result.metadata["word_count"] >= 0
        assert result.metadata["character_count"] >= 0

        # Ratios should be non-negative
        assert result.metadata["characters_per_word"] >= 0
        assert result.metadata["words_per_sentence"] >= 0

        # Reliable should be boolean
        assert isinstance(result.metadata["reliable"], bool)

    def test_character_count_alphanumeric_only(self):
        """Verify character count includes only alphanumeric characters."""
        text = "Hello123 World!!! Test@example.com"
        result = compute_ari(text)

        # Should count only: Hello123WorldTestexamplecom
        expected_chars = len("Hello123WorldTestexamplecom")
        assert result.metadata["character_count"] == expected_chars


class TestARIAgeRanges:
    """Test age range mapping."""

    def test_kindergarten_range(self):
        """Test kindergarten age range (grade 0)."""
        text = "I go."
        result = compute_ari(text)

        assert result.grade_level == 0
        assert "Kindergarten" in result.age_range

    def test_elementary_range(self):
        """Test elementary age range (grades 1-5)."""
        text = "The cat sat on the mat. The dog ran in the yard."
        result = compute_ari(text)

        if 1 <= result.grade_level <= 5:
            assert "Elementary" in result.age_range

    def test_middle_school_range(self):
        """Test middle school age range (grades 6-8)."""
        # Create text that produces middle school level
        text = """
        The American Revolution was a significant event in history.
        It occurred during the late eighteenth century.
        Many colonists wanted independence from British rule.
        """
        result = compute_ari(text)

        if 6 <= result.grade_level <= 8:
            assert "Middle School" in result.age_range

    def test_high_school_range(self):
        """Test high school age range (grades 9-12)."""
        # Create text that produces high school level
        text = (
            """
        The phenomenological approach to understanding consciousness has been
        extensively debated in philosophical circles for many decades.
        Researchers continue to investigate the fundamental nature of subjective
        experience and its relationship to objective reality.
        """
            * 2
        )  # Repeat to meet word count
        result = compute_ari(text)

        if 9 <= result.grade_level <= 12:
            assert "High School" in result.age_range

    def test_college_range(self):
        """Test college age range (grades 13-14)."""
        # Create text that produces college level
        text = (
            """
        The epistemological foundations of contemporary analytical philosophy
        necessitate a comprehensive understanding of formal logical systems.
        Philosophical investigations into the nature of knowledge require
        methodological rigor and systematic examination of foundational assumptions.
        """
            * 3
        )
        result = compute_ari(text)

        if 13 <= result.grade_level <= 14:
            assert "College" in result.age_range

    def test_graduate_range(self):
        """Test graduate age range (grade 15+)."""
        # Create text that produces graduate level
        complex_words = [
            "interdisciplinary",
            "phenomenological",
            "epistemological",
            "methodological",
            "comprehensive",
            "systematically",
        ]
        text = (
            " ".join(complex_words * 30)
            + ". "
            + " ".join(complex_words * 30)
            + ". "
            + " ".join(complex_words * 30)
            + "."
        )
        result = compute_ari(text)

        if result.grade_level >= 15:
            assert "Graduate" in result.age_range


class TestARIUnicode:
    """Test Unicode character handling."""

    def test_unicode_letters(self):
        """Test that Unicode letters are handled."""
        text = "Café résumé naïve façade."
        result = compute_ari(text)

        # Should complete without error
        assert result.ari_score is not None
        assert result.grade_level >= 0

    def test_non_latin_scripts(self):
        """Test handling of non-Latin scripts."""
        # Greek
        text_greek = "Γεια σου κόσμε"
        result = compute_ari(text_greek)
        assert result.metadata["word_count"] > 0

        # Cyrillic
        text_cyrillic = "Привет мир"
        result = compute_ari(text_cyrillic)
        assert result.metadata["word_count"] > 0

    def test_numbers_counted_as_characters(self):
        """Test that numbers are counted as characters."""
        text = "The year 2024 has 365 days."
        result = compute_ari(text)

        # Numbers should be included in character count
        # "Theyear2024has365days" = letters + digits
        assert result.metadata["character_count"] > 15


class TestARISpecialCases:
    """Test special input cases."""

    def test_urls_and_emails(self):
        """Test handling of URLs and email addresses."""
        text = "Visit https://example.com or email user@example.com for info."
        result = compute_ari(text)

        # Should complete without error
        assert result.ari_score is not None
        assert result.grade_level >= 0

    def test_numbers_in_text(self):
        """Test handling of numbers."""
        text = "In 2023, the company had 500 employees and revenue of $1,000,000."
        result = compute_ari(text)

        # Should complete without error
        assert result.ari_score is not None

    def test_contractions(self):
        """Test handling of contractions."""
        text = "I can't believe it's already over. They're leaving soon."
        result = compute_ari(text)

        # Should handle contractions naturally
        assert result.metadata["word_count"] >= 1
        assert result.grade_level >= 0

    def test_hyphenated_words(self):
        """Test handling of hyphenated compounds."""
        text = "The well-known twenty-first-century state-of-the-art solution."
        result = compute_ari(text)

        # Should count characters regardless of hyphenation
        assert result.metadata["character_count"] > 40


class TestARIFormula:
    """Test formula correctness."""

    def test_formula_components(self):
        """Verify formula components are calculated correctly."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_ari(text)

        chars_per_word = result.metadata["characters_per_word"]
        words_per_sent = result.metadata["words_per_sentence"]

        # Manual calculation: ARI = 4.71 × chars_per_word + 0.5 × words_per_sent - 21.43
        expected_ari = 4.71 * chars_per_word + 0.5 * words_per_sent - 21.43

        # Should match within floating point precision
        assert abs(result.ari_score - expected_ari) < 0.0001

    def test_longer_words_increase_score(self):
        """Test that longer words increase ARI score."""
        short_words = "The cat sat on the mat and ate the food."
        long_words = "The feline positioned itself upon the textile floor covering."

        result_short = compute_ari(short_words)
        result_long = compute_ari(long_words)

        # Longer words should produce higher character count per word
        assert (
            result_long.metadata["characters_per_word"]
            > result_short.metadata["characters_per_word"]
        )

    def test_longer_sentences_increase_score(self):
        """Test that longer sentences increase ARI score."""
        short_sentences = "The cat sat. The dog ran. The bird flew."
        long_sentence = "The cat sat on the mat while the dog ran around the yard."

        result_short = compute_ari(short_sentences)
        result_long = compute_ari(long_sentence)

        # Longer average sentence length should produce higher words per sentence
        assert (
            result_long.metadata["words_per_sentence"] > result_short.metadata["words_per_sentence"]
        )


class TestARIGutenbergTexts:
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

        result = compute_ari(text)

        # Doyle's writing style
        assert result.grade_level >= 5
        assert result.grade_level <= 15
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] > 10000

    def test_sign_of_four(self, fixtures_dir: Path):
        """Test with The Sign of the Four."""
        text_path = fixtures_dir / "doyle-the-sign-of-the-four.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_ari(text)

        assert result.grade_level >= 5
        assert result.metadata["reliable"]

    def test_valley_of_fear(self, fixtures_dir: Path):
        """Test with The Valley of Fear."""
        text_path = fixtures_dir / "doyle-the-valley-of-fear.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_ari(text)

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

            result = compute_ari(text)
            results.append((filename, result.grade_level))

        if len(results) < 2:
            pytest.skip("Not enough fixtures for consistency test")

        # All should be within a reasonable range (same author, similar era)
        grade_levels = [r[1] for r in results]
        assert max(grade_levels) - min(grade_levels) <= 4  # Within 4 grade levels


class TestARIComplexityLevels:
    """Test across various text complexity levels."""

    def test_children_book_simple(self):
        """Test very simple children's book style text."""
        text = """
        The cat is big. The dog is small. They play together.
        The cat runs fast. The dog runs too. They are friends.
        The sun is out. It is a nice day. They have fun.
        """
        result = compute_ari(text)

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
        result = compute_ari(text)

        # Should be middle grade level
        assert 5 <= result.grade_level <= 10

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
        result = compute_ari(text)

        # Should be high grade level
        assert result.grade_level >= 10


class TestARIReliability:
    """Test reliability flag behavior."""

    def test_reliability_threshold_exact(self):
        """Test reliability at exact threshold."""
        # 99 tokens (98 words + period = 99 tokens)
        text = " ".join(["word"] * 98) + "."
        result = compute_ari(text)
        assert not result.metadata["reliable"]
        assert result.metadata["word_count"] == 99

        # 100 tokens (99 words + period = 100 tokens)
        text = " ".join(["word"] * 99) + "."
        result = compute_ari(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] == 100

    def test_reliability_flag_type(self):
        """Verify reliability is always a boolean."""
        texts = ["", "Short.", " ".join(["word"] * 200) + "."]

        for text in texts:
            result = compute_ari(text)
            assert isinstance(result.metadata["reliable"], bool)

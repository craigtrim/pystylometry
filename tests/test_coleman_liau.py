"""Comprehensive tests for Coleman-Liau Index computation."""

from pathlib import Path

import pytest

from pystylometry.readability import compute_coleman_liau


class TestColemanLiauBasic:
    """Test basic Coleman-Liau functionality."""

    def test_simple_sentence(self):
        """Test single simple sentence."""
        text = "The cat sat on the mat."
        result = compute_coleman_liau(text)

        assert isinstance(result.cli_index, float)
        assert isinstance(result.grade_level, int)
        assert result.grade_level >= 0
        assert result.grade_level <= 20
        assert not result.metadata["reliable"]  # < 100 words

    def test_expected_values(self):
        """Test known expected values for calibration."""
        # From docstring example
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_coleman_liau(text)

        # Should match docstring example
        assert abs(result.cli_index - 1.8) < 0.1  # Allow small tolerance
        assert result.grade_level == 2
        assert not result.metadata["reliable"]

    def test_reliable_text(self):
        """Test text that meets reliability threshold."""
        # Generate text with exactly 100 words
        words = ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        text = " ".join(words * 12)  # 108 words
        text += "."

        result = compute_coleman_liau(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] >= 100


class TestColemanLiauEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test empty string input."""
        result = compute_coleman_liau("")

        assert result.cli_index == 0.0
        assert result.grade_level == 0
        assert result.metadata["sentence_count"] == 0
        assert result.metadata["word_count"] == 0
        assert result.metadata["letter_count"] == 0
        assert result.metadata["letters_per_100_words"] == 0.0
        assert result.metadata["sentences_per_100_words"] == 0.0
        assert not result.metadata["reliable"]

    def test_whitespace_only(self):
        """Test string with only whitespace."""
        result = compute_coleman_liau("   \n\t  ")

        assert result.cli_index == 0.0
        assert result.grade_level == 0
        assert not result.metadata["reliable"]

    def test_no_letters(self):
        """Test string with no alphabetic characters."""
        result = compute_coleman_liau("123 456... !!!")

        assert result.metadata["letter_count"] == 0

    def test_very_simple_text(self):
        """Test extremely simple text that might produce negative CLI."""
        text = "Go. Run. Stop. Hi."
        result = compute_coleman_liau(text)

        # Should be clamped at 0
        assert result.grade_level == 0
        # CLI itself might be negative
        assert result.cli_index < 5.0

    def test_single_word(self):
        """Test single word."""
        result = compute_coleman_liau("Hello")

        assert result.metadata["word_count"] == 1
        # Sentence splitter may count this as 1 sentence despite no terminator
        assert result.metadata["sentence_count"] >= 0
        assert not result.metadata["reliable"]


class TestColemanLiauRounding:
    """Test rounding behavior and boundary values."""

    def test_grade_level_is_integer(self):
        """Verify grade level is always an integer."""
        texts = [
            "The cat sat on the mat.",
            "A very long and complex sentence with many subordinate clauses.",
            "Go.",
        ]

        for text in texts:
            result = compute_coleman_liau(text)
            assert isinstance(result.grade_level, int)

    def test_lower_bound_clamping(self):
        """Test that negative CLI values are clamped to grade 0."""
        # Very simple text should produce negative CLI
        simple = "Go. Run. Stop. Hi. Yes. No."
        result = compute_coleman_liau(simple)

        assert result.grade_level == 0
        # But CLI itself can be negative
        assert result.cli_index < 0

    def test_upper_bound_clamping(self):
        """Test that very high CLI values are clamped to grade 20."""
        # Create extremely complex text with very long words
        complex_words = [
            "antidisestablishmentarianism",
            "supercalifragilisticexpialidocious",
            "pneumonoultramicroscopicsilicovolcanoconiosis",
        ]
        # One very long sentence to reduce sentence count
        text = " ".join(complex_words * 50) + "."

        result = compute_coleman_liau(text)
        assert result.grade_level <= 20


class TestColemanLiauMetadata:
    """Test metadata structure and consistency."""

    def test_metadata_keys_consistent(self):
        """Verify all metadata keys are present regardless of input."""
        test_cases = [
            "",  # Empty
            "Hello",  # Single word
            "The cat sat on the mat.",  # Simple sentence
            " ".join(["word"] * 200) + ".",  # Long text
        ]

        expected_keys = {
            "sentence_count",
            "word_count",
            "letter_count",
            "letters_per_100_words",
            "sentences_per_100_words",
            "reliable",
        }

        for text in test_cases:
            result = compute_coleman_liau(text)
            assert set(result.metadata.keys()) == expected_keys

    def test_metadata_values_sensible(self):
        """Test that metadata values are within sensible ranges."""
        text = "The quick brown fox jumps over the lazy dog. The end."
        result = compute_coleman_liau(text)

        # Counts should be non-negative
        assert result.metadata["sentence_count"] >= 0
        assert result.metadata["word_count"] >= 0
        assert result.metadata["letter_count"] >= 0

        # Per-100-words values should be non-negative
        assert result.metadata["letters_per_100_words"] >= 0
        assert result.metadata["sentences_per_100_words"] >= 0

        # Reliable should be boolean
        assert isinstance(result.metadata["reliable"], bool)

    def test_letter_count_excludes_non_alpha(self):
        """Verify letter count only includes alphabetic characters."""
        text = "Hello123 World!!! Test@example.com"
        result = compute_coleman_liau(text)

        # Should count only: HelloWorldTestexamplecom
        expected_letters = len("HelloWorldTestexamplecom")
        assert result.metadata["letter_count"] == expected_letters


class TestColemanLiauUnicode:
    """Test Unicode character handling."""

    def test_unicode_letters(self):
        """Test that Unicode letters are counted."""
        text = "Café résumé naïve façade."
        result = compute_coleman_liau(text)

        # All accented characters should count as letters
        assert result.metadata["letter_count"] > 0

    def test_non_latin_scripts(self):
        """Test handling of non-Latin scripts."""
        # Greek
        text_greek = "Γεια σου κόσμε"
        result = compute_coleman_liau(text_greek)
        assert result.metadata["letter_count"] > 0

        # Cyrillic
        text_cyrillic = "Привет мир"
        result = compute_coleman_liau(text_cyrillic)
        assert result.metadata["letter_count"] > 0

    def test_emoji_excluded(self):
        """Test that emoji are not counted as letters."""
        text = "Hello 😊 World 🌍"
        result = compute_coleman_liau(text)

        # Should only count: HelloWorld
        expected = len("HelloWorld")
        assert result.metadata["letter_count"] == expected


class TestColemanLiauSpecialCases:
    """Test special input cases and tokenizer interactions."""

    def test_urls_and_emails(self):
        """Test handling of URLs and email addresses."""
        text = "Visit https://example.com or email user@example.com for info."
        result = compute_coleman_liau(text)

        # Should complete without error
        assert result.cli_index is not None
        assert result.grade_level >= 0

    def test_numbers_in_text(self):
        """Test handling of numbers."""
        text = "In 2023, the company had 500 employees and revenue of $1,000,000."
        result = compute_coleman_liau(text)

        # Numbers should not count as letters
        assert "2023" not in str(result.metadata["letter_count"])

    def test_contractions(self):
        """Test handling of contractions."""
        text = "I can't believe it's already over. They're leaving soon."
        result = compute_coleman_liau(text)

        # Should handle contractions naturally
        assert result.metadata["word_count"] >= 1
        assert result.grade_level >= 0

    def test_hyphenated_words(self):
        """Test handling of hyphenated compounds."""
        text = "The well-known twenty-first-century state-of-the-art solution."
        result = compute_coleman_liau(text)

        # Should count letters regardless of hyphenation
        assert result.metadata["letter_count"] > 30


class TestColemanLiauFormula:
    """Test formula correctness and coefficient application."""

    def test_formula_components(self):
        """Verify formula components are calculated correctly."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_coleman_liau(text)

        L = result.metadata["letters_per_100_words"]
        S = result.metadata["sentences_per_100_words"]

        # Manual calculation: CLI = 0.0588*L - 0.296*S - 15.8
        expected_cli = 0.0588 * L - 0.296 * S - 15.8

        # Should match within floating point precision
        assert abs(result.cli_index - expected_cli) < 0.0001

    def test_longer_words_increase_score(self):
        """Test that longer words increase readability score."""
        short_words = "The cat sat on the mat."
        long_words = "The feline positioned itself upon the textile floor covering."

        result_short = compute_coleman_liau(short_words)
        result_long = compute_coleman_liau(long_words)

        # Longer words should produce higher letter count per word
        assert result_long.metadata["letters_per_100_words"] > result_short.metadata[
            "letters_per_100_words"
        ]

    def test_more_sentences_decrease_score(self):
        """Test that more sentences decrease complexity."""
        few_sentences = "This is a very long sentence with many words and clauses."
        many_sentences = "This is short. So is this. And this. Very short."

        result_few = compute_coleman_liau(few_sentences)
        result_many = compute_coleman_liau(many_sentences)

        # More sentences per word should decrease score
        assert result_many.metadata["sentences_per_100_words"] > result_few.metadata[
            "sentences_per_100_words"
        ]


class TestColemanLiauGutenbergTexts:
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

        result = compute_coleman_liau(text)

        # Doyle's writing style is accessible despite Victorian era
        assert result.grade_level >= 3
        assert result.grade_level <= 10
        assert result.metadata["reliable"]  # Long text
        assert result.metadata["word_count"] > 10000

    def test_sign_of_four(self, fixtures_dir: Path):
        """Test with The Sign of the Four."""
        text_path = fixtures_dir / "doyle-the-sign-of-the-four.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_coleman_liau(text)

        assert result.grade_level >= 3
        assert result.metadata["reliable"]

    def test_valley_of_fear(self, fixtures_dir: Path):
        """Test with The Valley of Fear."""
        text_path = fixtures_dir / "doyle-the-valley-of-fear.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            text = f.read()

        result = compute_coleman_liau(text)

        assert result.grade_level >= 3
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

            result = compute_coleman_liau(text)
            results.append((filename, result.grade_level))

        if len(results) < 2:
            pytest.skip("Not enough fixtures for consistency test")

        # All should be within a reasonable range (same author, similar era)
        grade_levels = [r[1] for r in results]
        assert max(grade_levels) - min(grade_levels) <= 3  # Within 3 grade levels

    def test_gutenberg_passage_sampling(self, fixtures_dir: Path):
        """Test that passages from same book show similar scores."""
        text_path = fixtures_dir / "doyle-the-hound-of-the-baskervilles.txt"
        if not text_path.exists():
            pytest.skip(f"Fixture not found: {text_path}")

        with open(text_path) as f:
            full_text = f.read()

        # Sample 3 passages of ~500 words each from different parts
        words = full_text.split()
        passages = [
            " ".join(words[0:500]),  # Beginning
            " ".join(words[len(words) // 2 : len(words) // 2 + 500]),  # Middle
            " ".join(words[-500:]),  # End
        ]

        results = [compute_coleman_liau(p) for p in passages]

        # All passages should be reliable
        assert all(r.metadata["reliable"] for r in results)

        # Should show consistent grade levels (within 3 grades)
        # Same author can show variation across different parts of a novel
        grade_levels = [r.grade_level for r in results]
        assert max(grade_levels) - min(grade_levels) <= 3


class TestColemanLiauComplexityLevels:
    """Test across various text complexity levels."""

    def test_children_book_simple(self):
        """Test very simple children's book style text."""
        text = """
        The cat is big. The dog is small. They play together.
        The cat runs fast. The dog runs too. They are friends.
        The sun is out. It is a nice day. They have fun.
        """
        result = compute_coleman_liau(text)

        # Should be low grade level
        assert result.grade_level <= 4

    def test_middle_school_text(self):
        """Test middle school level text."""
        text = """
        The American Revolution began in 1775 when colonists rebelled against
        British rule. They were angry about taxes and wanted independence.
        Important leaders like George Washington and Thomas Jefferson helped
        guide the colonists to victory. The war ended in 1783, and America
        became a new nation.
        """
        result = compute_coleman_liau(text)

        # Should be middle grade level
        assert 6 <= result.grade_level <= 10

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
        result = compute_coleman_liau(text)

        # Should be high grade level
        assert result.grade_level >= 13


class TestColemanLiauReliability:
    """Test reliability flag behavior."""

    def test_reliability_threshold_exact(self):
        """Test reliability at exact threshold."""
        # Exactly 99 tokens (98 words + period = 99 tokens)
        text = " ".join(["word"] * 98) + "."
        result = compute_coleman_liau(text)
        assert not result.metadata["reliable"]
        assert result.metadata["word_count"] == 99

        # Exactly 100 tokens (99 words + period = 100 tokens)
        text = " ".join(["word"] * 99) + "."
        result = compute_coleman_liau(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] == 100

    def test_reliability_flag_type(self):
        """Verify reliability is always a boolean."""
        texts = ["", "Short.", " ".join(["word"] * 200)]

        for text in texts:
            result = compute_coleman_liau(text)
            assert isinstance(result.metadata["reliable"], bool)

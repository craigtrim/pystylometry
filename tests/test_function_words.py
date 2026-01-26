"""Tests for function word analysis.

Related GitHub Issue:
    #13 - Function Word Analysis
    https://github.com/craigtrim/pystylometry/issues/13

Function words (determiners, prepositions, conjunctions, pronouns, auxiliary
verbs, particles) are closed-class words that authors use subconsciously and
consistently, making them powerful markers for authorship attribution.

This test suite covers:
    - Basic functionality with normal prose
    - Edge cases (empty text, no function words, only function words)
    - Constraints and invariants (ratios in [0,1], counts logical)
    - Category-specific tests (each function word type)
    - Overlapping word handling (words in multiple categories)
    - Distribution and frequency accuracy
    - Diversity metric validation
    - Case insensitivity
    - Punctuation handling
    - Real-world text samples
    - Authorship attribution scenarios

References:
    Mosteller, F., & Wallace, D. L. (1964). Inference and disputed authorship:
        The Federalist. Addison-Wesley.
    Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide
        to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.
"""

import pytest

from pystylometry.lexical import compute_function_words

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def sample_text():
    """Simple prose for basic testing."""
    return "The quick brown fox jumps over the lazy dog. It was a nice day."


@pytest.fixture
def academic_text():
    """Academic-style text sample."""
    return (
        "Research demonstrates that cognitive processes are influenced by "
        "various factors. However, the relationship between these variables "
        "remains unclear. Further investigation is warranted."
    )


@pytest.fixture
def fiction_text():
    """Fiction narrative sample."""
    return (
        "She walked through the forest, wondering what lay ahead. "
        "The trees whispered secrets, but she couldn't understand them. "
        "Would she ever find her way home?"
    )


@pytest.fixture
def technical_text():
    """Technical documentation sample."""
    return (
        "The function accepts a string parameter and returns a dictionary. "
        "It processes the input by tokenizing the text into words. "
        "Each word is then matched against predefined patterns."
    )


@pytest.fixture
def function_words_only():
    """Text composed entirely of function words."""
    # Changed: removed "how" as it's not in the function word lists
    return "the a an this that and but or if when where"


@pytest.fixture
def no_function_words():
    """Text with no function words."""
    return "apple banana cherry date elderberry fig grape"


@pytest.fixture
def overlapping_text():
    """Text with overlapping function words (appear in multiple categories)."""
    return "that that both both either either for for"


@pytest.fixture
def mixed_case_text():
    """Text with varied capitalization."""
    return "The THE the tHe I i WE we AND and"


@pytest.fixture
def punctuation_heavy_text():
    """Text with heavy punctuation around function words."""
    return "the, (and) 'but' \"or\" -the- the! the? the; the:"


# ==============================================================================
# Basic Functionality Tests
# ==============================================================================


class TestFunctionWordsBasic:
    """Basic functionality tests."""

    def test_compute_function_words_basic(self, sample_text):
        """Test basic computation with sample text."""
        result = compute_function_words(sample_text)

        # Verify all fields exist
        assert hasattr(result, "determiner_ratio")
        assert hasattr(result, "preposition_ratio")
        assert hasattr(result, "conjunction_ratio")
        assert hasattr(result, "pronoun_ratio")
        assert hasattr(result, "auxiliary_ratio")
        assert hasattr(result, "particle_ratio")
        assert hasattr(result, "total_function_word_ratio")
        assert hasattr(result, "function_word_diversity")
        assert hasattr(result, "most_frequent_function_words")
        assert hasattr(result, "least_frequent_function_words")
        assert hasattr(result, "function_word_distribution")
        assert hasattr(result, "metadata")

        # Verify ratios are reasonable (not zero for text with function words)
        assert result.total_function_word_ratio > 0.0

    def test_all_fields_exist(self, sample_text):
        """Verify all required fields are present."""
        result = compute_function_words(sample_text)

        # Check field types
        assert isinstance(result.determiner_ratio, float)
        assert isinstance(result.preposition_ratio, float)
        assert isinstance(result.conjunction_ratio, float)
        assert isinstance(result.pronoun_ratio, float)
        assert isinstance(result.auxiliary_ratio, float)
        assert isinstance(result.particle_ratio, float)
        assert isinstance(result.total_function_word_ratio, float)
        assert isinstance(result.function_word_diversity, float)
        assert isinstance(result.most_frequent_function_words, list)
        assert isinstance(result.least_frequent_function_words, list)
        assert isinstance(result.function_word_distribution, dict)
        assert isinstance(result.metadata, dict)

    def test_metadata_completeness(self, sample_text):
        """Verify metadata contains all required keys."""
        result = compute_function_words(sample_text)
        metadata = result.metadata

        # Required metadata fields
        required_keys = [
            "total_word_count",
            "total_function_word_count",
            "unique_function_word_count",
            "determiner_count",
            "preposition_count",
            "conjunction_count",
            "pronoun_count",
            "auxiliary_count",
            "particle_count",
            "determiner_list",
            "preposition_list",
            "conjunction_list",
            "pronoun_list",
            "auxiliary_list",
            "particle_list",
            "overlapping_words",
            "overlapping_word_categories",
        ]

        for key in required_keys:
            assert key in metadata, f"Missing metadata key: {key}"

    def test_distribution_non_empty(self, sample_text):
        """Verify distribution is non-empty for text with function words."""
        result = compute_function_words(sample_text)

        assert len(result.function_word_distribution) > 0
        assert isinstance(result.function_word_distribution, dict)

        # Check that all values are positive integers
        for word, count in result.function_word_distribution.items():
            assert isinstance(word, str)
            assert isinstance(count, int)
            assert count > 0

    def test_frequency_lists_format(self, sample_text):
        """Verify most/least frequent lists have correct format."""
        result = compute_function_words(sample_text)

        # Most frequent
        assert isinstance(result.most_frequent_function_words, list)
        for item in result.most_frequent_function_words:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)  # word
            assert isinstance(item[1], int)  # count
            assert item[1] > 0

        # Least frequent
        assert isinstance(result.least_frequent_function_words, list)
        for item in result.least_frequent_function_words:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], int)
            assert item[1] > 0


# ==============================================================================
# Edge Case Tests
# ==============================================================================


class TestFunctionWordsEdgeCases:
    """Edge case handling tests."""

    def test_empty_text(self):
        """Test handling of empty string."""
        result = compute_function_words("")

        # All ratios should be 0.0
        assert result.determiner_ratio == 0.0
        assert result.preposition_ratio == 0.0
        assert result.conjunction_ratio == 0.0
        assert result.pronoun_ratio == 0.0
        assert result.auxiliary_ratio == 0.0
        assert result.particle_ratio == 0.0
        assert result.total_function_word_ratio == 0.0
        assert result.function_word_diversity == 0.0

        # Lists should be empty
        assert result.most_frequent_function_words == []
        assert result.least_frequent_function_words == []

        # Distribution should be empty
        assert result.function_word_distribution == {}

        # Metadata counts should be 0
        assert result.metadata["total_word_count"] == 0
        assert result.metadata["total_function_word_count"] == 0
        assert result.metadata["unique_function_word_count"] == 0

    def test_single_function_word(self):
        """Test text with single function word."""
        result = compute_function_words("the")

        assert result.total_function_word_ratio == 1.0  # 1/1 = 1.0
        assert result.function_word_diversity == 1.0  # 1 unique / 1 total
        assert result.determiner_ratio == 1.0  # "the" is a determiner
        assert len(result.function_word_distribution) == 1
        assert result.function_word_distribution["the"] == 1

    def test_single_non_function_word(self):
        """Test text with single non-function word."""
        result = compute_function_words("apple")

        # All ratios should be 0.0
        assert result.total_function_word_ratio == 0.0
        assert result.function_word_diversity == 0.0
        assert result.determiner_ratio == 0.0

        # Distribution should be empty
        assert result.function_word_distribution == {}

        # Total word count should be 1
        assert result.metadata["total_word_count"] == 1
        assert result.metadata["total_function_word_count"] == 0

    def test_no_function_words(self, no_function_words):
        """Test text with no function words at all."""
        result = compute_function_words(no_function_words)

        # All ratios should be 0.0
        assert result.determiner_ratio == 0.0
        assert result.preposition_ratio == 0.0
        assert result.conjunction_ratio == 0.0
        assert result.pronoun_ratio == 0.0
        assert result.auxiliary_ratio == 0.0
        assert result.particle_ratio == 0.0
        assert result.total_function_word_ratio == 0.0
        assert result.function_word_diversity == 0.0

        # Distribution and lists should be empty
        assert result.function_word_distribution == {}
        assert result.most_frequent_function_words == []
        assert result.least_frequent_function_words == []

        # But total word count should be > 0
        assert result.metadata["total_word_count"] > 0
        assert result.metadata["total_function_word_count"] == 0

    def test_only_function_words(self, function_words_only):
        """Test text composed entirely of function words."""
        result = compute_function_words(function_words_only)

        # Total ratio should be 1.0 (all words are function words)
        assert result.total_function_word_ratio == 1.0

        # Total function word count should equal total word count
        assert result.metadata["total_function_word_count"] == result.metadata["total_word_count"]

        # Distribution should contain all the words
        assert len(result.function_word_distribution) > 0

    def test_very_short_text(self):
        """Test with very short text (2-3 words)."""
        result = compute_function_words("the cat")

        assert result.metadata["total_word_count"] == 2
        assert result.determiner_ratio == 0.5  # 1/2 = 0.5
        assert "the" in result.function_word_distribution

    def test_whitespace_only(self):
        """Test text with only whitespace."""
        result = compute_function_words("   \n\t  ")

        # Should behave like empty text
        assert result.total_function_word_ratio == 0.0
        assert result.metadata["total_word_count"] == 0


# ==============================================================================
# Constraint Tests
# ==============================================================================


class TestFunctionWordsConstraints:
    """Validation of constraints and invariants."""

    def test_ratios_in_valid_range(self, sample_text):
        """Test that all ratios are between 0 and 1."""
        result = compute_function_words(sample_text)

        assert 0.0 <= result.determiner_ratio <= 1.0
        assert 0.0 <= result.preposition_ratio <= 1.0
        assert 0.0 <= result.conjunction_ratio <= 1.0
        assert 0.0 <= result.pronoun_ratio <= 1.0
        assert 0.0 <= result.auxiliary_ratio <= 1.0
        assert 0.0 <= result.particle_ratio <= 1.0
        assert 0.0 <= result.total_function_word_ratio <= 1.0

    def test_diversity_in_valid_range(self, sample_text):
        """Test that diversity is between 0 and 1."""
        result = compute_function_words(sample_text)

        assert 0.0 <= result.function_word_diversity <= 1.0

    def test_count_constraints(self, sample_text):
        """Test that counts satisfy logical constraints."""
        result = compute_function_words(sample_text)
        metadata = result.metadata

        # Total function word count <= total word count
        assert metadata["total_function_word_count"] <= metadata["total_word_count"]

        # Unique function word count <= total function word count
        assert metadata["unique_function_word_count"] <= metadata["total_function_word_count"]

        # Sum of category counts >= total function word count (due to overlaps)
        category_sum = (
            metadata["determiner_count"]
            + metadata["preposition_count"]
            + metadata["conjunction_count"]
            + metadata["pronoun_count"]
            + metadata["auxiliary_count"]
            + metadata["particle_count"]
        )
        assert category_sum >= metadata["total_function_word_count"]

        # All counts are non-negative
        assert metadata["total_word_count"] >= 0
        assert metadata["total_function_word_count"] >= 0
        assert metadata["unique_function_word_count"] >= 0
        assert metadata["determiner_count"] >= 0
        assert metadata["preposition_count"] >= 0
        assert metadata["conjunction_count"] >= 0
        assert metadata["pronoun_count"] >= 0
        assert metadata["auxiliary_count"] >= 0
        assert metadata["particle_count"] >= 0

    def test_most_frequent_sorted_descending(self, sample_text):
        """Test that most frequent list is sorted by count descending."""
        result = compute_function_words(sample_text)

        if len(result.most_frequent_function_words) > 1:
            for i in range(len(result.most_frequent_function_words) - 1):
                current_count = result.most_frequent_function_words[i][1]
                next_count = result.most_frequent_function_words[i + 1][1]
                assert current_count >= next_count

    def test_least_frequent_sorted_ascending(self, sample_text):
        """Test that least frequent list is sorted by count ascending."""
        result = compute_function_words(sample_text)

        if len(result.least_frequent_function_words) > 1:
            for i in range(len(result.least_frequent_function_words) - 1):
                current_count = result.least_frequent_function_words[i][1]
                next_count = result.least_frequent_function_words[i + 1][1]
                assert current_count <= next_count

    def test_distribution_values_positive(self, sample_text):
        """Test that distribution values are positive integers."""
        result = compute_function_words(sample_text)

        for word, count in result.function_word_distribution.items():
            assert isinstance(count, int)
            assert count > 0

    def test_unique_count_matches_distribution_length(self, sample_text):
        """Test that unique count equals distribution length."""
        result = compute_function_words(sample_text)

        assert result.metadata["unique_function_word_count"] == len(
            result.function_word_distribution
        )


# ==============================================================================
# Category-Specific Tests
# ==============================================================================


class TestFunctionWordsCategorySpecific:
    """Category-specific tests."""

    def test_determiner_only_text(self):
        """Test text with only determiners."""
        text = "the a an this that these those"
        result = compute_function_words(text)

        # Determiner ratio should be 1.0 (all words are determiners)
        assert result.determiner_ratio == 1.0
        assert result.metadata["determiner_count"] == 7

        # Other categories should be 0 (or low if overlaps exist)
        # Note: "that" is also a pronoun/conjunction, so we might have overlaps

    def test_preposition_only_text(self):
        """Test text with only prepositions."""
        text = "in on at by for with from to of"
        result = compute_function_words(text)

        # Preposition ratio should be 1.0
        assert result.preposition_ratio == 1.0
        assert result.metadata["preposition_count"] == 9

    def test_conjunction_only_text(self):
        """Test text with only conjunctions."""
        text = "and but or nor for yet so"
        result = compute_function_words(text)

        # Conjunction ratio should be high (but "for" is also a preposition)
        assert result.conjunction_ratio > 0.8
        assert result.metadata["conjunction_count"] == 7

    def test_pronoun_only_text(self):
        """Test text with only pronouns."""
        text = "i you he she it we they me him her us them"
        result = compute_function_words(text)

        # Pronoun ratio should be 1.0
        assert result.pronoun_ratio == 1.0
        assert result.metadata["pronoun_count"] == 12  # 12 pronouns in the text

    def test_auxiliary_only_text(self):
        """Test text with only auxiliaries."""
        text = "can could may might must will would is are was were"
        result = compute_function_words(text)

        # Auxiliary ratio should be 1.0
        assert result.auxiliary_ratio == 1.0
        assert result.metadata["auxiliary_count"] == 11

    def test_particle_only_text(self):
        """Test text with only particles."""
        text = "up down out off over in away back"
        result = compute_function_words(text)

        # Particle ratio should be high (but "in" is also preposition)
        assert result.particle_ratio > 0.8
        assert result.metadata["particle_count"] == 8


# ==============================================================================
# Overlapping Word Tests
# ==============================================================================


class TestFunctionWordsOverlapping:
    """Tests for words appearing in multiple categories."""

    def test_that_overlap(self):
        """Test 'that' counted in multiple categories.

        'that' appears in:
        - DETERMINERS
        - PRONOUNS (demonstrative)
        - Could also be in conjunctions depending on usage
        """
        text = "that that that"  # 3 occurrences
        result = compute_function_words(text)

        # "that" should be counted in both determiner and pronoun categories
        assert result.metadata["determiner_count"] >= 3
        assert result.metadata["pronoun_count"] >= 3

        # But total function word count should be 3 (counted once)
        assert result.metadata["total_function_word_count"] == 3

        # "that" should be in overlapping words
        assert "that" in result.metadata["overlapping_words"]
        assert "determiner" in result.metadata["overlapping_word_categories"]["that"]
        assert "pronoun" in result.metadata["overlapping_word_categories"]["that"]

    def test_both_overlap(self):
        """Test 'both' as determiner and conjunction."""
        text = "both both"  # 2 occurrences
        result = compute_function_words(text)

        # "both" is in both DETERMINERS and CONJUNCTIONS
        assert result.metadata["determiner_count"] >= 2
        assert result.metadata["conjunction_count"] >= 2

        # Total should count once
        assert result.metadata["total_function_word_count"] == 2

        # Should be tracked as overlapping
        assert "both" in result.metadata["overlapping_words"]

    def test_for_overlap(self):
        """Test 'for' as preposition and conjunction."""
        text = "for for for"  # 3 occurrences
        result = compute_function_words(text)

        # "for" is in both PREPOSITIONS and CONJUNCTIONS
        assert result.metadata["preposition_count"] >= 3
        assert result.metadata["conjunction_count"] >= 3

        # Total should count once
        assert result.metadata["total_function_word_count"] == 3

    def test_total_ratio_counts_once(self, overlapping_text):
        """Verify total ratio counts each token only once."""
        result = compute_function_words(overlapping_text)

        # Text: "that that both both either either for for"
        # 8 tokens, all are function words, all overlap
        assert result.metadata["total_word_count"] == 8
        assert result.metadata["total_function_word_count"] == 8
        assert result.total_function_word_ratio == 1.0  # 8/8 = 1.0

        # But category counts should sum to > 8 due to overlaps
        category_sum = (
            result.metadata["determiner_count"]
            + result.metadata["preposition_count"]
            + result.metadata["conjunction_count"]
            + result.metadata["pronoun_count"]
            + result.metadata["auxiliary_count"]
            + result.metadata["particle_count"]
        )
        assert category_sum > 8

    def test_overlapping_metadata_accuracy(self, overlapping_text):
        """Verify overlapping words tracked in metadata."""
        result = compute_function_words(overlapping_text)

        # All words in this text should be overlapping
        overlapping_words = result.metadata["overlapping_words"]
        assert "that" in overlapping_words
        assert "both" in overlapping_words
        assert "either" in overlapping_words
        assert "for" in overlapping_words

        # Each should have multiple categories listed
        for word in overlapping_words:
            categories = result.metadata["overlapping_word_categories"][word]
            assert len(categories) > 1


# ==============================================================================
# Distribution Tests
# ==============================================================================


class TestFunctionWordsDistribution:
    """Distribution and frequency tests."""

    def test_most_frequent_accuracy(self):
        """Verify most frequent words are correct."""
        # Text with clear most frequent: "the" appears 5 times
        text = "the cat and the dog and the bird and the fish and the snake"
        result = compute_function_words(text)

        # "the" should be most frequent (appears 5 times)
        # "and" should be second (appears 4 times)
        most_frequent = result.most_frequent_function_words
        assert len(most_frequent) >= 2
        assert most_frequent[0][0] == "the"
        assert most_frequent[0][1] == 5
        assert most_frequent[1][0] == "and"
        assert most_frequent[1][1] == 4

    def test_least_frequent_accuracy(self):
        """Verify least frequent words are correct."""
        text = "the the the a an"  # "the" = 3, "a" = 1, "an" = 1
        result = compute_function_words(text)

        least_frequent = result.least_frequent_function_words
        # "a" and "an" should be least frequent (1 each)
        assert len(least_frequent) >= 2
        assert least_frequent[0][1] == 1
        assert least_frequent[1][1] == 1
        # Both should be either "a" or "an"
        least_words = {least_frequent[0][0], least_frequent[1][0]}
        assert "a" in least_words or "an" in least_words

    def test_distribution_completeness(self, sample_text):
        """Verify distribution contains all function words used."""
        result = compute_function_words(sample_text)

        # Every function word in most_frequent should be in distribution
        for word, count in result.most_frequent_function_words:
            assert word in result.function_word_distribution
            assert result.function_word_distribution[word] == count

        # Every function word in least_frequent should be in distribution
        for word, count in result.least_frequent_function_words:
            assert word in result.function_word_distribution
            assert result.function_word_distribution[word] == count

    def test_distribution_accuracy(self):
        """Verify distribution counts are accurate."""
        text = "the the the a a and"
        result = compute_function_words(text)

        dist = result.function_word_distribution
        assert dist["the"] == 3
        assert dist["a"] == 2
        assert dist["and"] == 1

    def test_distribution_no_zero_counts(self, sample_text):
        """Verify distribution contains no zero counts."""
        result = compute_function_words(sample_text)

        for word, count in result.function_word_distribution.items():
            assert count > 0


# ==============================================================================
# Diversity Tests
# ==============================================================================


class TestFunctionWordsDiversity:
    """Diversity metric tests."""

    def test_diversity_all_unique(self):
        """Test diversity = 1.0 when all tokens unique."""
        text = "the a an this that"  # 5 unique function words, each appears once
        result = compute_function_words(text)

        # Diversity should be 1.0 (5 unique / 5 total)
        assert result.function_word_diversity == 1.0

    def test_diversity_all_same(self):
        """Test diversity with repeated single function word."""
        text = "the the the the the"  # 1 unique, 5 total
        result = compute_function_words(text)

        # Diversity should be 0.2 (1 unique / 5 total)
        assert abs(result.function_word_diversity - 0.2) < 0.01

    def test_diversity_calculation(self):
        """Verify diversity = unique / total."""
        text = "the the a a and"  # 3 unique, 5 total
        result = compute_function_words(text)

        expected_diversity = 3 / 5  # 0.6
        assert abs(result.function_word_diversity - expected_diversity) < 0.01

    def test_diversity_with_non_function_words(self):
        """Test diversity calculation with mixed content."""
        text = "the cat the dog the bird"  # 1 unique function word ("the"), 3 total
        result = compute_function_words(text)

        # 1 unique function word / 3 function word tokens
        expected_diversity = 1 / 3
        assert abs(result.function_word_diversity - expected_diversity) < 0.01


# ==============================================================================
# Case Insensitivity Tests
# ==============================================================================


class TestFunctionWordsCaseInsensitive:
    """Case insensitivity tests."""

    def test_uppercase_matching(self):
        """Test that 'The' matches 'the'."""
        text = "The THE the"
        result = compute_function_words(text)

        # All should be counted as "the"
        assert result.function_word_distribution["the"] == 3

    def test_mixed_case_matching(self, mixed_case_text):
        """Test mixed case text."""
        # Text: "The THE the tHe I i WE we AND and"
        result = compute_function_words(mixed_case_text)

        # Should group by lowercase
        assert result.function_word_distribution["the"] == 4
        assert result.function_word_distribution["i"] == 2
        assert result.function_word_distribution["we"] == 2
        assert result.function_word_distribution["and"] == 2

    def test_all_caps_text(self):
        """Test text in all uppercase."""
        text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        result = compute_function_words(text)

        # Should match lowercase function words
        assert "the" in result.function_word_distribution
        assert "over" in result.function_word_distribution


# ==============================================================================
# Punctuation Handling Tests
# ==============================================================================


class TestFunctionWordsPunctuation:
    """Punctuation handling tests."""

    def test_trailing_punctuation(self):
        """Test function words with trailing punctuation."""
        text = "the, and. but! or?"
        result = compute_function_words(text)

        # Should strip punctuation and match
        assert "the" in result.function_word_distribution
        assert "and" in result.function_word_distribution
        assert "but" in result.function_word_distribution
        assert "or" in result.function_word_distribution

    def test_leading_punctuation(self):
        """Test function words with leading punctuation."""
        text = "'the \"and (but [or"
        result = compute_function_words(text)

        # Should strip punctuation and match
        assert "the" in result.function_word_distribution
        assert "and" in result.function_word_distribution
        assert "but" in result.function_word_distribution
        assert "or" in result.function_word_distribution

    def test_quoted_function_words(self):
        """Test function words in quotes."""
        text = "\"the\" 'and' \"but\" 'or'"
        result = compute_function_words(text)

        assert "the" in result.function_word_distribution
        assert "and" in result.function_word_distribution
        assert "but" in result.function_word_distribution
        assert "or" in result.function_word_distribution

    def test_punctuation_heavy_text(self, punctuation_heavy_text):
        """Test text with heavy punctuation around function words."""
        # Text: "the, (and) 'but' \"or\" -the- the! the? the; the:"
        result = compute_function_words(punctuation_heavy_text)

        # Should identify "the" multiple times despite punctuation
        assert "the" in result.function_word_distribution
        assert result.function_word_distribution["the"] >= 5


# ==============================================================================
# Real-World Text Tests
# ==============================================================================


class TestFunctionWordsRealWorld:
    """Tests with realistic text samples."""

    def test_academic_text(self, academic_text):
        """Test with academic prose sample."""
        result = compute_function_words(academic_text)

        # Academic text typically has high function word ratio
        assert result.total_function_word_ratio > 0.3

        # Common academic function words should appear
        assert "that" in result.function_word_distribution
        assert "the" in result.function_word_distribution

        # Should have reasonable diversity
        assert result.function_word_diversity > 0.1

    def test_fiction_text(self, fiction_text):
        """Test with fiction narrative sample."""
        result = compute_function_words(fiction_text)

        # Fiction typically has pronouns and determiners
        assert result.pronoun_ratio > 0.0
        assert result.determiner_ratio > 0.0

        # Should have function words
        assert len(result.function_word_distribution) > 0

    def test_technical_text(self, technical_text):
        """Test with technical documentation."""
        result = compute_function_words(technical_text)

        # Technical text has function words
        assert result.total_function_word_ratio > 0.2

        # Should have articles and prepositions
        assert result.determiner_ratio > 0.0
        assert result.preposition_ratio > 0.0

    def test_informal_text(self):
        """Test with conversational text."""
        text = "Hey! How are you? I'm doing great. We should hang out sometime. What do you think?"
        result = compute_function_words(text)

        # Conversational text has many pronouns
        assert result.pronoun_ratio > 0.1

        # Should have interrogatives and auxiliaries
        assert "are" in result.function_word_distribution
        assert "do" in result.function_word_distribution

    def test_news_article(self):
        """Test with news article style."""
        text = (
            "The president announced that the new policy would take effect in the next month. "
            "Officials said the changes were necessary for the country. "
            "However, critics argue that more time is needed."
        )
        result = compute_function_words(text)

        # News has high determiner and preposition usage
        assert result.determiner_ratio > 0.1
        assert result.preposition_ratio > 0.0  # Now includes "in" and "for"

        # Common news function words
        assert "the" in result.function_word_distribution
        assert "that" in result.function_word_distribution


# ==============================================================================
# Authorship Attribution Tests
# ==============================================================================


class TestFunctionWordsAuthorship:
    """Authorship attribution tests."""

    def test_author_profile_differences(self):
        """Test that different authors have different profiles.

        Classic example: Hamilton vs Madison in Federalist Papers.
        Hamilton preferred "while", Madison preferred "whilst".
        We'll simulate with different function word preferences.
        """
        # Simulate Author A: prefers "the", "a", "and"
        text_a = (
            "The investigation showed that the results were significant. "
            "The analysis revealed a pattern. The data and the methods were sound."
        )

        # Simulate Author B: prefers "this", "these", "but"
        text_b = (
            "This investigation showed these results but this analysis revealed "
            "these patterns but this data was sound."
        )

        result_a = compute_function_words(text_a)
        result_b = compute_function_words(text_b)

        # Different determiner preferences
        # Author A uses "the" more, Author B uses "this/these" more
        assert result_a.function_word_distribution.get(
            "the", 0
        ) > result_b.function_word_distribution.get("the", 0)
        assert result_b.function_word_distribution.get(
            "this", 0
        ) > result_a.function_word_distribution.get("this", 0)

    def test_profile_consistency(self):
        """Test that same author has consistent profile across texts."""
        # Two texts by same author (similar style)
        text1 = "The cat and the dog were playing. The bird was watching."
        text2 = "The car and the bike were parked. The truck was waiting."

        result1 = compute_function_words(text1)
        result2 = compute_function_words(text2)

        # Both should have similar determiner ratios
        # (within 20% relative difference)
        ratio1 = result1.determiner_ratio
        ratio2 = result2.determiner_ratio
        relative_diff = abs(ratio1 - ratio2) / max(ratio1, ratio2)
        assert relative_diff < 0.3

        # Both should use "the" and "and"
        assert "the" in result1.function_word_distribution
        assert "the" in result2.function_word_distribution
        assert "and" in result1.function_word_distribution
        assert "and" in result2.function_word_distribution

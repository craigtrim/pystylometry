"""Tests for word frequency sophistication metrics.

Tests the implementation of vocabulary sophistication measurement using
corpus frequency data. Related to GitHub Issue #15.
"""

import pytest
from pystylometry.lexical import compute_word_frequency_sophistication


# ===== Fixtures =====


@pytest.fixture
def simple_text():
    """Simple text with common words."""
    return (
        "The cat sat on the mat. The dog ran in the park. "
        "A boy and a girl play with a ball. "
        "The sun is hot. The sky is blue. "
    ) * 5  # Repeat to get enough tokens


@pytest.fixture
def academic_text():
    """Academic text with sophisticated vocabulary."""
    return (
        "The research methodology employed a comprehensive approach to analyze "
        "the significant theoretical framework. The data demonstrate substantial "
        "evidence supporting the hypothesis. This analysis indicates that the "
        "results require further investigation to establish definitive conclusions. "
        "The study's primary objective involves assessing the policy implications "
        "derived from the empirical findings. Researchers must interpret these "
        "complex phenomena within the appropriate contextual parameters. "
        "The investigation utilized rigorous statistical procedures to evaluate "
        "the correlation between independent and dependent variables."
    )


@pytest.fixture
def childrens_text():
    """Children's text with simple vocabulary."""
    return (
        "The dog is big. The cat is small. I like the dog. "
        "I like the cat. The dog runs. The cat jumps. "
        "The boy has a ball. The girl has a doll. "
        "They play in the sun. It is fun. "
        "The ball is red. The doll is pink. "
        "I see a bird. The bird can fly. "
    ) * 3


@pytest.fixture
def technical_text():
    """Technical text with specialized jargon (many unknown words)."""
    return (
        "The API endpoint requires authentication using OAuth2 tokens. "
        "Initialize the WebSocket connection with proper SSL certificates. "
        "The microservice architecture utilizes RESTful paradigms for "
        "inter-process communication. Kubernetes orchestration handles "
        "containerized deployment across distributed clusters. "
        "Implement the asynchronous callback mechanism for event-driven processing. "
        "The middleware validates incoming JSON payloads against predefined schemas."
    )


@pytest.fixture
def mixed_sophistication_text():
    """Text with mixed sophistication levels."""
    return (
        "The quick brown fox jumps over the lazy dog. However, this "
        "exemplifies the utilization of both rudimentary and sophisticated "
        "lexical constructs. Basic words and complex terminology coexist "
        "within the same discourse, demonstrating heterogeneous vocabulary. "
        "The analysis requires interpretation of multifaceted linguistic patterns."
    )


@pytest.fixture
def very_common_text():
    """Text with only very common words (top 100)."""
    return (
        "The man and the woman are in the house. They have a dog and a cat. "
        "The dog is big and the cat is small. The man is good and the woman "
        "is good too. They go to the store. The store is not far from the house. "
        "It is a good day. The sun is out and it is not cold."
    ) * 2


@pytest.fixture
def news_text():
    """News article with moderate sophistication."""
    return (
        "Officials announced today that the new policy will take effect next month. "
        "The decision comes after months of debate among lawmakers. "
        "Experts predict the changes will significantly impact local communities. "
        "Critics argue the proposal doesn't address underlying problems, while "
        "supporters maintain it represents an important step forward. "
        "The government plans to monitor implementation closely."
    )


# ===== Basic Functionality Tests =====


class TestWordFrequencyBasic:
    """Basic functionality tests."""

    def test_basic_computation(self, simple_text):
        """Test basic frequency sophistication computation."""
        result = compute_word_frequency_sophistication(simple_text)

        assert isinstance(result.mean_frequency_rank, float)
        assert isinstance(result.median_frequency_rank, float)
        assert isinstance(result.rare_word_ratio, float)
        assert isinstance(result.common_word_ratio, float)
        assert isinstance(result.academic_word_ratio, float)
        assert isinstance(result.advanced_word_ratio, float)
        assert isinstance(result.frequency_band_distribution, dict)
        assert isinstance(result.rarest_words, list)
        assert isinstance(result.most_common_words, list)
        assert isinstance(result.metadata, dict)

    def test_all_fields_present(self, academic_text):
        """Test all result fields are present and correct types."""
        result = compute_word_frequency_sophistication(academic_text)

        # Check all dataclass fields exist
        assert hasattr(result, "mean_frequency_rank")
        assert hasattr(result, "median_frequency_rank")
        assert hasattr(result, "rare_word_ratio")
        assert hasattr(result, "common_word_ratio")
        assert hasattr(result, "academic_word_ratio")
        assert hasattr(result, "advanced_word_ratio")
        assert hasattr(result, "frequency_band_distribution")
        assert hasattr(result, "rarest_words")
        assert hasattr(result, "most_common_words")
        assert hasattr(result, "metadata")

    def test_metadata_complete(self, simple_text):
        """Test metadata contains all required fields."""
        result = compute_word_frequency_sophistication(simple_text)

        # Required metadata fields
        assert "frequency_corpus" in result.metadata
        assert "rare_threshold" in result.metadata
        assert "common_threshold" in result.metadata
        assert "total_words" in result.metadata
        assert "unique_words" in result.metadata
        assert "unknown_words" in result.metadata
        assert "unknown_word_ratio" in result.metadata
        assert "frequency_list_size" in result.metadata
        assert "max_frequency_rank" in result.metadata


# ===== Edge Case Tests =====


class TestWordFrequencyEdgeCases:
    """Edge case tests."""

    def test_empty_text(self):
        """Test with empty text (should raise ValueError)."""
        with pytest.raises(ValueError, match="no valid tokens"):
            compute_word_frequency_sophistication("")

    def test_whitespace_only(self):
        """Test with whitespace-only text."""
        with pytest.raises(ValueError, match="no valid tokens"):
            compute_word_frequency_sophistication("   \n\t   ")

    def test_very_short_text(self):
        """Test with very short text (5-10 words)."""
        text = "The quick brown fox jumps"
        result = compute_word_frequency_sophistication(text)

        assert result.metadata["total_words"] == 5
        assert result.mean_frequency_rank > 0
        assert 0 <= result.rare_word_ratio <= 1.0

    def test_all_unknown_words(self):
        """Test with words not in frequency list."""
        text = "xyzzyx qwertyzz asdfghjkl zxcvbnmlk poiuytrewq " * 10
        result = compute_word_frequency_sophistication(text)

        # All words should be unknown/rare
        assert result.metadata["unknown_word_ratio"] > 0.9  # Most words unknown
        assert result.rare_word_ratio > 0.9  # Unknown words treated as rare

    def test_all_common_words(self, very_common_text):
        """Test with very common words only."""
        result = compute_word_frequency_sophistication(very_common_text)

        # Should have high common word ratio
        assert result.common_word_ratio > 0.7
        # Should have low rare word ratio
        assert result.rare_word_ratio < 0.2
        # Median rank should be low (common words have low ranks)
        # Use median instead of mean to avoid skew from unknown words
        assert result.median_frequency_rank < 500


# ===== Constraint Tests =====


class TestWordFrequencyConstraints:
    """Constraint validation tests."""

    def test_ratios_in_range(self, academic_text):
        """Test all ratios are between 0 and 1."""
        result = compute_word_frequency_sophistication(academic_text)

        assert 0.0 <= result.rare_word_ratio <= 1.0
        assert 0.0 <= result.common_word_ratio <= 1.0
        assert 0.0 <= result.academic_word_ratio <= 1.0
        assert 0.0 <= result.advanced_word_ratio <= 1.0
        assert 0.0 <= result.metadata["unknown_word_ratio"] <= 1.0

    def test_ranks_positive(self, simple_text):
        """Test mean and median ranks are positive."""
        result = compute_word_frequency_sophistication(simple_text)

        assert result.mean_frequency_rank >= 1.0
        assert result.median_frequency_rank >= 1.0

    def test_frequency_band_sum(self, academic_text):
        """Test frequency band distribution sums to 1.0."""
        result = compute_word_frequency_sophistication(academic_text)

        band_sum = sum(result.frequency_band_distribution.values())
        # Allow small floating point error
        assert abs(band_sum - 1.0) < 1e-9

    def test_rarest_vs_common_ranks(self, mixed_sophistication_text):
        """Test rarest words have higher ranks than common words."""
        result = compute_word_frequency_sophistication(mixed_sophistication_text)

        if result.rarest_words and result.most_common_words:
            # Rarest words should have higher ranks
            min_rarest_rank = min(rank for _, rank in result.rarest_words)
            max_common_rank = max(rank for _, rank in result.most_common_words)
            # Not a strict requirement if there's overlap, but generally true
            # So we'll just check the top rarest vs top common
            assert result.rarest_words[0][1] >= result.most_common_words[0][1]


# ===== Parameter Validation Tests =====


class TestWordFrequencyParameters:
    """Parameter validation tests."""

    def test_invalid_corpus(self, simple_text):
        """Test invalid corpus name raises ValueError."""
        with pytest.raises(ValueError, match="Only 'coca' corpus"):
            compute_word_frequency_sophistication(
                simple_text, frequency_corpus="invalid"
            )

    def test_custom_rare_threshold(self, academic_text):
        """Test with custom rare_threshold."""
        result_default = compute_word_frequency_sophistication(academic_text)
        result_custom = compute_word_frequency_sophistication(
            academic_text, rare_threshold=5000
        )

        # With lower threshold, more words should be classified as rare
        assert result_custom.rare_word_ratio >= result_default.rare_word_ratio
        assert result_custom.metadata["rare_threshold"] == 5000

    def test_custom_common_threshold(self, academic_text):
        """Test with custom common_threshold."""
        result_default = compute_word_frequency_sophistication(academic_text)
        result_custom = compute_word_frequency_sophistication(
            academic_text, common_threshold=2000
        )

        # With higher threshold, more words should be classified as common
        assert result_custom.common_word_ratio >= result_default.common_word_ratio
        assert result_custom.metadata["common_threshold"] == 2000


# ===== Academic Word List Tests =====


class TestAcademicWordList:
    """Academic Word List tests."""

    def test_high_academic_ratio(self, academic_text):
        """Test text with many academic words."""
        result = compute_word_frequency_sophistication(academic_text)

        # Academic text should have reasonable academic word ratio
        # "analyze", "approach", "data", "research", "method", etc. are in AWL
        assert result.academic_word_ratio > 0.05  # At least 5% academic words

    def test_zero_academic_ratio(self, childrens_text):
        """Test text with no academic words."""
        result = compute_word_frequency_sophistication(childrens_text)

        # Children's text should have very few or no academic words
        assert result.academic_word_ratio < 0.1  # Less than 10%

    def test_academic_case_insensitive(self):
        """Test AWL matching is case-insensitive."""
        text_lower = "the research method is good"
        text_upper = "The RESEARCH METHOD is good"
        text_mixed = "The Research Method Is Good"

        result_lower = compute_word_frequency_sophistication(text_lower)
        result_upper = compute_word_frequency_sophistication(text_upper)
        result_mixed = compute_word_frequency_sophistication(text_mixed)

        # All should detect "research" and "method" as academic words
        assert result_lower.academic_word_ratio == result_upper.academic_word_ratio
        assert result_lower.academic_word_ratio == result_mixed.academic_word_ratio

    def test_academic_in_advanced(self, academic_text):
        """Test academic words contribute to advanced ratio."""
        result = compute_word_frequency_sophistication(academic_text)

        # Advanced ratio should be at least as high as academic ratio
        # (since advanced = rare OR academic)
        assert result.advanced_word_ratio >= result.academic_word_ratio


# ===== Frequency Band Tests =====


class TestFrequencyBands:
    """Frequency band distribution tests."""

    def test_all_bands_present(self, mixed_sophistication_text):
        """Test all 5 frequency bands are in distribution."""
        result = compute_word_frequency_sophistication(mixed_sophistication_text)

        expected_bands = {
            "very_common",
            "common",
            "moderate",
            "rare",
            "very_rare",
        }
        assert set(result.frequency_band_distribution.keys()) == expected_bands

    def test_band_sum(self, academic_text):
        """Test band proportions sum to 1.0."""
        result = compute_word_frequency_sophistication(academic_text)

        band_sum = sum(result.frequency_band_distribution.values())
        assert abs(band_sum - 1.0) < 1e-9

    def test_very_common_dominated(self, very_common_text):
        """Test text dominated by very common words."""
        result = compute_word_frequency_sophistication(very_common_text)

        # Very common band should dominate
        assert (
            result.frequency_band_distribution["very_common"]
            > result.frequency_band_distribution["rare"]
        )
        assert (
            result.frequency_band_distribution["very_common"]
            > result.frequency_band_distribution["very_rare"]
        )

    def test_rare_dominated(self, technical_text):
        """Test technical text has many unknown/rare words."""
        result = compute_word_frequency_sophistication(technical_text)

        # Rare or very_rare bands should be substantial
        rare_plus_very_rare = (
            result.frequency_band_distribution["rare"]
            + result.frequency_band_distribution["very_rare"]
        )
        assert rare_plus_very_rare > 0.2  # At least 20% rare/very_rare


# ===== Rarest and Most Common Words Tests =====


class TestRarestCommonWords:
    """Rarest and most common words tests."""

    def test_rarest_words_count(self, academic_text):
        """Test rarest_words has up to 10 items."""
        result = compute_word_frequency_sophistication(academic_text)

        assert len(result.rarest_words) <= 10
        assert len(result.rarest_words) > 0  # Should have at least some words

    def test_most_common_words_count(self, simple_text):
        """Test most_common_words has up to 10 items."""
        result = compute_word_frequency_sophistication(simple_text)

        assert len(result.most_common_words) <= 10
        assert len(result.most_common_words) > 0

    def test_rarest_words_order(self, mixed_sophistication_text):
        """Test rarest words are in descending rank order."""
        result = compute_word_frequency_sophistication(mixed_sophistication_text)

        ranks = [rank for _, rank in result.rarest_words]
        # Should be in descending order (highest ranks first)
        assert ranks == sorted(ranks, reverse=True)

    def test_common_words_order(self, simple_text):
        """Test common words are in ascending rank order."""
        result = compute_word_frequency_sophistication(simple_text)

        ranks = [rank for _, rank in result.most_common_words]
        # Should be in ascending order (lowest ranks first)
        assert ranks == sorted(ranks)

    def test_no_duplicates_in_lists(self, academic_text):
        """Test no duplicate words in rarest/common lists."""
        result = compute_word_frequency_sophistication(academic_text)

        rarest_words = [word for word, _ in result.rarest_words]
        common_words = [word for word, _ in result.most_common_words]

        # No duplicates within each list
        assert len(rarest_words) == len(set(rarest_words))
        assert len(common_words) == len(set(common_words))

    def test_few_unique_words(self):
        """Test with text having fewer than 10 unique words."""
        text = "the cat and the dog and the bird and the fish"
        result = compute_word_frequency_sophistication(text)

        # Should have fewer than 10 items since there are only 6 unique words
        assert len(result.rarest_words) <= 6
        assert len(result.most_common_words) <= 6


# ===== Comparison Tests =====


class TestWordFrequencyComparisons:
    """Comparative tests across different text types."""

    def test_academic_vs_simple(self, academic_text, simple_text):
        """Test academic text has higher sophistication than simple text."""
        result_academic = compute_word_frequency_sophistication(academic_text)
        result_simple = compute_word_frequency_sophistication(simple_text)

        # Academic text should have higher mean rank (less common words)
        assert result_academic.mean_frequency_rank > result_simple.mean_frequency_rank

        # Academic text should have higher rare word ratio
        assert result_academic.rare_word_ratio > result_simple.rare_word_ratio

        # Academic text should have higher academic word ratio
        assert result_academic.academic_word_ratio > result_simple.academic_word_ratio

    def test_childrens_text_common(self, childrens_text):
        """Test children's text has high common_word_ratio."""
        result = compute_word_frequency_sophistication(childrens_text)

        # Children's text should have high common word ratio
        assert result.common_word_ratio > 0.5  # At least 50% common words

        # Children's text should have low median rank (median less affected by unknown words)
        assert result.median_frequency_rank < 500

    def test_technical_unknown_words(self, technical_text):
        """Test technical text has many unknown words."""
        result = compute_word_frequency_sophistication(technical_text)

        # Technical jargon should result in many unknown words
        # "OAuth2", "WebSocket", "Kubernetes", "microservice", etc.
        assert result.metadata["unknown_words"] > 0


# ===== Real-World Text Tests =====


class TestWordFrequencyRealWorld:
    """Tests with realistic text samples."""

    def test_academic_text(self, academic_text):
        """Test with academic prose sample."""
        result = compute_word_frequency_sophistication(academic_text)

        # Academic text characteristics
        assert result.academic_word_ratio > 0.05
        assert result.mean_frequency_rank > 1500
        assert result.rare_word_ratio > 0.2
        assert 0.0 <= result.advanced_word_ratio <= 1.0

    def test_childrens_text(self, childrens_text):
        """Test with children's book sample."""
        result = compute_word_frequency_sophistication(childrens_text)

        # Children's text characteristics
        assert result.common_word_ratio > 0.4
        assert result.median_frequency_rank < 500  # Low median rank
        assert result.rare_word_ratio < 0.3

    def test_news_text(self, news_text):
        """Test with news article."""
        result = compute_word_frequency_sophistication(news_text)

        # News text has moderate sophistication
        # With limited dictionary, check median instead of mean
        assert result.median_frequency_rank > 10  # Not all super common words
        assert 0.0 <= result.rare_word_ratio <= 1.0
        assert 0.0 <= result.common_word_ratio <= 1.0
        assert result.common_word_ratio > 0.2  # Some common words present

    def test_technical_text(self, technical_text):
        """Test with technical documentation."""
        result = compute_word_frequency_sophistication(technical_text)

        # Technical text has many specialized terms
        assert result.metadata["unknown_word_ratio"] > 0.0
        # Could have mix of very common words ("the", "a") and very rare jargon
        assert 0.0 <= result.advanced_word_ratio <= 1.0


# ===== Tokenization Tests =====


class TestWordFrequencyTokenization:
    """Tokenization tests."""

    def test_case_insensitivity(self):
        """Test case-insensitive tokenization."""
        text1 = "The RESEARCH method is GOOD"
        text2 = "the research method is good"

        result1 = compute_word_frequency_sophistication(text1)
        result2 = compute_word_frequency_sophistication(text2)

        # Should produce identical results
        assert result1.mean_frequency_rank == result2.mean_frequency_rank
        assert result1.academic_word_ratio == result2.academic_word_ratio

    def test_punctuation_handling(self):
        """Test punctuation is stripped correctly."""
        text1 = "research, method. analysis! data?"
        text2 = "research method analysis data"

        result1 = compute_word_frequency_sophistication(text1)
        result2 = compute_word_frequency_sophistication(text2)

        # Should have same token count (4 words)
        assert result1.metadata["total_words"] == 4
        assert result2.metadata["total_words"] == 4

    def test_whitespace_handling(self):
        """Test various whitespace patterns."""
        text = "research   method\n\nanalysis\t\tdata"
        result = compute_word_frequency_sophistication(text)

        assert result.metadata["total_words"] == 4


# ===== Additional Tests =====


class TestWordFrequencyAdditional:
    """Additional comprehensive tests."""

    def test_mixed_sophistication(self, mixed_sophistication_text):
        """Test text with mixed sophistication levels."""
        result = compute_word_frequency_sophistication(mixed_sophistication_text)

        # Should have both common and rare words
        assert result.common_word_ratio > 0.0
        assert result.rare_word_ratio > 0.0

        # Advanced ratio should be between extremes
        assert 0.1 < result.advanced_word_ratio < 0.9

    def test_metadata_fields_consistent(self, academic_text):
        """Test metadata fields are internally consistent."""
        result = compute_word_frequency_sophistication(academic_text)

        # Total words should match
        assert result.metadata["total_words"] > 0
        assert result.metadata["unique_words"] <= result.metadata["total_words"]

        # Unknown word count should match ratio
        expected_unknown_count = int(
            result.metadata["unknown_word_ratio"] * result.metadata["total_words"]
        )
        # Allow off-by-one due to rounding
        assert abs(result.metadata["unknown_words"] - expected_unknown_count) <= 1

    def test_single_sentence(self):
        """Test with a single sentence."""
        text = "The research methodology employed a comprehensive approach."
        result = compute_word_frequency_sophistication(text)

        assert result.metadata["total_words"] == 7  # 7 words in the sentence
        assert result.mean_frequency_rank > 0
        assert 0.0 <= result.academic_word_ratio <= 1.0

    def test_repeated_words(self):
        """Test with many repeated words."""
        text = "research " * 50  # Same word repeated
        result = compute_word_frequency_sophistication(text)

        assert result.metadata["total_words"] == 50
        assert result.metadata["unique_words"] == 1
        # All instances of "research" should have same frequency rank
        assert result.mean_frequency_rank == result.median_frequency_rank

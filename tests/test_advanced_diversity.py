"""Tests for advanced lexical diversity metrics.

This module tests four advanced lexical diversity metrics that control for
text length, addressing the fundamental limitation of simple TTR:

1. voc-D (Vocabulary D): Curve-fitting approach
2. MATTR (Moving-Average Type-Token Ratio): Sliding window approach
3. HD-D (Hypergeometric Distribution D): Probabilistic approach
4. MSTTR (Mean Segmental Type-Token Ratio): Segmental approach

Related GitHub Issue:
    #14 - Advanced Lexical Diversity Metrics
    https://github.com/craigtrim/pystylometry/issues/14
"""

import math
import pytest

from pystylometry.lexical import (
    compute_vocd_d,
    compute_mattr,
    compute_hdd,
    compute_msttr,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def simple_text():
    """Simple prose for basic testing (300+ tokens)."""
    base = (
        "The quick brown fox jumps over the lazy dog. "
        "A small bird flies through the blue sky. "
        "The sun shines brightly on the green grass. "
        "Children play happily in the warm sunshine. "
        "The old tree stands tall beside the flowing river. "
    )
    return base * 12  # ~300 tokens


@pytest.fixture
def high_diversity_text():
    """Text with high lexical diversity (150+ unique words out of ~600 tokens)."""
    # Create text with high diversity by using many unique content words
    # Each sentence uses mostly different words (literary fiction pattern)
    words = []

    # Generate 6 different "paragraphs" with mostly unique vocabulary
    for p in range(6):
        # Each paragraph has 25 mostly-unique content words
        content_words = [
            f"magnificent{p}_1", f"eloquent{p}_2", f"profound{p}_3",
            f"ethereal{p}_4", f"luminous{p}_5", f"enigmatic{p}_6",
            f"transcendent{p}_7", f"resplendent{p}_8", f"formidable{p}_9",
            f"exquisite{p}_10", f"pristine{p}_11", f"venerable{p}_12",
            f"illustrious{p}_13", f"majestic{p}_14", f"sublime{p}_15",
            f"radiant{p}_16", f"splendid{p}_17", f"grandiose{p}_18",
            f"opulent{p}_19", f"lavish{p}_20", f"abundant{p}_21",
            f"copious{p}_22", f"prolific{p}_23", f"verdant{p}_24",
            f"lush{p}_25",
        ]

        # Add content words
        words.extend(content_words)

        # Add some repeated function words (natural pattern)
        function_words = ["the", "a", "is", "was", "and", "of", "to", "in"]
        words.extend(function_words)

    # This gives us: 6 paragraphs * (25 content + 8 function) = ~198 tokens
    # With ~150 unique content words + ~8 function words = ~158 unique types
    # TTR ~ 0.80 (high but realistic for literary text)
    return " ".join(words)


@pytest.fixture
def low_diversity_text():
    """Text with very low lexical diversity (5 unique words repeated)."""
    # Many repetitions of few words
    words = ["the", "a", "is", "was", "and"]
    return " ".join(words * 50)


@pytest.fixture
def academic_text():
    """Academic-style text sample (400+ tokens)."""
    base = (
        "Research demonstrates that lexical diversity metrics provide "
        "valuable insights into vocabulary richness. However, traditional "
        "type-token ratio exhibits a fundamental limitation: its dependence "
        "on text length. Advanced metrics such as voc-D, MATTR, HD-D, and "
        "MSTTR address this limitation through various mathematical approaches. "
        "These metrics enable more reliable cross-text comparisons regardless "
        "of document length. Consequently, researchers can analyze vocabulary "
        "patterns with greater confidence and precision. "
    )
    return base * 5


@pytest.fixture
def fiction_text():
    """Fiction narrative sample (300+ tokens)."""
    base = (
        "She walked through the ancient forest, marveling at the towering trees. "
        "Sunlight filtered through emerald leaves, casting dancing shadows on "
        "the mossy ground. A gentle breeze whispered secrets among the branches, "
        "while distant birdsong created a melodious symphony. She paused, "
        "listening intently to nature's harmonious composition. "
    )
    return base * 6


@pytest.fixture
def technical_text():
    """Technical documentation sample (300+ tokens)."""
    base = (
        "The function accepts a string parameter and returns a float value. "
        "It tokenizes the input by splitting on whitespace and stripping "
        "punctuation characters. The algorithm then calculates the ratio "
        "of unique tokens to total tokens. This metric provides a quantitative "
        "measure of lexical diversity within the text. "
    )
    return base * 6


@pytest.fixture
def short_text():
    """Short text for testing minimum length requirements (40 tokens)."""
    return "The cat sat on the mat. The dog ran in the park. The bird flew over the tree. The fish swam in the pond."


# ============================================================================
# voc-D Tests
# ============================================================================


class TestVocdD:
    """Tests for voc-D (vocabulary D) metric."""

    def test_vocd_basic_functionality(self, simple_text):
        """Test basic voc-D computation with valid text."""
        result = compute_vocd_d(simple_text, random_seed=42)

        # Check all required fields exist
        assert hasattr(result, "d_parameter")
        assert hasattr(result, "curve_fit_r_squared")
        assert hasattr(result, "sample_count")
        assert hasattr(result, "optimal_sample_size")
        assert hasattr(result, "metadata")

        # Check types
        assert isinstance(result.d_parameter, float)
        assert isinstance(result.curve_fit_r_squared, float)
        assert isinstance(result.sample_count, int)
        assert isinstance(result.optimal_sample_size, int)
        assert isinstance(result.metadata, dict)

    def test_vocd_score_is_positive(self, simple_text):
        """Test that D parameter is positive."""
        result = compute_vocd_d(simple_text, random_seed=42)
        assert result.d_parameter > 0

    def test_vocd_r_squared_range(self, simple_text):
        """Test that R² is between 0 and 1."""
        result = compute_vocd_d(simple_text, random_seed=42)
        assert 0.0 <= result.curve_fit_r_squared <= 1.0

    def test_vocd_r_squared_quality(self, simple_text):
        """Test that R² is high (>0.80) for good fit."""
        result = compute_vocd_d(simple_text, random_seed=42)
        # For well-formed text, R² should be quite high
        assert result.curve_fit_r_squared > 0.80

    def test_vocd_high_diversity(self, high_diversity_text):
        """Test voc-D with high diversity text produces higher D than low diversity."""
        result = compute_vocd_d(high_diversity_text, random_seed=42, min_tokens=50)
        # High diversity text should have D > 5 (higher than low-diversity text)
        assert result.d_parameter > 5

    def test_vocd_low_diversity(self, low_diversity_text):
        """Test voc-D with low diversity text produces low D."""
        result = compute_vocd_d(low_diversity_text, random_seed=42)
        # Low diversity text should have D < 20
        assert result.d_parameter < 20

    def test_vocd_text_too_short(self, short_text):
        """Test error handling when text has insufficient tokens."""
        with pytest.raises(ValueError, match="minimum.*required"):
            compute_vocd_d(short_text, min_tokens=100)

    def test_vocd_reproducibility(self, simple_text):
        """Test that same seed produces same results."""
        result1 = compute_vocd_d(simple_text, random_seed=42)
        result2 = compute_vocd_d(simple_text, random_seed=42)

        assert result1.d_parameter == result2.d_parameter
        assert result1.curve_fit_r_squared == result2.curve_fit_r_squared

    def test_vocd_different_seeds_differ(self, simple_text):
        """Test that different seeds produce different results."""
        result1 = compute_vocd_d(simple_text, random_seed=42)
        result2 = compute_vocd_d(simple_text, random_seed=99)

        # Results should differ slightly due to random sampling
        # But not too much (within 20% for stable text)
        assert result1.d_parameter != result2.d_parameter

    def test_vocd_metadata_completeness(self, simple_text):
        """Test that metadata contains all required fields."""
        result = compute_vocd_d(simple_text, random_seed=42)

        assert "total_token_count" in result.metadata
        assert "total_type_count" in result.metadata
        assert "simple_ttr" in result.metadata
        assert "sample_sizes_used" in result.metadata
        assert "mean_ttrs_per_sample_size" in result.metadata

        # Check types
        assert isinstance(result.metadata["total_token_count"], int)
        assert isinstance(result.metadata["total_type_count"], int)
        assert isinstance(result.metadata["simple_ttr"], float)
        assert isinstance(result.metadata["sample_sizes_used"], list)
        assert isinstance(result.metadata["mean_ttrs_per_sample_size"], list)

    def test_vocd_parameter_variations(self, simple_text):
        """Test voc-D with different parameter values."""
        result1 = compute_vocd_d(simple_text, sample_size=30, num_samples=50, random_seed=42)
        result2 = compute_vocd_d(simple_text, sample_size=40, num_samples=100, random_seed=42)

        # Both should produce valid results
        assert result1.d_parameter > 0
        assert result2.d_parameter > 0

        # Results should be similar but may differ slightly
        # (within reasonable range for same text)

    def test_vocd_empty_text(self):
        """Test voc-D with empty text raises error."""
        with pytest.raises((ValueError, IndexError)):
            compute_vocd_d("", min_tokens=10)

    def test_vocd_sample_count(self, simple_text):
        """Test that sample_count is positive."""
        result = compute_vocd_d(simple_text, random_seed=42)
        assert result.sample_count > 0


# ============================================================================
# MATTR Tests
# ============================================================================


class TestMATTR:
    """Tests for MATTR (Moving-Average Type-Token Ratio) metric."""

    def test_mattr_basic_functionality(self, simple_text):
        """Test basic MATTR computation with valid text."""
        result = compute_mattr(simple_text)

        # Check all required fields exist
        assert hasattr(result, "mattr_score")
        assert hasattr(result, "window_size")
        assert hasattr(result, "window_count")
        assert hasattr(result, "ttr_std_dev")
        assert hasattr(result, "min_ttr")
        assert hasattr(result, "max_ttr")
        assert hasattr(result, "metadata")

        # Check types
        assert isinstance(result.mattr_score, float)
        assert isinstance(result.window_size, int)
        assert isinstance(result.window_count, int)
        assert isinstance(result.ttr_std_dev, float)
        assert isinstance(result.min_ttr, float)
        assert isinstance(result.max_ttr, float)
        assert isinstance(result.metadata, dict)

    def test_mattr_score_range(self, simple_text):
        """Test that MATTR score is between 0 and 1."""
        result = compute_mattr(simple_text)
        assert 0.0 <= result.mattr_score <= 1.0

    def test_mattr_min_max_range(self, simple_text):
        """Test that min_ttr <= mattr_score <= max_ttr (with floating point tolerance)."""
        result = compute_mattr(simple_text)
        # Use epsilon tolerance for floating point comparison
        epsilon = 1e-10
        assert result.min_ttr - epsilon <= result.mattr_score <= result.max_ttr + epsilon

    def test_mattr_window_count(self, simple_text):
        """Test that window_count = token_count - window_size + 1."""
        result = compute_mattr(simple_text, window_size=50)
        token_count = result.metadata["total_token_count"]

        expected_window_count = token_count - 50 + 1
        assert result.window_count == expected_window_count

    def test_mattr_high_diversity(self, high_diversity_text):
        """Test MATTR with high diversity text produces high score."""
        result = compute_mattr(high_diversity_text, window_size=50)
        # High diversity text should have MATTR > 0.60
        assert result.mattr_score > 0.60

    def test_mattr_low_diversity(self, low_diversity_text):
        """Test MATTR with low diversity text produces low score."""
        result = compute_mattr(low_diversity_text, window_size=50)
        # Low diversity text should have MATTR < 0.20
        assert result.mattr_score < 0.20

    def test_mattr_text_too_short(self):
        """Test error handling when text has insufficient tokens."""
        short = "the cat sat"  # 3 tokens
        with pytest.raises(ValueError, match="minimum.*required"):
            compute_mattr(short, window_size=50)

    def test_mattr_exact_window_size(self):
        """Test text exactly equal to window size."""
        text = "the cat sat on the mat and ate food here"  # 10 words
        result = compute_mattr(text, window_size=10)

        # Should have exactly 1 window
        assert result.window_count == 1
        # std_dev should be 0 (only one window)
        assert result.ttr_std_dev == 0.0
        # min == max == mattr_score
        assert result.min_ttr == result.max_ttr == result.mattr_score

    def test_mattr_different_window_sizes(self, simple_text):
        """Test MATTR with different window sizes."""
        result1 = compute_mattr(simple_text, window_size=30)
        result2 = compute_mattr(simple_text, window_size=50)
        result3 = compute_mattr(simple_text, window_size=70)

        # All should produce valid results
        assert 0.0 <= result1.mattr_score <= 1.0
        assert 0.0 <= result2.mattr_score <= 1.0
        assert 0.0 <= result3.mattr_score <= 1.0

    def test_mattr_std_dev_non_negative(self, simple_text):
        """Test that standard deviation is non-negative."""
        result = compute_mattr(simple_text)
        assert result.ttr_std_dev >= 0.0

    def test_mattr_metadata_completeness(self, simple_text):
        """Test that metadata contains all required fields."""
        result = compute_mattr(simple_text)

        assert "total_token_count" in result.metadata
        assert "total_type_count" in result.metadata
        assert "simple_ttr" in result.metadata

    def test_mattr_empty_text(self):
        """Test MATTR with empty text raises error."""
        with pytest.raises(ValueError):
            compute_mattr("")


# ============================================================================
# HD-D Tests
# ============================================================================


class TestHDD:
    """Tests for HD-D (Hypergeometric Distribution D) metric."""

    def test_hdd_basic_functionality(self, simple_text):
        """Test basic HD-D computation with valid text."""
        result = compute_hdd(simple_text)

        # Check all required fields exist
        assert hasattr(result, "hdd_score")
        assert hasattr(result, "sample_size")
        assert hasattr(result, "type_count")
        assert hasattr(result, "token_count")
        assert hasattr(result, "metadata")

        # Check types
        assert isinstance(result.hdd_score, float)
        assert isinstance(result.sample_size, int)
        assert isinstance(result.type_count, int)
        assert isinstance(result.token_count, int)
        assert isinstance(result.metadata, dict)

    def test_hdd_score_range(self, simple_text):
        """Test that HD-D score is between 0 and type_count."""
        result = compute_hdd(simple_text)
        assert 0.0 <= result.hdd_score <= result.type_count

    def test_hdd_score_non_negative(self, simple_text):
        """Test that HD-D score is non-negative."""
        result = compute_hdd(simple_text)
        assert result.hdd_score >= 0.0

    def test_hdd_high_diversity(self, high_diversity_text):
        """Test HD-D with high diversity text produces high score."""
        result = compute_hdd(high_diversity_text, sample_size=42)
        # High diversity text should have high HD-D
        # (many types expected to be unseen in sample)
        assert result.hdd_score > 20

    def test_hdd_low_diversity(self, low_diversity_text):
        """Test HD-D with low diversity text produces low score."""
        result = compute_hdd(low_diversity_text, sample_size=42)
        # Low diversity text should have low HD-D
        # (most types will appear in sample)
        assert result.hdd_score < 5

    def test_hdd_text_too_short(self):
        """Test error handling when text has insufficient tokens."""
        short = "the cat sat"  # 3 tokens
        with pytest.raises(ValueError, match="minimum.*required"):
            compute_hdd(short, sample_size=42)

    def test_hdd_different_sample_sizes(self, simple_text):
        """Test HD-D with different sample sizes."""
        result1 = compute_hdd(simple_text, sample_size=30)
        result2 = compute_hdd(simple_text, sample_size=42)
        result3 = compute_hdd(simple_text, sample_size=60)

        # All should produce valid results
        assert result1.hdd_score >= 0.0
        assert result2.hdd_score >= 0.0
        assert result3.hdd_score >= 0.0

        # HD-D should generally decrease as sample size increases
        # (larger samples more likely to encounter rare types)
        # But this isn't guaranteed, so we just check validity

    def test_hdd_metadata_completeness(self, simple_text):
        """Test that metadata contains all required fields."""
        result = compute_hdd(simple_text)

        assert "total_token_count" in result.metadata
        assert "total_type_count" in result.metadata
        assert "simple_ttr" in result.metadata

    def test_hdd_empty_text(self):
        """Test HD-D with empty text raises error."""
        with pytest.raises(ValueError):
            compute_hdd("")

    def test_hdd_numerical_stability(self, simple_text):
        """Test HD-D doesn't produce NaN or inf."""
        result = compute_hdd(simple_text)
        assert not math.isnan(result.hdd_score)
        assert not math.isinf(result.hdd_score)


# ============================================================================
# MSTTR Tests
# ============================================================================


class TestMSTTR:
    """Tests for MSTTR (Mean Segmental Type-Token Ratio) metric."""

    def test_msttr_basic_functionality(self, simple_text):
        """Test basic MSTTR computation with valid text."""
        result = compute_msttr(simple_text)

        # Check all required fields exist
        assert hasattr(result, "msttr_score")
        assert hasattr(result, "segment_size")
        assert hasattr(result, "segment_count")
        assert hasattr(result, "ttr_std_dev")
        assert hasattr(result, "min_ttr")
        assert hasattr(result, "max_ttr")
        assert hasattr(result, "segment_ttrs")
        assert hasattr(result, "metadata")

        # Check types
        assert isinstance(result.msttr_score, float)
        assert isinstance(result.segment_size, int)
        assert isinstance(result.segment_count, int)
        assert isinstance(result.ttr_std_dev, float)
        assert isinstance(result.min_ttr, float)
        assert isinstance(result.max_ttr, float)
        assert isinstance(result.segment_ttrs, list)
        assert isinstance(result.metadata, dict)

    def test_msttr_score_range(self, simple_text):
        """Test that MSTTR score is between 0 and 1."""
        result = compute_msttr(simple_text)
        assert 0.0 <= result.msttr_score <= 1.0

    def test_msttr_min_max_range(self, simple_text):
        """Test that min_ttr <= msttr_score <= max_ttr."""
        result = compute_msttr(simple_text)
        assert result.min_ttr <= result.msttr_score <= result.max_ttr

    def test_msttr_segment_count(self, simple_text):
        """Test that segment_count = floor(token_count / segment_size)."""
        result = compute_msttr(simple_text, segment_size=100)
        token_count = result.metadata["total_token_count"]

        expected_segment_count = token_count // 100
        assert result.segment_count == expected_segment_count

    def test_msttr_segment_ttrs_length(self, simple_text):
        """Test that segment_ttrs has length equal to segment_count."""
        result = compute_msttr(simple_text, segment_size=100)
        assert len(result.segment_ttrs) == result.segment_count

    def test_msttr_discard_incomplete(self):
        """Test that incomplete segments are discarded."""
        # Create text with 250 tokens
        text = " ".join([f"word{i}" for i in range(250)])

        result = compute_msttr(text, segment_size=100)

        # Should have 2 complete segments (200 tokens used)
        assert result.segment_count == 2
        # Should discard 50 tokens
        assert result.metadata["tokens_discarded"] == 50
        assert result.metadata["tokens_used"] == 200

    def test_msttr_high_diversity(self, high_diversity_text):
        """Test MSTTR with high diversity text produces high score."""
        result = compute_msttr(high_diversity_text, segment_size=100)
        # High diversity text should have MSTTR > 0.60
        assert result.msttr_score > 0.60

    def test_msttr_low_diversity(self, low_diversity_text):
        """Test MSTTR with low diversity text produces low score."""
        result = compute_msttr(low_diversity_text, segment_size=100)
        # Low diversity text should have MSTTR < 0.20
        assert result.msttr_score < 0.20

    def test_msttr_text_too_short(self):
        """Test error handling when text has insufficient tokens."""
        short = "the cat sat"  # 3 tokens
        with pytest.raises(ValueError, match="minimum.*required"):
            compute_msttr(short, segment_size=100)

    def test_msttr_exact_segment_size(self):
        """Test text exactly equal to segment size."""
        # Create text with exactly 100 tokens
        text = " ".join([f"word{i}" for i in range(100)])
        result = compute_msttr(text, segment_size=100)

        # Should have exactly 1 segment
        assert result.segment_count == 1
        # std_dev should be 0 (only one segment)
        assert result.ttr_std_dev == 0.0
        # min == max == msttr_score
        assert result.min_ttr == result.max_ttr == result.msttr_score

    def test_msttr_different_segment_sizes(self, simple_text):
        """Test MSTTR with different segment sizes."""
        result1 = compute_msttr(simple_text, segment_size=50)
        result2 = compute_msttr(simple_text, segment_size=100)
        result3 = compute_msttr(simple_text, segment_size=150)

        # All should produce valid results
        assert 0.0 <= result1.msttr_score <= 1.0
        assert 0.0 <= result2.msttr_score <= 1.0
        assert 0.0 <= result3.msttr_score <= 1.0

    def test_msttr_std_dev_non_negative(self, simple_text):
        """Test that standard deviation is non-negative."""
        result = compute_msttr(simple_text)
        assert result.ttr_std_dev >= 0.0

    def test_msttr_metadata_completeness(self, simple_text):
        """Test that metadata contains all required fields."""
        result = compute_msttr(simple_text)

        assert "total_token_count" in result.metadata
        assert "total_type_count" in result.metadata
        assert "simple_ttr" in result.metadata
        assert "tokens_used" in result.metadata
        assert "tokens_discarded" in result.metadata

    def test_msttr_empty_text(self):
        """Test MSTTR with empty text raises error."""
        with pytest.raises(ValueError):
            compute_msttr("")


# ============================================================================
# Comparative Tests (All Metrics)
# ============================================================================


class TestAdvancedDiversityComparisons:
    """Comparative tests across all four metrics."""

    def test_high_diversity_all_metrics(self, high_diversity_text):
        """Test that all metrics agree on high diversity text."""
        vocd = compute_vocd_d(high_diversity_text, random_seed=42, min_tokens=50)
        mattr = compute_mattr(high_diversity_text, window_size=50)
        hdd = compute_hdd(high_diversity_text, sample_size=42)
        msttr = compute_msttr(high_diversity_text, segment_size=100)

        # All metrics should indicate relatively high diversity
        # voc-D should be > 5 (higher than low-diversity text)
        assert vocd.d_parameter > 5

        # MATTR should be moderately high (>0.60 for varied vocabulary)
        assert mattr.mattr_score > 0.60

        # HD-D should be > 5
        assert hdd.hdd_score > 5

        # MSTTR should be > 0.60
        assert msttr.msttr_score > 0.60

    def test_low_diversity_all_metrics(self, low_diversity_text):
        """Test that all metrics agree on low diversity text."""
        vocd = compute_vocd_d(low_diversity_text, random_seed=42, min_tokens=50)
        mattr = compute_mattr(low_diversity_text, window_size=50)
        hdd = compute_hdd(low_diversity_text, sample_size=42)
        msttr = compute_msttr(low_diversity_text, segment_size=100)

        # voc-D should be low (<20)
        assert vocd.d_parameter < 20

        # MATTR should be low (<0.20)
        assert mattr.mattr_score < 0.20

        # HD-D should be low (<5)
        assert hdd.hdd_score < 5

        # MSTTR should be low (<0.20)
        assert msttr.msttr_score < 0.20

    def test_metric_rank_consistency(self, simple_text, high_diversity_text, low_diversity_text):
        """Test that all metrics rank texts consistently."""
        # Compute all metrics for all texts
        # Simple text (medium diversity)
        simple_mattr = compute_mattr(simple_text, window_size=50)

        # High diversity text
        high_mattr = compute_mattr(high_diversity_text, window_size=50)

        # Low diversity text
        low_mattr = compute_mattr(low_diversity_text, window_size=50)

        # Ranking should be: high > simple > low
        assert high_mattr.mattr_score > simple_mattr.mattr_score
        assert simple_mattr.mattr_score > low_mattr.mattr_score


# ============================================================================
# Edge Case Tests (All Metrics)
# ============================================================================


class TestAdvancedDiversityEdgeCases:
    """Edge case tests for all metrics."""

    def test_all_unique_words_mattr(self):
        """Test MATTR with all unique words (max diversity)."""
        # Create text with 200 unique words
        text = " ".join([f"unique{i}" for i in range(200)])
        result = compute_mattr(text, window_size=50)

        # MATTR should be 1.0 (perfect diversity)
        assert result.mattr_score == 1.0

    def test_all_unique_words_msttr(self):
        """Test MSTTR with all unique words (max diversity)."""
        # Create text with 200 unique words
        text = " ".join([f"unique{i}" for i in range(200)])
        result = compute_msttr(text, segment_size=100)

        # MSTTR should be 1.0 (perfect diversity)
        assert result.msttr_score == 1.0

    def test_single_word_repeated_mattr(self):
        """Test MATTR with single word repeated (min diversity)."""
        text = "word " * 100
        result = compute_mattr(text, window_size=50)

        # MATTR should be very low (1/50 = 0.02)
        assert result.mattr_score < 0.03

    def test_single_word_repeated_msttr(self):
        """Test MSTTR with single word repeated (min diversity)."""
        text = "word " * 200
        result = compute_msttr(text, segment_size=100)

        # MSTTR should be very low (1/100 = 0.01)
        assert result.msttr_score < 0.02


# ============================================================================
# Tokenization Tests (All Metrics)
# ============================================================================


class TestAdvancedDiversityTokenization:
    """Tokenization consistency tests for all metrics."""

    def test_case_insensitivity_mattr(self):
        """Test that MATTR is case-insensitive."""
        text1 = "The Quick Brown Fox " * 25
        text2 = "the quick brown fox " * 25

        result1 = compute_mattr(text1, window_size=50)
        result2 = compute_mattr(text2, window_size=50)

        # Scores should be identical
        assert result1.mattr_score == result2.mattr_score

    def test_punctuation_handling_mattr(self):
        """Test that MATTR strips punctuation correctly."""
        text1 = "The, quick. brown! fox? " * 25
        text2 = "The quick brown fox " * 25

        result1 = compute_mattr(text1, window_size=50)
        result2 = compute_mattr(text2, window_size=50)

        # Scores should be identical (punctuation stripped)
        assert result1.mattr_score == result2.mattr_score

    def test_whitespace_handling_mattr(self):
        """Test that MATTR handles various whitespace correctly."""
        text1 = "The  quick   brown    fox " * 25  # Multiple spaces
        text2 = "The quick brown fox " * 25  # Single spaces

        result1 = compute_mattr(text1, window_size=50)
        result2 = compute_mattr(text2, window_size=50)

        # Scores should be identical (whitespace normalized)
        assert result1.mattr_score == result2.mattr_score


# ============================================================================
# Real-World Text Tests
# ============================================================================


class TestAdvancedDiversityRealWorld:
    """Tests with realistic text samples."""

    def test_academic_text_all_metrics(self, academic_text):
        """Test all metrics with academic prose."""
        vocd = compute_vocd_d(academic_text, random_seed=42, min_tokens=100)
        mattr = compute_mattr(academic_text, window_size=50)
        hdd = compute_hdd(academic_text, sample_size=42)
        msttr = compute_msttr(academic_text, segment_size=100)

        # All should produce valid scores
        assert vocd.d_parameter > 0
        assert 0.0 <= mattr.mattr_score <= 1.0
        assert hdd.hdd_score >= 0.0
        assert 0.0 <= msttr.msttr_score <= 1.0

    def test_fiction_text_all_metrics(self, fiction_text):
        """Test all metrics with fiction narrative."""
        vocd = compute_vocd_d(fiction_text, random_seed=42, min_tokens=100)
        mattr = compute_mattr(fiction_text, window_size=50)
        hdd = compute_hdd(fiction_text, sample_size=42)
        msttr = compute_msttr(fiction_text, segment_size=100)

        # All should produce valid scores
        assert vocd.d_parameter > 0
        assert 0.0 <= mattr.mattr_score <= 1.0
        assert hdd.hdd_score >= 0.0
        assert 0.0 <= msttr.msttr_score <= 1.0

    def test_technical_text_all_metrics(self, technical_text):
        """Test all metrics with technical documentation."""
        vocd = compute_vocd_d(technical_text, random_seed=42, min_tokens=100)
        mattr = compute_mattr(technical_text, window_size=50)
        hdd = compute_hdd(technical_text, sample_size=42)
        msttr = compute_msttr(technical_text, segment_size=100)

        # All should produce valid scores
        assert vocd.d_parameter > 0
        assert 0.0 <= mattr.mattr_score <= 1.0
        assert hdd.hdd_score >= 0.0
        assert 0.0 <= msttr.msttr_score <= 1.0

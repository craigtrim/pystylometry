"""Tests for repetitive word and n-gram detection.

Related GitHub Issue:
    #28 - Verbal tics detection for slop analysis
    https://github.com/craigtrim/pystylometry/issues/28

This test suite covers:
    - Basic unigram detection with artificially repetitive text
    - Basic n-gram detection with repeated phrases
    - Edge cases (empty text, single word, short text)
    - Function word filtering (common phrases like "of the" not flagged)
    - Threshold and min_count parameter effects
    - Distribution metrics (entropy, variance)
    - N-gram validation (valid range, error messages)
    - Aggregate scoring (slop_score, flagged_per_10k)
    - Natural text produces few/no flags
"""

import math

import pytest

from pystylometry.lexical import compute_repetitive_ngrams, compute_repetitive_unigrams


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def repetitive_text():
    """Text with artificially repeated rare words — simulates AI slop."""
    # "shimmered" and "obsidian" are rare BNC words (bucket 5 and 7).
    # Repeating them 15+ times in a short text should trigger flagging.
    base = (
        "The castle walls shimmered in the moonlight. "
        "An obsidian tower rose above the landscape. "
        "The river shimmered beneath the stars. "
        "She gazed at the obsidian gates with wonder. "
    )
    # Repeat the base enough to get substantial counts
    return base * 10


@pytest.fixture
def natural_text():
    """Natural prose with normal word distribution — should produce few flags."""
    return (
        "The morning sun cast long shadows across the village square. "
        "Merchants set up their stalls, arranging fruits and vegetables "
        "in neat rows. Children ran between the carts, laughing and "
        "chasing each other. An old woman sat on a wooden bench, watching "
        "the commotion with quiet amusement. The baker emerged from his "
        "shop carrying fresh loaves, their aroma drifting through the air. "
        "Dogs barked at passing strangers while cats dozed on warm windowsills. "
        "The church bell rang twice, marking the hour. Farmers discussed "
        "the weather and crop prices over cups of strong coffee. A young "
        "girl played a flute near the fountain, drawing a small crowd of "
        "appreciative listeners. The cobblestone streets gleamed after the "
        "previous night's rain, reflecting the clear blue sky above."
    )


@pytest.fixture
def repeated_phrases_text():
    """Text with repeated content phrases — simulates AI verbal tics."""
    base = (
        "This is a testament to the remarkable progress we have made. "
        "The uncomfortable truth remains that challenges persist. "
        "A testament to human ingenuity can be found everywhere. "
        "The uncomfortable truth about modern society is complex. "
    )
    return base * 8


# ==============================================================================
# Unigram Tests
# ==============================================================================


class TestRepetitiveUnigrams:
    """Tests for compute_repetitive_unigrams."""

    def test_detects_repetitive_rare_words(self, repetitive_text):
        """Rare BNC words repeated many times should be flagged."""
        result = compute_repetitive_unigrams(repetitive_text)

        flagged_words = [w.word for w in result.repetitive_words]
        # "shimmered" appears 20 times (2 per base * 10 repeats)
        # BNC expected for ~400 words is near 0 — should be flagged
        assert "shimmered" in flagged_words
        assert "obsidian" in flagged_words

    def test_result_structure(self, repetitive_text):
        """Result should have all expected fields with correct types."""
        result = compute_repetitive_unigrams(repetitive_text)

        assert isinstance(result.repetitive_words, list)
        assert isinstance(result.total_content_words, int)
        assert isinstance(result.flagged_count, int)
        assert isinstance(result.flagged_words_per_10k, float)
        assert isinstance(result.mean_repetition_score, float)
        assert isinstance(result.slop_score, float)
        assert isinstance(result.chunk_size, int)
        assert isinstance(result.chunk_count, int)
        assert isinstance(result.metadata, dict)
        assert result.total_content_words > 0

    def test_repetitive_word_fields(self, repetitive_text):
        """Each RepetitiveWord should have correct field structure."""
        result = compute_repetitive_unigrams(repetitive_text)

        assert len(result.repetitive_words) > 0
        word = result.repetitive_words[0]

        assert isinstance(word.word, str)
        assert isinstance(word.count, int)
        assert isinstance(word.expected_count, float)
        assert isinstance(word.repetition_score, float)
        assert isinstance(word.chunk_counts, list)
        assert isinstance(word.distribution_entropy, float)
        assert isinstance(word.distribution_variance, float)
        assert word.count >= 3  # min_count default

    def test_sorted_by_score_descending(self, repetitive_text):
        """Flagged words should be sorted by repetition_score descending."""
        result = compute_repetitive_unigrams(repetitive_text)

        if len(result.repetitive_words) >= 2:
            scores = [w.repetition_score for w in result.repetitive_words]
            # Allow inf at the start
            for i in range(len(scores) - 1):
                if scores[i] != float("inf") and scores[i + 1] != float("inf"):
                    assert scores[i] >= scores[i + 1]

    def test_natural_text_fewer_flags(self, natural_text, repetitive_text):
        """Natural text should have fewer flagged words than repetitive text."""
        natural_result = compute_repetitive_unigrams(natural_text)
        repetitive_result = compute_repetitive_unigrams(repetitive_text)

        assert natural_result.flagged_count <= repetitive_result.flagged_count

    def test_empty_text(self):
        """Empty text should return empty result without error."""
        result = compute_repetitive_unigrams("")

        assert result.total_content_words == 0
        assert result.flagged_count == 0
        assert result.repetitive_words == []
        assert result.slop_score == 0.0

    def test_single_word(self):
        """Single word should not be flagged (below min_count)."""
        result = compute_repetitive_unigrams("hello")

        assert result.flagged_count == 0

    def test_min_count_parameter(self, repetitive_text):
        """Higher min_count should reduce flagged words."""
        result_low = compute_repetitive_unigrams(repetitive_text, min_count=3)
        result_high = compute_repetitive_unigrams(repetitive_text, min_count=15)

        assert result_high.flagged_count <= result_low.flagged_count

    def test_threshold_parameter(self, repetitive_text):
        """Higher threshold should reduce flagged words."""
        result_low = compute_repetitive_unigrams(repetitive_text, threshold=2.0)
        result_high = compute_repetitive_unigrams(repetitive_text, threshold=50.0)

        assert result_high.flagged_count <= result_low.flagged_count

    def test_chunk_counts_sum_to_total(self, repetitive_text):
        """Per-chunk counts should sum to the word's total count."""
        result = compute_repetitive_unigrams(repetitive_text)

        for word in result.repetitive_words:
            assert sum(word.chunk_counts) == word.count

    def test_slop_score_positive_for_repetitive(self, repetitive_text):
        """Slop score should be positive when repetitive words are found."""
        result = compute_repetitive_unigrams(repetitive_text)

        assert result.slop_score > 0.0

    def test_distribution_entropy_range(self, repetitive_text):
        """Entropy should be non-negative."""
        result = compute_repetitive_unigrams(repetitive_text)

        for word in result.repetitive_words:
            assert word.distribution_entropy >= 0.0

    def test_function_words_not_flagged(self):
        """Function words should never be flagged, even if highly repeated."""
        # "the" appears many times but is a function word
        text = "the the the the the quick brown fox the the the"
        result = compute_repetitive_unigrams(text)

        flagged_words = [w.word for w in result.repetitive_words]
        assert "the" not in flagged_words


# ==============================================================================
# N-gram Tests
# ==============================================================================


class TestRepetitiveNgrams:
    """Tests for compute_repetitive_ngrams."""

    def test_detects_repeated_phrases(self, repeated_phrases_text):
        """Repeated content phrases should be flagged."""
        result = compute_repetitive_ngrams(repeated_phrases_text, n=2)

        flagged_ngrams = [" ".join(ng.ngram) for ng in result.repetitive_ngrams]
        # "uncomfortable truth" appears 16 times (2 per base * 8 repeats)
        assert any("uncomfortable truth" in ng for ng in flagged_ngrams)

    def test_result_structure(self, repeated_phrases_text):
        """Result should have all expected fields."""
        result = compute_repetitive_ngrams(repeated_phrases_text, n=2)

        assert isinstance(result.repetitive_ngrams, list)
        assert result.n == 2
        assert isinstance(result.total_ngrams, int)
        assert isinstance(result.flagged_count, int)
        assert isinstance(result.flagged_per_10k, float)
        assert isinstance(result.chunk_size, int)
        assert isinstance(result.chunk_count, int)
        assert isinstance(result.metadata, dict)

    def test_ngram_fields(self, repeated_phrases_text):
        """Each RepetitiveNgram should have correct structure."""
        result = compute_repetitive_ngrams(repeated_phrases_text, n=2)

        if result.repetitive_ngrams:
            ng = result.repetitive_ngrams[0]
            assert isinstance(ng.ngram, tuple)
            assert len(ng.ngram) == 2
            assert isinstance(ng.count, int)
            assert isinstance(ng.frequency_per_10k, float)
            assert isinstance(ng.chunk_counts, list)
            assert isinstance(ng.distribution_entropy, float)
            assert isinstance(ng.distribution_variance, float)

    def test_function_word_ngrams_not_flagged(self):
        """N-grams composed entirely of function words should be excluded."""
        # "of the" is all function words — should not be flagged
        text = " ".join(["of the house"] * 20)
        result = compute_repetitive_ngrams(text, n=2, min_count=3)

        all_function_ngrams = [
            ng for ng in result.repetitive_ngrams
            if all(w in {"of", "the", "a", "in", "on", "to", "and", "is", "it", "for"}
                   for w in ng.ngram)
        ]
        assert len(all_function_ngrams) == 0

    def test_empty_text(self):
        """Empty text should return empty result."""
        result = compute_repetitive_ngrams("")

        assert result.total_ngrams == 0
        assert result.flagged_count == 0
        assert result.repetitive_ngrams == []

    def test_n_tuple_multiple_orders(self, repeated_phrases_text):
        """Tuple n should analyze multiple n-gram orders."""
        result = compute_repetitive_ngrams(repeated_phrases_text, n=(2, 3))

        assert result.n == (2, 3)
        # Should find both bigrams and trigrams
        ngram_sizes = {len(ng.ngram) for ng in result.repetitive_ngrams}
        # At least one order should produce results
        assert len(ngram_sizes) >= 1

    def test_n_single_int(self, repeated_phrases_text):
        """Single integer n should work."""
        result = compute_repetitive_ngrams(repeated_phrases_text, n=3)
        assert result.n == 3

    def test_n_validation_too_small(self):
        """n < 2 should raise ValueError with helpful message."""
        with pytest.raises(ValueError, match="too small.*compute_repetitive_unigrams"):
            compute_repetitive_ngrams("some text", n=1)

    def test_n_validation_too_large(self):
        """n > 5 should raise ValueError with helpful message."""
        with pytest.raises(ValueError, match="too large.*too sparse"):
            compute_repetitive_ngrams("some text", n=6)

    def test_n_validation_tuple_with_invalid(self):
        """Tuple with invalid values should raise ValueError."""
        with pytest.raises(ValueError):
            compute_repetitive_ngrams("some text", n=(2, 7))

    def test_sorted_by_count_descending(self, repeated_phrases_text):
        """Flagged n-grams should be sorted by count descending."""
        result = compute_repetitive_ngrams(repeated_phrases_text, n=2)

        if len(result.repetitive_ngrams) >= 2:
            counts = [ng.count for ng in result.repetitive_ngrams]
            for i in range(len(counts) - 1):
                assert counts[i] >= counts[i + 1]

    def test_chunk_counts_sum_to_total(self, repeated_phrases_text):
        """Per-chunk counts should sum to the n-gram's total count."""
        result = compute_repetitive_ngrams(repeated_phrases_text, n=2)

        for ng in result.repetitive_ngrams:
            assert sum(ng.chunk_counts) == ng.count

    def test_min_count_parameter(self, repeated_phrases_text):
        """Higher min_count should reduce flagged n-grams."""
        result_low = compute_repetitive_ngrams(repeated_phrases_text, n=2, min_count=2)
        result_high = compute_repetitive_ngrams(repeated_phrases_text, n=2, min_count=10)

        assert result_high.flagged_count <= result_low.flagged_count


# ==============================================================================
# Distribution Metric Tests
# ==============================================================================


class TestDistributionMetrics:
    """Tests for distribution entropy and variance calculations."""

    def test_even_distribution_low_entropy_relative(self):
        """Evenly distributed word should have higher entropy than clustered.

        Uses small chunk_size to ensure multiple chunks are created from
        the test texts.
        """
        # Create text where "obsidian" appears evenly across sections
        # Pad with enough filler words to get multiple chunks at chunk_size=20
        even_parts = []
        for i in range(10):
            even_parts.append(
                f"The obsidian walls stood firm against the harsh cold wind "
                f"Birds flew past the old stone tower on a warm sunny day "
                f"The river flowed gently below the ancient wooden bridge "
            )
        even_text = " ".join(even_parts)

        # Create text where "obsidian" is clustered in the first section only
        clustered_parts = []
        for i in range(10):
            if i < 2:
                clustered_parts.append(
                    f"The obsidian obsidian obsidian obsidian obsidian walls "
                    f"More obsidian dark obsidian structures appeared nearby "
                )
            else:
                clustered_parts.append(
                    f"The sunlight warmed the green valley on this fine day "
                    f"Flowers bloomed across the wide meadow quite naturally "
                )
        clustered_text = " ".join(clustered_parts)

        even_result = compute_repetitive_unigrams(
            even_text, threshold=1.0, min_count=2, chunk_size=20
        )
        clustered_result = compute_repetitive_unigrams(
            clustered_text, threshold=1.0, min_count=2, chunk_size=20
        )

        even_obsidian = next(
            (w for w in even_result.repetitive_words if w.word == "obsidian"), None
        )
        clustered_obsidian = next(
            (w for w in clustered_result.repetitive_words if w.word == "obsidian"), None
        )

        # Both should be found
        assert even_obsidian is not None, "obsidian not flagged in even text"
        assert clustered_obsidian is not None, "obsidian not flagged in clustered text"

        # Even distribution should have higher entropy than clustered
        assert even_obsidian.distribution_entropy > clustered_obsidian.distribution_entropy

    def test_entropy_is_zero_for_single_chunk(self):
        """Word appearing in only one chunk should have entropy of 0."""
        # Very short text — fits in one chunk
        text = "obsidian obsidian obsidian walls dark castle night"
        result = compute_repetitive_unigrams(text, chunk_size=1000, threshold=1.0, min_count=2)

        for word in result.repetitive_words:
            if word.word == "obsidian":
                # Single chunk → all weight in one bin → entropy = 0
                assert word.distribution_entropy == 0.0


# ==============================================================================
# Import Tests
# ==============================================================================


class TestImports:
    """Test that functions are accessible from the lexical module."""

    def test_import_from_lexical(self):
        """Functions should be importable from pystylometry.lexical."""
        from pystylometry.lexical import compute_repetitive_ngrams, compute_repetitive_unigrams

        assert callable(compute_repetitive_unigrams)
        assert callable(compute_repetitive_ngrams)

    def test_import_result_types(self):
        """Result types should be importable from pystylometry._types."""
        from pystylometry._types import (
            RepetitiveNgram,
            RepetitiveNgramsResult,
            RepetitiveUnigramsResult,
            RepetitiveWord,
        )

        assert RepetitiveWord is not None
        assert RepetitiveUnigramsResult is not None
        assert RepetitiveNgram is not None
        assert RepetitiveNgramsResult is not None

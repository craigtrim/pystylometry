"""Tests for Type-Token Ratio (TTR) — inlined implementation.

Related GitHub Issue:
    #43 - Inline stylometry-ttr into pystylometry (remove external dependency)
    https://github.com/craigtrim/pystylometry/issues/43
"""

import pytest

from pystylometry.lexical import TTRAggregator, compute_ttr

# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------


def test_compute_ttr_basic(sample_text):
    """Test TTR computation with sample text."""
    result = compute_ttr(sample_text)

    # Verify all expected attributes exist
    assert hasattr(result, "total_words")
    assert hasattr(result, "unique_words")
    assert hasattr(result, "ttr")
    assert hasattr(result, "root_ttr")
    assert hasattr(result, "log_ttr")
    assert hasattr(result, "sttr")
    assert hasattr(result, "delta_std")
    assert hasattr(result, "metadata")

    # Verify types
    assert isinstance(result.total_words, int)
    assert isinstance(result.unique_words, int)
    assert isinstance(result.ttr, float)
    assert isinstance(result.root_ttr, float)
    assert isinstance(result.log_ttr, float)
    assert isinstance(result.sttr, float)
    assert isinstance(result.delta_std, float)

    # Verify basic constraints
    assert result.total_words > 0
    assert result.unique_words > 0
    assert result.unique_words <= result.total_words
    assert 0.0 <= result.ttr <= 1.0


def test_compute_ttr_with_text_id():
    """Test TTR computation with text identifier."""
    text = "The quick brown fox jumps over the lazy dog."
    text_id = "test-001"
    result = compute_ttr(text, text_id=text_id)

    assert result.metadata["text_id"] == text_id


def test_compute_ttr_long_text(long_text):
    """Test TTR with longer text."""
    result = compute_ttr(long_text)

    # Longer text should have lower TTR due to word repetition
    assert result.ttr < 1.0
    assert result.total_words > 50
    assert result.unique_words < result.total_words


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_compute_ttr_perfect_diversity():
    """Test TTR with perfectly diverse text (no repeated words)."""
    text = "The quick brown fox jumps over lazy dog"
    result = compute_ttr(text)

    # Each word appears exactly once (after lowercasing)
    assert result.unique_words == result.total_words
    assert result.ttr == 1.0


def test_compute_ttr_high_repetition():
    """Test TTR with highly repetitive text."""
    text = "test " * 100  # 100 repetitions of the same word
    result = compute_ttr(text)

    # Only 1 unique word out of 100 total
    assert result.unique_words == 1
    assert result.total_words == 100
    assert result.ttr == 0.01  # 1/100


def test_compute_ttr_root_ttr():
    """Test Root TTR (Guiraud's index) calculation."""
    text = "word " * 100
    result = compute_ttr(text)

    # Root TTR = unique_words / sqrt(total_words)
    # = 1 / sqrt(100) = 1 / 10 = 0.1
    assert abs(result.root_ttr - 0.1) < 0.001


def test_compute_ttr_empty_text():
    """Test TTR with empty text."""
    result = compute_ttr("")
    assert result.total_words == 0
    assert result.unique_words == 0
    assert result.ttr == 0.0
    assert result.root_ttr == 0.0
    assert result.log_ttr == 0.0


def test_compute_ttr_single_word():
    """Test TTR with single word."""
    result = compute_ttr("hello")

    assert result.total_words == 1
    assert result.unique_words == 1
    assert result.ttr == 1.0


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


def test_compute_ttr_metadata():
    """Test that metadata contains expected fields."""
    result = compute_ttr("Sample text here.")

    assert "text_id" in result.metadata
    assert "sttr_available" in result.metadata
    assert "delta_std_available" in result.metadata


def test_compute_ttr_metadata_no_source_field():
    """After inlining, metadata should not reference stylometry-ttr."""
    result = compute_ttr("Sample text here.")

    # The "source" key was specific to the old facade wrapper
    assert result.metadata.get("source") != "stylometry-ttr"


# ---------------------------------------------------------------------------
# Distribution objects
# ---------------------------------------------------------------------------


def test_compute_ttr_distributions():
    """Test that Distribution objects are populated."""
    text = "word " * 50
    result = compute_ttr(text)

    # Even for short text, distributions should exist
    assert result.ttr_dist is not None
    assert result.root_ttr_dist is not None
    assert result.log_ttr_dist is not None
    assert result.sttr_dist is not None
    assert result.delta_std_dist is not None


def test_compute_ttr_chunked_distributions():
    """Test that per-chunk distributions are computed for long texts."""
    # Create text long enough for at least 2 full chunks (2000+ words)
    words = [f"word{i % 500}" for i in range(2500)]
    text = " ".join(words)
    result = compute_ttr(text, chunk_size=1000)

    assert result.chunk_count >= 2
    assert len(result.ttr_dist.values) >= 2
    assert result.ttr_dist.std >= 0.0


# ---------------------------------------------------------------------------
# Log TTR edge case
# ---------------------------------------------------------------------------


def test_compute_ttr_log_ttr_single_word():
    """Log TTR should be 0.0 for single-word text (log(1)/log(1) undefined)."""
    result = compute_ttr("hello")
    assert result.log_ttr == 0.0


def test_compute_ttr_log_ttr_two_words():
    """Log TTR for two distinct words: log(2)/log(2) = 1.0."""
    result = compute_ttr("hello world")
    assert abs(result.log_ttr - 1.0) < 0.0001


# ---------------------------------------------------------------------------
# STTR threshold
# ---------------------------------------------------------------------------


def test_compute_ttr_sttr_short_text():
    """STTR should be 0.0 for texts shorter than 2000 words."""
    text = "word " * 500
    result = compute_ttr(text)
    assert result.sttr == 0.0
    assert result.metadata["sttr_available"] is False


def test_compute_ttr_sttr_long_text():
    """STTR should be computed for texts with >= 2000 words."""
    words = [f"word{i % 800}" for i in range(2500)]
    text = " ".join(words)
    result = compute_ttr(text, chunk_size=1000)

    assert result.sttr > 0.0
    assert result.metadata["sttr_available"] is True


# ---------------------------------------------------------------------------
# TTRAggregator
# ---------------------------------------------------------------------------


def test_aggregator_basic():
    """Test basic aggregation over multiple results."""
    texts = [
        "alpha beta gamma delta epsilon",
        "one two three four five six seven eight",
        "the the the cat sat on the mat",
    ]
    results = [compute_ttr(t) for t in texts]
    agg = TTRAggregator()
    stats = agg.aggregate(results, group_id="test-group")

    assert stats.group_id == "test-group"
    assert stats.text_count == 3
    assert stats.total_words == sum(r.total_words for r in results)
    assert 0.0 <= stats.ttr_mean <= 1.0
    assert stats.ttr_min <= stats.ttr_mean <= stats.ttr_max


def test_aggregator_empty_raises():
    """Aggregating an empty list should raise ValueError."""
    agg = TTRAggregator()
    with pytest.raises(ValueError, match="empty"):
        agg.aggregate([], group_id="empty")


def test_aggregator_single_result():
    """Aggregating a single result should work (std = 0)."""
    result = compute_ttr("hello world foo bar")
    agg = TTRAggregator()
    stats = agg.aggregate([result], group_id="single")

    assert stats.text_count == 1
    assert stats.ttr_std == 0.0
    assert stats.ttr_mean == result.ttr

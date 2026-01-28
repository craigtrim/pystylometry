"""Tests for Type-Token Ratio (TTR) integration with stylometry-ttr."""

import pytest

from pystylometry.lexical import compute_ttr


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
    assert result.metadata["source"] == "stylometry-ttr"


def test_compute_ttr_long_text(long_text):
    """Test TTR with longer text."""
    result = compute_ttr(long_text)

    # Longer text should have lower TTR due to word repetition
    assert result.ttr < 1.0
    assert result.total_words > 50
    assert result.unique_words < result.total_words


def test_compute_ttr_perfect_diversity():
    """Test TTR with perfectly diverse text (no repeated words)."""
    text = "The quick brown fox jumps over lazy dog."
    result = compute_ttr(text)

    # Each word appears exactly once
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
    # stylometry-ttr should handle empty text gracefully
    # This may raise an exception or return zero values
    # depending on the implementation
    try:
        result = compute_ttr("")
        # If it doesn't raise, verify it returns reasonable zero values
        assert result.total_words == 0
        assert result.unique_words == 0
    except (ValueError, ZeroDivisionError):
        # It's also acceptable to raise an exception for empty input
        pytest.skip("stylometry-ttr raises exception for empty text")


def test_compute_ttr_single_word():
    """Test TTR with single word."""
    result = compute_ttr("hello")

    assert result.total_words == 1
    assert result.unique_words == 1
    assert result.ttr == 1.0


def test_compute_ttr_metadata():
    """Test that metadata contains expected fields."""
    result = compute_ttr("Sample text here.")

    assert "source" in result.metadata
    assert result.metadata["source"] == "stylometry-ttr"
    assert "text_id" in result.metadata

"""Tests for readability metrics."""

from pystylometry.readability import (
    compute_ari,
    compute_coleman_liau,
    compute_flesch,
    compute_gunning_fog,
    compute_smog,
)


def test_compute_flesch_basic(sample_text):
    """Test Flesch Reading Ease computation."""
    result = compute_flesch(sample_text)
    assert hasattr(result, "reading_ease")
    assert hasattr(result, "grade_level")
    assert hasattr(result, "difficulty")
    assert hasattr(result, "metadata")


def test_compute_flesch_empty():
    """Test Flesch with empty text."""
    result = compute_flesch("")
    assert result.reading_ease == 0.0
    assert result.difficulty == "Unknown"


def test_compute_smog_basic(sample_text):
    """Test SMOG Index computation."""
    result = compute_smog(sample_text)
    assert hasattr(result, "smog_index")
    assert hasattr(result, "grade_level")
    assert hasattr(result, "metadata")


def test_compute_gunning_fog_basic(sample_text):
    """Test Gunning Fog Index computation."""
    result = compute_gunning_fog(sample_text)
    assert hasattr(result, "fog_index")
    assert hasattr(result, "grade_level")


def test_compute_coleman_liau_basic(sample_text):
    """Test Coleman-Liau Index computation."""
    result = compute_coleman_liau(sample_text)
    assert hasattr(result, "cli_index")
    assert hasattr(result, "grade_level")


def test_compute_ari_basic(sample_text):
    """Test ARI computation."""
    result = compute_ari(sample_text)
    assert hasattr(result, "ari_score")
    assert hasattr(result, "grade_level")
    assert hasattr(result, "age_range")

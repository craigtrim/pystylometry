"""Tests for lexical diversity metrics."""

import math

from pystylometry.lexical import compute_hapax_ratios, compute_mtld, compute_yule


def test_compute_mtld_basic(sample_text):
    """Test MTLD computation with sample text."""
    result = compute_mtld(sample_text)
    assert hasattr(result, "mtld_forward")
    assert hasattr(result, "mtld_backward")
    assert hasattr(result, "mtld_average")
    assert hasattr(result, "metadata")


def test_compute_mtld_empty():
    """Test MTLD with empty text."""
    result = compute_mtld("")
    # Empty text returns NaN for metrics (per Distribution pattern)
    assert math.isnan(result.mtld_average)
    assert result.metadata["total_token_count"] == 0


def test_compute_yule_basic(sample_text):
    """Test Yule's K and I computation."""
    result = compute_yule(sample_text)
    assert hasattr(result, "yule_k")
    assert hasattr(result, "yule_i")
    assert hasattr(result, "metadata")


def test_compute_yule_empty():
    """Test Yule with empty text."""
    result = compute_yule("")
    assert math.isnan(result.yule_k)
    assert math.isnan(result.yule_i)


def test_compute_hapax_basic(sample_text):
    """Test hapax legomena analysis."""
    result = compute_hapax_ratios(sample_text)
    assert hasattr(result, "hapax_count")
    assert hasattr(result, "hapax_ratio")
    assert hasattr(result, "dis_hapax_count")
    assert hasattr(result, "dis_hapax_ratio")
    assert hasattr(result, "sichel_s")
    assert hasattr(result, "honore_r")


def test_compute_hapax_empty():
    """Test hapax with empty text."""
    result = compute_hapax_ratios("")
    assert result.hapax_count == 0
    # Empty text returns NaN for ratio metrics (per Distribution pattern)
    assert math.isnan(result.hapax_ratio)

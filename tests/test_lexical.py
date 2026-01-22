"""Tests for lexical diversity metrics."""

import pytest
from pystylometry.lexical import compute_mtld, compute_yule, compute_hapax_ratios


def test_compute_mtld_basic(sample_text):
    """Test MTLD computation with sample text."""
    result = compute_mtld(sample_text)
    assert hasattr(result, 'mtld_forward')
    assert hasattr(result, 'mtld_backward')
    assert hasattr(result, 'mtld_average')
    assert hasattr(result, 'metadata')


def test_compute_mtld_empty():
    """Test MTLD with empty text."""
    result = compute_mtld("")
    assert result.mtld_average == 0.0
    assert result.metadata['token_count'] == 0


def test_compute_yule_basic(sample_text):
    """Test Yule's K and I computation."""
    result = compute_yule(sample_text)
    assert hasattr(result, 'yule_k')
    assert hasattr(result, 'yule_i')
    assert hasattr(result, 'metadata')


def test_compute_yule_empty():
    """Test Yule with empty text."""
    result = compute_yule("")
    assert result.yule_k == 0.0
    assert result.yule_i == 0.0


def test_compute_hapax_basic(sample_text):
    """Test hapax legomena analysis."""
    result = compute_hapax_ratios(sample_text)
    assert hasattr(result, 'hapax_count')
    assert hasattr(result, 'hapax_ratio')
    assert hasattr(result, 'dis_hapax_count')
    assert hasattr(result, 'dis_hapax_ratio')
    assert hasattr(result, 'sichel_s')
    assert hasattr(result, 'honore_r')


def test_compute_hapax_empty():
    """Test hapax with empty text."""
    result = compute_hapax_ratios("")
    assert result.hapax_count == 0
    assert result.hapax_ratio == 0.0

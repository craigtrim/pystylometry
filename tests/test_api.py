"""Tests for the unified API."""

import pytest
from pystylometry import analyze, get_available_modules, __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_get_available_modules():
    """Test availability check function."""
    available = get_available_modules()
    assert isinstance(available, dict)
    assert "lexical" in available
    assert available["lexical"] is True  # Lexical is always available


def test_analyze_lexical_only(sample_text):
    """Test unified analyze with only lexical metrics."""
    result = analyze(sample_text, lexical=True)
    assert result.lexical is not None
    assert 'mtld' in result.lexical
    assert 'yule' in result.lexical
    assert 'hapax' in result.lexical


def test_analyze_empty_text():
    """Test analyze with empty text."""
    result = analyze("", lexical=True)
    assert result.lexical is not None


def test_analyze_no_metrics():
    """Test analyze with all metrics disabled."""
    result = analyze("test text", lexical=False)
    assert result.lexical is None
    assert result.readability is None


@pytest.mark.skipif(
    not get_available_modules()["readability"],
    reason="Readability module not installed"
)
def test_analyze_with_readability(sample_text):
    """Test analyze with readability metrics if available."""
    result = analyze(sample_text, lexical=True, readability=True)
    assert result.lexical is not None
    assert result.readability is not None
    assert 'flesch' in result.readability

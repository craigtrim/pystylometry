"""Tests for sentence type classification (Issue #18)."""

import pytest

from pystylometry.syntactic.sentence_types import compute_sentence_types

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def mixed_functional():
    """Text with mixed functional types."""
    return (
        "The sky is blue. "  # Declarative
        "Is it raining? "  # Interrogative
        "Close the window. "  # Imperative
        "What a lovely day!"  # Exclamatory
    )


@pytest.fixture
def mixed_structural():
    """Text with mixed structural types."""
    return (
        "The cat sat. "  # Simple
        "I came and I saw. "  # Compound
        "When I arrived, I saw her. "  # Complex
        "When I called, she came and she stayed."  # Compound-complex
    )


class TestRatioValidation:
    """Test that ratios are valid and sum correctly."""

    def test_structural_ratios_sum(self, mixed_structural):
        """Structural ratios should sum to 1.0."""
        result = compute_sentence_types(mixed_structural)

        total_structural = (
            result.simple_ratio
            + result.compound_ratio
            + result.complex_ratio
            + result.compound_complex_ratio
        )
        assert total_structural == pytest.approx(1.0, abs=0.01)

    def test_functional_ratios_sum(self, mixed_functional):
        """Functional ratios should sum to 1.0."""
        result = compute_sentence_types(mixed_functional)

        total_functional = (
            result.declarative_ratio
            + result.interrogative_ratio
            + result.imperative_ratio
            + result.exclamatory_ratio
        )
        assert total_functional == pytest.approx(1.0, abs=0.01)

    def test_all_ratios_in_range(self, mixed_structural):
        """All ratios should be between 0.0 and 1.0."""
        result = compute_sentence_types(mixed_structural)

        # Structural ratios
        assert 0.0 <= result.simple_ratio <= 1.0
        assert 0.0 <= result.compound_ratio <= 1.0
        assert 0.0 <= result.complex_ratio <= 1.0
        assert 0.0 <= result.compound_complex_ratio <= 1.0

        # Functional ratios
        assert 0.0 <= result.declarative_ratio <= 1.0
        assert 0.0 <= result.interrogative_ratio <= 1.0
        assert 0.0 <= result.imperative_ratio <= 1.0
        assert 0.0 <= result.exclamatory_ratio <= 1.0

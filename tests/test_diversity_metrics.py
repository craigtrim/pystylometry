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


@pytest.fixture
def simple_sentences():
    """Text with only simple sentences."""
    return "The cat sat. The dog ran. A bird flew."


class TestDiversityMetrics:
    """Test Shannon entropy diversity metrics."""

    def test_zero_diversity_structural(self, simple_sentences):
        """Test zero diversity (all same type)."""
        result = compute_sentence_types(simple_sentences)

        # All simple sentences = zero diversity
        assert result.structural_diversity == 0.0

    def test_low_diversity_structural(self):
        """Test low diversity (mostly one type)."""
        text = "Simple. Simple. Simple. When complex, it happens."
        result = compute_sentence_types(text)

        # Mostly simple, some complex = low diversity
        assert 0 < result.structural_diversity < 1.0

    def test_high_diversity_structural(self, mixed_structural):
        """Test high diversity (balanced distribution)."""
        result = compute_sentence_types(mixed_structural)

        # Multiple types = higher diversity
        assert result.structural_diversity > 0.5

    def test_shannon_entropy_calculation(self, mixed_functional):
        """Test Shannon entropy calculation."""
        result = compute_sentence_types(mixed_functional)

        # Should have positive functional diversity
        assert result.functional_diversity > 0

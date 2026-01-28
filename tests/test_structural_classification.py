"""Tests for sentence type classification (Issue #18)."""

import pytest

from pystylometry.syntactic.sentence_types import compute_sentence_types

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def complex_sentences():
    """Text with complex sentences."""
    return (
        "When I arrived, I saw her. "
        "Although it was raining, we went outside. "
        "Because the test failed, we had to restart."
    )


@pytest.fixture
def compound_complex_sentences():
    """Text with compound-complex sentences."""
    return "When I called, she came and she stayed. Although we tried, we failed but we learned."


@pytest.fixture
def compound_sentences():
    """Text with compound sentences."""
    return "I came and I saw. She laughed but he cried. We won or they lost."


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


class TestStructuralClassification:
    """Test structural classification (simple, compound, complex, compound-complex)."""

    def test_simple_sentences_only(self, simple_sentences):
        """Test text with only simple sentences."""
        result = compute_sentence_types(simple_sentences)

        # Should have high simple ratio
        assert result.simple_ratio >= 0.8
        assert result.simple_count >= 2

    def test_compound_sentences_only(self, compound_sentences):
        """Test text with compound sentences."""
        result = compute_sentence_types(compound_sentences)

        # Should have compound sentences
        assert result.compound_count >= 1
        assert result.compound_ratio > 0

    def test_complex_sentences_only(self, complex_sentences):
        """Test text with complex sentences."""
        result = compute_sentence_types(complex_sentences)

        # Should have complex sentences
        assert result.complex_count >= 2
        assert result.complex_ratio >= 0.5

    def test_compound_complex_sentences(self, compound_complex_sentences):
        """Test text with compound-complex sentences."""
        result = compute_sentence_types(compound_complex_sentences)

        # Should have compound-complex sentences
        assert result.compound_complex_count >= 1

    def test_mixed_structural_types(self, mixed_structural):
        """Test text with all structural types."""
        result = compute_sentence_types(mixed_structural)

        # Should have all types represented
        assert result.simple_count > 0
        assert result.compound_count > 0
        assert result.complex_count > 0

    def test_clause_counting_accuracy(self, mixed_structural):
        """Test clause counting in metadata."""
        result = compute_sentence_types(mixed_structural)

        clause_counts = result.metadata["clause_counts_per_sentence"]
        assert isinstance(clause_counts, list)
        assert len(clause_counts) == result.total_sentences
        assert all(isinstance(count, tuple) for count in clause_counts)

    def test_coordinating_conjunction_detection(self, compound_sentences):
        """Test that coordinating conjunctions are detected."""
        result = compute_sentence_types(compound_sentences)

        # Should detect compound sentences with "and", "but", "or"
        assert result.compound_count > 0

    def test_dependent_clause_detection(self, complex_sentences):
        """Test that dependent clauses are detected."""
        result = compute_sentence_types(complex_sentences)

        # Should detect complex sentences with dependent clauses
        assert result.complex_count > 0

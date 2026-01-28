"""Tests for sentence type classification (Issue #18)."""

import pytest

from pystylometry.syntactic.sentence_types import compute_sentence_types

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def declarative_sentences():
    """Text with only declarative sentences."""
    return "The sky is blue. The grass is green. Water is wet."


@pytest.fixture
def exclamatory_sentences():
    """Text with exclamations."""
    return "What a beautiful day! How wonderful! Amazing!"


@pytest.fixture
def imperative_sentences():
    """Text with commands."""
    return "Close the door. Look at the sky. Go to the store."


@pytest.fixture
def interrogative_sentences():
    """Text with questions."""
    return "Is the sky blue? Are you ready? What is your name?"


@pytest.fixture
def mixed_functional():
    """Text with mixed functional types."""
    return (
        "The sky is blue. "  # Declarative
        "Is it raining? "  # Interrogative
        "Close the window. "  # Imperative
        "What a lovely day!"  # Exclamatory
    )


class TestFunctionalClassification:
    """Test functional classification (declarative, interrogative, imperative, exclamatory)."""

    def test_declarative_only(self, declarative_sentences):
        """Test text with only declarative sentences."""
        result = compute_sentence_types(declarative_sentences)

        assert result.declarative_ratio == 1.0
        assert result.declarative_count == result.total_sentences

    def test_interrogative_only(self, interrogative_sentences):
        """Test text with only questions."""
        result = compute_sentence_types(interrogative_sentences)

        assert result.interrogative_count >= 2
        assert result.interrogative_ratio >= 0.8

    def test_imperative_only(self, imperative_sentences):
        """Test text with only commands."""
        result = compute_sentence_types(imperative_sentences)

        assert result.imperative_count >= 2
        assert result.imperative_ratio >= 0.5  # spaCy may not catch all

    def test_exclamatory_only(self, exclamatory_sentences):
        """Test text with only exclamations."""
        result = compute_sentence_types(exclamatory_sentences)

        assert result.exclamatory_count >= 2
        assert result.exclamatory_ratio >= 0.5

    def test_mixed_functional_types(self, mixed_functional):
        """Test text with all functional types."""
        result = compute_sentence_types(mixed_functional)

        # Should have multiple types
        types_present = sum(
            [
                result.declarative_count > 0,
                result.interrogative_count > 0,
                result.imperative_count > 0
                or result.exclamatory_count > 0,  # Either imperative or exclamatory
            ]
        )
        assert types_present >= 2

    def test_question_mark_detection(self, interrogative_sentences):
        """Test that question marks are detected."""
        result = compute_sentence_types(interrogative_sentences)

        # All sentences end with ?, should all be interrogative
        assert result.interrogative_count >= 2

    def test_exclamation_mark_detection(self, exclamatory_sentences):
        """Test that exclamation marks are detected."""
        result = compute_sentence_types(exclamatory_sentences)

        # All sentences end with !, should be exclamatory or imperative
        assert result.exclamatory_count + result.imperative_count >= 2

    def test_imperative_structure_detection(self, imperative_sentences):
        """Test that imperative structure is detected."""
        result = compute_sentence_types(imperative_sentences)

        # Should detect some imperatives
        assert result.imperative_count >= 1

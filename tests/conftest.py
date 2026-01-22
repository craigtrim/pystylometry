"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_text():
    """Simple sample text for testing."""
    return "The quick brown fox jumps over the lazy dog. The dog was sleeping."


@pytest.fixture
def long_text():
    """Longer sample text for more complex testing."""
    return """
    The quick brown fox jumps over the lazy dog. The dog was sleeping peacefully
    under the old oak tree. Suddenly, the fox appeared from behind the bushes.
    The dog woke up with a start and began barking loudly. The fox ran away quickly,
    disappearing into the forest. The dog settled back down, satisfied with his
    vigilant performance. The afternoon sun continued to shine brightly in the sky.
    """


@pytest.fixture
def multi_sentence_text():
    """Text with multiple sentences for sentence-level testing."""
    return """
    This is a short sentence. This is another sentence with more words in it.
    Here is a third sentence. And a fourth one! What about a question?
    """

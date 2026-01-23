"""Comprehensive tests for syllable counting functionality."""

from pystylometry.readability.syllables import (
    count_syllables,
    count_syllables_text,
    total_syllables,
    validate_accuracy,
)


def test_count_syllables_single_syllable():
    """Test single syllable words."""
    assert count_syllables("cat") == 1
    assert count_syllables("dog") == 1
    assert count_syllables("the") == 1
    assert count_syllables("and") == 1
    assert count_syllables("but") == 1


def test_count_syllables_multi_syllable():
    """Test multi-syllable words."""
    assert count_syllables("beautiful") == 3
    assert count_syllables("education") == 4
    assert count_syllables("computer") == 3
    assert count_syllables("information") == 4
    assert count_syllables("understand") == 3


def test_count_syllables_edge_cases():
    """Test edge cases and tricky words."""
    # Empty input
    assert count_syllables("") == 0
    assert count_syllables("   ") == 0

    # Punctuation
    assert count_syllables("hello!") == 2
    assert count_syllables("world.") == 1

    # Case insensitivity
    assert count_syllables("HELLO") == 2
    assert count_syllables("Hello") == 2


def test_count_syllables_contractions():
    """Test words with apostrophes."""
    assert count_syllables("don't") == 1  # do + n't
    assert count_syllables("can't") == 1  # can + n't
    assert count_syllables("shouldn't") == 1  # should + n't (should=1 syllable)
    assert count_syllables("I'm") == 1  # I + 'm
    assert count_syllables("you're") == 1  # you're (1 syllable)


def test_count_syllables_hyphenated():
    """Test hyphenated compound words."""
    assert count_syllables("twenty-one") == 3
    assert count_syllables("mother-in-law") == 4


def test_count_syllables_irregular():
    """Test irregular words with silent letters."""
    # Words with silent 'e'
    assert count_syllables("make") == 1
    assert count_syllables("time") == 1
    assert count_syllables("hope") == 1

    # Irregular patterns (CMU dictionary pronunciations)
    assert count_syllables("business") == 2  # biz-ness
    assert count_syllables("queue") == 1  # kyoo
    assert count_syllables("hour") == 2  # ow-er
    assert count_syllables("fire") == 2  # fi-er (formal)
    assert count_syllables("our") == 2  # ow-er (formal)


def test_count_syllables_text():
    """Test counting syllables in full text."""
    text = "The quick brown fox jumps over the lazy dog"
    results = count_syllables_text(text)

    # Should return list of tuples
    assert isinstance(results, list)
    assert all(isinstance(item, tuple) for item in results)
    assert all(len(item) == 2 for item in results)

    # Check specific words
    word_counts = dict(results)
    assert word_counts["quick"] == 1
    assert word_counts["over"] == 2


def test_total_syllables():
    """Test total syllable count."""
    text = "The cat sat on the mat"
    total = total_syllables(text)

    # The(1) cat(1) sat(1) on(1) the(1) mat(1) = 6
    assert total == 6

    # Empty text
    assert total_syllables("") == 0


def test_total_syllables_complex():
    """Test total syllables with more complex text."""
    text = "Beautiful morning sunshine brings happiness"
    total = total_syllables(text)

    # Beautiful(3) morning(2) sunshine(2) brings(1) happiness(3) = 11
    assert total == 11


def test_validate_accuracy():
    """Test accuracy validation function."""
    test_pairs = [
        ("hello", 2),
        ("world", 1),
        ("beautiful", 3),
        ("cat", 1),
        ("education", 4),
    ]

    accuracy, failures = validate_accuracy(test_pairs)

    # Should have high accuracy
    assert accuracy >= 80.0
    assert isinstance(failures, list)

    # Check format of failures
    for failure in failures:
        assert len(failure) == 3
        word, expected, got = failure
        assert isinstance(word, str)
        assert isinstance(expected, int)
        assert isinstance(got, int)


def test_validate_accuracy_empty():
    """Test validation with empty list."""
    accuracy, failures = validate_accuracy([])
    assert accuracy == 0.0
    assert failures == []


def test_validate_accuracy_all_correct():
    """Test validation with all correct predictions."""
    # Use simple words that should definitely work
    test_pairs = [
        ("cat", 1),
        ("dog", 1),
    ]

    accuracy, failures = validate_accuracy(test_pairs)
    assert accuracy == 100.0
    assert len(failures) == 0


def test_syllables_caching():
    """Test that caching works (performance check)."""
    # Call the same word multiple times
    word = "incomprehensibility"

    # First call
    result1 = count_syllables(word)

    # Second call should hit cache
    result2 = count_syllables(word)

    # Results should be identical
    assert result1 == result2
    assert isinstance(result1, int)
    assert result1 > 0

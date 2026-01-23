"""Comprehensive tests for Flesch Reading Ease and Flesch-Kincaid Grade Level."""

import math

from pystylometry.readability import compute_flesch


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
    assert math.isnan(result.reading_ease)
    assert math.isnan(result.grade_level)
    assert result.difficulty == "Unknown"
    assert result.metadata["sentence_count"] == 0
    assert result.metadata["word_count"] == 0


def test_compute_flesch_formulas():
    """Test that Flesch formulas produce expected results."""
    # Simple text should have high reading ease
    simple_text = "The cat sat. The dog ran. The bird flew."
    result = compute_flesch(simple_text)

    # Should be very easy to read
    assert result.reading_ease > 80  # Easy or Very Easy
    assert result.grade_level < 5  # Elementary level
    assert result.difficulty in ["Very Easy", "Easy"]

    # Check metadata is populated
    assert result.metadata["sentence_count"] == 3
    assert result.metadata["word_count"] > 0
    assert result.metadata["syllable_count"] > 0

    # Complex text should have low reading ease
    complex_text = (
        "Notwithstanding comprehensive regulatory frameworks, "
        "organizations endeavor to facilitate interdepartmental collaboration."
    )
    result2 = compute_flesch(complex_text)

    # Should be difficult to read
    assert result2.reading_ease < 50  # Difficult or Very Difficult
    assert result2.grade_level > 10  # Advanced level
    assert result2.difficulty in ["Difficult", "Very Difficult"]


def test_compute_flesch_difficulty_ratings():
    """Test difficulty rating thresholds."""
    # We can't easily construct text to hit exact scores, but we can verify
    # the mapping logic by checking actual results
    simple = "The cat sat on the mat."
    result = compute_flesch(simple)

    # Verify it returns one of the valid difficulty levels
    valid_difficulties = [
        "Very Easy",
        "Easy",
        "Fairly Easy",
        "Standard",
        "Fairly Difficult",
        "Difficult",
        "Very Difficult",
    ]
    assert result.difficulty in valid_difficulties


def test_compute_flesch_unbounded_range():
    """Test that Flesch scores can exceed typical 0-100 range."""
    # Very simple text should produce reading ease > 100
    simple = "Go. Do. Be. Me. We."
    result_simple = compute_flesch(simple)
    assert result_simple.reading_ease > 100, "Very simple text should exceed 100"
    assert result_simple.difficulty == "Very Easy"

    # Very complex text should produce reading ease < 0
    complex_text = (
        "Notwithstanding unequivocal manifestations of multidimensional "
        "philosophical presuppositions, anthropomorphic characterizations "
        "remain fundamentally incontrovertible."
    )
    result_complex = compute_flesch(complex_text)
    assert result_complex.reading_ease < 0, "Very complex text should be below 0"
    assert result_complex.difficulty == "Very Difficult"

    # Negative grade levels are possible for extremely simple text
    assert result_simple.grade_level < 0, "Very simple text can have negative grade level"


def test_compute_flesch_tokenizer_dependency():
    """
    Test edge cases that expose tokenizer/sentence-splitter correctness.

    CRITICAL DEPENDENCY: Everything hinges on tokenize() and split_sentences() correctness.

    Real-world failure modes:
    1. If tokenize() includes punctuation, numbers, or stray artifacts as "words,"
       syllable counter and word count both drift, making scores meaningless.
    2. If split_sentences() mishandles abbreviations (Dr., U.S.), ellipses, or
       dialogue punctuation, words/sentences term explodes, rating clean prose
       as "graduate-level."
    3. count_syllables() on non-words (2026, —, email@example.com) can crash
       or generate garbage syllables. This is the #1 real-world failure mode.
    """
    # Test with numbers - tokenizer behavior determines if these count as "words"
    text_with_numbers = "The year 2026 had 365 days. We counted to 100."
    result_numbers = compute_flesch(text_with_numbers)
    # If tokenizer includes numbers, syllable count becomes unpredictable
    # This test documents that we inherit tokenizer behavior, not control it
    assert result_numbers.metadata["word_count"] > 0  # Sanity check

    # Test with abbreviations - sentence splitter must handle these correctly
    text_with_abbrev = "Dr. Smith works at U.S. Steel. He arrived at 3 p.m. today."
    result_abbrev = compute_flesch(text_with_abbrev)
    # Should be 3 sentences, not 6+ (depends on split_sentences() handling ".")
    # If sentence count is wrong, words/sentences ratio explodes
    assert result_abbrev.metadata["sentence_count"] > 0  # Sanity check

    # Test with special characters - exposes non-word handling
    text_with_special = "The company uses C++ and Python. Email: test@example.com."
    result_special = compute_flesch(text_with_special)
    # count_syllables("C++") and count_syllables("test@example.com") behavior is undefined
    # This documents that we're implicitly treating every token as a syllabifiable word
    assert result_special.metadata["word_count"] > 0  # Sanity check

    # Test with hyphenated and apostrophe words - normalization policy
    text_with_punctuation = "Don't re-enter your co-operate status. O'Brian said so."
    result_punct = compute_flesch(text_with_punctuation)
    # No explicit normalization step means we inherit upstream tokenizer policy
    # on what counts as a "word" and how it's split
    assert result_punct.metadata["word_count"] > 0  # Sanity check


def test_compute_flesch_difficulty_label_semantics():
    """
    Test that difficulty labels are based on Reading Ease only, not grade level.

    DESIGN DECISION: The difficulty label ("Very Easy", "Difficult", etc.) is mapped
    exclusively from the Reading Ease score, even though grade_level is also computed.

    This can confuse callers who might assume the label reflects both metrics.
    For example, text with reading_ease=85 (Easy) might have grade_level=12 (college),
    but the label will still say "Easy" based solely on the reading ease score.

    This test documents and validates this conscious design choice.
    """

    def expected_difficulty(reading_ease: float) -> str:
        """Helper to map reading_ease to expected difficulty label."""
        if reading_ease >= 90:
            return "Very Easy"
        elif reading_ease >= 80:
            return "Easy"
        elif reading_ease >= 70:
            return "Fairly Easy"
        elif reading_ease >= 60:
            return "Standard"
        elif reading_ease >= 50:
            return "Fairly Difficult"
        elif reading_ease >= 30:
            return "Difficult"
        else:
            return "Very Difficult"

    # Test various texts and verify difficulty is based only on reading_ease
    test_cases = [
        "Go. Do. Be.",  # Very simple, should be "Very Easy"
        "The cat sat on the mat. The dog ran.",  # Simple
        (
            "Notwithstanding comprehensive regulatory frameworks, "
            "organizations endeavor to facilitate interdepartmental collaboration."
        ),  # Complex
    ]

    for text in test_cases:
        result = compute_flesch(text)
        expected = expected_difficulty(result.reading_ease)
        assert result.difficulty == expected, (
            f"Difficulty should match reading_ease threshold. "
            f"reading_ease={result.reading_ease:.1f}, "
            f"expected={expected}, got={result.difficulty}"
        )


def test_compute_flesch_upstream_garbage():
    """
    Test that Flesch computation inherits and propagates upstream tokenizer issues.

    NO NORMALIZATION STEP: The implementation has no explicit normalization,
    so it inherits all mess from tokenize() and split_sentences().

    Examples that behave differently based on tokenizer rules:
    - co-operate: 3 syllables or 4? (depends on hyphen handling)
    - O'Brian: 3 syllables or error? (apostrophe in middle)
    - email@example.com: crashes count_syllables? returns garbage?
    - C++: 1 syllable? error?
    - 3.14: how many syllables does a float have?
    - re-enter: 3 syllables or 2?

    This test documents that we DON'T control these edge cases - the tokenizer does.
    In production pipelines, you want this normalization policy explicit upfront.
    """
    # Test cases that expose lack of normalization
    edge_cases = [
        "The co-operate function was called.",  # Hyphen in middle of word
        "O'Brian arrived at 3.14 p.m.",  # Apostrophe, number with decimal, abbreviation
        "Email me at test@example.com please.",  # Email address
        "We use C++ and re-enter the loop.",  # Special chars, hyphen prefix
        "The price is $99.99 on sale.",  # Currency, decimal number
    ]

    for text in edge_cases:
        result = compute_flesch(text)
        # These should not crash, but the scores may be nonsensical
        # depending on how tokenizer handles these inputs
        assert result.metadata["word_count"] >= 0, f"Should handle: {text}"
        assert result.metadata["sentence_count"] >= 0, f"Should handle: {text}"
        # NOTE: We're not asserting specific scores because we can't control
        # upstream tokenizer behavior. This documents the dependency.

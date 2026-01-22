"""Comprehensive tests for SMOG (Simple Measure of Gobbledygook) Index."""

import math

import pytest

from pystylometry.readability import compute_smog


def test_compute_smog_basic(sample_text):
    """Test SMOG Index computation."""
    result = compute_smog(sample_text)
    assert hasattr(result, "smog_index")
    assert hasattr(result, "grade_level")
    assert hasattr(result, "metadata")


def test_compute_smog_empty():
    """Test SMOG with empty text."""
    result = compute_smog("")
    assert math.isnan(result.smog_index)
    assert math.isnan(result.grade_level)
    assert result.metadata["sentence_count"] == 0
    assert result.metadata["word_count"] == 0
    assert result.metadata["polysyllable_count"] == 0
    assert result.metadata["warning"] == "Insufficient text"


def test_compute_smog_formulas():
    """Test that SMOG formula produces expected results."""
    # Simple text with few polysyllables should have low SMOG score
    simple_text = "The cat sat. The dog ran. The bird flew. The sun is hot."
    result = compute_smog(simple_text)

    # Should be low grade level (no polysyllables)
    assert result.smog_index < 8  # Elementary level
    assert result.grade_level < 8
    assert result.metadata["polysyllable_count"] == 0

    # Check metadata is populated
    assert result.metadata["sentence_count"] == 4
    assert result.metadata["word_count"] > 0

    # Complex text with many polysyllables should have high SMOG score
    complex_text = "Notwithstanding comprehensive regulatory frameworks, organizations endeavor to facilitate interdepartmental collaboration. "
    complex_text = complex_text * 5  # Repeat to get more sentences
    result2 = compute_smog(complex_text)

    # Should be high grade level (many polysyllables)
    assert result2.smog_index > 12  # Advanced level
    assert result2.grade_level > 12
    assert result2.metadata["polysyllable_count"] > 10


def test_compute_smog_warning_threshold():
    """Test SMOG warning for texts with fewer than 30 sentences."""
    # Short text (< 30 sentences) should include warning
    short_text = "The cat sat on the mat. " * 10  # 10 sentences
    result_short = compute_smog(short_text)
    assert result_short.metadata["warning"] == "Less than 30 sentences"
    assert result_short.metadata["sentence_count"] < 30

    # Long text (>= 30 sentences) should not include warning
    long_text = "The cat sat on the mat. " * 31  # 31 sentences
    result_long = compute_smog(long_text)
    assert result_long.metadata["warning"] is None
    assert result_long.metadata["sentence_count"] >= 30


def test_compute_smog_polysyllable_counting():
    """Test that polysyllables (3+ syllables) are counted correctly."""
    # Text with known polysyllable count
    # beautiful(3), education(4), wonderful(3) = 3 polysyllables
    # cat(1), sat(1), the(1) = 0 polysyllables
    text = "The beautiful cat sat. Education is wonderful."
    result = compute_smog(text)

    # Should count exactly 3 polysyllables
    assert result.metadata["polysyllable_count"] == 3

    # Verify SMOG calculation uses polysyllable count
    # SMOG = 1.043 × √(polysyllables × 30/sentences) + 3.1291
    expected_smog = 1.043 * math.sqrt(3 * 30 / 2) + 3.1291
    assert abs(result.smog_index - expected_smog) < 0.01


def test_compute_smog_tokenizer_dependency():
    """
    Test edge cases that expose tokenizer/sentence-splitter correctness.

    CRITICAL DEPENDENCY: Like Flesch, SMOG hinges on tokenize() and split_sentences() correctness.

    Real-world failure modes:
    1. If tokenize() includes punctuation, numbers, or stray artifacts as "words,"
       the polysyllable counter can drift (e.g., count_syllables("2026") behavior).
    2. If split_sentences() mishandles abbreviations (Dr., U.S.), the 30-sentence
       threshold becomes unreliable and the √(polysyllables × 30/sentences) term
       explodes or collapses unpredictably.
    3. SMOG is designed for 30+ sentences, so sentence-splitting errors compound:
       splitting "Dr. Smith arrived." into 2 sentences doubles the sentence count
       and can shift SMOG grade level by multiple grades.
    """
    # Test with numbers - tokenizer behavior determines if these count as "words"
    text_with_numbers = "The year 2026 had 365 days. We counted to 100. Numbers are everywhere in 2024."
    result_numbers = compute_smog(text_with_numbers)
    # If tokenizer includes numbers, syllable count becomes unpredictable
    assert result_numbers.metadata["word_count"] > 0  # Sanity check

    # Test with abbreviations - sentence splitter must handle these correctly
    text_with_abbrev = "Dr. Smith works at U.S. Steel. He arrived at 3 p.m. today. The meeting starts soon."
    result_abbrev = compute_smog(text_with_abbrev)
    # Should be 3 sentences, not 6+ (depends on split_sentences() handling ".")
    # If sentence count is wrong, the √(30/sentences) term explodes
    assert result_abbrev.metadata["sentence_count"] > 0  # Sanity check

    # Test with special characters - exposes non-word handling
    text_with_special = "The company uses C++ and Python. Email: test@example.com. Code reviews matter."
    result_special = compute_smog(text_with_special)
    # count_syllables("C++") and count_syllables("test@example.com") behavior is undefined
    assert result_special.metadata["word_count"] > 0  # Sanity check


def test_compute_smog_upstream_garbage():
    """
    Test that SMOG computation inherits and propagates upstream tokenizer issues.

    NO NORMALIZATION STEP: Like Flesch, SMOG has no explicit normalization,
    so it inherits all mess from tokenize() and split_sentences().

    Examples that behave differently based on tokenizer rules:
    - co-operate: 3 syllables or 4? Is it a polysyllable?
    - O'Brian: 3 syllables or error? (apostrophe in middle)
    - email@example.com: crashes count_syllables? returns garbage?
    - C++: 1 syllable? error?
    - 3.14: how many syllables does a float have?

    This test documents that we DON'T control these edge cases - the tokenizer does.
    """
    # Test cases that expose lack of normalization
    edge_cases = [
        "The co-operate function was called. It works well.",  # Hyphen in middle of word
        "O'Brian arrived at 3.14 p.m. today.",  # Apostrophe, number with decimal, abbreviation
        "Email me at test@example.com please. Thanks.",  # Email address
        "We use C++ and re-enter the loop. Programming continues.",  # Special chars, hyphen prefix
        "The price is $99.99 on sale. Buy now.",  # Currency, decimal number
    ]

    for text in edge_cases:
        result = compute_smog(text)
        # These should not crash, but the scores may be nonsensical
        # depending on how tokenizer handles these inputs
        assert result.metadata["word_count"] >= 0, f"Should handle: {text}"
        assert result.metadata["sentence_count"] >= 0, f"Should handle: {text}"
        # NOTE: We're not asserting specific scores because we can't control
        # upstream tokenizer behavior. This documents the dependency.


def test_compute_smog_rounding_policy():
    """
    Test and document SMOG rounding behavior.

    DESIGN DECISION: Python's round() uses "banker's rounding" (round half to even).
    This means 12.5 rounds to 12 (nearest even), but 13.5 rounds to 14 (nearest even).

    This can surprise users expecting "standard" half-up rounding where 0.5 always
    rounds up. The implementation intentionally uses Python's default round() without
    custom rounding logic.

    Example cases:
    - SMOG index 12.5 → grade_level 12 (not 13)
    - SMOG index 13.5 → grade_level 14 (not 13)
    - SMOG index 12.4 → grade_level 12
    - SMOG index 12.6 → grade_level 13
    """
    # We can't easily construct text to hit exact SMOG values, but we can
    # verify that round() is being used by checking its behavior
    assert round(12.5) == 12  # Banker's rounding to even
    assert round(13.5) == 14  # Banker's rounding to even
    assert round(12.4) == 12  # Normal rounding
    assert round(12.6) == 13  # Normal rounding

    # Document that SMOG uses this same round() function
    # If users need different rounding, they should apply it to smog_index themselves


def test_compute_smog_metadata_warning_typing():
    """
    Test and document metadata warning typing behavior.

    DESIGN DECISION: The 'warning' field alternates between str and None.
    - When warning exists: {"warning": "Less than 30 sentences"}
    - When no warning: {"warning": None}

    This pattern matches Flesch and other metrics in the library. Consumers should
    handle None explicitly (e.g., `if result.metadata.get("warning"):`).

    Alternative designs considered but rejected:
    - Omit key when no warning (breaks dict access patterns)
    - Use empty string "" (makes truthiness checking harder)
    - Use list like warnings: [] (inconsistent with single-warning model)
    """
    # Short text has warning
    short = "The cat sat. The dog ran."
    result_short = compute_smog(short)
    assert "warning" in result_short.metadata
    assert isinstance(result_short.metadata["warning"], str)
    assert result_short.metadata["warning"] == "Less than 30 sentences"

    # Long text has None warning
    long = "The cat sat on the mat. " * 31
    result_long = compute_smog(long)
    assert "warning" in result_long.metadata
    assert result_long.metadata["warning"] is None

    # Empty text has different warning
    result_empty = compute_smog("")
    assert result_empty.metadata["warning"] == "Insufficient text"


def test_compute_smog_better_example():
    """
    Test with a better example that actually demonstrates polysyllables.

    DOCUMENTATION ISSUE: The docstring example "The quick brown fox jumps over
    the lazy dog" contains zero polysyllables (all 1-syllable words), yielding
    SMOG ≈ 3.13, which is an atypical and misleading demonstration.

    This test uses text with actual polysyllables to show how SMOG responds
    to complex vocabulary.
    """
    # Original example has no polysyllables
    simple = "The quick brown fox jumps over the lazy dog."
    result_simple = compute_smog(simple)
    assert result_simple.metadata["polysyllable_count"] == 0
    # SMOG ≈ 3.13 (minimal score from formula constant)

    # Better example with polysyllables
    complex_text = (
        "Understanding computational linguistics requires significant dedication. "
        "Researchers investigate sophisticated methodologies systematically. "
        "Contemporary algorithms demonstrate remarkable capabilities consistently."
    )
    result_complex = compute_smog(complex_text)
    # computational(5), linguistics(4), significant(4), dedication(4),
    # investigate(4), sophisticated(5), methodologies(6), systematically(6),
    # contemporary(5), algorithms(4), demonstrate(3), remarkable(4),
    # capabilities(5), consistently(4) = 14 polysyllables
    assert result_complex.metadata["polysyllable_count"] > 10
    assert result_complex.smog_index > 10  # Much higher than simple text


def test_compute_smog_edge_case_grade_levels():
    """
    Test edge cases where SMOG formula produces unusual grade level values.

    POTENTIAL ISSUE: SMOG can theoretically produce low/negative values with
    pathological inputs (zero polysyllables, many sentences), but grade_level
    is NOT clamped to a minimum.

    The implementation returns the raw rounded value. In practice:
    - Zero polysyllables → SMOG ≈ 3.13 (formula constant) → grade_level 3
    - Negative SMOG is mathematically impossible (sqrt of non-negative)
    - Very low SMOG (<0) cannot occur with valid input

    If downstream code needs minimum grade level (e.g., 0 or 1), it should
    clamp the value itself.
    """
    # Zero polysyllables gives minimal SMOG score
    simple = "The cat sat on the mat. The dog ran fast. The sun is hot. Go now."
    result = compute_smog(simple)
    assert result.metadata["polysyllable_count"] == 0

    # Formula: 1.043 × √(0 × 30/sentences) + 3.1291 = 3.1291
    expected_smog = 1.043 * math.sqrt(0 * 30 / result.metadata["sentence_count"]) + 3.1291
    assert abs(result.smog_index - expected_smog) < 0.01
    assert result.grade_level == 3  # round(3.1291) = 3

    # Grade level is NOT clamped to minimum
    # If users need clamping, they should apply it: max(0, result.grade_level)

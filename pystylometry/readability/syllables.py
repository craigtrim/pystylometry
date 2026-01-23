"""
Syllable counting using CMU Pronouncing Dictionary.

Uses the pronouncing library which provides access to the CMU Pronouncing
Dictionary for high-accuracy syllable counting based on phonetic transcriptions.
"""

import re
from functools import lru_cache

try:
    import pronouncing  # type: ignore[import-untyped]
except ImportError:
    raise ImportError(
        "The 'pronouncing' library is required for syllable counting. "
        "Install it with: pip install pystylometry[readability]"
    )


@lru_cache(maxsize=4096)
def count_syllables(word: str) -> int:
    """
    Count syllables using CMU Pronouncing Dictionary.

    Uses phonetic transcriptions from CMU dictionary. For words with multiple
    pronunciations, uses the first pronunciation (typically the most common).
    Falls back to simple vowel counting for words not in the dictionary.

    Args:
        word: Input word (handles mixed case, strips whitespace)

    Returns:
        Syllable count (minimum 1 for non-empty input)

    Example:
        >>> count_syllables("beautiful")
        3
        >>> count_syllables("fire")
        2
        >>> count_syllables("cruel")
        1
    """
    word = word.lower().strip()
    if not word:
        return 0

    # Strip common punctuation
    word = word.strip(".,;:!?\"'()-")
    if not word:
        return 0

    # Handle contractions by removing apostrophes
    if "'" in word:
        word = word.replace("'", "")

    # Handle hyphenated compounds
    if "-" in word:
        return sum(count_syllables(part) for part in word.split("-") if part)

    # Get pronunciations from CMU dictionary
    phones_list = pronouncing.phones_for_word(word)

    if phones_list:
        # Use first pronunciation (most common)
        # Count stress markers (0, 1, 2) in phoneme representation
        phones = phones_list[0]
        return pronouncing.syllable_count(phones)  # type: ignore[no-any-return]

    # Fallback for words not in dictionary: simple vowel counting
    return _fallback_count(word)


def _fallback_count(word: str) -> int:
    """
    Simple fallback syllable counter for words not in CMU dictionary.

    Uses basic vowel counting with silent-e adjustment.
    Less accurate than CMU but handles rare/technical words.
    """
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith("e") and count > 1:
        count -= 1

    # Ensure minimum of 1
    return max(1, count)


def count_syllables_text(text: str) -> list[tuple[str, int]]:
    """
    Count syllables for all words in a text.

    Args:
        text: Input text

    Returns:
        List of (word, syllable_count) tuples

    Example:
        >>> count_syllables_text("The quick brown fox")
        [('The', 1), ('quick', 1), ('brown', 1), ('fox', 1)]
    """

    words = re.findall(r"[a-zA-Z']+", text)
    return [(w, count_syllables(w)) for w in words]


def total_syllables(text: str) -> int:
    """
    Return total syllable count for text.

    Args:
        text: Input text

    Returns:
        Total number of syllables

    Example:
        >>> total_syllables("The quick brown fox")
        4
    """
    return sum(count for _, count in count_syllables_text(text))


def validate_accuracy(
    test_pairs: list[tuple[str, int]],
) -> tuple[float, list[tuple[str, int, int]]]:
    """
    Test accuracy against known word-syllable pairs.

    Args:
        test_pairs: List of (word, expected_syllables) tuples

    Returns:
        (accuracy_percentage, list of (word, expected, got) for failures)

    Example:
        >>> test_pairs = [("hello", 2), ("world", 1), ("beautiful", 3)]
        >>> accuracy, failures = validate_accuracy(test_pairs)
        >>> print(f"Accuracy: {accuracy:.1f}%")
    """
    failures = []
    for word, expected in test_pairs:
        got = count_syllables(word)
        if got != expected:
            failures.append((word, expected, got))

    if not test_pairs:
        return 0.0, []

    accuracy = (len(test_pairs) - len(failures)) / len(test_pairs) * 100
    return accuracy, failures

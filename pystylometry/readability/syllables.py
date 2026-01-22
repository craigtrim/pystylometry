"""Syllable counting utilities using CMU Pronouncing Dictionary."""


def count_syllables(word: str) -> int:
    """
    Count syllables in a word using CMU Pronouncing Dictionary with heuristic fallback.

    Args:
        word: The word to count syllables for

    Returns:
        Number of syllables in the word
    """
    # TODO: Implement with pronouncing library
    # For now, use simple heuristic fallback
    return _heuristic_syllable_count(word)


def _heuristic_syllable_count(word: str) -> int:
    """
    Simple heuristic syllable counter for fallback.

    This is a basic implementation that counts vowel groups.
    Should be replaced with CMU dict lookup when pronouncing is available.

    Args:
        word: The word to count syllables for

    Returns:
        Estimated number of syllables
    """
    word = word.lower().strip()
    if len(word) == 0:
        return 0

    vowels = "aeiouy"
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith("e") and syllable_count > 1:
        syllable_count -= 1

    # Ensure at least one syllable
    if syllable_count == 0:
        syllable_count = 1

    return syllable_count

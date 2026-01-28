"""Rhythm and prosody metrics for written text.

This module captures the musical qualities of written language, including
stress patterns, syllable rhythms, and phonological features. While traditionally
studied in spoken language, written text preserves many rhythmic patterns.

Related GitHub Issue:
    #25 - Rhythm and Prosody Metrics
    https://github.com/craigtrim/pystylometry/issues/25

Features analyzed:
    - Syllable patterns and stress patterns
    - Rhythmic regularity (coefficient of variation)
    - Phonological features (alliteration, assonance, consonance)
    - Syllable complexity (consonant clusters)
    - Sentence rhythm (length alternation)
    - Polysyllabic word usage
    - Metrical foot estimation (iambic, trochaic, dactylic, anapestic)

Dependencies:
    - CMU Pronouncing Dictionary (via pronouncing package)
    - pronouncing is already a dependency for pystylometry[readability]

References:
    Fabb, N., & Halle, M. (2008). Meter in Poetry: A New Theory. Cambridge
        University Press.
    Greene, E., Bodrumlu, T., & Knight, K. (2010). Automatic analysis of rhythmic
        poetry with applications to generation and translation. Proceedings of
        EMNLP, 524-533.
    Lea, R. B., Mulligan, E. J., & Walton, J. H. (2005). Sentence rhythm and
        text comprehension. Memory & Cognition, 33(3), 388-396.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache
from typing import Any

from .._types import RhythmProsodyResult

# =============================================================================
# DEPENDENCY: CMU PRONOUNCING DICTIONARY
# =============================================================================
# The pronouncing package provides access to the CMU Pronouncing Dictionary,
# which maps English words to ARPAbet phoneme sequences with stress markers.
# Stress markers: 0 = no stress, 1 = primary stress, 2 = secondary stress.

try:
    import pronouncing  # type: ignore[import-untyped]
except ImportError:
    raise ImportError(
        "The 'pronouncing' library is required for rhythm and prosody analysis. "
        "Install it with: pip install pystylometry[readability]"
    )

# =============================================================================
# VOWEL AND CONSONANT DEFINITIONS
# =============================================================================
# Used for alliteration, assonance, consonance, and cluster detection.

VOWELS = set("aeiou")
CONSONANTS = set("bcdfghjklmnpqrstvwxyz")

# ARPAbet vowel phonemes (used in CMU dictionary output)
ARPABET_VOWELS = {
    "AA",
    "AE",
    "AH",
    "AO",
    "AW",
    "AY",
    "EH",
    "ER",
    "EY",
    "IH",
    "IY",
    "OW",
    "OY",
    "UH",
    "UW",
}

# Consonant cluster patterns at word boundaries
# Reference: English phonotactics (Clements & Keyser, 1983)
INITIAL_CLUSTER_PATTERN = re.compile(r"^[bcdfghjklmnpqrstvwxyz]{2,}", re.IGNORECASE)
FINAL_CLUSTER_PATTERN = re.compile(r"[bcdfghjklmnpqrstvwxyz]{2,}$", re.IGNORECASE)


# =============================================================================
# PHONEME AND SYLLABLE HELPERS
# =============================================================================


def _extract_words(text: str) -> list[str]:
    """Extract alphabetic words from text, preserving order."""
    return re.findall(r"[a-zA-Z]+", text)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences on sentence-ending punctuation."""
    sentences = re.split(r"[.!?]+", text)
    return [s.strip() for s in sentences if s.strip()]


@lru_cache(maxsize=4096)
def _get_phones(word: str) -> str | None:
    """Get the first (most common) pronunciation from CMU dictionary.

    Returns the ARPAbet phoneme string, or None if the word is not found.
    CMU stress markers: 0 = no stress, 1 = primary, 2 = secondary.
    """
    phones_list = pronouncing.phones_for_word(word.lower())
    if phones_list:
        return phones_list[0]  # type: ignore[no-any-return]
    return None


@lru_cache(maxsize=4096)
def _count_syllables(word: str) -> int:
    """Count syllables using CMU dictionary, falling back to vowel heuristic.

    The CMU dictionary provides phoneme-level transcriptions with stress markers.
    Each vowel phoneme (marked 0, 1, or 2) represents one syllable nucleus.
    """
    phones = _get_phones(word)
    if phones:
        return pronouncing.syllable_count(phones)  # type: ignore[no-any-return]
    return _fallback_syllable_count(word)


def _fallback_syllable_count(word: str) -> int:
    """Heuristic syllable count for words not in CMU dictionary.

    Counts vowel groups and adjusts for silent-e.
    """
    word = word.lower()
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in VOWELS
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _get_stress_pattern(word: str) -> list[int]:
    """Extract stress pattern from CMU pronunciation.

    Returns a list of stress values (0, 1, 2) for each syllable.
    Returns empty list if word is not in CMU dictionary.

    Reference:
        CMU Pronouncing Dictionary stress encoding:
        0 = no stress, 1 = primary stress, 2 = secondary stress
    """
    phones = _get_phones(word)
    if not phones:
        return []
    return [int(ch) for ch in phones if ch.isdigit()]


def _get_vowel_phonemes(word: str) -> list[str]:
    """Extract vowel phonemes (without stress markers) from CMU pronunciation.

    Used for assonance detection: words sharing vowel sounds.
    """
    phones = _get_phones(word)
    if not phones:
        return []
    phonemes = phones.split()
    return [p.rstrip("012") for p in phonemes if p.rstrip("012") in ARPABET_VOWELS]


def _get_initial_sound(word: str) -> str | None:
    """Get the initial consonant sound from CMU pronunciation.

    Used for alliteration detection: words sharing initial consonant sounds.
    Falls back to the first letter if the word is not in CMU dictionary.
    """
    phones = _get_phones(word)
    if phones:
        first_phoneme = phones.split()[0].rstrip("012")
        if first_phoneme not in ARPABET_VOWELS:
            return first_phoneme
        return None  # Word starts with a vowel sound
    # Fallback: use first letter if consonant
    w = word.lower()
    if w and w[0] in CONSONANTS:
        return w[0]
    return None


def _get_consonant_phonemes(word: str) -> list[str]:
    """Extract consonant phonemes from CMU pronunciation.

    Used for consonance detection: words sharing consonant sounds.
    """
    phones = _get_phones(word)
    if not phones:
        return []
    phonemes = phones.split()
    return [p for p in phonemes if p.rstrip("012") not in ARPABET_VOWELS]


# =============================================================================
# SYLLABLE PATTERN METRICS
# =============================================================================


def _compute_syllable_metrics(
    words: list[str],
) -> tuple[float, float, float, float, list[int]]:
    """Compute syllable distribution metrics.

    Returns:
        (mean_syllables, std_dev, polysyllabic_ratio, monosyllabic_ratio,
         syllable_counts)

    Polysyllabic ratio: fraction of words with 3+ syllables.
        Relevant for readability and stylistic complexity.
    Monosyllabic ratio: fraction of single-syllable words.
        High monosyllabic ratio suggests simpler, more direct style.
    """
    if not words:
        return 0.0, 0.0, 0.0, 0.0, []

    syllable_counts = [_count_syllables(w) for w in words]
    n = len(syllable_counts)

    mean_syl = sum(syllable_counts) / n
    variance = sum((s - mean_syl) ** 2 for s in syllable_counts) / n
    std_dev = math.sqrt(variance)

    polysyllabic = sum(1 for s in syllable_counts if s >= 3)
    monosyllabic = sum(1 for s in syllable_counts if s == 1)

    return (
        mean_syl,
        std_dev,
        polysyllabic / n,
        monosyllabic / n,
        syllable_counts,
    )


# =============================================================================
# RHYTHMIC REGULARITY
# =============================================================================


def _compute_rhythmic_regularity(syllable_counts: list[int]) -> tuple[float, float]:
    """Compute rhythmic regularity from syllable count distribution.

    Rhythmic regularity is the inverse of the coefficient of variation (CV)
    of syllable counts per word. Lower CV means more uniform syllable lengths,
    which produces a more metrically regular text.

    Formula:
        CV = σ / μ  (coefficient of variation)
        Regularity = 1 / CV  (higher = more regular rhythm)

    When CV is 0 (all words same length), regularity is set to the word count
    as a practical upper bound.

    Reference:
        Lea, R. B., Mulligan, E. J., & Walton, J. H. (2005). Sentence rhythm
            and text comprehension. Memory & Cognition, 33(3), 388-396.

    Returns:
        (rhythmic_regularity, syllable_cv)
    """
    if not syllable_counts:
        return 0.0, 0.0

    n = len(syllable_counts)
    mean_syl = sum(syllable_counts) / n
    if mean_syl == 0.0:
        return 0.0, 0.0

    variance = sum((s - mean_syl) ** 2 for s in syllable_counts) / n
    std_dev = math.sqrt(variance)
    cv = std_dev / mean_syl

    if cv == 0.0:
        # All words have the same syllable count: maximally regular
        regularity = float(n)
    else:
        regularity = 1.0 / cv

    return regularity, cv


# =============================================================================
# STRESS PATTERN ENTROPY
# =============================================================================


def _compute_stress_entropy(words: list[str]) -> float:
    """Compute Shannon entropy of stress patterns across words.

    Each word's stress pattern (e.g., "10" for trochee, "01" for iamb) is
    treated as a categorical event. Higher entropy means more varied stress
    patterns; lower entropy means the text gravitates toward a few dominant
    metrical feet.

    Formula:
        H = -Σ p(pattern) × log₂(p(pattern))

    Reference:
        Shannon, C. E. (1948). A Mathematical Theory of Communication.
        Applied here to prosodic analysis following Greene et al. (2010).

    Returns:
        Shannon entropy in bits. 0.0 if no stress data available.
    """
    patterns: list[str] = []
    for word in words:
        stress = _get_stress_pattern(word)
        if stress:
            # Binarize: 0 stays 0 (unstressed), 1 or 2 become 1 (stressed)
            binary = "".join("1" if s > 0 else "0" for s in stress)
            patterns.append(binary)

    if not patterns:
        return 0.0

    counts = Counter(patterns)
    total = len(patterns)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)

    return entropy


# =============================================================================
# SENTENCE RHYTHM
# =============================================================================


def _compute_sentence_rhythm(text: str) -> tuple[float, float]:
    """Compute sentence-level rhythm metrics.

    Sentence length alternation measures the degree to which long and short
    sentences alternate. Authors with strong prose rhythm tend to vary sentence
    length deliberately, creating a sense of pacing.

    Alternation score: average absolute difference in word count between
    consecutive sentences, normalized by mean sentence length.

    Sentence rhythm score: composite metric combining alternation with
    sentence length variance (higher variance = more dynamic rhythm).

    Reference:
        Cutts, M. (2013). Oxford Guide to Plain English (4th ed.).
            Recommends varying sentence length for readability.

    Returns:
        (sentence_length_alternation, sentence_rhythm_score)
    """
    sentences = _split_sentences(text)
    if len(sentences) < 2:
        return 0.0, 0.0

    lengths = [len(_extract_words(s)) for s in sentences]
    lengths = [length for length in lengths if length > 0]

    if len(lengths) < 2:
        return 0.0, 0.0

    mean_len = sum(lengths) / len(lengths)
    if mean_len == 0.0:
        return 0.0, 0.0

    # Alternation: mean absolute diff between consecutive sentences
    diffs = [abs(lengths[i] - lengths[i - 1]) for i in range(1, len(lengths))]
    alternation = (sum(diffs) / len(diffs)) / mean_len

    # Rhythm score: combines alternation with normalized variance
    variance = sum((length - mean_len) ** 2 for length in lengths) / len(lengths)
    cv = math.sqrt(variance) / mean_len if mean_len > 0 else 0.0
    rhythm_score = (alternation + cv) / 2.0

    return alternation, rhythm_score


# =============================================================================
# PHONOLOGICAL FEATURES: ALLITERATION, ASSONANCE, CONSONANCE
# =============================================================================


def _compute_alliteration(words: list[str]) -> float:
    """Compute alliteration density (alliterative pairs per 100 words).

    Alliteration is the repetition of initial consonant sounds in adjacent
    or nearby words. This implementation checks consecutive word pairs for
    matching initial consonant phonemes using the CMU dictionary.

    Formula:
        density = (alliterative_pairs / total_words) × 100

    Reference:
        Fabb, N., & Halle, M. (2008). Meter in Poetry. Cambridge University
            Press. Chapter on phonological repetition in verse.

    Returns:
        Alliterative word pairs per 100 words.
    """
    if len(words) < 2:
        return 0.0

    pairs = 0
    for i in range(len(words) - 1):
        sound_a = _get_initial_sound(words[i])
        sound_b = _get_initial_sound(words[i + 1])
        if sound_a and sound_b and sound_a == sound_b:
            pairs += 1

    return (pairs / len(words)) * 100.0


def _compute_assonance(words: list[str]) -> float:
    """Compute assonance density (assonant pairs per 100 words).

    Assonance is the repetition of vowel sounds within nearby words,
    regardless of surrounding consonants. This implementation checks
    consecutive word pairs for shared vowel phonemes.

    Formula:
        density = (assonant_pairs / total_words) × 100

    Returns:
        Assonant word pairs per 100 words.
    """
    if len(words) < 2:
        return 0.0

    pairs = 0
    for i in range(len(words) - 1):
        vowels_a = set(_get_vowel_phonemes(words[i]))
        vowels_b = set(_get_vowel_phonemes(words[i + 1]))
        if vowels_a and vowels_b and vowels_a & vowels_b:
            pairs += 1

    return (pairs / len(words)) * 100.0


def _compute_consonance(words: list[str]) -> float:
    """Compute consonance density (consonant-repeating pairs per 100 words).

    Consonance is the repetition of consonant sounds within nearby words,
    especially at the end of words. This implementation checks consecutive
    word pairs for shared consonant phonemes.

    Formula:
        density = (consonant_pairs / total_words) × 100

    Returns:
        Consonant-repeating word pairs per 100 words.
    """
    if len(words) < 2:
        return 0.0

    pairs = 0
    for i in range(len(words) - 1):
        cons_a = set(_get_consonant_phonemes(words[i]))
        cons_b = set(_get_consonant_phonemes(words[i + 1]))
        if cons_a and cons_b and cons_a & cons_b:
            pairs += 1

    return (pairs / len(words)) * 100.0


# =============================================================================
# CONSONANT CLUSTER METRICS
# =============================================================================


def _compute_cluster_metrics(
    words: list[str],
) -> tuple[float, float, float]:
    """Compute consonant cluster complexity metrics.

    Consonant clusters (two or more consonants in sequence) contribute to
    the perceived complexity and rhythm of text. Languages and styles differ
    in their tolerance for complex clusters.

    Returns:
        (mean_cluster_length, initial_cluster_ratio, final_cluster_ratio)

    Where:
        mean_cluster_length: average length of all consonant clusters found
        initial_cluster_ratio: fraction of words starting with a cluster
        final_cluster_ratio: fraction of words ending with a cluster
    """
    if not words:
        return 0.0, 0.0, 0.0

    cluster_lengths: list[int] = []
    initial_count = 0
    final_count = 0

    for word in words:
        w = word.lower()

        initial_match = INITIAL_CLUSTER_PATTERN.match(w)
        if initial_match:
            initial_count += 1
            cluster_lengths.append(len(initial_match.group()))

        final_match = FINAL_CLUSTER_PATTERN.search(w)
        if final_match:
            final_count += 1
            cluster_lengths.append(len(final_match.group()))

    n = len(words)
    mean_cluster = sum(cluster_lengths) / len(cluster_lengths) if cluster_lengths else 0.0
    initial_ratio = initial_count / n
    final_ratio = final_count / n

    return mean_cluster, initial_ratio, final_ratio


# =============================================================================
# METRICAL FOOT ESTIMATION
# =============================================================================


def _compute_metrical_feet(words: list[str]) -> tuple[float, float, float, float]:
    """Estimate metrical foot ratios from word-level stress patterns.

    Classical meter is defined by patterns of stressed (S) and unstressed (U)
    syllables:
        - Iamb: U-S (e.g., "above", "begin")
        - Trochee: S-U (e.g., "garden", "happy")
        - Dactyl: S-U-U (e.g., "merrily", "beautiful")
        - Anapest: U-U-S (e.g., "understand", "intervene")

    This function examines each word's stress pattern and classifies it as
    matching one or more of these foot types. Multi-syllable words are
    decomposed into overlapping bigrams/trigrams of stress values.

    Reference:
        Fabb, N., & Halle, M. (2008). Meter in Poetry. Cambridge University
            Press.

    Returns:
        (iambic_ratio, trochaic_ratio, dactylic_ratio, anapestic_ratio)
        Each as a fraction of total detected foot patterns.
    """
    iambic = 0
    trochaic = 0
    dactylic = 0
    anapestic = 0
    total = 0

    for word in words:
        stress = _get_stress_pattern(word)
        if len(stress) < 2:
            continue

        # Binarize stress: 0 = unstressed, 1/2 = stressed
        binary = [1 if s > 0 else 0 for s in stress]

        # Check bigrams for iambic (0,1) and trochaic (1,0)
        for i in range(len(binary) - 1):
            pair = (binary[i], binary[i + 1])
            if pair == (0, 1):
                iambic += 1
                total += 1
            elif pair == (1, 0):
                trochaic += 1
                total += 1

        # Check trigrams for dactylic (1,0,0) and anapestic (0,0,1)
        for i in range(len(binary) - 2):
            triple = (binary[i], binary[i + 1], binary[i + 2])
            if triple == (1, 0, 0):
                dactylic += 1
                total += 1
            elif triple == (0, 0, 1):
                anapestic += 1
                total += 1

    if total == 0:
        return 0.0, 0.0, 0.0, 0.0

    return (
        iambic / total,
        trochaic / total,
        dactylic / total,
        anapestic / total,
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def compute_rhythm_prosody(text: str) -> RhythmProsodyResult:
    """Compute rhythm and prosody metrics for written text.

    Analyzes the musical qualities of written language through syllable
    patterns, stress patterns, phonological features, and metrical foot
    estimation. These metrics are particularly relevant for poetry analysis
    and literary stylometry, but also capture prose rhythm patterns.

    Related GitHub Issue:
        #25 - Rhythm and Prosody Metrics
        https://github.com/craigtrim/pystylometry/issues/25

    Metrics computed:

    Syllable patterns:
        - mean_syllables_per_word: Average syllable count across all words.
        - syllable_std_dev: Standard deviation of syllable counts.
        - polysyllabic_ratio: Fraction of words with 3+ syllables.
        - monosyllabic_ratio: Fraction of single-syllable words.

    Rhythmic regularity:
        - rhythmic_regularity: 1 / CV of syllable counts (higher = more regular).
        - syllable_cv: Coefficient of variation of syllable counts.
        - stress_pattern_entropy: Shannon entropy of stress patterns in bits.

    Sentence rhythm:
        - sentence_length_alternation: Normalized mean absolute difference
          between consecutive sentence lengths.
        - sentence_rhythm_score: Composite metric combining alternation
          and sentence length variance.

    Phonological features:
        - alliteration_density: Alliterative word pairs per 100 words.
        - assonance_density: Assonant word pairs per 100 words.
        - consonance_density: Consonant-repeating pairs per 100 words.

    Syllable complexity:
        - mean_consonant_cluster_length: Average length of consonant clusters.
        - initial_cluster_ratio: Words starting with consonant clusters.
        - final_cluster_ratio: Words ending with consonant clusters.

    Stress patterns (metrical feet):
        - iambic_ratio: Unstressed-stressed pairs / total feet.
        - trochaic_ratio: Stressed-unstressed pairs / total feet.
        - dactylic_ratio: Stressed-unstressed-unstressed trigrams / total feet.
        - anapestic_ratio: Unstressed-unstressed-stressed trigrams / total feet.

    Dependencies:
        Requires the ``pronouncing`` package for CMU dictionary access.
        Install with: ``pip install pystylometry[readability]``

    References:
        Fabb, N., & Halle, M. (2008). Meter in Poetry: A New Theory.
            Cambridge University Press.
        Greene, E., Bodrumlu, T., & Knight, K. (2010). Automatic analysis of
            rhythmic poetry with applications to generation and translation.
            Proceedings of EMNLP, 524-533.
        Lea, R. B., Mulligan, E. J., & Walton, J. H. (2005). Sentence rhythm
            and text comprehension. Memory & Cognition, 33(3), 388-396.

    Args:
        text: Input text to analyze. For reliable prosodic statistics, at
              least 100+ words are recommended. Shorter texts will produce
              valid but potentially unstable metrics.

    Returns:
        RhythmProsodyResult with syllable patterns, rhythmic regularity,
        phonological features, stress patterns, and complexity metrics.
        See ``_types.RhythmProsodyResult`` for complete field documentation.

    Example:
        >>> result = compute_rhythm_prosody("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Syllables/word: {result.mean_syllables_per_word:.2f}")
        >>> print(f"Rhythmic regularity: {result.rhythmic_regularity:.3f}")
        >>> print(f"Alliteration density: {result.alliteration_density:.2f}")
    """
    # Handle empty text
    if not text or not text.strip():
        return RhythmProsodyResult(
            mean_syllables_per_word=0.0,
            syllable_std_dev=0.0,
            polysyllabic_ratio=0.0,
            monosyllabic_ratio=0.0,
            rhythmic_regularity=0.0,
            syllable_cv=0.0,
            stress_pattern_entropy=0.0,
            sentence_length_alternation=0.0,
            sentence_rhythm_score=0.0,
            alliteration_density=0.0,
            assonance_density=0.0,
            consonance_density=0.0,
            mean_consonant_cluster_length=0.0,
            initial_cluster_ratio=0.0,
            final_cluster_ratio=0.0,
            iambic_ratio=0.0,
            trochaic_ratio=0.0,
            dactylic_ratio=0.0,
            anapestic_ratio=0.0,
            metadata={"word_count": 0, "warning": "Empty text"},
        )

    words = _extract_words(text)
    if not words:
        return RhythmProsodyResult(
            mean_syllables_per_word=0.0,
            syllable_std_dev=0.0,
            polysyllabic_ratio=0.0,
            monosyllabic_ratio=0.0,
            rhythmic_regularity=0.0,
            syllable_cv=0.0,
            stress_pattern_entropy=0.0,
            sentence_length_alternation=0.0,
            sentence_rhythm_score=0.0,
            alliteration_density=0.0,
            assonance_density=0.0,
            consonance_density=0.0,
            mean_consonant_cluster_length=0.0,
            initial_cluster_ratio=0.0,
            final_cluster_ratio=0.0,
            iambic_ratio=0.0,
            trochaic_ratio=0.0,
            dactylic_ratio=0.0,
            anapestic_ratio=0.0,
            metadata={"word_count": 0, "warning": "No words found"},
        )

    # =========================================================================
    # SYLLABLE PATTERNS
    # =========================================================================
    mean_syl, syl_std, poly_ratio, mono_ratio, syl_counts = _compute_syllable_metrics(words)

    # =========================================================================
    # RHYTHMIC REGULARITY
    # =========================================================================
    regularity, cv = _compute_rhythmic_regularity(syl_counts)

    # =========================================================================
    # STRESS PATTERN ENTROPY
    # =========================================================================
    stress_entropy = _compute_stress_entropy(words)

    # =========================================================================
    # SENTENCE RHYTHM
    # =========================================================================
    alternation, rhythm_score = _compute_sentence_rhythm(text)

    # =========================================================================
    # PHONOLOGICAL FEATURES
    # =========================================================================
    alliteration = _compute_alliteration(words)
    assonance = _compute_assonance(words)
    consonance = _compute_consonance(words)

    # =========================================================================
    # CONSONANT CLUSTER COMPLEXITY
    # =========================================================================
    mean_cluster, initial_ratio, final_ratio = _compute_cluster_metrics(words)

    # =========================================================================
    # METRICAL FOOT ESTIMATION
    # =========================================================================
    iambic, trochaic, dactylic, anapestic = _compute_metrical_feet(words)

    # =========================================================================
    # METADATA
    # =========================================================================
    # Collect per-word stress patterns for downstream analysis
    word_stress_patterns: dict[str, list[int]] = {}
    for word in set(words):
        stress = _get_stress_pattern(word)
        if stress:
            word_stress_patterns[word.lower()] = stress

    cmu_coverage = len(word_stress_patterns) / len(set(words)) if words else 0.0

    metadata: dict[str, Any] = {
        "word_count": len(words),
        "unique_words": len(set(w.lower() for w in words)),
        "sentence_count": len(_split_sentences(text)),
        "total_syllables": sum(syl_counts),
        "cmu_coverage": cmu_coverage,
        "syllable_distribution": dict(Counter(syl_counts)),
        "word_stress_patterns": word_stress_patterns,
    }

    return RhythmProsodyResult(
        mean_syllables_per_word=mean_syl,
        syllable_std_dev=syl_std,
        polysyllabic_ratio=poly_ratio,
        monosyllabic_ratio=mono_ratio,
        rhythmic_regularity=regularity,
        syllable_cv=cv,
        stress_pattern_entropy=stress_entropy,
        sentence_length_alternation=alternation,
        sentence_rhythm_score=rhythm_score,
        alliteration_density=alliteration,
        assonance_density=assonance,
        consonance_density=consonance,
        mean_consonant_cluster_length=mean_cluster,
        initial_cluster_ratio=initial_ratio,
        final_cluster_ratio=final_ratio,
        iambic_ratio=iambic,
        trochaic_ratio=trochaic,
        dactylic_ratio=dactylic,
        anapestic_ratio=anapestic,
        metadata=metadata,
    )

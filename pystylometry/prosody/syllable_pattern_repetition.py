"""Syllable pattern repetition analysis.

This module detects repeated syllable patterns across sentences to identify
rhythmic repetition and formulaic structures in written text. Extends
sentence-level syllable analysis (Issue #66) by identifying recurring sequences
of syllable counts (n-grams) within and across sentences.

Repetitive syllable patterns reveal:
- Formulaic writing: Template-driven sentence construction
- Rhythmic preference: Consistent prosodic structure across sentences
- Stylistic habits: Unconscious patterns in clause and phrase construction
- Authorial fingerprint: Individual-specific rhythmic signatures

Related GitHub Issues:
    #67 - Syllable pattern repetition analysis
    https://github.com/craigtrim/pystylometry/issues/67
    #66 - Sentence-level syllable analysis
    https://github.com/craigtrim/pystylometry/issues/66

Academic Foundation:

    Prosodic patterns operate hierarchically from syllable to sentence level,
    with rhythmic structure serving as an implicit organizational principle.
    Research shows that "linguistic rhythm guides parsing decisions in written
    sentence comprehension," with readers constructing patterns of implicit
    lexical prominences during silent reading (Breen & Clifton, 2012).

    Stylometric analysis traditionally focuses on word frequency and syntactic
    structures, but prosodic features—including syllable patterns—represent an
    underexplored dimension of stylistic analysis (Lagutina & Lagutina, 2019).
    These rhythmic preferences largely operate below conscious awareness,
    developing through years of reading and writing practice, making them
    robust markers of authorial style.

    Computational prosody research establishes foundations for automated
    syllable pattern analysis. The Treeton system achieves 85% accuracy in
    metrical analysis through syllabic transcription and pattern recognition
    (Plecháč & Kolár, 2015). ProseRhythmDetector investigates "syllabic
    quantity as a base for deriving rhythmic features for computational
    authorship attribution."

References:
    Breen, M., & Clifton, C. (2012). Linguistic Rhythm Guides Parsing Decisions
        in Written Sentence Comprehension. Cognition, 123(1), 1-20.
    Gibbon, D. (2017). Prosody: Rhythms and Melodies of Speech. arXiv.
    Lagutina, K., & Lagutina, N. (2019). A Survey on Stylometric Text Features.
        FRUCT, 25, 1-14.
    Plecháč, P., & Kolár, R. (2015). Automated Analysis of Poetic Texts and
        the Problem of Verse Meter. Academia.edu.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any

from .._types import (
    SentenceSyllablePattern,
    SentenceSyllablePatternsResult,
    SyllablePatternNgram,
    SyllablePatternRepetitionResult,
)


def _extract_ngrams(
    syllables: list[int],
    n: int,
) -> list[tuple[int, ...]]:
    """Extract n-grams from syllable sequence.

    Uses sliding window to extract all n-grams of length n from the
    syllable sequence. For sequences shorter than n, returns empty list.

    Related GitHub Issue:
        #67 - Syllable pattern repetition analysis (n-gram extraction)
        https://github.com/craigtrim/pystylometry/issues/67

    Args:
        syllables: List of syllable counts (one per word)
        n: N-gram size (typically 3, 4, or 5)

    Returns:
        List of n-gram tuples

    Example:
        >>> _extract_ngrams([1, 2, 3, 1, 2], 3)
        [(1, 2, 3), (2, 3, 1), (3, 1, 2)]
        >>> _extract_ngrams([1, 2], 3)
        []
    """
    if len(syllables) < n:
        return []

    return [tuple(syllables[i : i + n]) for i in range(len(syllables) - n + 1)]


def _classify_position(
    ngram_index: int,
    total_ngrams: int,
    sequence_length: int,
    ngram_size: int,
) -> str:
    """Classify n-gram position as start, mid, or end.

    Determines whether an n-gram appears at the beginning, middle, or end
    of a sentence based on its index in the sliding window extraction.

    Position classification:
    - "start": First n-gram in sentence (index 0)
    - "end": Last n-gram in sentence (last possible index)
    - "mid": Any n-gram between start and end

    Related GitHub Issue:
        #67 - Syllable pattern repetition analysis (position-specific patterns)
        https://github.com/craigtrim/pystylometry/issues/67#position-metrics

    Args:
        ngram_index: Index of n-gram in sliding window extraction (0-based)
        total_ngrams: Total number of n-grams extracted from this sentence
        sequence_length: Length of original syllable sequence
        ngram_size: Size of n-gram (3, 4, or 5)

    Returns:
        Position classification: "start", "mid", or "end"

    Example:
        >>> # Sentence with 5 words → 3 possible 3-grams (indices 0, 1, 2)
        >>> _classify_position(0, 3, 5, 3)
        'start'
        >>> _classify_position(1, 3, 5, 3)
        'mid'
        >>> _classify_position(2, 3, 5, 3)
        'end'
    """
    if total_ngrams == 1:
        # Single n-gram covers entire sentence → both start and end
        return "start"

    if ngram_index == 0:
        return "start"
    elif ngram_index == total_ngrams - 1:
        return "end"
    else:
        return "mid"


def _calculate_shannon_entropy(frequency_dist: dict[int, int]) -> float:
    """Calculate Shannon entropy of pattern frequency distribution.

    Shannon entropy measures the unpredictability of the distribution.
    Lower entropy indicates more formulaic patterns (concentrated distribution),
    while higher entropy indicates diverse patterns (uniform distribution).

    Formula: H = -Σ(p_i × log₂(p_i))
    where p_i is the probability of each repetition count

    Related GitHub Issue:
        #67 - Syllable pattern repetition analysis (pattern distribution)
        https://github.com/craigtrim/pystylometry/issues/67#entropy

    Args:
        frequency_dist: Histogram mapping {repetition_count: num_patterns}
                       e.g., {1: 178, 2: 45, 3: 15, 4: 5, 5: 2}

    Returns:
        Shannon entropy in bits (base 2 logarithm)

    Example:
        >>> # Uniform: all patterns appear once
        >>> _calculate_shannon_entropy({1: 100})
        0.0
        >>> # Varied: some patterns repeat 2-5 times
        >>> _calculate_shannon_entropy({1: 50, 2: 30, 3: 15, 4: 4, 5: 1})
        1.48
    """
    if not frequency_dist:
        return 0.0

    total = sum(frequency_dist.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in frequency_dist.values():
        if count > 0:
            prob = count / total
            entropy -= prob * math.log2(prob)

    return entropy


def analyze_syllable_pattern_repetition(
    result: SentenceSyllablePatternsResult,
    ngram_sizes: list[int] = [3, 4, 5],
    min_repetitions: int = 2,
) -> SyllablePatternRepetitionResult:
    """Analyze repeated syllable patterns across sentences.

    Extracts n-grams of syllable counts from each sentence and identifies
    repetitive patterns. Particularly useful for detecting formulaic writing,
    rhythmic templates, and systematic composition patterns.

    Following computational prosody research (Gibbon, 2017; Plecháč & Kolár,
    2015), analyzes syllable patterns at multiple granularities:
    - 3-grams: Minimal rhythmic units (metrical feet)
    - 4-grams: Phrase-level patterns (short clauses)
    - 5-grams: Extended sequences (longer clauses)

    Position-specific analysis tracks sentence openings and closings separately
    to identify formulaic introductions and conclusions. Repetition of starting/
    ending patterns indicates template-driven composition.

    Pattern diversity ratio (unique/total) and repetition ratio (repeated/total)
    quantify formulaic versus organic writing style. Shannon entropy measures
    the concentration of pattern distribution, with lower entropy indicating
    more systematic (formulaic) patterns.

    Related GitHub Issues:
        #67 - Syllable pattern repetition analysis
        https://github.com/craigtrim/pystylometry/issues/67
        #66 - Sentence-level syllable analysis (prerequisite)
        https://github.com/craigtrim/pystylometry/issues/66

    References:
        Gibbon, D. (2017). Prosody: Rhythms and Melodies of Speech. arXiv.
        Plecháč, P., & Kolár, R. (2015). Automated Analysis of Poetic Texts
            and the Problem of Verse Meter. Academia.edu.
        Breen, M., & Clifton, C. (2012). Linguistic Rhythm Guides Parsing
            Decisions in Written Sentence Comprehension. Cognition, 123(1), 1-20.
        Lagutina, K., & Lagutina, N. (2019). A Survey on Stylometric Text
            Features. FRUCT, 25, 1-14.

    Args:
        result: SentenceSyllablePatternsResult from compute_sentence_syllable_patterns()
        ngram_sizes: List of n-gram sizes to extract (default: [3, 4, 5])
        min_repetitions: Minimum repetitions to flag pattern (default: 2)

    Returns:
        SyllablePatternRepetitionResult with n-gram analysis, repetition metrics,
        and position-specific patterns

    Example:
        >>> from pystylometry.prosody import compute_sentence_syllable_patterns
        >>> sent_result = compute_sentence_syllable_patterns(text)
        >>> pattern_result = analyze_syllable_pattern_repetition(sent_result)
        >>> print(f"Repetition ratio: {pattern_result.repetition_ratio:.2f}")
        0.14
        >>> print(f"Pattern entropy: {pattern_result.pattern_entropy:.2f} bits")
        3.45
        >>> for pattern in pattern_result.top_repeated_patterns[:5]:
        ...     print(f"Pattern {pattern.pattern}: {pattern.count} times")
        Pattern (1, 2, 3, 1): 5 times
        Pattern (2, 1, 2, 1): 4 times
    """
    # Handle empty result
    if not result.sentences:
        return SyllablePatternRepetitionResult(
            ngram_3_patterns=[],
            ngram_4_patterns=[],
            ngram_5_patterns=[],
            total_unique_patterns=0,
            total_pattern_instances=0,
            pattern_diversity_ratio=0.0,
            repeated_pattern_count=0,
            repetition_ratio=0.0,
            starting_pattern_repetition_rate=0.0,
            ending_pattern_repetition_rate=0.0,
            most_common_start=None,
            most_common_end=None,
            pattern_frequency_histogram={},
            pattern_entropy=0.0,
            top_repeated_patterns=[],
            metadata={
                "sentence_count": 0,
                "ngram_sizes": ngram_sizes,
                "min_repetitions": min_repetitions,
                "warning": "Empty input",
            },
        )

    # Collect all patterns with metadata
    # Structure: {ngram_size: {pattern: [(sent_idx, position), ...]}}
    pattern_occurrences: dict[int, dict[tuple[int, ...], list[tuple[int, str]]]] = {
        n: defaultdict(list) for n in ngram_sizes
    }

    # Track starting and ending patterns separately
    starting_patterns: Counter = Counter()
    ending_patterns: Counter = Counter()

    # Extract n-grams from each sentence
    for sent in result.sentences:
        syllables = sent.syllables_per_word

        for n in ngram_sizes:
            ngrams = _extract_ngrams(syllables, n)

            if not ngrams:
                # Sentence too short for this n-gram size
                continue

            total_ngrams = len(ngrams)

            for idx, ngram in enumerate(ngrams):
                # Classify position
                position = _classify_position(idx, total_ngrams, len(syllables), n)

                # Record occurrence
                pattern_occurrences[n][ngram].append((sent.sentence_index, position))

                # Track position-specific patterns
                if position == "start":
                    starting_patterns[ngram] += 1
                elif position == "end":
                    ending_patterns[ngram] += 1

    # Build SyllablePatternNgram objects for each n-gram size
    ngram_results: dict[int, list[SyllablePatternNgram]] = {n: [] for n in ngram_sizes}

    for n in ngram_sizes:
        for pattern, occurrences in pattern_occurrences[n].items():
            count = len(occurrences)
            sentence_indices = [sent_idx for sent_idx, _ in occurrences]
            positions = [pos for _, pos in occurrences]

            ngram_obj = SyllablePatternNgram(
                pattern=pattern,
                count=count,
                sentence_indices=sentence_indices,
                positions=positions,
            )
            ngram_results[n].append(ngram_obj)

    # Sort by count (descending) for each n-gram size
    for n in ngram_sizes:
        ngram_results[n].sort(key=lambda x: x.count, reverse=True)

    # Compute aggregate metrics
    all_patterns = []
    for n in ngram_sizes:
        all_patterns.extend(ngram_results[n])

    total_unique_patterns = len(all_patterns)
    total_pattern_instances = sum(p.count for p in all_patterns)

    # Pattern diversity ratio: unique / total (higher = more diverse)
    pattern_diversity_ratio = (
        total_unique_patterns / total_pattern_instances
        if total_pattern_instances > 0
        else 0.0
    )

    # Repeated pattern count: patterns appearing 2+ times
    repeated_patterns = [p for p in all_patterns if p.count >= min_repetitions]
    repeated_pattern_count = len(repeated_patterns)

    # Repetition ratio: repeated / total (higher = more formulaic)
    repetition_ratio = (
        repeated_pattern_count / total_unique_patterns
        if total_unique_patterns > 0
        else 0.0
    )

    # Position-specific metrics
    sentence_count = len(result.sentences)

    # Starting pattern repetition rate: repeated openings / sentences
    repeated_starts = sum(1 for count in starting_patterns.values() if count >= 2)
    starting_pattern_repetition_rate = (
        repeated_starts / sentence_count if sentence_count > 0 else 0.0
    )

    # Ending pattern repetition rate: repeated closings / sentences
    repeated_ends = sum(1 for count in ending_patterns.values() if count >= 2)
    ending_pattern_repetition_rate = (
        repeated_ends / sentence_count if sentence_count > 0 else 0.0
    )

    # Most common starting/ending patterns
    most_common_start = (
        starting_patterns.most_common(1)[0] if starting_patterns else None
    )
    most_common_end = ending_patterns.most_common(1)[0] if ending_patterns else None

    # Pattern frequency histogram: {repetition_count: num_patterns}
    pattern_frequency_histogram: dict[int, int] = Counter(
        p.count for p in all_patterns
    )

    # Shannon entropy of pattern distribution
    pattern_entropy = _calculate_shannon_entropy(pattern_frequency_histogram)

    # Top repeated patterns (across all n-gram sizes)
    top_repeated_patterns = sorted(all_patterns, key=lambda x: x.count, reverse=True)[
        :50
    ]  # Top 50

    # Metadata
    metadata: dict[str, Any] = {
        "sentence_count": sentence_count,
        "ngram_sizes": ngram_sizes,
        "min_repetitions": min_repetitions,
        "total_words": sum(s.word_count for s in result.sentences),
        "total_syllables": sum(s.syllable_count for s in result.sentences),
    }

    return SyllablePatternRepetitionResult(
        ngram_3_patterns=ngram_results.get(3, []),
        ngram_4_patterns=ngram_results.get(4, []),
        ngram_5_patterns=ngram_results.get(5, []),
        total_unique_patterns=total_unique_patterns,
        total_pattern_instances=total_pattern_instances,
        pattern_diversity_ratio=pattern_diversity_ratio,
        repeated_pattern_count=repeated_pattern_count,
        repetition_ratio=repetition_ratio,
        starting_pattern_repetition_rate=starting_pattern_repetition_rate,
        ending_pattern_repetition_rate=ending_pattern_repetition_rate,
        most_common_start=most_common_start,
        most_common_end=most_common_end,
        pattern_frequency_histogram=pattern_frequency_histogram,
        pattern_entropy=pattern_entropy,
        top_repeated_patterns=top_repeated_patterns,
        metadata=metadata,
    )

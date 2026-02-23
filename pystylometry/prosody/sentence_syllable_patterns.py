"""Sentence-level syllable analysis.

This module computes syllable distribution patterns within individual sentences,
capturing rhythmic structure and complexity at the sentence level. Useful for
detecting uniform complexity patterns (AI detection) and fine-grained prosodic
analysis.

Related GitHub Issues:
    #66 - Sentence-level syllable analysis
    https://github.com/craigtrim/pystylometry/issues/66
    #65 - AI-generated text detection module
    https://github.com/craigtrim/pystylometry/issues/65

AI Detection Signal:
    AI-generated text tends to produce sentences with uniform complexity:
    - Similar total syllables per sentence (low CV)
    - Similar syllables-per-word across sentences (low complexity variance)
    - High complexity_uniformity_score (>0.8) indicates AI-like uniformity

References:
    Thomson, M. (2025). The 7 Red Flags That Tell Readers You're Using ChatGPT.
    Lea, R. B., Mulligan, E. J., & Walton, J. H. (2005). Sentence rhythm and
        text comprehension. Memory & Cognition, 33(3), 388-396.
"""

from __future__ import annotations

import math
import statistics
from typing import Any

from .._types import Distribution, SentenceSyllablePattern, SentenceSyllablePatternsResult

# Import syllable counting from readability module
try:
    from ..readability.syllables import count_syllables
except ImportError:
    raise ImportError(
        "The 'cmudict' library is required for syllable counting. "
        "Install it with: pip install pystylometry[readability]"
    )

# Import sentence segmentation and tokenization from utils
#
# Related GitHub Issue:
#     #68 - Replace spaCy with built-in utilities
#     https://github.com/craigtrim/pystylometry/issues/68
from .._utils import split_sentences, tokenize


def _coefficient_of_variation(values: list[float]) -> float:
    """Compute coefficient of variation (CV = std / mean).

    Returns 0.0 for empty list or zero mean.
    """
    if not values or len(values) < 2:
        return 0.0

    mean = statistics.mean(values)
    if mean == 0.0:
        return 0.0

    std = statistics.stdev(values)
    return std / mean


def _create_distribution(values: list[float]) -> Distribution:
    """Create a Distribution object from a list of values."""
    if not values:
        return Distribution(
            values=[],
            mean=0.0,
            median=0.0,
            std=0.0,
            range=0.0,
            iqr=0.0,
        )

    if len(values) == 1:
        return Distribution(
            values=values,
            mean=values[0],
            median=values[0],
            std=0.0,
            range=0.0,
            iqr=0.0,
        )

    mean_val = statistics.mean(values)
    median_val = statistics.median(values)
    std_val = statistics.stdev(values)
    range_val = max(values) - min(values)

    # IQR calculation
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    q1_idx = n // 4
    q3_idx = 3 * n // 4
    iqr_val = sorted_vals[q3_idx] - sorted_vals[q1_idx] if n >= 4 else 0.0

    return Distribution(
        values=values,
        mean=mean_val,
        median=median_val,
        std=std_val,
        range=range_val,
        iqr=iqr_val,
    )


def compute_sentence_syllable_patterns(
    text: str,
) -> SentenceSyllablePatternsResult:
    """Compute sentence-level syllable analysis.

    Analyzes syllable distribution patterns within individual sentences,
    capturing rhythmic structure and complexity at the sentence level.
    Useful for detecting uniform complexity patterns (AI detection) and
    fine-grained prosodic analysis.

    Related GitHub Issues:
        #66 - Sentence-level syllable analysis
        https://github.com/craigtrim/pystylometry/issues/66
        #65 - AI-generated text detection module
        https://github.com/craigtrim/pystylometry/issues/65

    Metrics computed:

    Per-sentence breakdowns:
        - sentence_index: 0-indexed sentence number
        - word_count: Total words in sentence
        - syllable_count: Total syllables in sentence
        - syllables_per_word: Per-word syllable counts
        - mean_syllables: Average syllables per word in sentence
        - syllable_cv: Coefficient of variation of syllables per word

    Aggregate statistics:
        - mean_syllables_per_sentence: Average total syllables per sentence
        - std_syllables_per_sentence: Std dev of total syllables per sentence
        - sentence_syllable_cv: CV of sentence syllable totals

    Complexity uniformity (AI detection signal):
        - mean_sentence_complexity: Avg syllables/word at sentence level
        - std_sentence_complexity: Std dev of sentence complexity
        - complexity_uniformity_score: 0-1 (higher = more uniform, AI-like)
          Formula: 1.0 / (1.0 + complexity_cv)

    AI Detection Signal:
        - complexity_uniformity_score > 0.8: High uniformity (AI-like)
        - sentence_syllable_cv < 0.15: Very uniform syllable distribution
        - Low std_sentence_complexity: Similar complexity across sentences

    Dependencies:
        Requires cmudict for syllable counting.
        Install with: pip install pystylometry[readability]

    Args:
        text: Input text to analyze

    Returns:
        SentenceSyllablePatternsResult with per-sentence breakdowns and
        aggregate statistics

    Example:
        >>> result = compute_sentence_syllable_patterns(
        ...     "The quick brown fox. Jumped over the lazy dog."
        ... )
        >>> for sent in result.sentences:
        ...     print(f"Sentence {sent.sentence_index}: {sent.syllable_count} syllables")
        Sentence 0: 4 syllables
        Sentence 1: 6 syllables
        >>> print(f"Uniformity score: {result.complexity_uniformity_score:.2f}")
    """
    # Handle empty text
    if not text or not text.strip():
        return SentenceSyllablePatternsResult(
            sentences=[],
            mean_syllables_per_sentence=0.0,
            std_syllables_per_sentence=0.0,
            sentence_syllable_cv=0.0,
            mean_sentence_complexity=0.0,
            std_sentence_complexity=0.0,
            complexity_uniformity_score=0.0,
            syllables_per_sentence_dist=_create_distribution([]),
            complexity_dist=_create_distribution([]),
            metadata={"sentence_count": 0, "warning": "Empty text"},
        )

    # Segment text into sentences using built-in utilities
    #
    # Related GitHub Issue:
    #     #68 - Replace spaCy with built-in utilities (removes 1M char limit)
    #     https://github.com/craigtrim/pystylometry/issues/68
    #     #66 - Sentence-level syllable analysis
    #     https://github.com/craigtrim/pystylometry/issues/66
    #     #67 - Syllable pattern repetition analysis
    #     https://github.com/craigtrim/pystylometry/issues/67
    sentences = split_sentences(text)

    if not sentences:
        return SentenceSyllablePatternsResult(
            sentences=[],
            mean_syllables_per_sentence=0.0,
            std_syllables_per_sentence=0.0,
            sentence_syllable_cv=0.0,
            mean_sentence_complexity=0.0,
            std_sentence_complexity=0.0,
            complexity_uniformity_score=0.0,
            syllables_per_sentence_dist=_create_distribution([]),
            complexity_dist=_create_distribution([]),
            metadata={"sentence_count": 0, "warning": "No sentences found"},
        )

    # Analyze each sentence
    sentence_patterns: list[SentenceSyllablePattern] = []

    for idx, sent_text in enumerate(sentences):
        # Tokenize and extract alphabetic words only
        #
        # Related GitHub Issue:
        #     #68 - Replace spaCy tokenization with built-in tokenize()
        #     https://github.com/craigtrim/pystylometry/issues/68
        words = [w for w in tokenize(sent_text) if w.isalpha()]

        if not words:
            # Skip empty sentences
            continue

        # Count syllables per word
        syllables_per_word = [count_syllables(word) for word in words]
        total_syllables = sum(syllables_per_word)
        mean_syllables = statistics.mean(syllables_per_word)
        syllable_cv = _coefficient_of_variation(
            [float(s) for s in syllables_per_word]
        )

        pattern = SentenceSyllablePattern(
            sentence_index=idx,
            word_count=len(words),
            syllable_count=total_syllables,
            syllables_per_word=syllables_per_word,
            mean_syllables=mean_syllables,
            syllable_cv=syllable_cv,
        )
        sentence_patterns.append(pattern)

    # Handle case where no valid sentences were found
    if not sentence_patterns:
        return SentenceSyllablePatternsResult(
            sentences=[],
            mean_syllables_per_sentence=0.0,
            std_syllables_per_sentence=0.0,
            sentence_syllable_cv=0.0,
            mean_sentence_complexity=0.0,
            std_sentence_complexity=0.0,
            complexity_uniformity_score=0.0,
            syllables_per_sentence_dist=_create_distribution([]),
            complexity_dist=_create_distribution([]),
            metadata={"sentence_count": 0, "warning": "No valid sentences found"},
        )

    # Compute aggregate statistics
    total_syllables_list = [float(s.syllable_count) for s in sentence_patterns]
    complexities = [s.mean_syllables for s in sentence_patterns]

    mean_syllables_per_sentence = statistics.mean(total_syllables_list)
    std_syllables_per_sentence = (
        statistics.stdev(total_syllables_list)
        if len(total_syllables_list) > 1
        else 0.0
    )
    sentence_syllable_cv = _coefficient_of_variation(total_syllables_list)

    mean_sentence_complexity = statistics.mean(complexities)
    std_sentence_complexity = (
        statistics.stdev(complexities) if len(complexities) > 1 else 0.0
    )

    # Calculate complexity uniformity score (AI detection signal)
    # Formula: 1.0 / (1.0 + complexity_cv)
    # Higher score = more uniform = AI-like
    complexity_cv = _coefficient_of_variation(complexities)
    complexity_uniformity_score = 1.0 / (1.0 + complexity_cv)

    # Create distributions
    syllables_per_sentence_dist = _create_distribution(total_syllables_list)
    complexity_dist = _create_distribution(complexities)

    # Metadata
    #
    # Related GitHub Issue:
    #     #68 - Removed spacy_model (no longer using spaCy)
    #     https://github.com/craigtrim/pystylometry/issues/68
    metadata: dict[str, Any] = {
        "sentence_count": len(sentence_patterns),
        "total_words": sum(s.word_count for s in sentence_patterns),
        "total_syllables": sum(s.syllable_count for s in sentence_patterns),
        "complexity_cv": complexity_cv,
    }

    return SentenceSyllablePatternsResult(
        sentences=sentence_patterns,
        mean_syllables_per_sentence=mean_syllables_per_sentence,
        std_syllables_per_sentence=std_syllables_per_sentence,
        sentence_syllable_cv=sentence_syllable_cv,
        mean_sentence_complexity=mean_sentence_complexity,
        std_sentence_complexity=std_sentence_complexity,
        complexity_uniformity_score=complexity_uniformity_score,
        syllables_per_sentence_dist=syllables_per_sentence_dist,
        complexity_dist=complexity_dist,
        metadata=metadata,
    )

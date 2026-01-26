"""Dialect detection using extensible JSON markers.

This module implements dialect detection for stylometric analysis, identifying
regional linguistic preferences (British vs. American English) and measuring
text markedness. The analysis uses native chunked analysis per Issue #27,
computing metrics per chunk and providing distributions for fingerprinting.

Related GitHub Issues:
    #35 - Dialect detection with extensible JSON markers
    https://github.com/craigtrim/pystylometry/issues/35
    #30 - Whonix stylometry features (regional linguistic preferences)
    https://github.com/craigtrim/pystylometry/issues/30
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27

Theoretical Background:
    Dialectometry (Goebl, 1982; Nerbonne, 2009) provides the quantitative
    framework for measuring dialect similarity. Rather than selecting individual
    "characteristic" features, modern dialectometry quantifies holistically
    across all available markers.

    Markedness theory (Battistella, 1990) informs the markedness_score: marked
    forms stand out against "standard" written English. High markedness suggests
    intentional stylistic choice or strong dialect identity.

    Eye dialect (spellings like "gonna" that look nonstandard but reflect
    standard pronunciation) indicates informal register, not regional dialect
    (Encyclopedia.com, "Slang, Dialect, and Marked Language").

Detection Strategy:
    1. Tokenize text and identify words
    2. Match vocabulary (lexical level): flat/apartment, lorry/truck
    3. Match spelling patterns (phonological/morphological): colour/color, -ise/-ize
    4. Match grammar patterns (syntactic): have got/have, collective noun agreement
    5. Count eye dialect markers separately (register, not dialect)
    6. Apply feature weights from linguistic research
    7. Compute scores and classify dialect

Chunking:
    Following Issue #27, the text is split into chunks (default 1000 words).
    Each chunk is analyzed independently, then results are aggregated into
    Distribution objects. This captures variance across the text, which can
    reveal mixed authorship (e.g., human + AI-generated content).

References:
    Battistella, Edwin L. "Markedness: The Evaluative Superstructure of
        Language." State University of New York Press, 1990.
    Goebl, Hans. "Dialektometrie: Prinzipien und Methoden des Einsatzes der
        numerischen Taxonomie im Bereich der Dialektgeographie." Verlag der
        Österreichischen Akademie der Wissenschaften, 1982.
    Labov, William. "The Social Stratification of English in New York City."
        Cambridge University Press, 2006.
    Nerbonne, John. "Data-Driven Dialectology." Language and Linguistics
        Compass, vol. 3, no. 1, 2009, pp. 175-198.
    Whonix Project. "Stylometry: Deanonymization Techniques." Whonix Wiki,
        https://www.whonix.org/wiki/Stylometry
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .._types import DialectResult, Distribution, chunk_text, make_distribution
from ._loader import get_markers

# Simple word tokenizer pattern
_WORD_PATTERN = re.compile(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b")


@dataclass
class _ChunkAnalysis:
    """Internal result from analyzing a single chunk.

    This dataclass holds per-chunk metrics that will be aggregated into
    distributions for the final DialectResult.

    Attributes:
        british_count: Weighted count of British markers
        american_count: Weighted count of American markers
        total_markers: Total unweighted marker count
        word_count: Total words in chunk
        eye_dialect_count: Eye dialect markers found
        markers_by_level: Markers categorized by linguistic level
        spelling_markers: Individual spelling markers found
        vocabulary_markers: Individual vocabulary markers found
        grammar_markers: Individual grammar markers found
    """

    british_count: float
    american_count: float
    total_markers: int
    word_count: int
    eye_dialect_count: int
    markers_by_level: dict[str, dict[str, int]]
    spelling_markers: dict[str, int]
    vocabulary_markers: dict[str, int]
    grammar_markers: dict[str, int]


def _tokenize_words(text: str) -> list[str]:
    """Extract words from text for analysis.

    Uses a simple regex pattern that captures contractions (don't, I'm)
    as single tokens. All words are lowercased for matching.

    Args:
        text: Input text

    Returns:
        List of lowercase words
    """
    return [match.group().lower() for match in _WORD_PATTERN.finditer(text)]


def _compute_dialect_single(text: str) -> _ChunkAnalysis:
    """Compute dialect metrics for a single chunk of text.

    This is the core detection function, called once per chunk. It matches
    vocabulary, spelling patterns, and grammar patterns against the text,
    applying feature weights from the JSON database.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Args:
        text: Single chunk of text to analyze

    Returns:
        _ChunkAnalysis with all metrics for this chunk
    """
    markers = get_markers()
    words = _tokenize_words(text)
    word_count = len(words)

    # Initialize counters
    british_count = 0.0
    american_count = 0.0
    total_markers = 0
    eye_dialect_count = 0

    markers_by_level: dict[str, dict[str, int]] = {
        "phonological": {},
        "morphological": {},
        "lexical": {},
        "syntactic": {},
    }
    spelling_markers: dict[str, int] = defaultdict(int)
    vocabulary_markers: dict[str, int] = defaultdict(int)
    grammar_markers: dict[str, int] = defaultdict(int)

    # ===== Vocabulary matching (lexical level) =====
    # Match against vocabulary pairs and exclusive vocabulary
    for word in words:
        if word in markers.british_vocabulary:
            british_count += 1.0  # Default weight 1.0 for vocabulary
            total_markers += 1
            vocabulary_markers[word] += 1
            markers_by_level["lexical"][word] = markers_by_level["lexical"].get(word, 0) + 1

        if word in markers.american_vocabulary:
            american_count += 1.0
            total_markers += 1
            vocabulary_markers[word] += 1
            markers_by_level["lexical"][word] = markers_by_level["lexical"].get(word, 0) + 1

    # ===== Standalone spelling matching (phonological level) =====
    # Direct word pairs like grey/gray, cheque/check
    for word in words:
        if word in markers.british_spellings:
            british_count += 0.9  # High weight for spelling differences
            total_markers += 1
            spelling_markers[word] += 1
            markers_by_level["phonological"][word] = (
                markers_by_level["phonological"].get(word, 0) + 1
            )

        if word in markers.american_spellings:
            american_count += 0.9
            total_markers += 1
            spelling_markers[word] += 1
            markers_by_level["phonological"][word] = (
                markers_by_level["phonological"].get(word, 0) + 1
            )

    # ===== Regex spelling patterns (morphological level) =====
    # Patterns like -ise/-ize, -our/-or with feature weights
    text_lower = text.lower()
    for pattern in markers.spelling_patterns:
        weight = pattern.weight
        feature_level = pattern.feature_level

        # Match British pattern
        if pattern.pattern_british:
            for match in pattern.pattern_british.finditer(text_lower):
                word = match.group().lower()
                # Skip exceptions
                if word not in pattern.exceptions:
                    british_count += weight
                    total_markers += 1
                    spelling_markers[word] += 1
                    markers_by_level[feature_level][word] = (
                        markers_by_level[feature_level].get(word, 0) + 1
                    )

        # Match American pattern
        if pattern.pattern_american:
            for match in pattern.pattern_american.finditer(text_lower):
                word = match.group().lower()
                if word not in pattern.exceptions:
                    american_count += weight
                    total_markers += 1
                    spelling_markers[word] += 1
                    markers_by_level[feature_level][word] = (
                        markers_by_level[feature_level].get(word, 0) + 1
                    )

    # ===== Grammar patterns (syntactic level) =====
    # Patterns like "have got", "gotten", collective noun agreement
    for grammar_pattern in markers.grammar_patterns:
        weight = grammar_pattern.weight

        # Match British grammar pattern
        if grammar_pattern.pattern_british:
            matches = list(grammar_pattern.pattern_british.finditer(text_lower))
            if matches:
                british_count += weight * len(matches)
                total_markers += len(matches)
                grammar_markers[grammar_pattern.name] = len(matches)
                markers_by_level["syntactic"][grammar_pattern.name] = markers_by_level[
                    "syntactic"
                ].get(grammar_pattern.name, 0) + len(matches)

        # Match American grammar pattern
        if grammar_pattern.pattern_american:
            matches = list(grammar_pattern.pattern_american.finditer(text_lower))
            if matches:
                american_count += weight * len(matches)
                total_markers += len(matches)
                grammar_markers[grammar_pattern.name] = grammar_markers.get(
                    grammar_pattern.name, 0
                ) + len(matches)
                markers_by_level["syntactic"][grammar_pattern.name] = markers_by_level[
                    "syntactic"
                ].get(grammar_pattern.name, 0) + len(matches)

    # ===== Eye dialect (register markers, not dialect) =====
    # gonna, wanna, etc. indicate informal register
    for word in words:
        if word in markers.eye_dialect_words:
            eye_dialect_count += 1

    return _ChunkAnalysis(
        british_count=british_count,
        american_count=american_count,
        total_markers=total_markers,
        word_count=word_count,
        eye_dialect_count=eye_dialect_count,
        markers_by_level=dict(markers_by_level),
        spelling_markers=dict(spelling_markers),
        vocabulary_markers=dict(vocabulary_markers),
        grammar_markers=dict(grammar_markers),
    )


def _classify_dialect(british_score: float, american_score: float) -> tuple[str, float]:
    """Classify dialect based on scores.

    Classification rules:
    - If both scores are very low (< 0.1), classify as "neutral"
    - If scores are close (within 20% of each other), classify as "mixed"
    - Otherwise, classify as the dominant dialect

    Args:
        british_score: Normalized British marker score (0.0-1.0)
        american_score: Normalized American marker score (0.0-1.0)

    Returns:
        Tuple of (dialect, confidence) where dialect is one of:
        "british", "american", "mixed", "neutral"
    """
    # Both very low -> neutral
    if british_score < 0.05 and american_score < 0.05:
        return "neutral", 0.5

    total = british_score + american_score
    if total == 0:
        return "neutral", 0.5

    # Calculate ratio
    british_ratio = british_score / total
    american_ratio = american_score / total

    # Close scores -> mixed
    if abs(british_ratio - american_ratio) < 0.2:
        confidence = 1.0 - abs(british_ratio - american_ratio)
        return "mixed", confidence

    # Dominant dialect
    if british_ratio > american_ratio:
        confidence = british_ratio
        return "british", confidence
    else:
        confidence = american_ratio
        return "american", confidence


def _compute_markedness(
    british_score: float, american_score: float, eye_dialect_ratio: float
) -> float:
    """Compute markedness score.

    Markedness measures how far the text deviates from "unmarked" standard
    English. High markedness suggests intentional stylistic choice or strong
    dialect identity.

    Following Battistella (1990), markedness is computed as the sum of:
    - Dialect marker density (British + American)
    - Eye dialect density (informal register markers)

    Normalized to 0.0-1.0 range.

    Args:
        british_score: Normalized British score
        american_score: Normalized American score
        eye_dialect_ratio: Eye dialect per 1000 words

    Returns:
        Markedness score 0.0-1.0 (higher = more marked)
    """
    # Combine dialect markers and eye dialect
    dialect_component = (british_score + american_score) / 2
    register_component = min(eye_dialect_ratio / 10, 1.0)  # Cap at 10 per 1000 words

    # Weighted combination (dialect matters more than register)
    markedness = 0.7 * dialect_component + 0.3 * register_component

    return min(markedness, 1.0)


def compute_dialect(text: str, chunk_size: int = 1000) -> DialectResult:
    """Compute dialect detection metrics for a text.

    This function uses native chunked analysis per Issue #27, computing
    metrics per chunk and aggregating into distributions. The variance
    across chunks can reveal mixed authorship (e.g., UK writer using
    ChatGPT-generated American English content).

    Related GitHub Issues:
        #35 - Dialect detection with extensible JSON markers
        https://github.com/craigtrim/pystylometry/issues/35
        #30 - Whonix stylometry features (regional linguistic preferences)
        https://github.com/craigtrim/pystylometry/issues/30
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Detection Process:
        1. Split text into chunks (default 1000 words)
        2. For each chunk:
           - Match vocabulary (lexical level)
           - Match spelling patterns (phonological/morphological)
           - Match grammar patterns (syntactic level)
           - Count eye dialect markers (register indicator)
           - Apply feature weights from linguistic research
        3. Aggregate into distributions
        4. Classify dialect and compute confidence

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        DialectResult with dialect classification, scores, distributions,
        and detailed marker breakdowns

    Example:
        >>> result = compute_dialect("The colour of the programme was brilliant.")
        >>> result.dialect
        'british'
        >>> result.british_score
        0.85
        >>> result.markedness_score
        0.42

        >>> # Detect mixed dialect
        >>> result = compute_dialect("I love the color of autumn leaves in the neighbourhood.")
        >>> result.dialect
        'mixed'
        >>> result.british_score_dist.std  # Low std = consistent markers
        0.02
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Analyze each chunk
    british_scores: list[float] = []
    american_scores: list[float] = []
    markedness_scores: list[float] = []

    total_eye_dialect = 0
    total_word_count = 0

    # Aggregate markers across chunks
    agg_markers_by_level: dict[str, dict[str, int]] = {
        "phonological": {},
        "morphological": {},
        "lexical": {},
        "syntactic": {},
    }
    agg_spelling: dict[str, int] = defaultdict(int)
    agg_vocabulary: dict[str, int] = defaultdict(int)
    agg_grammar: dict[str, int] = defaultdict(int)

    for chunk in chunks:
        analysis = _compute_dialect_single(chunk)

        # Skip empty chunks
        if analysis.word_count == 0:
            continue

        # Normalize scores to per-1000-words for comparability
        normalizer = 1000.0 / analysis.word_count if analysis.word_count > 0 else 0

        british_normalized = analysis.british_count * normalizer
        american_normalized = analysis.american_count * normalizer
        eye_dialect_ratio = analysis.eye_dialect_count * normalizer

        # Convert to 0-1 scale (cap at reasonable maximum)
        # Typical texts have 0-50 markers per 1000 words
        british_score = min(british_normalized / 50, 1.0)
        american_score = min(american_normalized / 50, 1.0)

        british_scores.append(british_score)
        american_scores.append(american_score)

        # Compute markedness for this chunk
        markedness = _compute_markedness(british_score, american_score, eye_dialect_ratio)
        markedness_scores.append(markedness)

        # Aggregate counts
        total_eye_dialect += analysis.eye_dialect_count
        total_word_count += analysis.word_count

        # Aggregate markers
        for level, markers in analysis.markers_by_level.items():
            for marker, count in markers.items():
                agg_markers_by_level[level][marker] = (
                    agg_markers_by_level[level].get(marker, 0) + count
                )

        for marker, count in analysis.spelling_markers.items():
            agg_spelling[marker] += count
        for marker, count in analysis.vocabulary_markers.items():
            agg_vocabulary[marker] += count
        for marker, count in analysis.grammar_markers.items():
            agg_grammar[marker] += count

    # Handle empty text
    if not british_scores:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return DialectResult(
            dialect="neutral",
            confidence=0.0,
            british_score=float("nan"),
            american_score=float("nan"),
            markedness_score=float("nan"),
            british_score_dist=empty_dist,
            american_score_dist=empty_dist,
            markedness_score_dist=empty_dist,
            markers_by_level=agg_markers_by_level,
            spelling_markers=dict(agg_spelling),
            vocabulary_markers=dict(agg_vocabulary),
            grammar_markers=dict(agg_grammar),
            eye_dialect_count=0,
            eye_dialect_ratio=0.0,
            register_hints={},
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={"total_word_count": 0},
        )

    # Build distributions
    british_dist = make_distribution(british_scores)
    american_dist = make_distribution(american_scores)
    markedness_dist = make_distribution(markedness_scores)

    # Classify based on mean scores
    dialect, confidence = _classify_dialect(british_dist.mean, american_dist.mean)

    # Compute overall eye dialect ratio
    eye_dialect_ratio = (
        (total_eye_dialect / total_word_count * 1000) if total_word_count > 0 else 0.0
    )

    # Build register hints
    register_hints: dict[str, Any] = {
        "eye_dialect_density": eye_dialect_ratio,
        "marker_density": (british_dist.mean + american_dist.mean) / 2,
    }

    return DialectResult(
        dialect=dialect,
        confidence=confidence,
        british_score=british_dist.mean,
        american_score=american_dist.mean,
        markedness_score=markedness_dist.mean,
        british_score_dist=british_dist,
        american_score_dist=american_dist,
        markedness_score_dist=markedness_dist,
        markers_by_level=agg_markers_by_level,
        spelling_markers=dict(agg_spelling),
        vocabulary_markers=dict(agg_vocabulary),
        grammar_markers=dict(agg_grammar),
        eye_dialect_count=total_eye_dialect,
        eye_dialect_ratio=eye_dialect_ratio,
        register_hints=register_hints,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "total_word_count": total_word_count,
            "markers_version": get_markers().version,
        },
    )

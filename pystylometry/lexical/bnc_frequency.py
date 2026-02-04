"""BNC (British National Corpus) frequency analysis for stylometric comparison.

This module computes word frequency ratios by comparing observed word frequencies
in a text against expected frequencies from the British National Corpus (BNC).
Words can be categorized as:
- Overused: appear more frequently than expected (ratio > 1)
- Underused: appear less frequently than expected (ratio < 1)
- Not in BNC: words that don't exist in the BNC corpus

Related GitHub Issue:
    #TBD - BNC frequency analysis CLI
    https://github.com/craigtrim/pystylometry/issues/TBD

References:
    British National Corpus: http://www.natcorp.ox.ac.uk/
    The BNC is a 100-million word collection of samples of written and spoken
    language from a wide range of sources, designed to represent a wide
    cross-section of British English from the late 20th century.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Literal

from .._utils import check_optional_dependency


@dataclass
class WordAnalysis:
    """Analysis of a single word against BNC frequency.

    Attributes:
        word: The word being analyzed (lowercase)
        observed: Number of times the word appears in the text
        expected: Expected count based on BNC relative frequency
        ratio: observed / expected (None if not in BNC)
        in_wordnet: Whether the word exists in WordNet
        char_type: Classification of character content
    """

    word: str
    observed: int
    expected: float | None
    ratio: float | None
    in_wordnet: bool | None
    char_type: Literal["latin", "unicode", "numeric", "mixed", "punctuation"]


@dataclass
class BNCFrequencyResult:
    """Result of BNC frequency analysis.

    Attributes:
        overused: Words appearing more frequently than expected (ratio > threshold)
        underused: Words appearing less frequently than expected (ratio < threshold)
        not_in_bnc: Words not found in the BNC corpus
        total_tokens: Total word count in the text
        unique_tokens: Number of unique words
        overuse_threshold: Ratio above which words are considered overused
        underuse_threshold: Ratio below which words are considered underused
        metadata: Additional analysis metadata
    """

    overused: list[WordAnalysis]
    underused: list[WordAnalysis]
    not_in_bnc: list[WordAnalysis]
    total_tokens: int
    unique_tokens: int
    overuse_threshold: float
    underuse_threshold: float
    metadata: dict


def _classify_char_type(
    word: str,
) -> Literal["latin", "unicode", "numeric", "mixed", "punctuation"]:
    """Classify the character content of a word.

    Args:
        word: Word to classify

    Returns:
        Character type classification:
        - latin: Pure ASCII alphabetic characters (a-z, A-Z)
        - unicode: Contains non-ASCII characters (accents, etc.)
        - numeric: Contains only digits
        - mixed: Contains letters and numbers or other combinations
        - punctuation: Contains only punctuation
    """
    if not word:
        return "punctuation"

    has_ascii_alpha = bool(re.search(r"[a-zA-Z]", word))
    has_unicode_alpha = any(unicodedata.category(c).startswith("L") and ord(c) > 127 for c in word)
    has_digit = any(c.isdigit() for c in word)
    has_punct = any(unicodedata.category(c).startswith("P") for c in word)

    # Determine classification
    if has_unicode_alpha:
        return "unicode"
    elif has_digit and not has_ascii_alpha:
        return "numeric"
    elif has_digit and has_ascii_alpha:
        return "mixed"
    elif has_ascii_alpha and not has_punct:
        return "latin"
    elif has_ascii_alpha and has_punct:
        return "mixed"
    elif not has_ascii_alpha and not has_digit:
        return "punctuation"
    else:
        return "mixed"


def compute_bnc_frequency(
    text: str,
    overuse_threshold: float = 1.3,
    underuse_threshold: float = 0.8,
    include_wordnet: bool = True,
    min_mentions: int = 1,
) -> BNCFrequencyResult:
    """Compute BNC frequency analysis for a text.

    Compares observed word frequencies against expected frequencies from the
    British National Corpus. Words are categorized as overused, underused,
    or not in BNC based on their frequency ratios.

    Args:
        text: Input text to analyze
        overuse_threshold: Ratio above which words are considered overused (default: 1.3)
        underuse_threshold: Ratio below which words are considered underused (default: 0.8)
        include_wordnet: Whether to check WordNet for unknown words (default: True)
        min_mentions: Minimum number of mentions to include word (default: 1)

    Returns:
        BNCFrequencyResult with categorized word lists

    Raises:
        ImportError: If bnc-lookup package is not installed

    Example:
        >>> result = compute_bnc_frequency("The captain ordered the larboard watch...")
        >>> result.overused[:3]  # Top 3 overused words
        [WordAnalysis(word='larboard', ratio=33153.5, ...), ...]
        >>> result.not_in_bnc[:3]  # Words not in BNC
        [WordAnalysis(word='xyzbot', ...), ...]
    """
    # Check dependency
    check_optional_dependency("bnc_lookup", "lexical")
    from bnc_lookup import relative_frequency  # type: ignore[import-untyped]

    # Optional wordnet lookup
    wordnet_checker = None
    if include_wordnet:
        try:
            from wordnet_lookup import (
                is_wordnet_term as _is_wordnet_term,  # type: ignore[import-untyped]
            )

            wordnet_checker = _is_wordnet_term
        except ImportError:
            # WordNet lookup is optional
            pass

    # Tokenize text (simple whitespace + punctuation stripping)
    raw_tokens = text.split()
    tokens = []
    for raw in raw_tokens:
        # Strip leading/trailing punctuation, lowercase
        cleaned = re.sub(r"^[^\w]+|[^\w]+$", "", raw).lower()
        if cleaned:
            tokens.append(cleaned)

    total_tokens = len(tokens)

    # Count observed frequency of each word
    observed = Counter(tokens)
    unique_words = list(observed.keys())

    # Get BNC relative frequencies (one at a time - bnc_lookup doesn't have batch)
    bnc_freqs = {word: relative_frequency(word) for word in unique_words}

    # Analyze each word
    overused: list[WordAnalysis] = []
    underused: list[WordAnalysis] = []
    not_in_bnc: list[WordAnalysis] = []

    for word, obs_count in observed.items():
        if obs_count < min_mentions:
            continue

        # Classify character type
        char_type = _classify_char_type(word)

        # Get BNC frequency
        rel_freq = bnc_freqs.get(word)

        # Check WordNet if requested
        in_wordnet = None
        if wordnet_checker is not None:
            in_wordnet = wordnet_checker(word)

        if rel_freq is None or rel_freq == 0:
            # Word not in BNC
            analysis = WordAnalysis(
                word=word,
                observed=obs_count,
                expected=None,
                ratio=None,
                in_wordnet=in_wordnet,
                char_type=char_type,
            )
            not_in_bnc.append(analysis)
        else:
            # Compute expected count and ratio
            expected = rel_freq * total_tokens
            ratio = obs_count / expected if expected > 0 else None

            analysis = WordAnalysis(
                word=word,
                observed=obs_count,
                expected=expected,
                ratio=ratio,
                in_wordnet=in_wordnet,
                char_type=char_type,
            )

            if ratio is not None:
                if ratio > overuse_threshold:
                    overused.append(analysis)
                elif ratio < underuse_threshold:
                    underused.append(analysis)

    # Sort by ratio (highest first for overused, lowest first for underused)
    overused.sort(key=lambda x: x.ratio or 0, reverse=True)
    underused.sort(key=lambda x: x.ratio or float("inf"))
    # Sort not_in_bnc by observed count
    not_in_bnc.sort(key=lambda x: x.observed, reverse=True)

    return BNCFrequencyResult(
        overused=overused,
        underused=underused,
        not_in_bnc=not_in_bnc,
        total_tokens=total_tokens,
        unique_tokens=len(unique_words),
        overuse_threshold=overuse_threshold,
        underuse_threshold=underuse_threshold,
        metadata={
            "include_wordnet": include_wordnet,
            "min_mentions": min_mentions,
            "overused_count": len(overused),
            "underused_count": len(underused),
            "not_in_bnc_count": len(not_in_bnc),
        },
    )

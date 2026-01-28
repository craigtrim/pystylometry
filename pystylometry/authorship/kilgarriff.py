"""Kilgarriff's Chi-Squared method for authorship attribution.

This module implements Adam Kilgarriff's chi-squared method for measuring
statistical distance between two text corpora based on word frequency
distributions. The method is particularly effective for authorship attribution
when comparing frequency profiles of common words.

Related GitHub Issues:
    #31 - Classical Stylometric Methods from Programming Historian
    https://github.com/craigtrim/pystylometry/issues/31
    #24 - Additional Authorship Attribution Methods
    https://github.com/craigtrim/pystylometry/issues/24
    #36 - Kilgarriff Chi-Squared drift detection (uses _kilgarriff_core)
    https://github.com/craigtrim/pystylometry/issues/36

Algorithm Overview:
    Kilgarriff's method compares two texts by:
    1. Combining both texts into a joint corpus
    2. Extracting the top N most frequent words from the joint corpus
    3. For each word, computing expected vs. observed frequencies
    4. Applying the chi-squared formula: χ² = Σ((O - E)² / E)

    Lower chi-squared values indicate more similar texts (likely same author).
    The method identifies which words contribute most to the difference,
    providing interpretable results.

Theoretical Background:
    The chi-squared test measures the discrepancy between observed and expected
    frequencies. In Kilgarriff's formulation, the expected frequency for a word
    is calculated assuming both texts come from the same underlying distribution
    (the joint corpus). Large deviations from this expectation contribute to
    higher chi-squared scores.

    Formula for expected frequency of word w in text T:
        E(w, T) = (count(w) in joint corpus) × (size(T) / size(joint corpus))

    Chi-squared contribution for word w:
        χ²(w) = ((O(w, T1) - E(w, T1))² / E(w, T1)) + ((O(w, T2) - E(w, T2))² / E(w, T2))

References:
    Kilgarriff, Adam. "Comparing Corpora." International Journal of Corpus
        Linguistics, vol. 6, no. 1, 2001, pp. 97-133.
        doi: 10.1075/ijcl.6.1.05kil

    Oakes, Michael P. "Statistics for Corpus Linguistics." Edinburgh University
        Press, 1998.

    Programming Historian. "Introduction to Stylometry with Python."
        https://programminghistorian.org/en/lessons/introduction-to-stylometry-with-python
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

from .._types import KilgarriffResult
from .._utils import tokenize


def _chi2_cdf(x: float, df: int) -> float:
    """
    Compute chi-squared CDF in pure Python (no scipy required).

    P(X ≤ x) for X ~ χ²(df), computed via the regularized lower
    incomplete gamma function: P(df/2, x/2).

    Uses series expansion for x < a+1, continued fraction otherwise.
    """
    if x <= 0 or df <= 0:
        return 0.0 if x <= 0 else 1.0

    a = df / 2.0
    z = x / 2.0

    if z < a + 1:
        # Series expansion for P(a, z)
        ap = a
        total = 1.0 / a
        delta = total

        for _ in range(1000):
            ap += 1
            delta *= z / ap
            total += delta
            if abs(delta) < abs(total) * 1e-15:
                break

        try:
            log_prefix = a * math.log(z) - z - math.lgamma(a)
            return min(max(total * math.exp(log_prefix), 0.0), 1.0)
        except (OverflowError, ValueError):
            return 0.0
    else:
        # Continued fraction for Q(a, z) = 1 - P(a, z)
        try:
            log_prefix = a * math.log(z) - z - math.lgamma(a)
        except (OverflowError, ValueError):
            return 1.0

        b = z + 1 - a
        c = 1.0 / 1e-30
        d = 1.0 / b
        h = d

        for i in range(1, 1000):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-15:
                break

        q = math.exp(log_prefix) * h
        return min(max(1.0 - q, 0.0), 1.0)


def _kilgarriff_core(
    tokens1: list[str],
    tokens2: list[str],
    n_words: int = 500,
) -> tuple[float, int, list[tuple[str, float]], dict[str, Any]]:
    """
    Core chi-squared computation between two tokenized texts.

    This internal function performs the actual chi-squared calculation and is
    shared by both compute_kilgarriff() (two-text comparison) and the
    consistency module's compute_kilgarriff_drift() (intra-document analysis).

    Related GitHub Issues:
        #31 - Classical Stylometric Methods from Programming Historian
        https://github.com/craigtrim/pystylometry/issues/31
        #36 - Shared by consistency/drift.py for sliding window analysis
        https://github.com/craigtrim/pystylometry/issues/36

    Algorithm:
        1. Count word frequencies in each token list
        2. Build joint vocabulary from top N words in combined corpus
        3. For each word in joint vocabulary:
           a. Compute observed count in each text
           b. Compute expected count based on joint corpus proportions
           c. Calculate chi-squared contribution: (O - E)² / E
        4. Sum contributions for total chi-squared statistic

    Args:
        tokens1: List of tokens from first text (already lowercased)
        tokens2: List of tokens from second text (already lowercased)
        n_words: Number of most frequent words to use (default: 500)

    Returns:
        Tuple of:
            - chi_squared: Total chi-squared statistic
            - df: Degrees of freedom (n_words - 1)
            - top_contributors: List of (word, contribution) pairs sorted by contribution
            - details: Dict with frequency tables and intermediate values

    Note:
        P-value computation is omitted because the chi-squared test assumptions
        are often violated in stylometric analysis (words are not independent).
        The raw chi-squared value is more useful for relative comparisons.

    Example:
        >>> tokens1 = ["the", "cat", "sat", "on", "the", "mat"]
        >>> tokens2 = ["the", "dog", "ran", "to", "the", "park"]
        >>> chi_sq, df, top, details = _kilgarriff_core(tokens1, tokens2, n_words=10)
        >>> print(f"Chi-squared: {chi_sq:.2f}")
    """
    # Handle edge cases
    if not tokens1 or not tokens2:
        return 0.0, 0, [], {"warning": "One or both token lists are empty"}

    # Count word frequencies
    freq1 = Counter(tokens1)
    freq2 = Counter(tokens2)

    # Build joint corpus vocabulary (top N words)
    # Kilgarriff (2001) recommends using the joint corpus to avoid bias
    joint_freq: Counter[str] = Counter()
    joint_freq.update(freq1)
    joint_freq.update(freq2)
    top_words = [word for word, _ in joint_freq.most_common(n_words)]

    # Calculate corpus sizes
    size1 = len(tokens1)
    size2 = len(tokens2)
    total_size = size1 + size2

    # Proportions for expected frequency calculation
    prop1 = size1 / total_size
    prop2 = size2 / total_size

    # Calculate chi-squared contributions for each word
    chi_squared = 0.0
    contributions: list[tuple[str, float]] = []

    for word in top_words:
        # Observed counts
        obs1 = freq1.get(word, 0)
        obs2 = freq2.get(word, 0)
        joint_count = obs1 + obs2

        # Expected counts (under null hypothesis of same distribution)
        # Expected = joint_count × proportion_of_corpus
        exp1 = joint_count * prop1
        exp2 = joint_count * prop2

        # Chi-squared contribution for this word
        # Only compute if expected > 0 to avoid division by zero
        contrib = 0.0
        if exp1 > 0:
            contrib += ((obs1 - exp1) ** 2) / exp1
        if exp2 > 0:
            contrib += ((obs2 - exp2) ** 2) / exp2

        chi_squared += contrib
        contributions.append((word, contrib))

    # Sort contributions by magnitude (descending)
    contributions.sort(key=lambda x: x[1], reverse=True)

    # Degrees of freedom: n_words - 1 (standard for chi-squared goodness of fit)
    df = len(top_words) - 1 if len(top_words) > 1 else 0

    # Detailed information for debugging and analysis
    details = {
        "text1_size": size1,
        "text2_size": size2,
        "joint_corpus_size": total_size,
        "text1_vocab": len(freq1),
        "text2_vocab": len(freq2),
        "joint_vocab": len(joint_freq),
        "features_used": len(top_words),
        "text1_proportion": prop1,
        "text2_proportion": prop2,
    }

    return chi_squared, df, contributions, details


def compute_kilgarriff(
    text1: str,
    text2: str,
    n_words: int = 500,
    top_features: int = 20,
) -> KilgarriffResult:
    """
    Compute Kilgarriff's chi-squared distance between two texts.

    This function measures the statistical distance between two texts based on
    their word frequency distributions. Lower values indicate more similar texts
    (likely same author or style). The method is particularly effective for
    authorship attribution.

    Related GitHub Issues:
        #31 - Classical Stylometric Methods from Programming Historian
        https://github.com/craigtrim/pystylometry/issues/31
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    Algorithm Overview:
        1. Tokenize both texts and convert to lowercase
        2. Extract top N most frequent words from joint corpus
        3. Compute chi-squared statistic comparing frequency distributions
        4. Identify most discriminating words

    Interpretation:
        - Lower χ² = More similar texts (likely same author)
        - Higher χ² = More different texts (likely different authors)
        - Top discriminating words reveal what makes texts different

    Recommended Usage:
        - Use n_words=500 for general authorship (Kilgarriff's recommendation)
        - Use n_words=100-200 for shorter texts (< 5000 words each)
        - Use n_words=1000+ for very long texts or fine-grained analysis

    References:
        Kilgarriff, Adam. "Comparing Corpora." International Journal of Corpus
            Linguistics, vol. 6, no. 1, 2001, pp. 97-133.

        Programming Historian. "Introduction to Stylometry with Python."
            https://programminghistorian.org/en/lessons/introduction-to-stylometry-with-python

    Args:
        text1: First text for comparison
        text2: Second text for comparison
        n_words: Number of most frequent words to analyze (default: 500).
            Higher values provide finer discrimination but require longer texts.
        top_features: Number of most distinctive features to return (default: 20).
            Controls the length of most_distinctive_features in the result.

    Returns:
        KilgarriffResult containing:
            - chi_squared: Chi-squared statistic (lower = more similar)
            - p_value: Statistical significance (often unreliable; use chi_squared for comparison)
            - degrees_of_freedom: n_words - 1
            - feature_count: Number of words used
            - most_distinctive_features: Words that contribute most to difference
            - metadata: Detailed frequency information

    Example:
        >>> # Compare two texts
        >>> result = compute_kilgarriff(text_by_author_a, text_by_author_b)
        >>> print(f"Chi-squared distance: {result.chi_squared:.2f}")
        >>> print(f"Most distinctive word: {result.most_distinctive_features[0][0]}")

        >>> # Lower chi-squared suggests same author
        >>> if result.chi_squared < threshold:
        ...     print("Texts are stylistically similar")

    Note:
        The p_value is included for completeness but should be interpreted
        cautiously. Chi-squared test assumptions (independence) are typically
        violated in text analysis. The raw chi_squared value is more reliable
        for relative comparisons between text pairs.
    """
    # Validate top_features
    if top_features < 1:
        raise ValueError("top_features must be >= 1")

    # Tokenize and lowercase
    # Using lowercase ensures "The" and "the" are counted together
    tokens1 = [t.lower() for t in tokenize(text1) if t.isalpha()]
    tokens2 = [t.lower() for t in tokenize(text2) if t.isalpha()]

    # Compute chi-squared using core function
    chi_squared, df, contributions, details = _kilgarriff_core(tokens1, tokens2, n_words=n_words)

    # P-value computation (pure Python, no scipy required)
    # Note: This is provided for completeness but should be used cautiously.
    # The chi-squared test assumes independence, which is violated in text.
    # For authorship attribution, relative chi-squared comparisons are more reliable.
    p_value = 1.0 - _chi2_cdf(chi_squared, df) if df > 0 else 1.0

    return KilgarriffResult(
        chi_squared=chi_squared,
        p_value=p_value,
        degrees_of_freedom=df,
        feature_count=len(contributions),
        most_distinctive_features=contributions[:top_features],
        metadata={
            **details,
            "all_contributions": contributions,  # Full list for detailed analysis
            "method": "kilgarriff_2001",
            "n_words_requested": n_words,
        },
    )

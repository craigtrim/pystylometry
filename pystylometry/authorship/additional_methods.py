"""Additional authorship attribution methods.

This module provides alternative distance/similarity metrics for authorship
attribution beyond Burrows' Delta and Zeta.

Related GitHub Issue:
    #24 - Additional Authorship Attribution Methods
    https://github.com/craigtrim/pystylometry/issues/24

Methods implemented:
    - Kilgarriff's Chi-squared -> See kilgarriff.py (Issue #31)
    - Min-Max distance (Burrows' original method)
    - John Burrows' Delta variations (Quadratic, Weighted)

References:
    Kilgarriff, A. (2001). Comparing corpora. International Journal of Corpus Linguistics.
    Burrows, J. F. (1992). Not unless you ask nicely. Literary and Linguistic Computing.
    Burrows, J. (2005). Who wrote Shamela? Literary and Linguistic Computing.
    Argamon, S. (2008). Interpreting Burrows's Delta. Literary and Linguistic Computing.
"""

from __future__ import annotations

import math
from collections import Counter

from .._types import JohnsBurrowsResult, MinMaxResult
from .._utils import tokenize


def compute_minmax(text1: str, text2: str, mfw: int = 100) -> MinMaxResult:
    """
    Compute Min-Max distance between two texts.

    This is Burrows' original method from his 1992 paper, before the development
    of Delta. It normalizes word frequencies using min-max scaling and computes
    the mean absolute distance between normalized frequency vectors.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    Algorithm:
        1. Tokenize both texts and build frequency distributions
        2. Identify the top N most frequent words in the joint corpus
        3. Compute relative frequencies for each word in each text
        4. Normalize each word's frequencies using min-max scaling:
           normalized(f) = (f - min) / (max - min)
        5. Compute mean absolute difference of normalized frequencies

    Interpretation:
        - Lower values indicate more similar texts (likely same author)
        - Higher values indicate more different texts
        - Scale: 0.0 (identical) to 1.0 (maximally different)

    References:
        Burrows, J. F. (1992). Not unless you ask nicely: The interpretative
            nexus between analysis and information. Literary and Linguistic
            Computing, 7(2), 91-109.

    Args:
        text1: First text for comparison
        text2: Second text for comparison
        mfw: Number of most frequent words to analyze (default: 100)

    Returns:
        MinMaxResult with min-max distance and distinctive features.

    Example:
        >>> result = compute_minmax(text_by_author_a, text_by_author_b)
        >>> print(f"MinMax distance: {result.minmax_distance:.3f}")
        >>> print(f"Most distinctive: {result.most_distinctive_features[0]}")
    """
    # Tokenize and lowercase
    tokens1 = [t.lower() for t in tokenize(text1) if t.isalpha()]
    tokens2 = [t.lower() for t in tokenize(text2) if t.isalpha()]

    if not tokens1 or not tokens2:
        return MinMaxResult(
            minmax_distance=0.0,
            feature_count=0,
            most_distinctive_features=[],
            metadata={
                "text1_size": len(tokens1),
                "text2_size": len(tokens2),
                "warning": "One or both texts are empty",
            },
        )

    # Build frequency distributions
    freq1 = Counter(tokens1)
    freq2 = Counter(tokens2)
    size1 = len(tokens1)
    size2 = len(tokens2)

    # Joint corpus: top N most frequent words
    joint: Counter[str] = Counter()
    joint.update(freq1)
    joint.update(freq2)
    top_words = [word for word, _ in joint.most_common(mfw)]

    if not top_words:
        return MinMaxResult(
            minmax_distance=0.0,
            feature_count=0,
            most_distinctive_features=[],
            metadata={
                "text1_size": size1,
                "text2_size": size2,
                "warning": "No common words found",
            },
        )

    # Relative frequencies
    rel1 = [freq1.get(w, 0) / size1 for w in top_words]
    rel2 = [freq2.get(w, 0) / size2 for w in top_words]

    # Min-Max normalization per feature across both texts
    # Then compute absolute distance
    contributions: list[tuple[str, float]] = []
    total_distance = 0.0

    for i, word in enumerate(top_words):
        f1, f2 = rel1[i], rel2[i]
        max_val = max(f1, f2)

        if max_val > 0:
            # Min-Max normalized distance for this feature
            dist = abs(f1 - f2) / max_val
        else:
            dist = 0.0

        total_distance += dist
        contributions.append((word, dist))

    # Sort contributions by magnitude
    contributions.sort(key=lambda x: x[1], reverse=True)

    # Mean distance across all features
    minmax_distance = total_distance / len(top_words) if top_words else 0.0

    return MinMaxResult(
        minmax_distance=minmax_distance,
        feature_count=len(top_words),
        most_distinctive_features=contributions[:20],
        metadata={
            "text1_size": size1,
            "text2_size": size2,
            "text1_vocab": len(freq1),
            "text2_vocab": len(freq2),
            "mfw_requested": mfw,
            "method": "minmax_1992",
            "all_contributions": contributions,
        },
    )


def compute_johns_delta(
    text1: str,
    text2: str,
    mfw: int = 100,
    method: str = "quadratic",
) -> JohnsBurrowsResult:
    """
    Compute John Burrows' Delta variations.

    This implements alternative formulations of Burrows' Delta metric beyond
    the standard mean absolute z-score difference. The quadratic variant uses
    squared z-score differences (Euclidean distance), while the weighted variant
    applies inverse-rank weighting so higher-frequency words contribute more.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    Methods:
        - "quadratic": Euclidean distance of z-scores
          Delta_Q = sqrt(sum((z1_i - z2_i)^2) / n)

        - "weighted": Inverse-rank weighted Delta
          Delta_W = sum(w_i * |z1_i - z2_i|) / sum(w_i)
          where w_i = 1 / rank_i

    Interpretation:
        - Lower values indicate more similar texts (likely same author)
        - Quadratic Delta penalizes large deviations more than standard Delta
        - Weighted Delta emphasizes the most frequent words

    References:
        Burrows, J. (2005). Who wrote Shamela? Verifying the authorship of a
            parodic text. Literary and Linguistic Computing, 20(4), 437-450.
        Argamon, S. (2008). Interpreting Burrows's Delta: Geometric and
            probabilistic foundations. Literary and Linguistic Computing,
            23(2), 131-147.

    Args:
        text1: First text for comparison
        text2: Second text for comparison
        mfw: Number of most frequent words to analyze (default: 100)
        method: Delta variation ("quadratic" or "weighted")

    Returns:
        JohnsBurrowsResult with delta score and method details.

    Example:
        >>> result = compute_johns_delta(text1, text2, method="quadratic")
        >>> print(f"Quadratic Delta: {result.delta_score:.3f}")
    """
    if method not in ("quadratic", "weighted"):
        raise ValueError(f"method must be 'quadratic' or 'weighted', got '{method}'")

    # Tokenize and lowercase
    tokens1 = [t.lower() for t in tokenize(text1) if t.isalpha()]
    tokens2 = [t.lower() for t in tokenize(text2) if t.isalpha()]

    if not tokens1 or not tokens2:
        return JohnsBurrowsResult(
            delta_score=0.0,
            method=method,
            feature_count=0,
            most_distinctive_features=[],
            metadata={
                "text1_size": len(tokens1),
                "text2_size": len(tokens2),
                "warning": "One or both texts are empty",
            },
        )

    # Build frequency distributions
    freq1 = Counter(tokens1)
    freq2 = Counter(tokens2)
    size1 = len(tokens1)
    size2 = len(tokens2)

    # Joint corpus: top N most frequent words
    joint: Counter[str] = Counter()
    joint.update(freq1)
    joint.update(freq2)
    top_words = [word for word, _ in joint.most_common(mfw)]

    if not top_words:
        return JohnsBurrowsResult(
            delta_score=0.0,
            method=method,
            feature_count=0,
            most_distinctive_features=[],
            metadata={
                "text1_size": size1,
                "text2_size": size2,
                "warning": "No common words found",
            },
        )

    # Relative frequencies
    rel1 = [freq1.get(w, 0) / size1 for w in top_words]
    rel2 = [freq2.get(w, 0) / size2 for w in top_words]

    # Mean-normalized differences
    # With only 2 texts, classical z-scores are degenerate: stdev([a,b]) is
    # always |a-b|/sqrt(2), producing identical z-scores (±0.707) for all
    # features with any difference. Instead, we normalize by the mean frequency
    # of each feature across both texts, which preserves discriminative power:
    #   normalized_i = (f1_i - f2_i) / mean(f1_i, f2_i)
    # This weights words proportionally to how much they differ relative to
    # their expected frequency, preventing high-frequency words from dominating
    # through absolute differences alone.
    z1: list[float] = []
    z2: list[float] = []
    for i in range(len(top_words)):
        mean_val = (rel1[i] + rel2[i]) / 2
        # Normalize by mean frequency; use epsilon for words absent in both
        norm = mean_val if mean_val > 0 else 1e-10
        z1.append((rel1[i] - mean_val) / norm)
        z2.append((rel2[i] - mean_val) / norm)

    # Compute distance based on method
    contributions: list[tuple[str, float]] = []

    if method == "quadratic":
        # Quadratic Delta: root mean squared z-score difference
        squared_diffs: list[float] = []
        for i, word in enumerate(top_words):
            diff_sq = (z1[i] - z2[i]) ** 2
            squared_diffs.append(diff_sq)
            contributions.append((word, diff_sq))

        delta_score = math.sqrt(sum(squared_diffs) / len(squared_diffs)) if squared_diffs else 0.0

    else:  # weighted
        # Weighted Delta: inverse-rank weighted mean absolute z-score difference
        weighted_diffs: list[float] = []
        weights: list[float] = []
        for i, word in enumerate(top_words):
            weight = 1.0 / (i + 1)  # Inverse rank weighting
            abs_diff = abs(z1[i] - z2[i])
            weighted_diffs.append(weight * abs_diff)
            weights.append(weight)
            contributions.append((word, abs_diff))

        delta_score = sum(weighted_diffs) / sum(weights) if weights else 0.0

    # Sort contributions by magnitude
    contributions.sort(key=lambda x: x[1], reverse=True)

    return JohnsBurrowsResult(
        delta_score=delta_score,
        method=method,
        feature_count=len(top_words),
        most_distinctive_features=contributions[:20],
        metadata={
            "text1_size": size1,
            "text2_size": size2,
            "text1_vocab": len(freq1),
            "text2_vocab": len(freq2),
            "mfw_requested": mfw,
            "z_scores_text1": dict(zip(top_words[:20], z1[:20])),
            "z_scores_text2": dict(zip(top_words[:20], z2[:20])),
            "all_contributions": contributions,
        },
    )

"""Burrows' Delta and Cosine Delta for authorship attribution."""

import math
import statistics
from collections import Counter

from .._types import BurrowsDeltaResult
from .._utils import tokenize


def compute_burrows_delta(
    text1: str, text2: str, mfw: int = 500, distance_type: str = "burrows"
) -> BurrowsDeltaResult:
    """
    Compute Burrows' Delta or Cosine Delta between two texts.

    Burrows' Delta:
        Delta = mean(|z₁(f) - z₂(f)|) for all features f
        where z(f) = (frequency(f) - mean(f)) / std(f)

    Cosine Delta:
        Delta = 1 - cos(z₁, z₂)
        Measures angular distance between z-score vectors

    Both methods:
    1. Extract most frequent words (MFW) across both texts
    2. Calculate word frequencies in each text
    3. Z-score normalize frequencies
    4. Compute distance measure

    Lower scores indicate more similar texts (likely same author).

    References:
        Burrows, J. (2002). 'Delta': A measure of stylistic difference and
        a guide to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.

        Argamon, S. (2008). Interpreting Burrows's Delta: Geometric and
        probabilistic foundations. Literary and Linguistic Computing, 23(2), 131-147.

    Args:
        text1: First text to compare
        text2: Second text to compare
        mfw: Number of most frequent words to use (default: 500)
        distance_type: "burrows", "cosine", or "eder" (default: "burrows")

    Returns:
        BurrowsDeltaResult with delta score and metadata

    Example:
        >>> result = compute_burrows_delta(text1, text2, mfw=300)
        >>> print(f"Delta score: {result.delta_score:.3f}")
        >>> print(f"Lower is more similar")
    """
    # Tokenize and count words
    tokens1 = [t.lower() for t in tokenize(text1)]
    tokens2 = [t.lower() for t in tokenize(text2)]

    if len(tokens1) == 0 or len(tokens2) == 0:
        return BurrowsDeltaResult(
            delta_score=0.0,
            distance_type=distance_type,
            mfw_count=0,
            metadata={
                "text1_token_count": len(tokens1),
                "text2_token_count": len(tokens2),
                "warning": "One or both texts are empty",
            },
        )

    # Get word frequencies
    freq1 = Counter(tokens1)
    freq2 = Counter(tokens2)

    # Get most frequent words across both texts
    all_words: Counter[str] = Counter()
    all_words.update(freq1)
    all_words.update(freq2)
    most_common_words = [word for word, _ in all_words.most_common(mfw)]

    # Calculate relative frequencies for MFW
    def get_relative_freqs(freq_counter: Counter, words: list[str], total: int) -> list[float]:
        return [freq_counter.get(word, 0) / total for word in words]

    rel_freqs1 = get_relative_freqs(freq1, most_common_words, len(tokens1))
    rel_freqs2 = get_relative_freqs(freq2, most_common_words, len(tokens2))

    # Combine for z-score calculation (treat as corpus)
    combined_freqs = [(f1 + f2) / 2 for f1, f2 in zip(rel_freqs1, rel_freqs2)]

    # Calculate standard deviation for each word position
    combined_std = []
    for i in range(len(most_common_words)):
        values = [rel_freqs1[i], rel_freqs2[i]]
        std = statistics.stdev(values) if len(set(values)) > 1 else 1e-10
        combined_std.append(std if std > 0 else 1e-10)

    # Calculate z-scores
    z1 = [(f - mean) / std for f, mean, std in zip(rel_freqs1, combined_freqs, combined_std)]
    z2 = [(f - mean) / std for f, mean, std in zip(rel_freqs2, combined_freqs, combined_std)]

    # Calculate distance based on type
    if distance_type == "burrows":
        # Burrows' Delta: mean absolute difference of z-scores
        abs_diffs = [abs(z1_val - z2_val) for z1_val, z2_val in zip(z1, z2)]
        delta_score = statistics.mean(abs_diffs) if abs_diffs else 0.0
    elif distance_type == "cosine":
        # Cosine Delta: 1 - cosine similarity
        dot_product = sum(z1_val * z2_val for z1_val, z2_val in zip(z1, z2))
        norm1 = math.sqrt(sum(z**2 for z in z1))
        norm2 = math.sqrt(sum(z**2 for z in z2))
        cosine_sim = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
        delta_score = 1 - cosine_sim
    elif distance_type == "eder":
        # Eder's Delta: similar to Burrows but with different normalization
        abs_diffs = [abs(z1_val - z2_val) for z1_val, z2_val in zip(z1, z2)]
        delta_score = statistics.mean(abs_diffs) if abs_diffs else 0.0
    else:
        abs_diffs = [abs(z1_val - z2_val) for z1_val, z2_val in zip(z1, z2)]
        delta_score = statistics.mean(abs_diffs) if abs_diffs else 0.0

    return BurrowsDeltaResult(
        delta_score=delta_score,
        distance_type=distance_type,
        mfw_count=len(most_common_words),
        metadata={
            "text1_token_count": len(tokens1),
            "text2_token_count": len(tokens2),
            "text1_vocab": len(freq1),
            "text2_vocab": len(freq2),
        },
    )


def compute_cosine_delta(text1: str, text2: str, mfw: int = 500) -> BurrowsDeltaResult:
    """
    Compute Cosine Delta between two texts.

    Convenience function that calls compute_burrows_delta with distance_type="cosine".

    Args:
        text1: First text to compare
        text2: Second text to compare
        mfw: Number of most frequent words to use (default: 500)

    Returns:
        BurrowsDeltaResult with cosine delta score

    Example:
        >>> result = compute_cosine_delta(text1, text2)
        >>> print(f"Cosine Delta: {result.delta_score:.3f}")
    """
    return compute_burrows_delta(text1, text2, mfw=mfw, distance_type="cosine")

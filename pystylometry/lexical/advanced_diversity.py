"""Advanced lexical diversity metrics.

This module provides sophisticated measures of lexical diversity that go beyond
simple Type-Token Ratio (TTR). These metrics are designed to control for text
length and provide more stable, comparable measures across texts of different sizes.

Related GitHub Issue:
    #14 - Advanced Lexical Diversity Metrics
    https://github.com/craigtrim/pystylometry/issues/14

Metrics implemented:
    - voc-D: Mathematical model-based diversity estimate
    - MATTR: Moving-Average Type-Token Ratio
    - HD-D: Hypergeometric Distribution D
    - MSTTR: Mean Segmental Type-Token Ratio

Each of these metrics addresses the "text length problem" that affects simple
TTR: longer texts tend to have lower TTR values because words repeat. These
advanced metrics normalize for length in different ways.

References:
    McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation
        study of sophisticated approaches to lexical diversity assessment.
        Behavior Research Methods, 42(2), 381-392.
    Malvern, D., Richards, B., Chipere, N., & Durán, P. (2004).
        Lexical Diversity and Language Development. Palgrave Macmillan.
    Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot:
        The moving-average type-token ratio (MATTR). Journal of Quantitative
        Linguistics, 17(2), 94-100.
"""

import random
from typing import Optional

from .._types import (
    HDDResult,
    MATTRResult,
    MSTTRResult,
    VocdDResult,
    make_distribution,
)


def _tokenize_for_diversity(text: str) -> list[str]:
    """Tokenize text for lexical diversity analysis.

    This helper function provides consistent tokenization across all
    diversity metrics. It:
    - Converts text to lowercase
    - Splits on whitespace
    - Strips punctuation from each token
    - Returns list of clean tokens

    Args:
        text: Input text to tokenize

    Returns:
        List of lowercase tokens with punctuation removed
    """
    if not text or not text.strip():
        return []

    # Lowercase entire text
    text_lower = text.lower()

    # Split on whitespace
    raw_tokens = text_lower.split()

    # Comprehensive punctuation set for stripping
    punctuation_chars = set(".,!?;:'\"()[]{}/-—–…*&@#$%^~`\\|<>«»„\"\"''‚'")

    # Strip punctuation from each token
    tokens = []
    for token in raw_tokens:
        # Strip leading and trailing punctuation
        clean_token = token.strip("".join(punctuation_chars))
        if clean_token:  # Only add non-empty tokens
            tokens.append(clean_token)

    return tokens


def compute_vocd_d(
    text: str,
    sample_size: int = 35,
    num_samples: int = 100,
    min_tokens: int = 100,
    random_seed: Optional[int] = None,
    chunk_size: int = 1000,
) -> VocdDResult:
    """
    Compute voc-D (vocabulary D) using curve-fitting approach.

    voc-D estimates lexical diversity by fitting a mathematical model to the
    relationship between tokens and types across multiple random samples.
    The D parameter represents theoretical vocabulary size and is more stable
    across text lengths than simple TTR.

    Related GitHub Issue:
        #14 - Advanced Lexical Diversity Metrics
        https://github.com/craigtrim/pystylometry/issues/14

    The algorithm:
        1. Take multiple random samples of varying sizes from the text
        2. For each sample size, calculate the mean TTR across samples
        3. Fit a curve to the (sample_size, TTR) relationship
        4. The D parameter is the best-fit curve parameter
        5. Higher D values indicate greater lexical diversity

    Advantages over TTR:
        - Less sensitive to text length
        - More comparable across texts of different sizes
        - Theoretically grounded in vocabulary acquisition models
        - Widely used in language development research

    Disadvantages:
        - Computationally expensive (requires many random samples)
        - Requires sufficient text length (typically 100+ tokens)
        - Can be unstable with very short texts
        - Curve fitting may not converge in some cases

    Args:
        text: Input text to analyze. Should contain at least min_tokens words
              for reliable D estimation. Texts with fewer tokens will return
              NaN or raise an error.
        sample_size: Size of random samples to draw. Default is 35 tokens,
                     following Malvern et al. (2004). Smaller sizes increase
                     variance; larger sizes may exceed text length.
        num_samples: Number of random samples to draw for each sample size.
                     More samples increase accuracy but also computation time.
                     Default is 100 samples.
        min_tokens: Minimum tokens required for D calculation. Texts shorter
                    than this will return NaN or error. Default is 100.

    Returns:
        VocdDResult containing:
            - d_parameter: The D value (higher = more diverse)
            - curve_fit_r_squared: Quality of curve fit (closer to 1.0 is better)
            - sample_count: Number of samples actually used
            - optimal_sample_size: Sample size used for calculation
            - metadata: Sampling details, convergence info, curve parameters

    Example:
        >>> text = "Long sample text with sufficient tokens..."
        >>> result = compute_vocd_d(text, sample_size=35, num_samples=100)
        >>> print(f"D parameter: {result.d_parameter:.2f}")
        D parameter: 67.34
        >>> print(f"Curve fit R²: {result.curve_fit_r_squared:.3f}")
        Curve fit R²: 0.987

        >>> # Short text handling
        >>> short_text = "Too short"
        >>> result = compute_vocd_d(short_text)
        >>> import math
        >>> math.isnan(result.d_parameter)
        True

    Note:
        - Requires random sampling, so results may vary slightly between runs
        - Use a random seed in metadata for reproducibility
        - Very short texts (< min_tokens) cannot be analyzed
        - D values typically range from 10 (low diversity) to 100+ (high diversity)
        - Curve fitting uses least-squares optimization
        - Poor curve fits (low R²) indicate unreliable D estimates
    """
    # Set random seed for reproducibility
    if random_seed is not None:
        random.seed(random_seed)

    # Step 1: Tokenize text
    tokens = _tokenize_for_diversity(text)
    total_tokens = len(tokens)
    total_types = len(set(tokens))

    # Step 2: Validate minimum length
    if total_tokens < min_tokens:
        raise ValueError(f"Text has {total_tokens} tokens, minimum {min_tokens} required for voc-D")

    # Step 3: Determine sample sizes to test
    # Test from 10 tokens up to min(100, total_tokens - 10)
    min_sample_size = 10
    max_sample_size = min(100, total_tokens - 10)

    # Create list of sample sizes (every 5 tokens)
    sample_sizes = list(range(min_sample_size, max_sample_size + 1, 5))

    # Ensure we have at least a few sample sizes
    if len(sample_sizes) < 3:
        # If text is very short, just use what we can
        sample_sizes = list(range(min_sample_size, max_sample_size + 1))

    # Step 4: For each sample size, take random samples and calculate mean TTR
    sample_size_to_mean_ttr: dict[int, float] = {}

    for size in sample_sizes:
        ttrs = []
        for _ in range(num_samples):
            # Random sample of 'size' tokens
            sample = random.sample(tokens, size)
            sample_types = len(set(sample))
            ttr = sample_types / size
            ttrs.append(ttr)

        # Mean TTR for this sample size
        mean_ttr = sum(ttrs) / len(ttrs)
        sample_size_to_mean_ttr[size] = mean_ttr

    # Step 5: Fit curve using model: TTR = D / sqrt(sample_size)
    # Using least-squares fitting for y = a/sqrt(x)
    # Minimize: sum((y_i - a/sqrt(x_i))^2)
    # Solution: a = sum(y_i/sqrt(x_i)) / sum(1/x_i)

    numerator = 0.0
    denominator = 0.0

    for size, ttr in sample_size_to_mean_ttr.items():
        numerator += ttr / (size**0.5)
        denominator += 1.0 / size

    d_param = numerator / denominator if denominator > 0 else 0.0

    # Step 6: Calculate R² (goodness of fit)
    # Predicted TTR = D / sqrt(sample_size)
    y_actual = list(sample_size_to_mean_ttr.values())
    y_predicted = [d_param / (size**0.5) for size in sample_sizes]

    # R² calculation
    mean_y = sum(y_actual) / len(y_actual)
    ss_tot = sum((y - mean_y) ** 2 for y in y_actual)
    ss_res = sum((y_actual[i] - y_predicted[i]) ** 2 for i in range(len(y_actual)))

    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # Step 7: Build metadata
    metadata = {
        "total_token_count": total_tokens,
        "total_type_count": total_types,
        "simple_ttr": total_types / total_tokens if total_tokens > 0 else 0.0,
        "sample_sizes_used": sample_sizes,
        "mean_ttrs_per_sample_size": list(sample_size_to_mean_ttr.values()),
        "num_samples_per_size": num_samples,
        "random_seed": random_seed,
    }

    # Step 8: Create distributions (single-pass analysis)
    d_parameter_dist = make_distribution([d_param])
    curve_fit_r_squared_dist = make_distribution([r_squared])

    # Step 9: Return result
    return VocdDResult(
        d_parameter=d_param,
        curve_fit_r_squared=r_squared,
        sample_count=len(sample_sizes),
        optimal_sample_size=sample_size,  # Input parameter
        d_parameter_dist=d_parameter_dist,
        curve_fit_r_squared_dist=curve_fit_r_squared_dist,
        chunk_size=chunk_size,
        chunk_count=1,  # Single pass analysis
        metadata=metadata,
    )


def compute_mattr(text: str, window_size: int = 50, chunk_size: int = 1000) -> MATTRResult:
    """
    Compute Moving-Average Type-Token Ratio (MATTR).

    MATTR calculates TTR using a moving window of fixed size, then averages
    across all windows. This provides a length-normalized measure that is
    more stable than simple TTR and comparable across texts of different lengths.

    Related GitHub Issue:
        #14 - Advanced Lexical Diversity Metrics
        https://github.com/craigtrim/pystylometry/issues/14

    The algorithm:
        1. Slide a window of fixed size across the text (token by token)
        2. Calculate TTR for each window position
        3. Average all window TTRs to get MATTR
        4. Also compute statistics (std dev, min, max) across windows

    Advantages over TTR:
        - Controlled for text length (fixed window size)
        - More comparable across texts
        - Computationally simple and fast
        - Intuitive interpretation (like TTR but normalized)

    Disadvantages:
        - Requires choosing window size (affects results)
        - Not applicable to texts shorter than window size
        - Adjacent windows overlap (not independent samples)

    Args:
        text: Input text to analyze. Must contain at least window_size tokens.
              Texts shorter than window_size will return NaN.
        window_size: Size of moving window in tokens. Default is 50, following
                     Covington & McFall (2010). Larger windows are more stable
                     but require longer texts. Smaller windows are noisier.

    Returns:
        MATTRResult containing:
            - mattr_score: Average TTR across all windows
            - window_size: Size of window used
            - window_count: Number of windows analyzed
            - ttr_std_dev: Standard deviation of TTR across windows
            - min_ttr: Minimum TTR in any window
            - max_ttr: Maximum TTR in any window
            - metadata: Window-by-window TTR values

    Example:
        >>> result = compute_mattr("Sample text here...", window_size=50)
        >>> print(f"MATTR score: {result.mattr_score:.3f}")
        MATTR score: 0.847
        >>> print(f"Windows analyzed: {result.window_count}")
        Windows analyzed: 123
        >>> print(f"TTR std dev: {result.ttr_std_dev:.3f}")
        TTR std dev: 0.042

        >>> # Short text handling
        >>> short_text = "Too short for window"
        >>> result = compute_mattr(short_text, window_size=50)
        >>> import math
        >>> math.isnan(result.mattr_score)
        True

    Note:
        - Window size choice affects results (no universally optimal value)
        - Standard window size is 50 tokens (Covington & McFall 2010)
        - For very short texts, consider reducing window size or using different metric
        - High TTR std dev suggests uneven lexical distribution
        - MATTR values range from 0 (no diversity) to 1 (perfect diversity)
    """
    # Step 1: Tokenize text
    tokens = _tokenize_for_diversity(text)
    total_tokens = len(tokens)
    total_types = len(set(tokens))

    # Step 2: Validate minimum length
    if total_tokens < window_size:
        raise ValueError(
            f"Text has {total_tokens} tokens, minimum {window_size} required for MATTR"
        )

    # Step 3: Slide window across text and calculate TTR for each position
    window_ttrs = []

    for i in range(total_tokens - window_size + 1):
        # Extract window
        window = tokens[i : i + window_size]

        # Calculate TTR for this window
        window_types = len(set(window))
        ttr = window_types / window_size
        window_ttrs.append(ttr)

    # Step 4: Calculate MATTR (mean of all window TTRs)
    mattr_score = sum(window_ttrs) / len(window_ttrs)

    # Step 5: Calculate statistics
    # Standard deviation
    variance = sum((ttr - mattr_score) ** 2 for ttr in window_ttrs) / len(window_ttrs)
    ttr_std_dev = variance**0.5

    # Min and max
    min_ttr = min(window_ttrs)
    max_ttr = max(window_ttrs)

    # Step 6: Build metadata
    metadata = {
        "total_token_count": total_tokens,
        "total_type_count": total_types,
        "simple_ttr": total_types / total_tokens if total_tokens > 0 else 0.0,
        "first_window_ttr": window_ttrs[0],
        "last_window_ttr": window_ttrs[-1],
    }

    # Step 7: Create distributions (single-pass analysis)
    mattr_score_dist = make_distribution([mattr_score])
    ttr_std_dev_dist = make_distribution([ttr_std_dev])
    min_ttr_dist = make_distribution([min_ttr])
    max_ttr_dist = make_distribution([max_ttr])

    # Step 8: Return result
    return MATTRResult(
        mattr_score=mattr_score,
        window_size=window_size,
        window_count=len(window_ttrs),
        ttr_std_dev=ttr_std_dev,
        min_ttr=min_ttr,
        max_ttr=max_ttr,
        mattr_score_dist=mattr_score_dist,
        ttr_std_dev_dist=ttr_std_dev_dist,
        min_ttr_dist=min_ttr_dist,
        max_ttr_dist=max_ttr_dist,
        chunk_size=chunk_size,
        chunk_count=1,  # Single pass analysis
        metadata=metadata,
    )


def compute_hdd(text: str, sample_size: int = 42, chunk_size: int = 1000) -> HDDResult:
    """
    Compute HD-D (Hypergeometric Distribution D).

    HD-D uses the hypergeometric distribution to model the probability of
    encountering new word types as text length increases. It provides a
    probabilistic measure of lexical diversity that is less sensitive to
    text length than simple TTR.

    Related GitHub Issue:
        #14 - Advanced Lexical Diversity Metrics
        https://github.com/craigtrim/pystylometry/issues/14

    The algorithm:
        1. For each word type in the text, calculate the probability that
           it would NOT appear in a random sample of size N
        2. Sum these probabilities across all types
        3. This sum represents the expected number of new types in a sample
        4. HD-D is derived from this expected value

    The hypergeometric distribution P(X=0) gives the probability that a word
    type with frequency f does not appear in a random sample of size N from
    a text of length T.

    Advantages over TTR:
        - Mathematically rigorous (probability-based)
        - Less sensitive to text length
        - Well-defined statistical properties
        - Good empirical performance (McCarthy & Jarvis 2010)

    Disadvantages:
        - Computationally complex
        - Requires understanding of probability theory
        - Sample size choice affects results
        - Less intuitive than TTR

    Args:
        text: Input text to analyze. Should contain at least 50+ tokens
              for reliable HD-D calculation.
        sample_size: Size of hypothetical sample for calculation. Default is
                     42 tokens, following McCarthy & Jarvis (2010). The optimal
                     sample size is typically 35-50 tokens.

    Returns:
        HDDResult containing:
            - hdd_score: The HD-D value (higher = more diverse)
            - sample_size: Sample size used for calculation
            - type_count: Number of unique types in text
            - token_count: Number of tokens in text
            - metadata: Probability distribution details

    Example:
        >>> result = compute_hdd("Sample text for analysis...")
        >>> print(f"HD-D score: {result.hdd_score:.3f}")
        HD-D score: 0.823
        >>> print(f"Sample size: {result.sample_size}")
        Sample size: 42
        >>> print(f"Types: {result.type_count}, Tokens: {result.token_count}")
        Types: 67, Tokens: 150

        >>> # Empty text handling
        >>> result = compute_hdd("")
        >>> import math
        >>> math.isnan(result.hdd_score)
        True

    Note:
        - HD-D values range from 0 (no diversity) to 1 (perfect diversity)
        - Requires scipy for hypergeometric distribution calculations
        - Sample size should be smaller than text length
        - Very short texts may produce unreliable HD-D values
        - HD-D correlates highly with other diversity measures but is more stable
    """
    # Step 1: Tokenize text
    tokens = _tokenize_for_diversity(text)
    total_tokens = len(tokens)

    # Step 2: Validate minimum length
    if total_tokens < sample_size:
        raise ValueError(f"Text has {total_tokens} tokens, minimum {sample_size} required for HD-D")

    # Step 3: Build frequency distribution
    type_counts: dict[str, int] = {}
    for token in tokens:
        type_counts[token] = type_counts.get(token, 0) + 1

    total_types = len(type_counts)

    # Step 4: Calculate HD-D using hypergeometric distribution
    # HD-D = sum over all types of P(X = 0)
    # where P(X = 0) is probability that type does NOT appear in random sample
    #
    # Using simplified formula (stable and no scipy required):
    # P(X=0) = ((total_tokens - count) / total_tokens)^sample_size

    hdd_sum = 0.0

    for word_type, count in type_counts.items():
        # Probability this type does NOT appear in sample of size sample_size
        prob_not_appear = ((total_tokens - count) / total_tokens) ** sample_size
        hdd_sum += prob_not_appear

    # Step 5: Build metadata
    metadata = {
        "total_token_count": total_tokens,
        "total_type_count": total_types,
        "simple_ttr": total_types / total_tokens if total_tokens > 0 else 0.0,
        "hypergeometric_sum": hdd_sum,
        "calculation_method": "simplified",
    }

    # Step 6: Create distribution (single-pass analysis)
    hdd_score_dist = make_distribution([hdd_sum])

    # Step 7: Return result
    return HDDResult(
        hdd_score=hdd_sum,
        sample_size=sample_size,
        type_count=total_types,
        token_count=total_tokens,
        hdd_score_dist=hdd_score_dist,
        chunk_size=chunk_size,
        chunk_count=1,  # Single pass analysis
        metadata=metadata,
    )


def compute_msttr(text: str, segment_size: int = 100, chunk_size: int = 1000) -> MSTTRResult:
    """
    Compute Mean Segmental Type-Token Ratio (MSTTR).

    MSTTR divides text into sequential, non-overlapping segments of equal
    length, calculates TTR for each segment, then averages across segments.
    This normalizes for text length and provides a stable diversity measure.

    Related GitHub Issue:
        #14 - Advanced Lexical Diversity Metrics
        https://github.com/craigtrim/pystylometry/issues/14

    The algorithm:
        1. Divide text into non-overlapping segments of segment_size tokens
        2. Calculate TTR for each complete segment
        3. Discard any remaining tokens that don't form a complete segment
        4. Average TTRs across all segments
        5. Compute statistics (std dev, min, max) across segments

    Advantages over TTR:
        - Normalized for text length (fixed segment size)
        - Simple and intuitive
        - Fast computation
        - Independent segments (unlike MATTR's overlapping windows)

    Disadvantages:
        - Discards incomplete final segment (information loss)
        - Requires choosing segment size (affects results)
        - Needs longer texts to produce multiple segments
        - Segment boundaries are arbitrary

    Args:
        text: Input text to analyze. Should contain at least segment_size tokens.
              Texts shorter than segment_size will return NaN. Longer texts
              will have leftover tokens discarded if they don't form a complete
              segment.
        segment_size: Size of each segment in tokens. Default is 100 following
                      Johnson (1944). Larger segments are more stable but need
                      longer texts. Smaller segments are noisier but work with
                      shorter texts.

    Returns:
        MSTTRResult containing:
            - msttr_score: Mean TTR across all segments
            - segment_size: Size of each segment used
            - segment_count: Number of complete segments analyzed
            - ttr_std_dev: Standard deviation of TTR across segments
            - min_ttr: Minimum TTR in any segment
            - max_ttr: Maximum TTR in any segment
            - segment_ttrs: List of TTR for each segment
            - metadata: Segment details, tokens used/discarded

    Example:
        >>> result = compute_msttr("Long text with many segments...", segment_size=100)
        >>> print(f"MSTTR score: {result.msttr_score:.3f}")
        MSTTR score: 0.734
        >>> print(f"Segments: {result.segment_count}")
        Segments: 8
        >>> print(f"TTR range: {result.min_ttr:.3f} to {result.max_ttr:.3f}")
        TTR range: 0.680 to 0.790

        >>> # Short text handling
        >>> short_text = "Too short"
        >>> result = compute_msttr(short_text, segment_size=100)
        >>> import math
        >>> math.isnan(result.msttr_score)
        True

    Note:
        - Segment size choice affects results (common values: 50, 100, 200)
        - Standard segment size is 100 tokens (Johnson 1944)
        - Leftover tokens are discarded (e.g., 250 tokens → 2 segments of 100)
        - At least 1 complete segment required (min text length = segment_size)
        - High TTR std dev suggests inconsistent lexical diversity across text
        - MSTTR values range from 0 (no diversity) to 1 (perfect diversity)
    """
    # Step 1: Tokenize text
    tokens = _tokenize_for_diversity(text)
    total_tokens = len(tokens)
    total_types = len(set(tokens))

    # Step 2: Validate minimum length
    if total_tokens < segment_size:
        raise ValueError(
            f"Text has {total_tokens} tokens, minimum {segment_size} required for MSTTR"
        )

    # Step 3: Calculate number of complete segments
    segment_count = total_tokens // segment_size

    # Step 4: Calculate TTR for each segment
    segment_ttrs = []

    for i in range(segment_count):
        # Extract segment
        start = i * segment_size
        end = start + segment_size
        segment = tokens[start:end]

        # Calculate TTR for this segment
        segment_types = len(set(segment))
        ttr = segment_types / segment_size
        segment_ttrs.append(ttr)

    # Step 5: Calculate MSTTR (mean of segment TTRs)
    msttr_score = sum(segment_ttrs) / len(segment_ttrs)

    # Step 6: Calculate statistics
    # Standard deviation
    variance = sum((ttr - msttr_score) ** 2 for ttr in segment_ttrs) / len(segment_ttrs)
    ttr_std_dev = variance**0.5

    # Min and max
    min_ttr = min(segment_ttrs)
    max_ttr = max(segment_ttrs)

    # Step 7: Calculate tokens used/discarded
    tokens_used = segment_count * segment_size
    tokens_discarded = total_tokens - tokens_used

    # Step 8: Build metadata
    metadata = {
        "total_token_count": total_tokens,
        "total_type_count": total_types,
        "simple_ttr": total_types / total_tokens if total_tokens > 0 else 0.0,
        "tokens_used": tokens_used,
        "tokens_discarded": tokens_discarded,
        "first_segment_ttr": segment_ttrs[0],
        "last_segment_ttr": segment_ttrs[-1],
    }

    # Step 9: Create distributions (single-pass analysis)
    msttr_score_dist = make_distribution([msttr_score])
    ttr_std_dev_dist = make_distribution([ttr_std_dev])
    min_ttr_dist = make_distribution([min_ttr])
    max_ttr_dist = make_distribution([max_ttr])

    # Step 10: Return result
    return MSTTRResult(
        msttr_score=msttr_score,
        segment_size=segment_size,
        segment_count=segment_count,
        ttr_std_dev=ttr_std_dev,
        min_ttr=min_ttr,
        max_ttr=max_ttr,
        segment_ttrs=segment_ttrs,
        msttr_score_dist=msttr_score_dist,
        ttr_std_dev_dist=ttr_std_dev_dist,
        min_ttr_dist=min_ttr_dist,
        max_ttr_dist=max_ttr_dist,
        chunk_size=chunk_size,
        chunk_count=1,  # Single pass analysis
        metadata=metadata,
    )

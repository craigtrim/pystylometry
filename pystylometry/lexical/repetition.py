"""Repetitive word and n-gram detection for verbal tics / slop analysis.

This module detects abnormally repetitive words and phrases in text — a common
pattern in AI-generated content ("slop") where certain content words and phrases
appear far more frequently than expected.

Generative models exhibit "verbal tics": they repeatedly use certain words and
phrases throughout generated text. Examples include "shimmered", "flickered",
"obsidian", "a testament to", "an uncomfortable truth". These patterns differ
from natural human writing where content words appear when contextually relevant,
repetition clusters around specific scenes or topics, and unusual words don't
appear with suspiciously even distribution.

Two functions are provided:

    compute_repetitive_unigrams:
        Compares observed word frequencies against the British National Corpus
        (BNC, ~100M tokens) baseline. Words that appear far more than their
        BNC relative frequency predicts are flagged.

    compute_repetitive_ngrams:
        Detects content n-grams (bigrams, trigrams, etc.) that repeat more
        than expected. No external corpus is required — content n-grams should
        not repeat verbatim often in natural writing.

Both functions support chunked analysis to reveal distribution patterns:
    - Even distribution across text = suspicious (model's consistent tic)
    - Clustered distribution = likely intentional (human describing a scene)

Related GitHub Issue:
    #28 - Verbal tics detection for slop analysis
    https://github.com/craigtrim/pystylometry/issues/28

Dependencies:
    - bnc-lookup >= 1.3.0 (optional, in lexical group)
      Provides expected_count() and bucket() for BNC baseline comparison.

References:
    British National Corpus Consortium. (2007). The British National Corpus,
        version 3 (BNC XML Edition). http://www.natcorp.ox.ac.uk/
    Kilgarriff, A. (2001). BNC database and word frequency lists.
        https://www.kilgarriff.co.uk/bnc-readme.html
"""

from __future__ import annotations

import math
import statistics
from collections import Counter

from .._types import (
    Distribution,
    RepetitiveNgram,
    RepetitiveNgramsResult,
    RepetitiveUnigramsResult,
    RepetitiveWord,
    chunk_text,
    make_distribution,
)
from .._utils import check_optional_dependency, tokenize
from .function_words import (
    AUXILIARIES,
    CONJUNCTIONS,
    DETERMINERS,
    PARTICLES,
    PREPOSITIONS,
    PRONOUNS,
)

# Union of all function word sets — used to filter out non-content words
_FUNCTION_WORDS = DETERMINERS | PREPOSITIONS | CONJUNCTIONS | PRONOUNS | AUXILIARIES | PARTICLES


def _chunk_entropy(chunk_counts: list[int]) -> float:
    """Compute Shannon entropy of a word's distribution across chunks.

    Entropy measures how evenly a word is distributed across chunks.
    Low entropy means the word appears evenly (suspicious for rare words).
    High entropy means the word is concentrated in specific chunks (natural).

    Formula:
        H = -sum(p_i * log2(p_i)) for each chunk i where p_i > 0
        p_i = count_in_chunk_i / total_count

    Args:
        chunk_counts: Per-chunk occurrence counts.

    Returns:
        Shannon entropy in bits. 0.0 if the word appears in only one chunk.
        Returns 0.0 for empty or all-zero counts.
    """
    total = sum(chunk_counts)
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in chunk_counts:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


def _tokenize_content_words(text: str) -> list[str]:
    """Tokenize text and return only lowercase alphabetic content words.

    Filters out:
        - Non-alphabetic tokens (punctuation, numbers)
        - Function words (determiners, prepositions, conjunctions,
          pronouns, auxiliaries, particles)

    Args:
        text: Input text.

    Returns:
        List of lowercase content word tokens.
    """
    tokens = tokenize(text.lower())
    return [t for t in tokens if t.isalpha() and t not in _FUNCTION_WORDS]


def compute_repetitive_unigrams(
    text: str,
    threshold: float = 3.0,
    chunk_size: int = 1000,
    min_count: int = 3,
) -> RepetitiveUnigramsResult:
    """Detect content words that repeat far more than expected based on BNC frequencies.

    For each content word in the text, computes:
        expected_count = BNC_relative_frequency(word) * text_length
        repetition_score = observed_count / expected_count

    Words exceeding the threshold score and minimum count are flagged.

    This function uses native chunked analysis to capture distribution patterns
    across the text. Words that are evenly distributed (low entropy) are more
    suspicious than words clustered in specific sections.

    Related GitHub Issue:
        #28 - Verbal tics detection for slop analysis
        https://github.com/craigtrim/pystylometry/issues/28

    References:
        British National Corpus Consortium. (2007). The British National Corpus,
            version 3 (BNC XML Edition). http://www.natcorp.ox.ac.uk/

    Args:
        text: Input text to analyze.
        threshold: Minimum repetition_score (observed/expected) to flag a word.
            Default 3.0 means the word must appear at least 3x more than expected.
        chunk_size: Number of words per chunk for distribution analysis (default: 1000).
        min_count: Minimum observed count to flag a word. Prevents flagging words
            that appear only once or twice, which aren't meaningfully repetitive
            regardless of their score. Default: 3.
    Returns:
        RepetitiveUnigramsResult with flagged words, aggregate scores, and metadata.

    Example:
        >>> result = compute_repetitive_unigrams(novel_text)
        >>> for w in result.repetitive_words[:5]:
        ...     print(f"{w.word}: {w.count}x (expected {w.expected_count:.1f}, "
        ...           f"score {w.repetition_score:.1f})")
        shimmered: 23x (expected 0.1, score 266.2)
        obsidian: 18x (expected 0.0, score 450.0)
        >>> print(f"Slop score: {result.slop_score:.1f}")
        Slop score: 42.7
    """
    check_optional_dependency("bnc_lookup", "lexical")

    from bnc_lookup import bucket as bnc_bucket  # type: ignore[import-untyped]
    from bnc_lookup import expected_count as bnc_expected_count  # type: ignore[import-untyped]

    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Tokenize each chunk into content words
    chunk_tokens: list[list[str]] = [_tokenize_content_words(chunk) for chunk in chunks]

    # Count content words per chunk
    chunk_counters: list[Counter[str]] = [Counter(tokens) for tokens in chunk_tokens]
    content_words_per_chunk = [len(tokens) for tokens in chunk_tokens]

    # Build global content word counts
    global_counter: Counter[str] = Counter()
    for counter in chunk_counters:
        global_counter.update(counter)

    total_content_words = sum(global_counter.values())

    # Handle empty text
    if total_content_words == 0:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return RepetitiveUnigramsResult(
            repetitive_words=[],
            total_content_words=0,
            flagged_count=0,
            flagged_words_per_10k=0.0,
            mean_repetition_score=0.0,
            slop_score=0.0,
            total_content_words_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={"threshold": threshold, "min_count": min_count},
        )

    # Evaluate each content word against BNC baseline
    flagged: list[RepetitiveWord] = []

    for word, observed in global_counter.items():
        if observed < min_count:
            continue

        # Get BNC expected count for this word given our text length
        expected = bnc_expected_count(word, total_content_words)
        word_bucket = bnc_bucket(word)

        if expected is None or expected == 0.0:
            # Word not in BNC or has zero expected frequency
            # Any repeated occurrence is notable
            score = float("inf")
            expected_val = 0.0
        else:
            expected_val = expected
            score = observed / expected_val

        if score >= threshold:
            # Build per-chunk counts for this word
            per_chunk = [counter.get(word, 0) for counter in chunk_counters]
            entropy = _chunk_entropy(per_chunk)
            variance = statistics.variance(per_chunk) if len(per_chunk) > 1 else 0.0

            flagged.append(
                RepetitiveWord(
                    word=word,
                    count=observed,
                    expected_count=expected_val,
                    repetition_score=score,
                    bnc_bucket=word_bucket,
                    chunk_counts=per_chunk,
                    distribution_entropy=entropy,
                    distribution_variance=variance,
                )
            )

    # Sort by repetition_score descending (inf sorts last with key trick)
    flagged.sort(
        key=lambda w: (
            -w.repetition_score if w.repetition_score != float("inf") else -1e18,
            -w.count,
        )
    )

    # Compute aggregate metrics
    flagged_count = len(flagged)
    flagged_words_per_10k = (
        flagged_count / (total_content_words / 10_000) if total_content_words > 0 else 0.0
    )

    # Mean repetition score (exclude inf for meaningful average)
    finite_scores = [w.repetition_score for w in flagged if w.repetition_score != float("inf")]
    mean_rep_score = statistics.mean(finite_scores) if finite_scores else 0.0

    slop_score = flagged_words_per_10k * mean_rep_score

    # Content words distribution
    content_dist = (
        make_distribution([float(c) for c in content_words_per_chunk])
        if content_words_per_chunk
        else Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
    )

    return RepetitiveUnigramsResult(
        repetitive_words=flagged,
        total_content_words=total_content_words,
        flagged_count=flagged_count,
        flagged_words_per_10k=flagged_words_per_10k,
        mean_repetition_score=mean_rep_score,
        slop_score=slop_score,
        total_content_words_dist=content_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "threshold": threshold,
            "min_count": min_count,
            "total_unique_content_words": len(global_counter),
            "inf_score_count": sum(1 for w in flagged if w.repetition_score == float("inf")),
        },
    )


def _validate_n(n: int | tuple[int, ...]) -> tuple[int, ...]:
    """Validate and normalize the n-gram order parameter.

    Args:
        n: Single integer or tuple of integers specifying n-gram orders.

    Returns:
        Sorted tuple of unique valid n-gram orders.

    Raises:
        ValueError: If any value is outside the range [2, 5] or input is empty.
    """
    values: tuple[int, ...]
    if isinstance(n, int):
        values = (n,)
    else:
        values = tuple(sorted(set(n)))

    if not values:
        raise ValueError("n must specify at least one n-gram order.")

    for v in values:
        if v < 2:
            raise ValueError(
                f"n-gram order {v} is too small. Minimum is 2 (bigrams). "
                f"For single-word repetition, use compute_repetitive_unigrams() instead."
            )
        if v > 5:
            raise ValueError(
                f"n-gram order {v} is too large. Maximum is 5. "
                f"N-grams of order 6+ are too sparse to produce meaningful repetition "
                f"signals in typical texts (they rarely repeat even once)."
            )

    return values


def _is_content_ngram(ngram: tuple[str, ...]) -> bool:
    """Check if an n-gram contains at least one content word.

    An n-gram composed entirely of function words (e.g., "of the", "in a")
    is expected to repeat and should not be flagged.

    Args:
        ngram: Tuple of words.

    Returns:
        True if at least one word is not a function word.
    """
    return any(word not in _FUNCTION_WORDS for word in ngram)


def compute_repetitive_ngrams(
    text: str,
    n: int | tuple[int, ...] = (2, 3),
    chunk_size: int = 1000,
    min_count: int = 3,
) -> RepetitiveNgramsResult:
    """Detect content n-grams that repeat more than expected within the text.

    Content n-grams (bigrams, trigrams, etc.) should rarely repeat verbatim in
    natural writing. This function flags n-grams that exceed a length-scaled
    threshold, filtering out n-grams composed entirely of function words.

    No external corpus is required — the threshold is computed internally based
    on text length. Any content n-gram appearing more than
    max(min_count, total_ngrams / 10000) times is flagged.

    Related GitHub Issue:
        #28 - Verbal tics detection for slop analysis
        https://github.com/craigtrim/pystylometry/issues/28

    Args:
        text: Input text to analyze.
        n: N-gram order(s) to analyze. Can be a single integer (e.g., 2 for
            bigrams) or a tuple of integers (e.g., (2, 3) for bigrams and
            trigrams). Valid range: 2 to 5. Default: (2, 3).
            - Values below 2 are rejected (use compute_repetitive_unigrams
              for single words).
            - Values above 5 are rejected (n-grams of order 6+ are too sparse
              to produce meaningful repetition signals).
        chunk_size: Number of words per chunk for distribution analysis (default: 1000).
        min_count: Minimum count to flag an n-gram. Default: 3.

    Returns:
        RepetitiveNgramsResult with flagged n-grams, counts, and metadata.

    Example:
        >>> result = compute_repetitive_ngrams(text, n=2)
        >>> for ng in result.repetitive_ngrams[:5]:
        ...     print(f"{' '.join(ng.ngram)}: {ng.count}x")
        uncomfortable truth: 8x
        >>> result = compute_repetitive_ngrams(text, n=(2, 3, 4))
        >>> print(f"Flagged: {result.flagged_count} n-grams")
    """
    # Validate n parameter
    n_values = _validate_n(n)

    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Tokenize each chunk — lowercase alpha only (but keep function words
    # so n-grams spanning content+function words are preserved; we filter
    # all-function-word n-grams separately)
    chunk_tokens: list[list[str]] = []
    for chunk in chunks:
        tokens = tokenize(chunk.lower())
        chunk_tokens.append([t for t in tokens if t.isalpha()])

    # Build n-grams per chunk for each requested order
    # chunk_ngram_counters[chunk_idx] aggregates across all n values
    chunk_ngram_counters: list[Counter[tuple[str, ...]]] = [Counter() for _ in chunks]
    total_ngram_count = 0

    for chunk_idx, tokens in enumerate(chunk_tokens):
        for nv in n_values:
            for i in range(len(tokens) - nv + 1):
                ngram = tuple(tokens[i : i + nv])
                if _is_content_ngram(ngram):
                    chunk_ngram_counters[chunk_idx][ngram] += 1
                    total_ngram_count += 1

    # Build global counts
    global_ngram_counter: Counter[tuple[str, ...]] = Counter()
    for counter in chunk_ngram_counters:
        global_ngram_counter.update(counter)

    # Determine threshold: any content n-gram appearing more than this is flagged
    length_threshold = max(min_count, total_ngram_count // 10_000)

    # Handle empty text
    if total_ngram_count == 0:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return RepetitiveNgramsResult(
            repetitive_ngrams=[],
            n=n,
            total_ngrams=0,
            flagged_count=0,
            flagged_per_10k=0.0,
            total_ngrams_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={"min_count": min_count, "effective_threshold": length_threshold},
        )

    # Flag n-grams exceeding threshold
    flagged: list[RepetitiveNgram] = []

    for ngram, count in global_ngram_counter.items():
        if count >= length_threshold:
            per_chunk = [counter.get(ngram, 0) for counter in chunk_ngram_counters]
            entropy = _chunk_entropy(per_chunk)
            variance = statistics.variance(per_chunk) if len(per_chunk) > 1 else 0.0
            freq_per_10k = count / (total_ngram_count / 10_000) if total_ngram_count > 0 else 0.0

            flagged.append(
                RepetitiveNgram(
                    ngram=ngram,
                    count=count,
                    frequency_per_10k=freq_per_10k,
                    chunk_counts=per_chunk,
                    distribution_entropy=entropy,
                    distribution_variance=variance,
                )
            )

    # Sort by count descending
    flagged.sort(key=lambda ng: -ng.count)

    flagged_count = len(flagged)
    flagged_per_10k = flagged_count / (total_ngram_count / 10_000) if total_ngram_count > 0 else 0.0

    # N-grams per chunk distribution
    ngrams_per_chunk = [sum(counter.values()) for counter in chunk_ngram_counters]
    ngrams_dist = (
        make_distribution([float(c) for c in ngrams_per_chunk])
        if ngrams_per_chunk
        else Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
    )

    return RepetitiveNgramsResult(
        repetitive_ngrams=flagged,
        n=n,
        total_ngrams=total_ngram_count,
        flagged_count=flagged_count,
        flagged_per_10k=flagged_per_10k,
        total_ngrams_dist=ngrams_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "min_count": min_count,
            "effective_threshold": length_threshold,
            "n_values": list(n_values),
            "total_unique_ngrams": len(global_ngram_counter),
        },
    )

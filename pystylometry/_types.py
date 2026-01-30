"""Result dataclasses for all pystylometry metrics.

This module defines dataclasses for all metric results in pystylometry.

Native Chunked Analysis (Issue #27):
    All metrics support chunked analysis by default. Results include:
    - Convenient access to the mean value (e.g., result.reading_ease)
    - Full distribution with per-chunk values and statistics (e.g., result.reading_ease_dist)

    The Distribution dataclass provides:
    - values: list of per-chunk metric values
    - mean, median, std: central tendency and variability
    - range, iqr: spread measures

    This design captures the variance and rhythm in writing style, which is
    essential for authorship attribution and linguistic fingerprinting.

References:
    STTR methodology: Johnson, W. (1944). Studies in language behavior.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any, Optional

# ===== Distribution and Chunking =====
# Related to GitHub Issue #27: Native chunked analysis with Distribution dataclass
# https://github.com/craigtrim/pystylometry/issues/27


@dataclass
class Distribution:
    """Distribution of metric values across chunks.

    This dataclass captures the variance and rhythm in writing style by storing
    per-chunk values along with descriptive statistics. The variance across chunks
    is often more revealing of authorial fingerprint than aggregate values.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Attributes:
        values: Raw per-chunk metric values
        mean: Arithmetic mean of values
        median: Middle value when sorted
        std: Standard deviation (0.0 for single-chunk)
        range: max - min (spread measure)
        iqr: Interquartile range (Q3 - Q1), robust spread measure

    Note:
        min/max are omitted as trivial operations on values:
        - min(dist.values), max(dist.values)

    Example:
        >>> dist = Distribution(
        ...     values=[65.2, 71.1, 68.8, 70.5],
        ...     mean=68.9, median=69.65, std=2.57,
        ...     range=5.9, iqr=3.15
        ... )
        >>> dist.std  # variance reveals authorial fingerprint
        2.57
    """

    values: list[float]
    mean: float
    median: float
    std: float
    range: float
    iqr: float


def chunk_text(text: str, chunk_size: int) -> list[str]:
    """Split text into word-based chunks of approximately equal size.

    Chunks are created by splitting on whitespace and grouping words.
    The last chunk may be smaller than chunk_size if the text doesn't
    divide evenly.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Args:
        text: The text to chunk
        chunk_size: Target number of words per chunk (default: 1000)

    Returns:
        List of text chunks. For text smaller than chunk_size,
        returns a single-element list with the entire text.

    Example:
        >>> chunks = chunk_text("word " * 2500, chunk_size=1000)
        >>> len(chunks)
        3
        >>> # First two chunks have ~1000 words, last has ~500
    """
    words = text.split()
    if not words:
        return [""]

    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_words))

    return chunks


def make_distribution(values: list[float]) -> Distribution:
    """Create a Distribution from a list of values.

    Computes all descriptive statistics for the distribution.
    Handles single-value lists by setting std, range, and iqr to 0.0.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Args:
        values: List of numeric values (must be non-empty)

    Returns:
        Distribution with computed statistics

    Raises:
        ValueError: If values is empty

    Example:
        >>> dist = make_distribution([65.2, 71.1, 68.8, 70.5])
        >>> dist.mean
        68.9
        >>> dist.std  # reveals variance in the signal
        2.57...
    """
    if not values:
        raise ValueError("Cannot create distribution from empty values")

    if len(values) == 1:
        return Distribution(
            values=values,
            mean=values[0],
            median=values[0],
            std=0.0,
            range=0.0,
            iqr=0.0,
        )

    # For 2-3 values, quantiles() needs special handling
    if len(values) < 4:
        q1 = values[0]
        q3 = values[-1]
    else:
        q = statistics.quantiles(values, n=4)
        q1, q3 = q[0], q[2]

    return Distribution(
        values=values,
        mean=statistics.mean(values),
        median=statistics.median(values),
        std=statistics.stdev(values),
        range=max(values) - min(values),
        iqr=q3 - q1,
    )


# ===== Lexical Results =====


@dataclass
class MTLDResult:
    """Result from MTLD (Measure of Textual Lexical Diversity) computation.

    All numeric metrics include both a mean value (convenient access) and
    a full distribution with per-chunk values and statistics.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Example:
        >>> result = compute_mtld(text, chunk_size=1000)
        >>> result.mtld_average  # mean MTLD across chunks
        72.5
        >>> result.mtld_average_dist.std  # MTLD variance
        8.3
    """

    # Convenient access (mean values)
    mtld_forward: float
    mtld_backward: float
    mtld_average: float

    # Full distributions
    mtld_forward_dist: Distribution
    mtld_backward_dist: Distribution
    mtld_average_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class YuleResult:
    """Result from Yule's K and I computation.

    All numeric metrics include both a mean value (convenient access) and
    a full distribution with per-chunk values and statistics.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Example:
        >>> result = compute_yule(text, chunk_size=1000)
        >>> result.yule_k  # mean across chunks
        120.5
        >>> result.yule_k_dist.std  # variance reveals fingerprint
        15.2
    """

    # Convenient access (mean values)
    yule_k: float
    yule_i: float

    # Full distributions
    yule_k_dist: Distribution
    yule_i_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class HapaxResult:
    """Result from Hapax Legomena analysis.

    All numeric metrics include both a mean value (convenient access) and
    a full distribution with per-chunk values and statistics.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Example:
        >>> result = compute_hapax(text, chunk_size=1000)
        >>> result.hapax_ratio  # mean across chunks
        0.45
        >>> result.hapax_ratio_dist.std  # variance
        0.08
    """

    # Convenient access (mean/total values)
    hapax_count: int  # Total across all chunks
    hapax_ratio: float  # Mean ratio
    dis_hapax_count: int  # Total across all chunks
    dis_hapax_ratio: float  # Mean ratio
    sichel_s: float  # Mean
    honore_r: float  # Mean

    # Full distributions (ratios only - counts don't distribute meaningfully)
    hapax_ratio_dist: Distribution
    dis_hapax_ratio_dist: Distribution
    sichel_s_dist: Distribution
    honore_r_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class LexiconCategories:
    """Categorization of words by lexicon presence."""

    neologisms: list[str]  # Not in WordNet AND not in BNC
    rare_words: list[str]  # In one lexicon but not both
    common_words: list[str]  # In both WordNet AND BNC
    neologism_ratio: float  # Ratio of neologisms to total hapax
    rare_word_ratio: float  # Ratio of rare words to total hapax
    metadata: dict[str, Any]


@dataclass
class HapaxLexiconResult:
    """Result from Hapax Legomena analysis with lexicon categorization.

    Extends basic hapax analysis by categorizing hapax legomena based on
    presence in WordNet and British National Corpus (BNC):

    - Neologisms: Words not in WordNet AND not in BNC (true novel words)
    - Rare words: Words in BNC but not WordNet, or vice versa
    - Common words: Words in both lexicons (just happen to appear once in text)

    This categorization is valuable for stylometric analysis as it distinguishes
    between vocabulary innovation (neologisms) and incidental hapax occurrence
    (common words that appear once).
    """

    hapax_result: HapaxResult  # Standard hapax metrics
    lexicon_analysis: LexiconCategories  # Lexicon-based categorization
    metadata: dict[str, Any]


@dataclass
class TTRResult:
    """Result from Type-Token Ratio (TTR) analysis.

    Measures vocabulary richness through the ratio of unique words (types)
    to total words (tokens).

    All numeric metrics include both a mean value (convenient access) and
    a full distribution with per-chunk values and statistics.

    Includes multiple TTR variants for length normalization:
    - Raw TTR: Direct ratio of unique to total words
    - Root TTR (Guiraud's index): types / sqrt(tokens)
    - Log TTR (Herdan's C): log(types) / log(tokens)
    - STTR: Standardized TTR across fixed-size chunks
    - Delta Std: Measures vocabulary consistency across chunks

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        Guiraud, P. (1960). Problèmes et méthodes de la statistique linguistique.
        Herdan, G. (1960). Type-token Mathematics.

    Example:
        >>> result = compute_ttr(text, chunk_size=1000)
        >>> result.ttr  # mean TTR across chunks
        0.42
        >>> result.ttr_dist.std  # TTR variance reveals fingerprint
        0.05
        >>> result.chunk_count
        59
    """

    # Convenient access (mean values)
    total_words: int
    unique_words: int
    ttr: float  # Raw TTR (mean)
    root_ttr: float  # Guiraud's index (mean)
    log_ttr: float  # Herdan's C (mean)
    sttr: float  # Standardized TTR (mean)
    delta_std: float  # Vocabulary consistency (mean)

    # Full distributions with per-chunk values
    ttr_dist: Distribution
    root_ttr_dist: Distribution
    log_ttr_dist: Distribution
    sttr_dist: Distribution
    delta_std_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class TTRAggregateResult:
    """Aggregated TTR statistics for a collection of texts.

    Computes group-level summary statistics (mean, std, min, max, median)
    across multiple ``TTRResult`` objects.  Useful for comparative analysis
    across authors, genres, or time periods.

    Related GitHub Issue:
        #43 - Inline stylometry-ttr into pystylometry (remove external dependency)
        https://github.com/craigtrim/pystylometry/issues/43

    Example:
        >>> from pystylometry.lexical import compute_ttr, TTRAggregator
        >>> results = [compute_ttr(t) for t in texts]
        >>> agg = TTRAggregator()
        >>> stats = agg.aggregate(results, group_id="Austen")
        >>> stats.ttr_mean
        0.412
    """

    group_id: str
    text_count: int
    total_words: int

    # Raw TTR statistics
    ttr_mean: float
    ttr_std: float
    ttr_min: float
    ttr_max: float
    ttr_median: float

    # Root TTR (Guiraud's index) statistics
    root_ttr_mean: float
    root_ttr_std: float

    # Log TTR (Herdan's C) statistics
    log_ttr_mean: float
    log_ttr_std: float

    # STTR statistics (None if no texts had enough words for STTR)
    sttr_mean: Optional[float]
    sttr_std: Optional[float]

    # Delta std mean (None if no texts had delta metrics)
    delta_std_mean: Optional[float]

    metadata: dict[str, Any]


# ===== Repetition Detection Results =====
# Related to GitHub Issue #28: Verbal tics detection for slop analysis
# https://github.com/craigtrim/pystylometry/issues/28


@dataclass
class RepetitiveWord:
    """A single word flagged as abnormally repetitive.

    The repetition_score is the ratio of observed count to expected count
    based on the word's frequency in the British National Corpus (BNC).
    Higher scores indicate stronger overrepresentation.

    Related GitHub Issue:
        #28 - Verbal tics detection for slop analysis
        https://github.com/craigtrim/pystylometry/issues/28

    Attributes:
        word: The flagged word (lowercased).
        count: Observed count in the text.
        expected_count: Expected count based on BNC relative frequency × text length.
            0.0 if word not found in BNC.
        repetition_score: count / expected_count. float('inf') if expected_count is 0.
        bnc_bucket: BNC frequency bucket (1-100, 1=most frequent). None if not in BNC.
        chunk_counts: Per-chunk occurrence counts (for distribution analysis).
        distribution_entropy: Shannon entropy of the word's chunk distribution.
            Low entropy = suspiciously even spread (model tic).
            High entropy = clustered usage (human writing about a specific scene).
        distribution_variance: Variance of per-chunk counts.
    """

    word: str
    count: int
    expected_count: float
    repetition_score: float
    bnc_bucket: int | None
    chunk_counts: list[int]
    distribution_entropy: float
    distribution_variance: float


@dataclass
class RepetitiveUnigramsResult:
    """Result from repetitive unigram detection.

    Identifies content words that appear far more frequently than expected
    based on their frequency in the British National Corpus (BNC, ~100M tokens).
    This is a key indicator of AI-generated "slop" where models exhibit verbal
    tics — repeating certain words with suspicious regularity.

    Related GitHub Issue:
        #28 - Verbal tics detection for slop analysis
        https://github.com/craigtrim/pystylometry/issues/28

    The slop_score provides a single aggregate metric:
        slop_score = flagged_words_per_10k × mean_repetition_score

    Where:
        - flagged_words_per_10k = count of flagged words / (total content words / 10000)
        - mean_repetition_score = mean repetition_score across all flagged words

    Higher slop_score = more likely AI-generated verbal tics.

    References:
        British National Corpus Consortium. (2007). The British National Corpus,
            version 3 (BNC XML Edition). http://www.natcorp.ox.ac.uk/

    Example:
        >>> result = compute_repetitive_unigrams(text)
        >>> for w in result.repetitive_words[:5]:
        ...     print(f"{w.word}: {w.count}x (expected {w.expected_count:.1f}, "
        ...           f"score {w.repetition_score:.1f})")
        shimmered: 23x (expected 0.1, score 266.2)
        >>> result.slop_score
        42.7
    """

    repetitive_words: list[RepetitiveWord]  # Sorted by repetition_score descending
    total_content_words: int
    flagged_count: int  # Number of words exceeding threshold
    flagged_words_per_10k: float  # flagged_count / (total_content_words / 10000)
    mean_repetition_score: float  # Mean score across flagged words
    slop_score: float  # Aggregate: flagged_words_per_10k × mean_repetition_score
    total_content_words_dist: Distribution
    chunk_size: int
    chunk_count: int
    metadata: dict[str, Any]


@dataclass
class RepetitiveNgram:
    """A single n-gram flagged as abnormally repetitive.

    Content n-grams (bigrams, trigrams, etc.) should rarely repeat verbatim
    in natural writing. N-grams that repeat beyond a length-scaled threshold
    are flagged.

    Related GitHub Issue:
        #28 - Verbal tics detection for slop analysis
        https://github.com/craigtrim/pystylometry/issues/28

    Attributes:
        ngram: The flagged n-gram as a tuple of words.
        count: Observed count in the text.
        frequency_per_10k: Occurrences per 10,000 n-grams.
        chunk_counts: Per-chunk occurrence counts.
        distribution_entropy: Shannon entropy of the n-gram's chunk distribution.
        distribution_variance: Variance of per-chunk counts.
    """

    ngram: tuple[str, ...]
    count: int
    frequency_per_10k: float
    chunk_counts: list[int]
    distribution_entropy: float
    distribution_variance: float


@dataclass
class RepetitiveNgramsResult:
    """Result from repetitive n-gram detection.

    Detects bigrams, trigrams, or higher-order n-grams that repeat more than
    expected within the text. No external corpus is required — content n-grams
    should not repeat verbatim often in natural writing.

    N-grams composed entirely of function words (e.g., "of the", "in a") are
    excluded since their repetition is expected.

    Related GitHub Issue:
        #28 - Verbal tics detection for slop analysis
        https://github.com/craigtrim/pystylometry/issues/28

    Example:
        >>> result = compute_repetitive_ngrams(text, n=2)
        >>> for ng in result.repetitive_ngrams[:5]:
        ...     print(f"{' '.join(ng.ngram)}: {ng.count}x "
        ...           f"({ng.frequency_per_10k:.1f} per 10k)")
        uncomfortable truth: 8x (1.6 per 10k)
    """

    repetitive_ngrams: list[RepetitiveNgram]  # Sorted by count descending
    n: int | tuple[int, ...]  # N-gram order(s) analyzed
    total_ngrams: int
    flagged_count: int
    flagged_per_10k: float  # flagged_count / (total_ngrams / 10000)
    total_ngrams_dist: Distribution
    chunk_size: int
    chunk_count: int
    metadata: dict[str, Any]


# ===== Readability Results =====


@dataclass
class FleschResult:
    """Result from Flesch Reading Ease and Flesch-Kincaid Grade computation.

    All numeric metrics include both a mean value (convenient access) and
    a full distribution with per-chunk values and statistics.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Example:
        >>> result = compute_flesch(text, chunk_size=1000)
        >>> result.reading_ease  # mean across chunks
        68.54
        >>> result.reading_ease_dist.std  # variance reveals fingerprint
        4.2
        >>> result.reading_ease_dist.values  # per-chunk values
        [65.2, 71.1, 68.8, ...]
    """

    # Convenient access (mean values)
    reading_ease: float
    grade_level: float
    difficulty: str  # Based on mean reading_ease

    # Full distributions
    reading_ease_dist: Distribution
    grade_level_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class SMOGResult:
    """Result from SMOG Index computation.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27
    """

    # Convenient access (mean values)
    smog_index: float
    grade_level: float

    # Full distributions
    smog_index_dist: Distribution
    grade_level_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class GunningFogResult:
    """Result from Gunning Fog Index computation.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27
    """

    # Convenient access (mean values)
    fog_index: float
    grade_level: float

    # Full distributions
    fog_index_dist: Distribution
    grade_level_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class ColemanLiauResult:
    """Result from Coleman-Liau Index computation.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27
    """

    # Convenient access (mean values)
    cli_index: float
    grade_level: float  # Changed to float for mean across chunks

    # Full distributions
    cli_index_dist: Distribution
    grade_level_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class ARIResult:
    """Result from Automated Readability Index computation.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27
    """

    # Convenient access (mean values)
    ari_score: float
    grade_level: float  # Changed to float for mean across chunks
    age_range: str  # Based on mean grade level

    # Full distributions
    ari_score_dist: Distribution
    grade_level_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Syntactic Results =====


@dataclass
class POSResult:
    """Result from Part-of-Speech ratio analysis.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27
    """

    # Convenient access (mean values)
    noun_ratio: float
    verb_ratio: float
    adjective_ratio: float
    adverb_ratio: float
    noun_verb_ratio: float
    adjective_noun_ratio: float
    lexical_density: float
    function_word_ratio: float

    # Full distributions
    noun_ratio_dist: Distribution
    verb_ratio_dist: Distribution
    adjective_ratio_dist: Distribution
    adverb_ratio_dist: Distribution
    noun_verb_ratio_dist: Distribution
    adjective_noun_ratio_dist: Distribution
    lexical_density_dist: Distribution
    function_word_ratio_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class SentenceStatsResult:
    """Result from sentence-level statistics.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27
    """

    # Convenient access (mean values)
    mean_sentence_length: float
    sentence_length_std: float
    sentence_length_range: float  # Changed to float for mean across chunks
    min_sentence_length: float  # Changed to float for mean across chunks
    max_sentence_length: float  # Changed to float for mean across chunks
    sentence_count: int  # Total across all chunks

    # Full distributions
    mean_sentence_length_dist: Distribution
    sentence_length_std_dist: Distribution
    sentence_length_range_dist: Distribution
    min_sentence_length_dist: Distribution
    max_sentence_length_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Authorship Results =====


@dataclass
class BurrowsDeltaResult:
    """Result from Burrows' Delta computation."""

    delta_score: float
    distance_type: str  # "burrows", "cosine", "eder"
    mfw_count: int
    metadata: dict[str, Any]


@dataclass
class ZetaResult:
    """Result from Zeta score computation."""

    zeta_score: float
    marker_words: list[str]
    anti_marker_words: list[str]
    metadata: dict[str, Any]


# ===== N-gram Results =====


@dataclass
class EntropyResult:
    """Result from n-gram entropy computation.

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27
    """

    # Convenient access (mean values)
    entropy: float
    perplexity: float
    ngram_type: str  # "character_bigram", "word_bigram", "word_trigram"

    # Full distributions
    entropy_dist: Distribution
    perplexity_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Character-Level Results =====
# Related to GitHub Issue #12: Character-Level Metrics
# https://github.com/craigtrim/pystylometry/issues/12


@dataclass
class CharacterMetricsResult:
    """Result from character-level metrics analysis.

    This dataclass holds character-level stylometric features that provide
    low-level insights into writing style. Character-level metrics are
    fundamental for authorship attribution and can capture distinctive
    patterns in punctuation, formatting, and word construction.

    Related GitHub Issues:
        #12 - Character-Level Metrics
        #27 - Native chunked analysis with Distribution dataclass

    Metrics included:
        - Average word length (characters per word)
        - Average sentence length (characters per sentence)
        - Punctuation density (punctuation marks per 100 words)
        - Punctuation variety (count of unique punctuation types)
        - Letter frequency distribution (26-element vector for a-z)
        - Vowel-to-consonant ratio
        - Digit frequency (count/ratio of numeric characters)
        - Uppercase ratio (uppercase letters / total letters)
        - Whitespace ratio (whitespace characters / total characters)

    References:
        Grieve, J. (2007). Quantitative authorship attribution: An evaluation
            of techniques. Literary and Linguistic Computing, 22(3), 251-270.
        Stamatatos, E. (2009). A survey of modern authorship attribution methods.
            JASIST, 60(3), 538-556.
    """

    # Convenient access (mean values)
    avg_word_length: float
    avg_sentence_length_chars: float
    punctuation_density: float
    punctuation_variety: float  # Changed to float for mean across chunks
    letter_frequency: dict[str, float]  # Aggregate frequency
    vowel_consonant_ratio: float
    digit_count: int  # Total across all chunks
    digit_ratio: float
    uppercase_ratio: float
    whitespace_ratio: float

    # Full distributions
    avg_word_length_dist: Distribution
    avg_sentence_length_chars_dist: Distribution
    punctuation_density_dist: Distribution
    punctuation_variety_dist: Distribution
    vowel_consonant_ratio_dist: Distribution
    digit_ratio_dist: Distribution
    uppercase_ratio_dist: Distribution
    whitespace_ratio_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Function Word Results =====
# Related to GitHub Issue #13: Function Word Analysis
# https://github.com/craigtrim/pystylometry/issues/13


@dataclass
class FunctionWordResult:
    """Result from function word analysis.

    Function words (determiners, prepositions, conjunctions, pronouns, auxiliary
    verbs) are highly frequent, content-independent words that are often used
    subconsciously. They are considered strong authorship markers because authors
    use them consistently across different topics and genres.

    Related GitHub Issues:
        #13 - Function Word Analysis
        #27 - Native chunked analysis with Distribution dataclass

    This analysis computes:
        - Frequency profiles for all function word categories
        - Ratios for specific grammatical categories
        - Most/least frequently used function words
        - Function word diversity metrics

    Function word categories analyzed:
        - Determiners: the, a, an, this, that, these, those, etc.
        - Prepositions: in, on, at, by, for, with, from, to, etc.
        - Conjunctions: and, but, or, nor, for, yet, so, etc.
        - Pronouns: I, you, he, she, it, we, they, etc.
        - Auxiliary verbs: be, have, do, can, will, shall, may, etc.
        - Particles: up, down, out, off, over, etc.

    References:
        Mosteller, F., & Wallace, D. L. (1964). Inference and disputed authorship:
            The Federalist. Addison-Wesley.
        Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide
            to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.
    """

    # Convenient access (mean values)
    determiner_ratio: float
    preposition_ratio: float
    conjunction_ratio: float
    pronoun_ratio: float
    auxiliary_ratio: float
    particle_ratio: float
    total_function_word_ratio: float
    function_word_diversity: float
    most_frequent_function_words: list[tuple[str, int]]  # Aggregate
    least_frequent_function_words: list[tuple[str, int]]  # Aggregate
    function_word_distribution: dict[str, int]  # Aggregate

    # Full distributions
    determiner_ratio_dist: Distribution
    preposition_ratio_dist: Distribution
    conjunction_ratio_dist: Distribution
    pronoun_ratio_dist: Distribution
    auxiliary_ratio_dist: Distribution
    particle_ratio_dist: Distribution
    total_function_word_ratio_dist: Distribution
    function_word_diversity_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Advanced Lexical Diversity Results =====
# Related to GitHub Issue #14: Advanced Lexical Diversity Metrics
# https://github.com/craigtrim/pystylometry/issues/14


@dataclass
class VocdDResult:
    """Result from voc-D computation.

    voc-D is a sophisticated measure of lexical diversity that uses a mathematical
    model to estimate vocabulary richness while controlling for text length.
    It fits a curve to the relationship between tokens and types across multiple
    random samples of the text.

    Related GitHub Issues:
        #14 - Advanced Lexical Diversity Metrics
        #27 - Native chunked analysis with Distribution dataclass

    The D parameter represents the theoretical vocabulary size and is more
    stable across different text lengths than simple TTR measures.

    References:
        Malvern, D., Richards, B., Chipere, N., & Durán, P. (2004).
            Lexical Diversity and Language Development. Palgrave Macmillan.
        McKee, G., Malvern, D., & Richards, B. (2000). Measuring vocabulary
            diversity using dedicated software. Literary and Linguistic Computing,
            15(3), 323-337.
    """

    # Convenient access (mean values)
    d_parameter: float
    curve_fit_r_squared: float
    sample_count: int  # Total across all chunks
    optimal_sample_size: int

    # Full distributions
    d_parameter_dist: Distribution
    curve_fit_r_squared_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class MATTRResult:
    """Result from MATTR (Moving-Average Type-Token Ratio) computation.

    MATTR computes TTR using a moving window of fixed size, which provides
    a more stable measure of lexical diversity than simple TTR, especially
    for longer texts. The moving window approach reduces the impact of text
    length on the TTR calculation.

    Related GitHub Issues:
        #14 - Advanced Lexical Diversity Metrics
        #27 - Native chunked analysis with Distribution dataclass

    References:
        Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot:
            The moving-average type-token ratio (MATTR). Journal of Quantitative
            Linguistics, 17(2), 94-100.
    """

    # Convenient access (mean values)
    mattr_score: float
    window_size: int
    window_count: int  # Total across all chunks
    ttr_std_dev: float
    min_ttr: float
    max_ttr: float

    # Full distributions
    mattr_score_dist: Distribution
    ttr_std_dev_dist: Distribution
    min_ttr_dist: Distribution
    max_ttr_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class HDDResult:
    """Result from HD-D (Hypergeometric Distribution D) computation.

    HD-D is a probabilistic measure of lexical diversity based on the
    hypergeometric distribution. It estimates the probability of encountering
    new word types as text length increases, providing a mathematically
    rigorous measure that is less sensitive to text length than TTR.

    Related GitHub Issues:
        #14 - Advanced Lexical Diversity Metrics
        #27 - Native chunked analysis with Distribution dataclass

    References:
        McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation
            study of sophisticated approaches to lexical diversity assessment.
            Behavior Research Methods, 42(2), 381-392.
    """

    # Convenient access (mean values)
    hdd_score: float
    sample_size: int
    type_count: int  # Total unique across all chunks
    token_count: int  # Total across all chunks

    # Full distributions
    hdd_score_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class MSTTRResult:
    """Result from MSTTR (Mean Segmental Type-Token Ratio) computation.

    MSTTR divides the text into sequential segments of equal length and
    computes the average TTR across all segments. This provides a length-
    normalized measure of lexical diversity that is more comparable across
    texts of different lengths.

    Related GitHub Issues:
        #14 - Advanced Lexical Diversity Metrics
        #27 - Native chunked analysis with Distribution dataclass

    References:
        Johnson, W. (1944). Studies in language behavior: I. A program of research.
            Psychological Monographs, 56(2), 1-15.
    """

    # Convenient access (mean values)
    msttr_score: float
    segment_size: int
    segment_count: int  # Total across all chunks
    ttr_std_dev: float
    min_ttr: float
    max_ttr: float
    segment_ttrs: list[float]  # Aggregate from all chunks

    # Full distributions
    msttr_score_dist: Distribution
    ttr_std_dev_dist: Distribution
    min_ttr_dist: Distribution
    max_ttr_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Word Frequency Sophistication Results =====
# Related to GitHub Issue #15: Word Frequency Sophistication Metrics
# https://github.com/craigtrim/pystylometry/issues/15


@dataclass
class WordFrequencySophisticationResult:
    """Result from word frequency sophistication analysis.

    Word frequency sophistication metrics measure how common or rare the
    vocabulary used in a text is, based on reference frequency lists from
    large corpora. Authors who use less frequent (more sophisticated) words
    score higher on these metrics.

    Related GitHub Issues:
        #15 - Word Frequency Sophistication Metrics
        #27 - Native chunked analysis with Distribution dataclass

    This analysis uses reference frequency data from:
        - COCA (Corpus of Contemporary American English)
        - BNC (British National Corpus)
        - Google N-grams
        - SUBTLEXus (subtitle frequencies)

    Metrics computed:
        - Mean word frequency (average frequency rank)
        - Median word frequency
        - Rare word ratio (words beyond frequency threshold)
        - Academic word ratio (from Academic Word List)
        - Advanced word ratio (sophisticated vocabulary)

    References:
        Brysbaert, M., & New, B. (2009). Moving beyond Kučera and Francis:
            A critical evaluation of current word frequency norms. Behavior
            Research Methods, Instruments, & Computers, 41(4), 977-990.
        Coxhead, A. (2000). A new academic word list. TESOL Quarterly, 34(2), 213-238.
    """

    # Convenient access (mean values)
    mean_frequency_rank: float
    median_frequency_rank: float
    rare_word_ratio: float
    common_word_ratio: float
    academic_word_ratio: float
    advanced_word_ratio: float
    frequency_band_distribution: dict[str, float]  # Aggregate
    rarest_words: list[tuple[str, float]]  # Aggregate
    most_common_words: list[tuple[str, float]]  # Aggregate

    # Full distributions
    mean_frequency_rank_dist: Distribution
    median_frequency_rank_dist: Distribution
    rare_word_ratio_dist: Distribution
    common_word_ratio_dist: Distribution
    academic_word_ratio_dist: Distribution
    advanced_word_ratio_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Additional Readability Results =====
# Related to GitHub Issue #16: Additional Readability Formulas
# https://github.com/craigtrim/pystylometry/issues/16


@dataclass
class DaleChallResult:
    """Result from Dale-Chall Readability Formula.

    The Dale-Chall formula uses a list of 3000 familiar words that 80% of
    fourth-graders understand. Words not on this list are considered "difficult."
    The formula provides a grade level estimate based on sentence length and
    the percentage of difficult words.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    Formula: 0.1579 * (difficult_words / total_words * 100) + 0.0496 * avg_sentence_length

    If % difficult words > 5%, add 3.6365 to the raw score.

    References:
        Dale, E., & Chall, J. S. (1948). A formula for predicting readability.
            Educational Research Bulletin, 27(1), 11-28.
        Chall, J. S., & Dale, E. (1995). Readability revisited: The new Dale-Chall
            readability formula. Brookline Books.
    """

    # Convenient access (mean values)
    dale_chall_score: float
    grade_level: str  # Based on mean score
    difficult_word_count: int  # Total across all chunks
    difficult_word_ratio: float  # Mean ratio
    avg_sentence_length: float  # Mean
    total_words: int  # Total across all chunks

    # Full distributions
    dale_chall_score_dist: Distribution
    difficult_word_ratio_dist: Distribution
    avg_sentence_length_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class LinsearWriteResult:
    """Result from Linsear Write Formula.

    The Linsear Write Formula was developed for the U.S. Air Force to calculate
    the readability of technical manuals. It categorizes words as "easy" (1-2
    syllables) or "hard" (3+ syllables) and uses sentence length to estimate
    grade level. It's particularly effective for technical writing.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    References:
        Klare, G. R. (1974-1975). Assessing readability. Reading Research Quarterly,
            10(1), 62-102.
    """

    # Convenient access (mean values)
    linsear_score: float
    grade_level: float  # Changed to float for mean across chunks
    easy_word_count: int  # Total across all chunks
    hard_word_count: int  # Total across all chunks
    avg_sentence_length: float  # Mean

    # Full distributions
    linsear_score_dist: Distribution
    grade_level_dist: Distribution
    avg_sentence_length_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class FryResult:
    """Result from Fry Readability Graph.

    The Fry Readability Graph uses average sentence length and average syllables
    per word to determine reading difficulty. It plots these values on a graph
    to determine the grade level. This implementation provides the numerical
    coordinates and estimated grade level.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    References:
        Fry, E. (1968). A readability formula that saves time. Journal of Reading,
            11(7), 513-578.
        Fry, E. (1977). Fry's readability graph: Clarifications, validity, and
            extension to level 17. Journal of Reading, 21(3), 242-252.
    """

    # Convenient access (mean values)
    avg_sentence_length: float
    avg_syllables_per_100: float
    grade_level: str  # Based on mean coordinates
    graph_zone: str  # Based on mean coordinates

    # Full distributions
    avg_sentence_length_dist: Distribution
    avg_syllables_per_100_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class FORCASTResult:
    """Result from FORCAST Readability Formula.

    FORCAST (FORmula for CASTing readability) was developed by the U.S. military
    to assess readability without counting syllables. It uses only single-syllable
    words as a measure, making it faster to compute than syllable-based formulas.
    Particularly useful for technical and military documents.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    Formula: 20 - (N / 10), where N is the number of single-syllable words
    per 150-word sample.

    References:
        Caylor, J. S., Sticht, T. G., Fox, L. C., & Ford, J. P. (1973).
            Methodologies for determining reading requirements of military
            occupational specialties. Human Resources Research Organization.
    """

    # Convenient access (mean values)
    forcast_score: float
    grade_level: float  # Changed to float for mean across chunks
    single_syllable_ratio: float  # Mean ratio
    single_syllable_count: int  # Total across all chunks
    total_words: int  # Total across all chunks

    # Full distributions
    forcast_score_dist: Distribution
    grade_level_dist: Distribution
    single_syllable_ratio_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


@dataclass
class PowersSumnerKearlResult:
    """Result from Powers-Sumner-Kearl Readability Formula.

    The Powers-Sumner-Kearl formula is a variation of the Flesch Reading Ease
    formula, recalibrated for primary grade levels (grades 1-4). It uses
    average sentence length and average syllables per word, but with different
    coefficients optimized for younger readers.

    Related GitHub Issues:
        #16 - Additional Readability Formulas
        #27 - Native chunked analysis with Distribution dataclass

    Formula: 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029

    References:
        Powers, R. D., Sumner, W. A., & Kearl, B. E. (1958). A recalculation of
            four adult readability formulas. Journal of Educational Psychology,
            49(2), 99-105.
    """

    # Convenient access (mean values)
    psk_score: float
    grade_level: float
    avg_sentence_length: float
    avg_syllables_per_word: float
    total_sentences: int  # Total across all chunks
    total_words: int  # Total across all chunks
    total_syllables: int  # Total across all chunks

    # Full distributions
    psk_score_dist: Distribution
    grade_level_dist: Distribution
    avg_sentence_length_dist: Distribution
    avg_syllables_per_word_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Advanced Syntactic Results =====
# Related to GitHub Issue #17: Advanced Syntactic Analysis
# https://github.com/craigtrim/pystylometry/issues/17


@dataclass
class AdvancedSyntacticResult:
    """Result from advanced syntactic analysis using dependency parsing.

    Advanced syntactic analysis uses dependency parsing to extract sophisticated
    grammatical features that go beyond simple POS tagging. These features
    capture sentence complexity, grammatical sophistication, and syntactic
    style preferences.

    Related GitHub Issues:
        #17 - Advanced Syntactic Analysis
        #27 - Native chunked analysis with Distribution dataclass

    Features analyzed:
        - Parse tree depth (sentence structural complexity)
        - T-units (minimal terminable units - independent clauses with modifiers)
        - Clausal density (clauses per T-unit)
        - Dependent clause ratio
        - Passive voice ratio
        - Subordination index
        - Coordination index
        - Sentence complexity score

    References:
        Hunt, K. W. (1965). Grammatical structures written at three grade levels.
            NCTE Research Report No. 3.
        Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
        Lu, X. (2010). Automatic analysis of syntactic complexity in second language
            writing. International Journal of Corpus Linguistics, 15(4), 474-496.
    """

    # Convenient access (mean values)
    mean_parse_tree_depth: float
    max_parse_tree_depth: float  # Changed to float for mean across chunks
    t_unit_count: int  # Total across all chunks
    mean_t_unit_length: float
    clausal_density: float
    dependent_clause_ratio: float
    passive_voice_ratio: float
    subordination_index: float
    coordination_index: float
    sentence_complexity_score: float
    dependency_distance: float
    left_branching_ratio: float
    right_branching_ratio: float

    # Full distributions
    mean_parse_tree_depth_dist: Distribution
    max_parse_tree_depth_dist: Distribution
    mean_t_unit_length_dist: Distribution
    clausal_density_dist: Distribution
    dependent_clause_ratio_dist: Distribution
    passive_voice_ratio_dist: Distribution
    subordination_index_dist: Distribution
    coordination_index_dist: Distribution
    sentence_complexity_score_dist: Distribution
    dependency_distance_dist: Distribution
    left_branching_ratio_dist: Distribution
    right_branching_ratio_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Sentence Type Results =====
# Related to GitHub Issue #18: Sentence Type Classification
# https://github.com/craigtrim/pystylometry/issues/18


@dataclass
class SentenceTypeResult:
    """Result from sentence type classification analysis.

    Sentence type classification categorizes sentences by their grammatical
    structure (simple, compound, complex, compound-complex) and communicative
    function (declarative, interrogative, imperative, exclamatory). Different
    authors and genres show distinct patterns in sentence type distribution.

    Related GitHub Issues:
        #18 - Sentence Type Classification
        #27 - Native chunked analysis with Distribution dataclass

    Structural types:
        - Simple: One independent clause (e.g., "The cat sat.")
        - Compound: Multiple independent clauses (e.g., "I came, I saw, I conquered.")
        - Complex: One independent + dependent clause(s) (e.g., "When I arrived, I saw her.")
        - Compound-Complex: Multiple independent + dependent
          (e.g., "I came when called, and I stayed.")

    Functional types:
        - Declarative: Statement (e.g., "The sky is blue.")
        - Interrogative: Question (e.g., "Is the sky blue?")
        - Imperative: Command (e.g., "Look at the sky!")
        - Exclamatory: Exclamation (e.g., "What a blue sky!")

    References:
        Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
        Huddleston, R., & Pullum, G. K. (2002). The Cambridge Grammar of the English Language.
    """

    # Convenient access (mean ratios)
    simple_ratio: float
    compound_ratio: float
    complex_ratio: float
    compound_complex_ratio: float
    declarative_ratio: float
    interrogative_ratio: float
    imperative_ratio: float
    exclamatory_ratio: float

    # Counts (totals across all chunks)
    simple_count: int
    compound_count: int
    complex_count: int
    compound_complex_count: int
    declarative_count: int
    interrogative_count: int
    imperative_count: int
    exclamatory_count: int
    total_sentences: int

    # Diversity (mean across chunks)
    structural_diversity: float
    functional_diversity: float

    # Full distributions
    simple_ratio_dist: Distribution
    compound_ratio_dist: Distribution
    complex_ratio_dist: Distribution
    compound_complex_ratio_dist: Distribution
    declarative_ratio_dist: Distribution
    interrogative_ratio_dist: Distribution
    imperative_ratio_dist: Distribution
    exclamatory_ratio_dist: Distribution
    structural_diversity_dist: Distribution
    functional_diversity_dist: Distribution

    # Chunking context
    chunk_size: int
    chunk_count: int

    metadata: dict[str, Any]


# ===== Extended N-gram Results =====
# Related to GitHub Issue #19: Extended N-gram Features
# https://github.com/craigtrim/pystylometry/issues/19


@dataclass
class ExtendedNgramResult:
    """Result from extended n-gram analysis.

    Extended n-gram analysis goes beyond basic bigram/trigram entropy to provide
    comprehensive n-gram statistics including frequency distributions, most
    distinctive n-grams, skipgrams, and part-of-speech n-grams. These features
    are valuable for authorship attribution and style analysis.

    Related GitHub Issue:
        #19 - Extended N-gram Features
        https://github.com/craigtrim/pystylometry/issues/19

    Features computed:
        - Trigram frequency distributions and top trigrams
        - 4-gram frequency distributions and top 4-grams
        - Skipgrams (n-grams with gaps, e.g., "the * dog")
        - POS n-grams (e.g., "DET ADJ NOUN")
        - Character trigrams and 4-grams
        - N-gram diversity metrics
        - Entropy for each n-gram order

    References:
        Guthrie, D., Allison, B., Liu, W., Guthrie, L., & Wilks, Y. (2006).
            A closer look at skip-gram modelling. LREC.
        Stamatatos, E. (2009). A survey of modern authorship attribution methods.
            JASIST, 60(3), 538-556.

    Example:
        >>> result = compute_extended_ngrams("Sample text for n-gram analysis...")
        >>> print(f"Top trigrams: {result.top_word_trigrams[:5]}")
        >>> print(f"Trigram entropy: {result.word_trigram_entropy:.2f}")
    """

    # Word n-grams
    top_word_trigrams: list[tuple[str, int]]  # Most frequent word trigrams
    top_word_4grams: list[tuple[str, int]]  # Most frequent word 4-grams
    word_trigram_count: int  # Total unique word trigrams
    word_4gram_count: int  # Total unique word 4-grams
    word_trigram_entropy: float  # Shannon entropy of trigram distribution
    word_4gram_entropy: float  # Shannon entropy of 4-gram distribution

    # Skipgrams (n-grams with gaps)
    top_skipgrams_2_1: list[tuple[str, int]]  # Top 2-skipgrams (gap of 1)
    top_skipgrams_3_1: list[tuple[str, int]]  # Top 3-skipgrams (gap of 1)
    skipgram_2_1_count: int  # Unique 2-skipgrams
    skipgram_3_1_count: int  # Unique 3-skipgrams

    # POS n-grams
    top_pos_trigrams: list[tuple[str, int]]  # Most frequent POS trigrams
    top_pos_4grams: list[tuple[str, int]]  # Most frequent POS 4-grams
    pos_trigram_count: int  # Unique POS trigrams
    pos_4gram_count: int  # Unique POS 4-grams
    pos_trigram_entropy: float  # Shannon entropy of POS trigram distribution

    # Character n-grams
    top_char_trigrams: list[tuple[str, int]]  # Most frequent character trigrams
    top_char_4grams: list[tuple[str, int]]  # Most frequent character 4-grams
    char_trigram_entropy: float  # Shannon entropy of char trigram distribution
    char_4gram_entropy: float  # Shannon entropy of char 4-gram distribution

    metadata: dict[str, Any]  # Full frequency distributions, parameters, etc.


# ===== Stylistic Markers Results =====
# Related to GitHub Issue #20: Stylistic Markers
# https://github.com/craigtrim/pystylometry/issues/20


@dataclass
class StylisticMarkersResult:
    """Result from stylistic markers analysis.

    Stylistic markers are specific linguistic features that authors tend to use
    consistently and often subconsciously. These include contraction usage,
    intensifier preferences, hedging expressions, punctuation habits, and more.
    They are powerful indicators of authorial identity.

    Related GitHub Issue:
        #20 - Stylistic Markers
        https://github.com/craigtrim/pystylometry/issues/20

    Markers analyzed:
        - Contraction usage (don't vs. do not, I'm vs. I am, etc.)
        - Intensifiers (very, really, extremely, quite, etc.)
        - Hedges (maybe, perhaps, probably, somewhat, etc.)
        - Modal auxiliaries (can, could, may, might, must, should, will, would)
        - Negation patterns (not, no, never, none, neither, etc.)
        - Exclamation frequency
        - Question frequency
        - Quotation usage
        - Parenthetical expressions
        - Ellipses and dashes

    References:
        Argamon, S., & Levitan, S. (2005). Measuring the usefulness of function
            words for authorship attribution. ACH/ALLC.
        Pennebaker, J. W. (2011). The secret life of pronouns. Bloomsbury Press.

    Example:
        >>> result = compute_stylistic_markers("Sample text with various markers...")
        >>> print(f"Contraction ratio: {result.contraction_ratio * 100:.1f}%")
        >>> print(f"Intensifier density: {result.intensifier_density:.2f}")
        >>> print(f"Hedging density: {result.hedging_density:.2f}")
    """

    # Contraction patterns
    contraction_ratio: float  # Contractions / (contractions + full forms)
    contraction_count: int  # Total contractions
    expanded_form_count: int  # Total expanded forms (e.g., "do not" vs "don't")
    top_contractions: list[tuple[str, int]]  # Most frequent contractions

    # Intensifiers and hedges
    intensifier_density: float  # Intensifiers per 100 words
    intensifier_count: int  # Total intensifier count
    top_intensifiers: list[tuple[str, int]]  # Most frequent intensifiers
    hedging_density: float  # Hedges per 100 words
    hedging_count: int  # Total hedge count
    top_hedges: list[tuple[str, int]]  # Most frequent hedges

    # Modal auxiliaries
    modal_density: float  # Modal auxiliaries per 100 words
    modal_distribution: dict[str, int]  # Count per modal (can, could, may, etc.)
    epistemic_modal_ratio: float  # Epistemic modals / all modals
    deontic_modal_ratio: float  # Deontic modals / all modals

    # Negation
    negation_density: float  # Negation markers per 100 words
    negation_count: int  # Total negation markers
    negation_types: dict[str, int]  # not, no, never, etc. with counts

    # Punctuation style
    exclamation_density: float  # Exclamation marks per 100 words
    question_density: float  # Question marks per 100 words
    quotation_density: float  # Quotation marks per 100 words
    parenthetical_density: float  # Parentheses per 100 words
    ellipsis_density: float  # Ellipses per 100 words
    dash_density: float  # Dashes (em/en) per 100 words
    semicolon_density: float  # Semicolons per 100 words
    colon_density: float  # Colons per 100 words

    metadata: dict[str, Any]  # Full lists, total word count, etc.


# ===== Vocabulary Overlap Results =====
# Related to GitHub Issue #21: Vocabulary Overlap and Similarity Metrics
# https://github.com/craigtrim/pystylometry/issues/21


@dataclass
class VocabularyOverlapResult:
    """Result from vocabulary overlap and similarity analysis.

    Vocabulary overlap metrics measure the similarity between two texts based on
    their shared vocabulary. These metrics are useful for authorship verification,
    plagiarism detection, and measuring stylistic consistency across texts.

    Related GitHub Issue:
        #21 - Vocabulary Overlap and Similarity Metrics
        https://github.com/craigtrim/pystylometry/issues/21

    Metrics computed:
        - Jaccard similarity (intersection / union)
        - Dice coefficient (2 * intersection / sum of sizes)
        - Overlap coefficient (intersection / min(size1, size2))
        - Cosine similarity (using word frequency vectors)
        - KL divergence (asymmetric distributional difference)
        - Shared vocabulary size and ratio
        - Unique words in each text
        - Most distinctive words for each text

    References:
        Jaccard, P. (1912). The distribution of the flora in the alpine zone.
            New Phytologist, 11(2), 37-50.
        Salton, G., & McGill, M. J. (1983). Introduction to Modern Information
            Retrieval. McGraw-Hill.
        Kullback, S., & Leibler, R. A. (1951). On Information and Sufficiency.
            Annals of Mathematical Statistics, 22(1), 79-86.
        Manning, C. D., & Schütze, H. (1999). Foundations of Statistical NLP.
            MIT Press.

    Example:
        >>> result = compute_vocabulary_overlap(text1, text2)
        >>> print(f"Jaccard similarity: {result.jaccard_similarity:.3f}")
        >>> print(f"Shared vocabulary: {result.shared_vocab_size} words")
        >>> print(f"Text1 unique: {result.text1_unique_count}")
    """

    # Similarity scores (0-1 range)
    jaccard_similarity: float  # Intersection / union
    dice_coefficient: float  # 2 * intersection / (size1 + size2)
    overlap_coefficient: float  # Intersection / min(size1, size2)
    cosine_similarity: float  # Cosine of frequency vectors
    kl_divergence: float  # Kullback-Leibler divergence (asymmetric, text1 || text2)

    # Vocabulary sizes
    text1_vocab_size: int  # Unique words in text 1
    text2_vocab_size: int  # Unique words in text 2
    shared_vocab_size: int  # Words in both texts
    union_vocab_size: int  # Words in either text
    text1_unique_count: int  # Words only in text 1
    text2_unique_count: int  # Words only in text 2

    # Shared and distinctive vocabulary
    shared_words: list[str]  # Words appearing in both texts
    text1_distinctive_words: list[tuple[str, float]]  # Words + TF-IDF scores for text 1
    text2_distinctive_words: list[tuple[str, float]]  # Words + TF-IDF scores for text 2

    # Ratios
    text1_coverage: float  # Shared / text1_vocab (how much of text1 is shared)
    text2_coverage: float  # Shared / text2_vocab (how much of text2 is shared)

    metadata: dict[str, Any]  # Full vocabulary sets, frequency vectors, etc.


# ===== Cohesion and Coherence Results =====
# Related to GitHub Issue #22: Cohesion and Coherence Metrics
# https://github.com/craigtrim/pystylometry/issues/22


@dataclass
class CohesionCoherenceResult:
    """Result from cohesion and coherence analysis.

    Cohesion and coherence metrics measure how well a text holds together
    structurally (cohesion) and semantically (coherence). These metrics are
    important for analyzing writing quality, readability, and authorial
    sophistication.

    Related GitHub Issue:
        #22 - Cohesion and Coherence Metrics
        https://github.com/craigtrim/pystylometry/issues/22

    Cohesion features:
        - Referential cohesion (pronouns, demonstratives pointing back)
        - Lexical cohesion (word repetition, synonyms, semantic relatedness)
        - Connective density (discourse markers, conjunctions)
        - Anaphora resolution success rate
        - Lexical chains (sequences of semantically related words)

    Coherence features:
        - Sentence-to-sentence semantic similarity
        - Topic consistency across paragraphs
        - Discourse structure (thesis, support, conclusion)
        - Semantic overlap between adjacent sentences

    References:
        Halliday, M. A. K., & Hasan, R. (1976). Cohesion in English. Longman.
        Graesser, A. C., McNamara, D. S., & Kulikowich, J. M. (2011). Coh-Metrix:
            Providing multilevel analyses of text characteristics. Educational
            Researcher, 40(5), 223-234.

    Example:
        >>> result = compute_cohesion_coherence("Multi-paragraph text...")
        >>> print(f"Pronoun density: {result.pronoun_density:.2f}")
        >>> print(f"Lexical overlap: {result.adjacent_sentence_overlap:.3f}")
        >>> print(f"Connective density: {result.connective_density:.2f}")
    """

    # Referential cohesion
    pronoun_density: float  # Pronouns per 100 words
    demonstrative_density: float  # Demonstratives (this, that, these, those) per 100 words
    anaphora_count: int  # Anaphoric references detected
    anaphora_resolution_ratio: float  # Successfully resolved / total

    # Lexical cohesion
    word_repetition_ratio: float  # Repeated content words / total content words
    synonym_density: float  # Synonym pairs per 100 words
    lexical_chain_count: int  # Number of lexical chains detected
    mean_chain_length: float  # Average length of lexical chains
    content_word_overlap: float  # Content word overlap between sentences

    # Connectives and discourse markers
    connective_density: float  # Discourse connectives per 100 words
    additive_connective_ratio: float  # "and", "also", "furthermore" / total connectives
    adversative_connective_ratio: float  # "but", "however", "nevertheless" / total
    causal_connective_ratio: float  # "because", "therefore", "thus" / total
    temporal_connective_ratio: float  # "then", "after", "before" / total

    # Coherence measures
    adjacent_sentence_overlap: float  # Mean semantic overlap between adjacent sentences
    paragraph_topic_consistency: float  # Mean topic consistency within paragraphs
    mean_sentence_similarity: float  # Mean cosine similarity between all sentence pairs
    semantic_coherence_score: float  # Composite coherence metric (0-1)

    # Structural coherence
    paragraph_count: int  # Number of paragraphs detected
    mean_paragraph_length: float  # Mean sentences per paragraph
    discourse_structure_score: float  # Quality of intro/body/conclusion structure

    metadata: dict[str, Any]  # Lexical chains, connective lists, similarity matrices, etc.


# ===== Genre and Register Results =====
# Related to GitHub Issue #23: Genre and Register Features
# https://github.com/craigtrim/pystylometry/issues/23


@dataclass
class GenreRegisterResult:
    """Result from genre and register classification analysis.

    Genre and register features distinguish between different types of texts
    (academic, journalistic, fiction, legal, etc.) based on linguistic patterns.
    These features can help identify the context and formality level of a text,
    and are useful for authorship attribution when combined with other metrics.

    Related GitHub Issue:
        #23 - Genre and Register Features
        https://github.com/craigtrim/pystylometry/issues/23

    Features analyzed:
        - Formality markers (Latinate words, nominalizations, passive voice)
        - Personal vs. impersonal style (1st/2nd person vs. 3rd person)
        - Abstract vs. concrete vocabulary
        - Technical term density
        - Narrative vs. expository markers
        - Dialogue presence and ratio
        - Register classification (frozen, formal, consultative, casual, intimate)

    References:
        Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
        Biber, D., & Conrad, S. (2009). Register, genre, and style. Cambridge
            University Press.
        Heylighen, F., & Dewaele, J. M. (1999). Formality of language: Definition,
            measurement and behavioral determinants. Internal Report, Center "Leo
            Apostel", Free University of Brussels.

    Example:
        >>> result = compute_genre_register("Academic paper text...")
        >>> print(f"Formality score: {result.formality_score:.2f}")
        >>> print(f"Register: {result.register_classification}")
        >>> print(f"Genre prediction: {result.predicted_genre}")
    """

    # Formality indicators
    formality_score: float  # Composite formality score (0-100)
    latinate_ratio: float  # Latinate words / total words
    nominalization_density: float  # Nominalizations per 100 words
    passive_voice_density: float  # Passive constructions per 100 words

    # Personal vs. impersonal
    first_person_ratio: float  # 1st person pronouns / total pronouns
    second_person_ratio: float  # 2nd person pronouns / total pronouns
    third_person_ratio: float  # 3rd person pronouns / total pronouns
    impersonal_construction_density: float  # "It is...", "There are..." per 100 words

    # Abstract vs. concrete
    abstract_noun_ratio: float  # Abstract nouns / total nouns
    concrete_noun_ratio: float  # Concrete nouns / total nouns
    abstractness_score: float  # Composite abstractness (based on word concreteness ratings)

    # Technical and specialized
    technical_term_density: float  # Technical/specialized terms per 100 words
    jargon_density: float  # Domain-specific jargon per 100 words

    # Narrative vs. expository
    narrative_marker_density: float  # Past tense, action verbs per 100 words
    expository_marker_density: float  # Present tense, linking verbs per 100 words
    narrative_expository_ratio: float  # Narrative / expository markers

    # Dialogue and quotation
    dialogue_ratio: float  # Dialogue / total text (estimated)
    quotation_density: float  # Quotations per 100 words

    # Classification results
    register_classification: str  # frozen, formal, consultative, casual, intimate
    predicted_genre: str  # academic, journalistic, fiction, legal, conversational, etc.
    genre_confidence: float  # Confidence in genre prediction (0-1)

    # Feature scores for major genres (0-1 scores for each)
    academic_score: float
    journalistic_score: float
    fiction_score: float
    legal_score: float
    conversational_score: float

    metadata: dict[str, Any]  # Feature details, word lists, classification probabilities, etc.


# ===== Additional Authorship Results =====
# Related to GitHub Issue #24: Additional Authorship Attribution Methods
# https://github.com/craigtrim/pystylometry/issues/24


@dataclass
class KilgarriffResult:
    """Result from Kilgarriff's Chi-squared method.

    Kilgarriff's chi-squared method compares word frequency distributions between
    texts using the chi-squared test. It's particularly effective for authorship
    attribution when comparing frequency profiles of common words.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    References:
        Kilgarriff, A. (2001). Comparing corpora. International Journal of Corpus
            Linguistics, 6(1), 97-133.

    Example:
        >>> result = compute_kilgarriff(text1, text2)
        >>> print(f"Chi-squared: {result.chi_squared:.2f}")
        >>> print(f"P-value: {result.p_value:.4f}")
    """

    chi_squared: float  # Chi-squared statistic
    p_value: float  # Statistical significance (p-value)
    degrees_of_freedom: int  # df for chi-squared test
    feature_count: int  # Number of features (words) compared
    most_distinctive_features: list[tuple[str, float]]  # Words + chi-squared contributions
    metadata: dict[str, Any]  # Frequency tables, expected values, etc.


@dataclass
class KilgarriffDriftResult:
    """Result from Kilgarriff chi-squared drift detection within a single document.

    This result captures stylistic drift patterns by comparing sequential chunks
    of text using Kilgarriff's chi-squared method. It enables detection of
    inconsistent authorship, heavy editing, pasted content, and AI-generated
    text signatures.

    Related GitHub Issues:
        #36 - Kilgarriff Chi-Squared drift detection for intra-document analysis
        https://github.com/craigtrim/pystylometry/issues/36
        #31 - Classical Stylometric Methods from Programming Historian
        https://github.com/craigtrim/pystylometry/issues/31

    Pattern Signatures:
        - consistent: Low, stable χ² across pairs (natural human writing)
        - gradual_drift: Slowly increasing trend (author fatigue, topic shift)
        - sudden_spike: One pair has high χ² (pasted content, different author)
        - suspiciously_uniform: Near-zero variance (possible AI generation)
        - unknown: Insufficient data for classification

    Marketing Name: "Style Drift Detector" / "Consistency Fingerprint"

    References:
        Kilgarriff, A. (2001). Comparing corpora. International Journal of Corpus
            Linguistics, 6(1), 97-133.

    Example:
        >>> result = compute_kilgarriff_drift(text, window_size=1000, stride=500)
        >>> result.pattern  # "consistent", "gradual_drift", "sudden_spike", etc.
        'consistent'
        >>> result.mean_chi_squared  # Average χ² across chunk pairs
        45.2
        >>> result.status  # "success", "marginal_data", "insufficient_data"
        'success'
    """

    # Status (graceful handling of edge cases)
    status: str  # "success", "marginal_data", "insufficient_data"
    status_message: str  # Human-readable explanation

    # Pattern classification
    pattern: str  # "consistent", "gradual_drift", "sudden_spike", "suspiciously_uniform", "unknown"
    pattern_confidence: float  # 0.0-1.0 confidence in classification

    # Holistic metrics (may be NaN if insufficient data)
    mean_chi_squared: float  # Average χ² across all chunk pairs
    std_chi_squared: float  # Standard deviation of χ² values
    max_chi_squared: float  # Highest χ² between any two chunks
    min_chi_squared: float  # Lowest χ² between any two chunks
    max_location: int  # Index of chunk boundary with max χ² (0-indexed)
    trend: float  # Linear regression slope of χ² over chunk pairs

    # Pairwise comparison data
    pairwise_scores: list[dict]  # [{"chunk_pair": (0, 1), "chi_squared": 45.2, "top_words": [...]}]

    # Window configuration (for reproducibility)
    window_size: int
    stride: int
    overlap_ratio: float  # Computed: max(0, 1 - stride/window_size)
    comparison_mode: str  # "sequential", "all_pairs", "fixed_lag"
    window_count: int

    # For all_pairs mode only
    distance_matrix: list[list[float]] | None  # None for sequential/fixed_lag

    # Thresholds used for pattern classification (for transparency)
    thresholds: dict[str, float]

    metadata: dict[str, Any]


# ===== Consistency Module Thresholds =====
# Related to GitHub Issue #36
# These are calibration constants for pattern classification

MIN_WINDOWS = 3  # Bare minimum for variance calculation
RECOMMENDED_WINDOWS = 5  # For reliable pattern classification


@dataclass
class MinMaxResult:
    """Result from Min-Max distance method (Burrows' original method).

    The Min-Max method normalizes feature frequencies using min-max scaling,
    then computes distance between texts. This was Burrows' original approach
    before developing Delta.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    References:
        Burrows, J. F. (1992). Not unless you ask nicely: The interpretative
            nexus between analysis and information. Literary and Linguistic
            Computing, 7(2), 91-109.

    Example:
        >>> result = compute_minmax(text1, text2)
        >>> print(f"MinMax distance: {result.minmax_distance:.3f}")
    """

    minmax_distance: float  # Min-max normalized distance
    feature_count: int  # Number of features used
    most_distinctive_features: list[tuple[str, float]]  # Features + contributions
    metadata: dict[str, Any]  # Normalized frequencies, scaling parameters, etc.


@dataclass
class JohnsBurrowsResult:
    """Result from John's Burrows' variation of Delta.

    John Burrows has developed several variations of the Delta method over
    the years. This captures alternative formulations including Quadratic
    Delta and other distance measures.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    References:
        Burrows, J. (2005). Who wrote Shamela? Verifying the authorship of a
            parodic text. Literary and Linguistic Computing, 20(4), 437-450.

    Example:
        >>> result = compute_johns_delta(text1, text2, method="quadratic")
        >>> print(f"Quadratic Delta: {result.delta_score:.3f}")
    """

    delta_score: float  # Delta distance score
    method: str  # "quadratic", "weighted", "rotated", etc.
    feature_count: int  # Number of MFW used
    most_distinctive_features: list[tuple[str, float]]  # Features + contributions
    metadata: dict[str, Any]  # Method-specific parameters, z-scores, etc.


@dataclass
class CompressionResult:
    """Result from compression-based authorship attribution.

    Compression-based methods use the Normalized Compression Distance (NCD) to
    measure similarity between texts. The intuition is that if two texts are
    similar, compressing them together will yield better compression than
    compressing separately. This approach is language-independent and captures
    deep statistical regularities.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    Formula:
        NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))

        where C(x) is the compressed size of x, and C(xy) is the compressed
        size of x and y concatenated.

    Interpretation:
        - NCD ≈ 0: Texts are very similar
        - NCD ≈ 1: Texts are very different
        - Typical same-author pairs: 0.3-0.6
        - Typical different-author pairs: 0.6-0.9

    References:
        Cilibrasi, R., & Vitányi, P. M. (2005). Clustering by compression.
            IEEE Transactions on Information Theory, 51(4), 1523-1545.

        Benedetto, D., Caglioti, E., & Loreto, V. (2002). Language trees and
            zipping. Physical Review Letters, 88(4), 048702.

    Example:
        >>> result = compute_compression_distance(text1, text2)
        >>> print(f"NCD: {result.ncd:.3f}")
        >>> if result.ncd < 0.5:
        ...     print("Texts likely by same author")
    """

    ncd: float  # Normalized Compression Distance [0, 1+]
    compressor: str  # Compression algorithm used (e.g., "gzip", "zlib", "bz2")
    text1_compressed_size: int  # Compressed size of text1 alone
    text2_compressed_size: int  # Compressed size of text2 alone
    combined_compressed_size: int  # Compressed size of concatenated texts
    metadata: dict[str, Any]  # Raw sizes, compression ratios, etc.


# ===== Rhythm and Prosody Results =====
# Related to GitHub Issue #25: Rhythm and Prosody Metrics
# https://github.com/craigtrim/pystylometry/issues/25


@dataclass
class RhythmProsodyResult:
    """Result from rhythm and prosody analysis.

    Rhythm and prosody metrics capture the musical qualities of written language,
    including stress patterns, syllable rhythms, and phonological features. While
    these are typically studied in spoken language, written text preserves many
    rhythmic patterns that vary by author and genre.

    Related GitHub Issue:
        #25 - Rhythm and Prosody Metrics
        https://github.com/craigtrim/pystylometry/issues/25

    Features analyzed:
        - Syllable patterns and stress patterns
        - Rhythmic regularity (coefficient of variation of syllable counts)
        - Phonological features (alliteration, assonance)
        - Syllable complexity (consonant clusters)
        - Sentence rhythm (alternating long/short sentences)
        - Polysyllabic word ratio

    References:
        Lea, R. B., Mulligan, E. J., & Walton, J. H. (2005). Sentence rhythm and
            text comprehension. Memory & Cognition, 33(3), 388-396.
        Louwerse, M. M., & Benesh, N. (2012). Representing spatial structure through
            maps and language: Lord of the Rings encodes the spatial structure of
            Middle Earth. Cognitive Science, 36(8), 1556-1569.

    Example:
        >>> result = compute_rhythm_prosody("Sample text with rhythm...")
        >>> print(f"Syllables per word: {result.mean_syllables_per_word:.2f}")
        >>> print(f"Rhythmic regularity: {result.rhythmic_regularity:.3f}")
        >>> print(f"Alliteration density: {result.alliteration_density:.2f}")
    """

    # Syllable patterns
    mean_syllables_per_word: float  # Average syllables per word
    syllable_std_dev: float  # Std dev of syllables per word
    polysyllabic_ratio: float  # Words with 3+ syllables / total
    monosyllabic_ratio: float  # Single-syllable words / total

    # Rhythmic regularity
    rhythmic_regularity: float  # 1 / CV of syllable counts (higher = more regular)
    syllable_cv: float  # Coefficient of variation of syllables per word
    stress_pattern_entropy: float  # Entropy of stress patterns

    # Sentence rhythm
    sentence_length_alternation: float  # Degree of long/short alternation
    sentence_rhythm_score: float  # Composite rhythm score

    # Phonological features
    alliteration_density: float  # Alliterative word pairs per 100 words
    assonance_density: float  # Assonant word pairs per 100 words
    consonance_density: float  # Consonant word pairs per 100 words

    # Syllable complexity
    mean_consonant_cluster_length: float  # Avg consonants in clusters
    initial_cluster_ratio: float  # Words starting with clusters / total
    final_cluster_ratio: float  # Words ending with clusters / total

    # Stress patterns (estimated for written text)
    iambic_ratio: float  # Iambic patterns (unstressed-stressed) / total
    trochaic_ratio: float  # Trochaic patterns (stressed-unstressed) / total
    dactylic_ratio: float  # Dactylic patterns / total
    anapestic_ratio: float  # Anapestic patterns / total

    metadata: dict[str, Any]  # Syllable counts, stress patterns, phoneme data, etc.


# ===== Dialect Detection Results =====
# Related to GitHub Issue #35: Dialect detection with extensible JSON markers
# https://github.com/craigtrim/pystylometry/issues/35
# Related to GitHub Issue #30: Whonix stylometry features
# https://github.com/craigtrim/pystylometry/issues/30


@dataclass
class DialectResult:
    """Result from dialect detection analysis.

    Dialect detection identifies regional linguistic preferences (British vs.
    American English) and measures text markedness - how far the text deviates
    from "unmarked" standard English. This analysis uses an extensible JSON-based
    marker database covering vocabulary, spelling patterns, grammar patterns,
    punctuation conventions, and idiomatic expressions.

    The analysis follows the chunking pattern from Issue #27, computing metrics
    per chunk and providing distributions for stylometric fingerprinting. Dialect
    markers are sparse, so variance across chunks can reveal mixed authorship
    (e.g., a UK speaker using ChatGPT-generated American English content).

    Related GitHub Issues:
        #35 - Dialect detection with extensible JSON markers
        https://github.com/craigtrim/pystylometry/issues/35
        #30 - Whonix stylometry features (regional linguistic preferences)
        https://github.com/craigtrim/pystylometry/issues/30
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    Theoretical Background:
        Markedness theory (Battistella, 1990) informs the markedness_score:
        marked forms stand out against "standard" written English. High
        markedness suggests intentional stylistic choice or strong dialect
        identity. Dialectometry (Goebl, 1982; Nerbonne, 2009) provides the
        quantitative framework for holistic dialect measurement.

    Feature Levels:
        Markers are categorized by linguistic level for fine-grained analysis:
        - Phonological: Spelling reflecting pronunciation (colour/color)
        - Morphological: Word formation (-ise/-ize, -our/-or, doubled L)
        - Lexical: Different words for same concept (flat/apartment)
        - Syntactic: Grammar differences (have got/have, collective nouns)

    Eye Dialect vs. True Dialect:
        Following Encyclopedia.com's distinction, "eye dialect" (gonna, wanna)
        indicates informal register, not regional dialect. True dialect markers
        (colour, flat, lorry) indicate actual regional preference.

    References:
        Battistella, Edwin L. "Markedness: The Evaluative Superstructure of
            Language." State University of New York Press, 1990.
        Goebl, Hans. "Dialektometrie: Prinzipien und Methoden des Einsatzes der
            numerischen Taxonomie im Bereich der Dialektgeographie." Verlag der
            Österreichischen Akademie der Wissenschaften, 1982.
        Nerbonne, John. "Data-Driven Dialectology." Language and Linguistics
            Compass, vol. 3, no. 1, 2009, pp. 175-198.
        Labov, William. "The Social Stratification of English in New York City."
            Cambridge University Press, 2006.
        Whonix Project. "Stylometry: Deanonymization Techniques." Whonix Wiki,
            https://www.whonix.org/wiki/Stylometry

    Example:
        >>> result = compute_dialect(text, chunk_size=1000)
        >>> result.dialect  # "british", "american", "mixed", or "neutral"
        'british'
        >>> result.british_score  # Mean across chunks
        0.72
        >>> result.british_score_dist.std  # Variance reveals fingerprint
        0.05
        >>> result.markedness_score  # Deviation from standard English
        0.35
    """

    # Classification result
    dialect: str  # "british", "american", "mixed", "neutral"
    confidence: float  # 0.0-1.0, how confident the classification is

    # Convenient access (mean values across chunks)
    british_score: float  # Mean British marker density (0.0-1.0)
    american_score: float  # Mean American marker density (0.0-1.0)
    markedness_score: float  # Mean deviation from unmarked standard (0.0-1.0)

    # Full distributions for stylometric fingerprinting
    british_score_dist: Distribution
    american_score_dist: Distribution
    markedness_score_dist: Distribution

    # Marker breakdown by linguistic level (aggregated across chunks)
    # Keys: "phonological", "morphological", "lexical", "syntactic"
    markers_by_level: dict[str, dict[str, int]]

    # Detailed marker counts (aggregated across chunks)
    spelling_markers: dict[str, int]  # {"colour": 2, "color": 1}
    vocabulary_markers: dict[str, int]  # {"flat": 1, "apartment": 0}
    grammar_markers: dict[str, int]  # {"have got": 1}

    # Eye dialect (informal register indicators, not true dialect)
    eye_dialect_count: int  # Total eye dialect markers (gonna, wanna, etc.)
    eye_dialect_ratio: float  # Eye dialect per 1000 words

    # Register analysis hints
    register_hints: dict[str, Any]  # {"formality": 0.7, "hedging_density": 0.05}

    # Chunking context
    chunk_size: int
    chunk_count: int

    # Extensible metadata
    metadata: dict[str, Any]


# ===== Unified Analysis Result =====


@dataclass
class AnalysisResult:
    """Unified result from comprehensive stylometric analysis."""

    lexical: dict[str, Any] | None = None
    readability: dict[str, Any] | None = None
    syntactic: dict[str, Any] | None = None
    authorship: dict[str, Any] | None = None
    ngrams: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

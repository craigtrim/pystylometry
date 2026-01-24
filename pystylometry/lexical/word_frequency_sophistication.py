"""Word frequency sophistication metrics for vocabulary analysis.

This module measures vocabulary sophistication by analyzing how common or rare
the words in a text are, based on reference frequency lists from large corpora.
Authors who consistently use less frequent (more sophisticated) vocabulary
will score higher on these metrics.

Related GitHub Issue:
    #15 - Word Frequency Sophistication Metrics
    https://github.com/craigtrim/pystylometry/issues/15

Frequency data sources:
    - COCA (Corpus of Contemporary American English)
    - BNC (British National Corpus)
    - Google N-grams
    - SUBTLEXus (subtitle word frequencies)
    - Academic Word List (AWL)

References:
    Brysbaert, M., & New, B. (2009). Moving beyond Kučera and Francis:
        A critical evaluation of current word frequency norms. Behavior
        Research Methods, Instruments, & Computers, 41(4), 977-990.
    Coxhead, A. (2000). A new academic word list. TESOL Quarterly, 34(2), 213-238.
    Davies, M. (2008-). The Corpus of Contemporary American English (COCA).
"""

from .._types import WordFrequencySophisticationResult


# Academic Word List (AWL) - Coxhead (2000)
# GitHub Issue #15: https://github.com/craigtrim/pystylometry/issues/15
# This is a subset of common academic words. The full AWL contains 570 word families.
# Consider loading from external file for complete list.
ACADEMIC_WORD_LIST = {
    "analyze", "approach", "area", "assess", "assume", "authority",
    "available", "benefit", "concept", "consist", "constitute", "context",
    "contract", "create", "data", "define", "derive", "distribute",
    "economy", "environment", "establish", "estimate", "evident", "export",
    "factor", "finance", "formula", "function", "identify", "income",
    "indicate", "individual", "interpret", "involve", "issue", "labor",
    "legal", "legislate", "major", "method", "occur", "percent", "period",
    "policy", "principle", "proceed", "process", "require", "research",
    "respond", "role", "section", "sector", "significant", "similar",
    "source", "specific", "structure", "theory", "vary",
    # Add more as needed - this is just a sample
}


def compute_word_frequency_sophistication(
    text: str,
    frequency_corpus: str = "coca",
    rare_threshold: int = 10000,
    common_threshold: int = 1000,
) -> WordFrequencySophisticationResult:
    """
    Compute word frequency sophistication metrics.

    Analyzes vocabulary sophistication by comparing text words against
    reference frequency lists from large corpora. Words are classified
    as common, rare, or academic based on their frequency ranks in the
    reference corpus.

    Related GitHub Issue:
        #15 - Word Frequency Sophistication Metrics
        https://github.com/craigtrim/pystylometry/issues/15

    Sophistication is a key indicator of writing quality and expertise:
        - Academic writing uses more low-frequency, technical words
        - Fiction uses moderate-frequency, descriptive words
        - Journalism uses high-frequency, accessible words
        - Authors with larger vocabularies use rarer words
        - Native speakers use different frequency profiles than learners

    Applications:
        - Assessing vocabulary richness beyond simple TTR
        - Comparing writing sophistication across authors or genres
        - Tracking vocabulary development over time
        - Identifying register (formal vs. informal)
        - Detecting text difficulty level

    Frequency bands (example for 100,000-word corpus):
        - Very common: Rank 1-1,000 (top 1%)
        - Common: Rank 1,001-5,000 (top 5%)
        - Moderate: Rank 5,001-10,000 (top 10%)
        - Rare: Rank 10,001-20,000 (top 20%)
        - Very rare: Rank 20,001+ (bottom 80%)

    Args:
        text: Input text to analyze. Should contain at least 50+ words
              for meaningful statistics. Shorter texts may have unreliable
              sophistication metrics.
        frequency_corpus: Reference corpus to use for frequency data.
                          Options: "coca", "bnc", "google_ngrams", "subtlex"
                          Default is "coca" (Corpus of Contemporary American English).
        rare_threshold: Frequency rank threshold for "rare" words. Words with
                        rank > rare_threshold are considered rare. Default 10,000.
        common_threshold: Frequency rank threshold for "common" words. Words with
                          rank <= common_threshold are considered common. Default 1,000.

    Returns:
        WordFrequencySophisticationResult containing:
            - mean_frequency_rank: Average frequency rank (lower = more common)
            - median_frequency_rank: Median frequency rank
            - rare_word_ratio: Proportion of words beyond rare_threshold
            - common_word_ratio: Proportion of words within common_threshold
            - academic_word_ratio: Proportion of Academic Word List words
            - advanced_word_ratio: Proportion of sophisticated vocabulary
            - frequency_band_distribution: Distribution across frequency bands
            - rarest_words: Least frequent words with their ranks
            - most_common_words: Most frequent words with their ranks
            - metadata: Corpus info, thresholds, counts, etc.

    Example:
        >>> result = compute_word_frequency_sophistication("Sample academic text...")
        >>> print(f"Mean frequency rank: {result.mean_frequency_rank:.1f}")
        Mean frequency rank: 4523.7
        >>> print(f"Rare word ratio: {result.rare_word_ratio:.3f}")
        Rare word ratio: 0.234
        >>> print(f"Academic words: {result.academic_word_ratio:.3f}")
        Academic words: 0.156

        >>> # Compare authors
        >>> author1 = compute_word_frequency_sophistication("Text by author 1...")
        >>> author2 = compute_word_frequency_sophistication("Text by author 2...")
        >>> print(f"Author 1 mean rank: {author1.mean_frequency_rank:.1f}")
        >>> print(f"Author 2 mean rank: {author2.mean_frequency_rank:.1f}")
        >>> # Lower rank = uses more common words

    Note:
        - Frequency ranks are corpus-specific (COCA ranks differ from BNC ranks)
        - Words not in reference corpus are assigned maximum rank + 1
        - Case-insensitive matching (all words lowercased)
        - Lemmatization recommended but not required
        - Function words (the, of, and) dominate high-frequency ranks
        - Stopword removal can provide cleaner sophistication metrics
        - Academic Word List is field-independent academic vocabulary
    """
    # TODO: Implement word frequency sophistication analysis
    # GitHub Issue #15: https://github.com/craigtrim/pystylometry/issues/15
    #
    # Implementation steps:
    # 1. Load frequency list for specified corpus (COCA, BNC, etc.)
    #    - Frequency lists should be: {word: rank} dictionaries
    #    - Load from external file (e.g., coca_frequencies.json)
    #    - Cache loaded frequencies for performance
    # 2. Tokenize input text and lowercase all words
    # 3. For each word, look up frequency rank:
    #    - If word in frequency dict, use its rank
    #    - If word not found, assign max_rank + 1 (very rare/unknown)
    # 4. Calculate mean and median frequency ranks
    # 5. Count words in different frequency bands:
    #    - Very common: rank <= common_threshold
    #    - Common: common_threshold < rank <= 5000
    #    - Moderate: 5000 < rank <= rare_threshold
    #    - Rare: rare_threshold < rank <= 20000
    #    - Very rare: rank > 20000
    # 6. Calculate ratios:
    #    - rare_word_ratio: words with rank > rare_threshold
    #    - common_word_ratio: words with rank <= common_threshold
    #    - academic_word_ratio: words in ACADEMIC_WORD_LIST
    #    - advanced_word_ratio: rare + academic words
    # 7. Find rarest words (highest ranks) with their ranks
    # 8. Find most common words (lowest ranks) with their ranks
    # 9. Build frequency band distribution dict
    # 10. Assemble metadata (corpus, thresholds, total words, etc.)
    # 11. Return WordFrequencySophisticationResult
    #
    # Metadata should include:
    #   - frequency_corpus: Which corpus was used
    #   - rare_threshold: Threshold for rare classification
    #   - common_threshold: Threshold for common classification
    #   - total_words: Total words analyzed
    #   - unknown_words: Words not in frequency list
    #   - unknown_word_ratio: Unknown words / total
    #   - frequency_list_size: Size of reference frequency list
    #
    # Data files needed:
    #   - coca_frequencies.json: {word: rank} for COCA
    #   - bnc_frequencies.json: {word: rank} for BNC
    #   - subtlex_frequencies.json: {word: rank} for SUBTLEXus
    #   - academic_word_list.json: Complete AWL word families
    #
    # Consider:
    #   - Should stopwords be excluded from analysis?
    #   - Should lemmatization be applied before lookup?
    #   - How to handle compound words or multi-word expressions?
    #   - Should word forms or lemmas be used for Academic Word List?
    raise NotImplementedError(
        "Word frequency sophistication not yet implemented. "
        "See GitHub Issue #15: https://github.com/craigtrim/pystylometry/issues/15"
    )

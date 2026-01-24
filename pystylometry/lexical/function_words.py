"""Function word analysis for authorship attribution.

Function words (determiners, prepositions, conjunctions, pronouns, auxiliary
verbs) are highly frequent, content-independent words that authors use
subconsciously and consistently across different topics. This makes them
powerful markers for authorship attribution.

Related GitHub Issue:
    #13 - Function Word Analysis
    https://github.com/craigtrim/pystylometry/issues/13

Features implemented:
    - Frequency profiles for all function word categories
    - Ratios for specific grammatical categories
    - Most/least frequently used function words
    - Function word diversity metrics

Function word categories:
    - Determiners: the, a, an, this, that, these, those, my, your, etc.
    - Prepositions: in, on, at, by, for, with, from, to, of, etc.
    - Conjunctions: and, but, or, nor, for, yet, so, because, although, etc.
    - Pronouns: I, you, he, she, it, we, they, me, him, her, us, them, etc.
    - Auxiliary verbs: be, have, do, can, will, shall, may, must, etc.
    - Particles: up, down, out, off, over, away, back, etc.

References:
    Mosteller, F., & Wallace, D. L. (1964). Inference and disputed authorship:
        The Federalist. Addison-Wesley.
    Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide
        to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.
    Argamon, S., & Levitan, S. (2005). Measuring the usefulness of function
        words for authorship attribution. ACH/ALLC.
"""

from .._types import FunctionWordResult


# Function word lists for English
# GitHub Issue #13: https://github.com/craigtrim/pystylometry/issues/13
# These lists should be comprehensive and cover all major function word categories.
# Consider loading from external resource files for easier maintenance.

# Determiners (articles, demonstratives, possessives, quantifiers)
DETERMINERS = {
    "the", "a", "an",  # Articles
    "this", "that", "these", "those",  # Demonstratives
    "my", "your", "his", "her", "its", "our", "their",  # Possessive determiners
    "some", "any", "no", "every", "each", "either", "neither",  # Quantifiers
    "much", "many", "more", "most", "few", "fewer", "less", "least",
    "all", "both", "half", "several", "enough",
}

# Prepositions (locative, temporal, other)
PREPOSITIONS = {
    "in", "on", "at", "by", "for", "with", "from", "to", "of",
    "about", "above", "across", "after", "against", "along", "among",
    "around", "as", "before", "behind", "below", "beneath", "beside",
    "between", "beyond", "but", "concerning", "considering", "despite",
    "down", "during", "except", "inside", "into", "like", "near",
    "off", "onto", "out", "outside", "over", "past", "regarding",
    "since", "through", "throughout", "till", "toward", "under",
    "underneath", "until", "up", "upon", "via", "within", "without",
}

# Conjunctions (coordinating, subordinating, correlative)
CONJUNCTIONS = {
    # Coordinating
    "and", "but", "or", "nor", "for", "yet", "so",
    # Subordinating
    "although", "because", "since", "unless", "while", "if", "when",
    "where", "after", "before", "once", "until", "as", "though",
    "even", "whereas", "wherever", "whenever",
    # Correlative components
    "either", "neither", "both", "whether",
}

# Pronouns (personal, possessive, reflexive, demonstrative, relative, indefinite)
PRONOUNS = {
    # Personal (subject)
    "i", "you", "he", "she", "it", "we", "they",
    # Personal (object)
    "me", "him", "her", "us", "them",
    # Possessive
    "mine", "yours", "his", "hers", "its", "ours", "theirs",
    # Reflexive
    "myself", "yourself", "himself", "herself", "itself",
    "ourselves", "yourselves", "themselves",
    # Demonstrative
    "this", "that", "these", "those",
    # Relative
    "who", "whom", "whose", "which", "that",
    # Indefinite
    "anybody", "anyone", "anything", "everybody", "everyone",
    "everything", "nobody", "no one", "nothing", "somebody",
    "someone", "something", "one",
}

# Auxiliary verbs (modal, primary)
AUXILIARIES = {
    # Modals
    "can", "could", "may", "might", "must", "shall", "should",
    "will", "would", "ought",
    # Primary auxiliaries (be, have, do)
    "am", "is", "are", "was", "were", "be", "being", "been",
    "have", "has", "had", "having",
    "do", "does", "did", "doing",
}

# Particles (often used with phrasal verbs)
PARTICLES = {
    "up", "down", "out", "off", "over", "in", "away",
    "back", "on", "along", "forth", "apart", "aside",
}


def compute_function_words(text: str) -> FunctionWordResult:
    """
    Compute function word frequency profiles for authorship analysis.

    Function words are closed-class words (determiners, prepositions,
    conjunctions, pronouns, auxiliaries) that authors use largely
    subconsciously and consistently. Their frequency patterns are
    powerful authorship markers because they're independent of topic.

    Related GitHub Issue:
        #13 - Function Word Analysis
        https://github.com/craigtrim/pystylometry/issues/13

    Why function words matter for authorship:
        1. Topic-independent: Used consistently across different subjects
        2. Subconscious usage: Authors don't deliberately vary their use
        3. High frequency: Appear often enough for reliable statistics
        4. Stable over time: Authors' function word patterns remain consistent
        5. Discriminative power: Different authors show distinct patterns

    Classic example: Mosteller & Wallace (1964) used function word
    frequencies to resolve the disputed authorship of the Federalist Papers,
    distinguishing between Hamilton and Madison based on their use of
    "while" vs. "whilst", "upon" vs. "on", etc.

    Args:
        text: Input text to analyze. Should be at least a few hundred words
              for reliable statistics. Function word analysis works best with
              longer texts (1000+ words) where frequency patterns stabilize.

    Returns:
        FunctionWordResult containing:
            - Ratios for each function word category (per total words)
            - Total function word ratio
            - Function word diversity (unique / total function words)
            - Most/least frequent function words with counts
            - Full distribution of all function words used
            - Metadata with category-specific counts

    Example:
        >>> result = compute_function_words("Sample text for analysis...")
        >>> print(f"Determiner ratio: {result.determiner_ratio:.3f}")
        Determiner ratio: 0.156
        >>> print(f"Preposition ratio: {result.preposition_ratio:.3f}")
        Preposition ratio: 0.112
        >>> print(f"Total function words: {result.total_function_word_ratio:.3f}")
        Total function words: 0.487
        >>> print(f"Most frequent: {result.most_frequent_function_words[:3]}")
        Most frequent: [('the', 45), ('of', 32), ('to', 28)]

        >>> # Authorship comparison example
        >>> text1 = "Text by author 1..."
        >>> text2 = "Text by author 2..."
        >>> r1 = compute_function_words(text1)
        >>> r2 = compute_function_words(text2)
        >>> # Compare determiner ratios, preposition preferences, etc.

    Note:
        - Case-insensitive matching (all text lowercased for matching)
        - Tokenization by whitespace and punctuation
        - Words must match exactly (no stemming or lemmatization)
        - Multi-word function words like "no one" are handled as separate tokens
        - Empty or very short texts may have unreliable ratios
        - Some words appear in multiple categories (e.g., "that" is both
          determiner and pronoun) - each category is counted independently
    """
    # TODO: Implement function word analysis
    # GitHub Issue #13: https://github.com/craigtrim/pystylometry/issues/13
    #
    # Implementation steps:
    # 1. Tokenize text into words (lowercase, strip punctuation)
    # 2. Count total words for ratio calculations
    # 3. Initialize counters for each function word category
    # 4. Iterate through tokens and count matches in each category:
    #    - Count determiners
    #    - Count prepositions
    #    - Count conjunctions
    #    - Count pronouns
    #    - Count auxiliaries
    #    - Count particles
    # 5. Build full distribution of all function words (word -> count)
    # 6. Calculate ratios (category count / total words)
    # 7. Calculate total function word ratio
    # 8. Calculate function word diversity (unique function words / total function word tokens)
    # 9. Find most frequent function words (sort distribution by count descending)
    # 10. Find least frequent function words (sort distribution by count ascending)
    # 11. Calculate metadata (total counts per category, word lists, etc.)
    # 12. Handle edge cases (empty text, no function words found, etc.)
    # 13. Return FunctionWordResult
    #
    # Metadata should include:
    #   - total_word_count: Total words in text
    #   - total_function_word_count: Total function word tokens
    #   - unique_function_word_count: Unique function words used
    #   - determiner_count: Total determiner tokens
    #   - preposition_count: Total preposition tokens
    #   - conjunction_count: Total conjunction tokens
    #   - pronoun_count: Total pronoun tokens
    #   - auxiliary_count: Total auxiliary tokens
    #   - particle_count: Total particle tokens
    #   - determiner_list: List of determiners found
    #   - preposition_list: List of prepositions found
    #   (etc. for other categories)
    #
    # Consider:
    #   - Should overlapping words (e.g., "that" in multiple categories) be
    #     counted in all applicable categories, or only once?
    #     Answer: Count in all applicable categories for category ratios,
    #     but count only once for total function word ratio.
    #   - How to handle contractions (e.g., "don't" contains "do")?
    #     Answer: Expand contractions first, or handle as special cases.
    #   - Should we weight by relative importance?
    #     Answer: No, keep raw frequencies for maximum transparency.
    raise NotImplementedError(
        "Function word analysis not yet implemented. "
        "See GitHub Issue #13: https://github.com/craigtrim/pystylometry/issues/13"
    )

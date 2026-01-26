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

from .._types import Distribution, FunctionWordResult, make_distribution

# Function word lists for English
# GitHub Issue #13: https://github.com/craigtrim/pystylometry/issues/13
# These lists should be comprehensive and cover all major function word categories.
# Consider loading from external resource files for easier maintenance.

# Determiners (articles, demonstratives, possessives, quantifiers)
DETERMINERS = {
    "the",
    "a",
    "an",  # Articles
    "this",
    "that",
    "these",
    "those",  # Demonstratives
    "my",
    "your",
    "his",
    "her",
    "its",
    "our",
    "their",  # Possessive determiners
    "some",
    "any",
    "no",
    "every",
    "each",
    "either",
    "neither",  # Quantifiers
    "much",
    "many",
    "more",
    "most",
    "few",
    "fewer",
    "less",
    "least",
    "all",
    "both",
    "half",
    "several",
    "enough",
}

# Prepositions (locative, temporal, other)
PREPOSITIONS = {
    "in",
    "on",
    "at",
    "by",
    "for",
    "with",
    "from",
    "to",
    "of",
    "about",
    "above",
    "across",
    "after",
    "against",
    "along",
    "among",
    "around",
    "as",
    "before",
    "behind",
    "below",
    "beneath",
    "beside",
    "between",
    "beyond",
    "but",
    "concerning",
    "considering",
    "despite",
    "down",
    "during",
    "except",
    "inside",
    "into",
    "like",
    "near",
    "off",
    "onto",
    "out",
    "outside",
    "over",
    "past",
    "regarding",
    "since",
    "through",
    "throughout",
    "till",
    "toward",
    "under",
    "underneath",
    "until",
    "up",
    "upon",
    "via",
    "within",
    "without",
}

# Conjunctions (coordinating, subordinating, correlative)
CONJUNCTIONS = {
    # Coordinating
    "and",
    "but",
    "or",
    "nor",
    "for",
    "yet",
    "so",
    # Subordinating
    "although",
    "because",
    "since",
    "unless",
    "while",
    "if",
    "when",
    "where",
    "after",
    "before",
    "once",
    "until",
    "as",
    "though",
    "even",
    "whereas",
    "wherever",
    "whenever",
    # Correlative components
    "either",
    "neither",
    "both",
    "whether",
}

# Pronouns (personal, possessive, reflexive, demonstrative, relative, indefinite)
PRONOUNS = {
    # Personal (subject)
    "i",
    "you",
    "he",
    "she",
    "it",
    "we",
    "they",
    # Personal (object)
    "me",
    "him",
    "her",
    "us",
    "them",
    # Possessive
    "mine",
    "yours",
    "his",
    "hers",
    "its",
    "ours",
    "theirs",
    # Reflexive
    "myself",
    "yourself",
    "himself",
    "herself",
    "itself",
    "ourselves",
    "yourselves",
    "themselves",
    # Demonstrative
    "this",
    "that",
    "these",
    "those",
    # Relative
    "who",
    "whom",
    "whose",
    "which",
    "that",
    # Indefinite
    "anybody",
    "anyone",
    "anything",
    "everybody",
    "everyone",
    "everything",
    "nobody",
    "no one",
    "nothing",
    "somebody",
    "someone",
    "something",
    "one",
}

# Auxiliary verbs (modal, primary)
AUXILIARIES = {
    # Modals
    "can",
    "could",
    "may",
    "might",
    "must",
    "shall",
    "should",
    "will",
    "would",
    "ought",
    # Primary auxiliaries (be, have, do)
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "being",
    "been",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
}

# Particles (often used with phrasal verbs)
PARTICLES = {
    "up",
    "down",
    "out",
    "off",
    "over",
    "in",
    "away",
    "back",
    "on",
    "along",
    "forth",
    "apart",
    "aside",
}


def compute_function_words(text: str, chunk_size: int = 1000) -> FunctionWordResult:
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
    # Step 1: Create union set of all function words (for total ratio calculation)
    all_function_words = (
        DETERMINERS | PREPOSITIONS | CONJUNCTIONS | PRONOUNS | AUXILIARIES | PARTICLES
    )

    # Step 2: Tokenize text (lowercase, split on whitespace, strip punctuation)
    if not text or not text.strip():
        # Handle empty text edge case
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return FunctionWordResult(
            determiner_ratio=0.0,
            preposition_ratio=0.0,
            conjunction_ratio=0.0,
            pronoun_ratio=0.0,
            auxiliary_ratio=0.0,
            particle_ratio=0.0,
            total_function_word_ratio=0.0,
            function_word_diversity=0.0,
            most_frequent_function_words=[],
            least_frequent_function_words=[],
            function_word_distribution={},
            determiner_ratio_dist=empty_dist,
            preposition_ratio_dist=empty_dist,
            conjunction_ratio_dist=empty_dist,
            pronoun_ratio_dist=empty_dist,
            auxiliary_ratio_dist=empty_dist,
            particle_ratio_dist=empty_dist,
            total_function_word_ratio_dist=empty_dist,
            function_word_diversity_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=0,
            metadata={
                "total_word_count": 0,
                "total_function_word_count": 0,
                "unique_function_word_count": 0,
                "determiner_count": 0,
                "preposition_count": 0,
                "conjunction_count": 0,
                "pronoun_count": 0,
                "auxiliary_count": 0,
                "particle_count": 0,
                "determiner_list": [],
                "preposition_list": [],
                "conjunction_list": [],
                "pronoun_list": [],
                "auxiliary_list": [],
                "particle_list": [],
                "overlapping_words": [],
                "overlapping_word_categories": {},
            },
        )

    # Lowercase entire text
    text_lower = text.lower()

    # Split on whitespace
    raw_tokens = text_lower.split()

    # Comprehensive punctuation set for stripping
    punctuation_chars = set(".,!?;:'\"()[]{}/-—–…*&@#$%^~`\\|<>«»„''‚'")

    # Strip punctuation from each token
    tokens = []
    for token in raw_tokens:
        # Strip leading and trailing punctuation
        clean_token = token.strip("".join(punctuation_chars))
        if clean_token:  # Only add non-empty tokens
            tokens.append(clean_token)

    total_words = len(tokens)

    # Step 3: Initialize counters for each category
    determiner_count = 0
    preposition_count = 0
    conjunction_count = 0
    pronoun_count = 0
    auxiliary_count = 0
    particle_count = 0

    # Step 4: Count tokens in each category (overlapping allowed)
    for token in tokens:
        if token in DETERMINERS:
            determiner_count += 1
        if token in PREPOSITIONS:
            preposition_count += 1
        if token in CONJUNCTIONS:
            conjunction_count += 1
        if token in PRONOUNS:
            pronoun_count += 1
        if token in AUXILIARIES:
            auxiliary_count += 1
        if token in PARTICLES:
            particle_count += 1

    # Step 5: Build distribution (count each function word only once per token)
    function_word_counts: dict[str, int] = {}
    for token in tokens:
        if token in all_function_words:
            function_word_counts[token] = function_word_counts.get(token, 0) + 1

    # Step 6: Calculate ratios
    if total_words > 0:
        determiner_ratio = determiner_count / total_words
        preposition_ratio = preposition_count / total_words
        conjunction_ratio = conjunction_count / total_words
        pronoun_ratio = pronoun_count / total_words
        auxiliary_ratio = auxiliary_count / total_words
        particle_ratio = particle_count / total_words

        total_function_word_count = sum(function_word_counts.values())
        total_function_word_ratio = total_function_word_count / total_words
    else:
        determiner_ratio = 0.0
        preposition_ratio = 0.0
        conjunction_ratio = 0.0
        pronoun_ratio = 0.0
        auxiliary_ratio = 0.0
        particle_ratio = 0.0
        total_function_word_count = 0
        total_function_word_ratio = 0.0

    # Step 7: Calculate diversity
    unique_function_word_count = len(function_word_counts)
    if total_function_word_count > 0:
        function_word_diversity = unique_function_word_count / total_function_word_count
    else:
        function_word_diversity = 0.0

    # Step 8: Find most/least frequent function words
    if function_word_counts:
        # Sort by count descending
        sorted_by_count = sorted(function_word_counts.items(), key=lambda x: x[1], reverse=True)

        # Top 10 most frequent
        most_frequent = sorted_by_count[:10]

        # Bottom 10 least frequent (reverse to get ascending order)
        least_frequent = sorted_by_count[-10:]
        least_frequent.reverse()
    else:
        most_frequent = []
        least_frequent = []

    # Step 9: Build category word lists (sorted)
    determiner_list = sorted([w for w in function_word_counts if w in DETERMINERS])
    preposition_list = sorted([w for w in function_word_counts if w in PREPOSITIONS])
    conjunction_list = sorted([w for w in function_word_counts if w in CONJUNCTIONS])
    pronoun_list = sorted([w for w in function_word_counts if w in PRONOUNS])
    auxiliary_list = sorted([w for w in function_word_counts if w in AUXILIARIES])
    particle_list = sorted([w for w in function_word_counts if w in PARTICLES])

    # Step 10: Find overlapping words (words in multiple categories)
    overlapping_words = []
    overlapping_word_categories: dict[str, list[str]] = {}

    for word in function_word_counts:
        categories = []
        if word in DETERMINERS:
            categories.append("determiner")
        if word in PREPOSITIONS:
            categories.append("preposition")
        if word in CONJUNCTIONS:
            categories.append("conjunction")
        if word in PRONOUNS:
            categories.append("pronoun")
        if word in AUXILIARIES:
            categories.append("auxiliary")
        if word in PARTICLES:
            categories.append("particle")

        if len(categories) > 1:
            overlapping_words.append(word)
            overlapping_word_categories[word] = categories

    overlapping_words.sort()

    # Step 11: Create single-value distributions (analysis is done on full text)
    determiner_ratio_dist = make_distribution([determiner_ratio])
    preposition_ratio_dist = make_distribution([preposition_ratio])
    conjunction_ratio_dist = make_distribution([conjunction_ratio])
    pronoun_ratio_dist = make_distribution([pronoun_ratio])
    auxiliary_ratio_dist = make_distribution([auxiliary_ratio])
    particle_ratio_dist = make_distribution([particle_ratio])
    total_function_word_ratio_dist = make_distribution([total_function_word_ratio])
    function_word_diversity_dist = make_distribution([function_word_diversity])

    # Step 12: Build metadata
    metadata = {
        "total_word_count": total_words,
        "total_function_word_count": total_function_word_count,
        "unique_function_word_count": unique_function_word_count,
        "determiner_count": determiner_count,
        "preposition_count": preposition_count,
        "conjunction_count": conjunction_count,
        "pronoun_count": pronoun_count,
        "auxiliary_count": auxiliary_count,
        "particle_count": particle_count,
        "determiner_list": determiner_list,
        "preposition_list": preposition_list,
        "conjunction_list": conjunction_list,
        "pronoun_list": pronoun_list,
        "auxiliary_list": auxiliary_list,
        "particle_list": particle_list,
        "overlapping_words": overlapping_words,
        "overlapping_word_categories": overlapping_word_categories,
    }

    # Step 13: Return result
    return FunctionWordResult(
        determiner_ratio=determiner_ratio,
        preposition_ratio=preposition_ratio,
        conjunction_ratio=conjunction_ratio,
        pronoun_ratio=pronoun_ratio,
        auxiliary_ratio=auxiliary_ratio,
        particle_ratio=particle_ratio,
        total_function_word_ratio=total_function_word_ratio,
        function_word_diversity=function_word_diversity,
        most_frequent_function_words=most_frequent,
        least_frequent_function_words=least_frequent,
        function_word_distribution=function_word_counts,
        determiner_ratio_dist=determiner_ratio_dist,
        preposition_ratio_dist=preposition_ratio_dist,
        conjunction_ratio_dist=conjunction_ratio_dist,
        pronoun_ratio_dist=pronoun_ratio_dist,
        auxiliary_ratio_dist=auxiliary_ratio_dist,
        particle_ratio_dist=particle_ratio_dist,
        total_function_word_ratio_dist=total_function_word_ratio_dist,
        function_word_diversity_dist=function_word_diversity_dist,
        chunk_size=chunk_size,
        chunk_count=1,  # Single pass analysis
        metadata=metadata,
    )

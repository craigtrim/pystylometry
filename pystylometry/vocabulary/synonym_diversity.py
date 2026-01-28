"""Synonym diversity analysis for authorship attribution.

This module measures how varied an author's word choices are within semantic
fields. Authors develop habitual preferences for specific words over their
synonyms (e.g., always choosing "start" over "begin" or "commence"),
creating reliable stylometric signatures that persist across topics.

Design Philosophy — Data Injection:
    This module is architecturally decoupled from any specific lexical
    resource. Rather than bundling WordNet or another synonym database,
    the function accepts an external synonym_map parameter: a simple
    dict[str, str] mapping lowercase words to cluster identifiers. This
    design allows users to:

    - Use WordNet synsets as clusters
    - Supply a custom thesaurus in JSON format
    - Use domain-specific synonym groups
    - Combine multiple data sources
    - Test with minimal inline data

    The analysis code handles tokenization, cluster assignment, diversity
    scoring, and repetition metrics — all independent of the data source.

Expected synonym_map Format:
    A dict[str, str] mapping lowercase words to cluster identifiers.
    Words mapping to the same cluster ID are treated as synonyms.
    Cluster IDs can be any string — they serve only as grouping keys.

    Example::

        {
            "said": "communication_verb",
            "stated": "communication_verb",
            "mentioned": "communication_verb",
            "remarked": "communication_verb",
            "noted": "communication_verb",
            "big": "size_adjective",
            "large": "size_adjective",
            "huge": "size_adjective",
            "enormous": "size_adjective",
            "start": "begin_verb",
            "begin": "begin_verb",
            "commence": "begin_verb",
            "initiate": "begin_verb",
        }

Related GitHub Issue:
    #30 - Whonix stylometric features (synonym choice)
    https://github.com/craigtrim/pystylometry/issues/30

Whonix Source:
    The Whonix Stylometry documentation identifies "synonym choice" as a
    deanonymization vector. Authors develop habitual preferences for
    specific words over their synonyms, creating reliable stylometric
    signatures.
    https://www.whonix.org/wiki/Stylometry

References:
    Argamon, S., et al. (2007). Stylistic text classification using
        functional lexical features. JASIST, 58(6), 802-822.
    Koppel, M., Schler, J., & Argamon, S. (2009). Computational methods
        in authorship attribution. JASIST, 60(1), 9-26.
    Stamatatos, E. (2009). A survey of modern authorship attribution
        methods. JASIST, 60(3), 538-556.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from .._types import SynonymDiversityResult

# =============================================================================
# MINIMAL DEFAULT SYNONYM MAP
# =============================================================================
# A small default synonym map for basic testing and demonstration. This is
# intentionally minimal — users should supply a comprehensive map from
# WordNet, a custom thesaurus, or another lexical resource for production
# use. The default map covers a few common semantic fields to enable
# out-of-the-box testing.
#
# Cluster IDs follow a simple naming convention: {semantic_field}_{pos}
# where pos is the part of speech (verb, adj, noun, adv).

DEFAULT_SYNONYM_MAP: dict[str, str] = {
    # Communication verbs — how the author attributes speech
    "said": "communication_verb",
    "stated": "communication_verb",
    "mentioned": "communication_verb",
    "remarked": "communication_verb",
    "noted": "communication_verb",
    "declared": "communication_verb",
    "announced": "communication_verb",
    "explained": "communication_verb",
    "reported": "communication_verb",
    "claimed": "communication_verb",
    # Size adjectives — how the author describes magnitude
    "big": "size_adj",
    "large": "size_adj",
    "huge": "size_adj",
    "enormous": "size_adj",
    "vast": "size_adj",
    "massive": "size_adj",
    "immense": "size_adj",
    "small": "smallness_adj",
    "tiny": "smallness_adj",
    "little": "smallness_adj",
    "minute": "smallness_adj",
    "miniature": "smallness_adj",
    # Begin/start verbs — common synonym choice pair
    "start": "begin_verb",
    "begin": "begin_verb",
    "commence": "begin_verb",
    "initiate": "begin_verb",
    "launch": "begin_verb",
    # End/finish verbs
    "end": "end_verb",
    "finish": "end_verb",
    "conclude": "end_verb",
    "complete": "end_verb",
    "terminate": "end_verb",
    # Movement verbs
    "walk": "movement_verb",
    "stroll": "movement_verb",
    "wander": "movement_verb",
    "stride": "movement_verb",
    "amble": "movement_verb",
    "march": "movement_verb",
    # Thinking verbs
    "think": "cognition_verb",
    "believe": "cognition_verb",
    "consider": "cognition_verb",
    "ponder": "cognition_verb",
    "reflect": "cognition_verb",
    "contemplate": "cognition_verb",
    # Good adjectives
    "good": "positive_adj",
    "great": "positive_adj",
    "excellent": "positive_adj",
    "wonderful": "positive_adj",
    "fantastic": "positive_adj",
    "superb": "positive_adj",
    # Bad adjectives
    "bad": "negative_adj",
    "terrible": "negative_adj",
    "awful": "negative_adj",
    "dreadful": "negative_adj",
    "horrible": "negative_adj",
    "atrocious": "negative_adj",
    # Important adjectives
    "important": "significance_adj",
    "significant": "significance_adj",
    "crucial": "significance_adj",
    "essential": "significance_adj",
    "vital": "significance_adj",
    "critical": "significance_adj",
    # Looking verbs
    "look": "perception_verb",
    "see": "perception_verb",
    "watch": "perception_verb",
    "observe": "perception_verb",
    "gaze": "perception_verb",
    "glance": "perception_verb",
    # Speed adverbs
    "quickly": "speed_adv",
    "rapidly": "speed_adv",
    "swiftly": "speed_adv",
    "fast": "speed_adv",
    "hastily": "speed_adv",
    "slowly": "slowness_adv",
    "gradually": "slowness_adv",
    "leisurely": "slowness_adv",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _tokenize(text: str) -> list[str]:
    """Simple word tokenization for synonym analysis.

    Splits text into lowercase tokens on word boundaries. Preserves
    apostrophe-containing words (contractions) but lowercases everything
    for consistent matching against the synonym map.

    Args:
        text: Raw input text.

    Returns:
        List of lowercase tokens.
    """
    # Normalize curly apostrophes
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    return re.findall(r"\b[\w']+\b", text.lower())


def _build_cluster_data(
    tokens: list[str], synonym_map: dict[str, str]
) -> dict[str, Counter[str]]:
    """Assign tokens to synonym clusters and count occurrences.

    For each token, check if it exists in the synonym_map. If so, add it
    to the appropriate cluster's Counter. Tokens not in the map are
    silently ignored (they contribute to unmapped_word_count instead).

    Args:
        tokens: List of lowercase tokens from _tokenize().
        synonym_map: Mapping of words to cluster IDs.

    Returns:
        Dict mapping cluster_id to Counter of word occurrences within
        that cluster. Only clusters with at least one observed word
        are included.
    """
    clusters: dict[str, Counter[str]] = {}

    for token in tokens:
        cluster_id = synonym_map.get(token)
        if cluster_id is not None:
            if cluster_id not in clusters:
                clusters[cluster_id] = Counter()
            clusters[cluster_id][token] += 1

    return clusters


def _compute_cluster_diversity(word_counts: Counter[str]) -> float:
    """Compute diversity within a single synonym cluster.

    Diversity is measured as the normalized Shannon entropy of the word
    frequency distribution within the cluster. A cluster where all
    occurrences use the same word has diversity 0.0. A cluster where
    occurrences are evenly distributed across all observed words has
    diversity 1.0.

    Formula:
        H = -sum(p_i * log2(p_i)) for each unique word i
        diversity = H / log2(n) if n > 1, else 0.0

    Where:
        p_i = frequency of word i / total occurrences in cluster
        n = number of unique words observed in the cluster

    This normalization (dividing by log2(n)) ensures that diversity is
    comparable across clusters of different sizes.

    Args:
        word_counts: Counter of word occurrences within a cluster.

    Returns:
        Normalized diversity score between 0.0 and 1.0.
    """
    total = sum(word_counts.values())
    unique_count = len(word_counts)

    # A cluster with only one unique word has zero diversity
    if unique_count <= 1:
        return 0.0

    # Compute Shannon entropy of the word distribution
    entropy = 0.0
    for count in word_counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Normalize by maximum possible entropy (log2 of unique words)
    max_entropy = math.log2(unique_count)
    return entropy / max_entropy if max_entropy > 0 else 0.0


def _compute_dominant_ratio(word_counts: Counter[str]) -> float:
    """Compute the dominant word ratio within a synonym cluster.

    The dominant ratio is the fraction of total occurrences captured by
    the single most frequent word in the cluster. A ratio of 1.0 means
    the author uses only one word from the cluster. A ratio close to
    1/n (where n = unique words) means usage is evenly distributed.

    This metric is the inverse signal of diversity: high dominant ratio
    = low diversity, and vice versa.

    Args:
        word_counts: Counter of word occurrences within a cluster.

    Returns:
        Dominant word ratio between 0.0 and 1.0.
    """
    total = sum(word_counts.values())
    if total == 0:
        return 0.0

    most_common_count = word_counts.most_common(1)[0][1]
    return most_common_count / total


def _compute_thesaurus_indicator(
    cluster_data: dict[str, Counter[str]],
    synonym_map: dict[str, str],
) -> float:
    """Estimate the likelihood of thesaurus-assisted writing.

    When an author uses an unusually high variety of synonyms within
    semantic clusters — especially rare or uncommon synonyms — it may
    indicate thesaurus use. Natural writing tends to show strong
    dominant-word preferences, while thesaurus-assisted writing shows
    more even distributions.

    The indicator is computed as the mean diversity across active
    clusters, weighted by the number of distinct words used relative
    to the number available in the map. High values (approaching 1.0)
    suggest possible thesaurus use.

    Important caveat: This metric has limited validity. Some authors
    naturally have rich vocabularies, and a high thesaurus indicator
    does not definitively prove thesaurus use. It is most useful as
    a comparative metric between texts by the same author.

    Args:
        cluster_data: Dict mapping cluster IDs to word Counters.
        synonym_map: The synonym map used for analysis.

    Returns:
        Thesaurus indicator between 0.0 and 1.0.
    """
    if not cluster_data:
        return 0.0

    # Count how many words are available in each cluster
    cluster_sizes: dict[str, int] = {}
    for word, cluster_id in synonym_map.items():
        cluster_sizes[cluster_id] = cluster_sizes.get(cluster_id, 0) + 1

    # For each active cluster, compute the coverage ratio:
    # how many of the available synonyms did the author actually use?
    coverage_scores: list[float] = []
    for cluster_id, word_counts in cluster_data.items():
        available = cluster_sizes.get(cluster_id, 1)
        used = len(word_counts)
        # Coverage = fraction of available synonyms actually used
        coverage = used / available if available > 0 else 0.0
        coverage_scores.append(coverage)

    if not coverage_scores:
        return 0.0

    # Mean coverage across active clusters
    return sum(coverage_scores) / len(coverage_scores)


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def compute_synonym_diversity(
    text: str,
    synonym_map: dict[str, str] | None = None,
) -> SynonymDiversityResult:
    """Analyze synonym diversity for authorship attribution.

    Measures how varied an author's word choices are within semantic fields
    (synonym clusters). The function tokenizes the text, assigns words to
    clusters using the provided synonym map, and computes diversity metrics
    for each active cluster.

    Related GitHub Issue:
        #30 - Whonix stylometric features (synonym choice)
        https://github.com/craigtrim/pystylometry/issues/30

    Whonix Source:
        The Whonix Stylometry documentation identifies "synonym choice" as a
        deanonymization vector:
        https://www.whonix.org/wiki/Stylometry

    Algorithm:
        1. Tokenize text (lowercase, word-boundary splitting)
        2. Map each token to its synonym cluster (if present in map)
        3. For each active cluster, compute:
           a. Normalized Shannon entropy (diversity within cluster)
           b. Dominant word ratio (concentration of most-used synonym)
           c. Words used and their frequencies
        4. Aggregate across clusters for overall metrics:
           a. Mean diversity score
           b. Mean repetition avoidance score (1 - dominant_ratio)
           c. Thesaurus usage indicator (coverage of available synonyms)
           d. Vocabulary sophistication (diversity * coverage blend)

    Data Injection:
        The synonym_map parameter controls which words are grouped as
        synonyms. Pass None to use the built-in minimal default map
        (suitable for testing), or supply a comprehensive map from
        WordNet, a custom JSON file, or any other source.

        Expected format: dict[str, str] mapping lowercase words to
        cluster identifiers. Example:
            {"said": "communication_verb", "stated": "communication_verb"}

    Args:
        text: Input text to analyze. Should contain at least 100+ words
              for meaningful statistics.
        synonym_map: Optional dict mapping words to cluster IDs.
                     If None, uses the built-in DEFAULT_SYNONYM_MAP.
                     Pass an empty dict {} to disable synonym mapping
                     (all words will be unmapped).

    Returns:
        SynonymDiversityResult with per-cluster details, overall diversity
        score, repetition avoidance, thesaurus indicator, and metadata.

    Example:
        >>> # Using default map
        >>> result = compute_synonym_diversity("He said hello. She stated goodbye.")
        >>> print(f"Diversity: {result.synonym_diversity_score:.2f}")
        >>>
        >>> # Using custom map
        >>> my_map = {"happy": "emotion", "glad": "emotion", "joyful": "emotion"}
        >>> result = compute_synonym_diversity(text, synonym_map=my_map)
        >>> for cluster in result.cluster_details:
        ...     print(f"  {cluster['cluster_id']}: {cluster['diversity']:.2f}")

    Note:
        - The default synonym map is intentionally minimal (for testing)
        - Supply a comprehensive map for production analysis
        - Diversity scores are normalized (0.0-1.0) for comparability
        - Clusters with only one word occurrence have diversity 0.0
        - The thesaurus indicator has limited validity (see docstring)
        - Empty text returns zero-valued metrics
    """
    # Use default map if none provided
    if synonym_map is None:
        synonym_map = DEFAULT_SYNONYM_MAP

    # Handle empty text edge case
    if not text or not text.strip():
        return SynonymDiversityResult(
            synonym_diversity_score=0.0,
            repetition_avoidance_score=0.0,
            thesaurus_indicator=0.0,
            vocabulary_sophistication=0.0,
            cluster_details=[],
            active_cluster_count=0,
            total_cluster_count=len(set(synonym_map.values())) if synonym_map else 0,
            mapped_word_count=0,
            unmapped_word_count=0,
            metadata={"word_count": 0, "warning": "Empty text"},
        )

    # Tokenize
    tokens = _tokenize(text)
    word_count = len(tokens)

    if word_count == 0:
        return SynonymDiversityResult(
            synonym_diversity_score=0.0,
            repetition_avoidance_score=0.0,
            thesaurus_indicator=0.0,
            vocabulary_sophistication=0.0,
            cluster_details=[],
            active_cluster_count=0,
            total_cluster_count=len(set(synonym_map.values())) if synonym_map else 0,
            mapped_word_count=0,
            unmapped_word_count=0,
            metadata={"word_count": 0, "warning": "No tokens found"},
        )

    # Count total unique clusters available in the map
    total_cluster_count = len(set(synonym_map.values())) if synonym_map else 0

    # Handle empty synonym map case
    if not synonym_map:
        return SynonymDiversityResult(
            synonym_diversity_score=0.0,
            repetition_avoidance_score=0.0,
            thesaurus_indicator=0.0,
            vocabulary_sophistication=0.0,
            cluster_details=[],
            active_cluster_count=0,
            total_cluster_count=0,
            mapped_word_count=0,
            unmapped_word_count=word_count,
            metadata={
                "word_count": word_count,
                "warning": "Empty synonym map",
            },
        )

    # =========================================================================
    # BUILD CLUSTER DATA
    # =========================================================================
    cluster_data = _build_cluster_data(tokens, synonym_map)

    # Count mapped vs. unmapped words
    mapped_word_count = sum(
        sum(counter.values()) for counter in cluster_data.values()
    )
    unmapped_word_count = word_count - mapped_word_count

    # =========================================================================
    # COMPUTE PER-CLUSTER METRICS
    # =========================================================================
    cluster_details: list[dict[str, Any]] = []
    diversity_scores: list[float] = []
    dominant_ratios: list[float] = []

    for cluster_id, word_counts in sorted(cluster_data.items()):
        diversity = _compute_cluster_diversity(word_counts)
        dominant_ratio = _compute_dominant_ratio(word_counts)
        most_common_word = word_counts.most_common(1)[0][0]

        cluster_details.append({
            "cluster_id": cluster_id,
            "words_used": sorted(word_counts.keys()),
            "total_occurrences": sum(word_counts.values()),
            "unique_words_used": len(word_counts),
            "diversity": diversity,
            "most_common": most_common_word,
            "dominant_ratio": dominant_ratio,
            "word_frequencies": dict(word_counts.most_common()),
        })

        diversity_scores.append(diversity)
        dominant_ratios.append(dominant_ratio)

    # =========================================================================
    # AGGREGATE METRICS
    # =========================================================================
    active_cluster_count = len(cluster_data)

    # Mean diversity across active clusters (0.0 if no active clusters)
    synonym_diversity_score = (
        sum(diversity_scores) / len(diversity_scores)
        if diversity_scores
        else 0.0
    )

    # Repetition avoidance: 1 - mean dominant ratio
    # High score = author avoids repeating the same synonym
    # Low score = author heavily favors one word per cluster
    mean_dominant_ratio = (
        sum(dominant_ratios) / len(dominant_ratios)
        if dominant_ratios
        else 1.0
    )
    repetition_avoidance_score = 1.0 - mean_dominant_ratio

    # Thesaurus indicator: coverage of available synonyms
    thesaurus_indicator = _compute_thesaurus_indicator(
        cluster_data, synonym_map
    )

    # Vocabulary sophistication: blend of diversity and coverage
    # This captures both "uses many synonyms" (diversity) and
    # "uses a wide range of the available synonyms" (coverage)
    vocabulary_sophistication = (
        (synonym_diversity_score * 0.6 + thesaurus_indicator * 0.4)
        if active_cluster_count > 0
        else 0.0
    )

    # =========================================================================
    # BUILD RESULT
    # =========================================================================
    metadata: dict[str, Any] = {
        "word_count": word_count,
        "synonym_map_size": len(synonym_map),
        "synonym_map_cluster_count": total_cluster_count,
        "mapped_word_ratio": mapped_word_count / word_count if word_count > 0 else 0.0,
        "using_default_map": synonym_map is DEFAULT_SYNONYM_MAP,
    }

    return SynonymDiversityResult(
        synonym_diversity_score=synonym_diversity_score,
        repetition_avoidance_score=repetition_avoidance_score,
        thesaurus_indicator=thesaurus_indicator,
        vocabulary_sophistication=vocabulary_sophistication,
        cluster_details=cluster_details,
        active_cluster_count=active_cluster_count,
        total_cluster_count=total_cluster_count,
        mapped_word_count=mapped_word_count,
        unmapped_word_count=unmapped_word_count,
        metadata=metadata,
    )

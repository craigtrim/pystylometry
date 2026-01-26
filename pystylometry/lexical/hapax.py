"""Hapax legomena and related vocabulary richness metrics.

This module implements hapax metrics with native chunked analysis for
stylometric fingerprinting.

Related GitHub Issue:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27
"""

import math
from collections import Counter

from .._types import (
    Distribution,
    HapaxLexiconResult,
    HapaxResult,
    LexiconCategories,
    chunk_text,
    make_distribution,
)
from .._utils import check_optional_dependency, tokenize


def _compute_hapax_single(text: str) -> tuple[int, float, int, float, float, float, dict]:
    """Compute hapax metrics for a single chunk of text.

    Returns:
        Tuple of (hapax_count, hapax_ratio, dis_hapax_count, dis_hapax_ratio,
                  sichel_s, honore_r, metadata_dict).
        Returns nans for ratios on empty input.
    """
    tokens = tokenize(text.lower())
    N = len(tokens)  # noqa: N806

    if N == 0:
        return (
            0,
            float("nan"),
            0,
            float("nan"),
            float("nan"),
            float("nan"),
            {"token_count": 0, "vocabulary_size": 0},
        )

    # Count frequency of each token
    freq_counter = Counter(tokens)
    V = len(freq_counter)  # noqa: N806

    # Count hapax legomena (V₁) and dislegomena (V₂)
    V1 = sum(1 for count in freq_counter.values() if count == 1)  # noqa: N806
    V2 = sum(1 for count in freq_counter.values() if count == 2)  # noqa: N806

    # Sichel's S: ratio of dislegomena to vocabulary size
    sichel_s = V2 / V if V > 0 else 0.0

    # Honoré's R: 100 × log(N) / (1 - V₁/V)
    if V1 == V:
        honore_r = float("inf")
    else:
        honore_r = 100 * math.log(N) / (1 - V1 / V)

    hapax_ratio = V1 / N if N > 0 else 0.0
    dis_hapax_ratio = V2 / N if N > 0 else 0.0

    return (
        V1,
        hapax_ratio,
        V2,
        dis_hapax_ratio,
        sichel_s,
        honore_r,
        {"token_count": N, "vocabulary_size": V},
    )


def compute_hapax_ratios(text: str, chunk_size: int = 1000) -> HapaxResult:
    """
    Compute hapax legomena, hapax dislegomena, and related richness metrics.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Hapax legomena = words appearing exactly once
    Hapax dislegomena = words appearing exactly twice

    Also computes:
    - Sichel's S: V₂ / V (ratio of dislegomena to total vocabulary)
    - Honoré's R: 100 × log(N) / (1 - V₁/V)

    Related GitHub Issue:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

    References:
        Sichel, H. S. (1975). On a distribution law for word frequencies.
        Journal of the American Statistical Association, 70(351a), 542-547.

        Honoré, A. (1979). Some simple measures of richness of vocabulary.
        Association for Literary and Linguistic Computing Bulletin, 7, 172-177.

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        HapaxResult with counts, ratios, distributions, and metadata

    Example:
        >>> result = compute_hapax_ratios("Long text here...", chunk_size=1000)
        >>> result.hapax_ratio  # Mean across chunks
        0.45
        >>> result.hapax_ratio_dist.std  # Variance reveals fingerprint
        0.08
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    hapax_ratio_values = []
    dis_hapax_ratio_values = []
    sichel_s_values = []
    honore_r_values = []
    honore_r_inf_count = 0  # Track chunks where all words are unique (V₁ = V)
    total_hapax_count = 0
    total_dis_hapax_count = 0
    total_tokens = 0
    total_vocab = 0
    valid_chunk_count = 0

    for chunk in chunks:
        h_cnt, h_rat, dh_cnt, dh_rat, sichel, honore, meta = _compute_hapax_single(chunk)
        total_hapax_count += h_cnt
        total_dis_hapax_count += dh_cnt
        total_tokens += meta.get("token_count", 0)
        total_vocab += meta.get("vocabulary_size", 0)

        if not math.isnan(h_rat):
            hapax_ratio_values.append(h_rat)
            valid_chunk_count += 1
        if not math.isnan(dh_rat):
            dis_hapax_ratio_values.append(dh_rat)
        if not math.isnan(sichel):
            sichel_s_values.append(sichel)
        if math.isinf(honore):
            # Track infinite values (when V₁ = V, maximal vocabulary richness)
            honore_r_inf_count += 1
        elif not math.isnan(honore):
            honore_r_values.append(honore)

    # Handle empty or all-invalid chunks
    if not hapax_ratio_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return HapaxResult(
            hapax_count=0,
            hapax_ratio=float("nan"),
            dis_hapax_count=0,
            dis_hapax_ratio=float("nan"),
            sichel_s=float("nan"),
            honore_r=float("nan"),
            hapax_ratio_dist=empty_dist,
            dis_hapax_ratio_dist=empty_dist,
            sichel_s_dist=empty_dist,
            honore_r_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={"total_token_count": 0, "total_vocabulary_size": 0},
        )

    # Build distributions
    hapax_ratio_dist = make_distribution(hapax_ratio_values)
    dis_hapax_ratio_dist = make_distribution(dis_hapax_ratio_values)
    sichel_s_dist = (
        make_distribution(sichel_s_values)
        if sichel_s_values
        else Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
    )

    # Handle honore_r specially: if all valid chunks had V₁ = V (all unique words),
    # return infinity to indicate maximal vocabulary richness
    if honore_r_values:
        honore_r_dist = make_distribution(honore_r_values)
        honore_r_final = honore_r_dist.mean
    elif honore_r_inf_count > 0 and honore_r_inf_count == valid_chunk_count:
        # All valid chunks had infinite honore_r (all words unique)
        honore_r_dist = Distribution(
            values=[], mean=float("inf"), median=float("inf"), std=0.0, range=0.0, iqr=0.0
        )
        honore_r_final = float("inf")
    else:
        honore_r_dist = Distribution(
            values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
        )
        honore_r_final = float("nan")

    return HapaxResult(
        hapax_count=total_hapax_count,
        hapax_ratio=hapax_ratio_dist.mean,
        dis_hapax_count=total_dis_hapax_count,
        dis_hapax_ratio=dis_hapax_ratio_dist.mean,
        sichel_s=sichel_s_dist.mean,
        honore_r=honore_r_final,
        hapax_ratio_dist=hapax_ratio_dist,
        dis_hapax_ratio_dist=dis_hapax_ratio_dist,
        sichel_s_dist=sichel_s_dist,
        honore_r_dist=honore_r_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "total_token_count": total_tokens,
            "total_vocabulary_size": total_vocab,
        },
    )


def compute_hapax_with_lexicon_analysis(text: str) -> HapaxLexiconResult:
    """
    Compute hapax legomena with lexicon-based categorization.

    Extends standard hapax analysis by categorizing hapax legomena based on
    presence in WordNet and British National Corpus (BNC). This distinguishes
    between:

    1. **Neologisms**: Words not in WordNet AND not in BNC
       - True novel words or proper nouns
       - High neologism ratio indicates vocabulary innovation

    2. **Rare Words**: Words in BNC but not WordNet, or vice versa
       - Technical jargon, specialized terminology
       - Words at the edges of common vocabulary

    3. **Common Words**: Words in both WordNet AND BNC
       - Standard vocabulary that happens to appear once
       - Low incidental usage of common words

    This categorization is valuable for stylometric analysis:
    - Authors with high neologism ratios are more innovative/creative
    - Technical writing typically has higher rare word ratios
    - Comparison of neologism vs common hapax distinguishes vocabulary
      innovation from incidental word usage

    Args:
        text: Input text to analyze

    Returns:
        HapaxLexiconResult with standard hapax metrics and lexicon categorization

    Raises:
        ImportError: If bnc-lookup or wordnet-lookup packages are not installed

    Example:
        >>> text = "The xyzbot platform facilitates interdepartmental synergy."
        >>> result = compute_hapax_with_lexicon_analysis(text)
        >>> result.lexicon_analysis.neologisms
        ['xyzbot', 'platform']
        >>> result.lexicon_analysis.rare_words
        ['facilitates', 'interdepartmental']
        >>> result.lexicon_analysis.common_words
        ['synergy']
        >>> print(f"Neologism ratio: {result.lexicon_analysis.neologism_ratio:.2%}")
        Neologism ratio: 40.00%

    References:
        British National Corpus: http://www.natcorp.ox.ac.uk/
        WordNet: https://wordnet.princeton.edu/
    """
    # Check dependencies
    check_optional_dependency("bnc_lookup", "lexical")
    check_optional_dependency("wordnet_lookup", "lexical")

    from bnc_lookup import exists as is_bnc_term  # type: ignore[import-untyped]
    from wordnet_lookup import is_wordnet_term  # type: ignore[import-untyped]

    # First compute standard hapax metrics
    hapax_result = compute_hapax_ratios(text)

    # If no hapax legomena, return empty categorization
    if hapax_result.hapax_count == 0:
        return HapaxLexiconResult(
            hapax_result=hapax_result,
            lexicon_analysis=LexiconCategories(
                neologisms=[],
                rare_words=[],
                common_words=[],
                neologism_ratio=0.0,
                rare_word_ratio=0.0,
                metadata={"total_hapax": 0},
            ),
            metadata={"note": "No hapax legomena found"},
        )

    # Get tokens and identify hapax words
    tokens = tokenize(text.lower())
    freq_counter = Counter(tokens)
    hapax_words = [word for word, count in freq_counter.items() if count == 1]

    # Categorize each hapax word by lexicon presence
    neologisms = []
    rare_words = []
    common_words = []

    for word in hapax_words:
        in_bnc = is_bnc_term(word)
        in_wordnet = is_wordnet_term(word)

        if not in_bnc and not in_wordnet:
            # Not in either lexicon → true neologism
            neologisms.append(word)
        elif in_bnc and in_wordnet:
            # In both lexicons → common word
            common_words.append(word)
        else:
            # In one but not the other → rare word
            rare_words.append(word)

    # Calculate ratios
    total_hapax = len(hapax_words)
    neologism_ratio = len(neologisms) / total_hapax if total_hapax > 0 else 0.0
    rare_word_ratio = len(rare_words) / total_hapax if total_hapax > 0 else 0.0
    common_word_ratio = len(common_words) / total_hapax if total_hapax > 0 else 0.0

    return HapaxLexiconResult(
        hapax_result=hapax_result,
        lexicon_analysis=LexiconCategories(
            neologisms=sorted(neologisms),
            rare_words=sorted(rare_words),
            common_words=sorted(common_words),
            neologism_ratio=neologism_ratio,
            rare_word_ratio=rare_word_ratio,
            metadata={
                "total_hapax": total_hapax,
                "neologism_count": len(neologisms),
                "rare_word_count": len(rare_words),
                "common_word_count": len(common_words),
                "common_word_ratio": common_word_ratio,
            },
        ),
        metadata={
            "lexicons_used": ["bnc", "wordnet"],
            "note": "Lexicon categorization based on BNC and WordNet presence",
        },
    )

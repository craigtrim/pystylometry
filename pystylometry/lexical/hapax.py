"""Hapax legomena and related vocabulary richness metrics."""

import math
from collections import Counter

from .._types import HapaxLexiconResult, HapaxResult, LexiconCategories
from .._utils import check_optional_dependency, tokenize


def compute_hapax_ratios(text: str) -> HapaxResult:
    """
    Compute hapax legomena, hapax dislegomena, and related richness metrics.

    Hapax legomena = words appearing exactly once
    Hapax dislegomena = words appearing exactly twice

    Also computes:
    - Sichel's S: V₂ / V (ratio of dislegomena to total vocabulary)
    - Honoré's R: 100 × log(N) / (1 - V₁/V)

    References:
        Sichel, H. S. (1975). On a distribution law for word frequencies.
        Journal of the American Statistical Association, 70(351a), 542-547.

        Honoré, A. (1979). Some simple measures of richness of vocabulary.
        Association for Literary and Linguistic Computing Bulletin, 7, 172-177.

    Args:
        text: Input text to analyze

    Returns:
        HapaxResult with counts, ratios, Sichel's S, Honoré's R, and metadata

        Note: When all words are unique (V₁ = V), Honoré's R returns float('inf')
        to indicate maximal vocabulary richness (division by zero case).

    Example:
        >>> text = "The quick brown fox jumps over the lazy dog"
        >>> result = compute_hapax_ratios(text)
        >>> result.hapax_count  # Words appearing once
        7
        >>> result.dis_hapax_count  # Words appearing twice
        1
        >>> print(f"Sichel's S: {result.sichel_s:.3f}")
        Sichel's S: 0.125
    """
    tokens = tokenize(text.lower())
    N = len(tokens)  # noqa: N806

    if N == 0:
        return HapaxResult(
            hapax_count=0,
            hapax_ratio=0.0,
            dis_hapax_count=0,
            dis_hapax_ratio=0.0,
            sichel_s=0.0,
            honore_r=0.0,
            metadata={"token_count": 0, "vocabulary_size": 0},
        )

    # Count frequency of each token
    freq_counter = Counter(tokens)
    V = len(freq_counter)  # noqa: N806

    # Count hapax legomena (V₁) and dislegomena (V₂)
    V1 = sum(1 for count in freq_counter.values() if count == 1)  # noqa: N806
    V2 = sum(1 for count in freq_counter.values() if count == 2)  # noqa: N806

    # Sichel's S: ratio of dislegomena to vocabulary size
    # S = V₂ / V
    sichel_s = V2 / V if V > 0 else 0.0

    # Honoré's R: 100 × log(N) / (1 - V₁/V)
    # R = 100 × log(N) / (1 - V₁/V)
    # If V₁ = V (all words appear once), denominator is 0, return infinity
    # This indicates maximal vocabulary richness (every word unique)
    if V1 == V:
        honore_r = float("inf")
    else:
        honore_r = 100 * math.log(N) / (1 - V1 / V)

    return HapaxResult(
        hapax_count=V1,
        hapax_ratio=V1 / N if N > 0 else 0.0,
        dis_hapax_count=V2,
        dis_hapax_ratio=V2 / N if N > 0 else 0.0,
        sichel_s=sichel_s,
        honore_r=honore_r,
        metadata={
            "token_count": N,
            "vocabulary_size": V,
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

    from bnc_lookup import is_bnc_term
    from wordnet_lookup import is_wordnet_term

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

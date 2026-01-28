"""Extended n-gram features for authorship attribution.

This module provides comprehensive n-gram analysis beyond basic bigram/trigram
entropy. Features include frequency distributions for higher-order n-grams,
skipgrams (n-grams with gaps), and POS n-grams, all valuable for stylometric
analysis and authorship attribution.

Related GitHub Issue:
    #19 - Extended N-gram Features
    https://github.com/craigtrim/pystylometry/issues/19

Features implemented:
    - Word trigrams and 4-grams (frequency distributions, top n-grams)
    - Skipgrams (n-grams with gaps, e.g., "the * dog")
    - POS n-grams (part-of-speech tag sequences)
    - Character trigrams and 4-grams
    - N-gram diversity metrics
    - Entropy calculations for each n-gram order

References:
    Guthrie, D., Allison, B., Liu, W., Guthrie, L., & Wilks, Y. (2006).
        A closer look at skip-gram modelling. LREC.
    Stamatatos, E. (2009). A survey of modern authorship attribution methods.
        JASIST, 60(3), 538-556.
    Kešelj, V., et al. (2003). N-gram-based author profiles for authorship
        attribution. PACLING.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Sequence

from .._types import ExtendedNgramResult
from .._utils import advanced_tokenize


def _generate_ngrams(sequence: Sequence[str], n: int) -> list[tuple[str, ...]]:
    """
    Generate n-grams from a sequence.

    Slides a window of size n across the sequence and yields tuples
    of n consecutive elements.

    Related GitHub Issue:
        #19 - Extended N-gram Features
        https://github.com/craigtrim/pystylometry/issues/19

    Args:
        sequence: List of tokens (words or characters)
        n: Size of the n-gram (e.g., 3 for trigrams)

    Returns:
        List of n-gram tuples

    Example:
        >>> _generate_ngrams(["the", "quick", "brown", "fox"], 2)
        [('the', 'quick'), ('quick', 'brown'), ('brown', 'fox')]
    """
    if len(sequence) < n:
        return []
    return [tuple(sequence[i : i + n]) for i in range(len(sequence) - n + 1)]


def _generate_skipgrams(sequence: Sequence[str], n: int, gap: int) -> list[tuple[str, ...]]:
    """
    Generate skipgrams (n-grams with gaps) from a sequence.

    Skipgrams capture non-contiguous word patterns. For example, with n=2 and
    gap=1, "the quick brown fox" yields ("the", "brown"), ("quick", "fox").
    This captures syntactic frames independent of specific intervening words.

    Related GitHub Issue:
        #19 - Extended N-gram Features
        https://github.com/craigtrim/pystylometry/issues/19

    References:
        Guthrie, D., et al. (2006). A closer look at skip-gram modelling. LREC.

    Args:
        sequence: List of tokens
        n: Number of words to include in each skipgram
        gap: Number of words to skip between included words

    Returns:
        List of skipgram tuples

    Example:
        >>> _generate_skipgrams(["the", "quick", "brown", "fox"], 2, 1)
        [('the', 'brown'), ('quick', 'fox')]
        >>> _generate_skipgrams(["a", "b", "c", "d", "e"], 3, 1)
        [('a', 'c', 'd'), ('b', 'd', 'e')]
    """
    if n < 2:
        return list(tuple([s]) for s in sequence)

    # Total span needed: we need n items with (n-1) gaps of size `gap`
    # First item at position i, subsequent items at i + (gap+1), i + 2*(gap+1), ...
    # For n=2, gap=1: positions [i, i+2] -> span of 3
    # For n=3, gap=1: positions [i, i+2, i+3] (first gap, then contiguous)
    # Actually for skipgrams like "word1 _ word3 word4" (n=3, gap=1):
    # positions [i, i+2, i+3]
    # The pattern is: first word, skip `gap`, then n-1 contiguous words

    skipgrams = []

    # Pattern: first word at i, then skip `gap` words, then n-1 contiguous words
    # Total span = 1 + gap + (n-1) = n + gap
    total_span = n + gap
    if len(sequence) < total_span:
        return []

    for i in range(len(sequence) - total_span + 1):
        # First word
        gram = [sequence[i]]
        # Skip `gap` words, then take n-1 contiguous words
        for j in range(n - 1):
            gram.append(sequence[i + gap + 1 + j])
        skipgrams.append(tuple(gram))

    return skipgrams


def _calculate_shannon_entropy(counter: Counter[tuple[str, ...]]) -> float:
    """
    Calculate Shannon entropy of a frequency distribution.

    Shannon entropy measures the uncertainty or information content in a
    distribution. Higher entropy indicates more uniform (diverse) distributions,
    while lower entropy indicates a few dominant n-grams.

    Related GitHub Issue:
        #19 - Extended N-gram Features
        https://github.com/craigtrim/pystylometry/issues/19

    Formula:
        H = -Σ p(x) * log2(p(x))
        where p(x) = count(x) / total

    Args:
        counter: Counter object with n-gram frequencies

    Returns:
        Shannon entropy in bits. Higher values indicate more diversity.

    Example:
        >>> from collections import Counter
        >>> _calculate_shannon_entropy(Counter({"a": 1, "b": 1, "c": 1, "d": 1}))
        2.0  # Maximum entropy for 4 equally likely outcomes
    """
    if not counter:
        return 0.0

    total = sum(counter.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counter.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    return entropy


def _format_ngram(ngram: tuple[str, ...]) -> str:
    """
    Format an n-gram tuple as a readable string.

    Args:
        ngram: Tuple of tokens

    Returns:
        Space-joined string for word n-grams, concatenated string for characters

    Example:
        >>> _format_ngram(("the", "quick", "fox"))
        'the quick fox'
    """
    return " ".join(ngram)


def _get_top_ngrams(counter: Counter[tuple[str, ...]], n: int) -> list[tuple[str, int]]:
    """
    Get top n most frequent n-grams formatted as strings.

    Args:
        counter: Counter of n-gram tuples
        n: Number of top items to return

    Returns:
        List of (ngram_string, count) tuples sorted by frequency
    """
    return [(_format_ngram(ngram), count) for ngram, count in counter.most_common(n)]


def compute_extended_ngrams(
    text: str,
    top_n: int = 20,
    include_pos_ngrams: bool = True,
    spacy_model: str = "en_core_web_sm",
) -> ExtendedNgramResult:
    """
    Compute extended n-gram features for stylometric analysis.

    Analyzes text to extract comprehensive n-gram statistics including
    word trigrams/4-grams, skipgrams, POS n-grams, and character n-grams.
    These features are powerful for authorship attribution because they
    capture both lexical and syntactic patterns.

    Related GitHub Issue:
        #19 - Extended N-gram Features
        https://github.com/craigtrim/pystylometry/issues/19

    Why extended n-grams matter:

    Word N-grams:
        - Capture phrasal patterns and collocations
        - Trigrams/4-grams more distinctive than bigrams
        - Reveal preferred multi-word expressions
        - Author-specific phrase preferences

    Skipgrams:
        - N-grams with gaps (e.g., "I * to" matches "I want to", "I have to")
        - Capture syntactic frames independent of specific words
        - Less sparse than contiguous n-grams
        - Model long-distance dependencies

    POS N-grams:
        - Abstract syntactic patterns (e.g., "DET ADJ NOUN")
        - Independent of vocabulary
        - Capture grammatical preferences
        - Complement word n-grams

    Character N-grams:
        - Language-independent features
        - Capture morphological patterns
        - Effective for short texts
        - Robust to OCR errors

    N-gram Types:

    Contiguous Word N-grams:
        - Trigrams: sequences of 3 words ("in the world")
        - 4-grams: sequences of 4 words ("at the end of")

    Skipgrams:
        - 2-skipgrams with gap 1: "word1 _ word3"
        - 3-skipgrams with gap 1: "word1 _ word3 word4"
        - Variable gap sizes possible

    POS N-grams:
        - POS trigrams: "DET ADJ NOUN" (the quick fox)
        - POS 4-grams: "VERB DET ADJ NOUN" (saw the quick fox)

    Character N-grams:
        - Character trigrams: "the", "he ", "e w"
        - Character 4-grams: "the ", "he w", "e wo"

    Args:
        text: Input text to analyze. Should contain at least 100+ words for
              meaningful n-gram statistics. Shorter texts will have sparse
              distributions.
        top_n: Number of most frequent n-grams to return for each type.
               Default is 20. Larger values provide more detail but increase
               result size.
        include_pos_ngrams: Whether to compute POS n-grams. Requires spaCy
                           and is slower. Default is True. Set to False for
                           faster computation without syntactic features.
        spacy_model: spaCy model for POS tagging (if include_pos_ngrams=True).
                    Default is "en_core_web_sm".

    Returns:
        ExtendedNgramResult containing:

        Word n-grams:
            - top_word_trigrams: Most frequent word trigrams with counts
            - top_word_4grams: Most frequent word 4-grams with counts
            - word_trigram_count: Total unique word trigrams
            - word_4gram_count: Total unique word 4-grams
            - word_trigram_entropy: Shannon entropy of trigram distribution
            - word_4gram_entropy: Shannon entropy of 4-gram distribution

        Skipgrams:
            - top_skipgrams_2_1: Top 2-skipgrams with gap of 1
            - top_skipgrams_3_1: Top 3-skipgrams with gap of 1
            - skipgram_2_1_count: Unique 2-skipgrams
            - skipgram_3_1_count: Unique 3-skipgrams

        POS n-grams (if include_pos_ngrams=True):
            - top_pos_trigrams: Most frequent POS trigrams with counts
            - top_pos_4grams: Most frequent POS 4-grams with counts
            - pos_trigram_count: Unique POS trigrams
            - pos_4gram_count: Unique POS 4-grams
            - pos_trigram_entropy: Shannon entropy of POS trigram distribution

        Character n-grams:
            - top_char_trigrams: Most frequent character trigrams with counts
            - top_char_4grams: Most frequent character 4-grams with counts
            - char_trigram_entropy: Shannon entropy of char trigram distribution
            - char_4gram_entropy: Shannon entropy of char 4-gram distribution

        Metadata:
            - Full frequency distributions
            - Parameters used
            - Token counts
            - etc.

    Example:
        >>> result = compute_extended_ngrams("Sample text for analysis...")
        >>> print(f"Top word trigrams: {result.top_word_trigrams[:3]}")
        Top word trigrams: [('in the world', 5), ('of the world', 4), ('at the time', 3)]
        >>> print(f"Word trigram entropy: {result.word_trigram_entropy:.2f}")
        Word trigram entropy: 4.32
        >>> print(f"Top POS trigrams: {result.top_pos_trigrams[:3]}")
        Top POS trigrams: [('DET ADJ NOUN', 12), ('VERB DET NOUN', 8), ('DET NOUN VERB', 6)]

        >>> # Compare authors using n-grams
        >>> author1 = compute_extended_ngrams("Text by author 1...")
        >>> author2 = compute_extended_ngrams("Text by author 2...")
        >>> # Compare top_word_trigrams for distinctive phrases

    Note:
        - Memory usage scales with text length and n-gram order
        - Longer texts have more unique n-grams (higher counts)
        - POS n-grams require spaCy (slower but valuable)
        - Character n-grams include whitespace
        - Skipgrams can be very sparse (many unique patterns)
        - Entropy values higher for more diverse n-gram distributions
    """
    # =========================================================================
    # TOKENIZATION
    # =========================================================================

    # Word tokenization: lowercase, strip punctuation for word n-grams
    words = advanced_tokenize(text, lowercase=True, strip_punctuation=True)

    # Character sequence: lowercase but preserve spaces (for character n-grams)
    chars = list(text.lower())

    # =========================================================================
    # WORD N-GRAMS
    # =========================================================================

    # Generate word trigrams (3-grams)
    word_trigrams = _generate_ngrams(words, 3)
    word_trigram_counter: Counter[tuple[str, ...]] = Counter(word_trigrams)

    # Generate word 4-grams
    word_4grams = _generate_ngrams(words, 4)
    word_4gram_counter: Counter[tuple[str, ...]] = Counter(word_4grams)

    # =========================================================================
    # SKIPGRAMS
    # =========================================================================

    # 2-skipgrams with gap of 1: (word1, word3) skipping word2
    skipgrams_2_1 = _generate_skipgrams(words, 2, 1)
    skipgram_2_1_counter: Counter[tuple[str, ...]] = Counter(skipgrams_2_1)

    # 3-skipgrams with gap of 1: (word1, word3, word4) skipping word2
    skipgrams_3_1 = _generate_skipgrams(words, 3, 1)
    skipgram_3_1_counter: Counter[tuple[str, ...]] = Counter(skipgrams_3_1)

    # =========================================================================
    # POS N-GRAMS (optional, requires spaCy)
    # =========================================================================

    pos_trigram_counter: Counter[tuple[str, ...]] = Counter()
    pos_4gram_counter: Counter[tuple[str, ...]] = Counter()
    pos_trigram_entropy = 0.0

    if include_pos_ngrams:
        try:
            import spacy

            # Load spaCy model
            try:
                nlp = spacy.load(spacy_model)
            except OSError:
                # Model not installed - provide helpful message
                raise ImportError(
                    f"spaCy model '{spacy_model}' not found. "
                    f"Install with: python -m spacy download {spacy_model}"
                )

            # Process text and extract POS tags
            doc = nlp(text)
            pos_tags = [token.pos_ for token in doc if not token.is_space]

            # Generate POS trigrams
            pos_trigrams = _generate_ngrams(pos_tags, 3)
            pos_trigram_counter = Counter(pos_trigrams)

            # Generate POS 4-grams
            pos_4grams = _generate_ngrams(pos_tags, 4)
            pos_4gram_counter = Counter(pos_4grams)

            pos_trigram_entropy = _calculate_shannon_entropy(pos_trigram_counter)

        except ImportError:
            # spaCy not installed - leave POS results empty
            pass

    # =========================================================================
    # CHARACTER N-GRAMS
    # =========================================================================

    # Character trigrams
    char_trigrams = _generate_ngrams(chars, 3)
    char_trigram_counter: Counter[tuple[str, ...]] = Counter(char_trigrams)

    # Character 4-grams
    char_4grams = _generate_ngrams(chars, 4)
    char_4gram_counter: Counter[tuple[str, ...]] = Counter(char_4grams)

    # =========================================================================
    # ENTROPY CALCULATIONS
    # =========================================================================

    word_trigram_entropy = _calculate_shannon_entropy(word_trigram_counter)
    word_4gram_entropy = _calculate_shannon_entropy(word_4gram_counter)
    char_trigram_entropy = _calculate_shannon_entropy(char_trigram_counter)
    char_4gram_entropy = _calculate_shannon_entropy(char_4gram_counter)

    # =========================================================================
    # BUILD RESULT
    # =========================================================================

    return ExtendedNgramResult(
        # Word n-grams
        top_word_trigrams=_get_top_ngrams(word_trigram_counter, top_n),
        top_word_4grams=_get_top_ngrams(word_4gram_counter, top_n),
        word_trigram_count=len(word_trigram_counter),
        word_4gram_count=len(word_4gram_counter),
        word_trigram_entropy=word_trigram_entropy,
        word_4gram_entropy=word_4gram_entropy,
        # Skipgrams
        top_skipgrams_2_1=_get_top_ngrams(skipgram_2_1_counter, top_n),
        top_skipgrams_3_1=_get_top_ngrams(skipgram_3_1_counter, top_n),
        skipgram_2_1_count=len(skipgram_2_1_counter),
        skipgram_3_1_count=len(skipgram_3_1_counter),
        # POS n-grams
        top_pos_trigrams=_get_top_ngrams(pos_trigram_counter, top_n),
        top_pos_4grams=_get_top_ngrams(pos_4gram_counter, top_n),
        pos_trigram_count=len(pos_trigram_counter),
        pos_4gram_count=len(pos_4gram_counter),
        pos_trigram_entropy=pos_trigram_entropy,
        # Character n-grams
        top_char_trigrams=_get_top_ngrams(char_trigram_counter, top_n),
        top_char_4grams=_get_top_ngrams(char_4gram_counter, top_n),
        char_trigram_entropy=char_trigram_entropy,
        char_4gram_entropy=char_4gram_entropy,
        # Metadata
        metadata={
            "parameters": {
                "top_n": top_n,
                "include_pos_ngrams": include_pos_ngrams,
                "spacy_model": spacy_model if include_pos_ngrams else None,
            },
            "token_count": len(words),
            "character_count": len(chars),
            "word_trigram_tokens": len(word_trigrams),
            "word_4gram_tokens": len(word_4grams),
            "char_trigram_tokens": len(char_trigrams),
            "char_4gram_tokens": len(char_4grams),
            "full_distributions": {
                "word_trigrams": dict(word_trigram_counter.most_common(100)),
                "word_4grams": dict(word_4gram_counter.most_common(100)),
                "skipgrams_2_1": dict(skipgram_2_1_counter.most_common(100)),
                "skipgrams_3_1": dict(skipgram_3_1_counter.most_common(100)),
                "pos_trigrams": dict(pos_trigram_counter.most_common(100)),
                "pos_4grams": dict(pos_4gram_counter.most_common(100)),
                "char_trigrams": dict(char_trigram_counter.most_common(100)),
                "char_4grams": dict(char_4gram_counter.most_common(100)),
            },
        },
    )

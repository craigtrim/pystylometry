"""Character-level metrics for stylometric analysis.

This module provides character-level features that capture low-level patterns
in writing style. Character-level metrics are fundamental for authorship
attribution and can reveal distinctive patterns in punctuation usage,
word construction, and formatting preferences.

Related GitHub Issues:
    #12 - Character-Level Metrics
    #27 - Native chunked analysis with Distribution dataclass

Features implemented:
    - Average word length (characters per word)
    - Average sentence length (characters per sentence)
    - Punctuation density and variety
    - Letter frequency distribution
    - Vowel-to-consonant ratio
    - Digit frequency and ratio
    - Uppercase ratio
    - Whitespace ratio

References:
    Grieve, J. (2007). Quantitative authorship attribution: An evaluation
        of techniques. Literary and Linguistic Computing, 22(3), 251-270.
    Stamatatos, E. (2009). A survey of modern authorship attribution methods.
        JASIST, 60(3), 538-556.
"""

import math

from .._types import CharacterMetricsResult, Distribution, chunk_text, make_distribution

# Character sets
_PUNCTUATION = {
    ".",
    ",",
    "!",
    "?",
    ";",
    ":",
    "-",
    "—",
    "–",  # Basic punctuation
    "'",
    '"',
    """, """,
    "'",
    "'",  # Quotes
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",  # Brackets
    "/",
    "\\",
    "|",  # Slashes
    "…",  # Ellipsis
    "*",
    "&",
    "@",
    "#",
    "$",
    "%",
    "^",
    "~",
    "`",  # Special symbols
}
_VOWELS = {"a", "e", "i", "o", "u"}
_STANDARD_LETTERS = set("abcdefghijklmnopqrstuvwxyz")


def _compute_character_metrics_single(text: str) -> dict:
    """Compute character-level metrics for a single chunk of text.

    Returns a dict with all computed values, or values containing nan for empty text.
    """
    if not text:
        return {
            "avg_word_length": float("nan"),
            "avg_sentence_length_chars": float("nan"),
            "punctuation_density": float("nan"),
            "punctuation_variety": 0,
            "vowel_consonant_ratio": float("nan"),
            "digit_count": 0,
            "digit_ratio": float("nan"),
            "uppercase_ratio": float("nan"),
            "whitespace_ratio": float("nan"),
            "letter_frequency": {letter: 0.0 for letter in "abcdefghijklmnopqrstuvwxyz"},
            "total_characters": 0,
            "total_letters": 0,
            "total_words": 0,
            "total_sentences": 0,
            "total_punctuation": 0,
            "total_whitespace": 0,
            "total_digits": 0,
            "punctuation_types": [],
            "vowel_count": 0,
            "consonant_count": 0,
            "uppercase_count": 0,
            "lowercase_count": 0,
        }

    # Initialize counters
    total_chars = len(text)
    letter_counts = {letter: 0 for letter in "abcdefghijklmnopqrstuvwxyz"}
    vowel_count = 0
    consonant_count = 0
    uppercase_count = 0
    lowercase_count = 0
    digit_count = 0
    whitespace_count = 0
    punctuation_count = 0
    punctuation_types = set()

    # Single pass through text
    for char in text:
        if char.isalpha():
            lower_char = char.lower()
            if lower_char in _STANDARD_LETTERS:
                letter_counts[lower_char] += 1

            if lower_char in _VOWELS:
                vowel_count += 1
            elif lower_char in _STANDARD_LETTERS:
                consonant_count += 1

            if char.isupper():
                uppercase_count += 1
            else:
                lowercase_count += 1

        elif char.isdigit():
            digit_count += 1
        elif char.isspace():
            whitespace_count += 1
        elif char in _PUNCTUATION:
            punctuation_count += 1
            punctuation_types.add(char)

    total_letters = vowel_count + consonant_count

    # Letter frequency distribution
    if total_letters > 0:
        letter_frequency = {
            letter: count / total_letters for letter, count in letter_counts.items()
        }
    else:
        letter_frequency = {letter: 0.0 for letter in "abcdefghijklmnopqrstuvwxyz"}

    # Word metrics
    words = text.split()
    total_words = len(words)

    if total_words > 0:
        word_lengths = [
            sum(1 for c in w if c.isalnum()) for w in words if any(c.isalnum() for c in w)
        ]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else float("nan")
    else:
        avg_word_length = float("nan")

    # Sentence metrics
    sentence_delimiters = {".", "!", "?"}
    sentences = []
    current_sentence = []

    for char in text:
        current_sentence.append(char)
        if char in sentence_delimiters:
            sentence_text = "".join(current_sentence).strip()
            if sentence_text:
                sentences.append(sentence_text)
            current_sentence = []

    if current_sentence:
        sentence_text = "".join(current_sentence).strip()
        if sentence_text:
            sentences.append(sentence_text)

    total_sentences = len(sentences)

    if total_sentences > 0:
        sentence_lengths = [len(sent) for sent in sentences]
        avg_sentence_length_chars = sum(sentence_lengths) / total_sentences
    else:
        avg_sentence_length_chars = float("nan")

    # Ratios
    punctuation_density = (
        (punctuation_count / total_words * 100) if total_words > 0 else float("nan")
    )
    punctuation_variety = len(punctuation_types)

    if consonant_count > 0:
        vowel_consonant_ratio = vowel_count / consonant_count
    elif vowel_count > 0:
        vowel_consonant_ratio = float("inf")
    else:
        vowel_consonant_ratio = float("nan")

    digit_ratio = digit_count / total_chars if total_chars > 0 else float("nan")
    uppercase_ratio = uppercase_count / total_letters if total_letters > 0 else float("nan")
    whitespace_ratio = whitespace_count / total_chars if total_chars > 0 else float("nan")

    return {
        "avg_word_length": avg_word_length,
        "avg_sentence_length_chars": avg_sentence_length_chars,
        "punctuation_density": punctuation_density,
        "punctuation_variety": punctuation_variety,
        "vowel_consonant_ratio": vowel_consonant_ratio,
        "digit_count": digit_count,
        "digit_ratio": digit_ratio,
        "uppercase_ratio": uppercase_ratio,
        "whitespace_ratio": whitespace_ratio,
        "letter_frequency": letter_frequency,
        "total_characters": total_chars,
        "total_letters": total_letters,
        "total_words": total_words,
        "total_sentences": total_sentences,
        "total_punctuation": punctuation_count,
        "total_whitespace": whitespace_count,
        "total_digits": digit_count,
        "punctuation_types": sorted(list(punctuation_types)),
        "vowel_count": vowel_count,
        "consonant_count": consonant_count,
        "uppercase_count": uppercase_count,
        "lowercase_count": lowercase_count,
    }


def compute_character_metrics(text: str, chunk_size: int = 1000) -> CharacterMetricsResult:
    """
    Compute character-level stylometric metrics.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Related GitHub Issues:
        #12 - Character-Level Metrics
        #27 - Native chunked analysis with Distribution dataclass

    Character-level features are particularly valuable because:
        1. They are language-independent (work across languages)
        2. They capture subconscious writing patterns
        3. They are resistant to topic variation
        4. They complement higher-level metrics (words, syntax)

    Metrics computed:
        - Average word length: Mean characters per word
        - Average sentence length (chars): Mean characters per sentence
        - Punctuation density: Punctuation marks per 100 words
        - Punctuation variety: Count of unique punctuation types used
        - Letter frequency: Distribution of a-z (case-insensitive)
        - Vowel-to-consonant ratio: Ratio of vowels to consonants
        - Digit count/ratio: Numeric character usage
        - Uppercase ratio: Uppercase letters / total letters
        - Whitespace ratio: Whitespace characters / total characters

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000)

    Returns:
        CharacterMetricsResult with all character-level features, distributions,
        and metadata.

    Example:
        >>> result = compute_character_metrics("Long text...", chunk_size=1000)
        >>> result.avg_word_length  # Mean across chunks
        4.5
        >>> result.avg_word_length_dist.std  # Variance reveals fingerprint
        0.3
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    chunk_results = [_compute_character_metrics_single(chunk) for chunk in chunks]

    # Collect values for distributions
    avg_word_length_vals = [
        r["avg_word_length"] for r in chunk_results if not math.isnan(r["avg_word_length"])
    ]
    avg_sentence_vals = [
        r["avg_sentence_length_chars"]
        for r in chunk_results
        if not math.isnan(r["avg_sentence_length_chars"])
    ]
    punct_density_vals = [
        r["punctuation_density"] for r in chunk_results if not math.isnan(r["punctuation_density"])
    ]
    punct_variety_vals = [float(r["punctuation_variety"]) for r in chunk_results]
    vc_ratio_vals = [
        r["vowel_consonant_ratio"]
        for r in chunk_results
        if not math.isnan(r["vowel_consonant_ratio"]) and not math.isinf(r["vowel_consonant_ratio"])
    ]
    digit_ratio_vals = [r["digit_ratio"] for r in chunk_results if not math.isnan(r["digit_ratio"])]
    uppercase_ratio_vals = [
        r["uppercase_ratio"] for r in chunk_results if not math.isnan(r["uppercase_ratio"])
    ]
    whitespace_ratio_vals = [
        r["whitespace_ratio"] for r in chunk_results if not math.isnan(r["whitespace_ratio"])
    ]

    # Aggregate totals
    total_digits = sum(r["digit_count"] for r in chunk_results)
    total_characters = sum(r["total_characters"] for r in chunk_results)
    total_letters = sum(r["total_letters"] for r in chunk_results)
    total_words = sum(r["total_words"] for r in chunk_results)
    total_sentences = sum(r["total_sentences"] for r in chunk_results)
    total_punctuation = sum(r["total_punctuation"] for r in chunk_results)
    total_whitespace = sum(r["total_whitespace"] for r in chunk_results)
    total_vowel_count = sum(r["vowel_count"] for r in chunk_results)
    total_consonant_count = sum(r["consonant_count"] for r in chunk_results)
    total_uppercase_count = sum(r["uppercase_count"] for r in chunk_results)
    total_lowercase_count = sum(r["lowercase_count"] for r in chunk_results)
    all_punctuation_types = set()
    for r in chunk_results:
        all_punctuation_types.update(r["punctuation_types"])

    # Aggregate letter frequency
    total_letter_counts = {letter: 0 for letter in "abcdefghijklmnopqrstuvwxyz"}
    for r in chunk_results:
        if r["total_letters"] > 0:
            for letter, freq in r["letter_frequency"].items():
                total_letter_counts[letter] += freq * r["total_letters"]

    if total_letters > 0:
        letter_frequency = {
            letter: count / total_letters for letter, count in total_letter_counts.items()
        }
    else:
        letter_frequency = {letter: 0.0 for letter in "abcdefghijklmnopqrstuvwxyz"}

    # Build distributions (handle empty case)
    def safe_dist(values: list[float]) -> Distribution:
        if not values:
            return Distribution(
                values=[], mean=float("nan"), median=float("nan"), std=0.0, range=0.0, iqr=0.0
            )
        return make_distribution(values)

    avg_word_length_dist = safe_dist(avg_word_length_vals)
    avg_sentence_dist = safe_dist(avg_sentence_vals)
    punct_density_dist = safe_dist(punct_density_vals)
    punct_variety_dist = safe_dist(punct_variety_vals)
    vc_ratio_dist = safe_dist(vc_ratio_vals)
    digit_ratio_dist = safe_dist(digit_ratio_vals)
    uppercase_ratio_dist = safe_dist(uppercase_ratio_vals)
    whitespace_ratio_dist = safe_dist(whitespace_ratio_vals)

    return CharacterMetricsResult(
        avg_word_length=avg_word_length_dist.mean,
        avg_sentence_length_chars=avg_sentence_dist.mean,
        punctuation_density=punct_density_dist.mean,
        punctuation_variety=punct_variety_dist.mean,
        letter_frequency=letter_frequency,
        vowel_consonant_ratio=vc_ratio_dist.mean,
        digit_count=total_digits,
        digit_ratio=digit_ratio_dist.mean,
        uppercase_ratio=uppercase_ratio_dist.mean,
        whitespace_ratio=whitespace_ratio_dist.mean,
        avg_word_length_dist=avg_word_length_dist,
        avg_sentence_length_chars_dist=avg_sentence_dist,
        punctuation_density_dist=punct_density_dist,
        punctuation_variety_dist=punct_variety_dist,
        vowel_consonant_ratio_dist=vc_ratio_dist,
        digit_ratio_dist=digit_ratio_dist,
        uppercase_ratio_dist=uppercase_ratio_dist,
        whitespace_ratio_dist=whitespace_ratio_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            "total_characters": total_characters,
            "total_letters": total_letters,
            "total_words": total_words,
            "total_sentences": total_sentences,
            "total_punctuation": total_punctuation,
            "total_whitespace": total_whitespace,
            "total_digits": total_digits,
            "punctuation_types": sorted(list(all_punctuation_types)),
            "vowel_count": total_vowel_count,
            "consonant_count": total_consonant_count,
            "uppercase_count": total_uppercase_count,
            "lowercase_count": total_lowercase_count,
        },
    )

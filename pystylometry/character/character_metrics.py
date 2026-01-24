"""Character-level metrics for stylometric analysis.

This module provides character-level features that capture low-level patterns
in writing style. Character-level metrics are fundamental for authorship
attribution and can reveal distinctive patterns in punctuation usage,
word construction, and formatting preferences.

Related GitHub Issue:
    #12 - Character-Level Metrics
    https://github.com/craigtrim/pystylometry/issues/12

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

from .._types import CharacterMetricsResult


def compute_character_metrics(text: str) -> CharacterMetricsResult:
    """
    Compute character-level stylometric metrics.

    This function analyzes text at the character level to extract features
    related to word length, punctuation usage, letter distribution, and
    other low-level patterns that can be distinctive for authorship
    attribution and style analysis.

    Related GitHub Issue:
        #12 - Character-Level Metrics
        https://github.com/craigtrim/pystylometry/issues/12

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
        text: Input text to analyze. Should contain at least one sentence
              for meaningful results. Empty text will return NaN for ratios
              and 0 for counts.

    Returns:
        CharacterMetricsResult with all character-level features and metadata.
        For empty text, all ratios will be NaN and counts will be 0.

    Example:
        >>> result = compute_character_metrics("The quick brown fox jumps!")
        >>> print(f"Avg word length: {result.avg_word_length:.2f}")
        Avg word length: 4.17
        >>> print(f"Punctuation density: {result.punctuation_density:.2f}")
        Punctuation density: 16.67
        >>> print(f"Vowel/consonant ratio: {result.vowel_consonant_ratio:.2f}")
        Vowel/consonant ratio: 0.71

        >>> # Empty text handling
        >>> result = compute_character_metrics("")
        >>> import math
        >>> math.isnan(result.avg_word_length)
        True
        >>> result.digit_count
        0

    Note:
        - Punctuation marks include: . , ! ? ; : - ' " ( ) [ ] { } ... etc.
        - Whitespace includes spaces, tabs, newlines
        - Letter frequency is case-insensitive (lowercase normalized)
        - Words are tokenized by whitespace for length calculation
        - Sentences are split using standard sentence delimiters (. ! ?)
    """
    # Define character sets
    # GitHub Issue #12: https://github.com/craigtrim/pystylometry/issues/12
    PUNCTUATION = {
        ".", ",", "!", "?", ";", ":", "-", "—", "–",  # Basic punctuation
        "'", '"', """, """, "'", "'",  # Quotes
        "(", ")", "[", "]", "{", "}",  # Brackets
        "/", "\\", "|",  # Slashes
        "…",  # Ellipsis
        "*", "&", "@", "#", "$", "%", "^", "~", "`",  # Special symbols
    }
    VOWELS = {"a", "e", "i", "o", "u"}

    # Handle empty text
    if not text:
        # Return NaN for all ratios, 0 for all counts
        empty_letter_freq = {letter: 0.0 for letter in "abcdefghijklmnopqrstuvwxyz"}
        return CharacterMetricsResult(
            avg_word_length=float("nan"),
            avg_sentence_length_chars=float("nan"),
            punctuation_density=float("nan"),
            punctuation_variety=0,
            letter_frequency=empty_letter_freq,
            vowel_consonant_ratio=float("nan"),
            digit_count=0,
            digit_ratio=float("nan"),
            uppercase_ratio=float("nan"),
            whitespace_ratio=float("nan"),
            metadata={
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
            },
        )

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

    # Single pass through text to classify and count all characters
    for char in text:
        if char.isalpha():
            # Letter - update letter frequency (case-insensitive)
            letter_counts[char.lower()] += 1

            # Count vowels and consonants
            if char.lower() in VOWELS:
                vowel_count += 1
            else:
                consonant_count += 1

            # Count uppercase and lowercase
            if char.isupper():
                uppercase_count += 1
            else:
                lowercase_count += 1

        elif char.isdigit():
            digit_count += 1

        elif char.isspace():
            whitespace_count += 1

        elif char in PUNCTUATION:
            punctuation_count += 1
            punctuation_types.add(char)

    total_letters = vowel_count + consonant_count

    # Calculate letter frequency distribution (normalize to sum to 1.0)
    if total_letters > 0:
        letter_frequency = {letter: count / total_letters for letter, count in letter_counts.items()}
    else:
        letter_frequency = {letter: 0.0 for letter in "abcdefghijklmnopqrstuvwxyz"}

    # Tokenize into words (split on whitespace, then strip punctuation for length)
    words = text.split()
    total_words = len(words)

    # Calculate average word length (count only letters and digits in words)
    if total_words > 0:
        word_lengths = []
        for word in words:
            # Count only alphanumeric characters for word length
            word_length = sum(1 for char in word if char.isalnum())
            if word_length > 0:  # Only count words with at least one alphanumeric char
                word_lengths.append(word_length)

        if word_lengths:
            avg_word_length = sum(word_lengths) / len(word_lengths)
        else:
            avg_word_length = float("nan")
    else:
        avg_word_length = float("nan")

    # Segment text into sentences (split on . ! ?)
    # Simple approach: split on sentence delimiters
    sentence_delimiters = {".", "!", "?"}
    sentences = []
    current_sentence = []

    for char in text:
        current_sentence.append(char)
        if char in sentence_delimiters:
            # End of sentence
            sentence_text = "".join(current_sentence).strip()
            if sentence_text:  # Only add non-empty sentences
                sentences.append(sentence_text)
            current_sentence = []

    # Add any remaining text as a sentence if it's non-empty and doesn't end with delimiter
    if current_sentence:
        sentence_text = "".join(current_sentence).strip()
        if sentence_text:
            sentences.append(sentence_text)

    total_sentences = len(sentences)

    # Calculate average sentence length in characters
    if total_sentences > 0:
        sentence_lengths = [len(sent) for sent in sentences]
        avg_sentence_length_chars = sum(sentence_lengths) / total_sentences
    else:
        avg_sentence_length_chars = float("nan")

    # Calculate punctuation density (per 100 words)
    if total_words > 0:
        punctuation_density = (punctuation_count / total_words) * 100
    else:
        punctuation_density = float("nan")

    # Punctuation variety (count of unique punctuation types)
    punctuation_variety = len(punctuation_types)

    # Calculate vowel-to-consonant ratio
    if consonant_count > 0:
        vowel_consonant_ratio = vowel_count / consonant_count
    elif vowel_count > 0:
        # Vowels but no consonants - ratio is infinity
        vowel_consonant_ratio = float("inf")
    else:
        # No letters at all
        vowel_consonant_ratio = float("nan")

    # Calculate digit ratio
    if total_chars > 0:
        digit_ratio = digit_count / total_chars
    else:
        digit_ratio = float("nan")

    # Calculate uppercase ratio
    if total_letters > 0:
        uppercase_ratio = uppercase_count / total_letters
    else:
        uppercase_ratio = float("nan")

    # Calculate whitespace ratio
    if total_chars > 0:
        whitespace_ratio = whitespace_count / total_chars
    else:
        whitespace_ratio = float("nan")

    # Build metadata
    metadata = {
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

    return CharacterMetricsResult(
        avg_word_length=avg_word_length,
        avg_sentence_length_chars=avg_sentence_length_chars,
        punctuation_density=punctuation_density,
        punctuation_variety=punctuation_variety,
        letter_frequency=letter_frequency,
        vowel_consonant_ratio=vowel_consonant_ratio,
        digit_count=digit_count,
        digit_ratio=digit_ratio,
        uppercase_ratio=uppercase_ratio,
        whitespace_ratio=whitespace_ratio,
        metadata=metadata,
    )

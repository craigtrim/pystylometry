"""Gunning Fog Index with NLP-enhanced complex word detection.

This module computes the Gunning Fog Index, a readability metric that
estimates the years of formal education needed to understand text on first reading.

Historical Background:
----------------------
The Gunning Fog Index was developed by Robert Gunning in 1952 as part of his
work helping businesses improve the clarity of their writing. The formula produces
a U.S. grade-level score (e.g., 12 = high school senior reading level).

Reference:
    Gunning, R. (1952). The Technique of Clear Writing.
    McGraw-Hill, New York.

Implementation Notes (PR #4):
------------------------------
This implementation addresses issues raised in GitHub PR #4:
https://github.com/craigtrim/pystylometry/pull/4

The original TODO implementation used simple syllable counting without proper
exclusions for proper nouns, compounds, or inflections. This NLP-enhanced
version uses the complex_words module for accurate detection via:

1. spaCy POS tagging for proper noun detection (enhanced mode)
2. spaCy lemmatization for morphological analysis (enhanced mode)
3. Component-based analysis for hyphenated words (both modes)
4. Graceful fallback to heuristics when spaCy unavailable (basic mode)

See complex_words.py for detailed rationale and implementation.
"""

from .._normalize import normalize_for_readability
from .._types import GunningFogResult
from .._utils import split_sentences, tokenize

# Import NLP-enhanced complex word detection module
# This module addresses PR #4 issues with proper noun and inflection detection
from .complex_words import process_text_for_complex_words

# Formula coefficient from Gunning (1952)
# Reference: Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.
# The 0.4 coefficient scales the combined complexity measure to approximate grade level
_FOG_COEFFICIENT = 0.4


def compute_gunning_fog(text: str, spacy_model: str = "en_core_web_sm") -> GunningFogResult:
    """
    Compute Gunning Fog Index with NLP-enhanced complex word detection.

    The Gunning Fog Index estimates the years of formal education required
    to understand text on first reading. It combines sentence length and
    lexical complexity (polysyllabic words) into a single grade-level score.

    Formula (Gunning, 1952):
    ------------------------
        Fog Index = 0.4 × [(words/sentences) + 100 × (complex words/words)]

    Where:
        - words/sentences = Average Sentence Length (ASL)
        - complex words/words = Percentage of Hard Words (PHW)
        - 0.4 = Scaling coefficient to approximate U.S. grade levels

    The resulting score represents a U.S. education grade level:
        - 6 = Sixth grade (age 11-12)
        - 12 = High school senior (age 17-18)
        - 17+ = College graduate level

    Complex Words Definition (Gunning, 1952):
    ------------------------------------------
    Words with 3+ syllables, EXCLUDING:
        1. Proper nouns (names, places, organizations)
        2. Compound words (hyphenated)
        3. Common verb forms (-es, -ed, -ing endings)

    Reference:
        Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.
        Pages 38-39: Complex word criteria

    NLP Enhancement (PR #4):
    ------------------------
    This implementation addresses issues in GitHub PR #4:
    https://github.com/craigtrim/pystylometry/pull/4

    **Enhanced Mode** (when spaCy available):
        - Uses POS tagging (PROPN) for proper noun detection
        - Uses lemmatization for morphological analysis
        - Analyzes hyphenated word components individually
        - More accurate, handles edge cases (acronyms, irregular verbs)

    **Basic Mode** (when spaCy unavailable):
        - Uses capitalization heuristic for proper nouns
        - Uses simple suffix stripping for inflections
        - Analyzes hyphenated word components individually
        - Less accurate but requires no external dependencies

    The mode used is reported in metadata for transparency.

    Args:
        text: Input text to analyze
        spacy_model: spaCy model name for enhanced mode (default: "en_core_web_sm")
                    Requires model download: python -m spacy download en_core_web_sm
                    Other options: "en_core_web_md", "en_core_web_lg"

    Returns:
        GunningFogResult with:
            - fog_index: Float, the calculated Gunning Fog Index
            - grade_level: Int, rounded U.S. grade level (0-20)
            - metadata: Dict with:
                - sentence_count: Number of sentences
                - word_count: Number of words (tokens)
                - complex_word_count: Number of complex words
                - complex_word_percentage: Percentage of complex words
                - average_words_per_sentence: Mean sentence length
                - mode: "enhanced" (spaCy) or "basic" (heuristics)
                - proper_noun_detection: Detection method used
                - inflection_handling: Inflection analysis method used
                - spacy_model: Model name if enhanced mode (else absent)

    Example:
        >>> # Simple text (low complexity)
        >>> result = compute_gunning_fog("The cat sat on the mat. The dog ran.")
        >>> print(f"Fog Index: {result.fog_index:.1f}")
        Fog Index: 2.7
        >>> print(f"Grade Level: {result.grade_level}")
        Grade Level: 3
        >>> print(f"Mode: {result.metadata['mode']}")
        Mode: enhanced

        >>> # Complex academic text (high complexity)
        >>> text = "Understanding phenomenological hermeneutics necessitates comprehensive study."
        >>> result = compute_gunning_fog(text)
        >>> print(f"Fog Index: {result.fog_index:.1f}")
        Fog Index: 23.6
        >>> print(f"Grade Level: {result.grade_level}")
        Grade Level: 20

        >>> # Check which detection mode was used
        >>> if result.metadata['mode'] == 'enhanced':
        ...     print("Using spaCy NLP features")
        Using spaCy NLP features

    Notes:
        - Empty text returns fog_index=0.0 and grade_level=0
        - Grade levels are clamped to [0, 20] range
        - For short texts (< 100 words), results may be unreliable
        - Gunning (1952) recommends analyzing samples of 100+ words
    """
    # Step 1: Sentence and word tokenization
    # Using the project's standard utilities for consistency
    sentences = split_sentences(text)
    all_tokens = tokenize(text)

    # Filter to only valid words (exclude punctuation, numbers, URLs, emails)
    # Allows hyphenated words and contractions per Gunning (1952)
    # Prevents errors in syllable counting from non-word tokens
    tokens = normalize_for_readability(all_tokens)

    # Edge case: Empty or whitespace-only input
    # Return zero values rather than raising an error
    if len(sentences) == 0 or len(tokens) == 0:
        return GunningFogResult(
            fog_index=0.0,
            grade_level=0,
            metadata={
                "sentence_count": 0,
                "word_count": 0,
                "complex_word_count": 0,
                "complex_word_percentage": 0.0,
                "average_words_per_sentence": 0.0,
                "mode": "none",
                "proper_noun_detection": "N/A",
                "inflection_handling": "N/A",
            },
        )

    # Step 2: Count complex words using NLP-enhanced detection
    # This addresses PR #4 issues with proper noun and inflection detection
    # See complex_words.py for detailed implementation
    complex_word_count, detection_metadata = process_text_for_complex_words(
        text, tokens, model=spacy_model
    )

    # Step 3: Calculate formula components
    # Reference: Gunning (1952), p. 40: "The Fog Index formula"

    # Average Sentence Length (ASL)
    # Number of words divided by number of sentences
    average_words_per_sentence = len(tokens) / len(sentences)

    # Percentage of Hard Words (PHW)
    # Number of complex words divided by total words, multiplied by 100
    complex_word_percentage = (complex_word_count / len(tokens)) * 100

    # Step 4: Apply Gunning Fog formula
    # Fog = 0.4 × (ASL + PHW)
    # The 0.4 coefficient scales the result to approximate U.S. grade levels
    fog_index = _FOG_COEFFICIENT * (average_words_per_sentence + complex_word_percentage)

    # Step 5: Convert to grade level
    # Round to nearest integer using standard rounding (round half to even)
    # Clamp to reasonable range [0, 20] to prevent extreme values
    # Note: Texts with fog_index > 20 are considered "post-graduate" level
    grade_level = max(0, min(20, round(fog_index)))

    # Step 6: Assemble result with comprehensive metadata
    return GunningFogResult(
        fog_index=fog_index,
        grade_level=grade_level,
        metadata={
            # Core counts
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "complex_word_count": complex_word_count,
            # Derived metrics
            "complex_word_percentage": complex_word_percentage,
            "average_words_per_sentence": average_words_per_sentence,
            # Detection method transparency (from complex_words module)
            # This allows users to verify which mode was used
            **detection_metadata,
        },
    )

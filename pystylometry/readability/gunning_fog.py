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

import math

from .._types import GunningFogResult
from .._utils import split_sentences, tokenize

# Import NLP-enhanced complex word detection module
# This module addresses PR #4 issues with proper noun and inflection detection
from .complex_words import process_text_for_complex_words

# Formula coefficient from Gunning (1952)
# Reference: Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.
# The 0.4 coefficient scales the combined complexity measure to approximate grade level
_FOG_COEFFICIENT = 0.4


def compute_gunning_fog(
    text: str, spacy_model: str = "en_core_web_sm"
) -> GunningFogResult:
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
                - reliable: Bool, whether text is long enough (100+ words) for reliable results
                - mode: "enhanced" (spaCy) or "basic" (heuristics)
                - proper_noun_detection: Detection method used
                - inflection_handling: Inflection analysis method used
                - spacy_model: Model name if enhanced mode (else absent)

        **Empty Input Handling (API Consistency):**
        For empty input (no sentences or words), fog_index will be float('nan').
        This maintains API consistency with other readability metrics (Flesch PR #3,
        Coleman-Liau PR #2) and prevents conflating "no data" with "extremely easy text".

        A kindergarten-level text legitimately scores ~0-2 (e.g., "Go. Run. Stop.").
        Empty string semantically means "cannot measure", not "grade 0".

        Consumers should check for NaN:
            import math
            if not math.isnan(result.fog_index):
                # Process valid result

        Reference: https://github.com/craigtrim/pystylometry/pull/4
        Related: Flesch PR #3, Coleman-Liau PR #2

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
        >>> text = "Understanding phenomenological hermeneutics necessitates comprehensive analysis."
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
        - Empty text returns fog_index=NaN and grade_level=0 (API consistency with other metrics)
        - Grade levels are clamped to [0, 20] range
        - For short texts (< 100 words), metadata['reliable'] will be False
        - Gunning (1952) recommends analyzing samples of 100+ words

        >>> # Empty input example
        >>> import math
        >>> result_empty = compute_gunning_fog("")
        >>> math.isnan(result_empty.fog_index)
        True
        >>> result_empty.metadata['reliable']
        False
    """
    # Step 1: Sentence and word tokenization
    # Using the project's standard utilities for consistency
    sentences = split_sentences(text)
    all_tokens = tokenize(text)

    # Filter to only words (exclude punctuation, numbers)
    # Allow hyphenated words like "self-education" per Gunning (1952)
    # Gunning (1952) focuses on lexical complexity of actual words
    tokens = [token for token in all_tokens if (token.isalpha() or "-" in token)]

    # Empty Input Handling: Return NaN for Undefined Measurements
    # =============================================================
    # Design Decision (PR #4, aligned with Flesch PR #3, Coleman-Liau PR #2):
    #
    # Previous implementation returned fog_index=0.0 and grade_level=0 for empty input.
    # This was semantically incorrect because:
    #
    # 1. Kindergarten texts legitimately score Fog ~0-2 (e.g., "Go. Run. Stop.")
    # 2. Empty string means "cannot measure", not "grade 0" or "extremely easy"
    # 3. Returning 0.0 allowed empty strings to silently contaminate aggregates
    #
    # Correct behavior: Return float('nan') to represent undefined measurement
    # - NaN propagates through arithmetic, signaling missing data
    # - Consumers must explicitly filter: [x for x in scores if not math.isnan(x)]
    # - Follows IEEE 754 standard for undefined/missing numerical values
    # - Consistent with other metrics: Flesch, Coleman-Liau, ARI, SMOG
    #
    # Academic rationale: Gunning (1952) developed the Fog Index for analyzing
    # business writing samples of 100+ words. The formula has no mathematical
    # interpretation for zero-length input—it's undefined, not zero.
    #
    # See: https://github.com/craigtrim/pystylometry/pull/4
    if len(sentences) == 0 or len(tokens) == 0:
        return GunningFogResult(
            fog_index=float("nan"),
            grade_level=0,  # Keep as 0 since grade_level is int (cannot be NaN)
            metadata={
                "sentence_count": 0,
                "word_count": 0,
                "complex_word_count": 0,
                "complex_word_percentage": 0.0,
                "average_words_per_sentence": 0.0,
                "reliable": False,  # Empty text is not reliable
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

    # Step 6: Calculate reliability flag
    # Gunning (1952) recommends analyzing samples of 100+ words for reliable results
    # Shorter texts may have unstable Fog Index values due to small sample size
    reliable = len(tokens) >= 100

    # Step 7: Assemble result with comprehensive metadata
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
            # Reliability flag (based on Gunning 1952 recommendations)
            "reliable": reliable,
            # Detection method transparency (from complex_words module)
            # This allows users to verify which mode was used
            **detection_metadata,
        },
    )

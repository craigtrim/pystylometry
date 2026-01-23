"""Coleman-Liau Index."""

import math

from .._types import ColemanLiauResult
from .._utils import split_sentences, tokenize

# Regression coefficients from Coleman & Liau (1975)
# Derived from empirical analysis of Cloze test results on graded texts
# Reference: Coleman, M., & Liau, T. L. (1975). A computer readability formula
#            designed for machine scoring. Journal of Applied Psychology, 60(2), 283.

# Coefficient for letters per 100 words
# Represents impact of word length on reading difficulty
_LETTER_COEFFICIENT = 0.0588

# Coefficient for sentences per 100 words (negative: more sentences = easier)
# Represents impact of sentence length on reading difficulty
_SENTENCE_COEFFICIENT = -0.296

# Intercept to calibrate scale to U.S. grade levels (1-16)
_INTERCEPT = -15.8


def compute_coleman_liau(text: str) -> ColemanLiauResult:
    """
    Compute Coleman-Liau Index.

    Formula:
        CLI = 0.0588 × L - 0.296 × S - 15.8

    Where:
        L = average number of letters per 100 words
        S = average number of sentences per 100 words

    The Coleman-Liau index relies on characters rather than syllables,
    making it easier to compute and not requiring syllable-counting algorithms.

    **Implementation Notes:**
    - Grade levels are NOT clamped (removed upper bound of 20 per PR #2 review).
      The original Coleman & Liau (1975) paper calibrated to grades 1-16 but did not
      specify an upper bound. Post-graduate texts may exceed grade 20.
    - Uses round-half-up rounding (not banker's rounding) for grade level calculation
    - Letter counts (Unicode alphabetic characters only) computed from tokenized words
      to ensure measurement consistency. Both letter count and word count use identical
      tokenization logic, preventing divergence in edge cases (emails, URLs, hyphens).
      See PR #2 review discussion: https://github.com/craigtrim/pystylometry/pull/2
    - Reliability heuristic based on validation study passage lengths (~100 words);
      shorter texts flagged in metadata
    - English-centric sentence splitting and Unicode assumptions limit true
      cross-language applicability

    References:
        Coleman, M., & Liau, T. L. (1975). A computer readability formula
        designed for machine scoring. Journal of Applied Psychology, 60(2), 283.

    Args:
        text: Input text to analyze

    Returns:
        ColemanLiauResult with CLI index and grade level

        **Empty Input Handling (API Consistency):**
        For empty input (no sentences or words), cli_index and grade_level
        will be float('nan'). This design choice maintains API consistency
        across all readability metrics (Flesch PR #3, Coleman-Liau PR #2,
        Gunning Fog PR #4) and prevents a critical semantic error:

        - Returning 0.0 conflates "no data" with "extremely easy text"
        - A kindergarten-level text legitimately scores CLI ~0-1
        - Empty string semantically means "cannot measure", not "grade 0"

        Consumers should check for NaN before arithmetic operations:
            import math
            if not math.isnan(result.cli_index):
                # Process valid result
                average_score = sum(scores) / len(scores)

        This follows the IEEE 754 standard for representing undefined/missing
        values and prevents silent propagation of meaningless zeros in statistics.

        Reference: https://github.com/craigtrim/pystylometry/pull/2
        Related: Flesch PR #3, Gunning Fog PR #4, ARI (pending)

    Example:
        >>> result = compute_coleman_liau("The quick brown fox jumps over the lazy dog.")
        >>> print(f"CLI Index: {result.cli_index:.1f}")
        CLI Index: 3.8
        >>> print(f"Grade Level: {result.grade_level}")
        Grade Level: 4
        >>> result.metadata["reliable"]
        False

        >>> # Empty input returns NaN (not 0.0)
        >>> import math
        >>> result_empty = compute_coleman_liau("")
        >>> math.isnan(result_empty.cli_index)
        True
        >>> result_empty.grade_level  # Integer, so returns 0 (cannot be NaN)
        0
    """
    sentences = split_sentences(text)
    tokens = tokenize(text)

    # CRITICAL: Count letters from tokenized words, NOT from raw text
    # ===============================================================
    # Coleman & Liau (1975) define L as "average number of letters per 100 words"
    # where both letters and words must be measured consistently from the same text units.
    #
    # Original implementation (buggy):
    #   letter_count = sum(1 for char in text if char.isalpha())
    #   This counted letters from RAW text but words from TOKENIZED text
    #
    # Problem cases (PR #2 review https://github.com/craigtrim/pystylometry/pull/2):
    #   - "test@example.com" → tokenizer may split into ['test', '@', 'example', '.', 'com']
    #     Raw letter count: 15 letters, Token count: 5 tokens → wrong ratio
    #   - "co-operate" → tokenizer may split into ['co', '-', 'operate']
    #     Raw letter count: 9 letters, Token count: 3 tokens → wrong ratio
    #   - URLs, special tokens, etc. → similar inconsistencies
    #
    # Fixed implementation:
    #   Count only alphabetic characters that appear in tokens, ensuring both
    #   measurements use identical tokenization logic and preventing edge case divergence.
    #
    # This maintains the mathematical integrity of the L term in the Coleman-Liau formula.
    letter_count = sum(1 for token in tokens for char in token if char.isalpha())

    # Empty Input Handling: Return NaN for Undefined Measurements
    # ============================================================
    # Design Decision (PR #2, aligned with Flesch PR #3, Gunning Fog PR #4):
    #
    # Previous implementation returned cli_index=0.0 and grade_level=0 for empty input.
    # This was semantically incorrect because:
    #
    # 1. Kindergarten texts legitimately score CLI ~0-1 (e.g., "Go. Run. Stop.")
    # 2. Empty string means "cannot measure", not "grade 0" or "extremely easy"
    # 3. Returning 0.0 allowed empty strings to silently contaminate aggregates:
    #        scores = [compute_coleman_liau(text).cli_index for text in texts]
    #        mean_score = sum(scores) / len(scores)  # Empty texts drag down mean!
    #
    # Correct behavior: Return float('nan') to represent undefined measurement
    # - NaN propagates through arithmetic, signaling missing data
    # - Consumers must explicitly filter: [x for x in scores if not math.isnan(x)]
    # - Follows IEEE 754 standard for undefined/missing numerical values
    # - Consistent with other metrics: Flesch, Gunning Fog, ARI, SMOG
    #
    # Academic rationale: Coleman & Liau (1975) defined CLI for "readable text"
    # (passages of ~100 words). The formula has no mathematical interpretation
    # for zero-length input—it's undefined, not zero.
    #
    # See: https://github.com/craigtrim/pystylometry/pull/2
    if len(sentences) == 0 or len(tokens) == 0:
        return ColemanLiauResult(
            cli_index=float("nan"),
            grade_level=0,  # Keep as 0 since grade_level is int (cannot be NaN)
            metadata={
                "sentence_count": len(sentences),
                "word_count": len(tokens),
                "letter_count": letter_count,
                "letters_per_100_words": 0.0,
                "sentences_per_100_words": 0.0,
                "reliable": False,
            },
        )

    # Calculate per 100 words
    L = (letter_count / len(tokens)) * 100  # noqa: N806
    S = (len(sentences) / len(tokens)) * 100  # noqa: N806

    # Compute Coleman-Liau Index using empirically-derived coefficients
    cli_index = _LETTER_COEFFICIENT * L + _SENTENCE_COEFFICIENT * S + _INTERCEPT

    # Grade Level Calculation and Bounds
    # ===================================
    # Round-half-up rounding (not Python's default banker's rounding):
    #   4.5 → 5 (always rounds up), not round-half-to-even
    #   math.floor(x + 0.5) implements this for both positive and negative values
    #
    # Lower bound (0): Prevent negative grades for very simple texts
    #   Coleman & Liau (1975) calibrated to U.S. grades 1-16, but simpler texts
    #   (e.g., "Go. Run. Stop.") can produce negative CLI values. We clamp to 0
    #   as there is no "negative grade level" in the educational system.
    #
    # Upper bound (REMOVED per PR #2 review):
    #   Original implementation clamped at grade 20, but this was arbitrary.
    #   Coleman & Liau (1975) did not specify an upper bound in their paper.
    #   Clamping discards information: PhD dissertations (grade 25) and complex
    #   legal documents (grade 30+) would both report as grade 20, making them
    #   indistinguishable. The empirical formula should determine the full range.
    #
    # See PR #2 discussion: https://github.com/craigtrim/pystylometry/pull/2
    grade_level = max(0, math.floor(cli_index + 0.5))

    # Reliability heuristic: validation study used ~100-word passages
    # Not a hard minimum, but shorter texts may deviate from expected behavior
    reliable = len(tokens) >= 100

    return ColemanLiauResult(
        cli_index=cli_index,
        grade_level=grade_level,
        metadata={
            "sentence_count": len(sentences),
            "word_count": len(tokens),
            "letter_count": letter_count,
            "letters_per_100_words": L,
            "sentences_per_100_words": S,
            "reliable": reliable,
        },
    )

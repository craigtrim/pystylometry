"""Additional readability formulas.

This module provides additional readability metrics beyond the core formulas
(Flesch, SMOG, Gunning Fog, Coleman-Liau, ARI). These formulas offer alternative
approaches to measuring text difficulty and are valuable for cross-validation
and comprehensive readability assessment.

Related GitHub Issue:
    #16 - Additional Readability Formulas
    https://github.com/craigtrim/pystylometry/issues/16

Formulas implemented:
    - Dale-Chall: Based on list of 3000 familiar words
    - Linsear Write: Developed for technical writing assessment
    - Fry Readability Graph: Visual graph-based assessment
    - FORCAST: Military formula using only single-syllable words
    - Powers-Sumner-Kearl: Recalibrated Flesch for primary grades

References:
    Dale, E., & Chall, J. S. (1948). A formula for predicting readability.
    Chall, J. S., & Dale, E. (1995). Readability revisited: The new Dale-Chall
        readability formula. Brookline Books.
    Klare, G. R. (1974-1975). Assessing readability. Reading Research Quarterly.
    Fry, E. (1968). A readability formula that saves time. Journal of Reading.
    Caylor, J. S., et al. (1973). Methodologies for determining reading requirements
        of military occupational specialties. Human Resources Research Organization.
    Powers, R. D., Sumner, W. A., & Kearl, B. E. (1958). A recalculation of four
        adult readability formulas. Journal of Educational Psychology.
"""

from .._types import (
    DaleChallResult,
    FORCASTResult,
    FryResult,
    LinsearWriteResult,
    PowersSumnerKearlResult,
)


# Dale-Chall List of 3000 Familiar Words (sample subset)
# GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16
# The full Dale-Chall list contains 3000 words that 80% of 4th graders understand.
# This is a small sample - load complete list from external file in production.
DALE_CHALL_FAMILIAR_WORDS = {
    "a", "able", "about", "above", "accept", "across", "act", "add", "afraid",
    "after", "afternoon", "again", "against", "age", "ago", "agree", "air",
    "all", "allow", "almost", "alone", "along", "already", "also", "always",
    "am", "among", "an", "and", "angry", "animal", "another", "answer", "any",
    "anyone", "anything", "appear", "apple", "are", "area", "arm", "around",
    "arrive", "art", "as", "ask", "at", "aunt", "away", "baby", "back", "bad",
    # ... (add all 3000 words from Dale-Chall list)
    # Load from external file: dale_chall_familiar_words.txt
}


def compute_dale_chall(text: str) -> DaleChallResult:
    """
    Compute Dale-Chall Readability Formula.

    The Dale-Chall formula estimates reading difficulty based on the percentage
    of words that are NOT on a list of 3000 familiar words (words understood
    by 80% of 4th graders). It also considers average sentence length.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula:
        Raw Score = 0.1579 * (difficult_words_pct) + 0.0496 * (avg_sentence_length)

        If difficult_words_pct > 5%:
            Adjusted Score = Raw Score + 3.6365

    Grade Level Correspondence:
        4.9 or lower: Grade 4 and below
        5.0-5.9: Grades 5-6
        6.0-6.9: Grades 7-8
        7.0-7.9: Grades 9-10
        8.0-8.9: Grades 11-12
        9.0-9.9: Grades 13-15 (College)
        10.0+: Grade 16+ (College Graduate)

    Advantages:
        - Based on empirical word familiarity data
        - Works well for educational materials
        - Well-validated across grade levels
        - Considers both vocabulary and syntax

    Disadvantages:
        - Requires maintaining 3000-word familiar list
        - List is dated (1948, updated 1995)
        - May not reflect modern vocabulary
        - Doesn't account for concept difficulty

    Args:
        text: Input text to analyze. Should contain at least one complete
              sentence. Empty text returns NaN values.

    Returns:
        DaleChallResult containing:
            - dale_chall_score: The Dale-Chall readability score
            - grade_level: Grade range (e.g., "7-8", "College")
            - difficult_word_count: Words not on familiar list
            - difficult_word_ratio: Difficult words / total words
            - avg_sentence_length: Average words per sentence
            - total_words: Total word count
            - metadata: List of difficult words, adjusted score flag, etc.

    Example:
        >>> result = compute_dale_chall("Sample educational text...")
        >>> print(f"Dale-Chall score: {result.dale_chall_score:.2f}")
        Dale-Chall score: 7.3
        >>> print(f"Grade level: {result.grade_level}")
        Grade level: 7-8
        >>> print(f"Difficult words: {result.difficult_word_ratio * 100:.1f}%")
        Difficult words: 12.4%

    Note:
        - Case-insensitive word matching
        - Punctuation stripped before word lookup
        - Proper nouns may be flagged as difficult even if well-known
        - Technical/specialized texts score higher than general texts
    """
    # TODO: Implement Dale-Chall readability formula
    # GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16
    #
    # Implementation steps:
    # 1. Load complete Dale-Chall familiar word list (3000 words)
    #    - Load from external file or bundled resource
    #    - Store as set for O(1) lookup
    # 2. Tokenize text into words (lowercase, strip punctuation)
    # 3. Segment text into sentences
    # 4. Count total words and sentences
    # 5. Calculate avg_sentence_length (words / sentences)
    # 6. For each word, check if in familiar list:
    #    - If NOT in list, count as difficult
    #    - Track difficult words for metadata
    # 7. Calculate difficult_word_ratio (difficult / total)
    # 8. Calculate difficult_word_pct (difficult_word_ratio * 100)
    # 9. Calculate raw score:
    #    raw = 0.1579 * difficult_word_pct + 0.0496 * avg_sentence_length
    # 10. If difficult_word_pct > 5.0:
    #     adjusted_score = raw + 3.6365
    #     Else:
    #     adjusted_score = raw
    # 11. Map score to grade level:
    #     4.9-: "4 and below"
    #     5.0-5.9: "5-6"
    #     6.0-6.9: "7-8"
    #     7.0-7.9: "9-10"
    #     8.0-8.9: "11-12"
    #     9.0-9.9: "College"
    #     10.0+: "College Graduate"
    # 12. Return DaleChallResult
    #
    # Metadata should include:
    #   - raw_score: Before adjustment
    #   - adjusted: Boolean indicating if adjustment applied
    #   - difficult_words_list: List of words not on familiar list
    #   - sentence_count: Total sentences
    raise NotImplementedError(
        "Dale-Chall formula not yet implemented. "
        "See GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16"
    )


def compute_linsear_write(text: str) -> LinsearWriteResult:
    """
    Compute Linsear Write Readability Formula.

    Developed for the U.S. Air Force to assess technical writing, the Linsear
    Write formula classifies words as "easy" (1-2 syllables) or "hard" (3+
    syllables) and uses sentence length to estimate grade level.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula:
        1. Count "easy" words (1-2 syllables): multiply count by 1
        2. Count "hard" words (3+ syllables): multiply count by 3
        3. Divide sum by number of sentences
        4. If result > 20, divide by 2 to get grade level
        5. If result <= 20, subtract 2, then divide by 2

    The formula is optimized for technical writing and works best with
    passages of about 100 words.

    Advantages:
        - Simple binary classification (easy/hard)
        - Effective for technical documents
        - Fast computation
        - Developed specifically for instructional materials

    Disadvantages:
        - Less well-known than other formulas
        - Binary word classification is crude
        - May overestimate difficulty of technical terms
        - Limited validation compared to Flesch or Dale-Chall

    Args:
        text: Input text to analyze. Works best with 100-word samples.
              Empty text returns NaN values.

    Returns:
        LinsearWriteResult containing:
            - linsear_score: The Linsear Write score
            - grade_level: Corresponding U.S. grade level (integer)
            - easy_word_count: Words with 1-2 syllables
            - hard_word_count: Words with 3+ syllables
            - avg_sentence_length: Average words per sentence
            - metadata: Calculation details, sentence count, etc.

    Example:
        >>> result = compute_linsear_write("Technical manual text...")
        >>> print(f"Linsear Write score: {result.linsear_score:.2f}")
        Linsear Write score: 11.3
        >>> print(f"Grade level: {result.grade_level}")
        Grade level: 11
        >>> print(f"Easy words: {result.easy_word_count}")
        Easy words: 78
        >>> print(f"Hard words: {result.hard_word_count}")
        Hard words: 22

    Note:
        - Syllable counting required (use existing syllable module)
        - Punctuation and numbers typically excluded
        - Most accurate with 100-word samples
        - Grade level is rounded to nearest integer
    """
    # TODO: Implement Linsear Write formula
    # GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16
    #
    # Implementation steps:
    # 1. Import syllable counting function from readability.syllables
    # 2. Tokenize text into words
    # 3. Segment text into sentences
    # 4. Count sentences
    # 5. For each word:
    #    - Count syllables
    #    - If 1-2 syllables: increment easy_count
    #    - If 3+ syllables: increment hard_count
    # 6. Calculate weighted sum:
    #    sum = (easy_count * 1) + (hard_count * 3)
    # 7. Divide by sentence count:
    #    score = sum / sentence_count
    # 8. Convert to grade level:
    #    if score > 20:
    #        grade = score / 2
    #    else:
    #        grade = (score - 2) / 2
    # 9. Round grade to nearest integer
    # 10. Calculate avg_sentence_length
    # 11. Return LinsearWriteResult
    #
    # Metadata should include:
    #   - total_words: Total word count
    #   - sentence_count: Total sentences
    #   - raw_score: Before grade conversion
    raise NotImplementedError(
        "Linsear Write formula not yet implemented. "
        "See GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16"
    )


def compute_fry(text: str) -> FryResult:
    """
    Compute Fry Readability Graph metrics.

    The Fry Readability Graph plots average sentence length against average
    syllables per 100 words to determine reading difficulty. This implementation
    provides the numerical coordinates and estimated grade level.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Method:
        1. Select three 100-word samples from text
        2. Count average sentence length across samples
        3. Count average syllables per 100 words across samples
        4. Plot coordinates on Fry graph (or use numerical approximation)
        5. Determine grade level from graph zone

    The original Fry graph has zones corresponding to grade levels 1-17+.
    This implementation uses numerical approximation to estimate grade level.

    Advantages:
        - Visual/graphical approach (intuitive)
        - Uses two independent dimensions (length & syllables)
        - Well-validated for educational materials
        - Covers wide range of grade levels (1-17+)

    Disadvantages:
        - Requires exactly 100-word samples (padding/truncation needed)
        - Graph reading can be subjective
        - Less precise than formula-based methods
        - Multiple samples needed for reliability

    Args:
        text: Input text to analyze. Should contain at least 100 words.
              Shorter texts are padded or return limited results.

    Returns:
        FryResult containing:
            - avg_sentence_length: Average words per sentence
            - avg_syllables_per_100: Average syllables per 100 words
            - grade_level: Estimated grade level (e.g., "5", "7", "College")
            - graph_zone: Which zone of Fry graph (for validity checking)
            - metadata: Sample details, total sentences, syllables, etc.

    Example:
        >>> result = compute_fry("Educational text for grade assessment...")
        >>> print(f"Avg sentence length: {result.avg_sentence_length:.1f}")
        Avg sentence length: 14.3
        >>> print(f"Syllables/100 words: {result.avg_syllables_per_100:.1f}")
        Syllables/100 words: 142.7
        >>> print(f"Grade level: {result.grade_level}")
        Grade level: 6

    Note:
        - Original method uses three 100-word samples
        - Implementation may use single sample or whole text
        - Syllable counting required
        - Grade level estimation uses zone boundaries
        - Some texts fall outside graph zones (marked as invalid)
    """
    # TODO: Implement Fry Readability Graph
    # GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16
    #
    # Implementation steps:
    # 1. Import syllable counting function
    # 2. Tokenize text and segment into sentences
    # 3. If text >= 100 words, extract sample(s):
    #    - Option A: Use first 100 words
    #    - Option B: Use three random 100-word samples and average
    # 4. For each sample:
    #    - Count sentences that fall within 100 words
    #    - Count syllables in 100 words
    # 5. Calculate avg_sentence_length (per sample)
    # 6. Calculate avg_syllables_per_100 (per sample)
    # 7. Average across samples if multiple
    # 8. Map (avg_sentence_length, avg_syllables_per_100) to grade level:
    #    - Use Fry graph zone boundaries
    #    - Approximate zones numerically
    # 9. Determine graph_zone (valid, above, below, etc.)
    # 10. Return FryResult
    #
    # Metadata should include:
    #   - sample_count: Number of samples used
    #   - total_sentences: Total sentence count
    #   - total_syllables: Total syllable count
    #   - total_words: Total word count
    #
    # Fry graph zones (approximate):
    # Grade 1: sentences ~6, syllables ~120
    # Grade 5: sentences ~10, syllables ~140
    # Grade 9: sentences ~15, syllables ~155
    # Grade 13+: sentences ~20+, syllables ~170+
    raise NotImplementedError(
        "Fry Readability Graph not yet implemented. "
        "See GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16"
    )


def compute_forcast(text: str) -> FORCASTResult:
    """
    Compute FORCAST Readability Formula.

    FORCAST (FORmula for CASTing readability) was developed by the U.S. military
    to assess readability without counting syllables. It uses only the count of
    single-syllable words as its metric, making it fast and simple.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula:
        Grade Level = 20 - (N / 10)

        Where N is the number of single-syllable words in a 150-word sample.

    The formula is optimized for technical and military documents and works
    best with standardized 150-word samples.

    Advantages:
        - Extremely simple (only counts single-syllable words)
        - No sentence segmentation required
        - Fast computation
        - Developed specifically for military/technical texts

    Disadvantages:
        - Less well-known and validated than other formulas
        - Requires exactly 150-word samples
        - Single dimension (doesn't consider sentence length)
        - May not generalize well beyond military context

    Args:
        text: Input text to analyze. Works best with 150-word samples.
              Shorter texts are padded or scored proportionally.
              Longer texts use first 150 words or multiple samples.

    Returns:
        FORCASTResult containing:
            - forcast_score: The FORCAST readability score
            - grade_level: Corresponding U.S. grade level (integer)
            - single_syllable_ratio: Single-syllable words / total words
            - single_syllable_count: Count of single-syllable words
            - total_words: Total word count analyzed
            - metadata: Sample details, calculation specifics, etc.

    Example:
        >>> result = compute_forcast("Military technical document...")
        >>> print(f"FORCAST score: {result.forcast_score:.2f}")
        FORCAST score: 9.7
        >>> print(f"Grade level: {result.grade_level}")
        Grade level: 10
        >>> print(f"Single-syllable ratio: {result.single_syllable_ratio:.3f}")
        Single-syllable ratio: 0.687

    Note:
        - Syllable counting required (but only to identify 1-syllable words)
        - Recommended sample size is 150 words
        - Multiple samples can be averaged for longer texts
        - Simpler than most readability formulas
        - Grade levels typically range from 5-12
    """
    # TODO: Implement FORCAST formula
    # GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16
    #
    # Implementation steps:
    # 1. Import syllable counting function
    # 2. Tokenize text into words
    # 3. Extract 150-word sample:
    #    - If text < 150 words: use all words, adjust calculation
    #    - If text >= 150 words: use first 150 words (or average multiple samples)
    # 4. For each word in sample:
    #    - Count syllables
    #    - If syllables == 1: increment single_syllable_count
    # 5. Calculate N (single_syllable_count per 150 words)
    #    - If sample != 150 words: scale proportionally
    #      N = single_syllable_count * (150 / actual_words)
    # 6. Calculate grade level:
    #    grade = 20 - (N / 10)
    # 7. Round grade to nearest integer
    # 8. Calculate ratios
    # 9. Return FORCASTResult
    #
    # Metadata should include:
    #   - sample_size: Actual words analyzed
    #   - scaled_n: N value (possibly scaled to 150)
    #   - samples_used: Number of 150-word samples if averaging
    raise NotImplementedError(
        "FORCAST formula not yet implemented. "
        "See GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16"
    )


def compute_powers_sumner_kearl(text: str) -> PowersSumnerKearlResult:
    """
    Compute Powers-Sumner-Kearl Readability Formula.

    The Powers-Sumner-Kearl (PSK) formula is a recalibration of the Flesch
    Reading Ease formula, optimized for primary grade levels (grades 1-4).
    It uses the same inputs (sentence length, syllables per word) but with
    different coefficients.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula:
        Grade Level = 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029

    The formula was derived from analysis of primary-grade texts and provides
    more accurate grade-level estimates for beginning readers than the original
    Flesch formula.

    Advantages:
        - Optimized for primary grades (1-4)
        - More accurate than Flesch for young readers
        - Uses same inputs as Flesch (easy to compare)
        - Well-validated on educational materials

    Disadvantages:
        - Less accurate for higher grade levels
        - Less well-known than Flesch
        - Limited range (not suitable for college-level texts)
        - Requires syllable counting

    Args:
        text: Input text to analyze. Optimized for children's literature
              and primary-grade educational materials. Empty text returns
              NaN values.

    Returns:
        PowersSumnerKearlResult containing:
            - psk_score: The Powers-Sumner-Kearl score
            - grade_level: Corresponding grade (decimal, e.g., 2.5 = mid-2nd grade)
            - avg_sentence_length: Average words per sentence
            - avg_syllables_per_word: Average syllables per word
            - total_sentences: Total sentence count
            - total_words: Total word count
            - total_syllables: Total syllable count
            - metadata: Comparison to Flesch, calculation details, etc.

    Example:
        >>> result = compute_powers_sumner_kearl("Children's book text...")
        >>> print(f"PSK score: {result.psk_score:.2f}")
        PSK score: 2.3
        >>> print(f"Grade level: {result.grade_level:.1f}")
        Grade level: 2.3
        >>> print(f"Avg sentence length: {result.avg_sentence_length:.1f}")
        Avg sentence length: 8.5

    Note:
        - Most accurate for grades 1-4
        - Can produce negative scores for very simple texts
        - Grade level is continuous (can be decimal)
        - Syllable counting required (same as Flesch)
        - Compare to Flesch results for validation
    """
    # TODO: Implement Powers-Sumner-Kearl formula
    # GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16
    #
    # Implementation steps:
    # 1. Import syllable counting function
    # 2. Tokenize text into words
    # 3. Segment text into sentences
    # 4. Count total_words, total_sentences, total_syllables
    # 5. Calculate avg_sentence_length = total_words / total_sentences
    # 6. Calculate avg_syllables_per_word = total_syllables / total_words
    # 7. Apply formula:
    #    grade = 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029
    # 8. Round to 1 decimal place for grade_level
    # 9. Optionally calculate Flesch score for comparison:
    #    flesch = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
    # 10. Return PowersSumnerKearlResult
    #
    # Metadata should include:
    #   - flesch_score: For comparison (optional)
    #   - flesch_grade: Flesch-Kincaid grade level (optional)
    #   - difference_from_flesch: PSK grade - Flesch grade
    raise NotImplementedError(
        "Powers-Sumner-Kearl formula not yet implemented. "
        "See GitHub Issue #16: https://github.com/craigtrim/pystylometry/issues/16"
    )

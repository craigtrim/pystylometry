"""Result dataclasses for all pystylometry metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ===== Lexical Results =====


@dataclass
class MTLDResult:
    """Result from MTLD (Measure of Textual Lexical Diversity) computation."""

    mtld_forward: float
    mtld_backward: float
    mtld_average: float
    metadata: dict[str, Any]


@dataclass
class YuleResult:
    """Result from Yule's K and I computation."""

    yule_k: float
    yule_i: float
    metadata: dict[str, Any]


@dataclass
class HapaxResult:
    """Result from Hapax Legomena analysis."""

    hapax_count: int
    hapax_ratio: float
    dis_hapax_count: int
    dis_hapax_ratio: float
    sichel_s: float
    honore_r: float
    metadata: dict[str, Any]


@dataclass
class LexiconCategories:
    """Categorization of words by lexicon presence."""

    neologisms: list[str]  # Not in WordNet AND not in BNC
    rare_words: list[str]  # In one lexicon but not both
    common_words: list[str]  # In both WordNet AND BNC
    neologism_ratio: float  # Ratio of neologisms to total hapax
    rare_word_ratio: float  # Ratio of rare words to total hapax
    metadata: dict[str, Any]


@dataclass
class HapaxLexiconResult:
    """Result from Hapax Legomena analysis with lexicon categorization.

    Extends basic hapax analysis by categorizing hapax legomena based on
    presence in WordNet and British National Corpus (BNC):

    - Neologisms: Words not in WordNet AND not in BNC (true novel words)
    - Rare words: Words in BNC but not WordNet, or vice versa
    - Common words: Words in both lexicons (just happen to appear once in text)

    This categorization is valuable for stylometric analysis as it distinguishes
    between vocabulary innovation (neologisms) and incidental hapax occurrence
    (common words that appear once).
    """

    hapax_result: HapaxResult  # Standard hapax metrics
    lexicon_analysis: LexiconCategories  # Lexicon-based categorization
    metadata: dict[str, Any]


@dataclass
class TTRResult:
    """Result from Type-Token Ratio (TTR) analysis.

    Wraps stylometry-ttr package functionality to measure vocabulary richness
    through the ratio of unique words (types) to total words (tokens).

    Includes multiple TTR variants for length normalization:
    - Raw TTR: Direct ratio of unique to total words
    - Root TTR (Guiraud's index): types / sqrt(tokens)
    - Log TTR (Herdan's C): log(types) / log(tokens)
    - STTR: Standardized TTR across fixed-size chunks
    - Delta Std: Measures vocabulary consistency across chunks

    References:
        Guiraud, P. (1960). Problèmes et méthodes de la statistique linguistique.
        Herdan, G. (1960). Type-token Mathematics.
    """

    total_words: int
    unique_words: int
    ttr: float  # Raw TTR
    root_ttr: float  # Guiraud's index
    log_ttr: float  # Herdan's C
    sttr: float  # Standardized TTR
    delta_std: float  # Vocabulary consistency
    metadata: dict[str, Any]


# ===== Readability Results =====


@dataclass
class FleschResult:
    """Result from Flesch Reading Ease and Flesch-Kincaid Grade computation."""

    reading_ease: float
    grade_level: float
    difficulty: str  # "Very Easy", "Easy", "Fairly Easy", "Standard", etc.
    metadata: dict[str, Any]


@dataclass
class SMOGResult:
    """Result from SMOG Index computation."""

    smog_index: float
    grade_level: float
    metadata: dict[str, Any]


@dataclass
class GunningFogResult:
    """Result from Gunning Fog Index computation."""

    fog_index: float
    grade_level: float
    metadata: dict[str, Any]


@dataclass
class ColemanLiauResult:
    """Result from Coleman-Liau Index computation."""

    cli_index: float
    grade_level: int
    metadata: dict[str, Any]


@dataclass
class ARIResult:
    """Result from Automated Readability Index computation."""

    ari_score: float
    grade_level: int
    age_range: str
    metadata: dict[str, Any]


# ===== Syntactic Results =====


@dataclass
class POSResult:
    """Result from Part-of-Speech ratio analysis."""

    noun_ratio: float
    verb_ratio: float
    adjective_ratio: float
    adverb_ratio: float
    noun_verb_ratio: float
    adjective_noun_ratio: float
    lexical_density: float
    function_word_ratio: float
    metadata: dict[str, Any]


@dataclass
class SentenceStatsResult:
    """Result from sentence-level statistics."""

    mean_sentence_length: float
    sentence_length_std: float
    sentence_length_range: int
    min_sentence_length: int
    max_sentence_length: int
    sentence_count: int
    metadata: dict[str, Any]


# ===== Authorship Results =====


@dataclass
class BurrowsDeltaResult:
    """Result from Burrows' Delta computation."""

    delta_score: float
    distance_type: str  # "burrows", "cosine", "eder"
    mfw_count: int
    metadata: dict[str, Any]


@dataclass
class ZetaResult:
    """Result from Zeta score computation."""

    zeta_score: float
    marker_words: list[str]
    anti_marker_words: list[str]
    metadata: dict[str, Any]


# ===== N-gram Results =====


@dataclass
class EntropyResult:
    """Result from n-gram entropy computation."""

    entropy: float
    perplexity: float
    ngram_type: str  # "character_bigram", "word_bigram", "word_trigram"
    metadata: dict[str, Any]


# ===== Character-Level Results =====
# Related to GitHub Issue #12: Character-Level Metrics
# https://github.com/craigtrim/pystylometry/issues/12


@dataclass
class CharacterMetricsResult:
    """Result from character-level metrics analysis.

    This dataclass holds character-level stylometric features that provide
    low-level insights into writing style. Character-level metrics are
    fundamental for authorship attribution and can capture distinctive
    patterns in punctuation, formatting, and word construction.

    Related GitHub Issue:
        #12 - Character-Level Metrics
        https://github.com/craigtrim/pystylometry/issues/12

    Metrics included:
        - Average word length (characters per word)
        - Average sentence length (characters per sentence)
        - Punctuation density (punctuation marks per 100 words)
        - Punctuation variety (count of unique punctuation types)
        - Letter frequency distribution (26-element vector for a-z)
        - Vowel-to-consonant ratio
        - Digit frequency (count/ratio of numeric characters)
        - Uppercase ratio (uppercase letters / total letters)
        - Whitespace ratio (whitespace characters / total characters)

    References:
        Grieve, J. (2007). Quantitative authorship attribution: An evaluation
            of techniques. Literary and Linguistic Computing, 22(3), 251-270.
        Stamatatos, E. (2009). A survey of modern authorship attribution methods.
            JASIST, 60(3), 538-556.

    Example:
        >>> result = compute_character_metrics("Sample text here.")
        >>> print(f"Avg word length: {result.avg_word_length:.2f} chars")
        >>> print(f"Punctuation density: {result.punctuation_density:.2f}")
        >>> print(f"Vowel/consonant ratio: {result.vowel_consonant_ratio:.2f}")
    """

    avg_word_length: float  # Mean characters per word
    avg_sentence_length_chars: float  # Mean characters per sentence
    punctuation_density: float  # Punctuation marks per 100 words
    punctuation_variety: int  # Count of unique punctuation types used
    letter_frequency: dict[str, float]  # Frequency distribution for a-z
    vowel_consonant_ratio: float  # Ratio of vowels to consonants
    digit_count: int  # Total count of digit characters (0-9)
    digit_ratio: float  # Digits / total characters
    uppercase_ratio: float  # Uppercase letters / total letters
    whitespace_ratio: float  # Whitespace characters / total characters
    metadata: dict[str, Any]  # Additional info (character counts, etc.)


# ===== Function Word Results =====
# Related to GitHub Issue #13: Function Word Analysis
# https://github.com/craigtrim/pystylometry/issues/13


@dataclass
class FunctionWordResult:
    """Result from function word analysis.

    Function words (determiners, prepositions, conjunctions, pronouns, auxiliary
    verbs) are highly frequent, content-independent words that are often used
    subconsciously. They are considered strong authorship markers because authors
    use them consistently across different topics and genres.

    Related GitHub Issue:
        #13 - Function Word Analysis
        https://github.com/craigtrim/pystylometry/issues/13

    This analysis computes:
        - Frequency profiles for all function word categories
        - Ratios for specific grammatical categories
        - Most/least frequently used function words
        - Function word diversity metrics

    Function word categories analyzed:
        - Determiners: the, a, an, this, that, these, those, etc.
        - Prepositions: in, on, at, by, for, with, from, to, etc.
        - Conjunctions: and, but, or, nor, for, yet, so, etc.
        - Pronouns: I, you, he, she, it, we, they, etc.
        - Auxiliary verbs: be, have, do, can, will, shall, may, etc.
        - Particles: up, down, out, off, over, etc.

    References:
        Mosteller, F., & Wallace, D. L. (1964). Inference and disputed authorship:
            The Federalist. Addison-Wesley.
        Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide
            to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.

    Example:
        >>> result = compute_function_words("Sample text for analysis.")
        >>> print(f"Determiner ratio: {result.determiner_ratio:.3f}")
        >>> print(f"Preposition ratio: {result.preposition_ratio:.3f}")
        >>> print(f"Most frequent: {result.most_frequent_function_words[:5]}")
    """

    determiner_ratio: float  # Determiners / total words
    preposition_ratio: float  # Prepositions / total words
    conjunction_ratio: float  # Conjunctions / total words
    pronoun_ratio: float  # Pronouns / total words
    auxiliary_ratio: float  # Auxiliary verbs / total words
    particle_ratio: float  # Particles / total words
    total_function_word_ratio: float  # All function words / total words
    function_word_diversity: float  # Unique function words / total function words
    most_frequent_function_words: list[tuple[str, int]]  # Top N with counts
    least_frequent_function_words: list[tuple[str, int]]  # Bottom N with counts
    function_word_distribution: dict[str, int]  # All function words with counts
    metadata: dict[str, Any]  # Category-specific counts, total counts, etc.


# ===== Advanced Lexical Diversity Results =====
# Related to GitHub Issue #14: Advanced Lexical Diversity Metrics
# https://github.com/craigtrim/pystylometry/issues/14


@dataclass
class VocdDResult:
    """Result from voc-D computation.

    voc-D is a sophisticated measure of lexical diversity that uses a mathematical
    model to estimate vocabulary richness while controlling for text length.
    It fits a curve to the relationship between tokens and types across multiple
    random samples of the text.

    Related GitHub Issue:
        #14 - Advanced Lexical Diversity Metrics
        https://github.com/craigtrim/pystylometry/issues/14

    The D parameter represents the theoretical vocabulary size and is more
    stable across different text lengths than simple TTR measures.

    References:
        Malvern, D., Richards, B., Chipere, N., & Durán, P. (2004).
            Lexical Diversity and Language Development. Palgrave Macmillan.
        McKee, G., Malvern, D., & Richards, B. (2000). Measuring vocabulary
            diversity using dedicated software. Literary and Linguistic Computing,
            15(3), 323-337.

    Example:
        >>> result = compute_vocd_d("Long sample text for voc-D analysis...")
        >>> print(f"D parameter: {result.d_parameter:.2f}")
        >>> print(f"Curve fit R²: {result.curve_fit_r_squared:.3f}")
    """

    d_parameter: float  # The D value (theoretical vocabulary size)
    curve_fit_r_squared: float  # Quality of curve fit (0-1)
    sample_count: int  # Number of random samples used
    optimal_sample_size: int  # Optimal token sample size used
    metadata: dict[str, Any]  # Sampling parameters, convergence info, etc.


@dataclass
class MATTRResult:
    """Result from MATTR (Moving-Average Type-Token Ratio) computation.

    MATTR computes TTR using a moving window of fixed size, which provides
    a more stable measure of lexical diversity than simple TTR, especially
    for longer texts. The moving window approach reduces the impact of text
    length on the TTR calculation.

    Related GitHub Issue:
        #14 - Advanced Lexical Diversity Metrics
        https://github.com/craigtrim/pystylometry/issues/14

    References:
        Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot:
            The moving-average type-token ratio (MATTR). Journal of Quantitative
            Linguistics, 17(2), 94-100.

    Example:
        >>> result = compute_mattr("Sample text here...", window_size=50)
        >>> print(f"MATTR score: {result.mattr_score:.3f}")
        >>> print(f"Window size: {result.window_size}")
    """

    mattr_score: float  # Average TTR across all windows
    window_size: int  # Size of moving window used
    window_count: int  # Number of windows analyzed
    ttr_std_dev: float  # Standard deviation of TTR across windows
    min_ttr: float  # Minimum TTR in any window
    max_ttr: float  # Maximum TTR in any window
    metadata: dict[str, Any]  # Window-by-window TTR values, etc.


@dataclass
class HDDResult:
    """Result from HD-D (Hypergeometric Distribution D) computation.

    HD-D is a probabilistic measure of lexical diversity based on the
    hypergeometric distribution. It estimates the probability of encountering
    new word types as text length increases, providing a mathematically
    rigorous measure that is less sensitive to text length than TTR.

    Related GitHub Issue:
        #14 - Advanced Lexical Diversity Metrics
        https://github.com/craigtrim/pystylometry/issues/14

    References:
        McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation
            study of sophisticated approaches to lexical diversity assessment.
            Behavior Research Methods, 42(2), 381-392.

    Example:
        >>> result = compute_hdd("Sample text for HD-D analysis...")
        >>> print(f"HD-D score: {result.hdd_score:.3f}")
        >>> print(f"Sample size: {result.sample_size}")
    """

    hdd_score: float  # The HD-D value
    sample_size: int  # Sample size used for calculation
    type_count: int  # Number of unique types in sample
    token_count: int  # Number of tokens in sample
    metadata: dict[str, Any]  # Probability distribution info, etc.


@dataclass
class MSTTRResult:
    """Result from MSTTR (Mean Segmental Type-Token Ratio) computation.

    MSTTR divides the text into sequential segments of equal length and
    computes the average TTR across all segments. This provides a length-
    normalized measure of lexical diversity that is more comparable across
    texts of different lengths.

    Related GitHub Issue:
        #14 - Advanced Lexical Diversity Metrics
        https://github.com/craigtrim/pystylometry/issues/14

    References:
        Johnson, W. (1944). Studies in language behavior: I. A program of research.
            Psychological Monographs, 56(2), 1-15.

    Example:
        >>> result = compute_msttr("Sample text...", segment_size=100)
        >>> print(f"MSTTR score: {result.msttr_score:.3f}")
        >>> print(f"Segments analyzed: {result.segment_count}")
    """

    msttr_score: float  # Mean TTR across all segments
    segment_size: int  # Size of each segment
    segment_count: int  # Number of segments analyzed
    ttr_std_dev: float  # Standard deviation of TTR across segments
    min_ttr: float  # Minimum TTR in any segment
    max_ttr: float  # Maximum TTR in any segment
    segment_ttrs: list[float]  # TTR for each individual segment
    metadata: dict[str, Any]  # Segment details, remaining tokens, etc.


# ===== Word Frequency Sophistication Results =====
# Related to GitHub Issue #15: Word Frequency Sophistication Metrics
# https://github.com/craigtrim/pystylometry/issues/15


@dataclass
class WordFrequencySophisticationResult:
    """Result from word frequency sophistication analysis.

    Word frequency sophistication metrics measure how common or rare the
    vocabulary used in a text is, based on reference frequency lists from
    large corpora. Authors who use less frequent (more sophisticated) words
    score higher on these metrics.

    Related GitHub Issue:
        #15 - Word Frequency Sophistication Metrics
        https://github.com/craigtrim/pystylometry/issues/15

    This analysis uses reference frequency data from:
        - COCA (Corpus of Contemporary American English)
        - BNC (British National Corpus)
        - Google N-grams
        - SUBTLEXus (subtitle frequencies)

    Metrics computed:
        - Mean word frequency (average frequency rank)
        - Median word frequency
        - Rare word ratio (words beyond frequency threshold)
        - Academic word ratio (from Academic Word List)
        - Advanced word ratio (sophisticated vocabulary)

    References:
        Brysbaert, M., & New, B. (2009). Moving beyond Kučera and Francis:
            A critical evaluation of current word frequency norms. Behavior
            Research Methods, Instruments, & Computers, 41(4), 977-990.
        Coxhead, A. (2000). A new academic word list. TESOL Quarterly, 34(2), 213-238.

    Example:
        >>> result = compute_word_frequency_sophistication("Sample text...")
        >>> print(f"Mean frequency rank: {result.mean_frequency_rank:.1f}")
        >>> print(f"Rare word ratio: {result.rare_word_ratio:.3f}")
        >>> print(f"Academic word ratio: {result.academic_word_ratio:.3f}")
    """

    mean_frequency_rank: float  # Average frequency rank of words
    median_frequency_rank: float  # Median frequency rank
    rare_word_ratio: float  # Words beyond frequency threshold / total
    common_word_ratio: float  # High-frequency words / total
    academic_word_ratio: float  # Academic Word List words / total
    advanced_word_ratio: float  # Sophisticated vocabulary / total
    frequency_band_distribution: dict[str, float]  # Distribution across frequency bands
    rarest_words: list[tuple[str, float]]  # Least frequent words with ranks
    most_common_words: list[tuple[str, float]]  # Most frequent words with ranks
    metadata: dict[str, Any]  # Corpus source, band thresholds, total words, etc.


# ===== Additional Readability Results =====
# Related to GitHub Issue #16: Additional Readability Formulas
# https://github.com/craigtrim/pystylometry/issues/16


@dataclass
class DaleChallResult:
    """Result from Dale-Chall Readability Formula.

    The Dale-Chall formula uses a list of 3000 familiar words that 80% of
    fourth-graders understand. Words not on this list are considered "difficult."
    The formula provides a grade level estimate based on sentence length and
    the percentage of difficult words.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula: 0.1579 * (difficult_words / total_words * 100) + 0.0496 * avg_sentence_length

    If % difficult words > 5%, add 3.6365 to the raw score.

    References:
        Dale, E., & Chall, J. S. (1948). A formula for predicting readability.
            Educational Research Bulletin, 27(1), 11-28.
        Chall, J. S., & Dale, E. (1995). Readability revisited: The new Dale-Chall
            readability formula. Brookline Books.

    Example:
        >>> result = compute_dale_chall("Sample text to analyze...")
        >>> print(f"Dale-Chall score: {result.dale_chall_score:.2f}")
        >>> print(f"Grade level: {result.grade_level}")
        >>> print(f"Difficult word %: {result.difficult_word_ratio * 100:.1f}%")
    """

    dale_chall_score: float  # The Dale-Chall readability score
    grade_level: str  # Corresponding grade level (e.g., "7-8", "College")
    difficult_word_count: int  # Words not on Dale-Chall list
    difficult_word_ratio: float  # Difficult words / total words
    avg_sentence_length: float  # Average words per sentence
    total_words: int  # Total word count
    metadata: dict[str, Any]  # List of difficult words, adjusted score, etc.


@dataclass
class LinsearWriteResult:
    """Result from Linsear Write Formula.

    The Linsear Write Formula was developed for the U.S. Air Force to calculate
    the readability of technical manuals. It categorizes words as "easy" (1-2
    syllables) or "hard" (3+ syllables) and uses sentence length to estimate
    grade level. It's particularly effective for technical writing.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    References:
        Klare, G. R. (1974-1975). Assessing readability. Reading Research Quarterly,
            10(1), 62-102.

    Example:
        >>> result = compute_linsear_write("Technical manual text...")
        >>> print(f"Linsear Write score: {result.linsear_score:.2f}")
        >>> print(f"Grade level: {result.grade_level}")
    """

    linsear_score: float  # The Linsear Write score
    grade_level: int  # Corresponding U.S. grade level
    easy_word_count: int  # Words with 1-2 syllables
    hard_word_count: int  # Words with 3+ syllables
    avg_sentence_length: float  # Average words per sentence
    metadata: dict[str, Any]  # Calculation details, sentence count, etc.


@dataclass
class FryResult:
    """Result from Fry Readability Graph.

    The Fry Readability Graph uses average sentence length and average syllables
    per word to determine reading difficulty. It plots these values on a graph
    to determine the grade level. This implementation provides the numerical
    coordinates and estimated grade level.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    References:
        Fry, E. (1968). A readability formula that saves time. Journal of Reading,
            11(7), 513-578.
        Fry, E. (1977). Fry's readability graph: Clarifications, validity, and
            extension to level 17. Journal of Reading, 21(3), 242-252.

    Example:
        >>> result = compute_fry("Sample educational text...")
        >>> print(f"Avg sentence length: {result.avg_sentence_length:.1f}")
        >>> print(f"Avg syllables/100 words: {result.avg_syllables_per_100:.1f}")
        >>> print(f"Grade level: {result.grade_level}")
    """

    avg_sentence_length: float  # Average words per sentence
    avg_syllables_per_100: float  # Average syllables per 100 words
    grade_level: str  # Estimated grade level (e.g., "5", "7", "College")
    graph_zone: str  # Which zone of Fry graph (for validity checking)
    metadata: dict[str, Any]  # Total sentences, total syllables, etc.


@dataclass
class FORCASTResult:
    """Result from FORCAST Readability Formula.

    FORCAST (FORmula for CASTing readability) was developed by the U.S. military
    to assess readability without counting syllables. It uses only single-syllable
    words as a measure, making it faster to compute than syllable-based formulas.
    Particularly useful for technical and military documents.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula: 20 - (N / 10), where N is the number of single-syllable words
    per 150-word sample.

    References:
        Caylor, J. S., Sticht, T. G., Fox, L. C., & Ford, J. P. (1973).
            Methodologies for determining reading requirements of military
            occupational specialties. Human Resources Research Organization.

    Example:
        >>> result = compute_forcast("Military technical document text...")
        >>> print(f"FORCAST score: {result.forcast_score:.2f}")
        >>> print(f"Grade level: {result.grade_level}")
    """

    forcast_score: float  # The FORCAST readability score
    grade_level: int  # Corresponding U.S. grade level
    single_syllable_ratio: float  # Single-syllable words / total words
    single_syllable_count: int  # Count of single-syllable words
    total_words: int  # Total word count
    metadata: dict[str, Any]  # Samples used, calculation details, etc.


@dataclass
class PowersSumnerKearlResult:
    """Result from Powers-Sumner-Kearl Readability Formula.

    The Powers-Sumner-Kearl formula is a variation of the Flesch Reading Ease
    formula, recalibrated for primary grade levels (grades 1-4). It uses
    average sentence length and average syllables per word, but with different
    coefficients optimized for younger readers.

    Related GitHub Issue:
        #16 - Additional Readability Formulas
        https://github.com/craigtrim/pystylometry/issues/16

    Formula: 0.0778 * avg_sentence_length + 0.0455 * avg_syllables_per_word - 2.2029

    References:
        Powers, R. D., Sumner, W. A., & Kearl, B. E. (1958). A recalculation of
            four adult readability formulas. Journal of Educational Psychology,
            49(2), 99-105.

    Example:
        >>> result = compute_powers_sumner_kearl("Children's book text...")
        >>> print(f"PSK score: {result.psk_score:.2f}")
        >>> print(f"Grade level: {result.grade_level}")
    """

    psk_score: float  # The Powers-Sumner-Kearl score
    grade_level: float  # Corresponding grade level (can be decimal for primary grades)
    avg_sentence_length: float  # Average words per sentence
    avg_syllables_per_word: float  # Average syllables per word
    total_sentences: int  # Total sentence count
    total_words: int  # Total word count
    total_syllables: int  # Total syllable count
    metadata: dict[str, Any]  # Calculation details, comparison to Flesch, etc.


# ===== Advanced Syntactic Results =====
# Related to GitHub Issue #17: Advanced Syntactic Analysis
# https://github.com/craigtrim/pystylometry/issues/17


@dataclass
class AdvancedSyntacticResult:
    """Result from advanced syntactic analysis using dependency parsing.

    Advanced syntactic analysis uses dependency parsing to extract sophisticated
    grammatical features that go beyond simple POS tagging. These features
    capture sentence complexity, grammatical sophistication, and syntactic
    style preferences.

    Related GitHub Issue:
        #17 - Advanced Syntactic Analysis
        https://github.com/craigtrim/pystylometry/issues/17

    Features analyzed:
        - Parse tree depth (sentence structural complexity)
        - T-units (minimal terminable units - independent clauses with modifiers)
        - Clausal density (clauses per T-unit)
        - Dependent clause ratio
        - Passive voice ratio
        - Subordination index
        - Coordination index
        - Sentence complexity score

    References:
        Hunt, K. W. (1965). Grammatical structures written at three grade levels.
            NCTE Research Report No. 3.
        Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
        Lu, X. (2010). Automatic analysis of syntactic complexity in second language
            writing. International Journal of Corpus Linguistics, 15(4), 474-496.

    Example:
        >>> result = compute_advanced_syntactic("Complex sentence structures...")
        >>> print(f"Parse tree depth: {result.mean_parse_tree_depth:.1f}")
        >>> print(f"T-units: {result.t_unit_count}")
        >>> print(f"Passive voice %: {result.passive_voice_ratio * 100:.1f}%")
    """

    mean_parse_tree_depth: float  # Average depth of dependency parse trees
    max_parse_tree_depth: int  # Maximum parse tree depth in text
    t_unit_count: int  # Number of T-units (minimal terminable units)
    mean_t_unit_length: float  # Average words per T-unit
    clausal_density: float  # Clauses per T-unit
    dependent_clause_ratio: float  # Dependent clauses / total clauses
    passive_voice_ratio: float  # Passive constructions / total sentences
    subordination_index: float  # Subordinate clauses / total clauses
    coordination_index: float  # Coordinate clauses / total clauses
    sentence_complexity_score: float  # Composite complexity metric
    dependency_distance: float  # Mean distance between heads and dependents
    left_branching_ratio: float  # Left-branching structures / total
    right_branching_ratio: float  # Right-branching structures / total
    metadata: dict[str, Any]  # Parse tree details, clause counts, etc.


# ===== Sentence Type Results =====
# Related to GitHub Issue #18: Sentence Type Classification
# https://github.com/craigtrim/pystylometry/issues/18


@dataclass
class SentenceTypeResult:
    """Result from sentence type classification analysis.

    Sentence type classification categorizes sentences by their grammatical
    structure (simple, compound, complex, compound-complex) and communicative
    function (declarative, interrogative, imperative, exclamatory). Different
    authors and genres show distinct patterns in sentence type distribution.

    Related GitHub Issue:
        #18 - Sentence Type Classification
        https://github.com/craigtrim/pystylometry/issues/18

    Structural types:
        - Simple: One independent clause (e.g., "The cat sat.")
        - Compound: Multiple independent clauses (e.g., "I came, I saw, I conquered.")
        - Complex: One independent + dependent clause(s) (e.g., "When I arrived, I saw her.")
        - Compound-Complex: Multiple independent + dependent (e.g., "I came when called, and I stayed.")

    Functional types:
        - Declarative: Statement (e.g., "The sky is blue.")
        - Interrogative: Question (e.g., "Is the sky blue?")
        - Imperative: Command (e.g., "Look at the sky!")
        - Exclamatory: Exclamation (e.g., "What a blue sky!")

    References:
        Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
        Huddleston, R., & Pullum, G. K. (2002). The Cambridge Grammar of the English Language.

    Example:
        >>> result = compute_sentence_types("Mix of sentence types here...")
        >>> print(f"Simple: {result.simple_ratio * 100:.1f}%")
        >>> print(f"Complex: {result.complex_ratio * 100:.1f}%")
        >>> print(f"Questions: {result.interrogative_ratio * 100:.1f}%")
    """

    # Structural type ratios (sum to 1.0)
    simple_ratio: float  # Simple sentences / total
    compound_ratio: float  # Compound sentences / total
    complex_ratio: float  # Complex sentences / total
    compound_complex_ratio: float  # Compound-complex / total

    # Functional type ratios (sum to 1.0)
    declarative_ratio: float  # Declarative sentences / total
    interrogative_ratio: float  # Interrogative (questions) / total
    imperative_ratio: float  # Imperative (commands) / total
    exclamatory_ratio: float  # Exclamatory sentences / total

    # Counts
    simple_count: int
    compound_count: int
    complex_count: int
    compound_complex_count: int
    declarative_count: int
    interrogative_count: int
    imperative_count: int
    exclamatory_count: int
    total_sentences: int

    # Diversity
    structural_diversity: float  # Shannon entropy of structural type distribution
    functional_diversity: float  # Shannon entropy of functional type distribution

    metadata: dict[str, Any]  # Sentence-by-sentence classifications, etc.


# ===== Extended N-gram Results =====
# Related to GitHub Issue #19: Extended N-gram Features
# https://github.com/craigtrim/pystylometry/issues/19


@dataclass
class ExtendedNgramResult:
    """Result from extended n-gram analysis.

    Extended n-gram analysis goes beyond basic bigram/trigram entropy to provide
    comprehensive n-gram statistics including frequency distributions, most
    distinctive n-grams, skipgrams, and part-of-speech n-grams. These features
    are valuable for authorship attribution and style analysis.

    Related GitHub Issue:
        #19 - Extended N-gram Features
        https://github.com/craigtrim/pystylometry/issues/19

    Features computed:
        - Trigram frequency distributions and top trigrams
        - 4-gram frequency distributions and top 4-grams
        - Skipgrams (n-grams with gaps, e.g., "the * dog")
        - POS n-grams (e.g., "DET ADJ NOUN")
        - Character trigrams and 4-grams
        - N-gram diversity metrics
        - Entropy for each n-gram order

    References:
        Guthrie, D., Allison, B., Liu, W., Guthrie, L., & Wilks, Y. (2006).
            A closer look at skip-gram modelling. LREC.
        Stamatatos, E. (2009). A survey of modern authorship attribution methods.
            JASIST, 60(3), 538-556.

    Example:
        >>> result = compute_extended_ngrams("Sample text for n-gram analysis...")
        >>> print(f"Top trigrams: {result.top_word_trigrams[:5]}")
        >>> print(f"Trigram entropy: {result.word_trigram_entropy:.2f}")
    """

    # Word n-grams
    top_word_trigrams: list[tuple[str, int]]  # Most frequent word trigrams
    top_word_4grams: list[tuple[str, int]]  # Most frequent word 4-grams
    word_trigram_count: int  # Total unique word trigrams
    word_4gram_count: int  # Total unique word 4-grams
    word_trigram_entropy: float  # Shannon entropy of trigram distribution
    word_4gram_entropy: float  # Shannon entropy of 4-gram distribution

    # Skipgrams (n-grams with gaps)
    top_skipgrams_2_1: list[tuple[str, int]]  # Top 2-skipgrams (gap of 1)
    top_skipgrams_3_1: list[tuple[str, int]]  # Top 3-skipgrams (gap of 1)
    skipgram_2_1_count: int  # Unique 2-skipgrams
    skipgram_3_1_count: int  # Unique 3-skipgrams

    # POS n-grams
    top_pos_trigrams: list[tuple[str, int]]  # Most frequent POS trigrams
    top_pos_4grams: list[tuple[str, int]]  # Most frequent POS 4-grams
    pos_trigram_count: int  # Unique POS trigrams
    pos_4gram_count: int  # Unique POS 4-grams
    pos_trigram_entropy: float  # Shannon entropy of POS trigram distribution

    # Character n-grams
    top_char_trigrams: list[tuple[str, int]]  # Most frequent character trigrams
    top_char_4grams: list[tuple[str, int]]  # Most frequent character 4-grams
    char_trigram_entropy: float  # Shannon entropy of char trigram distribution
    char_4gram_entropy: float  # Shannon entropy of char 4-gram distribution

    metadata: dict[str, Any]  # Full frequency distributions, parameters, etc.


# ===== Stylistic Markers Results =====
# Related to GitHub Issue #20: Stylistic Markers
# https://github.com/craigtrim/pystylometry/issues/20


@dataclass
class StylisticMarkersResult:
    """Result from stylistic markers analysis.

    Stylistic markers are specific linguistic features that authors tend to use
    consistently and often subconsciously. These include contraction usage,
    intensifier preferences, hedging expressions, punctuation habits, and more.
    They are powerful indicators of authorial identity.

    Related GitHub Issue:
        #20 - Stylistic Markers
        https://github.com/craigtrim/pystylometry/issues/20

    Markers analyzed:
        - Contraction usage (don't vs. do not, I'm vs. I am, etc.)
        - Intensifiers (very, really, extremely, quite, etc.)
        - Hedges (maybe, perhaps, probably, somewhat, etc.)
        - Modal auxiliaries (can, could, may, might, must, should, will, would)
        - Negation patterns (not, no, never, none, neither, etc.)
        - Exclamation frequency
        - Question frequency
        - Quotation usage
        - Parenthetical expressions
        - Ellipses and dashes

    References:
        Argamon, S., & Levitan, S. (2005). Measuring the usefulness of function
            words for authorship attribution. ACH/ALLC.
        Pennebaker, J. W. (2011). The secret life of pronouns. Bloomsbury Press.

    Example:
        >>> result = compute_stylistic_markers("Sample text with various markers...")
        >>> print(f"Contraction ratio: {result.contraction_ratio * 100:.1f}%")
        >>> print(f"Intensifier density: {result.intensifier_density:.2f}")
        >>> print(f"Hedging density: {result.hedging_density:.2f}")
    """

    # Contraction patterns
    contraction_ratio: float  # Contractions / (contractions + full forms)
    contraction_count: int  # Total contractions
    expanded_form_count: int  # Total expanded forms (e.g., "do not" vs "don't")
    top_contractions: list[tuple[str, int]]  # Most frequent contractions

    # Intensifiers and hedges
    intensifier_density: float  # Intensifiers per 100 words
    intensifier_count: int  # Total intensifier count
    top_intensifiers: list[tuple[str, int]]  # Most frequent intensifiers
    hedging_density: float  # Hedges per 100 words
    hedging_count: int  # Total hedge count
    top_hedges: list[tuple[str, int]]  # Most frequent hedges

    # Modal auxiliaries
    modal_density: float  # Modal auxiliaries per 100 words
    modal_distribution: dict[str, int]  # Count per modal (can, could, may, etc.)
    epistemic_modal_ratio: float  # Epistemic modals / all modals
    deontic_modal_ratio: float  # Deontic modals / all modals

    # Negation
    negation_density: float  # Negation markers per 100 words
    negation_count: int  # Total negation markers
    negation_types: dict[str, int]  # not, no, never, etc. with counts

    # Punctuation style
    exclamation_density: float  # Exclamation marks per 100 words
    question_density: float  # Question marks per 100 words
    quotation_density: float  # Quotation marks per 100 words
    parenthetical_density: float  # Parentheses per 100 words
    ellipsis_density: float  # Ellipses per 100 words
    dash_density: float  # Dashes (em/en) per 100 words
    semicolon_density: float  # Semicolons per 100 words
    colon_density: float  # Colons per 100 words

    metadata: dict[str, Any]  # Full lists, total word count, etc.


# ===== Vocabulary Overlap Results =====
# Related to GitHub Issue #21: Vocabulary Overlap and Similarity Metrics
# https://github.com/craigtrim/pystylometry/issues/21


@dataclass
class VocabularyOverlapResult:
    """Result from vocabulary overlap and similarity analysis.

    Vocabulary overlap metrics measure the similarity between two texts based on
    their shared vocabulary. These metrics are useful for authorship verification,
    plagiarism detection, and measuring stylistic consistency across texts.

    Related GitHub Issue:
        #21 - Vocabulary Overlap and Similarity Metrics
        https://github.com/craigtrim/pystylometry/issues/21

    Metrics computed:
        - Jaccard similarity (intersection / union)
        - Dice coefficient (2 * intersection / sum of sizes)
        - Overlap coefficient (intersection / min(size1, size2))
        - Cosine similarity (using word frequency vectors)
        - Shared vocabulary size and ratio
        - Unique words in each text
        - Most distinctive words for each text

    References:
        Jaccard, P. (1912). The distribution of the flora in the alpine zone.
            New Phytologist, 11(2), 37-50.
        Salton, G., & McGill, M. J. (1983). Introduction to Modern Information
            Retrieval. McGraw-Hill.

    Example:
        >>> result = compute_vocabulary_overlap(text1, text2)
        >>> print(f"Jaccard similarity: {result.jaccard_similarity:.3f}")
        >>> print(f"Shared vocabulary: {result.shared_vocab_size} words")
        >>> print(f"Text1 unique: {result.text1_unique_count}")
    """

    # Similarity scores (0-1 range)
    jaccard_similarity: float  # Intersection / union
    dice_coefficient: float  # 2 * intersection / (size1 + size2)
    overlap_coefficient: float  # Intersection / min(size1, size2)
    cosine_similarity: float  # Cosine of frequency vectors

    # Vocabulary sizes
    text1_vocab_size: int  # Unique words in text 1
    text2_vocab_size: int  # Unique words in text 2
    shared_vocab_size: int  # Words in both texts
    union_vocab_size: int  # Words in either text
    text1_unique_count: int  # Words only in text 1
    text2_unique_count: int  # Words only in text 2

    # Shared and distinctive vocabulary
    shared_words: list[str]  # Words appearing in both texts
    text1_distinctive_words: list[tuple[str, float]]  # Words + TF-IDF scores for text 1
    text2_distinctive_words: list[tuple[str, float]]  # Words + TF-IDF scores for text 2

    # Ratios
    text1_coverage: float  # Shared / text1_vocab (how much of text1 is shared)
    text2_coverage: float  # Shared / text2_vocab (how much of text2 is shared)

    metadata: dict[str, Any]  # Full vocabulary sets, frequency vectors, etc.


# ===== Cohesion and Coherence Results =====
# Related to GitHub Issue #22: Cohesion and Coherence Metrics
# https://github.com/craigtrim/pystylometry/issues/22


@dataclass
class CohesionCoherenceResult:
    """Result from cohesion and coherence analysis.

    Cohesion and coherence metrics measure how well a text holds together
    structurally (cohesion) and semantically (coherence). These metrics are
    important for analyzing writing quality, readability, and authorial
    sophistication.

    Related GitHub Issue:
        #22 - Cohesion and Coherence Metrics
        https://github.com/craigtrim/pystylometry/issues/22

    Cohesion features:
        - Referential cohesion (pronouns, demonstratives pointing back)
        - Lexical cohesion (word repetition, synonyms, semantic relatedness)
        - Connective density (discourse markers, conjunctions)
        - Anaphora resolution success rate
        - Lexical chains (sequences of semantically related words)

    Coherence features:
        - Sentence-to-sentence semantic similarity
        - Topic consistency across paragraphs
        - Discourse structure (thesis, support, conclusion)
        - Semantic overlap between adjacent sentences

    References:
        Halliday, M. A. K., & Hasan, R. (1976). Cohesion in English. Longman.
        Graesser, A. C., McNamara, D. S., & Kulikowich, J. M. (2011). Coh-Metrix:
            Providing multilevel analyses of text characteristics. Educational
            Researcher, 40(5), 223-234.

    Example:
        >>> result = compute_cohesion_coherence("Multi-paragraph text...")
        >>> print(f"Pronoun density: {result.pronoun_density:.2f}")
        >>> print(f"Lexical overlap: {result.adjacent_sentence_overlap:.3f}")
        >>> print(f"Connective density: {result.connective_density:.2f}")
    """

    # Referential cohesion
    pronoun_density: float  # Pronouns per 100 words
    demonstrative_density: float  # Demonstratives (this, that, these, those) per 100 words
    anaphora_count: int  # Anaphoric references detected
    anaphora_resolution_ratio: float  # Successfully resolved / total

    # Lexical cohesion
    word_repetition_ratio: float  # Repeated content words / total content words
    synonym_density: float  # Synonym pairs per 100 words
    lexical_chain_count: int  # Number of lexical chains detected
    mean_chain_length: float  # Average length of lexical chains
    content_word_overlap: float  # Content word overlap between sentences

    # Connectives and discourse markers
    connective_density: float  # Discourse connectives per 100 words
    additive_connective_ratio: float  # "and", "also", "furthermore" / total connectives
    adversative_connective_ratio: float  # "but", "however", "nevertheless" / total
    causal_connective_ratio: float  # "because", "therefore", "thus" / total
    temporal_connective_ratio: float  # "then", "after", "before" / total

    # Coherence measures
    adjacent_sentence_overlap: float  # Mean semantic overlap between adjacent sentences
    paragraph_topic_consistency: float  # Mean topic consistency within paragraphs
    mean_sentence_similarity: float  # Mean cosine similarity between all sentence pairs
    semantic_coherence_score: float  # Composite coherence metric (0-1)

    # Structural coherence
    paragraph_count: int  # Number of paragraphs detected
    mean_paragraph_length: float  # Mean sentences per paragraph
    discourse_structure_score: float  # Quality of intro/body/conclusion structure

    metadata: dict[str, Any]  # Lexical chains, connective lists, similarity matrices, etc.


# ===== Genre and Register Results =====
# Related to GitHub Issue #23: Genre and Register Features
# https://github.com/craigtrim/pystylometry/issues/23


@dataclass
class GenreRegisterResult:
    """Result from genre and register classification analysis.

    Genre and register features distinguish between different types of texts
    (academic, journalistic, fiction, legal, etc.) based on linguistic patterns.
    These features can help identify the context and formality level of a text,
    and are useful for authorship attribution when combined with other metrics.

    Related GitHub Issue:
        #23 - Genre and Register Features
        https://github.com/craigtrim/pystylometry/issues/23

    Features analyzed:
        - Formality markers (Latinate words, nominalizations, passive voice)
        - Personal vs. impersonal style (1st/2nd person vs. 3rd person)
        - Abstract vs. concrete vocabulary
        - Technical term density
        - Narrative vs. expository markers
        - Dialogue presence and ratio
        - Register classification (frozen, formal, consultative, casual, intimate)

    References:
        Biber, D. (1988). Variation across speech and writing. Cambridge University Press.
        Biber, D., & Conrad, S. (2009). Register, genre, and style. Cambridge
            University Press.
        Heylighen, F., & Dewaele, J. M. (1999). Formality of language: Definition,
            measurement and behavioral determinants. Internal Report, Center "Leo
            Apostel", Free University of Brussels.

    Example:
        >>> result = compute_genre_register("Academic paper text...")
        >>> print(f"Formality score: {result.formality_score:.2f}")
        >>> print(f"Register: {result.register_classification}")
        >>> print(f"Genre prediction: {result.predicted_genre}")
    """

    # Formality indicators
    formality_score: float  # Composite formality score (0-100)
    latinate_ratio: float  # Latinate words / total words
    nominalization_density: float  # Nominalizations per 100 words
    passive_voice_density: float  # Passive constructions per 100 words

    # Personal vs. impersonal
    first_person_ratio: float  # 1st person pronouns / total pronouns
    second_person_ratio: float  # 2nd person pronouns / total pronouns
    third_person_ratio: float  # 3rd person pronouns / total pronouns
    impersonal_construction_density: float  # "It is...", "There are..." per 100 words

    # Abstract vs. concrete
    abstract_noun_ratio: float  # Abstract nouns / total nouns
    concrete_noun_ratio: float  # Concrete nouns / total nouns
    abstractness_score: float  # Composite abstractness (based on word concreteness ratings)

    # Technical and specialized
    technical_term_density: float  # Technical/specialized terms per 100 words
    jargon_density: float  # Domain-specific jargon per 100 words

    # Narrative vs. expository
    narrative_marker_density: float  # Past tense, action verbs per 100 words
    expository_marker_density: float  # Present tense, linking verbs per 100 words
    narrative_expository_ratio: float  # Narrative / expository markers

    # Dialogue and quotation
    dialogue_ratio: float  # Dialogue / total text (estimated)
    quotation_density: float  # Quotations per 100 words

    # Classification results
    register_classification: str  # frozen, formal, consultative, casual, intimate
    predicted_genre: str  # academic, journalistic, fiction, legal, conversational, etc.
    genre_confidence: float  # Confidence in genre prediction (0-1)

    # Feature scores for major genres (0-1 scores for each)
    academic_score: float
    journalistic_score: float
    fiction_score: float
    legal_score: float
    conversational_score: float

    metadata: dict[str, Any]  # Feature details, word lists, classification probabilities, etc.


# ===== Additional Authorship Results =====
# Related to GitHub Issue #24: Additional Authorship Attribution Methods
# https://github.com/craigtrim/pystylometry/issues/24


@dataclass
class KilgarriffResult:
    """Result from Kilgarriff's Chi-squared method.

    Kilgarriff's chi-squared method compares word frequency distributions between
    texts using the chi-squared test. It's particularly effective for authorship
    attribution when comparing frequency profiles of common words.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    References:
        Kilgarriff, A. (2001). Comparing corpora. International Journal of Corpus
            Linguistics, 6(1), 97-133.

    Example:
        >>> result = compute_kilgarriff(text1, text2)
        >>> print(f"Chi-squared: {result.chi_squared:.2f}")
        >>> print(f"P-value: {result.p_value:.4f}")
    """

    chi_squared: float  # Chi-squared statistic
    p_value: float  # Statistical significance (p-value)
    degrees_of_freedom: int  # df for chi-squared test
    feature_count: int  # Number of features (words) compared
    most_distinctive_features: list[tuple[str, float]]  # Words + chi-squared contributions
    metadata: dict[str, Any]  # Frequency tables, expected values, etc.


@dataclass
class MinMaxResult:
    """Result from Min-Max distance method (Burrows' original method).

    The Min-Max method normalizes feature frequencies using min-max scaling,
    then computes distance between texts. This was Burrows' original approach
    before developing Delta.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    References:
        Burrows, J. F. (1992). Not unless you ask nicely: The interpretative
            nexus between analysis and information. Literary and Linguistic
            Computing, 7(2), 91-109.

    Example:
        >>> result = compute_minmax(text1, text2)
        >>> print(f"MinMax distance: {result.minmax_distance:.3f}")
    """

    minmax_distance: float  # Min-max normalized distance
    feature_count: int  # Number of features used
    most_distinctive_features: list[tuple[str, float]]  # Features + contributions
    metadata: dict[str, Any]  # Normalized frequencies, scaling parameters, etc.


@dataclass
class JohnsBurrowsResult:
    """Result from John's Burrows' variation of Delta.

    John Burrows has developed several variations of the Delta method over
    the years. This captures alternative formulations including Quadratic
    Delta and other distance measures.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    References:
        Burrows, J. (2005). Who wrote Shamela? Verifying the authorship of a
            parodic text. Literary and Linguistic Computing, 20(4), 437-450.

    Example:
        >>> result = compute_johns_delta(text1, text2, method="quadratic")
        >>> print(f"Quadratic Delta: {result.delta_score:.3f}")
    """

    delta_score: float  # Delta distance score
    method: str  # "quadratic", "weighted", "rotated", etc.
    feature_count: int  # Number of MFW used
    most_distinctive_features: list[tuple[str, float]]  # Features + contributions
    metadata: dict[str, Any]  # Method-specific parameters, z-scores, etc.


# ===== Rhythm and Prosody Results =====
# Related to GitHub Issue #25: Rhythm and Prosody Metrics
# https://github.com/craigtrim/pystylometry/issues/25


@dataclass
class RhythmProsodyResult:
    """Result from rhythm and prosody analysis.

    Rhythm and prosody metrics capture the musical qualities of written language,
    including stress patterns, syllable rhythms, and phonological features. While
    these are typically studied in spoken language, written text preserves many
    rhythmic patterns that vary by author and genre.

    Related GitHub Issue:
        #25 - Rhythm and Prosody Metrics
        https://github.com/craigtrim/pystylometry/issues/25

    Features analyzed:
        - Syllable patterns and stress patterns
        - Rhythmic regularity (coefficient of variation of syllable counts)
        - Phonological features (alliteration, assonance)
        - Syllable complexity (consonant clusters)
        - Sentence rhythm (alternating long/short sentences)
        - Polysyllabic word ratio

    References:
        Lea, R. B., Mulligan, E. J., & Walton, J. H. (2005). Sentence rhythm and
            text comprehension. Memory & Cognition, 33(3), 388-396.
        Louwerse, M. M., & Benesh, N. (2012). Representing spatial structure through
            maps and language: Lord of the Rings encodes the spatial structure of
            Middle Earth. Cognitive Science, 36(8), 1556-1569.

    Example:
        >>> result = compute_rhythm_prosody("Sample text with rhythm...")
        >>> print(f"Syllables per word: {result.mean_syllables_per_word:.2f}")
        >>> print(f"Rhythmic regularity: {result.rhythmic_regularity:.3f}")
        >>> print(f"Alliteration density: {result.alliteration_density:.2f}")
    """

    # Syllable patterns
    mean_syllables_per_word: float  # Average syllables per word
    syllable_std_dev: float  # Std dev of syllables per word
    polysyllabic_ratio: float  # Words with 3+ syllables / total
    monosyllabic_ratio: float  # Single-syllable words / total

    # Rhythmic regularity
    rhythmic_regularity: float  # 1 / CV of syllable counts (higher = more regular)
    syllable_cv: float  # Coefficient of variation of syllables per word
    stress_pattern_entropy: float  # Entropy of stress patterns

    # Sentence rhythm
    sentence_length_alternation: float  # Degree of long/short alternation
    sentence_rhythm_score: float  # Composite rhythm score

    # Phonological features
    alliteration_density: float  # Alliterative word pairs per 100 words
    assonance_density: float  # Assonant word pairs per 100 words
    consonance_density: float  # Consonant word pairs per 100 words

    # Syllable complexity
    mean_consonant_cluster_length: float  # Avg consonants in clusters
    initial_cluster_ratio: float  # Words starting with clusters / total
    final_cluster_ratio: float  # Words ending with clusters / total

    # Stress patterns (estimated for written text)
    iambic_ratio: float  # Iambic patterns (unstressed-stressed) / total
    trochaic_ratio: float  # Trochaic patterns (stressed-unstressed) / total
    dactylic_ratio: float  # Dactylic patterns / total
    anapestic_ratio: float  # Anapestic patterns / total

    metadata: dict[str, Any]  # Syllable counts, stress patterns, phoneme data, etc.


# ===== Unified Analysis Result =====


@dataclass
class AnalysisResult:
    """Unified result from comprehensive stylometric analysis."""

    lexical: dict[str, Any] | None = None
    readability: dict[str, Any] | None = None
    syntactic: dict[str, Any] | None = None
    authorship: dict[str, Any] | None = None
    ngrams: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

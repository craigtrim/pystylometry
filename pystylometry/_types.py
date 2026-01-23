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

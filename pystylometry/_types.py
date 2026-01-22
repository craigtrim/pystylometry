"""Result dataclasses for all pystylometry metrics."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ===== Lexical Results =====


@dataclass
class MTLDResult:
    """Result from MTLD (Measure of Textual Lexical Diversity) computation."""

    mtld_forward: float
    mtld_backward: float
    mtld_average: float
    metadata: Dict[str, Any]


@dataclass
class YuleResult:
    """Result from Yule's K and I computation."""

    yule_k: float
    yule_i: float
    metadata: Dict[str, Any]


@dataclass
class HapaxResult:
    """Result from Hapax Legomena analysis."""

    hapax_count: int
    hapax_ratio: float
    dis_hapax_count: int
    dis_hapax_ratio: float
    sichel_s: float
    honore_r: float
    metadata: Dict[str, Any]


# ===== Readability Results =====


@dataclass
class FleschResult:
    """Result from Flesch Reading Ease and Flesch-Kincaid Grade computation."""

    reading_ease: float
    grade_level: float
    difficulty: str  # "Very Easy", "Easy", "Fairly Easy", "Standard", etc.
    metadata: Dict[str, Any]


@dataclass
class SMOGResult:
    """Result from SMOG Index computation."""

    smog_index: float
    grade_level: int
    metadata: Dict[str, Any]


@dataclass
class GunningFogResult:
    """Result from Gunning Fog Index computation."""

    fog_index: float
    grade_level: int
    metadata: Dict[str, Any]


@dataclass
class ColemanLiauResult:
    """Result from Coleman-Liau Index computation."""

    cli_index: float
    grade_level: int
    metadata: Dict[str, Any]


@dataclass
class ARIResult:
    """Result from Automated Readability Index computation."""

    ari_score: float
    grade_level: int
    age_range: str
    metadata: Dict[str, Any]


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
    metadata: Dict[str, Any]


@dataclass
class SentenceStatsResult:
    """Result from sentence-level statistics."""

    mean_sentence_length: float
    sentence_length_std: float
    sentence_length_range: int
    min_sentence_length: int
    max_sentence_length: int
    sentence_count: int
    metadata: Dict[str, Any]


# ===== Authorship Results =====


@dataclass
class BurrowsDeltaResult:
    """Result from Burrows' Delta computation."""

    delta_score: float
    distance_type: str  # "burrows", "cosine", "eder"
    mfw_count: int
    metadata: Dict[str, Any]


@dataclass
class ZetaResult:
    """Result from Zeta score computation."""

    zeta_score: float
    marker_words: List[str]
    anti_marker_words: List[str]
    metadata: Dict[str, Any]


# ===== N-gram Results =====


@dataclass
class EntropyResult:
    """Result from n-gram entropy computation."""

    entropy: float
    perplexity: float
    ngram_type: str  # "character_bigram", "word_bigram", "word_trigram"
    metadata: Dict[str, Any]


# ===== Unified Analysis Result =====


@dataclass
class AnalysisResult:
    """Unified result from comprehensive stylometric analysis."""

    lexical: Optional[Dict[str, Any]] = None
    readability: Optional[Dict[str, Any]] = None
    syntactic: Optional[Dict[str, Any]] = None
    authorship: Optional[Dict[str, Any]] = None
    ngrams: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

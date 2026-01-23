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
    """Result from SMOG Index computation.

    API Consistency Note (Empty Input Handling):
    ============================================
    Changed grade_level from int to float to support NaN for empty input.
    This maintains API consistency with FleschResult and prevents conflating
    "no data" (NaN) with "kindergarten level" (0).

    Reference: PR #3 (Flesch), PR #2 (Coleman-Liau), PR #4 (Gunning Fog)
    See: https://github.com/craigtrim/pystylometry/pull/3
    """

    smog_index: float
    grade_level: float  # Changed from int to float for NaN support (API consistency)
    metadata: dict[str, Any]


@dataclass
class GunningFogResult:
    """Result from Gunning Fog Index computation.

    API Consistency Note (Empty Input Handling):
    ============================================
    Changed grade_level from int to float to support NaN for empty input.
    This maintains API consistency with FleschResult and prevents conflating
    "no data" (NaN) with "kindergarten level" (0).

    Reference: PR #4, aligned with Flesch PR #3, Coleman-Liau PR #2
    See: https://github.com/craigtrim/pystylometry/pull/4
    """

    fog_index: float
    grade_level: float  # Changed from int to float for NaN support (API consistency)
    metadata: dict[str, Any]


@dataclass
class ColemanLiauResult:
    """Result from Coleman-Liau Index computation.

    API Consistency Note (Empty Input Handling):
    ============================================
    Changed grade_level from int to float to support NaN for empty input.
    This maintains API consistency with FleschResult and prevents conflating
    "no data" (NaN) with "kindergarten level" (0).

    Reference: PR #2, aligned with Flesch PR #3, Gunning Fog PR #4
    See: https://github.com/craigtrim/pystylometry/pull/2
    """

    cli_index: float
    grade_level: float  # Changed from int to float for NaN support (API consistency)
    metadata: dict[str, Any]


@dataclass
class ARIResult:
    """Result from Automated Readability Index computation.

    API Consistency Note (Empty Input Handling):
    ============================================
    Changed grade_level from int to float to support NaN for empty input.
    This maintains API consistency with FleschResult and prevents conflating
    "no data" (NaN) with "kindergarten level" (0).

    Related: Flesch PR #3, Coleman-Liau PR #2, Gunning Fog PR #4
    """

    ari_score: float
    grade_level: float  # Changed from int to float for NaN support (API consistency)
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

"""Gunning Fog Index with NLP-enhanced complex word detection.

This module computes the Gunning Fog Index, a readability metric that
estimates the years of formal education needed to understand text on first reading.

This implementation includes native chunked analysis for stylometric fingerprinting.

Related GitHub Issues:
    #4 - NLP-enhanced complex word detection
    #27 - Native chunked analysis with Distribution dataclass

Historical Background:
----------------------
The Gunning Fog Index was developed by Robert Gunning in 1952 as part of his
work helping businesses improve the clarity of their writing. The formula produces
a U.S. grade-level score (e.g., 12 = high school senior reading level).

Reference:
    Gunning, R. (1952). The Technique of Clear Writing.
    McGraw-Hill, New York.
"""

import math

from .._normalize import normalize_for_readability
from .._types import Distribution, GunningFogResult, chunk_text, make_distribution
from .._utils import split_sentences, tokenize
from .complex_words import process_text_for_complex_words

# Formula coefficient from Gunning (1952)
_FOG_COEFFICIENT = 0.4


def _compute_gunning_fog_single(text: str, spacy_model: str) -> tuple[float, float, dict]:
    """Compute Gunning Fog metrics for a single chunk of text.

    Returns:
        Tuple of (fog_index, grade_level, metadata_dict).
        Returns (nan, nan, metadata) for empty/invalid input.
    """
    sentences = split_sentences(text)
    all_tokens = tokenize(text)
    tokens = normalize_for_readability(all_tokens)

    if len(sentences) == 0 or len(tokens) == 0:
        return (
            float("nan"),
            float("nan"),
            {
                "sentence_count": 0,
                "word_count": 0,
                "complex_word_count": 0,
                "complex_word_percentage": 0.0,
            },
        )

    # Count complex words using NLP-enhanced detection
    complex_word_count, detection_metadata = process_text_for_complex_words(
        text, tokens, model=spacy_model
    )

    # Calculate formula components
    average_words_per_sentence = len(tokens) / len(sentences)
    complex_word_percentage = (complex_word_count / len(tokens)) * 100

    # Apply Gunning Fog formula
    fog_index = _FOG_COEFFICIENT * (average_words_per_sentence + complex_word_percentage)
    grade_level = max(0, min(20, round(fog_index)))

    metadata = {
        "sentence_count": len(sentences),
        "word_count": len(tokens),
        "complex_word_count": complex_word_count,
        "complex_word_percentage": complex_word_percentage,
        "average_words_per_sentence": average_words_per_sentence,
        **detection_metadata,
    }

    return (fog_index, float(grade_level), metadata)


def compute_gunning_fog(
    text: str, chunk_size: int = 1000, spacy_model: str = "en_core_web_sm"
) -> GunningFogResult:
    """
    Compute Gunning Fog Index with NLP-enhanced complex word detection.

    This function uses native chunked analysis to capture variance and patterns
    across the text, which is essential for stylometric fingerprinting.

    Formula (Gunning, 1952):
    ------------------------
        Fog Index = 0.4 × [(words/sentences) + 100 × (complex words/words)]

    Where complex words are words with 3+ syllables, EXCLUDING:
        1. Proper nouns (names, places, organizations)
        2. Compound words (hyphenated)
        3. Common verb forms (-es, -ed, -ing endings)

    Related GitHub Issues:
        #4 - NLP-enhanced complex word detection
        #27 - Native chunked analysis with Distribution dataclass

    Reference:
        Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.

    Args:
        text: Input text to analyze
        chunk_size: Number of words per chunk (default: 1000).
            The text is divided into chunks of this size, and metrics are
            computed per-chunk.
        spacy_model: spaCy model name for enhanced mode (default: "en_core_web_sm")

    Returns:
        GunningFogResult with:
            - fog_index: Mean Fog Index across chunks
            - grade_level: Mean grade level across chunks
            - fog_index_dist: Distribution with per-chunk values and stats
            - grade_level_dist: Distribution with per-chunk values and stats
            - chunk_size: The chunk size used
            - chunk_count: Number of chunks analyzed

    Example:
        >>> result = compute_gunning_fog("Long text here...", chunk_size=1000)
        >>> result.fog_index  # Mean across chunks
        12.5
        >>> result.fog_index_dist.std  # Variance reveals fingerprint
        2.1
    """
    # Chunk the text
    chunks = chunk_text(text, chunk_size)

    # Compute metrics per chunk
    fog_values = []
    grade_values = []
    total_sentences = 0
    total_words = 0
    total_complex = 0
    detection_metadata: dict = {}

    for chunk in chunks:
        fi, gl, meta = _compute_gunning_fog_single(chunk, spacy_model)
        if not math.isnan(fi):
            fog_values.append(fi)
            grade_values.append(gl)
        total_sentences += meta.get("sentence_count", 0)
        total_words += meta.get("word_count", 0)
        total_complex += meta.get("complex_word_count", 0)
        # Capture detection metadata from first chunk (same for all chunks)
        if not detection_metadata and "mode" in meta:
            detection_metadata = {
                "mode": meta.get("mode"),
                "proper_noun_detection": meta.get("proper_noun_detection"),
                "inflection_handling": meta.get("inflection_handling"),
            }
            if "spacy_model" in meta:
                detection_metadata["spacy_model"] = meta.get("spacy_model")

    # Handle empty or all-invalid chunks
    if not fog_values:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return GunningFogResult(
            fog_index=float("nan"),
            grade_level=float("nan"),
            fog_index_dist=empty_dist,
            grade_level_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=len(chunks),
            metadata={
                # Backward-compatible keys
                "sentence_count": 0,
                "word_count": 0,
                "complex_word_count": 0,
                "complex_word_percentage": 0.0,
                "average_words_per_sentence": 0.0,
                # New prefixed keys for consistency
                "total_sentence_count": 0,
                "total_word_count": 0,
                "total_complex_word_count": 0,
                "reliable": False,
                # Detection metadata
                "mode": "none",
                "proper_noun_detection": "none",
                "inflection_handling": "none",
            },
        )

    # Build distributions
    fog_dist = make_distribution(fog_values)
    grade_dist = make_distribution(grade_values)

    # Reliability heuristic
    reliable = total_words >= 100 and total_sentences >= 3

    # Ensure detection metadata has defaults
    if not detection_metadata:
        detection_metadata = {
            "mode": "none",
            "proper_noun_detection": "none",
            "inflection_handling": "none",
        }

    return GunningFogResult(
        fog_index=fog_dist.mean,
        grade_level=grade_dist.mean,
        fog_index_dist=fog_dist,
        grade_level_dist=grade_dist,
        chunk_size=chunk_size,
        chunk_count=len(chunks),
        metadata={
            # Backward-compatible keys
            "sentence_count": total_sentences,
            "word_count": total_words,
            "complex_word_count": total_complex,
            "complex_word_percentage": (total_complex / total_words * 100)
            if total_words > 0
            else 0,
            "average_words_per_sentence": total_words / total_sentences
            if total_sentences > 0
            else 0,
            # New prefixed keys for consistency
            "total_sentence_count": total_sentences,
            "total_word_count": total_words,
            "total_complex_word_count": total_complex,
            "reliable": reliable,
            # Detection metadata
            **detection_metadata,
        },
    )

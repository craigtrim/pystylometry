"""Dialect marker data loading and caching.

This module provides efficient loading and caching of the dialect markers JSON
database. The JSON file contains vocabulary pairs, spelling patterns, grammar
patterns, and other linguistic markers used for dialect detection.

Related GitHub Issues:
    #35 - Dialect detection with extensible JSON markers
    https://github.com/craigtrim/pystylometry/issues/35
    #30 - Whonix stylometry features (regional linguistic preferences)
    https://github.com/craigtrim/pystylometry/issues/30

Architecture:
    The loader uses module-level caching to ensure the JSON file is read only
    once per Python session. This is important for performance when analyzing
    multiple texts, as the dialect markers database is moderately large (~50KB).

    The loader also pre-compiles regex patterns from the JSON to avoid repeated
    compilation overhead during detection.

Data Structure:
    The dialect_markers.json file follows an extensible schema with:
    - metadata: Version, sources, last updated date
    - feature_levels: Linguistic level categorization (phonological, etc.)
    - eye_dialect: Informal register markers (gonna, wanna)
    - pragmatic_markers: Discourse and politeness markers
    - vocabulary.pairs: American/British word pairs with categories
    - vocabulary.exclusive: Region-specific vocabulary
    - spelling_patterns.british_american: Regex patterns with weights
    - spelling_patterns.standalone: Direct word pairs
    - grammar_patterns: Grammar difference patterns
    - punctuation_patterns: Punctuation conventions
    - idiomatic_expressions: Idioms by dialect

References:
    Nerbonne, John. "Data-Driven Dialectology." Language and Linguistics
        Compass, vol. 3, no. 1, 2009, pp. 175-198.
    Grieve, Jack. "Quantitative Authorship Attribution: An Evaluation of
        Techniques." Literary and Linguistic Computing, vol. 22, no. 3,
        2007, pp. 251-270.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

# Path to the dialect markers JSON file
_DATA_DIR = Path(__file__).parent / "_data"
_MARKERS_FILE = _DATA_DIR / "dialect_markers.json"


@dataclass
class CompiledSpellingPattern:
    """Pre-compiled spelling pattern for efficient matching.

    Spelling patterns are compiled once at load time to avoid repeated
    regex compilation during detection. Each pattern includes metadata
    for weighted scoring and linguistic level categorization.

    Attributes:
        name: Pattern identifier (e.g., "our_or", "ise_ize")
        description: Human-readable description
        pattern_british: Compiled regex for British variant
        pattern_american: Compiled regex for American variant
        weight: Diagnostic value 0.0-1.0 (higher = more distinctive)
        feature_level: Linguistic level (phonological, morphological, etc.)
        exceptions: Words that match pattern but aren't dialect markers
    """

    name: str
    description: str
    pattern_british: re.Pattern | None
    pattern_american: re.Pattern | None
    weight: float
    feature_level: str
    exceptions: set[str] = field(default_factory=set)


@dataclass
class CompiledGrammarPattern:
    """Pre-compiled grammar pattern for efficient matching.

    Grammar patterns detect syntactic differences like "have got" vs "have",
    collective noun agreement, and shall/will usage.

    Attributes:
        name: Pattern identifier (e.g., "have_got", "gotten")
        description: Human-readable description
        pattern_british: Compiled regex for British variant (may be None)
        pattern_american: Compiled regex for American variant (may be None)
        weight: Diagnostic value 0.0-1.0
    """

    name: str
    description: str
    pattern_british: re.Pattern | None
    pattern_american: re.Pattern | None
    weight: float = 0.8


@dataclass
class DialectMarkers:
    """Container for all loaded and compiled dialect markers.

    This dataclass holds the complete dialect marker database after loading
    and preprocessing. It includes both raw data (for inspection) and
    pre-compiled patterns (for efficient detection).

    Related GitHub Issue:
        #35 - Dialect detection with extensible JSON markers
        https://github.com/craigtrim/pystylometry/issues/35

    Attributes:
        version: Data version from metadata
        vocabulary_pairs: List of American/British word pairs
        vocabulary_exclusive: Region-specific vocabulary by dialect
        spelling_patterns: Pre-compiled spelling patterns
        standalone_spellings: Direct British/American spelling pairs
        grammar_patterns: Pre-compiled grammar patterns
        eye_dialect_words: Set of eye dialect markers (gonna, wanna)
        pragmatic_markers: Discourse markers by dialect
        idiomatic_expressions: Idioms by dialect
        raw_data: Original JSON data for inspection
    """

    version: str
    vocabulary_pairs: list[dict[str, str]]
    vocabulary_exclusive: dict[str, list[str]]
    spelling_patterns: list[CompiledSpellingPattern]
    standalone_spellings: list[dict[str, str]]
    grammar_patterns: list[CompiledGrammarPattern]
    eye_dialect_words: set[str]
    pragmatic_markers: dict[str, Any]
    idiomatic_expressions: dict[str, list[dict[str, str]]]
    raw_data: dict[str, Any]

    # Pre-built lookup sets for fast matching
    british_vocabulary: set[str] = field(default_factory=set)
    american_vocabulary: set[str] = field(default_factory=set)
    british_spellings: set[str] = field(default_factory=set)
    american_spellings: set[str] = field(default_factory=set)


def _compile_spelling_pattern(pattern_data: dict[str, Any]) -> CompiledSpellingPattern:
    """Compile a single spelling pattern from JSON data.

    Args:
        pattern_data: Dictionary from spelling_patterns.british_american

    Returns:
        CompiledSpellingPattern with pre-compiled regexes
    """
    pattern_british = None
    pattern_american = None

    # Compile British pattern if present and not null
    british_pattern_str = pattern_data.get("pattern_british")
    if british_pattern_str is not None and isinstance(british_pattern_str, str):
        try:
            pattern_british = re.compile(british_pattern_str, re.IGNORECASE)
        except re.error:
            pass  # Skip invalid patterns

    # Compile American pattern if present and not null
    american_pattern_str = pattern_data.get("pattern_american")
    if american_pattern_str is not None and isinstance(american_pattern_str, str):
        try:
            pattern_american = re.compile(american_pattern_str, re.IGNORECASE)
        except re.error:
            pass

    # Extract exceptions as a set for fast lookup
    exceptions = set(pattern_data.get("exceptions", []))

    return CompiledSpellingPattern(
        name=pattern_data.get("name", "unknown"),
        description=pattern_data.get("description", ""),
        pattern_british=pattern_british,
        pattern_american=pattern_american,
        weight=pattern_data.get("weight", 0.8),
        feature_level=pattern_data.get("feature_level", "morphological"),
        exceptions=exceptions,
    )


def _compile_grammar_pattern(name: str, pattern_data: dict[str, Any]) -> CompiledGrammarPattern:
    """Compile a single grammar pattern from JSON data.

    Args:
        name: Pattern name (key from grammar_patterns)
        pattern_data: Dictionary with pattern details

    Returns:
        CompiledGrammarPattern with pre-compiled regexes
    """
    pattern_british = None
    pattern_american = None

    # Compile British pattern if present
    if "british_pattern" in pattern_data:
        try:
            pattern_british = re.compile(pattern_data["british_pattern"], re.IGNORECASE)
        except re.error:
            pass

    # Compile American pattern if present
    if "american_pattern" in pattern_data:
        try:
            pattern_american = re.compile(pattern_data["american_pattern"], re.IGNORECASE)
        except re.error:
            pass

    return CompiledGrammarPattern(
        name=name,
        description=pattern_data.get("description", ""),
        pattern_british=pattern_british,
        pattern_american=pattern_american,
        weight=pattern_data.get("weight", 0.8),
    )


def _build_vocabulary_sets(markers: DialectMarkers) -> None:
    """Build fast lookup sets from vocabulary pairs.

    Populates the british_vocabulary, american_vocabulary, british_spellings,
    and american_spellings sets for O(1) word lookup during detection.

    Args:
        markers: DialectMarkers to populate (modified in place)
    """
    # Build vocabulary sets from pairs
    for pair in markers.vocabulary_pairs:
        if "british" in pair:
            markers.british_vocabulary.add(pair["british"].lower())
        if "american" in pair:
            markers.american_vocabulary.add(pair["american"].lower())

    # Add exclusive vocabulary
    for word in markers.vocabulary_exclusive.get("british", []):
        markers.british_vocabulary.add(word.lower())
    for word in markers.vocabulary_exclusive.get("american", []):
        markers.american_vocabulary.add(word.lower())

    # Build spelling sets from standalone spellings
    for pair in markers.standalone_spellings:
        if "british" in pair:
            markers.british_spellings.add(pair["british"].lower())
        if "american" in pair:
            markers.american_spellings.add(pair["american"].lower())


@lru_cache(maxsize=1)
def load_dialect_markers() -> DialectMarkers:
    """Load and compile dialect markers from JSON file.

    This function is cached with lru_cache to ensure the JSON file is loaded
    only once per Python session. The cache has maxsize=1 since there's only
    one dialect markers file.

    Related GitHub Issue:
        #35 - Dialect detection with extensible JSON markers
        https://github.com/craigtrim/pystylometry/issues/35

    Returns:
        DialectMarkers with all data loaded and patterns compiled

    Raises:
        FileNotFoundError: If dialect_markers.json doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    with open(_MARKERS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Extract metadata
    metadata = data.get("metadata", {})
    version = metadata.get("version", "unknown")

    # Extract vocabulary
    vocabulary = data.get("vocabulary", {})
    vocabulary_pairs = vocabulary.get("pairs", [])
    vocabulary_exclusive = vocabulary.get("exclusive", {})

    # Compile spelling patterns
    spelling_data = data.get("spelling_patterns", {})
    compiled_spelling = [
        _compile_spelling_pattern(p) for p in spelling_data.get("british_american", [])
    ]
    standalone_spellings = spelling_data.get("standalone", [])

    # Compile grammar patterns
    grammar_data = data.get("grammar_patterns", {})
    compiled_grammar = [
        _compile_grammar_pattern(name, pdata) for name, pdata in grammar_data.items()
    ]

    # Extract eye dialect words
    eye_dialect_data = data.get("eye_dialect", {})
    eye_dialect_words = set()
    for word in eye_dialect_data.get("informal_contractions", []):
        eye_dialect_words.add(word.lower())
    for word in eye_dialect_data.get("phonetic_spellings", []):
        eye_dialect_words.add(word.lower())

    # Extract pragmatic markers
    pragmatic_markers = data.get("pragmatic_markers", {})

    # Extract idiomatic expressions
    idiomatic = data.get("idiomatic_expressions", {})

    # Build the markers container
    markers = DialectMarkers(
        version=version,
        vocabulary_pairs=vocabulary_pairs,
        vocabulary_exclusive=vocabulary_exclusive,
        spelling_patterns=compiled_spelling,
        standalone_spellings=standalone_spellings,
        grammar_patterns=compiled_grammar,
        eye_dialect_words=eye_dialect_words,
        pragmatic_markers=pragmatic_markers,
        idiomatic_expressions=idiomatic,
        raw_data=data,
    )

    # Build lookup sets for fast matching
    _build_vocabulary_sets(markers)

    return markers


def get_markers() -> DialectMarkers:
    """Get the cached dialect markers.

    This is the primary entry point for accessing dialect markers. It returns
    the cached markers from load_dialect_markers(), ensuring efficient access.

    Example:
        >>> markers = get_markers()
        >>> len(markers.vocabulary_pairs)
        165
        >>> "colour" in markers.british_spellings
        True

    Returns:
        DialectMarkers with all data loaded and patterns compiled
    """
    return load_dialect_markers()


def clear_cache() -> None:
    """Clear the dialect markers cache.

    This forces a reload of the JSON file on the next get_markers() call.
    Useful for testing or when the JSON file has been modified.
    """
    load_dialect_markers.cache_clear()

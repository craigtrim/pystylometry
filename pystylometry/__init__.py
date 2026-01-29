"""
pystylometry - Comprehensive Python package for stylometric analysis.

A modular package for text analysis with lexical, readability, syntactic,
authorship, n-gram, dialect detection, and consistency analysis metrics.

Installation:
    pip install pystylometry                    # Core (lexical only)
    pip install pystylometry[readability]       # With readability metrics
    pip install pystylometry[syntactic]         # With syntactic analysis
    pip install pystylometry[authorship]        # With authorship attribution
    pip install pystylometry[all]               # Everything

Usage:
    # Direct module imports
    from pystylometry.lexical import compute_mtld, compute_yule
    from pystylometry.readability import compute_flesch
    from pystylometry.syntactic import compute_pos_ratios
    from pystylometry.authorship import compute_burrows_delta, compute_kilgarriff
    from pystylometry.consistency import compute_kilgarriff_drift
    from pystylometry.dialect import compute_dialect

    # Or use the unified analyze() function
    from pystylometry import analyze

    results = analyze(text, lexical=True, readability=True)
    print(results.lexical['mtld'].mtld_average)
    print(results.readability['flesch'].reading_ease)

    # Dialect detection
    result = compute_dialect("The colour of the programme was brilliant.")
    print(result.dialect)  # 'british'
    print(result.british_score)  # 0.85

    # Consistency analysis (Style Drift Detector - Issue #36)
    from pystylometry.consistency import compute_kilgarriff_drift

    result = compute_kilgarriff_drift(long_document)
    print(result.pattern)  # 'consistent', 'sudden_spike', 'suspiciously_uniform', etc.
    print(result.pattern_confidence)
"""

from . import lexical  # noqa: E402
from ._types import AnalysisResult
from .tokenizer import TokenizationStats, Tokenizer, TokenMetadata

# Version
__version__ = "0.1.0"

# Optional exports - may raise ImportError if dependencies not installed
try:
    from . import readability  # noqa: F401

    _READABILITY_AVAILABLE = True
except ImportError:
    _READABILITY_AVAILABLE = False

try:
    from . import syntactic  # noqa: F401

    _SYNTACTIC_AVAILABLE = True
except ImportError:
    _SYNTACTIC_AVAILABLE = False

# Prosody requires pronouncing (CMU dictionary) - same dependency as readability
try:
    from . import prosody  # noqa: F401 - Rhythm and prosody metrics (Issue #25)

    _PROSODY_AVAILABLE = True
except ImportError:
    _PROSODY_AVAILABLE = False

# Authorship, ngrams, dialect, consistency, and stylistic use only stdlib (no external dependencies)
from . import (
    authorship,  # noqa: F401
    consistency,  # noqa: F401 - Style drift detection (Issue #36)
    dialect,  # noqa: F401
    ngrams,  # noqa: F401
    stylistic,  # noqa: F401 - Vocabulary overlap and similarity (Issue #21)
)

_AUTHORSHIP_AVAILABLE = True
_NGRAMS_AVAILABLE = True
_DIALECT_AVAILABLE = True
_CONSISTENCY_AVAILABLE = True
_STYLISTIC_AVAILABLE = True


def tokenize(text: str, **kwargs: object) -> list[str]:
    """Tokenize text using the stylometric tokenizer.

    Convenience wrapper around Tokenizer.tokenize(). All keyword arguments
    are forwarded to the Tokenizer constructor.

    Args:
        text: Input text to tokenize.
        **kwargs: Options forwarded to Tokenizer (lowercase, strip_numbers,
            expand_contractions, etc.).

    Returns:
        List of token strings.

    Example:
        >>> from pystylometry import tokenize
        >>> tokenize("Hello, world! It's a test.")
        ['hello', 'world', "it's", 'a', 'test']
    """
    return Tokenizer(**kwargs).tokenize(text)  # type: ignore[arg-type]


def tokenize_with_metadata(text: str, **kwargs: object) -> list[TokenMetadata]:
    """Tokenize text and return tokens with positional and type metadata.

    Args:
        text: Input text to tokenize.
        **kwargs: Options forwarded to Tokenizer.

    Returns:
        List of TokenMetadata objects.
    """
    return Tokenizer(**kwargs).tokenize_with_metadata(text)  # type: ignore[arg-type]


def analyze(
    text: str,
    lexical_metrics: bool = True,
    readability_metrics: bool = False,
    syntactic_metrics: bool = False,
    authorship_metrics: bool = False,
    ngram_metrics: bool = False,
) -> AnalysisResult:
    """
    Unified interface to compute multiple stylometric metrics at once.

    This is a convenience function that calls all requested metric computations
    and returns a unified result object. Only computes metrics for which the
    required optional dependencies are installed.

    Args:
        text: Input text to analyze
        lexical_metrics: Compute lexical diversity metrics (default: True)
        readability_metrics: Compute readability metrics (default: False)
        syntactic_metrics: Compute syntactic metrics (default: False)
        authorship_metrics: Compute authorship metrics (default: False)
            Note: Authorship metrics typically require multiple texts for comparison.
            This will compute features that can be used for authorship analysis.
        ngram_metrics: Compute n-gram entropy metrics (default: False)

    Returns:
        AnalysisResult with requested metrics in nested dictionaries

    Raises:
        ImportError: If requested analysis requires uninstalled dependencies

    Example:
        >>> from pystylometry import analyze
        >>> results = analyze(text, lexical=True, readability=True)
        >>> print(results.lexical['mtld'].mtld_average)
        >>> print(results.readability['flesch'].reading_ease)

    Example with all metrics:
        >>> results = analyze(text, lexical=True, readability=True,
        ...                   syntactic=True, ngrams=True)
        >>> print(f"MTLD: {results.lexical['mtld'].mtld_average:.2f}")
        >>> print(f"Flesch: {results.readability['flesch'].reading_ease:.1f}")
        >>> print(f"Noun ratio: {results.syntactic['pos'].noun_ratio:.3f}")
        >>> print(f"Bigram entropy: {results.ngrams['word_bigram'].entropy:.3f}")
    """
    result = AnalysisResult(metadata={"text_length": len(text)})

    # Lexical metrics (always available)
    if lexical_metrics:
        result.lexical = {}
        result.lexical["ttr"] = lexical.compute_ttr(text)
        result.lexical["mtld"] = lexical.compute_mtld(text)
        result.lexical["yule"] = lexical.compute_yule(text)
        result.lexical["hapax"] = lexical.compute_hapax_ratios(text)

    # Readability metrics (optional dependency)
    if readability_metrics:
        if not _READABILITY_AVAILABLE:
            raise ImportError(
                "Readability metrics require optional dependencies. "
                "Install with: pip install pystylometry[readability]"
            )
        # Import locally to avoid name conflict
        from . import readability as readability_module

        result.readability = {}
        result.readability["flesch"] = readability_module.compute_flesch(text)
        result.readability["smog"] = readability_module.compute_smog(text)
        result.readability["gunning_fog"] = readability_module.compute_gunning_fog(text)
        result.readability["coleman_liau"] = readability_module.compute_coleman_liau(text)
        result.readability["ari"] = readability_module.compute_ari(text)

    # Syntactic metrics (optional dependency)
    if syntactic_metrics:
        if not _SYNTACTIC_AVAILABLE:
            raise ImportError(
                "Syntactic metrics require optional dependencies. "
                "Install with: pip install pystylometry[syntactic]"
            )
        # Import locally to avoid name conflict
        from . import syntactic as syntactic_module

        result.syntactic = {}
        result.syntactic["pos"] = syntactic_module.compute_pos_ratios(text)
        result.syntactic["sentence_stats"] = syntactic_module.compute_sentence_stats(text)

    # Authorship metrics (uses stdlib only)
    # Note: These are typically used for comparison between texts
    # Here we just note that they're available but don't compute them
    # since they require multiple texts as input
    if authorship_metrics:
        result.authorship = {
            "note": "Authorship metrics require multiple texts for comparison. "
            "Use pystylometry.authorship.compute_burrows_delta(text1, text2) directly."
        }

    # N-gram metrics (uses stdlib only)
    if ngram_metrics:
        result.ngrams = {}
        result.ngrams["character_bigram"] = ngrams.compute_character_bigram_entropy(text)
        result.ngrams["word_bigram"] = ngrams.compute_word_bigram_entropy(text)

    return result


# Convenient access to availability flags
def get_available_modules() -> dict[str, bool]:
    """
    Get dictionary of available optional modules.

    Returns:
        Dictionary mapping module names to availability status

    Example:
        >>> from pystylometry import get_available_modules
        >>> available = get_available_modules()
        >>> if available['readability']:
        ...     from pystylometry.readability import compute_flesch
        >>> if available['consistency']:
        ...     from pystylometry.consistency import compute_kilgarriff_drift
    """
    return {
        "lexical": True,  # Always available
        "readability": _READABILITY_AVAILABLE,
        "syntactic": _SYNTACTIC_AVAILABLE,
        "authorship": _AUTHORSHIP_AVAILABLE,
        "ngrams": _NGRAMS_AVAILABLE,
        "dialect": _DIALECT_AVAILABLE,
        "consistency": _CONSISTENCY_AVAILABLE,  # Style drift detection (Issue #36)
        "stylistic": _STYLISTIC_AVAILABLE,  # Vocabulary overlap (Issue #21)
        "prosody": _PROSODY_AVAILABLE,  # Rhythm and prosody (Issue #25)
    }


__all__ = [
    "__version__",
    "analyze",
    "get_available_modules",
    "tokenize",
    "tokenize_with_metadata",
    "Tokenizer",
    "TokenMetadata",
    "TokenizationStats",
    "lexical",
]

# Conditionally add to __all__ based on availability
if _READABILITY_AVAILABLE:
    __all__.append("readability")
if _SYNTACTIC_AVAILABLE:
    __all__.append("syntactic")
if _AUTHORSHIP_AVAILABLE:
    __all__.append("authorship")
if _NGRAMS_AVAILABLE:
    __all__.append("ngrams")
if _DIALECT_AVAILABLE:
    __all__.append("dialect")
if _CONSISTENCY_AVAILABLE:
    __all__.append("consistency")
if _STYLISTIC_AVAILABLE:
    __all__.append("stylistic")
if _PROSODY_AVAILABLE:
    __all__.append("prosody")

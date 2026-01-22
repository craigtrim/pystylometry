"""
pystylometry - Comprehensive Python package for stylometric analysis.

A modular package for text analysis with lexical, readability, syntactic,
authorship, and n-gram metrics.

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
    from pystylometry.authorship import compute_burrows_delta

    # Or use the unified analyze() function
    from pystylometry import analyze

    results = analyze(text, lexical=True, readability=True)
    print(results.lexical['mtld'].mtld_average)
    print(results.readability['flesch'].reading_ease)
"""

from typing import Optional
from ._types import AnalysisResult

# Version
__version__ = "0.1.0"

# Core exports - always available
from . import lexical

# Optional exports - may raise ImportError if dependencies not installed
try:
    from . import readability
    _READABILITY_AVAILABLE = True
except ImportError:
    _READABILITY_AVAILABLE = False

try:
    from . import syntactic
    _SYNTACTIC_AVAILABLE = True
except ImportError:
    _SYNTACTIC_AVAILABLE = False

# Authorship and ngrams use only stdlib (no external dependencies)
from . import authorship
from . import ngrams
_AUTHORSHIP_AVAILABLE = True
_NGRAMS_AVAILABLE = True


def analyze(
    text: str,
    lexical: bool = True,
    readability: bool = False,
    syntactic: bool = False,
    authorship: bool = False,
    ngrams: bool = False,
) -> AnalysisResult:
    """
    Unified interface to compute multiple stylometric metrics at once.

    This is a convenience function that calls all requested metric computations
    and returns a unified result object. Only computes metrics for which the
    required optional dependencies are installed.

    Args:
        text: Input text to analyze
        lexical: Compute lexical diversity metrics (default: True)
        readability: Compute readability metrics (default: False)
        syntactic: Compute syntactic metrics (default: False)
        authorship: Compute authorship metrics (default: False)
            Note: Authorship metrics typically require multiple texts for comparison.
            This will compute features that can be used for authorship analysis.
        ngrams: Compute n-gram entropy metrics (default: False)

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
    if lexical:
        result.lexical = {}
        # TODO: Add when stylometry-ttr is integrated
        # result.lexical['ttr'] = lexical.compute_ttr(text)
        result.lexical['mtld'] = lexical.compute_mtld(text)
        result.lexical['yule'] = lexical.compute_yule(text)
        result.lexical['hapax'] = lexical.compute_hapax_ratios(text)

    # Readability metrics (optional dependency)
    if readability:
        if not _READABILITY_AVAILABLE:
            raise ImportError(
                "Readability metrics require optional dependencies. "
                "Install with: pip install pystylometry[readability]"
            )
        result.readability = {}
        result.readability['flesch'] = readability.compute_flesch(text)
        result.readability['smog'] = readability.compute_smog(text)
        result.readability['gunning_fog'] = readability.compute_gunning_fog(text)
        result.readability['coleman_liau'] = readability.compute_coleman_liau(text)
        result.readability['ari'] = readability.compute_ari(text)

    # Syntactic metrics (optional dependency)
    if syntactic:
        if not _SYNTACTIC_AVAILABLE:
            raise ImportError(
                "Syntactic metrics require optional dependencies. "
                "Install with: pip install pystylometry[syntactic]"
            )
        result.syntactic = {}
        result.syntactic['pos'] = syntactic.compute_pos_ratios(text)
        result.syntactic['sentence_stats'] = syntactic.compute_sentence_stats(text)

    # Authorship metrics (uses stdlib only)
    # Note: These are typically used for comparison between texts
    # Here we just note that they're available but don't compute them
    # since they require multiple texts as input
    if authorship:
        result.authorship = {
            "note": "Authorship metrics require multiple texts for comparison. "
                    "Use pystylometry.authorship.compute_burrows_delta(text1, text2) directly."
        }

    # N-gram metrics (uses stdlib only)
    if ngrams:
        result.ngrams = {}
        result.ngrams['character_bigram'] = ngrams.compute_character_bigram_entropy(text)
        result.ngrams['word_bigram'] = ngrams.compute_word_bigram_entropy(text)

    return result


# Convenient access to availability flags
def get_available_modules():
    """
    Get dictionary of available optional modules.

    Returns:
        Dictionary mapping module names to availability status

    Example:
        >>> from pystylometry import get_available_modules
        >>> available = get_available_modules()
        >>> if available['readability']:
        ...     from pystylometry.readability import compute_flesch
    """
    return {
        "lexical": True,  # Always available
        "readability": _READABILITY_AVAILABLE,
        "syntactic": _SYNTACTIC_AVAILABLE,
        "authorship": _AUTHORSHIP_AVAILABLE,
        "ngrams": _NGRAMS_AVAILABLE,
    }


__all__ = [
    "__version__",
    "analyze",
    "get_available_modules",
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

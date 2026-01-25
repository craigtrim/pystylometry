"""Consistency analysis module for pystylometry.

This module provides tools for analyzing internal stylistic consistency within
a single document. Unlike the `authorship` module (which compares different texts),
the `consistency` module focuses on detecting patterns within one text:

- Stylistic drift over the course of a document
- Sudden discontinuities suggesting pasted content or different authors
- Suspiciously uniform style (potential AI generation signature)
- Natural variation patterns in human writing

Related GitHub Issues:
    #36 - Kilgarriff Chi-Squared drift detection for intra-document analysis
    https://github.com/craigtrim/pystylometry/issues/36
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27

Marketing Names:
    - "Style Drift Detector"
    - "Consistency Fingerprint"
    - "Authorship Continuity Score"

Available Functions:
    compute_kilgarriff_drift: Detect stylistic drift using chi-squared method

Example Usage:
    >>> from pystylometry.consistency import compute_kilgarriff_drift
    >>>
    >>> # Analyze a document for stylistic consistency
    >>> result = compute_kilgarriff_drift(document_text)
    >>>
    >>> # Check the detected pattern
    >>> print(f"Pattern: {result.pattern}")  # e.g., "consistent", "sudden_spike"
    >>> print(f"Confidence: {result.pattern_confidence:.2f}")
    >>>
    >>> # Investigate potential AI generation
    >>> if result.pattern == "suspiciously_uniform":
    ...     print("Warning: Text shows unusually uniform style")
    >>>
    >>> # Find where the biggest style shift occurs
    >>> if result.pattern == "sudden_spike":
    ...     print(f"Major discontinuity at window boundary {result.max_location}")

References:
    Kilgarriff, Adam. "Comparing Corpora." International Journal of Corpus
        Linguistics, vol. 6, no. 1, 2001, pp. 97-133.

    Eder, Maciej. "Does Size Matter? Authorship Attribution, Small Samples,
        Big Problem." Digital Scholarship in the Humanities, vol. 30, no. 2,
        2015, pp. 167-182.
"""

from .drift import compute_kilgarriff_drift

__all__ = [
    "compute_kilgarriff_drift",
]

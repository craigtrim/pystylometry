"""Dialect detection module for stylometric analysis.

This module provides dialect detection capabilities, identifying regional
linguistic preferences (British vs. American English) and measuring text
markedness - how far the text deviates from "unmarked" standard English.

Related GitHub Issues:
    #35 - Dialect detection with extensible JSON markers
    https://github.com/craigtrim/pystylometry/issues/35
    #30 - Whonix stylometry features (regional linguistic preferences)
    https://github.com/craigtrim/pystylometry/issues/30
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27

Features:
    - British/American vocabulary matching (flat/apartment, lorry/truck)
    - Spelling pattern detection (-ise/-ize, -our/-or, -re/-er)
    - Grammar pattern analysis (have got/have, collective noun agreement)
    - Eye dialect identification (gonna, wanna - register, not dialect)
    - Feature weighting based on linguistic research
    - Markedness scoring for stylistic analysis
    - Native chunked analysis with distribution statistics

The analysis uses an extensible JSON database (dialect_markers.json) that
can be augmented with additional markers over time.

Usage:
    >>> from pystylometry.dialect import compute_dialect
    >>> result = compute_dialect("The colour of the programme was brilliant.")
    >>> result.dialect
    'british'
    >>> result.british_score
    0.85
    >>> result.markedness_score
    0.42

    >>> # Access distributions for stylometric fingerprinting
    >>> result.british_score_dist.std  # Variance across chunks
    0.05

    >>> # Inspect detailed marker breakdown
    >>> result.spelling_markers
    {'colour': 1, 'programme': 1}
    >>> result.markers_by_level['phonological']
    {'colour': 1}

References:
    Goebl, Hans. "Dialektometrie: Prinzipien und Methoden des Einsatzes der
        numerischen Taxonomie im Bereich der Dialektgeographie." Verlag der
        Österreichischen Akademie der Wissenschaften, 1982.
    Nerbonne, John. "Data-Driven Dialectology." Language and Linguistics
        Compass, vol. 3, no. 1, 2009, pp. 175-198.
    Whonix Project. "Stylometry: Deanonymization Techniques." Whonix Wiki,
        https://www.whonix.org/wiki/Stylometry
"""

from ._loader import DialectMarkers, clear_cache, get_markers
from .detector import compute_dialect

__all__ = [
    "compute_dialect",
    "get_markers",
    "clear_cache",
    "DialectMarkers",
]

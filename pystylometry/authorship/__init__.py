"""Authorship attribution metrics.

This module provides methods for authorship attribution - comparing texts to
determine whether they were written by the same author. Available methods
include classic approaches (Burrows' Delta, Zeta), statistical methods
(Kilgarriff's chi-squared), and information-theoretic methods (NCD).

Related GitHub Issues:
    #24 - Additional Authorship Attribution Methods
    https://github.com/craigtrim/pystylometry/issues/24
    #31 - Classical Stylometric Methods from Programming Historian
    https://github.com/craigtrim/pystylometry/issues/31

Available Functions:
    compute_burrows_delta: Classic Delta method for authorship distance
    compute_cosine_delta: Angular distance variant of Delta
    compute_zeta: Zeta method for marker word detection
    compute_kilgarriff: Chi-squared method for corpus comparison
    compute_minmax: Burrows' original min-max distance method
    compute_johns_delta: Delta variations (quadratic, weighted)
    compute_compression_distance: Normalized Compression Distance (NCD)
"""

from .additional_methods import compute_johns_delta, compute_minmax
from .burrows_delta import compute_burrows_delta, compute_cosine_delta
from .compression import compute_compression_distance
from .kilgarriff import compute_kilgarriff
from .zeta import compute_zeta

__all__ = [
    "compute_burrows_delta",
    "compute_compression_distance",
    "compute_cosine_delta",
    "compute_johns_delta",
    "compute_kilgarriff",
    "compute_minmax",
    "compute_zeta",
]

"""Character-level metrics for stylometric analysis.

This package provides character-level features for authorship attribution
and style analysis.

Related GitHub Issue:
    #12 - Character-Level Metrics
    https://github.com/craigtrim/pystylometry/issues/12
"""

from .character_metrics import compute_character_metrics

__all__ = [
    "compute_character_metrics",
]

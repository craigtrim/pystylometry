"""Rhythm and prosody metrics for written text.

Related GitHub Issue:
    #25 - Rhythm and Prosody Metrics
    https://github.com/craigtrim/pystylometry/issues/25
"""

from .rhythm_prosody import compute_rhythm_prosody

__all__ = [
    "compute_rhythm_prosody",
]

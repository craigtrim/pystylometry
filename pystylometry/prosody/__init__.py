"""Rhythm and prosody metrics for written text.

Related GitHub Issues:
    #25 - Rhythm and Prosody Metrics
    https://github.com/craigtrim/pystylometry/issues/25
    #66 - Sentence-level syllable analysis
    https://github.com/craigtrim/pystylometry/issues/66
    #67 - Syllable pattern repetition analysis
    https://github.com/craigtrim/pystylometry/issues/67
"""

from .rhythm_prosody import compute_rhythm_prosody
from .sentence_syllable_patterns import compute_sentence_syllable_patterns
from .syllable_pattern_repetition import analyze_syllable_pattern_repetition

__all__ = [
    "compute_rhythm_prosody",
    "compute_sentence_syllable_patterns",
    "analyze_syllable_pattern_repetition",
]

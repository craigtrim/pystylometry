"""Syntactic analysis metrics (requires spaCy)."""

from .pos_ratios import compute_pos_ratios
from .sentence_stats import compute_sentence_stats

__all__ = [
    "compute_pos_ratios",
    "compute_sentence_stats",
]

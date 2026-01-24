"""Syntactic analysis metrics (requires spaCy)."""

from .advanced_syntactic import compute_advanced_syntactic
from .pos_ratios import compute_pos_ratios
from .sentence_stats import compute_sentence_stats
from .sentence_types import compute_sentence_types

__all__ = [
    "compute_pos_ratios",
    "compute_sentence_stats",
    "compute_advanced_syntactic",
    "compute_sentence_types",
]

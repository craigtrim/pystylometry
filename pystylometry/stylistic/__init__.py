"""Stylistic analysis metrics.

Related GitHub Issues:
    #20 - Stylistic Markers
    #21 - Vocabulary Overlap and Similarity Metrics
    #22 - Cohesion and Coherence Metrics
    #23 - Genre and Register Features
"""

from .cohesion_coherence import compute_cohesion_coherence
from .genre_register import compute_genre_register
from .markers import compute_stylistic_markers
from .vocabulary_overlap import compute_vocabulary_overlap

__all__ = [
    "compute_stylistic_markers",
    "compute_vocabulary_overlap",
    "compute_cohesion_coherence",
    "compute_genre_register",
]

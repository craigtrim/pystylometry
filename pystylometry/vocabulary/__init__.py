"""Vocabulary analysis metrics for stylometric fingerprinting.

This subpackage analyzes vocabulary choice patterns — specifically synonym
diversity and semantic clustering — to capture authorial preferences in
word selection. Authors develop habitual preferences for specific words
over their synonyms (e.g., always choosing "start" over "begin"), creating
reliable stylometric signatures.

Related GitHub Issues:
    #30 - Whonix stylometric features
    https://github.com/craigtrim/pystylometry/issues/30

Whonix Source:
    The Whonix Stylometry documentation identifies "synonym choice" as a
    deanonymization vector.
    https://www.whonix.org/wiki/Stylometry

Modules:
    synonym_diversity: Semantic cluster diversity and synonym choice analysis
"""

from .synonym_diversity import compute_synonym_diversity

__all__ = [
    "compute_synonym_diversity",
]

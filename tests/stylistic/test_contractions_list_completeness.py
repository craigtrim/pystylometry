"""Comprehensive tests for stylistic markers module.

This module tests the stylistic markers functionality, including contraction
detection, intensifier analysis, hedge detection, modal auxiliary classification,
negation patterns, and punctuation style analysis.

Related GitHub Issues:
    #20 - Stylistic Markers
    https://github.com/craigtrim/pystylometry/issues/20

Test coverage:
    - Basic functionality and return type validation
    - Contraction detection and ratio calculation
    - Intensifier detection and density calculation
    - Hedge detection and density calculation
    - Modal auxiliary analysis (epistemic vs deontic)
    - Negation pattern detection
    - Punctuation style analysis (8 types)
    - Edge cases (empty text, no markers, short text)
    - Density normalization (per 100 words)
"""

from pystylometry.stylistic.markers import (
    CONTRACTIONS,
)


class TestContractionsListCompleteness:
    """Test that the contractions list is comprehensive."""

    def test_all_negative_contractions_present(self) -> None:
        """Test that all common negative contractions are in the list."""
        negative_contractions = [
            "aren't",
            "can't",
            "couldn't",
            "didn't",
            "doesn't",
            "don't",
            "hadn't",
            "hasn't",
            "haven't",
            "isn't",
            "mightn't",
            "mustn't",
            "needn't",
            "shouldn't",
            "wasn't",
            "weren't",
            "won't",
            "wouldn't",
        ]
        for contraction in negative_contractions:
            assert contraction in CONTRACTIONS

    def test_all_pronoun_contractions_present(self) -> None:
        """Test that all common pronoun contractions are in the list."""
        pronoun_contractions = [
            "i'm",
            "i've",
            "i'll",
            "i'd",
            "you're",
            "you've",
            "you'll",
            "you'd",
            "he's",
            "he'll",
            "he'd",
            "she's",
            "she'll",
            "she'd",
            "it's",
            "it'll",
            "it'd",
            "we're",
            "we've",
            "we'll",
            "we'd",
            "they're",
            "they've",
            "they'll",
            "they'd",
        ]
        for contraction in pronoun_contractions:
            assert contraction in CONTRACTIONS

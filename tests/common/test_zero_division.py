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

import math

from pystylometry.stylistic.markers import (
    compute_stylistic_markers,
)


class TestZeroDivision:
    """Test handling of potential zero division scenarios."""

    def test_no_modals_epistemic_ratio(self) -> None:
        """Test epistemic ratio when no modals present."""
        text = "The cat sat on the mat."
        result = compute_stylistic_markers(text)

        # Should be 0.0, not NaN or error
        assert result.epistemic_modal_ratio == 0.0
        assert result.deontic_modal_ratio == 0.0

    def test_no_contractable_forms(self) -> None:
        """Test contraction ratio when no contractable forms present."""
        text = "The sun shone brightly."
        result = compute_stylistic_markers(text)

        # Should be 0.0, not NaN or error
        assert result.contraction_ratio == 0.0

    def test_empty_result_no_nan(self) -> None:
        """Test that empty text doesn't produce NaN values."""
        result = compute_stylistic_markers("")

        # Check no NaN values
        assert not math.isnan(result.contraction_ratio)
        assert not math.isnan(result.intensifier_density)
        assert not math.isnan(result.hedging_density)
        assert not math.isnan(result.modal_density)
        assert not math.isnan(result.epistemic_modal_ratio)
        assert not math.isnan(result.deontic_modal_ratio)
        assert not math.isnan(result.negation_density)

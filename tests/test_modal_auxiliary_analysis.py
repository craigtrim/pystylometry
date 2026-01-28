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
    ALL_MODALS,
    DEONTIC_MODALS,
    EPISTEMIC_MODALS,
    compute_stylistic_markers,
)


class TestModalAuxiliaryAnalysis:
    """Test modal auxiliary detection and classification."""

    def test_modal_detection(self) -> None:
        """Test detection of modal auxiliaries."""
        text = "I can do it. You should try. We must go. They might help."
        result = compute_stylistic_markers(text)

        assert result.modal_density > 0
        assert len(result.modal_distribution) > 0

    def test_modal_distribution(self) -> None:
        """Test that modal distribution is correctly computed."""
        text = "can can could could could may"
        result = compute_stylistic_markers(text)

        assert result.modal_distribution.get("can", 0) == 2
        assert result.modal_distribution.get("could", 0) == 3
        assert result.modal_distribution.get("may", 0) == 1

    def test_epistemic_modal_ratio(self) -> None:
        """Test epistemic modal ratio calculation."""
        # Use only epistemic modals
        text = "I can do it. You could try. We may go. They might help."
        result = compute_stylistic_markers(text)

        # All modals are epistemic
        assert result.epistemic_modal_ratio > 0.5

    def test_deontic_modal_ratio(self) -> None:
        """Test deontic modal ratio calculation."""
        # Use only deontic modals
        text = "You must go. We shall try. They will help."
        result = compute_stylistic_markers(text)

        # Should have high deontic ratio
        assert result.deontic_modal_ratio > 0

    def test_modal_ratio_sum(self) -> None:
        """Test that epistemic and deontic ratios are reasonable."""
        text = "I can go and you must try. She could help but they will refuse."
        result = compute_stylistic_markers(text)

        # Note: Some modals can be both epistemic and deontic (e.g., "should")
        # So sum might exceed 1.0, but each ratio should be <= 1.0
        assert result.epistemic_modal_ratio <= 1.0
        assert result.deontic_modal_ratio <= 1.0

    def test_modal_list_completeness(self) -> None:
        """Test that the modal list is comprehensive."""
        common_modals = ["can", "could", "may", "might", "must", "shall", "should", "will", "would"]
        for modal in common_modals:
            assert modal in ALL_MODALS

    def test_epistemic_modal_list(self) -> None:
        """Test epistemic modal classification."""
        epistemic = ["may", "might", "could", "can", "would", "should"]
        for modal in epistemic:
            assert modal in EPISTEMIC_MODALS

    def test_deontic_modal_list(self) -> None:
        """Test deontic modal classification."""
        deontic = ["must", "shall", "will", "should"]
        for modal in deontic:
            assert modal in DEONTIC_MODALS

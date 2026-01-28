"""Tests for additional authorship attribution methods.

Tests cover:
    - compute_minmax: Min-Max distance (Burrows 1992)
    - compute_johns_delta: John Burrows' Delta variations (quadratic, weighted)
    - compute_compression_distance: Normalized Compression Distance (NCD)

Uses real literary fixtures from tests/fixtures/ for meaningful authorship
discrimination tests.

Related GitHub Issue:
    #24 - Additional Authorship Attribution Methods
    https://github.com/craigtrim/pystylometry/issues/24
"""

from pathlib import Path

import pytest

from pystylometry._types import (
    MinMaxResult,
)
from pystylometry.authorship import (
    compute_minmax,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ===== Shared Test Fixtures =====


# ===== compute_minmax Tests =====


@pytest.fixture(scope="module")
def dickens() -> str:
    """Single-author Dickens text from Kilgarriff fixtures."""
    return (FIXTURES_DIR / "kilgarriff" / "02-single-author-dickens.txt").read_text()


@pytest.fixture(scope="module")
def doyle_hound() -> str:
    """Full text of Doyle's Hound of the Baskervilles."""
    return (FIXTURES_DIR / "doyle-the-hound-of-the-baskervilles.txt").read_text()


@pytest.fixture(scope="module")
def doyle_sign() -> str:
    """Full text of Doyle's The Sign of the Four."""
    return (FIXTURES_DIR / "doyle-the-sign-of-the-four.txt").read_text()


class TestComputeMinmax:
    """Tests for the Min-Max distance method."""

    def test_returns_minmax_result(self, doyle_hound: str, dickens: str) -> None:
        """compute_minmax returns a MinMaxResult dataclass."""
        result = compute_minmax(doyle_hound, dickens)
        assert isinstance(result, MinMaxResult)

    def test_identical_texts_zero_distance(self, doyle_hound: str) -> None:
        """Identical texts should have zero MinMax distance."""
        result = compute_minmax(doyle_hound, doyle_hound)
        assert result.minmax_distance == 0.0

    def test_same_author_lower_distance(
        self, doyle_hound: str, doyle_sign: str, dickens: str
    ) -> None:
        """Same-author texts (two Doyle novels) should have lower distance
        than different-author texts (Doyle vs Dickens)."""
        same_author = compute_minmax(doyle_hound, doyle_sign)
        diff_author = compute_minmax(doyle_hound, dickens)
        assert same_author.minmax_distance < diff_author.minmax_distance

    def test_distance_range(self, doyle_hound: str, dickens: str) -> None:
        """MinMax distance should be between 0 and 1."""
        result = compute_minmax(doyle_hound, dickens)
        assert 0.0 <= result.minmax_distance <= 1.0

    def test_symmetry(self, doyle_hound: str, dickens: str) -> None:
        """MinMax distance should be symmetric: d(A,B) == d(B,A)."""
        result_ab = compute_minmax(doyle_hound, dickens)
        result_ba = compute_minmax(dickens, doyle_hound)
        assert abs(result_ab.minmax_distance - result_ba.minmax_distance) < 1e-10

    def test_feature_count(self, doyle_hound: str, dickens: str) -> None:
        """Feature count should match or be less than mfw parameter."""
        result = compute_minmax(doyle_hound, dickens, mfw=50)
        assert result.feature_count == 50

    def test_most_distinctive_features(self, doyle_hound: str, dickens: str) -> None:
        """Most distinctive features should be a list of (word, score) tuples."""
        result = compute_minmax(doyle_hound, dickens)
        assert len(result.most_distinctive_features) > 0
        for word, score in result.most_distinctive_features:
            assert isinstance(word, str)
            assert isinstance(score, float)
            assert score >= 0.0

    def test_distinctive_features_sorted_descending(self, doyle_hound: str, dickens: str) -> None:
        """Distinctive features should be sorted by contribution (descending)."""
        result = compute_minmax(doyle_hound, dickens)
        scores = [score for _, score in result.most_distinctive_features]
        assert scores == sorted(scores, reverse=True)

    def test_metadata_fields(self, doyle_hound: str, dickens: str) -> None:
        """Metadata should contain expected fields."""
        result = compute_minmax(doyle_hound, dickens)
        assert "text1_size" in result.metadata
        assert "text2_size" in result.metadata
        assert "text1_vocab" in result.metadata
        assert "text2_vocab" in result.metadata
        assert "mfw_requested" in result.metadata
        assert "method" in result.metadata
        assert result.metadata["method"] == "minmax_1992"

    def test_empty_text(self) -> None:
        """Empty text should return zero distance with warning."""
        result = compute_minmax("", "some text here")
        assert result.minmax_distance == 0.0
        assert result.feature_count == 0
        assert "warning" in result.metadata

    def test_mfw_parameter(self, doyle_hound: str, dickens: str) -> None:
        """Different mfw values should produce different feature counts."""
        result_small = compute_minmax(doyle_hound, dickens, mfw=10)
        result_large = compute_minmax(doyle_hound, dickens, mfw=200)
        assert result_small.feature_count == 10
        assert result_large.feature_count == 200

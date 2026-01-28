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
    JohnsBurrowsResult,
)
from pystylometry.authorship import (
    compute_johns_delta,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


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


class TestComputeJohnsDelta:
    """Tests for John Burrows' Delta variations."""

    def test_returns_johns_burrows_result(self, doyle_hound: str, dickens: str) -> None:
        """compute_johns_delta returns a JohnsBurrowsResult dataclass."""
        result = compute_johns_delta(doyle_hound, dickens)
        assert isinstance(result, JohnsBurrowsResult)

    def test_quadratic_method(self, doyle_hound: str, dickens: str) -> None:
        """Quadratic method should return a non-negative score."""
        result = compute_johns_delta(doyle_hound, dickens, method="quadratic")
        assert result.method == "quadratic"
        assert result.delta_score >= 0.0

    def test_weighted_method(self, doyle_hound: str, dickens: str) -> None:
        """Weighted method should return a non-negative score."""
        result = compute_johns_delta(doyle_hound, dickens, method="weighted")
        assert result.method == "weighted"
        assert result.delta_score >= 0.0

    def test_invalid_method(self, doyle_hound: str, dickens: str) -> None:
        """Invalid method should raise ValueError."""
        with pytest.raises(ValueError, match="method must be"):
            compute_johns_delta(doyle_hound, dickens, method="invalid")

    def test_identical_texts_zero_score(self, doyle_hound: str) -> None:
        """Identical texts should have zero delta score."""
        result_q = compute_johns_delta(doyle_hound, doyle_hound, method="quadratic")
        result_w = compute_johns_delta(doyle_hound, doyle_hound, method="weighted")
        assert result_q.delta_score == pytest.approx(0.0, abs=1e-6)
        assert result_w.delta_score == pytest.approx(0.0, abs=1e-6)

    def test_same_author_lower_than_diff_author(
        self, doyle_hound: str, doyle_sign: str, dickens: str
    ) -> None:
        """Same-author texts should have lower delta than different-author texts."""
        for method in ("quadratic", "weighted"):
            same = compute_johns_delta(doyle_hound, doyle_sign, method=method)
            diff = compute_johns_delta(doyle_hound, dickens, method=method)
            assert same.delta_score < diff.delta_score, (
                f"Method {method}: same-author ({same.delta_score:.3f}) "
                f"should be < diff-author ({diff.delta_score:.3f})"
            )

    def test_feature_count(self, doyle_hound: str, dickens: str) -> None:
        """Feature count should respect the mfw parameter."""
        result = compute_johns_delta(doyle_hound, dickens, mfw=30)
        assert result.feature_count == 30

    def test_most_distinctive_features_sorted(self, doyle_hound: str, dickens: str) -> None:
        """Distinctive features should be sorted descending by contribution."""
        result = compute_johns_delta(doyle_hound, dickens)
        scores = [s for _, s in result.most_distinctive_features]
        assert scores == sorted(scores, reverse=True)

    def test_metadata_contains_z_scores(self, doyle_hound: str, dickens: str) -> None:
        """Metadata should include z-score information."""
        result = compute_johns_delta(doyle_hound, dickens)
        assert "z_scores_text1" in result.metadata
        assert "z_scores_text2" in result.metadata
        assert isinstance(result.metadata["z_scores_text1"], dict)
        assert isinstance(result.metadata["z_scores_text2"], dict)

    def test_empty_text(self) -> None:
        """Empty text should return zero score with warning."""
        result = compute_johns_delta("", "hello world foo bar")
        assert result.delta_score == 0.0
        assert result.feature_count == 0
        assert "warning" in result.metadata

    def test_quadratic_vs_weighted_different_scores(self, doyle_hound: str, dickens: str) -> None:
        """Quadratic and weighted methods should generally produce different scores."""
        q = compute_johns_delta(doyle_hound, dickens, method="quadratic")
        w = compute_johns_delta(doyle_hound, dickens, method="weighted")
        # They use different formulas, so scores should differ
        assert q.delta_score != w.delta_score

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

from pystylometry.authorship import (
    compute_compression_distance,
    compute_johns_delta,
    compute_minmax,
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


class TestIntegration:
    """Cross-method integration tests."""

    def test_all_methods_agree_on_authorship(
        self, doyle_hound: str, doyle_sign: str, dickens: str
    ) -> None:
        """All methods should rank same-author pairs as more similar."""
        # MinMax: lower = more similar
        mm_same = compute_minmax(doyle_hound, doyle_sign)
        mm_diff = compute_minmax(doyle_hound, dickens)
        assert mm_same.minmax_distance < mm_diff.minmax_distance

        # John's Delta (quadratic): lower = more similar
        jd_same = compute_johns_delta(doyle_hound, doyle_sign, method="quadratic")
        jd_diff = compute_johns_delta(doyle_hound, dickens, method="quadratic")
        assert jd_same.delta_score < jd_diff.delta_score

        # NCD: lower = more similar
        ncd_same = compute_compression_distance(doyle_hound, doyle_sign)
        ncd_diff = compute_compression_distance(doyle_hound, dickens)
        assert ncd_same.ncd < ncd_diff.ncd

    def test_imports_from_package(self) -> None:
        """All methods should be importable from pystylometry.authorship."""
        from pystylometry.authorship import (  # noqa: F401
            compute_compression_distance,
            compute_johns_delta,
            compute_minmax,
        )

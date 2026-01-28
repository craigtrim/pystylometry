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
    CompressionResult,
)
from pystylometry.authorship import (
    compute_compression_distance,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


# ===== Shared Test Fixtures =====


# ===== compute_minmax Tests =====


@pytest.fixture(scope="module")
def ai_claude() -> str:
    """AI-generated text (Claude) from Kilgarriff fixtures."""
    return (FIXTURES_DIR / "kilgarriff" / "06-ai-claude.txt").read_text()


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


class TestComputeCompressionDistance:
    """Tests for the Normalized Compression Distance method."""

    def test_returns_compression_result(self, doyle_hound: str, dickens: str) -> None:
        """compute_compression_distance returns a CompressionResult."""
        result = compute_compression_distance(doyle_hound, dickens)
        assert isinstance(result, CompressionResult)

    def test_identical_texts_low_ncd(self) -> None:
        """Identical texts should have low NCD.

        Uses a short text because gzip's 32KB sliding window cannot exploit
        redundancy in texts larger than ~32KB when concatenated, causing NCD
        to approach 1.0 even for identical texts. bz2 (900KB blocks) handles
        larger texts but we test the principle with manageable size here.
        """
        short_text = "The quick brown fox jumps over the lazy dog. " * 100
        result = compute_compression_distance(short_text, short_text)
        # gzip header overhead means NCD won't reach 0 even for identical texts,
        # but it should be well below 0.5 (different-text range)
        assert result.ncd < 0.3

    def test_different_texts_higher_ncd(self, doyle_hound: str, dickens: str) -> None:
        """Different texts should have higher NCD than identical texts."""
        identical = compute_compression_distance(doyle_hound, doyle_hound)
        different = compute_compression_distance(doyle_hound, dickens)
        assert different.ncd > identical.ncd

    def test_same_author_lower_ncd(self, doyle_hound: str, doyle_sign: str, dickens: str) -> None:
        """Same-author texts should have lower NCD than different-author texts."""
        same = compute_compression_distance(doyle_hound, doyle_sign)
        diff = compute_compression_distance(doyle_hound, dickens)
        assert same.ncd < diff.ncd

    def test_gzip_compressor(self, doyle_hound: str, dickens: str) -> None:
        """gzip compressor should work and be recorded."""
        result = compute_compression_distance(doyle_hound, dickens, compressor="gzip")
        assert result.compressor == "gzip"
        assert result.ncd > 0

    def test_zlib_compressor(self, doyle_hound: str, dickens: str) -> None:
        """zlib compressor should work and be recorded."""
        result = compute_compression_distance(doyle_hound, dickens, compressor="zlib")
        assert result.compressor == "zlib"
        assert result.ncd > 0

    def test_bz2_compressor(self, doyle_hound: str, dickens: str) -> None:
        """bz2 compressor should work and be recorded."""
        result = compute_compression_distance(doyle_hound, dickens, compressor="bz2")
        assert result.compressor == "bz2"
        assert result.ncd > 0

    def test_invalid_compressor(self, doyle_hound: str, dickens: str) -> None:
        """Invalid compressor should raise ValueError."""
        with pytest.raises(ValueError, match="compressor must be one of"):
            compute_compression_distance(doyle_hound, dickens, compressor="lzma")

    def test_compressed_sizes_positive(self, doyle_hound: str, dickens: str) -> None:
        """All compressed sizes should be positive integers."""
        result = compute_compression_distance(doyle_hound, dickens)
        assert result.text1_compressed_size > 0
        assert result.text2_compressed_size > 0
        assert result.combined_compressed_size > 0

    def test_combined_less_than_sum(self, doyle_hound: str, dickens: str) -> None:
        """Combined compressed size should be less than sum of individual sizes
        (compression exploits shared patterns)."""
        result = compute_compression_distance(doyle_hound, dickens)
        individual_sum = result.text1_compressed_size + result.text2_compressed_size
        assert result.combined_compressed_size < individual_sum

    def test_metadata_fields(self, doyle_hound: str, dickens: str) -> None:
        """Metadata should contain expected fields."""
        result = compute_compression_distance(doyle_hound, dickens)
        assert "text1_raw_size" in result.metadata
        assert "text2_raw_size" in result.metadata
        assert "text1_compression_ratio" in result.metadata
        assert "text2_compression_ratio" in result.metadata
        assert "combined_compression_ratio" in result.metadata

    def test_compression_ratios_between_0_and_1(self, doyle_hound: str, dickens: str) -> None:
        """Compression ratios should be between 0 and 1 for normal text."""
        result = compute_compression_distance(doyle_hound, dickens)
        assert 0 < result.metadata["text1_compression_ratio"] < 1
        assert 0 < result.metadata["text2_compression_ratio"] < 1

    def test_empty_texts(self) -> None:
        """Two empty texts should return NCD of 0."""
        result = compute_compression_distance("", "")
        assert result.ncd == 0.0

    def test_symmetry(self, doyle_hound: str, dickens: str) -> None:
        """NCD should be approximately symmetric."""
        result_ab = compute_compression_distance(doyle_hound, dickens)
        result_ba = compute_compression_distance(dickens, doyle_hound)
        # Not exactly symmetric due to concatenation order, but should be close
        assert abs(result_ab.ncd - result_ba.ncd) < 0.1

    def test_different_compressors_similar_ranking(
        self, doyle_hound: str, doyle_sign: str, dickens: str
    ) -> None:
        """Different compressors should agree on relative similarity ordering."""
        for compressor in ("gzip", "zlib", "bz2"):
            same = compute_compression_distance(doyle_hound, doyle_sign, compressor=compressor)
            diff = compute_compression_distance(doyle_hound, dickens, compressor=compressor)
            assert same.ncd < diff.ncd, (
                f"Compressor {compressor}: same-author NCD ({same.ncd:.3f}) "
                f"should be < diff-author NCD ({diff.ncd:.3f})"
            )

    def test_human_vs_ai_detection(self, doyle_hound: str, doyle_sign: str, ai_claude: str) -> None:
        """Human-written texts should be more similar to each other than to
        AI-generated text."""
        human_pair = compute_compression_distance(doyle_hound, doyle_sign)
        human_ai = compute_compression_distance(doyle_hound, ai_claude)
        assert human_pair.ncd < human_ai.ncd

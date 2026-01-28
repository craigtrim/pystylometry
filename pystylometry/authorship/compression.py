"""Compression-based authorship attribution using Normalized Compression Distance.

This module implements the Normalized Compression Distance (NCD) method for
authorship attribution. NCD is a language-independent similarity metric based
on Kolmogorov complexity, approximated through real-world compressors.

Related GitHub Issue:
    #24 - Additional Authorship Attribution Methods
    https://github.com/craigtrim/pystylometry/issues/24

The core insight is that if two texts share statistical regularities (as texts
by the same author tend to), compressing them together yields better compression
than compressing separately. This captures deep patterns including vocabulary,
syntax, and stylistic preferences without requiring explicit feature engineering.

References:
    Cilibrasi, R., & Vitányi, P. M. (2005). Clustering by compression.
        IEEE Transactions on Information Theory, 51(4), 1523-1545.
    Benedetto, D., Caglioti, E., & Loreto, V. (2002). Language trees and
        zipping. Physical Review Letters, 88(4), 048702.
    Li, M., et al. (2004). The similarity metric. IEEE Transactions on
        Information Theory, 50(12), 3250-3264.
"""

from __future__ import annotations

import bz2
import gzip
import zlib

from .._types import CompressionResult

# Supported compressors mapped to their compress functions
_COMPRESSORS: dict[str, type] = {
    "gzip": type(None),  # placeholder, handled below
    "zlib": type(None),
    "bz2": type(None),
}

_VALID_COMPRESSORS = frozenset({"gzip", "zlib", "bz2"})


def _compress(data: bytes, compressor: str) -> bytes:
    """Compress data using the specified algorithm.

    Args:
        data: Raw bytes to compress.
        compressor: One of "gzip", "zlib", or "bz2".

    Returns:
        Compressed bytes.
    """
    if compressor == "gzip":
        return gzip.compress(data)
    if compressor == "zlib":
        return zlib.compress(data)
    if compressor == "bz2":
        return bz2.compress(data)
    raise ValueError(f"Unknown compressor: {compressor}")  # pragma: no cover


def compute_compression_distance(
    text1: str,
    text2: str,
    compressor: str = "gzip",
) -> CompressionResult:
    """
    Compute Normalized Compression Distance (NCD) between two texts.

    NCD approximates the normalized information distance, a universal similarity
    metric based on Kolmogorov complexity. Since Kolmogorov complexity is
    uncomputable, NCD uses real-world compressors as practical approximations.

    Related GitHub Issue:
        #24 - Additional Authorship Attribution Methods
        https://github.com/craigtrim/pystylometry/issues/24

    Algorithm:
        1. Encode both texts as UTF-8 bytes
        2. Compress text1, text2, and their concatenation separately
        3. Compute NCD using the formula:
           NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))

    Interpretation:
        - NCD ~ 0: Texts are maximally similar (identical information content)
        - NCD ~ 1: Texts are maximally different (no shared information)
        - Values slightly above 1.0 are possible due to compressor overhead
        - Typical same-author pairs: 0.3-0.6
        - Typical different-author pairs: 0.6-0.9

    Compressor choice:
        - "gzip" (default): Good balance of speed and accuracy; most widely used
          in NCD literature. Uses Lempel-Ziv (LZ77) algorithm.
        - "zlib": Same underlying algorithm as gzip but lower overhead. Slightly
          faster, very similar results.
        - "bz2": Uses Burrows-Wheeler transform. Better compression but slower.
          May capture different patterns than LZ-based methods.

    References:
        Cilibrasi, R., & Vitanyi, P. M. (2005). Clustering by compression.
            IEEE Transactions on Information Theory, 51(4), 1523-1545.
        Benedetto, D., Caglioti, E., & Loreto, V. (2002). Language trees and
            zipping. Physical Review Letters, 88(4), 048702.
        Li, M., et al. (2004). The similarity metric. IEEE Transactions on
            Information Theory, 50(12), 3250-3264.

    Args:
        text1: First text for comparison.
        text2: Second text for comparison.
        compressor: Compression algorithm to use ("gzip", "zlib", or "bz2").

    Returns:
        CompressionResult with NCD score and compression details.

    Raises:
        ValueError: If compressor is not one of "gzip", "zlib", "bz2".

    Example:
        >>> result = compute_compression_distance(text_by_author_a, text_by_author_b)
        >>> print(f"NCD: {result.ncd:.3f}")
        >>> print(f"Compressor: {result.compressor}")
        >>> if result.ncd < 0.5:
        ...     print("Texts likely by same author")
    """
    if compressor not in _VALID_COMPRESSORS:
        raise ValueError(
            f"compressor must be one of {sorted(_VALID_COMPRESSORS)}, got '{compressor}'"
        )

    # Encode texts as bytes
    bytes1 = text1.encode("utf-8")
    bytes2 = text2.encode("utf-8")
    bytes_combined = bytes1 + bytes2

    # Compress each component
    compressed1 = _compress(bytes1, compressor)
    compressed2 = _compress(bytes2, compressor)
    compressed_combined = _compress(bytes_combined, compressor)

    c1 = len(compressed1)
    c2 = len(compressed2)
    c12 = len(compressed_combined)

    # NCD formula: (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
    min_c = min(c1, c2)
    max_c = max(c1, c2)

    if max_c == 0:
        # Both texts are empty
        ncd = 0.0
    else:
        ncd = (c12 - min_c) / max_c

    # Compute compression ratios for metadata
    raw1 = len(bytes1)
    raw2 = len(bytes2)
    raw_combined = len(bytes_combined)

    return CompressionResult(
        ncd=ncd,
        compressor=compressor,
        text1_compressed_size=c1,
        text2_compressed_size=c2,
        combined_compressed_size=c12,
        metadata={
            "text1_raw_size": raw1,
            "text2_raw_size": raw2,
            "combined_raw_size": raw_combined,
            "text1_compression_ratio": c1 / raw1 if raw1 > 0 else 0.0,
            "text2_compression_ratio": c2 / raw2 if raw2 > 0 else 0.0,
            "combined_compression_ratio": c12 / raw_combined if raw_combined > 0 else 0.0,
            "min_compressed": min_c,
            "max_compressed": max_c,
        },
    )

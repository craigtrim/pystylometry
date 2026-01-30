"""Type-Token Ratio (TTR) analysis with native chunked computation.

Computes multiple TTR variants for measuring lexical diversity (vocabulary
richness). All metrics are computed per-chunk and wrapped in Distribution
objects for stylometric fingerprinting.

Previously delegated to the external ``stylometry-ttr`` package; now
computed inline using only the Python standard library (``math`` and
``statistics``).

Related GitHub Issues:
    #27 - Native chunked analysis with Distribution dataclass
    https://github.com/craigtrim/pystylometry/issues/27

    #43 - Inline stylometry-ttr into pystylometry (remove external dependency)
    https://github.com/craigtrim/pystylometry/issues/43

References:
    Guiraud, P. (1960). Problèmes et méthodes de la statistique linguistique.
    Herdan, G. (1960). Type-token Mathematics: A Textbook of Mathematical
        Linguistics. Mouton.
    Johnson, W. (1944). Studies in language behavior: I. A program of research.
        Psychological Monographs, 56(2), 1-15.
"""

from __future__ import annotations

import math
import statistics
from typing import Optional

from .._types import Distribution, TTRAggregateResult, TTRResult, make_distribution
from ..tokenizer import Tokenizer

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Minimum words required before STTR computation is meaningful.
# With fewer words we cannot form at least two full chunks, so the
# standardised metric would be unreliable.
_MIN_WORDS_FOR_STTR = 2000


def _compute_chunk_ttrs(tokens: list[str], chunk_size: int) -> list[float]:
    """Compute per-chunk raw TTR values for non-overlapping chunks.

    Only full-sized chunks are included so that every TTR is measured on the
    same token count, keeping the standardised metric unbiased.

    Args:
        tokens: Full token list.
        chunk_size: Number of tokens per chunk.

    Returns:
        List of per-chunk TTR values (may be empty if too few tokens).
    """
    total = len(tokens)
    chunk_ttrs: list[float] = []
    for i in range(0, total - chunk_size + 1, chunk_size):
        chunk = tokens[i : i + chunk_size]
        chunk_ttrs.append(len(set(chunk)) / chunk_size)
    return chunk_ttrs


def _compute_deltas(
    chunk_ttrs: list[float],
) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """Compute delta metrics: TTR(n) - TTR(n-1) for consecutive chunks.

    Delta metrics capture chunk-to-chunk vocabulary variability:
    - delta_mean: average change (positive = expanding vocabulary)
    - delta_std: volatility of change (stylometric fingerprint)
    - delta_min: largest negative swing
    - delta_max: largest positive swing

    Args:
        chunk_ttrs: Per-chunk TTR values (needs >= 2 values).

    Returns:
        Tuple of (delta_mean, delta_std, delta_min, delta_max).
        All ``None`` when fewer than 2 chunks are available.
    """
    if len(chunk_ttrs) < 2:
        return None, None, None, None

    deltas = [chunk_ttrs[i] - chunk_ttrs[i - 1] for i in range(1, len(chunk_ttrs))]
    d_mean = statistics.mean(deltas)
    d_std = statistics.stdev(deltas) if len(deltas) > 1 else 0.0
    return d_mean, d_std, min(deltas), max(deltas)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compute_ttr(
    text: str,
    text_id: str | None = None,
    chunk_size: int = 1000,
) -> TTRResult:
    """Compute Type-Token Ratio (TTR) metrics for vocabulary richness.

    Tokenises the input with pystylometry's ``Tokenizer`` (lowercase, words
    only), then computes five TTR-family metrics.  Each metric is computed
    per-chunk and the full per-chunk distribution is exposed via a
    ``Distribution`` object for stylometric fingerprinting.

    Metrics computed:
        - **Raw TTR**: ``unique_words / total_words``
        - **Root TTR** (Guiraud's index): ``unique_words / sqrt(total_words)``
        - **Log TTR** (Herdan's C): ``log(unique_words) / log(total_words)``
        - **STTR**: Mean TTR across fixed-size chunks (reduces length bias).
          Only computed when the text has >= 2000 words.
        - **Delta Std**: Std-dev of chunk-to-chunk TTR change (vocabulary
          consistency).  Only computed when >= 2 chunks are available.

    Related GitHub Issues:
        #27 - Native chunked analysis with Distribution dataclass
        https://github.com/craigtrim/pystylometry/issues/27

        #43 - Inline stylometry-ttr into pystylometry
        https://github.com/craigtrim/pystylometry/issues/43

    References:
        Guiraud, P. (1960). Problèmes et méthodes de la statistique
            linguistique.
        Herdan, G. (1960). Type-token Mathematics: A Textbook of Mathematical
            Linguistics. Mouton.
        Johnson, W. (1944). Studies in language behavior: I. A program of
            research. Psychological Monographs, 56(2), 1-15.

    Args:
        text: Input text to analyse.
        text_id: Optional identifier for the text (stored in metadata).
        chunk_size: Number of words per chunk for STTR and per-chunk
            distributions (default: 1000).

    Returns:
        TTRResult with all TTR variants, Distribution objects, and metadata.

    Example:
        >>> result = compute_ttr("The quick brown fox jumps over the lazy dog.")
        >>> print(f"Raw TTR: {result.ttr:.3f}")
        Raw TTR: 1.000
        >>> print(f"Root TTR: {result.root_ttr:.3f}")
        Root TTR: 3.000

        >>> # With text identifier
        >>> result = compute_ttr("Sample text here.", text_id="sample-001")
        >>> print(result.metadata["text_id"])
        sample-001
    """
    # Tokenise using pystylometry's own tokenizer (lowercase, words only)
    tokenizer = Tokenizer(lowercase=True, strip_punctuation=True)
    tokens = tokenizer.tokenize(text)

    total_words = len(tokens)

    # --- empty / trivial text --------------------------------------------------
    if total_words == 0:
        empty_dist = Distribution(
            values=[],
            mean=float("nan"),
            median=float("nan"),
            std=0.0,
            range=0.0,
            iqr=0.0,
        )
        return TTRResult(
            total_words=0,
            unique_words=0,
            ttr=0.0,
            root_ttr=0.0,
            log_ttr=0.0,
            sttr=0.0,
            delta_std=0.0,
            ttr_dist=empty_dist,
            root_ttr_dist=empty_dist,
            log_ttr_dist=empty_dist,
            sttr_dist=empty_dist,
            delta_std_dist=empty_dist,
            chunk_size=chunk_size,
            chunk_count=0,
            metadata={
                "text_id": text_id or "",
                "sttr_available": False,
                "delta_std_available": False,
            },
        )

    # --- global metrics --------------------------------------------------------
    unique_words = len(set(tokens))
    ttr_val = unique_words / total_words
    root_ttr_val = unique_words / math.sqrt(total_words)
    log_ttr_val = math.log(unique_words) / math.log(total_words) if total_words > 1 else 0.0

    # --- per-chunk metrics -----------------------------------------------------
    chunk_ttrs = _compute_chunk_ttrs(tokens, chunk_size)
    chunk_count = len(chunk_ttrs)

    # STTR: mean TTR across chunks (only meaningful with enough text)
    sttr_available = total_words >= _MIN_WORDS_FOR_STTR and chunk_count >= 1
    if sttr_available:
        sttr_val = statistics.mean(chunk_ttrs)
    else:
        sttr_val = 0.0

    # Delta metrics
    delta_mean, delta_std_val, delta_min, delta_max = _compute_deltas(chunk_ttrs)
    delta_std_available = delta_std_val is not None
    if delta_std_val is None:
        delta_std_val = 0.0

    # --- build Distribution objects --------------------------------------------
    # For per-chunk distributions: compute root_ttr and log_ttr per chunk as well
    if chunk_count >= 1:
        ttr_dist = make_distribution(chunk_ttrs)

        # Root TTR per chunk: for each chunk of chunk_size tokens,
        # root_ttr = unique / sqrt(chunk_size)
        root_ttr_chunks = [
            len(set(tokens[i : i + chunk_size])) / math.sqrt(chunk_size)
            for i in range(0, total_words - chunk_size + 1, chunk_size)
        ]
        root_ttr_dist = make_distribution(root_ttr_chunks)

        # Log TTR per chunk
        log_ttr_chunks = []
        for i in range(0, total_words - chunk_size + 1, chunk_size):
            chunk = tokens[i : i + chunk_size]
            u = len(set(chunk))
            t = len(chunk)
            val = math.log(u) / math.log(t) if t > 1 else 0.0
            log_ttr_chunks.append(val)
        log_ttr_dist = make_distribution(log_ttr_chunks)

        sttr_dist = (
            make_distribution(chunk_ttrs) if sttr_available else make_distribution([sttr_val])
        )
        delta_std_dist = (
            make_distribution([delta_std_val]) if delta_std_available else make_distribution([0.0])
        )
    else:
        # Not enough text for any chunks — wrap globals in single-value dists
        ttr_dist = make_distribution([ttr_val])
        root_ttr_dist = make_distribution([root_ttr_val])
        log_ttr_dist = make_distribution([log_ttr_val])
        sttr_dist = make_distribution([sttr_val])
        delta_std_dist = make_distribution([0.0])

    return TTRResult(
        total_words=total_words,
        unique_words=unique_words,
        ttr=round(ttr_val, 6),
        root_ttr=round(root_ttr_val, 4),
        log_ttr=round(log_ttr_val, 6),
        sttr=round(sttr_val, 6),
        delta_std=round(delta_std_val, 6),
        ttr_dist=ttr_dist,
        root_ttr_dist=root_ttr_dist,
        log_ttr_dist=log_ttr_dist,
        sttr_dist=sttr_dist,
        delta_std_dist=delta_std_dist,
        chunk_size=chunk_size,
        chunk_count=chunk_count if chunk_count >= 1 else 1,
        metadata={
            "text_id": text_id or "",
            "sttr_available": sttr_available,
            "delta_std_available": delta_std_available,
        },
    )


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


class TTRAggregator:
    """Aggregate per-text TTR results into group-level statistics.

    Useful for comparing vocabulary richness across authors, genres, or
    time periods by computing summary statistics (mean, std, min, max,
    median) over a collection of ``TTRResult`` objects.

    Related GitHub Issue:
        #43 - Inline stylometry-ttr into pystylometry
        https://github.com/craigtrim/pystylometry/issues/43

    Example:
        >>> from pystylometry.lexical import compute_ttr, TTRAggregator
        >>> results = [compute_ttr(t) for t in texts]
        >>> agg = TTRAggregator()
        >>> stats = agg.aggregate(results, group_id="Shakespeare")
        >>> print(stats.ttr_mean)
        0.412
    """

    def aggregate(self, results: list[TTRResult], group_id: str) -> TTRAggregateResult:
        """Compute aggregate statistics from multiple TTR results.

        Args:
            results: List of per-text ``TTRResult`` objects.
            group_id: Identifier for the group (e.g. author name).

        Returns:
            ``TTRAggregateResult`` with group-level statistics.

        Raises:
            ValueError: If *results* is empty.
        """
        if not results:
            raise ValueError("Cannot aggregate empty results list")

        ttrs = [r.ttr for r in results]
        root_ttrs = [r.root_ttr for r in results]
        log_ttrs = [r.log_ttr for r in results]
        sttrs = [r.sttr for r in results if r.metadata.get("sttr_available")]
        delta_stds = [r.delta_std for r in results if r.metadata.get("delta_std_available")]

        return TTRAggregateResult(
            group_id=group_id,
            text_count=len(results),
            total_words=sum(r.total_words for r in results),
            ttr_mean=round(statistics.mean(ttrs), 6),
            ttr_std=round(statistics.stdev(ttrs), 6) if len(ttrs) > 1 else 0.0,
            ttr_min=round(min(ttrs), 6),
            ttr_max=round(max(ttrs), 6),
            ttr_median=round(statistics.median(ttrs), 6),
            root_ttr_mean=round(statistics.mean(root_ttrs), 4),
            root_ttr_std=round(statistics.stdev(root_ttrs), 4) if len(root_ttrs) > 1 else 0.0,
            log_ttr_mean=round(statistics.mean(log_ttrs), 6),
            log_ttr_std=round(statistics.stdev(log_ttrs), 6) if len(log_ttrs) > 1 else 0.0,
            sttr_mean=round(statistics.mean(sttrs), 6) if sttrs else None,
            sttr_std=round(statistics.stdev(sttrs), 6) if len(sttrs) > 1 else None,
            delta_std_mean=round(statistics.mean(delta_stds), 6) if delta_stds else None,
            metadata={"group_id": group_id, "text_count": len(results)},
        )

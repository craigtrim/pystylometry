"""Lexical diversity metrics."""

# Re-export from stylometry-ttr
# from stylometry_ttr import compute_ttr, TTRResult

# Local implementations
from .hapax import compute_hapax_ratios, compute_hapax_with_lexicon_analysis
from .mtld import compute_mtld
from .yule import compute_yule

__all__ = [
    # "compute_ttr",  # From stylometry-ttr
    # "TTRResult",    # From stylometry-ttr
    "compute_mtld",
    "compute_yule",
    "compute_hapax_ratios",
    "compute_hapax_with_lexicon_analysis",
]

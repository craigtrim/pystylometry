"""Visualization module for pystylometry.

This module provides visualization functions for stylometric analysis results.

Matplotlib Functions (PNG output):
    Requires optional dependencies: pip install pystylometry[viz]

    plot_drift_timeline: Line chart of chi-squared values over document
    plot_drift_scatter: Scatter plot with reference zones (tic-tac-toe style)
    plot_drift_report: Combined multi-panel visualization

Interactive JSX Functions (HTML output):
    No additional dependencies required (uses React via CDN)

    export_drift_timeline_jsx: Interactive timeline chart
    export_drift_report_jsx: Interactive multi-panel dashboard
    export_drift_viewer: Standalone viewer with file upload

Related GitHub Issues:
    #38 - Visualization Options for Style Drift Detection
    https://github.com/craigtrim/pystylometry/issues/38

Example:
    >>> from pystylometry.consistency import compute_kilgarriff_drift
    >>> from pystylometry.viz import plot_drift_timeline, export_drift_timeline_jsx
    >>>
    >>> result = compute_kilgarriff_drift(text)
    >>> plot_drift_timeline(result, output="timeline.png")  # Static PNG
    >>> export_drift_timeline_jsx(result, "timeline.html")  # Interactive HTML
"""

from .drift import (  # noqa: E402
    plot_drift_report,
    plot_drift_scatter,
    plot_drift_timeline,
)
from .jsx import (  # noqa: E402
    export_drift_report_jsx,
    export_drift_timeline_jsx,
    export_drift_viewer,
)

try:
    import matplotlib  # noqa: F401
    import seaborn  # noqa: F401  # type: ignore[import-untyped]

    _VIZ_AVAILABLE = True
except ImportError:
    _VIZ_AVAILABLE = False


def _check_viz_available() -> None:
    """Raise ImportError if visualization dependencies are not installed."""
    if not _VIZ_AVAILABLE:
        raise ImportError(
            "Visualization requires optional dependencies. "
            "Install with: pip install pystylometry[viz] or poetry install --with viz"
        )


__all__ = [
    # Matplotlib (PNG)
    "plot_drift_timeline",
    "plot_drift_scatter",
    "plot_drift_report",
    # JSX (HTML)
    "export_drift_timeline_jsx",
    "export_drift_report_jsx",
    # Standalone viewer
    "export_drift_viewer",
]

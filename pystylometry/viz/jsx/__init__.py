"""Interactive JSX/HTML exports for pystylometry visualizations.

This module provides self-contained HTML exports using React via CDN.
Each visualization opens directly in a browser without build steps.

Available Functions:
    export_drift_timeline_jsx: Timeline of chi-squared values
    export_drift_report_jsx: Multi-panel dashboard
    export_drift_viewer: Standalone viewer with file upload (no pre-computed data)

Example:
    >>> from pystylometry.consistency import compute_kilgarriff_drift
    >>> from pystylometry.viz.jsx import export_drift_timeline_jsx, export_drift_viewer
    >>>
    >>> # Pre-computed visualization
    >>> result = compute_kilgarriff_drift(text)
    >>> export_drift_timeline_jsx(result, "timeline.html")
    >>>
    >>> # Standalone viewer (users can upload their own files)
    >>> export_drift_viewer("drift_analyzer.html")
"""

from .report import export_drift_report_jsx
from .timeline import export_drift_timeline_jsx
from .viewer import export_drift_viewer

__all__ = [
    "export_drift_timeline_jsx",
    "export_drift_report_jsx",
    "export_drift_viewer",
]

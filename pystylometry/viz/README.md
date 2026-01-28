# viz

![6 public functions](https://img.shields.io/badge/functions-6-blue)
![Optional: matplotlib](https://img.shields.io/badge/optional-matplotlib-yellow)

Visualization for drift detection results. Two output modes: static PNG (matplotlib) and interactive HTML (React JSX).

## Catalogue

| File | Functions | Output |
|------|-----------|--------|
| `drift.py` | `plot_drift_timeline`, `plot_drift_scatter`, `plot_drift_report` | PNG via matplotlib/seaborn |
| `jsx/report.py` | `export_drift_report_jsx` | Interactive HTML dashboard |
| `jsx/timeline.py` | `export_drift_timeline_jsx` | Interactive HTML timeline |
| `jsx/viewer.py` | `export_drift_viewer` | Standalone HTML viewer with file upload |
| `jsx/_base.py` | _(internal)_ | React/JSX rendering base |

## Install

```
pip install pystylometry[viz]   # For PNG output (matplotlib + seaborn)
# JSX/HTML output requires no additional dependencies
```

## See Also

- [`consistency/`](../consistency/) produces the `KilgarriffDriftResult` consumed by all viz functions

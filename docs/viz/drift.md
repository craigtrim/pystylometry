# Drift Visualization (Matplotlib)

## Static Visualizations for Kilgarriff Chi-Squared Drift Detection

---

## Theoretical Background

### Origins

Visualization of stylometric data transforms numeric drift detection results into interpretable visual patterns. The matplotlib-based visualization module provides publication-quality static plots for drift analysis results, complementing the interactive JSX/HTML exports for exploratory analysis.

The visualization design follows established principles from exploratory data analysis (Tukey, 1977) and information visualization (Few, 2012). Timeline plots reveal temporal patterns in chi-squared values. Scatter plots with reference zones provide comparative analysis across documents. Multi-panel reports combine multiple perspectives for comprehensive analysis.

### Mathematical Foundation

The visualizations use empirically derived reference bounds for zone classification:

| Bound | Value | Interpretation |
|-------|-------|----------------|
| `MEAN_CHI_LOW` | 100 | Below: AI-like baseline |
| `MEAN_CHI_HIGH` | 250 | Above: Human-like baseline |
| `CV_LOW` | 0.08 | Below: Very stable (suspiciously uniform) |
| `CV_HIGH` | 0.20 | Above: Volatile (potential discontinuity) |

The scatter plot uses a tic-tac-toe style zone layout:
- X-axis: Mean chi-squared (baseline stylistic variation)
- Y-axis: Coefficient of variation (volatility)

This two-dimensional representation captures both the overall level of inter-chunk difference and the stability of that difference across the document.

### Interpretation

**Timeline plots** reveal temporal structure:
- Flat lines indicate consistent style
- Upward trends indicate gradual drift
- Sharp peaks indicate splice points or author boundaries
- Flat low lines may indicate AI-generated content

**Scatter plots** enable comparative analysis:
- Bottom-left quadrant: AI-uniform zone (low mean, low CV)
- Bottom-right quadrant: Human-tight zone (high mean, low CV)
- Middle-right: Human normal zone (high mean, moderate CV)
- Top-right: Splice zone (high mean, high CV)
- Middle column: Transition zone (ambiguous)

---

## Implementation

### Core Algorithm

The module provides three visualization functions, all requiring matplotlib and seaborn:

**`plot_drift_timeline`**: Line chart of chi-squared values over the document
- Plots chi-squared value per window pair comparison
- Marks the spike location with a vertical red dashed line
- Shows reference threshold lines (AI baseline at 50, spike threshold at mean + 2 sigma)
- Displays mean line and summary statistics annotation
- Fills under the curve for visual weight

**`plot_drift_scatter`**: Reference zone scatter plot for comparing multiple documents
- Plots each document as a point with coordinates (mean_chi, CV)
- Colors points by detected pattern (green=consistent, red=spike, amber=drift, purple=uniform)
- Draws reference zone backgrounds and boundary lines
- Labels zones with descriptive names (AI-UNIFORM, HUMAN, SPLICE, TRANSITION)
- Shows reference bounds annotation

**`plot_drift_report`**: Multi-panel comprehensive report
- Panel 1 (full width): Chi-squared timeline
- Panel 2 (left): Histogram of chi-squared distribution with KDE
- Panel 3 (right): Summary statistics text panel
- Panel 4 (left): Horizontal bar chart of top contributing words at spike location
- Panel 5 (right): Zone classification with reference bounds

### Key Features

- **Seaborn styling**: Uses seaborn's `whitegrid` theme for clean, professional appearance
- **Configurable output**: Save to file (PNG, PDF, SVG) or display interactively
- **Configurable figure size**: Default sizes optimized for common use cases
- **Pattern-aware coloring**: Points and annotations colored by detected pattern
- **Reference thresholds**: Visual reference lines for AI baseline, spike detection, and mean

### Dependencies

Requires optional visualization dependencies:

```bash
pip install pystylometry[viz]
```

This installs matplotlib and seaborn. If these packages are not installed, importing the visualization functions will raise an `ImportError` with installation instructions.

---

## Usage

### API Examples

```python
from pystylometry.consistency import compute_kilgarriff_drift
from pystylometry.viz import plot_drift_timeline, plot_drift_scatter, plot_drift_report

# Compute drift result
result = compute_kilgarriff_drift(text)

# Timeline plot - save to file
plot_drift_timeline(result, output="timeline.png")

# Timeline plot - display interactively
plot_drift_timeline(result)

# Timeline with custom title and size
plot_drift_timeline(
    result,
    output="timeline.pdf",
    title="Style Analysis: Chapter 12",
    figsize=(16, 8),
    show_spike_threshold=True,
    show_ai_threshold=True,
)

# Scatter plot comparing multiple documents
results = [
    ("Novel Chapter 1", compute_kilgarriff_drift(chapter_1)),
    ("Novel Chapter 2", compute_kilgarriff_drift(chapter_2)),
    ("AI-Generated", compute_kilgarriff_drift(ai_text)),
    ("Spliced Document", compute_kilgarriff_drift(spliced_text)),
]
plot_drift_scatter(results, output="scatter.png")

# Scatter plot with custom options
plot_drift_scatter(
    results,
    output="scatter.svg",
    title="Document Comparison",
    figsize=(12, 10),
    show_zones=True,
    annotate_points=True,
)

# Comprehensive report
plot_drift_report(
    result,
    label="Manuscript Draft",
    output="report.png",
    figsize=(14, 10),
)
```

### Parameters

**`plot_drift_timeline`**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `result` | `KilgarriffDriftResult` | (required) | Drift detection result |
| `output` | `str \| Path \| None` | `None` | Output path; `None` shows interactively |
| `title` | `str \| None` | `None` | Custom title; auto-generated if `None` |
| `figsize` | `tuple[float, float]` | `(12, 6)` | Figure size in inches |
| `show_spike_threshold` | `bool` | `True` | Show spike detection threshold line |
| `show_ai_threshold` | `bool` | `True` | Show AI baseline threshold line |

**`plot_drift_scatter`**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `results` | `list[tuple[str, KilgarriffDriftResult]]` | (required) | List of (label, result) pairs |
| `output` | `str \| Path \| None` | `None` | Output path |
| `title` | `str` | `"Style Drift Detection..."` | Chart title |
| `figsize` | `tuple[float, float]` | `(10, 8)` | Figure size |
| `show_zones` | `bool` | `True` | Show reference zone backgrounds |
| `annotate_points` | `bool` | `True` | Label each point |

**`plot_drift_report`**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `result` | `KilgarriffDriftResult` | (required) | Drift detection result |
| `label` | `str` | `"Document"` | Document label for title |
| `output` | `str \| Path \| None` | `None` | Output path |
| `figsize` | `tuple[float, float]` | `(14, 10)` | Figure size |

---

## Limitations

### Static Output

Matplotlib plots are static images. For interactive exploration (hover details, point selection, chunk text display), use the JSX/HTML exports from `pystylometry.viz.jsx`.

### Reference Bounds

The zone boundaries in the scatter plot (`MEAN_CHI_LOW=100`, `MEAN_CHI_HIGH=250`, `CV_LOW=0.08`, `CV_HIGH=0.20`) are empirically derived estimates. They may not generalize to all genres and domains. Users should calibrate these bounds against their specific corpora.

### Dependency Weight

Matplotlib and seaborn are substantial dependencies. For lightweight deployments, use the JSX/HTML exports which require no additional Python packages.

### Axis Scaling

The scatter plot auto-scales axes based on data points but uses fixed zone boundaries. Documents with extreme values may cause zones to appear compressed or off-screen.

---

## References

Kilgarriff, Adam. "Comparing Corpora." *International Journal of Corpus Linguistics*, vol. 6, no. 1, 2001, pp. 97-133.

Tukey, John W. *Exploratory Data Analysis*. Addison-Wesley, 1977.

Few, Stephen. *Show Me the Numbers: Designing Tables and Graphs to Enlighten*. 2nd ed., Analytics Press, 2012.

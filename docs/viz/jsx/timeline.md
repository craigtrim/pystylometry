# Interactive Drift Timeline (JSX/HTML)

## Self-Contained Interactive Visualization for Style Drift Detection

---

## Theoretical Background

### Origins

Interactive visualizations provide richer exploration of stylometric data than static images. The JSX timeline export creates self-contained HTML files that open directly in any modern browser, combining the accessibility of web technologies with the analytical depth of pystylometry's drift detection.

The design philosophy follows Shneiderman's visual information seeking mantra: "Overview first, zoom and filter, then details on demand" (Shneiderman, 1996). The timeline provides an overview of drift patterns across the document. Hovering and clicking provide detailed information about individual comparisons. When chunk text is provided, users can read the actual content at any point in the timeline.

### Mathematical Foundation

The visualization renders the same chi-squared data produced by `compute_kilgarriff_drift()`, with additional derived values for visual encoding:

**Color encoding** uses z-score distance from mean:

```
z_score = |chi - mean_chi| / std_chi
distance = min(1, z_score / 3)
```

Points are colored on a green-yellow-red gradient:
- Green (distance = 0): At the mean, typical variation
- Yellow (distance = 0.5): 1.5 standard deviations from mean
- Red (distance = 1.0): 3+ standard deviations from mean

**Threshold lines**:
- Mean (mu): Horizontal gray line at the document's mean chi-squared
- AI baseline: Horizontal dashed amber line at chi-squared = 50
- Spike threshold (mu + 2 sigma): Horizontal dashed green line

**Classification per point**:

| Chi-squared Range | Label | Description |
|-------------------|-------|-------------|
| < AI threshold (50) | AI-like | Below AI baseline, unusually uniform |
| < 0.7 * mean | Low variance | Below mean, consistent style |
| < 1.3 * mean | Typical | Near mean, normal variation |
| < spike threshold | Elevated | Above mean, notable variation |
| >= spike threshold | Spike | Significant stylistic change |

### Interpretation

The interactive timeline enables exploration at multiple levels:

1. **Pattern overview**: The overall shape of the line reveals the classified pattern (flat=consistent, trending=drift, peaked=spike, flat-low=uniform)
2. **Point inspection**: Clicking a point shows the comparison details, deviation from mean, and percentile ranking
3. **Chunk comparison**: When chunk text is provided, the bottom panel shows the actual text content of both chunks in a comparison, enabling direct reading of the stylistic boundary
4. **Parameter review**: The stats panel shows all analysis parameters and results for reproducibility

---

## Implementation

### Core Algorithm

The export function transforms a `KilgarriffDriftResult` into a self-contained HTML file:

1. **Data extraction**: Extract chi-squared values, compute z-scores and distances for color encoding
2. **Configuration building**: Package all data, thresholds, and statistics into a JSON configuration object
3. **React component generation**: Generate JSX code for the interactive timeline component
4. **HTML assembly**: Combine React CDN links, Babel transpiler, configuration data, and component code into a single HTML file
5. **File writing**: Write the complete HTML file to disk

The generated HTML includes:
- React 18 via CDN (unpkg.com)
- Babel standalone transpiler for JSX
- Inline CSS styles
- Configuration data as a JavaScript object
- React component with SVG-based chart rendering

### Key Features

- **Self-contained HTML**: Single file, no build step, no server required. Opens directly in any browser.
- **Interactive line chart**: SVG-based rendering with smooth transitions and responsive interactions
- **Hover details**: Mouse over any point to see chi-squared value and distance from mean
- **Click to select**: Click a point to pin it and view detailed comparison analysis
- **Keyboard navigation**: Use arrow keys to navigate between points; Escape to deselect
- **Chunk text display**: When chunks are provided, shows the full text content of both chunks in a selected comparison, with a carousel middle panel for Analysis, Parameters, and Top Contributors
- **Reference threshold lines**: Visual indicators for mean, AI baseline, and spike threshold
- **Color-coded points**: Green-yellow-red gradient based on z-score distance from mean
- **Stats panel**: Complete analysis results including pattern, confidence, chi-squared statistics, parameters, and thresholds

### Dependencies

No additional Python dependencies required. The generated HTML uses React via CDN.

---

## Usage

### API Examples

```python
from pystylometry.consistency import compute_kilgarriff_drift
from pystylometry.viz.jsx import export_drift_timeline_jsx

# Basic timeline export
result = compute_kilgarriff_drift(text)
export_drift_timeline_jsx(result, "timeline.html")

# Custom title
export_drift_timeline_jsx(
    result,
    "analysis.html",
    title="Chapter 5 Style Analysis",
)

# Include chunk text for comparison view
# First, chunk the text manually to provide readable chunks
from pystylometry._types import chunk_text
chunks = chunk_text(text, chunk_size=1000)

export_drift_timeline_jsx(
    result,
    "detailed_timeline.html",
    title="Detailed Analysis with Chunk Text",
    chunks=chunks,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `result` | `KilgarriffDriftResult` | (required) | Drift detection result from `compute_kilgarriff_drift()` |
| `output_file` | `str \| Path` | (required) | Path to write the HTML file |
| `title` | `str` | `"Stylistic Drift Timeline"` | Chart title |
| `chunks` | `list[str] \| None` | `None` | Optional list of chunk text content for hover/click display |

### Return Value

Returns a `Path` object pointing to the generated HTML file.

### Raises

- `ValueError`: If fewer than 2 window comparisons are available in the result

---

## Limitations

### Browser Dependency

The generated HTML requires a modern browser with JavaScript enabled. React is loaded via CDN, so an internet connection is needed on first open (browsers typically cache the CDN scripts).

### SVG Rendering

The chart is rendered as SVG with fixed dimensions (750x400 pixels). Very large numbers of data points (100+) may produce a crowded chart. For documents producing many window comparisons, consider using larger window sizes to reduce the number of points.

### Babel Transpilation

The HTML uses Babel standalone to transpile JSX in the browser. This adds a brief delay on page load (typically under 1 second). For production deployments, consider pre-building the JavaScript.

### Chunk Text Size

When providing chunk text, the data is embedded directly in the HTML file. Very large documents will produce large HTML files. For documents over 100,000 words, consider omitting the `chunks` parameter.

---

## References

Kilgarriff, Adam. "Comparing Corpora." *International Journal of Corpus Linguistics*, vol. 6, no. 1, 2001, pp. 97-133.

Shneiderman, Ben. "The Eyes Have It: A Task by Data Type Taxonomy for Information Visualizations." *Proceedings of the IEEE Symposium on Visual Languages*, 1996, pp. 336-343.

# Standalone Drift Viewer

## Browser-Based Style Drift Analyzer with Client-Side Kilgarriff Chi-Squared

---

## Theoretical Background

### Origins

The standalone drift viewer addresses a practical deployment challenge: how to enable stylistic drift analysis for users who do not have Python installed. By implementing Kilgarriff's chi-squared method entirely in JavaScript and packaging it with a React-based user interface, the viewer creates a single HTML file that anyone can use to analyze their own text files.

This approach follows the principle of progressive disclosure: the viewer presents a simple drag-and-drop interface for initial use, configurable parameters for advanced users, and detailed interactive results for in-depth analysis. The client-side implementation ensures that text data never leaves the user's browser, which is important for confidential documents.

### Mathematical Foundation

The JavaScript implementation mirrors the Python implementation of Kilgarriff's chi-squared method:

1. **Tokenization**: Split on whitespace, filter to alphabetic tokens, lowercase
2. **Window creation**: Sliding windows with configurable size and stride
3. **Frequency counting**: Per-window word frequency dictionaries
4. **Top N words**: Extract the N most frequent words from all windows combined
5. **Chi-squared computation**: For each consecutive window pair, compute chi-squared over the top N words

```javascript
chi_squared = SUM over top_words:
    (O1 - E1)^2 / E1 + (O2 - E2)^2 / E2

where:
    E1 = (O1 + O2) * total1 / (total1 + total2)
    E2 = (O1 + O2) * total2 / (total1 + total2)
```

6. **Statistics**: Mean, standard deviation, min, max, CV, trend (linear regression slope)
7. **Pattern classification**: Using simplified thresholds matching the Python implementation

**Client-side pattern classification**:

| Condition | Pattern |
|-----------|---------|
| CV < 0.15 and mean < 50 | `suspiciously_uniform` |
| max > mean + 2*std and max > 2*mean | `sudden_spike` |
| abs(trend) > std * 0.1 | `gradual_drift` |
| Otherwise | `consistent` |

### Interpretation

The viewer produces the same types of analysis as the Python API:

- **Pattern detection**: Identifies consistent, gradual drift, sudden spike, or suspiciously uniform patterns
- **Timeline visualization**: Interactive line chart with color-coded points and reference thresholds
- **Chunk comparison**: Click any point to view the actual text content of both chunks being compared
- **Statistical summary**: Complete chi-squared statistics, parameters, and thresholds

The key difference from the Python implementation is that all computation happens in the browser. Results may differ slightly from the Python version due to tokenization differences (the JavaScript implementation uses simple whitespace splitting rather than pystylometry's tokenizer).

---

## Implementation

### Core Algorithm

The viewer is a single HTML file containing:

1. **React application** (via CDN): Manages UI state and component rendering
2. **Babel transpiler** (via CDN): Enables JSX syntax in the browser
3. **Kilgarriff chi-squared** (inline JavaScript): Complete client-side implementation
4. **File handling** (FileReader API): Reads uploaded text files without server interaction

The application has three states:

**Upload state**: Displays a drag-and-drop zone with configurable parameters (window size, stride, top N words). Shows computed overlap percentage based on current parameter settings.

**Processing state**: Displays a spinner while analysis runs. Analysis is executed via `setTimeout` to avoid blocking the UI thread.

**Results state**: Displays the interactive timeline chart, stats panel, and chunk comparison view. The timeline reuses the same SVG-based chart design as the pre-computed timeline export.

### Key Features

- **Self-contained HTML**: Single file containing all JavaScript, CSS, and logic. No build tools, no server, no Python required.
- **Drag-and-drop upload**: Drag a `.txt` file onto the drop zone, or click to browse. The FileReader API reads the file content client-side.
- **Configurable parameters**: Window size (100-5000 tokens), stride (50-2500 tokens), and top N words (50-1000) are configurable before file upload. Overlap percentage is computed and displayed in real time.
- **Auto-analysis**: Analysis begins automatically when a file is uploaded, providing immediate results.
- **Interactive timeline**: Same hover, click, and keyboard navigation as the pre-computed timeline export.
- **Chunk text display**: Click any point to view the actual text content of the two chunks being compared, with comparison analysis showing chi-squared, deviation, and percentile.
- **Privacy**: All computation happens client-side. No data is transmitted to any server.
- **Reset capability**: "New File" button returns to the upload state for analyzing additional files.

### Dependencies

No Python dependencies required to use the viewer. The HTML file loads React and Babel from CDN on first open.

To generate the viewer file, only pystylometry core is needed (no matplotlib or seaborn):

```bash
pip install pystylometry
```

---

## Usage

### API Examples

```python
from pystylometry.viz.jsx import export_drift_viewer

# Generate the standalone viewer
export_drift_viewer("drift_analyzer.html")

# Custom title
export_drift_viewer(
    "my_analyzer.html",
    title="Manuscript Style Checker",
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_file` | `str \| Path` | (required) | Path to write the HTML file |
| `title` | `str` | `"Stylistic Drift Analyzer"` | Page title displayed in the header |

### Return Value

Returns a `Path` object pointing to the generated HTML file.

### Using the Generated Viewer

1. Open the generated HTML file in any modern browser
2. (Optional) Adjust analysis parameters:
   - **Window Size**: Number of tokens per analysis window (default: 1000)
   - **Stride**: Token offset between consecutive windows (default: 500)
   - **Top N Words**: Most frequent words to use in chi-squared (default: 500)
3. Drag and drop a `.txt` file onto the upload zone, or click to browse
4. Analysis runs automatically; results appear within seconds
5. Explore the interactive timeline:
   - Hover over points for chi-squared values
   - Click a point to view the chunk text comparison
   - Review the stats panel for pattern classification and confidence
6. Click "New File" to analyze another document

### Sharing the Viewer

The generated HTML file can be shared with anyone. Recipients need only a modern browser to use it. The file is typically 30-50 KB in size, making it easy to email or post on internal wikis.

---

## Limitations

### Tokenization Differences

The JavaScript tokenizer uses simple whitespace splitting with an alphabetic filter, while the Python implementation uses pystylometry's standard tokenizer. This may cause minor differences in chi-squared values between the viewer and the Python API, particularly for texts with complex punctuation, hyphenation, or contractions.

### File Format

The viewer only accepts plain text (`.txt`) files. Other formats (PDF, DOCX, HTML) must be converted to plain text before uploading.

### Browser Performance

Client-side computation is slower than Python for very large texts. Documents over 500,000 words may take several seconds to analyze. The UI displays a spinner during processing.

### CDN Dependency

React and Babel are loaded from unpkg.com CDN. An internet connection is required on first open. After initial load, browsers typically cache these resources.

### Simplified Pattern Classification

The JavaScript pattern classification uses simplified thresholds compared to the Python implementation. While results are generally consistent, edge cases near threshold boundaries may be classified differently.

### No Export

The viewer displays results in-browser but does not provide options to export the analysis data (e.g., as JSON or CSV). For programmatic access to results, use the Python API directly.

---

## References

Kilgarriff, Adam. "Comparing Corpora." *International Journal of Corpus Linguistics*, vol. 6, no. 1, 2001, pp. 97-133.

Shneiderman, Ben. "The Eyes Have It: A Task by Data Type Taxonomy for Information Visualizations." *Proceedings of the IEEE Symposium on Visual Languages*, 1996, pp. 336-343.

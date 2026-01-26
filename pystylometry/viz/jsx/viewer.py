"""Standalone interactive viewer for Kilgarriff drift detection.

Creates a self-contained HTML file that:
- Accepts text file uploads
- Performs Kilgarriff chi-squared analysis client-side
- Displays interactive timeline visualization
- Can be shared and used without Python installed
"""

from __future__ import annotations

from pathlib import Path

from ._base import write_html_file


def export_drift_viewer(
    output_file: str | Path,
    title: str = "Stylistic Drift Analyzer",
) -> Path:
    """
    Export a standalone drift analysis viewer as HTML.

    Creates a self-contained HTML file that users can open in any browser
    to analyze their own text files. No Python or server required.

    Features:
    - Drag-and-drop or click to upload text files
    - Configurable analysis parameters
    - Interactive timeline visualization
    - Client-side Kilgarriff chi-squared implementation

    Args:
        output_file: Path to write the HTML file
        title: Page title

    Returns:
        Path to the generated HTML file

    Example:
        >>> export_drift_viewer("drift_analyzer.html")
        # Share drift_analyzer.html with anyone - they can analyze their own texts
    """
    html_content = _generate_viewer_html(title)
    return write_html_file(output_file, html_content)


def _generate_viewer_html(title: str) -> str:
    """Generate the complete HTML for the standalone viewer."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            background: #f8fafc;
            min-height: 100vh;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 12px;
        }}
        .card-title {{
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 12px;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            font-size: 12px;
        }}
        .stat-label {{ color: #6b7280; }}
        .stat-value {{ font-weight: 500; color: #1f2937; font-family: monospace; }}
        .dropzone {{
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 60px 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            background: white;
        }}
        .dropzone:hover, .dropzone.dragover {{
            border-color: #2563eb;
            background: #eff6ff;
        }}
        .dropzone-icon {{
            font-size: 48px;
            margin-bottom: 16px;
        }}
        .dropzone-text {{
            font-size: 16px;
            color: #4b5563;
            margin-bottom: 8px;
        }}
        .dropzone-subtext {{
            font-size: 13px;
            color: #9ca3af;
        }}
        .param-group {{
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}
        .param-item {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .param-label {{
            font-size: 11px;
            color: #6b7280;
            font-weight: 500;
        }}
        .param-input {{
            padding: 6px 10px;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            font-size: 13px;
            width: 120px;
        }}
        .param-input:focus {{
            outline: none;
            border-color: #2563eb;
        }}
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .btn-primary {{
            background: #2563eb;
            color: white;
        }}
        .btn-primary:hover {{
            background: #1d4ed8;
        }}
        .btn-secondary {{
            background: #f1f5f9;
            color: #475569;
        }}
        .btn-secondary:hover {{
            background: #e2e8f0;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 20px;
            font-weight: 600;
            color: #1f2937;
        }}
        .file-info {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: #f0fdf4;
            border-radius: 8px;
            margin-bottom: 16px;
        }}
        .file-info-icon {{
            font-size: 24px;
        }}
        .file-info-details {{
            flex: 1;
        }}
        .file-info-name {{
            font-weight: 500;
            color: #166534;
        }}
        .file-info-stats {{
            font-size: 12px;
            color: #4ade80;
        }}
        .processing {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 40px;
            color: #6b7280;
        }}
        .spinner {{
            width: 24px;
            height: 24px;
            border: 3px solid #e2e8f0;
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
{_get_viewer_component()}
    </script>
</body>
</html>"""


def _get_viewer_component() -> str:
    """Return the React component for the viewer."""
    return """
    // Color interpolation for data points
    function getPointColor(distance) {
        const green = [34, 197, 94];
        const yellow = [234, 179, 8];
        const red = [239, 68, 68];

        let r, g, b;
        if (distance < 0.5) {
            const t = distance * 2;
            r = Math.round(green[0] + (yellow[0] - green[0]) * t);
            g = Math.round(green[1] + (yellow[1] - green[1]) * t);
            b = Math.round(green[2] + (yellow[2] - green[2]) * t);
        } else {
            const t = (distance - 0.5) * 2;
            r = Math.round(yellow[0] + (red[0] - yellow[0]) * t);
            g = Math.round(yellow[1] + (red[1] - yellow[1]) * t);
            b = Math.round(yellow[2] + (red[2] - yellow[2]) * t);
        }
        return `rgb(${r}, ${g}, ${b})`;
    }

    // Kilgarriff chi-squared implementation
    function computeKilgarriffDrift(text, windowSize, stride, nWords) {
        // Tokenize: split on whitespace, keep only alphabetic tokens
        const tokens = text.split(/\\s+/).filter(t => /^[a-zA-Z]+$/.test(t)).map(t => t.toLowerCase());

        if (tokens.length < windowSize * 2) {
            return { error: `Text too short. Need at least ${windowSize * 2} words, got ${tokens.length}.` };
        }

        // Create windows
        const windows = [];
        let start = 0;
        while (start + windowSize <= tokens.length) {
            windows.push(tokens.slice(start, start + windowSize));
            start += stride;
        }

        if (windows.length < 3) {
            return { error: `Not enough windows. Got ${windows.length}, need at least 3.` };
        }

        // Get word frequencies for each window
        function getFrequencies(window) {
            const freq = {};
            for (const word of window) {
                freq[word] = (freq[word] || 0) + 1;
            }
            return freq;
        }

        // Get top N words from combined corpus
        const allFreq = {};
        for (const w of windows) {
            for (const word of w) {
                allFreq[word] = (allFreq[word] || 0) + 1;
            }
        }
        const sortedWords = Object.entries(allFreq)
            .sort((a, b) => b[1] - a[1])
            .slice(0, nWords)
            .map(e => e[0]);

        // Compute chi-squared between consecutive windows
        function chiSquared(freq1, freq2, topWords) {
            let chi = 0;
            const total1 = Object.values(freq1).reduce((a, b) => a + b, 0);
            const total2 = Object.values(freq2).reduce((a, b) => a + b, 0);

            for (const word of topWords) {
                const o1 = freq1[word] || 0;
                const o2 = freq2[word] || 0;
                const total = o1 + o2;
                if (total === 0) continue;

                const e1 = total * (total1 / (total1 + total2));
                const e2 = total * (total2 / (total1 + total2));

                if (e1 > 0) chi += Math.pow(o1 - e1, 2) / e1;
                if (e2 > 0) chi += Math.pow(o2 - e2, 2) / e2;
            }
            return chi;
        }

        // Compute pairwise scores
        const windowFreqs = windows.map(getFrequencies);
        const pairwiseScores = [];
        for (let i = 0; i < windows.length - 1; i++) {
            const chi = chiSquared(windowFreqs[i], windowFreqs[i + 1], sortedWords);
            pairwiseScores.push({ index: i, chi_squared: chi });
        }

        // Compute statistics
        const chiValues = pairwiseScores.map(p => p.chi_squared);
        const meanChi = chiValues.reduce((a, b) => a + b, 0) / chiValues.length;
        const variance = chiValues.reduce((a, b) => a + Math.pow(b - meanChi, 2), 0) / chiValues.length;
        const stdChi = Math.sqrt(variance);
        const minChi = Math.min(...chiValues);
        const maxChi = Math.max(...chiValues);
        const maxLocation = chiValues.indexOf(maxChi);

        // Compute trend (linear regression slope)
        const n = chiValues.length;
        const sumX = (n * (n - 1)) / 2;
        const sumY = chiValues.reduce((a, b) => a + b, 0);
        const sumXY = chiValues.reduce((a, y, i) => a + i * y, 0);
        const sumX2 = (n * (n - 1) * (2 * n - 1)) / 6;
        const trend = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);

        // Detect pattern
        const cv = meanChi > 0 ? stdChi / meanChi : 0;
        const spikeThreshold = meanChi + 2 * stdChi;
        const hasSpike = maxChi > spikeThreshold && maxChi > meanChi * 2;

        let pattern, confidence;
        if (cv < 0.15 && meanChi < 50) {
            pattern = "suspiciously_uniform";
            confidence = 1 - cv / 0.15;
        } else if (hasSpike) {
            pattern = "sudden_spike";
            confidence = Math.min(1, (maxChi - spikeThreshold) / spikeThreshold);
        } else if (Math.abs(trend) > stdChi * 0.1) {
            pattern = "gradual_drift";
            confidence = Math.min(1, Math.abs(trend) / (stdChi * 0.2));
        } else {
            pattern = "consistent";
            confidence = 1 - cv;
        }

        // Build chunk texts
        const chunks = windows.map(w => w.join(" "));

        return {
            pairwiseScores,
            chunks,
            stats: {
                pattern,
                confidence: Math.max(0, Math.min(1, confidence)),
                meanChi,
                stdChi,
                minChi,
                maxChi,
                cv,
                maxLocation,
                windowCount: windows.length,
                windowSize,
                stride,
                overlapRatio: (windowSize - stride) / windowSize,
                trend,
                comparisons: pairwiseScores.length,
            },
            thresholds: {
                mean: meanChi,
                spike: spikeThreshold,
                ai: 50,
            }
        };
    }

    function DriftViewer() {
        const [file, setFile] = React.useState(null);
        const [text, setText] = React.useState("");
        const [params, setParams] = React.useState({
            windowSize: 1000,
            stride: 500,
            nWords: 500,
        });
        const [result, setResult] = React.useState(null);
        const [error, setError] = React.useState(null);
        const [processing, setProcessing] = React.useState(false);
        const [dragOver, setDragOver] = React.useState(false);

        const fileInputRef = React.useRef(null);

        const handleFile = (f) => {
            if (!f) return;
            setFile(f);
            setError(null);
            setResult(null);

            const reader = new FileReader();
            reader.onload = (e) => {
                setText(e.target.result);
            };
            reader.onerror = () => {
                setError("Failed to read file");
            };
            reader.readAsText(f);
        };

        const handleDrop = (e) => {
            e.preventDefault();
            setDragOver(false);
            const f = e.dataTransfer.files[0];
            if (f && f.type === "text/plain") {
                handleFile(f);
            } else {
                setError("Please drop a .txt file");
            }
        };

        const runAnalysis = () => {
            if (!text) return;
            setProcessing(true);
            setError(null);

            // Use setTimeout to allow UI to update
            setTimeout(() => {
                const r = computeKilgarriffDrift(text, params.windowSize, params.stride, params.nWords);
                setProcessing(false);
                if (r.error) {
                    setError(r.error);
                } else {
                    setResult(r);
                }
            }, 50);
        };

        const reset = () => {
            setFile(null);
            setText("");
            setResult(null);
            setError(null);
        };

        // Auto-run analysis when text is loaded
        React.useEffect(() => {
            if (text && text.length > 0) {
                runAnalysis();
            }
        }, [text]);

        if (processing) {
            return (
                <div style={{ maxWidth: 800, margin: "0 auto" }}>
                    <div className="header">
                        <h1>Stylistic Drift Analyzer</h1>
                    </div>
                    <div className="card">
                        <div className="processing">
                            <div className="spinner"></div>
                            <span>Analyzing text...</span>
                        </div>
                    </div>
                </div>
            );
        }

        if (!file) {
            return (
                <div style={{ maxWidth: 600, margin: "0 auto" }}>
                    <div className="header">
                        <h1>Stylistic Drift Analyzer</h1>
                    </div>

                    <div className="card" style={{ marginBottom: 16 }}>
                        <div className="param-group">
                            <div className="param-item">
                                <label className="param-label">Window Size (tokens)</label>
                                <input
                                    type="number"
                                    className="param-input"
                                    value={params.windowSize}
                                    onChange={(e) => setParams({...params, windowSize: parseInt(e.target.value) || 1000})}
                                    min={100}
                                    max={5000}
                                />
                            </div>
                            <div className="param-item">
                                <label className="param-label">Stride (tokens)</label>
                                <input
                                    type="number"
                                    className="param-input"
                                    value={params.stride}
                                    onChange={(e) => setParams({...params, stride: parseInt(e.target.value) || 500})}
                                    min={50}
                                    max={2500}
                                />
                            </div>
                            <div className="param-item">
                                <label className="param-label">Top N Words</label>
                                <input
                                    type="number"
                                    className="param-input"
                                    value={params.nWords}
                                    onChange={(e) => setParams({...params, nWords: parseInt(e.target.value) || 500})}
                                    min={50}
                                    max={1000}
                                />
                            </div>
                        </div>
                        <div style={{ fontSize: 11, color: "#9ca3af" }}>
                            Overlap: {((params.windowSize - params.stride) / params.windowSize * 100).toFixed(0)}%
                        </div>
                    </div>

                    <div
                        className={`dropzone ${dragOver ? "dragover" : ""}`}
                        onClick={() => fileInputRef.current?.click()}
                        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                        onDragLeave={() => setDragOver(false)}
                        onDrop={handleDrop}
                    >
                        <div className="dropzone-icon">📄</div>
                        <div className="dropzone-text">Drop a text file here or click to browse</div>
                        <div className="dropzone-subtext">Supports .txt files</div>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".txt,text/plain"
                            style={{ display: "none" }}
                            onChange={(e) => handleFile(e.target.files?.[0])}
                        />
                    </div>

                    {error && (
                        <div style={{ marginTop: 16, padding: 12, background: "#fef2f2", borderRadius: 8, color: "#dc2626", fontSize: 13 }}>
                            {error}
                        </div>
                    )}

                    <div style={{ marginTop: 24, textAlign: "center", fontSize: 11, color: "#9ca3af" }}>
                        Powered by Kilgarriff Chi-Squared Analysis • Generated by pystylometry
                    </div>
                </div>
            );
        }

        if (!result) {
            return (
                <div style={{ maxWidth: 600, margin: "0 auto" }}>
                    <div className="header">
                        <h1>Stylistic Drift Analyzer</h1>
                        <button className="btn btn-secondary" onClick={reset}>← New File</button>
                    </div>

                    <div className="file-info">
                        <div className="file-info-icon">📄</div>
                        <div className="file-info-details">
                            <div className="file-info-name">{file.name}</div>
                            <div className="file-info-stats">{text.split(/\\s+/).length.toLocaleString()} words</div>
                        </div>
                    </div>

                    {error && (
                        <div style={{ padding: 12, background: "#fef2f2", borderRadius: 8, color: "#dc2626", fontSize: 13 }}>
                            {error}
                        </div>
                    )}
                </div>
            );
        }

        return <ResultsView file={file} result={result} params={params} onReset={reset} />;
    }

    function ResultsView({ file, result, params, onReset }) {
        const [hoveredIndex, setHoveredIndex] = React.useState(null);
        const [selectedIndex, setSelectedIndex] = React.useState(null);

        const { pairwiseScores, chunks, stats, thresholds } = result;

        // Build points data
        const points = pairwiseScores.map((p, i) => {
            const zScore = stats.stdChi > 0 ? Math.abs(p.chi_squared - stats.meanChi) / stats.stdChi : 0;
            const distance = Math.min(1, zScore / 3);
            return {
                index: i,
                chi: p.chi_squared,
                distance,
                window_pair: `${i} → ${i + 1}`,
                chunkA: chunks[i],
                chunkB: chunks[i + 1],
            };
        });

        // SVG dimensions
        const width = 750;
        const height = 400;
        const padding = { top: 40, right: 30, bottom: 50, left: 70 };
        const plotWidth = width - padding.left - padding.right;
        const plotHeight = height - padding.top - padding.bottom;

        // Bounds
        const yMin = 0;
        const yMax = Math.max(...points.map(p => p.chi)) * 1.15;
        const xMax = points.length - 1;

        // Scale functions
        const scaleX = (idx) => padding.left + (idx / xMax) * plotWidth;
        const scaleY = (chi) => padding.top + plotHeight - ((chi - yMin) / (yMax - yMin)) * plotHeight;

        // Active state
        const activeIndex = selectedIndex !== null ? selectedIndex : hoveredIndex;
        const activePoint = activeIndex !== null ? points[activeIndex] : null;
        const isSelected = selectedIndex !== null;
        const selectedPoint = selectedIndex !== null ? points[selectedIndex] : null;

        const handlePointClick = (i) => {
            setSelectedIndex(selectedIndex === i ? null : i);
        };

        // Build paths
        const linePath = points.map((p, i) =>
            `${i === 0 ? "M" : "L"} ${scaleX(p.index)} ${scaleY(p.chi)}`
        ).join(" ");

        const fillPath = linePath +
            ` L ${scaleX(points[points.length - 1].index)} ${scaleY(0)}` +
            ` L ${scaleX(0)} ${scaleY(0)} Z`;

        // Classification helper
        const getClassification = (chi) => {
            if (chi < thresholds.ai) return { label: "AI-like", color: "#f59e0b", desc: "Below AI baseline - unusually uniform" };
            if (chi < thresholds.mean * 0.7) return { label: "Low variance", color: "#10b981", desc: "Below mean - consistent style" };
            if (chi < thresholds.mean * 1.3) return { label: "Typical", color: "#6b7280", desc: "Near mean - normal variation" };
            if (chi < thresholds.spike) return { label: "Elevated", color: "#f97316", desc: "Above mean - notable variation" };
            return { label: "Spike", color: "#dc2626", desc: "Above spike threshold - significant change" };
        };

        return (
            <div style={{ maxWidth: width + 310, margin: "0 auto" }}>
                <div className="header">
                    <h1>Stylistic Drift Analyzer</h1>
                    <button className="btn btn-secondary" onClick={onReset}>← New File</button>
                </div>

                <div className="file-info">
                    <div className="file-info-icon">📄</div>
                    <div className="file-info-details">
                        <div className="file-info-name">{file.name}</div>
                        <div className="file-info-stats">
                            {stats.windowCount} windows • {stats.comparisons} comparisons
                        </div>
                    </div>
                </div>

                {/* Top row: Chart + Stats */}
                <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
                    {/* Chart */}
                    <svg width={width} height={height} style={{ background: "white", borderRadius: 8, boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
                        {/* Title */}
                        <text x={width / 2} y={20} textAnchor="middle" fontSize={14} fontWeight="500">
                            Drift Timeline: {file.name}
                        </text>

                        {/* Fill under curve */}
                        <path d={fillPath} fill="#dbeafe" opacity={0.4} />

                        {/* Mean line */}
                        <line
                            x1={padding.left}
                            y1={scaleY(thresholds.mean)}
                            x2={width - padding.right}
                            y2={scaleY(thresholds.mean)}
                            stroke="#6b7280"
                            strokeWidth={1}
                            opacity={0.6}
                        />
                        <text
                            x={width - padding.right + 5}
                            y={scaleY(thresholds.mean)}
                            fontSize={10}
                            fill="#6b7280"
                            dominantBaseline="middle"
                        >μ</text>

                        {/* AI threshold */}
                        {thresholds.ai < yMax && (
                            <>
                                <line
                                    x1={padding.left}
                                    y1={scaleY(thresholds.ai)}
                                    x2={width - padding.right}
                                    y2={scaleY(thresholds.ai)}
                                    stroke="#f59e0b"
                                    strokeWidth={1}
                                    strokeDasharray="4,4"
                                    opacity={0.6}
                                />
                                <text
                                    x={padding.left - 5}
                                    y={scaleY(thresholds.ai)}
                                    fontSize={10}
                                    fill="#f59e0b"
                                    textAnchor="end"
                                    dominantBaseline="middle"
                                >AI</text>
                            </>
                        )}

                        {/* Spike threshold */}
                        {thresholds.spike < yMax && (
                            <>
                                <line
                                    x1={padding.left}
                                    y1={scaleY(thresholds.spike)}
                                    x2={width - padding.right}
                                    y2={scaleY(thresholds.spike)}
                                    stroke="#10b981"
                                    strokeWidth={1}
                                    strokeDasharray="4,4"
                                    opacity={0.6}
                                />
                                <text
                                    x={padding.left - 5}
                                    y={scaleY(thresholds.spike)}
                                    fontSize={10}
                                    fill="#10b981"
                                    textAnchor="end"
                                    dominantBaseline="middle"
                                >μ+2σ</text>
                            </>
                        )}

                        {/* Max location line */}
                        {stats.maxLocation !== null && (
                            <line
                                x1={scaleX(stats.maxLocation)}
                                y1={padding.top}
                                x2={scaleX(stats.maxLocation)}
                                y2={height - padding.bottom}
                                stroke="#dc2626"
                                strokeWidth={2}
                                strokeDasharray="6,4"
                                opacity={0.5}
                            />
                        )}

                        {/* Main line */}
                        <path
                            d={linePath}
                            fill="none"
                            stroke="#2563eb"
                            strokeWidth={2}
                            strokeLinejoin="round"
                        />

                        {/* Data points */}
                        {points.map((point, i) => {
                            const isActive = activeIndex === i;
                            const isPinned = selectedIndex === i;
                            return (
                                <circle
                                    key={i}
                                    cx={scaleX(point.index)}
                                    cy={scaleY(point.chi)}
                                    r={isActive ? 7 : 5}
                                    fill={getPointColor(point.distance)}
                                    stroke={isPinned ? "#dc2626" : isActive ? "#1f2937" : "white"}
                                    strokeWidth={isPinned ? 3 : isActive ? 2 : 1.5}
                                    style={{ cursor: "pointer", transition: "all 0.15s ease" }}
                                    onMouseEnter={() => setHoveredIndex(i)}
                                    onMouseLeave={() => setHoveredIndex(null)}
                                    onClick={() => handlePointClick(i)}
                                />
                            );
                        })}

                        {/* X-axis */}
                        <line
                            x1={padding.left}
                            y1={height - padding.bottom}
                            x2={width - padding.right}
                            y2={height - padding.bottom}
                            stroke="#374151"
                        />
                        <text x={width / 2} y={height - 10} textAnchor="middle" fontSize={12}>
                            Window Pair Index
                        </text>

                        {/* Y-axis */}
                        <line
                            x1={padding.left}
                            y1={padding.top}
                            x2={padding.left}
                            y2={height - padding.bottom}
                            stroke="#374151"
                        />
                        <text
                            x={20}
                            y={height / 2}
                            textAnchor="middle"
                            fontSize={12}
                            transform={`rotate(-90, 20, ${height / 2})`}
                        >
                            Chi-squared (χ²)
                        </text>

                        {/* Y-axis ticks */}
                        {[0, 0.25, 0.5, 0.75, 1].map((t) => {
                            const val = yMin + t * (yMax - yMin);
                            return (
                                <text
                                    key={t}
                                    x={padding.left - 8}
                                    y={scaleY(val)}
                                    textAnchor="end"
                                    fontSize={10}
                                    fill="#6b7280"
                                    dominantBaseline="middle"
                                >
                                    {val.toFixed(0)}
                                </text>
                            );
                        })}
                    </svg>

                    {/* Stats panel */}
                    <div className="card" style={{ width: 280, height: height, overflowY: "auto" }}>
                        <h3 className="card-title">Analysis Results</h3>
                        <div className="stat-row">
                            <span className="stat-label">Pattern:</span>
                            <span className="stat-value">{stats.pattern.replace("_", " ")}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Confidence:</span>
                            <span className="stat-value">{(stats.confidence * 100).toFixed(1)}%</span>
                        </div>
                        <hr style={{ margin: "10px 0", border: "none", borderTop: "1px solid #e2e8f0" }} />
                        <div style={{ fontSize: 11, fontWeight: 500, color: "#6b7280", marginBottom: 6 }}>CHI-SQUARED STATISTICS</div>
                        <div className="stat-row">
                            <span className="stat-label">Mean χ²:</span>
                            <span className="stat-value">{stats.meanChi.toFixed(2)}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Std χ²:</span>
                            <span className="stat-value">{stats.stdChi.toFixed(2)}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">CV:</span>
                            <span className="stat-value">{stats.cv.toFixed(4)}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Range:</span>
                            <span className="stat-value">{stats.minChi.toFixed(1)} – {stats.maxChi.toFixed(1)}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Trend:</span>
                            <span className="stat-value">{stats.trend >= 0 ? "+" : ""}{stats.trend.toFixed(4)}</span>
                        </div>
                        {stats.maxLocation !== null && (
                            <div className="stat-row">
                                <span className="stat-label">Max at:</span>
                                <span className="stat-value">Window {stats.maxLocation}</span>
                            </div>
                        )}
                        <hr style={{ margin: "10px 0", border: "none", borderTop: "1px solid #e2e8f0" }} />
                        <div style={{ fontSize: 11, fontWeight: 500, color: "#6b7280", marginBottom: 6 }}>PARAMETERS</div>
                        <div className="stat-row">
                            <span className="stat-label">Window size:</span>
                            <span className="stat-value">{stats.windowSize} tokens</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Stride:</span>
                            <span className="stat-value">{stats.stride} tokens</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Overlap:</span>
                            <span className="stat-value">{(stats.overlapRatio * 100).toFixed(0)}%</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Windows:</span>
                            <span className="stat-value">{stats.windowCount}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Comparisons:</span>
                            <span className="stat-value">{stats.comparisons}</span>
                        </div>
                        <hr style={{ margin: "10px 0", border: "none", borderTop: "1px solid #e2e8f0" }} />
                        <div style={{ fontSize: 11, fontWeight: 500, color: "#6b7280", marginBottom: 6 }}>THRESHOLDS</div>
                        <div className="stat-row">
                            <span className="stat-label">AI baseline:</span>
                            <span className="stat-value">{thresholds.ai}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Mean (μ):</span>
                            <span className="stat-value">{thresholds.mean.toFixed(2)}</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">Spike (μ+2σ):</span>
                            <span className="stat-value">{thresholds.spike.toFixed(2)}</span>
                        </div>

                        {!selectedPoint && (
                            <p style={{ marginTop: 10, fontSize: 11, color: "#9ca3af" }}>
                                Click a point to view comparison details
                            </p>
                        )}
                    </div>
                </div>

                {/* Bottom row: 3 panels when point selected */}
                {selectedPoint && (() => {
                    const classification = getClassification(selectedPoint.chi);
                    const deviation = (selectedPoint.distance * 3).toFixed(2);
                    const percentile = Math.round((points.filter(p => p.chi <= selectedPoint.chi).length / points.length) * 100);

                    return (
                        <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
                            {/* Chunk A */}
                            <div className="card" style={{ flex: 1, margin: 0, padding: "12px" }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                                    <h3 className="card-title" style={{ margin: 0, fontSize: 13 }}>Chunk {selectedPoint.index}</h3>
                                    <button
                                        onClick={() => setSelectedIndex(null)}
                                        style={{
                                            background: "none",
                                            border: "none",
                                            cursor: "pointer",
                                            fontSize: 14,
                                            color: "#9ca3af",
                                            padding: "0 4px",
                                        }}
                                        title="Close"
                                    >✕</button>
                                </div>
                                <div style={{
                                    padding: 10,
                                    background: "#f8fafc",
                                    borderRadius: 4,
                                    fontSize: 11,
                                    lineHeight: 1.5,
                                    maxHeight: 200,
                                    overflowY: "auto",
                                    whiteSpace: "pre-wrap",
                                    wordBreak: "break-word",
                                    border: "1px solid #e2e8f0",
                                }}>
                                    {selectedPoint.chunkA}
                                </div>
                            </div>

                            {/* Comparison Analysis */}
                            <div className="card" style={{ width: 220, margin: 0, padding: "12px" }}>
                                <h3 className="card-title" style={{ margin: 0, marginBottom: 10, fontSize: 13 }}>Comparison Analysis</h3>
                                <div className="stat-row">
                                    <span className="stat-label">Window pair:</span>
                                    <span className="stat-value">{selectedPoint.window_pair}</span>
                                </div>
                                <div className="stat-row">
                                    <span className="stat-label">Chi-squared:</span>
                                    <span className="stat-value">{selectedPoint.chi.toFixed(2)}</span>
                                </div>
                                <div className="stat-row">
                                    <span className="stat-label">Deviation:</span>
                                    <span className="stat-value">{deviation}σ</span>
                                </div>
                                <div className="stat-row">
                                    <span className="stat-label">Percentile:</span>
                                    <span className="stat-value">{percentile}%</span>
                                </div>
                                <hr style={{ margin: "8px 0", border: "none", borderTop: "1px solid #e2e8f0" }} />
                                <div style={{
                                    padding: "8px 10px",
                                    background: classification.color + "15",
                                    borderRadius: 4,
                                    borderLeft: `3px solid ${classification.color}`
                                }}>
                                    <div style={{ fontWeight: 600, fontSize: 12, color: classification.color, marginBottom: 4 }}>
                                        {classification.label}
                                    </div>
                                    <div style={{ fontSize: 10, color: "#6b7280", lineHeight: 1.4 }}>
                                        {classification.desc}
                                    </div>
                                </div>
                            </div>

                            {/* Chunk B */}
                            {selectedPoint.chunkB && (
                                <div className="card" style={{ flex: 1, margin: 0, padding: "12px" }}>
                                    <h3 className="card-title" style={{ marginBottom: 6, fontSize: 13 }}>Chunk {selectedPoint.index + 1}</h3>
                                    <div style={{
                                        padding: 10,
                                        background: "#f8fafc",
                                        borderRadius: 4,
                                        fontSize: 11,
                                        lineHeight: 1.5,
                                        maxHeight: 200,
                                        overflowY: "auto",
                                        whiteSpace: "pre-wrap",
                                        wordBreak: "break-word",
                                        border: "1px solid #e2e8f0",
                                    }}>
                                        {selectedPoint.chunkB}
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })()}

                <p style={{ marginTop: 16, fontSize: 11, color: "#9ca3af", textAlign: "center" }}>
                    Powered by Kilgarriff Chi-Squared Analysis • Generated by pystylometry
                </p>
            </div>
        );
    }

    const root = ReactDOM.createRoot(document.getElementById("root"));
    root.render(<DriftViewer />);
"""

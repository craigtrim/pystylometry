"""Interactive report visualization for Kilgarriff drift detection.

Creates a multi-panel dashboard with:
- Timeline chart
- Distribution histogram
- Summary statistics
- Zone classification
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ._base import (
    CARD_STYLES,
    COLOR_INTERPOLATION_JS,
    generate_html_document,
    write_html_file,
)

if TYPE_CHECKING:
    from ..._types import KilgarriffDriftResult

# Reference bounds for zone classification
MEAN_CHI_LOW = 100
MEAN_CHI_HIGH = 250
CV_LOW = 0.08
CV_HIGH = 0.20


def export_drift_report_jsx(
    result: "KilgarriffDriftResult",
    output_file: str | Path,
    label: str = "Document",
    title: str | None = None,
    chunks: list[str] | None = None,
) -> Path:
    """
    Export an interactive multi-panel report as a standalone HTML file.

    Creates a self-contained HTML file with React via CDN featuring:
    - Interactive timeline chart with hover details
    - Chi-squared distribution histogram
    - Summary statistics panel
    - Zone classification with visual indicators
    - Top contributing words at spike location

    Args:
        result: KilgarriffDriftResult from compute_kilgarriff_drift()
        output_file: Path to write the HTML file (e.g., "report.html")
        label: Document label for title
        title: Custom title (auto-generated if None)
        chunks: Optional list of chunk text content for hover display

    Returns:
        Path to the generated HTML file

    Example:
        >>> result = compute_kilgarriff_drift(text)
        >>> export_drift_report_jsx(result, "report.html", label="My Document")
    """
    chi_values = [s["chi_squared"] for s in result.pairwise_scores]

    if len(chi_values) < 2:
        raise ValueError("Need at least 2 window comparisons for report")

    # Compute CV
    mean_chi = result.mean_chi_squared
    std_chi = result.std_chi_squared
    cv = std_chi / mean_chi if mean_chi > 0 else 0
    spike_threshold = mean_chi + 2 * std_chi if mean_chi > 0 else 100

    # Build histogram bins
    n_bins = min(15, len(chi_values))
    min_val = min(chi_values)
    max_val = max(chi_values)
    bin_width = (max_val - min_val) / n_bins if max_val > min_val else 1
    bins = [0] * n_bins
    for chi in chi_values:
        bin_idx = min(n_bins - 1, int((chi - min_val) / bin_width))
        bins[bin_idx] += 1

    histogram_data = {
        "bins": bins,
        "binWidth": round(bin_width, 2),
        "minVal": round(min_val, 2),
        "maxVal": round(max_val, 2),
    }

    # Build timeline points
    points_data = []
    for i, chi in enumerate(chi_values):
        if std_chi > 0:
            z_score = abs(chi - mean_chi) / std_chi
            distance = min(1, z_score / 3)
        else:
            distance = 0 if chi == mean_chi else 1

        point = {
            "index": i,
            "chi": round(chi, 2),
            "distance": round(distance, 3),
        }

        # Add chunk text if available
        if chunks:
            if i < len(chunks):
                point["chunkA"] = chunks[i]
            if i + 1 < len(chunks):
                point["chunkB"] = chunks[i + 1]

        points_data.append(point)

    # Get top words at spike if available
    top_words = []
    if result.max_location is not None and result.max_location < len(result.pairwise_scores):
        spike_data = result.pairwise_scores[result.max_location]
        if "top_words" in spike_data and spike_data["top_words"]:
            top_words = [
                {"word": w[0], "contribution": round(w[1], 2)} for w in spike_data["top_words"][:8]
            ]

    # Zone classification
    if mean_chi < MEAN_CHI_LOW:
        baseline_zone = "AI-like"
        baseline_color = "#dc2626"
    elif mean_chi > MEAN_CHI_HIGH:
        baseline_zone = "Human-like"
        baseline_color = "#22c55e"
    else:
        baseline_zone = "Transition"
        baseline_color = "#f59e0b"

    if cv < CV_LOW:
        volatility_zone = "Very stable"
        volatility_color = "#3b82f6"
    elif cv > CV_HIGH:
        volatility_zone = "Volatile"
        volatility_color = "#ef4444"
    else:
        volatility_zone = "Normal"
        volatility_color = "#22c55e"

    display_title = title or f"Drift Analysis Report: {label}"

    config = {
        "title": display_title,
        "label": label,
        "points": points_data,
        "hasChunks": chunks is not None and len(chunks) > 0,
        "histogram": histogram_data,
        "topWords": top_words,
        "thresholds": {
            "mean": round(mean_chi, 2),
            "spike": round(spike_threshold, 2),
        },
        "zones": {
            "baseline": {
                "name": baseline_zone,
                "color": baseline_color,
            },
            "volatility": {
                "name": volatility_zone,
                "color": volatility_color,
            },
        },
        "stats": {
            "pattern": result.pattern,
            "confidence": round(result.pattern_confidence, 3),
            "meanChi": round(mean_chi, 2),
            "stdChi": round(std_chi, 2),
            "minChi": round(result.min_chi_squared, 2),
            "maxChi": round(result.max_chi_squared, 2),
            "cv": round(cv, 4),
            "trend": round(result.trend, 4),
            "maxLocation": result.max_location,
            "windowCount": result.window_count,
            "windowSize": result.window_size,
            "stride": result.stride,
            "overlapRatio": round(result.overlap_ratio, 2),
        },
        "bounds": {
            "MEAN_CHI_LOW": MEAN_CHI_LOW,
            "MEAN_CHI_HIGH": MEAN_CHI_HIGH,
            "CV_LOW": CV_LOW,
            "CV_HIGH": CV_HIGH,
        },
    }

    component = _get_report_component()
    html_content = generate_html_document(
        title=display_title,
        config=config,
        react_component=component,
        component_name="DriftReport",
        extra_styles=CARD_STYLES + _get_report_styles(),
    )

    return write_html_file(output_file, html_content)


def _get_report_styles() -> str:
    """Additional CSS for report layout."""
    return """
    .report-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: auto auto;
      gap: 16px;
    }
    .report-grid .full-width {
      grid-column: 1 / -1;
    }
    .zone-badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      color: white;
    }
    .word-bar {
      display: flex;
      align-items: center;
      margin: 4px 0;
      font-size: 12px;
    }
    .word-label {
      width: 80px;
      font-family: ui-monospace, monospace;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .word-bar-bg {
      flex: 1;
      height: 16px;
      background: #e2e8f0;
      border-radius: 2px;
      margin-left: 8px;
      overflow: hidden;
    }
    .word-bar-fill {
      height: 100%;
      background: #2563eb;
      border-radius: 2px;
    }
"""


def _get_report_component() -> str:
    """Return the React component code for the report visualization."""
    return f"""
    {COLOR_INTERPOLATION_JS}

    function DriftReport() {{
      const [hoveredIndex, setHoveredIndex] = React.useState(null);
      const [selectedIndex, setSelectedIndex] = React.useState(null);

      const {{
        title, points, hasChunks, histogram, topWords, thresholds, zones, stats, bounds
      }} = CONFIG;

      // Active index: selected takes priority, then hovered
      const activeIndex = selectedIndex !== null ? selectedIndex : hoveredIndex;
      const activePoint = activeIndex !== null ? points[activeIndex] : null;
      const isSelected = selectedIndex !== null;
      const selectedPoint = selectedIndex !== null ? points[selectedIndex] : null;

      // Handle click to select/deselect
      const handlePointClick = (i) => {{
        if (selectedIndex === i) {{
          setSelectedIndex(null);
        }} else {{
          setSelectedIndex(i);
        }}
      }};

      // Timeline dimensions
      const timelineWidth = 700;
      const timelineHeight = 220;
      const padding = {{ top: 30, right: 20, bottom: 40, left: 60 }};
      const plotWidth = timelineWidth - padding.left - padding.right;
      const plotHeight = timelineHeight - padding.top - padding.bottom;

      const xMax = points.length - 1;
      const yMax = Math.max(...points.map(p => p.chi)) * 1.1;

      const scaleX = (idx) => padding.left + (idx / xMax) * plotWidth;
      const scaleY = (chi) => padding.top + plotHeight - (chi / yMax) * plotHeight;

      // Build path for line
      const linePath = points.map((p, i) =>
        `${{i === 0 ? 'M' : 'L'}} ${{scaleX(p.index)}} ${{scaleY(p.chi)}}`
      ).join(' ');

      const fillPath = linePath +
        ` L ${{scaleX(points[points.length - 1].index)}} ${{scaleY(0)}}` +
        ` L ${{scaleX(0)}} ${{scaleY(0)}} Z`;

      // Histogram dimensions
      const histWidth = 320;
      const histHeight = 180;
      const histPadding = {{ top: 20, right: 20, bottom: 30, left: 50 }};
      const histPlotWidth = histWidth - histPadding.left - histPadding.right;
      const histPlotHeight = histHeight - histPadding.top - histPadding.bottom;

      const maxBinCount = Math.max(...histogram.bins);
      const binWidth = histPlotWidth / histogram.bins.length;

      // Calculate max word contribution for scaling
      const maxContribution = topWords.length > 0
        ? Math.max(...topWords.map(w => w.contribution))
        : 1;

      return (
        <div style={{{{ maxWidth: 1050, margin: '0 auto' }}}}>
          <h1 style={{{{ fontSize: 18, fontWeight: 600, marginBottom: 20, color: '#1f2937' }}}}>
            {{title}}
          </h1>

          <div className="report-grid">
            {{/* Timeline - full width */}}
            <div className="card full-width">
              <h3 className="card-title">Chi-squared Timeline</h3>
              <svg width={{timelineWidth}} height={{timelineHeight}}>
                {{/* Fill under curve */}}
                <path d={{fillPath}} fill="#dbeafe" opacity={{0.4}} />

                {{/* Mean line */}}
                <line
                  x1={{padding.left}}
                  y1={{scaleY(thresholds.mean)}}
                  x2={{timelineWidth - padding.right}}
                  y2={{scaleY(thresholds.mean)}}
                  stroke="#6b7280"
                  strokeWidth={{1}}
                  opacity={{0.6}}
                />

                {{/* Max location marker */}}
                {{stats.maxLocation !== null && (
                  <>
                    <line
                      x1={{scaleX(stats.maxLocation)}}
                      y1={{padding.top}}
                      x2={{scaleX(stats.maxLocation)}}
                      y2={{timelineHeight - padding.bottom}}
                      stroke="#dc2626"
                      strokeWidth={{2}}
                      strokeDasharray="6,4"
                      opacity={{0.6}}
                    />
                    <circle
                      cx={{scaleX(stats.maxLocation)}}
                      cy={{scaleY(points[stats.maxLocation].chi)}}
                      r={{8}}
                      fill="#dc2626"
                      stroke="white"
                      strokeWidth={{2}}
                    />
                  </>
                )}}

                {{/* Main line */}}
                <path
                  d={{linePath}}
                  fill="none"
                  stroke="#2563eb"
                  strokeWidth={{2}}
                  strokeLinejoin="round"
                />

                {{/* Data points */}}
                {{points.map((point, i) => {{
                  const isActive = activeIndex === i;
                  const isPinned = selectedIndex === i;
                  return (
                    <circle
                      key={{i}}
                      cx={{scaleX(point.index)}}
                      cy={{scaleY(point.chi)}}
                      r={{isActive ? 7 : 5}}
                      fill={{getPointColor(point.distance)}}
                      stroke={{isPinned ? '#dc2626' : isActive ? '#1f2937' : 'white'}}
                      strokeWidth={{isPinned ? 3 : isActive ? 2 : 1.5}}
                      style={{{{ cursor: 'pointer' }}}}
                      onMouseEnter={{() => setHoveredIndex(i)}}
                      onMouseLeave={{() => setHoveredIndex(null)}}
                      onClick={{() => handlePointClick(i)}}
                    />
                  );
                }})}}

                {{/* Axes */}}
                <line
                  x1={{padding.left}}
                  y1={{timelineHeight - padding.bottom}}
                  x2={{timelineWidth - padding.right}}
                  y2={{timelineHeight - padding.bottom}}
                  stroke="#374151"
                />
                <line
                  x1={{padding.left}}
                  y1={{padding.top}}
                  x2={{padding.left}}
                  y2={{timelineHeight - padding.bottom}}
                  stroke="#374151"
                />
                <text x={{timelineWidth / 2}} y={{timelineHeight - 8}} textAnchor="middle" fontSize={{11}}>
                  Window Pair Index
                </text>
                <text x={{15}} y={{timelineHeight / 2}} textAnchor="middle" fontSize={{11}} transform={{`rotate(-90, 15, ${{timelineHeight / 2}})`}}>
                  χ²
                </text>
              </svg>
              {{/* Quick info bar for hovered/selected point */}}
              {{activePoint && (
                <div style={{{{ marginTop: 8, padding: '8px 12px', background: '#f8fafc', borderRadius: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: isSelected ? '2px solid #dc2626' : '1px solid #e2e8f0' }}}}>
                  <div style={{{{ fontSize: 12 }}}}>
                    {{isSelected && <span style={{{{ color: '#dc2626', marginRight: 6 }}}}>📌</span>}}
                    <strong>Window {{activePoint.index}}:</strong> χ² = {{activePoint.chi.toFixed(2)}}
                    {{hasChunks && !isSelected && <span style={{{{ color: '#9ca3af', marginLeft: 8 }}}}>(click to view chunks)</span>}}
                  </div>
                  {{isSelected && (
                    <button
                      onClick={{() => setSelectedIndex(null)}}
                      style={{{{
                        background: 'none',
                        border: 'none',
                        fontSize: 16,
                        cursor: 'pointer',
                        color: '#6b7280',
                        padding: '0 4px',
                      }}}}
                      title="Close"
                    >×</button>
                  )}}
                </div>
              )}}
            </div>

            {{/* Histogram */}}
            <div className="card">
              <h3 className="card-title">Distribution</h3>
              <svg width={{histWidth}} height={{histHeight}}>
                {{histogram.bins.map((count, i) => (
                  <rect
                    key={{i}}
                    x={{histPadding.left + i * binWidth + 1}}
                    y={{histPadding.top + histPlotHeight - (count / maxBinCount) * histPlotHeight}}
                    width={{binWidth - 2}}
                    height={{(count / maxBinCount) * histPlotHeight}}
                    fill="#2563eb"
                    opacity={{0.7}}
                  />
                ))}}
                {{/* Mean line */}}
                <line
                  x1={{histPadding.left + ((thresholds.mean - histogram.minVal) / (histogram.maxVal - histogram.minVal)) * histPlotWidth}}
                  y1={{histPadding.top}}
                  x2={{histPadding.left + ((thresholds.mean - histogram.minVal) / (histogram.maxVal - histogram.minVal)) * histPlotWidth}}
                  y2={{histHeight - histPadding.bottom}}
                  stroke="#dc2626"
                  strokeWidth={{2}}
                  strokeDasharray="4,4"
                />
                {{/* Axes */}}
                <line
                  x1={{histPadding.left}}
                  y1={{histHeight - histPadding.bottom}}
                  x2={{histWidth - histPadding.right}}
                  y2={{histHeight - histPadding.bottom}}
                  stroke="#374151"
                />
                <text x={{histWidth / 2}} y={{histHeight - 8}} textAnchor="middle" fontSize={{10}}>χ²</text>
              </svg>
            </div>

            {{/* Summary Statistics */}}
            <div className="card">
              <h3 className="card-title">Chi-Squared Statistics</h3>
              <div className="stat-row">
                <span className="stat-label">Mean χ²:</span>
                <span className="stat-value">{{stats.meanChi.toFixed(2)}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Std χ²:</span>
                <span className="stat-value">{{stats.stdChi.toFixed(2)}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">CV:</span>
                <span className="stat-value">{{stats.cv.toFixed(4)}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Range:</span>
                <span className="stat-value">{{stats.minChi.toFixed(1)}} – {{stats.maxChi.toFixed(1)}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Trend:</span>
                <span className="stat-value">{{stats.trend >= 0 ? '+' : ''}}{{stats.trend.toFixed(4)}}</span>
              </div>
              {{stats.maxLocation !== null && (
                <div className="stat-row">
                  <span className="stat-label">Max at:</span>
                  <span className="stat-value">Window {{stats.maxLocation}}</span>
                </div>
              )}}
              <hr style={{{{ margin: '8px 0', border: 'none', borderTop: '1px solid #e2e8f0' }}}} />
              <div className="stat-row">
                <span className="stat-label">Spike threshold:</span>
                <span className="stat-value">{{thresholds.spike.toFixed(2)}}</span>
              </div>
            </div>

            {{/* Zone Classification */}}
            <div className="card">
              <h3 className="card-title">Zone Classification</h3>
              <div style={{{{ marginBottom: 16 }}}}>
                <div style={{{{ fontSize: 12, color: '#6b7280', marginBottom: 4 }}}}>Baseline</div>
                <span className="zone-badge" style={{{{ background: zones.baseline.color }}}}>
                  {{zones.baseline.name}}
                </span>
                <div style={{{{ fontSize: 11, color: '#9ca3af', marginTop: 4 }}}}>
                  Mean χ² = {{stats.meanChi.toFixed(1)}}
                </div>
              </div>
              <div style={{{{ marginBottom: 16 }}}}>
                <div style={{{{ fontSize: 12, color: '#6b7280', marginBottom: 4 }}}}>Volatility</div>
                <span className="zone-badge" style={{{{ background: zones.volatility.color }}}}>
                  {{zones.volatility.name}}
                </span>
                <div style={{{{ fontSize: 11, color: '#9ca3af', marginTop: 4 }}}}>
                  CV = {{stats.cv.toFixed(4)}}
                </div>
              </div>
              <hr style={{{{ margin: '12px 0', border: 'none', borderTop: '1px solid #e2e8f0' }}}} />
              <div style={{{{ fontSize: 11, color: '#6b7280' }}}}>
                <div><strong>Reference Bounds:</strong></div>
                <div>AI: Mean χ² &lt; {{bounds.MEAN_CHI_LOW}}</div>
                <div>Human: Mean χ² &gt; {{bounds.MEAN_CHI_HIGH}}</div>
                <div>Stable: CV &lt; {{bounds.CV_LOW}}</div>
                <div>Volatile: CV &gt; {{bounds.CV_HIGH}}</div>
              </div>
            </div>

            {{/* Analysis Results */}}
            <div className="card">
              <h3 className="card-title">Analysis Results</h3>
              <div className="stat-row">
                <span className="stat-label">Pattern:</span>
                <span className="stat-value">{{stats.pattern.replace('_', ' ')}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Confidence:</span>
                <span className="stat-value">{{(stats.confidence * 100).toFixed(1)}}%</span>
              </div>
            </div>

            {{/* Parameters */}}
            <div className="card">
              <h3 className="card-title">Parameters</h3>
              <div className="stat-row">
                <span className="stat-label">Window size:</span>
                <span className="stat-value">{{stats.windowSize}} tokens</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Stride:</span>
                <span className="stat-value">{{stats.stride}} tokens</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Overlap:</span>
                <span className="stat-value">{{(stats.overlapRatio * 100).toFixed(0)}}%</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Windows:</span>
                <span className="stat-value">{{stats.windowCount}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Comparisons:</span>
                <span className="stat-value">{{points.length}}</span>
              </div>
            </div>

            {{/* Top Contributors */}}
            <div className="card">
              <h3 className="card-title">
                {{topWords.length > 0
                  ? `Top Contributors at Spike (Window ${{stats.maxLocation}})`
                  : 'Top Contributors at Spike'}}
              </h3>
              {{topWords.length > 0 ? (
                topWords.map((w, i) => (
                  <div key={{i}} className="word-bar">
                    <span className="word-label">{{w.word}}</span>
                    <div className="word-bar-bg">
                      <div
                        className="word-bar-fill"
                        style={{{{ width: `${{(w.contribution / maxContribution) * 100}}%` }}}}
                      />
                    </div>
                    <span style={{{{ marginLeft: 8, fontSize: 11, color: '#6b7280', fontFamily: 'ui-monospace' }}}}>
                      {{w.contribution.toFixed(1)}}
                    </span>
                  </div>
                ))
              ) : (
                <p style={{{{ fontSize: 13, color: '#9ca3af' }}}}>
                  {{stats.maxLocation !== null ? 'No word data available' : 'No spike detected'}}
                </p>
              )}}
            </div>
          </div>

          {{/* Chunk panels - full width below grid, only when selected */}}
          {{hasChunks && selectedPoint && selectedPoint.chunkA && (
            <div style={{{{ display: 'flex', gap: 12, marginTop: 8 }}}}>
              <div className="card" style={{{{ flex: 1, margin: 0, padding: '12px' }}}}>
                <div style={{{{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}}}>
                  <h3 className="card-title" style={{{{ margin: 0, fontSize: 13 }}}}>Chunk {{selectedPoint.index}}</h3>
                  <button
                    onClick={{() => setSelectedIndex(null)}}
                    style={{{{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: 14,
                      color: '#9ca3af',
                      padding: '0 4px',
                    }}}}
                    title="Close"
                  >✕</button>
                </div>
                <div style={{{{
                  padding: 10,
                  background: '#f8fafc',
                  borderRadius: 4,
                  fontSize: 11,
                  lineHeight: 1.5,
                  maxHeight: 220,
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  border: '1px solid #e2e8f0',
                }}}}>
                  {{selectedPoint.chunkA}}
                </div>
              </div>
              {{selectedPoint.chunkB && (
                <div className="card" style={{{{ flex: 1, margin: 0, padding: '12px' }}}}>
                  <h3 className="card-title" style={{{{ marginBottom: 6, fontSize: 13 }}}}>Chunk {{selectedPoint.index + 1}}</h3>
                  <div style={{{{
                    padding: 10,
                    background: '#f8fafc',
                    borderRadius: 4,
                    fontSize: 11,
                    lineHeight: 1.5,
                    maxHeight: 220,
                    overflowY: 'auto',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    border: '1px solid #e2e8f0',
                  }}}}>
                    {{selectedPoint.chunkB}}
                  </div>
                </div>
              )}}
            </div>
          )}}

          <p style={{{{ marginTop: 20, fontSize: 11, color: '#9ca3af', textAlign: 'center' }}}}>
            Generated by pystylometry
          </p>
        </div>
      );
    }}
"""

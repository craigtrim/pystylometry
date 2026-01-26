"""Interactive timeline visualization for Kilgarriff drift detection.

Creates a line chart with:
- X-axis: Window pair index (temporal position in document)
- Y-axis: Chi-squared value
- Hover interactions showing point details
- Reference threshold lines
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


def export_drift_timeline_jsx(
    result: "KilgarriffDriftResult",
    output_file: str | Path,
    title: str = "Stylistic Drift Timeline",
    chunks: list[str] | None = None,
) -> Path:
    """
    Export an interactive timeline visualization as a standalone HTML file.

    Creates a self-contained HTML file with React via CDN:
    - Line chart showing chi-squared values over document
    - Hover over points to see detailed values
    - Reference lines for mean, AI threshold, and spike threshold
    - Opens directly in any browser (no build step required)

    Args:
        result: KilgarriffDriftResult from compute_kilgarriff_drift()
        output_file: Path to write the HTML file (e.g., "timeline.html")
        title: Chart title
        chunks: Optional list of chunk text content for hover display

    Returns:
        Path to the generated HTML file

    Example:
        >>> result = compute_kilgarriff_drift(text)
        >>> export_drift_timeline_jsx(result, "timeline.html")
    """
    chi_values = [s["chi_squared"] for s in result.pairwise_scores]

    if len(chi_values) < 2:
        raise ValueError("Need at least 2 window comparisons for timeline")

    # Build data points with distance from mean for coloring
    mean_chi = result.mean_chi_squared
    std_chi = result.std_chi_squared
    spike_threshold = mean_chi + 2 * std_chi if mean_chi > 0 else 100

    points_data = []
    for i, chi in enumerate(chi_values):
        # Distance: how many std devs from mean
        if std_chi > 0:
            z_score = abs(chi - mean_chi) / std_chi
            distance = min(1, z_score / 3)  # Normalize: 3 std devs = max distance
        else:
            distance = 0 if chi == mean_chi else 1

        point = {
            "index": i,
            "chi": round(chi, 2),
            "distance": round(distance, 3),
            "window_pair": f"{i} → {i + 1}",
        }

        # Add chunk text if available
        if chunks:
            if i < len(chunks):
                point["chunkA"] = chunks[i]
            if i + 1 < len(chunks):
                point["chunkB"] = chunks[i + 1]

        points_data.append(point)

    # Axis bounds
    y_min = 0
    y_max = max(chi_values) * 1.15

    # Get top words at spike if available
    top_words = []
    if result.max_location is not None and result.max_location < len(result.pairwise_scores):
        spike_data = result.pairwise_scores[result.max_location]
        if "top_words" in spike_data and spike_data["top_words"]:
            top_words = [
                {"word": w[0], "contribution": round(w[1], 2)} for w in spike_data["top_words"][:8]
            ]

    config = {
        "title": title,
        "points": points_data,
        "hasChunks": chunks is not None and len(chunks) > 0,
        "topWords": top_words,
        "bounds": {
            "xMax": len(chi_values) - 1,
            "yMin": y_min,
            "yMax": round(y_max, 2),
        },
        "thresholds": {
            "mean": round(mean_chi, 2),
            "spike": round(spike_threshold, 2),
            "ai": 50,  # AI baseline threshold
        },
        "stats": {
            "pattern": result.pattern,
            "confidence": round(result.pattern_confidence, 3),
            "meanChi": round(mean_chi, 2),
            "stdChi": round(std_chi, 2),
            "minChi": round(result.min_chi_squared, 2),
            "maxChi": round(result.max_chi_squared, 2),
            "cv": round(std_chi / mean_chi, 4) if mean_chi > 0 else 0,
            "maxLocation": result.max_location,
            "windowCount": result.window_count,
            "windowSize": result.window_size,
            "stride": result.stride,
            "overlapRatio": round(result.overlap_ratio, 2),
            "trend": round(result.trend, 4),
            "comparisons": len(result.pairwise_scores),
        },
    }

    component = _get_timeline_component()
    html_content = generate_html_document(
        title=f"{title} - Drift Timeline",
        config=config,
        react_component=component,
        component_name="DriftTimeline",
        extra_styles=CARD_STYLES,
    )

    return write_html_file(output_file, html_content)


def _get_timeline_component() -> str:
    """Return the React component code for the timeline visualization."""
    return f"""
    {COLOR_INTERPOLATION_JS}

    function DriftTimeline() {{
      const [hoveredIndex, setHoveredIndex] = React.useState(null);
      const [selectedIndex, setSelectedIndex] = React.useState(0);
      const [middlePanelView, setMiddlePanelView] = React.useState(0); // 0=Analysis, 1=Parameters, 2=Top Contributors

      const {{ title, points, bounds, thresholds, stats, hasChunks, topWords }} = CONFIG;

      // Keyboard navigation for chart points
      React.useEffect(() => {{
        const handleKeyDown = (e) => {{
          if (e.key === 'ArrowLeft') {{
            if (selectedIndex === null) {{
              setSelectedIndex(points.length - 1); // Start at end
            }} else if (selectedIndex > 0) {{
              setSelectedIndex(selectedIndex - 1);
            }}
            e.preventDefault();
          }} else if (e.key === 'ArrowRight') {{
            if (selectedIndex === null) {{
              setSelectedIndex(0); // Start at beginning
            }} else if (selectedIndex < points.length - 1) {{
              setSelectedIndex(selectedIndex + 1);
            }}
            e.preventDefault();
          }} else if (e.key === 'Escape') {{
            setSelectedIndex(null);
            e.preventDefault();
          }}
        }};
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
      }}, [selectedIndex, points.length]);

      // Max word contribution for scaling
      const maxContribution = topWords && topWords.length > 0 ? Math.max(...topWords.map(w => w.contribution)) : 1;
      const {{ xMax, yMin, yMax }} = bounds;

      // SVG dimensions
      const width = 750;
      const height = 400;
      const padding = {{ top: 40, right: 30, bottom: 50, left: 70 }};
      const plotWidth = width - padding.left - padding.right;
      const plotHeight = height - padding.top - padding.bottom;

      // Scale functions
      const scaleX = (idx) => padding.left + (idx / xMax) * plotWidth;
      const scaleY = (chi) => padding.top + plotHeight - ((chi - yMin) / (yMax - yMin)) * plotHeight;

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

      // Build path for line
      const linePath = points.map((p, i) =>
        `${{i === 0 ? 'M' : 'L'}} ${{scaleX(p.index)}} ${{scaleY(p.chi)}}`
      ).join(' ');

      // Build path for fill under curve
      const fillPath = linePath +
        ` L ${{scaleX(points[points.length - 1].index)}} ${{scaleY(0)}}` +
        ` L ${{scaleX(0)}} ${{scaleY(0)}} Z`;

      // Classify comparison based on thresholds
      const getClassification = (chi) => {{
        if (chi < thresholds.ai) return {{ label: 'AI-like', color: '#f59e0b', desc: 'Below AI baseline - unusually uniform' }};
        if (chi < thresholds.mean * 0.7) return {{ label: 'Low variance', color: '#10b981', desc: 'Below mean - consistent style' }};
        if (chi < thresholds.mean * 1.3) return {{ label: 'Typical', color: '#6b7280', desc: 'Near mean - normal variation' }};
        if (chi < thresholds.spike) return {{ label: 'Elevated', color: '#f97316', desc: 'Above mean - notable variation' }};
        return {{ label: 'Spike', color: '#dc2626', desc: 'Above spike threshold - significant change' }};
      }};

      return (
        <div style={{{{ fontFamily: 'system-ui, sans-serif', maxWidth: width + 310 }}}}>
          {{/* Top row: Chart + Stats */}}
          <div style={{{{ display: 'flex', gap: 20, alignItems: 'flex-start' }}}}>
            {{/* Chart */}}
            <svg width={{width}} height={{height}} style={{{{ background: 'white', borderRadius: 8, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}}}>
              {{/* Title */}}
              <text x={{width / 2}} y={{20}} textAnchor="middle" fontSize={{14}} fontWeight="500">
                {{title}}
              </text>

              {{/* Fill under curve */}}
              <path d={{fillPath}} fill="#dbeafe" opacity={{0.4}} />

              {{/* Reference lines */}}
              {{/* Mean line */}}
              <line
                x1={{padding.left}}
                y1={{scaleY(thresholds.mean)}}
                x2={{width - padding.right}}
                y2={{scaleY(thresholds.mean)}}
                stroke="#6b7280"
                strokeWidth={{1}}
                opacity={{0.6}}
              />
              <text
                x={{width - padding.right + 5}}
                y={{scaleY(thresholds.mean)}}
                fontSize={{10}}
                fill="#6b7280"
                dominantBaseline="middle"
              >
                μ
              </text>

              {{/* AI threshold line */}}
              {{thresholds.ai < yMax && (
                <>
                  <line
                    x1={{padding.left}}
                    y1={{scaleY(thresholds.ai)}}
                    x2={{width - padding.right}}
                    y2={{scaleY(thresholds.ai)}}
                    stroke="#f59e0b"
                    strokeWidth={{1}}
                    strokeDasharray="4,4"
                    opacity={{0.6}}
                  />
                  <text
                    x={{padding.left - 5}}
                    y={{scaleY(thresholds.ai)}}
                    fontSize={{10}}
                    fill="#f59e0b"
                    textAnchor="end"
                    dominantBaseline="middle"
                  >
                    AI
                  </text>
                </>
              )}}

              {{/* Spike threshold line */}}
              {{thresholds.spike < yMax && (
                <>
                  <line
                    x1={{padding.left}}
                    y1={{scaleY(thresholds.spike)}}
                    x2={{width - padding.right}}
                    y2={{scaleY(thresholds.spike)}}
                    stroke="#10b981"
                    strokeWidth={{1}}
                    strokeDasharray="4,4"
                    opacity={{0.6}}
                  />
                  <text
                    x={{padding.left - 5}}
                    y={{scaleY(thresholds.spike)}}
                    fontSize={{10}}
                    fill="#10b981"
                    textAnchor="end"
                    dominantBaseline="middle"
                  >
                    μ+2σ
                  </text>
                </>
              )}}

              {{/* Max location vertical line */}}
              {{stats.maxLocation !== null && (
                <line
                  x1={{scaleX(stats.maxLocation)}}
                  y1={{padding.top}}
                  x2={{scaleX(stats.maxLocation)}}
                  y2={{height - padding.bottom}}
                  stroke="#dc2626"
                  strokeWidth={{2}}
                  strokeDasharray="6,4"
                  opacity={{0.5}}
                />
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
                    style={{{{ cursor: 'pointer', transition: 'all 0.15s ease' }}}}
                    onMouseEnter={{() => setHoveredIndex(i)}}
                    onMouseLeave={{() => setHoveredIndex(null)}}
                    onClick={{() => handlePointClick(i)}}
                  />
                );
              }})}}

              {{/* X-axis */}}
              <line
                x1={{padding.left}}
                y1={{height - padding.bottom}}
                x2={{width - padding.right}}
                y2={{height - padding.bottom}}
                stroke="#374151"
              />
              <text x={{width / 2}} y={{height - 10}} textAnchor="middle" fontSize={{12}}>
                Window Pair Index
              </text>

              {{/* Y-axis */}}
              <line
                x1={{padding.left}}
                y1={{padding.top}}
                x2={{padding.left}}
                y2={{height - padding.bottom}}
                stroke="#374151"
              />
              <text
                x={{20}}
                y={{height / 2}}
                textAnchor="middle"
                fontSize={{12}}
                transform={{`rotate(-90, 20, ${{height / 2}})`}}
              >
                Chi-squared (χ²)
              </text>

              {{/* Y-axis tick labels */}}
              {{[0, 0.25, 0.5, 0.75, 1].map((t) => {{
                const val = yMin + t * (yMax - yMin);
                return (
                  <text
                    key={{t}}
                    x={{padding.left - 8}}
                    y={{scaleY(val)}}
                    textAnchor="end"
                    fontSize={{10}}
                    fill="#6b7280"
                    dominantBaseline="middle"
                  >
                    {{val.toFixed(0)}}
                  </text>
                );
              }})}}
            </svg>

            {{/* Stats panel - matches chart height */}}
            <div className="card" style={{{{ width: 280, height: height, overflowY: 'auto' }}}}>
              <h3 className="card-title">Analysis Results</h3>
              <div className="stat-row">
                <span className="stat-label">Pattern:</span>
                <span className="stat-value">{{stats.pattern.replace('_', ' ')}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Confidence:</span>
                <span className="stat-value">{{(stats.confidence * 100).toFixed(1)}}%</span>
              </div>
              <hr style={{{{ margin: '10px 0', border: 'none', borderTop: '1px solid #e2e8f0' }}}} />
              <div style={{{{ fontSize: 11, fontWeight: 500, color: '#6b7280', marginBottom: 6 }}}}>CHI-SQUARED STATISTICS</div>
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
              <hr style={{{{ margin: '10px 0', border: 'none', borderTop: '1px solid #e2e8f0' }}}} />
              <div style={{{{ fontSize: 11, fontWeight: 500, color: '#6b7280', marginBottom: 6 }}}}>PARAMETERS</div>
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
                <span className="stat-value">{{stats.comparisons}}</span>
              </div>
              <hr style={{{{ margin: '10px 0', border: 'none', borderTop: '1px solid #e2e8f0' }}}} />
              <div style={{{{ fontSize: 11, fontWeight: 500, color: '#6b7280', marginBottom: 6 }}}}>THRESHOLDS</div>
              <div className="stat-row">
                <span className="stat-label">AI baseline:</span>
                <span className="stat-value">{{thresholds.ai}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Mean (μ):</span>
                <span className="stat-value">{{thresholds.mean.toFixed(2)}}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Spike (μ+2σ):</span>
                <span className="stat-value">{{thresholds.spike.toFixed(2)}}</span>
              </div>

              {{!selectedPoint && (
                <p style={{{{ marginTop: 10, fontSize: 11, color: '#9ca3af' }}}}>
                  {{hasChunks ? 'Click a point to view comparison details' : 'Hover over points for details'}}
                </p>
              )}}
            </div>
          </div>

          {{/* Bottom row: 3 panels when point selected */}}
          {{hasChunks && selectedPoint && selectedPoint.chunkA && (() => {{
            const classification = getClassification(selectedPoint.chi);
            const deviation = (selectedPoint.distance * 3).toFixed(2);
            const percentile = Math.round((points.filter(p => p.chi <= selectedPoint.chi).length / points.length) * 100);

            return (
              <div style={{{{ display: 'flex', gap: 12, marginTop: 12 }}}}>
                {{/* Chunk A */}}
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
                    maxHeight: 260,
                    overflowY: 'auto',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    border: '1px solid #e2e8f0',
                  }}}}>
                    {{selectedPoint.chunkA}}
                  </div>
                </div>

                {{/* Middle panel with carousel navigation */}}
                <div className="card" style={{{{ width: 260, height: 320, margin: 0, padding: '12px', display: 'flex', flexDirection: 'column', position: 'relative' }}}}>
                  {{/* Header with arrows */}}
                  <div style={{{{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}}}>
                    <button
                      onClick={{() => setMiddlePanelView(v => v === 0 ? 2 : v - 1)}}
                      style={{{{
                        background: '#f1f5f9',
                        border: '1px solid #e2e8f0',
                        borderRadius: 4,
                        cursor: 'pointer',
                        fontSize: 14,
                        padding: '4px 8px',
                        color: '#64748b',
                      }}}}
                      title="Previous view"
                    >←</button>
                    <h3 className="card-title" style={{{{ margin: 0, fontSize: 13 }}}}>
                      {{middlePanelView === 0 ? 'Comparison Analysis' : middlePanelView === 1 ? 'Parameters' : 'Top Contributors'}}
                    </h3>
                    <button
                      onClick={{() => setMiddlePanelView(v => v === 2 ? 0 : v + 1)}}
                      style={{{{
                        background: '#f1f5f9',
                        border: '1px solid #e2e8f0',
                        borderRadius: 4,
                        cursor: 'pointer',
                        fontSize: 14,
                        padding: '4px 8px',
                        color: '#64748b',
                      }}}}
                      title="Next view"
                    >→</button>
                  </div>

                  {{/* Content area - flex grow */}}
                  <div style={{{{ flex: 1 }}}}>
                    {{/* View 0: Comparison Analysis */}}
                    {{middlePanelView === 0 && (
                      <>
                        <div className="stat-row">
                          <span className="stat-label">Window pair:</span>
                          <span className="stat-value">{{selectedPoint.window_pair}}</span>
                        </div>
                        <div className="stat-row">
                          <span className="stat-label">Chi-squared:</span>
                          <span className="stat-value">{{selectedPoint.chi.toFixed(2)}}</span>
                        </div>
                        <div className="stat-row">
                          <span className="stat-label">Deviation:</span>
                          <span className="stat-value">{{deviation}}σ</span>
                        </div>
                        <div className="stat-row">
                          <span className="stat-label">Percentile:</span>
                          <span className="stat-value">{{percentile}}%</span>
                        </div>
                        <hr style={{{{ margin: '8px 0', border: 'none', borderTop: '1px solid #e2e8f0' }}}} />
                        <div style={{{{
                          padding: '8px 10px',
                          background: classification.color + '15',
                          borderRadius: 4,
                          borderLeft: `3px solid ${{classification.color}}`
                        }}}}>
                          <div style={{{{ fontWeight: 600, fontSize: 12, color: classification.color, marginBottom: 4 }}}}>
                            {{classification.label}}
                          </div>
                          <div style={{{{ fontSize: 10, color: '#6b7280', lineHeight: 1.4 }}}}>
                            {{classification.desc}}
                          </div>
                        </div>
                      </>
                    )}}

                    {{/* View 1: Parameters */}}
                    {{middlePanelView === 1 && (
                      <>
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
                          <span className="stat-value">{{stats.comparisons}}</span>
                        </div>
                      </>
                    )}}

                    {{/* View 2: Top Contributors */}}
                    {{middlePanelView === 2 && (
                      <>
                        {{topWords && topWords.length > 0 ? (
                          topWords.map((w, i) => (
                            <div key={{i}} style={{{{ display: 'flex', alignItems: 'center', marginBottom: 4, fontSize: 11 }}}}>
                              <span style={{{{ width: 60, fontFamily: 'ui-monospace, monospace', overflow: 'hidden', textOverflow: 'ellipsis' }}}}>{{w.word}}</span>
                              <div style={{{{ flex: 1, height: 14, background: '#e2e8f0', borderRadius: 2, marginLeft: 6, overflow: 'hidden' }}}}>
                                <div style={{{{ height: '100%', width: `${{(w.contribution / maxContribution) * 100}}%`, background: '#2563eb', borderRadius: 2 }}}} />
                              </div>
                              <span style={{{{ marginLeft: 6, fontSize: 10, color: '#6b7280', fontFamily: 'ui-monospace', minWidth: 32, textAlign: 'right' }}}}>
                                {{w.contribution.toFixed(1)}}
                              </span>
                            </div>
                          ))
                        ) : (
                          <p style={{{{ fontSize: 12, color: '#9ca3af', textAlign: 'center', marginTop: 20 }}}}>
                            {{stats.maxLocation !== null ? 'No word data available' : 'No spike detected'}}
                          </p>
                        )}}
                        {{topWords && topWords.length > 0 && (
                          <div style={{{{ fontSize: 10, color: '#9ca3af', marginTop: 8, textAlign: 'center' }}}}>
                            Spike at Window {{stats.maxLocation}}
                          </div>
                        )}}
                      </>
                    )}}
                  </div>

                  {{/* Panel indicator dots - fixed at bottom */}}
                  <div style={{{{ display: 'flex', justifyContent: 'center', gap: 6, paddingTop: 10 }}}}>
                    {{[0, 1, 2].map(i => (
                      <div
                        key={{i}}
                        onClick={{() => setMiddlePanelView(i)}}
                        style={{{{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          background: middlePanelView === i ? '#2563eb' : '#e2e8f0',
                          cursor: 'pointer',
                        }}}}
                        title={{i === 0 ? 'Comparison Analysis' : i === 1 ? 'Parameters' : 'Top Contributors'}}
                      />
                    ))}}
                  </div>
                </div>

                {{/* Chunk B */}}
                {{selectedPoint.chunkB && (
                  <div className="card" style={{{{ flex: 1, margin: 0, padding: '12px' }}}}>
                    <h3 className="card-title" style={{{{ marginBottom: 6, fontSize: 13 }}}}>Chunk {{selectedPoint.index + 1}}</h3>
                    <div style={{{{
                      padding: 10,
                      background: '#f8fafc',
                      borderRadius: 4,
                      fontSize: 11,
                      lineHeight: 1.5,
                      maxHeight: 260,
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
            );
          }})()}}

          <p style={{{{ marginTop: 16, fontSize: 11, color: '#9ca3af', textAlign: 'center' }}}}>
            Generated by pystylometry
          </p>
        </div>
      );
    }}
"""

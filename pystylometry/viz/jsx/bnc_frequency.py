"""Interactive HTML export for BNC frequency analysis.

This module generates a self-contained HTML report showing word frequency
comparisons against the British National Corpus (BNC).

The report has three sections:
1. Not in BNC - Words not found in the corpus (with WordNet and character type info)
2. Most Underused - Words appearing less frequently than expected
3. Most Overused - Words appearing more frequently than expected

Each word receives a morphological classification label from the word_class
module (e.g. ``apostrophe.contraction.negative``, ``hyphenated.reduplicated.ablaut``)
instead of raw boolean flag columns.  This was introduced in #53 to replace
the five boolean columns (unicode, numeric, apostrophe, hyphen, other) with
a single, more informative classification column.

Related GitHub Issues:
    #53 -- Replace boolean flag columns with word_class classification label
    https://github.com/craigtrim/pystylometry/issues/53

    #51 -- Word morphological classification taxonomy (provides classify_word)
    https://github.com/craigtrim/pystylometry/issues/51
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ._base import CARD_STYLES, generate_html_document, write_html_file

if TYPE_CHECKING:
    from pystylometry.lexical.bnc_frequency import BNCFrequencyResult


def export_bnc_frequency_jsx(
    result: "BNCFrequencyResult",
    output_file: str | Path,
    title: str = "BNC Word Frequency Analysis",
    source_file: str | None = None,
) -> Path:
    """Export BNC frequency analysis as interactive HTML.

    Generates a self-contained HTML file with three sections:
    - Not in BNC: Complete table with WordNet status and character type
    - Most Underused: Words below the underuse threshold
    - Most Overused: Words above the overuse threshold

    Args:
        result: BNCFrequencyResult from compute_bnc_frequency()
        output_file: Path to write the HTML file
        title: Page title (default: "BNC Word Frequency Analysis")
        source_file: Optional source filename to display

    Returns:
        Path to the written HTML file

    Example:
        >>> from pystylometry.lexical.bnc_frequency import compute_bnc_frequency
        >>> from pystylometry.viz.jsx import export_bnc_frequency_jsx
        >>> result = compute_bnc_frequency(text)
        >>> export_bnc_frequency_jsx(result, "frequency_report.html")
    """
    # classify_word provides the three-layer morphological taxonomy label
    # (e.g. "apostrophe.contraction.negative") that replaces the five boolean
    # flag columns (unicode, numeric, apostrophe, hyphen, other).
    # See: https://github.com/craigtrim/pystylometry/issues/53
    from pystylometry.lexical.word_class import classify_word

    # Build data for the React component
    not_in_bnc_data = [
        {
            "word": w.word,
            "observed": w.observed,
            "inWordnet": w.in_wordnet,
            "inGngram": w.in_gngram,
            "classification": classify_word(w.word).label,
        }
        for w in result.not_in_bnc
    ]

    underused_data = [
        {
            "word": w.word,
            "observed": w.observed,
            "expected": round(w.expected, 2) if w.expected else None,
            "ratio": round(w.ratio, 4) if w.ratio else None,
            "inWordnet": w.in_wordnet,
            "inGngram": w.in_gngram,
            "classification": classify_word(w.word).label,
        }
        for w in result.underused
    ]

    overused_data = [
        {
            "word": w.word,
            "observed": w.observed,
            "expected": round(w.expected, 2) if w.expected else None,
            "ratio": round(w.ratio, 1) if w.ratio else None,
            "inWordnet": w.in_wordnet,
            "inGngram": w.in_gngram,
            "classification": classify_word(w.word).label,
        }
        for w in result.overused
    ]

    config = {
        "title": title,
        "sourceFile": source_file,
        "notInBnc": not_in_bnc_data,
        "underused": underused_data,
        "overused": overused_data,
        "stats": {
            "totalTokens": result.total_tokens,
            "uniqueTokens": result.unique_tokens,
            "notInBncCount": len(result.not_in_bnc),
            "underusedCount": len(result.underused),
            "overusedCount": len(result.overused),
            "overuseThreshold": result.overuse_threshold,
            "underuseThreshold": result.underuse_threshold,
        },
    }

    react_component = """
    // Boolean flag badge colors
    const BOOL_COLORS = {
      true: { bg: '#BDD7EE', text: '#1e3a5f' },
      false: { bg: '#FCE4D6', text: '#7c4a2e' },
    };

    // Tab configuration
    const TABS = [
      { id: 'overused', label: 'Most Overused', color: '#ef4444' },
      { id: 'underused', label: 'Most Underused', color: '#3b82f6' },
      { id: 'notInBnc', label: 'Not in BNC', color: '#6b7280' },
    ];

    // WordNet status badge
    function WordnetBadge({ inWordnet }) {
      if (inWordnet === null || inWordnet === undefined) {
        return <span style={{ color: '#9ca3af', fontSize: '12px' }}>—</span>;
      }
      return inWordnet ? (
        <span style={{
          background: '#dcfce7',
          color: '#166534',
          padding: '2px 8px',
          borderRadius: '9999px',
          fontSize: '11px',
          fontWeight: 500,
        }}>Yes</span>
      ) : (
        <span style={{
          background: '#fee2e2',
          color: '#991b1b',
          padding: '2px 8px',
          borderRadius: '9999px',
          fontSize: '11px',
          fontWeight: 500,
        }}>No</span>
      );
    }

    // Boolean flag badge
    function BoolBadge({ value }) {
      const config = BOOL_COLORS[String(!!value)];
      return (
        <span style={{
          background: config.bg,
          color: config.text,
          padding: '2px 8px',
          borderRadius: '9999px',
          fontSize: '11px',
          fontWeight: 500,
        }}>{value ? 'true' : 'false'}</span>
      );
    }

    // Ratio display with color intensity
    function RatioDisplay({ ratio, isOverused }) {
      if (ratio === null || ratio === undefined) return '—';

      let color, intensity;
      if (isOverused) {
        intensity = Math.min(Math.log2(ratio) / 6, 1);
        const r = 239;
        const g = Math.round(68 + (1 - intensity) * 120);
        color = `rgb(${r}, ${g}, 68)`;
      } else {
        intensity = Math.min(Math.abs(Math.log2(ratio)) / 4, 1);
        const b = 246;
        const g = Math.round(130 + (1 - intensity) * 60);
        color = `rgb(59, ${g}, ${b})`;
      }

      const displayValue = isOverused ? ratio.toFixed(1) + 'x' : ratio.toFixed(4);

      return (
        <span style={{
          color: color,
          fontWeight: 600,
          fontFamily: 'ui-monospace, monospace',
        }}>{displayValue}</span>
      );
    }

    // Stats summary card
    function StatsCard({ stats, activeTab, onTabChange }) {
      return (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '4px' }}>Total Tokens</div>
              <div style={{ fontSize: '20px', fontWeight: 600 }}>{stats.totalTokens.toLocaleString()}</div>
            </div>
            <div>
              <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '4px' }}>Unique Words</div>
              <div style={{ fontSize: '20px', fontWeight: 600 }}>{stats.uniqueTokens.toLocaleString()}</div>
            </div>
            {TABS.map(tab => (
              <div
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                style={{
                  cursor: 'pointer',
                  padding: '8px',
                  margin: '-8px',
                  borderRadius: '8px',
                  background: activeTab === tab.id ? `${tab.color}10` : 'transparent',
                  border: activeTab === tab.id ? `2px solid ${tab.color}` : '2px solid transparent',
                  transition: 'all 0.15s',
                }}
              >
                <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '4px' }}>{tab.label}</div>
                <div style={{ fontSize: '20px', fontWeight: 600, color: tab.color }}>
                  {tab.id === 'overused' ? stats.overusedCount.toLocaleString() :
                   tab.id === 'underused' ? stats.underusedCount.toLocaleString() :
                   stats.notInBncCount.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Tab bar component
    function TabBar({ activeTab, onTabChange, stats }) {
      return (
        <div style={{ display: 'flex', gap: '4px', marginBottom: '16px', borderBottom: '2px solid #e2e8f0', paddingBottom: '0' }}>
          {TABS.map(tab => {
            const count = tab.id === 'overused' ? stats.overusedCount :
                          tab.id === 'underused' ? stats.underusedCount :
                          stats.notInBncCount;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                style={{
                  padding: '12px 20px',
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? tab.color : '#6b7280',
                  borderBottom: isActive ? `3px solid ${tab.color}` : '3px solid transparent',
                  marginBottom: '-2px',
                  transition: 'all 0.15s',
                }}
              >
                {tab.label}
                <span style={{
                  marginLeft: '8px',
                  padding: '2px 8px',
                  borderRadius: '9999px',
                  fontSize: '12px',
                  background: isActive ? `${tab.color}20` : '#f1f5f9',
                  color: isActive ? tab.color : '#6b7280',
                }}>{count.toLocaleString()}</span>
              </button>
            );
          })}
        </div>
      );
    }

    // Data table component
    function DataTable({ data, columns, emptyMessage, filter, onFilterChange }) {
      const [sortKey, setSortKey] = React.useState(null);
      const [sortDir, setSortDir] = React.useState('desc');

      const filteredData = React.useMemo(() => {
        if (!filter) return data;
        const lowerFilter = filter.toLowerCase();
        return data.filter(row => row.word.toLowerCase().includes(lowerFilter));
      }, [data, filter]);

      const sortedData = React.useMemo(() => {
        if (!sortKey) return filteredData;
        return [...filteredData].sort((a, b) => {
          let aVal = a[sortKey];
          let bVal = b[sortKey];
          if (aVal === null || aVal === undefined) aVal = sortDir === 'desc' ? -Infinity : Infinity;
          if (bVal === null || bVal === undefined) bVal = sortDir === 'desc' ? -Infinity : Infinity;
          if (typeof aVal === 'string') {
            return sortDir === 'desc' ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
          }
          return sortDir === 'desc' ? bVal - aVal : aVal - bVal;
        });
      }, [filteredData, sortKey, sortDir]);

      const handleSort = (key) => {
        if (sortKey === key) {
          setSortDir(sortDir === 'desc' ? 'asc' : 'desc');
        } else {
          setSortKey(key);
          setSortDir('desc');
        }
      };

      return (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '13px', color: '#6b7280' }}>{sortedData.length} words</span>
            <input
              type="text"
              placeholder="Filter words..."
              value={filter}
              onChange={(e) => onFilterChange(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '13px',
                width: '200px',
              }}
            />
          </div>

          {sortedData.length === 0 ? (
            <div style={{ padding: '48px', textAlign: 'center', color: '#9ca3af' }}>
              {filter ? 'No matching words' : emptyMessage}
            </div>
          ) : (
            <div style={{ overflowX: 'auto', maxHeight: '600px', overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead style={{ position: 'sticky', top: 0, background: 'white' }}>
                  <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                    {columns.map(col => (
                      <th
                        key={col.key}
                        onClick={() => col.sortable !== false && handleSort(col.key)}
                        style={{
                          textAlign: col.align || 'left',
                          padding: '10px 12px',
                          fontWeight: 600,
                          color: '#374151',
                          cursor: col.sortable !== false ? 'pointer' : 'default',
                          userSelect: 'none',
                          whiteSpace: 'nowrap',
                          background: 'white',
                        }}
                      >
                        {col.label}
                        {sortKey === col.key && (
                          <span style={{ marginLeft: '4px' }}>{sortDir === 'desc' ? '↓' : '↑'}</span>
                        )}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sortedData.map((row, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      {columns.map(col => (
                        <td key={col.key} style={{ padding: '10px 12px', textAlign: col.align || 'left' }}>
                          {col.render ? col.render(row[col.key], row) : row[col.key]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      );
    }

    // Main component
    function BNCFrequencyReport() {
      const { title, sourceFile, notInBnc, underused, overused, stats } = CONFIG;
      const [activeTab, setActiveTab] = React.useState('overused');
      const [filter, setFilter] = React.useState('');

      // Reset filter when tab changes
      const handleTabChange = (tab) => {
        setActiveTab(tab);
        setFilter('');
      };

      // Column definitions
      const boolRender = (v) => <BoolBadge value={v} />;

      // Classification label render -- dot-separated taxonomy path from
      // classify_word(), e.g. "apostrophe.contraction.negative".
      // See: https://github.com/craigtrim/pystylometry/issues/51
      const classificationRender = (v) => {
        if (!v || v === 'lexical') {
          return <span style={{ color: '#9ca3af', fontSize: '12px' }}>lexical</span>;
        }
        return (
          <code style={{
            background: '#f0f9ff',
            color: '#0369a1',
            padding: '2px 6px',
            borderRadius: '4px',
            fontSize: '11px',
            whiteSpace: 'nowrap',
          }}>{v}</code>
        );
      };

      const notInBncColumns = [
        { key: 'word', label: 'Word', render: (v) => <code style={{ background: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>{v}</code> },
        { key: 'observed', label: 'Mentions', align: 'right' },
        { key: 'inWordnet', label: 'In WordNet', align: 'center', render: (v) => <WordnetBadge inWordnet={v} />, sortable: false },
        { key: 'inGngram', label: 'In Ngram', align: 'center', render: boolRender, sortable: false },
        { key: 'classification', label: 'Classification', render: classificationRender },
      ];

      const frequencyColumns = (isOverused) => [
        { key: 'word', label: 'Word', render: (v) => <code style={{ background: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>{v}</code> },
        { key: 'observed', label: 'Observed', align: 'right' },
        { key: 'expected', label: 'Expected', align: 'right', render: (v) => v !== null ? v.toFixed(2) : '—' },
        { key: 'ratio', label: 'Ratio', align: 'right', render: (v) => <RatioDisplay ratio={v} isOverused={isOverused} /> },
        { key: 'inWordnet', label: 'In WordNet', align: 'center', render: (v) => <WordnetBadge inWordnet={v} />, sortable: false },
        { key: 'inGngram', label: 'In Ngram', align: 'center', render: boolRender, sortable: false },
        { key: 'classification', label: 'Classification', render: classificationRender },
      ];

      const getTabContent = () => {
        switch (activeTab) {
          case 'overused':
            return (
              <DataTable
                data={overused}
                columns={frequencyColumns(true)}
                emptyMessage="No significantly overused words"
                filter={filter}
                onFilterChange={setFilter}
              />
            );
          case 'underused':
            return (
              <DataTable
                data={underused}
                columns={frequencyColumns(false)}
                emptyMessage="No significantly underused words"
                filter={filter}
                onFilterChange={setFilter}
              />
            );
          case 'notInBnc':
            return (
              <DataTable
                data={notInBnc}
                columns={notInBncColumns}
                emptyMessage="All words found in BNC"
                filter={filter}
                onFilterChange={setFilter}
              />
            );
        }
      };

      return (
        <div>
          <div style={{ marginBottom: '24px' }}>
            <h1 style={{ margin: '0 0 8px', fontSize: '24px', fontWeight: 600 }}>{title}</h1>
            {sourceFile && (
              <div style={{ fontSize: '14px', color: '#6b7280' }}>
                Source: <code style={{ background: '#f1f5f9', padding: '2px 6px', borderRadius: '4px' }}>{sourceFile}</code>
              </div>
            )}
          </div>

          <StatsCard stats={stats} activeTab={activeTab} onTabChange={handleTabChange} />

          <div className="card">
            <TabBar activeTab={activeTab} onTabChange={handleTabChange} stats={stats} />
            {getTabContent()}
          </div>

          <div style={{ marginTop: '24px', padding: '16px', background: '#f8fafc', borderRadius: '8px', fontSize: '12px', color: '#6b7280' }}>
            <strong>About this analysis:</strong> Word frequencies are compared against the British National Corpus (BNC),
            a 100-million word collection of British English. Ratios indicate how much more (or less) frequently
            a word appears in this text compared to typical usage. Words not in BNC may be proper nouns,
            technical terms, neologisms, or OCR errors.
          </div>
        </div>
      );
    }
    """

    extra_styles = (
        CARD_STYLES
        + """
    code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    table {
      font-variant-numeric: tabular-nums;
    }
    input:focus {
      outline: 2px solid #3b82f6;
      outline-offset: -1px;
    }
    tr:hover {
      background: #f8fafc;
    }
    """
    )

    html = generate_html_document(
        title=title,
        config=config,
        react_component=react_component,
        component_name="BNCFrequencyReport",
        extra_styles=extra_styles,
    )

    return write_html_file(output_file, html)

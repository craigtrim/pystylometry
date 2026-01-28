# pystylometry

[![PyPI version](https://badge.fury.io/py/pystylometry.svg)](https://badge.fury.io/py/pystylometry)
[![Downloads](https://pepy.tech/badge/pystylometry)](https://pepy.tech/project/pystylometry)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-1022%20passed-brightgreen)]()

Stylometric analysis and authorship attribution for Python. 50+ metrics across 11 modules, from vocabulary diversity to AI-generation detection.

## Install

```bash
pip install pystylometry              # Core (lexical metrics)
pip install pystylometry[all]         # Everything
```

<details>
<summary>Individual extras</summary>

```bash
pip install pystylometry[readability]   # Readability formulas (pronouncing, spaCy)
pip install pystylometry[syntactic]     # POS/parse analysis (spaCy)
pip install pystylometry[authorship]    # Attribution methods
pip install pystylometry[ngrams]        # N-gram entropy
pip install pystylometry[viz]           # Matplotlib visualizations
```
</details>

## Usage

```python
from pystylometry.lexical import compute_mtld, compute_yule
from pystylometry.readability import compute_flesch

result = compute_mtld(text)
print(result.mtld_average)       # 72.4

result = compute_flesch(text)
print(result.reading_ease)       # 65.2
print(result.grade_level)        # 8.1
```

Every function returns a typed dataclass with the score, components, and metadata -- never a bare float.

### Unified API

```python
from pystylometry import analyze

results = analyze(text, lexical=True, readability=True, syntactic=True)
```

### Style Drift Detection

Detect authorship changes, spliced content, and AI-generated text within a single document.

```python
from pystylometry.consistency import compute_kilgarriff_drift

result = compute_kilgarriff_drift(document)
print(result.pattern)             # "sudden_spike"
print(result.pattern_confidence)  # 0.71
print(result.max_location)        # Window 23 -- the splice point
```

### CLI

```bash
pystylometry-drift manuscript.txt --window-size=500 --stride=250
pystylometry-viewer report.html
```

## Modules

| Module | Metrics | Description |
|--------|---------|-------------|
| [**lexical**](pystylometry/lexical/) | TTR, MTLD, Yule's K/I, Hapax, MATTR, VocD-D, HD-D, MSTTR, function words, word frequency | Vocabulary diversity and richness |
| [**readability**](pystylometry/readability/) | Flesch, Flesch-Kincaid, SMOG, Gunning Fog, Coleman-Liau, ARI, Dale-Chall, Fry, FORCAST, Linsear Write, Powers-Sumner-Kearl | Grade-level and difficulty scoring |
| [**syntactic**](pystylometry/syntactic/) | POS ratios, sentence types, parse tree depth, clausal density, passive voice, T-units, dependency distance | Sentence and parse structure (requires spaCy) |
| [**authorship**](pystylometry/authorship/) | Burrows' Delta, Cosine Delta, Zeta, Kilgarriff chi-squared, MinMax, John's Delta, NCD | Author attribution and text comparison |
| [**stylistic**](pystylometry/stylistic/) | Contractions, hedges, intensifiers, modals, punctuation, vocabulary overlap (Jaccard/Dice/Cosine/KL), cohesion, genre/register | Style markers and text similarity |
| [**character**](pystylometry/character/) | Letter frequencies, digit/uppercase ratios, special characters, whitespace | Character-level fingerprinting |
| [**ngrams**](pystylometry/ngrams/) | Word/character/POS n-grams, Shannon entropy, skipgrams | N-gram profiles and entropy |
| [**dialect**](pystylometry/dialect/) | British/American classification, spelling/grammar/vocabulary markers, markedness | Regional dialect detection |
| [**consistency**](pystylometry/consistency/) | Sliding-window chi-squared drift, pattern classification | Intra-document style analysis |
| [**prosody**](pystylometry/prosody/) | Syllable stress, rhythm regularity | Prose rhythm (requires spaCy) |
| [**viz**](pystylometry/viz/) | Timeline, scatter, report (PNG + interactive HTML) | Drift detection visualization |

## Development

```bash
git clone https://github.com/craigtrim/pystylometry && cd pystylometry
pip install -e ".[dev,all]"
make test       # 1022 tests
make lint       # ruff + mypy
make all        # lint + test + build
```

## License

MIT

## Author

Craig Trim -- craigtrim@gmail.com

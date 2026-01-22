# pystylometry

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![PyPI version](https://badge.fury.io/py/pystylometry.svg)](https://badge.fury.io/py/pystylometry)

A comprehensive Python package for stylometric analysis with modular architecture and optional dependencies.

## Features

**pystylometry** provides 50+ metrics across five analysis domains:

- **Lexical Diversity**: TTR, MTLD, Yule's K, Hapax ratios, and more
- **Readability**: Flesch, SMOG, Gunning Fog, Coleman-Liau, ARI
- **Syntactic Analysis**: POS ratios, sentence statistics (requires spaCy)
- **Authorship Attribution**: Burrows' Delta, Cosine Delta, Zeta scores
- **N-gram Analysis**: Character and word bigram entropy, perplexity

## Installation

Install only what you need:

```bash
# Core package (lexical metrics only)
pip install pystylometry

# With readability metrics
pip install pystylometry[readability]

# With syntactic metrics (requires spaCy)
pip install pystylometry[syntactic]

# With authorship metrics
pip install pystylometry[authorship]

# With n-gram analysis
pip install pystylometry[ngrams]

# Everything
pip install pystylometry[all]
```

## Quick Start

### Using Individual Modules

```python
from pystylometry.lexical import compute_mtld, compute_yule
from pystylometry.readability import compute_flesch

text = "Your text here..."

# Lexical diversity
mtld = compute_mtld(text)
print(f"MTLD: {mtld.mtld_average:.2f}")

yule = compute_yule(text)
print(f"Yule's K: {yule.yule_k:.2f}")

# Readability
flesch = compute_flesch(text)
print(f"Reading Ease: {flesch.reading_ease:.1f}")
print(f"Grade Level: {flesch.grade_level:.1f}")
```

### Using the Unified API

```python
from pystylometry import analyze

text = "Your text here..."

# Analyze with multiple metrics at once
results = analyze(text, lexical=True, readability=True)

# Access results
print(f"MTLD: {results.lexical['mtld'].mtld_average:.2f}")
print(f"Flesch: {results.readability['flesch'].reading_ease:.1f}")
```

### Checking Available Modules

```python
from pystylometry import get_available_modules

available = get_available_modules()
print(available)
# {'lexical': True, 'readability': True, 'syntactic': False, ...}
```

## API Design

### Clean, Consistent Interface

Every metric function:
- Takes text as input
- Returns a rich result object (never just a float)
- Includes metadata about the computation
- Has comprehensive docstrings with formulas and references

```python
from pystylometry.lexical import compute_yule

result = compute_yule(text)
# Returns: YuleResult(yule_k=..., yule_i=..., metadata={...})
```

## Available Metrics

### Lexical Diversity
- **TTR** - Type-Token Ratio (via stylometry-ttr)
- **MTLD** - Measure of Textual Lexical Diversity
- **Yule's K** - Vocabulary repetitiveness
- **Hapax Legomena** - Words appearing once/twice
- **Sichel's S** - Hapax-based richness
- **Honoré's R** - Vocabulary richness constant

### Readability
- **Flesch Reading Ease** - 0-100 difficulty scale
- **Flesch-Kincaid Grade** - US grade level
- **SMOG Index** - Years of education needed
- **Gunning Fog** - NLP-enhanced readability complexity (see below)
- **Coleman-Liau** - Character-based grade level
- **ARI** - Automated Readability Index

#### Gunning Fog Index - NLP Enhancement

The Gunning Fog Index implementation includes advanced NLP features when spaCy is available:

**Enhanced Mode** (with spaCy):
- Accurate proper noun detection via POS tagging (PROPN)
- True morphological analysis via lemmatization
- Component-based hyphenated word analysis
- Handles edge cases: acronyms, irregular verbs, compound nouns

**Basic Mode** (without spaCy):
- Capitalization-based proper noun detection
- Simple suffix stripping for inflections (-es, -ed, -ing)
- Component-based hyphenated word analysis
- Works without external dependencies

```python
from pystylometry.readability import compute_gunning_fog

text = "Understanding computational linguistics requires significant dedication."
result = compute_gunning_fog(text)

print(f"Fog Index: {result.fog_index:.1f}")
print(f"Grade Level: {result.grade_level}")
print(f"Detection Mode: {result.metadata['mode']}")  # "enhanced" or "basic"
```

**To enable enhanced mode:**
```bash
pip install pystylometry[readability]
python -m spacy download en_core_web_sm
```

**Reference:** Gunning, R. (1952). The Technique of Clear Writing. McGraw-Hill.

**Implementation Details:** See [GitHub PR #4](https://github.com/craigtrim/pystylometry/pull/4) for the rationale behind NLP enhancements.

### Syntactic (requires spaCy)
- **POS Ratios** - Noun/verb/adjective/adverb ratios
- **Lexical Density** - Content vs function words
- **Sentence Statistics** - Length, variation, complexity

### Authorship (requires scikit-learn, scipy)
- **Burrows' Delta** - Author distance measure
- **Cosine Delta** - Angular distance
- **Zeta Scores** - Distinctive word usage

### N-grams (requires nltk)
- **Character Bigram Entropy** - Character predictability
- **Word Bigram Entropy** - Word sequence predictability
- **Perplexity** - Language model fit

## Dependencies

**Core (always installed):**
- stylometry-ttr

**Optional:**
- `readability`: pronouncing (syllable counting), spacy>=3.8.0 (NLP-enhanced Gunning Fog)
- `syntactic`: spacy>=3.8.0 (POS tagging and syntactic analysis)
- `authorship`: None (pure Python + stdlib)
- `ngrams`: None (pure Python + stdlib)

**Note:** spaCy is shared between `readability` and `syntactic` groups. For enhanced Gunning Fog accuracy, download a language model:
```bash
python -m spacy download en_core_web_sm  # Small model (13MB)
python -m spacy download en_core_web_md  # Medium model (better accuracy)
```

## Development

```bash
# Clone the repository
git clone https://github.com/craigtrim/pystylometry
cd pystylometry

# Install with dev dependencies
pip install -e ".[dev,all]"

# Run tests
make test

# Run linters
make lint

# Format code
make format
```

## Project Status

🚧 **Phase 1 - Core Lexical Metrics** (In Progress)
- [x] Project structure
- [ ] MTLD implementation
- [ ] Yule's K implementation
- [ ] Hapax ratios implementation
- [ ] Tests
- [ ] v0.1.0 release

See [pystylometry-plan.md](.claude/context/pystylometry-plan.md) for the full roadmap.

## Why pystylometry?

- **Modular**: Install only what you need
- **Consistent**: Uniform API across all metrics
- **Rich Results**: Dataclass objects with metadata, not just numbers
- **Well-Documented**: Formulas, references, and interpretations
- **Type-Safe**: Full type hints for IDE support
- **Tested**: Comprehensive test suite

## References

See [stylometry-metrics.md](.claude/context/stylometry-metrics.md) for the complete metrics reference table with formulas.

## License

MIT License - see LICENSE file for details.

## Author

Craig Trim (craigtrim@gmail.com)

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.

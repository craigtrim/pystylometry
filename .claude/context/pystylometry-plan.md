# pystylometry - Project Planning Document

## Overview

A comprehensive Python package for stylometric analysis with modular architecture and optional dependencies.

## Why `pystylometry`?

**Name Analysis:**
- `stylometry` exists but abandoned (2015, 11 years old)
- `stylometry-cli` just launched (Jan 16, 2026) - different use case
- `pystylometry` is:
  - Clean and professional
  - Clearly Python-specific
  - Won't conflict with CLI tool
  - Natural home for existing stylometry-ttr code

## Package Structure

```
pystylometry/
├── lexical/       # TTR, MTLD, Yule's K, Hapax ratios, etc.
├── readability/   # Flesch, SMOG, Gunning Fog, Coleman-Liau, ARI
├── syntactic/     # POS ratios, sentence metrics, clause density
├── authorship/    # Burrows' Delta, Zeta, Cosine Delta
└── ngrams/        # Entropy, perplexity, sequence analysis
```

## Installation Options

Users can install only what they need:

```bash
# Core package (lexical metrics only)
pip install pystylometry

# With readability metrics
pip install pystylometry[readability]

# With syntactic metrics (requires spaCy)
pip install pystylometry[syntactic]

# With authorship metrics
pip install pystylometry[authorship]

# Everything
pip install pystylometry[all]
```

## API Design

### Clean, Consistent Interface

```python
# Lexical metrics
from pystylometry.lexical import compute_ttr, compute_mtld, compute_yule

result = compute_ttr(text, chunk_size=1000, return_chunks=True)
# Returns: TTRResult with .sttr, .sttr_std, .chunk_ttrs

# Readability metrics
from pystylometry.readability import compute_flesch, compute_smog

flesch = compute_flesch(text)
# Returns: FleschResult with .score, .grade_level, .difficulty

# Syntactic metrics
from pystylometry.syntactic import compute_pos_ratios, compute_sentence_stats

pos = compute_pos_ratios(text)
# Returns: POSResult with .noun_ratio, .verb_ratio, etc.

# Authorship metrics
from pystylometry.authorship import compute_burrows_delta

delta = compute_burrows_delta(text1, text2, mfw=500)
# Returns: float (distance measure)
```

### Unified Interface (Optional)

```python
from pystylometry import analyze

# Compute all available metrics at once
results = analyze(text,
                  lexical=True,
                  readability=True,
                  syntactic=False,  # Skip if not installed
                  authorship=False)

print(results.lexical.ttr)
print(results.readability.flesch_score)
```

## Dependencies Strategy

### Core Dependencies (Always Installed)
- `numpy` - numerical operations
- `dataclasses` - result objects

### Optional Dependencies

**Readability Module:**
```toml
[project.optional-dependencies]
readability = [
    "pronouncing>=0.2.0",  # CMU dict for syllable counting
]
```

**Syntactic Module:**
```toml
syntactic = [
    "spacy>=3.0.0",
    "en-core-web-sm @ https://...",  # Or instructions to download
]
```

**Authorship Module:**
```toml
authorship = [
    "scikit-learn>=1.0.0",  # For cosine similarity
    "scipy>=1.7.0",         # For statistical tests
]
```

**N-grams Module:**
```toml
ngrams = [
    "nltk>=3.8.0",
]
```

**All:**
```toml
all = [
    "pronouncing>=0.2.0",
    "spacy>=3.0.0",
    "scikit-learn>=1.0.0",
    "scipy>=1.7.0",
    "nltk>=3.8.0",
]
```

## Migration from stylometry-ttr

### Option A: Merge and Deprecate
1. Copy `stylometry-ttr` code into `pystylometry.lexical`
2. Mark `stylometry-ttr` as deprecated on PyPI
3. Add note: "This package is now part of pystylometry"

### Option B: Keep Both (Recommended)
1. `stylometry-ttr` remains standalone and lightweight
2. `pystylometry` depends on `stylometry-ttr` for TTR functionality:
   ```python
   # pystylometry/lexical/__init__.py
   from stylometry_ttr import compute_ttr, TTRResult
   __all__ = ['compute_ttr', 'TTRResult', 'compute_mtld', ...]
   ```
3. Users who only want TTR still use `stylometry-ttr`
4. Users who want comprehensive metrics use `pystylometry`

**Benefits of Option B:**
- No breaking changes for stylometry-ttr users
- Clear separation of concerns
- Lightweight option still exists
- Natural upgrade path

## Project Structure

```
pystylometry/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── Makefile
├── src/
│   └── pystylometry/
│       ├── __init__.py
│       ├── lexical/
│       │   ├── __init__.py
│       │   ├── ttr.py          # Re-export from stylometry-ttr
│       │   ├── mtld.py
│       │   ├── yule.py
│       │   └── hapax.py
│       ├── readability/
│       │   ├── __init__.py
│       │   ├── flesch.py
│       │   ├── smog.py
│       │   ├── gunning_fog.py
│       │   └── syllables.py    # CMU dict wrapper
│       ├── syntactic/
│       │   ├── __init__.py
│       │   ├── pos_ratios.py
│       │   └── sentence_stats.py
│       ├── authorship/
│       │   ├── __init__.py
│       │   ├── burrows_delta.py
│       │   └── zeta.py
│       └── ngrams/
│           ├── __init__.py
│           └── entropy.py
├── tests/
│   ├── conftest.py
│   ├── test_lexical.py
│   ├── test_readability.py
│   ├── test_syntactic.py
│   ├── test_authorship.py
│   └── test_ngrams.py
└── docs/
    └── metrics-reference.md  # The comprehensive table
```

## Implementation Priority

### Phase 1: Core Lexical (Week 1)
- [x] Project setup
- [ ] Re-export `stylometry-ttr` functionality
- [ ] Implement MTLD
- [ ] Implement Yule's K
- [ ] Implement Hapax ratios
- [ ] Write tests
- [ ] Publish v0.1.0

### Phase 2: Readability (Week 2)
- [ ] CMU dict syllable counter with heuristic fallback
- [ ] Flesch Reading Ease
- [ ] Flesch-Kincaid Grade
- [ ] SMOG Index
- [ ] Gunning Fog Index
- [ ] Coleman-Liau Index
- [ ] ARI
- [ ] Write tests
- [ ] Publish v0.2.0

### Phase 3: Syntactic (Week 3-4)
- [ ] spaCy integration
- [ ] POS ratio calculations
- [ ] Sentence-level statistics
- [ ] Clause density (if feasible)
- [ ] Write tests
- [ ] Publish v0.3.0

### Phase 4: Authorship & N-grams (Week 5-6)
- [ ] Burrows' Delta
- [ ] Cosine Delta
- [ ] Zeta scores
- [ ] Character/word bigram entropy
- [ ] Write tests
- [ ] Publish v1.0.0

## Consistent Result Objects

All functions return rich result objects (never just floats):

```python
@dataclass
class TTRResult:
    sttr: float
    sttr_std: float
    overall_ttr: float
    chunk_ttrs: List[ChunkTTR]
    metadata: Dict[str, Any]

@dataclass
class FleschResult:
    reading_ease: float
    grade_level: float
    difficulty: str  # "Very Easy", "Easy", "Difficult", etc.
    metadata: Dict[str, Any]

@dataclass
class YuleResult:
    yule_k: float
    yule_i: float
    hapax_ratio: float
    metadata: Dict[str, Any]
```

## Documentation Strategy

1. **README.md**: Quick start, installation, basic examples
2. **docs/metrics-reference.md**: Comprehensive metrics table (already created)
3. **Docstrings**: Every function with formula, example, references
4. **API Reference**: Auto-generated from docstrings
5. **Tutorials**: Jupyter notebooks for common tasks

## Testing Strategy

- Unit tests for each metric
- Integration tests with real texts (Gutenberg corpus)
- Comparison tests against known implementations
- Edge case tests (empty text, single word, etc.)
- Performance benchmarks

## Code Quality

```makefile
# Makefile targets
lint:
    ruff check .
    mypy src/

test:
    pytest tests/ -v --cov=pystylometry

format:
    ruff format .

all: format lint test
```

## Key Design Principles

1. **Lightweight by default**: Core package has minimal dependencies
2. **Consistent API**: All functions follow same pattern
3. **Rich results**: Return objects with metadata, not just numbers
4. **Type hints**: Full type coverage for IDE support
5. **Tested**: High test coverage with real-world examples
6. **Documented**: Clear formulas, references, interpretations
7. **Fast**: Optimize hot paths, use NumPy efficiently
8. **Extensible**: Easy to add new metrics

## References to Include

For each metric, cite:
- Original paper/author
- Formula source
- Interpretation guidelines
- Known limitations
- Recommended use cases

Example docstring:

```python
def compute_yule(text: str) -> YuleResult:
    """
    Compute Yule's K and I metrics for vocabulary richness.

    Yule's K measures vocabulary repetitiveness (higher = more repetitive).
    Yule's I is the inverse measure (higher = more diverse).

    Formula:
        K = 10⁴ × (Σm²×Vm - N) / N²
        I = (V² / Σm²×Vm) - (1/N)

    Where:
        - N = total tokens
        - V = vocabulary size
        - Vm = number of types occurring m times

    References:
        Yule, G. U. (1944). The Statistical Study of Literary Vocabulary.
        Cambridge University Press.

    Args:
        text: Input text to analyze

    Returns:
        YuleResult with .yule_k, .yule_i, and metadata

    Example:
        >>> result = compute_yule("The quick brown fox...")
        >>> print(f"Yule's K: {result.yule_k:.2f}")
        >>> print(f"Yule's I: {result.yule_i:.2f}")
    """
```

## Success Metrics

- **v0.1.0**: 5 lexical metrics implemented
- **v0.2.0**: All readability metrics functional
- **v0.3.0**: Syntactic analysis with spaCy
- **v1.0.0**: Full suite with authorship & n-grams
- **100+ downloads/month** within 3 months
- **Used in at least one academic paper** within 6 months

## Questions to Resolve

1. Should we use spaCy or NLTK for POS tagging? (spaCy is more accurate but heavier)
2. Include visualization helpers or keep strictly computational?
3. Support for non-English texts in v1.0 or later?
4. CLI interface in main package or separate `pystylometry-cli`?

## Next Steps

1. Create GitHub repo: `craigtrim/pystylometry`
2. Initialize with `pyproject.toml`, Makefile, .gitignore
3. Set up project structure
4. Port Phase 1 metrics from stylometry-ttr
5. Write comprehensive tests
6. Publish v0.1.0 to PyPI

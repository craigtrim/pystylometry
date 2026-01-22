# pystylometry - Project Context

Use this context when starting work on the pystylometry project to understand the architecture, goals, and available metrics.

## Overview

A comprehensive Python package for stylometric analysis with modular architecture and optional dependencies.

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

```bash
# Core package (lexical metrics only)
pip install pystylometry

# With readability metrics
pip install pystylometry[readability]

# With syntactic metrics (requires spaCy)
pip install pystylometry[syntactic]

# Everything
pip install pystylometry[all]
```

## API Design

### Clean, Consistent Interface

Every metric function:
- Takes text as input
- Returns a rich result object (never just a float)
- Includes metadata about the computation
- Has comprehensive docstrings with formulas and references

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
from pystylometry.syntactic import compute_pos_ratios

pos = compute_pos_ratios(text)
# Returns: POSResult with .noun_ratio, .verb_ratio, etc.
```

### Unified Interface (Optional)

```python
from pystylometry import analyze

# Compute all available metrics at once
results = analyze(text, lexical=True, readability=True, syntactic=False)

print(results.lexical.ttr)
print(results.readability.flesch_score)
```

## Dependencies Strategy

### Core Dependencies
- `stylometry-ttr>=0.1.0` - TTR functionality

### Optional Dependencies

**Readability:** `pronouncing>=0.2.0` (CMU dict for syllable counting)
**Syntactic:** `spacy>=3.8.0,<3.9.0` (POS tagging and NLP)
**Authorship:** None (uses only core dependencies)
**N-grams:** None (pure Python implementation)

## Implementation Phases

### Phase 1: Core Lexical ✅
- [x] Project setup and structure
- [ ] MTLD implementation
- [ ] Yule's K implementation
- [ ] Hapax ratios implementation
- [ ] Tests and v0.1.0 release

### Phase 2: Readability
- Flesch Reading Ease & Flesch-Kincaid Grade
- SMOG Index, Gunning Fog Index
- Coleman-Liau Index, ARI

### Phase 3: Syntactic
- spaCy integration for POS tagging
- POS ratio calculations
- Sentence-level statistics

### Phase 4: Authorship & N-grams
- Burrows' Delta, Cosine Delta, Zeta scores
- Character/word bigram entropy
- Full v1.0.0 release

## Key Design Principles

1. **Lightweight by default**: Core package has minimal dependencies
2. **Consistent API**: All functions follow same pattern
3. **Rich results**: Return dataclass objects with metadata, not just numbers
4. **Type hints**: Full type coverage for IDE support
5. **Tested**: High test coverage with real-world examples
6. **Documented**: Clear formulas, references, interpretations
7. **Fast**: Optimize hot paths, use NumPy efficiently
8. **Extensible**: Easy to add new metrics

## Comprehensive Metrics Reference

### Lexical Richness

| Metric | Formula | Measures |
|--------|---------|----------|
| TTR (Type-Token Ratio) | V / N | Basic vocabulary diversity |
| Root TTR (Guiraud) | V / √N | Length-normalized diversity |
| Log TTR (Herdan) | log(V) / log(N) | Logarithmic diversity |
| STTR (Standardized TTR) | mean(TTR per chunk) | Chunk-averaged diversity |
| MSTTR | mean(TTR per 100 words) | Mean segmental diversity |
| Hapax Legomena Ratio | V₁ / N | Words appearing exactly once |
| Hapax Dislegomena Ratio | V₂ / N | Words appearing exactly twice |
| Sichel's S | V₂ / V | Ratio of dis- to total types |
| Honoré's R | 100 × log(N) / (1 - V₁/V) | Vocabulary richness constant |
| Brunet's W | N^(V^-0.172) | Length-independent richness |
| Yule's K | 10⁴ × (Σm²×Vm - N) / N² | Vocabulary repetitiveness |
| Yule's I | (V² / Σm²×Vm) - (1/N) | Inverse of Yule's K |
| Simpson's D | Σ(Vm × m × (m-1)) / (N × (N-1)) | Probability of repetition |
| MTLD | Mean length of TTR > threshold | Maintained lexical diversity |
| HD-D | Hypergeometric distribution D | Sample-size independent diversity |
| VOCD-D | Curve-fitted diversity | Robust vocabulary measure |

### Readability

| Metric | Formula | Measures |
|--------|---------|----------|
| Flesch Reading Ease | 206.835 - 1.015×ASL - 84.6×ASW | Text difficulty (0-100) |
| Flesch-Kincaid Grade | 0.39×ASL + 11.8×ASW - 15.59 | US grade level |
| Gunning Fog Index | 0.4 × (ASL + complex word %) | Years of education needed |
| SMOG Index | 1.043 × √(polysyllables × 30/sentences) + 3.1291 | Education years |
| Coleman-Liau Index | 0.0588×L - 0.296×S - 15.8 | Grade level |
| ARI | 4.71×(chars/words) + 0.5×(words/sentences) - 21.43 | Automated readability |

### Syntactic / POS

| Metric | Formula | Measures |
|--------|---------|----------|
| Noun Ratio | nouns / N | Nominal style |
| Verb Ratio | verbs / N | Action density |
| Adjective Ratio | adjectives / N | Descriptive density |
| Adverb Ratio | adverbs / N | Modification style |
| Noun-Verb Ratio | nouns / verbs | Static vs dynamic |
| Adjective-Noun Ratio | adjectives / nouns | Description density |
| Lexical Density | content words / total words | Information packaging |

### Sentence-Level

| Metric | Formula | Measures |
|--------|---------|----------|
| Mean Sentence Length | total words / sentence count | Syntactic complexity |
| Sentence Length Std | σ of sentence lengths | Sentence variation |
| Sentence Length Range | max - min sentence length | Stylistic range |
| Clause Density | clauses / sentences | Subordination complexity |
| T-Unit Length | words per T-unit | Minimal terminable unit |

### Authorship-Specific

| Metric | Formula | Measures |
|--------|---------|----------|
| Burrows' Delta | mean│z(f) - z(f')│ | Author distance |
| Cosine Delta | 1 - cos(z, z') | Angular author distance |
| Eder's Delta | Burrows' with culling | Noise-reduced delta |
| Zeta Score | marker / anti-marker balance | Distinctive word usage |

### N-gram / Sequence

| Metric | Formula | Measures |
|--------|---------|----------|
| Character Bigram Entropy | -Σ p(bg) × log₂(p(bg)) | Character predictability |
| Word Bigram Entropy | -Σ p(bg) × log₂(p(bg)) | Word sequence predictability |
| Trigram Perplexity | 2^H(trigrams) | Language model fit |

## Legend

- **N** = total tokens
- **V** = vocabulary size (unique types)
- **V₁** = hapax legomena count (words appearing once)
- **V₂** = hapax dislegomena count (words appearing twice)
- **Vm** = words occurring m times
- **ASL** = average sentence length
- **ASW** = average syllables per word
- **L** = letters per 100 words
- **S** = sentences per 100 words

## Example Docstring Format

All metric functions should follow this pattern:

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

## Testing Strategy

- Unit tests for each metric
- Integration tests with real texts
- Comparison tests against known implementations
- Edge case tests (empty text, single word, etc.)
- Performance benchmarks

## Development Workflow

```bash
# Run linters
make lint

# Run tests
make test

# Format code
make format

# All checks
make all
```

## Project Repository

GitHub: https://github.com/craigtrim/pystylometry
PyPI: https://pypi.org/project/pystylometry/

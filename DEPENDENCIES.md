# pystylometry Dependencies

## Lightweight Design Philosophy

**pystylometry** is designed to be lightweight and modular. Most functionality works with minimal dependencies.

## Core Dependencies (Always Required)

```toml
numpy>=1.20.0                # ~15 MB - Numerical operations
stylometry-ttr>=0.1.0        # ~50 KB - TTR metrics
fast-sentence-segment>=0.1.0 # Sentence segmentation (Issue #69)
```

**Total core install: ~15 MB**

**Note:** Issue #69 replaced custom regex sentence segmentation with fast-sentence-segment for better accuracy and reliability.

## What Works with Core Only

### ✅ Lexical Module (Core)
- TTR, MTLD, Yule's K, Hapax ratios
- **Dependencies:** numpy, stylometry-ttr

### ✅ Authorship Module (Core)
- Burrows' Delta, Cosine Delta, Zeta scores
- **Dependencies:** numpy only (no sklearn/scipy needed!)
- Pure numpy implementation of cosine similarity and z-scores

### ✅ N-grams Module (Core)
- Character/word bigram entropy, perplexity
- **Dependencies:** NONE - pure Python!
- No NLTK needed - we implement n-grams with simple sliding window

## Optional Dependencies

### 📖 Readability Module
```bash
pip install pystylometry[readability]
```
- **Adds:** pronouncing (CMU dictionary for syllable counting)
- **Size:** ~2 MB
- **Fallback:** Works without it using heuristic syllable counter

### 📊 Syntactic Module (Deferred)
```bash
pip install pystylometry[syntactic]
```
- **Adds:** spacy + language model
- **Size:** ~500 MB with en_core_web_sm
- **Note:** Only install if you need POS tagging

## Installation Examples

```bash
# Minimal (15 MB)
pip install pystylometry

# With readability (17 MB)
pip install pystylometry[readability]

# Everything (517 MB due to spaCy)
pip install pystylometry[all]
```

## Removed Dependencies

We **removed** these heavy dependencies:
- ❌ **NLTK** - Implemented our own n-gram generation
- ❌ **scikit-learn** - Implemented cosine similarity ourselves
- ❌ **scipy** - Used numpy for statistics

## Module Summary

| Module | Dependencies | Works with Core? |
|--------|-------------|------------------|
| `lexical` | numpy, stylometry-ttr | ✅ Yes |
| `readability` | pronouncing (optional) | ✅ Yes (with fallback) |
| `authorship` | numpy only | ✅ Yes |
| `ngrams` | None (pure Python) | ✅ Yes |
| `syntactic` | spacy | ❌ No (optional module) |

## Why This Matters

1. **Fast installs** - Core package installs in seconds
2. **Small Docker images** - ~15 MB base install
3. **No dependency conflicts** - Fewer packages = fewer issues
4. **Works anywhere** - Even in constrained environments
5. **Pay for what you use** - Only add spaCy if you need POS tagging

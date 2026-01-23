# Coleman-Liau Index

## Overview

The Coleman-Liau Index (CLI) is a readability metric that estimates the U.S. grade level needed to understand a text. Unlike other readability formulas that rely on syllable counting (like Flesch-Kincaid), Coleman-Liau uses character counts, making it computationally simpler and potentially more suitable for automated analysis.

## What It Measures

The Coleman-Liau Index measures text complexity based on:
- **Average letters per word** (character-based complexity)
- **Average sentences per 100 words** (sentence structure complexity)

Higher values indicate more complex text requiring a higher educational level to comprehend.

## Formula

```
CLI = 0.0588 × L - 0.296 × S - 15.8
```

Where:
- **L** = Average number of letters per 100 words
- **S** = Average number of sentences per 100 words

### Grade Level Interpretation

| CLI Score | Grade Level | Reading Level |
|-----------|-------------|---------------|
| 1-6 | Elementary | Very easy to read |
| 7-8 | Middle School | Easy to read |
| 9-12 | High School | Average difficulty |
| 13-16 | College | Difficult |
| 17+ | Graduate | Very difficult |

## When to Use Coleman-Liau

**Best suited for:**
- Automated text analysis (no syllable counting needed)
- Cross-language comparisons (character-based)
- Large-scale corpus analysis
- Technical writing assessment
- Educational material evaluation

**Advantages:**
- Fast computation (no syllable counting)
- Syllable-free character-based approach
- Reliable for technical content
- Good for automated systems

**Limitations:**
- May underestimate readability for texts with many short words
- Less sensitive to word complexity than syllable-based metrics
- Can be affected by abbreviations and acronyms
- Letter counts from raw text vs. tokenized word counts may diverge in edge cases (URLs, email addresses, special tokens)
- English-centric sentence splitting and Unicode assumptions limit cross-language use

## Usage

### Basic Example

```python
from pystylometry.readability import compute_coleman_liau

text = """
The Coleman-Liau Index was developed in 1975 by Meri Coleman and T. L. Liau.
It provides a readability score based on characters rather than syllables.
This makes it particularly useful for automated text analysis systems.
"""

result = compute_coleman_liau(text)

print(f"CLI Index: {result.cli_index:.2f}")
print(f"Grade Level: {result.grade_level}")
print(f"Metadata: {result.metadata}")
```

### Analyzing Different Text Types

```python
# Technical documentation
technical_text = """
The algorithm employs a convolutional neural network architecture
with residual connections to optimize gradient flow during backpropagation.
Hyperparameter tuning was conducted using Bayesian optimization.
"""

# Simple narrative
simple_text = """
The cat sat on the mat. It was a sunny day.
Birds sang in the trees. The cat was happy.
"""

tech_result = compute_coleman_liau(technical_text)
simple_result = compute_coleman_liau(simple_text)

print(f"Technical text grade level: {tech_result.grade_level}")
print(f"Simple text grade level: {simple_result.grade_level}")
```

### Batch Analysis

```python
documents = [
    "First document text here...",
    "Second document text here...",
    "Third document text here...",
]

results = [compute_coleman_liau(doc) for doc in documents]

for i, result in enumerate(results, 1):
    print(f"Document {i}: CLI={result.cli_index:.2f}, Grade={result.grade_level}")
```

## Return Value

The function returns a `ColemanLiauResult` dataclass with:

```python
@dataclass
class ColemanLiauResult:
    cli_index: float          # Coleman-Liau Index score
    grade_level: int          # U.S. grade level (rounded)
    metadata: dict[str, Any]  # Additional metrics
```

### Metadata Fields

The `metadata` dictionary includes:
- `sentence_count`: Number of sentences detected
- `word_count`: Number of words (tokens)
- `letter_count`: Total alphabetic characters
- `letters_per_100_words`: Average letters per 100 words (L)
- `sentences_per_100_words`: Average sentences per 100 words (S)
- `reliable`: Boolean heuristic based on validation study passage lengths (~100 words); not a hard minimum but shorter texts may behave differently

## Comparison with Other Metrics

### Coleman-Liau vs. Flesch-Kincaid

| Feature | Coleman-Liau | Flesch-Kincaid |
|---------|--------------|----------------|
| **Basis** | Character counts | Syllable counts |
| **Speed** | Fast | Slower |
| **Accuracy** | Good for technical text | Better for narrative |
| **Implementation** | Simple | More complex |

### When to Choose Coleman-Liau

Choose Coleman-Liau when:
- Processing large volumes of text
- Working with technical documentation
- Need fast, automated analysis
- Syllable counting is impractical
- Working with multiple languages

Choose other metrics when:
- Analyzing creative writing
- Need maximum accuracy for narrative text
- Syllable complexity is important
- Processing speed is not critical

## Academic Background

**Original Paper:**
Coleman, M., & Liau, T. L. (1975). *A computer readability formula designed for machine scoring.* Journal of Applied Psychology, 60(2), 283-284.

**Key Contributions:**
- First readability formula designed specifically for computer implementation
- Eliminated need for syllable counting in readability assessment
- Demonstrated that character-based metrics correlate well with reading difficulty

**Research Findings:**
- Correlates well with Flesch-Kincaid (r ≈ 0.90)
- Particularly accurate for grades 4-12
- Works well with technical and expository text

## Practical Applications

### 1. Educational Material Assessment

```python
# Evaluate if textbook matches target grade level
textbook_chapter = """..."""
result = compute_coleman_liau(textbook_chapter)

target_grade = 8
if abs(result.grade_level - target_grade) <= 1:
    print(f"✓ Text appropriate for grade {target_grade}")
else:
    print(f"✗ Text too {'complex' if result.grade_level > target_grade else 'simple'}")
```

### 2. Content Simplification Tracking

```python
# Track readability improvements during revision
original = "Original complex text..."
revised = "Simplified revised text..."

original_cli = compute_coleman_liau(original).cli_index
revised_cli = compute_coleman_liau(revised).cli_index

improvement = original_cli - revised_cli
print(f"Readability improved by {improvement:.1f} grade levels")
```

### 3. Quality Control for Technical Writing

```python
# Ensure documentation meets readability standards
max_acceptable_grade = 12

docs = ["doc1.txt", "doc2.txt", "doc3.txt"]
for doc_path in docs:
    with open(doc_path) as f:
        text = f.read()

    result = compute_coleman_liau(text)

    # Check reliability threshold
    if not result.metadata["reliable"]:
        print(f"⚠ {doc_path}: Text too short (< 100 words) for reliable results")
        continue

    if result.grade_level > max_acceptable_grade:
        print(f"⚠ {doc_path}: Grade {result.grade_level} (too complex)")
```

## Best Practices

1. **Use adequate sample size**: Validation studies used ~100-word passages; shorter texts may deviate from expected behavior
2. **Consider audience**: Match grade level to your target readers
3. **Combine with other metrics**: Use alongside Flesch-Kincaid or SMOG for validation
4. **Account for context**: Technical terms may inflate scores appropriately
5. **Test with target audience**: Validate automated scores with real reader feedback

## Related Metrics

- [Flesch-Kincaid Grade Level](flesch.md) - Syllable-based readability
- [SMOG Index](smog.md) - Focuses on polysyllabic words
- [Gunning Fog Index](gunning_fog.md) - Emphasizes complex words
- [ARI (Automated Readability Index)](ari.md) - Another character-based metric

## References

1. Coleman, M., & Liau, T. L. (1975). A computer readability formula designed for machine scoring. *Journal of Applied Psychology*, 60(2), 283-284.

2. Kincaid, J. P., Fishburne Jr, R. P., Rogers, R. L., & Chissom, B. S. (1975). *Derivation of new readability formulas for Navy enlisted personnel*. Research Branch Report 8-75, Naval Technical Training Command.

3. DuBay, W. H. (2004). *The Principles of Readability*. Impact Information, Costa Mesa, California.

4. Benjamin, R. G. (2012). Reconstructing readability: Recent developments and recommendations in the analysis of text difficulty. *Educational Psychology Review*, 24(1), 63-88.

## See Also

- [pystylometry documentation](../README.md)
- [Readability metrics overview](readability_overview.md)
- [API Reference](../README.md#api-reference)

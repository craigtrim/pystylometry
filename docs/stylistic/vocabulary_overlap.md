# Vocabulary Overlap and Similarity Metrics

## Measuring Lexical Similarity Between Texts

Vocabulary overlap metrics quantify how similar two texts are based on their word usage. These measures are fundamental to stylometry, enabling comparison of authorial vocabulary, detection of shared sources, and identification of stylistic shifts between documents.

---

## Theoretical Background

### Origins

Vocabulary similarity measures draw from multiple disciplines:

- **Set Theory**: Jaccard's index (1912) originated in botanical ecology for comparing species distributions, later adopted for text comparison.
- **Information Retrieval**: Cosine similarity became standard for document comparison in vector space models (Salton & McGill 1983).
- **Information Theory**: Kullback-Leibler divergence (1951) measures how one probability distribution differs from another, useful for comparing word frequency distributions.

### Why Vocabulary Overlap Matters

**Authorial fingerprints**: Authors develop characteristic vocabularies over their careers. Comparing vocabulary overlap between texts can reveal shared authorship or influence.

**Source detection**: High vocabulary overlap between texts may indicate shared sources, plagiarism, or direct influence.

**Style drift**: Changes in vocabulary overlap between sections of a single work can reveal ghostwriting, collaboration, or stylistic evolution.

**Genre and register**: Different genres employ different vocabularies. Overlap metrics help quantify these differences.

---

## Metrics

### Jaccard Similarity

The Jaccard index measures the proportion of shared vocabulary relative to total vocabulary:

```
J(A, B) = |A ∩ B| / |A ∪ B|
```

Where A and B are the vocabulary sets of two texts.

- **Range**: 0.0 (no overlap) to 1.0 (identical vocabulary)
- **Properties**: Symmetric, intuitive interpretation
- **Best for**: Binary presence/absence comparison

### Sorensen-Dice Coefficient

The Dice coefficient gives more weight to shared terms:

```
D(A, B) = 2|A ∩ B| / (|A| + |B|)
```

- **Range**: 0.0 to 1.0
- **Properties**: Symmetric, always >= Jaccard for same data
- **Best for**: When shared vocabulary is more important than differences

### Overlap Coefficient

The overlap coefficient normalizes by the smaller vocabulary:

```
O(A, B) = |A ∩ B| / min(|A|, |B|)
```

- **Range**: 0.0 to 1.0
- **Properties**: Symmetric, handles size disparities well
- **Best for**: Comparing texts of very different lengths

### Cosine Similarity

Cosine similarity treats texts as frequency vectors and measures the angle between them:

```
cos(θ) = (A · B) / (||A|| × ||B||)
```

Where A and B are word frequency vectors.

- **Range**: 0.0 to 1.0 (for non-negative frequencies)
- **Properties**: Symmetric, considers word frequency
- **Best for**: When frequency matters, not just presence

### Kullback-Leibler Divergence

KL divergence measures how the word distribution of one text differs from another:

```
D_KL(P || Q) = Σ P(x) log(P(x) / Q(x))
```

- **Range**: 0.0 to infinity
- **Properties**: Asymmetric (order matters), requires smoothing for unseen words
- **Best for**: Detecting directional distributional differences

---

## Implementation

### API

```python
from pystylometry.stylistic import compute_vocabulary_overlap

result = compute_vocabulary_overlap(text1, text2)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text1` | str | required | First text to compare |
| `text2` | str | required | Second text to compare |
| `top_distinctive` | int | 20 | Number of distinctive words to return |

### Result Fields

**Similarity scores (0-1 range):**
- `jaccard_similarity`: Intersection / union
- `dice_coefficient`: 2 * intersection / (size1 + size2)
- `overlap_coefficient`: Intersection / min(size1, size2)
- `cosine_similarity`: Cosine of frequency vectors
- `kl_divergence`: Kullback-Leibler divergence (asymmetric, text1 || text2)

**Vocabulary sizes:**
- `text1_vocab_size`: Unique words in text 1
- `text2_vocab_size`: Unique words in text 2
- `shared_vocab_size`: Words appearing in both texts
- `union_vocab_size`: Words appearing in either text
- `text1_unique_count`: Words only in text 1
- `text2_unique_count`: Words only in text 2

**Ratios:**
- `shared_ratio`: Proportion of union that is shared
- `text1_unique_ratio`: Proportion unique to text 1
- `text2_unique_ratio`: Proportion unique to text 2

**Word lists:**
- `shared_words`: List of words in both texts
- `text1_distinctive_words`: Most distinctive words for text 1 (by TF-IDF)
- `text2_distinctive_words`: Most distinctive words for text 2 (by TF-IDF)

**Metadata:**
- `text1_word_count`: Total words in text 1
- `text2_word_count`: Total words in text 2
- `computation_time`: Time to compute metrics

---

## Example Usage

### Basic Comparison

```python
from pystylometry.stylistic import compute_vocabulary_overlap

text1 = """
The detective examined the crime scene carefully. He noted the
broken window, the scattered papers, and the missing jewelry.
"""

text2 = """
The investigator inspected the crime scene thoroughly. She observed
the shattered glass, the strewn documents, and the stolen valuables.
"""

result = compute_vocabulary_overlap(text1, text2)

print(f"Jaccard similarity: {result.jaccard_similarity:.3f}")
print(f"Cosine similarity: {result.cosine_similarity:.3f}")
print(f"Shared vocabulary: {result.shared_vocab_size} words")
print(f"Shared words: {result.shared_words[:10]}")
```

### Detecting Authorial Similarity

```python
# Compare known author samples
author_a_sample1 = "..."
author_a_sample2 = "..."
author_b_sample = "..."

# Same author should have higher overlap
same_author = compute_vocabulary_overlap(author_a_sample1, author_a_sample2)
diff_author = compute_vocabulary_overlap(author_a_sample1, author_b_sample)

print(f"Same author Jaccard: {same_author.jaccard_similarity:.3f}")
print(f"Different author Jaccard: {diff_author.jaccard_similarity:.3f}")
```

### Finding Distinctive Vocabulary

```python
result = compute_vocabulary_overlap(text1, text2, top_distinctive=10)

print("Words distinctive to Text 1:")
for word, score in result.text1_distinctive_words:
    print(f"  {word}: {score:.4f}")

print("Words distinctive to Text 2:")
for word, score in result.text2_distinctive_words:
    print(f"  {word}: {score:.4f}")
```

### Asymmetric Analysis with KL Divergence

```python
# KL divergence is asymmetric - order matters
result_forward = compute_vocabulary_overlap(text1, text2)
result_reverse = compute_vocabulary_overlap(text2, text1)

print(f"KL(text1 || text2): {result_forward.kl_divergence:.4f}")
print(f"KL(text2 || text1): {result_reverse.kl_divergence:.4f}")

# Symmetric metrics should be equal
assert result_forward.jaccard_similarity == result_reverse.jaccard_similarity
```

---

## Interpreting Results

### Similarity Score Ranges

| Score Range | Interpretation |
|-------------|----------------|
| 0.0 - 0.2 | Very different vocabulary |
| 0.2 - 0.4 | Some overlap, different styles/topics |
| 0.4 - 0.6 | Moderate overlap, similar domain |
| 0.6 - 0.8 | High overlap, likely same author or genre |
| 0.8 - 1.0 | Very high overlap, possible same source |

### When to Use Each Metric

| Metric | Use Case |
|--------|----------|
| Jaccard | General similarity, equal weighting |
| Dice | Emphasize shared vocabulary |
| Overlap | Compare texts of different lengths |
| Cosine | When word frequency matters |
| KL Divergence | Directional comparison, distribution shift |

---

## Applications

### Plagiarism Detection

High vocabulary overlap combined with similar word frequencies suggests copying or close paraphrasing:

```python
if result.jaccard_similarity > 0.7 and result.cosine_similarity > 0.8:
    print("Warning: High similarity detected")
```

### Style Drift Detection

Compare consecutive sections of a document to detect authorial changes:

```python
sections = split_into_sections(document)
for i in range(len(sections) - 1):
    overlap = compute_vocabulary_overlap(sections[i], sections[i+1])
    if overlap.jaccard_similarity < 0.3:
        print(f"Potential style shift between sections {i} and {i+1}")
```

### Authorship Verification

Create vocabulary profiles for known authors and compare:

```python
# Build author vocabulary profile from known works
known_works = [work1, work2, work3]
questioned_work = "..."

# Compare questioned work against known works
similarities = [
    compute_vocabulary_overlap(known, questioned_work).cosine_similarity
    for known in known_works
]
avg_similarity = sum(similarities) / len(similarities)
```

---

## Mathematical Properties

### Symmetric Metrics

Jaccard, Dice, Overlap coefficient, and Cosine similarity are symmetric:
- `f(A, B) = f(B, A)`

### Asymmetric Metrics

KL divergence is asymmetric:
- `D_KL(P || Q) != D_KL(Q || P)` in general

This asymmetry can be useful for detecting directional relationships, such as "text A uses vocabulary from text B" vs. "text B uses vocabulary from text A."

### Relationship Between Metrics

For any two texts:
- `Jaccard <= Dice` (Dice always >= Jaccard)
- `Overlap >= Jaccard` (when vocabularies differ in size)
- All metrics equal 1.0 for identical texts
- All set-based metrics equal 0.0 for disjoint vocabularies

---

## References

Jaccard, P. (1912). The distribution of the flora in the alpine zone. New Phytologist, 11(2), 37-50.

Sorensen, T. (1948). A method of establishing groups of equal amplitude in plant sociology based on similarity of species. Kongelige Danske Videnskabernes Selskab, 5(4), 1-34.

Salton, G., & McGill, M. J. (1983). Introduction to Modern Information Retrieval. McGraw-Hill.

Kullback, S., & Leibler, R. A. (1951). On Information and Sufficiency. Annals of Mathematical Statistics, 22(1), 79-86.

Manning, C. D., & Schutze, H. (1999). Foundations of Statistical Natural Language Processing. MIT Press.

# Hapax Legomena and Related Metrics

## Vocabulary Richness Through Rare Word Analysis

Hapax legomena -- words appearing exactly once in a text -- are among the most informative indicators of vocabulary richness and authorial style. This module computes hapax-based metrics including Sichel's S and Honore's R, with optional lexicon-based categorization that distinguishes neologisms from rare but established vocabulary.

---

## Theoretical Background

### Origins

The term "hapax legomenon" (plural: hapax legomena) derives from Greek, meaning "said once." In classical philology, hapax legomena were catalogued as rare textual occurrences that posed translation challenges. The transition to quantitative analysis came with the recognition that the proportion of once-occurring words in a text provides a stable, discriminating feature for authorship attribution.

Sichel (1975) formalized the relationship between dislegomena (words appearing exactly twice) and vocabulary size, while Honore (1979) developed a logarithmic measure that specifically highlights the role of hapax legomena relative to text length and vocabulary size.

### Mathematical Foundation

Define:
- `N` = total number of tokens
- `V` = vocabulary size (unique types)
- `V_1` = number of hapax legomena (types appearing exactly once)
- `V_2` = number of hapax dislegomena (types appearing exactly twice)

**Hapax Ratio:**

```
Hapax Ratio = V_1 / N
```

The proportion of the text occupied by once-occurring words.

**Dislegomena Ratio:**

```
Dislegomena Ratio = V_2 / N
```

The proportion of the text occupied by twice-occurring words.

**Sichel's S:**

```
S = V_2 / V
```

The proportion of the vocabulary that consists of dislegomena. Sichel demonstrated that this ratio is remarkably stable across texts by the same author and varies systematically between authors.

**Honore's R:**

```
R = 100 * log(N) / (1 - V_1 / V)
```

Honore's statistic integrates text length (N), vocabulary richness (V), and hapax proportion (V_1/V). Higher R values indicate richer vocabulary. When `V_1 = V` (all words are unique), R is infinite, indicating maximum vocabulary richness.

### Interpretation

| Metric | Low Value | High Value |
|--------|-----------|------------|
| Hapax Ratio | Few unique words (repetitive text) | Many unique words (diverse text) |
| Sichel's S | Few dislegomena relative to vocabulary | Many dislegomena relative to vocabulary |
| Honore's R | Limited vocabulary range | Rich, varied vocabulary |

Typical hapax ratios:
- **Short texts (< 500 words)**: 0.40-0.60
- **Medium texts (500-5000 words)**: 0.30-0.50
- **Long texts (> 5000 words)**: 0.20-0.40

### Lexicon-Based Analysis

The optional lexicon analysis extends standard hapax metrics by categorizing each hapax legomenon using external lexical resources:

1. **Neologisms**: Words absent from both WordNet and the British National Corpus (BNC). These represent true novel words, proper nouns, or domain-specific terminology not captured by general lexicons.

2. **Rare words**: Words present in one lexicon but not the other. These are at the edges of standard vocabulary -- technical terms, archaic words, or specialized jargon.

3. **Common words**: Words present in both WordNet and BNC. These are standard vocabulary items that happen to appear only once in the text (incidental hapax).

This three-way categorization distinguishes vocabulary innovation (neologisms) from incidental low-frequency usage (common hapax), providing a more nuanced picture of authorial vocabulary.

---

## Implementation

### Core Algorithm

Two functions are provided: one for standard hapax metrics and one with optional lexicon analysis.

```python
def compute_hapax_ratios(text: str, chunk_size: int = 1000) -> HapaxResult
def compute_hapax_with_lexicon_analysis(text: str) -> HapaxLexiconResult
```

**Standard hapax algorithm:**

1. Chunk the input text into segments of `chunk_size` words
2. For each chunk:
   a. Tokenize and lowercase the text
   b. Count frequency of each token
   c. Count V_1 (frequency = 1) and V_2 (frequency = 2)
   d. Compute Sichel's S = V_2 / V
   e. Compute Honore's R = 100 * log(N) / (1 - V_1/V)
3. Build Distribution objects from per-chunk values

**Lexicon analysis algorithm:**

1. Compute standard hapax metrics using `compute_hapax_ratios`
2. Identify all hapax legomena words
3. For each hapax word, check presence in WordNet and BNC
4. Categorize as neologism, rare, or common
5. Compute category ratios

### Key Features

1. **Comprehensive metrics**: Hapax count, ratio, dislegomena, Sichel's S, and Honore's R in a single call
2. **Chunked analysis**: Native chunking captures variance for stylometric fingerprinting
3. **Honore's R edge case handling**: When all words are unique (V_1 = V), returns infinity rather than raising an error; tracks infinite-value chunks separately
4. **Optional lexicon analysis**: WordNet + BNC categorization for deeper vocabulary characterization
5. **Sorted output**: Lexicon categories are alphabetically sorted for deterministic results

### Return Types

**HapaxResult** dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `hapax_count` | `int` | Total hapax legomena across all chunks |
| `hapax_ratio` | `float` | Mean hapax ratio (V_1/N) across chunks |
| `dis_hapax_count` | `int` | Total dislegomena across all chunks |
| `dis_hapax_ratio` | `float` | Mean dislegomena ratio (V_2/N) across chunks |
| `sichel_s` | `float` | Mean Sichel's S (V_2/V) across chunks |
| `honore_r` | `float` | Mean Honore's R across chunks |
| `hapax_ratio_dist` | `Distribution` | Distribution of hapax ratios |
| `dis_hapax_ratio_dist` | `Distribution` | Distribution of dislegomena ratios |
| `sichel_s_dist` | `Distribution` | Distribution of Sichel's S values |
| `honore_r_dist` | `Distribution` | Distribution of Honore's R values |
| `chunk_size` | `int` | Words per chunk |
| `chunk_count` | `int` | Number of chunks processed |
| `metadata` | `dict` | Total token count, vocabulary size |

**HapaxLexiconResult** dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `hapax_result` | `HapaxResult` | Standard hapax metrics |
| `lexicon_analysis` | `LexiconCategories` | Neologisms, rare words, common words with ratios |
| `metadata` | `dict` | Lexicons used, categorization notes |

---

## Usage

### API Examples

**Standard hapax analysis:**

```python
from pystylometry.lexical import compute_hapax_ratios

result = compute_hapax_ratios(text, chunk_size=1000)

print(f"Hapax count: {result.hapax_count}")
print(f"Hapax ratio: {result.hapax_ratio:.3f}")
print(f"Dislegomena count: {result.dis_hapax_count}")
print(f"Sichel's S: {result.sichel_s:.3f}")
print(f"Honore's R: {result.honore_r:.1f}")
```

**Chunked fingerprinting:**

```python
result = compute_hapax_ratios(long_text, chunk_size=500)

print(f"Hapax ratio mean: {result.hapax_ratio_dist.mean:.3f}")
print(f"Hapax ratio std: {result.hapax_ratio_dist.std:.3f}")
print(f"Sichel's S std: {result.sichel_s_dist.std:.3f}")
print(f"Chunks: {result.chunk_count}")
```

**Lexicon-based analysis (requires bnc-lookup and wordnet-lookup):**

```python
from pystylometry.lexical import compute_hapax_with_lexicon_analysis

result = compute_hapax_with_lexicon_analysis(text)

# Standard metrics
print(f"Hapax count: {result.hapax_result.hapax_count}")
print(f"Honore's R: {result.hapax_result.honore_r:.1f}")

# Lexicon categorization
lexicon = result.lexicon_analysis
print(f"Neologisms: {lexicon.neologisms[:5]}")
print(f"Rare words: {lexicon.rare_words[:5]}")
print(f"Common hapax: {lexicon.common_words[:5]}")
print(f"Neologism ratio: {lexicon.neologism_ratio:.2%}")
print(f"Rare word ratio: {lexicon.rare_word_ratio:.2%}")
```

**Comparing authors:**

```python
result_a = compute_hapax_ratios(text_a)
result_b = compute_hapax_ratios(text_b)

# Higher Honore's R = richer vocabulary
print(f"Author A Honore's R: {result_a.honore_r:.1f}")
print(f"Author B Honore's R: {result_b.honore_r:.1f}")

# Higher Sichel's S = more words appearing exactly twice
print(f"Author A Sichel's S: {result_a.sichel_s:.3f}")
print(f"Author B Sichel's S: {result_b.sichel_s:.3f}")
```

---

## Limitations

1. **Text length sensitivity**: Hapax ratio systematically decreases with text length because longer texts provide more opportunities for word repetition. Comparisons should use texts of similar length or rely on Honore's R which partially normalizes for length.

2. **Honore's R singularity**: When all words are unique (V_1 = V), Honore's R is infinite. This commonly occurs with very short texts and complicates statistical aggregation.

3. **Lexicon coverage**: The optional lexicon analysis depends on WordNet and BNC coverage. Domain-specific terminology, proper nouns, and recently coined words may be miscategorized as neologisms.

4. **Language dependence**: Hapax metrics assume English-language text for the lexicon analysis component. Standard hapax ratios work across languages but typical ranges differ.

5. **Tokenization effects**: Case normalization and punctuation handling affect which words are counted as hapax. The implementation lowercases all text, so "The" and "the" are treated as the same type.

6. **No morphological analysis**: Inflected forms (run, runs, running) are treated as separate types. Lemmatization would reduce hapax counts but provide different stylometric signals.

---

## References

- Sichel, H. S. (1975). On a distribution law for word frequencies. *Journal of the American Statistical Association*, 70(351a), 542-547.
- Honore, A. (1979). Some simple measures of richness of vocabulary. *Association for Literary and Linguistic Computing Bulletin*, 7, 172-177.
- Baayen, R. H. (2001). *Word Frequency Distributions*. Kluwer Academic Publishers.
- Popescu, I.-I., & Altmann, G. (2006). Some aspects of word frequencies. *Glottometrics*, 13, 23-46.
- British National Corpus Consortium. (2007). *The British National Corpus, version 3 (BNC XML Edition)*. http://www.natcorp.ox.ac.uk/
- Princeton University. (2010). *WordNet: A Lexical Database for English*. https://wordnet.princeton.edu/

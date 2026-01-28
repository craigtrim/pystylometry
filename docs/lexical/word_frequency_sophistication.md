# Word Frequency Sophistication

## Measuring Vocabulary Sophistication Through Corpus-Based Frequency Analysis

Word frequency sophistication quantifies how common or rare the words in a text are by comparing them against reference frequency lists from large corpora. Authors who consistently use less frequent, more specialized vocabulary score higher on sophistication metrics, making this a powerful indicator of register, expertise, and writing quality.

---

## Theoretical Background

### Origins

The study of word frequency in relation to vocabulary sophistication draws on a long tradition in corpus linguistics. Brysbaert and New (2009) demonstrated that word frequency norms derived from large, contemporary corpora provide superior predictions of lexical processing than earlier frequency counts. Their work established the importance of using modern, representative frequency lists for vocabulary assessment.

Coxhead (2000) complemented frequency-based analysis with the Academic Word List (AWL), a curated inventory of 570 word families that occur frequently across academic disciplines but are relatively uncommon in general English. The AWL has become a standard tool for assessing academic vocabulary knowledge and writing sophistication.

The combination of corpus frequency ranks and curated academic word lists provides a two-dimensional picture of vocabulary sophistication: frequency analysis reveals the general rarity profile, while AWL coverage reveals academic register alignment.

### Mathematical Foundation

**Frequency rank assignment:**

Each word in the text is mapped to its frequency rank in a reference corpus (e.g., COCA). Lower rank = more common.

```
rank(w) = position of w in corpus frequency list
```

Words not found in the reference corpus are assigned a default high rank (50,000), treating them as very rare.

**Mean and median frequency rank:**

```
Mean Rank = (1/N) * sum(rank(w_i)) for i = 1 to N
Median Rank = median of {rank(w_1), ..., rank(w_N)}
```

Lower mean/median rank indicates more common vocabulary; higher values indicate more sophisticated vocabulary.

**Frequency band distribution:**

Words are classified into bands based on their corpus rank:

| Band | Rank Range | Description |
|------|-----------|-------------|
| Very Common | 1-1,000 | Top 1% (function words, basic verbs) |
| Common | 1,001-5,000 | Top 5% (everyday vocabulary) |
| Moderate | 5,001-10,000 | Top 10% (educated vocabulary) |
| Rare | 10,001-20,000 | Top 20% (specialized vocabulary) |
| Very Rare | 20,001+ | Bottom 80% (domain-specific, technical) |

**Rare word ratio:**

```
Rare Ratio = count(words with rank > rare_threshold) / N
```

**Common word ratio:**

```
Common Ratio = count(words with rank <= common_threshold) / N
```

**Academic word ratio:**

```
Academic Ratio = count(words in AWL) / N
```

**Advanced word ratio:**

```
Advanced Ratio = count(words that are rare OR academic) / N
```

This union metric captures vocabulary that is either statistically rare in general English or characteristic of academic discourse.

### Interpretation

| Metric | Low Value | High Value |
|--------|-----------|------------|
| Mean frequency rank | Common vocabulary (accessible writing) | Rare vocabulary (sophisticated writing) |
| Rare word ratio | Simple, accessible prose | Complex, specialized prose |
| Academic word ratio | Non-academic register | Academic/formal register |
| Advanced word ratio | Basic vocabulary | Elevated vocabulary |

Typical profiles by genre:

| Genre | Mean Rank | Rare Ratio | Academic Ratio |
|-------|-----------|------------|----------------|
| Children's fiction | 500-2,000 | 0.05-0.15 | 0.01-0.03 |
| Journalism | 2,000-5,000 | 0.10-0.25 | 0.03-0.08 |
| Literary fiction | 3,000-8,000 | 0.15-0.30 | 0.05-0.10 |
| Academic writing | 5,000-15,000 | 0.20-0.40 | 0.10-0.20 |
| Technical/scientific | 8,000-25,000 | 0.30-0.50 | 0.15-0.25 |

---

## Implementation

### Core Algorithm

```python
def compute_word_frequency_sophistication(
    text: str,
    frequency_corpus: str = "coca",
    rare_threshold: int = 10000,
    common_threshold: int = 1000,
    chunk_size: int = 1000,
) -> WordFrequencySophisticationResult
```

**Algorithm steps:**

1. Tokenize the text (lowercase, strip punctuation)
2. Look up each word in the embedded COCA frequency dictionary
3. Assign rank 50,000 to unknown words (treated as very rare)
4. Compute mean and median frequency ranks
5. Count words in frequency bands (very common, common, moderate, rare, very rare)
6. Count words matching the Academic Word List (AWL)
7. Compute all ratios (rare, common, academic, advanced)
8. Identify the 10 rarest and 10 most common unique words
9. Wrap results in Distribution objects

### Reference Data

**COCA Frequency Ranks**: An embedded subset of the Corpus of Contemporary American English, mapping approximately 1,500 words to their frequency ranks. This covers the most common English words and a selection of academic/specialized vocabulary. Words outside this list receive rank 50,000.

**Academic Word List (AWL)**: An embedded subset of Coxhead's (2000) Academic Word List containing approximately 550 word forms covering the 570 AWL word families. This list captures field-independent academic vocabulary that appears across disciplines.

### Key Features

1. **Dual analysis dimensions**: Both corpus frequency and academic word coverage
2. **Five-band frequency distribution**: Very common through very rare, providing a detailed frequency profile
3. **Configurable thresholds**: Rare and common thresholds are adjustable for different applications
4. **Top/bottom word identification**: Reports the 10 rarest and 10 most common unique words
5. **Distribution objects**: All key metrics wrapped in Distribution for fingerprinting
6. **Unknown word tracking**: Metadata reports count and ratio of out-of-vocabulary words

### Return Type

`WordFrequencySophisticationResult` dataclass:

| Field | Type | Description |
|-------|------|-------------|
| `mean_frequency_rank` | `float` | Average frequency rank across all tokens |
| `median_frequency_rank` | `float` | Median frequency rank |
| `rare_word_ratio` | `float` | Proportion of tokens above rare threshold |
| `common_word_ratio` | `float` | Proportion of tokens below common threshold |
| `academic_word_ratio` | `float` | Proportion of tokens in AWL |
| `advanced_word_ratio` | `float` | Proportion of tokens that are rare OR academic |
| `frequency_band_distribution` | `dict` | Proportions in each frequency band |
| `rarest_words` | `list[tuple]` | Top 10 rarest (word, rank) pairs |
| `most_common_words` | `list[tuple]` | Top 10 most common (word, rank) pairs |
| `*_dist` fields | `Distribution` | Distribution for each metric |
| `metadata` | `dict` | Corpus info, thresholds, word counts |

---

## Usage

### API Examples

**Basic usage:**

```python
from pystylometry.lexical import compute_word_frequency_sophistication

result = compute_word_frequency_sophistication(
    "The empirical analysis demonstrates significant methodological implications."
)

print(f"Mean frequency rank: {result.mean_frequency_rank:.1f}")
print(f"Median frequency rank: {result.median_frequency_rank:.1f}")
print(f"Rare word ratio: {result.rare_word_ratio:.3f}")
print(f"Academic word ratio: {result.academic_word_ratio:.3f}")
print(f"Advanced word ratio: {result.advanced_word_ratio:.3f}")
```

**Frequency band analysis:**

```python
result = compute_word_frequency_sophistication(text)

for band, proportion in result.frequency_band_distribution.items():
    print(f"  {band}: {proportion:.1%}")

# Example output:
#   very_common: 45.2%
#   common: 20.1%
#   moderate: 8.3%
#   rare: 3.7%
#   very_rare: 22.7%
```

**Examining rarest and most common words:**

```python
result = compute_word_frequency_sophistication(text)

print("Rarest words:")
for word, rank in result.rarest_words:
    print(f"  {word}: rank {rank:.0f}")

print("Most common words:")
for word, rank in result.most_common_words:
    print(f"  {word}: rank {rank:.0f}")
```

**Custom thresholds:**

```python
# Stricter rare threshold
result_strict = compute_word_frequency_sophistication(
    text,
    rare_threshold=5000,    # Words ranked > 5000 are "rare"
    common_threshold=500,   # Only top 500 are "common"
)

# More permissive thresholds
result_permissive = compute_word_frequency_sophistication(
    text,
    rare_threshold=20000,
    common_threshold=2000,
)
```

**Comparing authors:**

```python
result_a = compute_word_frequency_sophistication(text_author_a)
result_b = compute_word_frequency_sophistication(text_author_b)

print(f"Author A - Mean rank: {result_a.mean_frequency_rank:.0f}, "
      f"Academic: {result_a.academic_word_ratio:.1%}")
print(f"Author B - Mean rank: {result_b.mean_frequency_rank:.0f}, "
      f"Academic: {result_b.academic_word_ratio:.1%}")
```

**Accessing metadata:**

```python
result = compute_word_frequency_sophistication(text)

print(f"Total words: {result.metadata['total_words']}")
print(f"Unique words: {result.metadata['unique_words']}")
print(f"Unknown words: {result.metadata['unknown_words']}")
print(f"Unknown ratio: {result.metadata['unknown_word_ratio']:.1%}")
print(f"Frequency list size: {result.metadata['frequency_list_size']}")
```

---

## Limitations

1. **Limited embedded vocabulary**: The embedded COCA frequency list covers approximately 1,500 words. Words outside this list are assigned rank 50,000, which inflates the rare word ratio for texts with specialized terminology. A production system should use the full COCA list (60,000+ words).

2. **Single corpus only**: Currently only the "coca" corpus is supported. Other frequency corpora (BNC, Google N-grams, SUBTLEXus) would provide different perspectives on word rarity, particularly for British English or spoken language.

3. **No lemmatization**: Words are matched in their surface form. "Analyzing," "analyzed," and "analysis" are treated as separate words with potentially different frequency ranks. Lemmatization would provide more accurate frequency lookups.

4. **Function word dominance**: Very common function words (the, of, and) dominate high-frequency ranks and can obscure differences in content word sophistication. Consider combining with function word analysis for a more nuanced picture.

5. **No context sensitivity**: The same word receives the same frequency rank regardless of its meaning. Polysemous words like "bank" (financial institution vs. river bank) are not disambiguated.

6. **AWL scope**: The Academic Word List was designed for English academic writing. It may not capture sophisticated vocabulary in non-academic registers (e.g., literary, legal, medical).

7. **Empty text handling**: The function raises `ValueError` for texts with no valid tokens rather than returning a default result.

---

## References

- Brysbaert, M., & New, B. (2009). Moving beyond Kucera and Francis: A critical evaluation of current word frequency norms and the introduction of a new and improved word frequency measure for American English. *Behavior Research Methods*, 41(4), 977-990.
- Coxhead, A. (2000). A new academic word list. *TESOL Quarterly*, 34(2), 213-238.
- Davies, M. (2008-). *The Corpus of Contemporary American English (COCA)*. Available at https://www.english-corpora.org/coca/.
- Laufer, B., & Nation, P. (1995). Vocabulary size and use: Lexical richness in L2 written production. *Applied Linguistics*, 16(3), 307-322.
- Read, J. (2000). *Assessing Vocabulary*. Cambridge University Press.
- Kyle, K., & Crossley, S. A. (2015). Automatically assessing lexical sophistication: Indices, tools, findings, and application. *TESOL Quarterly*, 49(4), 757-786.

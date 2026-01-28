# Burrows' Delta

## Measuring Stylistic Distance Through Word Frequency Standardization

Burrows' Delta is one of the most widely adopted computational methods for authorship attribution. It measures the stylistic distance between two texts by comparing z-score standardized frequencies of the most common words. The method operates on the principle that authors exhibit stable, unconscious patterns in their use of high-frequency function words, and that these patterns can be captured through statistical normalization.

---

## Theoretical Background

### Origins

John Burrows introduced the Delta measure in his 2002 paper "'Delta': A Measure of Stylistic Difference and a Guide to Likely Authorship" published in Literary and Linguistic Computing. The method emerged from Burrows' long-standing research into computational stylistics, building on his earlier work with principal component analysis of word frequencies. Delta was designed to be a simple, interpretable, and effective metric that could be applied without extensive statistical training.

The method gained rapid adoption in the digital humanities community because of its transparency and strong empirical performance. In comparative evaluations, Delta consistently ranked among the most effective methods for authorship attribution across multiple languages and genres, despite its relative simplicity.

### Mathematical Foundation

#### Classic Delta

Classic Burrows' Delta proceeds through the following steps:

1. **Tokenize** both texts and compute raw word frequencies
2. **Select** the n most frequent words from the combined vocabulary
3. **Compute z-scores** for each word in each text, standardizing against the mean and standard deviation of the combined frequency distribution
4. **Sum absolute differences** between the z-scores

The z-score for word w in text T is:

```
z_T(w) = (f_T(w) - mu(w)) / sigma(w)
```

where f_T(w) is the relative frequency of word w in text T, mu(w) is the mean frequency across the corpus, and sigma(w) is the standard deviation.

The Delta distance between texts A and B is:

```
Delta(A, B) = (1/n) * SUM(|z_A(w) - z_B(w)|) for the n most frequent words
```

This is equivalent to the Manhattan distance in z-score space, normalized by the number of features.

#### Cosine Delta

Cosine Delta replaces the Manhattan distance with angular distance in the z-score vector space:

```
Cosine_Delta(A, B) = (2/pi) * arccos(cos_sim(z_A, z_B))
```

where:

```
cos_sim(z_A, z_B) = (z_A . z_B) / (||z_A|| * ||z_B||)
```

The arccos transformation converts the cosine similarity (range -1 to +1) into a proper distance metric (range 0 to 1). The factor of 2/pi normalizes to the unit interval.

Cosine Delta was shown by Evert et al. (2017) to outperform Classic Delta in many attribution scenarios because it is invariant to vector magnitude. This means it captures directional differences in word usage patterns without being influenced by overall text length or verbosity differences.

### Interpretation

Lower Delta values indicate greater stylistic similarity. In authorship attribution experiments:

- **Same-author pairs** typically produce Delta values in the lower quartile of the distribution
- **Different-author pairs** produce higher values
- The method works best when comparing texts of similar genre and period

The z-score standardization is critical because it prevents high-frequency words (like "the" or "of") from dominating the distance calculation purely due to their magnitude. Instead, each word contributes proportionally to how unusual its frequency is relative to the norm.

---

## Implementation

### Core Algorithm

The pystylometry implementation provides both Classic Delta and Cosine Delta as separate functions with shared preprocessing:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text1` | required | First text for comparison |
| `text2` | required | Second text for comparison |
| `n_features` | 500 | Number of most frequent words to analyze |
| `chunk_size` | 1000 | Minimum token count for reliable statistics |

The `n_features` parameter controls the vocabulary size used for comparison. Burrows originally recommended 150 words, but subsequent research has shown that 500 features provides a robust balance across diverse corpora. The implementation uses the combined vocabulary of both texts, ranked by aggregate frequency.

### Key Features

**Z-score normalization**: Each word frequency is standardized using the mean and standard deviation computed from both texts. Words with zero standard deviation (identical frequency in both texts) are excluded to avoid division by zero.

**Chunking**: When texts exceed `chunk_size` tokens, the implementation computes Delta across aligned chunks and averages the results. This reduces the impact of local topic variation and provides a more stable estimate of overall stylistic distance.

**Feature selection**: The n most frequent words are selected from the combined vocabulary of both texts. This ensures that the comparison focuses on words that are well-attested in both texts, rather than words that may be frequent in one text but absent from the other.

**Result metadata**: The returned result object includes the distance value, the feature set used, per-word contributions to the distance, and the most distinctive features (words with the largest z-score differences).

---

## Usage

### API Examples

#### Classic Delta

```python
from pystylometry.authorship import compute_burrows_delta

text_a = "The cat sat on the mat. The cat was very happy."
text_b = "A dog ran through the park. The dog was quite tired."

result = compute_burrows_delta(text_a, text_b, n_features=500)

print(f"Delta distance: {result.delta:.4f}")
print(f"Features used: {result.n_features}")
print(f"Most distinctive: {result.most_distinctive_features[:5]}")
```

#### Cosine Delta

```python
from pystylometry.authorship import compute_cosine_delta

result = compute_cosine_delta(text_a, text_b, n_features=500)

print(f"Cosine Delta: {result.delta:.4f}")
print(f"Cosine similarity: {result.cosine_similarity:.4f}")
```

#### Comparing Multiple Candidates

```python
from pystylometry.authorship import compute_burrows_delta

unknown_text = open("unknown_manuscript.txt").read()
candidates = {
    "Author A": open("author_a_corpus.txt").read(),
    "Author B": open("author_b_corpus.txt").read(),
    "Author C": open("author_c_corpus.txt").read(),
}

results = {}
for name, corpus in candidates.items():
    result = compute_burrows_delta(unknown_text, corpus, n_features=500)
    results[name] = result.delta

# The candidate with the lowest Delta is the most likely author
best_match = min(results, key=results.get)
print(f"Most likely author: {best_match} (Delta = {results[best_match]:.4f})")
```

---

## Limitations

### Corpus Size Requirements

Delta requires sufficient text to produce stable word frequency estimates. Texts shorter than a few hundred words may yield unreliable z-scores, particularly for lower-frequency words in the feature set. The `chunk_size` parameter provides a minimum threshold, but results improve with longer texts (ideally 2000+ words per text).

### Genre and Period Sensitivity

Delta measures stylistic distance without distinguishing between authorial style and genre conventions. Two texts in the same genre by different authors may produce a lower Delta than two texts by the same author in different genres. For best results, compare texts of similar genre, period, and register.

### Feature Count Sensitivity

The choice of `n_features` affects results. Too few features (under 50) may miss important stylistic signals. Too many features (over 1000) introduce noise from low-frequency words with unstable statistics. The default of 500 is well-supported by the literature but may need adjustment for specialized corpora.

### Language Dependence

While Delta is in principle language-independent, its effectiveness depends on the linguistic characteristics of the target language. Languages with rich morphology may require lemmatization or stemming as a preprocessing step to achieve comparable performance to English.

### Z-Score Instability with Small Corpora

When computing z-scores from only two texts, the mean and standard deviation are based on just two data points. This can produce unstable standardization. For more robust results, z-scores should ideally be computed against a larger reference corpus, though the pystylometry implementation uses the two-text approach for simplicity and self-containedness.

---

## References

Burrows, John. "'Delta': A Measure of Stylistic Difference and a Guide to Likely Authorship." *Literary and Linguistic Computing*, vol. 17, no. 3, 2002, pp. 267-287. doi:10.1093/llc/17.3.267

Evert, Stefan, et al. "Understanding and Explaining Delta Measures for Authorship Attribution." *Digital Scholarship in the Humanities*, vol. 32, suppl. 2, 2017, pp. ii4-ii16. doi:10.1093/llc/fqx023

Hoover, David L. "Testing Burrows's Delta." *Literary and Linguistic Computing*, vol. 19, no. 4, 2004, pp. 453-475.

Argamon, Shlomo. "Interpreting Burrows's Delta: Geometric and Probabilistic Foundations." *Literary and Linguistic Computing*, vol. 23, no. 2, 2008, pp. 131-147.

Eder, Maciej. "Does Size Matter? Authorship Attribution, Small Samples, Big Problem." *Digital Scholarship in the Humanities*, vol. 30, no. 2, 2015, pp. 167-182.

Jannidis, Fotis, et al. "Improving Burrows' Delta: An Empirical Evaluation of Text Distance Measures." *Digital Humanities 2015 Conference Abstracts*, 2015.

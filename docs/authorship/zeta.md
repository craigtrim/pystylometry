# Zeta

## Identifying Marker Words That Distinguish Authors

Zeta is a method for authorship attribution that identifies words characteristic of one author or text versus another. Rather than computing a single distance metric, Zeta produces a ranked list of marker words with signed scores indicating which text each word favors. This makes Zeta uniquely interpretable among authorship attribution methods: it not only measures stylistic difference but explains it in terms of specific vocabulary choices.

---

## Theoretical Background

### Origins

John Burrows introduced the Zeta method in his 2007 paper "All Polled Up: Zeta and Iota as They Are" published in Digital Scholarship in the Humanities. The method emerged from Burrows' interest in finding words that reliably distinguish two texts or authors, complementing his earlier Delta method which focuses on aggregate distance. Craig and Kinney (2009) subsequently applied Zeta extensively in their investigation of Shakespeare attribution questions, demonstrating its effectiveness for discriminating between authors in early modern English drama.

Unlike frequency-based methods such as Delta or chi-squared, Zeta operates on word presence or absence within text segments rather than raw frequency counts. This design makes it robust to outlier effects where a single concentrated burst of a word could inflate its frequency despite being absent from most of the text.

### Mathematical Foundation

The Zeta score for a word w is computed as follows:

1. **Segment** text1 into equal-sized segments S1_1, S1_2, ..., S1_m
2. **Segment** text2 into equal-sized segments S2_1, S2_2, ..., S2_k
3. **Compute presence proportions**:
   - p1(w) = proportion of text1 segments containing word w
   - p2(w) = proportion of text2 segments containing word w
4. **Compute Zeta score**:

```
Zeta(w) = p1(w) - p2(w)
```

The Zeta score ranges from -1 to +1:

```
Zeta(w) =  +1  =>  word appears in every text1 segment, no text2 segments
Zeta(w) =   0  =>  word appears in equal proportions of both texts
Zeta(w) =  -1  =>  word appears in every text2 segment, no text1 segments
```

### Interpretation

Words with high positive Zeta scores are **marker words** for text1: they appear consistently throughout text1 but are absent or rare in text2. Words with high negative Zeta scores are marker words for text2.

The strength of Zeta lies in this consistency requirement. A word that appears 100 times in one paragraph of text1 but nowhere else would receive a low Zeta score because it appears in only one segment. Conversely, a word that appears once in each of 20 segments scores highly because it demonstrates consistent, distributed usage.

This property makes Zeta particularly effective at capturing authorial vocabulary preferences rather than topic-specific terminology. Topic words tend to cluster in specific passages, while authorial preference words (such as preferred conjunctions, discourse markers, or habitual expressions) distribute evenly across an entire work.

### Marker Word Categories

In practice, Zeta marker words typically fall into several categories:

- **Function words**: Preferred conjunctions, prepositions, or determiners (e.g., "whilst" vs. "while")
- **Discourse markers**: Habitual transitional expressions (e.g., "indeed", "moreover")
- **Lexical preferences**: Synonym choices that differ between authors (e.g., "commence" vs. "begin")
- **Modal expressions**: Characteristic hedging or certainty markers (e.g., "perhaps" vs. "certainly")

---

## Implementation

### Core Algorithm

The pystylometry implementation follows Burrows' original method with configurable parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text1` | required | First text for comparison |
| `text2` | required | Second text for comparison |
| `segment_size` | 1000 | Number of tokens per segment |
| `top_n` | 50 | Number of top marker words to return per text |

The `segment_size` parameter controls the granularity of the presence/absence calculation. Smaller segments (500 tokens) increase sensitivity but may produce noisier results. Larger segments (2000 tokens) produce more stable scores but require longer texts.

### Key Features

**Segment-based analysis**: Texts are divided into non-overlapping segments of `segment_size` tokens. The final segment is included only if it contains at least 50% of the target segment size, preventing short trailing segments from distorting proportions.

**Bidirectional scoring**: The implementation computes Zeta scores for all words in the combined vocabulary, returning the top markers for both text1 (positive scores) and text2 (negative scores). This provides a symmetric view of what distinguishes each text.

**Case normalization**: All tokens are lowercased before analysis to prevent case variants from splitting word counts. Proper nouns are thus treated the same as common words, which is appropriate since authorship attribution focuses on stylistic rather than content features.

**Result structure**: The returned result includes:
- Ranked list of text1 marker words with Zeta scores
- Ranked list of text2 marker words with Zeta scores
- Total number of segments per text
- Segment size used
- Full Zeta score dictionary for all words

---

## Usage

### API Examples

#### Basic Marker Word Detection

```python
from pystylometry.authorship import compute_zeta

text_a = open("author_a_novel.txt").read()
text_b = open("author_b_novel.txt").read()

result = compute_zeta(text_a, text_b, segment_size=1000, top_n=50)

print("Words characteristic of Text A:")
for word, score in result.text1_markers[:10]:
    print(f"  {word}: {score:+.3f}")

print("\nWords characteristic of Text B:")
for word, score in result.text2_markers[:10]:
    print(f"  {word}: {score:+.3f}")
```

#### Authorship Verification

```python
from pystylometry.authorship import compute_zeta

# Compare disputed text against two candidate authors
disputed = open("disputed_work.txt").read()
candidate_a = open("known_author_a.txt").read()
candidate_b = open("known_author_b.txt").read()

# Find markers between the two known authors
markers = compute_zeta(candidate_a, candidate_b, segment_size=1000, top_n=50)

# Examine which author's markers appear in the disputed text
disputed_tokens = set(disputed.lower().split())
a_overlap = sum(1 for w, _ in markers.text1_markers if w in disputed_tokens)
b_overlap = sum(1 for w, _ in markers.text2_markers if w in disputed_tokens)

print(f"Author A marker overlap: {a_overlap}/{len(markers.text1_markers)}")
print(f"Author B marker overlap: {b_overlap}/{len(markers.text2_markers)}")
```

#### Adjusting Segment Size

```python
from pystylometry.authorship import compute_zeta

# Use smaller segments for shorter texts
result = compute_zeta(short_text_a, short_text_b, segment_size=500, top_n=30)

# Use larger segments for more stable results with long texts
result = compute_zeta(long_text_a, long_text_b, segment_size=2000, top_n=50)
```

---

## Limitations

### Minimum Text Length

Zeta requires enough text to produce multiple segments per text. With a segment size of 1000 tokens, each text should ideally contain at least 5000 tokens (5 segments) for meaningful proportions. Texts that produce fewer than 3 segments will yield coarse Zeta scores limited to a small set of possible values (e.g., 0.0, 0.33, 0.67, 1.0 for 3 segments).

### Topic Contamination

Although Zeta's segment-based design reduces topic effects compared to frequency-based methods, it does not eliminate them entirely. If two texts are on very different topics, the top marker words may reflect content differences rather than authorial style. For best results, compare texts on similar subjects or in similar genres.

### Segment Size Trade-offs

The segment size parameter involves a trade-off between sensitivity and stability. Small segments capture fine-grained vocabulary patterns but may flag words that are merely topically concentrated. Large segments require longer texts and may miss subtle vocabulary preferences. There is no universally optimal segment size; it should be chosen based on the characteristics of the texts under analysis.

### Binary Presence Model

Zeta treats word occurrence as binary (present or absent in a segment) rather than counting occurrences. This means a word that appears 50 times in a segment receives the same credit as one that appears once. While this design reduces sensitivity to frequency outliers, it also discards potentially useful frequency information.

### Vocabulary Size Effects

For short texts with limited vocabulary overlap, many words will have Zeta scores of +1 or -1 simply because they occur in only one text. This ceiling effect can make it difficult to rank marker words meaningfully. The `top_n` parameter helps by limiting output to the most informative markers, but the underlying issue remains for very short texts.

---

## References

Burrows, John. "All Polled Up: Zeta and Iota as They Are." *Digital Scholarship in the Humanities*, vol. 22, no. 1, 2007, pp. 1-13.

Craig, Hugh, and Arthur F. Kinney. *Shakespeare, Computers, and the Mystery of Authorship*. Cambridge University Press, 2009.

Hoover, David L. "Teasing Out Authorship and Style with t-Tests and Zeta." *Digital Humanities 2010 Conference Abstracts*, 2010, pp. 168-170.

Eder, Maciej. "Rolling Stylometry." *Digital Scholarship in the Humanities*, vol. 31, no. 3, 2016, pp. 457-469.

Schoch, Christof. "Zeta for Contrastive Analysis: Theory, Practice, and an Application to French Tragedy and Comedy." *JADT 2018: Proceedings of the 14th International Conference on Statistical Analysis of Textual Data*, 2018.

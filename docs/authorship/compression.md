# Normalized Compression Distance

## Information-Theoretic Authorship Attribution via Data Compression

Normalized Compression Distance (NCD) is a language-independent similarity metric grounded in algorithmic information theory. It approximates the theoretical Normalized Information Distance using real-world data compressors. The core insight is that if two texts share statistical regularities (such as common vocabulary, syntax, or stylistic patterns), compressing them together will achieve better compression than compressing them separately. This property makes NCD applicable to authorship attribution without requiring any linguistic preprocessing or language-specific resources.

---

## Theoretical Background

### Origins

The theoretical foundation for NCD was established by Li, Chen, Li, Ma, and Vitanyi in their 2004 paper "The Similarity Metric" published in IEEE Transactions on Information Theory. They proved that the Normalized Information Distance (NID), based on Kolmogorov complexity, is a universal similarity metric: it discovers all effective similarities between objects. Since Kolmogorov complexity is uncomputable, Cilibrasi and Vitanyi (2005) proposed approximating it using standard data compression algorithms, yielding the Normalized Compression Distance.

NCD has been applied to diverse domains beyond text analysis, including music classification, genome comparison, malware detection, and image similarity. Its application to authorship attribution was explored by researchers seeking language-independent methods that do not require tokenization, part-of-speech tagging, or other NLP preprocessing.

### Mathematical Foundation

The Normalized Information Distance between two objects x and y is defined as:

```
NID(x, y) = (max(K(x|y), K(y|x))) / max(K(x), K(y))
```

where K(x) is the Kolmogorov complexity of x (the length of the shortest program that produces x) and K(x|y) is the conditional Kolmogorov complexity (the shortest program that produces x given y as input).

Since Kolmogorov complexity is uncomputable, NCD replaces it with the compressed size C(x) produced by a real-world compressor:

```
NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
```

where:
- C(x) = compressed size of string x
- C(y) = compressed size of string y
- C(xy) = compressed size of the concatenation of x and y
- min and max select the smaller and larger of the two individual compressed sizes

### Interpretation

NCD values are interpreted as follows:

```
NCD ~ 0.0  =>  Texts are maximally similar (identical or near-identical)
NCD ~ 1.0  =>  Texts are maximally different (no shared structure)
```

In practice, NCD values for text comparison typically fall in the range 0.2 to 1.0:

- **Same-author pairs**: typically 0.3 to 0.6, depending on text length and genre consistency
- **Different-author pairs**: typically 0.6 to 0.9
- **Identical texts**: close to 0.0 (limited only by compressor overhead)
- **Random vs. structured text**: close to 1.0

The metric satisfies the mathematical properties of a distance:
- **Identity**: NCD(x, x) = 0 (up to compressor artifacts)
- **Symmetry**: NCD(x, y) = NCD(y, x) (by definition)
- **Triangle inequality**: approximately satisfied by good compressors

### Why Compression Works for Authorship

Data compressors identify and exploit statistical regularities in their input. When two texts by the same author are concatenated, the compressor can reuse patterns learned from the first text to compress the second more efficiently. These shared patterns include:

- **Vocabulary overlap**: Common word choices compress well together
- **Syntactic patterns**: Repeated phrase structures create exploitable redundancy
- **Function word distributions**: Characteristic usage of "the", "and", "but" etc.
- **Rhythmic patterns**: Sentence length distributions and punctuation habits
- **Spelling and orthographic conventions**: Consistent spelling choices

---

## Implementation

### Core Algorithm

The pystylometry implementation uses zlib compression (the DEFLATE algorithm) as the default compressor:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text1` | required | First text for comparison |
| `text2` | required | Second text for comparison |

The implementation follows a straightforward procedure:

1. Encode both texts as UTF-8 byte strings
2. Compress text1 alone to obtain C(x)
3. Compress text2 alone to obtain C(y)
4. Concatenate text1 and text2, compress to obtain C(xy)
5. Apply the NCD formula

```python
# Pseudocode for the core computation
c_x = len(zlib.compress(text1.encode('utf-8')))
c_y = len(zlib.compress(text2.encode('utf-8')))
c_xy = len(zlib.compress((text1 + text2).encode('utf-8')))

ncd = (c_xy - min(c_x, c_y)) / max(c_x, c_y)
```

### Key Features

**No linguistic preprocessing**: NCD operates directly on raw text without tokenization, stopword removal, or any other NLP pipeline. This makes it applicable to any language, script, or writing system without modification.

**Compressor choice**: The implementation uses zlib (DEFLATE), which provides a good balance of compression quality and speed. The DEFLATE algorithm uses a combination of LZ77 (dictionary-based) and Huffman coding (entropy-based), capturing both local repetition patterns and character frequency distributions.

**Concatenation order**: The implementation concatenates text1 + text2 for the joint compression. Due to the sliding window nature of DEFLATE (32KB window), the compressor can reference patterns from text1 while compressing text2. The symmetry of the NCD formula ensures that the result is identical regardless of concatenation order.

**Result metadata**: The returned result includes the NCD value, the individual compressed sizes, the joint compressed size, and the compressor used.

---

## Usage

### API Examples

#### Basic Comparison

```python
from pystylometry.authorship import compute_compression_distance

text_a = open("text_a.txt").read()
text_b = open("text_b.txt").read()

result = compute_compression_distance(text_a, text_b)

print(f"NCD: {result.ncd:.3f}")
print(f"Compressed sizes: C(x)={result.c_x}, C(y)={result.c_y}, C(xy)={result.c_xy}")
```

#### Pairwise Author Comparison

```python
from pystylometry.authorship import compute_compression_distance

authors = {
    "Austen": open("austen_sample.txt").read(),
    "Dickens": open("dickens_sample.txt").read(),
    "Twain": open("twain_sample.txt").read(),
}

# Compute all pairwise distances
for name_a, text_a in authors.items():
    for name_b, text_b in authors.items():
        if name_a < name_b:
            result = compute_compression_distance(text_a, text_b)
            print(f"{name_a} vs {name_b}: NCD = {result.ncd:.3f}")
```

#### Attribution by Minimum Distance

```python
from pystylometry.authorship import compute_compression_distance

unknown = open("disputed_text.txt").read()
candidates = {
    "Author A": open("author_a.txt").read(),
    "Author B": open("author_b.txt").read(),
    "Author C": open("author_c.txt").read(),
}

distances = {}
for name, corpus in candidates.items():
    result = compute_compression_distance(unknown, corpus)
    distances[name] = result.ncd

best_match = min(distances, key=distances.get)
print(f"Most similar to: {best_match} (NCD = {distances[best_match]:.3f})")
```

---

## Limitations

### Compressor Window Size

The zlib DEFLATE algorithm uses a sliding window of 32KB. For texts longer than approximately 32KB, the compressor cannot reference patterns from the beginning of text1 while compressing the end of text2. This effectively limits the range of cross-text pattern matching. Very long texts may benefit from being truncated or sampled to fit within the compressor's effective window.

### Text Length Sensitivity

NCD is sensitive to the relative lengths of the two texts. When one text is much longer than the other, the compressed concatenation size C(xy) is dominated by the longer text, and the shorter text's contribution to shared compression becomes proportionally smaller. For best results, compare texts of similar length, or extract equal-length samples from longer works.

### Compression Quality

The quality of the NCD approximation depends on the compressor's ability to capture the relevant statistical regularities. Simple compressors (like run-length encoding) would produce poor approximations. zlib provides a reasonable balance, but more sophisticated compressors (like LZMA or PPM) may yield better discrimination at the cost of computation time.

### No Feature Interpretability

Unlike Delta or Zeta, NCD provides no insight into which specific features drive the similarity or dissimilarity. The result is a single numeric distance with no explanation of which vocabulary, syntactic, or stylistic patterns contributed. This makes NCD useful as a quick similarity metric but less informative for detailed stylistic analysis.

### Encoding Sensitivity

The compressed size depends on the byte encoding of the text. UTF-8 encoding of texts with many non-ASCII characters (accented letters, CJK characters) produces different byte patterns than ASCII text, which can affect compression ratios. When comparing texts in different scripts, the encoding overhead may introduce systematic bias.

### Non-Metric Behavior

While NCD approximates a true metric, real-world compressors introduce small violations of metric properties. In particular, NCD(x, x) may not be exactly 0 due to compressor overhead, and the triangle inequality may be slightly violated. These effects are typically small but can affect clustering or nearest-neighbor analyses.

---

## References

Li, Ming, Xin Chen, Xin Li, Bin Ma, and Paul M. B. Vitanyi. "The Similarity Metric." *IEEE Transactions on Information Theory*, vol. 50, no. 12, 2004, pp. 3250-3264. doi:10.1109/TIT.2004.838101

Cilibrasi, Rudi, and Paul M. B. Vitanyi. "Clustering by Compression." *IEEE Transactions on Information Theory*, vol. 51, no. 4, 2005, pp. 1523-1545. doi:10.1109/TIT.2005.844059

Benedetto, Dario, Emanuele Caglioti, and Vittorio Loreto. "Language Trees and Zipping." *Physical Review Letters*, vol. 88, no. 4, 2002, 048702.

Granados, Ana, et al. "Evaluating the Use of Normalized Compression Distance for Identifying the Author of a Document." *Proceedings of the 2nd International Workshop on AI Methods for Interdisciplinary Research in Language and Biology*, 2011.

Coutinho, Daniel P., and Mario A. T. Figueiredo. "Text Classification Using Compression-Based Dissimilarity Measures." *International Journal of Pattern Recognition and Artificial Intelligence*, vol. 20, no. 7, 2006, pp. 1101-1121.

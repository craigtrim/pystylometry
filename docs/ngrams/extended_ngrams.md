# Extended N-gram Features

## Capturing Authorial Fingerprints Through Sequential Patterns

Extended n-gram analysis provides comprehensive stylometric features beyond basic word frequencies. By examining sequences of words, characters, and syntactic patterns, these features capture the subtle regularities in how authors construct phrases and sentences.

---

## Theoretical Background

### Why N-grams Matter for Authorship

N-grams capture recurring patterns in text that often operate below conscious awareness. While an author might deliberately vary vocabulary, they rarely consciously control their preferred phrase constructions or character sequences. This makes n-gram profiles resistant to intentional style manipulation.

**Word n-grams** reveal preferred phrases and collocations:
- "at the end of" vs "in the final part"
- "I think that" vs "it seems to me"

**Character n-grams** capture morphological and orthographic patterns:
- Suffix preferences ("-tion" vs "-ment")
- Spelling variants ("colour" vs "color")
- Punctuation habits

**POS n-grams** abstract syntactic preferences:
- "DET ADJ NOUN" (the quick fox)
- "VERB PREP DET" (jumped over the)

### Skipgrams

Skipgrams extend traditional n-grams by allowing gaps between words. A 2-skipgram with gap 1 captures patterns like "I _ to" which matches "I want to", "I have to", "I need to". This reveals syntactic frames independent of specific lexical choices.

References:
- Guthrie, D., et al. (2006). "A closer look at skip-gram modelling." LREC.
- Kešelj, V., et al. (2003). "N-gram-based author profiles for authorship attribution." PACLING.

---

## Features Computed

### Word N-grams

| Feature | Description |
|---------|-------------|
| `top_word_trigrams` | Most frequent 3-word sequences with counts |
| `top_word_4grams` | Most frequent 4-word sequences with counts |
| `word_trigram_count` | Total unique word trigrams |
| `word_4gram_count` | Total unique word 4-grams |
| `word_trigram_entropy` | Shannon entropy of trigram distribution |
| `word_4gram_entropy` | Shannon entropy of 4-gram distribution |

### Skipgrams

| Feature | Description |
|---------|-------------|
| `top_skipgrams_2_1` | Top 2-skipgrams with gap of 1 (word1 _ word3) |
| `top_skipgrams_3_1` | Top 3-skipgrams with gap of 1 (word1 _ word3 word4) |
| `skipgram_2_1_count` | Unique 2-skipgrams |
| `skipgram_3_1_count` | Unique 3-skipgrams |

### POS N-grams (Optional)

| Feature | Description |
|---------|-------------|
| `top_pos_trigrams` | Most frequent POS tag trigrams |
| `top_pos_4grams` | Most frequent POS tag 4-grams |
| `pos_trigram_count` | Unique POS trigrams |
| `pos_4gram_count` | Unique POS 4-grams |
| `pos_trigram_entropy` | Shannon entropy of POS trigram distribution |

### Character N-grams

| Feature | Description |
|---------|-------------|
| `top_char_trigrams` | Most frequent 3-character sequences |
| `top_char_4grams` | Most frequent 4-character sequences |
| `char_trigram_entropy` | Shannon entropy of character trigram distribution |
| `char_4gram_entropy` | Shannon entropy of character 4-gram distribution |

---

## Shannon Entropy

Shannon entropy measures the diversity of an n-gram distribution:

```
H = -Σ p(x) × log₂(p(x))
```

where p(x) is the probability of n-gram x.

**Interpretation:**
- **High entropy**: Diverse, uniform distribution (many unique patterns)
- **Low entropy**: Concentrated distribution (few dominant patterns)

A text with entropy 5.0 bits has roughly 2⁵ = 32 "effective" unique n-grams, while entropy 10.0 suggests ~1024 effective patterns.

---

## Usage

### Basic Usage

```python
from pystylometry.ngrams import compute_extended_ngrams

result = compute_extended_ngrams(text)

# Word n-grams
print(f"Top trigram: {result.top_word_trigrams[0]}")
print(f"Trigram entropy: {result.word_trigram_entropy:.2f} bits")

# Skipgrams
print(f"Top skipgram: {result.top_skipgrams_2_1[0]}")

# Character n-grams
print(f"Top char trigram: {result.top_char_trigrams[0]}")
```

### Without POS Tagging

For faster computation without spaCy dependency:

```python
result = compute_extended_ngrams(text, include_pos_ngrams=False)
```

### Custom Parameters

```python
result = compute_extended_ngrams(
    text,
    top_n=50,                    # Return top 50 n-grams per type
    include_pos_ngrams=True,     # Include POS n-grams
    spacy_model="en_core_web_md" # Use medium spaCy model
)
```

---

## Comparing Authors

Extended n-grams excel at author comparison:

```python
from pystylometry.ngrams import compute_extended_ngrams

author_a = compute_extended_ngrams(text_by_author_a)
author_b = compute_extended_ngrams(text_by_author_b)

# Compare top word trigrams
a_trigrams = set(t[0] for t in author_a.top_word_trigrams[:20])
b_trigrams = set(t[0] for t in author_b.top_word_trigrams[:20])

overlap = a_trigrams & b_trigrams
unique_a = a_trigrams - b_trigrams
unique_b = b_trigrams - a_trigrams

print(f"Shared trigrams: {len(overlap)}")
print(f"Unique to A: {unique_a}")
print(f"Unique to B: {unique_b}")
```

---

## Related Issues

- GitHub Issue #19: Extended N-gram Features
  https://github.com/craigtrim/pystylometry/issues/19

## References

- Guthrie, D., Allison, B., Liu, W., Guthrie, L., & Wilks, Y. (2006). A closer look at skip-gram modelling. *LREC*.
- Stamatatos, E. (2009). A survey of modern authorship attribution methods. *JASIST*, 60(3), 538-556.
- Kešelj, V., Peng, F., Cercone, N., & Thomas, C. (2003). N-gram-based author profiles for authorship attribution. *PACLING*.

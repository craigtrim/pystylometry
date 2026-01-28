# Function Word Analysis

## Authorship Attribution Through Closed-Class Word Frequencies

Function words -- determiners, prepositions, conjunctions, pronouns, auxiliary verbs, and particles -- are the most powerful single feature class for authorship attribution. Because authors use them subconsciously and consistently regardless of topic, their frequency patterns form a reliable stylometric fingerprint.

---

## Theoretical Background

### Origins

The use of function words for authorship attribution was pioneered by Frederick Mosteller and David Wallace in their landmark 1964 study *Inference and Disputed Authorship: The Federalist*. They successfully resolved the disputed authorship of twelve Federalist Papers by analyzing the frequency distributions of common function words like "upon," "whilst," and "while" to distinguish between Alexander Hamilton and James Madison.

This approach was revolutionary because it demonstrated that seemingly trivial words -- those that carry grammatical rather than semantic meaning -- could reliably identify authors. The key insight is that content words are topic-dependent (a marine biologist writes about "ocean" and "coral" regardless of personal style), while function words reflect deep-seated linguistic habits that authors cannot easily disguise.

John Burrows (2002) extended this principle with his "Delta" method, which uses the frequencies of the most common words (predominantly function words) as a general-purpose authorship attribution technique. Argamon and Levitan (2005) further validated that function word frequencies outperform content word features across diverse attribution tasks.

### Mathematical Foundation

Function word analysis computes frequency ratios for six grammatical categories:

```
Determiner Ratio = count(determiners) / N
Preposition Ratio = count(prepositions) / N
Conjunction Ratio = count(conjunctions) / N
Pronoun Ratio = count(pronouns) / N
Auxiliary Ratio = count(auxiliaries) / N
Particle Ratio = count(particles) / N
```

Where `N` = total number of tokens in the text.

**Total function word ratio:**

```
Total FW Ratio = count(all unique function word tokens) / N
```

Note: Words appearing in multiple categories (e.g., "that" is both a determiner and a pronoun) are counted once per category for category ratios, but only once for the total function word ratio.

**Function word diversity:**

```
FW Diversity = unique_function_words_used / total_function_word_tokens
```

This measures how many different function words an author employs relative to their total function word usage. Higher diversity indicates a broader grammatical repertoire.

### Interpretation

Typical function word ratios in English prose:

| Category | Typical Range | Notes |
|----------|---------------|-------|
| Determiners | 0.10-0.18 | "the" dominates; article usage is highly author-specific |
| Prepositions | 0.08-0.15 | Varies with sentence complexity and style |
| Conjunctions | 0.03-0.08 | Higher in paratactic (coordinate) styles |
| Pronouns | 0.06-0.12 | First-person heavy in personal narrative |
| Auxiliaries | 0.04-0.10 | Reflects tense and modal preferences |
| Particles | 0.01-0.04 | Higher in informal, phrasal-verb-rich styles |
| **Total** | **0.40-0.55** | Nearly half of typical English prose |

Key authorship indicators:
- **Personal pronouns**: First-person frequency distinguishes autobiographical from impersonal styles
- **Modal auxiliaries**: "Shall" vs. "will," "might" vs. "could" vary systematically between authors
- **Conjunction preferences**: Coordination ("and," "but") vs. subordination ("although," "because") patterns
- **Preposition choices**: "Upon" vs. "on," "amongst" vs. "among" mark historical period and register

---

## Implementation

### Core Algorithm

```python
def compute_function_words(text: str, chunk_size: int = 1000) -> FunctionWordResult
```

**Algorithm steps:**

1. Tokenize the text: lowercase, split on whitespace, strip punctuation
2. Count tokens in each of six function word categories (allowing overlap)
3. Build a unified function word frequency distribution
4. Compute category ratios (per total words)
5. Compute total function word ratio and diversity
6. Identify most/least frequent function words (top/bottom 10)
7. Detect words appearing in multiple categories
8. Create Distribution objects for each ratio

### Function Word Categories

The implementation uses curated word lists for English:

| Category | Count | Examples |
|----------|-------|---------|
| Determiners | 33 | the, a, an, this, that, my, your, some, every |
| Prepositions | 50 | in, on, at, by, for, with, from, to, of, through |
| Conjunctions | 23 | and, but, or, because, although, while, if, when |
| Pronouns | 38 | I, you, he, she, it, we, they, myself, who, which |
| Auxiliaries | 20 | can, could, may, might, must, shall, should, will, am, is |
| Particles | 13 | up, down, out, off, over, away, back, along, forth |

**Overlap handling**: Some words belong to multiple categories (e.g., "that" is both a determiner and a pronoun; "for" is both a preposition and a conjunction). Each category is counted independently, but the total function word count uses a union set to avoid double-counting.

### Key Features

1. **Six grammatical categories**: Comprehensive coverage of English function word classes
2. **Overlap detection**: Identifies and reports words appearing in multiple categories
3. **Distribution dataclass**: Each ratio wrapped in Distribution for fingerprinting
4. **Frequency ranking**: Top 10 most and least frequent function words with counts
5. **Full distribution map**: Complete word-to-count mapping for detailed analysis
6. **Category word lists**: Metadata includes which specific function words were found per category

### Return Type

`FunctionWordResult` dataclass with fields:

| Field | Type | Description |
|-------|------|-------------|
| `determiner_ratio` | `float` | Determiner tokens / total tokens |
| `preposition_ratio` | `float` | Preposition tokens / total tokens |
| `conjunction_ratio` | `float` | Conjunction tokens / total tokens |
| `pronoun_ratio` | `float` | Pronoun tokens / total tokens |
| `auxiliary_ratio` | `float` | Auxiliary tokens / total tokens |
| `particle_ratio` | `float` | Particle tokens / total tokens |
| `total_function_word_ratio` | `float` | All function word tokens / total tokens |
| `function_word_diversity` | `float` | Unique FW types / total FW tokens |
| `most_frequent_function_words` | `list[tuple]` | Top 10 (word, count) pairs |
| `least_frequent_function_words` | `list[tuple]` | Bottom 10 (word, count) pairs |
| `function_word_distribution` | `dict` | Complete word-to-count mapping |
| `*_dist` fields | `Distribution` | Distribution for each ratio |
| `metadata` | `dict` | Counts, word lists, overlapping words |

---

## Usage

### API Examples

**Basic usage:**

```python
from pystylometry.lexical import compute_function_words

result = compute_function_words("The quick brown fox jumps over the lazy dog.")

print(f"Determiner ratio: {result.determiner_ratio:.3f}")
print(f"Preposition ratio: {result.preposition_ratio:.3f}")
print(f"Total FW ratio: {result.total_function_word_ratio:.3f}")
print(f"FW diversity: {result.function_word_diversity:.3f}")
```

**Examining frequency distributions:**

```python
result = compute_function_words(text)

# Most used function words
for word, count in result.most_frequent_function_words:
    print(f"  {word}: {count}")

# Least used function words
for word, count in result.least_frequent_function_words:
    print(f"  {word}: {count}")

# Full distribution
for word, count in sorted(result.function_word_distribution.items(),
                          key=lambda x: x[1], reverse=True):
    print(f"  {word}: {count}")
```

**Authorship comparison:**

```python
r1 = compute_function_words(text_author_1)
r2 = compute_function_words(text_author_2)

# Compare category profiles
categories = ["determiner", "preposition", "conjunction",
              "pronoun", "auxiliary", "particle"]
for cat in categories:
    ratio_1 = getattr(r1, f"{cat}_ratio")
    ratio_2 = getattr(r2, f"{cat}_ratio")
    print(f"{cat:>12}: Author 1 = {ratio_1:.3f}, Author 2 = {ratio_2:.3f}")
```

**Inspecting overlapping words:**

```python
result = compute_function_words(text)

print(f"Overlapping words: {result.metadata['overlapping_words']}")
for word, cats in result.metadata['overlapping_word_categories'].items():
    print(f"  '{word}' belongs to: {', '.join(cats)}")
```

---

## Limitations

1. **English-specific word lists**: The current implementation uses curated English function word lists. Other languages require different lists, and the categories may not map directly to other language families.

2. **Category overlap ambiguity**: Words like "that," "for," "since," and "but" serve different grammatical functions depending on context. Without part-of-speech tagging, the implementation counts all occurrences in all applicable categories, which may inflate certain ratios.

3. **No POS disambiguation**: The implementation uses lexicon-based matching rather than contextual POS tagging. "But" as a conjunction ("I tried, but failed") and "but" as a preposition ("all but one") are not distinguished.

4. **Tokenization simplicity**: Whitespace-based tokenization with punctuation stripping may handle contractions and hyphenated forms differently than linguistic tokenizers. Multi-word expressions like "no one" are not matched as single tokens.

5. **Minimum text length**: Function word statistics require sufficient text (at least a few hundred words) to produce stable ratios. Very short texts may have unreliable profiles.

6. **Historical variation**: Function word usage patterns change over centuries. Comparing 18th-century texts with modern prose requires awareness of historical shifts in preposition and conjunction usage.

---

## References

- Mosteller, F., & Wallace, D. L. (1964). *Inference and Disputed Authorship: The Federalist*. Addison-Wesley.
- Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide to likely authorship. *Literary and Linguistic Computing*, 17(3), 267-287.
- Argamon, S., & Levitan, S. (2005). Measuring the usefulness of function words for authorship attribution. *ACH/ALLC 2005*.
- Koppel, M., Schler, J., & Argamon, S. (2009). Computational methods in authorship attribution. *Journal of the American Society for Information Science and Technology*, 60(1), 9-26.
- Stamatatos, E. (2009). A survey of modern authorship attribution methods. *Journal of the American Society for Information Science and Technology*, 60(3), 538-556.

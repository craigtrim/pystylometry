# Sentence Type Classification

## Analyzing Structural and Functional Sentence Patterns for Stylometric Profiling

Sentence type classification assigns each sentence in a text to both a structural category (simple, compound, complex, compound-complex) and a functional category (declarative, interrogative, imperative, exclamatory). The resulting distributions reveal authorial preferences, genre conventions, and rhetorical strategies that distinguish writing styles at the syntactic level.

---

## Theoretical Background

### Origins

The classification of sentences by structure and function has deep roots in descriptive grammar. Quirk, Greenbaum, Leech, and Svartvik's *A Comprehensive Grammar of the English Language* (1985) codified the four-way structural classification used in this module. Huddleston and Pullum's *The Cambridge Grammar of the English Language* (2002) refined these categories with detailed criteria for clause identification.

In computational stylometry, Biber (1988) demonstrated that sentence type distributions vary systematically across registers:

- **Academic writing** favors complex and compound-complex sentences, reflecting the need to express nuanced logical relationships through subordination.
- **Fiction** uses a balanced mix of simple and complex sentences to create narrative rhythm and pacing.
- **Journalism** relies on simple and compound sentences for clarity and directness.
- **Instructional text** features a higher proportion of imperative sentences.

The functional classification (declarative, interrogative, imperative, exclamatory) captures communicative intent. The ratio of questions to statements, or the presence of commands, provides stylistic and rhetorical information that structural classification alone cannot reveal.

### Mathematical Foundation

**Structural ratios** are computed as proportions of total sentence count:

```
simple_ratio           = simple_count / total_sentences
compound_ratio         = compound_count / total_sentences
complex_ratio          = complex_count / total_sentences
compound_complex_ratio = compound_complex_count / total_sentences
```

These four ratios sum to 1.0.

**Functional ratios** follow the same pattern:

```
declarative_ratio   = declarative_count / total_sentences
interrogative_ratio = interrogative_count / total_sentences
imperative_ratio    = imperative_count / total_sentences
exclamatory_ratio   = exclamatory_count / total_sentences
```

These four ratios also sum to 1.0.

**Shannon entropy** measures the diversity of each distribution:

```
H = -sum(p * log2(p)) for all p > 0
```

where *p* is the ratio for each category. Higher entropy indicates more uniform distribution across categories; lower entropy indicates dominance of one or two categories.

- Maximum structural diversity: log2(4) = 2.0 bits (all four types equally frequent)
- Minimum diversity: 0.0 bits (only one type present)

### Interpretation

**Structural classification criteria:**

| Type | Independent Clauses | Dependent Clauses | Example |
|------|--------------------|--------------------|---------|
| Simple | 1 | 0 | "The cat sat on the mat." |
| Compound | 2+ | 0 | "I came, and I saw." |
| Complex | 1 | 1+ | "When I arrived, I saw her." |
| Compound-complex | 2+ | 1+ | "I came when called, and I stayed because I wanted to." |

**Functional classification criteria:**

| Type | Criterion | Example |
|------|-----------|---------|
| Declarative | Makes a statement; typically ends with period | "The sky is blue." |
| Interrogative | Asks a question; ends with question mark | "Is the sky blue?" |
| Imperative | Gives a command; no nominal subject; root is base verb | "Look at the sky." |
| Exclamatory | Expresses strong emotion; ends with exclamation mark | "What a blue sky!" |

**Genre patterns:**

| Genre | Structural Pattern | Functional Pattern |
|-------|-------------------|-------------------|
| Academic | High complex and compound-complex | Predominantly declarative |
| Fiction | Mixed simple and complex | Mostly declarative with some interrogative |
| Journalism | High simple and compound | Predominantly declarative |
| Technical/instructional | Complex and simple | Declarative with imperative |
| Dialogue-heavy fiction | Simple dominant | High interrogative and exclamatory |

---

## Implementation

### Core Algorithm

The implementation uses spaCy's dependency parser to identify clause boundaries and classify each sentence:

**Structural classification:**

1. For each sentence, count independent clauses by identifying the root clause (always 1) plus any verb conjuncts (`dep_="conj"`, `pos_="VERB"`) that have a coordinating conjunction sibling (`dep_="cc"`).
2. Count dependent clauses by identifying tokens with dependency labels in the set `{ccomp, advcl, acl, relcl, xcomp}`.
3. Apply classification rules:
   - 1 independent, 0 dependent = simple
   - 2+ independent, 0 dependent = compound
   - 1 independent, 1+ dependent = complex
   - 2+ independent, 1+ dependent = compound-complex

**Functional classification:**

1. Check the final token of each sentence for punctuation:
   - `?` indicates interrogative.
   - `!` triggers a secondary check: if the sentence has imperative structure, classify as imperative; otherwise, classify as exclamatory.
2. Check for imperative structure: no nominal subject (`nsubj`) and root is a verb with tag `VB` or `VBP`.
3. Default classification is declarative.

**Diversity metrics:**

Shannon entropy is computed for both the structural and functional distributions to quantify variety in sentence type usage.

### Key Features

- **Dual classification**: Every sentence receives both a structural and a functional label, enabling cross-tabulation (e.g., "complex interrogative" or "simple imperative").
- **Clause counting via dependency parsing**: Independent and dependent clause counts use spaCy's dependency relations rather than heuristic punctuation rules, providing more linguistically grounded classification.
- **Shannon entropy diversity**: The `structural_diversity` and `functional_diversity` fields quantify how evenly distributed sentence types are, enabling single-number comparisons between texts.
- **Sentence-by-sentence metadata**: The `metadata` dictionary includes a list of per-sentence classification records with text, structural type, functional type, and clause counts, supporting fine-grained analysis.
- **Empty text handling**: Texts with no sentences return `NaN` for all ratios, 0 for all counts, and `NaN` for diversity metrics.

---

## Usage

### API Examples

```python
from pystylometry.syntactic import compute_sentence_types

# Basic usage
text = """
The sun rose over the mountains. Birds began to sing, and the forest
came alive. Although it was early, the hikers were already on the trail.
Did they know what awaited them? Look at that magnificent view!
"""

result = compute_sentence_types(text)

# Structural distribution
print(f"Simple: {result.simple_ratio:.1%}")
print(f"Compound: {result.compound_ratio:.1%}")
print(f"Complex: {result.complex_ratio:.1%}")
print(f"Compound-complex: {result.compound_complex_ratio:.1%}")

# Functional distribution
print(f"Declarative: {result.declarative_ratio:.1%}")
print(f"Interrogative: {result.interrogative_ratio:.1%}")
print(f"Imperative: {result.imperative_ratio:.1%}")
print(f"Exclamatory: {result.exclamatory_ratio:.1%}")

# Diversity
print(f"Structural diversity: {result.structural_diversity:.3f} bits")
print(f"Functional diversity: {result.functional_diversity:.3f} bits")
```

```python
# Accessing raw counts
result = compute_sentence_types(text)
print(f"Total sentences: {result.total_sentences}")
print(f"Simple count: {result.simple_count}")
print(f"Complex count: {result.complex_count}")
print(f"Declarative count: {result.declarative_count}")
print(f"Interrogative count: {result.interrogative_count}")
```

```python
# Examining individual sentence classifications
result = compute_sentence_types(text)
for entry in result.metadata["sentence_classifications"]:
    print(f"  [{entry['structural_type']}] [{entry['functional_type']}] {entry['text'][:60]}...")
    print(f"    Independent: {entry['independent_clauses']}, Dependent: {entry['dependent_clauses']}")
```

```python
# Genre comparison
academic = compute_sentence_types(academic_text)
fiction = compute_sentence_types(fiction_text)

print(f"Academic complex ratio: {academic.complex_ratio:.2f}")
print(f"Fiction complex ratio: {fiction.complex_ratio:.2f}")
print(f"Academic structural diversity: {academic.structural_diversity:.3f}")
print(f"Fiction structural diversity: {fiction.structural_diversity:.3f}")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | (required) | Input text to analyze. Multiple sentences recommended for meaningful distributions. |
| `model` | `str` | `"en_core_web_sm"` | spaCy model with dependency parser. Larger models provide better clause detection accuracy. |
| `chunk_size` | `int` | `1000` | Number of words per chunk. Included for API consistency; sentence type analysis runs in a single pass. |

### Return Type

`SentenceTypeResult` dataclass with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `simple_ratio` | `float` | Simple sentences / total |
| `compound_ratio` | `float` | Compound sentences / total |
| `complex_ratio` | `float` | Complex sentences / total |
| `compound_complex_ratio` | `float` | Compound-complex / total |
| `declarative_ratio` | `float` | Declarative sentences / total |
| `interrogative_ratio` | `float` | Interrogative sentences / total |
| `imperative_ratio` | `float` | Imperative sentences / total |
| `exclamatory_ratio` | `float` | Exclamatory sentences / total |
| `simple_count` | `int` | Number of simple sentences |
| `compound_count` | `int` | Number of compound sentences |
| `complex_count` | `int` | Number of complex sentences |
| `compound_complex_count` | `int` | Number of compound-complex sentences |
| `declarative_count` | `int` | Number of declarative sentences |
| `interrogative_count` | `int` | Number of interrogative sentences |
| `imperative_count` | `int` | Number of imperative sentences |
| `exclamatory_count` | `int` | Number of exclamatory sentences |
| `total_sentences` | `int` | Total sentence count |
| `structural_diversity` | `float` | Shannon entropy of structural distribution (0.0 to 2.0 bits) |
| `functional_diversity` | `float` | Shannon entropy of functional distribution (0.0 to 2.0 bits) |
| `metadata` | `dict` | Per-sentence classifications, clause counts, model info |

---

## Limitations

- **Clause detection accuracy**: Structural classification depends on spaCy's dependency parser for clause identification. Complex or ambiguous sentences may be misclassified. The small model has lower parsing accuracy than larger models.
- **Punctuation dependency for functional types**: Interrogative and exclamatory classification relies on terminal punctuation (`?` and `!`). Texts with missing or non-standard punctuation (e.g., social media, transcribed speech) may be misclassified.
- **Imperative detection heuristic**: Imperatives are identified by the absence of a nominal subject combined with a base-form root verb. This heuristic may produce false positives for sentence fragments or false negatives for imperatives with explicit subjects ("You come here!").
- **Exclamatory vs. imperative ambiguity**: Sentences ending with `!` are classified as imperative only if they match the imperative structure heuristic; otherwise they are classified as exclamatory. This may misclassify emphatic declaratives ("I love it!") as exclamatory.
- **Open clausal complements**: The `xcomp` dependency label is counted as a dependent clause. Some linguists do not consider open clausal complements (e.g., "I want to go") as full dependent clauses, which may inflate the complex sentence count.
- **Single-pass analysis**: The `chunk_size` parameter is accepted for API consistency but does not trigger chunked processing.
- **Small sample instability**: With fewer than 10 sentences, ratios and diversity metrics may not reliably reflect the broader style of a text or author.

---

## References

- Biber, D. (1988). *Variation across speech and writing*. Cambridge University Press.
- Huddleston, R., & Pullum, G. K. (2002). *The Cambridge grammar of the English language*. Cambridge University Press.
- Quirk, R., Greenbaum, S., Leech, G., & Svartvik, J. (1985). *A comprehensive grammar of the English language*. Longman.
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379-423.
- Biber, D., Johansson, S., Leech, G., Conrad, S., & Finegan, E. (1999). *Longman grammar of spoken and written English*. Longman.

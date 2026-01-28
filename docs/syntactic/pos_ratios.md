# Part-of-Speech Ratio Analysis

## Quantifying Grammatical Category Distributions for Stylometric Profiling

Part-of-speech (POS) ratio analysis measures the proportional distribution of grammatical categories in a text. By computing the relative frequencies of nouns, verbs, adjectives, adverbs, and function words, POS ratios reveal fundamental differences in writing style, genre, and register that operate largely below conscious authorial control.

---

## Theoretical Background

### Origins

POS distribution analysis has roots in Douglas Biber's landmark multidimensional analysis of linguistic variation. In *Variation across Speech and Writing* (1988), Biber demonstrated that the relative frequencies of grammatical categories systematically distinguish spoken from written language, and further differentiate among registers such as academic prose, fiction, personal letters, and journalism.

Biber identified that certain POS distributions correlate with communicative dimensions:

- **Informational vs. involved production**: High noun ratios characterize informational text; high verb and pronoun ratios characterize involved, interactional text.
- **Narrative vs. non-narrative**: Narrative texts exhibit higher past-tense verb ratios; non-narrative texts show higher present-tense and nominal ratios.
- **Elaborated vs. situation-dependent reference**: Academic writing features higher adjective and noun ratios; casual speech relies more on adverbs and pronouns.

These findings established POS ratios as a foundational feature set in computational stylometry and register analysis.

### Mathematical Foundation

POS ratios are computed as simple proportions over the set of alphabetic tokens:

**Individual POS ratios:**

```
noun_ratio       = noun_count / total_tokens
verb_ratio       = verb_count / total_tokens
adjective_ratio  = adjective_count / total_tokens
adverb_ratio     = adverb_count / total_tokens
```

**Cross-category ratios:**

```
noun_verb_ratio      = noun_count / verb_count
adjective_noun_ratio = adjective_count / noun_count
```

**Lexical density** measures the proportion of content words (open-class categories) to total words. It captures how informationally dense a text is:

```
lexical_density = (nouns + verbs + adjectives + adverbs) / total_tokens
```

**Function word ratio** measures the proportion of grammatical (closed-class) words:

```
function_word_ratio = (determiners + prepositions + conjunctions) / total_tokens
```

### Interpretation

| Metric | Low Values | High Values |
|--------|-----------|-------------|
| Noun ratio | Procedural, action-oriented text | Informational, descriptive text |
| Verb ratio | Static, nominal text | Dynamic, narrative text |
| Adjective ratio | Sparse, direct prose | Elaborated, descriptive prose |
| Adverb ratio | Formal, academic style | Informal, conversational style |
| Noun-verb ratio | Verb-heavy, active text | Noun-heavy, nominal text |
| Adjective-noun ratio | Unmodified nouns | Heavily modified nouns |
| Lexical density | Grammatically rich, conversational | Informationally dense, academic |
| Function word ratio | Content-heavy text | Grammatically structured text |

Typical ranges observed in English:

- **Academic prose**: Lexical density 0.55-0.65, noun ratio 0.25-0.35
- **Fiction**: Lexical density 0.45-0.55, verb ratio 0.15-0.25
- **Conversational**: Lexical density 0.35-0.45, adverb ratio 0.08-0.15

---

## Implementation

### Core Algorithm

The implementation uses spaCy's statistical POS tagger, which assigns Universal Dependencies POS tags to each token. The algorithm:

1. Loads the specified spaCy model and processes the input text.
2. Iterates over all tokens, filtering to alphabetic tokens only (punctuation, numbers, and symbols are excluded).
3. Classifies each token by its coarse POS tag (`token.pos_`):
   - `NOUN` and `PROPN` are counted as nouns.
   - `VERB` includes all verb forms (main verbs, auxiliaries are tagged separately by spaCy).
   - `ADJ` covers adjectives.
   - `ADV` covers adverbs.
   - `DET` covers determiners (articles, demonstratives).
   - `ADP` covers adpositions (prepositions in English).
   - `CCONJ` and `SCONJ` cover coordinating and subordinating conjunctions.
4. Computes all ratios with division-by-zero protection (returns `NaN` when denominators are zero).
5. Returns a `POSResult` dataclass with scalar values, distribution objects, and metadata including raw counts.

### Key Features

- **Proper noun inclusion**: Both common nouns (`NOUN`) and proper nouns (`PROPN`) are counted as nouns, reflecting their shared syntactic role as nominal elements.
- **Alphabetic-only counting**: Non-alphabetic tokens (punctuation, digits, symbols) are excluded from both numerators and denominators, ensuring ratios reflect genuine grammatical distribution.
- **Safe division**: The noun-verb ratio and adjective-noun ratio return `NaN` when the denominator is zero, preventing runtime errors on texts lacking those categories.
- **Distribution dataclass**: Results include `Distribution` objects for each metric, enabling downstream statistical analysis when chunked processing is used.
- **Rich metadata**: The result includes raw counts for all POS categories, the model name, and total token count, supporting reproducibility and debugging.

---

## Usage

### API Examples

```python
from pystylometry.syntactic import compute_pos_ratios

# Basic usage
result = compute_pos_ratios("The quick brown fox jumps over the lazy dog.")
print(f"Noun ratio: {result.noun_ratio:.3f}")
print(f"Verb ratio: {result.verb_ratio:.3f}")
print(f"Adjective ratio: {result.adjective_ratio:.3f}")
print(f"Adverb ratio: {result.adverb_ratio:.3f}")
print(f"Lexical density: {result.lexical_density:.3f}")
print(f"Function word ratio: {result.function_word_ratio:.3f}")
```

```python
# Cross-category ratios
result = compute_pos_ratios(long_text)
print(f"Noun-verb ratio: {result.noun_verb_ratio:.2f}")
print(f"Adjective-noun ratio: {result.adjective_noun_ratio:.2f}")
```

```python
# Accessing metadata for detailed analysis
result = compute_pos_ratios(text, model="en_core_web_md")
print(f"Total tokens analyzed: {result.metadata['token_count']}")
print(f"Noun count: {result.metadata['noun_count']}")
print(f"Verb count: {result.metadata['verb_count']}")
print(f"Model used: {result.metadata['model']}")
```

```python
# Comparing two texts
academic = compute_pos_ratios(academic_text)
fiction = compute_pos_ratios(fiction_text)

print(f"Academic lexical density: {academic.lexical_density:.3f}")
print(f"Fiction lexical density: {fiction.lexical_density:.3f}")
print(f"Academic noun ratio: {academic.noun_ratio:.3f}")
print(f"Fiction noun ratio: {fiction.noun_ratio:.3f}")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | (required) | Input text to analyze |
| `model` | `str` | `"en_core_web_sm"` | spaCy model name. Larger models (e.g., `en_core_web_md`, `en_core_web_lg`) offer better tagging accuracy. |
| `chunk_size` | `int` | `1000` | Number of words per chunk. Included for API consistency; POS analysis runs in a single pass for accuracy. |

### Return Type

`POSResult` dataclass with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `noun_ratio` | `float` | Nouns / total tokens |
| `verb_ratio` | `float` | Verbs / total tokens |
| `adjective_ratio` | `float` | Adjectives / total tokens |
| `adverb_ratio` | `float` | Adverbs / total tokens |
| `noun_verb_ratio` | `float` | Nouns / verbs |
| `adjective_noun_ratio` | `float` | Adjectives / nouns |
| `lexical_density` | `float` | Content words / total tokens |
| `function_word_ratio` | `float` | Function words / total tokens |
| `metadata` | `dict` | Raw counts, model name, token count |

---

## Limitations

- **Tagger accuracy**: POS ratios depend entirely on the accuracy of the spaCy tagger. The small model (`en_core_web_sm`) achieves approximately 97% accuracy on standard English; domain-specific or historical texts may see lower accuracy.
- **Language specificity**: The implementation assumes English POS categories using the Universal Dependencies tagset. While spaCy supports other languages, the interpretation guidelines (lexical density norms, genre expectations) are English-specific.
- **Proper noun conflation**: Proper nouns and common nouns are merged into a single noun count. For some applications (e.g., named entity density analysis), separate counts may be preferable.
- **Single-pass analysis**: The `chunk_size` parameter is accepted for API consistency but does not trigger chunked processing. POS analysis runs on the full text in a single spaCy pass.
- **Auxiliary verbs**: spaCy may tag auxiliaries as `AUX` rather than `VERB`. The current implementation counts only `VERB` tokens, which excludes auxiliaries from the verb ratio. This is intentional, as content verb frequency is more stylistically informative than total verb frequency.
- **Alphabetic-only filter**: Tokens containing digits or special characters are excluded. This means hyphenated words and contractions may be partially counted depending on spaCy's tokenization.

---

## References

- Biber, D. (1988). *Variation across speech and writing*. Cambridge University Press.
- Biber, D., & Conrad, S. (2009). *Register, genre, and style*. Cambridge University Press.
- Halliday, M. A. K. (1985). *An introduction to functional grammar*. Edward Arnold.
- Ure, J. (1971). Lexical density and register differentiation. In G. Perren & J. Trim (Eds.), *Applications of linguistics* (pp. 443-452). Cambridge University Press.
- Stamatatos, E. (2009). A survey of modern authorship attribution methods. *Journal of the American Society for Information Science and Technology*, 60(3), 538-556.

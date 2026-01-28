# Dialect Detection

## Regional Linguistic Preference Analysis for Stylometric Fingerprinting

---

## Theoretical Background

### Origins

Dialectometry, established by Hans Goebl (1982), provides the quantitative framework for measuring dialect similarity across texts. Rather than selecting individual "characteristic" features, modern dialectometry quantifies holistically across all available markers, capturing the cumulative signature of regional language use. Nerbonne (2009) extended this data-driven approach to computational dialectology, demonstrating that aggregate measures across many features yield more reliable dialect classification than any single marker.

Markedness theory, formalized by Battistella (1990), informs the markedness scoring component. In linguistics, a "marked" form stands out against the "unmarked" (default or standard) form. High markedness in a text suggests intentional stylistic choice or strong dialect identity. The concept applies directly to stylometry: a writer who consistently uses "colour" instead of "color" is producing marked text relative to American English.

Eye dialect -- spellings like "gonna," "wanna," and "gotta" that look nonstandard but reflect standard pronunciation -- indicates informal register rather than regional dialect. The module tracks these separately, following the linguistic distinction between dialect markers (regional identity) and register markers (formality level).

### Mathematical Foundation

The dialect detection process operates at four linguistic levels:

1. **Lexical level** (vocabulary): Direct word matching against known British/American vocabulary pairs (e.g., flat/apartment, lorry/truck). Weight: 1.0 per match.

2. **Phonological level** (spelling): Direct spelling pair matching (e.g., grey/gray, cheque/check). Weight: 0.9 per match, reflecting high discriminative value.

3. **Morphological level** (spelling patterns): Regex-based pattern matching for systematic spelling differences (-ise/-ize, -our/-or, -re/-er). Weights from the JSON marker database, reflecting linguistic salience.

4. **Syntactic level** (grammar patterns): Phrase-level matching for grammatical constructions (e.g., "have got" vs. "gotten," collective noun agreement). Weights from the JSON marker database.

**Score Normalization**:

```
normalized_score = weighted_marker_count * (1000 / word_count)
dialect_score = min(normalized_score / 50, 1.0)
```

Scores are normalized to per-1000-words for cross-chunk comparability, then scaled to a 0.0-1.0 range assuming a practical maximum of 50 markers per 1000 words.

**Markedness Score**:

Following Battistella (1990):

```
markedness = 0.7 * dialect_component + 0.3 * register_component
```

Where:
- `dialect_component = (british_score + american_score) / 2`
- `register_component = min(eye_dialect_ratio / 10, 1.0)`

The weighting reflects that dialect markers carry more stylometric significance than register markers.

**Classification Rules**:

| Condition | Classification |
|-----------|----------------|
| Both scores < 0.05 | Neutral |
| Score ratio difference < 0.2 | Mixed |
| British ratio > American ratio | British |
| American ratio > British ratio | American |

### Interpretation

The dialect detector serves multiple purposes in stylometry:

- **Authorship attribution**: Consistent dialect usage is a strong authorship signal. A British writer using "colour" and "programme" consistently differs from an American writer.
- **AI-generated content detection**: Large language models often produce inconsistent dialect markers (mixing British and American forms), resulting in "mixed" classification or high variance across chunks.
- **Deanonymization defense**: As noted by the Whonix Project, dialect markers can reveal a writer's geographic origin (Labov, 2006).

---

## Implementation

### Core Algorithm

The pystylometry implementation uses an extensible JSON marker database with native chunked analysis:

1. **Chunking**: Split text into chunks of `chunk_size` words using `chunk_text()`
2. **Per-chunk analysis**: For each chunk:
   - Tokenize words using regex pattern `\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b`
   - Match vocabulary against British and American word sets
   - Match individual spelling pairs (grey/gray, etc.)
   - Apply regex patterns for systematic spelling differences
   - Match grammar patterns using compiled regex
   - Count eye dialect markers separately
   - Apply feature weights from the JSON database
3. **Normalization**: Convert raw counts to per-1000-word rates, then to 0.0-1.0 scores
4. **Distribution building**: Aggregate per-chunk scores into `Distribution` objects
5. **Classification**: Apply classification rules to mean scores

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | (required) | Input text to analyze |
| `chunk_size` | 1000 | Number of words per chunk |

### Key Features

- **Extensible JSON markers**: The dialect marker database (`dialect_markers.json`) can be extended with additional vocabulary, spelling patterns, and grammar rules without code changes.
- **Four linguistic levels**: Detection operates at lexical, phonological, morphological, and syntactic levels for comprehensive coverage.
- **Feature weighting**: Different marker types carry different weights based on their discriminative value in linguistic research.
- **Exception handling**: Spelling patterns include exception lists (e.g., "size" is excluded from the -ise/-ize pattern because it is standard in both dialects).
- **Native chunked analysis**: Per-chunk analysis with distribution statistics reveals whether dialect usage is consistent (single author) or variable (mixed authorship, AI-generated).
- **Register separation**: Eye dialect is tracked separately from true dialect markers, maintaining the linguistic distinction between regional and formality variation.

### Return Value

The function returns a `DialectResult` dataclass containing:

- `dialect`: Classification string (`"british"`, `"american"`, `"mixed"`, `"neutral"`)
- `confidence`: Classification confidence (0.0-1.0)
- `british_score` / `american_score`: Mean dialect scores (0.0-1.0)
- `markedness_score`: How far the text deviates from unmarked standard English (0.0-1.0)
- `british_score_dist` / `american_score_dist` / `markedness_score_dist`: `Distribution` objects
- `markers_by_level`: Dictionary mapping linguistic levels to detected markers
- `spelling_markers` / `vocabulary_markers` / `grammar_markers`: Detailed marker breakdowns
- `eye_dialect_count` / `eye_dialect_ratio`: Register marker statistics
- `register_hints`: Computed register indicators
- `chunk_size` / `chunk_count`: Chunking parameters
- `metadata`: Additional analysis metadata including marker database version

---

## Usage

### API Examples

```python
from pystylometry.dialect import compute_dialect

# Basic dialect detection
result = compute_dialect("The colour of the programme was brilliant.")
print(f"Dialect: {result.dialect}")          # 'british'
print(f"Confidence: {result.confidence:.2f}") # 0.85
print(f"British score: {result.british_score:.3f}")
print(f"American score: {result.american_score:.3f}")
print(f"Markedness: {result.markedness_score:.3f}")

# Detect mixed dialect (possible AI-generated content)
result = compute_dialect(
    "I love the color of autumn leaves in the neighbourhood."
)
print(f"Dialect: {result.dialect}")  # 'mixed'

# Inspect marker breakdown
print(f"Spelling markers: {result.spelling_markers}")
print(f"Vocabulary markers: {result.vocabulary_markers}")
print(f"Grammar markers: {result.grammar_markers}")
print(f"Markers by level: {result.markers_by_level}")

# Use distribution statistics for authorship analysis
result = compute_dialect(long_document, chunk_size=1000)
print(f"British score std: {result.british_score_dist.std:.4f}")
print(f"Markedness IQR: {result.markedness_score_dist.iqr:.4f}")

# Detect eye dialect (informal register)
result = compute_dialect("I'm gonna wanna go there.")
print(f"Eye dialect count: {result.eye_dialect_count}")
print(f"Eye dialect ratio: {result.eye_dialect_ratio:.2f} per 1000 words")
```

---

## Limitations

### Binary Dialect Model

The current implementation focuses on British vs. American English. Other English dialects (Australian, South African, Indian, Scottish) are not separately modeled. Text from these regions may be classified as "mixed" or assigned to the nearest modeled dialect.

### Marker Coverage

The JSON marker database is necessarily incomplete. Rare or domain-specific dialect markers may not be included. The extensible design allows additions, but the baseline database prioritizes high-frequency, well-documented markers.

### Context Independence

The detector matches markers without considering context. A word like "boot" (British for car trunk) is ambiguous without context. The current implementation matches all occurrences, which may produce false positives in texts where such words appear in non-dialect senses.

### Text Length

Short texts may contain too few markers for reliable classification. The classification thresholds are designed for texts of at least several hundred words. For short texts, the confidence score will reflect the limited evidence.

### Eye Dialect Sensitivity

The eye dialect detector uses a fixed word list. Novel informal spellings not in the list will not be detected.

---

## References

Battistella, Edwin L. *Markedness: The Evaluative Superstructure of Language*. State University of New York Press, 1990.

Goebl, Hans. *Dialektometrie: Prinzipien und Methoden des Einsatzes der numerischen Taxonomie im Bereich der Dialektgeographie*. Verlag der Osterreichischen Akademie der Wissenschaften, 1982.

Labov, William. *The Social Stratification of English in New York City*. Cambridge University Press, 2006.

Nerbonne, John. "Data-Driven Dialectology." *Language and Linguistics Compass*, vol. 3, no. 1, 2009, pp. 175-198.

Whonix Project. "Stylometry: Deanonymization Techniques." *Whonix Wiki*, https://www.whonix.org/wiki/Stylometry

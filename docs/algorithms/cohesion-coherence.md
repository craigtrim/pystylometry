# Cohesion and Coherence Metrics

## Measuring How Text Holds Together

Cohesion and coherence metrics measure how well a text holds together structurally (cohesion) and semantically (coherence). These metrics are critical for analyzing writing quality, readability, and authorial sophistication.

---

## Theoretical Background

### Origins

- **Halliday & Hasan (1976)**: Defined cohesion as linguistic resources that link parts of a text, categorizing them into reference, substitution, ellipsis, conjunction, and lexical cohesion.
- **Graesser et al. (2011)**: Developed Coh-Metrix, measuring over 100 indices of text difficulty and cohesion.
- **McNamara et al. (2010)**: Extended cohesion research to automated text evaluation.

### Cohesion vs. Coherence

**Cohesion** refers to explicit linguistic connections: pronouns referring back to nouns, conjunctions signaling relationships, and lexical repetition maintaining topic continuity.

**Coherence** refers to implicit logical connections: whether the text makes sense as a whole and whether ideas flow logically.

---

## Metric Categories

### Referential Cohesion

| Metric | Description |
|--------|-------------|
| `pronoun_density` | Pronouns per 100 words |
| `demonstrative_density` | Demonstratives (this, that, these, those) per 100 words |
| `anaphora_count` | Total anaphoric references detected |
| `anaphora_resolution_ratio` | Proportion of pronouns with identifiable antecedents |

### Lexical Cohesion

| Metric | Description |
|--------|-------------|
| `word_repetition_ratio` | Proportion of content words appearing in multiple sentences |
| `lexical_chain_count` | Number of lexical chains (repeated content words) |
| `mean_chain_length` | Average length of lexical chains |
| `content_word_overlap` | Mean Jaccard similarity of content words between adjacent sentences |

### Connectives

**Categories:**
- **Additive**: and, also, furthermore, moreover, additionally
- **Adversative**: but, however, nevertheless, yet, although
- **Causal**: because, therefore, thus, hence, consequently
- **Temporal**: then, after, before, when, finally

| Metric | Description |
|--------|-------------|
| `connective_density` | Total connectives per 100 words |
| `additive_connective_ratio` | Proportion of additive connectives |
| `adversative_connective_ratio` | Proportion of adversative connectives |
| `causal_connective_ratio` | Proportion of causal connectives |
| `temporal_connective_ratio` | Proportion of temporal connectives |

### Coherence Measures

| Metric | Description |
|--------|-------------|
| `adjacent_sentence_overlap` | Mean content word overlap between consecutive sentences |
| `mean_sentence_similarity` | Mean pairwise Jaccard similarity across all sentences |
| `paragraph_topic_consistency` | Consistency of vocabulary within paragraphs |
| `semantic_coherence_score` | Composite score (0-1) combining multiple coherence indicators |

### Structural Coherence

| Metric | Description |
|--------|-------------|
| `paragraph_count` | Number of paragraphs (separated by blank lines) |
| `mean_paragraph_length` | Mean sentences per paragraph |
| `discourse_structure_score` | Quality of intro/body/conclusion structure (0-1) |

---

## Implementation

### API

```python
from pystylometry.stylistic import compute_cohesion_coherence

result = compute_cohesion_coherence(text, model="en_core_web_sm")
```

### Dependencies

Requires spaCy:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

---

## Example Usage

### Analyzing Academic Text

```python
from pystylometry.stylistic import compute_cohesion_coherence

academic_text = """
This study examines the relationship between exercise and mental health.
Previous research has shown that physical activity reduces stress.
However, the mechanisms underlying these effects remain unclear.
Therefore, we conducted a randomized controlled trial.

The participants were randomly assigned to two groups.
After eight weeks, we measured psychological outcomes.

The results indicate significant improvements in the exercise group.
These findings suggest that regular physical activity benefits mental health.
"""

result = compute_cohesion_coherence(academic_text)

print(f"Pronoun density: {result.pronoun_density:.2f} per 100 words")
print(f"Connective density: {result.connective_density:.2f} per 100 words")
print(f"Semantic coherence: {result.semantic_coherence_score:.2f}")
```

### Examining Connective Distribution

```python
result = compute_cohesion_coherence(text)

print("Connective distribution:")
print(f"  Additive: {result.additive_connective_ratio:.1%}")
print(f"  Adversative: {result.adversative_connective_ratio:.1%}")
print(f"  Causal: {result.causal_connective_ratio:.1%}")
print(f"  Temporal: {result.temporal_connective_ratio:.1%}")
```

---

## Applications

### Writing Quality Assessment

Low connective density may indicate choppy prose. Low content word overlap suggests topic drift. Weak discourse structure indicates organizational problems.

### Authorship Analysis

Authors have characteristic cohesion patterns: connective preferences, pronoun usage density, and paragraph structure habits.

### AI-Generated Text Detection

AI text often shows distinctive cohesion patterns: higher uniformity in connective usage and atypical lexical chain patterns.

---

## Limitations

- **Simplified anaphora resolution**: Uses heuristics rather than true coreference resolution.
- **No synonym detection**: Lexical cohesion is based on exact word matches (lemmatized), not semantic similarity.
- **Jaccard similarity**: Sentence similarity uses word overlap rather than embedding-based semantics.
- **English-centric**: Connective and demonstrative lists are English-specific.

---

## References

Graesser, A. C., McNamara, D. S., & Kulikowich, J. M. (2011). Coh-Metrix: Providing multilevel analyses of text characteristics. Educational Researcher, 40(5), 223-234.

Halliday, M. A. K., & Hasan, R. (1976). Cohesion in English. Longman.

McNamara, D. S., Graesser, A. C., McCarthy, P. M., & Cai, Z. (2014). Automated evaluation of text and discourse with Coh-Metrix. Cambridge University Press.

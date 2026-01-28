# Genre and Register Classification

## Identifying Text Types and Formality Levels

Genre and register analysis identifies the type of text (academic, journalistic, fiction, legal, conversational) and its formality level by examining linguistic features such as vocabulary origin, nominalization density, pronoun usage, and discourse markers.

---

## Theoretical Background

### Origins

Register and genre classification draws on Douglas Biber's multidimensional analysis framework (Biber 1988), which identified systematic linguistic differences across text types using factor analysis of 67 linguistic features. Biber found that features like nominalizations, passive voice, and pronoun usage cluster in predictable ways that distinguish registers.

The formality scoring is based on the F-score proposed by Heylighen and Dewaele (1999), which quantifies formality as the degree to which language explicitly marks meaning through nouns, adjectives, and prepositions rather than relying on context.

Register classification uses Martin Joos's "Five Clocks" model (Joos 1961), which describes five levels of formality: frozen, formal, consultative, casual, and intimate.

### Key Concepts

**Register** refers to the variety of language associated with a particular situational context — the relationship between participants, the channel of communication, and the purpose. Registers vary along a formality continuum.

**Genre** refers to the conventionalized text type associated with a communicative purpose — academic papers, news articles, fiction, legal documents, etc. Genres have characteristic linguistic features.

**Formality** is measured through several proxies:
- **Latinate vs. Germanic vocabulary**: Words of Latin/French origin (e.g., *demonstrate*, *significant*, *constitute*) signal formal register; Germanic/Anglo-Saxon words (e.g., *show*, *big*, *make*) signal informal register
- **Nominalizations**: Verbs/adjectives turned into nouns (*investigate* → *investigation*) are characteristic of formal, academic writing (Biber 1988)
- **Passive voice**: Formal texts prefer passive constructions (*was demonstrated*) over active voice
- **Pronoun distribution**: First/second person pronouns indicate informal or personal style; third person and impersonal constructions indicate formal style

### Formality Score

The composite formality score (0–100) is adapted from Heylighen & Dewaele (1999):

```
formality = latinate_score + nominalization_score + passive_score
            - first_person_penalty - conversational_penalty
```

Where each component is bounded and weighted:
- Latinate vocabulary ratio: 0–40 points
- Nominalization density: 0–20 points (academic text typically has 3–6 per 100 words)
- Passive voice density: 0–15 points (formal text typically has 1–3 per 100 words)
- First person pronoun penalty: up to -15 points
- Conversational marker penalty: up to -20 points

### Register Classification

Registers follow Joos's Five Clocks (1961):

| Register | Formality Score | Characteristics |
|----------|----------------|-----------------|
| Frozen | ≥80 (or ≥3 legal markers) | Ritualized, unchanging (legal documents, prayers) |
| Formal | 60–79 | One-way, no feedback expected (academic papers, reports) |
| Consultative | 40–59 | Professional discourse (business, technical) |
| Casual | 20–39 | Relaxed, everyday speech (conversations with friends) |
| Intimate | <20 | Private, personal (close relationships) |

### Genre Prediction

Genre scores (0.0–1.0) are computed for five categories using weighted feature combinations:

- **Academic**: High nominalizations, Latinate ratio, passive voice, academic markers, impersonal constructions
- **Journalistic**: Journalistic markers, quotation density, middle formality, third person, mixed narrative/expository
- **Fiction**: Dialogue, narrative markers, concrete nouns, first person, lower Latinate ratio
- **Legal**: Legal markers, nominalizations, passive voice, Latinate ratio, high formality
- **Conversational**: Conversational markers, first/second person pronouns, low Latinate ratio, low formality

The predicted genre is the highest-scoring category. Confidence incorporates the margin over the second-best score.

---

## Implementation

### Core Algorithm

The `compute_genre_register` function extracts all features from a single text and returns a comprehensive result:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | (required) | Input text to analyze |
| `model` | `"en_core_web_sm"` | Reserved for future spaCy integration (currently unused) |

### Feature Extraction

The implementation uses regex-based heuristics (no external NLP dependencies required):

1. **Vocabulary classification**: Words are classified as Latinate or Germanic using curated word lists and suffix-based heuristics. Words longer than 6 characters with Latinate suffixes (-tion, -sion, -ment, -ity, etc.) are counted as Latinate. Short words (≤4 characters) without Latinate suffixes are counted as Germanic.

2. **Nominalization detection**: Words longer than 5 characters ending in -tion, -sion, -ment, -ness, -ity, -ance, -ence are counted as nominalizations.

3. **Passive voice detection**: Regex pattern matching for forms of "be" followed by optional adverb and past participle (-ed endings plus common irregular forms).

4. **Pronoun counting**: Separate counts for first person (I, me, my, we, us, our...), second person (you, your, yours...), and third person (he, she, it, they, one...).

5. **Abstract/concrete noun detection**: Abstract nouns identified by suffixes (-ness, -ity, -ism, -hood, -dom, etc.); concrete nouns matched against a curated list of physical objects (body parts, natural objects, man-made objects, animals, food, clothing).

6. **Narrative vs. expository markers**: Narrative markers include temporal words (suddenly, meanwhile), dialogue tags (said, whispered), and motion verbs (walked, ran). Expository markers include logical connectors (therefore, furthermore), definitional verbs (defined, comprises), and structural markers (firstly, additionally).

7. **Register-specific markers**: Separate word lists for legal (hereby, notwithstanding, pursuant), academic (hypothesis, methodology, correlation), journalistic (reported, alleged, sources), and conversational (yeah, gonna, awesome) registers.

8. **Dialogue detection**: Quotation marks are used to estimate the proportion of text that is dialogue.

9. **Technical terms**: Detected via acronyms (2–5 uppercase letters), alphanumeric tokens, and very long words (>12 characters).

### Return Type

`GenreRegisterResult` contains:

- **Formality indicators**: `formality_score`, `latinate_ratio`, `nominalization_density`, `passive_voice_density`
- **Personal style**: `first_person_ratio`, `second_person_ratio`, `third_person_ratio`, `impersonal_construction_density`
- **Vocabulary type**: `abstract_noun_ratio`, `concrete_noun_ratio`, `abstractness_score`, `technical_term_density`, `jargon_density`
- **Discourse mode**: `narrative_marker_density`, `expository_marker_density`, `narrative_expository_ratio`, `dialogue_ratio`, `quotation_density`
- **Classification**: `register_classification`, `predicted_genre`, `genre_confidence`
- **Genre scores**: `academic_score`, `journalistic_score`, `fiction_score`, `legal_score`, `conversational_score`
- **Metadata**: Raw counts, computation time

---

## Usage

### Basic Analysis

```python
from pystylometry.stylistic import compute_genre_register

result = compute_genre_register("The investigation demonstrates that the correlation...")

print(f"Formality score: {result.formality_score:.1f}")
print(f"Register: {result.register_classification}")
print(f"Predicted genre: {result.predicted_genre} ({result.genre_confidence:.1%})")
```

### Comparing Texts

```python
academic = compute_genre_register("""
    The investigation demonstrates that the correlation between
    nominalization frequency and formality is statistically significant.
""")

fiction = compute_genre_register("""
    She walked slowly down the dark corridor, her heart pounding.
    "Who's there?" she whispered into the shadows.
""")

print(f"Academic formality: {academic.formality_score:.1f}")
print(f"Fiction formality: {fiction.formality_score:.1f}")

print(f"Academic genre: {academic.predicted_genre}")
print(f"Fiction genre: {fiction.predicted_genre}")
```

### Examining Feature Details

```python
result = compute_genre_register(long_text)

# Genre score breakdown
print(f"Academic:       {result.academic_score:.3f}")
print(f"Journalistic:   {result.journalistic_score:.3f}")
print(f"Fiction:         {result.fiction_score:.3f}")
print(f"Legal:           {result.legal_score:.3f}")
print(f"Conversational:  {result.conversational_score:.3f}")

# Linguistic features
print(f"Latinate ratio: {result.latinate_ratio:.3f}")
print(f"Nominalization density: {result.nominalization_density:.2f} per 100 words")
print(f"Passive voice density: {result.passive_voice_density:.2f} per 100 words")
print(f"Narrative/expository ratio: {result.narrative_expository_ratio:.2f}")

# Raw counts in metadata
print(f"Word count: {result.metadata['word_count']}")
print(f"Pronoun counts: {result.metadata['pronoun_counts']}")
```

---

## Limitations

### Heuristic Approach

The current implementation uses regex-based heuristics rather than full NLP parsing. This means:
- Passive voice detection may miss complex constructions or produce false positives
- Word classification relies on suffix patterns, which can misclassify some words
- The `model` parameter is reserved for future spaCy integration but currently unused

### Vocabulary Lists

The Latinate/Germanic word lists and register marker lists are curated but not exhaustive. Texts with specialized vocabulary outside these lists may receive less accurate genre predictions.

### Short Text Sensitivity

Very short texts (under ~50 words) may not contain enough features for reliable classification. The formality score and genre predictions are more stable with longer passages.

### Genre Boundaries

Real-world texts often blend genre conventions. A newspaper feature story may contain narrative elements; an academic paper may include conversational asides. The genre scores reflect this: examine all five scores rather than relying solely on the predicted genre.

### English Only

All word lists and patterns are designed for English text. Non-English texts will produce unreliable results.

---

## References

Biber, Douglas. *Variation across Speech and Writing*. Cambridge University Press, 1988.

Biber, Douglas, and Susan Conrad. *Register, Genre, and Style*. Cambridge University Press, 2009.

Heylighen, Francis, and Jean-Marc Dewaele. "Formality of Language: Definition, Measurement and Behavioral Determinants." Internal Report, Center "Leo Apostel", Free University of Brussels, 1999.

Joos, Martin. *The Five Clocks*. Harcourt, Brace & World, 1961.

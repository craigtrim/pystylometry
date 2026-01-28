# Stylistic Markers

## Detecting Authorial Fingerprints Through Language Habits

Stylistic markers are specific linguistic features that authors use consistently and often subconsciously. These include contraction preferences, intensifier usage, hedging patterns, modal auxiliaries, negation patterns, and punctuation style habits. Because these features are difficult to consciously control, they serve as powerful indicators of authorial identity.

---

## Theoretical Background

### Origins

Research on stylistic markers draws from multiple fields:

- **Corpus Linguistics**: Biber's work on register variation demonstrated that function words and grammatical features differentiate text types more reliably than content words (Biber 1988).
- **Psychology of Language**: Pennebaker's research on pronoun usage revealed that small function words carry significant psychological and social meaning (Pennebaker 2011).
- **Authorship Attribution**: Argamon and Levitan showed that function word frequencies outperform content-based features for author identification (Argamon & Levitan 2005).

### Why Stylistic Markers Work

**Subconscious usage**: Authors don't deliberately vary these features. Contraction preferences, intensifier choices, and hedging patterns remain consistent even when an author attempts to disguise their style.

**Genre-independent**: Unlike vocabulary that shifts with topic, stylistic markers remain stable across different subjects. An author who favors "really" over "very" as an intensifier will do so whether writing about cooking or quantum physics.

**Psychologically meaningful**: These markers correlate with personality traits, emotional states, and cognitive patterns. High hedge usage often indicates analytical thinking; frequent intensifiers may signal emotional engagement.

---

## Marker Categories

### Contractions

Contraction usage indicates formality level and authorial habit. Some authors consistently prefer contracted forms ("can't", "don't", "I'm") while others favor expanded forms ("cannot", "do not", "I am").

The contraction ratio measures preference:

```
contraction_ratio = contractions / (contractions + expanded_forms)
```

A ratio near 1.0 indicates informal style with consistent contraction use. A ratio near 0.0 indicates formal style avoiding contractions.

**Tracked contractions include:**
- Negative contractions: can't, won't, don't, shouldn't, etc.
- Pronoun contractions: I'm, you're, he's, they've, etc.
- Other contractions: let's, that's, there's, etc.

### Intensifiers

Intensifiers amplify meaning. Their frequency and variety reveal authorial emphatic style.

**Categories:**
- **Amplifiers**: very, really, extremely, absolutely, completely, totally
- **Degree modifiers**: quite, rather, fairly, pretty, somewhat
- **Informal intensifiers**: super, way, real, awfully

Density is measured per 100 words for interpretability. An intensifier density of 5.0 means 5 intensifiers per 100 words.

### Hedges

Hedges weaken or qualify statements, expressing uncertainty or politeness.

**Categories:**
- **Epistemic hedges**: maybe, perhaps, possibly, probably, apparently
- **Approximators**: about, around, roughly, nearly, almost, virtually
- **Shield expressions**: seems, appears, suggests, indicates, tends

High hedge usage often indicates academic or cautious writing style. Low hedge usage may signal confident or assertive style.

### Modal Auxiliaries

Modal verbs express necessity, possibility, and permission. Their distribution reveals authorial stance.

**Epistemic modals** (possibility/probability):
- may, might, could, can, would

**Deontic modals** (necessity/obligation):
- must, shall, will, should, ought

The epistemic/deontic ratio indicates whether an author tends toward speculative (epistemic) or prescriptive (deontic) language.

### Negation Patterns

Negation frequency and type vary by author. Some writers favor direct negation ("not", "no") while others prefer implicit negation ("hardly", "barely", "rarely").

**Tracked markers:**
- Direct: not, no, never, none, nothing, nobody, nowhere
- Implicit: hardly, barely, scarcely, rarely, seldom
- Conjunctive: neither, nor, without

### Punctuation Style

Punctuation habits reveal authorial voice and genre conventions.

| Marker | Indicates |
|--------|-----------|
| Exclamation marks (!) | Emphatic, emotional style |
| Question marks (?) | Interactive, rhetorical style |
| Quotation marks | Dialogue, scare quotes |
| Parentheses () | Asides, qualification |
| Ellipses ... | Trailing off, suspense |
| Dashes — | Interruptions, emphasis |
| Semicolons ; | Sophisticated syntax |
| Colons : | Explanation, enumeration |

---

## Implementation

### API

```python
from pystylometry.stylistic import compute_stylistic_markers

result = compute_stylistic_markers(text)
```

### Result Fields

**Contraction analysis:**
- `contraction_ratio`: Float 0-1 indicating preference for contractions
- `contraction_count`: Total contractions detected
- `expanded_form_count`: Total expanded forms detected
- `top_contractions`: List of (contraction, count) tuples

**Intensifier analysis:**
- `intensifier_density`: Intensifiers per 100 words
- `intensifier_count`: Total intensifiers
- `top_intensifiers`: List of (word, count) tuples

**Hedge analysis:**
- `hedging_density`: Hedges per 100 words
- `hedging_count`: Total hedges
- `top_hedges`: List of (word, count) tuples

**Modal analysis:**
- `modal_density`: Modals per 100 words
- `modal_distribution`: Dict mapping each modal to its count
- `epistemic_modal_ratio`: Proportion of epistemic modals
- `deontic_modal_ratio`: Proportion of deontic modals

**Negation analysis:**
- `negation_density`: Negation markers per 100 words
- `negation_count`: Total negation markers
- `negation_types`: Dict mapping each marker to its count

**Punctuation analysis:**
- `exclamation_density`: Per 100 words
- `question_density`: Per 100 words
- `quotation_density`: Per 100 words
- `parenthetical_density`: Per 100 words
- `ellipsis_density`: Per 100 words
- `dash_density`: Per 100 words
- `semicolon_density`: Per 100 words
- `colon_density`: Per 100 words

---

## Example Usage

### Analyzing Formality

```python
from pystylometry.stylistic import compute_stylistic_markers

formal_text = """
The committee has determined that the proposal cannot be approved
at this time. We do not have sufficient evidence to support the
conclusions presented in the document.
"""

informal_text = """
I can't believe they didn't approve it! We've worked so hard on this
and it's really frustrating. Don't they understand what we're trying
to do here?
"""

formal_result = compute_stylistic_markers(formal_text)
informal_result = compute_stylistic_markers(informal_text)

print(f"Formal contraction ratio: {formal_result.contraction_ratio:.2f}")
# Output: 0.00 (no contractions)

print(f"Informal contraction ratio: {informal_result.contraction_ratio:.2f}")
# Output: 1.00 (all contracted forms)

print(f"Informal exclamation density: {informal_result.exclamation_density:.2f}")
# Output: High density of exclamation marks
```

### Detecting Hedging Style

```python
academic_text = """
The results suggest that the proposed methodology may be applicable
to a wide range of scenarios. It appears that the correlation is
statistically significant, although this finding should perhaps be
interpreted with caution.
"""

result = compute_stylistic_markers(academic_text)

print(f"Hedging density: {result.hedging_density:.2f} per 100 words")
print(f"Top hedges: {result.top_hedges[:3]}")
# Shows: suggest, may, appears, perhaps, should
```

### Comparing Modal Usage

```python
speculative_text = "This might work. It could be useful. We may try it."
prescriptive_text = "You must follow the rules. You shall comply. You will succeed."

spec_result = compute_stylistic_markers(speculative_text)
presc_result = compute_stylistic_markers(prescriptive_text)

print(f"Speculative epistemic ratio: {spec_result.epistemic_modal_ratio:.2f}")
# High epistemic ratio (might, could, may)

print(f"Prescriptive deontic ratio: {presc_result.deontic_modal_ratio:.2f}")
# High deontic ratio (must, shall, will)
```

---

## Applications

### Authorship Attribution

Compare marker profiles across known texts to identify authorial patterns:

```python
# Analyze texts from known authors
author_a_profile = compute_stylistic_markers(author_a_corpus)
author_b_profile = compute_stylistic_markers(author_b_corpus)

# Analyze unknown text
unknown_profile = compute_stylistic_markers(unknown_text)

# Compare contraction ratios, hedge densities, modal distributions
```

### AI-Generated Content Detection

AI-generated text often shows distinctive marker patterns:
- Lower contraction ratios (formal style)
- Higher hedge density (qualifying statements)
- More uniform punctuation patterns
- Different modal distributions than human writers

### Forensic Linguistics

Stylistic markers can help identify:
- Ghostwritten sections in documents
- Multiple authors in collaborative work
- Changes in authorial state (fatigue, emotional distress)

---

## References

Argamon, S., & Levitan, S. (2005). Measuring the usefulness of function words for authorship attribution. ACH/ALLC.

Biber, D. (1988). Variation across speech and writing. Cambridge University Press.

Lakoff, G. (1972). Hedges: A study in meaning criteria and the logic of fuzzy concepts. Chicago Linguistic Society Papers, 8, 183-228.

Pennebaker, J. W. (2011). The secret life of pronouns: What our words say about us. Bloomsbury Press.

# Advanced Syntactic Analysis

## Measuring Structural Complexity Through Dependency Parsing

Advanced syntactic analysis extracts sophisticated complexity metrics from dependency parse trees. By computing parse tree depth, T-unit length, clausal density, passive voice ratio, subordination and coordination indices, dependency distance, and branching direction, this module captures the multidimensional nature of syntactic complexity that distinguishes writing proficiency levels, genres, and individual authorial styles.

---

## Theoretical Background

### Origins

The study of syntactic complexity in written language was pioneered by Kellogg Hunt (1965), who introduced the T-unit (minimal terminable unit) as a more reliable measure of syntactic maturity than sentence length. Hunt demonstrated that as writers mature, they produce longer T-units with greater clausal density -- not merely longer sentences, but sentences with more embedded and subordinated clauses.

Edward Gibson's (2000) Dependency Locality Theory extended complexity analysis to the processing domain, proposing that the distance between syntactically related words in a sentence correlates with cognitive processing difficulty. Longer dependency distances impose greater working memory demands, making texts with long-distance dependencies harder to comprehend.

Xiaofei Lu (2010) developed the L2 Syntactic Complexity Analyzer (L2SCA), operationalizing 14 syntactic complexity measures for second language writing assessment. Lu's work established that multiple complexity dimensions (length, subordination, coordination, phrasal elaboration) capture distinct aspects of syntactic development.

Douglas Biber's (1988) multidimensional analysis showed that syntactic features such as passive voice ratio, subordination frequency, and clause types vary systematically across registers and genres, providing a functional explanation for complexity variation.

### Mathematical Foundation

**Parse tree depth** is the maximum path length from root to any leaf in the dependency tree:

```
depth(token) = 0                                    if token has no children
depth(token) = max(depth(child) for child in children) + 1   otherwise
```

Mean parse tree depth is the average across all sentences:

```
mean_parse_tree_depth = (1/n) * sum(depth(root_i) for i in 1..n)
```

**T-unit length** follows Hunt (1965). A T-unit is one independent clause plus all subordinate clauses attached to it:

```
mean_t_unit_length = total_words_in_t_units / t_unit_count
```

**Clausal density** measures the number of clauses packed into each T-unit:

```
clausal_density = total_clauses / t_unit_count
```

Where total clauses include the main clause plus all dependent clauses (identified by dependency labels: `csubj`, `ccomp`, `xcomp`, `advcl`, `acl`, `relcl`) and coordinate verb clauses (`conj` with `VERB` POS).

**Passive voice ratio:**

```
passive_voice_ratio = passive_sentence_count / total_sentences
```

Passive constructions are detected via dependency labels containing `pass` (e.g., `nsubjpass`, `auxpass`, or the modern `nsubj:pass`).

**Subordination and coordination indices:**

```
subordination_index = subordinate_clause_count / total_clauses
coordination_index  = coordinate_clause_count / total_clauses
```

Subordinate clauses are identified by the labels `{advcl, acl, relcl}`. Coordinate clauses are verb conjuncts (`conj` with `VERB` POS).

**Dependency distance** is the mean absolute token-position difference between each dependent and its head:

```
dependency_distance = (1/m) * sum(|token.i - token.head.i| for all non-root tokens)
```

where *m* is the number of non-root tokens.

**Branching direction** measures the proportion of dependents that precede (left-branching) vs. follow (right-branching) their heads:

```
left_branching_ratio  = left_count / (left_count + right_count)
right_branching_ratio = right_count / (left_count + right_count)
```

**Sentence complexity score** is a weighted composite of normalized individual metrics:

```
complexity = 0.3 * (mean_depth / 10)
           + 0.3 * (clausal_density / 3)
           + 0.2 * (mean_t_unit_length / 25)
           + 0.1 * subordination_index
           + 0.1 * (dependency_distance / 5)
```

Each component is clamped to [0, 1] before weighting.

### Interpretation

| Metric | Low Values | High Values |
|--------|-----------|-------------|
| Parse tree depth | Flat syntax; simple, short sentences | Deep embedding; nested clauses and phrases |
| Mean T-unit length | Short, simple independent clauses | Long clauses with extensive modification |
| Clausal density | One clause per T-unit; simple structures | Multiple clauses per T-unit; complex embedding |
| Dependent clause ratio | Few dependent clauses; coordinate or simple style | Many dependent clauses; subordinate style |
| Passive voice ratio | Active, direct style; fiction, conversation | Formal, impersonal style; academic, legal, scientific |
| Subordination index | Coordinate or simple clause structure | Heavy use of adverbial, relative, and adnominal clauses |
| Coordination index | Little inter-clause coordination | Frequent use of "and", "but", "or" to join clauses |
| Dependency distance | Short, local dependencies; easy processing | Long-distance dependencies; higher cognitive load |
| Left branching ratio | Right-branching dominant (typical English) | Left-branching dominant (pre-modification heavy) |
| Complexity score | Syntactically simple text | Syntactically complex text |

Typical ranges by genre:

| Genre | Parse Depth | T-unit Length | Clausal Density | Passive Ratio |
|-------|-------------|---------------|-----------------|---------------|
| Academic | 5-8 | 20-30 words | 2.0-3.0 | 0.20-0.35 |
| Fiction | 3-6 | 12-20 words | 1.5-2.5 | 0.05-0.15 |
| Journalism | 3-5 | 15-22 words | 1.3-2.0 | 0.10-0.20 |
| Conversation | 2-4 | 8-14 words | 1.0-1.5 | 0.02-0.08 |

---

## Implementation

### Core Algorithm

The implementation uses spaCy's dependency parser to extract all metrics in a single pass:

1. **Parse tree depth**: Recursively computes the maximum depth of each sentence's dependency tree starting from the root token. Leaf tokens have depth 0; internal nodes have depth equal to the maximum child depth plus 1.

2. **Dependency distance**: Iterates over all non-root tokens in the document, computing the absolute difference between each token's index and its head's index. The mean of these distances is reported.

3. **T-unit identification**: In the current implementation, each sentence is treated as one T-unit. This is a simplifying assumption; a more sophisticated approach would split compound sentences into separate T-units at coordinating conjunctions.

4. **Clause counting**: For each sentence, counts:
   - Total clauses: 1 (main) + dependent clauses + coordinate verb clauses
   - Dependent clauses: tokens with `dep_` in `{csubj, ccomp, xcomp, advcl, acl, relcl}`
   - Subordinate clauses: the subset `{advcl, acl, relcl}`
   - Coordinate clauses: tokens with `dep_="conj"` and `pos_="VERB"`

5. **Passive voice detection**: Scans each sentence for dependency labels containing the string `"pass"` (covering `nsubjpass`, `auxpass`, and `nsubj:pass` across spaCy versions).

6. **Branching direction**: For each non-root token, checks whether the token precedes (left-branching) or follows (right-branching) its head based on token indices.

7. **Complexity score**: Normalizes five individual metrics to the [0, 1] range using empirically chosen denominators (depth/10, clausal density/3, T-unit length/25, dependency distance/5, subordination index already in [0,1]), then computes a weighted sum.

### Key Features

- **Comprehensive metric suite**: Thirteen distinct syntactic metrics capture complementary dimensions of complexity (structural depth, clause organization, voice, directionality, processing difficulty).
- **Cross-version passive detection**: Passive voice detection handles both older spaCy formats (`nsubjpass`, `auxpass`) and newer formats (`nsubj:pass`, `aux:pass`) via substring matching on dependency labels.
- **Composite complexity score**: The `sentence_complexity_score` provides a single summary metric that weights multiple dimensions, useful for quick comparisons across texts.
- **NaN safety**: All ratio computations guard against division by zero, returning `NaN` for metrics that cannot be computed from the input (e.g., clausal density when no T-units are found).
- **Rich metadata**: The result includes per-sentence parse depths, T-unit lengths, clause count breakdowns, dependency distance samples, branching counts, and model information for full reproducibility.
- **Empty text handling**: Empty or unparseable text returns `NaN` for all float metrics, 0 for all integer metrics, and a warning in metadata.

---

## Usage

### API Examples

```python
from pystylometry.syntactic import compute_advanced_syntactic

# Basic usage
result = compute_advanced_syntactic(
    "Although the weather was harsh, the expedition continued. "
    "They crossed the river and climbed the ridge before nightfall."
)

# Parse tree complexity
print(f"Mean parse tree depth: {result.mean_parse_tree_depth:.1f}")
print(f"Max parse tree depth: {result.max_parse_tree_depth}")

# T-unit metrics
print(f"T-unit count: {result.t_unit_count}")
print(f"Mean T-unit length: {result.mean_t_unit_length:.1f} words")

# Clause metrics
print(f"Clausal density: {result.clausal_density:.2f}")
print(f"Dependent clause ratio: {result.dependent_clause_ratio:.2f}")
print(f"Subordination index: {result.subordination_index:.2f}")
print(f"Coordination index: {result.coordination_index:.2f}")
```

```python
# Voice and directionality
result = compute_advanced_syntactic(academic_text)
print(f"Passive voice ratio: {result.passive_voice_ratio:.1%}")
print(f"Dependency distance: {result.dependency_distance:.2f}")
print(f"Left branching: {result.left_branching_ratio:.1%}")
print(f"Right branching: {result.right_branching_ratio:.1%}")
```

```python
# Composite complexity
result = compute_advanced_syntactic(text)
print(f"Complexity score: {result.sentence_complexity_score:.3f}")
# Values closer to 1.0 indicate higher syntactic complexity
```

```python
# Comparing writing proficiency or genre
beginner = compute_advanced_syntactic(beginner_essay)
advanced = compute_advanced_syntactic(advanced_essay)

print(f"Beginner complexity: {beginner.sentence_complexity_score:.3f}")
print(f"Advanced complexity: {advanced.sentence_complexity_score:.3f}")
print(f"Beginner clausal density: {beginner.clausal_density:.2f}")
print(f"Advanced clausal density: {advanced.clausal_density:.2f}")
print(f"Beginner subordination: {beginner.subordination_index:.2f}")
print(f"Advanced subordination: {advanced.subordination_index:.2f}")
```

```python
# Accessing detailed metadata
result = compute_advanced_syntactic(text, model="en_core_web_md")
print(f"Sentence count: {result.metadata['sentence_count']}")
print(f"Total clauses: {result.metadata['total_clauses']}")
print(f"Independent clauses: {result.metadata['independent_clause_count']}")
print(f"Dependent clauses: {result.metadata['dependent_clause_count']}")
print(f"Passive sentences: {result.metadata['passive_sentence_count']}")
print(f"Parse depths per sentence: {result.metadata['parse_depths_per_sentence']}")
print(f"T-unit lengths: {result.metadata['t_unit_lengths']}")
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | (required) | Input text to analyze. Multiple sentences recommended for stable metrics. |
| `model` | `str` | `"en_core_web_sm"` | spaCy model with dependency parser. Larger models (`en_core_web_md`, `en_core_web_lg`) provide better parsing accuracy. |
| `chunk_size` | `int` | `1000` | Number of words per chunk. Included for API consistency; analysis runs in a single pass. |

### Return Type

`AdvancedSyntacticResult` dataclass with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `mean_parse_tree_depth` | `float` | Average dependency tree depth across sentences |
| `max_parse_tree_depth` | `int` | Maximum dependency tree depth in any sentence |
| `t_unit_count` | `int` | Number of T-units identified |
| `mean_t_unit_length` | `float` | Average words per T-unit |
| `clausal_density` | `float` | Total clauses / T-unit count |
| `dependent_clause_ratio` | `float` | Dependent clauses / total clauses |
| `passive_voice_ratio` | `float` | Passive sentences / total sentences |
| `subordination_index` | `float` | Subordinate clauses / total clauses |
| `coordination_index` | `float` | Coordinate clauses / total clauses |
| `sentence_complexity_score` | `float` | Weighted composite complexity (0.0 to 1.0) |
| `dependency_distance` | `float` | Mean token distance between dependents and heads |
| `left_branching_ratio` | `float` | Left-branching dependencies / total dependencies |
| `right_branching_ratio` | `float` | Right-branching dependencies / total dependencies |
| `metadata` | `dict` | Clause counts, parse depths, T-unit lengths, model info |

---

## Limitations

- **T-unit simplification**: The current implementation treats each sentence as a single T-unit. Compound sentences containing multiple independent clauses should ideally be split into separate T-units (one per independent clause). This simplification means T-unit count equals sentence count, and mean T-unit length equals mean sentence length. The clausal density metric partially compensates by counting all clause types within each sentence.
- **Parser accuracy**: All metrics depend on the quality of spaCy's dependency parsing. The small model (`en_core_web_sm`) achieves approximately 89-92% unlabeled attachment score (UAS); larger models achieve 93-95%. Parsing errors propagate to all derived metrics.
- **Recursive depth computation**: Parse tree depth is computed recursively. Extremely long sentences with deeply nested structures could theoretically cause stack overflow, though this is unlikely with natural language text.
- **Open clausal complement ambiguity**: The `xcomp` label (open clausal complement) is counted as a dependent clause. Constructions like "I want to go" include `xcomp`, which some frameworks do not consider a full clause. This may inflate clausal density for texts with many control verb constructions.
- **Passive voice heuristic**: Passive detection uses substring matching on dependency labels (`"pass" in dep_`). While this covers both older and newer spaCy label formats, it could theoretically match non-passive labels containing the substring "pass" in future model versions.
- **Complexity score weights**: The composite `sentence_complexity_score` uses fixed weights (0.3, 0.3, 0.2, 0.1, 0.1) and fixed normalization denominators that were empirically chosen. These may not be optimal for all text types or languages.
- **English-centric branching assumptions**: The branching direction analysis assumes English word order conventions. Languages with different canonical word orders (SOV, VSO) will show different baseline branching ratios.
- **Dependency distance sampling**: For performance, the metadata includes only the first 100 dependency distances. The mean is computed from all distances, but detailed analysis of the full distribution requires external computation.
- **Single-pass processing**: The `chunk_size` parameter is accepted for API consistency but does not trigger chunked analysis.

---

## References

- Hunt, K. W. (1965). *Grammatical structures written at three grade levels*. NCTE Research Report No. 3. National Council of Teachers of English.
- Biber, D. (1988). *Variation across speech and writing*. Cambridge University Press.
- Lu, X. (2010). Automatic analysis of syntactic complexity in second language writing. *International Journal of Corpus Linguistics*, 15(4), 474-496.
- Gibson, E. (2000). The dependency locality theory: A distance-based theory of linguistic complexity. In A. Marantz, Y. Miyashita, & W. O'Neil (Eds.), *Image, language, brain* (pp. 95-126). MIT Press.
- Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. *Journal of Cognitive Science*, 9(2), 159-191.
- Wolfe-Quintero, K., Inagaki, S., & Kim, H.-Y. (1998). *Second language development in writing: Measures of fluency, accuracy, and complexity*. University of Hawaii Press.
- Ortega, L. (2003). Syntactic complexity measures and their relationship to L2 proficiency: A research synthesis of college-level L2 writing. *Applied Linguistics*, 24(4), 492-518.

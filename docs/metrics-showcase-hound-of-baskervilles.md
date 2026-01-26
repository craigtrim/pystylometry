# Stylometric Analysis: The Hound of the Baskervilles

This document demonstrates all available metrics in `pystylometry` by analyzing Arthur Conan Doyle's classic novel *The Hound of the Baskervilles* (1902).

## Text Summary

| Property | Value |
|----------|-------|
| **Author** | Arthur Conan Doyle |
| **Title** | The Hound of the Baskervilles |
| **Year** | 1902 |
| **Characters** | 353,192 |
| **Words** | ~59,112 |
| **Genre** | Detective Fiction |

---

## Lexical Metrics

Lexical metrics measure vocabulary richness, diversity, and usage patterns.

### Type-Token Ratio (TTR)

The Type-Token Ratio measures vocabulary diversity by comparing unique words (types) to total words (tokens).

| Metric | Value | Description |
|--------|-------|-------------|
| **Raw TTR** | 0.0970 | Direct ratio of types to tokens |
| **Root TTR (Guiraud's Index)** | 23.6079 | Types / sqrt(tokens) |
| **Log TTR (Herdan's C)** | 0.7877 | log(types) / log(tokens) |
| **STTR (Standardized)** | 0.4147 | TTR across fixed-size chunks |
| **Delta Std** | 0.0305 | Vocabulary consistency measure |
| **Total Types** | 5,747 | Unique words |
| **Total Tokens** | 59,261 | Total words |

**Interpretation:** The low raw TTR (0.097) is typical for long texts due to word repetition. The Root TTR of 23.61 indicates moderate vocabulary richness for a novel of this length.

### MTLD (Measure of Textual Lexical Diversity)

MTLD provides a length-independent measure of lexical diversity.

| Metric | Value |
|--------|-------|
| **MTLD Forward** | 62.95 |
| **MTLD Backward** | 62.68 |
| **MTLD Average** | 62.82 |

**Interpretation:** An MTLD of ~63 indicates moderate lexical diversity, typical for accessible fiction writing.

### Yule's K and I

Statistical measures of vocabulary richness based on word frequency distribution.

| Metric | Value | Description |
|--------|-------|-------------|
| **Yule's K** | 130.6052 | Higher = more repetitive vocabulary |
| **Yule's I** | 0.5421 | Characteristic constant of vocabulary |

**Interpretation:** A Yule's K of ~131 suggests Doyle uses a moderately repetitive vocabulary, consistent with detective fiction's need for clarity.

### Hapax Legomena

Words that appear exactly once (hapax legomena) or twice (hapax dislegomena) in the text.

| Metric | Value | Description |
|--------|-------|-------------|
| **Hapax Legomena Count** | 2,922 | Words appearing once |
| **Hapax Legomena Ratio** | 0.0421 | Hapax / total tokens |
| **Hapax Dislegomena Count** | 885 | Words appearing twice |
| **Hapax Dislegomena Ratio** | 0.0127 | Dislegomena / total tokens |
| **Sichel's S** | 0.1515 | Dislegomena / types |
| **Honore's R** | 2,230.37 | Vocabulary richness statistic |

**Interpretation:** The Honore's R value of 2,230 is high, indicating substantial vocabulary richness and variety.

### Function Word Analysis

Function words (determiners, prepositions, pronouns, etc.) are important stylometric markers.

| Category | Ratio | Description |
|----------|-------|-------------|
| **Total Function Word Ratio** | 0.5352 | 53.5% of text is function words |
| **Function Word Diversity** | 0.0053 | Unique function words / total |
| **Determiner Ratio** | 0.1553 | the, a, an, this, etc. |
| **Preposition Ratio** | 0.1409 | in, on, at, by, etc. |
| **Conjunction Ratio** | 0.0679 | and, but, or, etc. |
| **Pronoun Ratio** | 0.1486 | I, he, she, it, etc. |
| **Auxiliary Ratio** | 0.0856 | be, have, do, will, etc. |
| **Particle Ratio** | 0.0306 | up, down, out, etc. |

**Top 10 Function Words:**

| Rank | Word | Count |
|------|------|-------|
| 1 | the | 3,266 |
| 2 | of | 1,588 |
| 3 | and | 1,564 |
| 4 | to | 1,395 |
| 5 | I | 1,283 |
| 6 | a | 1,280 |
| 7 | that | 1,082 |
| 8 | in | 896 |
| 9 | he | 877 |
| 10 | it | 850 |

### Advanced Lexical Diversity Metrics

#### VocD (Vocabulary Diversity)

| Metric | Value |
|--------|-------|
| **D Parameter** | 4.95 |
| **Sample Count** | 19 |
| **Optimal Sample Size** | 35 |

#### MATTR (Moving-Average Type-Token Ratio)

| Metric | Value |
|--------|-------|
| **MATTR Score** | 0.8268 |
| **MATTR Std Dev** | 0.0538 |
| **Window Size** | 50 |
| **Window Count** | 59,063 |
| **Min TTR** | 0.5400 |
| **Max TTR** | 0.9800 |

**Interpretation:** MATTR of 0.83 indicates high local vocabulary diversity, suggesting varied word choices within text segments.

#### HD-D (Hypergeometric Distribution D)

| Metric | Value |
|--------|-------|
| **HD-D Score** | 6,815.47 |
| **Sample Size** | 42 |
| **Type Count** | 6,852 |
| **Token Count** | 59,112 |

#### MSTTR (Mean Segmental Type-Token Ratio)

| Metric | Value |
|--------|-------|
| **MSTTR Score** | 0.7393 |
| **MSTTR Std Dev** | 0.0442 |
| **Segment Size** | 100 words |
| **Segment Count** | 591 |
| **Min TTR** | 0.5600 |
| **Max TTR** | 0.8600 |

### Word Frequency Sophistication

Measures vocabulary sophistication based on word frequency in reference corpora.

| Metric | Value | Description |
|--------|-------|-------------|
| **Mean Frequency Rank** | 16,105.08 | Average word frequency rank |
| **Median Frequency Rank** | 106.00 | Middle word frequency rank |
| **Rare Word Ratio** | 0.3205 | Low-frequency words |
| **Common Word Ratio** | 0.6671 | High-frequency words |
| **Academic Word Ratio** | 0.0064 | Academic Word List terms |
| **Advanced Word Ratio** | 0.3221 | Sophisticated vocabulary |

**Frequency Band Distribution:**

| Band | Ratio |
|------|-------|
| Very Common | 0.6671 |
| Common | 0.0124 |
| Moderate | 0.0000 |
| Rare | 0.0000 |
| Very Rare | 0.3205 |

---

## Readability Metrics

Readability formulas estimate the reading difficulty of text.

### Flesch Reading Ease

| Metric | Value |
|--------|-------|
| **Reading Ease Score** | 68.54 |
| **Grade Level (Flesch-Kincaid)** | 9.73 |
| **Difficulty** | Standard |

**Interpretation:** A score of 68.54 falls in the "Standard" range (60-70), indicating the text is easily understood by 13-15 year olds.

### SMOG Index

| Metric | Value |
|--------|-------|
| **SMOG Index** | 10.82 |
| **Grade Level** | 11 |

**Interpretation:** Requires approximately 11th grade education to understand.

### Gunning Fog Index

| Metric | Value |
|--------|-------|
| **Fog Index** | 11.86 |
| **Grade Level** | 12 |

**Interpretation:** Suggests 12th grade reading level based on sentence length and complex words.

### Coleman-Liau Index

| Metric | Value |
|--------|-------|
| **CLI Index** | 7.41 |
| **Grade Level** | 7 |

**Interpretation:** Character-based formula suggests 7th grade level.

### Automated Readability Index (ARI)

| Metric | Value |
|--------|-------|
| **ARI Score** | 9.55 |
| **Grade Level** | 10 |
| **Age Range** | 14-18 years (High School) |

### Dale-Chall Readability Score

| Metric | Value |
|--------|-------|
| **Dale-Chall Score** | 8.40 |
| **Difficult Word Count** | 13,277 |
| **Difficult Word Ratio** | 0.2255 |
| **Grade Level** | 11-12 |

**Interpretation:** 22.5% of words are not on the Dale-Chall familiar word list, resulting in an 11-12th grade reading level.

### Linsear Write Formula

| Metric | Value |
|--------|-------|
| **Linsear Write Score** | 27.92 |
| **Grade Level** | 14 |
| **Easy Words** | 54,481 |
| **Hard Words** | 4,398 |

### Fry Readability Graph

| Metric | Value |
|--------|-------|
| **Fry Grade Level** | 6 |
| **Avg Sentence Length** | 25.00 words |
| **Avg Syllables per 100 Words** | 136.00 |
| **Graph Zone** | Valid |

### FORCAST Index

| Metric | Value |
|--------|-------|
| **FORCAST Score** | 8.90 |
| **Grade Level** | 9 |
| **Single Syllable Ratio** | 0.7400 |

**Interpretation:** 74% monosyllabic words, yielding a 9th grade reading level.

### Powers-Sumner-Kearl Readability

| Metric | Value |
|--------|-------|
| **PSK Score** | -0.25 |
| **Grade Level** | -0.30 |
| **Avg Sentence Length** | 24.29 words |
| **Avg Syllables per Word** | 1.34 |

**Note:** Negative values indicate the text is below the primary grade level range this formula was designed for.

### Readability Summary

| Formula | Grade Level |
|---------|-------------|
| Flesch-Kincaid | 9.7 |
| SMOG | 11.0 |
| Gunning Fog | 12.0 |
| Coleman-Liau | 7.0 |
| ARI | 10.0 |
| Dale-Chall | 11-12 |
| Linsear Write | 14.0 |
| Fry | 6.0 |
| FORCAST | 9.0 |
| **Average** | **~10** |

**Conclusion:** The Hound of the Baskervilles is written at approximately a 10th grade reading level (age 15-16), making it accessible to most adult readers.

---

## Syntactic Metrics

Syntactic analysis examines sentence structure and grammatical patterns.

### Part-of-Speech Ratios

| POS Category | Ratio | Description |
|--------------|-------|-------------|
| **Noun Ratio** | 0.1985 | 19.9% nouns |
| **Verb Ratio** | 0.1258 | 12.6% verbs |
| **Adjective Ratio** | 0.0652 | 6.5% adjectives |
| **Adverb Ratio** | 0.0543 | 5.4% adverbs |
| **Noun-Verb Ratio** | 1.5776 | More nouns than verbs |
| **Adjective-Noun Ratio** | 0.3287 | Moderate adjective use |
| **Lexical Density** | 0.4439 | 44.4% content words |
| **Function Word Ratio** | 0.2837 | 28.4% function words |

**Interpretation:** The noun-verb ratio of 1.58 indicates a nominal style with emphasis on descriptions and entities, typical of narrative prose.

### Sentence Statistics

| Metric | Value |
|--------|-------|
| **Sentence Count** | 3,297 |
| **Mean Sentence Length** | 17.96 words |
| **Sentence Length Std Dev** | 11.18 |
| **Sentence Length Range** | 76 |
| **Min Sentence Length** | 1 word |
| **Max Sentence Length** | 77 words |

**Interpretation:** Average sentence length of ~18 words is characteristic of well-paced narrative prose. The high standard deviation (11.18) shows varied sentence lengths for stylistic effect.

### Advanced Syntactic Analysis

| Metric | Value | Description |
|--------|-------|-------------|
| **Mean Parse Tree Depth** | 5.04 | Average syntactic complexity |
| **Max Parse Tree Depth** | 17 | Most complex sentence structure |
| **T-Unit Count** | 3,297 | Minimal terminable units |
| **Mean T-Unit Length** | 23.16 words | Words per T-unit |
| **Clausal Density** | 2.6621 | Clauses per T-unit |
| **Dependent Clause Ratio** | 0.4997 | 50% dependent clauses |
| **Subordination Index** | 0.2453 | Degree of subordination |
| **Coordination Index** | 0.1246 | Degree of coordination |
| **Passive Voice Ratio** | 0.1089 | 10.9% passive constructions |
| **Sentence Complexity Score** | 0.6962 | Overall complexity metric |
| **Dependency Distance** | 3.4509 | Avg head-dependent distance |
| **Left Branching Ratio** | 0.4440 | Left-heavy structures |
| **Right Branching Ratio** | 0.5560 | Right-heavy structures |

**Interpretation:** The clausal density of 2.66 indicates complex sentence structures with multiple clauses. The near-equal left/right branching ratios show balanced sentence construction.

### Sentence Type Classification

#### Structural Types

| Type | Ratio | Count | Description |
|------|-------|-------|-------------|
| **Simple** | 0.2872 | 947 | One independent clause |
| **Compound** | 0.0607 | 200 | Multiple independent clauses |
| **Complex** | 0.4495 | 1,482 | Independent + dependent clauses |
| **Compound-Complex** | 0.2026 | 668 | Multiple independent + dependent |

**Interpretation:** 44.9% of sentences are complex, showing Doyle's preference for subordination over coordination. Only 6% are compound sentences.

#### Functional Types

| Type | Ratio | Count | Description |
|------|-------|-------|-------------|
| **Declarative** | 0.9275 | 3,058 | Statements |
| **Interrogative** | 0.0334 | 110 | Questions |
| **Exclamatory** | 0.0191 | 63 | Exclamations |
| **Imperative** | 0.0200 | 66 | Commands |

**Interpretation:** 92.8% declarative sentences reflect the narrative nature of the text, with dialogue contributing questions (3.3%) and exclamations (1.9%).

#### Diversity Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Structural Diversity** | 1.7474 | Shannon entropy of structure types |
| **Functional Diversity** | 0.4864 | Shannon entropy of function types |

---

## Character-Level Metrics

Character-level features capture low-level writing patterns.

### Basic Character Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Average Word Length** | 4.16 characters | Mean word length |
| **Average Sentence Length** | 83.98 characters | Mean sentence length |
| **Punctuation Density** | 13.6233 | Punctuation per 100 words |
| **Punctuation Variety** | 12 types | Unique punctuation marks |
| **Vowel-Consonant Ratio** | 0.6152 | Vowels / consonants |
| **Digit Count** | 93 | Numeric characters |
| **Digit Ratio** | 0.000263 | Digits / total characters |
| **Uppercase Ratio** | 0.0288 | Uppercase / total letters |
| **Whitespace Ratio** | 0.2725 | Whitespace / total characters |

**Interpretation:** The average word length of 4.16 characters is typical for English prose. The vowel-consonant ratio of 0.615 is close to the English average (~0.6).

### Letter Frequency Distribution

| Rank | Letter | Frequency |
|------|--------|-----------|
| 1 | e | 0.1222 |
| 2 | t | 0.0921 |
| 3 | a | 0.0801 |
| 4 | o | 0.0787 |
| 5 | i | 0.0695 |
| 6 | h | 0.0681 |
| 7 | n | 0.0667 |
| 8 | s | 0.0624 |
| 9 | r | 0.0585 |
| 10 | d | 0.0425 |

**Interpretation:** The letter frequency closely matches standard English distribution (ETAOIN SHRDLU), indicating typical English prose.

---

## N-gram Entropy Metrics

N-gram entropy measures the predictability and information content of the text.

### Character Bigram Entropy

| Metric | Value | Description |
|--------|-------|-------------|
| **Entropy** | 7.5928 bits | Information per bigram |
| **Perplexity** | 193.0498 | Prediction difficulty |
| **N-gram Type** | character_2gram | Character pairs |

**Interpretation:** A character bigram entropy of 7.59 bits indicates moderate predictability at the character level.

### Word Bigram Entropy

| Metric | Value | Description |
|--------|-------|-------------|
| **Entropy** | 13.5375 bits | Information per bigram |
| **Perplexity** | 11,890.62 | Prediction difficulty |
| **N-gram Type** | word_2gram | Word pairs |

**Interpretation:** The high word bigram perplexity of ~11,891 indicates diverse word combinations, consistent with varied narrative prose.

---

## Usage

To reproduce this analysis:

```python
from pathlib import Path

# Read the text
text = Path("tests/fixtures/doyle-the-hound-of-the-baskervilles.txt").read_text()

# Lexical metrics
from pystylometry.lexical import compute_ttr, compute_mtld, compute_yule
ttr = compute_ttr(text)
mtld = compute_mtld(text)
yule = compute_yule(text)

# Readability metrics
from pystylometry.readability import compute_flesch, compute_smog
flesch = compute_flesch(text)
smog = compute_smog(text)

# Syntactic metrics (requires spaCy)
from pystylometry.syntactic import compute_pos_ratios, compute_sentence_stats
pos = compute_pos_ratios(text)
stats = compute_sentence_stats(text)

# Character metrics
from pystylometry.character import compute_character_metrics
char = compute_character_metrics(text)

# N-gram metrics
from pystylometry.ngrams import compute_word_bigram_entropy
entropy = compute_word_bigram_entropy(text)
```

---

## References

1. Guiraud, P. (1960). *Problemes et methodes de la statistique linguistique*.
2. Flesch, R. (1948). "A new readability yardstick." *Journal of Applied Psychology*.
3. Burrows, J. (2002). "'Delta': A measure of stylistic difference." *Literary and Linguistic Computing*.
4. McCarthy, P. M., & Jarvis, S. (2010). "MTLD, vocd-D, and HD-D: A validation study." *Behavior Research Methods*.

# Word Morphological Classification

## Surface-Form Taxonomy for Corpus Frequency Analysis

Words in English corpora are not all plain lexical items. Contractions, hyphenated compounds, dialectal reductions, and borrowed words with non-ASCII characters each require distinct handling in frequency analysis. This module classifies words into a three-layer taxonomy based on orthographic properties and curated word lists, producing dot-separated labels such as `apostrophe.contraction.negative` or `hyphenated.reduplicated.ablaut`.

The primary motivation is BNC frequency analysis: the BNC's CLAWS4 tagger splits contractions into component tokens ("it" + "'s") and never counts them as single words, producing absurd overuse ratios (e.g. 93,000x for "it's") when compared against raw corpus text. Classification enables analysts to filter, group, or reweight these forms intelligently.

---

## Theoretical Background

### Taxonomy Layers

The taxonomy has three layers, from coarsest to most specific:

**L1 -- Orthographic class** (deterministic, based on character inspection):

| L1 Value | Trigger |
|----------|---------|
| `lexical` | Pure a-z, no special characters |
| `apostrophe` | Contains `'` |
| `hyphenated` | Contains `-` |
| `apostrophe_hyphenated` | Contains both `'` and `-` |
| `unicode` | Contains non-ASCII characters |
| `numeric` | Contains digits |
| `other` | Non-a-z characters not matching any above |

**L2 -- Morphological category** (pattern-matched via word lists and regex):

Examples: `contraction`, `possessive`, `enclitic`, `aphetic`, `dialectal`, `reduplicated`, `compound`, `prefixed`, `number_word`, `directional`, `phrasal_modifier`, `ordinal`, `compound_reduction`, `unclassified`.

**L3 -- Specific pattern** (most granular):

Examples: `negative`, `copula`, `auxiliary`, `archaic`, `poetic`, `pronoun_reduction`, `medial`, `initial`, `regional`, `g_dropping`, `singular`, `plural`, `exact`, `rhyming`, `ablaut`, `self`.

### Linguistic Foundations

The classification draws on established linguistic categories:

**Negative contractions (n't).** Zwicky & Pullum (1983) argued that -n't is an inflectional affix on auxiliary verbs, not a clitic. This makes negative contractions (don't, can't, won't) a linguistically distinct class from copula/auxiliary enclitics.

**Verbal clitics ('s, 're, 'll, 'd, 've).** Huddleston & Pullum (2002) distinguish verbal clitics (he's = he is) from the possessive 's, which is a phrasal clitic attaching to the end of a noun phrase rather than a specific word. The 's ambiguity (contraction vs. possessive) is resolved by listing pronoun/adverb hosts in the contraction set; anything else with 's falls to possessive.

**Aphetic forms ('twas, 'gainst).** Murray (1880) coined the term "aphesis" for the loss of unstressed initial vowels. Schutzler (2020) cataloged these forms across Late Modern English dialects, distinguishing archaic forms ('twas, 'tis) from poetic reductions ('gainst, 'neath).

**Compound classification.** Plag (2003/2018) covers compound classification and productive prefixation. Sun & Baayen (2020) validated hyphen presence as a systematic orthographic signal of compound type, making the hyphen a reliable classification feature.

**Reduplication.** Three formally recognized subtypes appear in English:
- **Exact** (bye-bye, hush-hush) -- identical elements
- **Rhyming** (helter-skelter, nitty-gritty) -- onset varies, rime matches
- **Ablaut** (zig-zag, tick-tock) -- vowel alternation following a phonological constraint where the first vowel is high/front (/I/) and the second is low/back (/ae/ or /Q/)

### Resolution Order

Classification proceeds in a fixed order designed to maximize precision:

1. **Exact lookup** against curated word lists (~200 entries)
2. **Regex patterns** for structural matches (prefixes, number words, ordinals, g-dropping)
3. **L1 flags** as a character-inspection safety net
4. **`unclassified`** when a word triggers a flag but matches no known pattern

The `unclassified` outcome exists at every L1 category to support iterative refinement: analyze a corpus, inspect unclassified words, add them to the appropriate word list or pattern, and re-run.

---

## Implementation

### API

```python
from pystylometry.lexical.word_class import classify_word, WordClass
```

**`classify_word(word: str) -> WordClass`**

Classifies a single word token into the three-layer taxonomy. Case is preserved in the result but matching is case-insensitive.

**`WordClass`** dataclass (frozen, slotted):

| Field | Type | Description |
|-------|------|-------------|
| `word` | `str` | The original word that was classified |
| `l1` | `str` | Orthographic class (always present) |
| `l2` | `str \| None` | Morphological category (may be `None` for `lexical`) |
| `l3` | `str \| None` | Specific pattern (may be `None` when L2 is the deepest level) |
| `label` | `str` (property) | Dot-separated path combining l1, l2, l3 |

### Classification Categories

The full taxonomy of currently recognized labels:

| Label | Example | Count |
|-------|---------|-------|
| `lexical` | trembling, house, quickly | -- |
| `apostrophe.contraction.negative` | don't, can't, won't | 22 |
| `apostrophe.contraction.copula` | it's, he's, there's | 21 |
| `apostrophe.contraction.auxiliary` | I'll, they'd, we've | 30 |
| `apostrophe.enclitic` | let's | 1 |
| `apostrophe.aphetic.archaic` | 'twas, 'tis, 'twill | 6 |
| `apostrophe.aphetic.poetic` | 'gainst, 'neath, 'twixt | 7 |
| `apostrophe.dialectal.pronoun_reduction` | 'em, 'er, 'im | 4 |
| `apostrophe.dialectal.medial` | o'clock, ma'am, ne'er | 8 |
| `apostrophe.dialectal.initial` | 'bout, 'cause, 'spose | 10 |
| `apostrophe.dialectal.regional` | y'all, ya'll | 2 |
| `apostrophe.dialectal.g_dropping` | runnin', jumpin' | regex |
| `apostrophe.possessive.singular` | dog's, Alice's | regex |
| `apostrophe.possessive.plural` | dogs', teachers' | regex |
| `apostrophe.unclassified` | (fallback) | -- |
| `hyphenated.reduplicated.exact` | bye-bye, hush-hush | 14 |
| `hyphenated.reduplicated.rhyming` | helter-skelter, wishy-washy | 18 |
| `hyphenated.reduplicated.ablaut` | zig-zag, tick-tock | 18 |
| `hyphenated.directional` | north-east, south-west | 14 |
| `hyphenated.compound.self` | self-esteem, self-aware | regex |
| `hyphenated.number_word` | twenty-one, forty-second | regex |
| `hyphenated.phrasal_modifier` | state-of-the-art | regex |
| `hyphenated.prefixed` | re-enter, co-operate | regex |
| `hyphenated.unclassified` | (fallback) | -- |
| `apostrophe_hyphenated.compound_reduction` | jack-o'-lantern, will-o'-the-wisp | 4 |
| `apostrophe_hyphenated.unclassified` | (fallback) | -- |
| `numeric.ordinal` | 1st, 2nd, 23rd, 100th | regex |
| `numeric.unclassified` | (fallback) | -- |
| `unicode.unclassified` | cafe, naive | -- |
| `other.unclassified` | (fallback) | -- |

---

## Usage

### Basic Classification

```python
from pystylometry.lexical.word_class import classify_word

result = classify_word("don't")
print(result.label)   # apostrophe.contraction.negative
print(result.l1)      # apostrophe
print(result.l2)      # contraction
print(result.l3)      # negative
```

### Classifying a Tokenized Text

```python
from pystylometry.lexical.word_class import classify_word

tokens = ["The", "cat", "couldn't", "cross", "the", "zig-zag", "path"]
for token in tokens:
    wc = classify_word(token)
    print(f"{token:20s} -> {wc.label}")
```

Output:

```
The                  -> lexical
cat                  -> lexical
couldn't             -> apostrophe.contraction.negative
cross                -> lexical
the                  -> lexical
zig-zag              -> hyphenated.reduplicated.ablaut
path                 -> lexical
```

### Filtering by Orthographic Class

```python
from pystylometry.lexical.word_class import classify_word

tokens = text.lower().split()
apostrophe_words = [t for t in tokens if classify_word(t).l1 == "apostrophe"]
contractions = [t for t in tokens if classify_word(t).l2 == "contraction"]
```

### Grouping by Label

```python
from collections import Counter
from pystylometry.lexical.word_class import classify_word

tokens = text.lower().split()
label_counts = Counter(classify_word(t).label for t in tokens)

for label, count in label_counts.most_common():
    print(f"{label:45s} {count:5d}")
```

### Identifying Unclassified Words for Refinement

```python
from pystylometry.lexical.word_class import classify_word

tokens = text.lower().split()
unclassified = [
    (t, classify_word(t))
    for t in set(tokens)
    if classify_word(t).label.endswith(".unclassified")
]

for word, wc in sorted(unclassified):
    print(f"{word:20s} -> {wc.label}")
```

This is the intended workflow for iterative refinement: run classification on a corpus, inspect the unclassified words, and add them to the appropriate word list or regex pattern.

---

## Limitations

1. **Finite word lists.** The curated word lists cover ~200 common forms. Less frequent contractions, dialectal spellings, or domain-specific hyphenated compounds will fall to `unclassified`. This is by design -- the lists are intended to grow incrementally through corpus analysis.

2. **No sentential context.** The classifier operates on isolated tokens. The 's ambiguity (contraction "he's" vs. possessive "the dog's") is resolved heuristically by listing known pronoun/adverb hosts as contractions. Context-dependent cases like "John's" (is/has vs. possessive) always resolve to possessive.

3. **BNC tokenization mismatch.** The BNC's CLAWS4 tagger splits contractions into component tokens. A word like "don't" in raw text corresponds to "do" + "n't" in the BNC. This module classifies the raw surface form, not the BNC-tokenized form.

4. **English only.** The word lists and regex patterns are designed for English. Apostrophe and hyphen conventions differ across languages.

5. **Case insensitivity.** Classification lowercases all input for matching. Words where case is semantically significant (e.g. proper nouns) are not distinguished.

6. **Unicode catch-all.** Non-ASCII words (cafe, naive, resume) are currently all `unicode.unclassified`. Finer-grained classification (e.g. distinguishing diacritics-on-English-loanwords from foreign-language text) is planned for future refinement.

---

## References

- Zwicky, A. M., & Pullum, G. K. (1983). Cliticization vs. Inflection: English N'T. *Language*, 59(3), 502-513. https://web.stanford.edu/~zwicky/ZPCliticsInfl.pdf
- Huddleston, R., & Pullum, G. K. (2002). *The Cambridge Grammar of the English Language*. Cambridge University Press.
- Plag, I. (2003/2018). *Word-Formation in English*. Cambridge Textbooks in Linguistics.
- Bauer, L. (2003). *Introducing Linguistic Morphology*. Edinburgh University Press.
- Murray, J. A. H. (1880). Aphesis. *Proceedings of the Philological Society*.
- Schutzler, O. (2020). Aphesis and Aphaeresis in Late Modern English Dialects. *English Studies*, 102(1). https://doi.org/10.1080/0013838X.2020.1866306
- Sun, C. C., & Baayen, R. H. (2020). Hyphenation as a Compounding Technique. https://quantling.org/~hbaayen/publications/SunBaayen2020.pdf
- BNC CLAWS4 tagger documentation. http://www.natcorp.ox.ac.uk/docs/URG/posguide.html

### Related GitHub Issues

- [#51 -- Word morphological classification taxonomy](https://github.com/craigtrim/pystylometry/issues/51)
- [#52 -- Linguistics literature supporting the taxonomy](https://github.com/craigtrim/pystylometry/issues/52)

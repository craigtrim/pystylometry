# Comprehensive Stylometry Metrics Reference

## Lexical Richness

| Metric | Formula | Measures |
|--------|---------|----------|
| TTR (Type-Token Ratio) | V / N | Basic vocabulary diversity |
| Root TTR (Guiraud) | V / √N | Length-normalized diversity |
| Log TTR (Herdan) | log(V) / log(N) | Logarithmic diversity |
| STTR (Standardized TTR) | mean(TTR per chunk) | Chunk-averaged diversity |
| MSTTR | mean(TTR per 100 words) | Mean segmental diversity |
| Hapax Legomena Ratio | V₁ / N | Words appearing exactly once |
| Hapax Dislegomena Ratio | V₂ / N | Words appearing exactly twice |
| Sichel's S | V₂ / V | Ratio of dis- to total types |
| Honoré's R | 100 × log(N) / (1 - V₁/V) | Vocabulary richness constant |
| Brunet's W | N^(V^-0.172) | Length-independent richness |
| Yule's K | 10⁴ × (Σm²×Vm - N) / N² | Vocabulary repetitiveness |
| Yule's I | (V² / Σm²×Vm) - (1/N) | Inverse of Yule's K |
| Simpson's D | Σ(Vm × m × (m-1)) / (N × (N-1)) | Probability of repetition |
| MTLD | Mean length of TTR > threshold | Maintained lexical diversity |
| HD-D | Hypergeometric distribution D | Sample-size independent diversity |
| VOCD-D | Curve-fitted diversity | Robust vocabulary measure |

## Sentence-Level

| Metric | Formula | Measures |
|--------|---------|----------|
| Mean Sentence Length | total words / sentence count | Syntactic complexity |
| Sentence Length Std | σ of sentence lengths | Sentence variation |
| Sentence Length Range | max - min sentence length | Stylistic range |
| Clause Density | clauses / sentences | Subordination complexity |
| T-Unit Length | words per T-unit | Minimal terminable unit |

## Word-Level

| Metric | Formula | Measures |
|--------|---------|----------|
| Mean Word Length | total chars / total words | Vocabulary sophistication |
| Word Length Std | σ of word lengths | Word length variation |
| Long Word Ratio | words > 6 chars / N | Complex word usage |
| Syllables per Word | syllables / N | Phonetic complexity |

## Function Words

| Metric | Formula | Measures |
|--------|---------|----------|
| Function Word Ratio | function words / N | Grammatical word reliance |
| Content Word Ratio | content words / N | Lexical word density |
| Pronoun Ratio | pronouns / N | Personal style marker |
| Article Ratio | (a, an, the) / N | Definiteness preference |
| Conjunction Ratio | conjunctions / N | Coordination style |
| Preposition Ratio | prepositions / N | Relational expression |

## Syntactic / POS

| Metric | Formula | Measures |
|--------|---------|----------|
| Noun Ratio | nouns / N | Nominal style |
| Verb Ratio | verbs / N | Action density |
| Adjective Ratio | adjectives / N | Descriptive density |
| Adverb Ratio | adverbs / N | Modification style |
| Noun-Verb Ratio | nouns / verbs | Static vs dynamic |
| Adjective-Noun Ratio | adjectives / nouns | Description density |
| Lexical Density | content words / total words | Information packaging |

## Punctuation

| Metric | Formula | Measures |
|--------|---------|----------|
| Comma Frequency | commas / sentences | Phrase segmentation |
| Semicolon Frequency | semicolons / sentences | Clause connection style |
| Question Frequency | ? / sentences | Interrogative style |
| Exclamation Frequency | ! / sentences | Emphatic style |
| Quote Frequency | quotes / N | Dialogue density |

## Readability

| Metric | Formula | Measures |
|--------|---------|----------|
| Flesch Reading Ease | 206.835 - 1.015×ASL - 84.6×ASW | Text difficulty (0-100) |
| Flesch-Kincaid Grade | 0.39×ASL + 11.8×ASW - 15.59 | US grade level |
| Gunning Fog Index | 0.4 × (ASL + complex word %) | Years of education needed |
| SMOG Index | 1.043 × √(polysyllables × 30/sentences) + 3.1291 | Education years |
| Coleman-Liau Index | 0.0588×L - 0.296×S - 15.8 | Grade level |
| ARI | 4.71×(chars/words) + 0.5×(words/sentences) - 21.43 | Automated readability |

## N-gram / Sequence

| Metric | Formula | Measures |
|--------|---------|----------|
| Character Bigram Entropy | -Σ p(bg) × log₂(p(bg)) | Character predictability |
| Word Bigram Entropy | -Σ p(bg) × log₂(p(bg)) | Word sequence predictability |
| Trigram Perplexity | 2^H(trigrams) | Language model fit |

## Authorship-Specific

| Metric | Formula | Measures |
|--------|---------|----------|
| Burrows' Delta | mean│z(f) - z(f')│ | Author distance |
| Cosine Delta | 1 - cos(z, z') | Angular author distance |
| Eder's Delta | Burrows' with culling | Noise-reduced delta |
| Zeta Score | marker / anti-marker balance | Distinctive word usage |

## Legend

- **N** = total tokens
- **V** = vocabulary size (unique types)
- **V₁** = hapax legomena count (words appearing once)
- **V₂** = hapax dislegomena count (words appearing twice)
- **Vm** = words occurring m times
- **ASL** = average sentence length
- **ASW** = average syllables per word
- **L** = letters per 100 words
- **S** = sentences per 100 words

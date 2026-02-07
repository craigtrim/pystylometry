# pystylometry Documentation

A Python library for stylometric analysis and authorship attribution.

## Authorship

- [Kilgarriff Chi-Squared Method](authorship/kilgarriff.md) - Corpus comparison and drift detection
- [Burrows' Delta](authorship/burrows_delta.md) - Burrows' Delta and Cosine Delta authorship distance
- [Zeta](authorship/zeta.md) - Zeta method for marker word detection
- [Compression Distance](authorship/compression.md) - Normalized Compression Distance (NCD)
- [Additional Methods](authorship/additional_methods.md) - MinMax, Delta variations, and NCD

## Character

- [Character Metrics](character/character_metrics.md) - Character-level stylometric features

## Lexical

- [Type-Token Ratio](lexical/ttr.md) - TTR, Root TTR, Log TTR, and STTR
- [MTLD](lexical/mtld.md) - Measure of Textual Lexical Diversity
- [Yule's K and I](lexical/yule.md) - Vocabulary richness via frequency spectrum
- [Hapax Legomena](lexical/hapax.md) - Hapax analysis, Sichel's S, Honore's R
- [Function Words](lexical/function_words.md) - Function word frequency and distribution
- [Advanced Diversity](lexical/advanced_diversity.md) - voc-D, MATTR, HD-D, MSTTR
- [Word Frequency Sophistication](lexical/word_frequency_sophistication.md) - COCA frequency ranks and Academic Word List
- [Repetitive Word and N-gram Detection](lexical/repetition.md) - Verbal tics and AI slop detection via BNC baseline
- [Word Morphological Classification](lexical/word_class.md) - Three-layer surface-form taxonomy for corpus frequency analysis

## Readability

- [Flesch](readability/flesch.md) - Flesch Reading Ease and Flesch-Kincaid Grade Level
- [SMOG](readability/smog.md) - Simple Measure of Gobbledygook
- [ARI](readability/ari.md) - Automated Readability Index
- [Coleman-Liau](readability/coleman_liau.md) - Coleman-Liau Index
- [Gunning Fog](readability/gunning_fog.md) - Gunning Fog Index
- [Syllables](readability/syllables.md) - Syllable counting utilities
- [Complex Words](readability/complex_words.md) - Complex word detection
- [Additional Formulas](readability/additional_formulas.md) - Dale-Chall, Linsear Write, Fry, FORCAST, Powers-Sumner-Kearl

## Syntactic

- [POS Ratios](syntactic/pos_ratios.md) - Part-of-speech ratio analysis
- [Sentence Statistics](syntactic/sentence_stats.md) - Sentence-level statistical features
- [Sentence Types](syntactic/sentence_types.md) - Sentence type classification
- [Advanced Syntactic](syntactic/advanced_syntactic.md) - Dependency distance, clause density, tree depth

## Stylistic

- [Stylistic Markers](stylistic/markers.md) - Contractions, intensifiers, hedges, modals, negation, punctuation
- [Vocabulary Overlap](stylistic/vocabulary_overlap.md) - Jaccard, Dice, Cosine, and KL divergence metrics
- [Cohesion and Coherence](stylistic/cohesion_coherence.md) - Referential cohesion, connectives, and coherence measures
- [Genre and Register](stylistic/genre_register.md) - Formality scoring, register classification, and genre prediction

## N-grams

- [Extended N-grams](ngrams/extended_ngrams.md) - Word, character, and POS n-gram analysis
- [Entropy](ngrams/entropy.md) - N-gram entropy and perplexity

## Dialect

- [Dialect Detector](dialect/detector.md) - British vs. American English detection and markedness scoring

## Prosody

- [Rhythm and Prosody](prosody/rhythm_prosody.md) - Syllable patterns, rhythmic regularity, phonological features

## Consistency

- [Stylistic Drift](consistency/drift.md) - Kilgarriff chi-squared intra-document drift detection

## Visualization

- [Drift Plots](viz/drift.md) - Matplotlib drift timeline, scatter, and report visualizations
- [Interactive Timeline](viz/jsx/timeline.md) - Self-contained HTML/JSX interactive timeline export
- [Standalone Viewer](viz/jsx/viewer.md) - Browser-based drag-and-drop drift analyzer

## Additional Resources

- [Metrics Showcase](metrics-showcase-hound-of-baskervilles.md) - Comprehensive metrics demonstration

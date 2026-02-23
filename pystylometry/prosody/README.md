# prosody

![3 public functions](https://img.shields.io/badge/functions-3-blue)
![Requires cmudict](https://img.shields.io/badge/requires-cmudict-orange)

Rhythm and stress pattern analysis for written text.

## Catalogue

| File | Function | What It Measures |
|------|----------|-----------------|
| `rhythm_prosody.py` | `compute_rhythm_prosody` | Syllable stress patterns, rhythm regularity, prose rhythm metrics |
| `sentence_syllable_patterns.py` | `compute_sentence_syllable_patterns` | Sentence-level syllable distribution, complexity uniformity (AI detection signal) |
| `syllable_pattern_repetition.py` | `analyze_syllable_pattern_repetition` | Repeated syllable n-gram patterns, formulaic writing detection, rhythmic templates |

## Related GitHub Issues

- [#66](https://github.com/craigtrim/pystylometry/issues/66) - Sentence-level syllable analysis
- [#67](https://github.com/craigtrim/pystylometry/issues/67) - Syllable pattern repetition analysis
- [#68](https://github.com/craigtrim/pystylometry/issues/68) - Replace spaCy with built-in utilities (removed size limit)

## See Also

- [`readability/syllables.py`](../readability/) for the syllable counting engine
- [`_utils.py`](../_utils.py) for sentence segmentation and tokenization (used by sentence syllable analysis)

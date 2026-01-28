# dialect

![1 public function](https://img.shields.io/badge/functions-1-blue)
![No external deps](https://img.shields.io/badge/deps-none-brightgreen)

Regional dialect detection (British vs. American English) with markedness scoring.

## Catalogue

| File | Function | What It Does |
|------|----------|-------------|
| `detector.py` | `compute_dialect` | Classifies text dialect, computes British/American scores, markedness |
| `_loader.py` | `get_markers`, `DialectMarkers` | Loads and caches extensible JSON marker database |
| `_data/dialect_markers.json` | _(data)_ | Vocabulary, spelling, grammar, and eye-dialect markers |

## Detection Categories

- **Vocabulary** -- flat/apartment, lorry/truck, boot/trunk
- **Spelling** -- colour/color, organise/organize, centre/center
- **Grammar** -- collective noun agreement, "have got" patterns
- **Eye dialect** -- gonna, wanna (register markers, not true dialect)

## See Also

- [`stylistic/`](../stylistic/) for broader style marker analysis
- [`stylistic/genre_register.py`](../stylistic/) for formality and register classification

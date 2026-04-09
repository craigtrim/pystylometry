"""Local CMU Pronouncing Dictionary wrapper — replaces the ``pronouncing`` package.

The third-party ``pronouncing`` library (v0.2.0, last updated 2015) is a thin
wrapper around the ``cmudict`` package. It uses the deprecated ``pkg_resources``
API (``from pkg_resources import resource_stream``), which fails on modern Python
environments where ``setuptools`` no longer ships ``pkg_resources`` by default.

This module provides the same two functions that pystylometry actually uses —
``phones_for_word`` and ``syllable_count`` — by talking to ``cmudict`` directly.
The ``cmudict`` package uses ``importlib.resources`` and works reliably.

When a direct CMU lookup misses, an optional **suffix-stripping cascade**
attempts to recover stress patterns by decomposing the word via lookup
libraries (BNC, WordNet, Google Ngrams) and finding a CMU-lookable stem.
See ``suffix_cascade.py`` for details.

Related GitHub Issues:
    #60 - Replace pronouncing with direct cmudict access
    https://github.com/craigtrim/pystylometry/issues/60
    #82 - Suffix-stripping CMU fallback via lookup libraries
    https://github.com/craigtrim/pystylometry/issues/82

References:
    CMU Pronouncing Dictionary:
        Weide, R. L. (1998). The CMU Pronouncing Dictionary, release 0.6d.
        Carnegie Mellon University.
        http://www.speech.cs.cmu.edu/cgi-bin/cmudict

    ARPAbet notation:
        Phonemes are represented in ARPAbet.  Vowel phonemes carry a trailing
        stress digit: 0 = no stress, 1 = primary stress, 2 = secondary stress.
        Example: "hello" → ``HH AH0 L OW1`` (2 syllables, stress on second).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

# ---------------------------------------------------------------------------
# Lazy-loaded CMU dictionary (~126 K entries).  Loaded once on first access
# and cached for the lifetime of the process.
# ---------------------------------------------------------------------------

_cmu_dict: Dict[str, List[List[str]]] | None = None


def _get_dict() -> Dict[str, List[List[str]]]:
    """Return the CMU dictionary, loading it lazily on first call.

    The dictionary maps lowercase words to a list of pronunciations.
    Each pronunciation is a list of ARPAbet phoneme strings, e.g.::

        {"hello": [["HH", "AH0", "L", "OW1"], ["HH", "EH0", "L", "OW1"]]}
    """
    global _cmu_dict  # noqa: PLW0603
    if _cmu_dict is None:
        import cmudict  # type: ignore[import-untyped]

        _cmu_dict = cmudict.dict()
    return _cmu_dict


# ---------------------------------------------------------------------------
# Public API — drop-in replacements for pronouncing.phones_for_word and
# pronouncing.syllable_count.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=8192)
def phones_for_word(word: str) -> List[str]:
    """Look up all pronunciations of *word* in the CMU dictionary.

    If the word is not found in CMU directly, a suffix-stripping cascade is
    attempted: the word is decomposed via lookup libraries (BNC, WordNet,
    Google Ngrams), suffixes are stripped to recover a CMU-lookable stem,
    and a synthetic ARPAbet string is reconstructed with the root's stress
    pattern plus unstressed placeholder syllables for the suffix material.

    Related GitHub Issues:
        #60 — https://github.com/craigtrim/pystylometry/issues/60
        #82 — https://github.com/craigtrim/pystylometry/issues/82

    Returns:
        A list of space-joined ARPAbet strings, or an empty list if the
        word cannot be resolved by either CMU or the suffix cascade.

    Example::

        >>> phones_for_word("hello")
        ['HH AH0 L OW1', 'HH EH0 L OW1']
        >>> phones_for_word("happiness")   # recovered via suffix cascade
        ['HH AE1 P IY0 N AH0']
        >>> phones_for_word("xyzzy")
        []
    """
    cmu = _get_dict()
    entries = cmu.get(word.lower())
    if entries is not None:
        # Direct CMU hit — return all pronunciations
        return [" ".join(phonemes) for phonemes in entries]

    # -----------------------------------------------------------------------
    # Suffix-stripping cascade fallback (Issue #82)
    #
    # The word is not in CMU.  Attempt to recover its stress pattern by
    # decomposing it morphologically and looking up the root in CMU.
    # -----------------------------------------------------------------------
    try:
        from .suffix_cascade import suffix_cascade_lookup

        phones_list, _source = suffix_cascade_lookup(word.lower(), cmu)
        if phones_list:
            return phones_list
    except Exception:
        # Suffix cascade is best-effort — never let it break core lookups
        pass

    return []


def syllable_count(phones: str) -> int:
    """Count syllables from an ARPAbet phoneme string.

    Syllable nuclei in ARPAbet are vowel phonemes, which are the only phonemes
    that carry a trailing stress digit (0, 1, or 2).  Counting those digits
    gives the syllable count.

    Args:
        phones: Space-joined ARPAbet string, e.g. ``"HH AH0 L OW1"``.

    Returns:
        Number of syllables (≥ 0).

    Example::

        >>> syllable_count("HH AH0 L OW1")
        2
        >>> syllable_count("K AE1 T")
        1
    """
    return sum(1 for phoneme in phones.split() if phoneme[-1].isdigit())
